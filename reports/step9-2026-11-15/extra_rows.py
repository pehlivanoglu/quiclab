#!/usr/bin/env python3
"""Step 8 rows (step8.one, unchanged) for the runs Step 9 adds: C12 (all AQMs) and M8 mixab.

    .venv/bin/python3 reports/step9-2026-11-15/extra_rows.py .runs/2026-11-14_1818_v3   # -> rows-extra.jsonl
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "step8-2026-11-15"))
import step8  # noqa: E402

if __name__ == "__main__":
    kdir = Path(sys.argv[1])
    runs = [p for p in sorted(kdir.iterdir()) if p.is_dir() and p.name.startswith(("v3-C12-", "v3-M8-"))]
    with Pool(8) as pool, open(HERE / "rows-extra.jsonl", "w") as fh:
        for r in pool.imap_unordered(step8.one, runs):
            fh.write(json.dumps(r) + "\n")
