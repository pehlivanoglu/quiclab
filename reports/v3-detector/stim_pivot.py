#!/usr/bin/env python3
"""Stimulus-level pivots (main detector): share of expected clients alarming in [start - 1 s, start + 10 s].

    .venv/bin/python3 reports/v3-detector/stim_pivot.py > reports/v3-detector/stim-pivot.md
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import summarize as S  # noqa: E402

_, stim = S.load()
W = [w for w in stim if "error" not in w and w.get("clients")]
for w in W:
    p = w["run"].split("-")
    w["block"], w["variant"], w["aqm"], w["rep"] = p[1], p[3], p[4], int(p[5][1:])


def share(ws, det=S.MAIN):
    return sum(x["hit"][det] for x in ws) / sum(x["clients"] for x in ws) if ws else float("nan")


def med(ws, k):
    v = [x[k] for x in ws if x.get(k) is not None]
    return float(np.median(v)) if v else float("nan")


print("# Stimulus-level detection (share of expected clients alarming), main detector v2-owd\n")
print("## C2 S-BURST (T-BASE default, BG-CBR surge): by AQM x u x d, r1 / r2; measured total load and video / calm (median)\n")
print("| AQM | u | d s | clients alarming r1 / r2 | total load | video / calm |")
print("|---|---|---|---|---|---|")
c2 = defaultdict(lambda: {1: [], 2: []})
for w in W:
    if w["block"] == "C2" and w["stimulus_type"] == "surge":
        c2[(w["aqm"], w["u_nominal"], w["d"])][w["rep"]].append(w)
for k in sorted(c2):
    v = c2[k]
    allw = v[1] + v[2]
    print(f"| {k[0]} | {k[1]:g} | {k[2]:g} | {S.f(share(v[1]))} / {S.f(share(v[2]))} | {S.f(med(allw, 'total_load'))} | "
          f"{S.f(med(allw, 'video_rel_calm'))} |")
print("\n## Every stimulus type, every block: by AQM (reps pooled), main and the other three detectors\n")
print("| block | stimulus | variant | AQM | windows | v2-owd | v2-fixed-owd | v2-rtt | v2-fixed-rtt | total load | video / calm |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
g = defaultdict(list)
for w in W:
    g[(w["block"], w["stimulus_type"], w["variant"], w["aqm"])].append(w)
for k in sorted(g, key=S.border):
    ws = g[k]
    print(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {len(ws)} | " + " | ".join(S.f(share(ws, d)) for d in S.DETS)
          + f" | {S.f(med(ws, 'total_load'))} | {S.f(med(ws, 'video_rel_calm'))} |")
print("\n## Hierarchies: by target level (H-HIER / H-DEPTH / H-INDEP / H-UNEVEN / L-LONG, all AQMs pooled per AQM)\n")
print("| block | AQM | target | windows | clients alarming | video / calm |")
print("|---|---|---|---|---|---|")
h = defaultdict(list)
for w in W:
    if w["block"] in ("C7", "C8", "C9", "C10", "C11", "C13", "M7", "M8"):
        h[(w["block"], w["aqm"], w["target"])].append(w)
for k in sorted(h, key=S.border):
    print(f"| {k[0]} | {k[1]} | {k[2]} | {len(h[k])} | {S.f(share(h[k]))} | {S.f(med(h[k], 'video_rel_calm'))} |")
