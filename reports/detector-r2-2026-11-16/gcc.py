"""Google Congestion Control's delay-based overuse detector, as implemented in libwebrtc (main branch, read
2026-11-16 from webrtc.googlesource.com/src):

  modules/congestion_controller/goog_cc/inter_arrival_delta.{h,cc}   InterArrivalDelta (send-time groups)
  modules/congestion_controller/goog_cc/trendline_estimator.{h,cc}   TrendlineEstimator (trendline + adaptive
                                                                      threshold + overuse state)
  modules/congestion_controller/goog_cc/delay_based_bwe.cc           feeding: send time and receive time per
                                                                      packet, sorted by receive time; detectors
                                                                      reset after kStreamTimeOut without packets

Every constant below is libwebrtc's default (S, source file in the comment). The IETF draft
(draft-ietf-rmcat-gcc-02, sections 5.1-5.4) uses a Kalman filter instead of the trendline; libwebrtc's trendline
is what WebRTC runs, so this follows libwebrtc. Rate control is not part of detection and is not implemented.
Output per packet update: the hypothesis "normal" / "overusing" / "underusing".
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

# inter_arrival_delta.{h,cc}, delay_based_bwe.cc
SEND_TIME_GROUP_MS = 5.0          # kSendTimeGroupLength
BURST_DELTA_MS = 5.0              # kBurstDeltaThreshold
MAX_BURST_MS = 100.0              # kMaxBurstDuration
REORDER_RESET = 3                 # kReorderedResetThreshold
ARRIVAL_OFFSET_RESET_MS = 3000.0  # kArrivalTimeOffsetThreshold
STREAM_TIMEOUT_MS = 2000.0        # kStreamTimeOut
# trendline_estimator.{h,cc}
WINDOW = 20                       # kDefaultTrendlineWindowSize
SMOOTHING = 0.9                   # kDefaultTrendlineSmoothingCoeff
GAIN = 4.0                        # kDefaultTrendlineThresholdGain
MAX_ADAPT_OFFSET_MS = 15.0        # kMaxAdaptOffsetMs
OVERUSE_TIME_MS = 10.0            # kOverUsingTimeThreshold
MIN_NUM_DELTAS = 60               # kMinNumDeltas
DELTA_COUNTER_MAX = 1000          # kDeltaCounterMax
K_UP, K_DOWN = 0.0087, 0.039      # k_up_, k_down_
THRESHOLD0 = 12.5                 # threshold_ initial
THRESHOLD_MIN, THRESHOLD_MAX = 6.0, 600.0
MAX_TIME_DELTA_MS = 100.0         # kMaxTimeDeltaMs in UpdateThreshold


@dataclass
class _Group:
    size: int = 0
    first_send: float | None = None
    send: float | None = None
    first_arrival: float | None = None
    complete: float | None = None
    last_system: float | None = None

    def empty(self) -> bool:
        return self.first_send is None


class InterArrivalDelta:
    def __init__(self, group_ms: float = SEND_TIME_GROUP_MS):
        self.group_ms = group_ms
        self.reset()

    def reset(self) -> None:
        self.cur, self.prev, self.reordered = _Group(), _Group(), 0

    def _belongs_to_burst(self, arrival: float, send: float) -> bool:
        arrival_delta = arrival - self.cur.complete
        send_delta = send - self.cur.send
        if send_delta == 0:
            return True
        propagation_delta = arrival_delta - send_delta
        return propagation_delta < 0 and arrival_delta <= BURST_DELTA_MS and \
            arrival - self.cur.first_arrival < MAX_BURST_MS

    def _new_group(self, arrival: float, send: float) -> bool:
        if self.cur.empty():
            return False
        if self._belongs_to_burst(arrival, send):
            return False
        return send - self.cur.first_send > self.group_ms

    def compute(self, send: float, arrival: float, system: float, size: int):
        """(send_delta, arrival_delta, size_delta) when a group closed against a previous one, else None."""
        out = None
        if self.cur.empty():
            self.cur = _Group(size, send, send, arrival, arrival, system)
            return None
        if self.cur.first_send > send:
            return None                                   # reordered packet
        if self._new_group(arrival, send):
            if not self.prev.empty():
                sd = self.cur.send - self.prev.send
                ad = self.cur.complete - self.prev.complete
                sysd = self.cur.last_system - self.prev.last_system
                if ad - sysd >= ARRIVAL_OFFSET_RESET_MS:
                    self.reset()
                    return None
                if ad < 0:
                    self.reordered += 1
                    if self.reordered >= REORDER_RESET:
                        self.reset()
                    return None
                self.reordered = 0
                out = (sd, ad, self.cur.size - self.prev.size)
            self.prev = self.cur
            self.cur = _Group(size, send, send, arrival, arrival, system)
        else:
            self.cur.size += size
            self.cur.send = max(self.cur.send, send)
            self.cur.complete = arrival
            self.cur.last_system = system
        return out


class TrendlineEstimator:
    def __init__(self):
        self.hist: deque = deque()
        self.num_deltas = 0
        self.first_arrival = None
        self.acc = 0.0
        self.smoothed = 0.0
        self.prev_trend = 0.0
        self.threshold = THRESHOLD0
        self.last_update = -1.0
        self.time_over = -1.0
        self.over_count = 0
        self.state = "normal"

    @staticmethod
    def _slope(points) -> float | None:
        n = len(points)
        xm = sum(p[0] for p in points) / n
        ym = sum(p[1] for p in points) / n
        num = sum((x - xm) * (y - ym) for x, y in points)
        den = sum((x - xm) ** 2 for x, _ in points)
        return num / den if den != 0 else None

    def update(self, recv_delta: float, send_delta: float, arrival_ms: float) -> str:
        delta = recv_delta - send_delta
        self.num_deltas = min(self.num_deltas + 1, DELTA_COUNTER_MAX)
        if self.first_arrival is None:
            self.first_arrival = arrival_ms
        self.acc += delta
        self.smoothed = SMOOTHING * self.smoothed + (1 - SMOOTHING) * self.acc
        self.hist.append((arrival_ms - self.first_arrival, self.smoothed))
        if len(self.hist) > WINDOW:
            self.hist.popleft()
        trend = self.prev_trend
        if len(self.hist) == WINDOW:
            s = self._slope(self.hist)
            trend = s if s is not None else trend
        self._detect(trend, send_delta, arrival_ms)
        return self.state

    def _detect(self, trend: float, ts_delta: float, now_ms: float) -> None:
        if self.num_deltas < 2:
            self.state = "normal"
            return
        modified = min(self.num_deltas, MIN_NUM_DELTAS) * trend * GAIN
        if modified > self.threshold:
            self.time_over = ts_delta / 2 if self.time_over == -1 else self.time_over + ts_delta
            self.over_count += 1
            if self.time_over > OVERUSE_TIME_MS and self.over_count > 1 and trend >= self.prev_trend:
                self.time_over = 0
                self.over_count = 0
                self.state = "overusing"
        elif modified < -self.threshold:
            self.time_over = -1
            self.over_count = 0
            self.state = "underusing"
        else:
            self.time_over = -1
            self.over_count = 0
            self.state = "normal"
        self.prev_trend = trend
        self._update_threshold(modified, now_ms)

    def _update_threshold(self, modified: float, now_ms: float) -> None:
        if self.last_update == -1:
            self.last_update = now_ms
        if abs(modified) > self.threshold + MAX_ADAPT_OFFSET_MS:
            self.last_update = now_ms
            return
        k = K_DOWN if abs(modified) < self.threshold else K_UP
        dt = min(now_ms - self.last_update, MAX_TIME_DELTA_MS)
        self.threshold = min(max(self.threshold + k * (abs(modified) - self.threshold) * dt, THRESHOLD_MIN), THRESHOLD_MAX)
        self.last_update = now_ms


def detect(packets, group_ms: float = SEND_TIME_GROUP_MS) -> list[tuple[float, str]]:
    """packets: iterable of (send_ms, arrival_ms, size) on one clock pair; processed sorted by arrival
    (delay_based_bwe.cc SortedByReceiveTime). Returns (arrival_ms, state) at every trendline update.
    The system time of a packet is its arrival time (offline replay)."""
    ia, tl = InterArrivalDelta(group_ms), TrendlineEstimator()
    last = None
    out = []
    for send, arr, size in sorted(packets, key=lambda p: (p[1], p[0])):
        if last is not None and arr - last > STREAM_TIMEOUT_MS:
            ia, tl = InterArrivalDelta(group_ms), TrendlineEstimator()
        last = arr
        d = ia.compute(send, arr, arr, int(size))
        if d is not None:
            out.append((arr, tl.update(d[1], d[0], arr)))
    return out


def episodes(states: list[tuple[float, str]]) -> list[tuple[float, float]]:
    """Overuse spans: from an update that enters "overusing" to the next update that leaves it."""
    out, start = [], None
    for t, s in states:
        if s == "overusing" and start is None:
            start = t
        elif s != "overusing" and start is not None:
            out.append((start, t))
            start = None
    if start is not None:
        out.append((start, math.inf))
    return out
