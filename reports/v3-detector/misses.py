#!/usr/bin/env python3
"""Where the main detector misses: (1) H-INDEP / other blocks, stimulus windows split into concurrent
(overlapping another target's window within 1 s) and not; (2) GT-H 600 harmful episodes missed, by AQM and
by the resource (egress) of the GT-Q episode, with their duration.

    .venv/bin/python3 reports/v3-detector/misses.py > reports/v3-detector/misses.md
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import summarize as S  # noqa: E402

rows, stim = S.load()
kdir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
print("# Where v2-owd misses\n")
print("## 1. Stimulus windows: concurrent vs alone (share of expected clients alarming)\n")
conc = {}
for r in rows:
    pass
win_conc = {}
for w in stim:
    if "error" in w or not w.get("clients"):
        continue
    p = w["run"].split("-")
    key = (p[1], p[4])
    rd = (kdir / w["run"]) if kdir else None
    win_conc.setdefault(w["run"], None)
cache = {}
agg = defaultdict(lambda: [0, 0, 0, 0])
for w in stim:
    if "error" in w or not w.get("clients") or kdir is None:
        continue
    if w["run"] not in cache:
        cache[w["run"]] = json.loads((kdir / w["run"] / "grouping" / "windows.json").read_text())
    ws = cache[w["run"]]
    m = next((x for x in ws if abs(x["start"] - w["start"]) < 1e-6 and x["target"] == w["target"]), {})
    p = w["run"].split("-")
    k = (p[1], p[4])
    i = 0 if not m.get("concurrent") else 2
    agg[k][i] += w["hit"][S.MAIN]
    agg[k][i + 1] += w["clients"]
print("| block | AQM | alone: clients alarming (n) | concurrent: clients alarming (n) |")
print("|---|---|---|---|")
for k in sorted(agg, key=S.border):
    a = agg[k]
    if a[3] == 0:
        continue
    print(f"| {k[0]} | {k[1]} | {S.f(a[0] / a[1]) if a[1] else '-'} ({a[1]}) | {S.f(a[2] / a[3])} ({a[3]}) |")
print("\n## 2. GT-H 600 harmful episodes: hit / missed by AQM and resource\n")
by = defaultdict(lambda: [0, 0, []])
for r in rows:
    if not r.get("gtq"):
        continue
    for e in r["gtq"]["episodes"]:
        if e["detector"] != S.MAIN or str(e["harmful_600"]) != "1":
            continue
        k = (r["aqm"], e["resource"].split("->")[0] if e["resource"].startswith("pub") else
             ("sub-ctrl egress" if e["resource"].endswith("sub-ctrl") else "bottleneck / access egress"))
        by[k][0] += 1
        by[k][1] += int(e["hit"])
        if not int(e["hit"]):
            by[k][2].append(float(e["t1"]) - float(e["t0"]))
print("| AQM | resource | harmful episodes | detected | missed: duration p50 / p90 s |")
print("|---|---|---|---|---|")
for k in sorted(by):
    n, h, d = by[k]
    q = (f"{np.median(d):.2f} / {np.percentile(d, 90):.2f}" if d else "-")
    print(f"| {k[0]} | {k[1]} | {n} | {S.f(h / n)} | {q} |")
