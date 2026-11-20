"""Frozen grouping candidates (user, 2026-11-18, item 3). Code and parameters fixed; see FREEZE.md.

Every candidate reads the same input: the client x event matrix of one run, events formed by E1-0.5 (npr0b.form_window
with W = 0.5 s on the frozen v2-owd onsets at T100), or by the frozen SETS v1.1 event formation (E0) for "SETS-v1.1".

    series = run(name, events, clients)   # one list of groups (frozensets) per event close
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT)]   # the copies here first (npr, npr_var, step12), then grouping/ (SETS tag)

ALPHA = 0.05   # (P) user 2026-11-18, every NPR candidate
CANDIDATES = {
    # name: (kind, reader spec or SETS k, event formation, note)
    "NPR-B": ("npr", "B", "E1-0.5", "past-fitted null (no universal-inference guarantee), alpha 0.05"),
    "NPR-A": ("npr", "A-m0.20-f0.05", "E1-0.5", "bounded null m_max 0.20, f_max 0.05, alpha 0.05 (pre-declared)"),
    "NPR-A10": ("npr", "A-m0.10-f0.05", "E1-0.5", "bounded null m_max 0.10, f_max 0.05, alpha 0.05 (post-hoc, labelled)"),
    "SETS-v1.1": ("sets", 2, "E0", "frozen SETS (tag grouping-sets-v1.1) on its own 150 ms events; k = 2 (k = 3 side by side)"),
    "SETS@E1-0.5": ("sets", 2, "E1-0.5", "frozen SETS rule on E1-0.5 events; k = 2 (k = 3 side by side)"),
}


def run(name: str, events: list[dict], clients: list[str], k: int | None = None) -> list[list[frozenset]]:
    """events: dicts with "ones" (clients with an onset) and "na" (clients not observable); in close order."""
    kind, spec, _, _ = CANDIDATES[name]
    if kind == "npr":
        import npr_var
        import step12
        rd = npr_var.make(spec, clients)
        out = []
        for e in events:
            rd.add(step12.matrix_col(e, clients))
            out.append([frozenset(g) for g in rd.read((ALPHA,))["groups"][ALPHA]])
        return out
    from grouping import sets as S
    from grouping.sets import SetsConfig
    cfg = SetsConfig()
    k = k or spec
    table, out = Counter(), []
    for e in events:
        m = frozenset(e["ones"])
        if len(m) >= cfg.min_set:
            table[m] += 1
        out.append([frozenset(g.members) for g in S.groups(table, k, cfg)] if table else [])
    return out
