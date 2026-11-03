#!/usr/bin/env python3
"""Run the detector matrix: every AQM x det-* scenario x repetition, then score.

    python3 scripts/det_matrix.py [--reps N] [--aqms a,b] [--scenarios a,b] [--campaign DIR] [--skip-existing]

Scenarios: capacity, cbr, ppbp (det-<name>.yaml) and the burst benchmark
burstcap, burstudp (generated from det-burst.yaml, seed = rep).

Every campaign gets its own folder .runs/<campaign>/ (default
<YYYY-MM-DD_HHMM>_det-<scenarios>; pass --campaign with an existing folder name
to resume it with --skip-existing). Run ids inside are det-<scenario>-<aqm>-r<rep>;
scenario copies with the AQM swapped go to <campaign>/_gen/. Each finished run
is scored (scripts/det_eval.py score) and the per-AQM x scenario tables are
written to <campaign>/det-report.{md,csv} (burst runs: det-burst-report.{md,csv}).
"""

from __future__ import annotations

import argparse
import datetime
import random
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / ".runs"
TOPOLOGY = ROOT / "configs" / "topologies" / "detector.yaml"
AQMS = {
    "pfifo": {},
    "red": {"red_min_bytes": 30_000, "red_max_bytes": 90_000},  # ~15 / 45 ms at 16 Mb/s
    "pie": {},
    "fq_codel": {},
    "dualpi2": {},
}
SCENARIOS = ["capacity", "cbr", "ppbp"]
BURST_SCENARIOS = ["burstcap", "burstudp"]

# Burst benchmark (configs/scenarios/det-burst.yaml): severity grid, played
# BURST_REPEATS times per run in a seeded random order with random calm gaps.
DEMAND_MBPS = 11.3      # measured wire rate of the four shared clients
BASE_MBPS = 17.5        # calm bottleneck capacity (u ~0.65)
BURST_U = (1.1, 1.3, 2.0)
BURST_S = (1, 2, 4)
BURST_REPEATS = 2
WARMUP_S, GAP_S, TAIL_S = 15.0, (10.0, 15.0), 10.0


def burst_events(kind: str, seed: int) -> tuple[list[dict], float]:
    """Scenario events for one burst run and its duration. Labels carry the
    designed severity; det_eval reads them back as ground truth."""
    rng = random.Random(seed)
    cells = [(u, s) for u in BURST_U for s in BURST_S] * BURST_REPEATS
    rng.shuffle(cells)
    t, plan = WARMUP_S, []
    for u, dur in cells:
        plan.append((round(t, 3), u, dur))
        t += dur + rng.uniform(*GAP_S)
    events = []
    if kind == "burstcap":
        for at, u, dur in plan:
            events += [
                {"at_s": at, "type": "link", "from": "router", "to": "switch",
                 "bandwidth_mbps": round(DEMAND_MBPS / u, 3), "label": f"burst u={u} d={dur}"},
                {"at_s": at + dur, "type": "link", "from": "router", "to": "switch",
                 "bandwidth_mbps": BASE_MBPS, "label": "burst-end"},
            ]
    else:
        events.append({"at_s": 0, "type": "bursts", "id": "udp-bursts", "route": "shared", "bursts": [
            {"start_s": at, "duration_s": dur, "rate_mbps": round(u * BASE_MBPS - DEMAND_MBPS, 3)}
            for at, u, dur in plan]})
    return events, round(t - GAP_S[0] + TAIL_S)


def scenario_for(name: str, aqm: str, rep: int = 1, campaign: Path = RUNS) -> Path:
    base = "burst" if name in BURST_SCENARIOS else name
    data = yaml.safe_load((ROOT / "configs" / "scenarios" / f"det-{base}.yaml").read_text())
    if name in BURST_SCENARIOS:
        # Same seed for every AQM: each repetition plays one burst sequence on all of them.
        data["events"], data["duration_s"] = burst_events(name, seed=rep)
    for router in data["routers"].values():
        limit = router.get("queue_limit_packets")
        router.clear()
        router.update({"aqm": aqm, "queue_limit_packets": limit, **AQMS[aqm]})
    out = campaign / "_gen" / f"det-{name}-{aqm}-r{rep}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(data, sort_keys=False))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--aqms", default=",".join(AQMS))
    ap.add_argument("--scenarios", default=",".join(SCENARIOS))
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--campaign", default=None, help="folder under .runs/ (default: timestamped)")
    args = ap.parse_args()
    name = args.campaign or (f"{datetime.datetime.now():%Y-%m-%d_%H%M}_det-"
                             + "-".join(args.scenarios.split(",")))
    campaign = RUNS / name
    campaign.mkdir(parents=True, exist_ok=True)
    print(f"campaign: {campaign}", flush=True)
    done = []
    for rep in range(1, args.reps + 1):
        for aqm in args.aqms.split(","):
            for scn in args.scenarios.split(","):
                run_id = f"det-{scn}-{aqm}-r{rep}"
                run_dir = campaign / run_id
                if not (args.skip_existing and (run_dir / "detector" / "detections.csv").exists()):
                    scenario = scenario_for(scn, aqm, rep, campaign)
                    print(f"== {run_id}", flush=True)
                    status = subprocess.run([sys.executable, "-m", "quiclab", "--runs-dir", str(campaign),
                                             "run", "-c", str(TOPOLOGY),
                                             "-s", str(scenario), "--run-id", run_id], cwd=ROOT)
                    if status.returncode != 0:
                        print(f"!! {run_id} failed ({status.returncode}); skipped", flush=True)
                        continue
                    det_eval.score(run_dir)
                done.append(run_dir)
                bursts = [r for r in done if det_eval.scenario_name(r) in BURST_SCENARIOS]
                others = [r for r in done if r not in bursts]
                if others:
                    text, table = det_eval.report(others)
                    (campaign / "det-report.md").write_text(text)
                    det_eval.write_csv(campaign / "det-report.csv", table)
                if bursts:
                    text, table = det_eval.burst_report(bursts)
                    (campaign / "det-burst-report.md").write_text(text)
                    det_eval.write_csv(campaign / "det-burst-report.csv", table)


if __name__ == "__main__":
    main()
