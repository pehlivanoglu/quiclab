#!/usr/bin/env python3
"""Part 1: v3 catalog (the catalog script reads only the old campaign folders, so its calm_load function is
called per v3 run instead: calm-load.jsonl), stimulus-window loads (v3-stimuli.csv), keyframe table (part2.md),
health summary and rep 1 vs rep 2 (the campaign's run-checks.md / rep-compare.md, copied).

    .venv/bin/python3 reports/v3-score/part1.py .runs/2026-11-14_1818_v3 > reports/v3-score/catalog-v3.md
"""
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import v3_stimuli  # noqa: E402

kdir = Path(sys.argv[1])
for name in ("run-checks.md", "rep-compare.md", "video-reaction.md", "gate-report.md"):
    shutil.copy(kdir / name, HERE / name)
print("# Scenario catalog, suite v3 (measured)\n")
print("Topologies, sizing, stimuli and the campaign matrix: reports/v3-suite/README.md and `scripts/v3_suite.py "
      "--plan-only` (per-egress C_e / BG_e table). This file adds the measured values.\n")
print("## 5. Measured calm load and video share per router egress (scenario_catalog.calm_load), rep 1 / rep 2\n")
print("| cell | egress | load r1 / r2 | video share r1 / r2 (QUIC bytes / router bytes) |\n|---|---|---|---|")
rows = defaultdict(dict)
for x in open(HERE / "calm-load.jsonl"):
    r = json.loads(x)
    if "egress" not in r:
        continue
    rows[r["run"].rsplit("-r", 1)[0]][int(r["run"].rsplit("-r", 1)[1])] = r["egress"]
for cell in sorted(rows):
    reps = rows[cell]
    hops = sorted({h for v in reps.values() for h in v if not h.split("->")[1].startswith(("rx-", "tx-"))})
    for h in hops:
        g = lambda k: " / ".join(str(reps[rp].get(h, {}).get(k, "-")) if rp in reps else "-" for rp in (1, 2))  # noqa: E731
        print(f"| {cell[3:]} | {h} | {g('load')} | {g('video_share')} |")
print("\n## 5b. Inside stimulus windows (v3-stimuli.csv, medians over the windows; loads / C_e at the target's ingress)\n")
print("| block | stimulus | u | windows | non-video | video | total | video / calm |\n|---|---|---|---|---|---|---|---|")
agg = defaultdict(list)
for rd in sorted(p for p in kdir.iterdir() if p.is_dir() and p.name.startswith("v3-")):
    for w in v3_stimuli.load(rd):
        agg[(rd.name.split("-")[1], w["stimulus_type"], w["u_nominal"])].append(w)
md = lambda ws, k: f"{np.median([w[k] for w in ws if w[k] is not None]):.3f}" if any(w[k] is not None for w in ws) else "-"  # noqa: E731
for k in sorted(agg, key=lambda k: (k[0][0], int(''.join(c for c in k[0] if c.isdigit()) or 0), str(k[1]), k[2] or 0)):
    ws = agg[k]
    print(f"| {k[0]} | {k[1]} | {k[2] if k[2] is not None else '-'} | {len(ws)} | {md(ws, 'nonvideo_load')} | "
          f"{md(ws, 'video_load')} | {md(ws, 'total_load')} | {md(ws, 'video_rel_calm')} |")
