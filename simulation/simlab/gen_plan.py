#!/usr/bin/env python3
"""A plan folder for a run that never ran on the testbed (stage C sizes), from the v4 suite's own planner.

    python3 simulation/simlab/gen_plan.py <out dir> --clients 100 [--point DEF] [--aqm pfifo] [--seed 1]

Calls scripts/v4_suite.plan_run unchanged (read-only use; it writes only into <out dir>/gen) for a G1-type
cell (T-LEAFn: one shaped leaf with N clients at LEAF_KBPS, S-BURST stimuli) and lays the result out like a
testbed run folder: topology.yaml, scenario.yaml, grouping/windows.json, v3-plan.json. simlab/plan.py then
builds the simulation plan from it (events.csv rows come from the scenario, plan.planned_event_rows).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB))
sys.path.insert(0, str(QUICLAB / "scripts"))

import v4_suite as v4  # noqa: E402


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out", type=Path)
    ap.add_argument("--clients", type=int, required=True)
    ap.add_argument("--point", default="DEF", choices=sorted(v4.POINTS))
    ap.add_argument("--aqm", default="pfifo")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    cell = v4.Cell("G1", "sburst", f"n{a.clients}", "base", (a.aqm,), point=a.point, seeds=(a.seed,),
                   opts=v4.leaf_opts(a.clients))
    gen = a.out / "gen"
    p = v4.plan_run(cell, a.aqm, a.seed, gen, "sim")
    (a.out / "grouping").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p.topology, a.out / "topology.yaml")
    shutil.copyfile(p.scenario, a.out / "scenario.yaml")
    shutil.copyfile(gen / f"{p.name}-windows.json", a.out / "grouping" / "windows.json")
    shutil.copyfile(gen / f"{p.name}-plan.json", a.out / "v3-plan.json")
    print(f"{p.name}: {a.clients} clients, {p.duration:g} s, point {a.point}, violations {p.violations}")


if __name__ == "__main__":
    main(sys.argv[1:])
