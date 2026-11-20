"""Incremental NPR-B, stage 1 (user, 2026-11-19): the frozen NPR-B with the past-fitted null kept per (group, event).

Frozen ReaderB.evalue(g, T) refits the null's EM on the group's events before e, for every event e of the group, at
every read: the fit for (g, e) depends only on g and on the events before e (the matrix is append-only), not on T, so
the same fit is recomputed at every later read (O(T^2) EM fits per node per read). Here the resulting log P0(x_e) is
kept in den_cache[(g, e)] and computed once, by the same function on the same input; the sum over e runs in the same
order. Nothing else changes: read(), the tree rebuilt from the root, propose, e-BH, the alternative (already cached
per (g, e) by the frozen code) are the frozen code. Expected output: bit-identical E values and groups.

Diagnostic-only difference: em_starts (winning EM start per null fit) counts each (g, e) fit once instead of once
per read. Groups and E values do not depend on it.

The frozen copies (../frozen-2026-11-18) are imported, never modified.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

FROZEN = Path(__file__).resolve().parents[1] / "frozen-2026-11-18"
if str(FROZEN) not in sys.path:
    sys.path.insert(0, str(FROZEN))

import npr       # noqa: E402  (frozen copy)
import npr_var   # noqa: E402  (frozen copy)

assert "frozen-2026-11-18" in npr.__file__ and "frozen-2026-11-18" in npr_var.__file__, "not the frozen copies"

ALPHA = 0.05   # (P) as candidates.py, NPR-B


@dataclass
class ReaderBIncr(npr_var.ReaderB):
    den_cache: dict = field(default_factory=dict)   # (group, e) -> log P0(x_e; null fitted on the group's events < e)

    def evalue(self, g, T):
        rows = np.array(g)
        num = den = 0.0
        ks, ns, first = [], [], True
        for e in range(T):
            xe = self.X[e][rows]
            if not (~np.isnan(xe)).any():
                continue
            fac = self._alt_factor(g, e)
            k, n = float(np.nansum(xe)), float(np.sum(~np.isnan(xe)))
            if first or fac is None:
                first = False
                ks.append(k), ns.append(n)
                continue
            d = self.den_cache.get((g, e))
            if d is None:   # the frozen computation, once per (g, e)
                _, (pi, m, f), si = npr.em_null(np.array(ks), np.array(ns))
                self.em_starts.append(si)
                d = float(np.logaddexp(math.log(pi) + npr._lp_on(k, n, m), math.log1p(-pi) + npr._lp_off(k, n, f)))
                self.den_cache[(g, e)] = d
            den += d
            num += fac
            ks.append(k), ns.append(n)
        return math.exp(min(700.0, num - den)) if ks else 1.0


def run(events, clients):
    """Same interface as candidates.run("NPR-B", ...): one list of groups (frozensets) per event close."""
    import step12   # frozen copy
    rd = ReaderBIncr(clients)
    out = []
    for e in events:
        rd.add(step12.matrix_col(e, clients))
        out.append([frozenset(g) for g in rd.read((ALPHA,))["groups"][ALPHA]])
    return out
