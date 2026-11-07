"""Hysteresis and don't-care bands shared by every ground truth (GT1, GT2, ...).

Each truth has one primary scalar x with a sourced entry threshold x_hi and a
band below it (x_lo = x_hi - band). A window enters the active state when the
GT's entry condition holds (x >= x_hi and its other entry conditions) and stays
active while its stay condition holds (x >= x_lo and its other stay
conditions). Persistence, backdated onsets, P_off and merging then work on the
active sequence, unchanged. Per window:

    inside an episode                 CONGESTED
    outside, x >= x_lo                AMBIGUOUS  (no verdict; also a short
                                                  active run that failed persistence)
    outside, x < x_lo                 CLEAR
"""

from __future__ import annotations

import numpy as np

CONGESTED, AMBIGUOUS, CLEAR = "CONGESTED", "AMBIGUOUS", "CLEAR"
NO_DATA = "NO_DATA"  # no information in the window (GT3): never CLEAR, ignored in scoring
LABEL_FIELDS = ("hop", "t_start", "t_end", "label")


def hysteresis(enter: np.ndarray, stay: np.ndarray) -> np.ndarray:
    """Active state per window: not active + enter -> active; active + stay -> active."""
    active = np.zeros(len(enter), dtype=bool)
    on = False
    for i in range(len(enter)):
        on = bool(stay[i]) if on else bool(enter[i])
        if not on and enter[i]:  # a failed stay may re-enter in the same window
            on = True
        active[i] = on
    return active


def labels(in_episode: np.ndarray, x: np.ndarray, x_lo: np.ndarray | float) -> np.ndarray:
    return np.where(in_episode, CONGESTED, np.where(x >= x_lo, AMBIGUOUS, CLEAR))


def spans(t_start: np.ndarray, t_end: np.ndarray, lab: np.ndarray) -> list[tuple[float, float, str]]:
    """Run-length (t_start, t_end, label) of per-window labels; windows are (t_start[i], t_end[i]]."""
    out = []
    for a, b, x in zip(t_start, t_end, lab):
        if out and out[-1][2] == x and abs(out[-1][1] - a) < 1e-9:
            out[-1] = (out[-1][0], float(b), x)
        else:
            out.append((float(a), float(b), str(x)))
    return out


def share(label_spans: list[tuple[float, float, str]], lo: float, hi: float) -> dict[str, float]:
    """Fraction of [lo, hi] under each label (time without a window counts as nothing)."""
    total = {CONGESTED: 0.0, AMBIGUOUS: 0.0, CLEAR: 0.0, NO_DATA: 0.0}
    for a, b, x in label_spans:
        total[x] += max(0.0, min(b, hi) - max(a, lo))
    span = max(hi - lo, 1e-9)
    return {k: v / span for k, v in total.items()}
