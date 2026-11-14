#!/usr/bin/env python3
"""Why the two false-alarm numbers differ (read-only).

    python3 reports/baselines-2026-11-12/fa_reconcile.py RUN_DIR...

For each run, the v2-owd alarm starts (after warm-up) are classified twice:
  e2e (grouping report, e2e_score.py): false = not inside a planned stimulus window
      the client is expected in (window end + 2 s); per minute of run time, all
      clients summed.
  gt_score (baseline table): false = inside CLEAR time of the client's GT1 view
      (outside every GT1 episode and AMBIGUOUS band on its path, outside the
      detection window of an episode); per minute of CLEAR time summed over clients.
The e2e false alarms are then split by what GT1 says at the alarm: inside a GT1
episode (real queue the plan did not script), AMBIGUOUS, or CLEAR.
Also: planned-window recall (share of expected clients that alarm in a shared
window) next to the GT1 episode recall.
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import gt1, gt_bands, gt_score, shadow_v2_frozen  # noqa: E402

print("| run | alarms | e2e false | of them: in GT1 episode / AMBIGUOUS / CLEAR | e2e FA/min (run min x clients) | "
      "gt_score FP | gt_score FA/min (CLEAR min) | CLEAR share of client time | planned-window recall | GT1 episode recall |")
print("|---|---|---|---|---|---|---|---|---|---|")
for rd in map(Path, sys.argv[1:]):
    run = ga.load_run(rd)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    view = gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1)
    eps = shadow_v2_frozen.episodes(run, "v2", mode="OWD", hold=True)
    starts = {("x", s): [a for a, _, _ in v] for s, v in eps.items()}
    sc = gt_score.score(run, view, starts, ("x",))["x"]
    windows = json.loads((rd / "grouping" / "windows.json").read_text())
    win = {s: [(w["start"], w["end"] + d.BURST_RECOVERY_S) for w in windows if s in w.get("expected", [])] for s in run.subs}
    n_al = n_false = 0
    cls = {"episode": 0, "ambiguous": 0, "clear": 0}
    for s, spans in eps.items():
        ep_s, code = view[s]
        for a, _, _ in spans:
            if a < d.WARMUP_S:
                continue
            n_al += 1
            if any(lo <= a <= hi for lo, hi in win[s]):
                continue
            n_false += 1
            c = code[min(len(code) - 1, int(a / gt_score.GRID_S))]
            if any(x - d.PRE_ONSET_LEAD_S <= a <= y for x, y in ep_s):
                cls["episode"] += 1
            elif c == gt_score.RANK[gt_bands.AMBIGUOUS]:
                cls["ambiguous"] += 1
            else:
                cls["clear"] += 1
    minutes = (run.duration - d.WARMUP_S) / 60
    clear_min = sc["clear_s"] / 60
    tot_client_min = minutes * len(run.subs)
    shared = [w for w in windows if len(w.get("expected", [])) >= 2]
    hit = [any(w["start"] <= a <= w["end"] + d.BURST_RECOVERY_S for a, _, _ in eps.get(s, [])) for w in shared for s in w["expected"]]
    print(f"| {rd.parent.name}/{rd.name} | {n_al} | {n_false} | {cls['episode']} / {cls['ambiguous']} / {cls['clear']} "
          f"| {n_false / minutes:.2f} | {sc['fp']} | {sc['fp'] / clear_min if clear_min else float('nan'):.2f} "
          f"| {clear_min / tot_client_min:.2f} | {np.mean(hit) if hit else float('nan'):.2f} "
          f"| {sc['detected'] / sc['episodes'] if sc['episodes'] else float('nan'):.2f} |")
