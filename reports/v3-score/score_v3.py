#!/usr/bin/env python3
"""Suite v3 scoring driver (brief of 2026-11-15). Measurement only: existing functions are called
unchanged; the detector (frozen Shadow v2, ip4 values), ECG v1.2 and h3 are not changed.

    .venv/bin/python3 reports/v3-score/score_v3.py detector  CAMPAIGN   -> det-rows.jsonl
    .venv/bin/python3 reports/v3-score/score_v3.py grouping  CAMPAIGN   -> grp-a.jsonl, grp-b.jsonl, grp-s5.jsonl
    .venv/bin/python3 reports/v3-score/score_v3.py catalog   CAMPAIGN   -> calm-load.jsonl

detector: reports/ppbp-diagnosis-2026-11-14/ppbp.py run_row on every run (GT1, GT3 source A as that
  script builds it, frame-latency harm, v2 / v2-fixed OWD episodes with start / overlap detection,
  F1 baseline state); the per-second state series is dropped from the rows.
grouping: ECG v1.2 (grouping_campaign.score_run, Config ENGINE_SET, delta 0.150 s, tag d150) with three
  onset sources: v2-owd, v2-fixed-owd, truth (burst hits). The Step 6 / 7 / 5 functions read the ECG
  output from the fixed dir grouping-d150-v2-owd, so each source is scored through a view folder
  (VIEWS/<source>/<campaign>/<run>: symlinks to the run's files, with grouping-d150-v2-owd pointing at
  that source's output). Per run and source: step7.a_row (ECG / h3 per-event truths, B1 votes, egress
  congestion shares in ECG events), step7.b_row (per-close coverage, tree, losses, sibling merge),
  grouping_step5.step5_run (B2 votes, Part A memberships).
catalog: scripts/scenario_catalog.calm_load on every run (measured calm load and video share per egress).

Runs for grouping (T): every run of C7 C8 C9 C10 C11 C12 C13 M6 M7 M8, plus C2 pfifo (the default point
next to M6).
"""

from __future__ import annotations

import json
import math
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reports" / "ppbp-diagnosis-2026-11-14"))
sys.path.insert(0, str(ROOT / "reports" / "step6-2026-11-14"))
sys.path.insert(0, str(ROOT / "reports" / "step7-2026-11-14"))

SOURCES = ("v2-owd", "v2-fixed-owd", "truth")
GROUP_BLOCKS = ("C7", "C8", "C9", "C10", "C11", "C12", "C13", "M6", "M7", "M8")
VIEWS = Path(os.environ.get("V3_VIEWS", "/tmp/claude-1001/-home-ubuntu-Research-Repos-multirelay/"
                                          "5363924b-068f-4123-bf1c-f65ab759cae3/scratchpad/views"))
JOBS = 12


def _json(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    if hasattr(o, "item"):
        return o.item()
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    return str(o)


def runs_of(kdir: Path) -> list[Path]:
    return sorted(p for p in kdir.iterdir() if p.is_dir() and p.name.startswith("v3-"))


def det_one(rd: Path):
    import ppbp
    row = ppbp.run_row(rd)
    for v in row["state"].values():
        v.pop("series", None)
    return row


def cat_one(rd: Path):
    import scenario_catalog
    return scenario_catalog.calm_load(rd)


def grp_runs(kdir: Path) -> list[Path]:
    out = []
    for rd in runs_of(kdir):
        b = rd.name.split("-")[1]
        if b in GROUP_BLOCKS or (b == "C2" and "-pfifo-" in rd.name):
            out.append(rd)
    return out


def ecg_one(rd: Path):
    import grouping_campaign as gc
    from grouping import Config
    cfg = Config.from_dict(gc.ENGINE_SET)
    res = gc.score_run(rd, cfg, tag="d150", sources=SOURCES, with_baselines=False)
    return {k: ("error" in v) if isinstance(v, dict) else v for k, v in res["ecg"].items()}


def view(rd: Path, src: str) -> Path:
    rd = rd.resolve()
    v = VIEWS / src / rd.parent.name / rd.name
    v.mkdir(parents=True, exist_ok=True)
    for p in rd.iterdir():
        if p.name.startswith("grouping-d150-"):
            continue
        link = v / p.name
        if not link.exists():
            link.symlink_to(p)
    link = v / "grouping-d150-v2-owd"
    target = rd / f"grouping-d150-{src}"
    if link.is_symlink() and os.readlink(link) != str(target):
        link.unlink()
    if not link.exists():
        link.symlink_to(target)
    return v


def grp_one(args):
    rd, src = args
    import grouping_step5 as s5
    import step7
    v = view(rd, src)
    out = {"run": rd.name, "source": src}
    for name, fn in (("a", lambda: step7.a_row(("sync", v))), ("b", lambda: step7.b_row(("sync", v))),
                     ("s5", lambda: s5.step5_run(v))):
        try:
            out[name] = fn()
        except Exception as e:  # noqa: BLE001
            out[name] = {"error": repr(e), "trace": traceback.format_exc()[-600:]}
    return out


def pool_write(fn, items, path: Path):
    n = 0
    with ProcessPoolExecutor(JOBS) as ex, path.open("w") as fh:
        for it, fut in [(it, ex.submit(fn, it)) for it in items]:
            try:
                fh.write(json.dumps(fut.result(), default=_json) + "\n")
            except Exception as e:  # noqa: BLE001
                fh.write(json.dumps({"item": str(it), "error": repr(e)}) + "\n")
            fh.flush()
            n += 1
            print(f"{path.name}: {n}/{len(items)}", flush=True)


def main(argv):
    cmd, kdir = argv[0], Path(argv[1])
    if cmd == "detector":
        pool_write(det_one, runs_of(kdir), HERE / "det-rows.jsonl")
    elif cmd == "catalog":
        pool_write(cat_one, runs_of(kdir), HERE / "calm-load.jsonl")
    elif cmd == "grouping":
        runs = grp_runs(kdir)
        pool_write(ecg_one, runs, HERE / "grp-ecg.jsonl")
        pool_write(grp_one, [(rd, s) for rd in runs for s in SOURCES], HERE / "grp-rows.jsonl")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
