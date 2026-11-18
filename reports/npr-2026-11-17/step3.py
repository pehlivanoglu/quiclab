#!/usr/bin/env python3
"""NPR STEP 3 (scale): synthetic model at 100 and 1000 clients, leaves of 10 to 500, next to SETS.

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/step3.py rows --m M --f F --rho RHO --na NA [--jobs 2]
    .venv/bin/python3 reports/npr-2026-11-17/step3.py report

Model (flat leaves under one root):
  - each event, each leaf is on with probability PI_LEAF; with probability P_UP the root is on (every leaf on);
    events with no leaf on are not generated;
  - a non-NA member of an on leaf has x = 1 with probability p_e ~ Beta (mean 1 - m, intra-event correlation rho):
    the measured bursty miss pattern; of an off leaf with probability f (false inclusion);
  - a member is NA with probability NA (in alarm from an earlier event).
m, f, rho, NA are the measured values of the selected event formation (passed in; P / FLAG). Reads at every
CHECK-th event (FLAG: cost), for NPR (V-bin and V-bb, alpha 0.05 / 0.01 / 0.1) and SETS (k = 1, 2, 3; the table of
the events' observed sets). Scored with the common scorer at each read; read time = wall clock of one read.
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))

PI_LEAF, P_UP = 0.25, 0.10     # (FLAG) leaf / root on probability per event
EVENTS, CHECK = 120, 5          # (FLAG) events per synthetic run, read every 5 events
LAYOUTS = {                     # (P) clients -> leaf sizes, 10 to 500
    100: (10, 20, 30, 40),
    1000: (10, 50, 100, 340, 500),
}
SEEDS = (1, 2)
ALPHAS = (0.05, 0.01, 0.1)
ROWS = HERE / "step3-rows.jsonl"


def synth(n_clients, sizes, m, f, rho, na, seed):
    rng = np.random.default_rng(seed)
    clients = [f"c{i:04d}" for i in range(n_clients)]
    leaves, i = {}, 0
    for j, s in enumerate(sizes):
        leaves[f"L{j}"] = clients[i:i + s]
        i += s
    events = []
    while len(events) < EVENTS:
        up = rng.random() < P_UP
        on = {n: up or rng.random() < PI_LEAF for n in leaves}
        if not any(on.values()):
            continue
        ones, nas = [], {}
        for n, mem in leaves.items():
            if on[n]:
                p = 1 - m if rho <= 0 else rng.beta((1 - m) * (1 - rho) / rho, m * (1 - rho) / rho) if m > 0 else 1.0
            else:
                p = f
            for c in mem:
                if rng.random() < na:
                    nas[c] = "in-alarm"
                elif rng.random() < p:
                    ones.append(c)
        hot = sorted([n for n, o in on.items() if o] + (["up"] if up else []))
        events.append({"ones": ones, "na": nas, "hot": hot, "close": float(len(events))})
    ts = {n: {"members": frozenset(v), "level": "leaf"} for n, v in leaves.items()}
    ts["up"] = {"members": frozenset(clients), "level": "up"}
    return clients, ts, events


def worker(args):
    n, sizes, m, f, rho, na, seed = args
    try:
        return _worker(n, sizes, m, f, rho, na, seed)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {"n": n, "seed": seed, "error": repr(ex), "tb": traceback.format_exc()[-2000:]}


def _worker(n, sizes, m, f, rho, na, seed):
    import grouping_score as gs
    import npr
    from grouping import sets as S
    from grouping.sets import SetsConfig
    import step12
    scfg = SetsConfig()
    clients, ts, events = synth(n, sizes, m, f, rho, na, seed)
    checks = list(range(CHECK - 1, len(events), CHECK))
    res, rt = {}, {}
    # SETS
    table = Counter()
    sc = {k: gs.Score(ts, clients) for k in (1, 2, 3)}
    t_s = []
    for i, e in enumerate(events):
        mset = frozenset(e["ones"])
        if len(mset) >= scfg.min_set:
            table[mset] += 1
        if i in checks:
            hn = set(e["hot"])
            hl = {"leaf" if x != "up" else "up" for x in hn}
            for k in (1, 2, 3):
                t = time.perf_counter()
                gr = [frozenset(g.members) for g in S.groups(table, k, scfg)] if table else []
                t_s.append(time.perf_counter() - t)
                sc[k].close(e["close"], hl, hn, gr)
    for k in (1, 2, 3):
        res[f"SETS k{k}"] = sc[k].summary()
    rt["SETS"] = t_s
    for v in ("bin", "bb"):
        rd = npr.Reader(clients, variant=v, rho=rho if v == "bb" else 0.0)
        scs = {a: gs.Score(ts, clients) for a in ALPHAS}
        tt = []
        for i, e in enumerate(events):
            rd.add(step12.matrix_col(e, clients))
            if i not in checks:
                continue
            t = time.perf_counter()
            r = rd.read(ALPHAS)
            tt.append(time.perf_counter() - t)
            hn = set(e["hot"])
            hl = {"leaf" if x != "up" else "up" for x in hn}
            for a in ALPHAS:
                scs[a].close(e["close"], hl, hn, [frozenset(g) for g in r["groups"][a]])
        for a in ALPHAS:
            res[f"NPR-{v} a{a}"] = scs[a].summary()
        rt[f"NPR-{v}"] = tt
    return {"n": n, "sizes": list(sizes), "m": m, "f": f, "rho": rho, "na": na, "seed": seed, "methods": res,
            "read_s": rt}


def cmd_rows(m, f, rho, na, jobs):
    jobs_l = [(n, sizes, m, f, rho, na, s) for n, sizes in LAYOUTS.items() for s in SEEDS]
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for out in pool.imap_unordered(worker, jobs_l):
            fh.write(json.dumps(out, default=lambda o: (sorted(o) if isinstance(o, (set, frozenset)) else
                                                         (o.tolist() if hasattr(o, "tolist") else str(o)))) + "\n")
            fh.flush()
            print(f"  n {out['n']} seed {out['seed']}{' ERROR ' + out['error'] if 'error' in out else ''}", flush=True)


def report():
    R = [json.loads(x) for x in ROWS.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    print("# NPR STEP 3 synthetic tables\n")
    if bad:
        print(f"Errors: {[(b['n'], b['seed'], b['error']) for b in bad]}\n")
    keys = sorted({(r["m"], r["f"], r["rho"], r["na"]) for r in R})
    for key in keys:
        print(f"## m {key[0]}, f {key[1]}, rho {key[2]}, NA {key[3]} (seeds {SEEDS} side by side)\n")
        for n in LAYOUTS:
            rows = [r for r in R if (r["m"], r["f"], r["rho"], r["na"]) == key and r["n"] == n]
            if not rows:
                continue
            print(f"### {n} clients, leaves {LAYOUTS[n]}\n")
            print("| method | leaf F1 | pair P | pair R | spurious / read | reads to first correct group (p50 over leaves) "
                  "| leaves never | read time p50 / max s |")
            print("|---|---|---|---|---|---|---|---|")
            for meth in rows[0]["methods"]:
                cells = []
                for r in sorted(rows, key=lambda r: r["seed"]):
                    s = r["methods"][meth]
                    p = s["pairs"]
                    pp = p[0] / (p[0] + p[1]) if p[0] + p[1] else float("nan")
                    pr = p[0] / (p[0] + p[2]) if p[0] + p[2] else float("nan")
                    ev = [e for e, _ in s["t_ok"].values()]
                    cells.append((s["levels"]["leaf"][2] if "leaf" in s["levels"] else float("nan"), pp, pr, s["spur"],
                                  np.median(ev) if ev else float("nan"), s["n_leaves"] - len(s["t_ok"])))
                fam = "SETS" if meth.startswith("SETS") else meth.split(" ")[0]
                t = [x for r in rows for x in r["read_s"].get(fam, [])]
                c = lambda i, d=3: " / ".join(f"{x[i]:.{d}f}" for x in cells)   # noqa: E731
                print(f"| {meth} | {c(0)} | {c(1)} | {c(2)} | {c(3, 2)} | {c(4, 0)} | "
                      f"{' / '.join(str(x[5]) for x in cells)} | {np.median(t):.4f} / {max(t):.3f} |")
            print()


def main(argv):
    if argv[0] == "rows":
        g = lambda k: float(argv[argv.index(k) + 1])   # noqa: E731
        cmd_rows(g("--m"), g("--f"), g("--rho"), g("--na"), int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2)
    elif argv[0] == "report":
        report()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
