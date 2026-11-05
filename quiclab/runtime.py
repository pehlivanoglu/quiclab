from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from quiclab.config.schema import TopologyConfig
from quiclab.exceptions import OrchestratorError

_RUN_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")


@dataclass(frozen=True)
class EdgeInterfaces:
    a: str
    b: str
    a_iface: str
    b_iface: str


def default_runs_dir() -> Path:
    return Path(__file__).resolve().parents[1] / ".runs"


def default_run_id() -> str:
    return time.strftime("run_%Y%m%d_%H%M%S")


def validate_run_id(run_id: str) -> None:
    """Raise OrchestratorError if run_id would escape the runs directory or break host naming."""
    if not _RUN_ID_RE.match(run_id):
        raise OrchestratorError(
            f"invalid run id {run_id!r}: must match {_RUN_ID_RE.pattern}"
        )


def run_finished(run_dir: Path) -> bool:
    """True when the scenario ran to its end: events.csv has its `end` row.
    An interrupted run has events.csv too, without that row."""
    events = run_dir / "events.csv"
    return events.exists() and any(line.startswith("end,") for line in events.read_text().splitlines())


def remove_partial_run(run_dir: Path, image: str = "quiclab:latest") -> None:
    """Delete an unfinished run's folder. A hard-killed container never handed
    its files back, so they may be root's: then remove them from a container."""
    if not run_dir.exists():
        return
    try:
        shutil.rmtree(run_dir)
    except PermissionError:
        parent = str(run_dir.resolve().parent)
        subprocess.run(["docker", "run", "--rm", "-v", f"{parent}:{parent}", image, "rm", "-rf", str(run_dir.resolve())],
                       check=True)


def topology_edges(topology: TopologyConfig) -> list[tuple[str, str]]:
    """Application (QUIC) edges: one per subscriber, toward its publisher."""
    return [(s.connects_to, sid) for sid, s in topology.subscribers.items()]


def all_node_ids(topology: TopologyConfig) -> list[str]:
    """Every node id in stable declaration order."""
    node_ids = [
        *topology.routers,
        *topology.publishers,
        *topology.subscribers,
        *topology.switches,
    ]
    if topology.traffic is not None:
        node_ids.extend(
            endpoint.id for endpoint in [*topology.traffic.senders, *topology.traffic.receivers]
        )
    return node_ids


def edge_interfaces(
    topology: TopologyConfig,
) -> list[EdgeInterfaces]:
    """One veth pair per `links:` entry, in declaration order.

    Direction is preserved (a = link.from_, b = link.to) so callers can map
    `forward`/`reverse` shaping onto a_iface/b_iface. Short node ids use
    Mininet's "<node>-eth<N>" scheme. Long ids get stable hashed names
    fitting Linux's 15-byte interface-name limit.
    """
    link_counter: dict[str, int] = {nid: 0 for nid in all_node_ids(topology)}
    edges: list[EdgeInterfaces] = []
    for link in topology.links:
        a, b = link.from_, link.to
        a_iface = _interface_name(a, link_counter[a])
        link_counter[a] += 1
        b_iface = _interface_name(b, link_counter[b])
        link_counter[b] += 1
        edges.append(
            EdgeInterfaces(a=a, b=b, a_iface=a_iface, b_iface=b_iface)
        )
    return edges


def _interface_name(node_id: str, index: int) -> str:
    natural = f"{node_id}-eth{index}"
    if len(natural) <= 15:
        return natural
    digest = hashlib.blake2s(node_id.encode(), digest_size=3).hexdigest()
    return f"{node_id[:4]}-{digest}e{index}"


# Canonical per-node addresses live on lo so they are reachable over any
# path; /24 pool → at most 254 nodes.
_LOOPBACK_POOL_PREFIX = "10.99.0."


def node_loopback_ips(topology: TopologyConfig) -> dict[str, str]:
    """Canonical /32 loopback address per node, deterministic by declaration order."""
    ordered = [nid for nid in all_node_ids(topology) if nid not in topology.switches]
    if len(ordered) > 254:
        raise OrchestratorError(
            f"topology has {len(ordered)} nodes but the loopback pool "
            f"{_LOOPBACK_POOL_PREFIX}0/24 only provides 254 addresses"
        )
    return {
        nid: f"{_LOOPBACK_POOL_PREFIX}{i}" for i, nid in enumerate(ordered, start=1)
    }


def traffic_route_ips(topology: TopologyConfig) -> dict[str, tuple[str, str]]:
    """Route name to sender/receiver aliases used for explicit path steering."""
    if topology.traffic is None:
        return {}
    if len(topology.traffic.routes) > 254:
        raise OrchestratorError("traffic supports at most 254 named routes")
    return {
        name: (f"10.100.0.{index}", f"10.101.0.{index}")
        for index, name in enumerate(topology.traffic.routes, start=1)
    }

