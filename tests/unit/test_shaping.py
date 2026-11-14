"""Unit tests for orchestrator/shaping.py qdisc chain synthesis."""

import pytest

from quiclab.config.schema import AqmKind, DirectionSpec
from quiclab.orchestrator.shaping import (
    client_flow_ids,
    flow_pin_commands,
    live_aqm_commands,
    live_shaping_commands,
    offload_disable_commands,
    shaping_commands,
)


def test_empty_spec_yields_no_commands():
    assert shaping_commands("r1-eth0", DirectionSpec()) == []


def test_netem_only_is_root_netem():
    spec = DirectionSpec(delay_ms=20)
    assert shaping_commands("r1-eth0", spec) == [
        "tc qdisc replace dev r1-eth0 root handle 10: netem delay 20ms limit 50000",
    ]


def test_netem_renders_jitter_and_loss():
    spec = DirectionSpec(delay_ms=20, jitter_ms=5, loss_pct=1)
    assert shaping_commands("r1-eth0", spec) == [
        "tc qdisc replace dev r1-eth0 root handle 10: "
        "netem delay 20ms 5ms loss 1% limit 50000",
    ]


def test_loss_only_is_valid_netem():
    spec = DirectionSpec(loss_pct=0.5)
    assert shaping_commands("r1-eth0", spec) == [
        "tc qdisc replace dev r1-eth0 root handle 10: netem loss 0.5% limit 50000",
    ]


def test_rate_only_is_htb_with_explicit_quantum():
    spec = DirectionSpec(bandwidth_mbps=50)
    assert shaping_commands("r1-eth0", spec) == [
        "tc qdisc replace dev r1-eth0 root handle 5: htb default 1",
        "tc class add dev r1-eth0 parent 5: classid 5:1 htb "
        "rate 50mbit ceil 50mbit burst 15k quantum 1500",
    ]


def test_rate_plus_netem_chains_netem_under_htb():
    spec = DirectionSpec(bandwidth_mbps=50, delay_ms=20)
    cmds = shaping_commands("r1-eth0", spec)
    assert cmds[:2] == shaping_commands("r1-eth0", DirectionSpec(bandwidth_mbps=50))
    assert cmds[2] == (
        "tc qdisc add dev r1-eth0 parent 5:1 handle 10: netem delay 20ms limit 50000"
    )


def test_rate_plus_aqm_chains_aqm_under_htb():
    spec = DirectionSpec(bandwidth_mbps=20)
    cmds = shaping_commands("r1-eth0", spec, AqmKind.dualpi2, 8)
    assert cmds[2] == "tc qdisc add dev r1-eth0 parent 5:1 handle 20: dualpi2 target 8ms"


@pytest.mark.parametrize(
    ("aqm", "expected"),
    [
        (
            AqmKind.red,
            "red limit 240000 min 20000 max 60000 avpkt 1200 burst 28 "
            "probability 0.02 bandwidth 20mbit ecn",
        ),
        (AqmKind.pie, "pie ecn"),
        (AqmKind.fq_codel, "fq_codel ecn"),
        (AqmKind.codel, "codel ecn"),
        (AqmKind.cake, "cake unlimited besteffort"),
    ],
)
def test_rate_plus_ecn_aqm_uses_reproducible_command(aqm, expected):
    commands = shaping_commands(
        "r1-eth0", DirectionSpec(bandwidth_mbps=20), aqm
    )

    assert commands[2] == f"tc qdisc add dev r1-eth0 parent 5:1 handle 20: {expected}"


def test_full_chain_uses_netem_child_slot_for_aqm():
    spec = DirectionSpec(bandwidth_mbps=20, delay_ms=5)
    cmds = shaping_commands("r1-eth0", spec, AqmKind.dualpi2)
    assert cmds[2] == (
        "tc qdisc add dev r1-eth0 parent 5:1 handle 10: netem delay 5ms limit 50000"
    )
    assert cmds[3] == "tc qdisc add dev r1-eth0 parent 10:1 handle 20: dualpi2"


def test_aqm_only_is_root_aqm():
    spec = DirectionSpec()
    assert shaping_commands("r1-eth0", spec, AqmKind.dualpi2) == [
        "tc qdisc replace dev r1-eth0 root handle 20: dualpi2",
    ]


def test_netem_plus_aqm_without_rate():
    spec = DirectionSpec(delay_ms=10)
    assert shaping_commands("r1-eth0", spec, AqmKind.dualpi2) == [
        "tc qdisc replace dev r1-eth0 root handle 10: netem delay 10ms limit 50000",
        "tc qdisc add dev r1-eth0 parent 10:1 handle 20: dualpi2",
    ]


def test_live_aqm_change_replaces_only_the_leaf():
    spec = DirectionSpec(bandwidth_mbps=20)

    assert live_aqm_commands(
        "r1-eth0", spec, AqmKind.red, AqmKind.dualpi2
    ) == [
        "tc qdisc del dev r1-eth0 parent 5:1 handle 20:",
        "tc qdisc add dev r1-eth0 parent 5:1 handle 20: red limit 240000 "
        "min 20000 max 60000 avpkt 1200 burst 28 probability 0.02 "
        "bandwidth 20mbit ecn",
    ]


def test_root_qdisc_always_uses_replace():
    for spec in (
        DirectionSpec(delay_ms=1),
        DirectionSpec(bandwidth_mbps=1),
        DirectionSpec(),
    ):
        first = shaping_commands(
            "x-eth0", spec, AqmKind.dualpi2 if spec.is_noop() else None
        )[0]
        assert first.startswith("tc qdisc replace dev x-eth0 root ")


def test_jitter_without_delay_rejected_by_schema():
    with pytest.raises(ValueError, match="jitter_ms requires delay_ms"):
        DirectionSpec(jitter_ms=5)


def test_is_noop():
    assert DirectionSpec().is_noop()
    assert not DirectionSpec(delay_ms=0).is_noop()


def test_offload_disable_commands():
    assert offload_disable_commands("sub-eth0") == [
        "ethtool -K sub-eth0 gso off tso off gro off",
        "ethtool -K sub-eth0 tx-udp-segmentation off",
    ]


def test_live_changes_rate_and_netem_without_replacing_qdiscs():
    previous = DirectionSpec(
        bandwidth_mbps=20, delay_ms=0, jitter_ms=0, loss_pct=0
    )
    updated = DirectionSpec(
        bandwidth_mbps=10, delay_ms=25, jitter_ms=3, loss_pct=1
    )

    assert live_shaping_commands("r1-eth0", previous, updated) == [
        "tc class change dev r1-eth0 parent 5: classid 5:1 htb "
        "rate 10mbit ceil 10mbit burst 15k quantum 1500",
        "tc qdisc change dev r1-eth0 parent 5:1 handle 10: "
        "netem delay 25ms 3ms loss 1% limit 50000",
    ]


def test_live_root_netem_change_preserves_qdisc():
    previous = DirectionSpec(loss_pct=0)
    updated = DirectionSpec(delay_ms=10, jitter_ms=2, loss_pct=0.5)

    assert live_shaping_commands("r1-eth0", previous, updated) == [
        "tc qdisc change dev r1-eth0 root handle 10: "
        "netem delay 10ms 2ms loss 0.5% limit 50000",
    ]


@pytest.mark.parametrize(
    ("previous", "updated"),
    [
        (DirectionSpec(), DirectionSpec(bandwidth_mbps=10)),
        (DirectionSpec(bandwidth_mbps=10), DirectionSpec()),
        (
            DirectionSpec(bandwidth_mbps=10),
            DirectionSpec(bandwidth_mbps=10, loss_pct=1),
        ),
    ],
)
def test_live_structural_change_rejected(previous, updated):
    with pytest.raises(ValueError, match="flush queued packets"):
        live_shaping_commands("r1-eth0", previous, updated)


def test_red_profile_defaults_unchanged_and_scales() -> None:
    from quiclab.config.schema import AqmKind
    from quiclab.orchestrator.shaping import _aqm_name

    spec = DirectionSpec(bandwidth_mbps=20)
    assert _aqm_name(AqmKind.red, spec, None) == (
        "red limit 240000 min 20000 max 60000 avpkt 1200 burst 28 probability 0.02 bandwidth 20mbit ecn")
    scaled = _aqm_name(AqmKind.red, DirectionSpec(bandwidth_mbps=90), None, None, (100_000, 300_000))
    assert "limit 1200000 min 100000 max 300000" in scaled and "burst 139" in scaled


def test_client_flow_ids_are_sorted_from_0x301_and_bounded():
    assert client_flow_ids(["sub-b", "sub-a", "sub-ctrl"]) == {"sub-a": 0x301, "sub-b": 0x302, "sub-ctrl": 0x303}
    assert max(client_flow_ids([f"s{i:03d}" for i in range(256)]).values()) == 0x400
    with pytest.raises(ValueError):
        client_flow_ids([f"s{i:03d}" for i in range(257)])


def test_flow_pins_mark_priority_on_fq_codel_and_filter_on_cake():
    ips, ids = {"sub-b": "10.0.0.3", "sub-a": "10.0.0.2"}, {"sub-a": 0x301, "sub-b": 0x302}
    fq = flow_pin_commands("r-eth1", AqmKind.fq_codel, ips, ids)
    assert fq == [
        "tc qdisc replace dev r-eth1 clsact",
        "tc filter replace dev r-eth1 egress pref 100 handle 1 protocol ip flower dst_ip 10.0.0.2 "
        "action skbedit priority 20:301 continue",
        "tc filter replace dev r-eth1 egress pref 101 handle 1 protocol ip flower dst_ip 10.0.0.3 "
        "action skbedit priority 20:302 continue",
    ]
    assert not any("parent 20:" in c for c in fq)   # a filter on fq_codel drops what it does not classify
    cake = flow_pin_commands("r-eth1", AqmKind.cake, ips, ids)
    assert cake == [
        "tc filter replace dev r-eth1 parent 20: pref 100 handle 1 protocol ip flower dst_ip 10.0.0.2 classid 20:301",
        "tc filter replace dev r-eth1 parent 20: pref 101 handle 1 protocol ip flower dst_ip 10.0.0.3 classid 20:302",
    ]
    for aqm in (AqmKind.pfifo, AqmKind.red, AqmKind.pie, AqmKind.codel, AqmKind.dualpi2, None):
        assert flow_pin_commands("r-eth1", aqm, ips, ids) == []


def test_jitter_distribution_and_order_keeping_reach_netem():
    spec = DirectionSpec(delay_ms=20, jitter_ms=10, jitter_distribution="normal", jitter_keep_order=True)
    cmds = shaping_commands("s-eth1", spec)
    assert cmds[-1].endswith("netem delay 20ms 10ms distribution normal rate 10gbit limit 50000")
    plain = shaping_commands("s-eth1", DirectionSpec(delay_ms=20, jitter_ms=10))[-1]
    assert "distribution" not in plain and "rate" not in plain
    with pytest.raises(ValueError):
        DirectionSpec(delay_ms=20, jitter_keep_order=True)
