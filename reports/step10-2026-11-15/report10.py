#!/usr/bin/env python3
"""Step 10 tables (phase1.jsonl, model10.json, rows10.jsonl, synth10.jsonl).

    .venv/bin/python3 reports/step10-2026-11-15/report10.py > reports/step10-2026-11-15/tables.md
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binom

HERE = Path(__file__).resolve().parent
P = [json.loads(x) for x in open(HERE / "phase1.jsonl") if x.strip()]
M = json.load(open(HERE / "model10.json"))
R = [json.loads(x) for x in open(HERE / "rows10.jsonl") if x.strip()]
ERR = [r for r in R if "error" in r]
R = [r for r in R if "error" not in r]
MAIN = sorted((r for r in R if r["aqm"] != "fq_codel"), key=lambda r: r["run"])
FQ = sorted((r for r in R if r["aqm"] == "fq_codel"), key=lambda r: r["run"])
SYN = [json.loads(x) for x in open(HERE / "synth10.jsonl") if x.strip()] if (HERE / "synth10.jsonl").exists() else []
PM = [p for p in P if p["aqm"] != "fq_codel"]
DEFS = ("O1", "O2", "O3", "O4")
VARS = ("old", "new", "contain")
BLOCKS = ["C7", "C8", "C9", "C10", "C11", "C12", "C13", "M7", "M8"]
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731
blk = lambda r: r["cell"].split("-")[0]   # noqa: E731
two = lambda vals, k=2: " / ".join(f(v, k) if not isinstance(v, str) else v for v in vals)   # noqa: E731
rtt_class = lambda ms: "20" if ms <= 21 else "25" if ms <= 26 else "35" if ms <= 36 else "50+"   # noqa: E731

print("# Step 10 tables\n")
if ERR:
    print("Errors: " + "; ".join(f"{e['run']}: {e['error']}" for e in ERR) + "\n")

# ═══ A ═══
A = [(p, a) for p in PM for a in p["A"]]
CATS = ["in another event, within delta", "in another event, within delta_max", "in another event, outside delta_max",
        "already in alarm", "alarmed, no onset reached ECG", "never alarmed", "not observable"]
print("## A1-A3. Clients behind a congested egress but missing from O1 (detector onsets): why (share of the missing pairs); rep 1 / rep 2\n")


def cat_row(sel, label):
    cols = []
    for rep in (1, 2):
        xs = [a for p, a in sel if p["rep"] == rep]
        c = Counter(a["cat"] for a in xs)
        cols.append((len(xs), c, sum(a["in_alarm_event"] for a in xs)))
    print(f"| {label} | {' / '.join(str(c[0]) for c in cols)} | " +
          " | ".join(" / ".join(f(c[1][k] / c[0]) if c[0] else "-" for c in cols) for k in CATS) +
          f" | {' / '.join(f(c[2] / c[0]) if c[0] else '-' for c in cols)} |")


hdr = "| group | missing pairs | " + " | ".join(CATS) + " | in alarm during the ECG event |"
print(hdr)
print("|---|---|" + "---|" * len(CATS) + "---|")
cat_row(A, "all")
for lv in ("leaf", "mid", "up", "root", "combined"):
    cat_row([(p, a) for p, a in A if a["level"] == lv], f"level {lv}")
for aqm in ("pfifo", "codel", "pie", "mixab"):
    cat_row([(p, a) for p, a in A if p["aqm"] == aqm], f"AQM {aqm}")
for rt in ("20", "25", "35", "50+"):
    cat_row([(p, a) for p, a in A if rtt_class(a["rtt_ms"]) == rt], f"RTT {rt} ms")
for rate in sorted({a["rate"] for _, a in A if a["rate"]}):
    cat_row([(p, a) for p, a in A if a["rate"] == rate], f"rate {rate} kb/s")
print()
print("Signed offset of the missing client's nearest onset from the event (t_al - t0, ms), per category (r1+r2):\n")
print("| category | n | p10 | p50 | p90 |")
print("|---|---|---|---|---|")
for k in CATS:
    xs = [a["offset_ms"] for _, a in A if a["cat"] == k and a["offset_ms"] is not None]
    if xs:
        print(f"| {k} | {len(xs)} | {f(np.percentile(xs, 10), 0)} | {f(np.percentile(xs, 50), 0)} | {f(np.percentile(xs, 90), 0)} |")
print()
print("## A4. Single-egress events missing >= 2 clients: what the missing clients share (r1+r2)\n")
print("| level | events | missing p50 | all missing same RTT class | same rate | same branch (C9 mid) | missing onset offset p50 ms | category mix |")
print("|---|---|---|---|---|---|---|---|")
by = defaultdict(list)
for p in PM:
    for x in {a["x"] for a in p["A"]}:
        ms = [a for a in p["A"] if a["x"] == x]
        e = p["events"][x]
        if len(e["hot"]) == 1 and len(ms) >= 2:
            by[ms[0]["level"]].append(ms)
for lv, evs in sorted(by.items()):
    offs = [a["offset_ms"] for ms in evs for a in ms if a["offset_ms"] is not None]
    cm = Counter(a["cat"] for ms in evs for a in ms)
    print(f"| {lv} | {len(evs)} | {f(float(np.median([len(ms) for ms in evs])), 0)} | "
          f"{f(np.mean([len({rtt_class(a['rtt_ms']) for a in ms}) == 1 for ms in evs]))} | "
          f"{f(np.mean([len({a['rate'] for a in ms}) == 1 for ms in evs]))} | "
          f"{f(np.mean([len({a['branch'] for a in ms}) == 1 and ms[0]['branch'] is not None for ms in evs]))} | "
          f"{f(float(np.median(offs)), 0) if offs else '-'} | {'; '.join(f'{k} {v}' for k, v in cm.most_common(3))} |")
print()

# ═══ B ═══
print("## B1-B2. Observed-set definitions, single-egress events, per level and AQM (pooled reps)\n")
print("Dispersion index = sum (k - n m)^2 / sum n m (1 - m) (1 = binomial). P / R = precision / recall of the observed set against the truth set.\n")
print("| definition | level | AQM | events | miss rate | false inclusion | dispersion | >= half missing: measured / binomial | O = T | P | R |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for key in sorted(M["B"], key=lambda k: (k.split("|")[1], k.split("|")[2], k.split("|")[0])):
    dfn, lv, aqm = key.split("|")
    v = M["B"][key]
    m = v["miss"] / v["n"] if v["n"] else math.nan
    k, n = np.array(v["k"]), np.array(v["size"])
    disp = float(np.sum((k - n * m) ** 2) / np.sum(n * m * (1 - m))) if 0 < m < 1 else math.nan
    hb = float(np.mean([1 - binom.cdf(math.ceil(x / 2) - 1, x, m) for x in n])) if len(n) and m > 0 else 0.0
    print(f"| {dfn} | {lv} | {aqm} | {v['ev']} | {f(m, 3)} | {f(v['fi'] / v['nn'] if v['nn'] else math.nan, 4)} | {f(disp)} | "
          f"{f(float(np.mean(k >= n / 2)))} / {f(hb, 3)} | {f(v['eq'] / v['ev'])} | {f(float(np.nanmean(v['P'])))} | {f(float(np.nanmean(v['R'])))} |")
print()
print(f"Pooled leaf false-inclusion rate per definition (used by the 'new' matching): " +
      ", ".join(f"{d} {f(M['f'][d], 4)}" for d in DEFS) + "\n")
print("Pooled per definition and level (all AQMs):\n")
print("| definition | level | miss rate | false inclusion | O = T share |")
print("|---|---|---|---|---|")
for dfn in DEFS:
    for lv in ("leaf", "mid", "up", "root"):
        vs = [v for k, v in M["B"].items() if k.startswith(f"{dfn}|{lv}|")]
        if not vs:
            continue
        miss, n, fi, nn = (sum(v[x] for v in vs) for x in ("miss", "n", "fi", "nn"))
        print(f"| {dfn} | {lv} | {f(miss / n, 3)} | {f(fi / nn if nn else math.nan, 4)} | {f(sum(v['eq'] for v in vs) / sum(v['ev'] for v in vs))} |")
print()
print("## B3. Leaf events while another egress is congested too: what each definition's observed set is (r1+r2)\n")
print("| definition | combination | events | = the leaf | = the union of congested sets | leaf + part of the other | subset of the leaf | other |")
print("|---|---|---|---|---|---|---|---|")
for dfn in DEFS:
    tally = defaultdict(Counter)
    for p in PM:
        for e in p["events"]:
            lv = [h for h in e["hot"] if p["levels"][h] == "leaf"]
            if not lv or len(e["hot"]) < 2:
                continue
            kind = "two leaves" if all(p["levels"][h] == "leaf" for h in e["hot"]) else "leaf + upstream"
            O = set(e[dfn])
            U = set(e["T"])
            L = [set(p["fam"][h]) for h in lv]
            c = tally[kind]
            c["n"] += 1
            if any(O == l for l in L):
                c["leaf"] += 1
            elif O == U:
                c["union"] += 1
            elif any(l < O for l in L) and O <= U:
                c["leaf+"] += 1
            elif any(O < l for l in L):
                c["sub"] += 1
            else:
                c["other"] += 1
    for kind, c in tally.items():
        print(f"| {dfn} | {kind} | {c['n']} | " + " | ".join(f(c[k] / c["n"]) for k in ("leaf", "union", "leaf+", "sub", "other")) + " |")
print()

# ═══ C ═══
METH = [(f"SETS {d} {v} k{k}", d, f"{v}|{k}|None") for d in DEFS + ("truth",) for v in VARS for k in (2, 3)]


def get(r, d, key):
    if d.startswith("ecg") or d.startswith("h3"):
        return r[d]
    return r[d]["sets"][key]


def pooled(sel, d, key, fn):
    return [fn([get(r, d, key) for r in sel if r["rep"] == rep]) for rep in (1, 2)]


def lvl(level, i):
    def fn(ss):
        xs = [s["levels"][level][i] for s in ss if level in s["levels"]]
        return float(np.mean(xs)) if xs else None
    return fn


print("## C1. Leaf level (headline): best-matching group per leaf, P / R / F1 mean over closes; spurious groups per close, "
      "and with groups of mean Jaccard < 0.85 / < 0.95 dropped (FLAG); rep 1 / rep 2\n")
print("| method | leaf P | leaf R | leaf F1 | spurious / close | F1, J >= 0.85 | spurious, J >= 0.85 | F1, J >= 0.95 | spurious, J >= 0.95 |")
print("|---|---|---|---|---|---|---|---|---|")
ROWS_C = METH + [("ECG (detector onsets)", "ecg|v2-owd", None), ("h3 (detector onsets)", "h3|v2-owd", None),
                 ("ECG (truth onsets)", "ecg|truth", None), ("h3 (truth onsets)", "h3|truth", None)]
spm = lambda ss: float(np.mean([s["spur_mean"] for s in ss])) if ss else None   # noqa: E731
for name, d, key in ROWS_C:
    cells = [two(pooled(MAIN, d, key, lvl("leaf", i))) for i in range(3)] + [two(pooled(MAIN, d, key, spm))]
    if key:
        for j in ("0.85", "0.95"):
            k2 = key.replace("None", j)
            cells += [two(pooled(MAIN, d, k2, lvl("leaf", 2))), two(pooled(MAIN, d, k2, spm))]
    else:
        cells += ["", "", "", ""]
    print(f"| {name} | " + " | ".join(cells) + " |")
print()
print("Leaf F1 per block (k = 2; rep 1 / rep 2):\n")
cols = [(f"{d} {v}", d, f"{v}|2|None") for d in DEFS for v in VARS] + [("ECG", "ecg|v2-owd", None), ("h3", "h3|v2-owd", None)]
print("| block | " + " | ".join(c[0] for c in cols) + " |")
print("|---|" + "---|" * len(cols))
for b in BLOCKS:
    sel = [r for r in MAIN if blk(r) == b]
    print(f"| {b} | " + " | ".join(two(pooled(sel, d, key, lvl("leaf", 2))) for _, d, key in cols) + " |")
print()

print("## C2. Pairs from each client's smallest group, same-leaf truth (summed over closes): P / R / coverage; rep 1 / rep 2\n")
print("| method | P | R | coverage |")
print("|---|---|---|---|")


def pairs(ss):
    p = np.sum([s["pairs"] for s in ss], axis=0) if ss else np.zeros(6)
    return p


for name, d, key in ROWS_C:
    ps = [pairs([get(r, d, key) for r in MAIN if r["rep"] == rep]) for rep in (1, 2)]
    print(f"| {name} | {two([p[0] / (p[0] + p[1]) if p[0] + p[1] else None for p in ps])} | "
          f"{two([p[0] / (p[0] + p[2]) if p[0] + p[2] else None for p in ps])} | {two([p[:4].sum() / p[:5].sum() if p[:5].sum() else None for p in ps])} |")
print()

print("## C3. Robustness: leaf F1 at the closes right after an upstream (up / mid / root) event vs all other closes "
      "(mean over runs that have upstream events); rep 1 / rep 2\n")
print("| method | after upstream | other closes | difference | closes after upstream (sum) |")
print("|---|---|---|---|---|")
for name, d, key in ROWS_C:
    v = {"up": [], "other": [], "n": []}
    for rep in (1, 2):
        ss = [get(r, d, key) for r in MAIN if r["rep"] == rep and get(r, d, key)["robust_n"]["up"]]
        a = [s["robust"]["up"] for s in ss]
        b = [s["robust"]["other"] for s in ss]
        v["up"].append(float(np.nanmean(a)) if a else None)
        v["other"].append(float(np.nanmean(b)) if b else None)
        v["n"].append(str(sum(s["robust_n"]["up"] for s in ss)))
    diff = [a - b if a is not None and b is not None else None for a, b in zip(v["up"], v["other"])]
    print(f"| {name} | {two(v['up'])} | {two(v['other'])} | {two(diff)} | {' / '.join(v['n'])} |")
print()

print("## C4. Time to a leaf group with F1 >= 0.9 (FLAG): leaf events / seconds (median over leaves; never); late joiner; rep 1 / rep 2\n")
print("| method | leaf events p50 | seconds p50 | never | late joiner: joined / cases | late: events p50 | late: seconds p50 |")
print("|---|---|---|---|---|---|---|")
for name, d, key in ROWS_C:
    v = defaultdict(list)
    for rep in (1, 2):
        ev, sec, nev = [], [], 0
        lj = []
        for r in MAIN:
            if r["rep"] != rep:
                continue
            s = get(r, d, key)
            for n_, l in r["levels"].items():
                if l != "leaf" or n_ not in r["ordinary"]:
                    continue
                if n_ in s["t_ok"]:
                    ev.append(s["t_ok"][n_][0])
                    sec.append(s["t_ok"][n_][1])
                else:
                    nev += 1
            if key and not d.startswith(("ecg", "h3")):
                vv, kk = key.split("|")[:2]
                lj += [x for x in r[d]["late"] if x["variant"] == vv and str(x["k"]) == kk]
        v["ev"].append(float(np.median(ev)) if ev else None)
        v["sec"].append(float(np.median(sec)) if sec else None)
        v["nev"].append(str(nev))
        j = [x for x in lj if x["joined"]]
        v["lj"].append(f"{len(j)}/{len(lj)}" if lj else "-")
        v["lev"].append(float(np.median([x["events"] for x in j])) if j else None)
        v["ls"].append(float(np.median([x["seconds"] for x in j])) if j else None)
    print(f"| {name} | {two(v['ev'], 0)} | {two(v['sec'], 0)} | {' / '.join(v['nev'])} | {' ; '.join(v['lj'])} | {two(v['lev'], 0)} | {two(v['ls'], 0)} |")
print()

print("## C5. Order: end groups identical for reversed and three random orders (runs)\n")
for d in DEFS + ("truth",):
    print(f"- {d}: {sum(r[d]['order_identical'] for r in MAIN)} of {len(MAIN)}")
print()

print("## C6. Side table: mid / up / root, best-match F1 mean over closes; rep 1 / rep 2\n")
print("| method | mid | up | root |")
print("|---|---|---|---|")
for name, d, key in ROWS_C:
    print(f"| {name} | " + " | ".join(two(pooled(MAIN, d, key, lvl(lv, 2))) for lv in ("mid", "up", "root")) + " |")
print()

# ═══ D ═══
if SYN:
    print("## D. Model (NOT a run): truth-onset sequences of C7 / C9 / C11 pfifo, every client -> r replicas, misses and false inclusions "
          "drawn with each definition's measured rates (independent) or per-event fractions resampled (joint). Leaf F1 at the end "
          "(mean over runs) and spurious groups at the end\n")
    print("| definition | mode | r | leaf sizes | " + " | ".join(f"{v} k{k}: leaf F1 / spurious" for v in VARS for k in (2, 3)) + " |")
    print("|---|---|---|---|" + "---|" * 6)
    g = defaultdict(list)
    for s in SYN:
        g[(s["def"], s["mode"], s["r"])].append(s)
    for (dfn, mode, rr), ss in sorted(g.items()):
        sizes = sorted({x for s in ss for x in s["leaf_sizes"]})
        cells = []
        for v in VARS:
            for k in (2, 3):
                key = f"{v}|{k}"
                cells.append(f"{f(float(np.mean([s[key]['leaf_end'] for s in ss])))} / {f(float(np.mean([s[key]['spur_end'] for s in ss])), 1)}")
        print(f"| {dfn} | {mode} | {rr} | {sizes[0]}..{sizes[-1]} | " + " | ".join(cells) + " |")
    print()

# ═══ E ═══
print("## E. fq_codel cells, same-link reading (per-event constrained sets seen >= 2 times): best F1 per link set and spurious groups per close\n")
print("| run | link sets | definition | " + " | ".join(f"{v} k{k}: F1 / spurious / groups" for v in VARS for k in (2, 3)) + " |")
print("|---|---|---|" + "---|" * 6)
for r in FQ:
    for dfn in DEFS:
        s = r["fq"][dfn]
        cells = [f"{f(s[f'{v}|{k}']['link_f1'])} / {f(s[f'{v}|{k}']['spur'], 1)} / {f(s[f'{v}|{k}']['groups'], 1)}" for v in VARS for k in (2, 3)]
        print(f"| {r['run'][3:]} | {s['link_sets']} | {dfn} | " + " | ".join(cells) + " |")
print()
