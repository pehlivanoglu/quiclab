#!/usr/bin/env python3
"""Short verification scenarios for the fq_codel pin fix: one per topology, cut from the v3 campaign's
generated scenarios (same topology, AQMs, background and first stimuli) to DURATION_S seconds.

    python3 scripts/fq_pin_short.py [.runs/2026-11-14_1818_v3/_gen] [out_dir]   # writes <out>/<name>.yaml

Then, per topology (the user runs these):
    quiclab run -c <gen>/<name>-topology.yaml -s <out>/<name>.yaml --run-id pinfix-<name>
    python3 scripts/fq_pin_check.py .runs/pinfix-<name>
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

DURATION_S = 60.0     # (M) long enough for the warm-up, one or two stimuli and backlogged fq_codel queues
SOURCES = {           # topology -> one fq_codel (or mixab) run of the v3 campaign
    "t-base": "v3-C2-sburst-s030u070-fq_codel-r1",
    "h-hier": "v3-C7-hhier-s030-fq_codel-r1",
    "h-depth": "v3-C9-hdepth-tree16-fq_codel-r1",
    "a-mixed": "v3-C12-amixed-access-fq_codel-r1",
    "mixab": "v3-M8-hhier-mixab-mixab-r1",
}


def _cut(x, left: float) -> None:
    """Cap every nested duration_s of an event so that nothing runs past the end."""
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "duration_s" and isinstance(v, (int, float)):
                x[k] = min(float(v), left)
            else:
                _cut(v, left)
    elif isinstance(x, list):
        for v in x:
            _cut(v, left)


def main(gen: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, run in SOURCES.items():
        sc = yaml.safe_load((gen / f"{run}.yaml").read_text())
        sc["duration_s"] = DURATION_S
        sc["events"] = [e for e in sc.get("events", []) if float(e.get("at_s", 0)) < DURATION_S - 5]
        for e in sc["events"]:
            _cut(e, DURATION_S - float(e.get("at_s", 0)) - 1.0)
        (out / f"{run}.yaml").write_text(yaml.safe_dump(sc, sort_keys=False))
        print(f"quiclab run -c {gen / (run + '-topology.yaml')} -s {out / (run + '.yaml')} --run-id pinfix-{name}")


if __name__ == "__main__":
    g = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".runs/2026-11-14_1818_v3/_gen")
    o = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".runs/pinfix-scenarios")
    main(g, o)
