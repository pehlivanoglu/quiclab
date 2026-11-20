#!/usr/bin/env python3
"""NPR variants V-A / V-B / V-C on E1-0.5 (user, 2026-11-18): the same runs and tables as steps 1-2.

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/step12v.py rows [--jobs 2]   # rows-v3-E1-0.5.jsonl
    .venv/bin/python3 reports/npr-2026-11-17/step12v.py report

Readers (npr_var.make): "corr" (the corrected test), "B" (past-fitted null), "A-m<m_max>-f<f_max>" for m_max in
{0.10, 0.20, 0.30} x f_max in {0.02, 0.05, 0.10} (main A-m0.20-f0.05). corr and the main A are read at the tier
alphas (E >= 1, 2, 5, 10, 20, 100: V-C); the others at alpha 0.05, 0.01, 0.1. Per reader and alpha: the common
scorer at every close, STEP 2 calibration (original order + 20 random orders), the late joiner (alpha 0.05), and the
event of the root's first accepted split against the first separating event (the diagnosis table).
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "scripts"), str(ROOT)]

SRC = ROOT / "reports" / "npr-step0b-2026-11-17" / "rows.jsonl"
CAND = "E1-0.5"
A_MAIN = "A-m0.20-f0.05"
SPECS = ("corr", "B", *[f"A-m{m:.2f}-f{f:.2f}" for m in (0.10, 0.20, 0.30) for f in (0.02, 0.05, 0.10)])
BASE_ALPHAS = (0.05, 0.01, 0.1)
PERMS = 20
ROWS = HERE / "rows-v3-E1-0.5.jsonl"


def alphas_of(spec):
    import npr_var
    return npr_var.TIER_ALPHAS if spec in ("corr", A_MAIN) else BASE_ALPHAS


def run_reader(spec, events, clients, alphas, hidden=None, until_release=None):
    import npr_var
    import step12
    rd = npr_var.make(spec, clients)
    reads = []
    for e in events:
        rd.add(step12.matrix_col(e, clients))
        t = time.perf_counter()
        r = rd.read(alphas)
        r["read_s"] = time.perf_counter() - t
        reads.append(r)
    return reads


def late_joiner(spec, ts, clients, ev):
    import grouping_score as gs
    import npr_var
    import step12
    out = []
    for n, info in ts.items():
        if info["level"] != "leaf" or len(info["members"]) < 3:
            continue
        L = frozenset(info["members"])
        hid = max(info["members"])
        rest = L - {hid}
        st = {"rel": None, "join": None}
        rd = npr_var.make(spec, clients)
        for i, e in enumerate(ev):
            hide = st["rel"] is None
            ones = [c for c in e["ones"] if not (hide and c == hid)]
            rd.add(step12.step_col(ones, e["na"], clients, hid if hide else None))
            groups = [frozenset(g) for g in rd.read((0.05,))["groups"][0.05]]
            if st["rel"] is None:
                if any(gs._f1(g, rest)[2] >= gs.F1_OK for g in groups):
                    st["rel"] = (i, e["close"])
            elif any(hid in g and gs._f1(g, L)[2] >= gs.F1_OK for g in groups):
                st["join"] = (i, e["close"])
                break
        rec = {"leaf": n, "released": st["rel"] is not None, "joined": st["join"] is not None}
        if st["rel"] and st["join"]:
            rec.update(events=st["join"][0] - st["rel"][0], seconds=st["join"][1] - st["rel"][1])
        out.append(rec)
    return out


def worker(row):
    try:
        return _worker(row)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {"run": row["run"], "error": repr(ex), "tb": traceback.format_exc()[-2500:]}


def _worker(row):
    import step12
    clients = row["clients"]
    ts = {n: {"members": frozenset(v["members"]), "level": v["level"]} for n, v in row["truth"].items()}
    ev = [e for e in row["cands"][CAND] if e["ones"]]
    calm = row["type"] == "calm" or not any(v["level"] == "leaf" for v in ts.values())
    out = {k: row[k] for k in ("run", "campaign", "block", "type", "aqm", "rep", "topology")}
    out["first_stim"] = step12.first_stim(ROOT / ".runs" / row["campaign"] / row["run"], list(ts))
    out["truth"] = row["truth"]
    L = {n: set(v["members"]) for n, v in row["truth"].items() if v["level"] == "leaf"}
    sep = None
    for i, e in enumerate(ev):
        H = set(e["hot"])
        on = [n for n in L if n in H or any(a in H for a, v in row["truth"].items() if a != n and L[n] < set(v["members"]))]
        if 0 < len(on) < len(L):
            sep = i + 1
            break
    out["first_separating_event"] = sep
    out["methods"], out["first_split"], out["late"], out["read_s"], out["calibration"] = {}, {}, {}, {}, []
    for spec in SPECS:
        al = alphas_of(spec)
        reads = run_reader(spec, ev, clients, al)
        out["read_s"][spec] = [r["read_s"] for r in reads]
        for a in al:
            if not calm:
                out["methods"][f"NPR-{spec} a{a}"] = step12.score_series(
                    ts, clients, ev, lambda i, a=a: [frozenset(g) for g in reads[i]["groups"][a]])
            out["first_split"][f"{spec} a{a}"] = next((i + 1 for i, r in enumerate(reads) if len(r["groups"][a]) > 1), None)
        if not calm:
            out["late"][spec] = late_joiner(spec, ts, clients, ev)
    # STEP 2 calibration: each true leaf alone, original order + PERMS random orders
    for n, mem in sorted((n, sorted(v)) for n, v in L.items()):
        sub = [e for e in ev if set(e["ones"]) & set(mem)]
        if len(mem) < 2 or len(sub) < 2:
            continue
        sub = [{**e, "ones": [c for c in e["ones"] if c in mem], "na": {c: x for c, x in e["na"].items() if c in mem}}
               for e in sub]
        for order in range(PERMS + 1):
            seq = list(sub)
            if order:
                random.Random(order - 1).shuffle(seq)
            rec = {"leaf": n, "size": len(mem), "events": len(seq), "whole_run": len(L) == 1, "perm": order}
            for spec in SPECS:
                al = alphas_of(spec)
                reads = run_reader(spec, seq, mem, al)
                for a in al:
                    rec[f"{spec} a{a}"] = any(len(r["groups"][a]) > 1 for r in reads)
            out["calibration"].append(rec)
    return out


def cmd_rows(jobs):
    rows = [json.loads(x) for x in SRC.read_text().splitlines() if x.strip()]
    rows = [r for r in rows if "error" not in r]
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}")]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rows = [r for r in rows if r["run"] not in done]
    print(f"{len(rows)} runs ({len(done)} already done)", flush=True)
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, out in enumerate(pool.imap_unordered(worker, rows), 1):
            fh.write(json.dumps(out, default=lambda o: None if (isinstance(o, float) and not math.isfinite(o))
                                else (sorted(o) if isinstance(o, (set, frozenset)) else
                                      (o.tolist() if hasattr(o, "tolist") else str(o)))) + "\n")
            fh.flush()
            print(f"  {i}/{len(rows)} {out['run']}{' ERROR ' + out['error'] if 'error' in out else ''}", flush=True)


def report():
    import step12_report as S
    R = [json.loads(x) for x in ROWS.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    FQ = S.FQ
    sq = lambda r: r["aqm"] not in FQ and r.get("methods")   # noqa: E731
    print("# NPR variants on E1-0.5 (step12v.py)\n")
    if bad:
        print(f"Errors: {[(b['run'], b['error']) for b in bad]}\n")
    old = {}
    for line in open(HERE / "rows-v2-E1-0.5.jsonl"):
        r = json.loads(line)
        old[r["run"]] = r
    refF = [S.pooled([old[r["run"]] for r in R if sq(r) and r["rep"] == rep and r["run"] in old], "SETS@E0 k2")
            for rep in (1, 2)]
    print(f"Frozen SETS k = 2 leaf F1 (same runs): {S.f_(refF[0]['F'])} / {S.f_(refF[1]['F'])}.\n")
    print("| variant | alpha (accept at E >= 1/alpha) | false-split share r1 / r2 (20 orders mean) | pair P | leaf F1 | "
          "root split lag, 2-leaf groups p50 / p90 (never) | first correct group s p50 / p90 | meets all three | "
          "passes at 0.90 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for spec in SPECS:
        for a in alphas_of(spec):
            m = f"NPR-{spec} a{a}"
            v = [S.pooled([r for r in R if sq(r) and r["rep"] == rep], m) for rep in (1, 2)]
            t = [S.times([r for r in R if sq(r) and r["rep"] == rep], m) for rep in (1, 2)]
            fs = []
            for rep in (1, 2):
                x = [c[f"{spec} a{a}"] for r in R if r["aqm"] not in FQ and r["rep"] == rep for c in r["calibration"]
                     if c["perm"] == 0]
                fs.append(float(np.mean(x)) if x else float("nan"))
            pm = [float(np.mean([c[f"{spec} a{a}"] for r in R if r["aqm"] not in FQ for c in r["calibration"]
                                 if c["perm"] == p])) for p in range(1, PERMS + 1)]
            lag = [r["first_split"][f"{spec} a{a}"] - r["first_separating_event"] for r in R if sq(r)
                   and len([1 for x in r["truth"].values() if x["level"] == "leaf"]) == 2
                   and r["first_split"][f"{spec} a{a}"] and r["first_separating_event"]]
            nev = sum(1 for r in R if sq(r) and len([1 for x in r["truth"].values() if x["level"] == "leaf"]) == 2
                      and not r["first_split"][f"{spec} a{a}"])
            ok, ok90 = (all(v[i] and v[i]["pP"] >= thr and v[i]["F"] >= refF[i]["F"] - 1e-12 and fs[i] <= a + 1e-12
                            for i in (0, 1)) for thr in (0.93, 0.90))
            lagt = f"{np.median(lag):.0f} / {np.percentile(lag, 90):.0f} ({nev})" if lag else f"- ({nev})"
            print(f"| {spec} | {a} (E >= {1 / a:g}) | {fs[0]:.3f} / {fs[1]:.3f} ({np.mean(pm):.3f}) | "
                  f"{' / '.join(S.f_(x['pP']) for x in v)} | {' / '.join(S.f_(x['F']) for x in v)} | {lagt} | "
                  f"{' / '.join(S.f_(x['s50'], 0) + ' / ' + S.f_(x['s90'], 0) for x in t)} | {'**yes**' if ok else 'no'} | "
                  f"{'**yes**' if ok90 else 'no'} |")
    print()
    print("## Full step 1-2 columns (single-queue, r1 / r2)\n")
    print("| variant | alpha | leaf P | leaf R | pair R | spurious / close | first correct group events p50 / p90 | "
          "late joiner joined / released, events p50, s p50 |")
    print("|---|---|---|---|---|---|---|---|")
    for spec in SPECS:
        for a in alphas_of(spec):
            m = f"NPR-{spec} a{a}"
            v = [S.pooled([r for r in R if sq(r) and r["rep"] == rep], m) for rep in (1, 2)]
            t = [S.times([r for r in R if sq(r) and r["rep"] == rep], m) for rep in (1, 2)]
            lj = ""
            if a == 0.05:
                cells = []
                for rep in (1, 2):
                    xs = [x for r in R if sq(r) and r["rep"] == rep for x in r["late"].get(spec, [])]
                    rel = [x for x in xs if x["released"]]
                    j = [x for x in rel if x["joined"]]
                    md = lambda k: f"{np.median([x[k] for x in j]):.0f}" if j else "-"   # noqa: E731
                    cells.append(f"{len(j)} / {len(rel)}, {md('events')}, {md('seconds')}")
                lj = " ; ".join(cells)
            print(f"| {spec} | {a} | {' / '.join(S.f_(x['P']) for x in v)} | {' / '.join(S.f_(x['R']) for x in v)} | "
                  f"{' / '.join(S.f_(x['pR']) for x in v)} | {' / '.join(S.f_(x['sp'], 2) for x in v)} | "
                  f"{' ; '.join(S.f_(x['ev50'], 0) + ' / ' + S.f_(x['ev90'], 0) for x in t)} | {lj or '-'} |")
    print()
    leaf_rates()


def leaf_rates():
    """Per true leaf under E1-0.5: the per-member miss rate (0 among non-NA members of on events) and false-inclusion
    rate (1 on off events); leaves with a member above each V-A bound."""
    sys.path.insert(0, str(ROOT / "reports" / "npr-step0-2026-11-17"))
    import npr0_report as N
    per_leaf = []
    for line in open(SRC):
        r = json.loads(line)
        if "error" in r or N.cls(r) != "single":
            continue
        v = {"truth": r["truth"], "events": [e for e in r["cands"][CAND] if e["ones"]], "aqm": r["aqm"], "rep": r["rep"],
             "type": r["type"]}
        acc = {}
        for n, info, i, on, kind, k, nn, x in N.per_event(v):
            for c, val in x.items():
                if val not in (0, 1):
                    continue
                a = acc.setdefault((n, c), [0, 0, 0, 0])
                if on:
                    a[0] += val == 0
                    a[1] += 1
                else:
                    a[2] += val == 1
                    a[3] += 1
        leaves = {}
        for (n, c), a in acc.items():
            leaves.setdefault(n, []).append((a[0] / a[1] if a[1] else None, a[2] / a[3] if a[3] else None))
        per_leaf += list(leaves.values())
    ms = [m for lv in per_leaf for m, _ in lv if m is not None]
    fs = [f for lv in per_leaf for _, f in lv if f is not None]
    print("## Measured per-member rates under E1-0.5 (single-queue; truth = strict-hot as in STEP 0)\n")
    print(f"Members: miss rate p50 {np.median(ms):.3f}, p90 {np.percentile(ms, 90):.3f}, p99 {np.percentile(ms, 99):.3f}, "
          f"max {max(ms):.3f}; false-inclusion rate p50 {np.median(fs):.4f}, p90 {np.percentile(fs, 90):.4f}, "
          f"p99 {np.percentile(fs, 99):.4f}, max {max(fs):.3f} (strict-hot off events include the short real congestion "
          "of 0b.4, so this overstates false inclusion).\n")
    print("| bound | leaves with a member above it | of leaves |\n|---|---|---|")
    for b in (0.10, 0.20, 0.30):
        print(f"| m_max {b} | {sum(any(m is not None and m > b for m, _ in lv) for lv in per_leaf)} | {len(per_leaf)} |")
    for b in (0.02, 0.05, 0.10):
        print(f"| f_max {b} | {sum(any(f is not None and f > b for _, f in lv) for lv in per_leaf)} | {len(per_leaf)} |")
    print()


def main(argv):
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2)
    else:
        report()


if __name__ == "__main__":
    main(sys.argv[1:])
