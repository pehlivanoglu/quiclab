#!/usr/bin/env python3
"""Step 8 tables from rows.jsonl (step8.py rows).

    .venv/bin/python3 reports/step8-2026-11-15/report.py > reports/step8-2026-11-15/tables.md

Event type from the congested egresses: none / leaf / mid / up / root (one egress) / nested (the union is one of
them, e.g. a+up) / disjoint (pairwise disjoint, e.g. a+b, A+C) / other. Sets of one client are not counted in
C (M). Orders in C6: reversed and three random permutations (seed crc32(run|i)) with the recorded time slots.
"""

from __future__ import annotations

import json
import math
import random
import zlib
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = [json.loads(x) for x in open(HERE / "rows.jsonl") if x.strip()]
ERR = [r for r in R if "error" in r]
R = [r for r in R if "error" not in r]
BLOCKS = ["C7", "C8", "C9", "C10", "C11", "C13", "M7"]
SRCS = ("v2-owd", "truth")
VERS = ("raw", "split", "pooled")
KS = (2, 3, 4)
LEVEL_ORDER = ["leaf", "mid", "up", "root", "nested", "disjoint", "other", "none"]
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731
blk = lambda r: r["cell"].split("-")[0]   # noqa: E731
NONFQ = [r for r in R if r["aqm"] != "fq_codel"]
FQ = [r for r in R if r["aqm"] == "fq_codel"]


def fam(r):
    return {n: frozenset(v) for n, v in r["fam"].items()}


def etype(r, hot):
    F = fam(r)
    if not hot:
        return "none"
    if len(hot) == 1:
        return r["levels"][hot[0]]
    u = frozenset().union(*[F[n] for n in hot])
    if any(F[n] == u for n in hot):
        return "nested"
    if all(not (F[a] & F[b]) for a, b in combinations(hot, 2)):
        return "disjoint"
    return "other"


def tset(r, hot):
    F = fam(r)
    return frozenset().union(*[F[n] for n in hot]) if hot else frozenset()


def name_of(r, S):
    for n, v in fam(r).items():
        if v == S:
            return n
    return None


def label(r, S):
    n = name_of(r, S)
    return f"**{n}**" if n else "{" + ",".join(sorted(S)) + "}"


def occurrences(r, src, ver, order=None):
    """[(event index in the given order, t0 slot, set)]"""
    ev = r[src]["events"]
    idx = order if order is not None else list(range(len(ev)))
    t_slots = [e["t0"] for e in ev]
    out = []
    for k, i in enumerate(idx):
        e = ev[i]
        sets = set()
        raw = frozenset(e["obs"]) if len(e["obs"]) >= 2 else None
        spl = [frozenset(c) for c in (e["classes"] or []) if len(c) >= 2]
        if ver == "raw" and raw:
            sets = {raw}
        elif ver == "split":
            sets = set(spl)
        elif ver == "pooled":
            sets = set(spl) | ({raw} if raw else set())
        for S in sets:
            out.append((k, t_slots[k], S))
    return out


def two(vals, k=2):
    return " / ".join("-" if v is None else (f(v, k) if isinstance(v, float) else str(v)) for v in vals)


print("# Step 8 tables\n")
if ERR:
    print("Errors: " + "; ".join(f"{e['run']}: {e['error']}" for e in ERR) + "\n")
print("Runs: " + ", ".join(f"{r['run'][3:]} ({r['queue_truth']})" for r in sorted(R, key=lambda r: r["run"]) if r["queue_truth"] != "qlog")
      + " use GT1 for the congested egresses (GT-Q invalid); all others the queue log.\n")

# ═══ A ═══
print("## A1. Observed set against the truth set, per event type (pfifo / codel / pie pooled per block); rep 1 / rep 2\n")
for src in SRCS:
    print(f"### onset source {src}\n")
    print("| block | event type | events | equal | strict subset (missing p50) | strict superset (extra p50) | other |")
    print("|---|---|---|---|---|---|---|")
    for b in BLOCKS + ["all"]:
        for t in LEVEL_ORDER:
            cols = []
            for rep in (1, 2):
                c, miss, extra = Counter(), [], []
                for r in NONFQ:
                    if r["rep"] != rep or (b != "all" and blk(r) != b):
                        continue
                    for e in r[src]["events"]:
                        if etype(r, e["hot"]) != t:
                            continue
                        O, T = frozenset(e["obs"]), tset(r, e["hot"])
                        if t == "none":
                            c["none"] += 1
                            continue
                        if O == T:
                            c["eq"] += 1
                        elif O < T:
                            c["sub"] += 1
                            miss.append(len(T - O))
                        elif O > T:
                            c["sup"] += 1
                            extra.append(len(O - T))
                        else:
                            c["oth"] += 1
                cols.append((c, miss, extra))
            n = [sum(c.values()) for c, _, _ in cols]
            if not any(n):
                continue
            sh = lambda key: " / ".join(f(c[key] / max(1, sum(c.values()))) for c, _, _ in cols)   # noqa: E731
            if t == "none":
                print(f"| {b} | none (no egress congested) | {two(n)} | - | - | - | - |")
                continue
            mi = " / ".join(f(float(np.median(m)), 0) if m else "-" for _, m, _ in cols)
            ex = " / ".join(f(float(np.median(x)), 0) if x else "-" for _, _, x in cols)
            print(f"| {b} | {t} | {two(n)} | {sh('eq')} | {sh('sub')} ({mi}) | {sh('sup')} ({ex}) | {sh('oth')} |")
    print()

print("## A2. Single-egress events: size of the difference |observed Δ truth| (share of events); rep 1 / rep 2\n")
print("| source | level | events | 0 | 1 | 2 | 3 | >= 4 |")
print("|---|---|---|---|---|---|---|---|")
for src in SRCS:
    for lv in ("leaf", "mid", "up", "root"):
        cols = []
        for rep in (1, 2):
            c = Counter()
            for r in NONFQ:
                if r["rep"] != rep:
                    continue
                for e in r[src]["events"]:
                    if etype(r, e["hot"]) == lv:
                        c[min(4, len(frozenset(e["obs"]) ^ tset(r, e["hot"])))] += 1
            cols.append(c)
        if not any(sum(c.values()) for c in cols):
            continue
        print(f"| {src} | {lv} | {two([sum(c.values()) for c in cols])} | " +
              " | ".join(" / ".join(f(c[k] / max(1, sum(c.values()))) for c in cols) for k in range(5)) + " |")
print()

print("## A3. Combined events: which union of the congested egresses' true sets the observed set equals (counts r1 / r2)\n")
for src in SRCS:
    print(f"### {src}\n")
    print("| block | type | observed set = | events r1 / r2 |")
    print("|---|---|---|---|")
    for b in BLOCKS:
        tally = defaultdict(lambda: [0, 0])
        for r in NONFQ:
            if blk(r) != b:
                continue
            F = fam(r)
            for e in r[src]["events"]:
                t = etype(r, e["hot"])
                if t not in ("nested", "disjoint", "other"):
                    continue
                O = frozenset(e["obs"])
                hit = None
                for k in range(len(e["hot"]), 0, -1):
                    for sub in combinations(e["hot"], k):
                        if frozenset().union(*[F[n] for n in sub]) == O:
                            hit = "+".join(sub)
                            break
                    if hit:
                        break
                if not hit:
                    big = frozenset().union(*[F[n] for n in e["hot"]])
                    inside = [n for n in e["hot"] if O <= F[n]]
                    hit = ("subset of " + "/".join(inside) if inside else ("subset of the union" if O <= big else "not inside the union")) + \
                          f" ({len(O)} clients)" if O else "empty"
                    hit = "no union: " + hit
                tally[(t, "+".join(e["hot"]), hit)][r["rep"] - 1] += 1
        for (t, hot, hit), v in sorted(tally.items(), key=lambda x: (x[0][0], x[0][1], -sum(x[1]))):
            print(f"| {b} | {t} {hot} | {hit} | {v[0]} / {v[1]} |")
    print()

# ═══ B ═══
print("## B. Within-event split (partition_fixed on the observed clients' curves; class 0 dropped)\n")
for src in SRCS:
    print(f"### {src}\n")
    print("| block | event type | events with >= 2 observed | split into the true sets exactly | true sets ∩ observed exactly | "
          "one class = observed | false split (>= 2 classes) | no data class | most common outcomes (r1+r2) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for b in BLOCKS + ["all"]:
        for t in ("leaf", "mid", "up", "root", "disjoint", "nested"):
            cols, pat = [], Counter()
            for rep in (1, 2):
                c = Counter()
                for r in NONFQ:
                    if r["rep"] != rep or (b != "all" and blk(r) != b):
                        continue
                    F = fam(r)
                    for e in r[src]["events"]:
                        if etype(r, e["hot"]) != t or e["classes"] is None:
                            continue
                        O = frozenset(e["obs"])
                        C = {frozenset(x) for x in e["classes"]}
                        want = {F[n] for n in e["hot"]}
                        if t == "nested":
                            want = {F[n] for n in e["hot"]}
                        c["n"] += 1
                        c["exact"] += C == want
                        c["exact_obs"] += C == {w & O for w in want if w & O}
                        c["one"] += C == {O - frozenset()} and len(C) == 1 and next(iter(C)) == O
                        c["many"] += len(C) >= 2
                        c["none"] += not C
                        pat[" | ".join(sorted(label(r, x) if name_of(r, x) else f"{{{len(x)}}}" for x in C)) or "no class"] += 1
                cols.append(c)
            if not any(c["n"] for c in cols):
                continue
            sh = lambda k: " / ".join(f(c[k] / c["n"]) if c["n"] else "-" for c in cols)   # noqa: E731
            if t in ("leaf", "mid", "up", "root"):
                ex = sh("exact")
            else:
                ex = sh("exact")
            top = "; ".join(f"{p} ({n})" for p, n in pat.most_common(3))
            print(f"| {b} | {t} | {two([c['n'] for c in cols])} | {ex} | {sh('exact_obs')} | {sh('one')} | {sh('many')} | {sh('none')} | {top} |")
    print()

# ═══ C ═══
print("## C1. Ten most frequent sets per run (end of run; **name** = a true set; {members} = spurious); C2 counts\n")
summary = defaultdict(list)    # (src, ver) -> per-run dict
for src in SRCS:
    for ver in VERS:
        print(f"### {src}, {ver}\n")
        print("| run | true sets seen / all | ranks of true sets (count) | top ten | true >= 2 / >= 3 / >= 4 | spurious >= 2 / >= 3 / >= 4 |")
        print("|---|---|---|---|---|---|")
        for r in sorted(NONFQ, key=lambda r: (BLOCKS.index(blk(r)), r["run"])):
            occ = occurrences(r, src, ver)
            cnt = Counter(S for _, _, S in occ)
            F = fam(r)
            trues = {v: n for n, v in F.items() if len(v) >= 2}
            ranked = sorted(cnt.items(), key=lambda x: -x[1])
            rank = lambda S: 1 + sum(1 for _, c in ranked if c > cnt[S])   # noqa: E731
            rk = ", ".join(f"{n} {rank(S)} ({cnt[S]})" if cnt[S] else f"{n} - (0)" for S, n in trues.items())
            top = ", ".join(f"{label(r, S)} {c}" for S, c in ranked[:10])
            tk = [sum(cnt[S] >= k for S in trues) for k in KS]
            sk = [sum(1 for S, c in cnt.items() if S not in trues and c >= k) for k in KS]
            summary[(src, ver)].append({"run": r, "tk": tk, "sk": sk, "n_true": len(trues), "seen": sum(cnt[S] > 0 for S in trues)})
            print(f"| {r['run'][3:]} | {sum(cnt[S] > 0 for S in trues)} / {len(trues)} | {rk} | {top} | {' / '.join(map(str, tk))} | "
                  f"{' / '.join(map(str, sk))} |")
        print()

print("## C2. Separation by count k, per block (sum over the block's runs): true sets reaching k of all true sets; spurious sets reaching k; rep 1 / rep 2\n")
for src in SRCS:
    print(f"### {src}\n")
    print("| block | version | true >= 2 | true >= 3 | true >= 4 | spurious >= 2 | spurious >= 3 | spurious >= 4 |")
    print("|---|---|---|---|---|---|---|---|")
    for b in BLOCKS + ["all"]:
        for ver in VERS:
            rows = [x for x in summary[(src, ver)] if b == "all" or blk(x["run"]) == b]
            cells = []
            for i in range(3):
                cells.append(" / ".join(f"{sum(x['tk'][i] for x in rows if x['run']['rep'] == rep)} of "
                                        f"{sum(x['n_true'] for x in rows if x['run']['rep'] == rep)}" for rep in (1, 2)))
            for i in range(3):
                cells.append(" / ".join(str(sum(x["sk"][i] for x in rows if x["run"]["rep"] == rep)) for rep in (1, 2)))
            print(f"| {b} | {ver} | " + " | ".join(cells) + " |")
    print()


def reach(r, src, ver, order=None):
    """per true set name: {k: (events, seconds)} at which its count first reaches k (None if never)."""
    occ = occurrences(r, src, ver, order)
    F = fam(r)
    out = {}
    for n, S in F.items():
        if len(S) < 2:
            continue
        ks, c = {}, 0
        for k_, t, X in occ:
            if X == S:
                c += 1
                if c in KS and c not in ks:
                    ks[c] = (k_ + 1, t)
        out[n] = {k: ks.get(k) for k in KS}
    return out


print("## C3. Time until each true set has been seen k times (median over runs; never = count of true sets that do not reach k); rep 1 / rep 2\n")
print("| source | version | level | k | events p50 | seconds p50 | never |")
print("|---|---|---|---|---|---|---|")
for src in SRCS:
    for ver in VERS:
        for lv in ("leaf", "mid", "up", "root"):
            for k in KS:
                cols = []
                for rep in (1, 2):
                    ev, sec, nev = [], [], 0
                    for r in NONFQ:
                        if r["rep"] != rep:
                            continue
                        for n, v in reach(r, src, ver).items():
                            if r["levels"][n] != lv:
                                continue
                            if v[k]:
                                ev.append(v[k][0])
                                sec.append(v[k][1])
                            else:
                                nev += 1
                    cols.append((ev, sec, nev))
                if not any(c[0] or c[2] for c in cols):
                    continue
                print(f"| {src} | {ver} | {lv} | {k} | " + " / ".join(f(float(np.median(c[0])), 0) if c[0] else "-" for c in cols) + " | "
                      + " / ".join(f(float(np.median(c[1])), 0) if c[1] else "-" for c in cols) + " | " + " / ".join(str(c[2]) for c in cols) + " |")
print()

print("## C4. Tolerance: a set counts an occurrence that differs from it by at most one client (FLAG)\n")
print("Sum over runs: true sets reaching k (exact → tolerant) and spurious distinct sets reaching k (exact → tolerant); raw version. Rep 1 / rep 2.\n")
print("| source | block | k | true exact → tolerant | spurious exact → tolerant |")
print("|---|---|---|---|---|")
for src in SRCS:
    for b in BLOCKS + ["all"]:
        for k in KS:
            cols = []
            for rep in (1, 2):
                te = tt = se = s_t = nt = 0
                for r in NONFQ:
                    if r["rep"] != rep or (b != "all" and blk(r) != b):
                        continue
                    occ = [S for _, _, S in occurrences(r, src, "raw")]
                    cnt = Counter(occ)
                    trues = {v for v in fam(r).values() if len(v) >= 2}
                    nt += len(trues)
                    tol = lambda S: sum(len(S ^ O) <= 1 for O in occ)   # noqa: E731
                    te += sum(cnt[S] >= k for S in trues)
                    tt += sum(tol(S) >= k for S in trues)
                    sp = [S for S in cnt if S not in trues]
                    se += sum(cnt[S] >= k for S in sp)
                    # tolerant spurious: distinct non-true sets that reach k and are not within 1 of a true set
                    s_t += sum(tol(S) >= k for S in sp if not any(len(S ^ T) <= 1 for T in trues))
                cols.append((te, tt, se, s_t, nt))
            print(f"| {src} | {b} | {k} | " + " / ".join(f"{c[0]} → {c[1]} of {c[4]}" for c in cols) + " | "
                  + " / ".join(f"{c[2]} → {c[3]}" for c in cols) + " |")
print()
print("Tolerant spurious = distinct non-true sets reaching k that are not themselves within one client of a true set "
      "(sets within one client of a true set are counted toward that true set).\n")

print("## C5. Are the recurring sets nested? Pairs of recurring sets (exact count >= k) that overlap without containment\n")
print("| source | version | k | recurring sets (sum over runs) r1 / r2 | crossing pairs r1 / r2 | crossing pairs involving a true set r1 / r2 | runs laminar r1 / r2 |")
print("|---|---|---|---|---|---|---|")
for src in SRCS:
    for ver in VERS:
        for k in KS:
            cols = []
            for rep in (1, 2):
                n = cr = crt = lam = runs = 0
                for r in NONFQ:
                    if r["rep"] != rep:
                        continue
                    cnt = Counter(S for _, _, S in occurrences(r, src, ver))
                    rec = [S for S, c in cnt.items() if c >= k]
                    trues = set(fam(r).values())
                    n += len(rec)
                    x = [(A, B) for A, B in combinations(rec, 2) if A & B and not (A <= B or B <= A)]
                    cr += len(x)
                    crt += sum(A in trues or B in trues for A, B in x)
                    lam += not x
                    runs += 1
                cols.append((n, cr, crt, f"{lam} of {runs}"))
            print(f"| {src} | {ver} | {k} | " + " | ".join(" / ".join(str(c[i]) for c in cols) for i in range(4)) + " |")
print()

print("## C6. Order: recorded, reversed and three random orders (same events; time slots kept). End counts identical in every run?"
      " Median events until a true set is seen twice, per level\n")
print("| source | version | end counts identical (runs) | level | recorded | reversed | random 1 | random 2 | random 3 |")
print("|---|---|---|---|---|---|---|---|---|")
for src in SRCS:
    for ver in VERS:
        same = 0
        per = defaultdict(lambda: defaultdict(list))
        for r in NONFQ:
            n = len(r[src]["events"])
            orders = {"recorded": list(range(n)), "reversed": list(range(n))[::-1]}
            for i in range(3):
                o = list(range(n))
                random.Random(zlib.crc32(f"{r['run']}|{src}|{i}".encode())).shuffle(o)
                orders[f"random {i + 1}"] = o
            ends = [Counter(S for _, _, S in occurrences(r, src, ver, o)) for o in orders.values()]
            same += all(e == ends[0] for e in ends)
            for name, o in orders.items():
                for nm, v in reach(r, src, ver, o).items():
                    if v[2]:
                        per[r["levels"][nm]][name].append(v[2][0])
        first = True
        for lv in ("leaf", "mid", "up", "root"):
            if lv not in per:
                continue
            print(f"| {src} | {ver} | {f'{same} of {len(NONFQ)}' if first else ''} | {lv} | " +
                  " | ".join(f(float(np.median(per[lv][o])), 0) + f" ({len(per[lv][o])})" if per[lv][o] else "-"
                             for o in ("recorded", "reversed", "random 1", "random 2", "random 3")) + " |")
            first = False
print()

# ═══ D ═══
print("## D. Share of event closes at which a group equals each true set exactly (mean over the run's closes), per level; rep 1 / rep 2\n")
print("ECG: groups with L >= A after each ECG event; h3: replay4 groups after each event; recurring k: the sets seen >= k times so far "
      "(exact) after each ECG event.\n")
for src in SRCS:
    print(f"### {src}\n")
    print("| block | level | ECG | h3 | rec raw k2 | rec raw k3 | rec raw k4 | rec split k2 | rec pooled k2 | rec pooled k3 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for b in BLOCKS + ["all"]:
        for lv in ("leaf", "mid", "up", "root"):
            vals = defaultdict(lambda: {1: [], 2: []})
            for r in NONFQ:
                if b != "all" and blk(r) != b:
                    continue
                trues = [(n, S) for n, S in fam(r).items() if r["levels"][n] == lv and len(S) >= 2]
                if not trues:
                    continue
                ev = r[src]["events"]
                share = lambda groups: np.mean([any(frozenset(g) == S for g in groups) for _, S in trues])   # noqa: E731
                vals["ECG"][r["rep"]].append(float(np.mean([share(e["groups"]) for e in ev])) if ev else math.nan)
                h3 = r[src]["h3"]
                vals["h3"][r["rep"]].append(float(np.mean([share(e["groups"]) for e in h3])) if h3 else math.nan)
                for ver, k, key in (("raw", 2, "rr2"), ("raw", 3, "rr3"), ("raw", 4, "rr4"), ("split", 2, "rs2"),
                                    ("pooled", 2, "rp2"), ("pooled", 3, "rp3")):
                    occ = occurrences(r, src, ver)
                    c, sh, j = Counter(), [], 0
                    for x in range(len(ev)):
                        while j < len(occ) and occ[j][0] <= x:
                            c[occ[j][2]] += 1
                            j += 1
                        sh.append(np.mean([c[S] >= k for _, S in trues]))
                    vals[key][r["rep"]].append(float(np.mean(sh)) if sh else math.nan)
            if not vals:
                continue
            g = lambda key: " / ".join(f(float(np.nanmean(vals[key][rep]))) if vals[key][rep] else "-" for rep in (1, 2))   # noqa: E731
            print(f"| {b} | {lv} | {g('ECG')} | {g('h3')} | {g('rr2')} | {g('rr3')} | {g('rr4')} | {g('rs2')} | {g('rp2')} | {g('rp3')} |")
    print()

print("Part E: see fq-control.md (fq_control.py; decision 2026-11-15: per-flow-queue egresses are a negative control).")
