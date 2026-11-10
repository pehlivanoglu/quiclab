#!/usr/bin/env python3
"""Score the SBD baselines (DCW, rmcatSBD, dcSBD) as grouping methods on
quiclab runs, next to ECG, against the same pairwise truth.

    python scripts/grouping_baselines.py .runs/<campaign>/det-*-r1 [--methods dcw,rmcat_sbd,dc_sbd]
                                        [--owd oracle|est] [--ecg grouping,grouping-owd,grouping-truth]

Grouping-only tooling. The baselines' own output (<run>/baselines/<method>-<owd>.csv,
window labels per client) is produced by scripts/sbd_baselines.py; this script
calls it when the file is missing and never rewrites it. Results go to
<run>/grouping/baselines.json.

Truth (grouping_adapter.truth_of): pairs_leaf = same tightest hit group
(detector/bursts.csv); pairs = hit by a common burst (share some link).

Per method and run:
  final      one grouping per run: a pair is SAME when the method groups it in
             at least half of the burst windows (windows that overlap a burst or
             its 2 s recovery, after the first burst). ECG: its decision at the
             close of the last event (SAME = same confirmed leaf). Both are
             scored against pairs_leaf (precision / recall over decided pairs)
             and against pairs.
  t_correct  first time the method's instantaneous grouping equals pairs_leaf
             on every pair (SBD: a window; ECG: an event close), or null.
  windows    SBD only, in its own terms: pairwise precision / recall per burst
             window against the pairs hit by a burst active in that window, and
             the fraction of pairs grouped in calm windows (false grouping).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import sbd_baselines as sbd  # noqa: E402

METHODS = ["dcw", "rmcat_sbd", "dc_sbd"]


def t_unit_of(run: d.Run) -> float:
    o = pd.read_csv(run.sender_file(run.subs[0], "owd"), usecols=["bin_mono_us"], nrows=50)
    return round(float(o.bin_mono_us.diff().median()) / 1e6, 3)


def sbd_file(run: d.Run, method: str, owd: str, t_unit: float) -> Path:
    step = "" if abs(t_unit - 0.005) < 1e-9 else f"-{t_unit * 1000:g}ms"
    return run.path / "baselines" / f"{method}-{owd}{step}.csv"


def windows_of(path: Path) -> list[tuple[float, dict[str, int]]]:
    df = pd.read_csv(path)
    return [(float(t), dict(zip(g.client, g.label))) for t, g in df.groupby("t_s", sort=True)]


def active_hits(truth: dict, t: float) -> list[set[str]]:
    return [set(b["hit"]) for b in truth["bursts"] if b["start"] <= t <= b["end"] + d.BURST_RECOVERY_S]


def prf(tp: int, fp: int, fn: int, tn: int) -> dict:
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None}


def score_final(same: dict[str, bool | None], truth: dict, key: str) -> dict:
    """same: pair -> True / False / None (undecided)."""
    tp = fp = fn = tn = unc = 0
    for p, s in same.items():
        if s is None:
            unc += 1
        elif s:
            tp += truth[key][p]
            fp += not truth[key][p]
        else:
            fn += truth[key][p]
            tn += not truth[key][p]
    out = prf(tp, fp, fn, tn)
    out.update({"uncertain": unc, "coverage": (tp + fp + fn + tn) / len(same) if same else None})
    return out


SUSTAIN_S = 5.0


def first_sustained(states: list[tuple[float, bool]], sustain_s: float = SUSTAIN_S) -> float | None:
    """First t at which the state is correct and every sample within the next
    sustain_s is too (a single lucky window does not count)."""
    ts = [t for t, _ in states]
    for i, (t, ok) in enumerate(states):
        if not ok:
            continue
        j = i
        while j < len(states) and ts[j] < t + sustain_s:
            if not states[j][1]:
                break
            j += 1
        else:
            return t
    return None


def score_sbd(windows: list[tuple[float, dict[str, int]]], truth: dict, pairs: list[str]) -> dict:
    first_burst = min((b["start"] for b in truth["bursts"]), default=d.BURST_WARMUP_S)
    grouped_burst = defaultdict(int)
    n_burst = n_calm = 0
    calm_grouped = 0
    w_tp = w_fp = w_fn = w_tn = 0
    correct = []
    for t, labels in windows:
        if t < first_burst:
            continue
        hits = active_hits(truth, t)
        same_now = {}
        for p in pairs:
            f, g = p.split("|")
            same_now[p] = f in labels and g in labels and labels[f] == labels[g]
        if hits:
            n_burst += 1
            for p in pairs:
                f, g = p.split("|")
                tr = any(f in h and g in h for h in hits)
                if same_now[p]:
                    grouped_burst[p] += 1
                    w_tp += tr
                    w_fp += not tr
                else:
                    w_fn += tr
                    w_tn += not tr
        else:
            n_calm += 1
            calm_grouped += sum(same_now.values())
        # Running belief: the majority rule over the burst windows seen so far
        # (an instantaneous grouping can never show two groups at once).
        correct.append((t, n_burst > 0 and all((grouped_burst[p] >= n_burst / 2) == truth["pairs_leaf"][p]
                                                for p in pairs)))
    final = {p: (grouped_burst[p] >= n_burst / 2) if n_burst else None for p in pairs}
    return {"final": {"vs_leaf": score_final(final, truth, "pairs_leaf"), "vs_link": score_final(final, truth, "pairs"),
                      "pairs": final},
            "t_correct": first_sustained(correct),
            "windows": {**prf(w_tp, w_fp, w_fn, w_tn), "n_burst": n_burst, "n_calm": n_calm,
                        "calm_grouped_fraction": calm_grouped / (n_calm * len(pairs)) if n_calm and pairs else None}}


def score_ecg(gdir: Path, truth: dict, pairs: list[str]) -> dict | None:
    m_path, pt_path = gdir / "metrics.json", gdir / "pairs_t.json"
    if not m_path.exists() or not pt_path.exists():
        return None
    m = json.loads(m_path.read_text())
    pairs_t = json.loads(pt_path.read_text())
    # ECG state holds between event closes; a close that stays correct through
    # every later close within SUSTAIN_S counts (the last close always does).
    t_correct = first_sustained([(e["t"], all((e["pairs"].get(p) == "SAME") == truth["pairs_leaf"][p] for p in pairs))
                                 for e in pairs_t])
    return {"final": {"vs_leaf": {k: m["pairwise"][k] for k in ("tp", "fp", "fn", "tn", "precision", "recall",
                                                                  "uncertain", "coverage")},
                      "vs_link": {k: m["pairwise_link"][k] for k in ("tp", "fp", "fn", "tn", "precision", "recall",
                                                                       "uncertain", "coverage")}},
            "t_correct": t_correct, "cases": m["cases"], "onset_source": m.get("onset_source", "shadow")}


def process(run_dir: Path, a) -> dict:
    run = d.Run(run_dir)
    truth = ga.truth_of(run)
    pairs = sorted(truth["pairs_leaf"])
    t_unit = t_unit_of(run)
    out = {"run": run_dir.name, "truth_source": truth["source"], "truth_leaf": truth["leaf"], "t_unit": t_unit,
           "methods": {}}
    for method in a.methods:
        f = sbd_file(run, method, a.owd, t_unit)
        if not f.exists():
            sbd.run_methods(run_dir, a.owd, t_unit, a.dcw_th, [method])
        out["methods"][method] = score_sbd(windows_of(f), truth, pairs)
    for g in a.ecg:
        r = score_ecg(run_dir / g, truth, pairs)
        if r is not None:
            out["methods"][f"ecg:{g}"] = r
    gdir = run_dir / "grouping"
    gdir.mkdir(exist_ok=True)
    (gdir / getattr(a, "out_name", "baselines.json")).write_text(json.dumps(out, indent=1))
    return out


def fmt(v) -> str:
    return "-" if v is None else f"{v:.2f}" if isinstance(v, float) else str(v)


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--methods", default=",".join(METHODS))
    ap.add_argument("--owd", choices=("oracle", "est"), default="oracle", help="baseline input (sbd_baselines.py)")
    ap.add_argument("--dcw-th", type=float, default=0.8)
    ap.add_argument("--ecg", default="grouping,grouping-owd,grouping-truth",
                    help="ECG output dirs under each run to put next to the baselines")
    a = ap.parse_args(argv)
    a.methods, a.ecg = a.methods.split(","), a.ecg.split(",")
    runs = [r for pat in a.runs for r in (sorted(Path().glob(str(pat))) if any(c in str(pat) for c in "*?[") else [pat])]
    rows = []
    for r in runs:
        if not (r / "events.csv").exists():
            print(f"skip {r}: not a run", file=sys.stderr)
            continue
        o = process(r, a)
        rows.append(o)
        print(f"{o['run']} (truth {o['truth_source']}, leaves {sorted(set(map(tuple, o['truth_leaf'].values())))})")
        for name, m in o["methods"].items():
            fl, fk = m["final"]["vs_leaf"], m["final"]["vs_link"]
            extra = f" windows P={fmt(m['windows']['precision'])} R={fmt(m['windows']['recall'])} " \
                    f"calm_grouped={fmt(m['windows']['calm_grouped_fraction'])}" if "windows" in m else \
                    f" cases={m['cases']}"
            print(f"  {name:22s} leaf P={fmt(fl['precision'])} R={fmt(fl['recall'])} cov={fmt(fl['coverage'])}"
                  f" | link P={fmt(fk['precision'])} R={fmt(fk['recall'])} | t_correct={fmt(m['t_correct'])}{extra}")
    if len(rows) > 1:
        names = sorted({n for o in rows for n in o["methods"]})
        print(f"\nmedian over {len(rows)} runs (final vs pairs_leaf):")
        for n in names:
            ms = [o["methods"][n] for o in rows if n in o["methods"]]
            P = [m["final"]["vs_leaf"]["precision"] for m in ms if m["final"]["vs_leaf"]["precision"] is not None]
            R = [m["final"]["vs_leaf"]["recall"] for m in ms if m["final"]["vs_leaf"]["recall"] is not None]
            T = [m["t_correct"] for m in ms if m["t_correct"] is not None]
            print(f"  {n:22s} P={fmt(statistics.median(P) if P else None)} R={fmt(statistics.median(R) if R else None)}"
                  f" t_correct={fmt(statistics.median(T) if T else None)} (reached in {len(T)}/{len(ms)}) n={len(ms)}")


if __name__ == "__main__":
    main(sys.argv[1:])
