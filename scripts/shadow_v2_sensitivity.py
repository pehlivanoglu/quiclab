#!/usr/bin/env python3
"""Sensitivity of v2 / v2-fixed to the two fitted values: the sigma floors and G_ref.

    python3 scripts/shadow_v2_sensitivity.py OUT_DIR .runs/<campaign> [...]   # -> OUT_DIR/sensitivity.md, sensitivity.csv

Baseline = the values shadow_v2_report.py derives with the frozen rules (RTT ticks). Each configuration scales them:
  - G_ref x m (floors at baseline): what if the FA-budget rule had picked another threshold;
  - all floors x m, G_ref held at baseline: raw effect of the floors;
  - all floors x m, G_ref re-fitted by the Step 3 rule: end-to-end effect of the floor choice;
  - one floor x m at a time, G_ref held.
The v2-fixed scale is recomputed with the scaled floors (it uses max(std, floor)). Detector, truths and scoring are
unchanged (theta_on 0.25, gt_score window, GT1 / GT2 / GT3 + path).
"""

from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_report as rep  # noqa: E402
import shadow_v2_results as res_mod  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402
import shadow_v2_step5 as s5  # noqa: E402

FEATS = ("F1", "F2", "F3", "F4")
LABELS = tuple(rep.V2)
CONFIGS: list[dict] = []  # {"name", "group", "floors", "stats", "g_ref"} (set before the pool forks)


def set_floors(floors: dict[str, float]) -> None:
    s3.FLOORS.clear()
    s3.FLOORS.update(floors)


def fit_g(args):
    floors, stats, label, calm_dirs = args
    set_floors(floors)
    s3.FIXED_STATS.clear()
    s3.FIXED_STATS.update(stats)
    return res_mod.fit_g_ref(rep.V2[label], calm_dirs)


def worker(run_dir: Path) -> dict:
    run = d.Run(run_dir)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params())
    views = {"GT1": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             "GT2": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2),
             "GT3": gt3.view_of(run, e3, l3, need_path=True)}
    starts = {}
    for c in CONFIGS:
        set_floors(c["floors"])
        s3.FIXED_STATS.clear()
        s3.FIXED_STATS.update(c["stats"])
        flows = s3.load_flows(run_dir)
        for label in LABELS:
            for s, df in flows.items():
                r = s3.run_cusum(df, rep.V2[label], c["g_ref"][label], False)
                starts[(f"{c['name']}|{label}", s)] = rep.spans_to_starts(s5.on_spans(r, rep.THETA))
    dets = tuple(sorted({k for k, _ in starts}))
    return {t: gt_score.score(run, v, starts, dets) for t, v in views.items()}


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    run_dirs = sorted(r for c in argv[1:] for r in Path(c).iterdir() if (r / "events.csv").exists())
    pfifo_r1 = [r for r in run_dirs if r.name.endswith("-pfifo-r1")]
    calm_dirs = [r for r in pfifo_r1 if r.name.split("-")[1] in s3.CALM_RUNS]
    s3.TICKS_DIR = rep.MODES["RTT"]

    base_floors = rep.floors_for(pfifo_r1)

    def stats_for(floors):
        set_floors(floors)
        return s3.fixed_stats(calm_dirs)

    variants = [("baseline", "baseline", base_floors)]
    for m in (0.25, 0.5, 2.0, 4.0, 10.0, 30.0):
        variants.append((f"floors x{m:g}", "floors all", {f: v * m for f, v in base_floors.items()}))
    for f in FEATS:
        for m in (0.5, 2.0):
            variants.append((f"{f} floor x{m:g}", "floor one", {**base_floors, f: base_floors[f] * m}))
    stats = {name: stats_for(fl) for name, _, fl in variants}
    jobs = [(name, label) for name, grp, _ in variants if grp in ("baseline", "floors all") for label in LABELS]
    fl_of = {name: fl for name, _, fl in variants}
    with ProcessPoolExecutor(max_workers=8) as pool:
        fitted = dict(zip(jobs, pool.map(fit_g, [(fl_of[n], stats[n], lab, calm_dirs) for n, lab in jobs])))
    base_g = {lab: fitted[("baseline", lab)] for lab in LABELS}

    CONFIGS.append({"name": "baseline", "group": "baseline", "floors": base_floors, "stats": stats["baseline"], "g_ref": base_g})
    for m in (0.5, 0.75, 1.25, 1.5, 2.0):
        CONFIGS.append({"name": f"G_ref x{m:g}", "group": "G_ref", "floors": base_floors, "stats": stats["baseline"],
                        "g_ref": {lab: g * m for lab, g in base_g.items()}})
    for name, grp, fl in variants[1:]:
        CONFIGS.append({"name": name + (" (G_ref held)" if grp == "floors all" else ""), "group": grp, "floors": fl,
                        "stats": stats[name], "g_ref": base_g})
        if grp == "floors all":
            CONFIGS.append({"name": name + " (G_ref refit)", "group": "floors all refit", "floors": fl, "stats": stats[name],
                            "g_ref": {lab: fitted[(name, lab)] for lab in LABELS}})

    with ProcessPoolExecutor(max_workers=20) as pool:
        res = list(pool.map(worker, run_dirs))

    rows = []
    for c in CONFIGS:
        for label in LABELS:
            row = {"config": c["name"], "group": c["group"], "detector": label, "g_ref": round(c["g_ref"][label], 1),
                   **{f"floor_{f}": round(c["floors"][f], 5) for f in FEATS}}
            for t in ("GT1", "GT2", "GT3"):
                s = gt_score.summarize([r[t][f"{c['name']}|{label}"] for r in res])
                row[f"{t}_recall"], row[f"{t}_precision"] = s["recall"], s["precision"]
                if t == "GT3":
                    row["GT3_fa_per_min"], row["GT3_p50_ms"], row["GT3_p90_ms"] = (s["fa_per_min"], s["late_latency_p50_ms"],
                                                                                    s["latency_p90_ms"])
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(out / "sensitivity.csv", index=False)

    cols = ["config", "G_ref", "GT3 P", "GT3 R", "FA/min", "p50", "p90", "GT1 R", "GT2 R"]
    L = ["# Shadow v2 sensitivity: sigma floors and G_ref", "",
         f"{len(run_dirs)} runs ({', '.join(Path(c).name for c in argv[1:])}), RTT ticks, theta_on {rep.THETA}.", "",
         "Baseline floors " + ", ".join(f"{f} {v:.4g}" for f, v in base_floors.items())
         + "; G_ref " + ", ".join(f"{k} {v:.1f}" for k, v in base_g.items()) + ".", ""]
    for label in LABELS:
        L += [f"## {label}", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        for _, r in df[df.detector == label].iterrows():
            L.append(f"| {r.config} | {r.g_ref:.1f} | {r.GT3_precision:.2f} | {r.GT3_recall:.2f} | {r.GT3_fa_per_min:.2f} | "
                     f"{r.GT3_p50_ms:.0f} | {r.GT3_p90_ms:.0f} | {r.GT1_recall:.2f} | {r.GT2_recall:.2f} |")
        L.append("")
    (out / "sensitivity.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
