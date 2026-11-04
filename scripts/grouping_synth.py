#!/usr/bin/env python3
"""Run the ECG synthetic scenarios (brief v1.1 §8) over seeds and profiles,
write metrics, L plots and a pass/fail table.

    python scripts/grouping_synth.py                      # S1-S6, both profiles, 10 seeds
    python scripts/grouping_synth.py --scenarios S4,S6 --seeds 3 --set theta_J=0.6 theta_cov=0.6
    python scripts/grouping_synth.py --sweep theta_J=0.6,0.7 --sweep theta_cov=0.6,0.7
    python scripts/grouping_synth.py --write-log          # also keep the onset logs (large)

Output: .runs/<YYYY-MM-DD_HHMM>_grouping-synth/ with table.md, per-run
metrics JSON under <scenario>/<profile>/, L plots for every run, and
evidence.jsonl for seed 0 of every cell.
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from grouping import replay, synth  # noqa: E402
from grouping.invariants import Invariants  # noqa: E402
from grouping.engine import Engine  # noqa: E402

KEY_METRICS = {
    "S1": ["events_to_leaf"], "S2": ["drift"], "S3": ["private_fraction", "true_private_fraction"],
    "S4": ["agg_after_confirm"], "S5": ["f2_events_to_member", "f3_in_B_by_3rd_B_event", "f5_member_idle"],
    "S6": ["G1_cases", "root_cases", "no_false_leaf"],
}


def parse_set(items: list[str]) -> dict:
    out = {}
    for it in items:
        k, v = it.split("=", 1)
        out[k] = json.loads(v) if v[0] in "[{" or v in ("true", "false", "null") else _num(v)
    return out


def _num(v: str):
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def run_cell(sid: str, profile: str, seed: int, over: dict, out: Path, keep_log: bool, write_log: bool) -> dict:
    sc = synth.SCENARIOS[sid]()
    prof = synth.PROFILES[profile]
    cfg = synth.config_for(prof, **over)
    records, truth = synth.generate(sc, prof, seed)
    cell = out / sid / profile
    cell.mkdir(parents=True, exist_ok=True)
    if write_log:
        synth.write_log(records, cell / f"seed{seed}-onsets.jsonl")
        (cell / f"seed{seed}-truth.json").write_text(json.dumps(truth, indent=1))
    holder = {}

    def factory(_records, cfg_, log=None):
        eng = Engine(cfg_, log)
        holder["inv"] = Invariants(eng)
        return eng
    res = replay.run(records, cfg, log_path=(cell / f"seed{seed}-evidence.jsonl") if keep_log else None,
                     engine_factory=factory)
    ok, detail = replay.check(sid, res, truth)
    m = replay.metrics(res, truth)
    m.update({"ok": ok, "detail": detail, "seed": seed, "profile": profile, "scenario": sid,
              "overrides": over, "invariants_checked": holder["inv"].n_checked})
    replay.dump(m, cell / f"seed{seed}-metrics.json")
    replay.plot_L(res, cell / f"seed{seed}-L.png", f"{sid} {sc.note} | {profile} seed {seed} | {over or 'defaults'}")
    return m


def fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.2f}"
    if isinstance(v, Counter):
        return ",".join(f"{k}:{n}" for k, n in sorted(v.items()))
    return str(v)


def table(results: list[dict], scenarios: list[str], profiles: list[str], sweeps: list[dict]) -> str:
    lines = ["| scenario | profile | overrides | pass | key metrics (median / per seed) |", "|---|---|---|---|---|"]
    for over in sweeps:
        for sid in scenarios:
            for prof in profiles:
                rows = [r for r in results if r["scenario"] == sid and r["profile"] == prof and r["overrides"] == over]
                if not rows:
                    continue
                n_ok = sum(r["ok"] for r in rows)
                keys = []
                for k in KEY_METRICS[sid]:
                    vals = [r["detail"].get(k) for r in rows]
                    nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
                    if nums and len(nums) == len(vals):
                        keys.append(f"{k}={statistics.median(nums):.2f}")
                    else:
                        keys.append(f"{k}=[{' '.join(fmt(v) for v in vals)}]")
                lines.append(f"| {sid} | {prof} | {over or 'defaults'} | {n_ok}/{len(rows)} | {'; '.join(keys)} |")
    return "\n".join(lines)


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenarios", default="S1,S2,S3,S4,S5,S6")
    ap.add_argument("--profiles", default="ideal,realistic")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE", help="config overrides")
    ap.add_argument("--sweep", action="append", default=[], metavar="KEY=V1,V2", help="cartesian sweep")
    ap.add_argument("--out", type=Path, help="output dir (default .runs/<ts>_grouping-synth)")
    ap.add_argument("--write-log", action="store_true", help="also write the onset logs")
    a = ap.parse_args(argv)
    scenarios, profiles = a.scenarios.split(","), a.profiles.split(",")
    base = parse_set(a.set)
    sweep_keys, sweep_vals = [], []
    for s in a.sweep:
        k, v = s.split("=", 1)
        sweep_keys.append(k)
        sweep_vals.append([_num(x) for x in v.split(",")])
    sweeps = [{**base, **dict(zip(sweep_keys, combo))} for combo in itertools.product(*sweep_vals)] or [base]
    out = a.out or ROOT / ".runs" / f"{datetime.now():%Y-%m-%d_%H%M}_grouping-synth"
    out.mkdir(parents=True, exist_ok=True)
    results, t0 = [], time.time()
    for over in sweeps:
        for sid in scenarios:
            for prof in profiles:
                for seed in range(a.seeds):
                    sub = out if len(sweeps) == 1 else out / "sweep" / "_".join(f"{k}{v}" for k, v in over.items())
                    results.append(run_cell(sid, prof, seed, over, sub, keep_log=seed == 0, write_log=a.write_log))
                    print(f"{sid} {prof} seed {seed} {over or ''}: {'pass' if results[-1]['ok'] else 'FAIL'} "
                          f"cases={results[-1]['cases']}", flush=True)
    md = table(results, scenarios, profiles, sweeps)
    (out / "table.md").write_text(f"# ECG synthetic scenarios\n\nseeds={a.seeds}, {time.time() - t0:.0f} s\n\n{md}\n")
    (out / "results.json").write_text(json.dumps(results, indent=1, default=replay._default))
    print(f"\n{md}\n\nwritten to {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
