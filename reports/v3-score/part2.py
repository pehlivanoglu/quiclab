#!/usr/bin/env python3
"""Part 2: keyframe queue. Per run and bottleneck egress (calm time; v3_gate.keyframe_peaks: queue
delay = 5 ms tc backlog / C_e in the 200 ms after each keyframe, p50 / p90 / max of the per-keyframe
peaks) next to 0.121 s U (P: I/P 4, 30 fps, 1 s GOP: keyframe = 4/33 of the GOP bytes; 0.121 s x s U x C_e
of video arrives at once) and next to that minus the measured pacing spread of a keyframe (median over
the egress's clients of the keyframe emission time, v3-emission.json; M). Reps side by side.
Then the share of ECG events (v2-owd onsets) in which an upstream / root egress is congested by the gt1
rule (step7 a_row hot_share_gen), per topology and s.

    .venv/bin/python3 reports/v3-score/part2.py .runs/2026-11-14_1818_v3 > reports/v3-score/part2.md
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

kdir = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
rows = defaultdict(dict)
for rd in sorted(p for p in kdir.iterdir() if p.is_dir() and p.name.startswith("v3-")):
    c = json.loads((rd / "v3-checks.json").read_text())
    plan = json.loads((rd / "v3-plan.json").read_text())
    em = json.loads((rd / "v3-emission.json").read_text()) if (rd / "v3-emission.json").exists() else {}
    rep = int(rd.name.rsplit("-r", 1)[1])
    cell = rd.name.rsplit("-r", 1)[0]
    for name, k in (c.get("keyframe_peaks") or {}).items():
        e = plan["egress"][name]
        spread = [em[s]["key_ms_p50"] for s in e["clients"] if s in em and em[s].get("key_ms_p50") is not None]
        ref = 121 * plan["s"] * plan["U"] if plan["s"] is not None else 121 * 1.0 * plan["U"]   # legacy: s = 1
        sp = float(np.median(spread)) if spread else np.nan
        rows[(cell, name)][rep] = {"hop": e["hop"], "s": plan["s"], "U": plan["U"], "p50": k["p50"], "p90": k["p90"],
                                   "max": k["max"], "ref": round(ref, 1), "spread": round(sp, 1),
                                   "ref_minus": round(ref - sp, 1)}


def level(cell, name):
    b = cell.split("-")[1]
    if name in ("root",):
        return "root"
    if name in ("up", "X", "Y"):
        return "upstream"
    return "leaf / single"


def show(sel, title):
    print(f"### {title}\n")
    print("| cell | egress (level) | s | U | 0.121 s U ms | minus keyframe pacing spread ms (spread) | peak p50 r1 / r2 | p90 r1 / r2 | max r1 / r2 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (cell, name) in sel:
        v = rows[(cell, name)]
        a = v.get(1) or v.get(2)
        g = lambda k: " / ".join(str(v[r][k]) if r in v else "-" for r in (1, 2))   # noqa: E731
        print(f"| {cell[3:]} | {name} ({level(cell, name)}) | {a['s'] if a['s'] is not None else 'legacy'} | {a['U']} | {a['ref']} | "
              f"{a['ref_minus']} ({g('spread')}) | {g('p50')} | {g('p90')} | {g('max')} |")
    print()


print("# Part 2: keyframe queue\n")
keys = sorted(rows)
show([k for k in keys if k[0].startswith("v3-C1a-")], "T-BASE CALM, every s and U (C1a)")
show([k for k in keys if k[0].startswith("v3-C1b-")], "Hierarchies CALM, per level (C1b)")
show([k for k in keys if k[0].startswith(("v3-C7-", "v3-C8-", "v3-C9-", "v3-C11-")) and "-pfifo" in k[0]],
     "Hierarchies with stimuli, calm time only, pfifo (C7 s 0.30, C8 s 0.65, C9, C11)")
show([k for k in keys if k[0].startswith(("v3-M6-", "v3-M7-", "v3-C2-sburst-s030u070-pfifo", "v3-C3a-"))],
     "Staggered phases (M6), noroot (M7), the default point (C2 pfifo) and s 0.10 / 0.65 (C3a)")

# ECG events with an upstream / root egress congested
grp = HERE / "grp-rows.jsonl"
if grp.exists():
    print("## ECG events (v2-owd onsets) with an upstream / root egress congested (gt1 rule: a GT1 episode of the "
          "egress overlaps [t0 - 1 s, t0 + 2 s])\n")
    print("| cell | s | egress | share of ECG events r1 / r2 | ECG events r1 / r2 | leaf egresses, share r1 / r2 |")
    print("|---|---|---|---|---|---|")
    G = defaultdict(dict)
    for x in open(grp):
        r = json.loads(x)
        if r.get("source") != "v2-owd" or "error" in r.get("a", {"error": 1}):
            continue
        a = r["a"]
        G[r["run"].rsplit("-r", 1)[0]][a["rep"]] = a
    for cell in sorted(G):
        reps = G[cell]
        a0 = reps.get(1) or reps.get(2)
        plan = json.loads((kdir / f"{cell}-r{a0['rep']}" / "v3-plan.json").read_text())
        ups = [e["hop"] for n, e in plan["egress"].items() if n in ("up", "root", "X", "Y") and e["shaped"]]
        if cell.split("-")[1] == "C12":
            ups = [plan["egress"]["main"]["hop"]]   # upstream of the access egresses
        leafs = a0["leaf_hops"]
        for h in ups:
            share = " / ".join(str(reps[r]["ecg"]["hot_share_gen"].get(h, "-")) if r in reps else "-" for r in (1, 2))
            nev = " / ".join(str(reps[r]["ecg"]["events"]) if r in reps else "-" for r in (1, 2))
            lf = " / ".join(", ".join(f"{x} {reps[r]['ecg']['hot_share_gen'].get(x, '-')}" for x in leafs) if r in reps else "-"
                            for r in (1, 2))
            print(f"| {cell[3:]} | {plan['s']} | {h} | {share} | {nev} | {lf} |")
