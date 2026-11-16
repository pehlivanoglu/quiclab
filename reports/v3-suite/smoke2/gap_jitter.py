#!/usr/bin/env python3
"""Smoke 2: absolute size of the backlogged-gap deviations on the T-TREE16 egresses.

    .venv/bin/python3 reports/v3-suite/smoke2/gap_jitter.py .runs/2026-11-14_1801_v3-smoke

Per target egress of the tree16 run: share of backlogged gaps within +-10 % of the previous
packet's serialization time; early (< 0.9) / late (> 1.1) shares; gap - ideal in us at
p0.5 / p1 / p99 / p99.5; the +-10 % band in us; the median ratio of the gap after a late one.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

rd = Path(sys.argv[1]) / "v3-SMOKE-calm-tree16-pfifo-r1"
plan = json.loads((rd / "v3-plan.json").read_text())
cap = {e["hop"]: e["C_e_mbps"] for e in plan["egress"].values()}
print("| hop | C Mb/s | packet time us | +-10 % band us | within 10 % | early / late | gap - ideal us p0.5 / p1 / p99 / p99.5 | gap after a late gap (median ratio) |")
print("|---|---|---|---|---|---|---|---|")
for row in csv.DictReader((rd / "router-trace" / "interfaces.csv").open()):
    if row["hop"] not in cap:
        continue
    C = cap[row["hop"]]
    d = pd.read_csv(rd / "router-trace" / f"{row['iface']}-packets.csv", usecols=["kind", "t_enq_ns", "t_deq_ns", "len"])
    d = d[d.kind == "dequeue"].sort_values("t_deq_ns", kind="stable")
    te, td, ln = (d[c].to_numpy(np.int64) for c in ("t_enq_ns", "t_deq_ns", "len"))
    b = (te[1:] >= 0) & (te[1:] < td[:-1])
    gap, ideal = np.diff(td)[b], 8 * ln[:-1][b] / (C * 1e6) * 1e9
    r, dev = gap / ideal, (gap - ideal) / 1e3
    late = np.flatnonzero(r > 1.1)
    nxt = np.median([r[i + 1] for i in late if i + 1 < len(r)]) if len(late) else float("nan")
    pkt = 1242 * 8 / C
    print(f"| {row['hop']} | {C} | {pkt:.0f} | {pkt / 10:.1f} | {np.mean(abs(r - 1) <= .1):.4f} | {np.mean(r < .9):.4f} / "
          f"{np.mean(r > 1.1):.4f} | {' / '.join(f'{x:.1f}' for x in np.quantile(dev, [.005, .01, .99, .995]))} | {nxt:.3f} |")
