#!/usr/bin/env python3
"""Stage C plan folders (spec section 6; user decisions 2026-11-19). Uses the v4 suite's own sizing, background and
stimulus code (scripts/v4_suite.py, scripts/v3_suite.py, read only; nothing there is edited) through a process-local
dispatch for the new topology kind "stagec".

    python3 simulation/simlab/stagec_gen.py <out dir> --clients 300 --layout L50 [--aqm pfifo] [--seed 1] [--point DEF]

Topology "stagec": publisher -> r1 -> r2 (the upstream egress "up", shaped) -> one switch per leaf (each leaf egress
shaped) -> clients. Every egress sized by the v4 rule at the run's point (DEF: s 0.30, U 0.50; EXT: U 0.70).
Layouts (P, user 2026-11-19 / spec 6): equal leaves of 10, 50, 100 clients; "uneven" = leaf sizes 2-200 from the
fixed list UNEVEN[N]. Client bitrates 500 and 1000 kb/s alternating inside every leaf (spec: mixed). Leaves are named
l01, l02, ... (zero-padded) in the order of UNEVEN / equal blocks; clients <leaf>c<k>.
Stimuli (600 s, P): independent surges on every leaf and on the upstream egress (v3 indep: levels U3, durations D3,
gaps 15 s exponential, >= 5 s), plus PAIR_SHARE x (number of leaves) two-leaf surges (two random leaves, same start,
level and duration). Background: the v4 rule (cbr).
"""

from __future__ import annotations

import argparse
import random
import shutil
import sys
from pathlib import Path

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB))
sys.path.insert(0, str(QUICLAB / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scale_ext  # noqa: E402,F401
import v3_suite as v3  # noqa: E402
import v4_suite as v4  # noqa: E402

DURATION_S = 600.0                                       # (P) user 2026-11-19
RATES = (500, 1000)                                      # (S) spec 6: mixed; alternating inside a leaf (P)
EQUAL = {"L10": 10, "L50": 50, "L100": 100}
_BASE = [2, 3, 5, 8, 12, 20, 50, 100, 200]               # (P) uneven 2-200
UNEVEN = {100: [2, 3, 5, 8, 12, 20, 50], 300: [2, 3, 5, 8, 12, 20, 50, 200], 1000: _BASE + _BASE + [200]}
PAIR_SHARE = 0.2                                         # (P) two-leaf surges: 0.2 per leaf (at least 2)
LAYOUTS = (*EQUAL, "uneven")


def leaf_sizes(n: int, layout: str) -> list[int]:
    if layout == "uneven":
        sizes = UNEVEN[n]
    else:
        k = EQUAL[layout]
        assert n % k == 0, (n, layout)
        sizes = [k] * (n // k)
    assert sum(sizes) == n, (n, layout, sum(sizes))
    return sizes


def build_stagec(variant: str, s: float, U: float, seed: int, opts: dict) -> v4.Topo:
    sizes = leaf_sizes(opts["n"], variant)
    w = max(2, len(str(len(sizes))))
    names = [f"l{i + 1:0{w}d}" for i in range(len(sizes))]
    n = v4._New(seed, s, U, {})
    b = n.b
    b.router("r1", "r2")
    b.switch(*(f"switch-{x}" for x in names))
    b.feed("r1")
    leaves = {}
    for x, k in zip(names, sizes):
        leaves[x] = {f"{x}c{j + 1:0{len(str(k))}d}": RATES[j % 2] for j in range(k)}
        n.rates.update(leaves[x])
    n.add("up", "r1", "r2", list(n.rates))
    for x in names:
        n.add(x, "r2", f"switch-{x}", list(leaves[x]))
        n.leaf_clients(f"switch-{x}", leaves[x])
    leaf_of = {c: x for x in names for c in leaves[x]}
    return n.topo("stagec", variant, leaf_of, {c: f"switch-{leaf_of[c]}" for c in leaf_of})


def plan_stagec(t: v4.Topo, seed: int) -> tuple[list, list, float]:
    rng = random.Random(f"stagec-{t.variant}-{len(t.rates)}-{seed}")
    st = v4.Stim4(t, seed)
    leaves = sorted(x for x in t.egress if x != "up")
    v3.indep(st, leaves + ["up"], rng, DURATION_S)
    if len(leaves) >= 2:
        for _ in range(max(2, round(PAIR_SHARE * len(leaves)))):
            a, b = rng.sample(leaves, 2)
            u, d = rng.choice(v3.U3), rng.choice(v3.D3)
            at = rng.uniform(v3.WARMUP_S, DURATION_S - v3.TAIL_S - d)
            for x in (a, b):
                st.surge(x, at, u, d, f"{a}+{b}")
    return st.events, v3.flag_concurrent(st.windows), DURATION_S


_topo_of, _plan_type4 = v4.topo_of, v4.plan_type4


def _topo_dispatch(c, seed):
    if c.kind != "stagec":
        return _topo_of(c, seed)
    s, U = c.su
    return build_stagec(c.variant, s, U, seed, c.opts)


def _plan_dispatch(rtype, t, seed, variant="", stim="surge"):
    if rtype != "stagec":
        return _plan_type4(rtype, t, seed, variant, stim)
    return plan_stagec(t, seed)


v4.topo_of = _topo_dispatch           # process-local; v4_suite.py itself is unchanged
v4.plan_type4 = _plan_dispatch


def make(out: Path, clients: int, layout: str, aqm: str, seed: int, point: str, block: str) -> dict:
    cell = v4.Cell(block, "stagec", layout, "stagec", (aqm,), point=point, seeds=(seed,), opts={"n": clients})
    gen = out / "gen"
    p = v4.plan_run(cell, aqm, seed, gen, "sim-stagec")
    (out / "grouping").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p.topology, out / "topology.yaml")
    shutil.copyfile(p.scenario, out / "scenario.yaml")
    shutil.copyfile(gen / f"{p.name}-windows.json", out / "grouping" / "windows.json")
    shutil.copyfile(gen / f"{p.name}-plan.json", out / "v3-plan.json")
    return {"name": p.name, "duration": p.duration, "violations": p.violations,
            "leaves": dict(zip(sorted(x for x in cell_egress(out) if x != "up"), leaf_sizes(clients, layout)))}


def cell_egress(out: Path) -> dict:
    import json
    return json.loads((out / "v3-plan.json").read_text())["egress"]


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out", type=Path)
    ap.add_argument("--clients", type=int, required=True)
    ap.add_argument("--layout", choices=LAYOUTS, required=True)
    ap.add_argument("--aqm", default="pfifo")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--point", default="DEF", choices=sorted(v4.POINTS))
    ap.add_argument("--block", default="C")
    a = ap.parse_args(argv)
    r = make(a.out, a.clients, a.layout, a.aqm, a.seed, a.point, a.block)
    print(f"{r['name']}: {a.clients} clients, {len(r['leaves'])} leaves, {r['duration']:g} s, violations {r['violations']}")


if __name__ == "__main__":
    main(sys.argv[1:])
