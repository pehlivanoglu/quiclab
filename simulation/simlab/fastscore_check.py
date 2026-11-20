#!/usr/bin/env python3
"""Acceptance check of the fast scoring path (fastscore.py) against the frozen path's outputs (user 2026-11-19, W5).

    nice -n 19 .venv/bin/python3 simulation/simlab/fastscore_check.py b2 <scratch dir> [--only NAME]
    nice -n 19 .venv/bin/python3 simulation/simlab/fastscore_check.py run300 <scratch dir>     # heavy: no campaign

For every run: a copy of the run folder in <scratch dir>/<batch>/<run> (real files; router-trace left out, it is not
read by GT3 or SETS; truth/ starts empty), so nothing is ever written into the original run. Same parent folder name
as the original, so the frozen tick files are found in reports/sim-cache (read only). The fast path then writes
truth/gt3.csv and truth/gt3-labels.csv into the copy and computes the SETS rows.

Compared with the frozen path's outputs of the same run:
  truth/gt3.csv, truth/gt3-labels.csv   byte for byte against the original run's files
  GT3 summary line                      against sim/scored.json "gt3" (b2) / the frozen re-run (run300)
  SETS rows                             JSON-identical (same floats) against rows-<ack>.jsonl "sim" -> "sets" (b2),
                                        against sim/sets.json (run300)
One differing byte stops the check (exit 1) and is reported. Writes <scratch>/fastscore-check.jsonl and prints
a markdown table.
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import fastscore  # noqa: E402

B2 = QUICLAB / "simulation" / "runs" / "stageB2-applimited"
ROWS = QUICLAB / "reports" / "sim-stageB2-applimited"
RUN300 = QUICLAB / "simulation" / "runs" / "scale300" / "sim-Cs-G1-sburst-n300-pfifo-r1"
SKIP = {"router-trace"}


def copy_run(src: Path, dst: Path) -> None:
    if dst.exists():
        sys.exit(f"{dst} exists: give an empty scratch dir")
    dst.mkdir(parents=True)
    for p in src.iterdir():
        if p.name in SKIP:
            continue
        if p.name == "truth":
            (dst / "truth").mkdir()
        elif p.is_dir():
            shutil.copytree(p, dst / p.name, symlinks=False)
        else:
            shutil.copy2(p, dst / p.name)


def canon(x) -> str:
    return json.dumps(x, sort_keys=True, default=str)


def cases(kind: str):
    if kind == "b2":
        for ack in ("matched", "spec"):
            rows = {r["name"]: r for r in map(json.loads, (ROWS / f"rows-{ack}.jsonl").read_text().splitlines())}
            for rd in sorted((B2 / ack).iterdir()):
                if not (rd / "sim" / "scored.json").exists():
                    continue
                yield ack, rd, rows.get(rd.name, {}).get("sim", {}).get("sets"), \
                    json.loads((rd / "sim" / "scored.json").read_text())["gt3"], \
                    Path(json.loads((rd / "sim" / "meta.json").read_text())["testbed_run"])
    else:
        yield "scale300", RUN300, json.loads((RUN300 / "sim" / "sets.json").read_text()), \
            json.loads((RUN300 / "sim" / "scored.json").read_text())["gt3"], RUN300.parent / "plan-n300"


def main(argv: list[str]) -> int:
    kind, scratch = argv[0], Path(argv[1])
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    out = scratch / "fastscore-check.jsonl"
    print("| batch | run | gt3.csv | gt3-labels.csv | GT3 line | SETS rows | CPU s |")
    print("|---|---|---|---|---|---|---|")
    bad = 0
    for batch, rd, sets_ref, line_ref, cfg_from in cases(kind):
        if only and only not in rd.name:
            continue
        cp = scratch / batch / rd.name
        copy_run(rd, cp)
        t = time.process_time()
        line, sets = fastscore.light_score(cp, cfg_from)
        cpu = time.process_time() - t
        res = {"batch": batch, "run": rd.name, "cpu_s": round(cpu, 1),
               "gt3.csv": (cp / "truth" / "gt3.csv").read_bytes() == (rd / "truth" / "gt3.csv").read_bytes(),
               "gt3-labels.csv": (cp / "truth" / "gt3-labels.csv").read_bytes() == (rd / "truth" / "gt3-labels.csv").read_bytes(),
               "gt3_line": line == line_ref,
               "sets": sets_ref is not None and canon(json.loads(canon(sets))) == canon(sets_ref)}
        ok = all(res[k] for k in ("gt3.csv", "gt3-labels.csv", "gt3_line", "sets"))
        with out.open("a") as f:
            f.write(json.dumps(res | ({} if ok else {"line": line, "line_ref": line_ref,
                                                     "sets_ref_missing": sets_ref is None})) + "\n")
        print(f"| {batch} | {rd.name} | " + " | ".join("same" if res[k] else "**DIFFERS**"
                                                        for k in ("gt3.csv", "gt3-labels.csv", "gt3_line", "sets"))
              + f" | {res['cpu_s']} |", flush=True)
        if not ok:
            bad += 1
            print(f"\nSTOP: {rd.name} differs (details in {out}); nothing further checked.")
            return 1
    print(f"\nall identical ({out})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
