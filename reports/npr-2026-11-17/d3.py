#!/usr/bin/env python3
"""D3: spread of alarm onsets within one leaf in one stimulus, against the detector's delay.

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/d3.py rows [--jobs 2]
    .venv/bin/python3 reports/npr-2026-11-17/d3.py report

Onsets: the frozen v2-owd onset log (grouping_adapter.build via r1.onsets_at, frozen tick files; K1 ticks from the
STEP 0 cache, nothing written in run folders). Per stimulus window (grouping/windows.json) and per true leaf that the
window congests (the window's target is the leaf or a set containing it): each member's first onset with
t_onset in [start - 1 s, end + 2 s]; spread = max - min over the members with an onset (n >= 2), on the aligned time
t_al = t_onset - mrtt / 2 (what the event formation uses) and on t_onset. RTT spread = max - min of the members'
mrtt (onset log meta). The detector's delay: v2-owd GT3 TP latencies from reports/detector-r2-2026-11-16/rows.jsonl.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "scripts"), str(ROOT), str(ROOT / "reports/sets-low-threshold-2026-11-16"),
                str(ROOT / "reports/npr-step0-2026-11-17")]
ROWS = HERE / "d3-rows.jsonl"


def worker(rd: Path) -> dict:
    try:
        import det_eval as d
        import grouping_score as gs
        import npr0
        import r1
        npr0._patch_tick_files()
        plan = json.loads((rd / "v3-plan.json").read_text())
        run = d.Run(rd)
        cfg, records, onsets = r1.onsets_at(rd, r1.LEVELS["T100"])
        mrtt = {o.flow: o.mrtt for k, _, o in records if k == "meta"}
        ts = gs.truth_sets(rd, run, plan)
        T = {n: set(v["members"]) for n, v in ts.items()}
        leaves = [n for n, v in ts.items() if v["level"] == "leaf"]
        wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
        by = defaultdict(list)
        for o in onsets:
            by[o["flow"]].append(o["t_onset"])
        out = []
        for w in wins:
            tgt = w.get("target")
            if tgt not in T:
                continue
            lo, hi = w["start"] - 1.0, w["end"] + 2.0
            for n in leaves:
                if not T[n] <= T[tgt]:
                    continue
                first = {c: min((t for t in by.get(c, []) if lo <= t <= hi), default=None) for c in T[n]}
                got = {c: t for c, t in first.items() if t is not None}
                if len(got) < 2:
                    continue
                al = [t - mrtt.get(c, 0.0) / 2 for c, t in got.items()]
                rt = [mrtt.get(c, 0.0) for c in T[n]]
                out.append({"leaf": n, "size": len(T[n]), "n_onset": len(got), "spread_al": max(al) - min(al),
                            "spread_raw": max(got.values()) - min(got.values()), "rtt_spread": max(rt) - min(rt),
                            "u": w.get("u"), "d": w.get("d"), "stim": w.get("stimulus_type")})
        return {"run": rd.name, "aqm": plan["aqm"], "rep": plan["rep"], "block": plan["block"], "spreads": out}
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2000:]}


def cmd_rows(jobs):
    import npr0
    rs = npr0.runs()
    with ROWS.open("w") as fh, Pool(jobs) as pool:
        for i, r in enumerate(pool.imap_unordered(worker, rs), 1):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {r['run']}{' ERROR ' + r['error'] if 'error' in r else ''}", flush=True)


def q(a, p):
    return float(np.percentile(a, p)) * 1000 if len(a) else float("nan")


def report():
    R = [json.loads(x) for x in ROWS.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    fq = ("fq_codel", "cake")
    print("# D3: onset spread within a leaf in one stimulus (ms)\n")
    if bad:
        print(f"Errors: {[(b['run'], b['error']) for b in bad]}\n")
    S = [(r, s) for r in R for s in r["spreads"]]
    print("| cells | key | leaf-stimuli | spread (aligned) p50 / p90 / p95 / p99 | spread (raw onset) p50 / p90 / p99 | "
          "share <= 0.5 s / 1 s / 2 s |")
    print("|---|---|---|---|---|---|")

    def row(label, key, xs):
        a = np.array([s["spread_al"] for s in xs])
        b = np.array([s["spread_raw"] for s in xs])
        if not len(a):
            return
        print(f"| {label} | {key} | {len(a)} | {q(a, 50):.0f} / {q(a, 90):.0f} / {q(a, 95):.0f} / {q(a, 99):.0f} | "
              f"{q(b, 50):.0f} / {q(b, 90):.0f} / {q(b, 99):.0f} | {np.mean(a <= 0.5):.3f} / {np.mean(a <= 1):.3f} / "
              f"{np.mean(a <= 2):.3f} |")
    for cls, sel in (("single-queue", lambda r: r["aqm"] not in fq), ("fq_codel / cake", lambda r: r["aqm"] in fq)):
        xs = [s for r, s in S if sel(r)]
        for rep in (1, 2):
            row(cls, f"all, r{rep}", [s for r, s in S if sel(r) and r["rep"] == rep])
        if cls != "single-queue":
            continue
        for a in ("pfifo", "codel", "pie", "red"):
            row(cls, f"AQM {a}", [s for r, s in S if r["aqm"] == a])
        for size in sorted({s["size"] for s in xs}):
            row(cls, f"leaf size {size}", [s for s in xs if s["size"] == size])
        for lo, hi in ((0, 0.0105), (0.0105, 0.0305), (0.0305, 1)):
            row(cls, f"RTT spread {lo * 1000:.0f}-{hi * 1000:.0f} ms", [s for s in xs if lo <= s["rtt_spread"] < hi])
        for u in (1.05, 1.15, 1.3):
            row(cls, f"intensity u {u}", [s for s in xs if s["u"] == u])
    print()
    lat = []
    for line in open(ROOT / "reports/detector-r2-2026-11-16/rows.jsonl"):
        r = json.loads(line)
        if "error" in r or r["aqm"] in fq or not r["block"].startswith("C") or r["type"] == "calm":
            continue
        lat += r["score"]["GT3"]["v2-owd"].get("latency", [])
    lat = np.array(lat)
    print(f"Detector delay (v2-owd, GT3 TP latency, single-queue C blocks, both reps, R2): p50 {q(lat, 50):.0f}, p90 "
          f"{q(lat, 90):.0f}, p95 {q(lat, 95):.0f}, p99 {q(lat, 99):.0f} ms; p90 - p10 {q(lat, 90) - q(lat, 10):.0f} ms.\n")


def main(argv):
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2)
    else:
        report()


if __name__ == "__main__":
    main(sys.argv[1:])
