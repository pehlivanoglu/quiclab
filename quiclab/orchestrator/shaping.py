"""Pure tc command synthesis for per-direction link shaping.

Replaces Mininet's TCLink/TCIntf machinery: instead of monkey-patching the
commands TCIntf synthesizes, quiclab builds the full egress qdisc chain itself
and runs it inside the owning container. The container's image provides the
tc binary, which is what makes dualpi2 usable at all — the router image ships
an iproute2 new enough for it, while the host and endpoint images do not.

Fixed handle scheme so chains are recognizable in `tc -s qdisc show`:

    5:  htb root (rate limiting), single class 5:1
    10: netem (delay / jitter / loss)
    20: AQM leaf (e.g. dualpi2)

Chain composition by spec contents:

    netem only              root netem
    rate only               htb
    rate + netem            htb -> netem
    rate + aqm              htb -> aqm
    rate + netem + aqm      htb -> netem -> aqm   (netem's single child slot)
    aqm only                root aqm
    netem + aqm             netem -> aqm

Initial setup installs the root with `tc qdisc replace`. Live value edits do
not reuse these construction commands: replacing an existing HTB root can
fail and rebuilding any root would flush queued packets. They instead change
the existing HTB class and netem qdisc in place.
"""

from __future__ import annotations

from quiclab.config.schema import AqmKind, DirectionSpec

# netem's default queue is 1000 packets; at high bandwidth-delay products it
# overflows and drops before the AQM ever sees pressure, silently becoming
# the real bottleneck. Raise it far past any queue we want to emulate.
_NETEM_LIMIT_PKTS = 50000

# An explicit quantum stops htb deriving one from r2q, which logs kernel
# warnings at the rates quiclab uses (the old backend monkey-patched r2q for
# the same reason).
_HTB_QUANTUM_BYTES = 1500

# netem `rate` that only keeps packet order under jitter (DirectionSpec.jitter_keep_order):
# far above any emulated link, so its serialisation time is negligible.
_ORDER_RATE = "10gbit"

_RED_MIN_BYTES, _RED_MAX_BYTES = 20_000, 60_000
_RED_AVPKT = 1200
# RED's hard limit is in bytes; a packet limit is converted at full-size packets.
_MTU_BYTES = 1500


def _red_profile(min_bytes: int | None, max_bytes: int | None, limit_packets: int | None = None) -> str:
    """RED thresholds; burst follows them (tc-red(8): burst ~ (2 min + max) / (3 avpkt)).
    The byte limit is 4x max unless a packet limit is given."""
    lo, hi = min_bytes or _RED_MIN_BYTES, max_bytes or _RED_MAX_BYTES
    burst = max(1, round((2 * lo + hi) / (3 * _RED_AVPKT)))
    limit = limit_packets * _MTU_BYTES if limit_packets else 4 * hi
    return f"limit {limit} min {lo} max {hi} avpkt {_RED_AVPKT} burst {burst} probability 0.02"


def _netem_args(spec: DirectionSpec) -> str:
    parts: list[str] = []
    if spec.delay_ms is not None:
        delay = f"delay {spec.delay_ms:g}ms"
        if spec.jitter_ms is not None:
            delay += f" {spec.jitter_ms:g}ms"
            if spec.jitter_distribution is not None:
                delay += f" distribution {spec.jitter_distribution}"
        parts.append(delay)
        if spec.jitter_ms is not None and spec.jitter_keep_order:
            parts.append(f"rate {_ORDER_RATE}")
    if spec.loss_pct is not None:
        parts.append(f"loss {spec.loss_pct:g}%")
    parts.append(f"limit {_NETEM_LIMIT_PKTS}")
    return " ".join(parts)


def shaping_commands(
    iface: str,
    spec: DirectionSpec,
    aqm: AqmKind | None = None,
    dualpi2_target_ms: float | None = None,
    queue_limit_packets: int | None = None,
    red_bytes: tuple[int | None, int | None] = (None, None),
) -> list[str]:
    """Ordered tc commands building the egress qdisc chain for one direction.

    Run them inside the node that owns `iface`. An all-None spec yields [].
    """
    has_rate = spec.bandwidth_mbps is not None
    has_netem = spec.delay_ms is not None or spec.loss_pct is not None
    cmds: list[str] = []
    parent: str | None = None  # None → the next qdisc becomes the root

    if has_rate:
        rate = f"{spec.bandwidth_mbps:g}mbit"
        cmds.append(f"tc qdisc replace dev {iface} root handle 5: htb default 1")
        cmds.append(
            f"tc class add dev {iface} parent 5: classid 5:1 htb "
            f"rate {rate} ceil {rate} burst 15k quantum {_HTB_QUANTUM_BYTES}"
        )
        parent = "5:1"

    if has_netem:
        netem = f"netem {_netem_args(spec)}"
        if parent is None:
            cmds.append(f"tc qdisc replace dev {iface} root handle 10: {netem}")
        else:
            cmds.append(f"tc qdisc add dev {iface} parent {parent} handle 10: {netem}")
        parent = "10:1"

    if aqm is not None:
        aqm_name = _aqm_name(aqm, spec, dualpi2_target_ms, queue_limit_packets, red_bytes)
        if parent is None:
            cmds.append(f"tc qdisc replace dev {iface} root handle 20: {aqm_name}")
        else:
            cmds.append(f"tc qdisc add dev {iface} parent {parent} handle 20: {aqm_name}")

    return cmds


def _aqm_name(
    aqm: AqmKind,
    spec: DirectionSpec,
    dualpi2_target_ms: float | None,
    queue_limit_packets: int | None = None,
    red_bytes: tuple[int | None, int | None] = (None, None),
) -> str:
    limit = f" limit {queue_limit_packets}" if queue_limit_packets else ""
    if aqm == AqmKind.pfifo:
        # No ECN: a FIFO only drops at its tail.
        return f"pfifo{limit}"
    if aqm == AqmKind.dualpi2:
        target = (
            f" target {dualpi2_target_ms:g}ms"
            if dualpi2_target_ms is not None
            else ""
        )
        return f"dualpi2{limit}{target}"
    if aqm == AqmKind.red:
        bandwidth = (
            f" bandwidth {spec.bandwidth_mbps:g}mbit"
            if spec.bandwidth_mbps is not None
            else ""
        )
        return f"red {_red_profile(*red_bytes, queue_limit_packets)}{bandwidth} ecn"
    if aqm == AqmKind.cake:
        # The HTB class above shapes; cake only queues (flow isolation + COBALT, ECN on by default).
        return "cake unlimited besteffort"
    return f"{aqm.value}{limit} ecn"


# Per-client flow pinning on multi-queue AQMs (docs/per-flow-queue-counters.md):
# each subscriber gets a fixed fq_codel / cake flow, so router-metrics can read
# its own queue from the class dump. Ids 0x301.. stay within fq_codel's 1024
# flows; tc reads class minors as hex, so they are always rendered with :x.
FLOW_ID_BASE = 0x300
FLOW_ID_MAX = 0x400
PIN_PREF_BASE = 100     # clsact egress prefs 100.. run before router-metrics' matchall (49152)
PINNED_AQMS = (AqmKind.fq_codel, AqmKind.cake)


def client_flow_ids(subscribers) -> dict[str, int]:
    """Subscriber -> pinned flow id (sorted ids, 0x301 upward)."""
    ids = {sid: FLOW_ID_BASE + 1 + i for i, sid in enumerate(sorted(subscribers))}
    if ids and max(ids.values()) > FLOW_ID_MAX:
        raise ValueError(f"{len(ids)} subscribers exceed the {FLOW_ID_MAX - FLOW_ID_BASE} pinned flow ids")
    return ids


def flow_pin_commands(iface: str, aqm: AqmKind | None, client_ips: dict[str, str],
                      flow_ids: dict[str, int]) -> list[str]:
    """Pin every client (by destination address) to its flow id on one egress.

    fq_codel: no filter on the qdisc (a filter there drops every packet it does
    not classify, ARP included); clsact egress sets skb->priority = 20:<id>,
    which fq_codel takes as the flow, and `continue` lets router-metrics'
    matchall still count the packet. Unmarked traffic keeps fq_codel's hash.
    cake: reads skb->priority only for the tin, so a flower filter on the qdisc
    sets the flow; packets no filter matches fall back to cake's hash.
    Idempotent (`replace` with fixed pref / handle): safe to repeat after a live
    AQM change. Other AQMs: nothing."""
    if aqm not in PINNED_AQMS:
        return []
    out = [f"tc qdisc replace dev {iface} clsact"] if aqm == AqmKind.fq_codel else []
    for i, sid in enumerate(sorted(client_ips)):
        pref, ip, fid = PIN_PREF_BASE + i, client_ips[sid], flow_ids[sid]
        if aqm == AqmKind.fq_codel:
            out.append(f"tc filter replace dev {iface} egress pref {pref} handle 1 protocol ip flower "
                       f"dst_ip {ip} action skbedit priority 20:{fid:x} continue")
        else:
            out.append(f"tc filter replace dev {iface} parent 20: pref {pref} handle 1 protocol ip flower "
                       f"dst_ip {ip} classid 20:{fid:x}")
    return out


def live_aqm_commands(
    iface: str,
    spec: DirectionSpec,
    updated: AqmKind | None,
    previous: AqmKind | None,
    dualpi2_target_ms: float | None = None,
    queue_limit_packets: int | None = None,
    red_bytes: tuple[int | None, int | None] = (None, None),
) -> list[str]:
    """Replace only the AQM leaf, preserving any HTB/netem ancestors."""
    has_rate = spec.bandwidth_mbps is not None
    has_netem = spec.delay_ms is not None or spec.loss_pct is not None
    parent = "10:1" if has_netem else "5:1" if has_rate else None
    commands: list[str] = []
    if previous is not None:
        location = f"parent {parent} handle 20:" if parent else "root handle 20:"
        commands.append(f"tc qdisc del dev {iface} {location}")
    if updated is not None:
        aqm_name = _aqm_name(updated, spec, dualpi2_target_ms, queue_limit_packets, red_bytes)
        if parent:
            commands.append(
                f"tc qdisc add dev {iface} parent {parent} handle 20: {aqm_name}"
            )
        else:
            commands.append(
                f"tc qdisc replace dev {iface} root handle 20: {aqm_name}"
            )
    return commands


def live_shaping_commands(
    iface: str, previous: DirectionSpec, updated: DirectionSpec
) -> list[str]:
    """Change shaping values without replacing qdiscs or flushing queues.

    Adding/removing HTB or netem changes the qdisc tree. That cannot preserve
    queued packets, so callers must reject such structural edits. Configure a
    bandwidth and a zero-valued netem field in YAML when those values need to
    remain editable throughout an experiment.
    """
    previous_has_rate = previous.bandwidth_mbps is not None
    updated_has_rate = updated.bandwidth_mbps is not None
    previous_has_netem = (
        previous.delay_ms is not None or previous.loss_pct is not None
    )
    updated_has_netem = updated.delay_ms is not None or updated.loss_pct is not None

    if (previous_has_rate, previous_has_netem) != (
        updated_has_rate,
        updated_has_netem,
    ):
        raise ValueError(
            "live edit would change the qdisc structure and flush queued packets; "
            "preconfigure bandwidth_mbps and loss_pct: 0 in YAML"
        )

    cmds: list[str] = []
    if previous.bandwidth_mbps != updated.bandwidth_mbps:
        rate = f"{updated.bandwidth_mbps:g}mbit"
        cmds.append(
            f"tc class change dev {iface} parent 5: classid 5:1 htb "
            f"rate {rate} ceil {rate} burst 15k quantum {_HTB_QUANTUM_BYTES}"
        )

    previous_netem = (
        previous.delay_ms,
        previous.jitter_ms,
        previous.jitter_distribution,
        previous.jitter_keep_order,
        previous.loss_pct,
    )
    updated_netem = (
        updated.delay_ms,
        updated.jitter_ms,
        updated.jitter_distribution,
        updated.jitter_keep_order,
        updated.loss_pct,
    )
    if previous_netem != updated_netem:
        parent = "parent 5:1" if updated_has_rate else "root"
        cmds.append(
            f"tc qdisc change dev {iface} {parent} handle 10: "
            f"netem {_netem_args(updated)}"
        )

    return cmds


def offload_disable_commands(iface: str) -> list[str]:
    """Disable segmentation/receive offloads that distort shaping.

    With GSO/TSO/GRO on, the qdiscs see up-to-64KB superpackets instead of
    wire-sized ones, so rate limits, netem loss, and AQM marking all operate
    on the wrong units.

    UDP GSO (QUIC senders such as mvfst batch up to dozens of packets into
    one skb) is a separate feature: veth forwards such skbs unsegmented, and
    the kernel splits them only after the next qdisc. Turning it off makes
    the sender's own interface segment them, so routers see wire-sized
    packets while the sender keeps its real GSO bursts. Separate command:
    older kernels may not expose the feature.
    """
    return [f"ethtool -K {iface} gso off tso off gro off",
            f"ethtool -K {iface} tx-udp-segmentation off"]
