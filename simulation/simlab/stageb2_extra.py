#!/usr/bin/env python3
"""Stage B2 report additions (user, 2026-11-18): SETS rows, onset-spread p90 direction, calm behaviour.

    python3 simulation/simlab/stageb2_extra.py > reports/sim-stageB2-applimited/extra.md

Reads rows-*.jsonl of stage B (v1) and B2 (stageb_compare output) for SETS and spread; computes the calm rows
fresh from the frozen detector's score series (read-only on testbed runs; tick files from the existing caches).

Calm behaviour, definitions fixed before looking at the numbers:
  calm time          stageb_compare.calm_mask (outside every stimulus window widened by [-1 s, +3 s], after
                     the warm-up), unmasked ticks with data
  calm alarms / min  frozen v2-owd alarms (episode arrival) in calm time / calm minutes, pooled over video clients
  sub-threshold      a maximal run of consecutive calm ticks with score >= theta_off (theta_on / 2) whose maximum
  event              stays below theta_on (no alarm)
  keyframe-aligned   the event's first tick lies in [keyframe write, keyframe write + 3 ticks] of the same client
                     (3, not 2: the 33.0 ms tick grid drifts against the 33.3 ms frame grid, so the tick after a
                     keyframe falls up to 3 ticks late; found on one testbed run before any table; chance ~ 10 %)
  score p99          99th percentile of the detector score over calm ticks, pooled
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import frozen  # noqa: E402  (patched tick cache)
import stageb  # noqa: E402
import stageb_compare as sc  # noqa: E402

fz, d = frozen.fz, frozen.d
REP = QUICLAB / "reports"
ROWS = {"testbed": None, "v1 matched": REP / "sim-stageB-2026-11-18" / "rows-matched.jsonl",
        "B2 matched": REP / "sim-stageB2-applimited" / "rows-matched.jsonl",
        "B2 spec": REP / "sim-stageB2-applimited" / "rows-spec.jsonl"}
RUNSETS = {"v1 matched": ("matched", "v1"), "B2 matched": ("matched", "applimited"), "B2 spec": ("spec", "applimited")}


def load(p: Path) -> dict:
    return {json.loads(l)["name"]: json.loads(l) for l in p.open()}


def cell(name: str) -> str:
    return name.removeprefix("sim-B-").rsplit("-r", 1)[0]


def fmt(x, n=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{n}f}"


def sets_row(s: dict, k: str):
    v = (s or {}).get(f"V {k}") or {}
    lf = (v.get("levels") or {}).get("leaf")
    p = v.get("pairs") or [0] * 5
    f1 = lf[2] if lf else None
    P = p[0] / (p[0] + p[1]) if p[0] + p[1] else None
    R = p[0] / (p[0] + p[2]) if p[0] + p[2] else None
    return f1, P, R


def calm(rd: Path) -> dict:
    run = d.Run(rd)
    wins = sc.windows(rd)
    fit = fz.FROZEN["OWD"]
    fz.s3.FLOORS.clear(); fz.s3.FLOORS.update(fit["floors"])
    fz.s3.FIXED_STATS.clear(); fz.s3.FIXED_STATS.update(fit["stats"])
    label = fz.LABEL["v2"] + " +hold gate:level+cap"
    th = fz.s3.THETA_ON
    alarms, minutes, sub, sub_kf, scores = 0, 0.0, 0, 0, []
    for s, f in fz.tick_files(run, "OWD").items():
        if s == sc.CTRL:
            continue
        tk = pd.read_csv(f, usecols=["t", "masked", "no_data"])
        r = fz.s3.run_cusum(fz.s3.load_flow(f), label, fit["g_ref"]["v2"], False)
        t, score = np.asarray(r["t"], float), np.asarray(r["score"], float)
        ok = sc.calm_mask(t, wins, run.duration) & ~tk.masked.astype(bool).values[:len(t)] & ~tk.no_data.astype(bool).values[:len(t)]
        tick = float(t[1] - t[0])
        minutes += ok.sum() * tick / 60
        scores.append(score[ok & np.isfinite(score)])
        arr = [a for a, _, _ in fz.s5.on_spans(r, th)]   # the frozen episodes (hold on), as frozen.episodes
        ti = np.searchsorted(t, arr)
        alarms += int(sum(ok[min(i, len(t) - 1)] for i in ti))
        fr = pd.read_csv(run.sender_file(s, "frames"), usecols=["keyframe", "write_us"])
        kf = np.sort(np.array([run.t_unix_us(w) for w in fr.write_us.values[fr.keyframe.values == 1]]))
        hi = ok & (score >= th / 2)
        k = 0
        while k < len(t):
            if not hi[k]:
                k += 1
                continue
            j = k
            while j + 1 < len(t) and hi[j + 1]:
                j += 1
            if np.nanmax(score[k:j + 1]) < th:
                sub += 1
                i = np.searchsorted(kf, t[k], side="right") - 1
                if i >= 0 and t[k] - kf[i] <= 3 * tick + 1e-9:
                    sub_kf += 1
            k = j + 1
    sc_all = np.concatenate(scores) if scores else np.array([])
    return {"calm_min": minutes, "alarms_per_min": alarms / minutes if minutes else math.nan,
            "sub_per_min": sub / minutes if minutes else math.nan, "sub_kf_share": sub_kf / sub if sub else math.nan,
            "score_p99": float(np.percentile(sc_all, 99)) if len(sc_all) else math.nan}


def main() -> None:
    rows = {k: load(p) for k, p in ROWS.items() if p}
    names = [n for n, *_ in stageb.runs("matched", "applimited")]
    tb_of = {n: tb for n, tb, *_ in stageb.runs("matched", "applimited")}
    cells = list(dict.fromkeys(cell(n) for n in names))

    print("## SETS (frozen, k = 2 / k = 3): leaf F1; pair precision; pair recall, r1 / r2\n")
    sides = ["testbed", "v1 matched", "B2 matched", "B2 spec"]
    print("| cell | k | " + " | ".join(sides) + " |")
    print("|---|---|" + "---|" * len(sides))
    for c in cells:
        rn = [n for n in names if cell(n) == c]
        for k in ("k2", "k3"):
            out = []
            for side in sides:
                src = rows["B2 matched"] if side == "testbed" else rows[side]
                part = []
                for n in rn:
                    r = src.get(n, {})
                    s = r.get("testbed" if side == "testbed" else "sim", {}).get("sets")
                    part.append(sets_row(s, k))
                out.append(" / ".join(f"{fmt(f)}; {fmt(P)}; {fmt(R)}" for f, P, R in part))
            if all(x.replace("-", "").replace(";", "").replace("/", "").strip() == "" for x in out):
                continue
            print(f"| {c} | {k[1]} | " + " | ".join(out) + " |")

    print("\n## Onset spread p90 per cell (ms, r1 / r2): testbed, simulation, simulation - testbed\n")
    print("| cell | testbed | B2 matched | diff | B2 spec | diff | v1 matched | diff |")
    print("|---|---|---|---|---|---|---|---|")
    for c in cells:
        rn = [n for n in names if cell(n) == c]
        tb = [rows["B2 matched"][n]["testbed"].get("spread_p90_ms", math.nan) for n in rn]
        if all(math.isnan(x) for x in tb):
            continue
        line = [" / ".join(fmt(x, 0) for x in tb)]
        for side in ("B2 matched", "B2 spec", "v1 matched"):
            sm = [rows[side][n]["sim"].get("spread_p90_ms", math.nan) for n in rn]
            line += [" / ".join(fmt(x, 0) for x in sm), " / ".join(f"{x - y:+.0f}" for x, y in zip(sm, tb))]
        print(f"| {c} | " + " | ".join(line) + " |")

    print("\n## Calm behaviour (frozen v2-owd, calm ticks): alarms / min; sub-threshold events / min; "
          "share keyframe-aligned; score p99\n")
    res = {}
    calm_sides = [("testbed", None)] + [(s, RUNSETS[s]) for s in ("v1 matched", "B2 matched")]
    for side, rs in calm_sides:
        for n, tb, sim, _ in stageb.runs(*(rs or ("matched", "applimited"))):
            res[(side, n)] = calm(tb if side == "testbed" else sim)
            print(f"<!-- {side} {n} done -->", file=sys.stderr, flush=True)
    (REP / "sim-stageB2-applimited" / "calm.json").write_text(json.dumps({f"{a}|{b}": v for (a, b), v in res.items()}, indent=1))
    print("| run | " + " | ".join(s for s, _ in calm_sides) + " |")
    print("|---|" + "---|" * len(calm_sides))
    for n in names:
        print(f"| {n.removeprefix('sim-B-')} | " + " | ".join(
            f"{fmt(v['alarms_per_min'])}; {fmt(v['sub_per_min'])}; {fmt(v['sub_kf_share'])}; {fmt(v['score_p99'], 3)}"
            for v in (res[(s, n)] for s, _ in calm_sides)) + " |")
    print("\nMedians over the 22 pairs:\n")
    for s, _ in calm_sides:
        v = [res[(s, n)] for n in names]
        print(f"- {s}: alarms / min {np.nanmedian([x['alarms_per_min'] for x in v]):.3f}, sub-threshold / min "
              f"{np.nanmedian([x['sub_per_min'] for x in v]):.2f}, keyframe-aligned share "
              f"{np.nanmedian([x['sub_kf_share'] for x in v]):.2f}, score p99 {np.nanmedian([x['score_p99'] for x in v]):.3f}")


if __name__ == "__main__":
    main()
