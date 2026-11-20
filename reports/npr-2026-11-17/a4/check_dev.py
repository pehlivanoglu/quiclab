#!/usr/bin/env python3
"""Test of a4.py on development runs only: its rows (dev/rows.jsonl) against the stored development results.

  1. events: the rebuilt E1-0.5 and E0 events equal reports/npr-step0b-2026-11-17/rows.jsonl (sha256 of the lists);
  2. scorer: pair vectors equal rows-v3-E1-0.5.jsonl ("NPR-B a0.05", "NPR-A-m0.20-f0.05 a0.05",
     "NPR-A-m0.10-f0.05 a0.05") and rows-v2-E1-0.5.jsonl ("SETS@E0 k2/k3", "SETS@E1-0.5 k2/k3");
  3. false splits: the leaf-alone first split (event and parts, original order) equals diag3-rows.jsonl;
  4. late joiner (NPR rows): equals rows-v3-E1-0.5.jsonl;
  5. run folders unchanged (a4.py also raises if not).

    .venv/bin/python3 reports/npr-2026-11-17/a4/check_dev.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NPRD = HERE.parent
ROOT = NPRD.parents[1]

MAP_V3 = {"NPR-B": "NPR-B a0.05", "NPR-A": "NPR-A-m0.20-f0.05 a0.05", "NPR-A10": "NPR-A-m0.10-f0.05 a0.05"}
MAP_V2 = {"SETS-v1.1": "SETS@E0 k2", "SETS-v1.1 k3": "SETS@E0 k3", "SETS@E1-0.5": "SETS@E1-0.5 k2",
          "SETS@E1-0.5 k3": "SETS@E1-0.5 k3"}
MAP_D3 = {"NPR-B": "B", "NPR-A": "A-m0.20-f0.05", "NPR-A10": "A-m0.10-f0.05"}
MAP_LATE = {"NPR-B": "B", "NPR-A": "A-m0.20-f0.05", "NPR-A10": "A-m0.10-f0.05"}


def load(p, runs):
    out = {}
    with open(p) as fh:
        for x in fh:
            if any(f'"run": "{r}"' in x for r in runs):
                d = json.loads(x)
                out[d["run"]] = d
    return out


def h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()


def main():
    A = [json.loads(x) for x in (HERE / "dev" / "rows.jsonl").read_text().splitlines() if x.strip()]
    err = [a for a in A if "error" in a]
    A = [a for a in A if "error" not in a]
    runs = {a["run"] for a in A}
    S0 = load(ROOT / "reports" / "npr-step0b-2026-11-17" / "rows.jsonl", runs)
    V3 = load(NPRD / "rows-v3-E1-0.5.jsonl", runs)
    V2 = load(NPRD / "rows-v2-E1-0.5.jsonl", runs)
    D3 = load(NPRD / "diag3-rows.jsonl", runs)
    bad = [f"error {e['run']}: {e['error']}" for e in err]
    n = 0
    for a in A:
        r = a["run"]
        s0 = S0[r]
        for c in ("E1-0.5", "E0"):
            n += 1
            if a["check"][c] != h(s0["cands"][c]):
                bad.append(f"{r}: {c} events differ from step0b")
        if not a["run_folder_unchanged"]:
            bad.append(f"{r}: run folder changed")
        calm = not V3[r].get("methods")
        for name, key in {**MAP_V3, **MAP_V2}.items():
            src = V3[r] if name in MAP_V3 else V2[r]
            if calm or key not in src.get("methods", {}):
                continue
            n += 1
            if [float(x) for x in a["cands"][name]["score"]["pairs"]] != [float(x) for x in src["methods"][key]["pairs"]]:
                bad.append(f"{r}: {name} pairs {a['cands'][name]['score']['pairs']} != {key} {src['methods'][key]['pairs']}")
            if a["cands"][name]["score"]["levels"] != src["methods"][key]["levels"]:
                bad.append(f"{r}: {name} levels differ from {key}")
        for name, spec in MAP_LATE.items():
            ref = (V3[r].get("late") or {}).get(spec)
            if ref is None:
                continue
            n += 1
            if a["cands"][name]["late"] != ref:
                bad.append(f"{r}: {name} late joiner differs")
        if r in D3:
            for name, spec in MAP_D3.items():
                mine = {c["leaf"]: (c["split"]["event"], c["split"]["parts"]) if c["split"] else None
                        for c in a["cands"][name]["false_splits"]}
                ref = {c["leaf"]: (c["splits"][spec]["event"], c["splits"][spec]["parts"]) if c["splits"].get(spec) else None
                       for c in D3[r]["calibration"]}
                n += 1
                if mine != ref:
                    bad.append(f"{r}: {name} leaf-alone splits {mine} != diag3 {ref}")
    print(f"{len(A)} runs, {n} comparisons, {len(bad)} differences")
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
