#!/usr/bin/env python3
"""Before / after tables for a B2 re-run set (user 2026-11-19: U1 CoDel recorder fix, fixed random streams).

    python3 simulation/simlab/b2_compare_sets.py <old report dir> <old runs dir prefix> <new report dir> \
        <new runs dir prefix> <run filter, e.g. codel> > out.md

Reads rows-{matched,spec}.jsonl of both report folders (stageb_compare output) and the run folders' tracer-counts.csv.
Prints: (1) per egress enq / deq / drop and the residual enq - deq - drop, before and after; (2) the light check's
run-wide packet balance (unacknowledged video + lost background - drops) before and after; (3) every simulation-side
measured value of the filtered runs, before and after, marked "*" where it moved; (4) every agreement verdict of the
tables-{ack}.md that changed.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def rows(rep: Path, ack: str) -> dict:
    return {r["name"]: r for r in map(json.loads, (rep / f"rows-{ack}.jsonl").read_text().splitlines())}


def flat(d, pre=""):
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            out.update(flat(v, f"{pre}{k}."))
        elif not isinstance(v, list):
            out[pre + k] = v
    return out


def same(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def fmt(v):
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def verdicts(rep: Path, ack: str) -> dict:
    out, metric = {}, None
    for ln in (rep / f"tables-{ack}.md").read_text().splitlines():
        if ln.startswith("### "):
            metric = ln[4:].split(" (")[0]
        elif ln.startswith("| sim-") and metric:
            c = [x.strip() for x in ln.strip("|").split("|")]
            out[(metric, c[0])] = (c[1], c[2], c[-1])
    return out


def counts(rd: Path) -> dict:
    p = rd / "router-trace" / "tracer-counts.csv"
    return {r["iface"]: (int(r["n_enq"]), int(r["n_deq"]), int(r["n_drop"])) for r in csv.DictReader(p.open())} \
        if p.exists() else {}


def main(argv: list[str]) -> None:
    old_rep, old_runs, new_rep, new_runs, filt = Path(argv[0]), argv[1], Path(argv[2]), argv[3], argv[4]
    import health_lite as hl
    for ack in ("matched", "spec"):
        o, n = rows(old_rep, ack), rows(new_rep, ack)
        names = [x for x in o if filt in x]
        od, nd = Path(f"{old_runs}{ack}"), Path(f"{new_runs}{ack}")
        print(f"\n## {ack}: {len(names)} runs matching '{filt}'\n")
        print("### Packet identity per egress (tracer counts): enq / deq / drop, residual enq - deq - drop\n")
        print("| run | egress | before | residual before | after | residual after |")
        print("|---|---|---|---|---|---|")
        for x in names:
            co, cn = counts(od / x), counts(nd / x)
            for i in sorted(co):
                a, b = co[i], cn.get(i, (0, 0, 0))
                print(f"| {x} | {i} | {a[0]} / {a[1]} / {a[2]} | {a[0] - a[1] - a[2]} | {b[0]} / {b[1]} / {b[2]} | "
                      f"{b[0] - b[1] - b[2]} |")
        print("\n### Run-wide packet balance (light check item 4: unacked video + lost background - drops)\n")
        print("| run | before: balance / drops | after: balance / drops |")
        print("|---|---|---|")
        for x in names:
            bo, bn = hl.item_sender(od / x), hl.item_sender(nd / x)
            print(f"| {x} | {bo['balance']} / {bo['drops']} | {bn['balance']} / {bn['drops']} |")
        print("\n### Simulation-side values that moved (all others identical)\n")
        print("| run | value | before | after |")
        print("|---|---|---|---|")
        moved = 0
        for x in names:
            fo, fn = flat(o[x]["sim"]), flat(n[x]["sim"])
            for k in sorted(set(fo) | set(fn)):
                if not same(fo.get(k), fn.get(k)):
                    moved += 1
                    print(f"| {x} | {k} | {fmt(fo.get(k))} | {fmt(fn.get(k))} * |")
        if not moved:
            print("| (none) | | | |")
        print("\n### Agreement verdicts that changed (tables-%s.md)\n" % ack)
        vo, vn = verdicts(old_rep, ack), verdicts(new_rep, ack)
        ch = [(k, vo[k], vn.get(k)) for k in vo if filt in k[1] and vo[k] != vn.get(k)]
        print("| metric | run | before: testbed / sim / verdict | after |")
        print("|---|---|---|---|")
        for (m, x), a, b in ch:
            print(f"| {m} | {x} | {' / '.join(a)} | {' / '.join(b) if b else '-'}{' *' if b and a[2] != b[2] else ''} |")
        if not ch:
            print("| (none) | | | |")


if __name__ == "__main__":
    main(sys.argv[1:])
