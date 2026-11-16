#!/usr/bin/env python3
"""Per traced egress of a smoke / gate folder: check-4 inputs from <run>/v3-checks.json.

    .venv/bin/python3 reports/v3-suite/smoke1/health_table.py .runs/<ts>_v3-smoke > reports/v3-suite/smoke1/health.md
"""
import csv
import json
import sys
from pathlib import Path

kdir = Path(sys.argv[1])
print(f"# Check 4 per traced egress: {kdir.name}\n")
print("| run | hop | unmatched deq (ratio) | unmatched enq (ratio) | max per 200 ms deq / enq | gaps within 10 % | "
      "gap p99 | 20 ms windows within 5 % (n) | ok |")
print("|---|---|---|---|---|---|---|---|---|")
for rd in sorted(p for p in kdir.iterdir() if (p / "v3-checks.json").exists()):
    r = json.loads((rd / "v3-checks.json").read_text())["4_health"]
    hops = {x["iface"]: x["hop"] for x in csv.DictReader((rd / "router-trace" / "interfaces.csv").open())}
    for i, v in r["egress"].items():
        print(f"| {rd.name} | {hops.get(i, i)} | {v['unmatched_deq']} ({v['unmatched_deq_ratio']}) | {v['unmatched_enq']} "
              f"({v['unmatched_enq_ratio']}) | {v['unmatched_deq_max_200ms']} / {v['unmatched_enq_max_200ms']} | "
              f"{v['gap_within10']:.4f} | {v['gap_p99']} | {v['win20_within5']} ({v['win20_n']}) | {'ok' if v['ok'] else 'FAIL'} |")
    print(f"| {rd.name} | recursion_misses per tracer {sorted(set(r['recursion_misses'].values()))}, unmatched total "
          f"{r['unmatched_total']}, cpu idle min {r['cpu_idle_min']} | | | | | | | |")
