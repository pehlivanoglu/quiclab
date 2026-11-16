#!/usr/bin/env python3
"""T-HAYES 4b diagnosis (offline, smoke 1 GT-Q traces; no emulation).

    .venv/bin/python3 reports/v4-suite/smoke1/hayes_4b.py > reports/v4-suite/smoke1/hayes-4b.md

For every target egress of a few smoke runs: the backlogged inter-dequeue gaps exactly as router_trace.service_stats
defines them (gap = t_deq[i+1] - t_deq[i] while packet i+1 was ready before packet i left; ideal = 8 len[i] / C),
the gap error e_i = gap_i - ideal_i, and the lag-1 correlation of consecutive errors (e_i, e_{i+1}) inside one busy
chain. A timestamp that is stamped late by x makes one gap longer by x and the next shorter by x, so tracer
timestamp noise gives a strongly negative lag-1 correlation (-0.5 for independent per-stamp noise); jitter of the
link's own service would give a correlation near zero, BUT HTB's own catch-up (a late release followed by an early
one paid from accumulated tokens) also gives a negative correlation, so the sign alone does not separate the two.
Also: the number of traced routers in the run and the run's CPU idle minimum (both grow the error magnitude).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

SMOKE = ROOT / ".runs" / "2026-11-16_0000_v4-smoke"
RUNS = ("v4-SMOKE-s-calm-hayes-pfifo-r1", "v4-SMOKE-s-calm-split4l-pfifo-r1", "v4-SMOKE-s-calm-par-k6-pfifo-r1",
        "v4-SMOKE-s-calm-base-n16-pfifo-r1", "v4-SMOKE-s-calm-teacup-pfifo-r1")


def errors(rd: Path, iface: str, hop: str):
    import det_eval as d
    from quiclab import router_trace as rt
    from quiclab.config.scenario import load_scenario
    from quiclab.config.schema import load_topology
    sc = load_scenario(rd / "scenario.yaml", load_topology(rd / "topology.yaml"))
    h = tuple(hop.split("->"))
    caps = rt.capacity_timeline(sc, h)
    delays = rt.delay_timeline(sc, h)
    epoch = d.Run(rd).epoch_mono_ns
    t = rt.read_packets(rd / "router-trace" / f"{iface}-packets.csv")
    dq = t[t["kind"] == "dequeue"].sort_values("t_deq_ns", kind="stable")
    t_deq, t_enq, ln = (dq[c].to_numpy(dtype=np.int64) for c in ("t_deq_ns", "t_enq_ns", "len"))
    if delays:
        t_enq = np.where(t_enq >= 0, t_enq + (rt.step_at(delays, (t_enq - epoch) / 1e9) * 1e6).astype(np.int64), t_enq)
    busy = (t_enq[1:] >= 0) & (t_enq[1:] < t_deq[:-1])
    when = np.array([c[0] for c in caps])
    mbps = np.array([c[1] for c in caps])
    cap = mbps[np.clip(np.searchsorted(when, (t_deq[1:] - epoch) / 1e9, side="right") - 1, 0, len(caps) - 1)] * 1e6
    e = (t_deq[1:] - t_deq[:-1]) - 8 * ln[:-1] / cap * 1e9      # ns, every gap
    pair = busy[:-1] & busy[1:]                                 # consecutive gaps in one busy chain
    a, b = e[:-1][pair], e[1:][pair]
    return e[busy], a, b


def main() -> None:
    print("# T-HAYES check 4b: tracer timestamp noise or link service jitter? (smoke 1, offline)\n")
    print("Lag-1 correlation of consecutive gap errors inside busy chains: about -0.5 = independent timestamp noise "
          "(a late stamp lengthens one gap and shortens the next); HTB catch-up after a late release is also negative, so "
          "the sign does not separate the two. 'pair sum' = e_i + e_(i+1), us.\n")
    print("| run | traced routers | CPU idle min | egress (role) | busy gaps | within max(10 %, 15 us) | error p1 / p99 us | "
          "lag-1 corr | pair-sum p1 / p99 us |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name in RUNS:
        rd = SMOKE / name
        plan = json.loads((rd / "v3-plan.json").read_text())
        targets = {e["hop"] for e in plan["egress"].values() if e.get("shaped", True)}
        rows = list(csv.DictReader((rd / "router-trace" / "interfaces.csv").open()))
        routers = len({r["router"] for r in rows})
        chk = json.loads((rd / "v3-checks.json").read_text())["4_health"]
        for r in rows:
            if r["hop"] not in targets:
                continue
            e, a, b = errors(rd, r["iface"], r["hop"])
            if len(e) < 100:
                continue
            ideal_ok = chk["egress"].get(r["iface"], {}).get("gap_within_tol")
            corr = float(np.corrcoef(a, b)[0, 1]) if len(a) > 10 else float("nan")
            s = (a + b) / 1e3
            print(f"| {name.replace('v4-SMOKE-s-calm-', '').replace('-pfifo-r1', '')} | {routers} | "
                  f"{chk.get('cpu_idle_min')} | {r['hop']} | {len(e)} | {ideal_ok if ideal_ok is None else round(ideal_ok, 4)} | "
                  f"{np.percentile(e, 1) / 1e3:.1f} / {np.percentile(e, 99) / 1e3:.1f} | {corr:.2f} | "
                  f"{np.percentile(s, 1):.1f} / {np.percentile(s, 99):.1f} |")


if __name__ == "__main__":
    main()
