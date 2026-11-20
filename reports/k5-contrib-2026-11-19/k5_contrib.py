#!/usr/bin/env python3
"""K5 per-signal contribution (user, 2026-11-19), with R2's definitions and code reused unchanged.

    rows   --set check|ref|k5|v3 [--only RUN[,RUN]] [--jobs 2] [--k5 <K5 folder>]   -> <set>/rows.jsonl
    check  R2 reproduction: rows of --set check against reports/detector-r2-2026-11-16/rows.jsonl
    report -> report.md, figure.csv

Sets:
  check  three v3 runs that R2 scored (BBR pfifo, BBR codel, Copa pfifo): every detector's GT3 / GT-Q / harm score and
         the frozen detector's contribution must equal R2's rows (the net share per signal is R2's share).
  ref    reference cells at 1000 ms without adaptation: K1 A2 (S-BURST, BBR, pfifo / codel / pie / red, seeds 1-5), K1
         A4 (H-HIERL, BBR, pfifo / codel / pie, seeds 1-5), K3 C1 Copa S-BURST and H-HIERL (pfifo / codel).
  k5     every finished K5 run except the gate.
  v3     R2's v3 runs, frozen detector only: the signed contribution (positive / negative per signal), which R2 did
         not store; R2's own rows give the rest of the v3 column.

Reused unchanged: r2.py (_setup, flows, cusum, ABL, contribution, on_at_harm), r2_report.agg, score_runs.alarm_on,
gt1 / gt2 / gt3 / gt_score / gtq / gtq_score. Detectors: frozen v2-owd and R2's ablation rows (G_ref from R2's
gref.json). No "no-F1" row: R2 has none; it would be a new variant needing its own G_ref fit (user decision).

Nothing is written in a run folder. Each run is read through a link farm under <set>/farm/<campaign>/<run>: one
symlink per top-level entry of the run, except truth/ (a real directory of symlinks to the run's truth files) and
shadow-v2/ when the run has none. The frozen tick files and GT-Q / GT-H truth (gtq.score, default parameters, as
reports/v3-detector/score_runs.py did for v3) are therefore written in the farm. The run folder's file list, sizes
and mtimes are compared before and after; any change raises an error.
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R2DIR = ROOT / "reports" / "detector-r2-2026-11-16"
sys.path[:0] = [str(R2DIR), str(ROOT / "scripts"), str(ROOT / "reports" / "v3-detector"), str(ROOT)]

V3 = ROOT / ".runs" / "2026-11-14_1818_v3"
K1 = ROOT / ".runs" / "2026-11-16_0105_v4-K1"
K3 = ROOT / ".runs" / "2026-11-16_0105_v4-K3"
CHECK_RUNS = ("v3-C2-sburst-s030u070-pfifo-r1", "v3-C2-sburst-s030u070-codel-r2", "v3-M13-sburst-copa-pfifo-r1")
FEATS = ("F1", "F2", "F3", "loss")
LEAD_WINDOW = 300   # R2: first signal within 300 ticks after a GT3 onset


# ---------------------------------------------------------------------------------------------------------- runs

def runs_of(kind, only=None, k5=None):
    if kind == "check":
        rs = [V3 / r for r in CHECK_RUNS]
    elif kind == "v3":
        import r2
        rs = r2.runs()
    elif kind == "ref":
        rs = sorted(p for p in K1.glob("v4-A2-sburst-def-*-r*") if p.name.split("-")[4] in ("pfifo", "codel", "pie", "red"))
        rs += sorted(p for p in K1.glob("v4-A4-hhier-def-*-r*") if p.name.split("-")[4] in ("pfifo", "codel", "pie"))
        rs += sorted(p for p in K3.glob("v4-C1-*-copa-*-r*") if any(f"-{t}-copa-" in p.name for t in ("sburst", "hhier"))
                     and p.name.split("-")[4] in ("pfifo", "codel"))
    else:
        assert k5, "--k5 <K5 campaign folder>"
        rs = sorted(p for p in Path(k5).iterdir() if p.is_dir() and p.name.startswith("v4-") and "-GATE-" not in p.name)
    rs = [p for p in rs if (p / "v3-checks.json").exists()]
    if only:
        rs = [p for p in rs if p.name in only]
    return rs


def folder_state(rd: Path) -> dict:
    return {str(p.relative_to(rd)): (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(rd.rglob("*")) if p.is_file()}


def farm(rd: Path, base: Path) -> Path:
    f = base / rd.parent.name / rd.name
    f.mkdir(parents=True, exist_ok=True)
    for e in rd.iterdir():
        dst = f / e.name
        if e.name == "truth":
            dst.mkdir(exist_ok=True)
            for t in e.iterdir():
                if not (dst / t.name).exists() and not (dst / t.name).is_symlink():
                    os.symlink(t, dst / t.name)
        elif not dst.exists() and not dst.is_symlink():
            os.symlink(e, dst)
    return f


# ---------------------------------------------------------------------------------------------------------- per run

def signed_contribution(r):
    """R2's contribution() loop (same excursion, same hold exclusion, loss = step - fused), with each tick's
    per-signal value added to a positive or a negative sum instead of one net sum."""
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    t, G, sf = np.asarray(r["t"]), np.asarray(r["G"]), r["s_f"]
    feats = ("F1", "F2", "F3")
    out = []
    for a, _, _ in s5.on_spans(r, s3.THETA_ON):
        k1 = int(np.searchsorted(t, a))
        zero = np.flatnonzero(G[:k1] == 0)
        k0 = int(zero[-1]) if len(zero) else 0
        pos, neg = dict.fromkeys(FEATS, 0.0), dict.fromkeys(FEATS, 0.0)
        for k in range(k0 + 1, k1 + 1):
            step = G[k] - G[k - 1]
            fused = sum(np.nan_to_num(sf[f][k]) for f in feats)
            if step == 0 and fused < 0:
                continue
            vals = {f: float(np.nan_to_num(sf[f][k])) for f in feats}
            vals["loss"] = float(step - fused)
            for f, v in vals.items():
                if v >= 0:
                    pos[f] += v
                else:
                    neg[f] += v
        g = float(G[k1]) if k1 < len(G) else float("nan")
        f3z = float(np.nan_to_num(sf["F3"][k1], nan=np.nan)) / 2 + 1 if k1 < len(G) else None
        out.append({"t": float(a), "G": g, "pos": pos, "neg": neg, "f3_zc_at_alarm": f3z})
    return out


def sender(run, s):
    """Sender drops (drops.csv: GOP-aware head drop, R2 send_queue.py) and adaptation (adapt.csv), run time in s."""
    import pandas as pd
    out = {"drops": [], "drop_bytes": 0, "prod_bytes": 0, "adapt": None}
    dr_f, fr_f, ad_f = run.sender_file(s, "drops"), run.sender_file(s, "frames"), run.sender_file(s, "adapt")
    if dr_f.exists():
        dr = pd.read_csv(dr_f)
        if len(dr):
            out["drops"] = [run.t_unix_us(float(x)) for x in dr.groupby("gop")["t_us"].min().sort_values()]
            out["drop_bytes"] = int(dr["size"].sum())
        fr = pd.read_csv(fr_f, usecols=["size"]) if fr_f.exists() else None
        out["prod_bytes"] = int((fr["size"].sum() if fr is not None else 0) + out["drop_bytes"])
    if ad_f.exists():
        ad = pd.read_csv(ad_f)
        out["adapt"] = {"t": [run.t_unix_us(float(x)) for x in ad["t_us"]], "scale": [float(x) for x in ad["scale"]]}
    return out


def worker(args):
    rd, kind = args
    try:
        return _worker(rd, kind)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(ex), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path, kind: str) -> dict:
    import yaml

    import det_eval as d
    import gt1
    import gt2
    import gt3
    import gt_score
    import gtq
    import gtq_score
    import r2
    import score_runs as sr
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    before = folder_state(rd)
    fd = farm(rd, HERE / kind / "farm")
    r2._setup()
    gref = json.loads(r2.GREF_FILE.read_text())
    run = d.Run(fd)
    plan = json.loads((fd / "v3-plan.json").read_text())
    fl = r2.flows(run)
    frozen_only = kind == "v3"
    spans = defaultdict(dict)
    frozen = {}
    for s, df in fl.items():
        r = s3.run_cusum(df, r2.FROZEN_LABEL, fz.FROZEN["OWD"]["g_ref"]["v2"], False)
        frozen[s] = r
        spans["v2-owd"][s] = [(a, b) for a, b, _ in s5.on_spans(r, s3.THETA_ON)]
        if not frozen_only:
            for name, (_f, _k, _c, _h, masks) in r2.ABL.items():
                spans[name][s] = [(a, b) for a, b, _ in
                                  s5.on_spans(r2.cusum(df, name, gref[name]["g_ref"], masks), s3.THETA_ON)]
    names = tuple(spans)
    starts = {(n, s): [a for a, _ in v] for n, per in spans.items() for s, v in per.items()}
    sp2 = {(n, s): v for n, per in spans.items() for s, v in per.items()}
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    v3view = gt3.view_of(run, eb, lb, need_path=True)
    out = {"run": rd.name, "campaign": rd.parent.name, "set": kind}
    if not frozen_only:
        e1, l1 = gt1.run_truth(run, gt1.Params())
        e2, l2 = gt2.run_truth(run, gt2.Params())
        hop1 = [(e["hop"], e["start_s"], e["end_s"]) for e in e1]
        hop2 = [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2]
        views = {"GT1": gt_score.client_view(run, hop1, l1), "GT2": gt_score.client_view(run, hop2, l2), "GT3": v3view}
        score = {}
        for tname, v in views.items():
            sc = gt_score.score(run, v, starts, names)
            for n in names:
                sc[n].update(sr.alarm_on(v, sp2, n))
            score[tname] = sc
        import gt_score_v2 as v2                          # D1 (user 2026-11-19): GT-L window 2 s, next to 10 s
        sc2 = v2.score(run, views["GT3"], starts, names)
        for n in names:
            sc2[n].update(v2.alarm_on(views["GT3"], sp2, n))
        out["score_v2"] = {"GT3": sc2}
        if not (fd / "truth" / "gtq.csv").exists() and not (fd / "truth" / "gtq-status.csv").exists():
            gtq.score(fd)                                 # writes fd/truth (the farm's real directory)
        gq = None
        if (fd / "truth" / "gtq.csv").exists():
            gtq_score.DETECTORS = names
            keep = gtq.write
            gtq.write = lambda *a, **k: None              # as r2.py: score_run would write gtq-score-episodes.csv
            try:
                res = gtq_score.score_run(fd, starts)
            finally:
                gtq.write = keep
            gq = res[1] if res is not None else None
        out.update(score=score, gtq=gq, harm=r2.on_at_harm(run, fd, sp2, names),
                   gtq_status=(d.rows(fd / "truth" / "gtq-status.csv")[0]
                               if (fd / "truth" / "gtq-status.csv").exists() else None))
    g3 = {s: [a for a, _ in eps] for s, (eps, _) in v3view.items()}
    out["contrib"] = {s: r2.contribution(run, s, r, [a for a in g3.get(s, []) if a >= d.WARMUP_S])
                      for s, r in frozen.items()}
    out["signed"] = {s: signed_contribution(r) for s, r in frozen.items()}
    out["alarm_spans"] = {s: spans["v2-owd"][s] for s in frozen}
    if not frozen_only:
        out["sender"] = {s: sender(run, s) for s in run.subs if s != "sub-ctrl"}
        topo = yaml.safe_load((fd / "topology.yaml").read_text())
        pub = next(iter(topo["publishers"].values()))
        cc = {s: v.get("cc") or v.get("congestion_control") for s, v in topo.get("subscribers", {}).items()}
        out.update(block=plan.get("block"), type=plan.get("type"), variant=plan.get("variant"), aqm=plan.get("aqm"),
                   rep=plan.get("rep"), topology=plan.get("topology"),
                   cc="copa" if "copa" in rd.name else "bbr",
                   send_buffer_ms=pub.get("send_buffer_ms", 1000), adapt=bool(pub.get("adapt_x")),
                   adapt_x=pub.get("adapt_x"), adapt_floor=pub.get("adapt_floor"), sub_cc=cc,
                   duration_s=run.duration)
    if folder_state(rd) != before:
        raise RuntimeError(f"run folder changed: {rd}")
    out["run_folder_unchanged"] = True
    return out


def cmd_rows(kind, jobs, only, k5):
    rs = runs_of(kind, only, k5)
    (HERE / kind).mkdir(parents=True, exist_ok=True)
    rows = HERE / kind / "rows.jsonl"
    done = set()
    if rows.exists():
        good = [x for x in rows.read_text().splitlines() if x.strip().endswith("}") and '"error"' not in x]
        done = {json.loads(x)["run"] for x in good}
        rows.write_text("".join(x + "\n" for x in good))
    rs = [r for r in rs if r.name not in done]
    print(f"{len(rs)} runs ({len(done)} done)", flush=True)
    enc = lambda o: None if isinstance(o, float) and not math.isfinite(o) else (  # noqa: E731
        o.tolist() if hasattr(o, "tolist") else str(o))
    with rows.open("a") as fh, Pool(jobs) as pool:
        for i, r in enumerate(pool.imap_unordered(worker, [(p, kind) for p in rs]), 1):
            fh.write(json.dumps(r, default=enc) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {r['run']}{' ERROR ' + r['error'] if 'error' in r else ''}", flush=True)
    return 0


# ---------------------------------------------------------------------------------------------------------- check

def cmd_check():
    """R2 reproduction on CHECK_RUNS: scores of every detector (GT1 / GT2 / GT3), GT-Q tallies, harm, the frozen
    detector's contribution (alarms and onsets); and positive + negative = R2's net share for every alarm."""
    mine = {r["run"]: r for r in map(json.loads, (HERE / "check" / "rows.jsonl").read_text().splitlines()) if "error" not in r}
    ref = {}
    for x in (R2DIR / "rows.jsonl").open():
        if any(f'"run": "{r}"' in x for r in CHECK_RUNS):
            d = json.loads(x)
            ref[d["run"]] = d
    bad, n = [], 0
    for run in CHECK_RUNS:
        a, b = mine.get(run), ref.get(run)
        if a is None or b is None:
            bad.append(f"{run}: missing ({'mine' if a is None else 'R2'})")
            continue
        for t in ("GT1", "GT2", "GT3"):
            for det, s in a["score"][t].items():
                n += 1
                if json.loads(json.dumps(s)) != b["score"][t].get(det):
                    bad.append(f"{run} {t} {det}: score differs")
        n += 1
        mg = [x for x in (a["gtq"] or []) if x["detector"] in a["score"]["GT3"]]
        rg = [x for x in (b["gtq"] or []) if x["detector"] in a["score"]["GT3"]]
        if mg != rg:
            bad.append(f"{run}: GT-Q tallies differ")
        for det in a["harm"]:
            n += 1
            if a["harm"][det] != b["harm"].get(det):
                bad.append(f"{run} harm {det} differs")
        n += 1
        if json.loads(json.dumps(a["contrib"])) != b["contrib"]:
            bad.append(f"{run}: contribution differs from R2")
        for s, al in a["signed"].items():
            for x, y in zip(al, a["contrib"][s]["alarms"]):
                n += 1
                for f in FEATS:
                    net = (x["pos"][f] + x["neg"][f]) / x["G"] if x["G"] else None
                    if (net is None) != (y[f] is None) or (net is not None and abs(net - y[f]) > 1e-9):
                        bad.append(f"{run} {s} alarm {x['t']:.2f} {f}: pos+neg {net} != R2 {y[f]}")
    print(f"R2 reproduction: {len(CHECK_RUNS)} runs, {n} comparisons, {len(bad)} differences")
    for b in bad[:40]:
        print("  " + b)
    return 1 if bad else 0


# ---------------------------------------------------------------------------------------------------------- report
# (written after the reproduction check is accepted; see README.md for the planned tables)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "rows":
        kind = argv[argv.index("--set") + 1]
        only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2
        k5 = argv[argv.index("--k5") + 1] if "--k5" in argv else None
        return cmd_rows(kind, jobs, only, k5)
    if argv[0] == "check":
        return cmd_check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
