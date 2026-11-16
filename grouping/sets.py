"""SETS v1 matching (frozen 2026-11-15, see grouping/FREEZE-sets-v1.md).

The state is a table {observed set -> count}; nothing else. Everything here is a pure function of that table,
so the output cannot depend on the order in which events arrived. This is the "old" rule of Step 9 / Step 10
(reports/step9-2026-11-15/sets.py, quantile path), ported to sets of flow names.

  S' counts toward S     |S' - S| <= EXTRA and |S - S'| <= q(|S|, m),
                         q = the Q quantile of Binomial(|S|, m)
  m                      estimated from the table: start at m = 0; assign every stored set to the smallest
                         group (k = K_EST) that contains it up to EXTRA extra flows; m = missing (flow,
                         observation) pairs / all (flow, observation) pairs of those assignments; recompute the
                         groups with the new m; repeat until |change| < M_TOL or M_ITERS rounds
  support(S)             sum of the counts of the stored sets that count toward S (S included)
  groups at k            stored sets with support >= k that do not count toward a stored set with a higher count
  mean Jaccard(S)        count-weighted mean of |S & S'| / |S | S'| over the sets counted toward S

Ties are broken by the order of the sets as bitmasks over the sorted flow names (the Step 9 order), so the
output is a deterministic function of the table.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from scipy.stats import binom

Q = 0.99          # (T) binomial quantile of the number of missed flows
EXTRA = 1         # (FLAG) flows an observation may have outside the set it counts toward
M_TOL = 1e-4      # (M) convergence of the m estimate
M_ITERS = 30      # (M) cap on m-estimate rounds
K_EST = 2         # (M) k used while estimating m
MIN_SET = 2       # (M) observed sets of fewer flows are not stored


@dataclass(frozen=True)
class Group:
    members: tuple[str, ...]
    support: int
    jaccard: float


def _pc(x: int) -> int:
    return x.bit_count()


@lru_cache(maxsize=200000)
def qmiss(n: int, m: float) -> int:
    if m <= 0:
        return 0
    return int(binom.ppf(Q, n, m))


def _masks(table: Counter) -> tuple[list[str], dict[frozenset, int]]:
    names = sorted({f for s in table for f in s})
    ix = {f: i for i, f in enumerate(names)}
    return names, {s: sum(1 << ix[f] for f in s) for s in table}


def _match_lists(c: dict[int, int], m: float) -> dict[int, list[int]]:
    sets = list(c)
    out = {}
    for s in sets:
        q = qmiss(_pc(s), round(m, 6))
        out[s] = [t for t in sets if _pc(t & ~s) <= EXTRA and _pc(s & ~t) <= q]
    return out


def _groups(c: dict[int, int], m: float, k: int) -> list[tuple[int, int, float]]:
    ml = _match_lists(c, m)
    sup = {s: sum(c[t] for t in ts) for s, ts in ml.items()}
    absorbed = set()
    for s, ts in ml.items():
        for t in ts:
            if t != s and c[s] > c[t]:
                absorbed.add(t)
    out = []
    for s in sorted(x for x in c if sup[x] >= k and x not in absorbed):
        j = sum(c[t] * _pc(s & t) / _pc(s | t) for t in ml[s]) / sup[s]
        out.append((s, sup[s], j))
    return out


def _estimate_m(c: dict[int, int]) -> tuple[float, int]:
    m, it = 0.0, 0
    for it in range(1, M_ITERS + 1):
        gsets = sorted((g for g, _, _ in _groups(c, m, K_EST)), key=lambda g: (_pc(g), g))
        miss = tot = 0
        for s, n in c.items():
            for g in gsets:
                if _pc(s & ~g) <= EXTRA and s & g:
                    miss += n * _pc(g & ~s)
                    tot += n * _pc(g)
                    break
        new = miss / tot if tot else 0.0
        if abs(new - m) < M_TOL:
            return new, it
        m = new
    return m, it


def estimate_m(table: Counter) -> tuple[float, int]:
    """(m, rounds) for a table {frozenset of flows: count}."""
    _, mk = _masks(table)
    return _estimate_m({mk[s]: n for s, n in table.items()})


def groups(table: Counter, k: int) -> list[Group]:
    """Every group with support >= k, its support and mean Jaccard (Step 9 order)."""
    names, mk = _masks(table)
    c = {mk[s]: n for s, n in table.items()}
    m, _ = _estimate_m(c)
    return [Group(tuple(names[i] for i in range(len(names)) if s >> i & 1), sup, j) for s, sup, j in _groups(c, m, k)]


def tree(gs: list[Group]) -> dict[tuple[str, ...], tuple[str, ...] | None]:
    """Inclusion order: each group's parent is the smallest group that strictly contains it (None = top)."""
    sets = [(frozenset(g.members), g.members) for g in gs]
    out = {}
    for s, name in sets:
        sup = [(len(t), tn) for t, tn in sets if s < t]
        out[name] = min(sup)[1] if sup else None
    return out
