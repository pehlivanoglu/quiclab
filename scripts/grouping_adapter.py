#!/usr/bin/env python3
"""Phase 3 step 0: build an ECG onset log from a quiclab run, measure the
cross-client onset spread per burst, run the ECG engine and score it against
the run's burst truth. Grouping-only tooling: it reads the detector outputs
and never writes under <run>/detector or <run>/baselines.

    python scripts/grouping_adapter.py .runs/<campaign>/det-burstcap-pfifo-r1 [more runs...]
    python scripts/grouping_adapter.py RUN... --spread-only
    python scripts/grouping_adapter.py RUN... --set delta=0.3 theta_J=0.6 theta_cov=0.6
    python scripts/grouping_adapter.py RUN... --onsets owd      # oracle delay detector
    python scripts/grouping_adapter.py RUN... --onsets truth    # burst truth as onsets
    python scripts/grouping_adapter.py RUN... --onsets shadow-owd   # the shadow on sender-side OWD (owd_mode)
    python scripts/grouping_adapter.py RUN... --onsets v2-owd       # Shadow v2 (also v2, v2-nohold, v2-fixed...)

Runs whose clients re-join (grouping campaign N5): every session has its own
sender files (<sub>@<n>-acks.csv ...) and is a flow of its own (load_run ->
SessionRun); window `expected` sets name sessions.

Per run, under <run>/grouping/ (shadow) or <run>/grouping-<onsets>/ (oracles):
onsets.jsonl (meta / obs / onset records), truth.json, spread.csv,
evidence.jsonl, metrics.json, pairs_t.json (pairwise decision after every
event close), L.png.

Mechanism A -> Onset, three sources (--onsets):
  shadow  the frozen shadow detector (tuned:full) pre_signal_on/off events
          from moqx_shadow_replay, merged into episodes (gaps < 1 s);
          t_arrival = episode start (alarm time); t_onset = start of the
          sustained queue-delay rise (rolling median of the per-ACK
          queue_delay_ms >= --backdate-qd-ms) that ends at the alarm, looked
          back at most --backdate-max seconds; equal to t_arrival when the
          samples show no rise.
  owd     oracle delay detector: det_eval.measured_bands on the client's exact
          OWD log (<sub>-owd.csv): a standing queue >= 10 ms for >= 0.5 s is
          an episode, its first bin the onset. A perfect sender would learn it
          one RTT after the send-time bin, so t_onset = t_arrival = bin + mrtt
          (same residual as the shadow source after the engine's -mrtt/2
          alignment). No detection delay, no misses; the real cross-flow
          onset spread stays.
  shadow-owd  the same frozen shadow replayed on owd_mode.owd_acks: rtt_us
          replaced by the acked packet's one-way delay + R0 (reverse-path
          delay leaves the input). Everything else as `shadow`.
  v2[-fixed][-owd][-nohold]  the frozen Shadow v2 (scripts/shadow_v2_frozen.py; ip4 fitted values): per-client
          CUSUM alarm episodes; t_arrival = alarm time, t_onset = the last tick with an empty CUSUM (G = 0)
          before the alarm (the detector's own onset, no queue-delay back-dating). "-fixed" = global scale
          instead of the per-flow one, "-owd" = one-way-delay input, "-nohold" = without the hold rule
          (a long event then gives several episodes instead of one). Episodes are not merged.
  truth   detector/bursts.csv: every client the truth labels "hit" gets one
          onset per burst at the burst start, t_onset = t_arrival = start +
          mrtt/2 (aligned onset = burst start, spread 0). The idealized upper
          bound: tests the tree logic alone.
Observability: sent.csv -> bytes in the trailing 200 ms >= obs_fraction *
rendition * 0.2 s (sent_rate mode) or acks.csv -> inflight >= 0.5 cwnd and
not app-limited (cwnd mode), per 20 ms window; in_episode from the episodes.
Truth (campaign runs, <run>/grouping/windows.json): a client is hit in a
stimulus window when the plan expected it and the window's router egress
shows a GT1 standing-queue episode inside [start, end + 2 s] (router counters
only, independent of any client signal; under fq_codel the router cannot say
which flows queued, so every expected client counts). The same windows scored
with GT3 per-client OWD episodes are the secondary truth (pairwise_gt3; GT3
reads the signal the OWD-mode detector reads). Older runs: detector/bursts.csv
hit sets; without those, the topology's leaf queue (det_eval.leaf_queues).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt3  # noqa: E402
import owd_mode  # noqa: E402
import shadow_v2_frozen  # noqa: E402
from grouping import Config, FlowMeta, ObsSample, Onset, replay  # noqa: E402
from grouping.engine import Engine  # noqa: E402
from grouping.invariants import Invariants  # noqa: E402

V2_SOURCES = {f"{det}{'-owd' if mode == 'OWD' else ''}{'' if hold else '-nohold'}": (det, mode, hold)
              for det in shadow_v2_frozen.LABEL for mode in shadow_v2_frozen.FROZEN for hold in (True, False)}
SHADOW_VARIANT, ON, OFF = "full", "pre_signal_on", "pre_signal_off"   # det_eval.replay(run, TUNED): variant "full" is the tuned setting
OBS_WINDOW = 0.020
TRAIL_S = 0.2


class SessionRun(d.Run):
    """A run whose clients re-joined: every session <sid>@<n> has its own sender
    files and counts as a flow. The topology gets an alias node per session
    (same links as the client) so the path and leaf-queue helpers work unchanged."""

    def __init__(self, path: Path):
        super().__init__(path)
        self.sid_of = {s: s for s in self.subs}
        for f in sorted((path / "publishers" / self.pub).glob("*@*-acks.csv")):
            flow = f.name[:-len("-acks.csv")]
            sid = flow.split("@")[0]
            if sid not in self.topology["subscribers"]:
                continue
            self.sid_of[flow] = sid
            self.topology["subscribers"][flow] = dict(self.topology["subscribers"][sid])
            self.topology["links"] += [{**link, "to": flow} for link in self.topology["links"] if link["to"] == sid]
        self.subs = list(self.sid_of)


def load_run(run_dir: Path) -> d.Run:
    run = d.Run(run_dir)
    return SessionRun(run_dir) if any((run_dir / "publishers" / run.pub).glob("*@*-acks.csv")) else run


def sessions_of(run: d.Run) -> dict[str, tuple[float, float | None]]:
    """Flow -> (join, leave) from the scenario's join / leave events; the first
    session is the client's own id, later ones <sid>@<n>."""
    out = {}
    for sid in run.topology["subscribers"]:
        if "@" in sid:
            continue
        times = sorted((e["at_s"], e["type"]) for e in run.scenario.get("events", [])
                       if e["type"] in ("join", "leave") and e["subscriber"] == sid)
        sessions: list[list] = [] if times and times[0][1] == "join" else [[0.0, None]]
        for t, kind in times:
            if kind == "join":
                sessions.append([t, None])
            else:
                sessions[-1][1] = t
        for n, (join, leave) in enumerate(sessions, start=1):
            out[sid if n == 1 else f"{sid}@{n}"] = (join, leave)
    return out


def merge_episodes(out: list[list[float]], warmup: float, merge_s: float = d.ALARM_MERGE_S) -> list[tuple[float, float]]:
    merged: list[list[float]] = []
    for s, e in out:
        if merged and s - merged[-1][1] < merge_s:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(s, e) for s, e in merged if s >= warmup]


def episodes_of(events: list[dict], sid: str, warmup: float) -> list[tuple[float, float]]:
    """(start, end) shadow alarm episodes of one client, flaps closer than ALARM_MERGE_S merged."""
    out, start = [], None
    for e in sorted((e for e in events if e["subscriber"] == sid and e["variant"] == SHADOW_VARIANT),
                    key=lambda e: e["t"]):
        if e["event"] == ON and start is None:
            start = e["t"]
        elif e["event"] == OFF and start is not None:
            out.append([start, e["t"]])
            start = None
    if start is not None:
        out.append([start, math.inf])
    return merge_episodes(out, warmup)


def owd_episodes(run: d.Run, sid: str, warmup: float) -> list[tuple[float, float]]:
    """Oracle delay detector: contiguous 'congested' bands of det_eval.measured_bands
    on the client's exact OWD log; bin times are send times."""
    pts = []
    for r in d.rows(run.sender_file(sid, "owd")):
        t = run.t_mono_us(int(r["bin_mono_us"]))
        if 0 <= t <= run.duration - d.SHUTDOWN_S:
            pts.append((t, int(r["owd_min_us"]) / 1000 if r["owd_min_us"] else None,
                        int(r["packets_sent"]), int(r["packets_timed"])))
    bands = d.measured_bands(pts, d.delay_changes(run, sid))
    out, start, last = [], None, None
    for t, band in bands:
        if band == "congested":
            if start is None:
                start = t
            last = t
        elif band != "none" and start is not None:   # 'none' bins (nothing sent) do not end a queue
            out.append([start, t])
            start = None
    if start is not None:
        out.append([start, last])
    return merge_episodes(out, warmup)


def truth_episodes(truth: dict, sid: str, warmup: float) -> list[tuple[float, float]]:
    """Burst truth as a detector: one episode per burst that hit the client."""
    return merge_episodes([[b["start"], b["end"]] for b in truth["bursts"] if sid in b["hit"]], warmup, merge_s=0.0)


def backdate(samples: pd.DataFrame, t_arr: float, max_back: float, qd_ms: float) -> float:
    """Start of the sustained queue-delay rise that ends at the alarm: the
    earliest sample of the contiguous run (rolling median over 5 ACKs of
    queue_delay_ms >= qd_ms) that contains t_arr; t_arr when there is none."""
    w = samples[(samples.t >= t_arr - max_back) & (samples.t <= t_arr + 0.05)]
    if len(w) < 3:
        return t_arr
    qd = w.queue_delay_ms.rolling(5, min_periods=1, center=True).median().values
    pos = qd >= qd_ms
    t = w.t.values
    i = int(np.searchsorted(t, t_arr, side="right")) - 1
    if i < 0 or not pos[i]:
        return t_arr
    while i > 0 and pos[i - 1]:
        i -= 1
    return float(t[i])


def sent_rate_obs(run: d.Run, sid: str, rendition_bps: float, fraction: float, t_end: float) -> np.ndarray:
    s = pd.read_csv(run.sender_file(sid, "sent"), usecols=["send_mono_us", "bytes"])
    t = run.t_mono_us(s.send_mono_us.values)
    edges = np.arange(0, t_end + OBS_WINDOW, OBS_WINDOW)
    per_win = np.histogram(t, bins=edges, weights=s.bytes.values)[0]
    k = int(round(TRAIL_S / OBS_WINDOW))
    trailing = np.convolve(per_win, np.ones(k), mode="full")[:len(per_win)]
    return trailing >= fraction * rendition_bps / 8 * TRAIL_S


def owd_timed_obs(run: d.Run, sid: str, t_end: float) -> np.ndarray:
    """Windows whose trailing 200 ms holds at least one OWD bin with a receive
    timestamp: where the oracle detector has data (an oracle gap is not silence)."""
    o = pd.read_csv(run.sender_file(sid, "owd"), usecols=["bin_mono_us", "packets_timed"])
    t = run.t_mono_us(o.bin_mono_us.values[o.packets_timed.values > 0])
    edges = np.arange(0, t_end + OBS_WINDOW, OBS_WINDOW)
    per_win = np.histogram(t, bins=edges)[0]
    k = int(round(TRAIL_S / OBS_WINDOW))
    return np.convolve(per_win, np.ones(k), mode="full")[:len(per_win)] > 0


def cwnd_obs(run: d.Run, sid: str, t_end: float) -> np.ndarray:
    a = pd.read_csv(run.sender_file(sid, "acks"), usecols=["mono_us", "app_limited", "cwnd_bytes", "inflight_bytes"])
    a["t"] = run.t_mono_us(a.mono_us.values)
    a["w"] = (a.t // OBS_WINDOW).astype(int)
    g = a.groupby("w").agg(applim=("app_limited", "max"), infl=("inflight_bytes", "max"), cwnd=("cwnd_bytes", "max"))
    n = int(math.ceil(t_end / OBS_WINDOW)) + 1
    out = np.zeros(n, dtype=bool)
    ok = g[(g.applim == 0) & (g.infl >= 0.5 * g.cwnd)].index.values
    out[ok[(ok >= 0) & (ok < n)]] = True
    return out


def build(run_dir: Path, cfg: Config, backdate_max: float, warmup: float, qd_ms: float,
          source: str = "shadow") -> tuple[list, dict, list[dict]]:
    run = load_run(run_dir)
    truth = truth_of(run)
    truth["secondary"] = truth_of(run, "gt3") if (run_dir / "grouping" / "windows.json").exists() else None
    t_end = run.duration
    rendition = {s: float(run.topology["subscribers"][s]["rate_kbps"]) * 1000 for s in run.subs}
    mrtt = {}
    for s in run.subs:
        a = pd.read_csv(run.sender_file(s, "acks"), usecols=["min_rtt_us"])
        mrtt[s] = float(a.min_rtt_us.min()) / 1e6
    onsets = []
    if source in ("shadow", "shadow-owd"):
        with tempfile.TemporaryDirectory() as tmp:
            acks = None
            if source == "shadow-owd":
                (Path(tmp) / "acks").mkdir()
                acks = {s: owd_mode.owd_acks(run, s, Path(tmp) / "acks") for s in run.subs}
            events = d.replay(run, d.TUNED, samples_to=Path(tmp), acks=acks)
            samples = {}
            for s in run.subs:
                f = Path(tmp) / f"{s}.csv"
                if f.exists():
                    df = pd.read_csv(f, usecols=["mono_us", "queue_delay_ms"])
                    df["t"] = run.t_mono_us(df.mono_us.values)
                    samples[s] = df
        eps = {s: episodes_of(events, s, warmup) for s in run.subs}
        for s in run.subs:
            for start, end in eps[s]:
                t_on = backdate(samples[s], start, backdate_max, qd_ms) if s in samples else start
                onsets.append({"flow": s, "t_arrival": start, "t_onset": t_on, "end": end})
    elif source in V2_SOURCES:
        for s, spans in shadow_v2_frozen.episodes(run, *V2_SOURCES[source]).items():
            onsets += [{"flow": s, "t_arrival": start, "t_onset": t_on, "end": end}
                       for start, end, t_on in spans if start >= warmup]
    elif source == "owd":
        eps = {s: owd_episodes(run, s, warmup) for s in run.subs}
        for s in run.subs:
            for start, end in eps[s]:
                t = start + mrtt[s]
                onsets.append({"flow": s, "t_arrival": t, "t_onset": t, "end": end + mrtt[s]})
    elif source == "truth":
        if not truth["bursts"]:
            raise RuntimeError(f"{run_dir.name}: no burst hit labels, --onsets truth needs detector/bursts.csv")
        eps = {s: truth_episodes(truth, s, warmup) for s in run.subs}
        for s in run.subs:
            for start, end in eps[s]:
                t = start + mrtt[s] / 2
                onsets.append({"flow": s, "t_arrival": t, "t_onset": t, "end": end + mrtt[s] / 2})
    else:
        raise ValueError(source)
    eps = {s: [(o["t_arrival"], o["end"]) for o in onsets if o["flow"] == s] for s in run.subs}
    records: list = [("meta", 0.0, FlowMeta(s, mrtt[s], False, rendition[s])) for s in run.subs]
    for o in onsets:
        records.append(("onset", o["t_arrival"], Onset(o["flow"], o["t_onset"], o["t_arrival"])))
    n = int(math.ceil(t_end / OBS_WINDOW)) + 1
    for s in run.subs:
        obs = sent_rate_obs(run, s, rendition[s], cfg.obs_fraction, t_end) if cfg.obs_mode == "sent_rate" \
            else cwnd_obs(run, s, t_end)
        if source == "owd":
            cov = owd_timed_obs(run, s, t_end)
            obs = obs & cov[:len(obs)]
        starts = np.array([a for a, _ in eps[s]])
        ends = np.array([b for _, b in eps[s]])
        for i in range(n):
            t = round(i * OBS_WINDOW, 6)
            j = int(np.searchsorted(starts, t, side="right")) - 1
            in_ep = bool(j >= 0 and t < ends[j])
            ob = bool(i < len(obs) and obs[i] and t >= warmup)
            records.append(("obs", t, ObsSample(s, t, ob, in_ep)))
    order = {"meta": 0, "obs": 1, "onset": 2}
    records.sort(key=lambda r: (r[1], order[r[0]], r[2].flow))
    truth["episodes"] = {s: [(a, b) for a, b in eps[s]] for s in run.subs}
    truth["onset_source"] = source
    return records, truth, onsets


def leaf_groups(bursts: list[dict], same: dict[str, set[str]], subs: list[str]) -> dict[str, frozenset]:
    """Tightest *shared* group of a client. With plan windows (`expected`): the
    intersection of the expected sets of the shared windows (>= 2 expected
    clients) in which the client was hit, so a partial hit under fq_codel (2 of
    3 clients queue) still says "link a" and a private access-link window does
    not shrink the group to the client itself. Without expected sets
    (bursts.csv): the intersection of the hit sets containing the client.
    On a split topology an upstream burst gives A u B and a downstream one A,
    so leaf(a1) = A: the a-b pair shares a link (pairs) but not a leaf
    (pairs_leaf). Without any hits (topology truth) the group is the client's
    `same` set. A client in no shared group gets the empty set."""
    if not bursts:
        return {s: frozenset(same[s] | {s}) if same[s] else frozenset() for s in subs}
    out = {}
    for s in subs:
        sets = []
        for b in bursts:
            if s not in b["hit"]:
                continue
            exp = b.get("expected")
            if exp is not None:
                if len(exp) >= 2:
                    sets.append(set(exp))
            elif len(b["hit"]) >= 1:
                sets.append(set(b["hit"]))
        out[s] = frozenset(set.intersection(*sets)) if sets else frozenset()
    return out


def congested_bins(run: d.Run, sid: str) -> np.ndarray:
    """Times of the OWD bins det_eval.measured_bands marks congested (standing
    queue >= 10 ms for >= 0.5 s, or loss) on the client's exact OWD log."""
    pts = []
    for r in d.rows(run.sender_file(sid, "owd")):
        t = run.t_mono_us(int(r["bin_mono_us"]))
        if 0 <= t <= run.duration - d.SHUTDOWN_S:
            pts.append((t, int(r["owd_min_us"]) / 1000 if r["owd_min_us"] else None,
                        int(r["packets_sent"]), int(r["packets_timed"])))
    return np.array([t for t, band in d.measured_bands(pts, d.delay_changes(run, sid)) if band == "congested"])


def window_hop(run: d.Run, w: dict) -> str | None:
    """The stimulated router egress of a window as "from->to": the window's `hop`
    when the plan wrote it, else the deepest hop whose clients are exactly the
    expected set (private window: the client's own access egress). None when
    nothing is expected (reverse-path stimuli)."""
    if w.get("hop"):
        return w["hop"]
    expected = set(w.get("expected", []))
    if not expected:
        return None
    paths = {s: d.path_hops(run, run.pub, s) for s in run.subs}
    behind = defaultdict(set)
    for s, hops in paths.items():
        for hop in hops:
            behind[hop].add(s)
    candidates = [hop for hop, clients in behind.items() if clients == expected]
    if not candidates:
        return None
    first = next(iter(expected))
    return "->".join(max(candidates, key=lambda hop: paths[first].index(hop)))


def overlaps(episodes: list[tuple[float, float]], lo: float, hi: float) -> bool:
    return any(a <= hi and b >= lo for a, b in episodes)


def measured_bursts(run: d.Run, windows: list[dict], hop_episodes: dict[str, list[tuple[float, float]]],
                    flow_episodes: dict[str, list[tuple[float, float]]] | None = None) -> list[dict]:
    """Burst records (same shape as bursts.csv's) from the campaign's stimulus
    windows and a congestion truth. Primary (hop_episodes = GT1 standing-queue
    episodes per router egress): every expected client is hit when the window's
    egress has an episode inside [start, end + BURST_RECOVERY_S]; the router
    cannot say which flows queued, so under fq_codel this overstates the hit set.
    Secondary (flow_episodes = GT3 per-client episodes): an expected client is
    hit when its own episodes overlap the window; GT3 reads the same OWD the
    detector's OWD mode reads, so it is the comparison truth, not the primary."""
    expanded = []
    for w in windows:
        hop = window_hop(run, w)
        if w.get("from_truth") and hop:
            # Continuous stimulus (ppbp): one truth window per GT1 episode of the hop inside the planned span.
            expanded += [{**w, "start": a, "end": b, "from_truth": True}
                         for a, b in hop_episodes.get(hop, []) if a <= w["end"] and b >= w["start"]]
        else:
            expanded.append(w)
    out = []
    for i, w in enumerate(expanded):
        lo, hi = w["start"], w["end"] + d.BURST_RECOVERY_S
        expected = w.get("expected", [])
        if flow_episodes is not None:
            hit = sorted(s for s in expected if overlaps(flow_episodes.get(s, []), lo, hi))
        else:
            hop = window_hop(run, w)
            hit = sorted(expected) if hop and overlaps(hop_episodes.get(hop, []), lo, hi) else []
        out.append({"burst": i, "start": w["start"], "end": w["end"], "hit": hit, "uncertain": [],
                    "kind": w.get("kind"), "target": w.get("target"), "expected": expected,
                    "hop": window_hop(run, w)})
    return out


def gt1_hop_episodes(run: d.Run) -> dict[str, list[tuple[float, float]]]:
    """GT1 standing-queue episodes per router egress "from->to" (router counters only)."""
    out = defaultdict(list)
    for e in gt1.run_truth(run, gt1.Params())[0]:
        out[e["hop"]].append((float(e["start_s"]), float(e["end_s"])))
    return dict(out)


def gt3_flow_episodes(run: d.Run) -> dict[str, list[tuple[float, float]]]:
    """GT3 per-client episodes (receiver OWD + loss; shares its input with the OWD-mode detector)."""
    out = defaultdict(list)
    for e in gt3.run_truth(run, gt3.Params(), path_queues=False)[0]:
        out[e["flow"]].append((float(e["t_on"]), float(e["t_end"])))
    return dict(out)


TRUTHS = ("gt1", "gt3")   # primary: router queue; secondary: per-client OWD (same signal as the OWD-mode detector)


def truth_of(run: d.Run, truth_source: str = "gt1") -> dict:
    paths = {s: d.path_hops(run, run.pub, s) for s in run.subs}
    group_of = {s: g or s for s, g in d.leaf_queues(run.topology, paths).items()}
    truth = {"run": run.path.name, "subs": run.subs, "topology_group": group_of, "bursts": [], "pairs": {},
             "truth_source": truth_source}
    bursts_csv = run.path / "detector" / "bursts.csv"
    windows_json = run.path / "grouping" / "windows.json"
    same = defaultdict(set)
    if windows_json.exists():
        # Grouping campaign run: stimulus windows from the plan, hits from the router's
        # queue counters (gt1) or, as the comparison, from the clients' own OWD (gt3).
        windows = json.loads(windows_json.read_text())
        if truth_source == "gt3":
            truth["bursts"] = measured_bursts(run, windows, gt1_hop_episodes(run), gt3_flow_episodes(run))
            truth["source"] = "windows.json + GT3 per-client OWD episodes (same signal as the OWD-mode detector)"
        else:
            truth["bursts"] = measured_bursts(run, windows, gt1_hop_episodes(run))
            truth["source"] = "windows.json + GT1 router standing-queue episodes on the stimulated egress"
        for b in truth["bursts"]:
            for x in b["hit"]:
                same[x] |= set(b["hit"])
    elif bursts_csv.exists():
        b = pd.read_csv(bursts_csv)
        for (burst, start, end), g in b.groupby(["burst", "start", "end"]):
            hit = sorted(g[g["class"] == "hit"].subscriber)
            unc = sorted(g[g["class"] == "uncertain"].subscriber)
            truth["bursts"].append({"burst": int(burst), "start": float(start), "end": float(end), "hit": hit,
                                    "uncertain": unc})
            for x in hit:
                same[x] |= set(hit)
        truth["source"] = "bursts.csv (both hit by a common burst)"
    if not any(same.values()) and not windows_json.exists():
        # No hit labels (TCP scenarios score "uncertain"): fall back to topology.
        # Campaign runs keep their measured truth even when nothing was hit
        # (reverse-path stimuli): every pair is then DIFFERENT.
        for s in run.subs:
            same[s] = {x for x in run.subs if group_of[x] == group_of[s] and group_of[s] != s}
        truth["source"] = "topology (same leaf queue)"
        truth["bursts"] = []
    leaf = leaf_groups([b for b in truth["bursts"] if b["hit"]], same, run.subs)
    truth["leaf"] = {s: sorted(l) for s, l in leaf.items()}
    truth["pairs_leaf"] = {}
    subs = sorted(run.subs)
    for i, f in enumerate(subs):
        for g in subs[i + 1:]:
            truth["pairs"][f"{f}|{g}"] = g in same[f]
            truth["pairs_leaf"][f"{f}|{g}"] = bool(leaf[f]) and leaf[f] == leaf[g]
    return truth


def spread_rows(truth: dict, onsets: list[dict]) -> list[dict]:
    """Per burst: spread of t_arrival and of t_onset across the hit clients."""
    rows = []
    by_flow = defaultdict(list)
    for o in onsets:
        by_flow[o["flow"]].append(o)
    for b in truth.get("bursts", []):
        arr, on = [], []
        for s in b["hit"]:
            cand = [o for o in by_flow[s] if b["start"] <= o["t_arrival"] <= b["end"] + d.BURST_RECOVERY_S]
            if cand:
                o = min(cand, key=lambda o: o["t_arrival"])
                arr.append(o["t_arrival"])
                on.append(o["t_onset"])
        if len(arr) >= 2:
            rows.append({"burst": b["burst"], "start": b["start"], "n_hit": len(b["hit"]), "n_detected": len(arr),
                         "spread_arrival_ms": round((max(arr) - min(arr)) * 1e3, 1),
                         "spread_onset_ms": round((max(on) - min(on)) * 1e3, 1),
                         "first_arrival_ms": round((min(arr) - b["start"]) * 1e3, 1),
                         "first_onset_ms": round((min(on) - b["start"]) * 1e3, 1),
                         "backdate_ms": round(statistics.median(a - o for a, o in zip(arr, on)) * 1e3, 1)})
    return rows


def pair_metrics(res: replay.Result, truth: dict, key: str = "pairs_leaf") -> dict:
    """ECG SAME (same leaf, both confirmed) against truth[key]: pairs_leaf (same
    tightest group) or pairs (hit by a common burst, i.e. share some link)."""
    pairs = res.pairs()
    tp = fp = fn = tn = unc = 0
    detail = {}
    for (f, g), dec in pairs.items():
        same = truth[key][f"{f}|{g}"]
        detail[f"{f}|{g}"] = {"decided": dec, "truth_same": same}
        if dec == "UNCERTAIN":
            unc += 1
        elif dec == "SAME":
            tp += same
            fp += not same
        else:
            fn += same
            tn += not same
    dec_n = tp + fp + fn + tn
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "uncertain": unc,
            "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None,
            "coverage": dec_n / len(pairs) if pairs else None, "pairs": detail}


def out_dir(run_dir: Path, a) -> Path:
    return run_dir / (a.out or ("grouping" if a.onsets == "shadow" else f"grouping-{a.onsets}"))


def process(run_dir: Path, cfg: Config, a) -> dict:
    out = out_dir(run_dir, a)
    out.mkdir(exist_ok=True)
    records, truth, onsets = build(run_dir, cfg, a.backdate_max, a.warmup, a.backdate_qd_ms, a.onsets)
    rows = spread_rows(truth, onsets)
    with (out / "spread.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["burst"])
        w.writeheader()
        w.writerows(rows)
    summary = {"run": run_dir.name, "onsets": len(onsets), "bursts_measured": len(rows)}
    if rows:
        for k in ("spread_arrival_ms", "spread_onset_ms", "first_arrival_ms", "first_onset_ms", "backdate_ms"):
            vals = sorted(r[k] for r in rows)
            summary[k] = {"p50": vals[len(vals) // 2], "p90": vals[min(len(vals) - 1, int(0.9 * len(vals)))]}
    if a.spread_only:
        return summary
    from grouping import synth
    synth.write_log(records, out / "onsets.jsonl")
    holder = {}

    def factory(_r, cfg_, log=None):
        eng = Engine(cfg_, log)
        holder["inv"] = Invariants(eng)
        return eng
    res = replay.run(records, cfg, log_path=out / "evidence.jsonl", engine_factory=factory)
    pm = pair_metrics(res, truth, "pairs_leaf")
    pm_link = pair_metrics(res, truth, "pairs")
    secondary = truth.pop("secondary", None)
    pm_gt3 = pair_metrics(res, secondary, "pairs_leaf") if secondary else None
    run = load_run(run_dir)
    extra = outcome_metrics(res, truth, run, json.loads((run_dir / "grouping" / "windows.json").read_text())
                            if (run_dir / "grouping" / "windows.json").exists() else [])
    metrics = {"run": run_dir.name, "onset_source": a.onsets, "config": cfg.to_dict(), "cases": dict(res.cases),
               "pairwise": pm, "pairwise_link": pm_link, "spans": replay.span_stats(res), "leaves": res.leaves,
               "final": res.final["flows"], "spread": summary, "truth_source": truth["source"],
               "truth_leaf": truth["leaf"], "invariants_checked": holder["inv"].n_checked,
               "events": res.events, "bursts": truth["bursts"], "series": res.series,
               "pairwise_gt3": pm_gt3, "truth_leaf_gt3": secondary["leaf"] if secondary else None, **extra}
    replay.dump(metrics, out / "metrics.json")
    (out / "pairs_t.json").write_text(json.dumps(res.pairs_t()))
    (out / "truth.json").write_text(json.dumps({**truth, "secondary_gt3": secondary}, indent=1))
    replay.plot_L(res, out / "L.png", f"{run_dir.name}: {a.onsets} onsets -> ECG (delta={cfg.delta}, theta={cfg.theta_J})")
    summary.update({"cases": dict(res.cases), "precision": pm["precision"], "recall": pm["recall"],
                    "coverage": pm["coverage"], "uncertain": pm["uncertain"], "tp": pm["tp"], "fp": pm["fp"],
                    "precision_link": pm_link["precision"], "recall_link": pm_link["recall"],
                    "precision_gt3": pm_gt3["precision"] if pm_gt3 else None,
                    "recall_gt3": pm_gt3["recall"] if pm_gt3 else None,
                    "leaves": {n: l["members"] for n, l in res.leaves.items() if l["kind"] == "leaf" and l["members"]},
                    **extra})
    return summary


CTRL = "sub-ctrl"
PRIVATE_RECOVERY_S = d.BURST_RECOVERY_S


def confirmed_leaves(res: replay.Result) -> list[frozenset]:
    """Member sets of the confirmed leaves with at least two reported members."""
    flows = res.final["flows"]
    out = []
    for n, leaf in res.leaves.items():
        if leaf["kind"] != "leaf" or not leaf["confirmed"]:
            continue
        members = frozenset(f for f in leaf["members"] if flows.get(f, {}).get("member", False))
        if len(members) >= 2:
            out.append(members)
    return out


def membership_events(res: replay.Result) -> dict[str, int]:
    """Per flow that was reported a member at some close: the number of events
    it took part in up to and including the one after which it was a member."""
    out, n = {}, defaultdict(int)
    for e, snap in zip(res.events, res.snapshots):
        for f in e["members"]:
            n[f] += 1
        for f, st in snap["flows"].items():
            if f not in out and st.get("member") and st["node"] is not None:
                out[f] = n[f]
    return out


def private_window_outcomes(res: replay.Result, windows: list[dict]) -> dict:
    """Private windows (`cell` private, one expected client): solo when every
    ECG event of that client inside [start, end + recovery] has it as the only
    member, silent when there is none, grouped otherwise."""
    out = {"n": 0, "solo": 0, "silent": 0, "grouped": 0}
    for w in windows:
        if w.get("cell") != "private" or len(w.get("expected", [])) != 1:
            continue
        c = w["expected"][0]
        evs = [e for e in res.events if w["start"] <= e["t0"] <= w["end"] + PRIVATE_RECOVERY_S and c in e["members"]]
        out["n"] += 1
        out["silent" if not evs else "solo" if all(len(e["members"]) == 1 for e in evs) else "grouped"] += 1
    return out


def outcome_metrics(res: replay.Result, truth: dict, run: d.Run, windows: list[dict]) -> dict:
    """Spec section 6 outputs: tree correctness, control client, membership speed,
    private windows, sessions (off-membership = a session reported a confirmed
    member outside its own [join, leave])."""
    leaves = confirmed_leaves(res)
    truth_groups = {frozenset(g) for g in truth["leaf"].values() if len(g) >= 2}
    out = {"tree_correct": set(leaves) == truth_groups, "leaves_truth": sorted(sorted(g) for g in truth_groups),
           "ctrl_grouped": any(CTRL in g for g in leaves) if CTRL in truth["subs"] else None,
           "membership_events": membership_events(res)}
    if any(w.get("cell") == "private" for w in windows):
        out["private_windows"] = private_window_outcomes(res, windows)
    sessions = sessions_of(run)
    if any("@" in f for f in sessions):
        out["sessions"] = {f: list(v) for f, v in sessions.items()}
        off = 0
        nodes_confirmed = {}
        for snap in res.snapshots:
            for n, node in snap.get("nodes", {}).items():
                nodes_confirmed[(snap["t"], str(n))] = node["confirmed"]
            for f, st in snap["flows"].items():
                join, leave = sessions.get(f, (0.0, None))
                outside = snap["t"] < join or (leave is not None and snap["t"] > leave + PRIVATE_RECOVERY_S)
                if outside and st.get("member") and st["node"] is not None \
                        and nodes_confirmed.get((snap["t"], str(st["node"])), False):
                    off += 1
        out["off_membership"] = off
        per_flow = defaultdict(int)
        for e in res.events:
            for f in e["members"]:
                per_flow[f] += 1
        three = [f for f in sessions if per_flow[f] >= 3 and f != CTRL]
        members = [f for f in three if f in out["membership_events"]]
        idx = sorted(out["membership_events"][f] for f in members)
        out["session_stats"] = {"sessions": len([f for f in sessions if f != CTRL]), "sessions_3_events": len(three),
                                "members": len(members), "event_index_p50": idx[len(idx) // 2] if idx else None}
    return out


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--onsets", choices=("shadow", "owd", "truth", "shadow-owd", *V2_SOURCES), default="shadow",
                    help="Mechanism A source")
    ap.add_argument("--out", help="subdirectory under each run (default grouping, grouping-owd, grouping-truth)")
    ap.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE", help="engine config overrides")
    ap.add_argument("--backdate-max", type=float, default=1.0, help="max look-back for the backlog onset (s)")
    ap.add_argument("--backdate-qd-ms", type=float, default=10.0, help="queue delay that counts as backlog (ms)")
    ap.add_argument("--warmup", type=float, default=d.WARMUP_S, help="ignore onsets before this run time (s)")
    ap.add_argument("--spread-only", action="store_true", help="only measure the per-burst onset spread")
    a = ap.parse_args(argv)
    over = {}
    for it in a.set:
        k, v = it.split("=", 1)
        try:
            over[k] = json.loads(v)
        except json.JSONDecodeError:
            over[k] = v
    cfg = Config.from_dict(over)
    runs = [r for pat in a.runs for r in (sorted(Path().glob(str(pat))) if any(c in str(pat) for c in "*?[") else [pat])]
    rows = []
    for r in runs:
        if not (r / "events.csv").exists():
            print(f"skip {r}: not a run", file=sys.stderr)
            continue
        try:
            s = process(r, cfg, a)
        except RuntimeError as e:
            print(f"skip {e}", file=sys.stderr)
            continue
        rows.append(s)
        sp = s.get("spread_onset_ms")
        print(f"{s['run']}: onsets={s['onsets']} bursts={s['bursts_measured']}"
              + (f" spread arrival p50={s['spread_arrival_ms']['p50']} p90={s['spread_arrival_ms']['p90']}"
                 f" | onset p50={sp['p50']} p90={sp['p90']} | backdate p50={s['backdate_ms']['p50']} ms" if sp else "")
              + ("" if a.spread_only else f"\n    cases={s['cases']} pairs P={s['precision']} R={s['recall']} "
                 f"cov={s['coverage']} leaves={s['leaves']}"), flush=True)
    if len(rows) > 1 and rows[0].get("spread_onset_ms"):
        def agg(k, q):
            return statistics.median(r[k][q] for r in rows if k in r)
        print(f"\nall runs (median of per-run values): arrival spread p50={agg('spread_arrival_ms', 'p50'):.0f} "
              f"p90={agg('spread_arrival_ms', 'p90'):.0f} ms | backdated onset spread p50={agg('spread_onset_ms', 'p50'):.0f} "
              f"p90={agg('spread_onset_ms', 'p90'):.0f} ms | backdate p50={agg('backdate_ms', 'p50'):.0f} ms")
    if not a.spread_only and rows:
        P = [r["precision"] for r in rows if r.get("precision") is not None]
        R = [r["recall"] for r in rows if r.get("recall") is not None]
        C = [r["coverage"] for r in rows if r.get("coverage") is not None]
        print(f"pairwise over {len(rows)} runs: precision median={statistics.median(P) if P else None} "
              f"recall median={statistics.median(R) if R else None} coverage median={statistics.median(C) if C else None}")


if __name__ == "__main__":
    main(sys.argv[1:])
