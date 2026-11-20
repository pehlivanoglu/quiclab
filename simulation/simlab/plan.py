#!/usr/bin/env python3
"""Testbed run plan -> simulator plan + run-folder skeleton.

    python3 simulation/simlab/plan.py <testbed run dir> <sim run dir> [--seed N]

Reads the testbed run's own topology.yaml + scenario.yaml through quiclab's models and
helpers (read-only use of the quiclab package: link conditions, router queues, interface
names, loopback addresses, traced / sampled egresses, qtraffic schedules), so the
simulation runs the same plan and operating point. Writes:

    <sim run>/sim/plan.txt       read by ns3/quicsim (one record per line)
    <sim run>/topology.yaml, scenario.yaml          verbatim copies (the frozen readers' input)
    <sim run>/events.csv         the testbed's event log rows, applied exactly at at_s
    <sim run>/grouping/{windows,plan}.json, v3-plan.json, v3-stimuli.csv   plan artifacts, copied

Anything the simulation does not model raises (no silent approximation): jitter, loss,
asymmetric delays, fq_codel / cake / dualpi2, TCP background, salvos, asv, pauses,
forced paths, AQM changes, delay changes.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB))

from quiclab import router_trace  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.orchestrator import mininet_backend as mb  # noqa: E402  (mininet itself is imported lazily)
from quiclab.runtime import all_node_ids, edge_interfaces, node_loopback_ips, traffic_route_ips  # noqa: E402

# Simulation constants (tags as in simulation/NOTES.md).
UNSHAPED_BPS = 10_000_000_000      # (FLAG) a direction without bandwidth: veth, effectively unlimited
NETEM_LIMIT_P = 50_000             # (M) shaping.py _NETEM_LIMIT_PKTS: queue of a direction with netem, no AQM
HTB_LEAF_LIMIT_P = 1_000           # (FLAG) rate-only direction without AQM: htb's default leaf, txqueuelen 1000
AQM_DEFAULT_LIMIT_P = 1_000        # (FLAG) Linux default limit of pfifo / codel / pie when the plan gives none
SEGMENT = 1208                     # (M) TCP payload: 1208 + 52 = 1260 B IP packet, the testbed's 1232 B QUIC packet
# Delayed-ACK profiles (receiver side, per client):
#   spec     every 2 segments, at most 25 ms (spec 4 "close to mvfst"; the user found that assumption wrong)
#   matched  the testbed's mvfst policy (mvfst 4b691f3, qvideo/build/_deps/mvfst-src):
#            ACK after 10 ack-eliciting packets (QuicConstants.h:625,627 rxPacketsBeforeAck{Before,After}Init = 10;
#            QuicStateFunctions.cpp:128-152), else on the ACK timer max(timer tick, min(maxAckDelay, 0.25 x srtt))
#            rounded up to ms (QuicTransportBaseLite.cpp:3766-3777; kAckTimerFactor 0.25 QuicConstants.h:631;
#            kMaxAckTimeout 25 ms :633; AckStates.h:81); tick = folly HHWheelTimer default 10 ms (HHWheelTimer.h:99;
#            qvideo Client.cpp:265 default EventBase). No ACK_FREQUENCY (Client.cpp:69-85 sets none).
#            ns-3 has one fixed delayed-ACK timeout per socket: it is set from the client's base RTT (FLAG: mvfst
#            uses the live srtt, so under queueing its timer grows up to 25 ms).
DELACK = {"spec": (2, 25.0), "matched": (10, None)}
MVFST_TICK_MS, MVFST_MAX_ACK_DELAY_MS, MVFST_ACK_TIMER_FACTOR = 10, 25, 0.25


def delack_for(profile: str, base_rtt_s: float) -> tuple[int, float]:
    count, ms = DELACK[profile]
    if ms is None:
        ms = max(MVFST_TICK_MS, math.ceil(min(MVFST_MAX_ACK_DELAY_MS, MVFST_ACK_TIMER_FACTOR * base_rtt_s * 1000)))
    return count, ms
SNDBUF = RCVBUF = 16 << 20         # (FLAG) large: the send queue lives in the application (pump caps it at a cwnd)
INIT_CWND = 10                     # (M) segments, as Linux / mvfst
MIN_RTO_MS = 200                   # (M) Linux minimum RTO (ns-3 default 1 s)
EPOCH_S = 2.0                      # (FLAG) simulator time of scenario t = 0; clients connect before it
CONNECT_LEAD_S = 1.0               # initial clients connect this long before the epoch
MONO0_NS = 1_000_000_000_000_000   # clock offsets: any fixed values work (readers subtract the epoch)
UNIX0_NS = 1_800_000_000_000_000_000
VIDEO_PORT_BASE = 40_000
BG_SPORT_BASE, BG_SPORT_STRIDE = 30_000, 300


class Unsupported(RuntimeError):
    pass


def kv(**items) -> str:
    return " ".join(f"{k}={v}" for k, v in items.items())


def _secs(ms) -> float:
    return (ms or 0.0) / 1000.0


TRACE_MODES = ("full", "sample", "none")
SAMPLE_EVERY, SAMPLE_MIN = 10, 3          # (P) user 2026-11-18: upstream + every 10th leaf, never fewer than 3 leaves


def sampled_leaves(plan: dict) -> list[str]:
    """Leaf egresses traced under "sample": every 10th leaf in name order (the first, the 11th, ...), topped up in name
    order to at least 3 (or all leaves if there are fewer). The upstream egress ("up") is always traced."""
    leaves = sorted(n for n in plan.get("egress", {}) if n != "up")
    pick = leaves[::SAMPLE_EVERY]
    for x in leaves:
        if len(pick) >= min(SAMPLE_MIN, len(leaves)):
            break
        if x not in pick:
            pick.append(x)
    return sorted(pick)


PORT_MODES = ("global", "route", "reuse")
PORT_SPAN = 65_536 - BG_SPORT_BASE       # ports available above BG_SPORT_BASE on one source node
REUSE_GUARD_S = 1.0                      # (P) a port block is reused only this long after its source ended
PER_FLOW_AQMS = ("fq_codel", "fq_pie", "fq_cobalt", "cake", "sfq", "fq")


def bg_ports(events: list, mode: str) -> list[int]:
    """First source port of every background / stimulus source, in event order.
    global (stages A / B, default): one range, blocks of max(STRIDE, flows), as before item 5;
    route  (stage C): per route (source node), blocks of exactly the source's flows, never reused;
    reuse  (stage C, pfifo without GT-Q only): per route, a block is given to a later source once the earlier
           one has ended (REUSE_GUARD_S later); the source opens its sockets at its start (plan "lazy=1")."""
    out = [0] * len(events)
    if mode == "global":
        sport = BG_SPORT_BASE
        for i, e in enumerate(events):
            out[i] = sport
            sport += max(BG_SPORT_STRIDE, len(getattr(e, "flow_weights", None) or [1]))
            if sport > 65_536:
                raise Unsupported(f"background source ports beyond 65535 at {e.id}")
        return out
    nxt: dict[str, int] = {}
    active: dict[str, list[tuple[int, int, float]]] = {}   # route -> [(first, flows, end_s)]
    for i in sorted(range(len(events)), key=lambda k: (events[k].at_s, k)):
        e = events[i]
        n = len(getattr(e, "flow_weights", None) or [1])
        if mode == "route":
            first = nxt.get(e.route, 0)
            nxt[e.route] = first + n
        else:
            live = [b for b in active.get(e.route, []) if b[2] + REUSE_GUARD_S > e.at_s]
            first = 0
            for a, k, _ in sorted(live):
                if first + n <= a:
                    break
                first = max(first, a + k)
            live.append((first, n, e.at_s + e.duration_s))
            active[e.route] = live
        if first + n > PORT_SPAN:
            raise Unsupported(f"background source ports beyond 65535 on route {e.route} at {e.id} ({mode})")
        out[i] = BG_SPORT_BASE + first
    return out


FAST_BPS = 100_000_000_000              # (P) user 2026-11-19: every link direction that is not a designed bottleneck


def build(tb_run: Path, out: Path, seed: int, ack: str = "spec", trace: str = "full", ports: str = "global",
          fast_links: bool = False) -> list[str]:
    topo = load_topology(tb_run / "topology.yaml")
    scen = load_scenario(tb_run / "scenario.yaml", topo)
    lines = [
        "run " + kv(duration_s=f"{scen.duration_s:g}", epoch_s=EPOCH_S, mono0_ns=MONO0_NS, unix0_ns=UNIX0_NS,
                    seed=seed, segment=SEGMENT, ack_profile=ack, delack_count=DELACK["spec"][0], delack_ms=DELACK["spec"][1], sndbuf=SNDBUF,
                    rcvbuf=RCVBUF, init_cwnd=INIT_CWND, min_rto_ms=MIN_RTO_MS, connect_lead_s=CONNECT_LEAD_S,
                    **({"all_totals": 1} if fast_links else {}))
    ]
    # fast links (stage C and the 300-client test; user 2026-11-19): a direction that is not a designed bottleneck
    # (a shaped egress of v3-plan.json) never limits; testbed-counterpart plans keep the testbed's rates
    bott = ({tuple(e["hop"].split("->")) for e in json.loads((tb_run / "v3-plan.json").read_text())["egress"].values()
             if e.get("shaped")} if fast_links else set())
    for nid in all_node_ids(topo):
        lines.append("node " + kv(name=nid))

    # links and every egress queue (shaping.py chain: htb -> netem -> AQM)
    edges = edge_interfaces(topo)
    iface_hop: dict[str, tuple[str, str]] = {}
    spec_of: dict[tuple[str, str], object] = {}
    for edge, link in zip(edges, topo.links):
        fwd, rev = scen.initial_link(link.from_, link.to)
        for spec in (fwd, rev):
            if spec.jitter_ms is not None or spec.loss_pct is not None:
                raise Unsupported(f"jitter / loss on {link.from_}-{link.to}")
        rate = lambda s: int(s.bandwidth_mbps * 1e6) if s.bandwidth_mbps is not None else UNSHAPED_BPS  # noqa: E731
        fast = lambda a, b, s: FAST_BPS if fast_links and (a, b) not in bott else rate(s)  # noqa: E731
        lines.append("link " + kv(a=edge.a, b=edge.b, rate_ab=fast(edge.a, edge.b, fwd), rate_ba=fast(edge.b, edge.a, rev),
                                  delay_ab=_secs(fwd.delay_ms), delay_ba=_secs(rev.delay_ms)))
        for nid, peer, iface, spec in ((edge.a, edge.b, edge.a_iface, fwd), (edge.b, edge.a, edge.b_iface, rev)):
            iface_hop[iface] = (nid, peer)
            spec_of[(nid, peer)] = spec
            queue = scen.router_queue(nid).on(peer) if nid in topo.routers else None
            aqm = queue.aqm.value if queue is not None and queue.aqm is not None else None
            if aqm is None:
                limit = NETEM_LIMIT_P if spec.delay_ms is not None else HTB_LEAF_LIMIT_P
                lines.append("egress " + kv(node=nid, peer=peer, aqm="fifo", limit_p=limit))
                continue
            if aqm not in ("pfifo", "codel", "pie", "red"):
                raise Unsupported(f"AQM {aqm} on {nid}->{peer}")
            limit = queue.queue_limit_packets
            if queue.queue_limit_bdp is not None:
                limit = mb.bdp_queue_limit(topo, scen, (nid, peer), spec, queue.queue_limit_bdp)
            limit = limit or AQM_DEFAULT_LIMIT_P
            extra = {}
            if aqm == "red":   # shaping.py _red_profile, bytes (Linux red is byte-based)
                lo = queue.red_min_bytes or 20_000
                hi = queue.red_max_bytes or 60_000
                extra = dict(min_b=lo, max_b=hi, limit_b=(queue.queue_limit_packets * 1500 if queue.queue_limit_packets
                                                          else 4 * hi), avpkt=1200, max_p=0.02, rate_bps=rate(spec))
            if queue.ecn is not False and aqm in ("codel", "pie", "red"):
                raise Unsupported(f"ECN on {nid}->{peer} (spec 4: ECN off)")
            lines.append("egress " + kv(node=nid, peer=peer, aqm=aqm, limit_p=limit, **extra))

    # sampled (router-metrics) and traced (GT-Q) egresses, exactly the testbed's selection
    metrics = {iface for rid, r in topo.routers.items() if r.queue_metrics.enabled
               for iface in mb.client_facing_router_interfaces(topo, rid)}
    traced = ({iface for lst in mb.gtq_trace_interfaces(topo, scen).values() for iface, _ in lst}
              if router_trace.enabled(topo) else set())
    pkt_clients = None   # None: every client per the global flag (trace "full", the testbed's behaviour)
    if trace != "full":
        v3plan = json.loads((tb_run / "v3-plan.json").read_text())
        keep = {"up", *sampled_leaves(v3plan)} if trace == "sample" else set()
        hops = {tuple(v3plan["egress"][n]["hop"].split("->")) for n in keep}
        traced = {i for i in traced if iface_hop[i] in hops}
        pkt_clients = {c for n in keep - {"up"} for c in v3plan["egress"][n]["clients"]}
    for n, iface in enumerate(sorted(metrics | traced), start=2):
        nid, peer = iface_hop[iface]
        qm = topo.routers[nid].queue_metrics if nid in topo.routers else None
        lim = next((ln for ln in lines if ln.startswith(f"egress node={nid} peer={peer} ")), "")
        limit_p = int(lim.split("limit_p=")[1].split()[0]) if "limit_p=" in lim else 0
        lines.append("monitor " + kv(node=nid, peer=peer, iface=iface, metrics=int(iface in metrics),
                                     interval_ms=qm.interval_ms if qm else 25,
                                     queue_interval_ms=(qm.queue_interval_ms or 0) if qm else 0,
                                     trace=int(iface in traced), delay_s=_secs(spec_of[(nid, peer)].delay_ms),
                                     limit_p=limit_p, ifindex=n, **({"totals": 1} if trace != "full" else {})))

    # video
    ips = node_loopback_ips(topo)
    pub_id, pub = next(iter(topo.publishers.items()))
    if len(topo.publishers) != 1:
        raise Unsupported("more than one publisher")
    leave_at = {e.subscriber: e.at_s for e in scen.events if e.type == "leave"}
    for i, (sid, sub) in enumerate(topo.subscribers.items()):
        if sub.path is not None:
            raise Unsupported(f"forced path for {sid}")
        lines.append("video " + kv(sid=sid, pub=sub.connects_to, rate_kbps=sub.rate_kbps, phase_ms=sub.phase_ms or 0,
                                   port=VIDEO_PORT_BASE + i, join_s=f"{scen.join_at(sid):g}",
                                   leave_s=f"{leave_at.get(sid, -1):g}", pub_ip=ips[sub.connects_to], sub_ip=ips[sid],
                                   **({} if pkt_clients is None else {"pkt_log": int(sid in pkt_clients)}),
                                   **dict(zip(("delack_count", "delack_ms"),
                                              delack_for(ack, mb.base_rtt_s(topo, scen, sub.connects_to, sid))))))
    gop_frames = max(1, round(pub.gop_ms * pub.fps / 1000))
    first_sub = next(iter(topo.subscribers.values()))
    lines.append("videoparams " + kv(pub=pub_id, fps=pub.fps, gop_frames=gop_frames, ip_ratio=pub.ip_ratio,
                                     sigma=pub.size_sigma, vseed=pub.seed, send_buffer_ms=pub.send_buffer_ms,
                                     stats_ms=pub.stats_ms, client_stats_ms=first_sub.stats_ms,
                                     buffer_ms=first_sub.buffer_ms, pkt_log=int(router_trace.enabled(topo))))

    # background and stimuli: the qtraffic sources, as qtraffic_send_argv builds them
    routes = traffic_route_ips(topo)
    if ports == "reuse":   # user 2026-11-19 (U2): only without GT-Q and without a per-flow queue
        other = [ln.split()[1:4] for ln in lines if ln.startswith("egress ")
                 and not any(f" aqm={q} " in ln for q in ("pfifo", "fifo"))]
        if trace != "none" or other:
            raise Unsupported(f"port reuse needs trace 'none' (no GT-Q) and pfifo queues only (no per-flow queue); "
                              f"trace {trace}, other queues {other[:2]}")
    events = list(scen.ppbp())
    first_port = bg_ports(events, ports)
    for ei, e in enumerate(events):
        path = topo.traffic.routes[e.route].path
        saddr, daddr = routes[e.route]
        common = dict(id=e.id, src=path[0], dst=path[-1], at_s=f"{e.at_s:g}", duration_s=f"{e.duration_s:g}",
                      packet=e.packet_size_bytes, port=mb._flow_port(topo, scen, e.id),
                      sport=first_port[ei], saddr=saddr, daddr=daddr, **({"lazy": 1} if ports == "reuse" else {}))
        sched = lambda entries: ",".join(f"{a:g}:{d:g}:{r:g}" for a, d, r in entries)  # noqa: E731
        if e.type == "ppbp":
            lines.append("bg " + kv(**common, process="pace", seed=e.seed,
                                    ppbp=f"{e.mean_mbps:g}:{e.burst_mbps:g}:{e.mean_burst_s:g}:{e.hurst:g}"))
        elif e.type == "bg":
            if e.process == "tcp":
                raise Unsupported(f"TCP background {e.id}")
            lines.append("bg " + kv(**common, process="poisson", seed=e.seed, schedule=sched(e.schedule()),
                                    weights=",".join(f"{w:g}" for w in e.flow_weights)))
        elif e.type == "bursts" and e.process == "pace":
            lines.append("bg " + kv(**common, process="pace", seed=1,
                                    schedule=sched((b.start_s, b.duration_s, b.rate_mbps) for b in e.bursts)))
        elif e.type == "bursts" and e.process == "poisson":
            lines.append("bg " + kv(**common, process="poisson", seed=e.seed, schedule=sched(e.schedule()),
                                    weights=",".join(f"{w:g}" for w in (e.flow_weights or [1.0]))))
        else:
            raise Unsupported(f"traffic source {e.id} ({e.type} {getattr(e, 'process', '')})")

    # live changes
    for e in scen.events:
        if e.type in ("bg", "bursts", "ppbp", "join", "leave"):
            continue
        if e.type == "link":
            if any(getattr(e, k, None) is not None for k in ("delay_ms", "jitter_ms", "loss_pct")):
                raise Unsupported(f"link event at {e.at_s} changes delay / jitter / loss")
            a, b = (e.from_, e.to) if e.direction == "forward" else (e.to, e.from_)
            lines.append("linkevent " + kv(t_s=f"{e.at_s:g}", a=a, b=b, rate_bps=int(e.bandwidth_mbps * 1e6)))
            continue
        raise Unsupported(f"scenario event type {e.type} at {e.at_s}")
    return lines


def planned_event_rows(plan_dir: Path) -> list[dict]:
    """events.csv rows for a plan that never ran on the testbed (stage C, generated by the v4 suite): the rows
    the testbed's runner writes (mininet_backend: epoch, one per scenario event with the same detail text, end,
    teardown); applied times are filled in by event_rows."""
    topo = load_topology(plan_dir / "topology.yaml")
    scen = load_scenario(plan_dir / "scenario.yaml", topo)
    base = dict(at_s="", applied_s="", applied_mono_ns="", applied_unix_ns="", target="", detail="", label="",
                status="applied", error="")
    rows = [dict(base, event="epoch", at_s="0", detail=f"duration_s={scen.duration_s:g} stream_start_unix_us=0")]
    for e in scen.events:
        detail = {"bg": lambda e: f"bg {e.process} rate_mbps={e.rate_mbps:g} flows={len(e.flow_weights)}",
                  "bursts": lambda e: f"bursts={len(e.bursts)} process={e.process}",
                  "ppbp": lambda e: (f"mean_mbps={e.mean_mbps:g} burst_mbps={e.burst_mbps:g} "
                                     f"mean_burst_s={e.mean_burst_s:g} hurst={e.hurst:g} seed={e.seed}")}.get(e.type)
        if detail is None:
            raise Unsupported(f"no events.csv row model for planned event type {e.type}")
        rows.append(dict(base, event=e.type, at_s=f"{e.at_s:g}", target=e.id, detail=detail(e), label=e.label or ""))
    rows.append(dict(base, event="end", at_s=f"{scen.duration_s:g}"))
    rows.append(dict(base, event="teardown"))
    return rows


def event_rows(tb_run: Path) -> list[str]:
    """events.csv: the testbed's rows with the applied times replaced by the exact plan times."""
    import csv

    def mono(t: float) -> int:
        return MONO0_NS + round((EPOCH_S + t) * 1e9)

    def unix(t: float) -> int:
        return UNIX0_NS + round((EPOCH_S + t) * 1e9)

    out = []
    if not (tb_run / "events.csv").exists():
        rows = planned_event_rows(tb_run)
    else:
        with (tb_run / "events.csv").open() as f:
            rows = list(csv.DictReader(f))
    fields = list(rows[0])
    for r in rows:
        if r["event"] == "teardown":
            t = float(rows[-2]["applied_s"] or rows[-2]["at_s"] or 0) if len(rows) > 1 else 0.0
        else:
            t = float(r["at_s"] or 0)
        r = dict(r, applied_s=f"{t:.6f}", applied_mono_ns=mono(t), applied_unix_ns=unix(t), status="applied", error="")
        if r["event"] == "epoch":
            r["detail"] = " ".join(w if not w.startswith("stream_start_unix_us=") else
                                   f"stream_start_unix_us={unix(0) // 1000}" for w in r["detail"].split())
        out.append(r)
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(out)
    return buf.getvalue().splitlines()


PLAN_ARTIFACTS = ("grouping/windows.json", "grouping/plan.json", "v3-plan.json", "v3-stimuli.csv")


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("testbed_run", type=Path)
    ap.add_argument("sim_run", type=Path)
    ap.add_argument("--seed", type=int, required=True, help="rep index (spec 4: rep index = seed)")
    ap.add_argument("--ack", choices=sorted(DELACK), default="spec", help="receiver delayed-ACK profile")
    ap.add_argument("--trace", choices=TRACE_MODES, default="full",
                    help="full = the testbed's traced egresses (stages A / B); sample = upstream + every 10th leaf (>= 3) "
                         "and -pkts / -pktacks only for their clients; none = no per-packet router trace (stage C)")
    ap.add_argument("--ports", choices=PORT_MODES, default="global",
                    help="background source ports: global (stages A / B), route (stage C), reuse (stage C, pfifo "
                         "without GT-Q only; sockets open at each source's start)")
    ap.add_argument("--fast-links", action="store_true",
                    help="every link direction that is not a designed bottleneck at 100 Gb/s, and queue totals of every "
                         "queue disc (stage C and the 300-client test only; never for a testbed-counterpart run)")
    a = ap.parse_args(argv)
    lines = build(a.testbed_run, a.sim_run, a.seed, a.ack, a.trace, a.ports, a.fast_links)
    (a.sim_run / "sim").mkdir(parents=True, exist_ok=True)
    (a.sim_run / "sim" / "plan.txt").write_text("\n".join(lines) + "\n")
    for name in ("topology.yaml", "scenario.yaml"):
        shutil.copyfile(a.testbed_run / name, a.sim_run / name)
    (a.sim_run / "events.csv").write_text("\n".join(event_rows(a.testbed_run)) + "\n")
    for rel in PLAN_ARTIFACTS:
        if (a.testbed_run / rel).exists():
            (a.sim_run / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(a.testbed_run / rel, a.sim_run / rel)
    (a.sim_run / "sim" / "source.txt").write_text(f"testbed_run={a.testbed_run.resolve()}\nseed={a.seed}\nack={a.ack}\n")
    print(f"plan: {len(lines)} records -> {a.sim_run / 'sim' / 'plan.txt'}")


if __name__ == "__main__":
    main(sys.argv[1:])
