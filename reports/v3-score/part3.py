#!/usr/bin/env python3
"""Part 3: detector, from det-rows.jsonl (ppbp.run_row per run: GT1, GT3 source A, frame-latency harm,
v2 / v2-fixed OWD frozen, start / overlap detection, F1 baseline state) and, for 3d, the stimulus windows of
reports/v3-detector/stimuli.jsonl. Reps side by side; `*` = the reps of a cell differ by more than the
largest rep difference of the other cells of its block (>= 2 others): not reliable.

    .venv/bin/python3 reports/v3-score/part3.py > reports/v3-score/part3.md

Definitions (as ppbp.py): overlap recall = an alarm span overlaps the episode; start recall = gt_score's
rule; long = episodes >= 2 s (P: gt_score bins); harmful = a missed playout deadline in [t_on, t_end + 2 s]
(P: shadow_v2_step0); precision = tp / (tp + fp) (gt_score); CALM false alarms per client-minute = fp /
(clients x minutes after warm-up), clients = the instrumented ones (sub-ctrl included, as ppbp.run_row).
State: above = learned baseline (running minimum + mu_F1) above the run's queue-free OWD, sigma_F1, and
sens = the sustained F1 level for an alarm within 1 s (ms above the queue-free delay); medians over the
clients (M).
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DETS = ("v2", "v2-fixed")
rows = [json.loads(x) for x in open(HERE / "det-rows.jsonl") if x.strip() and '"error"' not in x[:80]]
plans = {}
for r in rows:
    p = json.loads((ROOT / ".runs/2026-11-14_1818_v3" / r["run"] / "v3-plan.json").read_text())
    r["s"], r["U"], r["bg"], r["block"], r["rep"] = p["s"], p["U"], p["bg_mode"], p["block"], p["rep"]
    r["cell"] = r["run"].rsplit("-r", 1)[0][3:]
ORDER = [f"G{i}" for i in (1, 2, 3)] + ["C1a", "C1b"] + [f"C{i}" for i in range(2, 16)] + [f"M{i}" for i in range(1, 15)]
ORDER = ORDER[:5] + ["C2", "C3a", "C3b"] + [f"C{i}" for i in range(4, 16)] + [f"M{i}" for i in range(1, 15)]
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731


def ep_metrics(rs, truth, det):
    eps = [e for r in rs for e in r["episodes"] if e["truth"] == truth]
    def rec(sel, key):
        return sum(e[f"{det}_{key}"] for e in sel) / len(sel) if sel else math.nan
    long = [e for e in eps if e["dur"] >= 2.0]
    harm = [e for e in eps if e["harm"]]
    sc = [r[f"score_{truth.lower()}"][det] for r in rs]
    tp, fp = sum(x["tp"] for x in sc), sum(x["fp"] for x in sc)
    return {"n": len(eps), "overlap": rec(eps, "overlap"), "start": rec(eps, "start"), "long_n": len(long),
            "long": rec(long, "overlap"), "harm_n": len(harm), "harm": rec(harm, "overlap"),
            "precision": tp / (tp + fp) if tp + fp else math.nan, "fp": fp,
            "fa_cm": fp / sum(r["clients"] * r["minutes"] for r in rs) if rs else math.nan}


cells = defaultdict(lambda: {1: [], 2: []})
for r in rows:
    cells[r["cell"]][r["rep"]].append(r)
border = lambda c: (ORDER.index(c.split("-")[0]) if c.split("-")[0] in ORDER else 99, c)   # noqa: E731


def flags(vals):
    by = defaultdict(dict)
    for c, (a, b) in vals.items():
        if not (math.isnan(a) or math.isnan(b)):
            by[c.split("-")[0]][c] = abs(a - b)
    out = set()
    for blk, dd in by.items():
        for c, v in dd.items():
            o = [x for k, x in dd.items() if k != c]
            if len(o) >= 2 and v > max(o) + 1e-12:
                out.add(c)
    return out


print("# Part 3: detector (frozen Shadow v2 on OWD; GT1 and GT3 source A as ppbp.py builds them)\n")
for truth in ("GT3", "GT1"):
    print(f"## 3a / 3c. {truth} per cell: v2 | v2-fixed, rep 1 / rep 2\n")
    print("| cell | s | U | bg | episodes r1 / r2 | overlap R v2 | overlap R fixed | R >= 2 s v2 | R >= 2 s fixed | "
          "R harmful v2 (n) | R harmful fixed | precision v2 | precision fixed | FA / client-min v2 | FA / client-min fixed |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    M = {c: {rep: {det: ep_metrics(v[rep], truth, det) for det in DETS} for rep in (1, 2) if v[rep]} for c, v in cells.items()}
    fl = {}
    for det in DETS:
        for k in ("overlap", "precision", "fa_cm"):
            fl[(det, k)] = flags({c: (m[1][det][k], m[2][det][k]) for c, m in M.items() if 1 in m and 2 in m})
    for c in sorted(M, key=border):
        m = M[c]
        r0 = (cells[c][1] or cells[c][2])[0]
        two = lambda det, k, d=2: " / ".join(f(m[rp][det][k], d) if rp in m else "-" for rp in (1, 2)) + (  # noqa: E731
            "*" if c in fl.get((det, k), ()) else "")
        print(f"| {c} | {r0['s'] if r0['s'] is not None else 'legacy'} | {r0['U']} | {r0['bg']} | "
              f"{' / '.join(str(m[rp]['v2']['n']) if rp in m else '-' for rp in (1, 2))} | {two('v2', 'overlap')} | "
              f"{two('v2-fixed', 'overlap')} | {two('v2', 'long')} | {two('v2-fixed', 'long')} | {two('v2', 'harm')} "
              f"({' / '.join(str(m[rp]['v2']['harm_n']) if rp in m else '-' for rp in (1, 2))}) | {two('v2-fixed', 'harm')} | "
              f"{two('v2', 'precision')} | {two('v2-fixed', 'precision')} | {two('v2', 'fa_cm', 3)} | {two('v2-fixed', 'fa_cm', 3)} |")
    print()

print("## 3b. Learned calm baseline and sigma of F1 (OWD) and the sustained queue needed for an alarm in 1 s\n")
print("Medians over the cell's clients (excluding sub-ctrl), per rep. above = baseline above the queue-free delay (ms); "
      "sigma_F1 (ms); sens = F1 level above the queue-free delay that alarms within 1 s through F1 alone (ms).\n")
print("| cell | s | U | bg | v2 above r1 / r2 | v2 sigma r1 / r2 | v2 sens 1 s r1 / r2 | fixed above | fixed sigma | fixed sens 1 s r1 / r2 |")
print("|---|---|---|---|---|---|---|---|---|---|")
for c in sorted(cells, key=border):
    if not c.startswith(("C1a", "C1b", "C2-", "C3a", "C3b", "M3", "M4", "M6", "C7", "C9", "C11", "C8", "G1")):
        continue
    v = cells[c]
    r0 = (v[1] or v[2])[0]
    def st(rep, det, key, sub=None):
        xs = []
        for r in v[rep]:
            for k, s in r["state"].items():
                d_, cl = k.split("|")
                if d_ == det and cl != "sub-ctrl" and s.get(key) is not None:
                    xs.append(s[key][sub] if sub else s[key])
        return f(float(np.median(xs)), 1) if xs else "-"
    two = lambda det, key, sub=None: " / ".join(st(rp, det, key, sub) for rp in (1, 2))   # noqa: E731
    print(f"| {c} | {r0['s'] if r0['s'] is not None else 'legacy'} | {r0['U']} | {r0['bg']} | {two('v2', 'above_p50')} | "
          f"{two('v2', 'sig_p50')} | {two('v2', 'sens_ms', '1.0')} | {two('v2-fixed', 'above_p50')} | {two('v2-fixed', 'sig_p50')} | "
          f"{two('v2-fixed', 'sens_ms', '1.0')} |")
print()

# 3d by stimulus (stimulus windows: share of expected clients alarming in [start - 1 s, start + 10 s])
print("## 3d. By stimulus: share of the expected clients alarming in [start - 1 s, start + 10 s], v2-owd | v2-fixed-owd\n")
stim = [json.loads(x) for x in open(ROOT / "reports/v3-detector/stimuli.jsonl") if x.strip()]
g = defaultdict(lambda: {1: [], 2: []})
for w in stim:
    if "error" in w or not w.get("clients"):
        continue
    p = w["run"].split("-")
    blk, var, aqm, rep = p[1], p[3], p[4], int(p[5][1:])
    st_ = w["stimulus_type"]
    if blk in ("C2", "M3", "C4", "C5", "C6", "M2", "C12"):
        lab = f"u {w['u_nominal']:g}" if w.get("u_nominal") is not None else w["cell"].split(" d=")[0]
        g[(blk, st_, var, aqm, lab)][rep].append(w)
print("| block | stimulus | variant (bg) | AQM | cell | windows r1 / r2 | v2-owd r1 / r2 | v2-fixed-owd r1 / r2 | video / calm median |")
print("|---|---|---|---|---|---|---|---|---|")
sh = lambda ws, d: f(sum(x["hit"][d] for x in ws) / sum(x["clients"] for x in ws)) if ws else "-"   # noqa: E731
for k in sorted(g, key=lambda k: (["C2", "M3", "C4", "C5", "C6", "M2", "C12"].index(k[0]), k[2], k[3], k[1], k[4])):
    v = g[k]
    vr = [x["video_rel_calm"] for x in v[1] + v[2] if x.get("video_rel_calm") is not None]
    print(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {k[4]} | {len(v[1])} / {len(v[2])} | {sh(v[1], 'v2-owd')} / {sh(v[2], 'v2-owd')} | "
          f"{sh(v[1], 'v2-fixed-owd')} / {sh(v[2], 'v2-fixed-owd')} | {f(float(np.median(vr))) if vr else '-'} |")
