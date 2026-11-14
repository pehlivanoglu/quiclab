#!/usr/bin/env python3
"""FlowBot's ground truth, ported to quiclab runs (read-only).

FlowBot (flowbot/src/siamese/preprocess.py, DataGetter.get_double_queues /
get_truth_from_queue) labels each flow at every 5 ms sample of an ns-3 run:
    q_win(queue) = rolling mean of packet_in_queue over the last 10 samples (50 ms)
    label = -1 when q_win < 50 packets on every candidate queue of the flow,
            else the candidate queue with the larger q_win.
Its candidate queues are the flow's two possible bottlenecks (left / right of
the dumbbell). Here: every sampled router egress on the client's path.

Port (constants: QLEN_TH 50 packets and WINDOW_S 50 ms are FlowBot's, no FLAG):
  * queue length = queue_packets of router-metrics: the 5 ms queue-only CSV when
    the topology records it (split, tree8, uneven), else the 25 ms CSV; the
    50 ms window is kept in time (10 samples at 5 ms, 2 at 25 ms);
  * an egress is "bottleneck" while its windowed queue >= 50 packets; a client
    is congested while any egress on its path is (label != -1 in FlowBot);
  * episodes = contiguous congested time per egress (no minimum duration, as in
    FlowBot); labels CONGESTED / CLEAR (no AMBIGUOUS band in FlowBot).
  * fq_codel / cake: the egress's total queue length (FlowBot only had FIFO
    queues; there is no per-flow variant in its code).
Scoring goes through gt_score.client_view like GT1 / GT2.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt_bands  # noqa: E402

QLEN_TH = 50          # packets (FlowBot th=50)
WINDOW_S = 0.050      # FlowBot rolling(10) at 5 ms


def series(run: det_eval.Run, csv: Path) -> tuple[np.ndarray, np.ndarray]:
    fine = csv.with_name(csv.stem + "-queue.csv")
    src = fine if fine.exists() else csv
    rows = det_eval.rows(src)
    t = np.array([run.t_mono_us(int(r["timestamp_mono_ns"]) / 1000) for r in rows])
    q = np.array([float(r["queue_packets"]) for r in rows])
    keep = (t >= 0) & (t <= run.duration - det_eval.SHUTDOWN_S)
    return t[keep], q[keep]


def windowed(t: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Mean of the samples in (t - WINDOW_S, t] (FlowBot: rolling(10, min_periods=1))."""
    if len(t) == 0:
        return q
    c = np.concatenate([[0.0], np.cumsum(q)])
    lo = np.searchsorted(t, t - WINDOW_S, side="right")
    hi = np.arange(1, len(t) + 1)
    return (c[hi] - c[lo]) / (hi - lo)


def run_truth(run: det_eval.Run) -> tuple[list[dict], list[dict]]:
    eps, labs = [], []
    for hop, csv in gt1.router_egresses(run):
        t, q = series(run, csv)
        if len(t) < 2:
            continue
        on = windowed(t, q) >= QLEN_TH
        hop_id = f"{hop[0]}->{hop[1]}"
        lab = np.where(on, gt_bands.CONGESTED, gt_bands.CLEAR)
        labs += [{"hop": hop_id, "t_start": round(a, 4), "t_end": round(b, 4), "label": x}
                 for a, b, x in gt_bands.spans(t[:-1], t[1:], lab[1:])]
        i = 0
        while i < len(on):
            if not on[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(on) and on[j + 1]:
                j += 1
            start, end = float(t[i - 1] if i else t[i]), float(t[j])
            if end >= det_eval.WARMUP_S:
                eps.append({"hop": hop_id, "start_s": start, "end_s": end})
            i = j + 1
    return eps, labs
