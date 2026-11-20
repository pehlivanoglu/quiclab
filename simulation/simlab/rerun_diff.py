#!/usr/bin/env python3
"""Compare a re-run of simulation runs with an earlier batch, file by file.

    python3 simulation/simlab/rerun_diff.py <old batch dir> <new batch dir> [out.md]

Per run and file present in either: identical, or the number of differing lines and where the first
difference lies (line index / file length). Files the scoring writes later (truth/, sim/meta.json,
sim/scored.json, logs/, episode caches) are not compared. A difference confined to the last lines of
a file is reported as "tail only" (the end-of-run fix changes only writes after the run's end).
"""

from __future__ import annotations

import sys
from pathlib import Path

SKIP = ("truth/", "logs/", "sim/meta.json", "sim/scored.json", "sim/episodes-v2-owd.json", "gtq-health.csv", "qdiscs.txt")


def lines(p: Path) -> list[bytes]:
    return p.read_bytes().splitlines() if p.exists() else []


def main(old: Path, new: Path, out: Path | None) -> None:
    rows = []
    for nr in sorted(p for p in new.iterdir() if p.is_dir() and p.name.startswith("sim-")):
        orun = old / nr.name
        if not orun.exists():
            rows.append(f"| {nr.name} | (no earlier run) | | |")
            continue
        files = {str(f.relative_to(nr)) for f in nr.rglob("*") if f.is_file()}
        files |= {str(f.relative_to(orun)) for f in orun.rglob("*") if f.is_file()}
        same, diffs = 0, []
        for rel in sorted(files):
            if rel.startswith(SKIP):
                continue
            a, b = lines(orun / rel), lines(nr / rel)
            if a == b:
                same += 1
                continue
            first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
            n = max(len(a), len(b))
            ndiff = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
            tail = n - first <= 5
            diffs.append(f"{rel} ({ndiff} lines, from {first}/{n}{', tail only' if tail else ''})")
        verdict = "identical" if not diffs else ("tail only" if all("tail only" in d for d in diffs) else "DIFFERS")
        rows.append(f"| {nr.name} | {same} identical | {verdict} | {'; '.join(diffs[:6])}{' ...' if len(diffs) > 6 else ''} |")
    text = "| run | files | verdict | differing files |\n|---|---|---|---|\n" + "\n".join(rows) + "\n"
    print(text)
    if out:
        out.write_text(text)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else None)
