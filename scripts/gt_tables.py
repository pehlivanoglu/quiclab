#!/usr/bin/env python3
"""Detector precision / recall / detection latency against GT1 and GT2.

    python3 scripts/gt_tables.py OUT_PREFIX .runs/<campaign> [...]   # OUT_PREFIX.md + OUT_PREFIX.csv

Truths: gt1.Params() and gt2.Params() defaults (bands included). Scoring:
gt_score (client = union of the router-egress episodes on its path; TP = first
alarm in [t_on - 1 s, min(end, t_on + 10 s)]; AMBIGUOUS alarms ignored; CLEAR
alarms are FP). Detectors: every det_eval.DETECTORS entry. Tables: overall,
per topology (campaign), per topology x scenario. Pooled over AQMs and reps.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402

DETECTORS = tuple(det_eval.DETECTORS)
MAIN = ("shadow", "shadow_verified", "shadow_m4", "gcc", "bbr")
TRUTHS = ("GT1", "GT2", "GT3")


def topology(run_dir: Path) -> str:
    name = run_dir.parent.name
    return name.split("_det-")[-1] if "_det-" in name else name


def worker(run_dir: Path) -> dict:
    run = det_eval.Run(run_dir)
    starts = gt_score.alarm_starts(run, DETECTORS)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    hops = {"GT1": [(e["hop"], e["start_s"], e["end_s"]) for e in e1],
            "GT2": [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2]}
    views = {gt: gt_score.client_view(run, h, l) for (gt, h), l in zip(hops.items(), (l1, l2))}
    e3, l3 = gt3.run_truth(run, gt3.Params(), path_queues=False)
    views["GT3"] = gt3.view_of(run, e3, l3)
    score = {gt: gt_score.score(run, v, starts, DETECTORS) for gt, v in views.items()}
    for gt, h in hops.items():  # link-level recall next to the per-client one
        for det, extra in gt_score.hop_score(run, h, starts, DETECTORS).items():
            score[gt][det].update(extra)
    return {"topology": topology(run_dir), "scenario": det_eval.scenario_name(run_dir), "aqm": run.aqm, "score": score}


def _f(x: float, d: int = 2) -> str:
    return "-" if x != x else f"{x:.{d}f}"


def pooled(res: list[dict], gt: str, det: str) -> dict:
    return gt_score.summarize([r["score"][gt][det] for r in res])


def long_table(res, gt, groups, detectors):
    rows = []
    for key, runs in groups:
        for det in detectors:
            s = pooled(runs, gt, det)
            rows.append([*key, det, s["episodes"], _f(s["precision"]), _f(s["recall"]),
                         *(f"{_f(r)} ({n})" for r, n in zip(s["bin_recall"], s["bin_episodes"])),
                         f"{_f(s['hop_recall'])} ({s['hop_episodes']})" if s["hop_episodes"] else "-", _f(s["f1"]),
                         _f(s["latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0), _f(s["early_share"]),
                         _f(s["late_latency_p50_ms"], 0), _f(s["fa_per_min"])])
    return rows


def md(header, rows):
    return gt1._table(header, rows)


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        sys.exit(__doc__)
    prefix = Path(argv[0])
    runs = sorted(d for c in argv[1:] for d in Path(c).iterdir() if (d / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    cols = ["episodes", "precision", "recall", *(f"recall {b} (n)" for b in gt_score.BIN_LABELS),
            "hop-level recall (n)", "F1", "latency p50 (ms)", "latency p90 (ms)", "share alarmed before t_on",
            "latency p50 of alarms after t_on (ms)", "FA / min CLEAR"]
    by_topo = defaultdict(list)
    by_scn = defaultdict(list)
    for r in res:
        by_topo[r["topology"]].append(r)
        by_scn[(r["topology"], r["scenario"])].append(r)
    lines = ["# Detectors vs GT1, GT2 and GT3", "",
             f"{len(res)} runs ({', '.join(Path(c).name for c in argv[1:])}), pooled over AQMs and reps. "
             f"GT1 {gt1.Params().tag()}; GT2 {gt2.Params().tag()}; GT3 {gt3.Params().tag()}. GT1 / GT2 episodes are per "
             "client (router-egress episodes on its path), so a short hop episode counts once for every client behind "
             "that hop; GT3 episodes are the client's own. Recall is given unfiltered and per episode-duration bin "
             "(every bin shown, no cut-off); for GT1 / GT2 also per hop episode (detected when any exposed client alarms). Latency = alarm - t_on "
             "of detected episodes (0 if the alarm came first, up to 1 s early).", ""]
    csv_rows = []
    for gt in TRUTHS:
        overall = long_table(res, gt, [((), res)], DETECTORS)
        topo = long_table(res, gt, [((t,), v) for t, v in sorted(by_topo.items())], DETECTORS)
        lines += [f"## {gt}", "", "### Overall", "", md(["detector", *cols], overall), "",
                  "### Per topology", "", md(["topology", "detector", *cols], topo), "",
                  "### Per topology and scenario (precision / recall / recall of episodes >= 2 s / latency p50 ms)", ""]
        rows = []
        for (t, s), v in sorted(by_scn.items()):
            cells = []
            for det in MAIN:
                x = pooled(v, gt, det)
                cells.append(f"{_f(x['precision'])} / {_f(x['recall'])} / {_f(x['bin_recall'][-1])} / "
                             f"{_f(x['latency_p50_ms'], 0)}")
            first = pooled(v, gt, MAIN[0])
            rows.append([t, s, first["episodes"], first["bin_episodes"][-1], *cells])
        lines += [md(["topology", "scenario", "episodes", "episodes >= 2 s", *MAIN], rows), ""]
        csv_rows += [[gt, "overall", "", "", *r] for r in overall]
        csv_rows += [[gt, "topology", r[0], "", *r[1:]] for r in topo]
        csv_rows += [[gt, "scenario", *r] for r in long_table(res, gt, sorted(by_scn.items()), DETECTORS)]
    prefix.with_suffix(".md").write_text("\n".join(lines))
    with prefix.with_suffix(".csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["truth", "level", "topology", "scenario", "detector", *cols])
        w.writerows(csv_rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:])
