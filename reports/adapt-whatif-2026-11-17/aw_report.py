"""Tables for the CC-driven adaptation what-if (aw.py rows.jsonl). Reps side by side where it matters."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

X = (0.7, 0.85, 1.0)
TYPE = {"sburst": "surge", "sramp": "ramp", "stcp": "tcp", "sjoin": "join", "hhier": "surge", "hdepth": "surge",
        "hindep": "surge", "huneven": "surge", "llong": "surge", "amixed": "surge+capdrop", "rrev": "reverse",
        "nloss": "loss", "sstress": "surge", "ssparse": "surge"}
LADDER = (0.5, 1.0, 2.5, 5.0, 8.0, 12.0)


def rate_class(bps: float) -> float:
    return min(LADDER, key=lambda r: abs(r - bps / 1e6))


def f_(x, d=2):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def report(path: Path) -> None:
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    print("# Adaptation what-if tables (aw_report.py)\n")
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    # 1. calm ratio
    print("## Calm time: estimate / nominal (median over clients of each client's p5 / p50 / p95)\n")
    print("Calm runs (C1a / C1b) for BBR; Copa from the M13 runs' calm stretches. Phase swing = max / min of the "
          "per-100-ms-bin medians across the GOP, divided by the client's p50.\n")
    print("| CC | operating point | rate Mb/s | clients | p5 | p50 | p95 | phase swing min / max | calm min |")
    print("|---|---|---|---|---|---|---|---|---|")
    g = defaultdict(list)
    for r in R:
        if not (r["calm"] or r["block"] == "M13"):
            continue
        for s, c in r["clients"].items():
            if "ratio_p" in c:
                g[(c["cc"], r["variant"] if r["calm"] else "M13 calm stretches", rate_class(c["nominal_bps"]))].append(c)
    for k in sorted(g, key=str):
        cs = g[k]
        p = np.median([c["ratio_p"] for c in cs], axis=0)
        sw = [(min(x for x in c["phase_median"] if x is not None) / c["ratio_p"][1],
               max(x for x in c["phase_median"] if x is not None) / c["ratio_p"][1])
              for c in cs if c.get("phase_median") and any(x is not None for x in c["phase_median"])]
        swm = np.median(sw, axis=0) if sw else (None, None)
        print(f"| {k[0]} | {k[1]} | {k[2]} | {len(cs)} | {f_(p[0])} | {f_(p[1])} | {f_(p[2])} | "
              f"{f_(swm[0])} / {f_(swm[1])} | {sum(c['calm_s'] for c in cs) / 60:.0f} |")
    print()
    # 2. false cuts
    print("## False cuts in calm time: entries into the cut state per client-minute, and share of calm time cut\n")
    print("| CC | rate Mb/s | calm client-min | " + " | ".join(f"x {x}: cuts / min, time share" for x in X) + " |")
    print("|---|---|---|" + "---|" * len(X))
    g = defaultdict(list)
    for r in R:
        if not (r["calm"] or r["block"] == "M13"):
            continue
        for s, c in r["clients"].items():
            if "ratio_p" in c:
                g[(c["cc"], rate_class(c["nominal_bps"]))].append(c)
    for k in sorted(g):
        cs = g[k]
        m = sum(c["calm_s"] for c in cs) / 60
        cells = []
        for x in X:
            n = sum(c[f"cuts_{x}"] for c in cs)
            sh = sum(c[f"cut_share_{x}"] * c["calm_s"] for c in cs) / max(sum(c["calm_s"] for c in cs), 1e-9)
            cells.append(f"{n / m:.2f}, {sh:.2f}" if m else "-")
        print(f"| {k[0]} | {k[1]} | {m:.0f} | " + " | ".join(cells) + " |")
    print()
    # 3. onsets
    ons = [(r, o) for r in R if not r["calm"] for o in r["onsets"]]
    print("## After a GT3 onset: the cut against the frozen alarm and the first GOP drop\n")
    print("Per onset with an alarm: cut found within 10 s; already in force at t_on - 1 s; cut - alarm (p50, "
          "negative = the cut comes first); share with the cut before the alarm; among onsets followed by a GOP "
          "drop, share with the cut before the drop.\n")
    for cc in ("bbr", "copa"):
        sel = [(r, o) for r, o in ons if o["cc"] == cc]
        if not sel:
            continue
        print(f"### {cc.upper()}\n")
        print("| AQM | stimulus | x | onsets r1 / r2 | cut found | already | cut - alarm p50 s | cut before alarm | "
              "alarm - t_on p50 s | cut before drop (n) |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        g = defaultdict(lambda: {1: [], 2: []})
        for r, o in sel:
            g[(r["aqm"], TYPE.get(r["type"], r["type"]))][r["rep"]].append(o)
            g[("all", "all")][r["rep"]].append(o)
        for k in sorted(g, key=lambda z: (z[0] != "all", z)):
            for x in X:
                cells = []
                for rep in (1, 2):
                    os_ = [o for o in g[k][rep] if o["t_alarm"] is not None]
                    if not os_:
                        cells.append(None)
                        continue
                    found = [o for o in os_ if o[f"cut_{x}"] is not None]
                    al = [o for o in found if o[f"already_{x}"]]
                    d = [o[f"cut_{x}"] - o["t_alarm"] for o in found]
                    dr = [o for o in os_ if o["t_drop"] is not None]
                    cb = [o for o in dr if o[f"cut_{x}"] is not None and o[f"cut_{x}"] < o["t_drop"]]
                    cells.append({"n": len(os_), "found": len(found) / len(os_), "already": len(al) / len(os_),
                                  "d50": float(np.median(d)) if d else None,
                                  "before": sum(v < 0 for v in d) / len(os_),
                                  "lat": float(np.median([o["t_alarm"] - o["t_on"] for o in os_])),
                                  "drop": (len(cb) / len(dr) if dr else None, len(dr))})
                if not any(cells):
                    continue
                c = lambda key, d=2: " / ".join(f_(v[key], d) if v else "-" for v in cells)   # noqa: E731
                print(f"| {k[0]} | {k[1]} | {x} | " + " / ".join(str(v["n"]) if v else "0" for v in cells) +
                      f" | {c('found')} | {c('already')} | {c('d50')} | {c('before')} | {c('lat')} | " +
                      " / ".join(f"{f_(v['drop'][0])} ({v['drop'][1]})" if v else "-" for v in cells) + " |")
        print()
