#!/usr/bin/env python3
"""Score sender-side per-client congestion detectors on quiclab runs.

    python3 scripts/det_eval.py score .runs/<run> [...]      # truth + replay + per-run CSVs
    python3 scripts/det_eval.py report .runs/<run> [...]     # per-AQM x scenario tables
    python3 scripts/det_eval.py bursts .runs/<run> [...]     # burst benchmark tables

score: rebuilds network truth per subscriber from the run itself (link
capacities, video demand, cross traffic), replays the moq-testbed shadow
detector (moqx_shadow_replay) over the sender's per-ACK record
(publishers/<pub>/<sub>-acks.csv, -sent.csv) and writes <run>/detector/
truth.csv, alarms.csv, detections.csv.

Truth (moq-testbed shadow_report rules): per hop, FIFO-like queues (pfifo,
red, pie) give every flow u = offered / capacity;
fq_codel gives each flow its max-min fair share. A subscriber's u is the
worst hop on its path. u >= 1 congested, u < 0.85 clear, between ambiguous
(not scored). Congested episodes closer than MERGE_GAP_S merge; shorter than
MIN_EPISODE_S are ignored; episodes whose integral of (u - 1) dt is below
MIN_EXCESS_S are minor (not scored, alarms in them excluded). PPBP uses its realized offered load (1 s mean).

Scoring: an onset is caught by a detector when an alarm starts in
[t0 - PRE_ONSET_LEAD_S, min(episode end, t0 + SEARCH_S)]; latency is
max(0, alarm - t0). An alarm start is a TP when it is the first in such a
window, a duplicate if a later one, excluded during warm-up, congestion or
the ambiguous band, else a false positive (clear band). Precision =
TP / (TP + FP); false alarms per minute of clear time.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.runtime import edge_interfaces  # noqa: E402
REPLAY = ROOT.parent / "moq-testbed" / "build" / "moqx_shadow_replay"

CONGESTED_U = 1.0
CLEAR_U = 0.85
WARMUP_S = 5.0
GRID_S = 0.1
MERGE_GAP_S = 1.0
MIN_EPISODE_S = 0.5
# Severity: an episode is scored only if its overload, integral of (u - 1) dt,
# would add at least this much queuing delay in a FIFO; milder ones (a 1 BDP
# queue absorbs them) are neither onsets nor false-alarm exposure.
MIN_EXCESS_S = 0.05
PRE_ONSET_LEAD_S = 1.0
SEARCH_S = 10.0
DEADLINES_MS = (250, 500, 1000, 2000)
FQ_AQMS = {"fq_codel"}

# m4 live setting (moq-testbed configs/matrix/shadow-m4.yaml).
PARAMS = {
    "residual_floor_ms": 20, "gradient_scale": 1, "excess_trigger": 0, "backlog_ms": 30,
    "floor_window_ms": 500, "shared_require_backlog": 1, "deficit_min_delay_ms": 5,
    "backlog_flush_ratio": 1.2, "propagation": 0, "min_signals": 2, "verified_ms": 200,
}
# Sender-side setting, chosen by offline sweep on det-*-pfifo-r1 only (other
# AQMs and repetitions are held out): no GOP floor on the residual delay and a
# 100 ms backlog window; the m4 windows (500 ms) cost ~0.5 s of latency.
TUNED = {**PARAMS, "floor_window_ms": 0, "backlog_window_ms": 100}
VARIANTS = ["full", "gcc", "backlog_only", "deficit_only", "gradient_only", "offered_only", "loss_only"]
# Detector name -> (variant, event). "verified" is the full variant's second level.
DETECTORS = {
    "shadow": ("tuned:full", "pre_signal_on"),
    "shadow_verified": ("tuned:full", "verified_on"),
    "shadow_m4": ("full", "pre_signal_on"),
    "gcc": ("gcc", "pre_signal_on"),
    "bbr": ("", "bbr_bw_drop"),
    **{v: (v, "pre_signal_on") for v in VARIANTS[2:]},
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        if not items:
            return
        w = csv.DictWriter(f, fieldnames=list(items[0]))
        w.writeheader()
        w.writerows(items)


# ── run model ────────────────────────────────────────────────────────────

class Run:
    def __init__(self, path: Path):
        self.path = path
        self.topology = yaml.safe_load((path / "topology.yaml").read_text())
        self.scenario = yaml.safe_load((path / "scenario.yaml").read_text())
        self.events = rows(path / "events.csv")
        epoch = self.events[0]
        assert epoch["event"] == "epoch", f"{path}: events.csv must start with epoch"
        self.epoch_mono_ns = int(epoch["applied_mono_ns"]) - round(float(epoch["applied_s"]) * 1e9)
        self.epoch_unix_ns = int(epoch["applied_unix_ns"]) - round(float(epoch["applied_s"]) * 1e9)
        self.duration = float(self.scenario["duration_s"])
        self.aqm = next(iter(self.scenario["routers"].values()))["aqm"]
        self.pub = next(iter(self.topology["publishers"]))
        self.subs = list(self.topology["subscribers"])

    def t_mono_us(self, us: float) -> float:
        return (us * 1000 - self.epoch_mono_ns) / 1e9

    def t_unix_us(self, us: float) -> float:
        return (us * 1000 - self.epoch_unix_ns) / 1e9

    def sender_file(self, sid: str, suffix: str) -> Path:
        return self.path / "publishers" / self.pub / f"{sid}-{suffix}.csv"


def path_hops(run: Run, src: str, dst: str) -> list[tuple[str, str]]:
    adj = defaultdict(set)
    for link in run.topology["links"]:
        adj[link["from"]].add(link["to"])
        adj[link["to"]].add(link["from"])
    prev, todo = {src: None}, [src]
    for node in todo:
        for n in sorted(adj[node]):
            if n not in prev:
                prev[n] = node
                todo.append(n)
    nodes, n = [], dst
    while n is not None:
        nodes.append(n)
        n = prev[n]
    nodes.reverse()
    return list(zip(nodes, nodes[1:]))


def capacity_series(run: Run) -> dict[tuple[str, str], list[tuple[float, float]]]:
    """Forward bandwidth per directed hop: [(t, Mb/s)], initial value at t=0."""
    default = (run.scenario.get("link_defaults") or {}).get("forward", {}).get("bandwidth_mbps", math.inf)
    caps: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(lambda: [(0.0, default)])
    for link in run.scenario.get("links", []):
        bw = (link.get("forward") or {}).get("bandwidth_mbps", default)
        caps[(link["from"], link["to"])] = [(0.0, bw)]
        rev = (link.get("reverse") or {}).get("bandwidth_mbps")
        if rev is not None:
            caps[(link["to"], link["from"])] = [(0.0, rev)]
    for e in run.events:
        if e["event"] == "link" and e["status"] == "applied" and "bandwidth_mbps=" in e["detail"]:
            hop, direction = e["target"].split(":")
            a, b = hop.split("->")
            key = (a, b) if direction == "forward" else (b, a)
            bw = float(e["detail"].split("bandwidth_mbps=")[1].split()[0])
            caps[key].append((float(e["applied_s"]), bw))
    return caps


def value_at(series: list[tuple[float, float]], t: float) -> float:
    v = series[0][1]
    for when, x in series:
        if when <= t:
            v = x
    return v


def demand_bps(run: Run, sid: str) -> float:
    """Wire rate the video asks for: produced frame bytes x QUIC overhead."""
    frames = rows(run.sender_file(sid, "frames"))
    drops = rows(run.sender_file(sid, "drops"))
    produced = sum(int(r["size"]) for r in frames) + sum(int(r["size"]) for r in drops)
    times = [int(r["send_us"]) for r in frames]
    span = (max(times) - min(times)) / 1e6 if len(times) > 1 else 1.0
    last = rows(run.sender_file(sid, "cc"))[-1]
    app = int(last["app_bytes"]) or 1
    overhead = max(1.0, (int(last["bytes_sent"]) - int(last["retx_bytes"])) / app)
    return produced * 8 / span * overhead


def cross_series(run: Run) -> list[dict]:
    """Cross flows: hops, and offered Mb/s as a function of run time."""
    routes = run.topology.get("traffic", {}).get("routes", {})
    applied = {e["target"]: float(e["applied_s"]) for e in run.events
               if e["event"] in {"flow", "ppbp", "bursts"} and e["status"] == "applied"}
    out = []
    for ev in run.scenario.get("events", []):
        if ev["type"] not in {"flow", "ppbp", "bursts"} or ev["id"] not in applied:
            continue
        path = routes[ev["route"]]["path"]
        hops = list(zip(path, path[1:]))
        start = applied[ev["id"]]
        end = start + float(ev.get("duration_s", run.duration)) if ev["type"] != "bursts" else run.duration
        if ev["type"] == "flow" and ev["kind"] == "udp":
            rate = float(ev["rate_mbps"])
            out.append({"id": ev["id"], "hops": hops, "bulk": False,
                        "rate": lambda t, s=start, e=end, r=rate: r if s <= t < e else 0.0})
        elif ev["type"] == "flow":
            out.append({"id": ev["id"], "hops": hops, "bulk": True,
                        "rate": lambda t, s=start, e=end: math.inf if s <= t < e else 0.0})
        else:
            sent = rows(run.path / "traffic" / f"{ev['id']}-sent.csv")
            pts = [(run.t_unix_us(int(r["t_us"])), int(r["sent_bytes"])) for r in sent]
            # Realized offered load, 1 s mean centred on each 100 ms bin (a
            # trailing mean would put every onset ~0.5 s late).
            series = []
            for i, (t, _) in enumerate(pts):
                window = [b for _, b in pts[max(0, i - 5):i + 5]]
                series.append((t, sum(window) * 8 / 1e6 / (len(window) * 0.1)))
            out.append({"id": ev["id"], "hops": hops, "bulk": False,
                        # Zero outside the sender's log: the source has not started or has stopped.
                        "rate": lambda t, s=series: value_at(s, t) if s and s[0][0] <= t <= s[-1][0] + 0.1 else 0.0})
    return out


def maxmin_level(capacity: float, demands: list[float]) -> float:
    remaining, left = capacity, len(demands)
    for d in sorted(demands):
        share = remaining / left if left else math.inf
        if d > share:
            return share
        remaining -= d
        left -= 1
    return math.inf


def utilization(run: Run, demand: dict[str, float], caps, cross, paths, t: float) -> dict[str, float]:
    u = {sid: 0.0 for sid in run.subs}
    fq = run.aqm in FQ_AQMS
    for hop in {h for p in paths.values() for h in p}:
        cap = value_at(caps[hop], t) * 1e6
        media = {s: demand[s] for s, p in paths.items() if hop in p and active(run, s, t)}
        others = [f["rate"](t) * 1e6 for f in cross if hop in f["hops"]]
        bulk = any(math.isinf(x) for x in others)
        others = [x for x in others if not math.isinf(x)]
        total = sum(media.values()) + sum(others)
        if not fq:
            for s in media:
                u[s] = max(u[s], CLEAR_U if bulk else total / cap)
            continue
        level = maxmin_level(cap, [*media.values(), *others, *([math.inf] if bulk else [])])
        for s, d in media.items():
            u[s] = max(u[s], d / level if math.isfinite(level) else total / cap)
    return u


def active(run: Run, sid: str, t: float) -> bool:
    joins = {e["subscriber"]: e["at_s"] for e in run.scenario.get("events", []) if e["type"] == "join"}
    leaves = {e["subscriber"]: e["at_s"] for e in run.scenario.get("events", []) if e["type"] == "leave"}
    return joins.get(sid, 0) <= t < leaves.get(sid, math.inf)


def build_truth(run: Run) -> tuple[list[dict], dict[str, list[tuple[float, str]]]]:
    """Onset episodes per subscriber and the band on the GRID_S grid."""
    demand = {s: demand_bps(run, s) for s in run.subs}
    caps, cross = capacity_series(run), cross_series(run)
    paths = {s: path_hops(run, run.pub, s) for s in run.subs}
    grid = [i * GRID_S for i in range(int(run.duration / GRID_S))]
    bands: dict[str, list[tuple[float, str]]] = {s: [] for s in run.subs}
    us: dict[str, list[float]] = {s: [] for s in run.subs}
    for t in grid:
        for s, u in utilization(run, demand, caps, cross, paths, t).items():
            us[s].append(u)
            bands[s].append((t, "congested" if u >= CONGESTED_U else "clear" if u < CLEAR_U else "ambiguous"))
    episodes = []
    for s in run.subs:
        spans, start = [], None
        for (t, band), u in zip(bands[s], us[s]):
            if band == "congested" and start is None:
                start = t
            elif band != "congested" and start is not None:
                spans.append([start, t])
                start = None
        if start is not None:
            spans.append([start, run.duration])
        merged = []
        for a, b in spans:
            if merged and a - merged[-1][1] < MERGE_GAP_S:
                merged[-1][1] = b
            else:
                merged.append([a, b])
        for a, b in merged:
            if b - a < MIN_EPISODE_S or a < WARMUP_S:
                continue
            inside = [u for (t, _), u in zip(bands[s], us[s]) if a <= t < b]
            excess = sum(max(0.0, u - 1) for u in inside) * GRID_S
            episodes.append({"subscriber": s, "t0": round(a, 3), "end": round(b, 3),
                             "duration_s": round(b - a, 3), "peak_u": round(max(inside), 3),
                             "excess_s": round(excess, 3), "scored": int(excess >= MIN_EXCESS_S),
                             "demand_mbps": round(demand[s] / 1e6, 3)})
    return episodes, bands


def router_series(run: Run, iface_csv: Path, caps: list[tuple[float, float]]) -> dict[str, list[float]]:
    """Bottleneck egress per sample: queue delay at the current capacity, rates, drops + marks."""
    out = defaultdict(list)
    prev = None
    for x in rows(iface_csv):
        t = run.t_mono_us(int(x["timestamp_mono_ns"]) / 1000)
        if t < 0:
            continue
        cap = value_at(caps, t) * 1e6
        out["t"].append(t)
        out["queue_ms"].append(int(x["queue_backlog_bytes"]) * 8 / cap * 1000 if math.isfinite(cap) else 0)
        out["cap_mbps"].append(cap / 1e6)
        dt = int(x["interval_ns"]) / 1e9 or math.nan
        out["offered_mbps"].append(int(x["offered_bytes"]) * 8 / dt / 1e6)
        out["sent_mbps"].append(int(x["transmitted_bytes"]) * 8 / dt / 1e6)
        drops = marks = 0
        if prev is not None:
            drops = max(0, int(x["drops"]) - int(prev["drops"]))
            marks = max(0, int(x["ecn_marks"]) - int(prev["ecn_marks"]))
        out["drops"].append(drops)
        out["marks"].append(marks)
        prev = x
    return out


def bottleneck(run: Run, sid: str, caps) -> tuple[tuple[str, str], Path | None]:
    """The client's lowest-capacity hop and the router-metrics CSV of its egress."""
    hops = path_hops(run, run.pub, sid)
    hop = min(hops, key=lambda h: value_at(caps[h], 0))
    topology = load_topology(run.path / "topology.yaml")
    for edge in edge_interfaces(topology):
        iface = edge.a_iface if (edge.a, edge.b) == hop else edge.b_iface if (edge.b, edge.a) == hop else None
        if iface:
            path = run.path / "router-metrics" / hop[0] / f"{iface}.csv"
            return hop, path if path.exists() else None
    return hop, None


# ── detector replay ──────────────────────────────────────────────────────

def replay(run: Run, params: dict, samples_to: Path | None = None) -> list[dict]:
    """Detector events with run time t and subscriber, from moqx_shadow_replay.

    samples_to: also keep the first variant's per-ACK detector columns there,
    one <subscriber>.csv each (detector state for plots)."""
    if not REPLAY.exists():
        sys.exit(f"replay binary missing: {REPLAY} (build moq-testbed target moqx_shadow_replay)")
    paths = {s: path_hops(run, run.pub, s) for s in run.subs}
    # Group = clients sharing their first router egress (topology ground truth).
    group_of = {s: f"{p[1][0]}->{p[1][1]}" if len(p) > 1 else "" for s, p in paths.items()}
    sizes = defaultdict(int)
    for g in group_of.values():
        sizes[g] += 1
    with tempfile.TemporaryDirectory() as tmp:
        manifest = Path(tmp) / "manifest.tsv"
        lines = []
        for s in run.subs:
            acks = run.sender_file(s, "acks")
            if not acks.exists():
                sys.exit(f"{acks} missing: the run predates per-ACK recording")
            group = group_of[s] if sizes[group_of[s]] > 1 else ""
            lines.append("\t".join([s, s, group, s, str(acks), str(run.sender_file(s, "sent"))]))
        manifest.write_text("\n".join(lines) + "\n")
        argv = [str(REPLAY), "--manifest", str(manifest), "--output", tmp]
        if samples_to is None:
            argv.append("--events-only")
        for v in VARIANTS:
            argv += ["--variant", v]
        for k, v in params.items():
            argv += ["--param", f"{k}={v}"]
        subprocess.run(argv, check=True, capture_output=True)
        if samples_to is not None:
            samples_to.mkdir(parents=True, exist_ok=True)
            for f in (Path(tmp) / "samples").glob("*.csv"):
                f.replace(samples_to / f"{f.name.split('__')[0]}.csv")
        out = []
        with (Path(tmp) / "events.jsonl").open() as f:
            for line in f:
                e = json.loads(line)
                if e["scope"] != "flow":
                    continue
                out.append({"t": round(run.t_mono_us(e["mono_us"]), 4), "subscriber": e["flow"],
                            "variant": e["variant"] or "", "event": e["event"],
                            "evidence": "+".join(e.get("evidence", []))})
    return out


# ── scoring ──────────────────────────────────────────────────────────────

def band_at(bands: list[tuple[float, str]], t: float) -> str:
    i = min(len(bands) - 1, max(0, int(t / GRID_S)))
    return bands[i][1]


def score(run_dir: Path, overrides: dict | None = None, tag: str = "detector") -> None:
    run = Run(run_dir)
    episodes, bands = build_truth(run)
    events = replay(run, {**PARAMS, **(overrides or {})})
    if not overrides:
        events += [{**e, "variant": f"tuned:{e['variant']}"} for e in replay(run, TUNED) if e["variant"]]
    starts = defaultdict(list)
    for e in events:
        for name, (variant, ev) in DETECTORS.items():
            if e["variant"] == variant and e["event"] == ev:
                starts[(name, e["subscriber"])].append(e["t"])

    detections = []
    windows, minor = defaultdict(list), defaultdict(list)
    for ep in episodes:
        if not ep["scored"]:
            minor[ep["subscriber"]].append((ep["t0"], ep["end"]))
            continue
        lo, hi = ep["t0"] - PRE_ONSET_LEAD_S, min(ep["end"], ep["t0"] + SEARCH_S)
        windows[ep["subscriber"]].append((lo, hi))
        row = dict(ep)
        for name in DETECTORS:
            hit = next((t for t in sorted(starts[(name, ep["subscriber"])]) if lo <= t <= hi), None)
            row[f"{name}_ms"] = None if hit is None else round(max(0.0, hit - ep["t0"]) * 1000, 1)
        detections.append(row)

    alarms = []
    for (name, sid), ts in starts.items():
        used = set()
        for t in sorted(ts):
            win = next((w for w in windows[sid] if w[0] <= t <= w[1]), None)
            band = band_at(bands[sid], t)
            if t < WARMUP_S:
                label = "excluded"
            elif win is not None:
                label = "duplicate" if win in used else "tp"
                used.add(win)
            elif band != "clear" or any(a <= t <= b for a, b in minor[sid]):
                label = "excluded"
            else:
                label = "fp"
            alarms.append({"detector": name, "subscriber": sid, "t": t, "label": label, "band": band})

    clear_s = {s: sum(GRID_S for t, b in bands[s] if b == "clear" and t >= WARMUP_S) for s in run.subs}
    scored = sum(ep["scored"] for ep in episodes)
    out = run_dir / tag
    write_csv(out / "truth.csv", episodes)
    write_csv(out / "detections.csv", detections)
    write_csv(out / "alarms.csv", sorted(alarms, key=lambda a: (a["detector"], a["subscriber"], a["t"])))
    write_csv(out / "exposure.csv", [{"subscriber": s, "clear_s": round(v, 1)} for s, v in clear_s.items()])
    write_csv(out / "events.csv", events)
    if bursts := burst_truth(run):
        score_bursts(run, events, bursts)
    print(f"{run_dir.name}: aqm={run.aqm} onsets={scored} minor={len(episodes) - scored} "
          f"alarms={sum(a['detector'] == 'shadow' for a in alarms)}")


# ── burst benchmark (det-burstcap / det-burstudp) ────────────────────────

BURST_WARMUP_S = 15.0   # first burst starts here (det_matrix WARMUP_S)
BURST_RECOVERY_S = 2.0  # after a burst ends: queue drain + BBR recovery, not calm
ALARM_MERGE_S = 1.0     # alarm starts closer than this are one alarm episode (flaps)
BURST_DEADLINES_MS = (500, 1000, 2000)


def burst_truth(run: Run) -> list[dict]:
    """Injected bursts with exact start/end (run time) and the aggregate u they
    put on the bottleneck (all flows, FIFO view). Empty for other scenarios."""
    out = []
    links = [e for e in run.events if e["event"] == "link" and e["status"] == "applied"]
    caps = capacity_series(run)
    demand = {s: demand_bps(run, s) / 1e6 for s in run.subs}
    paths = {s: path_hops(run, run.pub, s) for s in run.subs}
    for i, e in enumerate(links):
        if not e["label"].startswith("burst u="):
            continue
        hop = tuple(e["target"].split(":")[0].split("->"))
        end = next(float(x["applied_s"]) for x in links[i + 1:]
                   if x["label"] == "burst-end" and tuple(x["target"].split(":")[0].split("->")) == hop)
        start = float(e["applied_s"])
        # Label "burst u=<u> d=<d> [client]": designed severity (a ramp's peak).
        fields = dict(f.split("=") for f in e["label"].split()[1:] if "=" in f)
        out.append({"start": start, "end": end, "kind": "ramp" if "ramp" in run.path.name else "capacity",
                    "hop": hop, "rate_mbps": value_at(caps[hop], start + 0.01),
                    "u_label": float(fields["u"]), "d_label": float(fields["d"])})
    applied = {e["target"]: float(e["applied_s"]) for e in run.events if e["event"] == "flow"}
    for ev in run.scenario.get("events", []):
        if ev["type"] == "flow" and ev.get("kind") == "tcp" and ev["id"] in applied:
            path = run.topology["traffic"]["routes"][ev["route"]]["path"]
            hops = list(zip(path, path[1:]))
            start = applied[ev["id"]]
            out.append({"start": start, "end": start + float(ev["duration_s"]), "kind": "tcp",
                        "hop": min(hops, key=lambda h: value_at(caps[h], start)), "rate_mbps": math.inf,
                        "u_label": 0.0, "d_label": float(ev["duration_s"])})
        if ev["type"] != "bursts":
            continue
        path = run.topology["traffic"]["routes"][ev["route"]]["path"]
        hops = list(zip(path, path[1:]))
        for b in rows(run.path / "traffic" / f"{ev['id']}-bursts.csv"):
            start = float(ev["at_s"]) + float(b["start_s"])
            # The bottleneck this burst crosses: the lowest-capacity hop of its route.
            hop = min(hops, key=lambda h: value_at(caps[h], start))
            out.append({"start": start, "end": start + float(b["duration_s"]), "kind": "udp", "hop": hop,
                        "rate_mbps": float(b["rate_mbps"])})
    for b in out:
        cap = value_at(caps[b["hop"]], b["start"] + 0.01)
        # Only the video behind this hop loads it.
        load = sum(d for s, d in demand.items() if b["hop"] in paths[s]) + (b["rate_mbps"] if b["kind"] == "udp" else 0)
        b["u_agg"] = round(load / cap, 3)
        b["u_cell"] = b.get("u_label", round(b["u_agg"], 1))
        b["d_cell"] = b.get("d_label", round(b["end"] - b["start"], 1))
    return sorted(out, key=lambda b: b["start"])


def alarm_episodes(starts: list[float]) -> list[float]:
    """First start of each run of alarm starts closer than ALARM_MERGE_S."""
    out, last = [], None
    for t in sorted(starts):
        if last is None or t - last >= ALARM_MERGE_S:
            out.append(t)
        last = t
    return out


def score_bursts(run: Run, events: list[dict], bursts: list[dict]) -> None:
    """Per client and burst: hit (model u_c >= 1 at mid-burst), unaffected
    (u_c < CLEAR_U) or uncertain. A hit is caught by the first alarm episode
    starting in [start, end + BURST_RECOVERY_S]; latency from the burst start.
    Alarm episodes: tp (first in a hit window), dup (later in it), uncertain
    (warm-up or an uncertain burst's window), fp (anywhere else: calm time and
    windows of bursts that did not affect this client)."""
    demand = {s: demand_bps(run, s) for s in run.subs}
    caps, cross = capacity_series(run), cross_series(run)
    paths = {s: path_hops(run, run.pub, s) for s in run.subs}
    hop_files = {}
    for s in run.subs:
        hop, path = bottleneck(run, s, caps)
        hop_files[hop] = path
    router = {hop: router_series(run, path, caps[hop]) for hop, path in hop_files.items() if path}
    starts = defaultdict(list)
    for e in events:
        for name, (variant, ev) in DETECTORS.items():
            if e["variant"] == variant and e["event"] == ev:
                starts[(name, e["subscriber"])].append(e["t"])

    truth_rows, alarm_rows, exposure = [], [], []
    for sid in run.subs:
        windows = []
        for i, b in enumerate(bursts):
            u_c = utilization(run, demand, caps, cross, paths, (b["start"] + b["end"]) / 2)[sid]
            cls = "hit" if u_c >= CONGESTED_U else "unaffected" if u_c < CLEAR_U else "uncertain"
            if b["kind"] == "tcp":
                cls = "uncertain"  # elastic TCP: the model cannot say; needs measured per-client truth
            windows.append((b["start"], b["end"] + BURST_RECOVERY_S, cls, i))
            row = {"subscriber": sid, "burst": i, "start": round(b["start"], 3), "end": round(b["end"], 3),
                   "kind": b["kind"], "u_cell": b["u_cell"], "d_cell": b["d_cell"], "u_agg": b["u_agg"],
                   "u_client": round(u_c, 3), "class": cls}
            r = router.get(b["hop"])
            row["router_qmax_ms"] = row["router_drops"] = ""
            if r:  # measured check: did the bottleneck queue or drop during the burst?
                inside = [k for k, t in enumerate(r["t"]) if b["start"] <= t <= b["end"] + 1.0]
                row["router_qmax_ms"] = round(max((r["queue_ms"][k] for k in inside), default=0), 1)
                row["router_drops"] = sum(r["drops"][k] + r["marks"][k] for k in inside)
            for name in DETECTORS:
                eps = alarm_episodes(starts[(name, sid)])
                hit = next((t for t in eps if b["start"] <= t <= b["end"] + BURST_RECOVERY_S), None)
                row[f"{name}_ms"] = None if hit is None or cls != "hit" else round((hit - b["start"]) * 1000, 1)
            truth_rows.append(row)
        busy = sorted((a, z) for a, z, cls, _ in windows if cls != "unaffected")
        covered, cursor = 0.0, BURST_WARMUP_S
        for a, z in busy:
            a, z = max(a, cursor), min(z, run.duration)
            if z > a:
                covered += z - a
                cursor = z
        exposure.append({"subscriber": sid, "calm_s": round(run.duration - BURST_WARMUP_S - covered, 1)})
        for name in DETECTORS:
            used = set()
            for t in alarm_episodes(starts[(name, sid)]):
                win = next((w for w in windows if w[0] <= t <= w[1] and w[2] != "unaffected"), None)
                if t < BURST_WARMUP_S:
                    label = "uncertain"
                elif win is None:
                    label = "fp"
                elif win[2] == "uncertain":
                    label = "uncertain"
                else:
                    label = "dup" if win[3] in used else "tp"
                    used.add(win[3])
                alarm_rows.append({"detector": name, "subscriber": sid, "t": round(t, 3), "label": label})
    out = run.path / "detector"
    write_csv(out / "bursts.csv", truth_rows)
    write_csv(out / "burst_alarms.csv", alarm_rows)
    write_csv(out / "burst_exposure.csv", exposure)


def summarize_bursts(run_dirs: list[Path], detectors: list[str], cell: tuple | None = None) -> list[dict]:
    """cell: (u_cell, d_cell) to restrict recall/latency to one severity."""
    hits, alarms, calm = [], [], 0.0
    for r in run_dirs:
        hits += [b for b in rows(r / "detector" / "bursts.csv") if b["class"] == "hit"]
        alarms += rows(r / "detector" / "burst_alarms.csv")
        calm += sum(float(x["calm_s"]) for x in rows(r / "detector" / "burst_exposure.csv"))
    if cell:
        hits = [b for b in hits if (float(b["u_cell"]), float(b["d_cell"])) == cell]
    out = []
    for name in detectors:
        lat = [float(b[f"{name}_ms"]) for b in hits if b[f"{name}_ms"]]
        mine = [a for a in alarms if a["detector"] == name]
        tp = sum(a["label"] == "tp" for a in mine)
        fp = sum(a["label"] == "fp" for a in mine)
        dup = sum(a["label"] == "dup" for a in mine)
        row = {"detector": name, "hits": len(hits)}
        for dl in BURST_DEADLINES_MS:
            row[f"recall@{dl}ms"] = round(sum(x <= dl for x in lat) / len(hits), 2) if hits else None
        row["recall_any"] = round(len(lat) / len(hits), 2) if hits else None
        row["lat_p50_ms"] = _q(lat, 0.5)
        row["lat_p90_ms"] = _q(lat, 0.9)
        if not cell:
            row["precision"] = round(tp / (tp + fp), 2) if tp + fp else None
            row["fa_per_min"] = round(fp / (calm / 60), 2) if calm else None
            row["episodes_per_hit"] = round((tp + dup) / tp, 2) if tp else None
        out.append(row)
    return out


def burst_report(run_dirs: list[Path], detectors: list[str] | None = None) -> tuple[str, list[dict]]:
    detectors = detectors or ["shadow", "shadow_verified", "shadow_m4", "gcc", "bbr"]
    cells = defaultdict(list)
    for r in run_dirs:
        cells[(Run(r).aqm, scenario_name(r))].append(r)
    lines, table = [], []
    for (aqm, scn), dirs in sorted(cells.items()):
        rows_ = summarize_bursts(dirs, detectors)
        lines += [f"### {aqm} / {scn} ({len(dirs)} runs, {rows_[0]['hits']} client-bursts hit)", "",
                  "| detector | " + " | ".join(k for k in rows_[0] if k not in {"detector", "hits"}) + " |",
                  "|---" * (len(rows_[0]) - 1) + "|"]
        for row in rows_:
            lines.append("| " + " | ".join("-" if v is None else str(v) for k, v in row.items() if k != "hits") + " |")
            table.append({"aqm": aqm, "scenario": scn, "cell": "all", "runs": len(dirs), **row})
        grid = sorted({(float(b["u_cell"]), float(b["d_cell"])) for r in dirs
                       for b in rows(r / "detector" / "bursts.csv")})
        lines += ["", "Recall (any) / median latency (ms) per severity (u = 0: elastic TCP):", "",
                  "| detector | " + " | ".join(f"u{u:g} {dd:g}s" for u, dd in grid) + " |",
                  "|---" * (len(grid) + 1) + "|"]
        for name in detectors:
            cells_ = []
            for u, dd in grid:
                (c,) = summarize_bursts(dirs, [name], (u, dd))
                cells_.append("-" if not c["hits"] else f"{c['recall_any']} / {c['lat_p50_ms']}")
                table.append({"aqm": aqm, "scenario": scn, "cell": f"u{u:g}-{dd:g}s", "runs": len(dirs), **c})
            lines.append(f"| {name} | " + " | ".join(cells_) + " |")
        lines.append("")
    return "\n".join(lines), table


# ── report ───────────────────────────────────────────────────────────────

def _q(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))]


def summarize(run_dirs: list[Path], detectors: list[str], tag: str = "detector") -> list[dict]:
    det, alarms, clear = [], [], 0.0
    for r in run_dirs:
        det += rows(r / tag / "detections.csv")
        alarms += rows(r / tag / "alarms.csv")
        clear += sum(float(x["clear_s"]) for x in rows(r / tag / "exposure.csv"))
    out = []
    for name in detectors:
        lat = [float(d[f"{name}_ms"]) for d in det if d[f"{name}_ms"]]
        tp = sum(a["label"] == "tp" for a in alarms if a["detector"] == name)
        fp = sum(a["label"] == "fp" for a in alarms if a["detector"] == name)
        row = {"detector": name, "onsets": len(det)}
        for dl in DEADLINES_MS:
            row[f"recall@{dl}ms"] = round(sum(x <= dl for x in lat) / len(det), 2) if det else None
        row["recall_any"] = round(len(lat) / len(det), 2) if det else None
        row["lat_p50_ms"] = _q(lat, 0.5)
        row["lat_p90_ms"] = _q(lat, 0.9)
        row["precision"] = round(tp / (tp + fp), 2) if tp + fp else None
        row["fa_per_min"] = round(fp / (clear / 60), 2) if clear else None
        out.append(row)
    return out


def report(run_dirs: list[Path], detectors: list[str] | None = None, tag: str = "detector",
           by_scenario: bool = True) -> tuple[str, list[dict]]:
    detectors = detectors or ["shadow", "shadow_verified", "shadow_m4", "gcc", "bbr"]
    cells = defaultdict(list)
    for r in run_dirs:
        cells[(Run(r).aqm, scenario_name(r) if by_scenario else "all")].append(r)
    lines = []
    all_rows = []
    for (aqm, scn), dirs in sorted(cells.items()):
        rows_ = summarize(dirs, detectors, tag)
        lines += [f"### {aqm} / {scn} ({len(dirs)} runs, {rows_[0]['onsets']} onsets)", "",
                  "| detector | " + " | ".join(k for k in rows_[0] if k not in {"detector", "onsets"}) + " |",
                  "|---" * (len(rows_[0]) - 1) + "|"]
        for row in rows_:
            lines.append("| " + " | ".join("-" if v is None else str(v) for k, v in row.items() if k != "onsets") + " |")
            all_rows.append({"aqm": aqm, "scenario": scn, "runs": len(dirs), **row})
        lines.append("")
    return "\n".join(lines), all_rows


def scenario_name(run_dir: Path) -> str:
    # det_matrix run ids: det-<scenario>-<aqm>-r<rep>
    parts = run_dir.name.split("-")
    return parts[1] if parts[0] == "det" and len(parts) >= 4 else run_dir.name


def main(argv: list[str]) -> None:
    """Options: --param KEY=VALUE (detector override), --tag NAME (output subdir,
    default detector), --detectors a,b (report), --all-scenarios (report: one
    table per AQM)."""
    if len(argv) < 2 or argv[0] not in {"score", "report", "bursts"}:
        sys.exit(__doc__)
    cmd, rest = argv[0], argv[1:]
    overrides, tag, detectors, by_scenario, dirs = {}, "detector", None, True, []
    while rest:
        a = rest.pop(0)
        if a == "--param":
            k, v = rest.pop(0).split("=")
            overrides[k] = float(v)
        elif a == "--tag":
            tag = rest.pop(0)
        elif a == "--detectors":
            detectors = rest.pop(0).split(",")
        elif a == "--all-scenarios":
            by_scenario = False
        else:
            dirs.append(Path(a))
    if cmd == "score":
        for d in dirs:
            score(d, overrides, tag)
    elif cmd == "bursts":
        print(burst_report(dirs, detectors)[0])
    else:
        print(report(dirs, detectors, tag, by_scenario)[0])


if __name__ == "__main__":
    main(sys.argv[1:])
