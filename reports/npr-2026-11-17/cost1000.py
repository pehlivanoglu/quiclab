#!/usr/bin/env python3
"""B.b item b (user, 2026-11-18): frozen NPR-B and NPR-A on the synthetic 1000-client input (step3 model, layout
1000 = leaves 10 / 50 / 100 / 340 / 500, E1-0.5 parameters m 0.011, f 0.001, rho 0.4, NA 0.111, seed 1).
Process CPU time of one event (matrix update + read at alpha 0.05) for every event up to 100, single thread, the
frozen code as it is. One line per event goes to cost1000-events.jsonl as it is measured.

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/cost1000.py run REPEATS
    .venv/bin/python3 reports/npr-2026-11-17/cost1000.py report

Peak memory: a separate pass with tracemalloc (its own overhead; CPU of that pass is not used), the peak of Python
allocations while the reader is fed, after the input is built.
"""

from __future__ import annotations

import json
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "frozen-2026-11-18"), str(HERE.parents[1])]

OUT = HERE / "cost1000-events.jsonl"
N, SIZES = 1000, (10, 50, 100, 340, 500)
M, F, RHO, NA, SEED = 0.011, 0.001, 0.4, 0.111, 1   # (P) step3-rows-v2 parameters
UPTO = 100
MARKS = (10, 50, 100)
SPECS = {"NPR-B": "B", "NPR-A": "A-m0.20-f0.05"}


def synth():
    import step3   # the step3 model, unchanged (imported from the working folder, not frozen: input only)
    return step3.synth(N, SIZES, M, F, RHO, NA, SEED)


def feed(spec, clients, events, rep, fh, mem=False):
    import npr_var
    import step12
    rd = npr_var.make(spec, clients)
    if mem:
        tracemalloc.start()
    for i, e in enumerate(events[:UPTO], 1):
        c0 = time.process_time()
        rd.add(step12.matrix_col(e, clients))
        g = rd.read((0.05,))["groups"][0.05]
        dt = time.process_time() - c0
        rec = {"spec": spec, "rep": rep, "event": i, "cpu_s": dt, "groups": len(g), "cache": len(rd.cache)}
        if mem:
            rec["peak_bytes"] = tracemalloc.get_traced_memory()[1]
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
    if mem:
        tracemalloc.stop()


def run(repeats):
    import npr
    import npr_var
    import step12
    assert all("frozen-2026-11-18" in m.__file__ for m in (npr, npr_var, step12)), "not the frozen copies"
    sys.path.append(str(HERE))
    clients, _, events = synth()
    with OUT.open("a") as fh:
        for rep in range(1, repeats + 1):
            for name, spec in SPECS.items():
                feed(spec, clients, events, rep, fh)
        for name, spec in SPECS.items():
            feed(spec, clients, events, "mem", fh, mem=True)


def report():
    R = [json.loads(x) for x in OUT.read_text().splitlines() if x.strip()]
    print("# Frozen NPR on the synthetic 1000-client input (cost1000.py)\n")
    print("Process CPU per event (matrix update + read), single thread, nice 19, machine shared with the campaign. "
          "Python: an upper bound for a native implementation.\n")
    print("| method | event | CPU s min | median | repeats | cumulative CPU to this event, median s | groups |")
    print("|---|---|---|---|---|---|---|")
    for spec in SPECS.values():
        reps = sorted({r["rep"] for r in R if r["spec"] == spec and r["rep"] != "mem"})
        for ev in MARKS:
            v = [r["cpu_s"] for r in R if r["spec"] == spec and r["event"] == ev and r["rep"] != "mem"]
            cum = [sum(r["cpu_s"] for r in R if r["spec"] == spec and r["rep"] == k and r["event"] <= ev) for k in reps
                   if any(r["spec"] == spec and r["rep"] == k and r["event"] == ev for r in R)]
            g = [r["groups"] for r in R if r["spec"] == spec and r["event"] == ev]
            if v:
                print(f"| {spec} | {ev} | {min(v):.3f} | {np.median(v):.3f} | {len(v)} | {np.median(cum):.1f} | {g[0]} |")
    print()
    for spec in SPECS.values():
        m = [r for r in R if r["spec"] == spec and r["rep"] == "mem"]
        if m:
            print(f"- {spec}: peak traced Python memory of the reader {max(r['peak_bytes'] for r in m) / 2**20:.1f} MiB "
                  f"(to event {max(r['event'] for r in m)}).")


if __name__ == "__main__":
    if sys.argv[1:2] == ["run"]:
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    else:
        report()
