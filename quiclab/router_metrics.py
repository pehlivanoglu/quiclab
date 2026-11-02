#!/usr/bin/env python3
"""Sample router qdisc counters and instantaneous queue state into CSV."""

from __future__ import annotations

import argparse
import csv
import json
import signal
import socket
import struct
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CSV_FIELDS = (
    "timestamp_mono_ns",
    "interval_ns",
    "collection_duration_ns",
    "offered_bytes",
    "transmitted_bytes",
    "drops",
    "dualpi2_drops",
    "l_enqueued_packets",
    "c_enqueued_packets",
    "ecn_marks",
    "step_marks",
    "queue_capacity_packets",
    "queue_packets",
    "queue_percent",
    "queue_backlog_bytes",
    "queue_memory_capacity_bytes",
    "queue_memory_bytes",
    "queue_memory_percent",
    "l_head_delay_us",
    "c_head_delay_us",
    "separate_queue_packets",
    "separate_queue_backlog_bytes",
    "counter_reset",
)


# Fast queue-only samples (`--queue-only`): read over rtnetlink, so a 5 ms
# period does not fork tc 200 times a second next to the relay.
QUEUE_CSV_FIELDS = ("timestamp_mono_ns", "queue_packets", "queue_backlog_bytes", "drops")
_QUEUE_KINDS = {"dualpi2", "red", "pie", "fq_codel", "pfifo"}


@dataclass(frozen=True)
class Sample:
    timestamp_mono_ns: int
    collection_duration_ns: int
    offered_bytes: int
    root_transmitted_bytes: int
    root_drops: int
    dualpi2_drops: int
    l_enqueued_packets: int
    c_enqueued_packets: int
    ecn_marks: int
    step_marks: int
    queue_capacity_packets: int
    queue_packets: int
    queue_backlog_bytes: int
    queue_memory_capacity_bytes: int
    queue_memory_bytes: int
    l_head_delay_us: int
    c_head_delay_us: int
    separate_queue_packets: int
    separate_queue_backlog_bytes: int


def _tc_json(*args: str) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["tc", "-j", "-s", "-d", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    value = json.loads(result.stdout)
    if not isinstance(value, list):
        raise RuntimeError(f"tc returned unexpected JSON for {' '.join(args)}")
    return value


def _offered_bytes(filters: list[dict[str, Any]]) -> int:
    for entry in filters:
        if entry.get("kind") != "matchall":
            continue
        for action in entry.get("options", {}).get("actions", []):
            if action.get("kind") == "gact":
                return int(action.get("stats", {}).get("bytes", 0))
    raise RuntimeError("offered-byte matchall counter is missing")


def _root(qdiscs: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        return next(qdisc for qdisc in qdiscs if qdisc.get("root"))
    except StopIteration as error:
        raise RuntimeError("qdisc hierarchy has no root qdisc") from error


def select_queue(qdiscs: list[dict[str, Any]]) -> dict[str, Any]:
    """The qdisc whose occupancy is the link queue: the first AQM leaf in
    dump order, else the root."""
    return next((q for q in qdiscs if q.get("kind") in _QUEUE_KINDS), _root(qdiscs))


def parse_sample(
    qdiscs: list[dict[str, Any]],
    filters: list[dict[str, Any]],
    timestamp_mono_ns: int,
    collection_duration_ns: int,
) -> Sample:
    root = _root(qdiscs)

    dualpi2 = next(
        (qdisc for qdisc in qdiscs if qdisc.get("kind") == "dualpi2"), None
    )
    queue = select_queue(qdiscs)

    options = queue.get("options", {})
    capacity = 0 if queue.get("kind") == "red" else int(options.get("limit", 0))
    ecn_marks = {
        "dualpi2": "ecn-mark",
        "red": "marked",
        "pie": "ecn_mark",
        "fq_codel": "ecn_mark",
    }

    # HTB mirrors descendant backlog, so do not sum it with the leaf. Netem
    # is the only separate queue synthesized by quiclab's current hierarchy.
    separate = [q for q in qdiscs if q.get("kind") == "netem"]
    return Sample(
        timestamp_mono_ns=timestamp_mono_ns,
        collection_duration_ns=collection_duration_ns,
        offered_bytes=_offered_bytes(filters),
        root_transmitted_bytes=int(root.get("bytes", 0)),
        root_drops=int(root.get("drops", 0)),
        dualpi2_drops=int(dualpi2.get("drops", 0)) if dualpi2 else 0,
        l_enqueued_packets=int(dualpi2.get("pkts-in-l", 0)) if dualpi2 else 0,
        c_enqueued_packets=int(dualpi2.get("pkts-in-c", 0)) if dualpi2 else 0,
        ecn_marks=int(queue.get(ecn_marks.get(str(queue.get("kind")), ""), 0)),
        step_marks=int(dualpi2.get("step-mark", 0)) if dualpi2 else 0,
        queue_capacity_packets=capacity,
        queue_packets=int(queue.get("qlen", 0)),
        queue_backlog_bytes=int(queue.get("backlog", 0)),
        queue_memory_capacity_bytes=int(dualpi2.get("memory-limit", 0)) if dualpi2 else 0,
        queue_memory_bytes=int(dualpi2.get("memory-used", 0)) if dualpi2 else 0,
        l_head_delay_us=int(dualpi2.get("delay-l", 0)) if dualpi2 else 0,
        c_head_delay_us=int(dualpi2.get("delay-c", 0)) if dualpi2 else 0,
        separate_queue_packets=sum(int(q.get("qlen", 0)) for q in separate),
        separate_queue_backlog_bytes=sum(int(q.get("backlog", 0)) for q in separate),
    )


def collect(interface: str) -> tuple[Sample, list[dict[str, Any]]]:
    start_ns = time.monotonic_ns()
    filters = _tc_json("filter", "show", "dev", interface, "egress")
    qdiscs = _tc_json("qdisc", "show", "dev", interface)
    end_ns = time.monotonic_ns()
    return parse_sample(qdiscs, filters, end_ns, end_ns - start_ns), qdiscs


def _delta(current: int, previous: int) -> tuple[int, bool]:
    if current < previous:
        return 0, True
    return current - previous, False


def interval_row(previous: Sample, current: Sample) -> dict[str, int | float]:
    deltas: dict[str, int] = {}
    reset = False
    for output, field in (
        ("offered_bytes", "offered_bytes"),
        ("transmitted_bytes", "root_transmitted_bytes"),
        ("drops", "root_drops"),
        ("dualpi2_drops", "dualpi2_drops"),
        ("l_enqueued_packets", "l_enqueued_packets"),
        ("c_enqueued_packets", "c_enqueued_packets"),
        ("ecn_marks", "ecn_marks"),
        ("step_marks", "step_marks"),
    ):
        deltas[output], wrapped = _delta(getattr(current, field), getattr(previous, field))
        reset |= wrapped

    queue_percent = (
        100.0 * current.queue_packets / current.queue_capacity_packets
        if current.queue_capacity_packets
        else float("nan")
    )
    memory_percent = (
        100.0 * current.queue_memory_bytes / current.queue_memory_capacity_bytes
        if current.queue_memory_capacity_bytes
        else 0.0
    )
    return {
        "timestamp_mono_ns": current.timestamp_mono_ns,
        "interval_ns": current.timestamp_mono_ns - previous.timestamp_mono_ns,
        "collection_duration_ns": current.collection_duration_ns,
        **deltas,
        "queue_capacity_packets": current.queue_capacity_packets,
        "queue_packets": current.queue_packets,
        "queue_percent": round(queue_percent, 6),
        "queue_backlog_bytes": current.queue_backlog_bytes,
        "queue_memory_capacity_bytes": current.queue_memory_capacity_bytes,
        "queue_memory_bytes": current.queue_memory_bytes,
        "queue_memory_percent": round(memory_percent, 6),
        "l_head_delay_us": current.l_head_delay_us,
        "c_head_delay_us": current.c_head_delay_us,
        "separate_queue_packets": current.separate_queue_packets,
        "separate_queue_backlog_bytes": current.separate_queue_backlog_bytes,
        "counter_reset": int(reset),
    }


def run(interface: str, interval_ms: int, output: Path) -> None:
    stopped = False

    def stop(_signum, _frame) -> None:
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    output.parent.mkdir(parents=True, exist_ok=True)

    previous, _ = collect(interface)
    period_ns = interval_ms * 1_000_000
    deadline_ns = previous.timestamp_mono_ns + period_ns

    with output.open("w", newline="", buffering=1) as destination:
        writer = csv.DictWriter(destination, fieldnames=CSV_FIELDS)
        writer.writeheader()
        while not stopped:
            remaining_ns = deadline_ns - time.monotonic_ns()
            if remaining_ns > 0:
                time.sleep(remaining_ns / 1_000_000_000)
            current, _ = collect(interface)
            writer.writerow(interval_row(previous, current))
            previous = current
            deadline_ns += period_ns
            if deadline_ns <= current.timestamp_mono_ns:
                deadline_ns = current.timestamp_mono_ns + period_ns


_RTM_NEWQDISC, _RTM_GETQDISC = 36, 38
_NLM_F_REQUEST, _NLM_F_DUMP = 0x1, 0x300
_NLMSG_ERROR, _NLMSG_DONE = 2, 3
_NLMSG_HDR = struct.Struct("=IHHII")
_TCMSG = struct.Struct("=BBHiIII")
_RTA_HDR = struct.Struct("=HH")
_TCA_KIND, _TCA_STATS2, _TCA_STATS_QUEUE = 1, 7, 3
_GNET_STATS_QUEUE = struct.Struct("=IIIII")  # qlen, backlog, drops, requeues, overlimits
_TC_H_ROOT = 0xFFFFFFFF


def _attributes(data: bytes, offset: int, end: int):
    while offset + _RTA_HDR.size <= end:
        length, kind = _RTA_HDR.unpack_from(data, offset)
        if length < _RTA_HDR.size:
            break
        yield kind & 0x3FFF, data[offset + _RTA_HDR.size:offset + length]
        offset += (length + 3) & ~3


def parse_qdisc_dump(data: bytes, ifindex: int) -> tuple[list[dict[str, Any]], bool]:
    """Qdiscs of `ifindex` from RTM_NEWQDISC messages, in dump order, with the
    keys `select_queue` reads; and whether the dump is complete."""
    qdiscs: list[dict[str, Any]] = []
    offset = 0
    while offset + _NLMSG_HDR.size <= len(data):
        length, kind, _, _, _ = _NLMSG_HDR.unpack_from(data, offset)
        if length < _NLMSG_HDR.size:
            break
        if kind == _NLMSG_DONE:
            return qdiscs, True
        if kind == _NLMSG_ERROR:
            (error,) = struct.unpack_from("=i", data, offset + _NLMSG_HDR.size)
            if error:
                raise OSError(-error, "RTM_GETQDISC failed")
        elif kind == _RTM_NEWQDISC:
            body = offset + _NLMSG_HDR.size
            _, _, _, index, _, parent, _ = _TCMSG.unpack_from(data, body)
            if index == ifindex:
                qdisc: dict[str, Any] = {"root": parent == _TC_H_ROOT}
                for attr, payload in _attributes(data, body + _TCMSG.size, offset + length):
                    if attr == _TCA_KIND:
                        qdisc["kind"] = payload.rstrip(b"\0").decode()
                    elif attr == _TCA_STATS2:
                        for nested, value in _attributes(payload, 0, len(payload)):
                            if nested == _TCA_STATS_QUEUE and len(value) >= _GNET_STATS_QUEUE.size:
                                qlen, backlog, drops, _, _ = _GNET_STATS_QUEUE.unpack_from(value)
                                qdisc.update(qlen=qlen, backlog=backlog, drops=drops)
                qdiscs.append(qdisc)
        offset += (length + 3) & ~3
    return qdiscs, False


def netlink_qdiscs(sock: socket.socket, ifindex: int, seq: int) -> list[dict[str, Any]]:
    request = _TCMSG.pack(0, 0, 0, ifindex, 0, 0, 0)
    sock.send(_NLMSG_HDR.pack(_NLMSG_HDR.size + len(request), _RTM_GETQDISC,
                              _NLM_F_REQUEST | _NLM_F_DUMP, seq, 0) + request)
    qdiscs: list[dict[str, Any]] = []
    while True:
        part, done = parse_qdisc_dump(sock.recv(65536), ifindex)
        qdiscs.extend(part)
        if done:
            return qdiscs


def run_queue(interface: str, interval_ms: int, output: Path) -> None:
    stopped = False

    def stop(_signum, _frame) -> None:
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    output.parent.mkdir(parents=True, exist_ok=True)
    ifindex = socket.if_nametoindex(interface)
    period_ns = interval_ms * 1_000_000
    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE) as sock, \
            output.open("w", newline="", buffering=1) as destination:
        sock.bind((0, 0))
        writer = csv.writer(destination)
        writer.writerow(QUEUE_CSV_FIELDS)
        seq = 0
        deadline_ns = time.monotonic_ns()
        while not stopped:
            remaining_ns = deadline_ns - time.monotonic_ns()
            if remaining_ns > 0:
                time.sleep(remaining_ns / 1_000_000_000)
            seq += 1
            queue = select_queue(netlink_qdiscs(sock, ifindex, seq))
            writer.writerow((time.monotonic_ns(), queue.get("qlen", 0), queue.get("backlog", 0),
                             queue.get("drops", 0)))
            deadline_ns += period_ns
            # After a stall, skip missed slots instead of sampling back to back.
            deadline_ns = max(deadline_ns, time.monotonic_ns())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", required=True)
    parser.add_argument("--interval-ms", type=int, default=25)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--queue-only", action="store_true",
                        help="sample only the queue occupancy over rtnetlink (fast)")
    args = parser.parse_args()
    if args.interval_ms <= 0:
        parser.error("--interval-ms must be positive")
    if args.queue_only:
        run_queue(args.interface, args.interval_ms, args.output)
    else:
        run(args.interface, args.interval_ms, args.output)


if __name__ == "__main__":
    main()
