#!/usr/bin/env python3
"""Re-run named v4 campaign runs into a NEW folder (re-run list, reports/v4-health-2026-11-17/rerun-list.md).

    .venv/bin/python3 scripts/rerun_v4.py --plan-only --out <dir> RUN ...   # regenerate + compare with the originals
    .venv/bin/python3 scripts/rerun_v4.py --run --out .runs/<ts>_v4-rerun RUN ...   # the user starts it

The suite v4 planner is used unchanged (scripts/v4_suite.py: CAMPAIGNS, plan_all, run_one); each run's set (K1 / K2 /
K3) is found from the campaign folder that holds the original. Before running, every regenerated plan, topology,
scenario and windows file must be byte-identical to the original campaign's _gen file, except the plan's "git"
field (the planning commit, recorded only); else nothing runs. The
originals and their folders are never written. Resume: a run whose folder in --out already has v3-checks.json is
skipped.

Run ids the runtime refuses (quiclab/runtime.py _RUN_ID_RE; K3 I1 "ip1.2" cells, user 2026-11-19): the files are
regenerated and compared under the original name, then byte-copied to a new name with "." -> "p" (ip1.2 -> ip1p2);
only the file names and the run id change, the file contents (which record variant "ip1.2") are unchanged. The
mapping is printed and recorded in reports/npr-2026-11-17/a4-rules.md.
"""

from __future__ import annotations

import argparse
import dataclasses
import filecmp
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import v4_suite as v4   # noqa: E402
from quiclab.runtime import _RUN_ID_RE   # noqa: E402

RUNS = Path(__file__).resolve().parents[1] / ".runs"
CAMPS = {"K1": "2026-11-16_0105_v4-K1", "K2": "2026-11-16_0105_v4-K2", "K3": "2026-11-16_0105_v4-K3"}
SUFFIXES = ("-plan.json", "-topology.yaml", ".yaml", "-windows.json")


def safe_id(name: str) -> str:
    """The original name if the runtime accepts it, else "." -> "p" (the only change)."""
    if _RUN_ID_RE.match(name):
        return name
    new = name.replace(".", "p")
    assert _RUN_ID_RE.match(new), new
    return new


def main(argv):
    ap = argparse.ArgumentParser()
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--plan-only", action="store_true")
    m.add_argument("--run", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--nmax", type=int, default=40, help="K1 only (the K1 campaign used 40)")
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args(argv)
    todo = []
    for name in a.runs:
        sets = [k for k, c in CAMPS.items() if (RUNS / c / "_gen" / f"{name}-plan.json").exists()]
        if len(sets) != 1:
            print(f"{name}: found in {sets or 'no campaign'}")
            return 2
        todo.append((sets[0], name))
    plans, bad = [], []
    for k in dict.fromkeys(s for s, _ in todo):
        cells = v4.CAMPAIGNS[k](a.nmax) if k == "K1" else v4.CAMPAIGNS[k]()
        gen = a.out / "_gen"   # v3.run_one copies <out>/_gen/<name>-plan.json and -windows.json
        want = {n for s, n in todo if s == k}
        for p in v4.plan_all(gen, cells, k):
            if p.name not in want:
                continue
            v4.validate(p)
            for suf in SUFFIXES:
                new, old = gen / f"{p.name}{suf}", RUNS / CAMPS[k] / "_gen" / f"{p.name}{suf}"
                same = old.exists() and new.exists() and filecmp.cmp(old, new, shallow=False)
                note = ""
                if not same and suf == "-plan.json" and old.exists() and new.exists():
                    jo, jn = json.loads(old.read_text()), json.loads(new.read_text())
                    if {**jo, "git": None} == {**jn, "git": None}:   # the planning commit is recorded, not used
                        same, note = True, f" (only git differs: {jo.get('git')} -> {jn.get('git')})"
                print(f"{p.name}{suf}: {'identical' if same else 'DIFFERENT'}{note}")
                if not same:
                    bad.append(f"{p.name}{suf}")
            new = safe_id(p.name)
            if new != p.name:   # byte copy under the new name; contents unchanged
                for suf in SUFFIXES:
                    shutil.copyfile(gen / f"{p.name}{suf}", gen / f"{new}{suf}")
                    same = filecmp.cmp(gen / f"{p.name}{suf}", gen / f"{new}{suf}", shallow=False)
                    print(f"  -> {new}{suf}: {'byte-identical copy' if same else 'COPY DIFFERS'}")
                    if not same:
                        bad.append(f"{new}{suf}")
                p = dataclasses.replace(p, name=new, scenario=gen / f"{new}.yaml",
                                        topology=gen / f"{new}-topology.yaml")
            plans.append(p)
    missing = {safe_id(n) for _, n in todo} - {p.name for p in plans}
    for _, n in todo:
        if safe_id(n) != n:
            print(f"run id: {n} -> {safe_id(n)}")
    if missing or bad:
        print(f"not run: missing {sorted(missing)}, different {bad}")
        return 2
    print(f"{len(plans)} runs, {sum(p.duration for p in plans) / 3600:.2f} h emulated")
    if a.plan_only:
        return 0
    for p in plans:
        if (a.out / p.name / "v3-checks.json").exists():
            print(f"{p.name}: done, skipped")
            continue
        v4.run_one(p, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
