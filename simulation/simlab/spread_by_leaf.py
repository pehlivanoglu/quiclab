#!/usr/bin/env python3
"""Onset spread against leaf size: a listing, no criterion (user 2026-11-18, before the 300-client test run).

    python3 simulation/simlab/spread_by_leaf.py [sim batch dir ...] > out.md

Sides: "sim" = the given simulation batch folders (default: stage B2 ack-matched); "testbed" = their K1
counterparts plus every K1 G1-G3 cell whose frozen tick files are already cached (nothing is built for testbed runs;
read-only). Per stimulus window (grouping/windows.json): each expected member's first frozen v2-owd onset in
[start - 1 s, start + 10 s] (as stageb_compare); leaf size = number of expected members; spread = last - first onset
over the members with an onset (>= 2). Late member: onset more than 0.5 s (the event window) after the stimulus's
first onset. Per client: how often it is late, with its access delay, bitrate and position in the leaf
(v3-plan.json / topology.yaml).
"""

from __future__ import annotations

import collections
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import frozen  # noqa: E402
import stageb  # noqa: E402

K1 = stageb.K1
WINDOW_S = 0.5


def cached(rd: Path) -> bool:
    run = frozen.d.Run(rd)
    key = Path(rd.parent.name) / rd.name / "shadow-v2"
    for base in [rd / "shadow-v2", *[r / key for r in frozen.READ_ONLY], frozen.CACHE / key]:
        if all((base / "ticks-frozen-owd" / f"{s}.csv").exists() for s in run.subs):
            return True
    return False


def stimuli(rd: Path) -> list[dict]:
    wp = rd / "grouping" / "windows.json"
    wins = json.loads(wp.read_text()) if wp.exists() else []
    if not wins:
        return []
    eps = frozen.episodes(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    topo = yaml.safe_load((rd / "topology.yaml").read_text())
    acc = plan.get("access_delay_ms") or {}
    out = []
    for w in wins:
        members = list(w.get("expected", []))
        on = {m: min((o for a, b, o in eps.get(m, []) if w["start"] - 1.0 <= o <= w["start"] + 10.0), default=None)
              for m in members}
        got = {m: o for m, o in on.items() if o is not None}
        first = min(got.values()) if got else None
        out.append({"run": rd.name, "n": len(members), "start": w["start"], "kind": w.get("kind"),
                    "missed": [m for m in members if m not in got],
                    "spread_ms": 1000 * (max(got.values()) - first) if len(got) >= 2 else math.nan,
                    "late": {m: round(1000 * (o - first), 1) for m, o in got.items() if o - first > WINDOW_S},
                    "client": {m: {"acc_ms": acc.get(m), "kbps": topo["subscribers"][m]["rate_kbps"], "pos": i}
                               for i, m in enumerate(members)}})
    return out


def q(x, p):
    return float(np.percentile(x, p)) if len(x) else math.nan


def main(argv: list[str]) -> None:
    batches = [Path(a) for a in argv] or [stageb.OUT_OF[("applimited", "matched")]]
    sim_runs = sorted(p for b in batches for p in b.iterdir() if (p / "sim" / "scored.json").exists())
    tb_runs = {Path(json.loads((p / "sim" / "meta.json").read_text())["testbed_run"]) for p in sim_runs}
    tb_runs |= {p for p in K1.glob("v4-G[123]-*") if cached(p)}
    sides = {"testbed": sorted(tb_runs), "sim": sim_runs}
    res = {side: [s for rd in runs for s in stimuli(rd)] for side, runs in sides.items()}
    print(f"Runs: testbed {len(sides['testbed'])} (B2 counterparts + cached K1 G1-G3), simulation {len(sim_runs)} "
          f"({', '.join(b.parent.name + '/' + b.name for b in batches)}). Late = onset > first onset + {WINDOW_S} s.\n")

    print("## Spread per stimulus by leaf size (ms)\n")
    print("| leaf size | side | runs | stimuli (>= 2 onsets) | p50 | p90 | p98 | max | stimuli > 0.5 s | late members per such stimulus (mean) | lateness p50 / max ms | missed members |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n in sorted({s["n"] for v in res.values() for s in v}):
        for side in ("testbed", "sim"):
            st = [s for s in res[side] if s["n"] == n]
            if not st:
                continue
            sp = np.array([s["spread_ms"] for s in st if not math.isnan(s["spread_ms"])])
            big = [s for s in st if s["late"]]
            late = [v for s in big for v in s["late"].values()]
            print(f"| {n} | {side} | {len({s['run'] for s in st})} | {len(sp)} | {q(sp, 50):.0f} | {q(sp, 90):.0f} | "
                  f"{q(sp, 98):.0f} | {sp.max() if len(sp) else math.nan:.0f} | {len(big)} | "
                  f"{np.mean([len(s['late']) for s in big]) if big else 0:.1f} | "
                  f"{q(late, 50):.0f} / {max(late) if late else math.nan:.0f} | {sum(len(s['missed']) for s in st)} |")

    print("\n## Who is late: share of a client's stimuli in which it is late, by attribute (pooled over runs)\n")
    for attr, label in (("acc_ms", "access delay ms"), ("kbps", "bitrate kb/s"), ("pos", "position in leaf (0 = first)")):
        print(f"\n### {label}\n")
        print("| leaf size | side | " + label + ": late / member-stimuli (share) |")
        print("|---|---|---|")
        for n in sorted({s["n"] for v in res.values() for s in v}):
            for side in ("testbed", "sim"):
                st = [s for s in res[side] if s["n"] == n and s["late"]]
                if not st:
                    continue
                tot, lt = collections.Counter(), collections.Counter()
                for s in st:
                    for m, c in s["client"].items():
                        v = c[attr] if attr != "pos" else (c["pos"] * 4 // max(1, n))   # position in quarters
                        tot[v] += 1
                        lt[v] += m in s["late"]
                key = "quarter " if attr == "pos" else ""
                print(f"| {n} | {side} | " + ", ".join(f"{key}{k}: {lt[k]} / {tot[k]} ({lt[k] / tot[k]:.2f})"
                                                       for k in sorted(tot, key=lambda x: (x is None, x))) + " |")

    print("\n## Repeat offenders: clients late in >= 3 stimuli of one run\n")
    print("| side | run | client (late count / stimuli; access ms, kb/s, position) |")
    print("|---|---|---|")
    for side in ("testbed", "sim"):
        by_run = collections.defaultdict(list)
        for s in res[side]:
            by_run[s["run"]].append(s)
        for run, st in sorted(by_run.items()):
            cnt = collections.Counter(m for s in st for m in s["late"])
            rep = [(m, c) for m, c in cnt.most_common() if c >= 3]
            if rep:
                info = st[0]["client"]
                print(f"| {side} | {run} | " + "; ".join(
                    f"{m} {c} / {len(st)} ({info[m]['acc_ms']}, {info[m]['kbps']}, {info[m]['pos']})" for m, c in rep) + " |")
    (QUICLAB / "reports" / "sim-stageB2-applimited" / "spread-by-leaf.json").write_text(json.dumps(res, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
