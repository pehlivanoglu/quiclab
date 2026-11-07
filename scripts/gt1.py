#!/usr/bin/env python3
"""GT1: standing-queue congestion truth from the router's own queue counters.

    python3 scripts/gt1.py score .runs/<run> [...]           # <run>/truth/gt1.csv (+ gt1-5ms.csv)
    python3 scripts/gt1.py report .runs/<campaign>            # validation tables -> <campaign>/gt1-report.md
    options: --target MS --interval S|auto --util-th X|auto --merge-gap S|interval

Definition (CoDel's persistent-queue test, RFC 8289 / Nichols & Jacobson 2012,
on sampled counters): a bottleneck egress is congested while its queueing
delay never falls below TARGET for at least INTERVAL. Per sample i of the
router-metrics CSV (25 ms tc counters; 5 ms rtnetlink `-queue.csv` where
recorded):

    q_ms[i]   = backlog_bytes[i] * 8 / C(t_i)                 (sojourn of a packet arriving now)
    above[i]  = q_ms[i] >= TARGET and backlog_bytes[i] >= MTU  (tc-codel's drop condition)

Two consecutive above samples form one standing queue only if the queue
cannot have emptied in between. A backlog of D ms needs D ms to drain, so the
interval (t[i-1], t[i]] is continuous when q_ms[i-1] >= dt, or else when the
link stayed busy: transmitted bytes >= util_th x the capacity integral over
the interval. util_th "auto" = 1 - MTU / (C dt): one packet of counter
quantisation (at 5.665 Mb/s a 25 ms interval carries ~12 packets, so a
fixed 0.98 cuts 23 % of the intervals of a queue pinned at its limit).

A run of continuous above samples at least INTERVAL long is an episode; its
start is the first above sample (true onset in (start_lo, start]: the
previous sample saw no standing queue). Episodes closer than merge_gap merge.
INTERVAL is 150 ms (decided 2026-11-07: the same persistence as GT2's P_on);
"auto" = max(100 ms, largest client base RTT on the run), CoDel's "order of the
worst-case RTT", remains an option. C(t) is the scenario's nominal capacity (link
events applied); the capacity integral handles intervals spanning a change.

Hop level only: a client is *possibly* affected when its path crosses the
hop. fq_codel: the backlog sums all sub-queues, so q_ms is no flow's delay.
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402
import gt_bands  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.runtime import edge_interfaces  # noqa: E402

TARGET_MS = 5.0       # CoDel default
INTERVAL_MIN_S = 0.1  # CoDel default; raised to the largest base RTT
MTU = 1500
WARMUP_S = det_eval.WARMUP_S
SHUTDOWN_S = det_eval.SHUTDOWN_S
SWEEP = {"target_ms": (2.0, 5.0, 10.0), "interval_s": ("auto", 0.1, 0.15, 0.2, 0.35),
         "util_th": ("auto", 0.95, 0.98), "merge_gap_s": ("interval", 0.2, 0.5)}


@dataclass(frozen=True)
class Params:
    target_ms: float = TARGET_MS
    interval_s: float | str = 0.15
    util_th: float | str = "auto"
    merge_gap_s: float | str = "interval"
    mtu: int = MTU
    q_band_ms: float = 2.5    # hysteresis: stay while q_ms >= target - band (gt_bands)
    util_band: float = 0.0    # busy test is not relaxed inside an episode (2026-11-07: relaxing it merged keyframe queues)

    def resolve(self, max_rtt_s: float) -> "Params":
        interval = max(INTERVAL_MIN_S, max_rtt_s) if self.interval_s == "auto" else float(self.interval_s)
        gap = interval if self.merge_gap_s == "interval" else float(self.merge_gap_s)
        return replace(self, interval_s=interval, merge_gap_s=gap)

    def tag(self) -> str:
        return (f"target={self.target_ms:g} interval={self.interval_s if isinstance(self.interval_s, str) else f'{self.interval_s:g}'}"
                f" util_th={self.util_th if isinstance(self.util_th, str) else f'{self.util_th:g}'}"
                f" merge={self.merge_gap_s if isinstance(self.merge_gap_s, str) else f'{self.merge_gap_s:g}'}"
                f" q_band={self.q_band_ms:g} util_band={self.util_band:g}")


# ── core ──────────────────────────────────────────────────────────────────

def capacity_integral(caps: list[tuple[float, float]], t0: float, t1: float) -> float:
    """Bits the link could carry in (t0, t1] under the step series caps [(t, Mb/s)]."""
    total, t = 0.0, t0
    for when, bw in caps:
        if when <= t0:
            continue
        if when >= t1:
            break
        total += (when - t) * det_eval.value_at(caps, t) * 1e6
        t = when
    return total + (t1 - t) * det_eval.value_at(caps, t) * 1e6


def capacity_max(caps: list[tuple[float, float]], t0: float, t1: float) -> float:
    """Highest capacity (bps) in force anywhere in [t0, t1]."""
    return max([det_eval.value_at(caps, t0)] + [bw for when, bw in caps if t0 < when <= t1]) * 1e6


def gt1_episodes(t: np.ndarray, backlog_bytes: np.ndarray, tx_bytes: np.ndarray | None,
                 caps: list[tuple[float, float]], p: Params, drops: np.ndarray | None = None) -> list[dict]:
    """Standing-queue episodes on one egress (see gt1_core)."""
    return gt1_core(t, backlog_bytes, tx_bytes, caps, p, drops)[0]


def gt1_core(t: np.ndarray, backlog_bytes: np.ndarray, tx_bytes: np.ndarray | None,
             caps: list[tuple[float, float]], p: Params, drops: np.ndarray | None = None):
    """(episodes, per-sample labels) on one egress. t: sample times (s, run clock);
    backlog_bytes: backlog at t; tx_bytes: bytes transmitted in (t[i-1], t[i]]
    or None (queue-only CSV: continuity then relies on the drain bound alone).
    caps: [(t, Mb/s)] step series. p must be resolved (numeric interval, gap).
    drops: packets dropped in (t[i-1], t[i]], summed per episode when given.

    Hysteresis (gt_bands): a run enters at a sample with q_ms >= target and
    backlog >= MTU, and stays while q_ms >= target - q_band, backlog >= MTU
    and the queue cannot have emptied since the previous sample (drain bound,
    or util >= util_th - util_band). With both bands 0 this is the plain GT1."""
    n = len(t)
    if n < 2:
        return [], np.array([], dtype=str)
    cap_now = np.array([det_eval.value_at(caps, x) for x in t]) * 1e6
    q_ms = backlog_bytes * 8 / cap_now * 1000
    q_lo = p.target_ms - p.q_band_ms
    enter = (q_ms >= p.target_ms) & (backlog_bytes >= p.mtu)
    # continuous[i]: the queue cannot have emptied in (t[i-1], t[i]] (busy at the stay threshold).
    continuous = np.zeros(n, dtype=bool)
    for i in range(1, n):
        dt = t[i] - t[i - 1]
        drain_ms = backlog_bytes[i - 1] * 8 / capacity_max(caps, t[i - 1], t[i]) * 1000
        if drain_ms >= dt * 1000:
            continuous[i] = True
        elif tx_bytes is not None:
            cap_bits = capacity_integral(caps, t[i - 1], t[i])
            th = 1 - p.mtu * 8 / cap_bits if p.util_th == "auto" else float(p.util_th)
            continuous[i] = cap_bits > 0 and tx_bytes[i] * 8 / cap_bits >= th - p.util_band
    stay = (q_ms >= q_lo) & (backlog_bytes >= p.mtu) & continuous
    runs, start = [], None
    for i in range(n):
        if start is not None and not stay[i]:
            runs.append((start, i - 1))
            start = None
        if start is None and enter[i]:
            start = i
    if start is not None:
        runs.append((start, n - 1))
    episodes = []
    for a, b in runs:
        if t[b] - t[a] < p.interval_s:
            continue
        ep = {"start_s": float(t[a]), "start_lo_s": float(t[a - 1]) if a else float(t[a]), "end_s": float(t[b]),
              "q_min_ms": float(q_ms[a:b + 1].min()), "q_max_ms": float(q_ms[a:b + 1].max()),
              "cap_mbps": float(cap_now[a] / 1e6), "drops": int(drops[a:b + 1].sum()) if drops is not None else 0,
              "fragments": 1, "_a": a, "_b": b}
        if episodes and ep["start_s"] - episodes[-1]["end_s"] < p.merge_gap_s:
            last = episodes[-1]
            last.update(end_s=ep["end_s"], q_min_ms=min(last["q_min_ms"], ep["q_min_ms"]),
                        q_max_ms=max(last["q_max_ms"], ep["q_max_ms"]), drops=last["drops"] + ep["drops"],
                        fragments=last["fragments"] + 1, _b=b)
        else:
            episodes.append(ep)
    in_episode = np.zeros(n, dtype=bool)
    for ep in episodes:
        in_episode[ep.pop("_a"):ep.pop("_b") + 1] = True
        ep["duration_s"] = ep["end_s"] - ep["start_s"]
    return episodes, gt_bands.labels(in_episode, q_ms, q_lo)


# ── run access ────────────────────────────────────────────────────────────

def base_rtts(run: det_eval.Run) -> dict[str, float]:
    """Per client: two-way propagation (s) along its path from the scenario's link delays."""
    delay = {}
    for link in run.scenario.get("links", []):
        a, b = link["from"], link["to"]
        delay[(a, b)] = (link.get("forward") or {}).get("delay_ms", 0.0)
        delay[(b, a)] = (link.get("reverse") or {}).get("delay_ms", 0.0)
    return {s: sum(delay.get(h, 0.0) + delay.get(h[::-1], 0.0) for h in det_eval.path_hops(run, run.pub, s)) / 1000
            for s in run.subs}


def router_egresses(run: det_eval.Run) -> list[tuple[tuple[str, str], Path]]:
    """Every sampled router egress: (hop, 25 ms CSV)."""
    topology = load_topology(run.path / "topology.yaml")
    out = []
    for edge in edge_interfaces(topology):
        for hop, iface in (((edge.a, edge.b), edge.a_iface), ((edge.b, edge.a), edge.b_iface)):
            path = run.path / "router-metrics" / hop[0] / f"{iface}.csv"
            if path.exists():
                out.append((hop, path))
    return out


@lru_cache(maxsize=None)
def _samples(run_dir: Path, csv: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    return load_samples(det_eval.Run(run_dir), csv)


@lru_cache(maxsize=None)
def _bursts(run_dir: Path) -> tuple[dict, ...]:
    return tuple(det_eval.burst_truth(det_eval.Run(run_dir)))


def load_samples(run: det_eval.Run, csv: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray]:
    """(t, backlog_bytes, tx_bytes or None, drops per interval) inside [0, duration - SHUTDOWN_S].
    The 25 ms CSV holds per-interval deltas; the queue-only CSV holds the cumulative drop counter."""
    rows = det_eval.rows(csv)
    t = np.array([run.t_mono_us(int(r["timestamp_mono_ns"]) / 1000) for r in rows])
    keep = (t >= 0) & (t <= run.duration - SHUTDOWN_S)
    backlog = np.array([int(r["queue_backlog_bytes"]) for r in rows], dtype=float)[keep]
    drops = np.array([int(r["drops"]) for r in rows], dtype=float)
    if rows and "transmitted_bytes" in rows[0]:
        tx = np.array([int(r["transmitted_bytes"]) for r in rows], dtype=float)[keep]
    else:
        tx, drops = None, np.diff(drops, prepend=drops[:1]).clip(min=0)
    return t[keep], backlog, tx, drops[keep]


def run_truth(run: det_eval.Run, p: Params, fine: bool = False) -> tuple[list[dict], list[dict]]:
    """GT1 episodes and label spans of every sampled egress of a run (fine: the 5 ms queue-only CSVs).
    A sample's label covers (t[i-1], t[i]]."""
    caps = det_eval.capacity_series(run)
    resolved = p.resolve(max(base_rtts(run).values(), default=0.0))
    out, labs = [], []
    for hop, csv in router_egresses(run):
        if fine:
            csv = csv.with_name(csv.stem + "-queue.csv")
            if not csv.exists():
                continue
        t, backlog, tx, drops = _samples(run.path, csv)
        eps, lab = gt1_core(t, backlog, tx, caps[hop], resolved, drops)
        hop_id = f"{hop[0]}->{hop[1]}"
        for ep in eps:
            if ep["end_s"] >= WARMUP_S:
                out.append({"hop": hop_id, "iface": csv.stem.removesuffix("-queue"),
                            **{k: round(v, 4) if isinstance(v, float) else v for k, v in ep.items()},
                            "interval_s": round(resolved.interval_s, 3), "source": "5ms" if fine else "25ms"})
        if len(t) > 1:
            labs += [{"hop": hop_id, "t_start": round(a, 4), "t_end": round(b, 4), "label": x}
                     for a, b, x in gt_bands.spans(t[:-1], t[1:], lab[1:])]
    return sorted(out, key=lambda e: (e["start_s"], e["hop"])), labs


def run_episodes(run: det_eval.Run, p: Params, fine: bool = False) -> list[dict]:
    """GT1 episodes of every sampled egress of a run (fine: the 5 ms queue-only CSVs)."""
    return run_truth(run, p, fine)[0]


def score(run_dir: Path, p: Params) -> None:
    run = det_eval.Run(run_dir)
    out = run_dir / "truth"
    eps, labs = run_truth(run, p)
    det_eval.write_csv(out / "gt1.csv", eps)
    det_eval.write_csv(out / "gt1-labels.csv", labs)
    fine = run_episodes(run, p, fine=True)
    if fine:
        det_eval.write_csv(out / "gt1-5ms.csv", fine)
    print(f"{run_dir.name}: aqm={run.aqm} episodes={len(eps)}" + (f" episodes_5ms={len(fine)}" if fine else ""))


# ── validation ────────────────────────────────────────────────────────────

CALM = ("calm030", "calm065", "calm090", "calmcbr090")
BURST_RECOVERY_S = det_eval.BURST_RECOVERY_S
ONSET_SLACK_S = 0.05  # an episode may start this much before the event is logged as applied


def match_bursts(run: det_eval.Run, eps: list[dict]) -> list[dict]:
    """Per injected event (det_eval.burst_truth): episodes on its hop that are
    running at its start or begin during it (n_episodes; > 1 = fragmented), lag
    of the earliest one, and episodes beginning in the recovery after it."""
    out = []
    for b in _bursts(run.path):
        hop = f"{b['hop'][0]}->{b['hop'][1]}"
        during = [e for e in eps if e["hop"] == hop and e["start_s"] <= b["end"] and e["end_s"] >= b["start"] - ONSET_SLACK_S]
        recovery = [e for e in eps if e["hop"] == hop and b["end"] < e["start_s"] <= b["end"] + BURST_RECOVERY_S]
        out.append({"start": b["start"], "end": b["end"], "kind": b["kind"], "hop": hop, "u_agg": b["u_agg"],
                    "n_episodes": len(during), "n_recovery": len(recovery),
                    "lag_s": min(e["start_s"] for e in during) - b["start"] if during else None})
    return out


def extra_episodes(eps: list[dict], matches: list[dict]) -> list[dict]:
    """Episodes touching no event window [start - slack, end + recovery] on their hop."""
    return [e for e in eps if not any(e["hop"] == b["hop"] and e["start_s"] <= b["end"] + BURST_RECOVERY_S
                                      and e["end_s"] >= b["start"] - ONSET_SLACK_S for b in matches)]


def _q(v: list[float], q: float) -> str:
    v = sorted(v)
    return f"{v[min(len(v) - 1, int(q * len(v)))]:.3f}" if v else "-"


def _table(header: list[str], rows: list[list]) -> str:
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
                     + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def calm_table(runs: list[det_eval.Run], p: Params) -> str:
    rows = []
    for run in runs:
        eps = run_episodes(run, p)
        by_hop = defaultdict(list)
        for e in eps:
            by_hop[e["hop"]].append(e)
        rows.append([run.path.name, run.aqm, len(eps),
                     "; ".join(f"{h}: {len(v)} ep, dur p50 {_q([e['duration_s'] for e in v], 0.5)} max {max(e['duration_s'] for e in v):.3f} s, "
                               f"q_max p50 {_q([e['q_max_ms'] for e in v], 0.5)} ms, with drops {sum(1 for e in v if e['drops'])}, "
                               f"start phase mod 1 s {_phase(v)}"
                               for h, v in sorted(by_hop.items())) or "-"])
    return _table(["run", "aqm", "episodes", "per hop"], rows)


def _phase(eps: list[dict]) -> str:
    """Dominant start time modulo the 1 s GOP: '0.8 s (84 %)' when episodes are keyframe-locked."""
    counts = defaultdict(int)
    for e in eps:
        counts[round(e["start_s"] % 1.0, 1) % 1.0] += 1
    phase, n = max(counts.items(), key=lambda kv: kv[1])
    return f"{phase:.1f} s ({100 * n / len(eps):.0f} %)"


def extra_table(runs: list[det_eval.Run], p: Params) -> str:
    """Episodes outside every event window, per run and hop: how long, how deep, with loss, keyframe-locked?"""
    rows = []
    for run in runs:
        eps = run_episodes(run, p)
        extra = extra_episodes(eps, match_bursts(run, eps))
        by_hop = defaultdict(list)
        for e in extra:
            by_hop[e["hop"]].append(e)
        for hop, v in sorted(by_hop.items()):
            rows.append([run.path.name, run.aqm, hop, len(v), _q([e["duration_s"] for e in v], 0.5),
                         _q([e["duration_s"] for e in v], 0.9), f"{max(e['duration_s'] for e in v):.3f}",
                         _q([e["q_max_ms"] for e in v], 0.5), sum(1 for e in v if e["drops"]), _phase(v)])
    return _table(["run", "aqm", "hop", "extra", "dur p50 (s)", "dur p90", "dur max", "q_max p50 (ms)", "with drops", "start phase"], rows)


def burst_table(runs: list[det_eval.Run], p: Params) -> tuple[str, dict]:
    """Per run: events, caught (>= 1 episode or covered), missed, fragmented, lag quantiles."""
    rows, agg = [], defaultdict(lambda: defaultdict(list))
    for run in runs:
        eps = run_episodes(run, p)
        m = match_bursts(run, eps)
        if not m:
            continue
        lags = [x["lag_s"] for x in m if x["lag_s"] is not None]
        caught = sum(1 for x in m if x["n_episodes"])
        frag = sum(1 for x in m if x["n_episodes"] > 1)
        recovery = sum(x["n_recovery"] for x in m)
        extra = extra_episodes(eps, m)
        rows.append([run.path.name, run.aqm, len(m), caught, len(m) - caught, frag, recovery, len(extra),
                     _q(lags, 0.5), _q(lags, 0.9), _q(lags, 1.0)])
        scn = det_eval.scenario_name(run.path)
        agg[scn]["events"].append(len(m)); agg[scn]["caught"].append(caught); agg[scn]["extra"].append(len(extra))
    return _table(["run", "aqm", "events", "caught", "missed", "fragmented", "recovery episodes", "extra episodes",
                   "lag p50", "lag p90", "lag max"], rows), agg


def split_table(runs: list[det_eval.Run], p: Params) -> str:
    """25 ms vs 5 ms on the same run: counts and start-time differences of matched episodes."""
    rows = []
    for run in runs:
        coarse, fine = run_episodes(run, p), run_episodes(run, p, fine=True)
        if not fine:
            continue
        diffs, matched = [], 0
        for e in coarse:
            same = [f for f in fine if f["hop"] == e["hop"] and f["start_s"] <= e["end_s"] and f["end_s"] >= e["start_s"]]
            if same:
                matched += 1
                diffs.append(e["start_s"] - min(f["start_s"] for f in same))
        rows.append([run.path.name, run.aqm, len(coarse), len(fine), matched, len(fine) - sum(
            1 for f in fine if any(e["hop"] == f["hop"] and f["start_s"] <= e["end_s"] and f["end_s"] >= e["start_s"] for e in coarse)),
            _q(diffs, 0.5), _q(diffs, 0.9), _q([abs(d) for d in diffs], 1.0)])
    return _table(["run", "aqm", "episodes 25 ms", "episodes 5 ms", "matched", "5 ms only", "start diff p50 (s)", "p90", "max |diff|"], rows)


def sweep_table(calm_runs: list[det_eval.Run], burst_runs: list[det_eval.Run]) -> str:
    rows = []
    base = Params()
    variants = [base]
    for key, values in SWEEP.items():
        for v in values:
            cand = Params(**{**base.__dict__, key: v})
            if cand != base:
                variants.append(cand)
    for p in variants:
        calm_eps = sum(len(run_episodes(r, p)) for r in calm_runs)
        events = caught = frag = extra = 0
        lags = []
        for r in burst_runs:
            eps = run_episodes(r, p)
            m = match_bursts(r, eps)
            events += len(m)
            caught += sum(1 for x in m if x["n_episodes"])
            frag += sum(1 for x in m if x["n_episodes"] > 1)
            lags += [x["lag_s"] for x in m if x["lag_s"] is not None]
            extra += len(extra_episodes(eps, m))
        rows.append([p.tag(), calm_eps, f"{caught}/{events}", frag, extra, _q(lags, 0.5), _q(lags, 0.9)])
    return _table(["params", "calm episodes", "events caught", "fragmented", "extra episodes", "lag p50", "lag p90"], rows)


INTERVAL_CHOICES = (0.1, 0.15, 0.2)


def interval_table(runs: list[det_eval.Run]) -> str:
    """Per scenario and AQM, the INTERVAL candidates side by side: episodes in calm
    runs, events caught / fragmented and episodes outside every event window."""
    cells = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0]))  # calm eps, events, caught, frag, extra
    for run in runs:
        key = (det_eval.scenario_name(run.path), run.aqm)
        for iv in INTERVAL_CHOICES:
            eps = run_episodes(run, Params(interval_s=iv))
            c = cells[key][iv]
            m = match_bursts(run, eps)
            if m:
                c[1] += len(m)
                c[2] += sum(1 for x in m if x["n_episodes"])
                c[3] += sum(1 for x in m if x["n_episodes"] > 1)
                c[4] += len(extra_episodes(eps, m))
            else:
                c[0] += len(eps)
    rows = []
    for (scn, aqm), by_iv in sorted(cells.items()):
        row = [scn, aqm]
        for iv in INTERVAL_CHOICES:
            calm_eps, events, caught, frag, extra = by_iv[iv]
            row.append(f"{caught}/{events} caught, {frag} frag, {extra} extra" if events else f"{calm_eps} episodes")
        rows.append(row)
    return _table(["scenario", "aqm"] + [f"INTERVAL {iv * 1000:g} ms" for iv in INTERVAL_CHOICES], rows)


def report(campaign: Path, p: Params) -> str:
    runs = [det_eval.Run(d) for d in sorted(campaign.iterdir()) if (d / "events.csv").exists()]
    calm = [r for r in runs if det_eval.scenario_name(r.path) in CALM]
    bursty = [r for r in runs if _bursts(r.path)]
    pfifo_bursts = [r for r in bursty if r.aqm == "pfifo"]
    rtts = {det_eval.scenario_name(r.path): max(base_rtts(r).values()) for r in runs}
    auto = ("; interval auto = max(" + f"{INTERVAL_MIN_S:g} s, largest base RTT) -> "
            + ", ".join(f"{k} {max(INTERVAL_MIN_S, v):.3f} s" for k, v in sorted(rtts.items()))) if p.interval_s == "auto" else ""
    lines = [f"# GT1 validation: {campaign.name}", "", f"Params: {p.tag()}; MTU {p.mtu}; warm-up {WARMUP_S:g} s excluded{auto}", ""]
    if calm:
        lines += ["## 1. Calm runs (no injected event: a truth episode here is real congestion the scenario did not script (keyframe overflow, AQM drops), not an error; detector false alarms count in CLEAR time only)", "", calm_table(calm, p), ""]
    if bursty:
        lines += ["## 2. Injected events: one episode each (caught = an episode on the hop runs at the event start or begins "
                  "before its end; fragmented = more than one; recovery = episodes beginning within 2 s after the end; "
                  "extra = episodes touching no event window; lag = earliest episode start - event start, s)", ""]
        table, agg = burst_table(bursty, p)
        lines += [table, "", "Per scenario (all AQMs): " + "; ".join(
            f"{s} {sum(v['caught'])}/{sum(v['events'])} caught, {sum(v['extra'])} extra" for s, v in sorted(agg.items())), "",
            "### 2b. Extra episodes (outside every event window)", "", extra_table(bursty, p), ""]
    split = split_table(runs, p)
    if split.count("\n") > 1:
        lines += ["## 3. Sampling error: 25 ms vs 5 ms queue CSV (same run)", "", split, ""]
    if calm or pfifo_bursts:
        lines += ["## 5. Parameter sweep (calm runs: all AQMs; events: pfifo runs)", "", sweep_table(calm, pfifo_bursts), ""]
    lines += ["## 6. INTERVAL 100 / 150 / 200 ms per scenario and AQM (runs without injected events: episode count; "
              "with events: caught, fragmented, episodes outside every event window)", "", interval_table(runs), ""]
    text = "\n".join(lines)
    (campaign / "gt1-report.md").write_text(text)
    return text


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[0] not in {"score", "report"}:
        sys.exit(__doc__)
    cmd, rest, kw, dirs = argv[0], argv[1:], {}, []
    while rest:
        a = rest.pop(0)
        if a in {"--target", "--interval", "--util-th", "--merge-gap"}:
            v = rest.pop(0)
            key = {"--target": "target_ms", "--interval": "interval_s", "--util-th": "util_th", "--merge-gap": "merge_gap_s"}[a]
            kw[key] = v if v in {"auto", "interval"} else float(v)
        else:
            dirs.append(Path(a))
    p = Params(**kw)
    for d in dirs:
        if cmd == "score":
            score(d, p)
        else:
            print(report(d, p))


if __name__ == "__main__":
    main(sys.argv[1:])
