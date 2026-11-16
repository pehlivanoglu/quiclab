#!/usr/bin/env python3
"""Suite v3 detector report from rows.jsonl / stimuli.jsonl (score_runs.py). Reps side by side; counts
pooled (summed), never averaged across reps; a cell is flagged (*) when its |r1 - r2| exceeds the
largest |r1 - r2| of the other cells of its block for that metric (>= 2 other cells).

    .venv/bin/python3 reports/v3-detector/summarize.py .runs/2026-11-14_1818_v3 > reports/v3-detector/report.md
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gt_score  # noqa: E402
import gtq_score  # noqa: E402
import v3_suite as v3  # noqa: E402

HERE = Path(__file__).resolve().parent
DETS = ("v2-owd", "v2-fixed-owd", "v2-rtt", "v2-fixed-rtt")
MAIN = "v2-owd"
TRUTHS = ("GT1", "GT2", "GT3")
BLOCK_ORDER = [c.block for c in v3.GATE + v3.CORE + v3.MICRO]


def load():
    rows = [json.loads(x) for x in open(HERE / "rows.jsonl") if x.strip()]
    stim = [json.loads(x) for x in open(HERE / "stimuli.jsonl") if x.strip()]
    return rows, stim


def f(x, k=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x:.{k}f}" if isinstance(x, float) else str(x)


def gsum(rs, truth, det):
    """gt_score pooled metrics + alarm-on recall + hop recall."""
    tal = [r["score"][truth][det] for r in rs]
    m = gt_score.summarize(tal)
    ep = sum(t["episodes"] for t in tal)
    m["alarm_on_recall"] = sum(t.get("alarm_on", 0) for t in tal) / ep if ep else math.nan
    return m


def qsum(rs, det):
    eps = [e for r in rs if r.get("gtq") for e in r["gtq"]["episodes"] if e["detector"] == det]
    tal = [t for r in rs if r.get("gtq") for t in r["gtq"]["tallies"] if t["detector"] == det]
    if not tal:
        return None
    return gtq_score._metrics(eps, tal)


def qboot(rs, det, seed=1):
    by = {}
    for r in rs:
        if r.get("gtq"):
            by[r["run"]] = ([e for e in r["gtq"]["episodes"] if e["detector"] == det],
                            [t for t in r["gtq"]["tallies"] if t["detector"] == det])
    return gtq_score._boot(by, np.random.default_rng(seed)) if by else {}


def border(key):
    b = key[0]
    return (BLOCK_ORDER.index(b) if b in BLOCK_ORDER else 99, key)


def flags(cells: dict, block_of) -> set:
    """cells: key -> (r1, r2). Flag key when |r1 - r2| > max |r1 - r2| of the other cells of the block."""
    out = set()
    by = defaultdict(dict)
    for k, (a, b) in cells.items():
        if a is not None and b is not None and not (math.isnan(a) or math.isnan(b)):
            by[block_of(k)][k] = abs(a - b)
    for blk, dd in by.items():
        for k, v in dd.items():
            others = [x for kk, x in dd.items() if kk != k]
            if len(others) >= 2 and v > max(others) + 1e-12:
                out.add(k)
    return out


def main(argv):
    kdir = Path(argv[0])
    rows, stim = load()
    L = []
    P = L.append
    P("# Suite v3: detector report (frozen Shadow v2)\n")
    P(f"Campaign `{kdir}`: {len(rows)} runs scored (scripts: reports/v3-detector/score_runs.py, summarize.py). "
      "Detectors frozen with the ip4 values (scripts/shadow_v2_frozen.py), nothing refitted on v3. "
      f"Main detector **{MAIN}** (v2, one-way delay from ACK receive timestamps, hold rule, loss gate level+cap, "
      "theta_on 0.25). Truths: GT1, GT2, GT3 (source B), GT-Q, GT-H. Reps side by side; counts pooled.\n")

    # ── 1. overall
    P("## 1. Overall, all runs\n")
    P("### 1a. GT1 / GT2 / GT3 (per client, gt_score)\n")
    P("| truth | detector | episodes | precision | recall (start) | recall (alarm-on) | F1 | FA / min CLEAR | "
      "latency p50 / p90 ms | early alarms | hop-level recall (episodes) |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    for t in TRUTHS:
        for det in DETS:
            m = gsum(rows, t, det)
            hop = f"{f(m['hop_recall'])} ({m['hop_episodes']})" if t != "GT3" else "-"
            P(f"| {t} | {det} | {m['episodes']} | {f(m['precision'])} | {f(m['recall'])} | {f(m['alarm_on_recall'])} | "
              f"{f(m['f1'])} | {f(m['fa_per_min'])} | {f(m['latency_p50_ms'], 0)} / {f(m['latency_p90_ms'], 0)} | "
              f"{f(m['early_share'])} | {hop} |")
    P("")
    P("### 1b. GT-Q / GT-H (per flow, gtq_score; 95 % CI: runs resampled)\n")
    valid = [r for r in rows if r.get("gtq")]
    inval = [r["run"] for r in rows if not r.get("gtq")]
    P(f"GT-Q valid on {len(valid)} of {len(rows)} runs" + (f"; not valid: {inval}" if inval else "") + ".\n")
    P("| detector | GT-Q episodes | precision GT-Q [CI] | recall GT-Q [CI] | recall GT-H 300 / 600 [CI] / 1000 | "
      "strict precision GT-H 600 | FA / flow-hour | L_obs p50 / p95 ms | lead before harm 600 p50 ms | "
      "alarm before harm 600 | GT-H 600 episodes |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    for det in DETS:
        m, ci = qsum(valid, det), qboot(valid, det)
        if m is None:
            continue
        c = lambda k: f"[{ci[k][0]:.2f}, {ci[k][1]:.2f}]" if k in ci else ""   # noqa: E731
        P(f"| {det} | {m['episodes']} | {f(m['precision_gtq'])} {c('precision_gtq')} | {f(m['recall_gtq'])} "
          f"{c('recall_gtq')} | {f(m['recall_gth300'])} / {f(m['recall_gth600'])} {c('recall_gth600')} / "
          f"{f(m['recall_gth1000'])} | {f(m['precision_gth600_strict'])} | {f(m['fa_per_flow_hour'], 1)} | "
          f"{m['L_obs_p50_ms']} / {m['L_obs_p95_ms']} | {m['lead600_p50_ms']} | {f(m['alarm_before_harm'])} | "
          f"{m['gth600_episodes']} |")
    P("")
    P("### 1c. Rep 1 vs rep 2, main detector\n")
    P("| truth | rep | episodes | precision | recall | alarm-on recall | FA / min | latency p50 ms |")
    P("|---|---|---|---|---|---|---|---|")
    for t in TRUTHS:
        for rep in (1, 2):
            m = gsum([r for r in rows if r["rep"] == rep], t, MAIN)
            P(f"| {t} | {rep} | {m['episodes']} | {f(m['precision'])} | {f(m['recall'])} | {f(m['alarm_on_recall'])} | "
              f"{f(m['fa_per_min'])} | {f(m['latency_p50_ms'], 0)} |")
    for rep in (1, 2):
        m = qsum([r for r in valid if r["rep"] == rep], MAIN)
        P(f"| GT-Q / GT-H 600 | {rep} | {m['episodes']} / {m['gth600_episodes']} | {f(m['precision_gtq'])} | "
          f"{f(m['recall_gtq'])} / {f(m['recall_gth600'])} | - | {f(m['fa_per_flow_hour'], 1)} per flow-h | "
          f"{m['L_obs_p50_ms']} |")
    P("")

    # ── 2. per block x variant x AQM
    cellkey = lambda r: (r["block"], r["type"], r["variant"], r["aqm"])   # noqa: E731
    by = defaultdict(lambda: {1: [], 2: []})
    for r in rows:
        by[cellkey(r)][r["rep"]].append(r)
    P(f"## 2. Per cell ({MAIN}): block x scenario x variant x AQM, rep 1 | rep 2\n")
    P("`*` = the two reps disagree by more than the largest rep difference of the other cells of the block "
      "(not reliable without a known cause). FA per minute of CLEAR time. `-` = no episode / no CLEAR time.\n")
    for t in TRUTHS:
        P(f"### 2.{TRUTHS.index(t) + 1} {t}\n")
        P("| block | scenario | variant | AQM | episodes r1 / r2 | precision r1 / r2 | recall r1 / r2 | "
          "alarm-on recall r1 / r2 | FA / min r1 / r2 | latency p50 ms r1 / r2 |")
        P("|---|---|---|---|---|---|---|---|---|---|")
        mets = {k: {rep: gsum(v[rep], t, MAIN) if v[rep] else None for rep in (1, 2)} for k, v in by.items()}
        fl = {}
        for name in ("precision", "recall", "fa_per_min"):
            fl[name] = flags({k: (m[1][name] if m[1] else None, m[2][name] if m[2] else None)
                              for k, m in mets.items()}, lambda k: k[0])
        for k in sorted(mets, key=border):
            a, b = mets[k][1], mets[k][2]
            g = lambda m, n, d=2: f(m[n], d) if m else "-"   # noqa: E731
            star = lambda n: "*" if k in fl.get(n, ()) else ""   # noqa: E731
            P(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {g(a, 'episodes')} / {g(b, 'episodes')} | "
              f"{g(a, 'precision')} / {g(b, 'precision')}{star('precision')} | {g(a, 'recall')} / {g(b, 'recall')}"
              f"{star('recall')} | {g(a, 'alarm_on_recall')} / {g(b, 'alarm_on_recall')} | "
              f"{g(a, 'fa_per_min')} / {g(b, 'fa_per_min')}{star('fa_per_min')} | "
              f"{g(a, 'latency_p50_ms', 0)} / {g(b, 'latency_p50_ms', 0)} |")
        P("")
    P("### 2.4 GT-Q / GT-H\n")
    P("| block | scenario | variant | AQM | GT-Q episodes r1 / r2 | precision GT-Q r1 / r2 | recall GT-Q r1 / r2 | "
      "recall GT-H 600 r1 / r2 (episodes) | FA / flow-hour r1 / r2 | L_obs p50 ms r1 / r2 |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    qm = {k: {rep: qsum([r for r in v[rep] if r.get("gtq")], MAIN) for rep in (1, 2)} for k, v in by.items()}
    qfl = {n: flags({k: (m[1][n] if m[1] else None, m[2][n] if m[2] else None) for k, m in qm.items()},
                    lambda k: k[0]) for n in ("precision_gtq", "recall_gtq", "recall_gth600")}
    for k in sorted(qm, key=border):
        a, b = qm[k][1], qm[k][2]
        g = lambda m, n, d=2: f(m[n], d) if m else "-"   # noqa: E731
        star = lambda n: "*" if k in qfl.get(n, ()) else ""   # noqa: E731
        P(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {g(a, 'episodes')} / {g(b, 'episodes')} | "
          f"{g(a, 'precision_gtq')} / {g(b, 'precision_gtq')}{star('precision_gtq')} | "
          f"{g(a, 'recall_gtq')} / {g(b, 'recall_gtq')}{star('recall_gtq')} | "
          f"{g(a, 'recall_gth600')} / {g(b, 'recall_gth600')}{star('recall_gth600')} "
          f"({g(a, 'gth600_episodes')} / {g(b, 'gth600_episodes')}) | {g(a, 'fa_per_flow_hour', 1)} / "
          f"{g(b, 'fa_per_flow_hour', 1)} | {g(a, 'L_obs_p50_ms', 0)} / {g(b, 'L_obs_p50_ms', 0)} |")
    P("")

    # ── 3. s and U (T-BASE)
    P(f"## 3. Share s and load U on T-BASE ({MAIN})\n")
    P("C1a = CALM (no stimulus: every alarm is a false alarm, so FA / min is the number); "
      "C2 / C3a = S-BURST. Reps pooled per row only in the 'both' column; r1 / r2 shown.\n")
    P("| block | variant (s, U) | AQM | GT1 FA / min r1 / r2 | GT3 FA / min r1 / r2 | GT-Q FA / flow-h r1 / r2 | "
      "GT3 recall r1 / r2 | GT-Q recall r1 / r2 |")
    P("|---|---|---|---|---|---|---|---|")
    for k in sorted(by, key=border):
        if k[0] not in ("C1a", "C2", "C3a", "C3b") or k[1] not in ("calm", "sburst"):
            continue
        g1 = {rep: gsum(by[k][rep], "GT1", MAIN) for rep in (1, 2) if by[k][rep]}
        g3 = {rep: gsum(by[k][rep], "GT3", MAIN) for rep in (1, 2) if by[k][rep]}
        gq = {rep: qsum([r for r in by[k][rep] if r.get("gtq")], MAIN) for rep in (1, 2) if by[k][rep]}
        two = lambda d_, n, dd=2: " / ".join(f(d_[rp][n], dd) if d_.get(rp) else "-" for rp in (1, 2))  # noqa: E731
        P(f"| {k[0]} | {k[2]} | {k[3]} | {two(g1, 'fa_per_min')} | {two(g3, 'fa_per_min')} | "
          f"{two(gq, 'fa_per_flow_hour', 1)} | {two(g3, 'recall')} | {two(gq, 'recall_gtq')} |")
    P("")

    # ── 4. stimulus level
    P(f"## 4. Stimulus level ({MAIN}): share of the expected clients alarming in [start - 1 s, start + 10 s]\n")
    P("Measured loads from v3-stimuli.csv (router ingress of the target, / C_e): total and the video relative to "
      "its calm rate (medians over the windows). Nominal u in the row name.\n")
    sk = defaultdict(lambda: {1: [], 2: []})
    for w in stim:
        if "error" in w or not w.get("clients"):
            continue
        p = w["run"].split("-")
        blk, aqm, rep = p[1], p[4], int(p[5][1:])
        lab = (f"u {w['u_nominal']:g}" if w.get("u_nominal") is not None else w["cell"]) + \
              (f" d {w['d']:g}" if w.get("d") is not None and w["stimulus_type"] in ("surge", "capdrop") else "")
        sk[(blk, w["stimulus_type"], p[3], aqm, lab)][rep].append(w)
    P("| block | stimulus | variant | AQM | cell | windows r1 / r2 | clients alarming r1 / r2 | "
      "total load r1 / r2 | video / calm r1 / r2 |")
    P("|---|---|---|---|---|---|---|---|---|")
    for k in sorted(sk, key=border):
        v = sk[k]
        share = lambda ws: f(sum(x["hit"][MAIN] for x in ws) / sum(x["clients"] for x in ws)) if ws else "-"  # noqa: E731
        med = lambda ws, n: f(float(np.median([x[n] for x in ws if x.get(n) is not None]))) if ws and any(  # noqa: E731
            x.get(n) is not None for x in ws) else "-"
        P(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {k[4]} | {len(v[1])} / {len(v[2])} | {share(v[1])} / {share(v[2])} | "
          f"{med(v[1], 'total_load')} / {med(v[2], 'total_load')} | {med(v[1], 'video_rel_calm')} / "
          f"{med(v[2], 'video_rel_calm')} |")
    P("")

    # ── 5. detector variants per block (GT3 and GT-Q recall / FA)
    P("## 5. All four detector variants per block (reps pooled by summing counts)\n")
    P("| block | GT3 P / R / FA per min: v2-owd | v2-fixed-owd | v2-rtt | v2-fixed-rtt | GT-Q P / R: v2-owd | "
      "v2-fixed-owd | v2-rtt | v2-fixed-rtt |")
    P("|---|---|---|---|---|---|---|---|---|")
    byb = defaultdict(list)
    for r in rows:
        byb[r["block"]].append(r)
    for b in sorted(byb, key=lambda x: BLOCK_ORDER.index(x) if x in BLOCK_ORDER else 99):
        cells3 = []
        for det in DETS:
            m = gsum(byb[b], "GT3", det)
            cells3.append(f"{f(m['precision'])} / {f(m['recall'])} / {f(m['fa_per_min'])}")
        cq = []
        for det in DETS:
            m = qsum([r for r in byb[b] if r.get("gtq")], det)
            cq.append(f"{f(m['precision_gtq'])} / {f(m['recall_gtq'])}" if m else "-")
        P(f"| {b} | " + " | ".join(cells3) + " | " + " | ".join(cq) + " |")
    P("")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
