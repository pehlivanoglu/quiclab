#!/usr/bin/env python3
"""Step 9 (2026-11-15): SETS (sets.py) replayed on the v3 runs and scored next to ECG and h3.
Measurement only: the detector, ECG v1.2, h3 and the Step 8 rows (step8.one: observed sets, congested
egresses, within-event split classes, ECG and h3 groups per close) are used unchanged.

    .venv/bin/python3 reports/step9-2026-11-15/extra_rows.py .runs/2026-11-14_1818_v3     # C12, M8 rows
    .venv/bin/python3 reports/step9-2026-11-15/step9.py rows .runs/2026-11-14_1818_v3      # -> rows9.jsonl
    .venv/bin/python3 reports/step9-2026-11-15/step9.py synth                              # -> synth9.jsonl
    .venv/bin/python3 reports/step9-2026-11-15/report9.py > reports/step9-2026-11-15/tables.md

True sets: clients behind each shaped plan egress with an ordinary (single) queue; M8: up and a only (b is
fq_codel). Levels leaf / mid / up / root. Scores per close (every ECG event for ECG and SETS, every h3
event for h3), averaged over the run:
  per true set: the group with the highest F1 (P = share of the group in the true set, R = share of the
  true set in the group); no group = R 0; exact = a group equals the true set;
  spurious: groups that are the best match of no true set; type: union of two true sets / strict subset of a
  true set / strict superset of a true set / other;
  pairs from each client's smallest group (SAME = same smallest group, DIFFERENT = both grouped, else
  UNCERTAIN) against same-leaf truth (leaf-level true sets) and against the shared-queue truth (the two
  share an egress that has been congested in an event so far) (M);
  time to F1 >= 0.9 (FLAG) per true set (events of that egress, seconds) and per client (its leaf).
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
import zlib
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "step8-2026-11-15"))
import sets as S  # noqa: E402

KDIR = Path(".runs/2026-11-14_1818_v3")
BLOCKS = ("C7", "C8", "C9", "C10", "C11", "C12", "C13", "M7", "M8")
SRCS = ("v2-owd", "truth")
RULES = ("exact", "quantile", "fixed")
KS = (2, 3, 4)
F1_OK = 0.9      # (FLAG)
CTRL = "sub-ctrl"


def load_rows():
    R = []
    for p in (HERE.parent / "step8-2026-11-15" / "rows.jsonl", HERE / "rows-extra.jsonl"):
        for x in open(p):
            r = json.loads(x)
            if "error" not in r:
                R.append(r)
    return R


def ordinary_fam(r):
    if not r["cell"].startswith("M8"):
        return {n: v for n, v in r["fam"].items() if len(v) >= 2}
    import fq_control
    plan = json.loads((KDIR / r["run"] / "v3-plan.json").read_text())
    aqm = fq_control.egress_aqm(KDIR / r["run"], plan)
    return {n: v for n, v in r["fam"].items() if aqm.get(n) == "pfifo" and len(v) >= 2}


# ── scoring helpers (shared by SETS, ECG, h3) ───────────────────────────

class Ctx:
    def __init__(self, r, src):
        self.r, self.src = r, src
        self.clients = sorted(set(r["clients"]) | {c for e in r[src]["events"] for c in e["obs"]} - {CTRL})
        self.ix = {c: i for i, c in enumerate(self.clients)}
        self.fam = ordinary_fam(r)
        self.lv = {n: r["levels"][n] for n in self.fam}
        self.T = {n: self.bm(v) for n, v in self.fam.items()}
        self.leaves = [b for n, b in self.T.items() if self.lv[n] == "leaf"]
        self.hop_fam = r["fam"]       # all shaped egresses (congestion bookkeeping)
        ev = r[src]["events"]
        self.t = [e["t0"] for e in ev]
        self.hot = [set(e["hot"]) for e in ev]
        self.obs = [self.bm(e["obs"]) for e in ev]
        self.by_t = {round(e["t0"], 3): x for x, e in enumerate(ev)}

    def bm(self, cl):
        b = 0
        for c in cl:
            if c in self.ix:
                b |= 1 << self.ix[c]
        return b

    def names(self, b):
        return [c for c, i in self.ix.items() if b >> i & 1]


def f1(g, t):
    i = S.pc(g & t)
    if not i:
        return 0.0, 0.0, 0.0
    p, r_ = i / S.pc(g), i / S.pc(t)
    return p, r_, 2 * p * r_ / (p + r_)


def classify(g, T):
    """true set / union of two true sets / true set minus clients (smallest true set containing it) /
    true set plus clients / other."""
    if g in T.values():
        return "true set"
    tv = list(T.values())
    for i, a in enumerate(tv):
        for b in tv[i + 1:]:
            if not (a & b) and g == a | b:
                return "union of two true sets"
    inside = [(S.pc(t), n) for n, t in T.items() if g & ~t == 0]
    if inside:
        return f"true set minus clients ({min(inside)[1]})"
    if any(t & ~g == 0 for t in tv):
        return "true set plus clients"
    return "other"


class Scorer:
    """Accumulates the per-close scores of one method / variant over a run."""

    def __init__(self, ctx: Ctx):
        self.c = ctx
        self.n = 0
        self.lev = defaultdict(lambda: np.zeros(4))      # level -> sum of P, R, F1, exact over (close, true set)
        self.lev_n = Counter()
        self.spur = []
        self.spur_life = {}
        self.pair = np.zeros(6)        # tp fp fn tn unc (same-leaf), sum over closes
        self.pairq = np.zeros(2)       # right, wrong (shared-queue truth) over SAME pairs
        self.t_ok = {}
        self.t_client = {}
        self.congested = set()
        self.end = None

    def close(self, x, groups):
        c = self.c
        self.n += 1
        self.congested |= c.hot[x]
        best_of = {}
        for n, t in c.T.items():
            best = max(((f1(g, t), g) for g in groups), key=lambda z: z[0][2], default=((0.0, 0.0, 0.0), None))
            (p, r_, ff), g = best
            if g is None:
                p = 0.0
            self.lev[c.lv[n]] += (p, r_, ff, float(g == t))
            self.lev_n[c.lv[n]] += 1
            if g is not None:
                best_of[n] = g
            if ff >= F1_OK and n not in self.t_ok:
                egress_events = sum(1 for y in range(x + 1) if n in c.hot[y])
                self.t_ok[n] = (egress_events, c.t[x], x + 1)
        bests = set(best_of.values())
        sp = [g for g in groups if g not in bests]
        self.spur.append(len(sp))
        for g in sp:
            L = self.spur_life.setdefault(g, [x, x])
            L[1] = x
        # clients' leaf
        for cl, i in c.ix.items():
            if cl in self.t_client:
                continue
            leaf = next((t for t in c.leaves if t >> i & 1), None)
            if leaf is None:
                continue
            if any(g >> i & 1 and f1(g, leaf)[2] >= F1_OK for g in groups):
                self.t_client[cl] = (x + 1, c.t[x])
        # pairs from the smallest group
        small = {}
        for i in range(len(c.clients)):
            gs = [g for g in groups if g >> i & 1]
            if gs:
                small[i] = min(gs, key=lambda g: (S.pc(g), g))
        cnt = np.zeros(6)
        rq = np.zeros(2)
        cong_sets = [c.bm(c.hop_fam[n]) for n in self.congested if n in c.hop_fam]
        for i in range(len(c.clients)):
            for j in range(i + 1, len(c.clients)):
                same_leaf = any(t >> i & 1 and t >> j & 1 for t in c.leaves)
                if i not in small or j not in small:
                    cnt[4] += 1
                elif small[i] == small[j]:
                    cnt[0 if same_leaf else 1] += 1
                    shared = any(b >> i & 1 and b >> j & 1 for b in cong_sets)
                    rq[0 if shared else 1] += 1
                else:
                    cnt[2 if same_leaf else 3] += 1
        self.pair += cnt
        self.pairq += rq
        self._last = (groups, cnt, rq, sp)

    def summary(self, final_groups_info=None):
        c = self.c
        out = {"closes": self.n,
               "levels": {lv: list(self.lev[lv] / self.lev_n[lv]) for lv in self.lev},
               "spur_mean": float(np.mean(self.spur)) if self.spur else math.nan,
               "pairs": list(self.pair), "pairs_q": list(self.pairq),
               "t_ok": {n: v for n, v in self.t_ok.items()}, "t_client": self.t_client,
               "n_true": {lv: sum(1 for n in c.T if c.lv[n] == lv) for lv in set(c.lv.values())}}
        if self.n:
            groups, cnt, rq, sp = self._last
            out["end"] = {"groups": len(groups), "spurious": len(sp), "pairs": list(cnt), "pairs_q": list(rq),
                          "levels": {}, "spur": [{"size": S.pc(g), "best_f1": max((f1(g, t)[2] for t in c.T.values()), default=0),
                                                  "type": classify(g, c.T), "life": self.spur_life[g][1] - self.spur_life[g][0] + 1}
                                                 for g in sp]}
            for n, t in c.T.items():
                (p, r_, ff), g = max(((f1(g, t), g) for g in groups), key=lambda z: z[0][2], default=((0, 0, 0), None))
                out["end"]["levels"].setdefault(c.lv[n], []).append([p, r_, ff, float(g == t)])
        out["spur_lives"] = [v[1] - v[0] + 1 for v in self.spur_life.values()]
        return out


# ── SETS replay ──────────────────────────────────────────────────────────

def sets_variants():
    return [(rule, k, cr) for rule in RULES for k in KS for cr in (False, True)]


def run_sets(ctx: Ctx, m_fixed: float, obs=None, keep_end=True):
    """Score all SETS variants at every close. Returns {variant: summary}, m trace, cost."""
    obs = ctx.obs if obs is None else obs
    tab = S.Table()
    sc = {v: Scorer(ctx) for v in sets_variants()}
    m_trace, work, d_trace = [], [], []
    for x, o in enumerate(obs):
        tab.add(o)
        m, it = S.estimate_m(tab.c) if tab.c else (0.0, 0)
        m_trace.append((round(m, 4), it))
        ml = {}
        w = 0
        for rule, mm in (("exact", 0.0), ("quantile", m), ("fixed", m_fixed)):
            ml[rule], ww = S.match_lists(tab.c, rule, mm)
            w += ww
        work.append(w)
        d_trace.append(len(tab.c))
        for (rule, k, cr), s in sc.items():
            mm = {"exact": 0.0, "quantile": m, "fixed": m_fixed}[rule]
            gs, _ = S.groups_of(tab.c, rule, mm, k, cr, ml=ml[rule])
            s.close(x, [g for g, _, _ in gs])
    out = {}
    for v, s in sc.items():
        out["|".join(map(str, v))] = s.summary()
    # end-of-run group detail (support, Jaccard, right/spurious)
    detail = {}
    m_end, it_end = S.estimate_m(tab.c)
    for rule, k, cr in sets_variants():
        mm = {"exact": 0.0, "quantile": m_end, "fixed": m_fixed}[rule]
        gs, _ = S.groups_of(tab.c, rule, mm, k, cr)
        rows = []
        for g, sup, jac in gs:
            bf = max(((f1(g, t)[2], n) for n, t in ctx.T.items()), default=(0, None))
            rows.append({"members": ctx.names(g), "support": sup, "jaccard": round(jac, 3), "best_f1": round(bf[0], 3),
                         "best": bf[1], "type": classify(g, ctx.T)})
        detail["|".join(map(str, (rule, k, cr)))] = rows
    cost = {"distinct_end": len(tab.c), "bytes_end": tab.size_bytes(len(ctx.clients)), "events": len(obs),
            "clients": len(ctx.clients), "work_mean": float(np.mean(work)) if work else 0, "d_trace": d_trace[::5]}
    return out, detail, {"m_end": m_end, "m_iters_end": it_end, "m_trace": m_trace[::5]}, cost, tab


def end_groups(c: Counter, m_fixed):
    m, _ = S.estimate_m(c)
    out = {}
    for rule, k, cr in sets_variants():
        mm = {"exact": 0.0, "quantile": m, "fixed": m_fixed}[rule]
        gs, _ = S.groups_of(c, rule, mm, k, cr)
        out[(rule, k, cr)] = sorted((g, sp) for g, sp, _ in gs)
    return out


def late_joiner(ctx: Ctx, m_fixed):
    """Hide one client of each leaf (>= 3 clients; the last by name, M) until a group with F1 >= 0.9 to the
    leaf without it is reported; then let it take part. Events (all / of that leaf's egress) and seconds
    from release to the first close with a group that contains it and has F1 >= 0.9 to the leaf."""
    out = []
    names = {b: n for n, b in ctx.T.items()}
    for leaf in ctx.leaves:
        if S.pc(leaf) < 3:
            continue
        lname = names[leaf]
        hid = max(i for i in range(len(ctx.clients)) if leaf >> i & 1)
        rest = leaf & ~(1 << hid)
        for rule in ("exact", "quantile"):
            for k in KS:
                tab = S.Table()
                released, joined = None, None
                for x, o in enumerate(ctx.obs):
                    tab.add(o if released is not None else o & ~(1 << hid))
                    m = S.estimate_m(tab.c)[0] if rule == "quantile" else 0.0
                    gs = [g for g, _, _ in S.groups_of(tab.c, rule, m, k)[0]]
                    if released is None:
                        if any(f1(g, rest)[2] >= F1_OK for g in gs):
                            released = x
                        continue
                    if any(g >> hid & 1 and f1(g, leaf)[2] >= F1_OK for g in gs):
                        joined = x
                        break
                rec = {"leaf": lname, "client": ctx.clients[hid], "rule": rule, "k": k,
                       "released": released is not None, "joined": joined is not None}
                if released is not None and joined is not None:
                    rec["events"] = joined - released
                    rec["leaf_events"] = sum(1 for y in range(released + 1, joined + 1) if lname in ctx.hot[y])
                    rec["seconds"] = ctx.t[joined] - ctx.t[released]
                out.append(rec)
    return out


def unions(ctx: Ctx, r, src, m_fixed):
    """Part D: groups (quantile, k = 2, no crossing filter, end of run) that are the disjoint union of two
    other groups; within-event split outcome over the events whose observed set matches the union."""
    tab = S.Table()
    for o in ctx.obs:
        tab.add(o)
    m, _ = S.estimate_m(tab.c)
    out = []
    for k in KS:
        gs = [g for g, _, _ in S.groups_of(tab.c, "quantile", m, k)[0]]
        kept = {g for g, _, _ in S.groups_of(tab.c, "quantile", m, k, True)[0]}
        for u in gs:
            for i, a in enumerate(gs):
                for b in gs[i + 1:]:
                    if a == u or b == u or a & b or (a | b) != u:
                        continue
                    q = S.qmiss(S.pc(u), round(m, 6))
                    res = Counter()
                    for e, o in zip(r[src]["events"], ctx.obs):
                        if not (S.pc(o & ~u) <= S.EXTRA and S.pc(u & ~o) <= q) or e["classes"] is None:
                            continue
                        C = {ctx.bm(cl) for cl in e["classes"]}
                        want = {x & o for x in (a, b) if x & o}
                        res["n"] += 1
                        res["exact" if C == want else "one class" if len(C) == 1 and o in C else "none" if not C else "other"] += 1
                    tv = set(ctx.T.values())
                    case = ("true upstream, parts true sets" if u in tv and a in tv and b in tv else
                            "union of concurrent true sets (not a queue)" if u not in tv and a in tv and b in tv else
                            "parts not both true sets")
                    out.append({"k": k, "union": ctx.names(u), "parts": [ctx.names(a), ctx.names(b)], "case": case,
                                "removed_by_crossing": u not in kept, **res})
    return out


def worker(args):
    r, m_fixed = args
    try:
        out = {"run": r["run"], "cell": r["cell"], "block": r["block"], "aqm": r["aqm"], "rep": r["rep"]}
        for src in SRCS:
            ctx = Ctx(r, src)
            if r["aqm"] == "fq_codel":
                out[src] = fq_part(ctx, r, src, m_fixed[src])
                continue
            t0 = time.time()
            sets_sc, detail, mm, cost, tab = run_sets(ctx, m_fixed[src])
            cost["seconds"] = time.time() - t0
            # ECG and h3 on the same yardstick
            ecg = Scorer(ctx)
            for x, e in enumerate(r[src]["events"]):
                ecg.close(x, [ctx.bm(g) for g in e["groups"] if len(g) >= 2])
            h3 = Scorer(ctx)
            for e in r[src]["h3"]:
                x = ctx.by_t.get(round(e["t0"], 3))
                if x is None:
                    x = int(np.argmin([abs(t - e["t0"]) for t in ctx.t])) if ctx.t else 0
                h3.close(x, [ctx.bm(g) for g in e["groups"] if len(g) >= 2])
            # order: the end table and groups for reversed and three random orders
            orders = {"reversed": list(range(len(ctx.obs)))[::-1]}
            for i in range(3):
                o = list(range(len(ctx.obs)))
                random.Random(zlib.crc32(f"{r['run']}|{src}|{i}".encode())).shuffle(o)
                orders[f"random {i + 1}"] = o
            ref = end_groups(tab.c, m_fixed[src])
            same = {}
            for name, o in orders.items():
                t2 = S.Table()
                for i in o:
                    t2.add(ctx.obs[i])
                same[name] = end_groups(t2.c, m_fixed[src]) == ref
            out[src] = {"sets": sets_sc, "detail": detail, "m": mm, "cost": cost, "ecg": ecg.summary(), "h3": h3.summary(),
                        "order_identical": same, "late": late_joiner(ctx, m_fixed[src]), "unions": unions(ctx, r, src, m_fixed[src]),
                        "fam": {n: ctx.fam[n] for n in ctx.fam}, "levels": ctx.lv}
        return out
    except Exception as e:   # noqa: BLE001
        import traceback
        return {"run": r["run"], "error": repr(e), "tb": traceback.format_exc()[-2000:]}


# ── Part E (fq_codel) ────────────────────────────────────────────────────

def fq_part(ctx: Ctx, r, src, m_fixed):
    """Groups SETS reports among clients behind a per-flow-queue egress (all clients here). Same-queue
    reading: every group is false. Same-link reading: true sets = distinct per-event constrained sets
    (fq_truth, >= 2 clients) seen in >= 2 events (M); per close best F1 per such set and spurious groups."""
    ev = r[src]["events"]
    cons = Counter(frozenset(e.get("fq_truth", [])) for e in ev if len(e.get("fq_truth", [])) >= 2)
    link_sets = {"+".join(sorted(s)): ctx.bm(s) for s, n in cons.items() if n >= 2}
    tab = S.Table()
    per = defaultdict(lambda: {"groups": [], "f1": [], "spur": []})
    for x, o in enumerate(ctx.obs):
        tab.add(o)
        m = S.estimate_m(tab.c)[0]
        for rule, mm in (("exact", 0.0), ("quantile", m)):
            for k in KS:
                gs = [g for g, _, _ in S.groups_of(tab.c, rule, mm, k)[0]]
                v = per[f"{rule}|{k}"]
                v["groups"].append(len(gs))
                bests = set()
                fs = []
                for t in link_sets.values():
                    b = max(((f1(g, t)[2], g) for g in gs), default=(0.0, None))
                    fs.append(b[0])
                    if b[1] is not None:
                        bests.add(b[1])
                v["f1"].append(float(np.mean(fs)) if fs else math.nan)
                v["spur"].append(sum(g not in bests for g in gs))
    m_end = S.estimate_m(tab.c)[0]
    end = {}
    for rule, mm in (("exact", 0.0), ("quantile", m_end)):
        for k in KS:
            gs = S.groups_of(tab.c, rule, mm, k)[0]
            end[f"{rule}|{k}"] = [{"members": ctx.names(g), "support": sp, "jaccard": round(j, 3),
                                   "best_link_f1": round(max((f1(g, t)[2] for t in link_sets.values()), default=0), 3)} for g, sp, j in gs]
    return {"fq": True, "per": {k: {"groups_mean": float(np.mean(v["groups"])), "link_f1_mean": float(np.nanmean(v["f1"])) if v["f1"] else math.nan,
                                    "link_spur_mean": float(np.mean(v["spur"]))} for k, v in per.items()},
            "end": end, "link_sets": {k: S.pc(b) for k, b in link_sets.items()}, "m_end": m_end}


# ── Part C (model) ───────────────────────────────────────────────────────

def miss_model(R):
    """Per level and AQM (v2-owd onsets, single-egress events): miss rate, false-inclusion rate, per-event
    miss fractions; and the pooled per-source miss rate used as the fixed-m reference."""
    stats = defaultdict(lambda: {"miss": 0, "n": 0, "fi": 0, "nn": 0, "per_event": [], "k_miss": [], "size": []})
    pooled = {s: [0, 0] for s in SRCS}
    for r in R:
        if r["aqm"] == "fq_codel":
            continue
        fam = r["fam"]
        allc = set(r["clients"]) - {CTRL}
        for src in SRCS:
            for e in r[src]["events"]:
                if len(e["hot"]) != 1:
                    continue
                h = e["hot"][0]
                beh = set(fam[h])
                o = set(e["obs"])
                miss = len(beh - o)
                pooled[src][0] += miss
                pooled[src][1] += len(beh)
                if src != "v2-owd":
                    continue
                st = stats[(r["levels"][h], r["aqm"])]
                st["miss"] += miss
                st["n"] += len(beh)
                st["fi"] += len(o - beh)
                st["nn"] += len(allc - beh)
                st["per_event"].append(miss / len(beh))
                st["k_miss"].append(miss)
                st["size"].append(len(beh))
    fixed = {s: v[0] / v[1] if v[1] else 0.0 for s, v in pooled.items()}
    return stats, fixed


def synth_run(args):
    """One synthetic replay: the truth-onset observed sets of a run, every client replaced by r replicas;
    each replica of an observed client missed and each replica of an unobserved client added with the
    measured rates (level of the event's congested egress, pooled over AQMs); misses per event drawn
    either independently (binomial) or with the event's miss fraction resampled from the measured
    per-event fractions of that level (joint)."""
    row, rr, model, mode, seed = args
    rng = random.Random(seed)
    ctx = Ctx(row, "truth")
    n = len(ctx.clients)
    rep = lambda b: sum(((1 << rr) - 1) << (i * rr) for i in range(n) if b >> i & 1)   # noqa: E731
    T = {nm: rep(b) for nm, b in ctx.T.items()}
    obs = []
    for x, e in enumerate(row["truth"]["events"]):
        if len(e["obs"]) < 2:
            continue
        lvl = row["levels"][e["hot"][0]] if len(e["hot"]) == 1 else "leaf"
        mdl = model.get(lvl) or model["leaf"]
        mfrac = rng.choice(mdl["per_event"]) if mode == "joint" else mdl["m"]
        b = rep(ctx.obs[x])
        out = 0
        for i in range(n * rr):
            if b >> i & 1:
                if rng.random() >= mfrac:
                    out |= 1 << i
            elif rng.random() < mdl["f"]:
                out |= 1 << i
        obs.append((out, e["t0"], set(e["hot"])))
    res = {}
    tab = S.Table()
    t_work = []
    for x, (o, t0, hot) in enumerate(obs):
        tab.add(o)
        if x % 5 == 4 or x == len(obs) - 1:
            t1 = time.time()
            m = S.estimate_m(tab.c)[0]
            for rule, mm in (("exact", 0.0), ("quantile", m)):
                for k in KS:
                    gs = [g for g, _, _ in S.groups_of(tab.c, rule, mm, k)[0]]
                    v = res.setdefault(f"{rule}|{k}", {"f1": defaultdict(list), "spur": [], "end": None})
                    bests = set()
                    per_lv = defaultdict(list)
                    for nm, t in T.items():
                        bf = max(((f1(g, t)[2], g) for g in gs), default=(0.0, None))
                        per_lv[ctx.lv[nm]].append(bf[0])
                        if bf[1] is not None:
                            bests.add(bf[1])
                    for lv_, xs in per_lv.items():
                        v["f1"][lv_].append(float(np.mean(xs)))
                    v["spur"].append(sum(g not in bests for g in gs))
            t_work.append(time.time() - t1)
    out = {"run": row["run"], "r": rr, "mode": mode, "group_sizes": {nm: S.pc(t) for nm, t in T.items()},
           "distinct_end": len(tab.c), "bytes_end": tab.size_bytes(n * rr), "read_seconds_mean": float(np.mean(t_work)),
           "m_end": S.estimate_m(tab.c)[0]}
    for key, v in res.items():
        out[key] = {"f1_mean": {lv: float(np.mean(x)) for lv, x in v["f1"].items()},
                    "f1_end": {lv: x[-1] for lv, x in v["f1"].items()},
                    "spur_mean": float(np.mean(v["spur"])), "spur_end": v["spur"][-1]}
    return out


if __name__ == "__main__":
    R = [r for r in load_rows() if r["block"] in BLOCKS]
    stats, fixed = miss_model(R)
    if sys.argv[1] == "rows":
        KDIR = Path(sys.argv[2])
        json.dump({"fixed_m": fixed, "model": {f"{k[0]}|{k[1]}": {"miss": v["miss"] / v["n"] if v["n"] else None,
                                                                 "fi": v["fi"] / v["nn"] if v["nn"] else None,
                                                                 "n_events": len(v["per_event"]), "k_miss": v["k_miss"],
                                                                 "size": v["size"]} for k, v in stats.items()}},
                  open(HERE / "model9.json", "w"))
        with Pool(10) as pool, open(HERE / "rows9.jsonl", "w") as fh:
            for res in pool.imap_unordered(worker, [(r, fixed) for r in R]):
                fh.write(json.dumps(res) + "\n")
                fh.flush()
    elif sys.argv[1] == "synth":
        # model per level pooled over AQMs (v2-owd)
        lv = defaultdict(lambda: {"miss": 0, "n": 0, "fi": 0, "nn": 0, "per_event": []})
        for (l, a), v in stats.items():
            for kk in ("miss", "n", "fi", "nn"):
                lv[l][kk] += v[kk]
            lv[l]["per_event"] += v["per_event"]
        model = {l: {"m": v["miss"] / v["n"], "f": v["fi"] / v["nn"] if v["nn"] else 0.0, "per_event": v["per_event"]} for l, v in lv.items()}
        base = [r for r in R if r["block"] in ("C7", "C9", "C11") and r["aqm"] == "pfifo"]
        jobs = [(r, rr, model, mode, zlib.crc32(f"{r['run']}|{rr}|{mode}".encode()))
                for r in base for rr in (1, 5, 25, 100) for mode in ("independent", "joint")]
        with Pool(10) as pool, open(HERE / "synth9.jsonl", "w") as fh:
            for res in pool.imap_unordered(synth_run, jobs):
                fh.write(json.dumps(res) + "\n")
                fh.flush()
