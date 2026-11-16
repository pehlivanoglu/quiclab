#!/usr/bin/env python3
"""GT-H 600 harmful episodes of v2-owd that gtq_score counts as missed (no alarm START in the collar):
was the alarm ON during the episode (an earlier alarm held over it)? Per AQM.

    .venv/bin/python3 reports/v3-detector/gth_alarm_on.py .runs/2026-11-14_1818_v3 > reports/v3-detector/gth-alarm-on.md
"""
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
HERE = Path(__file__).resolve().parent


def one(args):
    rd, eps = args
    import det_eval as d
    import shadow_v2_frozen as fz
    sp = fz.episodes(d.Run(rd), "v2", mode="OWD", hold=True)
    out = []
    for e in eps:
        t0, t1 = float(e["t0"]), float(e["t1"])
        on = any(a <= t1 and b >= t0 for a, b, _ in sp.get(e["flow"], []))
        out.append((int(e["hit"]), on))
    return out


def main(kdir):
    rows = [json.loads(x) for x in open(HERE / "rows.jsonl") if x.strip()]
    jobs, aqm = [], []
    for r in rows:
        if not r.get("gtq"):
            continue
        eps = [e for e in r["gtq"]["episodes"] if e["detector"] == "v2-owd" and str(e["harmful_600"]) == "1"]
        if eps:
            jobs.append((kdir / r["run"], eps))
            aqm.append(r["aqm"])
    agg = defaultdict(lambda: [0, 0, 0, 0])   # harmful, hit (start in collar), missed but alarm on, missed and off
    with ProcessPoolExecutor(12) as ex:
        for a, res in zip(aqm, ex.map(one, jobs)):
            for hit, on in res:
                agg[a][0] += 1
                agg[a][1] += hit
                agg[a][2] += (not hit) and on
                agg[a][3] += (not hit) and not on
    print("# GT-H 600 harmful episodes, v2-owd: alarm start in the collar vs alarm on during the episode\n")
    print("| AQM | harmful | alarm start in collar (gtq_score recall) | missed but alarm on (held) | alarm off | alarm on or start |")
    print("|---|---|---|---|---|---|")
    tot = [0, 0, 0, 0]
    for a in sorted(agg):
        n, h, on, off = agg[a]
        tot = [x + y for x, y in zip(tot, agg[a])]
        print(f"| {a} | {n} | {h / n:.2f} | {on / n:.2f} | {off / n:.2f} | {(h + on) / n:.2f} |")
    n, h, on, off = tot
    print(f"| all | {n} | {h / n:.2f} | {on / n:.2f} | {off / n:.2f} | {(h + on) / n:.2f} |")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
