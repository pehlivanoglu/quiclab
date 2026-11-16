#!/usr/bin/env python3
"""Gate check 4b diagnosis: service timing of a traced egress while truly backlogged.

    .venv/bin/python3 reports/v3-suite/gate4/service.py <run>:<hop> [...] > reports/v3-suite/gate4/service.md

Backlogged gap: packet i+1 was enqueued before packet i was dequeued (both matched; no
netem on the traced bottlenecks used here). ratio = (t_deq[i+1] - t_deq[i]) / (8 len / C),
C = the egress's capacity in force (scenario), with len = len[i] (the packet whose tokens
HTB pays before it releases i+1: the right ideal) and, for comparison, len[i+1] (what
router_trace.interdequeue_ratio uses today). Histogram on fixed ratio bins, plus the
pattern test: within one busy period, sum of gaps over runs of near-zero gaps.

20 ms windows: busy periods = maximal chains of backlogged gaps; each busy period of
>= 20 ms is cut into consecutive 20 ms windows from its start; ratio = bytes dequeued in
(w, w + 20 ms] / (C x 20 ms). Windows with a capacity change inside are skipped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from quiclab import router_trace  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402

BINS = [0, 0.05, 0.2, 0.5, 0.8, 0.95, 1.05, 1.2, 1.5, 2, 3, 5, 10, 20, 50, np.inf]
WIN_NS = 20_000_000


def epoch_ns(rd: Path) -> int:
    ev = pd.read_csv(rd / "events.csv")
    return int(ev[ev.event == "epoch"].applied_mono_ns.iloc[0])


def analyse(rd: Path, hop: str) -> dict:
    ifaces = pd.read_csv(rd / "router-trace" / "interfaces.csv")
    iface = ifaces[ifaces.hop == hop].iface.iloc[0]
    topo = load_topology(rd / "topology.yaml")
    sc = load_scenario(rd / "scenario.yaml", topo)
    caps = router_trace.capacity_timeline(sc, tuple(hop.split("->")))
    when = np.array([c[0] for c in caps])
    mbps = np.array([c[1] for c in caps])
    t0 = epoch_ns(rd)
    d = pd.read_csv(rd / "router-trace" / f"{iface}-packets.csv", usecols=["kind", "t_enq_ns", "t_deq_ns", "len"])
    d = d[d.kind == "dequeue"].sort_values("t_deq_ns")
    te, td, ln = (d[c].to_numpy(np.int64) for c in ("t_enq_ns", "t_deq_ns", "len"))
    busy = (te[1:] >= 0) & (te[1:] < td[:-1])
    gap = (td[1:] - td[:-1]).astype(float)
    run_t = (td[1:] - t0) / 1e9
    cap = mbps[np.clip(np.searchsorted(when, run_t, side="right") - 1, 0, len(mbps) - 1)] * 1e6
    ideal_next = 8 * ln[1:] / cap * 1e9
    ideal = 8 * ln[:-1] / cap * 1e9
    ratio = gap[busy] / ideal[busy]
    ratio_next = gap[busy] / ideal_next[busy]
    hist, _ = np.histogram(ratio, BINS)
    # pattern: in backlogged stretches, how much time sits in gaps < 0.2 vs > 1.5 packet times
    near0 = ratio < 0.2
    big = ratio > 1.5
    # 20 ms windows over busy periods
    idx = np.flatnonzero(busy)
    starts = idx[np.r_[True, np.diff(idx) > 1]]
    ends = idx[np.r_[np.diff(idx) > 1, True]] + 1          # busy chain covers packets starts[k] .. ends[k]
    cum = np.r_[0, np.cumsum(ln)]
    win = []
    for a, b in zip(starts, ends):
        ta, tb = td[a], td[b]
        k = 0
        while ta + (k + 1) * WIN_NS <= tb:
            w0, w1 = ta + k * WIN_NS, ta + (k + 1) * WIN_NS
            i0, i1 = np.searchsorted(td, [w0, w1], side="right")
            r0, r1 = (w0 - t0) / 1e9, (w1 - t0) / 1e9
            c0 = mbps[max(0, np.searchsorted(when, r0, side="right") - 1)]
            c1 = mbps[max(0, np.searchsorted(when, r1, side="right") - 1)]
            if c0 == c1:
                win.append((cum[i1] - cum[i0]) * 8 / (c0 * 1e6 * WIN_NS / 1e9))
            k += 1
    win = np.array(win)
    return {"run": f"{rd.parent.name}/{rd.name}", "hop": hop, "iface": iface,
            "capacity_mbps": sorted(set(mbps.tolist())), "dequeues": int(len(td)), "backlogged_gaps": int(busy.sum()),
            "ratio_bins": [f"{BINS[i]:g}-{BINS[i + 1]:g}" for i in range(len(BINS) - 1)],
            "ratio_hist": hist.tolist(),
            "ratio_p50_p90_p99_p999": [round(float(np.quantile(ratio, q)), 3) for q in (0.5, 0.9, 0.99, 0.999)],
            "ratio_max": round(float(ratio.max()), 2),
            "ratio_next_p50_p90_p99_p999": [round(float(np.quantile(ratio_next, q)), 3) for q in (0.5, 0.9, 0.99, 0.999)],
            "ratio_next_hist": np.histogram(ratio_next, BINS)[0].tolist(),
            "gap_ms_p50_p99_p999_max": [round(float(np.quantile(gap[busy], q)) / 1e6, 3) for q in (0.5, 0.99, 0.999, 1)],
            "share_within_10pct": round(float((np.abs(ratio - 1) <= 0.10).mean()), 4),
            "share_within_10pct_next": round(float((np.abs(ratio_next - 1) <= 0.10).mean()), 4),
            "share_gaps_lt0.2": round(float(near0.mean()), 4), "share_gaps_gt1.5": round(float(big.mean()), 4),
            "time_share_in_gt1.5_gaps": round(float(gap[busy][big].sum() / gap[busy].sum()), 4),
            "mean_ratio_of_gt1.5": round(float(ratio[big].mean()), 2) if big.any() else None,
            "gt10_share": round(float((ratio > 10).mean()), 5),
            "windows_20ms": int(len(win)),
            "win_ratio_p01_p50_p99": [round(float(np.quantile(win, q)), 4) for q in (0.01, 0.5, 0.99)] if len(win) else None,
            "win_share_within_5pct": round(float((np.abs(win - 1) <= 0.05).mean()), 4) if len(win) else None,
            "win_share_below_0.95": round(float((win < 0.95).mean()), 4) if len(win) else None,
            "win_share_above_1.05": round(float((win > 1.05).mean()), 4) if len(win) else None}


def main(argv: list[str]) -> None:
    out = []
    for arg in argv:
        path, _, hop = arg.rpartition(":")
        out.append(analyse(ROOT / path if not Path(path).is_absolute() else Path(path), hop))
    for r in out:
        print(f"## {r['run']} {r['hop']} ({r['iface']}, C {r['capacity_mbps']} Mb/s)\n")
        print(f"{r['dequeues']} dequeues, {r['backlogged_gaps']} backlogged gaps; gap ms p50 / p99 / p99.9 / max "
              f"{r['gap_ms_p50_p99_p999_max']}.\n")
        print(f"- ideal from len[i] (HTB pays packet i before releasing i+1): p50 / p90 / p99 / p99.9 = "
              f"{r['ratio_p50_p90_p99_p999']}, max {r['ratio_max']}; within +-10 %: {r['share_within_10pct']:.2%}")
        print(f"- ideal from len[i+1] (router_trace today): p50 / p90 / p99 / p99.9 = "
              f"{r['ratio_next_p50_p90_p99_p999']}; within +-10 %: {r['share_within_10pct_next']:.2%}\n")
        print("| gap / ideal | " + " | ".join(r["ratio_bins"]) + " |")
        print("|---|" + "---|" * len(r["ratio_bins"]))
        tot = sum(r["ratio_hist"])
        print("| len[i] | " + " | ".join(f"{h / tot:.4f}" for h in r["ratio_hist"]) + " |")
        print("| len[i+1] | " + " | ".join(f"{h / tot:.4f}" for h in r["ratio_next_hist"]) + " |\n")
        print(f"- gaps < 0.2 packet times: {r['share_gaps_lt0.2']:.1%}; gaps > 1.5: {r['share_gaps_gt1.5']:.1%} "
              f"(mean {r['mean_ratio_of_gt1.5']} packet times, {r['time_share_in_gt1.5_gaps']:.1%} of backlogged "
              f"time); gaps > 10: {r['gt10_share']:.3%}")
        print(f"- 20 ms backlogged windows: {r['windows_20ms']}; bytes / (C x 20 ms) p1 / p50 / p99 = "
              f"{r['win_ratio_p01_p50_p99']}; within +-5 %: {r['win_share_within_5pct']:.2%} "
              f"(below 0.95: {r['win_share_below_0.95']:.2%}, above 1.05: {r['win_share_above_1.05']:.2%})\n")
    (Path(__file__).parent / "service.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
