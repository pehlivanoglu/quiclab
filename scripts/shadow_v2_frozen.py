#!/usr/bin/env python3
"""The frozen Shadow v2 for other pipelines (grouping): alarm episodes of every flow of one run.

    episodes(run, "v2", mode="OWD", hold=True) -> {flow: [(t_alarm, t_end, t_onset), ...]}

No truth is read: the tick files are built from the per-ACK replay dump only (<run>/shadow-v2/ticks-frozen[-owd]),
and the detector freezes its own statistics on its own score. Works on any det_eval.Run, including the grouping
adapter's SessionRun (one flow per session).

Detector: fusion d, loss gate level+cap, with or without the hold rule (scripts/shadow_v2_step3.py), theta_on 0.25.
Fitted values: FROZEN below = the ip4 campaigns (reports/detector-v2/ip4/report.md), not re-fitted per campaign.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import owd_mode  # noqa: E402
import shadow_v2_step1 as s1  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402
import shadow_v2_step5 as s5  # noqa: E402

LABEL = {"v2": "fuse d: s1+s2+s3+sL", "v2-fixed": "fuse d fixed"}
FROZEN = {
    "RTT": {"floors": {"F1": 0.3171, "F2": 0.3979, "F3": 0.004303, "F4": 0.004136},
            "g_ref": {"v2": 67.2, "v2-fixed": 75.5},
            "stats": {"F1": (3.277, 3.771), "F2": (-0.0205, 4.312), "F3": (-0.008994, 0.04832),
                      "F4": (0.01814, 0.05036), "L": (0.0001618, 0.005913)}},
    "OWD": {"floors": {"F1": 0.2731, "F2": 0.3682, "F3": 0.004279, "F4": 0.004138},
            "g_ref": {"v2": 67.7, "v2-fixed": 77.9},
            "stats": {"F1": (1.503, 3.181), "F2": (-0.06983, 4.119), "F3": (-0.008922, 0.04725),
                      "F4": (0.01795, 0.05028), "L": (0.000162, 0.005916)}},
}


def tick_files(run: d.Run, mode: str) -> dict[str, Path]:
    """Truth-free tick files of every flow (built once per run and mode)."""
    owd = mode == "OWD"
    out = run.path / "shadow-v2" / ("ticks-frozen-owd" if owd else "ticks-frozen")
    files = {s: out / f"{s}.csv" for s in run.subs}
    if all(f.exists() for f in files.values()):
        return files
    dump = run.path / "shadow-v2" / ("v1-samples-owd" if owd else "v1-samples")
    if not all((dump / f"{s}.csv").exists() for s in run.subs):
        with tempfile.TemporaryDirectory() as tmp:
            acks = {s: owd_mode.owd_acks(run, s, Path(tmp)) for s in run.subs} if owd else None
            d.replay(run, d.TUNED, samples_to=dump, acks=acks, grouping="none")
    out.mkdir(parents=True, exist_ok=True)
    no_truth = np.zeros(1, dtype=int)
    for s, f in files.items():
        rate = run.topology["subscribers"][s]["rate_kbps"] * 1000
        s1.ticks_for(run, s, dump, no_truth, rate, s1.tick_s(run)).to_csv(f, index=False)
    return files


def episodes(run: d.Run, det: str = "v2", mode: str = "RTT", hold: bool = True) -> dict[str, list[tuple[float, float, float]]]:
    """(alarm time, end, onset = last tick with G = 0 before the alarm) per flow."""
    fit = FROZEN[mode]
    s3.FLOORS.clear()
    s3.FLOORS.update(fit["floors"])
    s3.FIXED_STATS.clear()
    s3.FIXED_STATS.update(fit["stats"])
    label = LABEL[det] + (" +hold" if hold else "") + " gate:level+cap"
    out = {}
    for s, f in tick_files(run, mode).items():
        r = s3.run_cusum(s3.load_flow(f), label, fit["g_ref"][det], False)
        out[s] = s5.on_spans(r, s3.THETA_ON)
    return out
