"""SETS matching variants for Step 10 (2026-11-15). The state is still only {observed set -> count}; every
output is computed from the table when it is read. Sets are int bitmasks.

Variants of "S' counts toward S":
  old       Step 9 (sets.py): |S' - S| <= 1 (FLAG) and |S - S'| <= q(|S|, m), m estimated for the whole table by
            starting from exact matches (sets.estimate_m).
  new       |S' - S| <= x(N - |S|, f) and |S - S'| <= q(|S|, m_S):
              x = Q quantile (T) of Binomial(observable clients outside S, f), f = the measured false-inclusion
              rate of the observed-set definition (M: pooled single-egress leaf events, Step 10 Part B);
              m_S per candidate set from participation: matched observations M_S (start: the containment rule,
              M), participation of a member = share (count-weighted) of M_S containing it, m_S = 1 - mean
              participation; repeat with the new M_S until m_S stops changing (|change| < 1e-4 or 10 rounds, M).
  contain   S' counts toward S when |S' & S| >= CONTAIN x |S'| (FLAG 0.9), whatever is missing. Cannot tell a
            partial observation of S from a real sub-group of S: every leaf set counts toward its upstream set.
Groups = stored sets with support >= k that do not count toward a stored set with a higher count.
"""

from __future__ import annotations

import math
from collections import Counter
from functools import lru_cache

from scipy.stats import binom

import sets as S1   # Step 9 module (unchanged)

Q = 0.99          # (T)
CONTAIN = 0.9     # (FLAG)
M_TOL, M_ROUNDS = 1e-4, 10   # (M)
pc = S1.pc


@lru_cache(maxsize=400000)
def qx(n: int, p: float) -> int:
    if n <= 0 or p <= 0:
        return 0
    return int(binom.ppf(Q, n, p))


def _contain(t, s):
    return pc(t & s) >= CONTAIN * pc(t)


def match_lists(c: Counter, variant: str, n_clients: int = 0, f: float = 0.0, m_old: float = 0.0):
    """{S: [S' counted toward S]} and {S: m_S} for the stored sets."""
    sets = list(c)
    if variant == "old":
        ml, _ = S1.match_lists(c, "quantile", m_old)
        return ml, {s: m_old for s in sets}
    if variant == "contain":
        return {s: [t for t in sets if _contain(t, s)] for s in sets}, {s: math.nan for s in sets}
    ml, ms = {}, {}
    for s in sets:
        n = pc(s)
        xs = qx(n_clients - n, round(f, 6))
        cand = [t for t in sets if _contain(t, s)]
        m = math.nan
        for _ in range(M_ROUNDS):
            tot = sum(c[t] for t in cand)
            # mean participation of the members = sum count x |S' & S| / (total count x |S|)
            new = 1.0 - (sum(c[t] * pc(t & s) for t in cand) / (tot * n) if tot else 0.0)
            cand2 = [t for t in sets if pc(t & ~s) <= xs and pc(s & ~t) <= qx(n, round(new, 6))]
            if s not in cand2:
                cand2.append(s)
            if not math.isnan(m) and abs(new - m) < M_TOL and set(cand2) == set(cand):
                break
            m, cand = new, cand2
        ml[s], ms[s] = cand, m
    return ml, ms


def groups_of(c: Counter, k: int, ml):
    """[(set, support, mean Jaccard)] (Step 9 rule on the given match lists)."""
    sup = {s: sum(c[t] for t in ts) for s, ts in ml.items()}
    absorbed = set()
    for s, ts in ml.items():
        for t in ts:
            if t != s and c[s] > c[t]:
                absorbed.add(t)
    out = []
    for s in sorted(x for x in c if sup[x] >= k and x not in absorbed):
        j = sum(c[t] * pc(s & t) / pc(s | t) for t in ml[s]) / sup[s]
        out.append((s, sup[s], j))
    return out
