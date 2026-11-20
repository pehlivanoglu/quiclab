#!/usr/bin/env python3
"""D1 (user, 2026-11-19): GT-L headline numbers under the old window (gt_score.py, 10 s after onset) and the new one
(gt_score_v2.py, 2 s), frozen detector v2-owd, GT-L = GT3 source B (as reports/v3-detector and R2), side by side.

    rows   --set v3|k1 [--only RUN,...] [--jobs 2]   -> <set>/rows.jsonl
    report                                          -> d1-report.md

Runs: v3 = every v3 run (reports/v3-detector's set); k1 = the K1 default cells (every "-def-" cell, seeds 1-5).
Read through a link farm (k5_contrib.farm): tick files are built in the farm, never in a run folder; K1 runs whose
frozen tick files already exist in reports/npr-step0-2026-11-17/cache are linked from there (read only). Run folders
are checked unchanged (file list, sizes, mtimes). Detector, GT-L labels and both scorers are used unchanged.
Check in every run: gt_score_v2.score with search_s = 10 equals gt_score.score (the new code is the old rule).
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
K5C = ROOT / "reports" / "k5-contrib-2026-11-19"
sys.path[:0] = [str(K5C), str(ROOT / "reports" / "detector-r2-2026-11-16"), str(ROOT / "scripts"),
                str(ROOT / "reports" / "v3-detector"), str(ROOT)]

V3 = ROOT / ".runs" / "2026-11-14_1818_v3"
K1 = ROOT / ".runs" / "2026-11-16_0105_v4-K1"
NPR0_CACHE = ROOT / "reports" / "npr-step0-2026-11-17" / "cache"
DET = "v2-owd"


def runs_of(kind, only):
    if kind == "v3":
        rs = sorted(p for p in V3.iterdir() if p.is_dir() and p.name.startswith("v3-") and (p / "events.csv").exists())
    else:
        rs = sorted(p for p in K1.iterdir() if p.is_dir() and "-def-" in p.name and (p / "v3-checks.json").exists())
    return [p for p in rs if not only or p.name in only]


def worker(args):
    try:
        return _worker(*args)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {"run": args[0].name, "error": repr(ex), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path, kind: str):
    import det_eval as d
    import gt3
    import gt_score
    import gt_score_v2 as v2
    import k5_contrib as K
    import r2
    import score_runs as sr
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    before = K.folder_state(rd)
    fd = K.farm(rd, HERE / kind / "farm")
    if not (fd / "shadow-v2").exists() and not (fd / "shadow-v2").is_symlink():
        c = NPR0_CACHE / rd.parent.name / rd.name / "shadow-v2"
        subs = list(d.Run(fd).subs)
        if all((c / "ticks-frozen-owd" / f"{s}.csv").exists() for s in subs):
            os.symlink(c, fd / "shadow-v2")
    r2._setup()
    run = d.Run(fd)
    spans, starts = {}, {}
    for s, df in r2.flows(run).items():
        r = s3.run_cusum(df, r2.FROZEN_LABEL, fz.FROZEN["OWD"]["g_ref"]["v2"], False)
        spans[(DET, s)] = [(a, b) for a, b, _ in s5.on_spans(r, s3.THETA_ON)]
        starts[(DET, s)] = [a for a, _ in spans[(DET, s)]]
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    view = gt3.view_of(run, eb, lb, need_path=True)
    old = gt_score.score(run, view, starts, (DET,))[DET]
    old.update(sr.alarm_on(view, spans, DET))
    new = v2.score(run, view, starts, (DET,))[DET]
    new.update(v2.alarm_on(view, spans, DET))
    chk = v2.score(run, view, starts, (DET,), search_s=d.SEARCH_S)[DET]
    chk.update(v2.alarm_on(view, spans, DET, search_s=d.SEARCH_S))
    if json.dumps(chk, sort_keys=True) != json.dumps(old, sort_keys=True):
        raise RuntimeError("gt_score_v2 with search_s = 10 differs from gt_score")
    if K.folder_state(rd) != before:
        raise RuntimeError(f"run folder changed: {rd}")
    p = rd.name.split("-")
    return {"run": rd.name, "set": kind, "block": p[1], "type": p[2], "aqm": p[4], "rep": int(p[5][1:]),
            "old": old, "new": new, "v2_equals_v1_at_10s": True}


def cmd_rows(kind, jobs, only):
    (HERE / kind).mkdir(parents=True, exist_ok=True)
    out = HERE / kind / "rows.jsonl"
    done = set()
    if out.exists():
        good = [x for x in out.read_text().splitlines() if x.strip().endswith("}") and '"error"' not in x]
        done = {json.loads(x)["run"] for x in good}
        out.write_text("".join(x + "\n" for x in good))
    rs = [p for p in runs_of(kind, only) if p.name not in done]
    print(f"{len(rs)} runs ({len(done)} done)", flush=True)
    with out.open("a") as fh, Pool(jobs) as pool:
        for i, r in enumerate(pool.imap_unordered(worker, [(p, kind) for p in rs]), 1):
            fh.write(json.dumps(r, default=lambda o: None if isinstance(o, float) and not math.isfinite(o) else str(o)) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {r['run']}{' ERROR ' + r['error'] if 'error' in r else ''}", flush=True)
    return 0


def agg(rows, ver):
    tp = fp = ep = on = 0
    clear = 0.0
    lat = []
    for r in rows:
        s = r[ver]
        tp, fp, ep, on = tp + s["tp"], fp + s["fp"], ep + s["episodes"], on + s["alarm_on"]
        clear += s["clear_s"]
        lat += s["latency"]
    q = lambda p: float(np.percentile(lat, p)) * 1000 if lat else None   # noqa: E731
    return {"P": tp / (tp + fp) if tp + fp else None, "R": tp / ep if ep else None, "on": on / ep if ep else None,
            "fa": fp / (clear / 60) if clear else None, "p50": q(50), "p90": q(90), "ep": ep, "tp": tp}


def f_(x, d=3):
    return "-" if x is None else f"{x:.{d}f}"


def cmd_report():
    L = ["# D1: GT-L window 10 s (old, gt_score.py) against 2 s (new, gt_score_v2.py), frozen v2-owd\n",
         "Only the matching window's end changes (min(t_end, t_on + 10 s) -> min(t_end, t_on + 2 s)); 1 s lead, "
         "labels, detector unchanged. FA / min: alarm starts in CLEAR time per minute of CLEAR time (a start that "
         "falls out of the shorter window is inside the episode and stays ignored, so FA / min cannot change). "
         "Delay: latency of detected episodes, clipped at 0 (as today). Per AQM, seeds side by side; old / new "
         "(new - old).\n"]
    bad = []
    for kind, title in (("v3", "v3 detector blocks (all v3 runs)"), ("k1", "K1 default cells (-def-)")):
        f = HERE / kind / "rows.jsonl"
        if not f.exists():
            continue
        R = [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
        bad += [r for r in R if "error" in r]
        R = [r for r in R if "error" not in r]
        reps = sorted({r["rep"] for r in R})
        L.append(f"## {title}: {len(R)} runs, seeds {reps}\n")
        L.append("| AQM | seed | episodes | P old / new (diff) | onset R | alarm-on R | FA / min | delay p50 ms | "
                 "delay p90 ms |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for aqm in sorted({r["aqm"] for r in R}) + ["all"]:
            for rep in reps:
                sel = [r for r in R if r["rep"] == rep and (aqm == "all" or r["aqm"] == aqm)]
                if not sel:
                    continue
                o, n = agg(sel, "old"), agg(sel, "new")

                def c(k, d=3):
                    if o[k] is None or n[k] is None:
                        return f"{f_(o[k], d)} / {f_(n[k], d)}"
                    return f"{f_(o[k], d)} / {f_(n[k], d)} ({n[k] - o[k]:+.{d}f})"
                L.append(f"| {aqm} | r{rep} | {o['ep']} | {c('P')} | {c('R')} | {c('on')} | {c('fa')} | "
                         f"{c('p50', 0)} | {c('p90', 0)} |")
        L.append("")
    if bad:
        L.append(f"Errors: {[(b['run'], b['error']) for b in bad]}\n")
    (HERE / "d1-report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def main(argv):
    if argv[:1] == ["rows"]:
        return cmd_rows(argv[argv.index("--set") + 1], int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2,
                        set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None)
    if argv[:1] == ["report"]:
        return cmd_report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
