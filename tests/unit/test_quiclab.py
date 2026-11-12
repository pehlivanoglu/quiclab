from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

import csv
import json
import time

from quiclab.config.scenario import RouterQueue, Scenario, load_scenario
from quiclab.config.schema import DirectionSpec, TopologyConfig, load_topology
from quiclab.designer import dump_draft_yaml, schema_contract_issues
from quiclab.orchestrator.mininet_backend import (
    LiveNetwork,
    MininetBackend,
    RunRecord,
    _queue_text,
    apply_live_router_aqm,
    client_facing_router_interfaces,
    initial_shaping_commands,
    iperf_client_argv,
    iperf_json_to_csv,
)
from quiclab.orchestrator.scenario_runner import EventLog, ScenarioRunner
from quiclab.orchestrator.routing import addressed_links
from quiclab.runtime import edge_interfaces, node_loopback_ips, remove_partial_run, run_finished, topology_edges
from quiclab.visualizer import (
    read_last_row,
    read_netns_counters,
    snapshot_status,
    topology_snapshot,
)

CONFIGS = Path(__file__).resolve().parents[2] / "configs"
TOPOLOGIES = CONFIGS / "topologies"
PAIRS = [
    ("single.yaml", "single-step.yaml"),
    ("shared.yaml", "shared-cross.yaml"),
    ("cc-sweep.yaml", "aqm-cc-sweep.yaml"),
    ("flowbot-like.yaml", "flowbot-load-070.yaml"),
    ("flowbot-like.yaml", "flowbot-load-080.yaml"),
    ("flowbot-like.yaml", "flowbot-load-090.yaml"),
    ("flowbot-like.yaml", "flowbot-load-100.yaml"),
]


def _shared() -> TopologyConfig:
    return load_topology(TOPOLOGIES / "shared.yaml")


def _shared_scenario() -> Scenario:
    return load_scenario(CONFIGS / "scenarios" / "shared-cross.yaml", _shared())


def _raw(name: str) -> dict:
    return yaml.safe_load((TOPOLOGIES / name).read_text())


def _scenario_raw(name: str) -> dict:
    return yaml.safe_load((CONFIGS / "scenarios" / name).read_text())


@pytest.mark.parametrize(("topology", "scenario"), PAIRS)
def test_examples_validate_and_round_trip_through_designer(topology: str, scenario: str) -> None:
    load_scenario(CONFIGS / "scenarios" / scenario, load_topology(TOPOLOGIES / topology))
    assert TopologyConfig.model_validate(yaml.safe_load(dump_draft_yaml(_raw(topology))))


def test_designer_schema_contract_holds() -> None:
    assert schema_contract_issues() == []


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: d["subscribers"]["sub"].update(rate_kbps=1234), "not on publisher"),
        (lambda d: d["subscribers"]["sub"].update(connects_to="nope"), "not a known publisher"),
        (lambda d: d["subscribers"]["sub"].update(phase_ms=2000), "phase_ms"),
        (lambda d: d["publishers"]["pub"].update(ladder_kbps=[500, 500]), "duplicate"),
        (lambda d: d.update(links=d["links"][:1]), "no path of links"),
        (lambda d: d["publishers"]["pub"].update(cc_algo="vegas"), "cc_algo"),
        (lambda d: d.update(startup={"publisher_warmup_s": 2, "stream_start_s": 1.5}), "stream_start_s"),
    ],
)
def test_schema_rejects(mutate, message: str) -> None:
    raw = _raw("single.yaml")
    mutate(raw)
    with pytest.raises(ValueError, match=message):
        TopologyConfig.model_validate(raw)


def test_application_edges_and_addresses() -> None:
    topology = _shared()
    assert ("pub", "sub-a") in topology_edges(topology)
    loopbacks = node_loopback_ips(topology)
    assert "switch" not in loopbacks and len(set(loopbacks.values())) == len(loopbacks)
    iface_ips, neighbors = addressed_links(topology)
    # Bridge ports are unnumbered; LAN members see each other across the bridge.
    assert all(ip == "" for _, ip in iface_ips["switch"])
    assert "sub-b" in neighbors["sub-a"] and "router" in neighbors["sub-a"]


def test_live_aqm_swap_respects_egress_overrides() -> None:
    topology = _shared()
    names = {e.a_iface: e.b for e in edge_interfaces(topology) if e.a == "router"}
    names |= {e.b_iface: e.a for e in edge_interfaces(topology) if e.b == "router"}
    specs = {(i, d): DirectionSpec() for i in range(len(topology.links)) for d in ("forward", "reverse")}
    mixed = RouterQueue(aqm="pfifo", egress={"switch": RouterQueue(aqm="fq_codel")})
    assert mixed.on("switch").aqm == "fq_codel" and mixed.on("sub-ctrl").aqm == "pfifo"
    ran = []

    def run(node, command):
        ran.append((node, command))
        return 0, ""

    apply_live_router_aqm(topology, "router", RouterQueue(aqm="pie"), mixed, specs, run)
    assert {node for node, _ in ran} == {"router"}
    # Each egress is replaced by the router-wide queue; the override is gone.
    replaced = {names[c.split()[4]]: c.split()[-2:] for _, c in ran}
    assert set(replaced) == set(names.values())
    assert all(aqm[0] == "pie" for aqm in replaced.values())


def test_queue_text_is_unchanged_without_overrides() -> None:
    assert _queue_text(RouterQueue(aqm="fq_codel", queue_limit_packets=80)) == "aqm=fq_codel queue_limit_packets=80"
    assert _queue_text(RouterQueue()) == "aqm=default"


def test_router_metrics_follow_receiver_side_egresses() -> None:
    topology = _shared()
    names = {e.a_iface: e.b for e in edge_interfaces(topology) if e.a == "router"}
    names |= {e.b_iface: e.a for e in edge_interfaces(topology) if e.b == "router"}
    facing = {names[i] for i in client_facing_router_interfaces(topology, "router")}
    assert facing == {"switch", "sub-ctrl"}


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: d["links"].append({"from": "sub-a", "to": "switch"}), "declared from/to order"),
        (lambda d: d["routers"].update(nope={}), "not a topology router"),
        (lambda d: d["events"].append({"at_s": 5, "type": "link", "from": "switch", "to": "sub-a",
                                        "bandwidth_mbps": 3}), "congestion belongs on a router egress"),
        (lambda d: d["events"].append({"at_s": 5, "type": "link", "from": "router", "to": "switch",
                                        "direction": "reverse", "bandwidth_mbps": 3}),
         "congestion belongs on a router egress"),
        (lambda d: d["routers"]["router"].update(egress={"sub-a": {"aqm": "pie"}}), "not neighbors of router"),
        (lambda d: d["routers"]["router"].update(egress={"switch": {"egress": {"pub": {"aqm": "pie"}}}}),
         "cannot have its own egress"),
        (lambda d: d["events"].append({"at_s": 5, "type": "aqm", "router": "router",
                                        "egress": {"sub-a": {"aqm": "pie"}}}), "not neighbors of router"),
        (lambda d: d["routers"]["router"].update(aqm=None), "queue_limit_packets requires an aqm"),
        (lambda d: d["routers"]["router"].update(aqm="red", queue_limit_packets=30), "must exceed red_max_bytes"),
        (lambda d: d["events"].append({"at_s": 95, "type": "leave", "subscriber": "sub-a"}), "after duration_s"),
        (lambda d: (d.pop("link_defaults"), d["events"].append(
            {"at_s": 5, "type": "link", "from": "pub", "to": "router", "direction": "reverse",
             "bandwidth_mbps": 3})), "no initial bandwidth_mbps"),
        (lambda d: d["events"].append({"at_s": 5, "type": "link", "from": "router", "to": "switch",
                                        "delay_ms": 3}), "declare loss_pct: 0"),
        (lambda d: d["events"].append({"at_s": 70, "type": "flow", "kind": "udp", "id": "cross-udp",
                                        "route": "shared", "duration_s": 1, "rate_mbps": 1}), "duplicate flow"),
        (lambda d: d["events"].append({"at_s": 80, "type": "flow", "kind": "tcp", "id": "late",
                                        "route": "shared", "duration_s": 20}), "past duration_s"),
        (lambda d: d["events"].append({"at_s": 85, "type": "bursts", "id": "b", "route": "shared",
                                        "bursts": [{"start_s": 1, "duration_s": 5, "rate_mbps": 2}]}),
         "past duration_s"),
        (lambda d: d["events"].append({"at_s": 5, "type": "bursts", "id": "b", "route": "nope",
                                        "bursts": [{"start_s": 0, "duration_s": 1, "rate_mbps": 2}]}),
         "unknown traffic route"),
        (lambda d: d["events"].extend([{"at_s": 5, "type": "leave", "subscriber": "sub-d"},
                                       {"at_s": 8, "type": "leave", "subscriber": "sub-d"}]), "leaves before it joins"),
        (lambda d: d["events"].append({"at_s": 20, "type": "join", "subscriber": "sub-d"}), "joins twice"),
        (lambda d: d["events"].append({"at_s": 10, "type": "leave", "subscriber": "sub-d"}), "two membership events"),
        (lambda d: d["events"].append({"at_s": 5, "type": "join", "subscriber": "ghost"}), "not a topology subscriber"),
    ],
)
def test_scenario_rejects(mutate, message: str) -> None:
    raw = _scenario_raw("shared-cross.yaml")
    mutate(raw)
    with pytest.raises(ValueError, match=message):
        Scenario.model_validate(raw).check_against(_shared())


def test_bursts_event_is_a_qtraffic_source() -> None:
    raw = _scenario_raw("shared-cross.yaml")
    raw["events"].append({"at_s": 10, "type": "bursts", "id": "b", "route": "shared", "bursts": [
        {"start_s": 0, "duration_s": 1, "rate_mbps": 3}, {"start_s": 5, "duration_s": 4, "rate_mbps": 8}]})
    scenario = Scenario.model_validate(raw)
    scenario.check_against(_shared())
    (bursts,) = [e for e in scenario.ppbp() if e.type == "bursts"]
    assert bursts.duration_s == 9 and "b" in scenario.traffic_ids()


def test_scenario_initial_conditions_merge_defaults() -> None:
    scenario = _shared_scenario()
    forward, reverse = scenario.initial_link("router", "switch")
    assert forward.bandwidth_mbps == 6 and reverse.bandwidth_mbps == 100
    forward, _ = scenario.initial_link("switch", "sub-a")
    assert forward.bandwidth_mbps == 100 and forward.delay_ms == 5
    # Unlisted links get the defaults; listed links lay their fields over them.
    assert scenario.initial_link("switch", "traffic-rx")[0].bandwidth_mbps == 100
    assert scenario.join_at("sub-d") == 10 and scenario.join_at("sub-a") == 0


def test_subscriber_sessions_alternate_and_get_session_ids() -> None:
    raw = _scenario_raw("shared-cross.yaml")
    raw["events"] += [{"at_s": 30, "type": "leave", "subscriber": "sub-d"},
                      {"at_s": 50, "type": "join", "subscriber": "sub-d"},
                      {"at_s": 40, "type": "leave", "subscriber": "sub-a"},
                      {"at_s": 60, "type": "join", "subscriber": "sub-a"},
                      {"at_s": 70, "type": "leave", "subscriber": "sub-a"}]
    scenario = Scenario.model_validate(raw).check_against(_shared())
    assert scenario.sessions("sub-d") == [(10, 30), (50, None)]
    assert scenario.sessions("sub-a") == [(0.0, 40), (60, 70)]
    assert scenario.sessions("sub-b") == [(0.0, None)]
    assert Scenario.session_id("sub-a", 1) == "sub-a" and Scenario.session_id("sub-a", 2) == "sub-a_2"
    subs = {"sub-a", "sub-b"}
    assert Scenario.session_of("sub-a_2", subs) == ("sub-a", 2) and Scenario.session_of("sub-a_12", subs) == ("sub-a", 12)
    assert Scenario.session_of("sub-a", subs) == ("sub-a", 1) and Scenario.session_of("sub-x_2", subs) == ("sub-x_2", 1)
    assert Scenario.session_of("sub-a_1", subs) == ("sub-a_1", 1)


def test_later_session_id_must_not_collide_with_a_subscriber() -> None:
    import copy
    topology = _shared()
    raw_topology = topology.model_dump(by_alias=True)
    raw_topology["subscribers"]["sub-a_2"] = copy.deepcopy(raw_topology["subscribers"]["sub-a"])
    raw_topology["links"] += [{**copy.deepcopy(link), "to": "sub-a_2"} for link in raw_topology["links"] if link["to"] == "sub-a"]
    raw = _scenario_raw("shared-cross.yaml")
    raw["events"] += [{"at_s": 40, "type": "leave", "subscriber": "sub-a"}, {"at_s": 60, "type": "join", "subscriber": "sub-a"}]
    with pytest.raises(ValueError, match="already a topology subscriber"):
        Scenario.model_validate(raw).check_against(type(topology).model_validate(raw_topology))


def test_iperf_client_argv() -> None:
    topology, scenario = _shared(), _shared_scenario()
    flows = {flow.id: flow for flow in scenario.flows()}
    udp = iperf_client_argv(topology, scenario, flows["cross-udp"])
    assert udp[:2] == ["iperf3", "-c"] and "-u" in udp and "3.5M" in udp
    assert udp[udp.index("-p") + 1] == "5201"
    tcp = iperf_client_argv(topology, scenario, flows["cross-tcp"])
    assert "-u" not in tcp and tcp[tcp.index("-C") + 1] == "cubic"
    assert tcp[tcp.index("-p") + 1] == "5202"
    assert tcp[tcp.index("-B") + 1] == "10.100.0.1"


class _FakeNode:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def cmd(self, command: str) -> str:
        self.commands.append(command)
        marker = "__QUICLAB_COMMAND_STATUS__"
        return f"\n{marker}0\n" if marker in command else ""


class _FakeNet:
    def __init__(self, ids) -> None:
        self.nodes = {nid: _FakeNode() for nid in ids}

    def get(self, nid: str) -> _FakeNode:
        return self.nodes[nid]


def test_configure_network_routes_and_shapes(tmp_path: Path) -> None:
    topology = _shared()
    record = RunRecord(run_id="t", run_dir=tmp_path, loopback_ips=node_loopback_ips(topology))
    record.node_iface_ips, _ = addressed_links(topology)
    for edge in edge_interfaces(topology):
        ips = dict(record.node_iface_ips[edge.a]), dict(record.node_iface_ips[edge.b])
        record.edge_ips[(edge.a, edge.b)] = (ips[0][edge.a_iface].split("/")[0],
                                             ips[1][edge.b_iface].split("/")[0])
    net = _FakeNet([*record.loopback_ips, "switch"])
    MininetBackend._configure_network(net, topology, _shared_scenario(), record, lambda _: None)

    router = "\n".join(net.get("router").commands)
    assert "echo 1 > /proc/sys/net/ipv4/ip_forward" in router
    assert "pfifo" in router and "htb" in router
    pub = "\n".join(net.get("pub").commands)
    assert f"ip route replace {record.loopback_ips['sub-a']}/32" in pub
    assert "master br0" in "\n".join(net.get("switch").commands)
    # Cross traffic is pinned to its declared route via alias addresses.
    assert "10.101.0.1/32" in "\n".join(net.get("traffic-tx").commands)


def test_visualizer_reads_namespace_counters_and_last_csv_row(tmp_path: Path) -> None:
    assert read_netns_counters(os.getpid(), "lo") is not None
    assert read_netns_counters(os.getpid(), "no-such-if") is None
    path = tmp_path / "c.csv"
    path.write_text("t_us,cc,buffer_ms\n")
    assert read_last_row(path) is None
    path.write_text("t_us,cc,buffer_ms\n1000000,bbr,5\n2000000,bbr,6.5\n3000000,bb")
    row = read_last_row(path)  # the half-written last row is ignored
    assert row == {"t_us": 2000000, "cc": "bbr", "buffer_ms": 6.5}
    assert snapshot_status(row, now_unix_ms=2500) == "ok"
    assert snapshot_status(row, now_unix_ms=10_000) == "stale"
    assert read_last_row(tmp_path / "missing.csv") is None


def test_iperf_json_becomes_interval_csv(tmp_path: Path) -> None:
    result = {
        "start": {"timestamp": {"timesecs": 1000}},
        "intervals": [
            {"sum": {"start": 0, "end": 1, "bytes": 125000, "bits_per_second": 1e6, "retransmits": 2},
             "streams": [{"snd_cwnd": 14480, "rtt": 21000}]},
            {"sum": {"start": 1, "end": 2, "bytes": 250000, "bits_per_second": 2e6, "retransmits": 0},
             "streams": [{"snd_cwnd": 28960, "rtt": 22000}]},
        ],
    }
    source = tmp_path / "cross.json"
    source.write_text(json.dumps(result))
    iperf_json_to_csv(source, tmp_path / "cross.csv")
    rows = list(csv.DictReader((tmp_path / "cross.csv").open()))
    assert [r["bits_per_second"] for r in rows] == ["1000000", "2000000"]
    assert rows[1]["unix_s"] == "1001.000" and rows[0]["rtt_us"] == "21000"


def test_scenario_runner_applies_events_on_time(tmp_path: Path) -> None:
    raw = {"duration_s": 0.3, "events": [
        {"at_s": 0.2, "type": "leave", "subscriber": "sub-a"},
        {"at_s": 0.1, "type": "join", "subscriber": "sub-a"},
    ]}
    scenario = Scenario.model_validate(raw).check_against(_shared())
    epoch = time.monotonic()
    log = EventLog(tmp_path / "events.csv", epoch)
    applied: list[tuple[str, float]] = []

    def record(event):
        applied.append((event.type, time.monotonic() - epoch))
        if event.type == "leave":
            raise RuntimeError("client gone")
        return event.subscriber, ""

    runner = ScenarioRunner(scenario, epoch, log, {"join": record, "leave": record})
    runner.start()
    assert runner.finished.wait(2)
    log.close()
    assert [name for name, _ in applied] == ["join", "leave"]
    assert 0.09 <= applied[0][1] < 0.2
    rows = list(csv.DictReader((tmp_path / "events.csv").open()))
    assert [(r["event"], r["status"]) for r in rows] == [("join", "applied"), ("leave", "error"), ("end", "applied")]
    assert rows[1]["error"] == "client gone"


def test_live_network_records_changes(tmp_path: Path) -> None:
    topology, scenario = _shared(), _shared_scenario()
    commands: list[tuple[str, str]] = []
    log = EventLog(tmp_path / "events.csv", time.monotonic())
    network = LiveNetwork(topology, scenario, lambda node, cmd: (commands.append((node, cmd)) or (0, "")), log)
    link = Scenario.model_validate({"duration_s": 1, "events": [
        {"at_s": 0, "type": "link", "from": "router", "to": "switch", "bandwidth_mbps": 2},
        {"at_s": 0, "type": "aqm", "router": "router", "aqm": "fq_codel"},
    ]}).events
    assert network.apply_event(link[0]) == ("router->switch:forward", "bandwidth_mbps=2")
    assert any("htb rate 2mbit" in cmd for _, cmd in commands)
    target, detail = network.apply_event(link[1])
    assert detail == "aqm=fq_codel" and network.queues["router"].aqm.value == "fq_codel"
    assert any("fq_codel" in cmd and node == "router" for node, cmd in commands)
    # A live switch to fq_codel pins every client on the router's egresses (priority mark, no qdisc filter).
    pins = [cmd for node, cmd in commands if node == "router" and "skbedit priority 20:" in cmd]
    assert pins and all(cmd.endswith(" continue") for cmd in pins)
    log.close()


def test_initial_shaping_pins_clients_only_on_fq_codel_and_cake_routers() -> None:
    topology = _shared()
    for aqm, marker in (("fq_codel", "skbedit priority 20:"), ("cake", "classid 20:")):
        raw = _scenario_raw("shared-cross.yaml")
        raw["routers"] = {"router": {"aqm": aqm}}
        commands = initial_shaping_commands(topology, Scenario.model_validate(raw).check_against(topology))
        pins = [cmd for node, cmd in commands if marker in cmd]
        assert pins and {node for node, cmd in commands if marker in cmd} == {"router"}
        ids = {cmd.split(marker)[1].split()[0] for cmd in pins}
        assert ids == {f"{0x301 + i:x}" for i in range(len(topology.subscribers))}
    raw = _scenario_raw("shared-cross.yaml")
    raw["routers"] = {"router": {"aqm": "pie"}}
    commands = initial_shaping_commands(topology, Scenario.model_validate(raw).check_against(topology))
    assert not any("skbedit" in cmd or "flower" in cmd for _, cmd in commands)


def test_visualizer_snapshot_roles() -> None:
    nodes = {n["id"]: n for n in topology_snapshot(_shared())["nodes"]}
    assert nodes["pub"]["role"] == "publisher" and nodes["pub"]["cc_algo"] == "bbr2"
    assert nodes["sub-b"]["rate_kbps"] == 1000
    assert nodes["traffic-rx"]["role"] == "traffic-receiver"


@pytest.mark.parametrize(
    ("aqm", "expected"),
    [
        ("pfifo", "pfifo limit 300"),
        ("pie", "pie limit 300 ecn"),
        ("fq_codel", "fq_codel limit 300 ecn"),
        ("dualpi2", "dualpi2 limit 300"),
        ("red", "red limit 450000 "),
    ],
)
def test_queue_limit_reaches_every_aqm(aqm: str, expected: str) -> None:
    from quiclab.config.schema import AqmKind, DirectionSpec
    from quiclab.orchestrator.shaping import shaping_commands

    commands = shaping_commands("r-eth0", DirectionSpec(bandwidth_mbps=50), AqmKind(aqm), None, 300)
    assert expected in commands[-1]


def test_run_finished_needs_the_end_row(tmp_path: Path) -> None:
    assert not run_finished(tmp_path)
    events = tmp_path / "events.csv"
    events.write_text("event,at_s\nepoch,0\nlink,5\nteardown,\n")  # Ctrl-C: teardown without end
    assert not run_finished(tmp_path)
    events.write_text("event,at_s\nepoch,0\nend,300\nteardown,\n")
    assert run_finished(tmp_path)


def test_remove_partial_run(tmp_path: Path) -> None:
    run = tmp_path / "r"
    (run / "logs").mkdir(parents=True)
    remove_partial_run(run)
    assert not run.exists()
    remove_partial_run(run)  # already gone: no error
