#!/usr/bin/env python3
"""Computational cost of SETS v1 on synthetic input (2026-11-15). NOT an accuracy test: it says nothing about
how well groups are found at these sizes; it measures time and memory only.

    .venv/bin/python3 scripts/sets_bench.py [out.md]

Input model (M): N clients split into leaves of g clients; over HORIZON_S seconds, events at rate lam per
second, each on a random leaf; the observed set is the leaf with the measured bursty miss pattern (COMPLETE
share of events complete, the rest missing a uniform MISS_LO..MISS_HI share) plus false inclusions of other
clients at rate F_INCL. Per configuration: time per event (table update at the close), time per read
(groups at k = 2) at the end of the horizon, table size and peak memory, for exact matching (a group is a
set seen >= k times, no matching) and for the frozen matching. A read that exceeds READ_CAP_S is stopped and
reported as "> cap".
"""

from __future__ import annotations

import multiprocessing as mp
import random
import sys
import time
import tracemalloc
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HORIZON_S = 600.0     # (M)
COMPLETE = 0.75       # (M) share of events observed complete (v3, O1, leaf: 0.75)
MISS_LO, MISS_HI = 0.05, 0.5   # (M)
F_INCL = 0.006        # (M) v3 leaf false-inclusion rate, O1
READ_CAP_S = 300.0    # (M)
GRID = [(100, g) for g in (10, 50)] + [(n, g) for n in (1000, 10000) for g in (10, 50, 100, 500)]
RATES = (0.1, 1.0, 10.0)


def observations(n, g, lam, seed=0):
    rng = random.Random(seed)
    flows = [f"c{i:05d}" for i in range(n)]
    leaves = [flows[i:i + g] for i in range(0, n - g + 1, g)]
    out = []
    for _ in range(int(lam * HORIZON_S)):
        leaf = rng.choice(leaves)
        if rng.random() < COMPLETE:
            o = set(leaf)
        else:
            miss = rng.uniform(MISS_LO, MISS_HI)
            o = {c for c in leaf if rng.random() >= miss}
        k_extra = sum(1 for _ in range(n - g) if rng.random() < F_INCL) if n - g < 2000 else \
            int(rng.gauss(F_INCL * (n - g), (F_INCL * (n - g)) ** 0.5) + 0.5)
        for c in rng.sample(flows, max(0, k_extra)):
            o.add(c)
        if len(o) >= 2:
            out.append(frozenset(o))
    return out


def _read(table, rule, q):
    from grouping import sets as S
    t0 = time.perf_counter()
    tracemalloc.start()
    if rule == "exact":
        gs = [s for s, c in table.items() if c >= 2]
    else:
        gs = S.groups(table, 2)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    q.put((time.perf_counter() - t0, peak, len(gs)))


def one(n, g, lam):
    obs = observations(n, g, lam)
    tab = Counter()
    tracemalloc.start()
    t0 = time.perf_counter()
    for o in obs:
        tab[o] += 1
    t_ev = (time.perf_counter() - t0) / max(1, len(obs))
    cur, peak_tab = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    res = {"n": n, "g": g, "lam": lam, "events": len(obs), "distinct": len(tab), "event_us": t_ev * 1e6,
           "table_mb": cur / 2 ** 20}
    for rule in ("exact", "frozen"):
        q = mp.Queue()
        p = mp.Process(target=_read, args=(tab, rule, q))
        p.start()
        p.join(READ_CAP_S)
        if p.is_alive():
            p.terminate()
            res[rule] = None
        else:
            dt, peak, ng = q.get()
            res[rule] = {"read_s": dt, "peak_mb": peak / 2 ** 20, "groups": ng}
    return res


def main(out: Path | None):
    rows = []
    for n, g in GRID:
        for lam in RATES:
            r = one(n, g, lam)
            rows.append(r)
            print(r, file=sys.stderr, flush=True)
    lines = ["| clients | group size | events / s | events | distinct sets | time per event (µs) | table (MB) | "
             "exact: read (s) / peak (MB) | frozen: read (s) / peak (MB) | frozen groups at k = 2 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        ex, fr = r["exact"], r["frozen"]
        lines.append(f"| {r['n']} | {r['g']} | {r['lam']:g} | {r['events']} | {r['distinct']} | {r['event_us']:.1f} | "
                     f"{r['table_mb']:.2f} | {f'{ex['read_s']:.4f} / {ex['peak_mb']:.2f}' if ex else f'> {READ_CAP_S:g} s'} | "
                     f"{f'{fr['read_s']:.3f} / {fr['peak_mb']:.2f}' if fr else f'> {READ_CAP_S:g} s'} | "
                     f"{fr['groups'] if fr else '-'} |")
    txt = "\n".join(lines) + "\n"
    print(txt)
    if out:
        out.write_text(txt)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
