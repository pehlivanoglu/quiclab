import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402
import det_matrix  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402


@pytest.mark.parametrize("aqm", sorted(det_matrix.AQMS))
@pytest.mark.parametrize("topology", sorted(det_matrix.TOPOLOGIES))
@pytest.mark.parametrize("name", sorted(det_matrix.BURST_SCENARIOS))
def test_every_event_scenario_validates(name: str, topology: str, aqm: str, tmp_path: Path) -> None:
    spec = det_matrix.BURST_SCENARIOS[name]
    targets = {t for tgt in spec.get("targets", ()) for t in tgt.split("+")}
    if not targets <= set(det_matrix.TOPOLOGIES[topology][2]):
        pytest.skip(f"{name} targets bottlenecks {topology} does not have")
    if spec["kind"] == "access" and topology != "access":
        with pytest.raises(SystemExit, match="needs --topology access"):
            det_matrix.scenario_for(name, aqm, 1, tmp_path, topology)
        return
    topo = load_topology(ROOT / "configs" / "topologies" / det_matrix.TOPOLOGIES[topology][0])
    load_scenario(det_matrix.scenario_for(name, aqm, 1, tmp_path, topology), topo)


def test_isolate_congests_a_private_router_egress() -> None:
    events, _ = det_matrix.burst_events("isolate", seed=1, topology="access")
    assert {(e["from"], e["to"]) for e in events} == {("ra", "sub-a"), ("rb", "sub-b"), ("rc", "sub-c"), ("rd", "sub-d")}


@pytest.mark.parametrize("topo_file", sorted(p.name for p in (ROOT / "configs" / "topologies").glob("*.yaml")))
def test_cross_traffic_enters_at_a_router_not_through_a_switch(topo_file: str) -> None:
    topo = load_topology(ROOT / "configs" / "topologies" / topo_file)
    for name, route in (topo.traffic.routes.items() if topo.traffic else ()):
        assert route.path[1] in topo.routers, f"{topo_file} route {name}"


@pytest.mark.parametrize("topo,scenario", [
    ("detector.yaml", "det-burst.yaml"), ("detector-large.yaml", "det-burst-large.yaml"),
    ("detector-access.yaml", "det-burst-access.yaml"), ("detector-split.yaml", "det-burst-split.yaml"),
    ("detector-tree8.yaml", "grp-burst-tree8.yaml"), ("detector-rev.yaml", "grp-burst-rev.yaml"),
    ("flowbot-like.yaml", "flowbot-load-100.yaml"), ("shared.yaml", "shared-cross.yaml"),
])
def test_switch_ports_are_faster_than_the_router_egress_feeding_them(topo: str, scenario: str) -> None:
    t = load_topology(ROOT / "configs" / "topologies" / topo)
    sc = load_scenario(ROOT / "configs" / "scenarios" / scenario, t)
    for link in t.links:
        if link.to in t.switches:
            feed = sc.initial_link(link.from_, link.to)[0].bandwidth_mbps
            ports = [sc.initial_link(x.from_, x.to)[0].bandwidth_mbps for x in t.links if x.from_ == link.to]
            assert all(p > feed for p in ports), f"{link.from_} -> {link.to}: {feed} vs ports {ports}"


@pytest.mark.parametrize("topo,expected", [
    ("detector.yaml", {"sub-a": "router->switch", "sub-d": "router->switch", "sub-ctrl": ""}),
    ("detector-access.yaml", {"sub-a": "router->switch", "sub-ctrl": ""}),
    ("detector-rev.yaml", {"sub-a": "r1->switch", "sub-ctrl": ""}),
    ("detector-split.yaml", {"a1": "r2->switch-a", "b3": "r2->switch-b", "sub-ctrl": ""}),
    ("detector-tree8.yaml", {"a1": "r1->switch-a", "b1": "r1->switch-b", "c2": "r2->switch-c", "d1": "r2->switch-d",
                             "sub-ctrl": ""}),
    ("flowbot-like.yaml", {"a00": "r2->switch-a", "b09": "r2->switch-b"}),
])
def test_detector_group_is_the_leaf_queue(topo: str, expected: dict) -> None:
    raw = yaml.safe_load((ROOT / "configs" / "topologies" / topo).read_text())
    run = SimpleNamespace(topology=raw)
    pub = next(iter(raw["publishers"]))
    groups = det_eval.leaf_queues(raw, {s: det_eval.path_hops(run, pub, s) for s in raw["subscribers"]})
    assert {s: groups[s] for s in expected} == expected


def test_split_bursts_hit_only_their_bottleneck() -> None:
    n = det_matrix.topology_numbers("split")
    assert set(n["hops"]["a"]["clients"]) == {"a1", "a2", "a3"}
    assert set(n["hops"]["up"]["clients"]) == {"a1", "a2", "a3", "b1", "b2", "b3"}  # sub-ctrl branches off r1
    events, _ = det_matrix.burst_events("splitcap", seed=1, topology="split")
    starts = [e for e in events if e.get("label", "").startswith("burst u=")]
    assert len(starts) == 2 * 3 * 5  # (u, d) x targets, "a+up" drops two links
    serial = [e for e in starts if e["at_s"] == next(x["at_s"] for x in starts if x["label"].endswith(" a")
                                                       and sum(y["at_s"] == x["at_s"] for y in starts) == 2)]
    assert {(e["from"], e["to"]) for e in serial} == {("r1", "r2"), ("r2", "switch-a")}


def _pts(owd_of, t_end=3.0, step=0.005):
    """(t, owd_min_ms, sent, timed) every 5 ms; owd_of(t) -> (owd_ms, sent, timed)."""
    return [(round(i * step, 3), *owd_of(i * step)) for i in range(int(t_end / step))]


def test_measured_bands_keyframe_spike_is_not_congestion() -> None:
    # 10 ms propagation; a 100 ms keyframe queue (shorter than the 200 ms transient window).
    pts = _pts(lambda t: (10 + (30 if 1.0 <= t < 1.1 else 0), 2, 2))
    assert {b for _, b in det_eval.measured_bands(pts, [])} == {"clear"}


def test_measured_bands_standing_queue_onset_and_delay_step() -> None:
    # Queue of 40 ms from 1.0 s to 1.5 s; propagation steps +20 ms at 2.0 s (not a queue).
    # One packet stamped just before the step leaves after it (lower delay than its segment).
    pts = _pts(lambda t: (10 + (40 if 1.0 <= t < 1.5 else 0) + (20 if 2.0 <= t < 2.5 else 0)
                          - (20 if abs(t - 2.495) < 1e-9 else 0), 2, 2))
    bands = det_eval.measured_bands(pts, [2.0, 2.5])
    congested = [t for t, b in bands if b == "congested"]
    assert congested[0] == 1.0  # onset at the queue's start, not a window later
    assert all(t < 1.5 for t in congested)
    after = [(t, b) for t, b in bands if t >= 2.0]
    assert all(b == "none" for t, b in after if min(abs(t - 2.0), abs(t - 2.5)) < 0.25)  # netem transition
    assert all(b == "clear" for t, b in after if min(abs(t - 2.0), abs(t - 2.5)) >= 0.25)


def test_measured_bands_loss_onset_and_oracle_gap() -> None:
    # 40 % loss from 1.0 s, no queue; no receive timestamps at all after 2.0 s (oracle gap).
    def owd(t):
        if t >= 2.0:
            return None, 2, 0
        return 10, 5, (3 if t >= 1.0 else 5)
    bands = det_eval.measured_bands(_pts(owd), [])
    assert next(t for t, b in bands if b == "congested") == 1.0
    assert all(b == "ambiguous" for t, b in bands if t >= 2.0)
