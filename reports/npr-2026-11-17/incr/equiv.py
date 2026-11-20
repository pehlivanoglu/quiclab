#!/usr/bin/env python3
"""Stage 1 acceptance on the development runs: incremental NPR-B against frozen NPR-B, every close of every run.

Input: the development rows (reports/npr-step0b-2026-11-17/rows.jsonl: v3 161 + K1 development 102 runs; no
validation run, checked against valset.json), events E1-0.5 with at least one onset, as the v3 table (step12v.py).
Per run: groups at every close identical, and every E value (each evalue call, in call order) bit-identical.
Any difference is a failure (the summary says FAIL and the exit code is 1). Reading only; nothing written in run
folders. Output: incr/equiv-rows.jsonl (resumable), incr/equiv.md.

    .venv/bin/python3 reports/npr-2026-11-17/incr/equiv.py rows [--jobs 2]
    .venv/bin/python3 reports/npr-2026-11-17/incr/equiv.py report
"""

from __future__ import annotations

import json
import struct
import sys
import time
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import npr_b_incr as I   # noqa: E402  (frozen copies on sys.path)
import npr_var           # noqa: E402
import step12            # noqa: E402

assert "frozen-2026-11-18" in npr_var.__file__ and "frozen-2026-11-18" in step12.__file__

SRC = HERE.parents[1] / "npr-step0b-2026-11-17" / "rows.jsonl"
VALSET = HERE.parent / "valset.json"
ROWS = HERE / "equiv-rows.jsonl"
MD = HERE / "equiv.md"
CAND = "E1-0.5"


def bits(x):
    return struct.pack("<d", x).hex()


@dataclass
class FrozenRec(npr_var.ReaderB):
    log: list = field(default_factory=list)

    def evalue(self, g, T):
        E = super().evalue(g, T)
        self.log.append((g, T, bits(E)))
        return E


@dataclass
class IncrRec(I.ReaderBIncr):
    log: list = field(default_factory=list)

    def evalue(self, g, T):
        E = super().evalue(g, T)
        self.log.append((g, T, bits(E)))
        return E


def series(cls, events, clients):
    rd, groups, cpu = cls(clients), [], 0.0
    for e in events:
        rd.add(step12.matrix_col(e, clients))
        c0 = time.process_time()
        groups.append(sorted(sorted(g) for g in rd.read((I.ALPHA,))["groups"][I.ALPHA]))
        cpu += time.process_time() - c0
    return rd, groups, cpu


def worker(row):
    try:
        clients = row["clients"]
        ev = [e for e in row["cands"][CAND] if e["ones"]]
        a, ga, ca = series(FrozenRec, ev, clients)
        b, gb, cb = series(IncrRec, ev, clients)
        diff = next((i + 1 for i, (x, y) in enumerate(zip(ga, gb)) if x != y), None)
        ediff = next((i for i, (x, y) in enumerate(zip(a.log, b.log)) if x != y), None)
        return {"run": row["run"], "campaign": row["campaign"], "closes": len(ev), "groups_equal": ga == gb,
                "first_group_diff_close": diff, "E_calls": [len(a.log), len(b.log)],
                "E_equal": a.log == b.log, "first_E_diff_call": ediff,
                "cpu_s": [round(ca, 3), round(cb, 3)], "em_starts_count": [len(a.em_starts), len(b.em_starts)]}
    except Exception as e:   # noqa: BLE001
        import traceback
        return {"run": row.get("run"), "error": repr(e), "tb": traceback.format_exc()[-1500:]}


def cmd_rows(jobs):
    val = {(r["campaign"], r["run"]) for r in json.load(open(VALSET)) if r["table"] in ("main", "robustness")}
    rows = [json.loads(x) for x in SRC.read_text().splitlines() if x.strip()]
    rows = [r for r in rows if "error" not in r]
    short = lambda c: c.split("_v4-")[-1] if "_v4-" in c else c   # noqa: E731
    assert not [r for r in rows if (short(r["campaign"]), r["run"]) in val], "a validation run in the input"
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}") and '"error"' not in x]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rows = [r for r in rows if r["run"] not in done]
    rows.sort(key=lambda r: -len(r["cands"][CAND]))   # longest first (one run takes ~30 min frozen)
    print(f"{len(rows)} runs ({len(done)} already done)", flush=True)
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, out in enumerate(pool.imap_unordered(worker, rows), 1):
            fh.write(json.dumps(out) + "\n")
            fh.flush()
            bad = "error" in out or not (out["groups_equal"] and out["E_equal"])
            print(f"  {i}/{len(rows)} {out['run']} {'DIFF/ERROR' if bad else 'identical'}", flush=True)


def report():
    R = [json.loads(x) for x in ROWS.read_text().splitlines() if x.strip()]
    err = [r for r in R if "error" in r]
    ok = [r for r in R if "error" not in r]
    gbad = [r for r in ok if not r["groups_equal"]]
    ebad = [r for r in ok if not r["E_equal"]]
    passed = not err and not gbad and not ebad and len(ok) == 263
    fz, inc = sum(r["cpu_s"][0] for r in ok), sum(r["cpu_s"][1] for r in ok)
    L = ["# Incremental NPR-B, stage 1: equivalence on the development runs (equiv.py)\n",
         f"**{'PASS' if passed else 'FAIL'}**: {len(ok)} runs compared (263 expected), {sum(r['closes'] for r in ok)} "
         f"closes; groups differ in {len(gbad)} runs; E values differ in {len(ebad)} runs; errors {len(err)}.\n",
         f"E values compared: {sum(r['E_calls'][0] for r in ok)} evalue calls, bit for bit (IEEE-754 doubles).\n",
         f"Read CPU (process time, the two readers in the same worker): frozen {fz:.0f} s, incremental {inc:.0f} s "
         f"(ratio {fz / max(inc, 1e-9):.1f}). Measured under the guard, machine shared: indicative only; cost1000 is "
         "the cost measurement.\n",
         "Diagnostic-only difference: em_starts (winning EM start per null fit) has "
         f"{sum(r['em_starts_count'][0] for r in ok)} entries frozen and {sum(r['em_starts_count'][1] for r in ok)} "
         "incremental (one per (group, event) fit instead of one per read); groups and E values do not use it.\n"]
    if gbad or ebad or err:
        L.append("| run | first close with different groups | first differing E call | error |\n|---|---|---|---|")
        for r in gbad + [x for x in ebad if x not in gbad] + err:
            L.append(f"| {r['run']} | {r.get('first_group_diff_close')} | {r.get('first_E_diff_call')} | "
                     f"{r.get('error', '')} |")
    MD.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if passed else 1


def main(argv):
    if argv[:1] == ["rows"]:
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2)
        return 0
    if argv[:1] == ["report"]:
        return report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
