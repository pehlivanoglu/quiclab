#!/usr/bin/env python3
"""Restore <run>/truth/gtq-score-episodes.csv of the v3 runs to the v3-detector state (the four frozen detectors,
exactly as reports/v3-detector/score_runs.py wrote it). The first R2 batch overwrote it with the R2 detector set;
no script reads the file, but the run folders must stay as they were.
    nice -n 19 .venv/bin/python3 reports/detector-r2-2026-11-16/restore_gtq_episodes.py
"""
import sys
from pathlib import Path
from multiprocessing import Pool
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
DETS = {"v2-owd": ("v2", "OWD"), "v2-fixed-owd": ("v2-fixed", "OWD"), "v2-rtt": ("v2", "RTT"), "v2-fixed-rtt": ("v2-fixed", "RTT")}


def one(rd):
    import det_eval as d, gtq_score, shadow_v2_frozen as fz
    if not (rd / "truth" / "gtq.csv").exists():
        return rd.name, "no gtq"
    run = d.Run(rd)
    starts = {}
    for name, (det, mode) in DETS.items():
        for s, eps in fz.episodes(run, det, mode=mode, hold=True).items():
            starts[(name, s)] = [a for a, _, _ in eps]
    gtq_score.DETECTORS = tuple(DETS)
    gtq_score.score_run(rd, starts)
    return rd.name, "restored"


if __name__ == "__main__":
    k = ROOT / ".runs" / "2026-11-14_1818_v3"
    rs = sorted(p for p in k.iterdir() if p.is_dir() and (p / "events.csv").exists())
    with Pool(4) as pool:
        for name, st in pool.imap_unordered(one, rs):
            print(name, st, flush=True)
