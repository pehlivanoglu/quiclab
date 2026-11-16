"""SETS engine (v1, frozen 2026-11-15; see grouping/FREEZE-sets-v1.md).

Event formation is ECG's, inherited unchanged from Engine: onset alignment (half the flow's min RTT), the
delta / delta_max / hold clustering, the in-episode rule (a second onset while a flow is in an episode is
ignored) and closing by tick(). What ECG does at an event close (case matching, sequential evidence, the
tree, decay) is replaced: at a close the engine stores the event's observed set

    O1 = the flows with an onset in the event, minus `exclude` (control flows)

in a table {set: count}, if it has at least two flows. Groups, their support and mean Jaccard, and the tree
are computed from that table whenever they are read (grouping.sets). No k is fixed: every read takes k.
Nothing is forgotten (no decay): a flow that leaves or changes branch keeps its old sets.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Callable, Iterable

from . import sets as S
from .config import Config
from .engine import Engine
from .types import Event


class SetsEngine(Engine):
    def __init__(self, cfg: Config, log: Callable[[dict], None] | None = None, exclude: Iterable[str] = ()):
        super().__init__(cfg, log)
        self.exclude = frozenset(exclude)
        self.table: Counter = Counter()
        self.events: list[dict] = []

    # ECG's evidence decay has nothing to act on here.
    def _decay(self, t: float) -> None:
        return None

    def _close(self, e: Event) -> None:
        self.closed_events += 1
        self.last_close = (self.now, e.id)
        flows = tuple(sorted({m.flow for m in e.members} - self.exclude))
        stored = len(flows) >= S.MIN_SET
        if stored:
            self.table[frozenset(flows)] += 1
        rec = {"id": e.id, "t": self.now, "t0": e.t0, "members": list(flows), "stored": stored}
        self.events.append(rec)
        self._log({"type": "event", **rec})
        for cb in self.on_event_closed:
            cb(self, e, "SETS")

    # ── outputs (pure functions of the table) ───────────────────────────

    def groups(self, k: int) -> list[S.Group]:
        return S.groups(self.table, k)

    def tree(self, k: int) -> dict:
        return S.tree(self.groups(k))

    def memberships(self, flow: str, k: int) -> list[S.Group]:
        """The groups that contain `flow`, smallest first (a flow may be in several nested groups)."""
        return sorted((g for g in self.groups(k) if flow in g.members), key=lambda g: (len(g.members), g.members))

    def snapshot(self) -> dict:
        return {"t": self.now, "table": {",".join(sorted(s)): n for s, n in sorted(self.table.items(), key=lambda x: sorted(x[0]))},
                "m": S.estimate_m(self.table)[0] if self.table else 0.0,
                "groups": {k: [g.__dict__ for g in self.groups(k)] for k in (2, 3)}}


def replay_log(path: str | Path, cfg: Config, exclude: Iterable[str] = (),
               on_close: Callable[[SetsEngine, Event], None] | None = None) -> SetsEngine:
    """Feed an onset log (meta / obs / onset records, grouping.synth.read_log format) with the same tick
    schedule as grouping.replay.run."""
    from .synth import read_log
    return replay_records(read_log(path), cfg, exclude, on_close)


def replay_records(records, cfg: Config, exclude: Iterable[str] = (),
                   on_close: Callable[[SetsEngine, Event], None] | None = None) -> SetsEngine:
    eng = SetsEngine(cfg, exclude=exclude)
    if on_close:
        eng.on_event_closed.append(lambda en, e, case: on_close(en, e))
    next_tick = 0.0
    for kind, t, obj in records:
        while next_tick <= t:
            eng.tick(next_tick)
            next_tick = round(next_tick + cfg.obs_window, 6)
        if kind == "meta":
            eng.on_meta(obj)
        elif kind == "obs":
            eng.on_obs(obj)
        else:
            eng.on_onset(obj)
    eng.finish()
    return eng
