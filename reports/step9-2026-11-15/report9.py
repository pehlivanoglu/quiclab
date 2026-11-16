#!/usr/bin/env python3
"""Step 9 tables from rows9.jsonl, synth9.jsonl and model9.json (step9.py).

    .venv/bin/python3 reports/step9-2026-11-15/report9.py > reports/step9-2026-11-15/tables.md
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = [json.loads(x) for x in open(HERE / "rows9.jsonl") if x.strip()]
ERR = [r for r in R if "error" in r]
R = [r for r in R if "error" not in r]
MAIN = sorted((r for r in R if r["aqm"] != "fq_codel"), key=lambda r: r["run"])
FQ = sorted((r for r in R if r["aqm"] == "fq_codel"), key=lambda r: r["run"])
MODEL = json.load(open(HERE / "model9.json"))
SYN = [json.loads(x) for x in open(HERE / "synth9.jsonl") if x.strip()] if (HERE / "synth9.jsonl").exists() else []
BLOCKS = ["C7", "C8", "C9", "C10", "C11", "C12", "C13", "M7", "M8"]
LEVELS = ["leaf", "mid", "up", "root"]
SRCS = ("v2-owd", "truth")
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731
blk = lambda r: r["cell"].split("-")[0]   # noqa: E731
METHODS = [("SETS q k2", "sets", "quantile|2|False"), ("SETS q k3", "sets", "quantile|3|False"),
           ("SETS q k4", "sets", "quantile|4|False"), ("SETS q k3 +cross", "sets", "quantile|3|True"),
           ("SETS exact k3", "sets", "exact|3|False"), ("SETS fixed-m k3", "sets", "fixed|3|False"),
           ("ECG", "ecg", None), ("h3", "h3", None)]


def summ(r, src, kind, key):
    s = r[src][kind]
    return s[key] if key else s


def two(vals, k=2):
    return " / ".join(f(v, k) if not isinstance(v, str) else v for v in vals)


print("# Step 9 tables\n")
if ERR:
    print("Errors: " + "; ".join(f"{e['run']}: {e['error']}" for e in ERR) + "\n")

# ── A ──
print("## A. SETS state and the estimated miss rate m (quantile rule), end of run\n")
print(f"Fixed-m reference (Part C item 1, pooled single-egress events): v2-owd {f(MODEL['fixed_m']['v2-owd'], 3)}, "
      f"truth {f(MODEL['fixed_m']['truth'], 3)}.\n")
print("| run | source | events | clients | distinct sets | m (iterations) | order: end groups identical (rev / 3 random) |")
print("|---|---|---|---|---|---|---|")
for r in MAIN:
    for src in SRCS:
        s = r[src]
        print(f"| {r['run'][3:]} | {src} | {s['cost']['events']} | {s['cost']['clients']} | {s['cost']['distinct_end']} | "
              f"{f(s['m']['m_end'], 3)} ({s['m']['m_iters_end']}) | {'yes' if all(s['order_identical'].values()) else 'NO ' + str(s['order_identical'])} |")
print()

# ── B1 ──
for src in SRCS:
    print(f"## B1. Best-matching group per true set: F1 (mean over closes, then over the block's runs), onset source {src}; rep 1 / rep 2\n")
    print("| block | level | " + " | ".join(m[0] for m in METHODS) + " |")
    print("|---|---|" + "---|" * len(METHODS))
    for b in BLOCKS + ["all"]:
        for lv in LEVELS:
            cols = []
            for name, kind, key in METHODS:
                v = []
                for rep in (1, 2):
                    xs = [summ(r, src, kind, key)["levels"][lv][2] for r in MAIN if r["rep"] == rep and (b == "all" or blk(r) == b)
                          and lv in summ(r, src, kind, key)["levels"]]
                    v.append(float(np.mean(xs)) if xs else None)
                cols.append(v)
            if all(x is None for c in cols for x in c):
                continue
            print(f"| {b} | {lv} | " + " | ".join(two(c) for c in cols) + " |")
    print()
    print(f"### B1 detail ({src}, all blocks): precision / recall / F1 / exactly equal, mean over closes; rep 1 / rep 2\n")
    print("| method | level | P | R | F1 | exact (reference) |")
    print("|---|---|---|---|---|---|")
    for name, kind, key in METHODS:
        for lv in LEVELS:
            vals = []
            for i in range(4):
                v = []
                for rep in (1, 2):
                    xs = [summ(r, src, kind, key)["levels"][lv][i] for r in MAIN if r["rep"] == rep and lv in summ(r, src, kind, key)["levels"]]
                    v.append(float(np.mean(xs)) if xs else None)
                vals.append(v)
            if all(x is None for c in vals for x in c):
                continue
            print(f"| {name} | {lv} | " + " | ".join(two(c) for c in vals) + " |")
    print()

# ── B2 ──
for src in SRCS:
    print(f"## B2. Spurious groups, onset source {src}: per close (mean), at the end (sum over runs), sizes, best F1 to any true set, type, life; rep 1 / rep 2\n")
    print("| block | method | per close | at end | end size p50 | end best F1 p50 | end types (r1+r2) | life p50 closes (max) |")
    print("|---|---|---|---|---|---|---|---|")
    for b in BLOCKS + ["all"]:
        for name, kind, key in METHODS:
            pc, end, sz, bf, ty, life = [], [], [], [], Counter(), []
            for rep in (1, 2):
                rs = [summ(r, src, kind, key) for r in MAIN if r["rep"] == rep and (b == "all" or blk(r) == b)]
                pc.append(float(np.mean([s["spur_mean"] for s in rs])) if rs else None)
                end.append(sum(s["end"]["spurious"] for s in rs if "end" in s))
                ss = [x for s in rs if "end" in s for x in s["end"]["spur"]]
                sz.append(float(np.median([x["size"] for x in ss])) if ss else None)
                bf.append(float(np.median([x["best_f1"] for x in ss])) if ss else None)
                for x in ss:
                    ty[x["type"].split(" (")[0]] += 1
                life += [l for s in rs for l in s["spur_lives"]]
            if b != "all" and not any(end) and not any(pc):
                continue
            print(f"| {b} | {name} | {two(pc)} | {end[0]} / {end[1]} | {two(sz, 0)} | {two(bf)} | "
                  f"{'; '.join(f'{k} {v}' for k, v in ty.most_common(4))} | {f(float(np.median(life)), 0) if life else '-'} ({max(life) if life else '-'}) |")
    print()

print("## A6 / B. Second confidence: end-of-run SETS groups by mean Jaccard to their observations; share wrong (best F1 < 0.9)\n")
print("| source | variant | Jaccard < 0.7 | 0.7-0.85 | 0.85-0.95 | >= 0.95 |")
print("|---|---|---|---|---|---|")
bins = [(0, 0.7), (0.7, 0.85), (0.85, 0.95), (0.95, 1.01)]
for src in SRCS:
    for var in ("quantile|2|False", "quantile|3|False", "quantile|4|False"):
        cells = []
        for lo, hi in bins:
            g = [x for r in MAIN for x in r[src]["detail"][var] if lo <= x["jaccard"] < hi]
            cells.append(f"{f(sum(x['best_f1'] < 0.9 for x in g) / len(g))} of {len(g)}" if g else "-")
        print(f"| {src} | {var} | " + " | ".join(cells) + " |")
print()

# ── B3 ──
print("## B3. Pairs from each client's smallest group (summed over closes): same-leaf precision / recall / coverage; shared-queue precision; rep 1 / rep 2\n")
for src in SRCS:
    print(f"### {src}\n")
    print("| block | method | P same-leaf | R same-leaf | coverage | P shared-queue | P / R at end |")
    print("|---|---|---|---|---|---|---|")
    for b in BLOCKS + ["all"]:
        for name, kind, key in METHODS:
            v = defaultdict(list)
            for rep in (1, 2):
                rs = [summ(r, src, kind, key) for r in MAIN if r["rep"] == rep and (b == "all" or blk(r) == b)]
                p = np.sum([s["pairs"] for s in rs], axis=0) if rs else np.zeros(6)
                q = np.sum([s["pairs_q"] for s in rs], axis=0) if rs else np.zeros(2)
                e = np.sum([s["end"]["pairs"] for s in rs if "end" in s], axis=0) if rs else np.zeros(6)
                v["P"].append(p[0] / (p[0] + p[1]) if p[0] + p[1] else None)
                v["R"].append(p[0] / (p[0] + p[2]) if p[0] + p[2] else None)
                v["cov"].append((p[:4].sum()) / p[:5].sum() if p[:5].sum() else None)
                v["Pq"].append(q[0] / q.sum() if q.sum() else None)
                v["end"].append(f"{f(e[0] / (e[0] + e[1]) if e[0] + e[1] else None)}/{f(e[0] / (e[0] + e[2]) if e[0] + e[2] else None)}")
            print(f"| {b} | {name} | {two(v['P'])} | {two(v['R'])} | {two(v['cov'])} | {two(v['Pq'])} | {' ; '.join(v['end'])} |")
    print()

# ── B4 ──
print("## B4. Time until a true set has a group with F1 >= 0.9 (FLAG): events of its egress / seconds, median over true sets (never); client view: events / seconds until in a group matching its leaf; rep 1 / rep 2\n")
print("| source | method | level | egress events p50 | seconds p50 | never | client: events p50 | client: seconds p50 |")
print("|---|---|---|---|---|---|---|---|")
for src in SRCS:
    for name, kind, key in METHODS:
        for lv in LEVELS:
            cols = defaultdict(list)
            for rep in (1, 2):
                ev, sec, nev, cev, csec = [], [], 0, [], []
                for r in MAIN:
                    if r["rep"] != rep:
                        continue
                    s = summ(r, src, kind, key)
                    for n, l in r[src]["levels"].items():
                        if l != lv:
                            continue
                        if n in s["t_ok"]:
                            ev.append(s["t_ok"][n][0])
                            sec.append(s["t_ok"][n][1])
                        else:
                            nev += 1
                    if lv == "leaf":
                        for c, (x, t) in s["t_client"].items():
                            cev.append(x)
                            csec.append(t)
                cols["ev"].append(float(np.median(ev)) if ev else None)
                cols["sec"].append(float(np.median(sec)) if sec else None)
                cols["nev"].append(str(nev))
                cols["cev"].append(float(np.median(cev)) if cev else None)
                cols["csec"].append(float(np.median(csec)) if csec else None)
            if all(x is None for x in cols["ev"]) and cols["nev"] == ["0", "0"]:
                continue
            print(f"| {src} | {name} | {lv} | {two(cols['ev'], 0)} | {two(cols['sec'], 0)} | {' / '.join(cols['nev'])} | "
                  f"{two(cols['cev'], 0) if lv == 'leaf' else ''} | {two(cols['csec'], 0) if lv == 'leaf' else ''} |")
print()

# ── B5 ──
print("## B5. Late joiner (one client of each leaf of >= 3 hidden until the rest has a group; SETS); rep 1 / rep 2\n")
print("| source | rule | k | cases | released | joined | events p50 | leaf events p50 | seconds p50 |")
print("|---|---|---|---|---|---|---|---|---|")
for src in SRCS:
    for rule in ("exact", "quantile"):
        for k in (2, 3, 4):
            v = defaultdict(list)
            for rep in (1, 2):
                L = [x for r in MAIN if r["rep"] == rep for x in r[src]["late"] if x["rule"] == rule and x["k"] == k]
                j = [x for x in L if x["joined"]]
                v["n"].append(str(len(L)))
                v["rel"].append(str(sum(x["released"] for x in L)))
                v["j"].append(str(len(j)))
                v["ev"].append(float(np.median([x["events"] for x in j])) if j else None)
                v["lev"].append(float(np.median([x["leaf_events"] for x in j])) if j else None)
                v["s"].append(float(np.median([x["seconds"] for x in j])) if j else None)
            print(f"| {src} | {rule} | {k} | {' / '.join(v['n'])} | {' / '.join(v['rel'])} | {' / '.join(v['j'])} | {two(v['ev'], 0)} | "
                  f"{two(v['lev'], 0)} | {two(v['s'], 0)} |")
print()

# ── B7 ──
print("## B7. Cost (SETS): distinct sets stored, bytes, pair comparisons per read (all three rules), replay seconds\n")
print("| block | clients | events p50 | distinct sets p50 (max) | bytes p50 | comparisons per read p50 | replay s p50 (all 18 variants, scoring included) |")
print("|---|---|---|---|---|---|---|")
for b in BLOCKS:
    rs = [r["v2-owd"]["cost"] for r in MAIN if blk(r) == b]
    if not rs:
        continue
    print(f"| {b} | {rs[0]['clients']} | {f(float(np.median([x['events'] for x in rs])), 0)} | {f(float(np.median([x['distinct_end'] for x in rs])), 0)} "
          f"({max(x['distinct_end'] for x in rs)}) | {f(float(np.median([x['bytes_end'] for x in rs])), 0)} | "
          f"{f(float(np.median([x['work_mean'] for x in rs])), 0)} | {f(float(np.median([x['seconds'] for x in rs])), 1)} |")
print()

# ── C ──
print("## C1. Miss and false-inclusion rates (v2-owd onsets, single-egress events), per level and AQM; dispersion of misses\n")
print("Dispersion index = sum (k - n m)^2 / sum n m (1 - m) over the events (1 = binomial). Share of events missing >= half of the "
      "clients: measured vs binomial expectation.\n")
print("| level | AQM | events | miss rate | false inclusion | dispersion index | >= half missing: measured | binomial |")
print("|---|---|---|---|---|---|---|---|")
from scipy.stats import binom  # noqa: E402
pool = defaultdict(lambda: {"k": [], "n": [], "miss": 0, "nn": 0})
for key, v in sorted(MODEL["model"].items()):
    lv, aqm = key.split("|")
    k, n = np.array(v["k_miss"]), np.array(v["size"])
    m = v["miss"]
    disp = float(np.sum((k - n * m) ** 2) / np.sum(n * m * (1 - m))) if m and 0 < m < 1 else math.nan
    half_meas = float(np.mean(k >= n / 2)) if len(k) else math.nan
    half_bin = float(np.mean([1 - binom.cdf(math.ceil(x / 2) - 1, x, m) for x in n])) if len(n) else math.nan
    print(f"| {lv} | {aqm} | {v['n_events']} | {f(m, 3)} | {f(v['fi'], 4)} | {f(disp)} | {f(half_meas)} | {f(half_bin, 3)} |")
print()

if SYN:
    print("## C2 / C3. Model replay (NOT a run): truth-onset event sequences of C7 / C9 / C11 pfifo, every client replaced by r replicas, "
          "misses and false inclusions drawn with the C1 rates (independent, or with the per-event miss fraction resampled = joint)\n")
    print("| base | r | mode | group sizes (leaf .. root) | rule k | F1 leaf end | F1 up/mid end | F1 root end | F1 leaf mean | spurious end | "
          "spurious mean | distinct sets | m estimated | read s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    by = defaultdict(list)
    for s in SYN:
        by[(s["run"].split("-")[1], s["r"], s["mode"])].append(s)
    for (bl, rr, mode), ss in sorted(by.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        sizes = sorted(set(ss[0]["group_sizes"].values()))
        for key in ("exact|2", "exact|3", "quantile|2", "quantile|3", "quantile|4"):
            xs = [s[key] for s in ss if key in s]
            if not xs:
                continue
            g = lambda lv, which: f(float(np.mean([x[which][lv] for x in xs if lv in x[which]])) if any(lv in x[which] for x in xs) else None)  # noqa: E731
            upmid = [x["f1_end"].get("up", x["f1_end"].get("mid")) for x in xs if ("up" in x["f1_end"] or "mid" in x["f1_end"])]
            print(f"| {bl} | {rr} | {mode} | {sizes[0]}..{sizes[-1]} | {key} | {g('leaf', 'f1_end')} | {f(float(np.mean(upmid))) if upmid else '-'} | "
                  f"{g('root', 'f1_end')} | {g('leaf', 'f1_mean')} | {f(float(np.mean([x['spur_end'] for x in xs])), 1)} | "
                  f"{f(float(np.mean([x['spur_mean'] for x in xs])), 1)} | {f(float(np.mean([s['distinct_end'] for s in ss])), 0)} | "
                  f"{f(float(np.mean([s['m_end'] for s in ss])), 3)} | {f(float(np.mean([s['read_seconds_mean'] for s in ss])), 2)} |")
    print()

# ── D ──
print("## D. Unions: groups (quantile rule, end of run) that are the disjoint union of two other groups; within-event split over the events whose observed set matches the union\n")
for src in SRCS:
    print(f"### {src}\n")
    print("| block | case | k | unions r1 / r2 | events | split exactly into the two parts | one class | other | removed by crossing filter |")
    print("|---|---|---|---|---|---|---|---|---|")
    agg = defaultdict(lambda: {1: Counter(), 2: Counter()})
    for r in MAIN:
        for u in r[src]["unions"]:
            a = agg[(blk(r), u["case"], u["k"])][r["rep"]]
            a["unions"] += 1
            for kk in ("n", "exact", "one class", "other", "none"):
                a[kk] += u.get(kk, 0)
            a["removed"] += u["removed_by_crossing"]
    for (b, case, k), v in sorted(agg.items()):
        n = v[1]["n"] + v[2]["n"]
        sh = lambda kk: f((v[1][kk] + v[2][kk]) / n) if n else "-"   # noqa: E731
        print(f"| {b} | {case} | {k} | {v[1]['unions']} / {v[2]['unions']} | {n} | {sh('exact')} | {sh('one class')} | {sh('other')} | "
              f"{v[1]['removed']} / {v[2]['removed']} |")
    print()

# ── E ──
print("## E. fq_codel cells: groups SETS reports (all clients are behind per-flow-queue egresses)\n")
print("Same-queue reading: every group is false. Same-link reading: true sets = distinct per-event constrained sets (own sub-queue, "
      "Step 8 rule) seen in >= 2 events (M); best F1 per such set, mean over closes; spurious = groups that are no such set's best match.\n")
print("| run | source | link sets | rule k | groups per close | link F1 mean | link spurious per close | groups at end: members (support, best link F1) |")
print("|---|---|---|---|---|---|---|---|")
for r in FQ:
    for src in SRCS:
        s = r[src]
        for key in ("exact|3", "quantile|2", "quantile|3", "quantile|4"):
            p = s["per"][key]
            end = "; ".join(f"{{{','.join(g['members'])}}} ({g['support']}, {g['best_link_f1']})" for g in s["end"][key][:6])
            print(f"| {r['run'][3:]} | {src} | {len(s['link_sets'])} | {key} | {f(p['groups_mean'])} | {f(p['link_f1_mean'])} | "
                  f"{f(p['link_spur_mean'])} | {end or 'none'} |")
print()
