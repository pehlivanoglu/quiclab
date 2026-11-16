"""SETS v1 matching (frozen 2026-11-15, see grouping/FREEZE-sets-v1.md).

The state is a table {observed set -> count}; nothing else. Everything here is a pure function of that table
(and the configuration), so the output cannot depend on the order in which events arrived. This is the "old"
rule of Step 9 / Step 10 (reports/step9-2026-11-15/sets.py, quantile path), ported to sets of flow names.

  S' counts toward S     |S' - S| <= extra and |S - S'| <= q(|S|, m),
                         q = the `q` quantile of Binomial(|S|, m)
  m                      estimated from the table: start at m = 0; assign every stored set to the smallest
                         group (k = k_est) that contains it up to `extra` extra flows; m = missing (flow,
                         observation) pairs / all (flow, observation) pairs of those assignments; recompute the
                         groups with the new m; repeat until |change| < m_tol or m_iters rounds
  support(S)             sum of the counts of the stored sets that count toward S (S included)
  groups at k            stored sets with support >= k that do not count toward a stored set with a higher count
  mean Jaccard(S)        count-weighted mean of |S & S'| / |S | S'| over the sets counted toward S
  crossing filter        (option, off by default) while two groups overlap without one containing the other,
                         drop the member of a crossing pair that takes part in more crossings; tie: the lower
                         support; tie: the later set in the order below (Step 9)

Ties are broken by the order of the sets as bitmasks over the sorted flow names (the Step 9 order), so the
output is a deterministic function of the table.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field, fields
from functools import lru_cache

from scipy.stats import binom

from .config import Config


@dataclass(frozen=True)
class SetsConfig:
    """Every constant of SETS v1, with its tag (TAGS). `event` holds the ECG event-formation constants the
    engine inherits (only those listed in EVENT_FIELDS are used by SETS)."""
    q: float = 0.99                 # binomial quantile of the number of missed flows
    extra: int = 1                  # flows an observation may have outside the set it counts toward
    m_tol: float = 1e-4             # convergence of the m estimate
    m_iters: int = 30               # cap on m-estimate rounds
    k_est: int = 2                  # k used while estimating m
    min_set: int = 2                # observed sets of fewer flows are not stored
    crossing: bool = False          # crossing filter (option)
    exclude: tuple[str, ...] = ("sub-ctrl",)   # control flows left out of every observed set
    event: Config = field(default_factory=Config)

    TAGS = {"q": "T", "extra": "FLAG", "m_tol": "M", "m_iters": "M", "k_est": "M", "min_set": "M",
            "crossing": "M (option, off)", "exclude": "M",
            "event.delta": "P (user decision 2026-11-11)", "event.delta_max": "M (= 2 delta)", "event.hold": "M",
            "event.align_mode": "M", "event.obs_window": "M", "event.in_episode_rule": "M (ECG engine, always on)"}
    EVENT_FIELDS = ("delta", "delta_max", "hold", "align_mode", "align_table", "obs_window")

    def constants(self) -> list[tuple[str, object, str]]:
        """(name, value, tag) of every constant, inherited event formation included."""
        out = [(f.name, getattr(self, f.name), self.TAGS[f.name]) for f in fields(self) if f.name != "event"]
        for n in self.EVENT_FIELDS:
            if n == "align_table":
                continue
            out.append((f"event.{n}", getattr(self.event, n), self.TAGS[f"event.{n}"]))
        out.append(("event.in_episode_rule", "second onset in an episode ignored", self.TAGS["event.in_episode_rule"]))
        return out

    def to_dict(self) -> dict:
        d = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "event"}
        d["exclude"] = list(self.exclude)
        d["event"] = self.event.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SetsConfig":
        d = dict(d)
        ev = Config.from_dict(d.pop("event", {}))
        if "exclude" in d:
            d["exclude"] = tuple(d["exclude"])
        return cls(event=ev, **d)


FROZEN = SetsConfig()
# module-level names of the frozen values (kept for readers of Step 9 / 10 and the tests)
Q, EXTRA, M_TOL, M_ITERS, K_EST, MIN_SET = FROZEN.q, FROZEN.extra, FROZEN.m_tol, FROZEN.m_iters, FROZEN.k_est, FROZEN.min_set


@dataclass(frozen=True)
class Group:
    members: tuple[str, ...]
    support: int
    jaccard: float
    parent: tuple[str, ...] | None = None    # smallest group that strictly contains it (inclusion order)


def _pc(x: int) -> int:
    return x.bit_count()


@lru_cache(maxsize=200000)
def _qmiss(n: int, m: float, q: float) -> int:
    if m <= 0:
        return 0
    return int(binom.ppf(q, n, m))


def qmiss(n: int, m: float, cfg: SetsConfig = FROZEN) -> int:
    return _qmiss(n, round(m, 6), cfg.q)


def _masks(table: Counter) -> tuple[list[str], dict[frozenset, int]]:
    names = sorted({f for s in table for f in s})
    ix = {f: i for i, f in enumerate(names)}
    return names, {s: sum(1 << ix[f] for f in s) for s in table}


def _match_lists(c: dict[int, int], m: float, cfg: SetsConfig) -> dict[int, list[int]]:
    sets = list(c)
    out = {}
    for s in sets:
        q = qmiss(_pc(s), m, cfg)
        out[s] = [t for t in sets if _pc(t & ~s) <= cfg.extra and _pc(s & ~t) <= q]
    return out


def _crossing_filter(gs: list[int], sup: dict[int, int]) -> list[int]:
    gs = sorted(gs)
    while True:
        cross = [(a, b) for i, a in enumerate(gs) for b in gs[i + 1:] if a & b and (a & ~b) and (b & ~a)]
        if not cross:
            return gs
        n = Counter(x for p in cross for x in p)
        a, b = max(cross, key=lambda p: (max(n[p[0]], n[p[1]]), p))
        if n[a] != n[b]:
            drop = a if n[a] > n[b] else b
        elif sup[a] != sup[b]:
            drop = a if sup[a] < sup[b] else b
        else:
            drop = max(a, b)
        gs.remove(drop)


def _groups(c: dict[int, int], m: float, k: int, cfg: SetsConfig, crossing: bool = False) -> list[tuple[int, int, float]]:
    ml = _match_lists(c, m, cfg)
    sup = {s: sum(c[t] for t in ts) for s, ts in ml.items()}
    absorbed = set()
    for s, ts in ml.items():
        for t in ts:
            if t != s and c[s] > c[t]:
                absorbed.add(t)
    gs = sorted(x for x in c if sup[x] >= k and x not in absorbed)
    if crossing:
        gs = _crossing_filter(gs, sup)
    out = []
    for s in gs:
        j = sum(c[t] * _pc(s & t) / _pc(s | t) for t in ml[s]) / sup[s]
        out.append((s, sup[s], j))
    return out


def _estimate_m(c: dict[int, int], cfg: SetsConfig) -> tuple[float, int]:
    m, it = 0.0, 0
    for it in range(1, cfg.m_iters + 1):
        gsets = sorted((g for g, _, _ in _groups(c, m, cfg.k_est, cfg)), key=lambda g: (_pc(g), g))
        miss = tot = 0
        for s, n in c.items():
            for g in gsets:
                if _pc(s & ~g) <= cfg.extra and s & g:
                    miss += n * _pc(g & ~s)
                    tot += n * _pc(g)
                    break
        new = miss / tot if tot else 0.0
        if abs(new - m) < cfg.m_tol:
            return new, it
        m = new
    return m, it


def estimate_m(table: Counter, cfg: SetsConfig = FROZEN) -> tuple[float, int]:
    """(m, rounds) for a table {frozenset of flows: count}."""
    _, mk = _masks(table)
    return _estimate_m({mk[s]: n for s, n in table.items()}, cfg)


def groups(table: Counter, k: int, cfg: SetsConfig = FROZEN, crossing: bool | None = None) -> list[Group]:
    """Every group with support >= k: members, support, mean Jaccard and parent (Step 9 order)."""
    names, mk = _masks(table)
    c = {mk[s]: n for s, n in table.items()}
    m, _ = _estimate_m(c, cfg)
    raw = _groups(c, m, k, cfg, cfg.crossing if crossing is None else crossing)
    named = [(tuple(names[i] for i in range(len(names)) if s >> i & 1), sup, j) for s, sup, j in raw]
    par = tree([Group(n, s, j) for n, s, j in named])
    return [Group(n, s, j, par[n]) for n, s, j in named]


def tree(gs: list[Group]) -> dict[tuple[str, ...], tuple[str, ...] | None]:
    """Inclusion order: each group's parent is the smallest group that strictly contains it (None = top);
    tie between equal-size parents: the lexicographically first member tuple."""
    sets = [(frozenset(g.members), g.members) for g in gs]
    out = {}
    for s, name in sets:
        sup = [(len(t), tn) for t, tn in sets if s < t]
        out[name] = min(sup)[1] if sup else None
    return out


def smallest_group(gs: list[Group], flow: str) -> Group | None:
    """The smallest group that contains `flow` (tie: the Step 9 bitmask order, i.e. the list order)."""
    cand = [(len(g.members), i, g) for i, g in enumerate(gs) if flow in g.members]
    return min(cand)[2] if cand else None
