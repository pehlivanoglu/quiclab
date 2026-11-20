#!/usr/bin/env python3
"""Diagnosis of the v3 variant table (user, 2026-11-18, items 2a-2e). Listing only: the same 263 runs, the same
readers (npr_var.make) and the same scorer; nothing in the tests is changed.

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/diag3.py rows [--jobs 2]   # diag3-rows.jsonl
    .venv/bin/python3 reports/npr-2026-11-17/diag3.py report > reports/npr-2026-11-17/diag3.md

rows (single-queue runs only, alpha 0.05, readers NPR_SPECS and SETS on E1-0.5 / E0 events):
  calibration, original order (perm 0 of step12v): each true leaf alone; for every false split the event, the parts
    and per member the miss rate and the onset-lag share (2a);
  whole run: the pair counts of the common scorer per close, split into different-leaf pairs (false merges) by leaf
    pair and by "before / after the root's first split" (2b), and the run's pair vector (checked against v3 rows);
  SETS k = 2, 3 on E1-0.5 and on E0 (frozen v1.1 events): first close with two or more groups, leaf-alone split (2d).
report: 2a-2e tables. Rows are read from diag3-rows.jsonl, rows-v3-E1-0.5.jsonl and rows-v2-E1-0.5.jsonl.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "scripts"), str(ROOT)]

SRC = ROOT / "reports" / "npr-step0b-2026-11-17" / "rows.jsonl"
ROWS = HERE / "diag3-rows.jsonl"
CAND = "E1-0.5"
FQ = ("fq_codel", "cake")
ALPHA = 0.05
NPR_SPECS = ("B", "corr", "A-m0.20-f0.05", "A-m0.10-f0.05")
LATE_S = 1.0        # (M) as D1: the member's onset falls into a later event within 1 s of this event's close
LATE_MISS = 0.10    # (P) user: late responder = miss rate > 0.10 ...
LATE_LAG = 0.5      # (M) ... or a consistent onset lag: at least half of its misses followed by its onset (LATE_S)
BOOT = 2000         # (M) bootstrap resamples over runs within a seed
PAIR_OK = 0.90      # (P) user 2026-11-18
WIDE_RTT_MS = 20.0  # (M, LABEL ONLY: listing, never a criterion; user 2026-11-19) 2f: a leaf is wide-RTT when its members' planned access delays span more than this (the
                    # standard sets span 5-20 ms; K1 G3 w16 spans 5-95 ms). Scenario definition, not a criterion.


def acc_split(c, part):
    """(split-off mean, rest mean, rest min-max, leaf span, wide) of planned access delays, or None if unknown."""
    a = c["access_ms"]
    if any(a.get(x) is None for x in a):
        return None
    rest = [a[x] for x in a if x not in part]
    off = [a[x] for x in part]
    span = max(a.values()) - min(a.values())
    return float(np.mean(off)), float(np.mean(rest)) if rest else None, (min(rest), max(rest)) if rest else None, span, \
        span > WIDE_RTT_MS


def reads_of(spec, events, clients):
    import npr_var
    import step12
    rd = npr_var.make(spec, clients)
    out = []
    for e in events:
        rd.add(step12.matrix_col(e, clients))
        out.append([frozenset(g) for g in rd.read((ALPHA,))["groups"][ALPHA]])
    return out


def sets_series(events, k):
    from grouping import sets as S
    from grouping.sets import SetsConfig
    cfg = SetsConfig()
    table, out = Counter(), []
    for e in events:
        m = frozenset(e["ones"])
        if len(m) >= cfg.min_set:
            table[m] += 1
        out.append([frozenset(g.members) for g in S.groups(table, k, cfg)] if table else [])
    return out


def member_stats(mem, sub, ev_all):
    """Per member of a leaf: miss rate on the leaf's events (0 among non-NA) and the share of its misses followed by
    its own onset in a later event starting within LATE_S of the miss event's close."""
    st = {}
    for x in mem:
        zeros = [j for j, e in enumerate(sub) if x not in e["ones"] and x not in e["na"]]
        nn = sum(1 for e in sub if x not in e["na"])
        lag = 0
        for j in zeros:
            e = sub[j]
            if any(x in f["ones"] and e["t0"] < f["t0"] <= e["close"] + LATE_S for f in ev_all):
                lag += 1
        miss = len(zeros) / nn if nn else None
        st[x] = {"miss": miss, "zeros": len(zeros), "lag_share": lag / len(zeros) if zeros else None,
                 "late": bool((miss is not None and miss > LATE_MISS) or (len(zeros) >= 2 and lag / len(zeros) >= LATE_LAG))}
    return st


def pair_split(ts, clients, groups_series, first_split):
    """The common scorer's pair rule (each client's smallest group; grouping_score.Score.close) per close, with the
    different-leaf pairs in one group (false merges) counted by leaf pair and by before / after the first split."""
    leaves = {n: set(v["members"]) for n, v in ts.items() if v["level"] == "leaf"}
    leaf_of = {c: n for n, s in leaves.items() for c in s}
    rank = {c: i for i, c in enumerate(clients)}
    key = lambda g: tuple(sorted((rank.get(c, -1) for c in g), reverse=True))   # noqa: E731
    pairs = np.zeros(5)
    fm = Counter()
    phase = {"before": np.zeros(2), "after": np.zeros(2)}   # [same-leaf together, different-leaf together]
    for i, groups in enumerate(groups_series):
        ph = "before" if first_split is None or i + 1 < first_split else "after"
        small = {}
        for c in clients:
            cg = [g for g in groups if c in g]
            if cg:
                small[c] = min(cg, key=lambda g: (len(g), key(g)))
        for a_i, a in enumerate(clients):
            for b in clients[a_i + 1:]:
                same = any(a in s and b in s for s in leaves.values())
                if a not in small or b not in small:
                    pairs[4] += 1
                elif small[a] == small[b]:
                    pairs[0 if same else 1] += 1
                    phase[ph][0 if same else 1] += 1
                    if not same:
                        fm["|".join(sorted((leaf_of.get(a, "-"), leaf_of.get(b, "-"))))] += 1
                else:
                    pairs[2 if same else 3] += 1
    return {"pairs": pairs.tolist(), "false_merge": dict(fm), "phase": {k: v.tolist() for k, v in phase.items()}}


def _worker(row):
    import yaml
    clients = row["clients"]
    ts = row["truth"]
    ev = [e for e in row["cands"][CAND] if e["ones"]]
    e0 = [e for e in row["cands"]["E0"] if e["ones"]]
    calm = row["type"] == "calm" or not any(v["level"] == "leaf" for v in ts.values())
    out = {k: row[k] for k in ("run", "campaign", "block", "type", "aqm", "rep")}
    rd = ROOT / ".runs" / row["campaign"] / row["run"]
    plan = json.loads((rd / "v3-plan.json").read_text()) if (rd / "v3-plan.json").exists() else {}
    acc = plan.get("access_delay_ms", {})
    L = {n: sorted(v["members"]) for n, v in ts.items() if v["level"] == "leaf"}
    # 2a: leaf alone, original order
    cal = []
    for n, mem in sorted(L.items()):
        sub = [e for e in ev if set(e["ones"]) & set(mem)]
        if len(mem) < 2 or len(sub) < 2:
            continue
        sub = [{**e, "ones": [c for c in e["ones"] if c in mem], "na": {c: x for c, x in e["na"].items() if c in mem}}
               for e in sub]
        stats = member_stats(mem, sub, ev)
        rec = {"leaf": n, "size": len(mem), "events": len(sub), "whole_run": len(L) == 1, "members": stats,
               "access_ms": {x: acc.get(x) for x in mem}, "splits": {}}
        meths = {s: (lambda s=s: reads_of(s, sub, mem)) for s in NPR_SPECS}
        e0s = [e for e in e0 if set(e["ones"]) & set(mem)]
        e0s = [{**e, "ones": [c for c in e["ones"] if c in mem]} for e in e0s]
        for k in (2, 3):
            meths[f"SETS@E1-0.5 k{k}"] = lambda k=k: sets_series(sub, k)
            meths[f"SETS@E0 k{k}"] = lambda k=k: sets_series(e0s, k)
        for m, f in meths.items():
            ser = f()
            i = next((j for j, g in enumerate(ser) if len(g) > 1), None)
            if i is None:
                rec["splits"][m] = None
                continue
            kids = [g for g in ser[i] if len(g) < len(mem)]
            covered = set().union(*kids) if kids else set()
            parts = sorted([sorted(g) for g in kids] + ([sorted(set(mem) - covered)] if set(mem) - covered else []),
                           key=len)
            rec["splits"][m] = {"event": i + 1, "close": sub[i]["close"] if not m.startswith("SETS@E0") else None,
                                "parts": parts}
        cal.append(rec)
    out["calibration"] = cal
    # 2b / 2d: whole run
    if not calm:
        out["first_separating_event"] = None
        for i, e in enumerate(ev):
            H = set(e["hot"])
            on = [n for n in L if n in H or any(a in H for a, v in ts.items() if a != n and set(L[n]) < set(v["members"]))]
            if 0 < len(on) < len(L):
                out["first_separating_event"] = i + 1
                break
        out["n_leaves"] = len(L)
        out["whole"] = {}
        for m in NPR_SPECS:
            ser = reads_of(m, ev, clients)
            fs = next((j + 1 for j, g in enumerate(ser) if len(g) > 1), None)
            out["whole"][f"NPR-{m} a{ALPHA}"] = {"first_split": fs, **pair_split(ts, clients, ser, fs)}
        for name, events in (("SETS@E1-0.5", ev), ("SETS@E0", e0)):
            for k in (2, 3):
                ser = sets_series(events, k)
                fs = next((j + 1 for j, g in enumerate(ser) if len(g) > 1), None)
                out["whole"][f"{name} k{k}"] = {"first_split": fs, "events": len(events),
                                                **pair_split(ts, clients, ser, fs)}
    return out


def worker(row):
    try:
        return _worker(row)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {"run": row["run"], "error": repr(ex), "tb": traceback.format_exc()[-2500:]}


def cmd_rows(jobs):
    rows = [json.loads(x) for x in SRC.read_text().splitlines() if x.strip()]
    rows = [r for r in rows if "error" not in r and r["aqm"] not in FQ]
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}")]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rows = [r for r in rows if r["run"] not in done]
    print(f"{len(rows)} runs ({len(done)} already done)", flush=True)
    enc = lambda o: (sorted(o) if isinstance(o, (set, frozenset)) else (o.tolist() if hasattr(o, "tolist") else str(o)))  # noqa: E731
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, out in enumerate(pool.imap_unordered(worker, rows), 1):
            fh.write(json.dumps(out, default=enc) + "\n")
            fh.flush()
            print(f"  {i}/{len(rows)} {out['run']}{' ERROR ' + out['error'] if 'error' in out else ''}", flush=True)


# ---------------------------------------------------------------------------------------------------------- report

def f_(x, d=3):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def pp(p):
    return p[0] / (p[0] + p[1]) if p[0] + p[1] else None


def boot_ci(vecs, seed=0):
    """95 % percentile interval of pooled pair precision, resampling runs within one seed."""
    if not vecs:
        return None, None
    v = np.array(vecs)
    rng = np.random.default_rng(seed)
    b = []
    for _ in range(BOOT):
        s = v[rng.integers(0, len(v), len(v))].sum(axis=0)
        if s[0] + s[1]:
            b.append(s[0] / (s[0] + s[1]))
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def cell(r):
    return f"{r['block']}-{r['type']}-{r['aqm']}"


def report():
    D = [json.loads(x) for x in ROWS.read_text().splitlines() if x.strip()]
    bad = [r for r in D if "error" in r]
    D = [r for r in D if "error" not in r]
    V3 = {r["run"]: r for r in map(json.loads, open(HERE / "rows-v3-E1-0.5.jsonl")) if "error" not in r}
    V2 = {r["run"]: r for r in map(json.loads, open(HERE / "rows-v2-E1-0.5.jsonl")) if "error" not in r}
    print("# NPR v3 diagnosis (items 2a-2e; diag3.py)\n")
    print(f"Single-queue runs {len(D)} ({sum(r['rep'] == 1 for r in D)} r1 / {sum(r['rep'] == 2 for r in D)} r2); "
          f"alpha {ALPHA}. Errors: {[(b['run'], b['error']) for b in bad] or 'none'}.\n")

    # consistency with the v3 rows: false-split share and pair vectors must be reproduced exactly
    chk = []
    for spec in NPR_SPECS:
        for rep in (1, 2):
            x = [bool(c["splits"][spec]) for r in D if r["rep"] == rep for c in r["calibration"]]
            y = [c[f"{spec} a{ALPHA}"] for r in D if r["rep"] == rep for c in V3[r["run"]]["calibration"] if c["perm"] == 0]
            chk.append(f"{spec} r{rep} {np.mean(x):.3f} (v3 {np.mean(y):.3f})")
    same = all(np.allclose(r["whole"][m]["pairs"], V3[r["run"]]["methods"][m]["pairs"])
               for r in D if r.get("whole") for m in r["whole"] if m.startswith("NPR-"))
    print("Check against rows-v3: false-split share " + "; ".join(chk) + f". Pair vectors identical: {same}.\n")

    # ---- 2a
    print("## 2a. V-B false splits (leaf alone, original order), r1 against r2\n")
    for spec in ("B",):
        for rep in (1, 2):
            C = [(r, c) for r in D if r["rep"] == rep for c in r["calibration"]]
            S_ = [(r, c) for r, c in C if c["splits"][spec]]
            print(f"### {spec}, r{rep}: {len(S_)} false splits of {len(C)} leaves ({len(S_) / len(C):.3f})\n")
            by_run = Counter(r["run"] for r, _ in S_)
            by_cell = Counter(cell(r) for r, _ in S_)
            leaves_cell = Counter(cell(r) for r, _ in C)
            sizes = Counter(len(c["splits"][spec]["parts"][0]) for _, c in S_)
            late_n = wide_n = unk_n = 0
            lines = []
            for r, c in S_:
                part = c["splits"][spec]["parts"][0]
                lt = [x for x in part if c["members"][x]["late"]]
                late_n += bool(lt)
                ms = ", ".join(f"{x} miss {f_(c['members'][x]['miss'], 2)} lag {f_(c['members'][x]['lag_share'], 2)}"
                               for x in part)
                ac = acc_split(c, part)
                if ac is None:
                    unk_n += 1
                    act, wt = "unknown (plan has no access delays)", "unknown"
                else:
                    wide_n += ac[4]
                    act = (f"{ac[0]:.1f} vs {f_(ac[1], 1)} ({ac[2][0]:g}-{ac[2][1]:g})" if ac[2] else f"{ac[0]:.1f} vs -")
                    wt = f"{'yes' if ac[4] else 'no'} (span {ac[3]:g})"
                lines.append(f"| {r['run']} | {c['leaf']} ({c['size']}) | {c['splits'][spec]['event']} / {c['events']} | "
                             f"{len(part)} | {ms} | {act} | {wt} | {'yes' if lt else 'no'} |")
            print(f"Split-off part size: {dict(sorted(sizes.items()))}; split-off part holds a late responder: "
                  f"{late_n} / {len(S_)}; runs with a false split: {len(by_run)} (max {max(by_run.values(), default=0)} "
                  f"per run); from wide-RTT leaves (access-delay span > {WIDE_RTT_MS:g} ms): {wide_n} / {len(S_)}"
                  f"{f' ({unk_n} with unknown access delays)' if unk_n else ''}.\n")
            print("| cell | false splits / leaves |\n|---|---|")
            for k, v in sorted(by_cell.items(), key=lambda z: -z[1]):
                print(f"| {k} | {v} / {leaves_cell[k]} |")
            print("\n| run | leaf (size) | split at event / events | part size | split-off members (miss rate, onset-lag "
                  "share) | access ms: split-off mean vs rest mean (rest range) | wide-RTT leaf | late responder |"
                  "\n|---|---|---|---|---|---|---|---|")
            print("\n".join(lines))
            print()
        # paired by cell: same cell in both seeds
        cells = sorted({cell(r) for r in D})
        diff = []
        for k in cells:
            n = [sum(bool(c["splits"][spec]) for r in D if r["rep"] == rep and cell(r) == k for c in r["calibration"])
                 for rep in (1, 2)]
            if n[0] != n[1]:
                diff.append((k, n))
        print(f"Cells whose count of B false splits differs between r1 and r2: "
              + "; ".join(f"{k} {a} / {b}" for k, (a, b) in diff) + "\n")
        # late responders in leaves: present in both seeds?
        lr = []
        for rep in (1, 2):
            C = [c for r in D if r["rep"] == rep for c in r["calibration"]]
            lr.append((sum(any(m["late"] for m in c["members"].values()) for c in C), len(C),
                       sum(bool(c["splits"][spec]) for c in C if any(m["late"] for m in c["members"].values())),
                       sum(bool(c["splits"][spec]) for c in C if not any(m["late"] for m in c["members"].values()))))
        print("| rep | leaves with a late responder / leaves | false splits in those leaves | in leaves without |\n|---|---|---|---|")
        for rep, (a, b, s1, s0) in zip((1, 2), lr):
            print(f"| r{rep} | {a} / {b} | {s1} / {a} | {s0} / {b - a} |")
        print()
        # other methods for reference
        print("Leaf-alone false splits, other readers and SETS (r1 / r2): " + "; ".join(
            f"{m} " + " / ".join(f"{sum(bool(c['splits'][m]) for r in D if r['rep'] == rep for c in r['calibration'])}"
                                 for rep in (1, 2))
            for m in ("corr", "A-m0.20-f0.05", "A-m0.10-f0.05")) + ".\n")

    # ---- 2b
    print("## 2b. False merges behind pair precision (corr, V-A, and B for reference)\n")
    W = [r for r in D if r.get("whole")]
    for m in ("NPR-corr a0.05", "NPR-A-m0.20-f0.05 a0.05", "NPR-A-m0.10-f0.05 a0.05", "NPR-B a0.05"):
        print(f"### {m}\n")
        print("| rep | pair P | different-leaf pairs together: before the root's first split / after | runs never split "
              "(2+ leaves) | their share of different-leaf pairs |\n|---|---|---|---|---|")
        for rep in (1, 2):
            R = [r for r in W if r["rep"] == rep]
            p = np.sum([r["whole"][m]["pairs"] for r in R], axis=0)
            bf = sum(r["whole"][m]["phase"]["before"][1] for r in R)
            af = sum(r["whole"][m]["phase"]["after"][1] for r in R)
            nev = [r for r in R if r["n_leaves"] >= 2 and r["whole"][m]["first_split"] is None]
            nfp = sum(r["whole"][m]["pairs"][1] for r in nev)
            print(f"| r{rep} | {f_(pp(p))} | {bf:.0f} / {af:.0f} ({bf / (bf + af):.2f} before) | {len(nev)} | "
                  f"{nfp / p[1]:.2f} |" if p[1] else f"| r{rep} | {f_(pp(p))} | - | - | - |")
        print()
        for rep in (1, 2):
            R = [r for r in W if r["rep"] == rep]
            byc = defaultdict(lambda: np.zeros(5))
            for r in R:
                byc[cell(r)] += np.array(r["whole"][m]["pairs"])
            tot = sum(v[1] for v in byc.values())
            worst = sorted(byc.items(), key=lambda z: -z[1][1])[:8]
            print(f"r{rep}: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):")
            print("| cell | share | cell pair P | top leaf pairs (count) |\n|---|---|---|---|")
            for k, v in worst:
                lp = Counter()
                for r in R:
                    if cell(r) == k:
                        lp.update(r["whole"][m]["false_merge"])
                top = ", ".join(f"{a} {b:.0f}" for a, b in lp.most_common(3))
                print(f"| {k} | {f_(v[1] / tot if tot else None, 2)} | {f_(pp(v))} | {top} |")
            low = [k for k, v in byc.items() if pp(v) is not None and pp(v) < PAIR_OK]
            rest = np.sum([v for k, v in byc.items() if k not in low], axis=0)
            print(f"\nCells with their own pair P < {PAIR_OK}: {', '.join(sorted(low)) or 'none'}. Pair P with them "
                  f"{f_(pp(np.sum(list(byc.values()), axis=0)))}, without them {f_(pp(rest))} (for understanding only).\n")
        # the slow leaves behind the p90 of "seconds to first correct group"
        for rep in (2,):
            secs = []
            for r in W:
                if r["rep"] != rep:
                    continue
                s = V3[r["run"]]["methods"].get(m)
                if not s:
                    continue
                for n, (e, t) in s.get("t_ok", {}).items():
                    fs = V3[r["run"]]["first_stim"].get(n)
                    if fs is not None:
                        secs.append((t - fs, r["run"], n, r["whole"][m]["first_split"], r["n_leaves"]))
            secs.sort(reverse=True)
            k = max(1, len(secs) // 10)
            slow = secs[:k]
            print(f"r{rep}: slowest 10 % of leaves (s from first stimulus >= {slow[-1][0]:.0f} s): "
                  f"{sum(1 for x in slow if x[4] >= 2)} / {k} are in runs with 2+ leaves; cells "
                  + ", ".join(f"{a} {b}" for a, b in Counter(cell(next(z for z in W if z['run'] == x[1])) for x in slow).most_common(6))
                  + ".\n")

    # ---- 2c
    print("## 2c. Column meanings\n")
    print("- false-split share r1 / r2: share of true leaves (each run alone through the reader, events in their "
          "recorded order) with at least one accepted split; the value in brackets is the same share averaged over 20 "
          "random orders of each leaf's events (both seeds pooled), i.e. how the share behaves when the event order is "
          "exchangeable as the e-value guarantee assumes.")
    print("- first correct group s p50 / p90: per leaf, seconds from the leaf's first own stimulus (windows.json) to "
          "the first close at which some group has F1 >= F1_OK with that leaf; the p50 of 1 means half of the leaves "
          "are grouped correctly at the close of their first event (E1-0.5 closes 0.5 s after the first onset, plus "
          "the onset delay; the table rounds to whole seconds). Format in tables-v3.md: r1 p50 / p90 / r2 p50 / p90.\n")

    # ---- 2d + 2e
    print("## 2d / 2e. NPR rows and SETS reference rows, same runs and scorer, 95 % bootstrap intervals\n")
    print(f"Pair P interval: percentile bootstrap over runs within a seed ({BOOT} resamples).\n")
    print("| method | pair P r1 [95 %] | pair P r2 [95 %] | pair R r1 / r2 | leaf F1 r1 / r2 | leaf-alone false splits r1 / r2 | "
          "root split lag (2-leaf) p50 / p90 (never) | first correct group s p50 / p90 r1 ; r2 | late joiner joined / "
          "released r1 ; r2 |\n|---|---|---|---|---|---|---|---|---|")
    import step12_report as S
    rows_m = [(f"NPR-{s} a{ALPHA}", s, V3) for s in NPR_SPECS] + \
             [(f"{n} k{k}", f"{n} k{k}", V2) for n in ("SETS@E1-0.5", "SETS@E0") for k in (2, 3)]
    for meth, key, src in rows_m:
        cells = []
        for rep in (1, 2):
            R = [src[r["run"]] for r in W if r["rep"] == rep and meth in src[r["run"]].get("methods", {})]
            vecs = [x["methods"][meth]["pairs"] for x in R]
            lo, hi = boot_ci(vecs, seed=rep)
            cells.append((S.pooled(R, meth), (lo, hi), S.times(R, meth)))
        fsp = [None if key.startswith("SETS") else
               np.mean([bool(c["splits"][key]) for r in D if r["rep"] == rep for c in r["calibration"]]) for rep in (1, 2)]
        lag = [r["whole"][meth]["first_split"] - r["first_separating_event"] for r in W
               if r["n_leaves"] == 2 and r["whole"][meth]["first_split"] and r["first_separating_event"]]
        nev = sum(1 for r in W if r["n_leaves"] == 2 and not r["whole"][meth]["first_split"])
        lagt = (f"{np.median(lag):.0f} / {np.percentile(lag, 90):.0f} ({nev})" if lag else f"- ({nev})") \
            if not meth.startswith("SETS@E0") else (f"(E0 events) {np.median(lag):.0f} / {np.percentile(lag, 90):.0f} ({nev})"
                                                    if lag else f"(E0 events) - ({nev})")
        lj = []
        for rep in (1, 2):
            lk = {"NPR-B a0.05": ("B", V3), "NPR-corr a0.05": ("corr", V3), "NPR-A-m0.20-f0.05 a0.05": ("A-m0.20-f0.05", V3),
                  "NPR-A-m0.10-f0.05 a0.05": ("A-m0.10-f0.05", V3), "SETS@E1-0.5 k2": ("SETS k2", V2),
                  "SETS@E0 k2": ("SETS@E0 k2", V2)}.get(meth)
            if not lk:
                lj.append("-")
                continue
            xs = []
            for r_ in W:
                if r_["rep"] != rep:
                    continue
                lt = lk[1][r_["run"]].get("late") or {}
                xs += lt.get(lk[0], []) if isinstance(lt, dict) else [x for x in lt if x.get("method") == lk[0]]
            lj.append(f"{sum(x['joined'] for x in xs)} / {sum(x['released'] for x in xs)}")
        v = [c[0] for c in cells]
        print(f"| {meth} | {f_(v[0]['pP'])} [{f_(cells[0][1][0])}, {f_(cells[0][1][1])}] | {f_(v[1]['pP'])} "
              f"[{f_(cells[1][1][0])}, {f_(cells[1][1][1])}] | {f_(v[0]['pR'])} / {f_(v[1]['pR'])} | "
              f"{f_(v[0]['F'])} / {f_(v[1]['F'])} | {f_(fsp[0])} / {f_(fsp[1])} | {lagt} | "
              f"{' ; '.join(S.f_(c[2]['s50'], 0) + ' / ' + S.f_(c[2]['s90'], 0) for c in cells)} | {' ; '.join(lj)} |")
    print("\nSETS has no split test and no tree (it reports observed sets, which may nest inside one leaf), so a "
          "leaf-alone false-split share is not defined for it ('-'); its root split lag is the first close with two or "
          "more groups. SETS@E0 root split lag is counted in E0 events against the "
          "E1-0.5 first separating event, so it is not comparable with the other rows.\n")


def main(argv):
    if argv[:1] == ["rows"]:
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2
        cmd_rows(jobs)
    elif argv[:1] == ["report"]:
        report()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
