"""Stage 1 incremental NPR-B against frozen NPR-B: group series and every E value bit-identical (small synthetic data).

    .venv/bin/python3 -m pytest -q reports/npr-2026-11-17/incr/test_npr_b_incr.py
"""

from __future__ import annotations

import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import npr_b_incr as I   # noqa: E402  (puts the frozen copies on sys.path)
import npr               # noqa: E402
import npr_var           # noqa: E402


def bits(x: float) -> bytes:
    return struct.pack("<d", x)


@dataclass
class FrozenRec(npr_var.ReaderB):
    log: list = field(default_factory=list)

    def evalue(self, g, T):
        E = super().evalue(g, T)
        self.log.append((g, T, bits(E)))
        return E


@dataclass
class IncrRec(I.ReaderBIncr):
    log: list = field(default_factory=list)

    def evalue(self, g, T):
        E = super().evalue(g, T)
        self.log.append((g, T, bits(E)))
        return E


def synth(seed, sizes, T, m, f, na, p_on):
    """Leaves of the given sizes; per event each leaf on with p_on; on member 1 w.p. 1-m, off member 1 w.p. f; NA w.p. na."""
    rng = np.random.default_rng(seed)
    clients = [f"c{i}" for i in range(sum(sizes))]
    leaf = np.repeat(np.arange(len(sizes)), sizes)
    cols = []
    while len(cols) < T:
        on = rng.random(len(sizes)) < p_on
        if not on.any():
            continue
        x = np.where(on[leaf], rng.random(len(leaf)) > m, rng.random(len(leaf)) < f).astype(float)
        x[rng.random(len(leaf)) < na] = np.nan
        if np.nansum(x) == 0:
            continue
        cols.append(x)
    return clients, cols


CASES = [   # (seed, leaf sizes, events, m, f, na, p_on)
    (1, (4, 4), 30, 0.05, 0.01, 0.0, 0.5),
    (2, (3, 5, 6), 40, 0.10, 0.02, 0.05, 0.4),
    (3, (10,), 30, 0.10, 0.02, 0.05, 0.6),         # one leaf: should mostly stay whole
    (4, (2, 2, 3, 8), 50, 0.20, 0.05, 0.10, 0.35),
    (5, (6, 6), 40, 0.30, 0.10, 0.0, 0.5),          # noisy
    (6, (5, 12, 3), 60, 0.08, 0.01, 0.02, 0.3),
]


@pytest.mark.parametrize("case", CASES, ids=[f"seed{c[0]}" for c in CASES])
def test_bit_identical(case):
    seed, sizes, T, m, f, na, p_on = case
    clients, cols = synth(seed, sizes, T, m, f, na, p_on)
    a, b = FrozenRec(clients), IncrRec(clients)
    for t, col in enumerate(cols, 1):
        a.add(col.copy()), b.add(col.copy())
        ra, rb = a.read((I.ALPHA,)), b.read((I.ALPHA,))
        assert ra["groups"] == rb["groups"], f"groups differ at close {t}"
        assert (ra["E_root"] is None) == (rb["E_root"] is None)
        if ra["E_root"] is not None:
            assert bits(ra["E_root"]) == bits(rb["E_root"]), f"E_root differs at close {t}"
    assert a.log == b.log            # every E value, same calls in the same order, bit for bit
    assert len(b.den_cache) > 0
    assert len(b.em_starts) <= len(a.em_starts)   # diagnostic counter only: one fit per (g, e) instead of per read


def test_run_matches_frozen_candidate():
    """incr.run equals the frozen candidates.run("NPR-B") group series on event dicts."""
    import candidates   # frozen copy
    clients, cols = synth(7, (4, 6, 3), 35, 0.1, 0.02, 0.05, 0.4)
    events = [{"ones": [c for c, x in zip(clients, col) if x == 1],
               "na": {c: 1 for c, x in zip(clients, col) if np.isnan(x)}} for col in cols]
    assert I.run(events, clients) == candidates.run("NPR-B", events, clients)


def test_splits_happen():
    """Guard against a vacuous test: the synthetic cases do produce splits (more than the root)."""
    clients, cols = synth(1, (4, 4), 30, 0.05, 0.01, 0.0, 0.5)
    r = I.ReaderBIncr(clients)
    for col in cols:
        r.add(col)
    assert len(r.read((I.ALPHA,))["groups"][I.ALPHA]) > 1
