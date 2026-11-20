"""Frozen detector access that never writes into a run folder.

shadow_v2_frozen.tick_files builds <run>/shadow-v2/ when it is missing; on a testbed run under
.runs/ that is forbidden (simulation spec section 0). Same mechanism as
reports/npr-step0-2026-11-17/npr0.py: tick_files is replaced by a version that looks for
existing tick files (the run folder, then the NPR session's cache, read-only) and builds
missing ones only under CACHE. Simulation runs are treated the same way, so every run's
tick files come from one code path.

    from frozen import episodes
    episodes(Path(run_dir))  -> {client: [(t_alarm, t_end, t_onset), ...]}   (v2, OWD, hold)
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB))
sys.path.insert(0, str(QUICLAB / "scripts"))

import det_eval as d  # noqa: E402
import owd_mode  # noqa: E402
import shadow_v2_frozen as fz  # noqa: E402
import shadow_v2_step1 as s1  # noqa: E402

import os  # noqa: E402

# Tick-file cache. Stage C (user 2026-11-19, W2) points it outside quiclab/ with QUICLAB_SIM_TICK_CACHE;
# every other use keeps reports/sim-cache.
CACHE = Path(os.environ["QUICLAB_SIM_TICK_CACHE"]) if os.environ.get("QUICLAB_SIM_TICK_CACHE") \
    else QUICLAB / "reports" / "sim-cache"
READ_ONLY = [QUICLAB / "reports" / "npr-step0-2026-11-17" / "cache"]


def _tick_files(run: d.Run, mode: str) -> dict[str, Path]:
    owd = mode == "OWD"
    sub = "ticks-frozen-owd" if owd else "ticks-frozen"
    key = Path(run.path.parent.name) / run.path.name / "shadow-v2"
    for base in [run.path / "shadow-v2", *[r / key for r in READ_ONLY], CACHE / key]:
        files = {s: base / sub / f"{s}.csv" for s in run.subs}
        if all(f.exists() for f in files.values()):
            return files
    base = CACHE / key
    if base.resolve().is_relative_to(run.path.resolve()):
        raise RuntimeError(f"refusing to build tick files inside {run.path}")
    dump = base / ("v1-samples-owd" if owd else "v1-samples")
    if not all((dump / f"{s}.csv").exists() for s in run.subs):
        with tempfile.TemporaryDirectory() as tmp:
            acks = {s: owd_mode.owd_acks(run, s, Path(tmp)) for s in run.subs} if owd else None
            d.replay(run, d.TUNED, samples_to=dump, acks=acks, grouping="none")
    out = base / sub
    out.mkdir(parents=True, exist_ok=True)
    files = {s: out / f"{s}.csv" for s in run.subs}
    no_truth = np.zeros(1, dtype=int)
    for s, f in files.items():
        rate = run.topology["subscribers"][s]["rate_kbps"] * 1000
        s1.ticks_for(run, s, dump, no_truth, rate, s1.tick_s(run)).to_csv(f, index=False)
    return files


fz.tick_files = _tick_files


def episodes(run_dir: Path, mode: str = "OWD") -> dict[str, list[tuple]]:
    """The frozen v2 detector's alarm episodes per client (hold on), as the grouping pipelines use."""
    return fz.episodes(d.Run(run_dir), "v2", mode=mode, hold=True)
