"""Pydantic v2 schema for a quiclab scenario: everything that varies over a run.

The topology says what exists and how it is wired; a scenario says what the
network does: initial link conditions, router AQMs, and timed events (link
changes, AQM swaps, iperf3 flows, client join/leave) up to `duration_s`.

Validated against one topology (`load_scenario`):
  - links name declared topology links in their declared from/to order
  - routers name declared routers; AQM parameters match the AQM kind
  - live link events cannot add HTB or netem (that would flush queues): the
    initial conditions must already declare bandwidth_mbps / netem fields
  - link events cannot change the capacity of a switch egress: congestion
    belongs on router egresses, switches only distribute
  - flows use declared traffic routes; flow ids are unique
  - a subscriber's join / leave events alternate in time (on at t=0 unless its
    first event is a join); every session after the first runs as client
    <subscriber>@<n>, with its own sender files
  - every event happens within duration_s
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import ConfigDict, Field, model_validator

from quiclab.config.schema import AqmKind, DirectionSpec, TopologyConfig, _StrictBase
from quiclab.exceptions import ConfigError


class RouterQueue(_StrictBase):
    """AQM leaf on every egress of one router; `egress` replaces it (whole
    queue, no field merge) on the egresses it names, by neighbor node id."""

    aqm: AqmKind | None = None
    dualpi2_target_ms: float | None = Field(default=None, gt=0)
    # Hard queue limit for every AQM (packets; RED converts at 1500 B).
    queue_limit_packets: int | None = Field(default=None, gt=0, le=100_000)
    # RED thresholds in bytes (default 20 kB / 60 kB); scale them with the
    # link's BDP, or a fast link drops at a fraction of a millisecond of queue.
    red_min_bytes: int | None = Field(default=None, gt=0)
    red_max_bytes: int | None = Field(default=None, gt=0)
    egress: dict[str, "RouterQueue"] | None = None

    def on(self, neighbor: str) -> "RouterQueue":
        """The queue on this router's egress toward `neighbor`."""
        return (self.egress or {}).get(neighbor, self)

    def queues(self) -> list["RouterQueue"]:
        """The router-wide queue and every egress override."""
        return [self, *(self.egress or {}).values()]

    @model_validator(mode="after")
    def _check_aqm_parameters(self) -> "RouterQueue":
        if any(q.egress is not None for q in (self.egress or {}).values()):
            raise ValueError("an egress queue cannot have its own egress overrides")
        if self.dualpi2_target_ms is not None and self.aqm != AqmKind.dualpi2:
            raise ValueError("dualpi2_target_ms requires aqm: dualpi2")
        if self.queue_limit_packets is not None and self.aqm is None:
            raise ValueError("queue_limit_packets requires an aqm")
        if (self.red_min_bytes is not None or self.red_max_bytes is not None) and self.aqm != AqmKind.red:
            raise ValueError("red_min_bytes / red_max_bytes require aqm: red")
        if (self.red_min_bytes or 20_000) >= (self.red_max_bytes or 60_000):
            raise ValueError("red_min_bytes must be below red_max_bytes")
        if (self.aqm == AqmKind.red and self.queue_limit_packets is not None
                and self.queue_limit_packets * 1500 <= (self.red_max_bytes or 60_000)):
            raise ValueError("red queue_limit_packets x 1500 B must exceed red_max_bytes")
        return self


class LinkDefaults(_StrictBase):
    """Initial conditions for every link the scenario does not list, and the
    base the listed ones are laid over (per field)."""

    forward: DirectionSpec = Field(default_factory=DirectionSpec)
    reverse: DirectionSpec = Field(default_factory=DirectionSpec)


class LinkConditions(_StrictBase):
    """Initial conditions of one topology link; forward = from→to egress."""

    from_: str = Field(alias="from")
    to: str
    forward: DirectionSpec = Field(default_factory=DirectionSpec)
    reverse: DirectionSpec = Field(default_factory=DirectionSpec)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class _Event(_StrictBase):
    at_s: float = Field(ge=0)
    label: str | None = None


class LinkEvent(_Event):
    """In-place change of one link direction (tc change: queues survive)."""

    type: Literal["link"]
    from_: str = Field(alias="from")
    to: str
    direction: Literal["forward", "reverse"] = "forward"
    bandwidth_mbps: float | None = Field(default=None, gt=0)
    delay_ms: float | None = Field(default=None, ge=0)
    jitter_ms: float | None = Field(default=None, ge=0)
    loss_pct: float | None = Field(default=None, ge=0, le=100)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="after")
    def _check(self) -> "LinkEvent":
        if all(v is None for v in (self.bandwidth_mbps, self.delay_ms, self.jitter_ms, self.loss_pct)):
            raise ValueError("link event must set bandwidth_mbps, delay_ms, jitter_ms or loss_pct")
        return self

    def applied_to(self, spec: DirectionSpec) -> DirectionSpec:
        changes = {
            name: getattr(self, name)
            for name in ("bandwidth_mbps", "delay_ms", "jitter_ms", "loss_pct")
            if getattr(self, name) is not None
        }
        return DirectionSpec.model_validate({**spec.model_dump(), **changes})


class AqmEvent(_Event, RouterQueue):
    """Replace the AQM leaf on every egress of `router` (and any earlier
    egress overrides, unless this event declares its own)."""

    type: Literal["aqm"]
    router: str

    def queue(self) -> RouterQueue:
        return RouterQueue.model_validate(self.model_dump(include=set(RouterQueue.model_fields)))


class _FlowEvent(_Event):
    type: Literal["flow"]
    id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
    route: str
    duration_s: float = Field(gt=0)


class TcpFlowEvent(_FlowEvent):
    """iperf3 TCP bulk; `cc` selects the kernel congestion control (-C)."""

    kind: Literal["tcp"]
    cc: Literal["cubic", "reno", "bbr"] | None = None
    parallel: int = Field(default=1, gt=0, le=128)


class UdpFlowEvent(_FlowEvent):
    """iperf3 UDP constant bit rate."""

    kind: Literal["udp"]
    rate_mbps: float = Field(gt=0)
    packet_size_bytes: int = Field(default=1200, ge=64, le=1472)


FlowEvent = Annotated[TcpFlowEvent | UdpFlowEvent, Field(discriminator="kind")]


class PpbpEvent(_Event):
    """PPBP cross traffic (qtraffic): Poisson burst arrivals, Pareto burst
    lengths (shape 3 - 2*hurst), `burst_mbps` per active burst; long-run load
    `mean_mbps`. The seed fixes every burst, so runs repeat exactly."""

    type: Literal["ppbp"]
    id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
    route: str
    duration_s: float = Field(gt=0)
    mean_mbps: float = Field(gt=0)
    burst_mbps: float = Field(gt=0)
    mean_burst_s: float = Field(default=0.5, gt=0)
    hurst: float = Field(default=0.8, gt=0.5, lt=1)
    seed: int = Field(default=1, ge=0)
    packet_size_bytes: int = Field(default=1200, ge=64, le=1472)


class Burst(_StrictBase):
    start_s: float = Field(ge=0)  # from the event's at_s
    duration_s: float = Field(gt=0)
    rate_mbps: float = Field(gt=0)


class BurstsEvent(_Event):
    """Fixed UDP bursts (qtraffic --schedule): each burst sends at its rate
    from at_s + start_s for duration_s, timed on the stream clock like PPBP,
    so burst starts are exact ground truth. Overlapping bursts add up."""

    type: Literal["bursts"]
    id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
    route: str
    bursts: list[Burst] = Field(min_length=1)
    packet_size_bytes: int = Field(default=1200, ge=64, le=1472)

    @property
    def duration_s(self) -> float:
        return max(b.start_s + b.duration_s for b in self.bursts)


class JoinEvent(_Event):
    """Subscriber connects now instead of at t=0 (or again, after a leave)."""

    type: Literal["join"]
    subscriber: str


class LeaveEvent(_Event):
    """Subscriber's client stops (connection closes)."""

    type: Literal["leave"]
    subscriber: str


Event = Annotated[
    LinkEvent | AqmEvent | FlowEvent | PpbpEvent | BurstsEvent | JoinEvent | LeaveEvent,
    Field(discriminator="type"),
]


class Scenario(_StrictBase):
    duration_s: float = Field(gt=0)
    link_defaults: LinkDefaults = Field(default_factory=LinkDefaults)
    links: list[LinkConditions] = Field(default_factory=list)
    routers: dict[str, RouterQueue] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)

    def initial_link(self, from_: str, to: str) -> tuple[DirectionSpec, DirectionSpec]:
        """(forward, reverse) at t=0 for a topology link."""
        for link in self.links:
            if (link.from_, link.to) == (from_, to):
                return (
                    link.forward.merged_over(self.link_defaults.forward),
                    link.reverse.merged_over(self.link_defaults.reverse),
                )
        return self.link_defaults.forward, self.link_defaults.reverse

    def router_queue(self, router_id: str) -> RouterQueue:
        return self.routers.get(router_id) or RouterQueue()

    def flows(self) -> list[TcpFlowEvent | UdpFlowEvent]:
        return [e for e in self.events if e.type == "flow"]

    def ppbp(self) -> list[PpbpEvent | BurstsEvent]:
        """qtraffic sources: PPBP and fixed bursts."""
        return [e for e in self.events if e.type in ("ppbp", "bursts")]

    def traffic_ids(self) -> list[str]:
        """iperf3 flows and PPBP processes share one port range, in file order."""
        return [e.id for e in self.events if e.type in ("flow", "ppbp", "bursts")]

    def join_at(self, subscriber: str) -> float:
        """First connection time (0 unless the subscriber's first event is a join)."""
        return self.sessions(subscriber)[0][0]

    def sessions(self, subscriber: str) -> list[tuple[float, float | None]]:
        """(join, leave) per session in time order; leave None = until the end.
        Session n >= 2 runs as client id `<subscriber>@<n>` (see session_id)."""
        times = sorted((e.at_s, e.type) for e in self.events
                       if e.type in ("join", "leave") and e.subscriber == subscriber)
        out: list[tuple[float, float | None]] = []
        if not times or times[0][1] == "leave":
            out.append((0.0, None))
        for t, kind in times:
            if kind == "join":
                out.append((t, None))
            else:
                out[-1] = (out[-1][0], t)
        return out

    @staticmethod
    def session_id(subscriber: str, n: int) -> str:
        return subscriber if n == 1 else f"{subscriber}@{n}"

    def check_against(self, topology: TopologyConfig) -> "Scenario":
        declared = {(link.from_, link.to) for link in topology.links}
        seen: set[tuple[str, str]] = set()
        for link in self.links:
            key = (link.from_, link.to)
            if key not in declared:
                raise ValueError(
                    f"scenario link {list(key)!r} must name a topology link in its declared from/to order"
                )
            if key in seen:
                raise ValueError(f"scenario link {list(key)!r} listed twice")
            seen.add(key)
        neighbors: dict[str, set[str]] = {}
        for link in topology.links:
            neighbors.setdefault(link.from_, set()).add(link.to)
            neighbors.setdefault(link.to, set()).add(link.from_)

        def check_egress(rid: str, queue: RouterQueue, where: str) -> None:
            unknown = sorted(set(queue.egress or {}) - neighbors.get(rid, set()))
            if unknown:
                raise ValueError(f"{where}: egress {unknown!r} are not neighbors of router {rid!r}")

        for rid, queue in self.routers.items():
            if rid not in topology.routers:
                raise ValueError(f"scenario router {rid!r} is not a topology router")
            check_egress(rid, queue, f"scenario router {rid!r}")

        routes = topology.traffic.routes if topology.traffic is not None else {}
        flow_ids: set[str] = set()
        membership: dict[str, list[tuple[float, str]]] = {}
        for event in self.events:
            where = f"event at {event.at_s:g}s ({event.type})"
            if event.at_s > self.duration_s:
                raise ValueError(f"{where} is after duration_s {self.duration_s:g}")
            if event.type == "link":
                if (event.from_, event.to) not in declared:
                    raise ValueError(f"{where}: link {[event.from_, event.to]!r} is not a topology link "
                                     "in its declared from/to order")
                egress_node = event.from_ if event.direction == "forward" else event.to
                if event.bandwidth_mbps is not None and egress_node in topology.switches:
                    raise ValueError(f"{where}: changes the capacity of an egress of switch {egress_node!r}; "
                                     "congestion belongs on a router egress")
                forward, reverse = self.initial_link(event.from_, event.to)
                spec = forward if event.direction == "forward" else reverse
                # Live edits keep the qdisc tree; they cannot add HTB or netem.
                if event.bandwidth_mbps is not None and spec.bandwidth_mbps is None:
                    raise ValueError(f"{where}: changes bandwidth on a direction with no initial bandwidth_mbps")
                has_netem = spec.delay_ms is not None or spec.loss_pct is not None
                changes_netem = any(v is not None for v in (event.delay_ms, event.jitter_ms, event.loss_pct))
                if changes_netem and not has_netem:
                    raise ValueError(f"{where}: changes netem on a direction with no initial "
                                     "delay_ms or loss_pct (declare loss_pct: 0)")
                if event.jitter_ms is not None and event.applied_to(spec).delay_ms is None:
                    raise ValueError(f"{where}: jitter_ms requires delay_ms")
            elif event.type == "aqm":
                if event.router not in topology.routers:
                    raise ValueError(f"{where}: {event.router!r} is not a topology router")
                check_egress(event.router, event, where)
            elif event.type in ("flow", "ppbp", "bursts"):
                if event.route not in routes:
                    raise ValueError(f"{where}: flow {event.id!r} uses unknown traffic route {event.route!r}")
                if event.id in flow_ids:
                    raise ValueError(f"{where}: duplicate flow id {event.id!r}")
                flow_ids.add(event.id)
                if event.at_s + event.duration_s > self.duration_s:
                    raise ValueError(f"{where}: flow {event.id!r} runs past duration_s")
            else:
                if event.subscriber not in topology.subscribers:
                    raise ValueError(f"{where}: {event.subscriber!r} is not a topology subscriber")
                membership.setdefault(event.subscriber, []).append((event.at_s, event.type))
        for sid, times in membership.items():
            times.sort()
            on = times[0][1] == "leave"   # on from t=0 when the first event is a leave
            last = -1.0
            for t, kind in times:
                if (kind == "join") == on:
                    raise ValueError(f"subscriber {sid!r} {'leaves before it joins' if kind == 'leave' else 'joins twice'}"
                                     f" at {t:g}s")
                if t <= last:
                    raise ValueError(f"subscriber {sid!r} has two membership events at {t:g}s")
                on, last = kind == "join", t
        return self


def load_scenario(path: str | Path, topology: TopologyConfig) -> Scenario:
    """Load a scenario YAML and validate it against `topology`."""
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text())
    except FileNotFoundError as e:
        raise ConfigError(f"scenario not found: {p}") from e
    except yaml.YAMLError as e:
        raise ConfigError(f"failed to parse {p}: {e}") from e
    if not isinstance(raw, dict):
        raise ConfigError(f"{p}: top-level value must be a mapping")
    try:
        return Scenario.model_validate(raw).check_against(topology)
    except Exception as e:
        raise ConfigError(f"{p}: {e}") from e
