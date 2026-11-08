#!/usr/bin/env python3
"""Regenerate every ground-truth artefact of one or more campaigns with the
current truth defaults, so nothing on disk mixes settings.

    python3 scripts/truth_refresh.py TAG .runs/<campaign> [...]     # e.g. TAG 2026-11-05

Per run: truth/gt1.csv (+ -labels, -5ms), gt2.csv (+ -labels), gt3.csv (+ -labels),
truth/plots/. Per campaign: gt1-report.md, gt2-report.md, truth-plots.html,
TRUTH-SETTINGS.md. Across the campaigns (prefix .runs/TAG_...): gt3-report,
gt3-window-check, gt-bands-report, gt-detector-tables, owd-mode,
shadow-v2-step0, and .runs/TAG_TRUTH-SETTINGS.md.

TRUTH-SETTINGS.md records the three Params tags, the git commit (with -dirty
when the tree has changes) and a sha256 over the truth / scoring scripts, so a
report can be matched to the exact code that produced it.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import truth_plot  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
SCRIPTS = ("gt_bands.py", "gt1.py", "gt2.py", "gt3.py", "gt_score.py", "truth_plot.py", "det_eval.py")
CROSS = (  # (output prefix / file, argv after the python script)
    ("gt3-report.md", ["scripts/gt3_report.py"]),
    ("gt3-window-check.md", ["scripts/gt3_window_check.py"]),
    ("gt-bands-report.md", ["scripts/gt_bands_report.py"]),
    ("gt-detector-tables", ["scripts/gt_tables.py"]),
    ("owd-mode", ["scripts/owd_mode.py"]),
    ("shadow-v2-step0", ["scripts/shadow_v2_step0.py"]),
)


def settings_text() -> str:
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    h = hashlib.sha256()
    for name in SCRIPTS:
        h.update((ROOT / "scripts" / name).read_bytes())
    return "\n".join([
        "# Ground-truth settings used for every file in this folder", "",
        f"generated: {datetime.now().isoformat(timespec='seconds')}",
        f"git: {git}", f"scripts sha256 ({', '.join(SCRIPTS)}): {h.hexdigest()}", "",
        f"GT1: {gt1.Params().tag()}", f"GT2: {gt2.Params().tag()}", f"GT3: {gt3.Params().tag()}", "",
        "Decisions (2026-11-07): GT1 INTERVAL fixed 150 ms, queue band 2.5 ms, no util band; GT2 P_off 300 ms; "
        "GT3 persistence and merge 0.5 s (link-level truths use the 150 ms CoDel scale, the client-level truth "
        "the playout-buffer / RTT scale). The spec's 150 ms GT3 is reported as a sensitivity row in gt3-window-check.",
        "Scoring: gt_score (TP = first alarm in [t_on - 1 s, min(t_end, t_on + 10 s)], AMBIGUOUS / NO_DATA ignored, "
        "CLEAR = FP). Detector replay: det_eval.TUNED / PARAMS, grouping as stated in each report.", "",
    ])


def score_run(run_dir: Path) -> str:
    gt1.score(run_dir, gt1.Params())
    gt2.score(run_dir, gt2.Params())
    gt3.score(run_dir, gt3.Params())
    return truth_plot.plot(run_dir)


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        sys.exit(__doc__)
    tag, campaigns = argv[0], [Path(c) for c in argv[1:]]
    t0 = time.time()
    runs = sorted(r for c in campaigns for r in c.iterdir() if (r / "events.csv").exists())
    print(f"{len(runs)} runs in {len(campaigns)} campaigns", flush=True)
    with ProcessPoolExecutor(max_workers=12) as pool:
        for line in pool.map(score_run, runs):
            print("  " + line, flush=True)
    print(f"per-run truths and plots: {time.time() - t0:.0f} s", flush=True)
    for c in campaigns:
        truth_plot.index(c, sorted(r for r in runs if r.parent == c))
        gt1.report(c, gt1.Params())
        gt2.report(c, gt2.Params())
        (c / "TRUTH-SETTINGS.md").write_text(settings_text())
        print(f"{c.name}: gt1-report, gt2-report, truth-plots.html, TRUTH-SETTINGS.md ({time.time() - t0:.0f} s)", flush=True)
    runs_dir = campaigns[0].parent
    for out, argv_ in CROSS:
        t1 = time.time()
        subprocess.run([PY, *argv_, str(runs_dir / f"{tag}_{out}"), *map(str, campaigns)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
        print(f"{out}: {time.time() - t1:.0f} s", flush=True)
    (runs_dir / f"{tag}_TRUTH-SETTINGS.md").write_text(settings_text())
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
