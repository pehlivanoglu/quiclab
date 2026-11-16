#!/usr/bin/env python3
"""Smoke 1 (classic tracepoints) vs smoke 2 (raw tracepoints): is the measurement unchanged?

    .venv/bin/python3 reports/v3-suite/smoke2/compare12.py .runs/2026-11-14_1730_v3-smoke .runs/2026-11-14_1801_v3-smoke

1. Sojourn on router->switch (base CALM and S-BURST): t_deq - t_enq of matched dequeues
   (router-trace/<iface>-packets.csv; no netem on that egress), p50 / p99 / mean, plus the
   share of packets with a sojourn above one packet time.
2. Calm load, video share and keyframe-peak p50 / p90 per bottleneck egress, every run
   (<run>/v3-checks.json of each smoke).
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

s1, s2 = map(Path, sys.argv[1:3])


def sojourn(rd: Path, hop: str) -> dict:
    iface = next(r["iface"] for r in csv.DictReader((rd / "router-trace" / "interfaces.csv").open()) if r["hop"] == hop)
    d = pd.read_csv(rd / "router-trace" / f"{iface}-packets.csv", usecols=["kind", "t_enq_ns", "t_deq_ns"])
    d = d[(d.kind == "dequeue") & (d.t_enq_ns >= 0)]
    s = (d.t_deq_ns - d.t_enq_ns).to_numpy() / 1e6
    return {"n": len(s), "p50_ms": round(float(np.median(s)), 3), "p99_ms": round(float(np.quantile(s, 0.99)), 3),
            "mean_ms": round(float(s.mean()), 3), "share_gt_0.2ms": round(float(np.mean(s > 0.2)), 4)}


print("## Sojourn on router->switch (ms)\n")
print("| run | smoke 1: n, p50 / p99 / mean, share > 0.2 ms | smoke 2: same |")
print("|---|---|---|")
for run in ("v3-SMOKE-calm-s030u070-pfifo-r1", "v3-SMOKE-sburst-s030u070-pfifo-r1"):
    a, b = sojourn(s1 / run, "router->switch"), sojourn(s2 / run, "router->switch")
    f = lambda x: f"{x['n']}, {x['p50_ms']} / {x['p99_ms']} / {x['mean_ms']}, {x['share_gt_0.2ms']}"   # noqa: E731
    print(f"| {run} | {f(a)} | {f(b)} |")

print("\n## Load, share, keyframe peak per bottleneck egress (smoke 1 -> smoke 2)\n")
print("| run | egress | load | share / 0.96 | keyframe peak p50 ms | p90 ms |")
print("|---|---|---|---|---|---|")
dl, ds, dk = [], [], []
for rd2 in sorted(s2.glob("v3-SMOKE-*")):
    c1 = json.loads((s1 / rd2.name / "v3-checks.json").read_text())
    c2 = json.loads((rd2 / "v3-checks.json").read_text())
    for name, e2 in c2["1_load_share"]["egress"].items():
        e1 = c1["1_load_share"]["egress"][name]
        k1, k2 = c1["keyframe_peaks"].get(name, {}), c2["keyframe_peaks"].get(name, {})
        dl.append(abs(e2["load"] - e1["load"]))
        ds.append(abs(e2["share"] - e1["share"]))
        dk.append(abs(k2.get("p50", np.nan) - k1.get("p50", np.nan)))
        print(f"| {rd2.name} | {name} | {e1['load']} -> {e2['load']} | {e1['share']} -> {e2['share']} | "
              f"{k1.get('p50')} -> {k2.get('p50')} | {k1.get('p90')} -> {k2.get('p90')} |")
print(f"\nLargest |change|: load {max(dl):.3f}, share {max(ds):.3f}, keyframe peak p50 {np.nanmax(dk):.1f} ms "
      f"(median {np.nanmedian(dk):.1f} ms).")


def tc_queue(rd: Path, hop: str, cap_mbps: float) -> dict:
    """Tracer-independent: queue delay from the 5 ms tc backlog samples (router-metrics)."""
    iface = next(r["iface"] for r in csv.DictReader((rd / "router-trace" / "interfaces.csv").open()) if r["hop"] == hop)
    router = hop.split("->")[0]
    q = pd.read_csv(rd / "router-metrics" / router / f"{iface}-queue.csv", usecols=["queue_backlog_bytes"])
    dl = q.queue_backlog_bytes.to_numpy() * 8 / (cap_mbps * 1e6) * 1000
    return {"p50_ms": round(float(np.median(dl)), 3), "p90_ms": round(float(np.quantile(dl, 0.9)), 3),
            "mean_ms": round(float(dl.mean()), 3)}


print("\n## Same egress, tracer-independent (tc backlog every 5 ms / C), ms\n")
print("| run | smoke 1: p50 / p90 / mean | smoke 2: same |")
print("|---|---|---|")
for run in ("v3-SMOKE-calm-s030u070-pfifo-r1", "v3-SMOKE-sburst-s030u070-pfifo-r1"):
    cap = json.loads((s2 / run / "v3-plan.json").read_text())["egress"]["main"]["C_e_mbps"]
    a, b = tc_queue(s1 / run, "router->switch", cap), tc_queue(s2 / run, "router->switch", cap)
    print(f"| {run} | {a['p50_ms']} / {a['p90_ms']} / {a['mean_ms']} | {b['p50_ms']} / {b['p90_ms']} / {b['mean_ms']} |")


print("\n## Sojourn floor on router->switch (empty queue: the enqueue / dequeue probe points), us\n")
print("| run | smoke 1: min / p1 / p5 | smoke 2: min / p1 / p5 |")
print("|---|---|---|")
for run in ("v3-SMOKE-calm-s030u070-pfifo-r1", "v3-SMOKE-sburst-s030u070-pfifo-r1"):
    out = []
    for s in (s1, s2):
        rd = s / run
        iface = next(r["iface"] for r in csv.DictReader((rd / "router-trace" / "interfaces.csv").open())
                     if r["hop"] == "router->switch")
        d = pd.read_csv(rd / "router-trace" / f"{iface}-packets.csv", usecols=["kind", "t_enq_ns", "t_deq_ns"])
        d = d[(d.kind == "dequeue") & (d.t_enq_ns >= 0)]
        x = (d.t_deq_ns - d.t_enq_ns).to_numpy() / 1e3
        out.append(f"{x.min():.1f} / {np.quantile(x, .01):.1f} / {np.quantile(x, .05):.1f}")
    print(f"| {run} | {out[0]} | {out[1]} |")
