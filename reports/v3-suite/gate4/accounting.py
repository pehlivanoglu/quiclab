#!/usr/bin/env python3
"""Gate check 4a diagnosis: where in time are the GT-Q tracer's unmatched packets?

    .venv/bin/python3 reports/v3-suite/gate4/accounting.py > reports/v3-suite/gate4/accounting.md

Two kinds, per traced egress of every existing GT-Q run (router-trace/):
- unmatched dequeues: rows of kind `nohit` in <iface>-packets.csv (a dequeue with no
  enqueue record: n_nohit from the kernel side, plus "requeues" more than 100 ms after the
  address's previous dequeue, which router_trace reclassifies as nohit). They have times.
- unmatched enqueues: residual = n_enq - n_deq - n_drop (tracer-counts.csv). Their enqueue
  records are not written to the CSV (only dequeue / drop rows are), so their times are
  unknown; bounded here with the queue occupancy at the tracer's end (5 ms queue CSV): a
  packet still queued at stop must show up there.
Edges: first / last 1 s of the trace (tracer_start_ns / tracer_end_ns).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
EDGE_NS = 1_000_000_000


def runs() -> list[Path]:
    return sorted(p.parent.parent for p in (ROOT / ".runs").rglob("router-trace/tracer-counts.csv"))


def rows(rd: Path) -> list[dict]:
    out = []
    for c in csv.DictReader((rd / "router-trace" / "tracer-counts.csv").open()):
        n = {k: int(c[k]) for k in ("n_enq", "n_deq", "n_drop", "n_requeue", "n_nohit", "requeue_stale",
                                     "tracer_start_ns", "tracer_end_ns")}
        p = rd / "router-trace" / f"{c['iface']}-packets.csv"
        t = pd.read_csv(p, usecols=["kind", "t_deq_ns", "len", "proto", "saddr", "daddr"])
        nh = t[t.kind == "nohit"]
        a, b = n["tracer_start_ns"], n["tracer_end_ns"]
        rel = (nh.t_deq_ns.values - a) / 1e9
        edge = ((nh.t_deq_ns.values - a) < EDGE_NS) | ((b - nh.t_deq_ns.values) < EDGE_NS)
        q = rd / "router-metrics" / c["router"] / f"{c['iface']}-queue.csv"
        q_end = None
        if q.exists():
            qq = pd.read_csv(q, usecols=["timestamp_mono_ns", "queue_packets"])
            before = qq[qq.timestamp_mono_ns <= b]
            q_end = (int(before.queue_packets.iloc[-1]), round((b - int(before.timestamp_mono_ns.iloc[-1])) / 1e9, 3)) \
                if len(before) else None
        out.append({"run": f"{rd.parent.name}/{rd.name}", "iface": c["iface"], "deq": n["n_deq"],
                    "residual": n["n_enq"] - n["n_deq"] - n["n_drop"], "nohit": len(nh),
                    "nohit_edge": int(edge.sum()), "nohit_mid": int((~edge).sum()),
                    "nohit_rel_s": np.round(rel, 1).tolist(), "trace_s": round((b - a) / 1e9, 1),
                    "nohit_len": sorted(set(nh.len.tolist()))[:6], "q_at_end": q_end,
                    "drop": n["n_drop"]})
    return out


def main() -> None:
    allr = [r for rd in runs() for r in rows(rd)]
    print("# Gate 4a: GT-Q unmatched packets in the existing runs\n")
    print(f"{len({r['run'] for r in allr})} runs, {len(allr)} traced egresses.\n")
    tot = lambda k: sum(r[k] for r in allr)   # noqa: E731
    print(f"- unmatched dequeues (nohit): {tot('nohit')}; in the first / last 1 s: {tot('nohit_edge')}; "
          f"elsewhere: {tot('nohit_mid')}")
    print(f"- unmatched enqueues (residual): {tot('residual')} (min {min(r['residual'] for r in allr)}, "
          f"max {max(r['residual'] for r in allr)}); egresses with residual != 0: "
          f"{sum(r['residual'] != 0 for r in allr)} of {len(allr)}; queue at the tracer's end non-zero on "
          f"{sum(1 for r in allr if r['q_at_end'] and r['q_at_end'][0])} egresses")
    mids = np.concatenate([np.array(r["nohit_rel_s"]) / r["trace_s"] for r in allr if r["nohit"]] or [np.array([])])
    if len(mids):
        h, _ = np.histogram(mids, bins=10, range=(0, 1))
        print(f"- nohit position in the trace (deciles of trace time): {h.tolist()}")
    xs = [(r["drop"] / max(r["deq"], 1), r["residual"] + r["nohit"]) for r in allr]
    if len(xs) > 2:
        print(f"- correlation of (residual + nohit) with drop share across egresses: "
              f"{np.corrcoef(*zip(*xs))[0, 1]:.2f}; with dequeues: "
              f"{np.corrcoef([r['deq'] for r in allr], [r['residual'] + r['nohit'] for r in allr])[0, 1]:.2f}")
    print("\n| run | iface | dequeues | drops | residual (enq - deq - drop) | nohit | nohit first/last 1 s | "
          "nohit times s (trace length) | queue pkts at tracer end (age s) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in allr:
        times = r["nohit_rel_s"]
        tt = ", ".join(map(str, times[:8])) + (" ..." if len(times) > 8 else "")
        print(f"| {r['run']} | {r['iface']} | {r['deq']} | {r['drop']} | {r['residual']} | {r['nohit']} | "
              f"{r['nohit_edge']} | {tt} ({r['trace_s']}) | {r['q_at_end']} |")


if __name__ == "__main__":
    sys.exit(main())
