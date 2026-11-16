#!/usr/bin/env python3
"""Pin check of a finished run (2026-11-15 fq_codel fix): every fq_codel egress must carry the catch-all
flow-hash filter onto classes 20:1 .. 20:300, and the per-class router metrics may show backlog only on the
clients' pinned classes (20:301 ..) or on classes <= 20:300, never on a class above 20:300 that is not a client's.

    python3 scripts/fq_pin_check.py .runs/<run> [...]

Needs <run>/qdiscs.txt, <run>/tc-filters.txt (runs from 2026-11-15 on) and router-metrics/*-flows.csv.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BASE = 0x300


def check(rd: Path) -> list[str]:
    bad = []
    fq = set()
    dev = None
    for line in (rd / "qdiscs.txt").read_text().splitlines():
        if line.startswith("=="):
            dev = tuple(line.split()[1:3])
        elif line.startswith("qdisc fq_codel"):
            fq.add(dev)
    if not (rd / "tc-filters.txt").exists():
        return ["no tc-filters.txt (run made before the fix)"]
    filt, dev = {}, None
    for line in (rd / "tc-filters.txt").read_text().splitlines():
        if line.startswith("=="):
            dev = tuple(line.split()[1:3])
            filt[dev] = ""
        else:
            filt[dev] = filt.get(dev, "") + line + "\n"
    for d in sorted(fq):
        f = filt.get(d, "")
        if not ("flow" in f and f"divisor {BASE}" in f and "baseclass 20:1" in f):
            bad.append(f"{d[0]} {d[1]}: catch-all filter missing")
    ids = {}
    p = rd / "router-metrics" / "flow-ids.json"
    if p.exists():
        ids = {int(str(v).split(":")[-1], 16) for v in json.loads(p.read_text()).values()}
    for f in sorted((rd / "router-metrics").rglob("*-flows.csv")):
        rows = list(csv.DictReader(f.open()))
        stray = {r["class"] for r in rows if int(r["class"], 16) > BASE and (ids and int(r["class"], 16) not in ids)
                 and int(r["backlog_bytes"]) > 0}
        if stray:
            bad.append(f"{f.relative_to(rd)}: backlog on non-client classes above 20:{BASE:x}: {sorted(stray)}")
    return bad


if __name__ == "__main__":
    rc = 0
    for a in sys.argv[1:]:
        b = check(Path(a))
        print(f"{Path(a).name}: {'OK' if not b else 'FAIL'}")
        for x in b:
            print("  ", x)
        rc |= bool(b)
    sys.exit(rc)
