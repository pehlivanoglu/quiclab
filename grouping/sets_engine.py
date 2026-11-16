"""SETS engine (v1, frozen 2026-11-15; see grouping/FREEZE-sets-v1.md).

Same input interface as ECG (FlowMeta, ObsSample, Onset, tick). Event formation and the per-flow
observability state are ECG's, inherited unchanged from grouping.Engine (not copied): onset alignment (half
the flow's min RTT), the delta / delta_max / hold clustering, the in-episode rule (a second onset while a flow
is in an episode is ignored) and closing by tick(). What ECG does at an event close (case matching,
sequential evidence, the tree, decay) is not used. At a close the engine stores the event's observed set

    O1 = the flows with an onset in the event, minus the configured control flows

in a table {set: count}, if it has at least `min_set` flows. Groups (members, support, mean Jaccard, parent by
inclusion), the tree and each client's smallest group are computed from that table whenever they are read
(grouping.sets); reading never changes the state. No k is fixed: every read takes k. Nothing is forgotten
(no decay): a flow that leaves or changes branch keeps its old sets.

O1 keeps every flow with an onset in the event, as Steps 8-10 did: ECG's own observability check at the close
(Engine._observable) is not applied to the members (1.4 % of the v3 event members, 147 of 10397, fail it).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable

from . import sets as S
from .config import Config
from .engine import Engine
from .sets import SetsConfig
from .types import Event

STATE_VERSION = 1


class SetsEngine(Engine):
    def __init__(self, cfg: SetsConfig | Config | None = None, log: Callable[[dict], None] | None = None,
                 exclude: Iterable[str] | None = None):
        if cfg is None:
            cfg = SetsConfig()
        elif isinstance(cfg, Config):
            cfg = SetsConfig(event=cfg)
        if exclude is not None:
            cfg = SetsConfig.from_dict({**cfg.to_dict(), "exclude": list(exclude)})
        self.scfg = cfg
        super().__init__(cfg.event, log)
        self.exclude = frozenset(cfg.exclude)
        self.table: Counter = Counter()
        self.events: list[dict] = []

    # ECG's evidence decay has nothing to act on here.
    def _decay(self, t: float) -> None:
        return None

    def _close(self, e: Event) -> None:
        self.closed_events += 1
        self.last_close = (self.now, e.id)
        flows = tuple(sorted({m.flow for m in e.members} - self.exclude))
        stored = len(flows) >= self.scfg.min_set
        if stored:
            self.table[frozenset(flows)] += 1
        rec = {"id": e.id, "t": self.now, "t0": e.t0, "members": list(flows), "stored": stored}
        self.events.append(rec)
        self._log({"type": "event", **rec})
        for cb in self.on_event_closed:
            cb(self, e, "SETS")

    # ── read API (pure functions of the table) ──────────────────────────

    def groups(self, k: int, crossing: bool | None = None) -> list[S.Group]:
        return S.groups(self.table, k, self.scfg, crossing)

    def tree(self, k: int, crossing: bool | None = None) -> dict:
        return S.tree(self.groups(k, crossing))

    def smallest_group(self, flow: str, k: int, crossing: bool | None = None) -> S.Group | None:
        return S.smallest_group(self.groups(k, crossing), flow)

    def memberships(self, flow: str, k: int, crossing: bool | None = None) -> list[S.Group]:
        """The groups that contain `flow`, smallest first (a flow may be in several nested groups)."""
        return sorted((g for g in self.groups(k, crossing) if flow in g.members), key=lambda g: (len(g.members), g.members))

    def snapshot(self) -> dict:
        return {"t": self.now, "m": S.estimate_m(self.table, self.scfg)[0] if self.table else 0.0,
                "groups": {k: [g.__dict__ for g in self.groups(k)] for k in (2, 3)}}

    # ── state dump / restore ────────────────────────────────────────────

    def dump(self) -> dict:
        """The SETS state (the table) plus the configuration and the closed-event log. ECG's transient
        event-formation state (open events, per-flow episode flags) is not part of it: dump between events."""
        return {"version": STATE_VERSION, "config": self.scfg.to_dict(), "t": self.now,
                "table": [[sorted(s), n] for s, n in sorted(self.table.items(), key=lambda x: sorted(x[0]))],
                "events": self.events}

    @classmethod
    def restore(cls, state: dict, log: Callable[[dict], None] | None = None) -> "SetsEngine":
        if state.get("version") != STATE_VERSION:
            raise ValueError(f"SETS state version {state.get('version')!r}, expected {STATE_VERSION}")
        eng = cls(SetsConfig.from_dict(state["config"]), log)
        eng.table = Counter({frozenset(s): int(n) for s, n in state["table"]})
        eng.events = list(state.get("events", []))
        eng.now = float(state.get("t", 0.0))
        return eng

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.dump(), sort_keys=True))

    @classmethod
    def load(cls, path: str | Path) -> "SetsEngine":
        return cls.restore(json.loads(Path(path).read_text()))


def replay_log(path: str | Path, cfg: SetsConfig | Config | None = None, exclude: Iterable[str] | None = None,
               on_close: Callable[[SetsEngine, Event], None] | None = None) -> SetsEngine:
    """Feed an onset log (meta / obs / onset records, grouping.synth.read_log format) with the same tick
    schedule as grouping.replay.run."""
    from .synth import read_log
    return replay_records(read_log(path), cfg, exclude, on_close)


def replay_records(records, cfg: SetsConfig | Config | None = None, exclude: Iterable[str] | None = None,
                   on_close: Callable[[SetsEngine, Event], None] | None = None, hide: Callable | None = None) -> SetsEngine:
    """`hide(engine, onset) -> bool`: drop an onset before it reaches the engine (late-joiner tests)."""
    eng = SetsEngine(cfg, exclude=exclude)
    if on_close:
        eng.on_event_closed.append(lambda en, e, case: on_close(en, e))
    next_tick = 0.0
    step = eng.scfg.event.obs_window
    for kind, t, obj in records:
        while next_tick <= t:
            eng.tick(next_tick)
            next_tick = round(next_tick + step, 6)
        if kind == "meta":
            eng.on_meta(obj)
        elif kind == "obs":
            eng.on_obs(obj)
        elif not (hide and hide(eng, obj)):
            eng.on_onset(obj)
    eng.finish()
    return eng
