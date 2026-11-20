#!/usr/bin/env python3
"""Stage C desk numbers for the grid decided by the user on 2026-11-19, extrapolated from the measured 300-client run
(reports/sim-scale300). Nothing is run; prints markdown tables.

    python3 simulation/simlab/stagec_numbers.py > reports/sim-stageC-plan/numbers.md

Grid: 600 s. 100 and 300 clients x 4 layouts x pfifo / CoDel x 2 seeds, GT-Q with sampled router trace (upstream +
every 10th leaf, >= 3 leaves). 1000 clients: pfifo, 4 layouts x 2 seeds + the U 0.70 row (2 runs; layout L50 assumed,
FLAG), no GT-Q, no router trace. 10,000-client column: per 100 simulated seconds, no router trace (its run length is
not planned).

Rules (FLAG, every one an assumption):
- sizes and times linear in client-seconds, except where stated;
- health / GT-Q memory and time linear in router-trace bytes;
- detector / SETS memory linear in client-s (upper bounds, unmeasured above 300 clients);
- quicsim time linear .. N^1.24 (25 -> 300 clients);
- U 0.70 runs x1.4 simulation time (more background packets; unmeasured);
- quadratic scoring input: det_eval.Run is built twice per flow in each gt3.run_truth call (SETS step and GT3 step),
  0.164 s per build at 300 x 335 s (measured); one build parses topology.yaml (grows with N) and scenario.yaml (grows
  with N x duration).
"""

from __future__ import annotations

import math

CS300 = 300 * 335
M = {  # measured, 300 x 335 s
    "rt_up_raw": 601.2e6, "rt_leaf_raw": 2304.6e6, "rt_z": 393.7e6,
    "pub_raw": 1958.8e6, "pkts_raw": 227.2e6, "pub_z": 445.6e6, "pkts_z": 70.4e6,
    "rest_raw": 232.2e6 + 123.9e6 + 11.6e6, "rest_z": 66.7e6 + 8.1e6,
    "cache_raw": 1246.4e6, "cache_z": 406.2e6, "onsets": 178.9e3,
    "quicsim_s": 474.7, "quicsim_rss": 0.52, "health_s": 557, "health_gb": 8.96, "gtq_s": 1345, "gtq_gb": 11.0,
    "det_s": 184, "det_gb": 1.41, "sets_s": 200, "sets_gb": 2.29, "gt3_s": 145,
    "build_s": 0.164, "yaml_topo": 29186, "yaml_scen": 71976, "pair_s_close": 2.45 / 40, "closes": 40,
}
TRACE300 = M["rt_up_raw"] + M["rt_leaf_raw"]
LAYOUTS = {"L10": 10, "L50": 50, "L100": 100, "uneven": 50}   # uneven: L50 proxy for the sampled share (FLAG)


def f_sampled(n, size):
    L = max(1, n // size)
    return min(L, max(3, math.ceil(L / 10))) / L


def quad_s(n, dur):
    """Seconds of det_eval.Run builds in ONE gt3.run_truth call (2 builds per flow)."""
    per_build = M["build_s"] * (M["yaml_topo"] * n / 300 + M["yaml_scen"] * n * dur / (300 * 335)) / (M["yaml_topo"] + M["yaml_scen"])
    return 2 * n * per_build


def run(n, layout, q, seed, u, dur, trace):
    cs = n * dur
    k = cs / CS300
    f = f_sampled(n, LAYOUTS[layout]) if trace else 0.0
    rt_raw = (M["rt_up_raw"] + f * M["rt_leaf_raw"]) * k if trace else 0.0
    rt_z = rt_raw * M["rt_z"] / TRACE300
    pk = f if trace else 0.0                                     # -pkts / -pktacks only where traced
    pub_raw = (M["pub_raw"] - (1 - pk) * M["pkts_raw"]) * k
    pub_z = (M["pub_z"] - (1 - pk) * M["pkts_z"]) * k
    tb = rt_raw / TRACE300                                       # trace bytes relative to the 300 run
    simf = 1.4 if u == "U0.70" else 1.0
    closes = M["closes"] * dur / 335
    quad = quad_s(n, dur)
    t = {"sim": M["quicsim_s"] * n / 300 * dur / 335 * simf, "sim_hi": M["quicsim_s"] * (n / 300) ** 1.24 * dur / 335 * simf,
         "health": M["health_s"] * tb if trace else 0.0, "gtq": M["gtq_s"] * tb if trace else 0.0,
         "det": M["det_s"] * k,
         "sets": (M["sets_s"] - quad_s(300, 335) - M["pair_s_close"] * M["closes"]) * k + M["pair_s_close"] * (n / 300) ** 2 * closes + quad,
         "gt3": (M["gt3_s"] - quad_s(300, 335)) * k + quad, "quad": 2 * quad}
    mem = {"sim": (520 + 0.56 * (n - 300)) / 1024, "health": M["health_gb"] * tb if trace else 0.0,
           "gtq": M["gtq_gb"] * tb if trace else 0.0, "det": M["det_gb"] * k, "sets": M["sets_gb"] * k}
    disk = {"router-trace": (rt_raw, rt_z), "publishers": (pub_raw, pub_z), "rest": (M["rest_raw"] * k, M["rest_z"] * k),
            "onsets+events": (M["onsets"] * 2 * k, M["onsets"] * 2 * k), "tick cache": (M["cache_raw"] * k, M["cache_z"] * k)}
    return {"n": n, "layout": layout, "q": q, "seed": seed, "u": u, "dur": dur, "trace": trace, "f": f, "cs": cs,
            "t": t, "mem": mem, "disk": disk}


def grid(dur=600):
    rs = [run(n, lay, q, s, "U0.50", dur, True) for n in (100, 300) for lay in LAYOUTS for q in ("pfifo", "codel") for s in (1, 2)]
    rs += [run(1000, lay, "pfifo", s, "U0.50", dur, False) for lay in LAYOUTS for s in (1, 2)]
    rs += [run(1000, "L50", "pfifo", s, "U0.70", dur, False) for s in (1, 2)]
    return rs


def gb(x):
    return f"{x / 1e9:.1f}"


def main():
    rs = grid()
    print(f"# Stage C numbers (extrapolated from the 300-client run; rules in simulation/simlab/stagec_numbers.py)\n")
    print(f"Grid: {len(rs)} runs, {sum(r['cs'] for r in rs) / 1e6:.2f} M client-seconds.\n")
    print("## Per run (600 s)\n")
    print("| clients | layout | queue | U | runs | sampled f | raw output GB | zstd output GB | tick cache raw GB | "
          "sim min | health min | GT-Q min | detector min | SETS min | GT3 min | of which N^2 input min | "
          "peak GB: sim / health / GT-Q / detector / SETS |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    seen = {}
    for r in rs:
        key = (r["n"], r["layout"], r["q"], r["u"])
        seen.setdefault(key, []).append(r)
    for (n, lay, q, u), group in seen.items():
        r = group[0]
        raw = sum(v[0] for k, v in r["disk"].items() if k != "tick cache")
        z = sum(v[1] for k, v in r["disk"].items() if k != "tick cache")
        t, m = r["t"], r["mem"]
        print(f"| {n} | {lay} | {q} | {u} | {len(group)} | {r['f']:.2f} | {gb(raw)} | {gb(z)} | {gb(r['disk']['tick cache'][0])} | "
              f"{min(t['sim'], t['sim_hi']) / 60:.0f}-{max(t['sim'], t['sim_hi']) / 60:.0f} | {t['health'] / 60:.0f} | {t['gtq'] / 60:.0f} | {t['det'] / 60:.0f} | "
              f"{t['sets'] / 60:.0f} | {t['gt3'] / 60:.0f} | {t['quad'] / 60:.0f} | "
              f"{m['sim']:.1f} / {m['health']:.1f} / {m['gtq']:.1f} / {m['det']:.1f} / {m['sets']:.1f} |")

    print("\n## Disk for the grid, by component (GB)\n")
    print("| component | raw | zstd -3 |")
    print("|---|---|---|")
    for comp in ("router-trace", "publishers", "rest", "onsets+events", "tick cache"):
        print(f"| {comp} | {gb(sum(r['disk'][comp][0] for r in rs))} | {gb(sum(r['disk'][comp][1] for r in rs))} |")
    raw_out = sum(sum(v[0] for k, v in r["disk"].items() if k != "tick cache") for r in rs)
    z_out = sum(sum(v[1] for k, v in r["disk"].items() if k != "tick cache") for r in rs)
    big = max(rs, key=lambda r: sum(v[0] for v in r["disk"].values()))
    big_raw = sum(v[0] for k, v in big["disk"].items() if k != "tick cache")
    print(f"| **outputs (all but cache)** | **{gb(raw_out)}** | **{gb(z_out)}** |")
    print(f"\nLargest single run in flight: {big['n']} clients {big['layout']}: raw output {gb(big_raw)} GB + its tick cache "
          f"{gb(big['disk']['tick cache'][0])} GB raw (outside quiclab/).")

    print("\n## Time for the grid (hours)\n")
    tot = lambda k: sum(r["t"][k] for r in rs) / 3600   # noqa: E731
    heavy = tot("health") + tot("gtq") + tot("det")
    light = tot("sets") + tot("gt3")
    print("| part | hours | how it runs |")
    print("|---|---|---|")
    print(f"| simulation | {tot('sim'):.1f} - {tot('sim_hi'):.1f} core-h | in parallel |")
    print(f"| heavy scoring (health, GT-Q, detector) | {heavy:.1f} | one at a time |")
    print(f"| light scoring (SETS, GT3) | {light:.1f} core-h | beside the heavy queue |")
    print(f"| of which the N^2 input reading (det_eval.Run per flow) | {tot('quad'):.1f} core-h | inside SETS and GT3 |")
    by = {n: sum(r["t"]["quad"] for r in rs if r["n"] == n) / 3600 for n in (100, 300, 1000)}
    print(f"\nN^2 input reading by size: 100: {by[100]:.1f} h, 300: {by[300]:.1f} h, 1000: {by[1000]:.1f} h.")
    print(f"Light scoring at 1000 clients: {sum(r['t']['sets'] + r['t']['gt3'] for r in rs if r['n'] == 1000) / 3600:.1f} core-h, "
          f"heavy at 1000: {sum(r['t']['det'] for r in rs if r['n'] == 1000) / 3600:.1f} h.")

    print("\n## 10,000 clients, no router trace, per 100 simulated seconds (run length not planned)\n")
    r = run(10000, "L50", "pfifo", 1, "U0.50", 100, False)
    raw = sum(v[0] for k, v in r["disk"].items() if k != "tick cache")
    z = sum(v[1] for k, v in r["disk"].items() if k != "tick cache")
    t, m = r["t"], r["mem"]
    print("| quantity | per 100 s simulated |")
    print("|---|---|")
    print(f"| raw output / zstd | {gb(raw)} / {gb(z)} GB |")
    print(f"| tick cache raw / zstd | {gb(r['disk']['tick cache'][0])} / {gb(r['disk']['tick cache'][1])} GB |")
    print(f"| simulation | {t['sim'] / 3600:.1f} - {t['sim_hi'] / 3600:.1f} h, peak {m['sim']:.1f} GB |")
    print(f"| detector | {t['det'] / 60:.0f} min, <= {m['det']:.1f} GB |")
    print(f"| SETS step | {t['sets'] / 3600:.1f} h (of which N^2 input {quad_s(10000, 100) / 3600:.1f} h, pair loop "
          f"{M['pair_s_close'] * (10000 / 300) ** 2 * M['closes'] * 100 / 335 / 3600:.1f} h), <= {m['sets']:.1f} GB |")
    print(f"| GT3 step | {t['gt3'] / 3600:.1f} h (of which N^2 input {quad_s(10000, 100) / 3600:.1f} h) |")
    print("| health | light check only (not written) |")
    print("| GT-Q | not run (user) |")


if __name__ == "__main__":
    main()
