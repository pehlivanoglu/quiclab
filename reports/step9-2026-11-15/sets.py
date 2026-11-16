"""SETS: set-based grouping (Step 9, 2026-11-15).

State: a table {observed set -> count}. Nothing else. Everything below is computed from the table when
it is read, so the output cannot depend on the order of events. Sets are int bitmasks over a fixed client
index.

Matching (S' counted toward S):
  exact     S' == S
  quantile  |S' - S| <= EXTRA (FLAG) and |S - S'| <= q(|S|, m), q = the Q quantile (T) of Binomial(|S|, m)
Support(S) = sum of the counts of the observed sets that match S (S itself included).
Groups = observed sets with support >= k that do not match another observed set with a higher count
(a fragment is absorbed by the set it comes from).
Crossing filter (variant): while two groups overlap without containment, drop the member of a crossing
pair that takes part in more crossings; tie: the lower support; tie: the larger bitmask (M, deterministic).
m (quantile rule) is estimated from the table: start with m = 0 (exact plus EXTRA); assign every stored
set to the smallest group that contains it up to EXTRA extra clients (M); m = missing (client, observation)
pairs / all (client, observation) pairs of those assignments; recompute the groups with the new m and
repeat until |change| < M_TOL (M) or M_ITERS (M).
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache

from scipy.stats import binom

Q = 0.99          # (T) binomial quantile of the number of missed clients
EXTRA = 1         # (FLAG) clients an observation may have outside the set it is counted toward
M_TOL = 1e-4      # (M)
M_ITERS = 30      # (M)
K_EST = 2         # (M) k used while estimating m


def pc(x: int) -> int:
    return x.bit_count()


@lru_cache(maxsize=200000)
def qmiss(n: int, m: float) -> int:
    if m <= 0:
        return 0
    return int(binom.ppf(Q, n, m))


class Table:
    """The whole state."""

    def __init__(self):
        self.c: Counter = Counter()

    def add(self, s: int) -> None:
        if pc(s) >= 2:
            self.c[s] += 1

    def size_bytes(self, n_clients: int) -> int:
        return len(self.c) * ((n_clients + 7) // 8 + 8)


def match_lists(c: Counter, rule: str, m: float):
    """For each stored set S: the stored sets S' that match S."""
    sets = list(c)
    out = {}
    for s in sets:
        if rule == "exact":
            out[s] = [s]
            continue
        n = pc(s)
        q = qmiss(n, round(m, 6))
        out[s] = [t for t in sets if pc(t & ~s) <= EXTRA and pc(s & ~t) <= q]
    return out, len(sets) ** 2 if rule != "exact" else len(sets)


def groups_of(c: Counter, rule: str, m: float, k: int, crossing: bool = False, ml=None):
    """[(set, support, mean Jaccard)] and the number of pair comparisons."""
    if ml is None:
        ml, work = match_lists(c, rule, m)
    else:
        work = 0
    sup = {s: sum(c[t] for t in ts) for s, ts in ml.items()}
    absorbed = set()
    for s, ts in ml.items():
        for t in ts:
            if t != s and c[s] > c[t]:
                absorbed.add(t)
    gs = sorted(s for s in c if sup[s] >= k and s not in absorbed)
    if crossing:
        gs = crossing_filter(gs, sup)
    out = []
    for s in gs:
        j = sum(c[t] * pc(s & t) / pc(s | t) for t in ml[s]) / sup[s]
        out.append((s, sup[s], j))
    return out, work


def crossing_filter(gs, sup):
    gs = sorted(gs)
    while True:
        cross = [(a, b) for i, a in enumerate(gs) for b in gs[i + 1:]
                 if a & b and (a & ~b) and (b & ~a)]
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


def estimate_m(c: Counter):
    """(m, iterations) from the table (see module doc)."""
    m, it = 0.0, 0
    for it in range(1, M_ITERS + 1):
        gs, _ = groups_of(c, "quantile", m, K_EST)
        gsets = sorted((g for g, _, _ in gs), key=lambda g: (pc(g), g))
        miss = tot = 0
        for s, n in c.items():
            for g in gsets:
                if pc(s & ~g) <= EXTRA and s & g:
                    miss += n * pc(g & ~s)
                    tot += n * pc(g)
                    break
        new = miss / tot if tot else 0.0
        if abs(new - m) < M_TOL:
            return new, it
        m = new
    return m, it
