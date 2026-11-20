#!/usr/bin/env python3
"""cost1000 repeated with incremental NPR-B (stage 1), frozen NPR-B side by side, extended to 300 and 1000 events.

Same method as ../cost1000.py: the step3 synthetic 1000-client model with the same parameters and seed; process CPU per
event (add + read), single thread, 5 repeats (min and median), then one tracemalloc pass for peak memory. The events
come from step3.synth with EVENTS raised to 1000: the generator draws sequentially, so the first 120 events are the
ones cost1000 used (checked below against cost1000's own input). Frozen: repeat 1 to the cap below, repeats
2..5 and the memory pass to event 100 (cost1000's range).

Frozen NPR-B is run as far as reasonable: it stops at the first event whose CPU exceeds FROZEN_EVENT_CAP_S, or when its
cumulative CPU in one repeat exceeds FROZEN_TOTAL_CAP_S; the stop point is recorded. Incremental NPR-B runs all 1000
events. Groups of the two are compared at every close both computed (any difference: FAIL).

    .venv/bin/python3 reports/npr-2026-11-17/incr/cost_incr.py run [repeats]     # -> cost-incr-events.jsonl
    .venv/bin/python3 reports/npr-2026-11-17/incr/cost_incr.py report            # -> cost-incr.md
"""

from __future__ import annotations

import json
import statistics as st
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import npr_b_incr as I   # noqa: E402  (frozen copies first on sys.path)
import npr_var           # noqa: E402
import step12            # noqa: E402

sys.path.append(str(HERE.parent))   # step3 (input model only) and cost1000 (its constants)
import cost1000 as C     # noqa: E402
import step3             # noqa: E402

OUT = HERE / "cost-incr-events.jsonl"
MD = HERE / "cost-incr.md"
EVENTS = 1000
MARKS = (10, 50, 100, 300, 1000)
FROZEN_EVENT_CAP_S = 60.0      # (M) stop frozen at the first event above 60 s CPU ...
FROZEN_TOTAL_CAP_S = 3 * 3600  # (M) ... or above 3 h cumulative in one repeat
FROZEN_LATER_REPS_UPTO = 100   # (M) frozen repeats 2..5 and its memory pass stop at event 100 (cost1000's range):
                               # only repeat 1 goes on to the cap (a full frozen repeat can take hours)


def synth():
    keep = step3.EVENTS
    step3.EVENTS = 120
    _, _, ref = step3.synth(C.N, C.SIZES, C.M, C.F, C.RHO, C.NA, C.SEED)   # cost1000's input
    step3.EVENTS = EVENTS
    try:
        clients, leaves, events = step3.synth(C.N, C.SIZES, C.M, C.F, C.RHO, C.NA, C.SEED)
    finally:
        step3.EVENTS = keep
    assert events[:120] == ref, "first 120 events differ from cost1000's input"
    return clients, events


def feed(kind, clients, events, rep, fh, mem=False, groups_out=None, upto=None):
    rd = npr_var.make("B", clients) if kind == "frozen" else I.ReaderBIncr(clients)
    if mem:
        tracemalloc.start()
    total, stopped = 0.0, None
    for i, e in enumerate(events[:upto], 1):
        c0 = time.process_time()
        rd.add(step12.matrix_col(e, clients))
        g = rd.read((I.ALPHA,))["groups"][I.ALPHA]
        dt = time.process_time() - c0
        total += dt
        rec = {"kind": kind, "rep": rep, "event": i, "cpu_s": dt, "groups": len(g), "cache": len(rd.cache),
               "den_cache": len(getattr(rd, "den_cache", {}))}
        if mem:
            rec["peak_bytes"] = tracemalloc.get_traced_memory()[1]
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        if groups_out is not None:
            groups_out.append(sorted(sorted(x) for x in g))
        if kind == "frozen" and (dt > FROZEN_EVENT_CAP_S or total > FROZEN_TOTAL_CAP_S):
            stopped = {"event": i, "cpu_s": dt, "total_s": total}
            fh.write(json.dumps({"kind": kind, "rep": rep, "stopped": stopped}) + "\n")
            fh.flush()
            break
    if mem:
        tracemalloc.stop()
    return stopped


def run(repeats):
    clients, events = synth()
    with OUT.open("a") as fh:
        for rep in range(1, repeats + 1):
            gi, gf = [], []
            feed("incr", clients, events, rep, fh, groups_out=gi)
            stop = feed("frozen", clients, events, rep, fh, groups_out=gf,
                        upto=None if rep == 1 else FROZEN_LATER_REPS_UPTO)
            n = len(gf)
            same = gi[:n] == gf
            fh.write(json.dumps({"rep": rep, "groups_equal_closes": n, "groups_equal": same,
                                 "first_diff": next((k + 1 for k in range(n) if gi[k] != gf[k]), None)}) + "\n")
            fh.flush()
            if not same:
                print(f"FAIL: groups differ (rep {rep})", flush=True)
                return 1
            if rep == 1 and stop:
                print(f"frozen stopped at event {stop['event']} (rep 1)", flush=True)
        feed("incr", clients, events, "mem", fh, mem=True)
        feed("frozen", clients, events, "mem", fh, mem=True, upto=FROZEN_LATER_REPS_UPTO)
    return 0


def report():
    R = [json.loads(x) for x in OUT.read_text().splitlines() if x.strip()]
    ev = [r for r in R if "event" in r and r.get("rep") != "mem"]
    mem = [r for r in R if r.get("rep") == "mem" and "event" in r]
    stops = [r for r in R if "stopped" in r]
    eq = [r for r in R if "groups_equal" in r]
    L = ["# Incremental NPR-B (stage 1) against frozen NPR-B, synthetic 1000 clients, up to 1000 events (cost_incr.py)\n",
         "Process CPU per event (add + read), single thread, nice 19, machine shared with the campaign. Python: an "
         "upper bound for a native implementation. Same input as cost1000 for events 1-120 (checked).\n",
         "Groups identical at every close both readers computed: " +
         ("yes" if eq and all(r["groups_equal"] for r in eq) else "**NO (FAIL)**") +
         " (" + ", ".join(f"rep {r['rep']}: {r['groups_equal_closes']} closes" for r in eq) + ").\n",
         "Frozen stop point: " + ("; ".join(f"rep {r['rep']}: event {r['stopped']['event']} "
                                           f"({r['stopped']['cpu_s']:.1f} s that event, {r['stopped']['total_s']:.0f} s "
                                           "cumulative)" for r in stops) or "not stopped (all 1000 events)") + "\n",
         "| reader | event | CPU s min | median | repeats | cumulative CPU to this event, median s | groups |",
         "|---|---|---|---|---|---|---|"]
    for kind in ("frozen", "incr"):
        by = {}
        for r in ev:
            if r["kind"] == kind:
                by.setdefault(r["rep"], {})[r["event"]] = r
        for mk in MARKS:
            xs = [d[mk]["cpu_s"] for d in by.values() if mk in d]
            if not xs:
                L.append(f"| {kind} | {mk} | - | - | 0 | - | - |")
                continue
            cum = st.median(sum(d[j]["cpu_s"] for j in range(1, mk + 1)) for d in by.values() if mk in d)
            g = next(d[mk]["groups"] for d in by.values() if mk in d)
            L.append(f"| {kind} | {mk} | {min(xs):.3f} | {st.median(xs):.3f} | {len(xs)} | {cum:.1f} | {g} |")
    L.append("")
    for kind in ("frozen", "incr"):
        m = [r for r in mem if r["kind"] == kind]
        if m:
            L.append(f"- {kind}: peak traced Python memory {max(r['peak_bytes'] for r in m) / 2**20:.1f} MiB "
                     f"(to event {max(r['event'] for r in m)}).")
    MD.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def main(argv):
    if argv[:1] == ["run"]:
        return run(int(argv[1]) if len(argv) > 1 else 5)
    if argv[:1] == ["report"]:
        return report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
