"""Score detector alarms against a three-label ground truth (gt_bands labels).

Truth per client: episodes [(t_on, t_end)] and label spans [(t_start, t_end,
label)]. Resource-level truths (GT1, GT2) become per-client by exposure: a
client sees the union of the episodes and the worst label (CONGESTED >
AMBIGUOUS > CLEAR) of the router egresses on its path.

Rules (ground-truth bands note, section 7): an episode is detected when an
alarm starts in [t_on - PRE_ONSET_LEAD_S, min(t_end, t_on + SEARCH_S)] (the
det_eval window); the first such alarm is a TP, later ones duplicates. Any
other alarm start: inside an episode ignored, in AMBIGUOUS time ignored, in
CLEAR time a FP. Alarms during the warm-up are not scored, nor are episodes
starting in it. Precision = TP / (TP + FP); false alarms per minute of CLEAR
time; F1 from precision and episode recall.
"""

from __future__ import annotations

import statistics
from collections import defaultdict

import numpy as np

import det_eval
import gt_bands

RANK = {gt_bands.NO_DATA: -1, gt_bands.CLEAR: 0, gt_bands.AMBIGUOUS: 1, gt_bands.CONGESTED: 2}
NAMES = {v: k for k, v in RANK.items()}
GRID_S = 0.005
SCORED = ("shadow", "gcc", "bbr")
# Recall is also broken down by episode duration (no cut-off: every bin is reported).
BINS = ((0.0, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, float("inf")))
BIN_LABELS = ("< 0.5 s", "0.5-1 s", "1-2 s", ">= 2 s")


def _bin(duration: float) -> int:
    return next(i for i, (lo, hi) in enumerate(BINS) if lo <= duration < hi)


def client_view_codes(run: det_eval.Run, spans: list[dict]) -> np.ndarray:
    """Label code per GRID_S cell from one series of label spans (-1: no window covers the cell)."""
    n = int(run.duration / GRID_S)
    grid_t = (np.arange(n) + 0.5) * GRID_S
    if not spans:
        return np.full(n, -1)
    starts = np.array([x["t_start"] for x in spans])
    ends = np.array([x["t_end"] for x in spans])
    codes = np.array([RANK[x["label"]] for x in spans])
    k = np.searchsorted(starts, grid_t, side="right") - 1
    kk = np.clip(k, 0, None)
    return np.where((k >= 0) & (grid_t <= ends[kk]), codes[kk], -1)


def client_view(run: det_eval.Run, hop_eps: list[tuple[str, float, float]],
                hop_labels: list[dict]) -> dict[str, tuple[list[tuple[float, float]], np.ndarray]]:
    """Per client: (merged episodes on its path, label code per GRID_S cell)."""
    by_hop = defaultdict(list)
    for x in hop_labels:
        by_hop[x["hop"]].append(x)
    per_hop = {hop: client_view_codes(run, spans) for hop, spans in by_hop.items()}
    out = {}
    for s in run.subs:
        hops = [f"{a}->{b}" for a, b in det_eval.path_hops(run, run.pub, s)]
        arrays = [per_hop[h] for h in hops if h in per_hop]
        code = np.max(arrays, axis=0) if arrays else np.full(int(run.duration / GRID_S), -1)
        merged: list[list[float]] = []
        for a, b in sorted((a, b) for h, a, b in hop_eps if h in hops):
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        out[s] = ([(a, b) for a, b in merged], code)
    return out


def alarm_starts(run: det_eval.Run, detectors=SCORED, acks=None, grouping: str = "topology") -> dict[tuple[str, str], list[float]]:
    """(detector, client) -> alarm start times, from the same replays det_eval.score uses."""
    # As det_eval.score: tuned variants relabelled, BBR's own events ("" variant) taken once, from the m4 replay.
    events = [{**e, "variant": f"tuned:{e['variant']}"} for e in det_eval.replay(run, det_eval.TUNED, acks=acks, grouping=grouping)
              if e["variant"]]
    events += det_eval.replay(run, det_eval.PARAMS, acks=acks, grouping=grouping)  # m4 setting: gcc, shadow_m4, single-signal variants, bbr
    starts = defaultdict(list)
    for e in events:
        for name in detectors:
            variant, ev = det_eval.DETECTORS[name]
            if e["variant"] == variant and e["event"] == ev:
                starts[(name, e["subscriber"])].append(e["t"])
    return starts


def score(run: det_eval.Run, view: dict, starts: dict, detectors=SCORED) -> dict[str, dict]:
    """Per detector tallies over all clients of one run."""
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
                lo, hi = a - det_eval.PRE_ONSET_LEAD_S, min(b, a + det_eval.SEARCH_S)
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


def summarize(tallies: list[dict]) -> dict[str, float]:
    """Pool tallies of one detector over runs."""
    ep = sum(t["episodes"] for t in tallies)
    det = sum(t["detected"] for t in tallies)
    tp, fp = sum(t["tp"] for t in tallies), sum(t["fp"] for t in tallies)
    clear = sum(t["clear_s"] for t in tallies)
    lat = [x for t in tallies for x in t["latency"]]
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = det / ep if ep else float("nan")
    f1 = 2 * p * r / (p + r) if p == p and r == r and p + r else float("nan")
    return {"episodes": ep, "recall": r, "precision": p, "f1": f1, "fa_per_min": fp / (clear / 60) if clear else float("nan"),
            "latency_p50_ms": statistics.median(lat) * 1000 if lat else float("nan"),
            "latency_p90_ms": float(np.percentile(lat, 90)) * 1000 if lat else float("nan"),
            "detected": det, "tp": tp, "fp": fp,
            "early_share": sum(t.get("early", 0) for t in tallies) / det if det else float("nan"),
            "late_latency_p50_ms": statistics.median(x for t in tallies for x in t.get("late_latency", [])) * 1000
            if any(t.get("late_latency") for t in tallies) else float("nan"),
            "bin_episodes": [sum(t["bin_episodes"][i] for t in tallies) for i in range(len(BINS))],
            "bin_recall": [(sum(t["bin_detected"][i] for t in tallies) / n if n else float("nan"))
                           for i, n in enumerate(sum(t["bin_episodes"][i] for t in tallies) for i in range(len(BINS)))],
            "hop_episodes": sum(t.get("hop_episodes", 0) for t in tallies),
            "hop_recall": (sum(t.get("hop_detected", 0) for t in tallies) / sum(t.get("hop_episodes", 0) for t in tallies)
                           if sum(t.get("hop_episodes", 0) for t in tallies) else float("nan"))}


def hop_score(run: det_eval.Run, hop_eps: list[tuple[str, float, float]], starts: dict, detectors=SCORED) -> dict[str, dict]:
    """Link-level recall for resource truths (GT1 / GT2): one count per hop episode,
    detected when any client whose path crosses the hop alarms in the det_eval window.
    Returns per detector {"hop_episodes", "hop_detected"} to merge into score() tallies."""
    exposed = {}
    for s in run.subs:
        for a, b in det_eval.path_hops(run, run.pub, s):
            exposed.setdefault(f"{a}->{b}", []).append(s)
    out = {}
    for name in detectors:
        t = {"hop_episodes": 0, "hop_detected": 0}
        for hop, a, b in hop_eps:
            if a < det_eval.WARMUP_S or not exposed.get(hop):
                continue
            t["hop_episodes"] += 1
            lo, hi = a - det_eval.PRE_ONSET_LEAD_S, min(b, a + det_eval.SEARCH_S)
            if any(lo <= x <= hi for s in exposed[hop] for x in starts.get((name, s), [])):
                t["hop_detected"] += 1
        out[name] = t
    return out
