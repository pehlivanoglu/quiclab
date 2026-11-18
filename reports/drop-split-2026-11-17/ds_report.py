"""Tables for the pre-drop / post-drop split (ds.py rows.jsonl). Reps side by side (r1 / r2)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

SINGLE = ("pfifo", "codel", "pie", "red")
FQ = ("fq_codel", "cake")
CATS = ("all", "nodrop", "pre", "post")
CAT_NAME = {"all": "all windows", "nodrop": "windows with no drop", "pre": "drop windows, before t_drop",
            "post": "drop windows, after t_drop"}
DETS = ("v2-owd", "D2-gcc", "D3-10ms-200ms")


def load(path: Path):
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    return [r for r in R if "error" not in r], [r for r in R if "error" in r]


def f_(x, d=2):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def share_table(R, key, title):
    print(f"| {title} | windows r1 / r2 | no drop r1 / r2 |\n|---|---|---|")
    groups = defaultdict(lambda: {1: [0, 0], 2: [0, 0]})
    for r in R:
        for w in r["windows"]:
            k = key(r, w)
            groups[k][r["rep"]][0] += 1
            groups[k][r["rep"]][1] += w["t_drop"] is None
    for k in sorted(groups, key=str):
        g = groups[k]
        print(f"| {k} | {g[1][0]} / {g[2][0]} | " +
              " / ".join(f_(g[rep][1] / g[rep][0]) if g[rep][0] else "-" for rep in (1, 2)) + " |")
    print()


def det_agg(rows, cat, det):
    tp = fp = ep = 0
    clear = 0.0
    lat = []
    gm = gf = hh = hn = 0
    for r in rows:
        s = r["score"][cat][det]
        tp, fp, ep, clear = tp + s["tp"], fp + s["fp"], ep + s["episodes"], clear + s["clear_s"]
        lat += s["latency"]
        if r["gtq"]:
            m, f = r["gtq"][cat][det]
            gm, gf = gm + m, gf + f
        h = r["harm"][cat][det]
        hh, hn = hh + h[0], hn + h[1]
    q = lambda p: float(np.percentile(lat, p)) * 1000 if lat else None   # noqa: E731
    return {"P": tp / (tp + fp) if tp + fp else None, "R": tp / ep if ep else None,
            "fa": fp / (clear / 60) if clear else None, "p50": q(50), "p90": q(90),
            "gq": gm / (gm + gf) if gm + gf else None, "harm": hh / hn if hn else None, "ep": ep, "hn": hn,
            "ga": gm + gf}


def det_table(R, sel, title):
    print(f"#### {title}\n")
    print("| window part | detector | GT-Q P | on at t_harm (n) | GT3 P | GT3 R | FA / min | delay p50 ms | p90 ms | "
          "GT3 episodes |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for cat in CATS:
        for det in DETS:
            v = [det_agg([r for r in R if sel(r) and r["rep"] == rep], cat, det) for rep in (1, 2)]
            cell = lambda k, d=2: " / ".join(f_(x[k], d) for x in v)   # noqa: E731
            print(f"| {CAT_NAME[cat]} | {det} | {cell('gq')} | {cell('harm')} ({v[0]['hn']} / {v[1]['hn']}) | "
                  f"{cell('P')} | {cell('R')} | {cell('fa')} | {cell('p50', 0)} | {cell('p90', 0)} | "
                  f"{v[0]['ep']} / {v[1]['ep']} |")
    print()


def grp_agg(rows, cat, k):
    ss = [r["grouping"]["methods"][f"{cat} k{k}"] for r in rows if r.get("grouping")]
    n_close = sum(r["grouping"]["closes"][cat] for r in rows if r.get("grouping"))
    if not ss:
        return None
    p = np.sum([s["pairs"] for s in ss], axis=0)
    leaf = [s["levels"]["leaf"] for s in ss if "leaf" in s["levels"] and not np.isnan(s["levels"]["leaf"][2])]
    return {"pP": p[0] / (p[0] + p[1]) if p[0] + p[1] else None, "pR": p[0] / (p[0] + p[2]) if p[0] + p[2] else None,
            "F": float(np.mean([x[2] for x in leaf])) if leaf else None, "runs": len(leaf), "closes": n_close,
            "pairs": int(p[0] + p[1])}


def grp_table(R, sel, title):
    print(f"#### {title}\n")
    print("| window part | k | pair P | pair R | leaf F1 (mean over runs) | runs with closes | event closes | "
          "grouped pairs judged |")
    print("|---|---|---|---|---|---|---|---|")
    for cat in CATS:
        for k in (2, 3):
            v = [grp_agg([r for r in R if sel(r) and r["rep"] == rep], cat, k) for rep in (1, 2)]
            if not any(v):
                continue
            cell = lambda key, d=3: " / ".join(f_(x[key], d) if x else "-" for x in v)   # noqa: E731
            ints = lambda key: " / ".join(str(x[key]) if x else "0" for x in v)   # noqa: E731
            print(f"| {CAT_NAME[cat]} | {k} | {cell('pP')} | {cell('pR')} | {cell('F')} | {ints('runs')} | "
                  f"{ints('closes')} | {ints('pairs')} |")
    print()


def nodrop_runs(R, sel, title):
    rs = [r for r in R if sel(r) and r.get("grouping") and r["windows"] and all(w["t_drop"] is None for w in r["windows"])]
    print(f"#### {title}: runs with no drop in any window ({len(rs)} runs: "
          f"{', '.join(sorted(r['run'][3:] for r in rs)) or 'none'})\n")
    if not rs:
        print("No such runs.\n")
        return
    print("| k | pair P r1 / r2 | pair R | leaf F1 | closes |\n|---|---|---|---|---|")
    for k in (2, 3):
        v = [grp_agg([r for r in rs if r["rep"] == rep], "all", k) for rep in (1, 2)]
        cell = lambda key, d=3: " / ".join(f_(x[key], d) if x else "-" for x in v)   # noqa: E731
        print(f"| {k} | {cell('pP')} | {cell('pR')} | {cell('F')} | " +
              " / ".join(str(x["closes"]) if x else "0" for x in v) + " |")
    print()


def before_drop(R, sel, title):
    """First alarm start per drop window before t_drop; SETS onsets in drop windows before t_drop."""
    print(f"#### {title}\n")
    print("| rep | drop windows | with a first v2-owd alarm | alarm before t_drop | t_drop - first alarm p50 / p10 s | "
          "SETS onsets in drop windows | before t_drop | in no-drop windows |")
    print("|---|---|---|---|---|---|---|---|")
    for rep in (1, 2):
        rows = [r for r in R if sel(r) and r["rep"] == rep]
        dw = [w for r in rows for w in r["windows"] if w["t_drop"] is not None]
        fa = [w for w in dw if w["first_alarm"] is not None]
        bef = [w for w in fa if w["first_alarm"] < w["t_drop"]]
        gap = [w["t_drop"] - w["first_alarm"] for w in fa]
        on = defaultdict(int)
        for r in rows:
            if r.get("grouping"):
                for c, n in r["grouping"]["onsets"].items():
                    on[c] += n
        tot = on["pre"] + on["post"]
        print(f"| r{rep} | {len(dw)} | {len(fa)} | {f_(len(bef) / len(fa) if fa else None)} | "
              f"{f_(float(np.median(gap)) if gap else None)} / {f_(float(np.percentile(gap, 10)) if gap else None)} | "
              f"{tot} | {f_(on['pre'] / tot if tot else None)} | {on['nodrop']} |")
    print()


def report(path: Path) -> None:
    R, bad = load(path)
    print("# Drop-split tables (ds_report.py)\n")
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    stim = lambda r: r["type"] != "calm" and r["windows"]   # noqa: E731
    print("## Windows with no sender drop\n")
    share_table([r for r in R if stim(r)], lambda r, w: r["block"], "block")
    share_table([r for r in R if stim(r)], lambda r, w: r["aqm"], "AQM")
    share_table([r for r in R if stim(r)], lambda r, w: f"u {w['u']}" if w.get("u") is not None else "u -", "intensity u")
    share_table([r for r in R if stim(r)], lambda r, w: f"d {w['d']} s" if w.get("d") is not None else "d -",
                "duration d")
    share_table([r for r in R if stim(r)], lambda r, w: r["variant"], "operating point (variant)")
    share_table([r for r in R if stim(r)], lambda r, w: r["cc"], "CC")
    print("## Alarms and onsets before the first drop\n")
    sq = lambda r: stim(r) and r["aqm"] in SINGLE   # noqa: E731
    fq = lambda r: stim(r) and r["aqm"] in FQ   # noqa: E731
    before_drop(R, sq, "Single-queue AQM runs")
    before_drop(R, fq, "fq_codel / cake runs")
    print("## Detector, three ways (plus the part after t_drop)\n")
    det_table(R, lambda r: sq(r) and r["block"].startswith("C"), "Single-queue AQM cells (C blocks)")
    det_table(R, lambda r: fq(r) and r["block"].startswith("C"), "fq_codel / cake (C blocks)")
    det_table(R, lambda r: stim(r) and r["block"].startswith("M"), "Microbenchmarks (M blocks)")
    print("## Grouping (frozen SETS, common scorer), by the window part of the event close\n")
    grp_table(R, sq, "Single-queue AQM runs")
    grp_table(R, fq, "fq_codel / cake runs (same-link truth)")
    nodrop_runs(R, sq, "Single-queue AQM")
    nodrop_runs(R, fq, "fq_codel / cake")
