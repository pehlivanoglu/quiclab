"""Data types shared by the ECG engine, generator, adapter and replay tool
(brief v1.1 §3, §6.1, §6.5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# ── inputs ───────────────────────────────────────────────────────────────

@dataclass
class Onset:
    flow: str
    t_onset: float          # best estimate of when congestion started (s, relay clock)
    t_arrival: float        # when the detector raised the alarm (>= t_onset)
    track: str = "delay"    # delay | ecn | rate | loss
    magnitude: float = 1.0  # statistic / threshold at crossing, >= 1
    primed: bool = False    # Phase 2


@dataclass
class ObsSample:
    flow: str
    t: float                # window start
    observable: bool
    in_episode: bool
    intervened: bool = False  # Phase 2


@dataclass
class FlowMeta:
    flow: str
    mrtt: float
    ecn_capable: bool = False
    rendition_bps: float | None = None


# ── engine state ─────────────────────────────────────────────────────────

@dataclass
class Member:
    flow: str
    t_al: float
    t_arrival: float
    track: str
    magnitude: float
    primed: bool


@dataclass
class Event:
    id: int
    t0: float
    members: list[Member] = field(default_factory=list)
    closes_at: float = 0.0


@dataclass
class Node:
    id: int
    kind: Literal["leaf", "internal", "root"]
    parent: int | None
    members: set[str] = field(default_factory=set)       # leaves: flows with node == id
    candidates: set[str] = field(default_factory=set)    # flows with cand[id] > 0
    children: set[int] = field(default_factory=set)      # internal / root
    support: float = 0.0
    confirmed: bool = False
    sub_patterns: dict[frozenset, float] = field(default_factory=dict)
    created_t: float = 0.0
    created_event: int = 0
    confirmed_t: float | None = None
    confirmed_events: int | None = None  # events on this node up to confirmation
    n_events: int = 0


@dataclass
class FlowState:
    node: int | None = None
    L: float = 0.0
    cand: dict[int, float] = field(default_factory=dict)
    lag: dict[int, tuple[float, float, int]] = field(default_factory=dict)  # node -> (mu, sigma, count)
    solo: float = 0.0
    together: float = 0.0
    apart: float = 0.0
    lambda_bg: float = 0.0
    lambda_t: float | None = None     # time of the last onset counted in lambda_bg
    in_episode: bool = False          # from the latest obs sample
    episode_since: float | None = None  # t_onset of the accepted onset whose episode is still open


# ── outputs ──────────────────────────────────────────────────────────────

@dataclass
class ConfirmedShared:
    node: int
    fired: list[str]
    silent: list[str]
    conf: float
    t_close: float
    tracks: list[str]


@dataclass
class Private:
    flow: str
    t: float


@dataclass
class PredictedShared:   # Phase 2: defined, never emitted
    node: int
    conf: float
    t: float
    trigger: str


@dataclass
class LatentShared:      # Phase 4: defined, never emitted
    flow_a: str
    flow_b: str
    conf: float
