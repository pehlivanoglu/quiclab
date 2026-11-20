#!/usr/bin/env python3
"""Stage B batch (spec section 5): the testbed's K1 counterparts, two seeds, then the frozen scoring.

    python3 simulation/simlab/stageb.py --plan-only        # run list, client-seconds, disk estimate
    python3 simulation/simlab/stageb.py                    # run (resumable: complete runs are skipped)

Launch through reports/batch_guard.py (auto --session sim --cores 1). One run at a time.
Per run: simlab/run.py (plan + quicsim + GT-Q health), then the frozen truths on the
simulation folder (scripts/gt1.py, gt3.py, gtq.py score; they write <sim run>/truth/) and the
frozen v2-owd detector (simlab/frozen.py; tick cache under reports/sim-cache/). Nothing is
written to a testbed run.
Run names: sim-B-<block>-<scenario>-<queue>-r<seed> (spec section 9); seed = rep index; the
testbed counterpart is K1 <block>-<scenario>-<queue>-r<seed>.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
K1 = QUICLAB / ".runs" / "2026-11-16_0105_v4-K1"
RUNS = QUICLAB / "simulation" / "runs"
# Run sets: "v1" = stage B before the application-limited patch (2026-11-18), "applimited" = with it (re-run).
# v1 runs deleted 2026-11-19 (reports/sim-stageB-2026-11-18/RESTORED.md): the "v1" set no longer exists on disk.
OUT_OF = {("v1", "spec"): RUNS / "stageB-2026-11-18", ("v1", "matched"): RUNS / "stageB-2026-11-18-ackmatched",
          ("applimited", "spec"): RUNS / "stageB2-applimited" / "spec",
          ("applimited", "matched"): RUNS / "stageB2-applimited" / "matched",
          # B2 re-run after the CoDel double-count fix in the recorder (user 2026-11-19, U1); the folder name is the
          # tick-cache key, so it differs from B2's "matched" / "spec"
          ("codelfix", "matched"): RUNS / "stageB2-codelfix" / "codelfix-matched",
          ("codelfix", "spec"): RUNS / "stageB2-codelfix" / "codelfix-spec",
          # B2 re-run with fixed random streams (BBR, PIE, RED; user 2026-11-19): the reference from then on
          ("streams", "matched"): RUNS / "stageB2-streams" / "streams-matched",
          ("streams", "spec"): RUNS / "stageB2-streams" / "streams-spec",
          # fixed streams for PIE / RED only (BBR left on automatic numbering: fixing it changes pfifo / CoDel)
          ("pie-streams", "matched"): RUNS / "stageB2-piestreams" / "piestreams-matched",
          ("pie-streams", "spec"): RUNS / "stageB2-piestreams" / "piestreams-spec"}
SETS = ("v1", "applimited", "codelfix", "streams", "pie-streams")   # stage B3 (mvfst drain mark, patch 2) dropped 2026-11-19: no effect (reports/sim-stageB3-mvfst-drain)
PY = sys.executable
SEEDS = (1, 2)
MB_PER_CLIENT_S = 0.2          # measured: smoke A2 (0.18), PPBP N6 (0.14); estimate only

# spec section 5: scenario, clients, queues, testbed counterpart
CELLS = [
    ("A1", "calm-base", ("pfifo", "codel")),        # CALM, 4 clients
    ("A1", "calm-split4l", ("pfifo", "codel")),     # CALM, 8 clients
    ("A2", "sburst-def", ("pfifo", "codel", "pie")),  # S-BURST on T-BASE, 4
    ("A4", "hhier-def", ("pfifo", "codel")),        # H-HIERL on T-SPLIT4L, 8
    ("G1", "sburst-n16", ("pfifo",)),               # G-SIZE on T-LEAFn, 16
    ("G1", "sburst-n24", ("pfifo",)),               # G-SIZE on T-LEAFn, 24
]


def runs(ack: str = "matched", run_set: str = "applimited") -> list[tuple[str, Path, Path, int]]:
    OUT = OUT_OF[(run_set, ack)]
    out = []
    for block, scen, queues in CELLS:
        for q in queues:
            for seed in SEEDS:
                tb = K1 / f"v4-{block}-{scen}-{q}-r{seed}"
                out.append((f"sim-B-{block}-{scen}-{q}-r{seed}", tb, OUT / f"sim-B-{block}-{scen}-{q}-r{seed}", seed))
    return out


def client_seconds(tb: Path) -> float:
    topo = yaml.safe_load((tb / "topology.yaml").read_text())
    scen = yaml.safe_load((tb / "scenario.yaml").read_text())
    return len(topo["subscribers"]) * float(scen["duration_s"])


def score(sim: Path) -> dict:
    res = {}
    for s in ("gt1", "gt3", "gtq"):
        p = subprocess.run([PY, str(HERE / "scale_ext.py"), str(QUICLAB / "scripts" / f"{s}.py"), "score", str(sim)], capture_output=True, text=True)
        res[s] = (p.stdout.strip().splitlines() or [""])[-1] if p.returncode == 0 else f"FAILED: {p.stderr[-300:]}"
    p = subprocess.run([PY, "-c", f"import sys; sys.path.insert(0, {str(HERE)!r}); import scale_ext, frozen, json; "
                        f"from pathlib import Path; e = frozen.episodes(Path({str(sim)!r})); "
                        f"json.dump({{k: [list(x) for x in v] for k, v in e.items()}}, open({str(sim / 'sim' / 'episodes-v2-owd.json')!r}, 'w'))"],
                       capture_output=True, text=True)
    res["detector"] = "ok" if p.returncode == 0 else f"FAILED: {p.stderr[-300:]}"
    return res


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--set", dest="run_set", choices=SETS, default="applimited", help="run set (output folder)")
    ap.add_argument("--ack", choices=("matched", "spec"), default="matched",
                    help="delayed-ACK profile (plan.py); matched = primary from 2026-11-18, spec = second row in stage B only")
    ap.add_argument("--only", default="", help="comma-separated run names (subset)")
    a = ap.parse_args(argv)
    todo = runs(a.ack, a.run_set)
    if a.only:
        todo = [x for x in todo if x[0] in a.only.split(",")]
    total_cs = 0.0
    for name, tb, sim, seed in todo:
        cs = client_seconds(tb)
        total_cs += cs
        done = (sim / "sim" / "scored.json").exists()
        print(f"{name:42s} tb={tb.name:34s} client_s={cs:7.0f} est_GB={cs * MB_PER_CLIENT_S / 1e3:5.2f} {'done' if done else ''}")
    print(f"{len(todo)} runs, {total_cs:.0f} client-seconds, est. {total_cs * MB_PER_CLIENT_S / 1e3:.1f} GB")
    if a.plan_only:
        return
    for name, tb, sim, seed in todo:
        if (sim / "sim" / "scored.json").exists():
            continue
        free = shutil.disk_usage("/").free / 1e9
        if free < 30:
            sys.exit(f"free disk {free:.0f} GB < 30 GB: stopping before {name}")
        if sim.exists() and not (sim / "sim" / "meta.json").exists():
            shutil.rmtree(sim)  # incomplete earlier attempt of this run (simulation output only)
        t0 = time.time()
        if not (sim / "sim" / "meta.json").exists():
            p = subprocess.run([PY, str(HERE / "run.py"), str(tb), str(sim), "--seed", str(seed), "--ack", a.ack])
            if p.returncode != 0:
                print(f"{name}: FAILED (run.py exit {p.returncode})", flush=True)
                continue
        res = score(sim)
        res["score_wall_s"] = round(time.time() - t0, 1)
        (sim / "sim" / "scored.json").write_text(json.dumps(res, indent=1) + "\n")
        print(f"{name}: {json.dumps(res)}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
