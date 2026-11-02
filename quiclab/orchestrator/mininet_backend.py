"""Mininet backend: the whole topology inside one (privileged) container.

Every node (publisher, subscriber, router, switch, traffic endpoint) is a
plain Mininet host: its own network namespace, sharing the container's file
system, kernel, and clock. Wiring comes from `links:` (one veth pair per
link); switches are Linux bridges in their own namespace; routers forward IP
and own the link queues. Shaping is explicit tc (orchestrator/shaping.py).

Addressing: each direct link or switched LAN gets a /24 from
`_LINK_SUBNET_POOL`; every IP node gets a canonical /32 on lo from
10.99.0.0/24. One shared /etc/hosts maps node names to the /32s, and static
/32 routes (BFS over the link graph) pin every flow to the declared path.

The scenario sets every link condition and router AQM at t=0 (the run
epoch) and then applies its events on time; the run tears down by itself at
`duration_s` (or, interactive, when the Mininet CLI exits). Mininet is
imported lazily so host-side commands (validate, design) work without it.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import shlex
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from quiclab.config.scenario import (
    RouterQueue,
    Scenario,
    TcpFlowEvent,
    UdpFlowEvent,
    load_scenario,
)
from quiclab.config.schema import DirectionSpec, TopologyConfig, load_topology
from quiclab.exceptions import OrchestratorError
from quiclab.orchestrator.routing import (
    addressed_links,
    next_hops,
    route_commands,
    routed_path,
)
from quiclab.orchestrator.shaping import (
    live_aqm_commands,
    live_shaping_commands,
    offload_disable_commands,
    shaping_commands,
)
from quiclab.orchestrator.scenario_runner import EventLog, ScenarioRunner
from quiclab.runtime import (
    all_node_ids,
    default_run_id,
    default_runs_dir,
    edge_interfaces,
    node_loopback_ips,
    traffic_route_ips,
    validate_run_id,
)

_log = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_QVIDEO_SERVER = _PROJECT_ROOT / "qvideo" / "build" / "qvideo-server"
_QVIDEO_CLIENT = _PROJECT_ROOT / "qvideo" / "build" / "qvideo-client"
_ROUTER_METRICS = _PROJECT_ROOT / "quiclab" / "router_metrics.py"

_LINK_SUBNET_POOL = "10.20.0.0/16"

# Routers must not interfere with the emulated paths: no reverse path
# filtering (asymmetric routes are legitimate) and no ICMP redirects.
_ROUTER_SYSCTLS = {
    "net.ipv4.ip_forward": "1",
    "net.ipv4.conf.all.rp_filter": "0",
    "net.ipv4.conf.default.rp_filter": "0",
    "net.ipv4.conf.all.send_redirects": "0",
    "net.ipv4.conf.default.send_redirects": "0",
}
_ENDPOINT_SYSCTLS = {
    "net.ipv4.conf.all.accept_redirects": "0",
    "net.ipv4.conf.default.accept_redirects": "0",
}

CommandRunner = Callable[[str, str], tuple[int, str]]


@dataclass
class RunRecord:
    run_id: str
    run_dir: Path
    loopback_ips: dict[str, str] = field(default_factory=dict)
    # (from, to) per link → (from-side IP, to-side IP) on that link's /24.
    edge_ips: dict[tuple[str, str], tuple[str, str]] = field(default_factory=dict)
    # node_id → ordered list of (iface_name, "x.x.x.x/24").
    node_iface_ips: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    # node_id → pid of its namespace shell (for mnexec and /proc/<pid>/net).
    pids: dict[str, int] = field(default_factory=dict)
    # Host monotonic time that scenario at_s values count from.
    epoch_mono_s: float | None = None


def _import_mininet():
    try:
        from mininet.cli import CLI
        from mininet.log import info, setLogLevel
        from mininet.net import Mininet
    except ImportError as e:
        raise OrchestratorError(
            f"Mininet is not importable: {e!s}. Run inside the quiclab image "
            "(`python -m quiclab run` starts it for you)."
        ) from e

    # Mininet's CLI resets identchars in __init__; extend them at run() so
    # hyphenated node ids like `sub-a` parse as one token.
    class _LenientCLI(CLI):  # type: ignore[misc, valid-type]
        def run(self):
            if "-" not in self.identchars:
                self.identchars = self.identchars + "-"
            super().run()

    return _LenientCLI, info, setLogLevel, Mininet


def namespace_runner(pids: dict[str, int]) -> CommandRunner:
    """Run a shell command inside a node's namespaces, safe from any thread."""

    def run(node_id: str, command: str) -> tuple[int, str]:
        pid = pids.get(node_id)
        if pid is None:
            raise OrchestratorError(f"unknown running node {node_id!r}")
        result = subprocess.run(
            ["mnexec", "-a", str(pid), "sh", "-c", command],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout + result.stderr

    return run


class MininetBackend:
    def __init__(self, runs_dir: str | Path | None = None) -> None:
        self._runs_root = Path(runs_dir) if runs_dir else default_runs_dir()
        self._runs_root.mkdir(parents=True, exist_ok=True)

    def up(
        self,
        topology_path: str | Path,
        scenario_path: str | Path,
        run_id: str | None = None,
        interactive: bool = False,
        on_running: Callable[[TopologyConfig, RunRecord, "LiveNetwork"], None] | None = None,
    ) -> RunRecord:
        topology = load_topology(topology_path)
        scenario = load_scenario(scenario_path, topology)
        for binary in (_QVIDEO_SERVER, _QVIDEO_CLIENT):
            if not binary.exists():
                raise OrchestratorError(
                    f"{binary} missing; run `python -m quiclab build qvideo` first"
                )
        run_id = run_id or default_run_id()
        validate_run_id(run_id)

        CLI, info, setLogLevel, Mininet = _import_mininet()
        setLogLevel("info")

        run_dir = self._runs_root / run_id
        if run_dir.exists():
            raise OrchestratorError(f"run dir {run_dir} already exists; choose a different --run-id")
        run_dir.mkdir(parents=True)
        for sub in ("logs", "clients", "traffic"):
            (run_dir / sub).mkdir()
        shutil.copyfile(topology_path, run_dir / "topology.yaml")
        shutil.copyfile(scenario_path, run_dir / "scenario.yaml")
        _modprobe_modules(topology, scenario)

        net = Mininet(controller=None, build=False, autoSetMacs=True)
        record = RunRecord(run_id=run_id, run_dir=run_dir, loopback_ips=node_loopback_ips(topology))
        processes: list[tuple[str, subprocess.Popen]] = []
        clients: dict[str, subprocess.Popen] = {}
        runner = None
        events = None
        try:
            self._build(net, topology, record, info)
            info("*** Starting network\n")
            net.start()
            record.pids = {nid: net.get(nid).pid for nid in all_node_ids(topology)}
            _write_etc_hosts(record)
            # The Mininet CLI rewrites node names via defaultIntf().updateIP(),
            # which reads the link /24 address; only the /32s are routed.
            for nid, ip in record.loopback_ips.items():
                intf = net.get(nid).defaultIntf()
                if intf is not None:
                    intf.updateIP = lambda ip=ip: ip
            # Mininet assigns its own addresses at start; re-apply ours.
            for nid, iface_ips in record.node_iface_ips.items():
                node = net.get(nid)
                for iface, ip_cidr in iface_ips:
                    node.cmd(f"ip addr flush dev {iface}")
                    if ip_cidr:
                        node.cmd(f"ip addr add {ip_cidr} dev {iface}")
                    node.cmd(f"ip link set {iface} up")

            self._configure_network(net, topology, scenario, record, info)
            processes.extend(_start_router_metrics(net, topology, record, info))
            _sanity_ping(net, topology, record)
            # One stream start (T0) shared by every client is also the scenario's
            # t=0, so events land at the same point of the GOP grid every run.
            mono_now, unix_now_ns = time.monotonic(), time.time_ns()
            start_unix_ns = unix_now_ns + int(topology.startup.stream_start_s * 1e9)
            record.epoch_mono_s = mono_now + topology.startup.stream_start_s
            processes.extend(_launch_publishers(net, topology, record, start_unix_ns // 1000, info))
            if topology.startup.publisher_warmup_s > 0:
                time.sleep(topology.startup.publisher_warmup_s)
            processes.extend(_start_iperf_servers(net, topology, scenario, record, info))
            initial = [sid for sid in topology.subscribers if scenario.join_at(sid) == 0]
            for sid in initial:
                clients[sid] = _launch_subscriber(net, topology, sid, record, info)
            _await_connected(topology, initial, record)
            time.sleep(max(0.0, record.epoch_mono_s - time.monotonic()))

            events = EventLog(run_dir / "events.csv", record.epoch_mono_s)
            events.write("epoch", 0.0, detail=f"duration_s={scenario.duration_s:g} "
                                              f"stream_start_unix_us={start_unix_ns // 1000}")
            network = LiveNetwork(topology, scenario, namespace_runner(record.pids), events)
            runner = ScenarioRunner(scenario, record.epoch_mono_s, events, {
                "link": network.apply_event,
                "aqm": network.apply_event,
                "flow": lambda e: _start_flow(net, topology, scenario, record, processes, e),
                "join": lambda e: _join(net, topology, e.subscriber, record, clients, info),
                "leave": lambda e: _leave(e.subscriber, clients),
            })
            runner.start()
            info(f"*** scenario: {len(scenario.events)} event(s), {scenario.duration_s:g} s\n")
            if on_running is not None:
                on_running(topology, record, network)

            info(f"\n*** quiclab run_id={run_id}  output: {run_dir}\n")
            if interactive:
                info("***   Exit the CLI to tear the topology down (the scenario keeps running).\n\n")
                CLI(net)
            else:
                info("***   Running until the scenario ends; Ctrl-C tears down early.\n")
                runner.finished.wait()
        finally:
            if runner is not None:
                runner.stop()
            processes.extend(clients.items())
            _stop_processes(processes)
            if events is not None:
                events.write("teardown", "")
                events.close()
            _iperf_results_to_csv(run_dir / "traffic")
            info("*** Stopping network\n")
            try:
                net.stop()
            except Exception as e:  # net.stop() can throw on partial state
                _log.warning("net.stop() raised during teardown: %s", e)
            _hand_back_run_dir(run_dir)
        return record

    def _build(self, net, topology: TopologyConfig, record: RunRecord, info) -> None:
        """Add every node and link to `net`. Pure construction; no start()."""
        info(f"*** quiclab run_id={record.run_id}\n")
        record.node_iface_ips, _ = addressed_links(topology, _LINK_SUBNET_POOL)
        nodes = {nid: net.addHost(nid, ip=None) for nid in all_node_ids(topology)}
        interface_addresses = {
            iface: address
            for entries in record.node_iface_ips.values()
            for iface, address in entries
        }
        for edge in edge_interfaces(topology):
            a_ip = interface_addresses[edge.a_iface]
            b_ip = interface_addresses[edge.b_iface]
            net.addLink(
                nodes[edge.a],
                nodes[edge.b],
                intfName1=edge.a_iface,
                intfName2=edge.b_iface,
            )
            record.edge_ips[(edge.a, edge.b)] = (a_ip.split("/")[0], b_ip.split("/")[0])

    @staticmethod
    def _configure_network(
        net, topology: TopologyConfig, scenario: Scenario, record: RunRecord, info
    ) -> None:
        """Bridges, loopbacks, sysctls, offloads, static routes, shaping."""
        node_ids = list(record.loopback_ips)

        for sid in topology.switches:
            node = net.get(sid)
            node.cmd("ip link add br0 type bridge stp_state 0")
            for iface, _ in record.node_iface_ips[sid]:
                node.cmd(f"ip addr flush dev {iface}")
                node.cmd(f"ip link set {iface} master br0")
                node.cmd(f"ip link set {iface} up")
            node.cmd("ip link set br0 up")

        info("*** Assigning canonical /32 loopback addresses and sysctls\n")
        for nid in node_ids:
            node = net.get(nid)
            node.cmd("ip link set lo up")
            node.cmd(f"ip addr replace {record.loopback_ips[nid]}/32 dev lo")
            sysctls = _ROUTER_SYSCTLS if nid in topology.routers else _ENDPOINT_SYSCTLS
            for key, value in sysctls.items():
                node.cmd(f"echo {value} > /proc/sys/{key.replace('.', '/')}")

        info("*** Disabling NIC offloads on link interfaces\n")
        for nid, iface_ips in record.node_iface_ips.items():
            node = net.get(nid)
            for iface, _ in iface_ips:
                for cmd in offload_disable_commands(iface):
                    out = node.cmd(cmd)
                    if out and out.strip():
                        _log.warning("%s: %r printed: %s", nid, cmd, out.strip())

        info("*** Installing static /32 routes\n")
        edges = edge_interfaces(topology)
        if topology.switches:
            _, neighbor_addrs = addressed_links(topology, _LINK_SUBNET_POOL)
        else:
            neighbor_addrs = {}
            for edge in edges:
                a_ip, b_ip = record.edge_ips[(edge.a, edge.b)]
                neighbor_addrs.setdefault(edge.a, {})[edge.b] = (b_ip, edge.a_iface)
                neighbor_addrs.setdefault(edge.b, {})[edge.a] = (a_ip, edge.b_iface)
        hops = next_hops(node_ids, [
            (node, peer) for node, peers in neighbor_addrs.items() for peer in peers
        ])
        for nid in node_ids:
            node = net.get(nid)
            for cmd in route_commands(nid, hops[nid], record.loopback_ips, neighbor_addrs.get(nid, {})):
                node.cmd(cmd)

        if topology.traffic is not None:
            aliases = traffic_route_ips(topology)
            for name, (sender_ip, receiver_ip) in aliases.items():
                path = topology.traffic.routes[name].path
                net.get(path[0]).cmd(f"ip addr replace {sender_ip}/32 dev lo")
                net.get(path[-1]).cmd(f"ip addr replace {receiver_ip}/32 dev lo")
            for name, route in topology.traffic.routes.items():
                sender_ip, receiver_ip = aliases[name]
                path = routed_path(route.path, topology.switches)
                for target, hops_path in ((receiver_ip, path), (sender_ip, list(reversed(path)))):
                    for index, (current, neighbor) in enumerate(zip(hops_path, hops_path[1:])):
                        next_ip, iface = neighbor_addrs[current][neighbor]
                        source = ""
                        if index == 0:
                            source = f" src {sender_ip if target == receiver_ip else receiver_ip}"
                        net.get(current).cmd(
                            f"ip route replace {target}/32 via {next_ip} dev {iface}{source}"
                        )

        info("*** Applying initial link conditions and AQMs from the scenario\n")
        for edge, link in zip(edges, topology.links):
            forward, reverse = scenario.initial_link(link.from_, link.to)
            for nid, iface, spec in ((edge.a, edge.a_iface, forward), (edge.b, edge.b_iface, reverse)):
                node = net.get(nid)
                queue = scenario.router_queue(nid) if nid in topology.routers else RouterQueue()
                for cmd in shaping_commands(iface, spec, queue.aqm, queue.dualpi2_target_ms,
                                            queue.queue_limit_packets,
                                            (queue.red_min_bytes, queue.red_max_bytes)):
                    status, out = _node_command_status(node, cmd)
                    if status:
                        raise OrchestratorError(f"{nid}: {cmd!r} failed: {out or f'exit {status}'}")


def _write_etc_hosts(record: RunRecord) -> None:
    # Hosts share the container's file system: one file serves every node.
    marker = "# quiclab"
    lines = [
        line for line in Path("/etc/hosts").read_text().splitlines() if not line.endswith(marker)
    ]
    lines += [f"{ip}\t{nid}\t{marker}" for nid, ip in record.loopback_ips.items()]
    Path("/etc/hosts").write_text("\n".join(lines) + "\n")


def _popen(net, node_id: str, argv: list[str], log_path: Path) -> subprocess.Popen:
    log = log_path.open("ab")
    try:
        return net.get(node_id).popen(argv, stdout=log, stderr=subprocess.STDOUT)
    finally:
        log.close()  # the child keeps its own descriptor


def _launch_publishers(net, topology: TopologyConfig, record: RunRecord, start_unix_us: int, info) -> list:
    started = []
    for pid, publisher in topology.publishers.items():
        out_dir = record.run_dir / "publishers" / pid
        out_dir.mkdir(parents=True, exist_ok=True)
        workers = publisher.workers or max(1, len(topology.subscribers_of(pid)))
        argv = [
            str(_QVIDEO_SERVER),
            "--host=0.0.0.0",
            f"--port={publisher.listen_port}",
            f"--cc={publisher.cc_algo}",
            f"--ladder_kbps={','.join(map(str, publisher.ladder_kbps))}",
            f"--fps={publisher.fps}",
            f"--gop_ms={publisher.gop_ms}",
            f"--ip_ratio={publisher.ip_ratio}",
            f"--size_sigma={publisher.size_sigma}",
            f"--seed={publisher.seed}",
            f"--stats_ms={publisher.stats_ms}",
            f"--workers={workers}",
            f"--start_unix_us={start_unix_us}",
            f"--out_dir={out_dir}",
            "--logtostderr",
        ]
        info(f"*** {pid}: {shlex.join(argv)}\n")
        started.append((pid, _popen(net, pid, argv, record.run_dir / "logs" / f"{pid}.log")))
    return started


def _launch_subscriber(net, topology: TopologyConfig, sid: str, record: RunRecord, info) -> subprocess.Popen:
    subscriber = topology.subscribers[sid]
    publisher = topology.publishers[subscriber.connects_to]
    argv = [
        str(_QVIDEO_CLIENT),
        f"--host={subscriber.connects_to}",
        f"--port={publisher.listen_port}",
        f"--id={sid}",
        f"--rate_kbps={subscriber.rate_kbps}",
        f"--phase_ms={subscriber.phase_ms}",
        f"--fps={publisher.fps}",
        f"--buffer_ms={subscriber.buffer_ms}",
        f"--stats_ms={subscriber.stats_ms}",
        f"--out_dir={record.run_dir / 'clients'}",
        "--logtostderr",
    ]
    info(f"*** {sid}: {shlex.join(argv)}\n")
    return _popen(net, sid, argv, record.run_dir / "logs" / f"{sid}.log")


def _await_connected(topology: TopologyConfig, subscribers: list[str], record: RunRecord) -> None:
    """Every subscriber's request reached its publisher before the stream start.

    The publisher opens <sub>-cc.csv when the request arrives; a client that
    misses T0 would tune in a GOP later and break run-to-run comparability.
    """
    pending = set(subscribers)
    while pending:
        pending = {
            sid for sid in pending
            if not (record.run_dir / "publishers" / topology.subscribers[sid].connects_to / f"{sid}-cc.csv").exists()
        }
        if pending and time.monotonic() >= record.epoch_mono_s:
            raise OrchestratorError(
                f"{sorted(pending)} not connected before the stream start; raise startup.stream_start_s"
            )
        time.sleep(0.02)


_spawn_lock = threading.Lock()


def _join(net, topology, sid: str, record: RunRecord, clients: dict, info) -> tuple[str, str]:
    # Mininet node shells are not thread-safe; popen spawns mnexec directly.
    with _spawn_lock:
        clients[sid] = _launch_subscriber(net, topology, sid, record, info)
    return sid, f"pid={clients[sid].pid}"


def _leave(sid: str, clients: dict) -> tuple[str, str]:
    process = clients.get(sid)
    if process is None or process.poll() is not None:
        raise OrchestratorError(f"{sid} is not running")
    process.terminate()
    return sid, "terminated"


def _flow_port(topology: TopologyConfig, scenario: Scenario, flow_id: str) -> int:
    ids = [flow.id for flow in scenario.flows()]
    return topology.defaults.traffic.base_port + ids.index(flow_id)


def _start_iperf_servers(net, topology: TopologyConfig, scenario: Scenario, record: RunRecord, info) -> list:
    flows = scenario.flows()
    if not flows:
        return []
    assert topology.traffic is not None
    aliases = traffic_route_ips(topology)
    started = []
    for flow in flows:
        receiver = topology.traffic.routes[flow.route].path[-1]
        port = _flow_port(topology, scenario, flow.id)
        argv = ["iperf3", "-s", "-1", "-B", aliases[flow.route][1], "-p", str(port)]
        started.append((receiver, _popen(net, receiver, argv, record.run_dir / "logs" / f"{flow.id}-server.log")))
    deadline = time.monotonic() + topology.startup.traffic_ready_timeout_s
    for flow in flows:
        receiver = topology.traffic.routes[flow.route].path[-1]
        port = _flow_port(topology, scenario, flow.id)
        while f":{port} " not in net.get(receiver).cmd(f"ss -Hltn sport = :{port}") + " ":
            if time.monotonic() > deadline:
                raise OrchestratorError(f"iperf3 server for flow {flow.id!r} did not start")
            time.sleep(0.05)
    info(f"*** {len(started)} iperf3 server(s) listening\n")
    return started


def iperf_client_argv(topology: TopologyConfig, scenario: Scenario, flow: TcpFlowEvent | UdpFlowEvent) -> list[str]:
    sender_ip, receiver_ip = traffic_route_ips(topology)[flow.route]
    argv = [
        "iperf3", "-c", receiver_ip, "-B", sender_ip, "-p", str(_flow_port(topology, scenario, flow.id)),
        "-t", f"{flow.duration_s:g}", "--json",
    ]
    if isinstance(flow, TcpFlowEvent):
        argv += ["-P", str(flow.parallel)]
        if flow.cc is not None:
            argv += ["-C", flow.cc]
    else:
        argv += ["-u", "-b", f"{flow.rate_mbps:g}M", "-l", str(flow.packet_size_bytes)]
    return argv


def _start_flow(net, topology, scenario, record: RunRecord, processes: list, flow) -> tuple[str, str]:
    sender = topology.traffic.routes[flow.route].path[0]
    argv = iperf_client_argv(topology, scenario, flow)
    with _spawn_lock:
        process = _popen(net, sender, argv, record.run_dir / "traffic" / f"{flow.id}.json")
        processes.append((sender, process))
    return flow.id, f"{flow.kind} {shlex.join(argv[1:])}"


IPERF_FIELDS = (
    "flow", "unix_s", "start_s", "end_s", "bytes", "bits_per_second",
    "retransmits", "snd_cwnd_bytes", "rtt_us", "jitter_ms", "lost_packets", "packets",
)


def iperf_json_to_csv(json_path: Path, csv_path: Path) -> None:
    """One row per iperf3 interval (summed over parallel streams)."""
    data = json.loads(json_path.read_text() or "{}")
    start_unix = data.get("start", {}).get("timestamp", {}).get("timesecs", 0)
    with csv_path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=IPERF_FIELDS)
        writer.writeheader()
        for interval in data.get("intervals", []):
            total = interval["sum"]
            streams = interval.get("streams", [])
            single = streams[0] if len(streams) == 1 else {}
            writer.writerow({
                "flow": json_path.stem,
                "unix_s": f"{start_unix + total['start']:.3f}",
                "start_s": f"{total['start']:.3f}",
                "end_s": f"{total['end']:.3f}",
                "bytes": total.get("bytes", ""),
                "bits_per_second": f"{total.get('bits_per_second', 0):.0f}",
                "retransmits": total.get("retransmits", ""),
                "snd_cwnd_bytes": single.get("snd_cwnd", ""),
                "rtt_us": single.get("rtt", ""),
                "jitter_ms": total.get("jitter_ms", ""),
                "lost_packets": total.get("lost_packets", ""),
                "packets": total.get("packets", ""),
            })
        if data.get("error"):
            writer.writerow({"flow": json_path.stem, "unix_s": "", "start_s": "error",
                             "end_s": data["error"]})


def _iperf_results_to_csv(traffic_dir: Path) -> None:
    for json_path in sorted(traffic_dir.glob("*.json")):
        try:
            iperf_json_to_csv(json_path, json_path.with_suffix(".csv"))
            json_path.unlink()
        except (OSError, ValueError, KeyError) as e:
            _log.warning("iperf3 result %s kept as JSON: %s", json_path.name, e)


def _stop_processes(processes: list[tuple[str, subprocess.Popen]]) -> None:
    # Clients first so their final playback rows are written while servers live.
    for _, process in reversed(processes):
        if process.poll() is None:
            process.terminate()
    deadline = time.monotonic() + 5
    for node_id, process in processes:
        try:
            process.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            _log.warning("%s: process %s ignored SIGTERM; killing", node_id, process.args)
            process.kill()


def _start_router_metrics(net, topology: TopologyConfig, record: RunRecord, info) -> list:
    started = []
    for router_id, router in topology.routers.items():
        if not router.queue_metrics.enabled:
            continue
        interfaces = client_facing_router_interfaces(topology, router_id)
        if not interfaces:
            raise OrchestratorError(f"router {router_id!r} queue_metrics found no client-facing egress")
        info(f"*** Sampling {router_id} queue metrics every {router.queue_metrics.interval_ms} ms\n")
        node = net.get(router_id)
        out_dir = record.run_dir / "router-metrics" / router_id
        out_dir.mkdir(parents=True, exist_ok=True)
        prefixes = []
        for iface in interfaces:
            for command in (
                f"tc qdisc replace dev {iface} clsact",
                f"tc filter replace dev {iface} egress protocol all pref 49152 handle 1 matchall action pass",
            ):
                status, output = _node_command_status(node, command)
                if status:
                    raise OrchestratorError(f"{router_id}: {command!r} failed: {output or f'exit {status}'}")
            prefix = out_dir / iface
            log = record.run_dir / "logs" / f"{router_id}-metrics-{iface}.log"
            started.append((router_id, _popen(net, router_id, [
                "python3", str(_ROUTER_METRICS), "--interface", iface,
                "--interval-ms", str(router.queue_metrics.interval_ms),
                "--output", f"{prefix}.csv",
            ], log)))
            if router.queue_metrics.queue_interval_ms is not None:
                started.append((router_id, _popen(net, router_id, [
                    "python3", str(_ROUTER_METRICS), "--interface", iface, "--queue-only",
                    "--interval-ms", str(router.queue_metrics.queue_interval_ms),
                    "--output", f"{prefix}-queue.csv",
                ], log)))
            prefixes.append((iface, prefix, router.queue_metrics.queue_interval_ms is not None))
        # Collectors write their first rows after a moment; poll, do not race.
        deadline = time.monotonic() + 3
        for iface, prefix, queue_only in prefixes:
            files = [Path(f"{prefix}.csv")]
            if queue_only:
                files.append(Path(f"{prefix}-queue.csv"))
            while not all(f.exists() and f.stat().st_size for f in files):
                if time.monotonic() > deadline:
                    raise OrchestratorError(f"{router_id}: queue metrics failed on {iface}; see logs/")
                time.sleep(0.05)
    return started


def _sanity_ping(net, topology: TopologyConfig, record: RunRecord) -> None:
    """Best-effort ping along every publisher/subscriber pair; warn-only."""
    for sid, subscriber in topology.subscribers.items():
        out = net.get(sid).cmd(f"ping -c1 -W2 {record.loopback_ips[subscriber.connects_to]}")
        if " 0% packet loss" not in out:
            _log.warning("sanity ping %s -> %s failed:\n%s", sid, subscriber.connects_to, out)


def apply_live_link_shaping(
    topology: TopologyConfig,
    link_index: int,
    direction: str,
    spec: DirectionSpec,
    previous: DirectionSpec,
    run: CommandRunner,
) -> None:
    """Change one link direction in place without flushing its qdisc chain."""
    edge = edge_interfaces(topology)[link_index]
    node_id, iface = (edge.a, edge.a_iface) if direction == "forward" else (edge.b, edge.b_iface)
    try:
        commands = live_shaping_commands(iface, previous, spec)
    except ValueError as error:
        raise OrchestratorError(f"{node_id}: {error}") from error

    def apply(pending: list[str]) -> None:
        for command in pending:
            status, output = run(node_id, command)
            if status:
                raise OrchestratorError(f"{node_id}: {command!r} failed: {output.strip() or f'exit {status}'}")

    try:
        apply(commands)
    except OrchestratorError:
        try:
            apply(live_shaping_commands(iface, spec, previous))
        except OrchestratorError as rollback_error:
            _log.error("failed to restore %s %s shaping: %s", node_id, iface, rollback_error)
        raise


def apply_live_router_aqm(
    topology: TopologyConfig,
    router_id: str,
    queue: RouterQueue,
    previous: RouterQueue,
    specs: dict[tuple[int, str], DirectionSpec],
    run: CommandRunner,
) -> None:
    """Replace the AQM leaf on every egress owned by one running router."""

    def apply(value: RouterQueue, current: RouterQueue) -> None:
        for index, edge in enumerate(edge_interfaces(topology)):
            if edge.a == router_id:
                iface, spec = edge.a_iface, specs[(index, "forward")]
            elif edge.b == router_id:
                iface, spec = edge.b_iface, specs[(index, "reverse")]
            else:
                continue
            for command in live_aqm_commands(
                iface, spec, value.aqm, current.aqm, value.dualpi2_target_ms,
                value.queue_limit_packets, (value.red_min_bytes, value.red_max_bytes),
            ):
                status, output = run(router_id, command)
                if status:
                    raise OrchestratorError(f"{router_id}: {command!r} failed: {output.strip() or f'exit {status}'}")

    try:
        apply(queue, previous)
    except OrchestratorError:
        try:
            apply(previous, queue)
        except OrchestratorError as rollback_error:
            _log.error("failed to restore %s AQM: %s", router_id, rollback_error)
        raise


class LiveNetwork:
    """Current link conditions and AQMs of a running topology.

    The scenario runner and the visualizer both change the network through
    here, so every change is serialized and lands in events.csv.
    """

    def __init__(self, topology: TopologyConfig, scenario: Scenario, run: CommandRunner,
                 events: EventLog) -> None:
        self.topology = topology
        self._run = run
        self._events = events
        self._lock = threading.Lock()
        self.links: dict[tuple[int, str], DirectionSpec] = {}
        for index, link in enumerate(topology.links):
            forward, reverse = scenario.initial_link(link.from_, link.to)
            self.links[(index, "forward")] = forward
            self.links[(index, "reverse")] = reverse
        self.queues = {rid: scenario.router_queue(rid) for rid in topology.routers}

    def set_link(self, index: int, direction: str, spec: DirectionSpec) -> None:
        with self._lock:
            previous = self.links[(index, direction)]
            if spec != previous:
                apply_live_link_shaping(self.topology, index, direction, spec, previous, self._run)
                self.links[(index, direction)] = spec

    def set_queue(self, router_id: str, queue: RouterQueue) -> None:
        with self._lock:
            previous = self.queues[router_id]
            if queue != previous:
                apply_live_router_aqm(self.topology, router_id, queue, previous, self.links, self._run)
                self.queues[router_id] = queue

    def apply_event(self, event) -> tuple[str, str]:
        """Scenario `link` / `aqm` events (the runner records them)."""
        if event.type == "aqm":
            queue = event.queue()
            self.set_queue(event.router, queue)
            return event.router, _queue_text(queue)
        index = next(i for i, link in enumerate(self.topology.links)
                     if (link.from_, link.to) == (event.from_, event.to))
        spec = event.applied_to(self.links[(index, event.direction)])
        self.set_link(index, event.direction, spec)
        return f"{event.from_}->{event.to}:{event.direction}", _spec_text(spec)

    def manual(self, kind: str, target: str, apply: Callable[[], None], detail: str) -> None:
        """Visualizer edits: applied like events and recorded as `manual_*`."""
        try:
            apply()
        except OrchestratorError as e:
            self._events.write(f"manual_{kind}", "", target, detail, error=str(e))
            raise
        self._events.write(f"manual_{kind}", "", target, detail)


def _spec_text(spec: DirectionSpec) -> str:
    return " ".join(f"{k}={v:g}" for k, v in spec.model_dump().items() if v is not None)


def _queue_text(queue: RouterQueue) -> str:
    return " ".join(
        f"{k}={v.value if hasattr(v, 'value') else v}" for k, v in queue.model_dump().items() if v is not None
    ) or "aqm=default"


def client_facing_router_interfaces(topology: TopologyConfig, router_id: str) -> list[str]:
    """Router egresses whose far-side component contains a receiver."""
    adjacency: dict[str, set[str]] = {}
    for link in topology.links:
        adjacency.setdefault(link.from_, set()).add(link.to)
        adjacency.setdefault(link.to, set()).add(link.from_)
    receivers = set(topology.subscribers)
    if topology.traffic is not None:
        receivers.update(endpoint.id for endpoint in topology.traffic.receivers)

    result = []
    for edge in edge_interfaces(topology):
        if edge.a == router_id:
            peer, iface = edge.b, edge.a_iface
        elif edge.b == router_id:
            peer, iface = edge.a, edge.b_iface
        else:
            continue
        pending = [peer]
        reachable: set[str] = set()
        while pending:
            node = pending.pop()
            if node == router_id or node in reachable:
                continue
            reachable.add(node)
            pending.extend(adjacency.get(node, ()))
        if reachable & receivers:
            result.append(iface)
    return result


def _node_command_status(node, command: str) -> tuple[int, str]:
    marker = "__QUICLAB_COMMAND_STATUS__"
    output = node.cmd(f'{command}; printf "\\n{marker}%s\\n" "$?"')
    before, found, after = output.rpartition(marker)
    if not found:
        return 1, f"{output.strip()} (missing command status)".strip()
    try:
        status = int(after.splitlines()[0].strip())
    except (IndexError, ValueError):
        return 1, f"{output.strip()} (invalid command status)".strip()
    return status, before.strip()


def _modprobe_modules(topology: TopologyConfig, scenario: Scenario) -> None:
    """Best-effort modprobe (host /lib/modules is mounted) before tc needs them."""
    queues = [*scenario.routers.values(), *(e.queue() for e in scenario.events if e.type == "aqm")]
    modules = {f"sch_{q.aqm.value}" for q in queues if q.aqm}
    modules.discard("sch_pfifo")  # built into sch_fifo
    modules |= {"sch_htb", "sch_netem"}
    if any(isinstance(f, TcpFlowEvent) and f.cc == "bbr" for f in scenario.flows()):
        modules.add("tcp_bbr")
    for module in sorted(modules):
        try:
            subprocess.run(["modprobe", module], check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError) as e:
            _log.warning("modprobe %s failed (%s); relying on kernel autoload", module, e)


def _hand_back_run_dir(run_dir: Path) -> None:
    """The container runs as root; give the run output back to the host user."""
    uid, gid = os.environ.get("QUICLAB_HOST_UID"), os.environ.get("QUICLAB_HOST_GID")
    if not uid or not gid:
        return
    subprocess.run(["chown", "-R", f"{uid}:{gid}", str(run_dir)], check=False)
