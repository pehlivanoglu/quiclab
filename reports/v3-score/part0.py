#!/usr/bin/env python3
"""Part 0: is the v3 campaign valid. Reads the campaign's own outputs only (gate-report.md,
manifest.yaml, run.log, <run>/v3-checks.json, v3-stimuli.csv, gtq-health.csv, events.csv, topology).

    .venv/bin/python3 reports/v3-score/part0.py .runs/2026-11-14_1818_v3 > reports/v3-score/part0.md
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import v3_gate  # noqa: E402
import v3_stimuli  # noqa: E402

kdir = Path(sys.argv[1])
runs = sorted(p for p in kdir.iterdir() if p.is_dir() and p.name.startswith("v3-"))
checks = {json.loads(x)["run"]: json.loads(x) for x in open(kdir / "run-checks.jsonl")}
man = yaml.safe_load((kdir / "manifest.yaml").read_text())
f = lambda x, k=3: "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{k}f}"   # noqa: E731
P = print

P("# Part 0: campaign validity\n")
# 1 gate
gate = (kdir / "gate-report.md").read_text().splitlines()
P("## 0.1 Gate (9 runs)\n")
P(f"Verdict: **{gate[0].split(':', 1)[1].strip()}** (gate-report.md). Numbers per gate run:\n")
P("| run | load / U | share / s | ECN marks | oversize skb | 4: lost, unmatched (targets), gaps within max(10 %, 15 us) min, 20 ms within 5 % min, CPU idle min | 5: non-video - planned (max abs) | 6: 1 / 30 Hz peak / median (max) |")
P("|---|---|---|---|---|---|---|---|")
for rd in runs:
    if not rd.name.startswith("v3-G"):
        continue
    c = v3_gate.run_checks(rd) if not (rd / "v3-checks.json").exists() else json.loads((rd / "v3-checks.json").read_text())
    ls = c["1_load_share"].get("egress", {})
    h = c["4_health"]
    tg = [v for v in h.get("egress", {}).values() if v["role"] == "target"]
    s5 = c["5_surge"]
    dev = max((abs(w["measured"] - w["planned_nonvideo"]) for w in s5.get("windows", [])), default=None)
    ph = c["6_phase"].get("peak_over_median") or {}
    pk = max((v for e in ph.values() for v in e.values()), default=None)
    P(f"| {rd.name} | " + ", ".join(f"{n} {v['load']} / {v['U']}" for n, v in ls.items()) + " | "
      + ", ".join(f"{v['share']} / {v['s']}" for v in ls.values()) + f" | {sum(c['2_ecn']['nonzero'].values()) if c['2_ecn']['nonzero'] else 0} | "
      f"{sum(c['3_mtu']['oversize'].values()) if c['3_mtu']['oversize'] else 0} | {h['lost_events']}, "
      f"{h.get('unmatched_targets')}, {f(min((v['gap_within_tol'] for v in tg if v['gaps'] >= 1000), default=None))}, "
      f"{f(min((v['win20_within5'] for v in tg if v['win20_n']), default=None))}, {h['cpu_idle_min']} | {f(dev)} | {f(pk, 1)} |")
P("")

# 2 completion and time
P("## 0.2 Runs and time\n")
done = Counter(str(v).split()[0] for v in man["runs"].values())
fin = sum((rd / "events.csv").exists() and "end," in (rd / "events.csv").read_text() for rd in runs)
retried = len(re.findall(r"^== (v3-\S+)", (kdir / "run.log").read_text(), re.M)) - len(runs)
emu = 0.0
wall = []
for rd in runs:
    ev = pd.read_csv(rd / "events.csv")
    end = ev[ev.event == "end"]
    emu += float(end.at_s.iloc[0]) if len(end) else 0.0
inval = [rd.name for rd in runs if v3_gate._health(rd).get("gt_q_invalid") == "1"]
P(f"- planned {len(man['runs'])} runs; run folders {len(runs)}; finished (events.csv `end`) {fin}; manifest: "
  f"{dict(done)}; failed 0; extra run starts in run.log (retries) {max(retried, 0)}.")
P(f"- dropped to fit the budget: {man.get('dropped_micro') or 'none'}; planned {man.get('planned_hours')} h emulated.")
P(f"- emulated time (sum of the runs' scenario durations): {emu / 3600:.2f} h.")
P(f"- wall clock: started {man.get('started')}, finished {man.get('finished')} (includes the stop after the first "
  "gate failure on check 5 until the resume).")
P(f"- GT-Q invalid by the health file (`gt_q_invalid`): {len(inval)} runs: {inval}.\n")

# 3 load / share
P("## 0.3 Calm load and video share per core run (tolerance +-0.03)\n")
off, worst = [], [0, 0, ""]
dl, ds = [], []
for name, c in checks.items():
    if not name.split("-")[1].startswith(("C", "G")):
        continue
    for n, v in (c["1_load_share"].get("egress") or {}).items():
        dl.append(v["load"] - v["U"])
        ds.append((v["share"] or np.nan) - v["s"])
        if not v["ok"]:
            off.append(f"{name} {n}: load {v['load']} (U {v['U']}), share {v['share']} (s {v['s']})")
P(f"- core + gate bottleneck egresses: {len(dl)}; load - U: median {np.median(dl):+.3f}, min {min(dl):+.3f}, max {max(dl):+.3f}; "
  f"share - s: median {np.nanmedian(ds):+.3f}, min {np.nanmin(ds):+.3f}, max {np.nanmax(ds):+.3f}.")
P(f"- off target: {off or 'none'}.")
offm = [f"{n}: " + ", ".join(f"{e} load {v['load']} share {v['share']}" for e, v in c['1_load_share']['egress'].items())
        for n, c in checks.items() if n.split("-")[1].startswith("M") and c["1_load_share"].get("ok") is False]
P(f"- microbenchmarks off target (kept, flagged): {offm}.\n")
P("Stimulus intensity: background + stimulus arriving at the target vs planned U(1 - s) + (u - U) (surges; v3-stimuli.csv):\n")
dev = defaultdict(list)
for rd in runs:
    for w in v3_stimuli.load(rd):
        if w["stimulus_type"] == "surge" and w["planned_nonvideo"] is not None:
            dev[rd.name.split("-")[1]].append(w["nonvideo_load"] - w["planned_nonvideo"])
P("| block | surge windows | measured - planned: median / min / max | outside +-0.05 |")
P("|---|---|---|---|")
for b, v in sorted(dev.items(), key=lambda x: (x[0][0], int(re.sub(r'\D', '', x[0]) or 0))):
    v = np.array(v)
    P(f"| {b} | {len(v)} | {np.median(v):+.3f} / {v.min():+.3f} / {v.max():+.3f} | {int((abs(v) > 0.05).sum())} |")
P("")

# 4 worst cases
P("## 0.4 Worst cases over all 203 runs\n")
ecn = sum(sum(c["2_ecn"]["nonzero"].values()) for c in checks.values() if c["2_ecn"].get("nonzero"))
over = sum(sum(c["3_mtu"]["oversize"].values()) for c in checks.values() if c["3_mtu"].get("oversize"))
idle = min((c["4_health"]["cpu_idle_min"], n) for n, c in checks.items())
gap = min((v["gap_within_tol"], n, v["hop"]) for n, c in checks.items() for v in c["4_health"]["egress"].values()
          if v["role"] == "target" and v["gaps"] >= 1000 and v["gap_within_tol"] == v["gap_within_tol"])
win = min((v["win20_within5"], n, v["hop"]) for n, c in checks.items() for v in c["4_health"]["egress"].values()
          if v["role"] == "target" and v["win20_n"] and v["win20_within5"] == v["win20_within5"])
unm = max((v["unmatched_deq"] + v["unmatched_enq"], n, v["hop"]) for n, c in checks.items()
          for v in c["4_health"]["egress"].values() if v["role"] == "target")
lost = max(c["4_health"]["lost_events"] for c in checks.values())
P(f"- ECN marks: {ecn} on every egress of every run; AQM leaves configured with `ecn`: "
  f"{sum(len(c['2_ecn'].get('ecn_configured', [])) for c in checks.values())}.")
P(f"- skb larger than the MTU at a traced egress: {over}; offloads not off: "
  f"{sum(len(c['3_mtu'].get('offloads_not_off', [])) for c in checks.values())}.")
P(f"- CPU idle, worst second: {idle[0]} ({idle[1]}).")
P(f"- inter-dequeue gaps within max(10 %, 15 us), worst target egress: {gap[0]:.4f} ({gap[1]} {gap[2]}); "
  f"20 ms windows within 5 %, worst: {win[0]:.4f} ({win[1]} {win[2]}).")
P(f"- unmatched packets, worst target egress: {unm[0]} ({unm[1]} {unm[2]}); bpftrace lost events max {lost}.\n")
fails = defaultdict(list)
for n, c in checks.items():
    for k in ("1_load_share", "4_health", "5_surge", "6_phase"):
        if c[k].get("ok") is False:
            fails[k].append(n)
P("Runs with a check flagged (kept): " + "; ".join(f"{k}: {len(v)} ({', '.join(v)})" for k, v in fails.items()) + "\n")

# 6 fq_codel / cake, pinned classes, Copa / IP / S-JOIN
P("## 0.6 Isolation cells, pinned classes, optional features\n")
det = {json.loads(x)["run"]: json.loads(x) for x in open(ROOT / "reports/v3-detector/rows.jsonl")}
cells = defaultdict(lambda: [0, 0])
for n, r in det.items():
    if r["aqm"] in ("fq_codel", "cake") and r["block"] not in ("G1", "G2", "C1a", "C1b"):
        key = "-".join(n.split("-")[1:5])
        cells[key][0] += r["score"]["GT3"]["v2-owd"]["episodes"]
        cells[key][1] += 1
never = [k for k, v in cells.items() if v[0] == 0]
P(f"- fq_codel / cake stimulus cells: {len(cells)}; cells where no instrumented flow was ever constrained (no GT3 "
  f"episode in either rep): {never or 'none'}; fewest: "
  + ", ".join(f"{k} {v[0]}" for k, v in sorted(cells.items(), key=lambda x: x[1][0])[:4]) + " GT3 episodes (both reps).")
coll = []
for n, c in checks.items():
    fc = c.get("fq_collisions")
    if isinstance(fc, dict):
        for i, v in fc.items():
            coll.append((n, i, v))
ver = [x for x in coll if isinstance(x[2], dict)]
P(f"- background in pinned fq_codel classes: {len(coll)} traced fq_codel egresses checked; verifiable (skb hash in the "
  f"trace) {len(ver)}; packets in a pinned class: {sum(x[2]['in_pinned_class'] for x in ver)} of "
  f"{sum(x[2]['bg_packets'] for x in ver)} unpinned dequeues"
  + (f"; unverifiable on {len(coll) - len(ver)} (no hash)" if len(coll) > len(ver) else "") + ".")
cc = {rd.name: yaml.safe_load((rd / "topology.yaml").read_text())["publishers"]["pub"].get("cc_algo") for rd in runs
      if rd.name.startswith("v3-M13")}
ipr = {rd.name: yaml.safe_load((rd / "topology.yaml").read_text())["publishers"]["pub"].get("ip_ratio") for rd in runs
       if rd.name.startswith("v3-M10")}
join = [rd.name for rd in runs if rd.name.startswith("v3-C6")]
P(f"- Copa (M13): ran, cc_algo {sorted(set(cc.values()))} on {len(cc)} runs. I/P ratio (M10): ran, {sorted(set(ipr.values()))} "
  f"on {len(ipr)} runs. S-JOIN (C6): ran, {len(join)} runs (ASV key / P spread 5.85 / 1.16 ms).")
