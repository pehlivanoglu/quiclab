"""Pydantic v2 schema for the quiclab topology config.

A topology is a YAML file with node-bearing blocks (publishers = QUIC video
senders, subscribers = QUIC video clients, routers, switches, traffic) plus
`links:` physical wiring and inheritable link defaults. Every node id is unique
across the whole topology: it becomes a Mininet host name and the name other
nodes use to reach it.

Schema invariants enforced here:
  - node ids globally unique across all node kinds
  - subscriber connects_to resolves to a known publisher; its rate is on that
    publisher's ladder and its keyframe phase is within one GOP
  - links reference known nodes, each undirected pair appears at most once
  - every publisher/subscriber pair has a path through the link graph
  - links are wiring only; conditions, AQMs and traffic flows live in the
    scenario (quiclab/config/scenario.py)
  - every declared router and switch appears in at least one link
"""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from quiclab.exceptions import ConfigError

_NODE_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
_MIN_PORT = 1024
_MAX_PORT = 65535


class _StrictBase(BaseModel):
    """Reject unknown fields so typos surface as ConfigError, not silent drops."""

    model_config = ConfigDict(extra="forbid", frozen=False)


# ── defaults ───────────────────────────────────────────────────────────────


class AqmKind(str, Enum):
    """AQM qdiscs quiclab can synthesize tc commands for."""

    dualpi2 = "dualpi2"
    red = "red"
    pie = "pie"
    fq_codel = "fq_codel"
    pfifo = "pfifo"  # plain FIFO leaf with an explicit packet limit


# mvfst congestion controllers (quic::congestionControlStrToType names).
CcAlgo = Literal["bbr", "bbr2", "bbr2modular", "copa", "cubic", "newreno"]


class TrafficDefaults(_StrictBase):
    # iperf3 server port of the first flow; flow i listens on base_port + i.
    base_port: int = Field(default=5201, ge=_MIN_PORT, le=_MAX_PORT - 1024)


class StartupConfig(_StrictBase):
    publisher_warmup_s: float = Field(default=1.0, ge=0)
    traffic_ready_timeout_s: float = Field(default=5.0, gt=0)


# ── nodes ──────────────────────────────────────────────────────────────────


class PublisherConfig(_StrictBase):
    """qvideo-server: live synthetic video, one QUIC stream per GOP."""

    listen_port: int = Field(default=4433, ge=_MIN_PORT, le=_MAX_PORT)
    cc_algo: CcAlgo = "bbr"
    ladder_kbps: list[Annotated[int, Field(gt=0, le=1_000_000)]] = Field(
        default_factory=lambda: [500, 1000, 2500, 5000, 8000, 12000], min_length=1
    )
    fps: int = Field(default=30, ge=1, le=120)
    gop_ms: int = Field(default=2000, gt=0)
    # Mean I-frame size over mean P-frame size.
    ip_ratio: float = Field(default=8.0, ge=1)
    # Lognormal sigma of the per-frame size noise (mean-preserving).
    size_sigma: float = Field(default=0.2, ge=0, le=2)
    seed: int = Field(default=1, ge=0)
    stats_ms: int = Field(default=50, gt=0)
    # QUIC worker threads (one EventBase each); unset: one per subscriber.
    workers: int | None = Field(default=None, gt=0, le=256)

    @model_validator(mode="after")
    def _check(self) -> "PublisherConfig":
        if len(set(self.ladder_kbps)) != len(self.ladder_kbps):
            raise ValueError("ladder_kbps has duplicate renditions")
        if self.gop_ms * self.fps < 1000:
            raise ValueError("gop_ms must hold at least one frame at this fps")
        return self


class SubscriberConfig(_StrictBase):
    """qvideo-client: one fixed rendition with simulated playback."""

    connects_to: str
    rate_kbps: int = Field(default=2500, gt=0)
    # Keyframe phase of this client's live schedule; equal phases = in sync.
    phase_ms: int = Field(default=0, ge=0)
    buffer_ms: int = Field(default=600, ge=0)
    stats_ms: int = Field(default=100, gt=0)


class QueueMetricsConfig(_StrictBase):
    enabled: bool = False
    interval_ms: int = Field(default=25, gt=0)
    # Optional extra queue-occupancy-only sampler (rtnetlink, no tc fork),
    # e.g. 5 ms for fine-grained queue truth; unset: none.
    queue_interval_ms: int | None = Field(default=None, gt=0)



class RouterConfig(_StrictBase):
    """An IP-forwarding namespace that owns link queues; its AQM is set per scenario."""

    queue_metrics: QueueMetricsConfig = Field(default_factory=QueueMetricsConfig)


class SwitchConfig(_StrictBase):
    """Unmanaged Linux bridge inside its own namespace."""


class TrafficEndpointConfig(_StrictBase):
    id: str


class TrafficRouteConfig(_StrictBase):
    path: list[str] = Field(min_length=3)


class TrafficConfig(_StrictBase):
    senders: list[TrafficEndpointConfig] = Field(min_length=1)
    receivers: list[TrafficEndpointConfig] = Field(min_length=1)
    routes: dict[str, TrafficRouteConfig] = Field(min_length=1, max_length=254)

    @model_validator(mode="before")
    @classmethod
    def normalize_endpoints(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        result = dict(value)
        for role in ("sender", "receiver"):
            if role in result:
                if f"{role}s" in result:
                    raise ValueError(
                        f"use either traffic.{role} or traffic.{role}s, not both"
                    )
                result[f"{role}s"] = [result.pop(role)]
        return result

    @model_validator(mode="after")
    def _check_local_references(self) -> "TrafficConfig":
        seen_endpoints: set[str] = set()
        for endpoint in [*self.senders, *self.receivers]:
            if not _NODE_ID_RE.fullmatch(endpoint.id):
                raise ValueError(
                    f"traffic endpoint id {endpoint.id!r} must match {_NODE_ID_RE.pattern}"
                )
            if endpoint.id in seen_endpoints:
                raise ValueError(f"traffic endpoint id {endpoint.id!r} reused")
            seen_endpoints.add(endpoint.id)
        for name in self.routes:
            if not _NODE_ID_RE.fullmatch(name):
                raise ValueError(f"traffic route name {name!r} must match {_NODE_ID_RE.pattern}")
        return self


# ── links (Containernet-only shaping) ──────────────────────────────────────


class DirectionSpec(_StrictBase):
    """Shaping for one direction of a link: the egress qdisc chain on one interface."""

    bandwidth_mbps: float | None = Field(default=None, gt=0)
    delay_ms: float | None = Field(default=None, ge=0)
    jitter_ms: float | None = Field(default=None, ge=0)
    loss_pct: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def _check_jitter_requires_delay(self) -> "DirectionSpec":
        if self.jitter_ms is not None and self.delay_ms is None:
            raise ValueError(
                "jitter_ms requires delay_ms (netem syntax: delay <ms> <jitter>)"
            )
        return self

    def is_noop(self) -> bool:
        return (
            self.bandwidth_mbps is None
            and self.delay_ms is None
            and self.jitter_ms is None
            and self.loss_pct is None
        )

    def merged_over(self, base: "DirectionSpec") -> "DirectionSpec":
        """This spec's explicitly-set fields laid over `base`.

        Per-field, not per-block: a link that sets only `bandwidth_mbps` still
        inherits `delay_ms` from the default. `model_fields_set` — not a
        truthiness or None test — decides what "explicitly set" means, so
        `delay_ms: 0` overrides a nonzero default.
        """
        merged = base.model_dump()
        merged.update(self.model_dump(include=self.model_fields_set))
        return DirectionSpec.model_validate(merged)


class Defaults(_StrictBase):
    traffic: TrafficDefaults = Field(default_factory=TrafficDefaults)


class LinkSpec(_StrictBase):
    """One link (veth pair) between two node ids. Wiring only: a scenario sets
    its conditions; `forward` there means from→to, `reverse` to→from."""

    from_: str = Field(alias="from")
    to: str

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="after")
    def _check_endpoints_differ(self) -> "LinkSpec":
        if self.from_ == self.to:
            raise ValueError(f"link endpoints must differ (got {self.from_!r} twice)")
        return self

    def canonical_key(self) -> tuple[str, str]:
        """Alphabetically-ordered endpoint pair for dedup + lookup."""
        return tuple(sorted([self.from_, self.to]))  # type: ignore[return-value]


# ── top-level topology ─────────────────────────────────────────────────────



class TopologyConfig(_StrictBase):
    defaults: Defaults = Field(default_factory=Defaults)
    startup: StartupConfig = Field(default_factory=StartupConfig)
    publishers: dict[str, PublisherConfig] = Field(default_factory=dict)
    subscribers: dict[str, SubscriberConfig] = Field(default_factory=dict)
    routers: dict[str, RouterConfig] = Field(default_factory=dict)
    switches: dict[str, SwitchConfig] = Field(default_factory=dict)
    traffic: TrafficConfig | None = None
    links: list[LinkSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check(self) -> "TopologyConfig":
        if not self.publishers:
            raise ValueError("at least one publisher is required")
        if not self.links:
            raise ValueError("links are required: they are the only wiring")

        all_nodes: dict[str, str] = {}
        for kind, group in (
            ("publisher", self.publishers),
            ("subscriber", self.subscribers),
            ("router", self.routers),
            ("switch", self.switches),
        ):
            for nid in group:
                if not _NODE_ID_RE.match(nid):
                    raise ValueError(
                        f"invalid {kind} id {nid!r}: must match {_NODE_ID_RE.pattern}"
                    )
                if nid in all_nodes:
                    raise ValueError(
                        f"node id {nid!r} reused: already declared as a "
                        f"{all_nodes[nid]}"
                    )
                all_nodes[nid] = kind

        if self.traffic is not None:
            for kind, endpoint in (
                *(("traffic sender", endpoint) for endpoint in self.traffic.senders),
                *(("traffic receiver", endpoint) for endpoint in self.traffic.receivers),
            ):
                nid = endpoint.id
                if nid in all_nodes:
                    raise ValueError(
                        f"node id {nid!r} reused: already declared as a "
                        f"{all_nodes[nid]}"
                    )
                all_nodes[nid] = kind
                all_nodes[nid] = kind

        for sid, s in self.subscribers.items():
            publisher = self.publishers.get(s.connects_to)
            if publisher is None:
                raise ValueError(
                    f"subscriber {sid!r} connects_to {s.connects_to!r} is not a known publisher"
                )
            if s.rate_kbps not in publisher.ladder_kbps:
                raise ValueError(
                    f"subscriber {sid!r} rate_kbps {s.rate_kbps} is not on publisher "
                    f"{s.connects_to!r} ladder {publisher.ladder_kbps}"
                )
            if s.phase_ms >= publisher.gop_ms:
                raise ValueError(f"subscriber {sid!r} phase_ms must be below gop_ms")

        # Links are the physical wiring: endpoints must exist, each undirected
        # pair appears once.
        seen_links: set[tuple[str, str]] = set()
        linked_nodes: set[str] = set()
        for link in self.links:
            for endpoint in (link.from_, link.to):
                if endpoint not in all_nodes:
                    raise ValueError(
                        f"link references unknown node {endpoint!r}"
                    )
            key = link.canonical_key()
            if key in seen_links:
                raise ValueError(
                    f"duplicate link between {key[0]!r} and {key[1]!r}"
                )
            seen_links.add(key)
            linked_nodes.update(key)
        for rid in self.routers:
            if rid not in linked_nodes:
                raise ValueError(f"router {rid!r} does not appear in any link")

        # Bridges use no STP: reject loops and duplicate attachments to one LAN.
        switch_parent = {sid: sid for sid in self.switches}

        def switch_root(sid: str) -> str:
            while switch_parent[sid] != sid:
                sid = switch_parent[sid]
            return sid

        for sid in self.switches:
            if sid not in linked_nodes:
                raise ValueError(f"switch {sid!r} does not appear in any link")
        for link in self.links:
            if link.from_ in self.switches and link.to in self.switches:
                a, b = switch_root(link.from_), switch_root(link.to)
                if a == b:
                    raise ValueError("switch links must not contain a Layer 2 loop")
                switch_parent[a] = b
        attachments: set[tuple[str, str]] = set()
        for link in self.links:
            for node, peer in ((link.from_, link.to), (link.to, link.from_)):
                if node not in self.switches and peer in self.switches:
                    key = (node, switch_root(peer))
                    if key in attachments:
                        raise ValueError(f"node {node!r} has multiple ports on the same switched LAN")
                    attachments.add(key)

        if self.traffic is not None:
            senders = {endpoint.id for endpoint in self.traffic.senders}
            receivers = {endpoint.id for endpoint in self.traffic.receivers}
            link_keys = {link.canonical_key() for link in self.links}
            for name, route in self.traffic.routes.items():
                if route.path[0] not in senders or route.path[-1] not in receivers:
                    raise ValueError(
                        f"traffic route {name!r} must start at a declared sender "
                        "and end at a declared receiver"
                    )
                if len(set(route.path)) != len(route.path):
                    raise ValueError(f"traffic route {name!r} repeats a node")
                for intermediate in route.path[1:-1]:
                    if (
                        intermediate not in self.routers
                        and intermediate not in self.switches
                    ):
                        raise ValueError(
                            f"traffic route {name!r} intermediate {intermediate!r} "
                            "must be a router or switch"
                        )
                for a, b in zip(route.path, route.path[1:]):
                    if tuple(sorted((a, b))) not in link_keys:
                        raise ValueError(
                            f"traffic route {name!r} uses undeclared link {a!r}-{b!r}"
                        )

        # Every publisher/subscriber pair must be realizable through the links.
        component: dict[str, str] = {nid: nid for nid in all_nodes}

        def _root(nid: str) -> str:
            while component[nid] != nid:
                component[nid] = component[component[nid]]
                nid = component[nid]
            return nid

        for link in self.links:
            component[_root(link.from_)] = _root(link.to)
        for sid, subscriber in sorted(self.subscribers.items()):
            if _root(sid) != _root(subscriber.connects_to):
                raise ValueError(
                    f"no path of links connects {sid!r} and {subscriber.connects_to!r}"
                )

        return self

    # ── helpers for downstream code ─────────────────────────────────────────

    def link_for(self, a: str, b: str) -> LinkSpec | None:
        """Return the link between two nodes, regardless of ordering, or None."""
        wanted = tuple(sorted([a, b]))
        for link in self.links:
            if link.canonical_key() == wanted:
                return link
        return None

    def subscribers_of(self, pid: str) -> list[str]:
        return [sid for sid, s in self.subscribers.items() if s.connects_to == pid]


def load_topology(path: str | Path) -> TopologyConfig:
    """Load and validate a topology YAML. Raises ConfigError on any failure."""
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text())
    except FileNotFoundError as e:
        raise ConfigError(f"topology config not found: {p}") from e
    except yaml.YAMLError as e:
        raise ConfigError(f"failed to parse {p}: {e}") from e

    if raw is None:
        raise ConfigError(f"{p} is empty")
    if not isinstance(raw, dict):
        raise ConfigError(
            f"{p}: top-level value must be a mapping, got {type(raw).__name__}"
        )

    try:
        return TopologyConfig.model_validate(raw)
    except Exception as e:
        raise ConfigError(f"{p}: {e}") from e
