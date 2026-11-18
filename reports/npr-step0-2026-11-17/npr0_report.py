"""NPR STEP 0 tables from rows.jsonl (npr0.py). Single-queue cells and per-flow-queue cells (fq_codel / cake) apart;
reps side by side where they are compared."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binom

FQ = ("fq_codel", "cake")
MID = (0.25, 0.75)          # (P) the note's band
BINS = np.linspace(0, 1, 11)


def f_(x, d=2):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def cls(r):
    return "fq" if r["aqm"] in FQ else "single"


def leaf_views(r):
    """Per leaf: members, ancestors (truth sets strictly containing it), parent key (sorted ancestor names)."""
    T = {n: set(v["members"]) for n, v in r["truth"].items()}
    out = {}
    for n, v in r["truth"].items():
        if v["level"] != "leaf":
            continue
        anc = sorted(a for a, s in T.items() if a != n and T[n] < s)
        out[n] = {"members": sorted(T[n]), "anc": anc}
    return out


def per_event(r):
    """Yield (leaf, info, event index, on, kind, k, n, x dict) for every leaf and event."""
    L = leaf_views(r)
    for i, e in enumerate(r["events"]):
        H = set(e["hot"])
        ones = set(e["ones"])
        for n, info in L.items():
            on_leaf = n in H
            anc_hot = any(a in H for a in info["anc"])
            on = on_leaf or anc_hot
            if on_leaf:
                kind = "only this leaf" if H == {n} else "this leaf and others"
            elif anc_hot:
                kind = "only upstream"
            else:
                kind = "no congested egress"
            x = {c: 1 if c in ones else ("NA:" + e["na"][c] if c in e["na"] else 0) for c in info["members"]}
            nn = sum(1 for v in x.values() if v in (0, 1))
            k = sum(1 for v in x.values() if v == 1)
            yield n, info, i, on, kind, k, nn, x


def load(path):
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    return [r for r in R if "error" not in r], [r for r in R if "error" in r]


def sec01(R):
    print("## 0.1 Within-leaf agreement (events where at least one member has x = 1)\n")
    print("k / n = members with 1 over members not NA. Share of events with k / n in [0.25, 0.75] and with k = n; "
          "histogram in tenths (0-0.1 ... 0.9-1.0, where 1.0 falls in the last bin).\n")
    for c in ("single", "fq"):
        print(f"### {c}-queue cells\n" if c == "single" else "### fq_codel / cake cells\n")
        print("| leaf size | event type | events | k/n in [0.25, 0.75] | k = n | k/n p10 / p50 | histogram (tenths) |")
        print("|---|---|---|---|---|---|---|")
        g = defaultdict(list)
        for r in R:
            if cls(r) != c:
                continue
            for n, info, i, on, kind, k, nn, x in per_event(r):
                if k >= 1 and nn:
                    g[(len(info["members"]), kind)].append(k / nn)
                    g[(len(info["members"]), "all")].append(k / nn)
        for key in sorted(g, key=lambda z: (z[0], z[1] != "all", z[1])):
            v = np.array(g[key])
            h = np.histogram(v, BINS)[0]
            print(f"| {key[0]} | {key[1]} | {len(v)} | {np.mean((v >= MID[0]) & (v <= MID[1])):.3f} | "
                  f"{np.mean(v == 1):.3f} | {np.percentile(v, 10):.2f} / {np.median(v):.2f} | "
                  f"{' '.join(str(int(x)) for x in h)} |")
        print()


def rates(rows):
    """m and f per (class, leaf size): m = misses / non-NA members of on leaves; f = ones / non-NA of off leaves."""
    acc = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        for n, info, i, on, kind, k, nn, x in per_event(r):
            a = acc[(cls(r), len(info["members"]))]
            if on:
                a[0] += nn - k
                a[1] += nn
            else:
                a[2] += k
                a[3] += nn
    return {key: (a[0] / a[1] if a[1] else np.nan, a[2] / a[3] if a[3] else np.nan) for key, a in acc.items()}


def sec02(R):
    print("## 0.2 Majority-vote error by group size\n")
    print("On: the leaf is truly on and fewer than half of its non-NA members have 1. Off: truly off and at least half "
          "have 1. Every event of the run counts (events with n = 0 skipped). Prediction: independent members with "
          "the measured m (on) and f (off) of the same class and size, at each event's n. Reps side by side.\n")
    reps = sorted({r["rep"] for r in R})
    for c in ("single", "fq"):
        print(f"### {'single-queue' if c == 'single' else 'fq_codel / cake'} cells\n")
        print("| leaf size | rep | on events | on error | predicted | m | off events | off error | predicted | f |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for rep in reps:
            rows = [r for r in R if r["rep"] == rep and cls(r) == c]
            mf = rates(rows)
            g = defaultdict(lambda: {"on": [], "off": [], "pon": [], "poff": []})
            for r in rows:
                for n, info, i, on, kind, k, nn, x in per_event(r):
                    if nn == 0:
                        continue
                    s = len(info["members"])
                    m, f = mf[(c, s)]
                    if on:
                        g[s]["on"].append(k < nn / 2)
                        g[s]["pon"].append(binom.cdf(np.ceil(nn / 2) - 1, nn, 1 - m))
                    else:
                        g[s]["off"].append(k >= nn / 2)
                        g[s]["poff"].append(binom.sf(np.ceil(nn / 2) - 1, nn, f))
            for s in sorted(g):
                v = g[s]
                m, f = mf[(c, s)]
                mean = lambda a: float(np.mean(a)) if a else None   # noqa: E731
                print(f"| {s} | r{rep} | {len(v['on'])} | {f_(mean(v['on']), 3)} | {f_(mean(v['pon']), 3)} | {f_(m, 3)} | "
                      f"{len(v['off'])} | {f_(mean(v['off']), 3)} | {f_(mean(v['poff']), 4)} | {f_(f, 4)} |")
        print()


def sec03(R):
    print("## 0.3 Burstiness of misses (truly on events, n >= 2)\n")
    print("Per leaf p = its pooled hit rate; variance ratio = sum (k - n p)^2 / sum n p (1 - p) (1 = binomial); "
          "rho = (sum (k - n p)^2 - sum n p (1 - p)) / sum n (n - 1) p (1 - p) (method of moments, beta-binomial), "
          "pooled over the leaves of the cell. Reps side by side.\n")
    reps = sorted({r["rep"] for r in R})
    print("| AQM | leaf size | " + " | ".join(f"r{x}: events, var ratio, rho" for x in reps) + " |")
    print("|---|---|" + "---|" * len(reps))
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0.0, 0.0]))
    for r in R:
        per_leaf = defaultdict(list)
        for n, info, i, on, kind, k, nn, x in per_event(r):
            if on and nn >= 2:
                per_leaf[n].append((k, nn, len(info["members"])))
        for n, ev in per_leaf.items():
            K, N = sum(e[0] for e in ev), sum(e[1] for e in ev)
            p = K / N
            if p in (0.0, 1.0):
                num, den, d2 = sum((e[0] - e[1] * p) ** 2 for e in ev), 0.0, 0.0
            else:
                num = sum((e[0] - e[1] * p) ** 2 for e in ev)
                den = sum(e[1] * p * (1 - p) for e in ev)
                d2 = sum(e[1] * (e[1] - 1) * p * (1 - p) for e in ev)
            a = acc[(r["aqm"], ev[0][2])][r["rep"]]
            a[0] += len(ev)
            a[1] += num
            a[2] += den
            a[3] += d2
    for key in sorted(acc):
        cells = []
        for rep in reps:
            a = acc[key].get(rep)
            if not a or not a[0]:
                cells.append("-")
                continue
            vr = a[1] / a[2] if a[2] else None
            rho = (a[1] - a[2]) / a[3] if a[3] else None
            cells.append(f"{a[0]}, {f_(vr)}, {f_(rho)}")
        print(f"| {key[0]} | {key[1]} | " + " | ".join(cells) + " |")
    print()


def sec04(R):
    print("## 0.4 NA accounting: members of truly on leaves that SETS counts as missed (x != 1)\n")
    print("Events where the leaf is on and at least one member has 1 (the events SETS learns from), and all on events.\n")
    print("| cells | events | members not 1 | NA: in-alarm | NA: no-ack | NA: absent | true 0 |")
    print("|---|---|---|---|---|---|---|")
    for c in ("single", "fq"):
        for sel in ("k >= 1", "all on"):
            cnt = Counter()
            ev = 0
            for r in R:
                if cls(r) != c:
                    continue
                for n, info, i, on, kind, k, nn, x in per_event(r):
                    if not on or (sel == "k >= 1" and k == 0):
                        continue
                    ev += 1
                    for v in x.values():
                        if v != 1:
                            cnt[v] += 1
            tot = sum(cnt.values())
            sh = lambda key: f"{cnt[key]} ({cnt[key] / tot:.2f})" if tot else "-"   # noqa: E731
            print(f"| {c}, {sel} | {ev} | {tot} | {sh('NA:in-alarm')} | {sh('NA:no-ack')} | {sh('NA:absent')} | {sh(0)} |")
    print()


def sec05(R):
    print("## 0.5 Separation of sibling leaves\n")
    print("Sibling leaves = leaves with the same set of ancestors (same parent). Per pair: share of the events with at "
          "least one of the two on in which exactly one is on (truth; an on ancestor makes both on).\n")
    print("| scenario type | cells | pairs | events with >= 1 on | exactly one on | per-pair p10 / p50 |")
    print("|---|---|---|---|---|---|")
    g = defaultdict(lambda: [0, 0, 0, []])
    for r in R:
        L = leaf_views(r)
        names = sorted(L)
        pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if L[a]["anc"] == L[b]["anc"]]
        if not pairs:
            continue
        ons = defaultdict(dict)
        for n, info, i, on, kind, k, nn, x in per_event(r):
            ons[i][n] = on
        for a, b in pairs:
            tot = one = 0
            for i in ons:
                if ons[i][a] or ons[i][b]:
                    tot += 1
                    one += ons[i][a] != ons[i][b]
            key = (r["type"], cls(r))
            g[key][0] += 1
            g[key][1] += tot
            g[key][2] += one
            if tot:
                g[key][3].append(one / tot)
    for key in sorted(g):
        p, t, o, sh = g[key]
        q = f"{np.percentile(sh, 10):.2f} / {np.median(sh):.2f}" if sh else "-"
        print(f"| {key[0]} | {key[1]} | {p} | {t} | {f_(o / t if t else None)} | {q} |")
    print()


def _ac(v, lag):
    v = np.asarray(v, dtype=float)
    if len(v) <= lag + 2 or np.var(v) == 0:
        return None
    a, b = v[:-lag] - v.mean(), v[lag:] - v.mean()
    return float(np.sum(a * b) / np.sum((v - v.mean()) ** 2))


def sec06(R):
    print("## 0.6 Dependence between events\n")
    print("Per leaf, over the run's events in time order: lag-1 / lag-2 autocorrelation of on (1) / off (0), and of the "
          "miss count (non-NA members with 0) over the leaf's on events. Mean over leaves with a defined value "
          "(non-constant sequence, > lag + 2 values). Reps side by side.\n")
    reps = sorted({r["rep"] for r in R})
    print("| cells | leaf size | " + " | ".join(f"r{x}: leaves, on/off lag1 / lag2, misses lag1 / lag2" for x in reps) + " |")
    print("|---|---|" + "---|" * len(reps))
    acc = defaultdict(lambda: defaultdict(lambda: [[], [], [], []]))
    for r in R:
        seq = defaultdict(list)
        miss = defaultdict(list)
        size = {}
        for n, info, i, on, kind, k, nn, x in per_event(r):
            seq[n].append(int(on))
            size[n] = len(info["members"])
            if on:
                miss[n].append(nn - k)
        for n in seq:
            a = acc[(cls(r), size[n])][r["rep"]]
            for j, v in enumerate((_ac(seq[n], 1), _ac(seq[n], 2), _ac(miss[n], 1), _ac(miss[n], 2))):
                if v is not None:
                    a[j].append(v)
    for key in sorted(acc):
        cells = []
        for rep in reps:
            a = acc[key].get(rep)
            if not a:
                cells.append("-")
                continue
            m = [f_(float(np.mean(x))) if x else "-" for x in a]
            cells.append(f"{max(len(x) for x in a)}, {m[0]} / {m[1]}, {m[2]} / {m[3]}")
        print(f"| {key[0]} | {key[1]} | " + " | ".join(cells) + " |")
    print()


def report(path: Path) -> None:
    R, bad = load(path)
    print("# NPR STEP 0 tables (npr0_report.py)\n")
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    by = Counter((r["campaign"].split("_")[-1], cls(r)) for r in R)
    print(f"Runs: {dict(by)}; events: {sum(len(r['events']) for r in R)}.\n")
    sec01(R)
    sec02(R)
    sec03(R)
    sec04(R)
    sec05(R)
    sec06(R)
