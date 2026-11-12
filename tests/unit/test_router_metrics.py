from __future__ import annotations

from dataclasses import replace

from quiclab.router_metrics import flow_rows, interval_row, parse_flows, parse_sample


def _qdiscs() -> list[dict]:
    return [
        {
            "kind": "htb",
            "handle": "5:",
            "root": True,
            "bytes": 1000,
            "drops": 3,
            "backlog": 200,
            "qlen": 2,
        },
        {
            "kind": "netem",
            "handle": "10:",
            "parent": "5:1",
            "bytes": 1000,
            "drops": 3,
            "backlog": 200,
            "qlen": 2,
        },
        {
            "kind": "dualpi2",
            "handle": "20:",
            "parent": "10:1",
            "options": {"limit": 200},
            "bytes": 1000,
            "drops": 1,
            "backlog": 120,
            "qlen": 1,
            "pkts-in-l": 20,
            "pkts-in-c": 30,
            "ecn-mark": 4,
            "step-mark": 5,
            "delay-l": 100,
            "delay-c": 200,
            "memory-used": 400,
            "memory-limit": 1000,
        },
    ]


def _filters() -> list[dict]:
    return [
        {
            "kind": "matchall",
            "options": {
                "actions": [
                    {"kind": "gact", "stats": {"bytes": 1300, "packets": 12}}
                ]
            },
        }
    ]


def test_parse_sample_uses_root_totals_leaf_occupancy_and_separate_netem():
    sample = parse_sample(_qdiscs(), _filters(), 10_000, 500)

    assert sample.offered_bytes == 1300
    assert sample.root_transmitted_bytes == 1000
    assert sample.root_drops == 3
    assert sample.dualpi2_drops == 1
    assert sample.queue_capacity_packets == 200
    assert sample.queue_packets == 1
    assert sample.separate_queue_packets == 2
    assert sample.l_enqueued_packets == 20
    assert sample.c_enqueued_packets == 30


def test_parse_sample_uses_pfifo_when_dualpi2_is_absent():
    qdiscs = [
        {"kind": "htb", "root": True, "bytes": 1000, "drops": 3},
        {
            "kind": "pfifo",
            "parent": "5:1",
            "options": {"limit": 200},
            "backlog": 1200,
            "qlen": 10,
        },
    ]

    sample = parse_sample(qdiscs, _filters(), 10_000, 500)

    assert sample.queue_capacity_packets == 200
    assert sample.queue_packets == 10
    assert sample.queue_backlog_bytes == 1200
    assert sample.dualpi2_drops == 0
    assert sample.l_enqueued_packets == 0
    assert sample.c_enqueued_packets == 0


def test_parse_sample_uses_non_dualpi2_aqm_queue_and_ecn_counter():
    counters = (
        ("red", "marked"),
        ("pie", "ecn_mark"),
        ("fq_codel", "ecn_mark"),
    )
    for kind, mark_field in counters:
        qdiscs = [
            {"kind": "htb", "root": True, "bytes": 1000, "drops": 3},
            {
                "kind": kind,
                "parent": "5:1",
                "options": {"limit": 200},
                "backlog": 1200,
                "qlen": 10,
                mark_field: 7,
            },
        ]

        sample = parse_sample(qdiscs, _filters(), 10_000, 500)

        assert sample.queue_packets == 10
        assert sample.queue_backlog_bytes == 1200
        assert sample.ecn_marks == 7
        assert sample.queue_capacity_packets == (0 if kind == "red" else 200)


def test_interval_row_differences_counters_but_keeps_instantaneous_state():
    previous = parse_sample(_qdiscs(), _filters(), 10_000, 500)
    current = replace(
        previous,
        timestamp_mono_ns=25_010_000,
        collection_duration_ns=700,
        offered_bytes=2300,
        root_transmitted_bytes=1800,
        root_drops=5,
        dualpi2_drops=2,
        l_enqueued_packets=24,
        c_enqueued_packets=36,
        ecn_marks=7,
        step_marks=9,
        queue_packets=50,
        queue_memory_bytes=500,
    )

    row = interval_row(previous, current)

    assert row["interval_ns"] == 25_000_000
    assert row["offered_bytes"] == 1000
    assert row["transmitted_bytes"] == 800
    assert row["drops"] == 2
    assert row["dualpi2_drops"] == 1
    assert row["l_enqueued_packets"] == 4
    assert row["c_enqueued_packets"] == 6
    assert row["queue_packets"] == 50
    assert row["queue_percent"] == 25.0
    assert row["queue_memory_percent"] == 50.0
    assert row["counter_reset"] == 0


def test_interval_row_marks_counter_reset_without_negative_delta():
    previous = parse_sample(_qdiscs(), _filters(), 10_000, 500)
    current = replace(previous, timestamp_mono_ns=20_000, offered_bytes=10)

    row = interval_row(previous, current)

    assert row["offered_bytes"] == 0
    assert row["counter_reset"] == 1


def _nl_attr(kind: int, payload: bytes) -> bytes:
    import struct

    raw = struct.pack("=HH", 4 + len(payload), kind) + payload
    return raw + b"\0" * (-len(raw) % 4)


def _nl_qdisc(ifindex: int, parent: int, kind: str, qlen: int, backlog: int, drops: int) -> bytes:
    import struct

    queue = _nl_attr(3, struct.pack("=IIIII", qlen, backlog, drops, 0, 0))
    body = (struct.pack("=BBHiIII", 0, 0, 0, ifindex, 0, parent, 0)
            + _nl_attr(1, kind.encode() + b"\0") + _nl_attr(7 | 0x8000, queue))
    return struct.pack("=IHHII", 16 + len(body), 36, 2, 1, 0) + body


def test_netlink_dump_selects_the_same_queue_as_tc():
    import struct

    from quiclab.router_metrics import parse_qdisc_dump, select_queue

    data = (_nl_qdisc(7, 0xFFFFFFFF, "htb", 3, 3000, 1)
            + _nl_qdisc(9, 0xFFFFFFFF, "fq_codel", 50, 50, 0)  # another interface
            + _nl_qdisc(7, 0x50001, "dualpi2", 3, 3000, 1)
            + _nl_qdisc(7, 0xFFFFFFF1, "clsact", 0, 0, 0)
            + struct.pack("=IHHII", 20, 3, 2, 1, 0) + b"\0" * 4)
    qdiscs, done = parse_qdisc_dump(data, 7)

    assert done
    assert [(q["kind"], q["root"]) for q in qdiscs] == [("htb", True), ("dualpi2", False), ("clsact", False)]
    assert select_queue(qdiscs) == {"root": False, "kind": "dualpi2", "qlen": 3, "backlog": 3000, "drops": 1}
    # Same rule as the tc JSON path.
    assert select_queue(_qdiscs())["kind"] == "dualpi2"


def test_netlink_dump_without_aqm_falls_back_to_root():
    from quiclab.router_metrics import parse_qdisc_dump, select_queue

    qdiscs, done = parse_qdisc_dump(_nl_qdisc(7, 0xFFFFFFFF, "htb", 1, 100, 0), 7)

    assert not done
    assert select_queue(qdiscs)["backlog"] == 100


def test_flow_rows_keep_pinned_classes_and_backlogged_hashed_ones():
    flows = parse_flows("301=sub-a, 302=sub-b,")
    assert flows == {"301": "sub-a", "302": "sub-b"}
    classes = [{"class": "fq_codel", "handle": "20:301", "stats": {"backlog": 115506, "qlen": 93, "drops": 4}},
               {"class": "fq_codel", "handle": "20:302", "stats": {"backlog": 0, "qlen": 0, "drops": 0}},
               {"class": "fq_codel", "handle": "20:1d3", "stats": {"backlog": 1242, "qlen": 1, "drops": 0}},
               {"class": "fq_codel", "handle": "20:2e4", "stats": {"backlog": 0, "qlen": 0, "drops": 0}}]
    assert flow_rows(classes, flows, 7) == [(7, "301", "sub-a", 93, 115506, 4), (7, "302", "sub-b", 0, 0, 0),
                                            (7, "1d3", "", 1, 1242, 0)]
