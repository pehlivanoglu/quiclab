#!/usr/bin/env python3
"""GT3 with a longer persistence window: truth-only checks first, then detector scores.

    python3 scripts/gt3_window_check.py OUT.md .runs/<campaign> [...]
"""

from __future__ import annotations

import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt3  # noqa: E402
import gt3_report  # noqa: E402
import gt_score  # noqa: E402

P = gt3.Params()
VARIANTS = {"P_min 150 ms (spec)": replace(P, p_min=0.15, p_off=0.15), "P_min 400 ms": replace(P, p_min=0.4, p_off=0.15), "P_min 500 ms": replace(P, p_min=0.5, p_off=0.15),
            "P_min 500 ms + P_off 500 ms": replace(P, p_min=0.5, p_off=0.5)}
NEG = ("calm030", "calm065", "randloss", "delaystep")
DETS = ("shadow", "gcc", "bbr")


def worker(run_dir: Path) -> dict:
    run = det_eval.Run(run_dir)
    starts = gt_score.alarm_starts(run, DETS)
    out = {"name": run.path.name, "aqm": run.aqm, "scn": det_eval.scenario_name(run.path), "v": {}}
    cur = gt3.current(run)
    out["v"]["old (det_eval, 0.5 s forward min, 2 s merge)"] = {
        "n": sum(len(x) for x in cur[0].values()),
        "short": sum(1 for x in cur[0].values() for a, b in x if b - a < 0.5),
        "events": gt3_report.events_per_client(run, [{"flow": s, "t_on": a, "t_end": b} for s, x in cur[0].items() for a, b in x]),
        "score": gt_score.score(run, gt3.as_view(run, cur), starts, DETS)}
    for name, p in VARIANTS.items():
        eps, labels = gt3.run_truth(run, p, path_queues=False)
        out["v"][name] = {"n": len(eps), "short": sum(1 for e in eps if e["duration"] < 0.5),
                          "events": gt3_report.events_per_client(run, eps),
                          "score": gt_score.score(run, gt3.view_of(run, eps, labels), starts, DETS)}
    return out


def main(argv):
    runs = sorted(d for c in argv[1:] for d in Path(c).iterdir() if (d / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    names = list(res[0]["v"])
    T = gt1._table
    rows = []
    for name in names:
        neg = {s: sum(r["v"][name]["n"] for r in res if r["scn"] == s) for s in NEG}
        ev = [x for r in res if r["scn"] in ("burstcap",) for x in r["v"][name]["events"]]
        ev_all = [x for r in res for x in r["v"][name]["events"]]
        n = sum(r["v"][name]["n"] for r in res)
        short = sum(r["v"][name]["short"] for r in res)
        rows.append([name, n, f"{short} ({100 * short / max(1, n):.0f} %)", *neg.values(),
                     f"{sum(1 for x in ev if x['n'])}/{len(ev)}",
                     f"{sum(1 for x in ev_all if x['n'])}/{len(ev_all)}", sum(1 for x in ev_all if x["n"] > 1),
                     gt3_report._q([x["lag"] for x in ev_all], 0.5), gt3_report._q([x["lag"] for x in ev_all], 0.9)])
    L = ["# GT3 persistence window check", "", "## Truth only (no detector involved)", "",
         T(["truth", "episodes", "< 0.5 s", *NEG, "burstcap event x client caught", "all injected event x client caught",
            "split events", "onset lag p50 (s)", "p90"], rows), ""]
    rows = []
    for aqm in sorted({r["aqm"] for r in res}):
        for name in names:
            cells = []
            for d in DETS:
                s = gt_score.summarize([r["v"][name]["score"][d] for r in res if r["aqm"] == aqm])
                cells.append(f"{s['precision']:.2f} / {s['recall']:.2f} / {s['recall_long']:.2f} / {s['latency_p50_ms']:.0f}")
            rows.append([aqm, name, *cells])
    L += ["## Detector scores (precision / recall / recall >= 1 s / latency p50 ms)", "",
          T(["aqm", "truth", *DETS], rows), ""]
    Path(argv[0]).write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
