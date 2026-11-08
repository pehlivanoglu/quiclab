#!/usr/bin/env python3
"""GT3: flow-impact truth per client, from its own packets' one-way delay and loss.

    python3 scripts/gt3.py score .runs/<run> [...]     # <run>/truth/gt3.csv + gt3-labels.csv

Source A (used when timed / sent >= 50 % for the client): publishers/<pub>/<sub>-owd.csv,
written by qvideo-server's OwdRecorder: the client's own receive timestamps
(carried in its QUIC ACKs) minus the send time, per 5 ms bin of SEND time, with
the bin minimum and the packets sent / timestamped. Sender and client share one
CLOCK_MONOTONIC, so the OWD is exact. Source B: clients/<sub>-frames.csv, one
OWD per frame (delay channel only, delta frames; keyframes are NO_DATA there).

Per window w (5 ms bin, or one frame for B):
    base   trailing minimum OWD over BASE_WINDOW_S, restarted at every forward
           delay change on the path (det_eval.delay_changes); +-0.25 s around a
           change is NO_DATA
    q      window minimum OWD - base
    x_d    trailing minimum of q over P_MIN (0.5 s); the delay channel enters at
           x_d >= 10 ms, stays while >= 5 ms; its onset is backdated to the start
           of that window
    x_l    (sent - timestamped) / sent over the trailing 1 s, when >= 50 packets
           were sent and some were timestamped (else no loss information); enters
           at >= 10 %, stays while >= 3 %; onset backdated to the first bin with a
           lost packet in that second
Each channel has its own state machine (gt_bands.hysteresis); a window without
information keeps the state. active = delay or loss. Persistence as GT1 / GT2:
K of N windows active (N = P_ON / W, K / N = 4 / 6); t_on = the onset of the first
active window of the qualifying run, trigger = the channels active there; the
episode ends after P_OFF (0.5 s) without an active window. Labels: CONGESTED in an
episode; outside it NO_DATA (no timestamped packet, or near a delay change),
AMBIGUOUS when the 150 ms minimum of q (P_AMB, the link-level persistence of
GT1 / GT2) is >= 5 ms or x_l >= 3 %, else CLEAR: a standing queue of 150-500 ms
is neither an episode nor clear time, so an alarm on it is not a false alarm.

Loss is the receiver's evidence (sent but never timestamped), as det_eval's
measured truth uses, not the sender's newly_lost (relay-side loss detection).
The time axis is the send time, the axis the sender-side detectors see.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt_bands  # noqa: E402

NO_DATA = gt_bands.NO_DATA
FIELDS = ("flow", "episode_id", "t_on", "t_end", "duration", "trigger", "peak_q", "mean_q", "loss_rate",
          "severity", "owd_source", "path_queue_episodes")


@dataclass(frozen=True)
class Params:
    d_enter_ms: float = 10.0
    d_stay_ms: float = 5.0
    l_enter: float = 0.10
    l_stay: float = 0.03
    # 0.5 s (not the spec's shared 150 ms): chosen 2026-11-07 from truth-only checks
    # (scripts/gt3_window_check.py): no sub-0.5 s episodes, negatives 3-4x lower, 97 % of
    # the injected event x client hits kept, split events 917 -> 336.
    p_min: float = 0.5
    p_amb: float = 0.15  # window of the AMBIGUOUS band (link-level persistence)
    p_on: float = 0.15
    p_off: float = 0.5
    kn: float = 4 / 6
    base_window_s: float = 10.0
    min_packets: int = 50
    loss_window_s: float = 1.0
    exclude_s: float = det_eval.DELAY_CHANGE_S
    min_coverage: float = 0.5

    def tag(self) -> str:
        return (f"delay {self.d_enter_ms:g}/{self.d_stay_ms:g} ms, loss {self.l_enter:g}/{self.l_stay:g}, "
                f"P_min {self.p_min * 1000:g} ms, P_amb {self.p_amb * 1000:g} ms, K/N {self.kn:.2f}, base {self.base_window_s:g} s, "
                f"min packets {self.min_packets}")


# ── inputs ────────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def source_a(run_dir: Path, sid: str):
    """(t, owd_ms or nan, sent, timed) per 5 ms send-time bin, run clock."""
    run = det_eval.Run(run_dir)
    df = pd.read_csv(run.sender_file(sid, "owd"))
    t = (df["bin_mono_us"].to_numpy() * 1000 - run.epoch_mono_ns) / 1e9
    keep = (t >= 0) & (t <= run.duration - det_eval.SHUTDOWN_S)
    return (t[keep], df["owd_min_us"].to_numpy(dtype=float)[keep] / 1000,
            df["packets_sent"].to_numpy(dtype=float)[keep], df["packets_timed"].to_numpy(dtype=float)[keep])


@lru_cache(maxsize=None)
def source_b(run_dir: Path, sid: str):
    """(t, owd_ms with keyframes as nan) per frame, run clock (send time)."""
    run = det_eval.Run(run_dir)
    df = pd.read_csv(run.path / "clients" / f"{sid}-frames.csv")
    t = (df["send_us"].to_numpy() * 1000 - run.epoch_unix_ns) / 1e9
    owd = np.where(df["keyframe"].to_numpy() == 1, np.nan, df["owd_us"].to_numpy(dtype=float) / 1000)
    keep = (t >= 0) & (t <= run.duration - det_eval.SHUTDOWN_S)
    order = np.argsort(t[keep])
    return t[keep][order], owd[keep][order]


def coverage(run_dir: Path, sid: str) -> float:
    """Timestamped / sent packets in source A; 0 when the run has no OWD oracle."""
    if not det_eval.Run(run_dir).sender_file(sid, "owd").exists():
        return 0.0
    _, _, sent, timed = source_a(run_dir, sid)
    return float(timed.sum() / sent.sum()) if sent.sum() else 0.0


# ── core ──────────────────────────────────────────────────────────────────

def _rolling_min(t: np.ndarray, x: np.ndarray, window_s: float) -> np.ndarray:
    """Trailing time-window minimum ignoring nan (nan when the window has no value)."""
    s = pd.Series(x, index=pd.to_datetime(t, unit="s"))
    return s.rolling(f"{int(round(window_s * 1e6))}us", min_periods=1).min().to_numpy()


def baseline(t: np.ndarray, owd: np.ndarray, changes: list[float], window_s: float) -> np.ndarray:
    """Trailing minimum OWD over window_s, restarted at each delay change."""
    base = np.full(len(t), np.nan)
    edges = [-math.inf, *sorted(changes), math.inf]
    for a, b in zip(edges, edges[1:]):
        m = (t >= a) & (t < b)
        if m.any():
            base[m] = _rolling_min(t[m], owd[m], window_s)
    return base


def _channel(x: np.ndarray, enter: float, stay: float, onset_of, informative: np.ndarray):
    """State machine with carry over uninformative windows; returns (active, onset time per window)."""
    n = len(x)
    active = np.zeros(n, dtype=bool)
    onset = np.full(n, np.nan)
    on, since = False, np.nan
    for i in range(n):
        if informative[i] and not math.isnan(x[i]):
            if on and x[i] < stay:
                on = False
            if not on and x[i] >= enter:
                on, since = True, onset_of(i)
        active[i], onset[i] = on, since if on else np.nan
    return active, onset


def flow_core(t, owd, sent, timed, changes, p: Params, dt: float):
    """Episodes and per-window labels for one flow. sent / timed None = no loss channel (source B)."""
    n = len(t)
    if n < 2:
        return [], np.array([], dtype=object), {}
    excluded = np.zeros(n, dtype=bool)
    for c in changes:
        excluded |= np.abs(t - c) < p.exclude_s
    base = baseline(t, owd, changes, p.base_window_s)
    q = owd - base
    x_d = _rolling_min(t, np.where(excluded, np.nan, q), p.p_min)
    has_q = ~np.isnan(x_d) & ~excluded
    d_act, d_on = _channel(x_d, p.d_enter_ms, p.d_stay_ms,
                           lambda i: max(t[0], t[i] - p.p_min + dt), has_q)
    if sent is not None:
        cs, ct = np.concatenate(([0], np.cumsum(sent))), np.concatenate(([0], np.cumsum(timed)))
        lo = np.searchsorted(t, t - p.loss_window_s, side="right")
        hi = np.arange(1, n + 1)
        ws, wt = cs[hi] - cs[lo], ct[hi] - ct[lo]
        ok = (ws >= p.min_packets) & (wt > 0) & ~excluded
        x_l = np.where(ok, (ws - np.minimum(wt, ws)) / np.maximum(ws, 1), np.nan)
        lost_bin = sent > timed

        def loss_onset(i):
            j = lo[i] + int(np.argmax(lost_bin[lo[i]:i + 1])) if lost_bin[lo[i]:i + 1].any() else i
            return t[j]
        l_act, l_on = _channel(x_l, p.l_enter, p.l_stay, loss_onset, ok)
    else:
        x_l = np.full(n, np.nan)
        l_act, l_on = np.zeros(n, dtype=bool), np.full(n, np.nan)
    active = d_act | l_act
    big_n = max(1, round(p.p_on / dt))
    k = max(1, math.ceil(p.kn * big_n - 1e-9))
    counts = np.convolve(active.astype(int), np.ones(big_n, dtype=int), "full")[big_n - 1:]
    episodes, i = [], 0
    while i < n:
        if counts[i] < k:
            i += 1
            continue
        start = i + int(np.argmax(active[i:i + big_n]))
        last, j = start, start + 1
        while j < n and t[j] - (t[last] + dt) < p.p_off - 1e-9:
            if active[j]:
                last = j
            j += 1
        onsets = [x for x in (d_on[start], l_on[start]) if not math.isnan(x)]
        trig = "both" if d_act[start] and l_act[start] else "delay" if d_act[start] else "loss"
        span = slice(start, last + 1)
        qs = q[span][~np.isnan(q[span])]
        loss = None
        if sent is not None and sent[span].sum():
            loss = float((sent[span].sum() - min(timed[span].sum(), sent[span].sum())) / sent[span].sum())
        episodes.append({"t_on": float(min(onsets)) if onsets else float(t[start]), "t_end": float(t[last] + dt),
                         "trigger": trig, "peak_q": float(qs.max()) if len(qs) else float("nan"),
                         "mean_q": float(qs.mean()) if len(qs) else float("nan"), "loss_rate": loss})
        i = last + 1
    in_ep = np.zeros(n, dtype=bool)
    for e in episodes:
        in_ep |= (t >= e["t_on"]) & (t < e["t_end"])
    no_data = excluded | (np.isnan(owd) if sent is None else (timed == 0))
    x_amb = _rolling_min(t, np.where(excluded, np.nan, q), p.p_amb)
    amb = (np.nan_to_num(x_amb, nan=-1) >= p.d_stay_ms) | (np.nan_to_num(x_l, nan=-1) >= p.l_stay)
    lab = np.where(in_ep, gt_bands.CONGESTED,
                   np.where(no_data, NO_DATA, np.where(amb, gt_bands.AMBIGUOUS, gt_bands.CLEAR)))
    return episodes, lab, {"q": q, "x_d": x_d, "x_l": x_l}


def severity(e: dict) -> str:
    q, loss = e["peak_q"], e["loss_rate"] or 0.0
    if q > 200 or loss > 0.10:
        return "severe"
    if (q != q or q < 50) and loss < 0.02:
        return "mild"
    return "moderate"


def flow_truth(run: det_eval.Run, sid: str, p: Params = Params(), source: str = "auto"):
    """(episodes, label spans, source used) for one client."""
    use_a = source == "A" or (source == "auto" and coverage(run.path, sid) >= p.min_coverage)
    changes = det_eval.delay_changes(run, sid)
    if use_a:
        t, owd, sent, timed = source_a(run.path, sid)
        eps, lab, _ = flow_core(t, owd, sent, timed, changes, p, 0.005)
        width = np.full(len(t), 0.005)
    else:
        t, owd = source_b(run.path, sid)
        dt = float(np.median(np.diff(t))) if len(t) > 1 else 1 / 30
        eps, lab, _ = flow_core(t, owd, None, None, changes, p, dt)
        width = np.append(np.diff(t), dt) if len(t) else np.array([])
    spans = gt_bands.spans(t, t + width, lab) if len(t) else []
    return eps, spans, "A" if use_a else "B"


def run_truth(run: det_eval.Run, p: Params = Params(), source: str = "auto", path_queues: bool = True):
    """GT3 episodes (rows of FIELDS) and label rows ({hop: flow, t_start, t_end, label}) for every client."""
    queues = []
    if path_queues:
        import gt1
        import gt2
        queues = [("GT1", e["hop"], e["start_s"], e["end_s"]) for e in gt1.run_truth(run, gt1.Params())[0]]
        queues += [("GT2", e["queue_id"], e["t_on"], e["t_end"]) for e in gt2.run_truth(run, gt2.Params())[0]]
    out, labels = [], []
    for sid in run.subs:
        eps, spans, src = flow_truth(run, sid, p, source)
        hops = {f"{a}->{b}" for a, b in det_eval.path_hops(run, run.pub, sid)}
        labels += [{"hop": sid, "t_start": round(a, 4), "t_end": round(b, 4), "label": x} for a, b, x in spans]
        n = 0
        for e in eps:
            if e["t_end"] < det_eval.WARMUP_S:
                continue
            n += 1
            pq = [f"{g}:{h}@{a:.3f}" for g, h, a, b in queues if h in hops and a <= e["t_end"] and b >= e["t_on"]]
            out.append({"flow": sid, "episode_id": n, "t_on": round(e["t_on"], 4), "t_end": round(e["t_end"], 4),
                        "duration": round(e["t_end"] - e["t_on"], 4), "trigger": e["trigger"],
                        "peak_q": round(e["peak_q"], 2), "mean_q": round(e["mean_q"], 2),
                        "loss_rate": "" if e["loss_rate"] is None else round(e["loss_rate"], 4),
                        "severity": severity(e), "owd_source": src, "path_queue_episodes": ";".join(pq)})
    return sorted(out, key=lambda e: (e["t_on"], e["flow"])), labels


def score(run_dir: Path, p: Params = Params()) -> None:
    run = det_eval.Run(run_dir)
    eps, labels = run_truth(run, p)
    det_eval.write_csv(run_dir / "truth" / "gt3-labels.csv", labels)
    path = run_dir / "truth" / "gt3.csv"
    with path.open("w") as f:  # header even when empty
        f.write(",".join(FIELDS) + "\n")
        for e in eps:
            f.write(",".join(str(e[k]) for k in FIELDS) + "\n")
    srcs = sorted({e["owd_source"] for e in eps}) or ["-"]
    print(f"{run_dir.name}: aqm={run.aqm} gt3_episodes={len(eps)} sources={','.join(srcs)}")


# ── views for scoring ─────────────────────────────────────────────────────

def current(run: det_eval.Run):
    """The existing det_eval.measured_truth as (episodes per client, label spans per client), or None."""
    measured = det_eval.measured_truth(run)
    if measured is None:
        return None
    episodes, grids = measured
    eps = {s: [(e["t0"], e["end"]) for e in episodes if e["subscriber"] == s] for s in run.subs}
    labels = {}
    for s, grid in grids.items():
        lab = [gt_bands.CONGESTED if any(a <= t + det_eval.GRID_S / 2 <= b for a, b in eps[s])
               else gt_bands.CLEAR if band == "clear" else gt_bands.AMBIGUOUS for t, band in grid]
        ts = np.array([t for t, _ in grid])
        labels[s] = gt_bands.spans(ts, ts + det_eval.GRID_S, np.array(lab))
    return eps, labels


def as_view(run: det_eval.Run, truth) -> dict:
    """Per-client (episodes, label codes) as gt_score.score expects."""
    import gt_score
    eps, labels = truth
    out = {}
    for s in run.subs:
        rows = [{"hop": s, "t_start": a, "t_end": b, "label": x} for a, b, x in labels.get(s, [])]
        out[s] = (eps.get(s, []), gt_score.client_view_codes(run, rows))
    return out


def view_of(run: det_eval.Run, eps: list[dict], labels: list[dict], need_path: bool = False) -> dict:
    """gt_score view from run_truth output. need_path: only episodes with a GT1 / GT2 queue on the path
    count (the others become AMBIGUOUS time)."""
    import gt_score
    out = {}
    for s in run.subs:
        mine = [e for e in eps if e["flow"] == s]
        keep = [(e["t_on"], e["t_end"]) for e in mine if not need_path or e["path_queue_episodes"]]
        drop = [(e["t_on"], e["t_end"]) for e in mine if need_path and not e["path_queue_episodes"]]
        rows = [x for x in labels if x["hop"] == s]
        code = gt_score.client_view_codes(run, rows)
        for a, b in drop:
            lo, hi = int(a / gt_score.GRID_S), int(b / gt_score.GRID_S) + 1
            code[lo:hi] = np.where(code[lo:hi] == gt_score.RANK[gt_bands.CONGESTED],
                                   gt_score.RANK[gt_bands.AMBIGUOUS], code[lo:hi])
        out[s] = (keep, code)
    return out


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[0] != "score":
        sys.exit(__doc__)
    for d in argv[1:]:
        score(Path(d))


if __name__ == "__main__":
    main(sys.argv[1:])
