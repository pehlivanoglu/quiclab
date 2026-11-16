#!/usr/bin/env python3
"""Copa runs (M13: T-BASE, single leaf of 4 clients, video congestion control Copa, BG-CBR, s 0.30 U 0.70,
sburst grid, pfifo and codel, 2 reps) next to the same point with BBR (C2 sburst s030u070 pfifo / codel).
Measurement only; every script called unchanged.

    .venv/bin/python3 reports/copa-2026-11-15/copa.py rows .runs/2026-11-14_1818_v3     # ECG (score_v3.ecg_one) + Step 8 / 9 rows
    .venv/bin/python3 reports/copa-2026-11-15/copa.py report > reports/copa-2026-11-15/tables.md

Detector numbers come from reports/v3-detector/rows.jsonl and stimuli.jsonl (frozen Shadow v2, OWD; GT1 / GT2 /
GT3 as in RAPOR.md; GT-Q / GT-H from gtq_score). Grouping: ECG v1.2 (delta 0.150 s), h3 (replay4, m = 3) and
SETS (Step 9) on the single true set {4 clients behind router->switch}; scores as Step 9 part B.
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
for p in ("reports/v3-score", "reports/step8-2026-11-15", "reports/step9-2026-11-15", "scripts"):
    sys.path.insert(0, str(ROOT / p))
RUNS = [f"v3-M13-sburst-copa-{a}-r{r}" for a in ("pfifo", "codel") for r in (1, 2)] + \
       [f"v3-C2-sburst-s030u070-{a}-r{r}" for a in ("pfifo", "codel") for r in (1, 2)]
CELL = lambda run: ("Copa " if "M13" in run else "BBR ") + run.split("-")[-2]   # noqa: E731
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731


def ecg(rd):
    import score_v3
    if (rd / "grouping-d150-truth" / "metrics.json").exists():
        return rd.name, "present"
    return rd.name, score_v3.ecg_one(rd)


def rows(kdir: Path):
    rds = [kdir / r for r in RUNS]
    with Pool(6) as pool:
        for name, res in pool.imap_unordered(ecg, rds):
            print("ECG", name, res, file=sys.stderr)
        import step8
        R8 = list(pool.imap_unordered(step8.one, rds))
    import step9
    allrows = [r for r in step9.load_rows() if r["block"] in step9.BLOCKS]
    _, fixed = step9.miss_model(allrows)
    with Pool(6) as pool:
        R9 = list(pool.imap_unordered(step9.worker, [(r, fixed) for r in R8 if "error" not in r]))
    with open(HERE / "rows-copa.jsonl", "w") as fh:
        for r in R8:
            fh.write(json.dumps({"kind": "step8", **r}) + "\n")
        for r in R9:
            fh.write(json.dumps({"kind": "step9", **r}) + "\n")


def two(vals, k=2):
    return " / ".join(f(v, k) if not isinstance(v, str) else v for v in vals)


def report():
    det = {json.loads(x)["run"]: json.loads(x) for x in open(ROOT / "reports/v3-detector/rows.jsonl") if x.strip()}
    stim = [json.loads(x) for x in open(ROOT / "reports/v3-detector/stimuli.jsonl") if x.strip()]
    G = [json.loads(x) for x in open(HERE / "rows-copa.jsonl") if x.strip()]
    s8 = {r["run"]: r for r in G if r["kind"] == "step8" and "error" not in r}
    s9 = {r["run"]: r for r in G if r["kind"] == "step9" and "error" not in r}
    cells = defaultdict(dict)
    for run in RUNS:
        cells[CELL(run)][int(run[-1])] = run
    order = ["Copa pfifo", "BBR pfifo", "Copa codel", "BBR codel"]

    print("# Copa runs: detector and grouping (tables)\n")
    print("Copa = M13 (video CC Copa); BBR = C2 sburst s030u070 (same topology, load, stimuli, AQM). Every value rep 1 / rep 2.\n")

    print("## 1. Detector (frozen Shadow v2, OWD)\n")
    for det_name in ("v2-owd", "v2-fixed-owd"):
        print(f"### {det_name}\n")
        print("| cell | truth | episodes | recall | precision | latency p50 / p95 ms | false alarms per client-hour (CLEAR) | alarm on during episode |")
        print("|---|---|---|---|---|---|---|---|")
        for c in order:
            for t in ("GT3", "GT1", "GT2"):
                vals = defaultdict(list)
                for rep in (1, 2):
                    s = det[cells[c][rep]]["score"][t][det_name]
                    lat = [x for x in s["latency"] if x is not None]
                    vals["n"].append(str(s["episodes"]))
                    vals["R"].append(s["detected"] / s["episodes"] if s["episodes"] else None)
                    vals["P"].append(s["tp"] / (s["tp"] + s["fp"]) if s["tp"] + s["fp"] else None)
                    vals["lat"].append(f"{f(np.percentile(lat, 50) * 1e3, 0)}/{f(np.percentile(lat, 95) * 1e3, 0)}" if lat else "-")
                    vals["fa"].append(s["fp"] / (s["clear_s"] / 3600) if s["clear_s"] else None)
                    vals["on"].append(s["alarm_on"] / s["episodes"] if s["episodes"] else None)
                print(f"| {c} | {t} | {' / '.join(vals['n'])} | {two(vals['R'])} | {two(vals['P'])} | {' / '.join(vals['lat'])} | "
                      f"{two(vals['fa'], 1)} | {two(vals['on'])} |")
        print()
    print("### GT-Q / GT-H (gtq_score; valid GT-Q in all 8 runs)\n")
    print("| cell | GT-Q precision | GT-H 600 harmful episodes | GT-H start in collar | alarm before harm (start in collar, before t_harm) |")
    print("|---|---|---|---|---|")
    for c in order:
        v = defaultdict(list)
        for rep in (1, 2):
            g = det[cells[c][rep]]["gtq"]
            tal = [x for x in g["tallies"] if x["detector"] == "v2-owd"]
            m, fp = sum(x["alarms_matched"] for x in tal), sum(x["fp"] for x in tal)
            v["P"].append(m / (m + fp) if m + fp else None)
            h = [e for e in g["episodes"] if e["detector"] == "v2-owd" and str(e["harmful_600"]) == "1"]
            v["n"].append(str(len(h)))
            v["R"].append(sum(e["hit"] for e in h) / len(h) if h else None)
            lead = [e for e in h if e["hit"] and e.get("lead_600_ms") not in (None,) and not (isinstance(e["lead_600_ms"], float) and math.isnan(e["lead_600_ms"])) and e["lead_600_ms"] > 0]
            v["b"].append(len(lead) / len(h) if h else None)
        print(f"| {c} | {two(v['P'])} | {' / '.join(v['n'])} | {two(v['R'])} | {two(v['b'])} |")
    print()
    print("### By stimulus: share of the 4 clients alarming in [start - 1 s, start + 10 s] (v2-owd), and the video's load during the "
          "window relative to calm\n")
    print("| cell | u | d s | windows r1 / r2 | alarm share r1 / r2 | video / calm r1 / r2 (median) |")
    print("|---|---|---|---|---|---|")
    for c in order:
        grp = defaultdict(lambda: {1: [], 2: []})
        for w in stim:
            if w.get("run") in cells[c].values() and w.get("clients"):
                grp[(w.get("u_nominal"), w.get("d"))][int(w["run"][-1])].append(w)
        for (u, dd), v in sorted(grp.items(), key=lambda x: (x[0][0] or 0, x[0][1] or 0)):
            sh = lambda ws: f(sum(x["hit"]["v2-owd"] for x in ws) / sum(x["clients"] for x in ws)) if ws else "-"   # noqa: E731
            vr = lambda ws: f(float(np.median([x["video_rel_calm"] for x in ws if x.get("video_rel_calm") is not None]))) if ws else "-"  # noqa: E731
            print(f"| {c} | {u} | {dd} | {len(v[1])} / {len(v[2])} | {sh(v[1])} / {sh(v[2])} | {vr(v[1])} / {vr(v[2])} |")
    print()

    print("## 2. Grouping (one true set: the 4 clients behind router->switch)\n")
    for src in ("v2-owd", "truth"):
        print(f"### onset source {src}\n")
        print("| cell | ECG events | observed set = all 4 | missing clients p50 when not | SETS k2 F1 | SETS k3 F1 | ECG F1 | h3 F1 | "
              "spurious per close SETS k3 / ECG / h3 | events to F1 >= 0.9 SETS k2 / ECG / h3 | pair P / R SETS k3 | pair P / R ECG | pair P / R h3 |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for c in order:
            v = defaultdict(list)
            for rep in (1, 2):
                run = cells[c][rep]
                ev = [e for e in s8[run][src]["events"] if len(e["obs"]) >= 1]
                fam = set(next(iter(s8[run]["fam"].values())))
                full = [set(e["obs"]) == fam for e in ev]
                miss = [len(fam - set(e["obs"])) for e in ev if set(e["obs"]) != fam]
                v["n"].append(str(len(ev)))
                v["full"].append(float(np.mean(full)) if full else None)
                v["miss"].append(float(np.median(miss)) if miss else None)
                z = s9[run][src]
                lvf = lambda s_: s_["levels"].get("leaf", [None, None, None])[2]   # noqa: E731
                v["s2"].append(lvf(z["sets"]["quantile|2|False"]))
                v["s3"].append(lvf(z["sets"]["quantile|3|False"]))
                v["e"].append(lvf(z["ecg"]))
                v["h"].append(lvf(z["h3"]))
                v["sp"].append(f"{f(z['sets']['quantile|3|False']['spur_mean'])}/{f(z['ecg']['spur_mean'])}/{f(z['h3']['spur_mean'])}")
                t = lambda s_: str(next(iter(s_["t_ok"].values()))[2]) if s_["t_ok"] else "never"   # noqa: E731
                v["t"].append(f"{t(z['sets']['quantile|2|False'])}/{t(z['ecg'])}/{t(z['h3'])}")

                def pr(s_):
                    p = s_["pairs"]
                    return f"{f(p[0] / (p[0] + p[1]) if p[0] + p[1] else None)}/{f(p[0] / (p[0] + p[2]) if p[0] + p[2] else None)}"
                v["ps"].append(pr(z["sets"]["quantile|3|False"]))
                v["pe"].append(pr(z["ecg"]))
                v["ph"].append(pr(z["h3"]))
            print(f"| {c} | {' / '.join(v['n'])} | {two(v['full'])} | {two(v['miss'], 0)} | {two(v['s2'])} | {two(v['s3'])} | "
                  f"{two(v['e'])} | {two(v['h'])} | {' ; '.join(v['sp'])} | {' ; '.join(v['t'])} | {' ; '.join(v['ps'])} | "
                  f"{' ; '.join(v['pe'])} | {' ; '.join(v['ph'])} |")
        print()


if __name__ == "__main__":
    if sys.argv[1] == "rows":
        rows(Path(sys.argv[2]))
    else:
        report()
