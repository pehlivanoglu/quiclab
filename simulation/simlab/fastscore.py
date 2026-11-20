#!/usr/bin/env python3
"""Fast scoring path for GT3 + SETS (user 2026-11-19, W5). Next to the frozen scorer; no frozen file is changed.

The frozen path rebuilds det_eval.Run (three YAML / CSV parses) twice per client inside every gt3.run_truth call,
and computes GT3 twice per run (the GT3 step, and again inside the SETS onset building via
grouping_adapter.truth_of). Both are quadratic in clients through the YAML size. Here, inside one process:

  1. det_eval.Run(path): the parsed attributes are kept per run (keyed by the resolved path and the three input
     files' size / mtime) and every call gets a fresh object restored from a pickle of them, so no caller can
     change another caller's object; `path` is the argument of this call, as in the frozen class.
  2. gt3.flow_truth(run, sid, p, source): kept per (run path, client, parameters, source); every call gets a fresh
     copy (pickle) of the result. gt3.run_truth itself is unchanged, so path_queues (True in the GT3 step, False
     inside SETS) is applied as before.

    from fastscore import light_score   # GT3 step + SETS step of one run, one process
    gt3_line, sets = light_score(run_dir, cfg_from)

Accepted only if its outputs are byte-identical to the frozen path (fastscore_check.py); until then stage C uses
the frozen path.
"""

from __future__ import annotations

import contextlib
import io
import pickle
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scale_ext  # noqa: E402,F401
import frozen  # noqa: E402,F401
import stageb_compare  # noqa: E402  (sys.path for scripts/, r1)

import det_eval  # noqa: E402
import gt3  # noqa: E402

_FrozenRun = det_eval.Run
_frozen_flow_truth = gt3.flow_truth
_RUNS: dict[tuple, bytes] = {}
_FLOWS: dict[tuple, bytes] = {}


def _key(path: Path) -> tuple:
    p = Path(path).resolve()
    st = tuple((f, (p / f).stat().st_size, (p / f).stat().st_mtime_ns) for f in ("topology.yaml", "scenario.yaml", "events.csv"))
    return (str(p),) + st


class CachedRun(_FrozenRun):
    def __init__(self, path: Path):   # noqa: D107  (no super().__init__: the attributes come from the cache)
        k = _key(path)
        blob = _RUNS.get(k)
        if blob is None:
            blob = pickle.dumps({a: v for a, v in vars(_FrozenRun(path)).items() if a != "path"})
            _RUNS[k] = blob
        self.__dict__.update(pickle.loads(blob))
        self.path = path


def flow_truth(run, sid, p=gt3.Params(), source="auto"):
    k = (str(Path(run.path).resolve()), sid, repr(p), source)
    blob = _FLOWS.get(k)
    if blob is None:
        blob = pickle.dumps(_frozen_flow_truth(run, sid, p, source))
        _FLOWS[k] = blob
    return pickle.loads(blob)


def install() -> None:
    det_eval.Run = CachedRun
    gt3.flow_truth = flow_truth


def clear() -> None:
    _RUNS.clear()
    _FLOWS.clear()


def light_score(run_dir: Path, cfg_from: Path) -> tuple[str, dict]:
    """The GT3 step (truth/gt3.csv, truth/gt3-labels.csv, its summary line) and the SETS step (stageb_compare
    .sets_scores) of one run, as the frozen path computes them, in one process with the caches above."""
    install()
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gt3.score(Path(run_dir))
        line = (buf.getvalue().strip().splitlines() or [""])[-1]
        sets = stageb_compare.sets_scores(Path(run_dir), Path(cfg_from))
        return line, sets
    finally:
        clear()
