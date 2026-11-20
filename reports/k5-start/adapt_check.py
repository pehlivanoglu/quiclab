#!/usr/bin/env python3
"""K5 gate adaptation check (user, 2026-11-19): did CC-driven adaptation engage in the gate's adaptation run?
Reading only; nothing is written in the run folder. Output: stdout and reports/k5-start/adapt-check.md.

    .venv/bin/python3 reports/k5-start/adapt_check.py [K5 campaign folder]   # default: newest .runs/*_v4-K5
"""

from __future__ import annotations

import csv
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "adapt-check.md"
FLOOR = 0.3   # (P) user 2026-11-17, k5_suite.ADAPT_FLOOR


def main(argv):
    camps = [Path(argv[0])] if argv else sorted(Path(p) for p in glob.glob(str(ROOT / ".runs" / "*_v4-K5")))
    if not camps:
        print("no K5 campaign folder")
        return 2
    runs = sorted(Path(p) for p in glob.glob(str(camps[-1] / "v4-GATE-sburst-adapt-*")) if Path(p).is_dir())
    if not runs:
        print(f"no gate adaptation run in {camps[-1]} yet")
        return 2
    rd = runs[-1]
    finished = (rd / "v3-checks.json").exists()
    files = sorted(rd.rglob("*-adapt.csv"))
    lines = [f"# K5 gate adaptation check\n", f"Run: {rd} (finished: {'yes' if finished else 'no, still running'})\n"]
    if not files:
        lines.append("**No -adapt.csv found: adaptation did not engage (or the run has not reached the server start).**")
        ok = False
    else:
        ok = True
        lines.append("| file | rows | rows scale < 1 | share | lowest scale | floor reached (scale <= 0.3) |")
        lines.append("|---|---|---|---|---|---|")
        for f in files:
            sc = [float(r["scale"]) for r in csv.DictReader(f.open())]
            below = [x for x in sc if x < 1.0]
            low = min(sc) if sc else None
            lines.append(f"| {f.relative_to(rd)} | {len(sc)} | {len(below)} | "
                         f"{len(below) / len(sc):.3f} | {low if low is None else f'{low:.3f}'} | "
                         f"{'yes' if low is not None and low <= FLOOR + 1e-9 else 'no'} |" if sc else
                         f"| {f.relative_to(rd)} | 0 | - | - | - | - |")
            ok = ok and bool(below)
        lines.append("")
        lines.append("Verdict: " + ("adaptation engaged (scale < 1 in every adapt file)." if ok else
                                    "**adaptation did NOT engage in at least one file (no row with scale < 1).**"))
    text = "\n".join(lines) + "\n"
    OUT.write_text(text)
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
