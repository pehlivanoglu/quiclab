#!/usr/bin/env python3
"""Shadow v2 full report on one set of campaigns: every scenario x AQM, every truth, v2 / v2-fixed / BBR / gcc,
event statistics, and the RTT vs one-way-delay (OWD) comparison.

    python3 scripts/shadow_v2_report.py OUT_DIR .runs/<campaign> [...]   # -> OUT_DIR/report.md, cells.csv, events.csv

Detectors: v2 and v2-fixed as frozen (fusion d, hold, loss gate level+cap; scripts/shadow_v2_step3.py), gcc and BBR
from the replay (det_eval, no grouping). Fitted values are re-derived on these campaigns with the frozen rules,
nothing else changes: Step 2 floors (10 % of the median end-of-run EWMA sigma over pfifo-r1 flows), v2-fixed scale
(calm ticks of calm030 / calm065 pfifo-r1), G_ref (Step 3 rule, <= 0.1 FA / min at theta_on on those runs).
theta_on 0.25, theta_off 0.125 for T_clear.

Truths per client: GT1 (CoDel-style standing queue on a router egress of the client's path), GT2 (demand >=
capacity on such an egress), GT3 + path (the client's own one-way delay / loss impact while a GT1 or GT2 queue is
on its path; main truth). Scoring: gt_score (TP = first alarm start in [t_on - 1 s, min(end, t_on + 10 s)];
AMBIGUOUS / NO_DATA ignored; other alarm starts in CLEAR time are false alarms). Repeats are pooled per cell.

OWD mode (scripts/owd_mode.py): the per-ACK RTT is replaced by the packet's one-way delay (receiver timestamps
carried in ACKs) + R0, so reverse-path delay leaves the delay features. v2 / v2-fixed get OWD tick files
(<run>/shadow-v2/ticks-owd, own floors / scale / G_ref by the same rules). RTT and OWD rows are both scored
against GT3 source B (client frame log), which does not share the ACK receive timestamps with the OWD mode.
"""

from __future__ import annotations

import math
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import owd_mode  # noqa: E402
import shadow_v2_results as res_mod  # noqa: E402
import shadow_v2_step1 as s1  # noqa: E402
import shadow_v2_step2 as s2  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402
import shadow_v2_step5 as s5  # noqa: E402

V2 = {"v2": "fuse d: s1+s2+s3+sL +hold gate:level+cap", "v2-fixed": "fuse d fixed +hold gate:level+cap"}
MODES = {"RTT": "ticks", "OWD": "ticks-owd"}
TRUTHS = ("GT1", "GT2", "GT3")
DETS = ("v2", "v2-fixed", "bbr", "gcc")
OWD_ROWS = ("v2 RTT", "v2 OWD", "v2-fixed RTT", "v2-fixed OWD", "gcc RTT", "gcc OWD")
THETA = s3.THETA_ON
FIT: dict[str, dict] = {}  # mode -> {"floors", "stats", "g_ref"} (set before the pool forks)


def use(mode: str) -> None:
    s3.TICKS_DIR = MODES[mode]
    s3.FLOORS.clear()
    s3.FLOORS.update(FIT[mode]["floors"])
    s3.FIXED_STATS.clear()
    s3.FIXED_STATS.update(FIT[mode]["stats"])


# ── preparation ──────────────────────────────────────────────────────────

def prepare(run_dir: Path) -> str:
    """RTT tick files (with the causal-normaliser columns) and OWD tick files for one run."""
    run = d.Run(run_dir)
    first = run_dir / "shadow-v2" / "ticks" / f"{run.subs[0]}.csv"
    if not first.exists() or "d0" not in pd.read_csv(first, nrows=0).columns:
        s1.worker(run_dir)
    if not (run_dir / "shadow-v2" / "ticks-owd" / f"{run.subs[-1]}.csv").exists():
        dump = run_dir / "shadow-v2" / "v1-samples-owd"
        with tempfile.TemporaryDirectory() as tmp:
            acks = {s: owd_mode.owd_acks(run, s, Path(tmp)) for s in run.subs}
            d.replay(run, d.TUNED, samples_to=dump, acks=acks, grouping="none")
        s1.worker(run_dir, dump=dump, out_name="ticks-owd")
    return run_dir.name


def floors_for(pfifo_r1: list[Path]) -> dict[str, float]:
    """Step 2 rule: 10 % of the median end-of-run EWMA sigma (no floor, calm ticks) over pfifo-r1 flows."""
    sig = defaultdict(list)
    for rd in pfifo_r1:
        for df in s3.load_flows(rd).values():
            calm = df.calm.to_numpy(bool)
            for f in ("F1", "F2", "F3", "F4"):
                v = s2.causal_z(df[f].to_numpy(dtype=float), calm, "ewma", s3.T, 0.0)[3]
                if np.isfinite(v) and v > 0:
                    sig[f].append(v)
    return {f: 0.1 * float(np.median(v)) for f, v in sig.items()}


def fit_one(args):
    mode, label, calm_dirs = args
    use(mode)
    return (mode, label), res_mod.fit_g_ref(V2[label], calm_dirs)


# ── per run ──────────────────────────────────────────────────────────────

def spans_to_starts(spans):
    return [a for a, _, _ in spans]


def worker(run_dir: Path) -> dict:
    run = d.Run(run_dir)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params())
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    views = {"GT1": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             "GT2": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2),
             "GT3": gt3.view_of(run, e3, l3, need_path=True)}
    view_b = gt3.view_of(run, eb, lb, need_path=True)
    starts = {}
    for mode in MODES:
        use(mode)
        for label, feat in V2.items():
            for s, df in s3.load_flows(run_dir).items():
                r = s3.run_cusum(df, feat, FIT[mode]["g_ref"][label], False)
                starts[(f"{label} {mode}", s)] = spans_to_starts(s5.on_spans(r, THETA))
    rtt = gt_score.alarm_starts(run, ("gcc", "bbr"), grouping="none")
    with tempfile.TemporaryDirectory() as tmp:
        acks = {s: owd_mode.owd_acks(run, s, Path(tmp)) for s in run.subs}
        owd = gt_score.alarm_starts(run, ("gcc",), acks=acks, grouping="none")
    for (det, s), v in rtt.items():
        starts[(f"{det} RTT" if det == "gcc" else det, s)] = v
    for (det, s), v in owd.items():
        starts[(f"{det} OWD", s)] = v
    main = {"v2": "v2 RTT", "v2-fixed": "v2-fixed RTT", "bbr": "bbr", "gcc": "gcc RTT"}
    keyed = {(name, s): starts.get((src, s), []) for name, src in main.items() for s in run.subs}
    score = {t: gt_score.score(run, v, keyed, DETS) for t, v in views.items()}
    owd_score = gt_score.score(run, view_b, starts, OWD_ROWS)
    # events after the warm-up: GT1 / GT2 per router egress, GT3 per client
    ev = {"GT1": [e["end_s"] - e["start_s"] for e in e1 if e["start_s"] >= d.WARMUP_S],
          "GT2": [e["t_end"] - e["t_on"] for e in e2 if e["t_on"] >= d.WARMUP_S],
          "GT3": [b - a for s, (eps, _) in views["GT3"].items() for a, b in eps if a >= d.WARMUP_S]}
    return {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir), "topo": run_dir.parent.name.split("_det-")[-1],
            "rep": run_dir.name.rsplit("-", 1)[-1], "clients": len(run.subs), "dur_min": (run.duration - d.WARMUP_S) / 60,
            "score": score, "owd": owd_score, "ev": ev}


# ── report ───────────────────────────────────────────────────────────────

def _f(x, k=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    run_dirs = sorted(r for c in argv[1:] for r in Path(c).iterdir() if (r / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        list(pool.map(prepare, run_dirs))
    pfifo_r1 = [r for r in run_dirs if r.name.endswith("-pfifo-r1")]
    calm_dirs = [r for r in pfifo_r1 if r.name.split("-")[1] in s3.CALM_RUNS]
    for mode, tick_dir in MODES.items():
        s3.TICKS_DIR = tick_dir
        floors = floors_for(pfifo_r1)
        s3.FLOORS.clear(); s3.FLOORS.update(floors)
        FIT[mode] = {"floors": floors, "stats": s3.fixed_stats(calm_dirs), "g_ref": {}}
    with ProcessPoolExecutor(max_workers=12) as pool:
        for (mode, label), g in pool.map(fit_one, [(m, lab, calm_dirs) for m in MODES for lab in V2]):
            FIT[mode]["g_ref"][label] = g
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, run_dirs))
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=s3.ROOT, capture_output=True, text=True).stdout.strip()

    def pooled(rs, truth, det, key="score"):
        return gt_score.summarize([r[key][truth][det] for r in rs] if key == "score" else [r["owd"][det] for r in rs])

    cells = defaultdict(list)
    for r in res:
        cells[(r["topo"], r["scn"], r["aqm"])].append(r)
    rows = []
    for (topo, scn, aqm), rs in sorted(cells.items()):
        for truth in TRUTHS:
            for det in DETS:
                s = pooled(rs, truth, det)
                rows.append({"topology": topo, "scenario": scn, "aqm": aqm, "runs": len(rs), "truth": truth, "detector": det,
                             "episodes": s["episodes"], "precision": s["precision"], "recall": s["recall"], "fa_per_min": s["fa_per_min"],
                             "latency_p50_ms": s["late_latency_p50_ms"], "latency_p90_ms": s["latency_p90_ms"], "tp": s["tp"], "fp": s["fp"]})
        for det in OWD_ROWS:
            s = pooled(rs, None, det, key="owd")
            rows.append({"topology": topo, "scenario": scn, "aqm": aqm, "runs": len(rs), "truth": "GT3 (B) owd-cmp", "detector": det,
                         "episodes": s["episodes"], "precision": s["precision"], "recall": s["recall"], "fa_per_min": s["fa_per_min"],
                         "latency_p50_ms": s["late_latency_p50_ms"], "latency_p90_ms": s["latency_p90_ms"], "tp": s["tp"], "fp": s["fp"]})
    cdf = pd.DataFrame(rows)
    cdf.to_csv(out / "cells.csv", index=False)
    erows = []
    for (topo, scn, aqm), rs in sorted(cells.items()):
        row = {"topology": topo, "scenario": scn, "aqm": aqm, "runs": len(rs), "clients": rs[0]["clients"],
               "minutes_per_run": round(float(np.mean([r["dur_min"] for r in rs])), 2)}
        for t in TRUTHS:
            v = [x for r in rs for x in r["ev"][t]]
            row[f"{t}_per_run"] = len(v) / len(rs)
            row[f"{t}_dur_p50_s"] = float(np.median(v)) if v else float("nan")
            row[f"{t}_dur_p90_s"] = float(np.percentile(v, 90)) if v else float("nan")
            row[f"{t}_total_s_per_run"] = sum(v) / len(rs)
        erows.append(row)
    edf = pd.DataFrame(erows)
    edf.to_csv(out / "events.csv", index=False)
    L = ["# Shadow v2 report", "", f"{len(res)} runs, campaigns {', '.join(Path(c).name for c in argv[1:])}; git {git}.", "",
         "## Fitted values (frozen rules, re-derived on these campaigns)", ""]
    for mode, f in FIT.items():
        L.append(f"- {mode}: floors " + ", ".join(f"{k} {v:.4g}" for k, v in f["floors"].items()) + "; G_ref "
                 + ", ".join(f"{k} {v:.1f}" for k, v in f["g_ref"].items()) + "; v2-fixed scale "
                 + ", ".join(f"{k} mu {m:.4g} sigma {sg:.4g}" for k, (m, sg) in f["stats"].items()))
    L += ["", "## Overall (all runs pooled)", ""]
    orow = []
    for truth in TRUTHS:
        for det in DETS:
            s = pooled(res, truth, det)
            orow.append([truth, det, s["episodes"], _f(s["precision"]), _f(s["recall"]), _f(s["fa_per_min"]),
                         _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0)])
    for det in OWD_ROWS:
        s = pooled(res, None, det, key="owd")
        orow.append(["GT3 (B) owd-cmp", det, s["episodes"], _f(s["precision"]), _f(s["recall"]), _f(s["fa_per_min"]),
                     _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0)])
    L += [s3.s1.table(["truth", "detector", "episodes", "precision", "recall", "FA / min", "latency p50 (ms)", "p90 (ms)"], orow), ""]
    (out / "report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
