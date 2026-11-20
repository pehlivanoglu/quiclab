"""GT-L (GT3 in code) scorer, version 2 (user decision D1, 2026-11-19): the matching window after a truth onset is
2 s instead of SEARCH_S = 10 s. Everything else is gt_score.py's rule, unchanged: an episode is detected when an
alarm starts in [t_on - PRE_ONSET_LEAD_S, min(t_end, t_on + SEARCH_S_V2)]; the first such start is a TP and its
latency is max(0, start - t_on); later starts in the window are duplicates; other starts inside an episode and in
AMBIGUOUS / NO_DATA time are ignored; a start in CLEAR time is a FP. Alarm-on recall
(reports/v3-detector/score_runs.alarm_on) with the same window.

gt_score.py (version 1, 10 s) and its outputs stay as they are; this module is used next to it.
"""

from __future__ import annotations

import det_eval
import gt_bands
from gt_score import BINS, GRID_S, RANK, _bin

VERSION = 2
SEARCH_S_V2 = 2.0   # (P) user decision D1, 2026-11-19 (version 1: det_eval.SEARCH_S = 10 s)


def score(run: det_eval.Run, view: dict, starts: dict, detectors, search_s: float = SEARCH_S_V2) -> dict[str, dict]:
    """gt_score.score with the matching window's end at min(t_end, t_on + search_s)."""
    out = {}
    for name in detectors:
        t = {"episodes": 0, "detected": 0, "tp": 0, "fp": 0, "clear_s": 0.0, "amb_s": 0.0, "latency": [],
             "bin_episodes": [0] * len(BINS), "bin_detected": [0] * len(BINS), "early": 0, "late_latency": []}
        for s, (eps, code) in view.items():
            alarms = sorted(a for a in starts.get((name, s), []) if a >= det_eval.WARMUP_S)
            cells = code[int(det_eval.WARMUP_S / GRID_S):]
            t["clear_s"] += float((cells == RANK[gt_bands.CLEAR]).sum()) * GRID_S
            t["amb_s"] += float((cells == RANK[gt_bands.AMBIGUOUS]).sum()) * GRID_S
            used = set()
            for a, b in eps:
                if a < det_eval.WARMUP_S:
                    continue
                t["episodes"] += 1
                k = _bin(b - a)
                t["bin_episodes"][k] += 1
                lo, hi = a - det_eval.PRE_ONSET_LEAD_S, min(b, a + search_s)
                hit = next((x for x in alarms if lo <= x <= hi), None)
                if hit is not None:
                    t["detected"] += 1
                    t["bin_detected"][k] += 1
                    t["tp"] += 1
                    t["latency"].append(max(0.0, hit - a))
                    if hit < a:
                        t["early"] += 1
                    else:
                        t["late_latency"].append(hit - a)
                    used.add(hit)
                used.update(x for x in alarms if lo <= x <= hi)
            for x in alarms:
                if x in used or any(a <= x <= b for a, b in eps):
                    continue
                c = code[min(len(code) - 1, int(x / GRID_S))]
                if c == RANK[gt_bands.CLEAR]:
                    t["fp"] += 1
        out[name] = t
    return out


def alarm_on(view: dict, spans: dict, det: str, search_s: float = SEARCH_S_V2) -> dict:
    """score_runs.alarm_on with the same window end."""
    ep = on = 0
    for s, (eps, _) in view.items():
        sp = spans.get((det, s), [])
        for a, b in eps:
            if a < det_eval.WARMUP_S:
                continue
            ep += 1
            lo, hi = a - det_eval.PRE_ONSET_LEAD_S, min(b, a + search_s)
            on += any(x <= hi and y >= lo for x, y in sp)
    return {"episodes": ep, "alarm_on": on}
