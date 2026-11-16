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
    <subscriber>_<n>, with its own sender files (qvideo client ids allow only
    alphanumerics, '-' and '_'); no topology subscriber may already carry such an id
  - every event happens within duration_s
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, ClassVar, Literal

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
    # Alternative to queue_limit_packets: the limit as a multiple of the egress's
    # BDP at t=0 (initial bandwidth x largest base RTT of the subscribers behind
    # it, full-size packets, at least 2). Off unless set; no scenario sets it.
    queue_limit_bdp: float | None = Field(default=None, gt=0, le=100)
    # RED thresholds in bytes (default 20 kB / 60 kB); scale them with the
    # link's BDP, or a fast link drops at a fraction of a millisecond of queue.
    red_min_bytes: int | None = Field(default=None, gt=0)
    red_max_bytes: int | None = Field(default=None, gt=0)
    # ECN marking on red / pie / fq_codel / codel; unset = on (every scenario before
    # suite v3). Suite v3 sets false. pfifo never marks; cake keeps its own default.
    ecn: bool | None = None
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
        if self.queue_limit_bdp is not None and (self.aqm is None or self.queue_limit_packets is not None):
            raise ValueError("queue_limit_bdp requires an aqm and excludes queue_limit_packets")
        if self.ecn is not None and self.aqm not in (AqmKind.red, AqmKind.pie, AqmKind.fq_codel, AqmKind.codel):
            raise ValueError("ecn applies to red, pie, fq_codel and codel")
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


class AsvSpec(_StrictBase):
    """Aggregate synchronized video (qtraffic --process=asv): the frame-size
    pattern of one rendition of the run's publisher (same seed), frames on the
    shared live grid at phase 0, every frame scaled by the scheduled rate at its
    GOP start / the rendition's payload rate, and spread evenly over the given
    emission times (measured on real clients: key_spread_ms / p_spread_ms)."""

    rendition_kbps: int = Field(default=5000, gt=0)
    key_spread_ms: float = Field(ge=0)
    p_spread_ms: float = Field(ge=0)


class BurstsEvent(_Event):
    """Fixed UDP bursts (qtraffic --schedule): each burst sends at its rate
    from at_s + start_s for duration_s, timed on the stream clock like PPBP,
    so burst starts are exact ground truth. Overlapping bursts add up.

    process pace (default): one socket, 1 ms credit loop (every scenario before suite v3).
    process poisson: one socket and one Poisson departure process per entry of
      flow_weights (relative rates; seed fixes every departure).
    process asv: aggregate synchronized video (`asv`), one socket.
    ramp_up_s / ramp_down_s (poisson, asv): every burst rises linearly from 0 to
    its rate over ramp_up_s and falls back over ramp_down_s, in ramp_step_s
    steps; the burst's start / duration / rate stay the truth (the ramp's peak)."""

    type: Literal["bursts"]
    id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
    route: str
    bursts: list[Burst] = Field(min_length=1)
    packet_size_bytes: int = Field(default=1200, ge=64, le=1472)
    process: Literal["pace", "poisson", "asv"] = "pace"
    flow_weights: list[Annotated[float, Field(gt=0)]] | None = Field(default=None, min_length=1, max_length=256)
    seed: int = Field(default=1, ge=0)
    ramp_up_s: float = Field(default=0, ge=0)
    ramp_down_s: float = Field(default=0, ge=0)
    ramp_step_s: float = Field(default=0.5, gt=0)
    asv: AsvSpec | None = None

    @model_validator(mode="after")
    def _check_process(self) -> "BurstsEvent":
        if self.flow_weights is not None and self.process != "poisson":
            raise ValueError("flow_weights requires process: poisson")
        if (self.asv is not None) != (self.process == "asv"):
            raise ValueError("process: asv requires asv, and asv requires process: asv")
        if (self.ramp_up_s or self.ramp_down_s) and self.process == "pace":
            raise ValueError("ramp_up_s / ramp_down_s require process poisson or asv")
        for b in self.bursts:
            if self.ramp_up_s + self.ramp_down_s > b.duration_s + 1e-9:
                raise ValueError("ramp_up_s + ramp_down_s exceed a burst's duration")
        return self

    @property
    def duration_s(self) -> float:
        return max(b.start_s + b.duration_s for b in self.bursts)

    def schedule(self) -> list[tuple[float, float, float]]:
        """qtraffic --schedule entries (start_s, duration_s, rate_mbps): the bursts,
        each ramp as a staircase of overlapping steps that add up to the burst's rate."""
        out: list[tuple[float, float, float]] = []
        for b in self.bursts:
            up = max(1, round(self.ramp_up_s / self.ramp_step_s)) if self.ramp_up_s else 0
            down = max(1, round(self.ramp_down_s / self.ramp_step_s)) if self.ramp_down_s else 0
            if not up and not down:
                out.append((b.start_s, b.duration_s, b.rate_mbps))
                continue
            # n = max(up, down) layers of rate / n: layer i switches on at step i of the
            # ramp-up and off at step i of the ramp-down (same height on both sides when
            # up == down; otherwise the ramp with fewer steps takes bigger ones).
            n = max(up, down, 1)
            end = b.start_s + b.duration_s
            for i in range(n):
                on = b.start_s + (self.ramp_up_s * i / n if up else 0.0)
                off = end - (self.ramp_down_s * (n - 1 - i) / n if down else 0.0)
                out.append((round(on, 6), round(off - on, 6), b.rate_mbps / n))
        return out


class BgEvent(_Event):
    """Always-on background on one traffic route (suite v3), not a stimulus: no
    truth script treats it as a burst. `rate_mbps` is the mean UDP payload / TCP
    goodput rate.
    process poisson: qtraffic, one Poisson process per entry of flow_weights.
    process tcp: one qtraffic TCP connection (cc), application-paced to rate_mbps;
      with on_s / off_s it sends rate_mbps x (on_s + off_s) / on_s for on_s, then
      idles off_s, starting phase_s into the cycle.
    periods (poisson only; suite v4 BG-ONOFF): explicit on periods [start_s, duration_s]
      relative to at_s; the source sends rate_mbps (its on rate) inside them and nothing
      outside."""

    type: Literal["bg"]
    id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
    route: str
    duration_s: float = Field(gt=0)
    rate_mbps: float = Field(gt=0)
    process: Literal["poisson", "tcp"] = "poisson"
    flow_weights: list[Annotated[float, Field(gt=0)]] = Field(default_factory=lambda: [1.0], min_length=1,
                                                               max_length=256)
    seed: int = Field(default=1, ge=0)
    packet_size_bytes: int = Field(default=1200, ge=64, le=1472)
    cc: Literal["cubic", "reno", "bbr"] | None = None
    on_s: float | None = Field(default=None, gt=0)
    off_s: float | None = Field(default=None, gt=0)
    phase_s: float = Field(default=0, ge=0)
    periods: list[tuple[Annotated[float, Field(ge=0)], Annotated[float, Field(gt=0)]]] | None = \
        Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _check_process(self) -> "BgEvent":
        if self.process != "tcp" and (self.cc or self.on_s or self.off_s or self.phase_s):
            raise ValueError("cc / on_s / off_s / phase_s require process: tcp")
        if (self.on_s is None) != (self.off_s is None):
            raise ValueError("on_s and off_s go together")
        if self.periods is not None:
            if self.process != "poisson":
                raise ValueError("periods require process: poisson")
            if any(a + d > self.duration_s + 1e-9 for a, d in self.periods):
                raise ValueError("a period runs past duration_s")
        return self

    def schedule(self) -> list[tuple[float, float, float]]:
        """qtraffic --schedule entries relative to at_s."""
        if self.periods is not None:
            return [(float(a), float(d), self.rate_mbps) for a, d in self.periods]
        if self.on_s is None:
            return [(0.0, self.duration_s, self.rate_mbps)]
        cycle = self.on_s + self.off_s
        peak = self.rate_mbps * cycle / self.on_s
        out, t = [], -(self.phase_s % cycle)
        while t < self.duration_s:
            a, b = max(t, 0.0), min(t + self.on_s, self.duration_s)
            if b > a:
                out.append((round(a, 6), round(b - a, 6), peak))
            t += cycle
        return out


class JoinEvent(_Event):
    """Subscriber connects now instead of at t=0 (or again, after a leave)."""

    type: Literal["join"]
    subscriber: str


class LeaveEvent(_Event):
    """Subscriber's client stops (connection closes)."""

    type: Literal["leave"]
    subscriber: str


class SalvoFlow(_StrictBase):
    start_s: float = Field(ge=0)   # from the event's at_s
    bytes: int = Field(gt=0)


class SalvoEvent(_Event):
    """Short TCP flows (suite v4 `shorttcp`; qtraffic --process=salvo): each entry opens
    its own TCP connection (cc) at at_s + start_s, writes `bytes` as fast as the
    connection allows and closes. The process lives duration_s (unfinished flows are
    cut there)."""

    type: Literal["salvo"]
    id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
    route: str
    duration_s: float = Field(gt=0)
    flows: list[SalvoFlow] = Field(min_length=1, max_length=4096)
    cc: Literal["cubic", "reno", "bbr"] | None = None
    packet_size_bytes: int = Field(default=1200, ge=64, le=1472)   # qtraffic's common flag; TCP ignores it

    @model_validator(mode="after")
    def _check_flows(self) -> "SalvoEvent":
        if any(f.start_s >= self.duration_s for f in self.flows):
            raise ValueError("a salvo flow starts at or after duration_s")
        return self


class PauseEvent(_Event):
    """The publisher stops sending video to one subscriber (session 1) for duration_s
    (qvideo-server --pause): no frame due in [at_s, at_s + duration_s) is produced for
    it; production resumes at the first keyframe due at or after the end. The
    connection stays up (the client keeps pinging)."""

    type: Literal["pause"]
    subscriber: str
    duration_s: float = Field(gt=0)


Event = Annotated[
    LinkEvent | AqmEvent | FlowEvent | PpbpEvent | BurstsEvent | BgEvent | JoinEvent | LeaveEvent
    | SalvoEvent | PauseEvent,
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

    def ppbp(self) -> list[PpbpEvent | BurstsEvent | BgEvent | SalvoEvent]:
        """qtraffic sources: PPBP, fixed bursts, background and short-TCP salvos."""
        return [e for e in self.events if e.type in ("ppbp", "bursts", "bg", "salvo")]

    def pauses(self) -> list[PauseEvent]:
        return [e for e in self.events if e.type == "pause"]

    def traffic_ids(self) -> list[str]:
        """iperf3 flows and qtraffic processes share one port range, in file order."""
        return [e.id for e in self.events if e.type in ("flow", "ppbp", "bursts", "bg", "salvo")]

    def join_at(self, subscriber: str) -> float:
        """First connection time (0 unless the subscriber's first event is a join)."""
        return self.sessions(subscriber)[0][0]

    def sessions(self, subscriber: str) -> list[tuple[float, float | None]]:
        """(join, leave) per session in time order; leave None = until the end.
        Session n >= 2 runs as client id `<subscriber>_<n>` (see session_id)."""
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

    SESSION_SEP: ClassVar[str] = "_"
    SESSION_RE: ClassVar[re.Pattern] = re.compile(r"^(.+)_([2-9]|[1-9][0-9]+)$")

    @staticmethod
    def session_id(subscriber: str, n: int) -> str:
        return subscriber if n == 1 else f"{subscriber}{Scenario.SESSION_SEP}{n}"

    @staticmethod
    def session_of(client_id: str, subscribers) -> tuple[str, int]:
        """(subscriber, session number) of a client id; the id itself and 1 when it
        is not a later session of one of `subscribers` (check_against keeps such ids
        out of the topology, so `subscribers` may also hold the session aliases)."""
        m = Scenario.SESSION_RE.match(client_id)
        if m and m.group(1) in subscribers:
            return m.group(1), int(m.group(2))
        return client_id, 1

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
            elif event.type == "pause":
                if event.subscriber not in topology.subscribers:
                    raise ValueError(f"{where}: {event.subscriber!r} is not a topology subscriber")
                if event.at_s + event.duration_s > self.duration_s:
                    raise ValueError(f"{where}: pause of {event.subscriber!r} runs past duration_s")
            elif event.type in ("flow", "ppbp", "bursts", "bg", "salvo"):
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
        for sid in membership:
            for n in range(2, len(self.sessions(sid)) + 1):
                if self.session_id(sid, n) in topology.subscribers:
                    raise ValueError(f"session {n} of {sid!r} would run as {self.session_id(sid, n)!r},"
                                     " which is already a topology subscriber")
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
