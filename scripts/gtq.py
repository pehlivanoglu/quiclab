#!/usr/bin/env python3
"""GT-Q: constraining-queue episodes per flow, from per-packet router traces;
GT-H: the GT-Q episodes in which the flow misses the player's latency budget.

    python3 scripts/gtq.py score .runs/<run> [...]     # <run>/truth/gtq*.csv, gth*.csv
    python3 scripts/gtq.py score --tolerate 5e-4 ...    # accept runs off only in enqueue pairing (tolerant())
    python3 scripts/gtq.py summary .runs/<campaign>     # <campaign>/gtq-health-summary.{csv,md}

Spec: "Ground Truth and Scoring Spec, final" v1.2, sections 3.1-3.7. GT1 / GT2 / GT3
are untouched; GT-Q and GT-H are separate outputs next to them. Offline only: a
pure function of the run's logs and scenario config.

Inputs: router-trace/<iface>-packets.csv (quiclab/router_trace.py), the run's
topology / scenario / events.csv, publishers/<pub>/<sub>-pkts.csv and -pktacks.csv
(t_obs), clients/<sub>-frames.csv plus the sender's frames / drops (GT-H).

Per traced resource r (a bottleneck egress) and video flow f:
  tau(t) = 8 MTU / C_r(t)   (C from the scenario's applied link events)
  W      = max(largest base RTT of the flows through r, frame interval of f)
  sojourn sequence: every packet dequeued at r (shared queue: pfifo, RED, PIE,
    CoDel), or only f's own sub-queue (fq_codel: the pinned flow id when
    skb->priority carries it, else reciprocal_scale(skb->hash, 1024); other
    flows' packets in that sub-queue are included and flagged as a collision)
  busy run: consecutive dequeued packets with sojourn > tau; interval
    [t_enq first busy, t_deq of the next non-busy packet]
  standing interval: a busy run lasting >= W; drop interval: [t_d, t_d + W]
    per drop of f's packets at r; union, merged across gaps < W; kept when f
    enqueued at least one packet at r inside it
  gray: busy runs of [W/2, W) without an f drop, and episodes with no overlap
    with the episodes at threshold 2 tau
Direction: r is forward for f when f's video packets pass it, reverse when only
f's ACKs do (reverse episodes are tagged and are never positives).
t_obs (section 6.3): (b) the first ACK that acknowledges the first affected
packet (router packet matched to its QUIC packet number by flow + order + size),
when the flow's match rate >= 0.95; (a) otherwise: t_deq + base OWD r -> client
+ base delay client -> sender. Both are reported where both exist.
GT-H(B): a frame is a deadline miss when it is not completely received by
t_gen + B (send_us / recv_us, never late_us); frames the sender head-dropped
count as misses at t_gen + B. An episode is harmful when a frame generated in
[t0 - W, t1 + d_obs + W] misses; t_harm = the earliest harm instant.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
import det_eval  # noqa: E402
from quiclab import router_trace as rt  # noqa: E402

MTU_BYTES = 1500
BUDGETS_MS = (600, 300, 1000)   # primary first
PRIMARY_MS = 600
STIM_BEFORE_W = 3.0             # t_stim: latest stimulus in [t0 - 3 W, t0 + W]
FQ_AQMS = {"fq_codel"}
OWN_FLOW_AQMS = {"cake"}        # cake's set-associative hash is not reproduced: f's own packets only
FQ_FLOWS = 1024
FQ_MAJOR = 0x20                 # the AQM leaf handle 20: (quiclab.orchestrator.shaping)
FRAME_FPS_DEFAULT = 30

EPISODE_FIELDS = ("flow", "episode_id", "resource", "direction", "t0", "t1", "duration", "kind",
                  "max_sojourn_ms", "median_sojourn_ms", "f_drops", "multi", "t_stim", "W_ms", "tau_ms",
                  "aqm", "t_ref", "t_obs", "t_obs_method", "d_obs_ms", "t_obs_b_minus_a_ms",
                  *(f"{k}_{b}" for b in BUDGETS_MS for k in ("harmful", "t_harm")))


@dataclass(frozen=True)
class Params:
    w_scale: float = 1.0      # sensitivity: W x {0.5, 1, 2}
    tau_scale: float = 1.0    # sensitivity: tau x {1, 2}
    gray_lo: float = 0.5      # gray busy runs: [gray_lo W, W)

    def tag(self) -> str:
        return f"W x{self.w_scale:g}, tau x{self.tau_scale:g}, gray [{self.gray_lo:g} W, W)"


# ── core (pure, on arrays in seconds) ─────────────────────────────────────

def busy_runs(t_enq: np.ndarray, t_deq: np.ndarray, tau: np.ndarray) -> list[tuple[float, float, int, int]]:
    """Maximal runs of consecutive busy packets (sojourn > tau) in dequeue order:
    (start, end, first index, last index). start = t_enq of the first busy packet;
    end = when the queue drained: t_deq of the first non-busy packet after the run,
    but no later than t_deq of the last busy packet + tau. (Spec 3.4 says the next
    packet's t_deq; read literally that stretches a run over the idle gap until the
    next arrival, e.g. a whole frame interval on a lightly loaded link.)"""
    busy = (t_deq - t_enq) > tau
    if not busy.any():
        return []
    edges = np.diff(np.concatenate(([0], busy.astype(np.int8), [0])))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) - 1
    n = len(t_deq)
    return [(float(t_enq[i]), float(min(t_deq[j + 1], t_deq[j] + tau[j]) if j + 1 < n else t_deq[j] + tau[j]),
             int(i), int(j)) for i, j in zip(starts, ends)]


def merge(intervals: list[tuple[float, float]], gap: float) -> list[tuple[float, float]]:
    """Union of intervals, joining those separated by less than `gap`."""
    out: list[list[float]] = []
    for a, b in sorted(intervals):
        if out and a - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def _overlaps(a: float, b: float, others: list[tuple[float, float]]) -> bool:
    return any(x < b and a < y for x, y in others)


def _intervals(t_enq, t_deq, tau, drops, W):
    runs = busy_runs(t_enq, t_deq, tau)
    standing = [(a, b) for a, b, _, _ in runs if b - a >= W]
    dropped = [(d, d + W) for d in drops]
    return runs, standing, dropped


def queue_episodes(t_enq: np.ndarray, t_deq: np.ndarray, tau: np.ndarray, f_drops: np.ndarray,
                   f_enq: np.ndarray, W: float, p: Params = Params()) -> tuple[list[dict], list[dict]]:
    """GT-Q episodes and gray intervals of one (resource, flow).

    t_enq / t_deq / tau: the sojourn sequence in dequeue order (s, tau per packet);
    f_drops: drop times of f's packets at r; f_enq: enqueue times of f's packets (presence)."""
    order = np.argsort(t_deq, kind="stable")
    t_enq, t_deq, tau = t_enq[order], t_deq[order], tau[order]
    f_drops = np.sort(np.asarray(f_drops, dtype=float))
    f_enq = np.sort(np.asarray(f_enq, dtype=float))
    runs, standing, dropped = _intervals(t_enq, t_deq, tau, f_drops, W)
    merged = merge(standing + dropped, W)

    def present(a: float, b: float) -> bool:
        i = np.searchsorted(f_enq, a, side="left")
        return i < len(f_enq) and f_enq[i] <= b

    _, standing2, _ = _intervals(t_enq, t_deq, 2 * tau, f_drops, W)
    merged2 = merge(standing2 + dropped, W)
    episodes, gray = [], []
    for a, b in merged:
        if not present(a, b):
            continue
        n_drop = int(((f_drops >= a) & (f_drops <= b)).sum())
        has_standing = _overlaps(a, b, standing)
        kind = "both" if has_standing and n_drop else "standing" if has_standing else "drop"
        if not _overlaps(a, b, merged2):
            gray.append({"t_start": a, "t_end": b, "why": "below 2 tau"})
            continue
        episodes.append({"t0": a, "t1": b, "kind": kind, "f_drops": n_drop})
    for a, b, _, _ in runs:
        dur = b - a
        if p.gray_lo * W <= dur < W and not ((f_drops >= a) & (f_drops <= b)).any() \
                and not _overlaps(a, b, [(e["t0"], e["t1"]) for e in episodes]):
            gray.append({"t_start": a, "t_end": b, "why": "short busy run"})
    return episodes, sorted(gray, key=lambda g: g["t_start"])


def fq_index(prio: np.ndarray, hashes: np.ndarray) -> np.ndarray:
    """fq_codel sub-queue per packet: skb->priority 20:<minor> (1..1024) picks
    flow minor - 1, otherwise reciprocal_scale(skb->hash, 1024)."""
    prio = prio.astype(np.int64)
    major, minor = prio >> 16, prio & 0xFFFF
    pinned = (major == FQ_MAJOR) & (minor >= 1) & (minor <= FQ_FLOWS)
    hashed = (hashes.astype(np.uint64) * np.uint64(FQ_FLOWS)) >> np.uint64(32)
    return np.where(pinned, minor - 1, hashed.astype(np.int64))


# ── frames (GT-H) ─────────────────────────────────────────────────────────

def frame_table(run: det_eval.Run, sid: str) -> pd.DataFrame:
    """One row per frame the sender produced for sid: t_gen (s), t_recv (s, nan =
    never completely received), dropped (sender head drop)."""
    pub_dir = run.path / "publishers" / run.pub
    sent = pd.read_csv(pub_dir / f"{sid}-frames.csv") if (pub_dir / f"{sid}-frames.csv").exists() else pd.DataFrame()
    drops = pd.read_csv(pub_dir / f"{sid}-drops.csv") if (pub_dir / f"{sid}-drops.csv").exists() else pd.DataFrame()
    recv_path = run.path / "clients" / f"{sid}-frames.csv"
    recv = pd.read_csv(recv_path) if recv_path.exists() else pd.DataFrame(columns=["index", "send_us", "recv_us"])
    rows = []
    if len(sent):
        rows.append(pd.DataFrame({"index": sent["index"], "gen_us": sent["send_us"], "dropped": False}))
    if len(drops):
        rows.append(pd.DataFrame({"index": drops["index"], "gen_us": drops["t_us"] - drops["age_us"], "dropped": True}))
    if len(recv):  # a frame the client has and the sender log lacks (sender log cut short)
        rows.append(pd.DataFrame({"index": recv["index"], "gen_us": recv["send_us"], "dropped": False}))
    if not rows:
        return pd.DataFrame(columns=["index", "t_gen", "t_recv", "dropped"])
    frames = pd.concat(rows).sort_values(["index", "dropped"], ascending=[True, False])
    frames = frames.drop_duplicates("index", keep="first").set_index("index")
    got = recv.drop_duplicates("index").set_index("index")["recv_us"] if len(recv) else pd.Series(dtype=float)
    out = pd.DataFrame({"t_gen": [run.t_unix_us(v) for v in frames["gen_us"]],
                        "dropped": frames["dropped"].to_numpy()}, index=frames.index)
    out["t_recv"] = [run.t_unix_us(got[i]) if i in got.index and not d else math.nan
                     for i, d in zip(out.index, out["dropped"])]
    return out.reset_index()


def deadline_misses(frames: pd.DataFrame, budget_s: float, horizon: float) -> np.ndarray:
    """Harm instants t_gen + B of the frames that miss B. A frame never received
    counts only when t_gen + B lies before the horizon (end of the client's log)."""
    t_gen, t_recv = frames["t_gen"].to_numpy(dtype=float), frames["t_recv"].to_numpy(dtype=float)
    due = t_gen + budget_s
    miss = np.where(np.isnan(t_recv), due <= horizon, t_recv > due)
    return np.sort(due[miss])


def harm(t0: float, t1: float, c_pre: float, c_post: float, frames: pd.DataFrame, budget_s: float,
         horizon: float) -> float | None:
    """Earliest harm instant of a miss among frames generated in [t0 - c_pre, t1 + c_post]."""
    t_gen = frames["t_gen"].to_numpy(dtype=float)
    sel = frames[(t_gen >= t0 - c_pre) & (t_gen <= t1 + c_post)]
    due = deadline_misses(sel, budget_s, horizon)
    return float(due[0]) if len(due) else None


# ── run model ─────────────────────────────────────────────────────────────

def _delays(run: det_eval.Run) -> dict[tuple[str, str], float]:
    """One-way propagation (s) per directed hop at t=0 (as gt1.base_rtts)."""
    delay = {}
    defaults = run.scenario.get("link_defaults") or {}
    for link in run.scenario.get("links", []):
        a, b = link["from"], link["to"]
        delay[(a, b)] = ((link.get("forward") or {}).get("delay_ms",
                         (defaults.get("forward") or {}).get("delay_ms", 0.0)) or 0.0) / 1000
        delay[(b, a)] = ((link.get("reverse") or {}).get("delay_ms",
                         (defaults.get("reverse") or {}).get("delay_ms", 0.0)) or 0.0) / 1000
    return delay


def _rtt(run: det_eval.Run, delay, a: str, b: str) -> float:
    return sum(delay.get(h, 0.0) + delay.get(h[::-1], 0.0) for h in det_eval.path_hops(run, a, b))


def delay_series(run: det_eval.Run, hop: tuple[str, str]) -> list[tuple[float, float]]:
    """Netem delay (s) of one directed hop over time: t=0 value, then every applied
    link event that set delay_ms (events.csv applied times, as capacity_series)."""
    a, b = hop
    out = [(0.0, _delays(run).get(hop, 0.0))]
    for e in run.events:
        if e["event"] == "link" and e["status"] == "applied" and "delay_ms=" in e["detail"]:
            target, direction = e["target"].split(":")
            x, y = target.split("->")
            if ((x, y) if direction == "forward" else (y, x)) == (a, b):
                out.append((float(e["applied_s"]), float(e["detail"].split("delay_ms=")[1].split()[0]) / 1000))
    return sorted(out)


def flows_through(run: det_eval.Run, hop: tuple[str, str]) -> list[tuple[str, str]]:
    """(src, dst) pairs whose path crosses hop: video (publisher -> subscriber) and
    cross traffic (every traffic sender -> receiver pair)."""
    pairs = [(run.topology["subscribers"][s].get("connects_to", run.pub), s) for s in run.subs]
    traffic = run.topology.get("traffic") or {}
    senders = [e["id"] for e in traffic.get("senders", [])]
    receivers = [e["id"] for e in traffic.get("receivers", [])]
    pairs += [(a, b) for a in senders for b in receivers]
    return [(a, b) for a, b in pairs if hop in det_eval.path_hops(run, a, b)]


def rtt_max(run: det_eval.Run, hop: tuple[str, str]) -> float:
    delay = _delays(run)
    return max((_rtt(run, delay, a, b) for a, b in flows_through(run, hop)), default=0.0)


def frame_interval(run: det_eval.Run, sid: str) -> float:
    pub = run.topology["subscribers"][sid].get("connects_to", run.pub)
    return 1.0 / float((run.topology["publishers"].get(pub) or {}).get("fps", FRAME_FPS_DEFAULT))


def stimuli(run: det_eval.Run) -> list[float]:
    """Scripted stimulus times t_stim (run s): link / aqm / flow / ppbp events and burst starts."""
    out = []
    for e in run.scenario.get("events", []) or []:
        if e.get("type") in ("link", "aqm", "flow", "ppbp"):
            out.append(float(e["at_s"]))
        elif e.get("type") == "bursts":
            out += [float(e["at_s"]) + float(b.get("start_s", 0.0)) for b in e.get("bursts", [])]
    return sorted(out)


def aqm_of(run: det_eval.Run, hop: tuple[str, str]) -> tuple[str, bool]:
    """(AQM on the egress at t=0, whether an aqm event changes that router)."""
    router, peer = hop
    queue = (run.scenario.get("routers") or {}).get(router) or {}
    aqm = ((queue.get("egress") or {}).get(peer) or queue).get("aqm") or "none"
    changed = any(e.get("type") == "aqm" and e.get("router", router) == router
                  for e in run.scenario.get("events", []) or [])
    return aqm, changed


def loopbacks(run: det_eval.Run) -> dict[str, str]:
    from quiclab.config.schema import load_topology
    from quiclab.runtime import node_loopback_ips
    return node_loopback_ips(load_topology(run.path / "topology.yaml"))


def traced(run: det_eval.Run) -> list[tuple[str, tuple[str, str], Path]]:
    """(iface, hop, packets csv) of every traced egress."""
    meta = run.path / rt.TRACE_DIR / "interfaces.csv"
    if not meta.exists():
        return []
    out = []
    for row in det_eval.rows(meta):
        path = run.path / rt.TRACE_DIR / f"{row['iface']}-packets.csv"
        if path.exists():
            a, b = row["hop"].split("->")
            out.append((row["iface"], (a, b), path))
    return out


def tolerant(run_dir: Path, h: dict, share: float) -> tuple[bool, str]:
    """Explicit opt-in (gtq.py score --tolerate SHARE): accept a gt_q_invalid run when
    the tracer started and stopped cleanly, lost no event, every interface's rows equal
    the kernel counters, and only the enqueue pairing is off: residual (enq - deq - drop)
    and late nohit dequeues each <= SHARE of the interface's packets."""
    if h.get("tracer_started") != "1" or h.get("tracer_stopped_clean") != "1" or h.get("lost_events") != "0":
        return False, "tracer start / stop / lost events"
    counts = run_dir / rt.TRACE_DIR / "tracer-counts.csv"
    if not counts.exists():
        return False, "no tracer counts"
    worst = 0.0
    for r in det_eval.rows(counts):
        n = {k: int(v) for k, v in r.items() if v.lstrip("-").isdigit()}
        rows = (n["rows_dequeue"], n["rows_drop"], n["rows_nohit"])
        if rows != (n["n_deq"], n["n_drop"], n["n_nohit"]) or n["n_truncated"] or n["n_enq"] <= 0:
            return False, f"{r['iface']}: rows / counters / truncated"
        res = (n["n_enq"] - n["n_deq"] - n["n_drop"]) / n["n_enq"]
        late = n["nohit_late"] / max(1, n["n_deq"])
        if res < 0 or res > share or late > share:
            return False, f"{r['iface']}: residual {res:.1e} / late nohit {late:.1e} > {share:g}"
        worst = max(worst, res, late)
    return True, f"accepted with --tolerate {share:g} (worst pairing share {worst:.1e}); health: {h.get('invalid_reasons', '')}"


def validity(run_dir: Path, tolerate: float = 0.0) -> tuple[bool, str]:
    """GT-Q is usable unless the run is gt_q_invalid (health file), or, without a
    health file, the tracer counters fail the identity / show lost events.
    tolerate > 0: see tolerant()."""
    h = rt.read_health(run_dir)
    if h:
        if h.get("gtq_logging") == "0":
            return False, "GT-Q logging off"
        if h.get("gt_q_invalid") == "1" and tolerate > 0:
            return tolerant(run_dir, h, tolerate)
        return h.get("gt_q_invalid") != "1", h.get("invalid_reasons", "")
    counts = run_dir / rt.TRACE_DIR / "tracer-counts.csv"
    if not counts.exists():
        return False, "no router trace"
    for r in det_eval.rows(counts):
        row = {k: int(v) if v.lstrip("-").isdigit() else v for k, v in r.items()}
        ok, why = rt.identity(row)
        if not ok or row["lost_events"] != 0:
            return False, why or "lost tracer events"
    return True, ""


# ── t_obs ─────────────────────────────────────────────────────────────────

class Obs:
    """t_obs for one (resource, flow): ACK mapping (b) and config fallback (a)."""

    def __init__(self, run: det_eval.Run, sid: str, hop: tuple[str, str], fpk: pd.DataFrame):
        pub = run.topology["subscribers"][sid].get("connects_to", run.pub)
        delay = _delays(run)
        hops = det_eval.path_hops(run, pub, sid)
        after = hops[hops.index(hop) + 1:] if hop in hops else []
        self.d_a = sum(delay.get(h, 0.0) for h in after) + sum(delay.get(h[::-1], 0.0) for h in hops)
        self.run, self.match_rate, self.pn_ack = run, None, None
        pkts = run.path / "publishers" / pub / f"{sid}-pkts.csv"
        acks = run.path / "publishers" / pub / f"{sid}-pktacks.csv"
        if pkts.exists() and acks.exists() and len(fpk):
            s = rt.read_sender_packets(pkts)
            arrival = "t_arr_ns" if "t_arr_ns" in fpk else "t_enq_ns"
            order = fpk[fpk["len"] >= rt.MATCH_MIN_LEN].sort_values(arrival, kind="stable")
            idx, self.match_rate = rt.match_flow((order[arrival] // 1000).tolist(), order["len"].tolist(),
                                                 s["send_mono_us"].tolist(), s["size"].tolist())
            if len(s):
                first = rt.first_ack_us(acks, int(s["pn"].max()))
                pns = s["pn"].to_numpy()
                ack_us = np.array([first[pns[k]] if k >= 0 else -1 for k in idx], dtype=np.int64)
                self.pn_ack = pd.Series(ack_us, index=order.index)

    @property
    def trusted(self) -> bool:
        return self.match_rate is not None and self.match_rate >= rt.MATCH_TRUST

    def at(self, affected: pd.DataFrame, t_ref: float) -> tuple[float, str, float | None]:
        """(t_obs, method, b - a in s or None) for the first affected packets (router rows, t_deq order)."""
        a = t_ref + self.d_a
        b = None
        if self.pn_ack is not None:
            for i in affected.index[:200]:
                us = self.pn_ack.get(i, -1)
                if us >= 0:
                    b = self.run.t_mono_us(us)
                    break
        if b is not None and self.trusted:
            return b, "ack", b - a
        method = "config" if self.match_rate is None else "config (match rate low)" if not self.trusted else "config (no ack)"
        return a, method, (b - a) if b is not None else None


# ── per run ───────────────────────────────────────────────────────────────

def run_truth(run: det_eval.Run, p: Params = Params()) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """(episodes, gray, params rows, frame-miss rows) of every traced resource x video flow."""
    ips = loopbacks(run)
    caps = det_eval.capacity_series(run)
    stim = stimuli(run)
    horizon_end = run.duration - det_eval.SHUTDOWN_S
    episodes, gray, params = [], [], []
    for iface, hop, path in traced(run):
        table = rt.read_packets(path)
        to_s = lambda ns: (ns.astype(np.int64) - run.epoch_mono_ns) / 1e9  # noqa: E731
        # Netem on the egress (delay only, see mininet_backend.gtq_trace_interfaces): a packet
        # is queued from t_enq + delay(t_enq). t_arr_ns keeps the raw arrival for the sender match.
        delays = delay_series(run, hop)
        table["t_arr_ns"] = table["t_enq_ns"]
        if any(d for _, d in delays):
            has = table["t_enq_ns"] >= 0
            extra = rt.step_at(delays, to_s(table.loc[has, "t_enq_ns"].to_numpy())) * 1e9
            table.loc[has, "t_enq_ns"] = table.loc[has, "t_enq_ns"] + extra.astype(np.int64)
        deq = table[table["kind"] == "dequeue"]
        aqm, aqm_changed = aqm_of(run, hop)
        rtt = rtt_max(run, hop)
        cap = caps.get(hop, [(0.0, math.inf)])
        when, mbps = np.array([c[0] for c in cap]), np.array([c[1] for c in cap])

        def tau_at(t: np.ndarray) -> np.ndarray:
            c = mbps[np.clip(np.searchsorted(when, t, side="right") - 1, 0, len(cap) - 1)] * 1e6
            return 8 * MTU_BYTES / c * p.tau_scale

        index = fq_index(deq["prio"].to_numpy(), deq["hash"].to_numpy()) if aqm in FQ_AQMS else None
        tuples = deq["saddr"] + ">" + deq["daddr"] + ":" + deq["sport"].astype(str) + ">" + deq["dport"].astype(str)
        for sid in run.subs:
            pub = run.topology["subscribers"][sid].get("connects_to", run.pub)
            src, dst = ips[pub], ips[sid]
            fwd_all = table[(table["saddr"] == src) & (table["daddr"] == dst) & (table["proto"] == 17)]
            rev_all = table[(table["saddr"] == dst) & (table["daddr"] == src) & (table["proto"] == 17)]
            fpk, direction = (fwd_all, "forward") if len(fwd_all) else (rev_all, "reverse")
            if not len(fpk):
                continue
            W = max(rtt, frame_interval(run, sid)) * p.w_scale
            collision = ""
            if aqm in FQ_AQMS:
                mine = index[deq.index.get_indexer(fpk.index[fpk["kind"] == "dequeue"])]
                q = int(pd.Series(mine).mode().iloc[0]) if len(mine) else -1
                seq = deq[index == q]
                f_tuple = set(tuples.loc[fpk.index[fpk["kind"] == "dequeue"]])
                others = set(tuples.loc[seq.index]) - f_tuple
                collision = ";".join(sorted(others))
            elif aqm in OWN_FLOW_AQMS:
                seq, q = deq.loc[deq.index.intersection(fpk.index)], -1
            else:
                seq, q = deq, -1
            t_deq = to_s(seq["t_deq_ns"].to_numpy())
            t_enq = to_s(seq["t_enq_ns"].to_numpy())
            ok = seq["t_enq_ns"].to_numpy() >= 0
            t_deq, t_enq = t_deq[ok], t_enq[ok]
            fdrop = fpk[fpk["kind"] == "drop"]
            f_drops = to_s(fdrop["t_drop_ns"].to_numpy())
            f_enq = to_s(fpk.loc[fpk["t_enq_ns"] >= 0, "t_enq_ns"].to_numpy())
            eps, gr = queue_episodes(t_enq, t_deq, tau_at(t_deq), f_drops, f_enq, W, p)
            obs = Obs(run, sid, hop, fpk) if direction == "forward" else None
            fdeq = fpk[(fpk["kind"] == "dequeue") & (fpk["t_enq_ns"] >= 0)]
            f_t_deq = to_s(fdeq["t_deq_ns"].to_numpy())
            f_soj = f_t_deq - to_s(fdeq["t_enq_ns"].to_numpy())
            f_tau = tau_at(f_t_deq)
            for e in eps:
                inside = (f_t_deq >= e["t0"]) & (f_t_deq <= e["t1"])
                soj = f_soj[inside]
                affected = fdeq[inside & (f_soj > f_tau)]
                if len(affected):
                    t_ref = float(to_s(affected["t_deq_ns"].to_numpy()[:1])[0])
                else:  # drop-only: the first dropped packet of f
                    d = f_drops[(f_drops >= e["t0"]) & (f_drops <= e["t1"])]
                    t_ref = float(d[0]) if len(d) else e["t0"]
                if obs is not None:
                    t_obs, method, b_a = obs.at(affected, t_ref)
                    if not len(affected):
                        method = "config (drop only)"
                        t_obs, b_a = t_ref + obs.d_a, None
                else:
                    t_obs, method, b_a = math.nan, "reverse", None
                before = [s for s in stim if e["t0"] - STIM_BEFORE_W * W <= s <= e["t0"] + W]
                episodes.append({
                    "flow": sid, "resource": f"{hop[0]}->{hop[1]}", "iface": iface, "direction": direction,
                    "t0": e["t0"], "t1": e["t1"], "duration": e["t1"] - e["t0"], "kind": e["kind"],
                    "max_sojourn_ms": float(soj.max() * 1e3) if len(soj) else math.nan,
                    "median_sojourn_ms": float(np.median(soj) * 1e3) if len(soj) else math.nan,
                    "f_drops": e["f_drops"], "t_stim": before[-1] if before else math.nan,
                    "W_ms": W * 1e3, "tau_ms": float(tau_at(np.array([e["t0"]]))[0] * 1e3), "aqm": aqm,
                    "t_ref": t_ref, "t_obs": t_obs, "t_obs_method": method,
                    "d_obs_ms": (t_obs - t_ref) * 1e3 if not math.isnan(t_obs) else math.nan,
                    "t_obs_b_minus_a_ms": b_a * 1e3 if b_a is not None else math.nan, "_W": W})
            gray += [{"flow": sid, "resource": f"{hop[0]}->{hop[1]}", "direction": direction, **g} for g in gr]
            params.append({"resource": f"{hop[0]}->{hop[1]}", "iface": iface, "flow": sid, "direction": direction,
                           "aqm": aqm, "aqm_changed": int(aqm_changed), "W_ms": round(W * 1e3, 3),
                           "rtt_max_ms": round(rtt * 1e3, 3), "netem_delay_ms_t0": round(delays[0][1] * 1e3, 3), "frame_interval_ms": round(frame_interval(run, sid) * 1e3, 3),
                           "tau_ms_t0": round(float(tau_at(np.array([0.0]))[0]) * 1e3, 4),
                           "tau_ms_min": round(float(8 * MTU_BYTES / (mbps.max() * 1e6) * p.tau_scale * 1e3), 4),
                           "tau_ms_max": round(float(8 * MTU_BYTES / (mbps.min() * 1e6) * p.tau_scale * 1e3), 4),
                           "sojourn_packets": len(t_deq), "fq_index": q, "fq_collision": collision,
                           "match_rate": "" if obs is None or obs.match_rate is None else round(obs.match_rate, 4),
                           "params": p.tag()})
    # multi: overlapping forward episodes of one flow on different resources
    by_flow = defaultdict(list)
    for e in episodes:
        if e["direction"] == "forward":
            by_flow[e["flow"]].append(e)
    for e in episodes:
        e["multi"] = int(e["direction"] == "forward" and any(
            o is not e and o["resource"] != e["resource"] and o["t0"] < e["t1"] and e["t0"] < o["t1"]
            for o in by_flow[e["flow"]]))
    # GT-H
    misses = []
    for sid in run.subs:
        mine = [e for e in episodes if e["flow"] == sid and e["direction"] == "forward"]
        try:
            frames = frame_table(run, sid)
        except (OSError, KeyError, pd.errors.ParserError):
            frames = pd.DataFrame(columns=["index", "t_gen", "t_recv", "dropped"])
        recv = frames["t_recv"].dropna()
        horizon = min(horizon_end, float(recv.max())) if len(recv) else horizon_end
        for e in mine:
            c_pre = e["_W"]
            c_post = (0.0 if math.isnan(e["d_obs_ms"]) else e["d_obs_ms"] / 1e3) + e["_W"]
            e["_collar"] = (e["t0"] - c_pre, e["t1"] + c_post)
            for b in BUDGETS_MS:
                t = harm(e["t0"], e["t1"], c_pre, c_post, frames, b / 1000, horizon) if len(frames) else None
                e[f"harmful_{b}"] = int(t is not None)
                e[f"t_harm_{b}"] = t if t is not None else math.nan
        for b in BUDGETS_MS:
            due = deadline_misses(frames, b / 1000, horizon) if len(frames) else np.array([])
            t_gen = due - b / 1000
            covered = np.zeros(len(due), dtype=bool)
            for e in mine:
                lo, hi = e["_collar"]
                covered |= (t_gen >= lo) & (t_gen <= hi)
            misses.append({"flow": sid, "budget_ms": b, "frames": len(frames), "misses": len(due),
                           "misses_in_episode": int(covered.sum()), "misses_outside": int((~covered).sum()),
                           "outside_rate": round(float((~covered).sum()) / len(frames), 6) if len(frames) else ""})
    for e in episodes:
        if e["direction"] != "forward":
            for b in BUDGETS_MS:
                e[f"harmful_{b}"], e[f"t_harm_{b}"] = 0, math.nan
    episodes.sort(key=lambda e: (e["flow"], e["t0"], e["resource"]))
    counter = defaultdict(int)
    for e in episodes:
        counter[e["flow"]] += 1
        e["episode_id"] = counter[e["flow"]]
    return episodes, gray, params, misses


def _fmt(v):
    if isinstance(v, float):
        return "" if math.isnan(v) else f"{v:.6f}".rstrip("0").rstrip(".") if abs(v) < 1e6 else f"{v:.3f}"
    return v


def write(path: Path, rows: list[dict], fields) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: _fmt(r.get(k, "")) for k in fields})


def score(run_dir: Path, p: Params = Params(), tolerate: float = 0.0) -> str:
    """Write GT-Q / GT-H for one run (truth/gtq*.csv, gth*.csv); invalid runs get
    truth/gtq-status.csv only. Returns a one-line summary."""
    out = run_dir / "truth"
    ok, why = validity(run_dir, tolerate)
    status = {"valid": int(ok), "reason": why, "params": p.tag(), "tolerate": tolerate}
    if not ok:
        write(out / "gtq-status.csv", [status], status)
        for name in ("gtq.csv", "gtq-gray.csv", "gtq-params.csv", "gth.csv", "gth-outside.csv"):
            (out / name).unlink(missing_ok=True)   # never leave a stale GT-Q next to an invalid run
        return f"{run_dir.name}: GT-Q not produced ({why})"
    run = det_eval.Run(run_dir)
    episodes, gray, params, misses = run_truth(run, p)
    write(out / "gtq.csv", episodes, EPISODE_FIELDS)
    write(out / "gtq-gray.csv", gray, ("flow", "resource", "direction", "t_start", "t_end", "why"))
    write(out / "gtq-params.csv", params, list(params[0]) if params else ("resource",))
    gth = [{"flow": e["flow"], "episode_id": e["episode_id"], "budget_ms": b, "primary": int(b == PRIMARY_MS),
            "t0": e["t0"], "t1": e["t1"], "t_harm": e[f"t_harm_{b}"]}
           for e in episodes for b in BUDGETS_MS if e.get(f"harmful_{b}")]
    write(out / "gth.csv", gth, ("flow", "episode_id", "budget_ms", "primary", "t0", "t1", "t_harm"))
    write(out / "gth-outside.csv", misses, ("flow", "budget_ms", "frames", "misses", "misses_in_episode",
                                            "misses_outside", "outside_rate"))
    status["episodes"] = sum(e["direction"] == "forward" for e in episodes)
    status["gth_600"] = sum(e.get("harmful_600", 0) for e in episodes)
    write(out / "gtq-status.csv", [status], status)
    return (f"{run_dir.name}: gtq_episodes={status['episodes']} gth600={status['gth_600']} "
            f"gray={len(gray)} reverse={sum(e['direction'] == 'reverse' for e in episodes)}")


# ── campaign health summary ───────────────────────────────────────────────

def summary(campaign: Path) -> str:
    """<campaign>/gtq-health-summary.csv (one row per run) and .md (invalid runs, worst CPU idle)."""
    rows = []
    for run_dir in sorted(p for p in campaign.iterdir() if (p / "events.csv").exists()):
        h = rt.read_health(run_dir)
        rows.append({"run": run_dir.name, "gtq_logging": h.get("gtq_logging", ""),
                     "gt_q_invalid": h.get("gt_q_invalid", "" if h else "no health file"),
                     "lost_events": h.get("lost_events", ""), "cpu_idle_min": h.get("cpu_idle_min", ""),
                     "cpu_idle_mean": h.get("cpu_idle_mean", ""), "match_rate_min": h.get("match_rate_min", ""),
                     "bytes_written": h.get("bytes_written", ""), "invalid_reasons": h.get("invalid_reasons", "")})
    write(campaign / "gtq-health-summary.csv", rows, rows[0] if rows else ("run",))
    invalid = [r for r in rows if r["gt_q_invalid"] == "1"]
    idle = [(float(r["cpu_idle_min"]), r["run"]) for r in rows if r["cpu_idle_min"] not in ("", None)]
    total = sum(int(r["bytes_written"]) for r in rows if str(r["bytes_written"]).isdigit())
    lines = [f"# GT-Q logging health: {campaign.name}", "",
             f"runs {len(rows)}, logging on {sum(r['gtq_logging'] == '1' for r in rows)}, "
             f"gt_q_invalid {len(invalid)}, no health file {sum(r['gt_q_invalid'] == 'no health file' for r in rows)}",
             f"worst CPU idle (min over the run): {min(idle)[0]:.3f} ({min(idle)[1]})" if idle else "worst CPU idle: -",
             f"bytes written by the new logging: {total / 1e9:.2f} GB", ""]
    if invalid:
        lines += ["| run | reasons |", "|---|---|"] + [f"| {r['run']} | {r['invalid_reasons']} |" for r in invalid]
    (campaign / "gtq-health-summary.md").write_text("\n".join(lines) + "\n")
    return lines[2]


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[0] not in ("score", "summary"):
        sys.exit(__doc__)
    tolerate = 0.0
    if "--tolerate" in argv:
        i = argv.index("--tolerate")
        tolerate = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    for d in argv[1:]:
        print(score(Path(d), tolerate=tolerate) if argv[0] == "score" else summary(Path(d)))


if __name__ == "__main__":
    main(sys.argv[1:])
