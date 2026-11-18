"""R2 tables from rows.jsonl. GT3 (source B) headline as reports/v3-detector: P = TP / (TP + FP), R = TP / episodes,
alarm-on R, false alarms per minute of CLEAR time, latency p50 / p90 over the pooled TP latencies; GT-Q precision =
matched / (matched + fp) (gray ignored); on at t_harm = harmful GT-H 600 episodes whose t_harm an alarm span
covers. Reps side by side (r1 / r2)."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SINGLE = ("pfifo", "codel", "pie", "red")
FQ = ("fq_codel", "cake")
MAIN = ("v2-owd", "D1-bw", "D1-pacing", "D1-cwnd", "D2-gcc", "D2-gcc-frame", "D2-v1-gcc-floor500",
        "D2-v1-gcc-floor350", "D2-v1-gcc-floor200", "D2-v1-gcc-floor0", "D4-rfc8382", "D4-rfc8382-noloss", "D5-v1")
ABL = ("v2-owd", "abl:ref", "abl:F1-only", "abl:F2-only", "abl:F3-only", "abl:L-only", "abl:no-F2", "abl:no-F3",
       "abl:no-loss", "abl:no-gate", "abl:no-hold", "abl:no-masks")
TYPE = {"sburst": "surge", "sramp": "ramp", "stcp": "tcp", "sjoin": "join", "hhier": "surge", "hdepth": "surge",
        "hindep": "surge", "huneven": "surge", "llong": "surge", "amixed": "surge+capdrop", "rrev": "reverse",
        "nloss": "loss", "sstress": "surge", "ssparse": "surge", "calm": "calm"}


def load(path: Path):
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    return [r for r in R if "error" not in r], [r for r in R if "error" in r]


def agg(rows, det, truth="GT3"):
    tp = fp = ep = on = 0
    clear = 0.0
    lat = []
    gm = gf = 0
    hh = hn = 0
    for r in rows:
        s = r["score"][truth].get(det)
        if not s:
            continue
        tp, fp, ep, on = tp + s["tp"], fp + s["fp"], ep + s["episodes"], on + s.get("alarm_on", 0)
        clear += s["clear_s"]
        lat += s.get("latency", [])
        for t in (r.get("gtq") or []):
            if t["detector"] == det:
                gm, gf = gm + t["alarms_matched"], gf + t["fp"]
        h = (r.get("harm") or {}).get(det)
        if h:
            hh, hn = hh + h[0], hn + h[1]
    q = lambda p: float(np.percentile(lat, p)) * 1000 if lat else None   # noqa: E731
    return {"P": tp / (tp + fp) if tp + fp else None, "R": tp / ep if ep else None, "on": on / ep if ep else None,
            "fa": fp / (clear / 60) if clear else None, "p50": q(50), "p90": q(90),
            "gq": gm / (gm + gf) if gm + gf else None, "harm": hh / hn if hn else None, "ep": ep}


def f_(x, d=2):
    return "-" if x is None else f"{x:.{d}f}"


def table(R, sel, dets, title):
    print(f"### {title}\n")
    print("| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for det in dets:
        v = [agg([r for r in R if sel(r) and r["rep"] == rep], det) for rep in (1, 2)]
        print(f"| {det} | " + " | ".join(" / ".join(f_(x[k], 0 if k in ("p50", "p90") else 2) for x in v)
                                      for k in ("P", "R", "on", "fa", "p50", "p90", "gq", "harm")) +
              f" | {v[0]['ep']} / {v[1]['ep']} |")
    print()


def d3_grid(R, sel):
    print("### D3 simple thresholds on F1 (single-queue cells): full grid (r1 / r2)\n")
    print("| X ms | Y ms | GT3 P | GT3 R | FA / min | delay p50 | p90 | F1 (pooled) |")
    print("|---|---|---|---|---|---|---|---|")
    best = None
    for X in (5, 10, 20):
        for Y in (100, 200, 500):
            det = f"D3-{X}ms-{Y}ms"
            v = [agg([r for r in R if sel(r) and r["rep"] == rep], det) for rep in (1, 2)]
            allv = agg([r for r in R if sel(r)], det)
            f1 = 2 * allv["P"] * allv["R"] / (allv["P"] + allv["R"]) if allv["P"] and allv["R"] else 0.0
            if best is None or f1 > best[1]:
                best = (det, f1)
            print(f"| {X} | {Y} | " + " | ".join(" / ".join(f_(x[k], 0 if k in ("p50", "p90") else 2) for x in v)
                                                for k in ("P", "R", "fa", "p50", "p90")) + f" | {f1:.3f} |")
    print(f"\nBest cell for the baseline (highest pooled GT3 F1, deliberately generous): **{best[0]}** ({best[1]:.3f}).\n")
    return best[0]


def by_type(R, dets):
    print("### Delay by stimulus type and AQM, pooled reps (p50 ms; GT3 R in brackets)\n")
    types = sorted({TYPE.get(r["type"], r["type"]) for r in R})
    aqms = [a for a in (*SINGLE, *FQ) if any(r["aqm"] == a for r in R)]
    print("| type | AQM | " + " | ".join(dets) + " |")
    print("|---|---|" + "---|" * len(dets))
    for ty in types:
        if ty in ("calm", "loss", "reverse"):
            continue
        for a in aqms:
            rs = [r for r in R if TYPE.get(r["type"], r["type"]) == ty and r["aqm"] == a and r["block"].startswith("C")]
            if not rs:
                continue
            cells = []
            for det in dets:
                x = agg(rs, det)
                cells.append(f"{f_(x['p50'], 0)} ({f_(x['R'])})")
            print(f"| {ty} | {a} | " + " | ".join(cells) + " |")
    print()


def contrib(R):
    print("## Per-signal contribution (frozen v2-owd)\n")
    print("Share of G at alarm start from each signal (mean over alarm starts; G summed over the excursion since G "
          "was last 0, ticks where the hold rule zeroed a negative step excluded; loss = the gated loss term). "
          "First signal to reach z >= 1 after a GT3 onset (within 300 ticks), and its median lead over the next one "
          "(ticks of 33 ms).\n")
    groups = defaultdict(list)
    for r in R:
        if r["block"].startswith("G"):
            continue
        key_aqm = r["aqm"]
        key_cc = r["cc"]
        for s, c in r["contrib"].items():
            if s == "sub-ctrl":
                continue
            for k in ((key_cc, key_aqm, "all"), (key_cc, "all", TYPE.get(r["type"], r["type"]))):
                groups[k].append(c)
    print("| CC | AQM | stimulus | alarms | F1 | F2 | F3 | loss | onsets | first: F1 | F2 | F3 | L | none | lead of first, ticks p50 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sorted(groups):
        cs = groups[k]
        al = [a for c in cs for a in c["alarms"] if a["G"]]
        sh = {f: (float(np.mean([a[f] for a in al if a[f] is not None])) if al else None) for f in ("F1", "F2", "F3", "loss")}
        first, leads = Counter(), []
        ons = [o for c in cs for o in c["onsets"]]
        for o in ons:
            ft = {f: v for f, v in o["first_tick"].items() if v is not None}
            if not ft:
                first["none"] += 1
                continue
            order = sorted(ft.items(), key=lambda z: z[1])
            first[order[0][0]] += 1
            if len(order) > 1:
                leads.append(order[1][1] - order[0][1])
        n = len(ons) or 1
        print(f"| {k[0]} | {k[1]} | {k[2]} | {len(al)} | " + " | ".join(f_(sh[f]) for f in ("F1", "F2", "F3", "loss")) +
              f" | {len(ons)} | " + " | ".join(f"{first[f] / n:.2f}" for f in ("F1", "F2", "F3", "L", "none")) +
              f" | {f_(float(np.median(leads)) if leads else None, 1)} |")
    print()


def report(path: Path) -> None:
    R, bad = load(path)
    print("# R2 tables (r2_report.py)\n")
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    core = lambda r: r["block"].startswith("C") and r["type"] != "calm"   # noqa: E731
    print("## Baselines\n")
    table(R, lambda r: core(r) and r["aqm"] in SINGLE, MAIN, "Single-queue AQM cells (C blocks: pfifo, codel, pie, red)")
    for a in SINGLE:
        table(R, lambda r, a=a: core(r) and r["aqm"] == a, MAIN, f"{a} (C blocks)")
    table(R, lambda r: core(r) and r["aqm"] in FQ, MAIN, "Per-flow-queue AQM cells (fq_codel, cake; detector truth = own sub-queue)")
    table(R, lambda r: r["block"].startswith("M") and r["type"] != "calm", MAIN, "Microbenchmarks (M blocks)")
    best = d3_grid(R, lambda r: core(r) and r["aqm"] in SINGLE)
    table(R, lambda r: core(r) and r["aqm"] in SINGLE, ("v2-owd", best), "Frozen detector next to the best D3 cell")
    by_type(R, ("v2-owd", "D1-bw", "D2-gcc", "D2-v1-gcc-floor0", "D5-v1"))
    print("## Ablation of the frozen detector (one change each; G_ref refitted per variant)\n")
    g = json.loads((path.parent / "gref.json").read_text())
    print("G_ref (refit on v3 calm pfifo-r1 s030u070 / s065u070): " +
          ", ".join(f"{k} {v['g_ref']:.1f}" for k, v in g.items()) + "; frozen v2-owd 67.7 (ip4 fit).\n")
    table(R, lambda r: core(r) and r["aqm"] in SINGLE, ABL, "Single-queue AQM cells")
    table(R, lambda r: core(r) and r["aqm"] in FQ, ABL, "fq_codel / cake")
    table(R, lambda r: r["block"] == "C15", ("v2-owd", "abl:ref", "abl:no-gate", "abl:no-loss", "abl:L-only"),
          "Random loss (C15): loss-gate ablation (no GT3 episodes expected; FA / min is the result)")
    table(R, lambda r: r["block"].startswith("M") and r["type"] != "calm", ABL, "Microbenchmarks")
    calm = lambda r: r["type"] == "calm"   # noqa: E731
    print("### Calm runs: false alarms per minute (GT3 CLEAR time)\n")
    print("| detector | FA / min r1 / r2 |\n|---|---|")
    for det in (*MAIN, *ABL[1:]):
        v = [agg([r for r in R if calm(r) and r["rep"] == rep], det) for rep in (1, 2)]
        print(f"| {det} | {f_(v[0]['fa'])} / {f_(v[1]['fa'])} |")
    print()
    contrib(R)
