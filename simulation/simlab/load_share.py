#!/usr/bin/env python3
"""Measured calm load and video share against target on simulation runs, next to the testbed counterpart.

    python3 simulation/simlab/load_share.py [ack] [run set] > out.md

Uses the frozen v3 check function itself (scripts/v3_gate.check_load_share: calm load within LOAD_TOL of U, video
share / 0.96 within SHARE_TOL of s); v3_gate.run_checks is not called (it writes v3-checks.json into the run).
Testbed values: the run's own v3-checks.json (read only).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "scripts"), str(HERE.parents[1]), str(HERE)]
import stageb  # noqa: E402
import v3_gate  # noqa: E402


def main(argv):
    ack, run_set = (argv + ["matched", "applimited"])[:2] if len(argv) < 2 else argv[:2]
    print("| run | egress | U | load testbed | load sim | share testbed | share sim | ok testbed | ok sim |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name, tb, sim, _ in stageb.runs(ack, run_set):
        s = v3_gate.check_load_share(sim, json.loads((sim / "v3-plan.json").read_text()))
        t = json.loads((tb / "v3-checks.json").read_text()).get("1_load_share", {})
        for e, v in (s.get("egress") or {}).items():
            tv = (t.get("egress") or {}).get(e, {})
            print(f"| {name.removeprefix('sim-B-')} | {e} | {v.get('U')} | {tv.get('load')} | {v.get('load')} | "
                  f"{tv.get('share')} | {v.get('share')} | {tv.get('ok')} | {v.get('ok')} |")


if __name__ == "__main__":
    main(sys.argv[1:])
