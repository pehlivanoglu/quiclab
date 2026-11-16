#!/usr/bin/env python3
"""Step 10 (2026-11-15): where the observed set loses clients, three definitions of it, SETS with two
matching fixes, leaf-level scoring, robustness to upstream events, scale model again, fq_codel.
Measurement only. Inputs, all unchanged: Step 8 rows (events, congested egresses, ECG / h3 groups per close),
the ECG output of each run (metrics.json events with close times, evidence.jsonl onsets with their event and
aligned time, onsets.jsonl observability), the frozen detector's alarm spans (shadow_v2_frozen.episodes,
v2, OWD, hold), gt1.base_rtts, the client rates.

    .venv/bin/python3 reports/step10-2026-11-15/step10.py rows .runs/2026-11-14_1818_v3    # -> rows10.jsonl, model10.json
    .venv/bin/python3 reports/step10-2026-11-15/step10.py synth                            # -> synth10.jsonl
    .venv/bin/python3 reports/step10-2026-11-15/report10.py > reports/step10-2026-11-15/tables.md

Observed sets per ECG event (detector onsets; event = [t0, t_close] from metrics.json):
  O1  the event's members (as Steps 8 / 9).
  O2  observable clients in alarm at any time in [t0, t_close].
  O3  observable clients whose alarm started in [t0 - base RTT of the client (P), t_close] and is on at t0 when
      it started before t0.
  O4  O1 plus observable clients whose ECG onset (aligned time) lies within delta_max (T, ECG config) of t0,
      whichever event ECG assigned it to (added after Part A: most misses are onsets split into a neighbouring event).
  truth: O1 with truth onsets (reference).
Truth set of an event: clients behind the congested egresses (Step 8 rule).
"""

from __future__ import annotations

import bisect
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
ROOT = HERE.parents[1]
for p in ("reports/step9-2026-11-15", "reports/step8-2026-11-15", "scripts"):
    sys.path.insert(0, str(ROOT / p))
import sets as S1  # noqa: E402
import sets2 as S2  # noqa: E402
import step9  # noqa: E402

KDIR = Path(".runs/2026-11-14_1818_v3")
CTRL = "sub-ctrl"
DEFS = ("O1", "O2", "O3", "O4")
VARIANTS = ("old", "new", "contain")
KS = (2, 3)
JF = (None, 0.85, 0.95)       # (FLAG) mean-Jaccard filters
DELTA, DELTA_MAX = 0.15, 0.30  # ECG v1.2 config (T, read from metrics.json)


def load_rows():
    return [r for r in step9.load_rows() if r["block"] in step9.BLOCKS]


# ── phase 1: observed sets, Part A, Part B ──────────────────────────────

def phase1(r):
    try:
        import det_eval as d
        import gt1
        import shadow_v2_frozen as fz
        rd = KDIR / r["run"]
        run = d.Run(rd)
        gdir = rd / "grouping-d150-v2-owd"
        m = json.loads((gdir / "metrics.json").read_text())
        evm = m["events"]
        cfg = m["config"]
        onsets = defaultdict(list)       # client -> [(t_al, t_onset, event_id)]
        for x in open(gdir / "evidence.jsonl"):
            if '"type": "onset"' in x:
                o = json.loads(x)
                onsets[o["flow"]].append((o["t_al"], o["t_onset"], o["event_id"]))
        obs_t, obs_v = defaultdict(list), defaultdict(list)
        for x in open(gdir / "onsets.jsonl"):
            if '"obs"' in x:
                o = json.loads(x)
                obs_t[o["flow"]].append(o["t"])
                obs_v[o["flow"]].append(o["observable"])
        spans = fz.episodes(run, "v2", mode="OWD", hold=True)
        rtt = gt1.base_rtts(run)
        rate = {s: (run.topology["subscribers"].get(s) or {}).get("rate_kbps") for s in run.subs}
        clients = sorted(set(r["clients"]) - {CTRL})
        fam = r["fam"]
        lev = r["levels"]

        def observable(c, t):
            ts = obs_t.get(c)
            if not ts:
                return False
            i = bisect.bisect_right(ts, t) - 1
            return bool(obs_v[c][i]) if i >= 0 else False

        events = []
        A = []
        for x, (e, em) in enumerate(zip(r["v2-owd"]["events"], evm)):
            t0, tc = em["t0"], em["t"]
            o1 = set(e["obs"]) - {CTRL}
            obsv = {c for c in clients if observable(c, t0)}
            o2 = {c for c in obsv if any(on <= tc and en >= t0 for (al, en, on) in spans.get(c, []))}
            o3 = set()
            for c in obsv:
                for (al, en, on) in spans.get(c, []):
                    if t0 - rtt.get(c, 0.05) <= on <= tc and (on >= t0 or en >= t0):
                        o3.add(c)
                        break
            # O4 (from Part A): O1 plus observable clients whose ECG onset (aligned) lies within delta_max of t0,
            # whichever ECG event it was assigned to
            o4 = o1 | {c for c in obsv if any(abs(ta - t0) <= DELTA_MAX for ta, _, _ in onsets.get(c, []))}
            hot = e["hot"]
            T = set().union(*[set(fam[h]) for h in hot]) - {CTRL} if hot else set()
            events.append({"t0": t0, "t": tc, "hot": hot, "T": sorted(T), "O1": sorted(o1), "O2": sorted(o2), "O3": sorted(o3), "O4": sorted(o4),
                           "groups": e["groups"], "fq_truth": e.get("fq_truth"), "n_obs": len(obsv)})
            # Part A: missing from O1 although behind a congested egress
            lvl = lev[hot[0]] if len(hot) == 1 else ("combined" if hot else "none")
            for c in sorted(T - o1):
                rec = {"x": x, "client": c, "level": lvl, "rate": rate.get(c), "rtt_ms": round(rtt.get(c, math.nan) * 1e3, 1),
                       "observable": observable(c, t0), "in_alarm_event": any(on <= tc and en >= t0 for (al, en, on) in spans.get(c, [])),
                       "branch": next((n for n in fam if lev.get(n) == "mid" and c in fam[n]), None)}
                lo, hi = t0 - 5.0, tc + 5.0          # (M) search window when no stimulus window is known
                cover = [(al, en, on) for (al, en, on) in spans.get(c, []) if on <= t0 <= en]
                near = [(abs(ta - t0), ta - t0, ev) for ta, to, ev in onsets.get(c, []) if lo <= ta <= hi]
                rec["in_alarm_window"] = any(on <= hi and en >= lo for (al, en, on) in spans.get(c, []))
                if not rec["observable"]:
                    cat, off = "not observable", None
                elif cover and min(on for _, _, on in cover) < t0 - DELTA_MAX:
                    cat, off = "already in alarm", min(on for _, _, on in cover) - t0
                elif near:
                    _, off, ev = min(near)
                    cat = ("in another event, within delta" if abs(off) <= DELTA else
                           "in another event, within delta_max" if abs(off) <= DELTA_MAX else "in another event, outside delta_max")
                elif rec["in_alarm_window"]:
                    cat, off = "alarmed, no onset reached ECG", None
                else:
                    cat, off = "never alarmed", None
                rec["cat"], rec["offset_ms"] = cat, (round(off * 1e3, 1) if off is not None else None)
                A.append(rec)
        meta = {c: {"rate": rate.get(c), "rtt_ms": round(rtt.get(c, math.nan) * 1e3, 1)} for c in clients}
        return {"run": r["run"], "cell": r["cell"], "block": r["block"], "aqm": r["aqm"], "rep": r["rep"], "fam": fam, "levels": lev,
                "clients": clients, "events": events, "A": A, "meta": meta, "delta": cfg["delta"], "delta_max": cfg["delta_max"],
                "truth_events": [{"t0": e["t0"], "O1": sorted(set(e["obs"]) - {CTRL}), "hot": e["hot"], "groups": e["groups"]}
                                 for e in r["truth"]["events"]],
                "h3": r["v2-owd"]["h3"], "h3_truth": r["truth"]["h3"], "ordinary": step9.ordinary_fam(r)}
    except Exception as ex:   # noqa: BLE001
        import traceback
        return {"run": r["run"], "error": repr(ex), "tb": traceback.format_exc()[-2000:]}


def partB(P):
    """Per definition, level and AQM over single-egress events: miss / false-inclusion counts, per-event
    fractions; and the pooled leaf false-inclusion rate per definition (used by the 'new' matching)."""
    out = defaultdict(lambda: {"miss": 0, "n": 0, "fi": 0, "nn": 0, "k": [], "size": [], "eq": 0, "ev": 0,
                               "P": [], "R": [], "pe_miss": [], "pe_fi": []})
    for p in P:
        if p["aqm"] == "fq_codel":
            continue
        N = len(p["clients"])
        for e in p["events"]:
            if len(e["hot"]) != 1:
                continue
            lv = p["levels"][e["hot"][0]]
            T = set(e["T"])
            for dfn in DEFS:
                O = set(e[dfn])
                s = out[(dfn, lv, p["aqm"])]
                miss, fi = len(T - O), len(O - T)
                s["miss"] += miss
                s["n"] += len(T)
                s["fi"] += fi
                s["nn"] += N - len(T)
                s["k"].append(miss)
                s["size"].append(len(T))
                s["eq"] += O == T
                s["ev"] += 1
                s["P"].append(len(O & T) / len(O) if O else math.nan)
                s["R"].append(len(O & T) / len(T) if T else math.nan)
                s["pe_miss"].append(miss / len(T))
                s["pe_fi"].append(fi / (N - len(T)) if N > len(T) else 0.0)
    return out


# ── phase 2: SETS replays ────────────────────────────────────────────────

class Ctx2(step9.Ctx):
    """step9.Ctx built from phase-1 data for one definition."""

    def __init__(self, p, dfn, truth_src=False):
        self.r = {"fam": p["fam"], "levels": p["levels"]}
        self.clients = sorted(set(p["clients"]))
        self.ix = {c: i for i, c in enumerate(self.clients)}
        self.fam = p["ordinary"]
        self.lv = {n: p["levels"][n] for n in self.fam}
        self.T = {n: self.bm(v) for n, v in self.fam.items()}
        self.leaves = [b for n, b in self.T.items() if self.lv[n] == "leaf"]
        self.hop_fam = p["fam"]
        ev = p["truth_events"] if truth_src else p["events"]
        self.t = [e["t0"] for e in ev]
        self.hot = [set(e["hot"]) for e in ev]
        self.obs = [self.bm(e["O1" if truth_src else dfn]) for e in ev]
        self.by_t = {round(e["t0"], 3): x for x, e in enumerate(ev)}
        self.ev = ev
        self.upstream = [any(p["levels"].get(h) in ("up", "mid", "root") for h in e["hot"]) for e in ev]


def leaf_f1(ctx, groups):
    if not ctx.leaves:
        return math.nan
    return float(np.mean([max((step9.f1(g, t)[2] for g in groups), default=0.0) for t in ctx.leaves]))


def read_groups(c, variant, k, n_clients, f, m_old_cache):
    if variant == "old":
        m = m_old_cache.setdefault("m", S1.estimate_m(c)[0])
        ml, _ = S2.match_lists(c, "old", m_old=m)
    else:
        ml, _ = S2.match_lists(c, variant, n_clients=n_clients, f=f)
    return S2.groups_of(c, k, ml)


def replay(ctx, f, track_robust=True):
    """Every (variant, k, Jaccard filter): Scorer summary + leaf F1 after upstream / other closes."""
    tab = S1.Table()
    keys = [(v, k, j) for v in VARIANTS for k in KS for j in JF]
    sc = {key: step9.Scorer(ctx) for key in keys}
    rob = {key: {"up": [], "other": []} for key in keys}
    n = len(ctx.clients)
    for x, o in enumerate(ctx.obs):
        tab.add(o)
        cache = {}
        for v in VARIANTS:
            for k in KS:
                gs = read_groups(tab.c, v, k, n, f, cache)
                for j in JF:
                    g = [s for s, sp, jac in gs if j is None or jac >= j]
                    sc[(v, k, j)].close(x, g)
                    rob[(v, k, j)]["up" if ctx.upstream[x] else "other"].append(leaf_f1(ctx, g))
    out = {}
    for key in keys:
        s = sc[key].summary()
        s["robust"] = {w: float(np.nanmean(v)) if v else math.nan for w, v in rob[key].items()}
        s["robust_n"] = {w: len(v) for w, v in rob[key].items()}
        out["|".join(map(str, key))] = s
    return out, tab


def method_score(ctx, closes):
    s = step9.Scorer(ctx)
    rob = {"up": [], "other": []}
    for x, groups in closes:
        s.close(x, groups)
        rob["up" if ctx.upstream[x] else "other"].append(leaf_f1(ctx, groups))
    out = s.summary()
    out["robust"] = {w: float(np.nanmean(v)) if v else math.nan for w, v in rob.items()}
    out["robust_n"] = {w: len(v) for w, v in rob.items()}
    return out


def late(ctx, f):
    out = []
    names = {b: n for n, b in ctx.T.items()}
    n = len(ctx.clients)
    for leaf in ctx.leaves:
        if S1.pc(leaf) < 3:
            continue
        hid = max(i for i in range(n) if leaf >> i & 1)
        rest = leaf & ~(1 << hid)
        for v in VARIANTS:
            for k in KS:
                tab = S1.Table()
                rel = joined = None
                for x, o in enumerate(ctx.obs):
                    tab.add(o if rel is not None else o & ~(1 << hid))
                    gs = [g for g, _, _ in read_groups(tab.c, v, k, n, f, {})]
                    if rel is None:
                        if any(step9.f1(g, rest)[2] >= step9.F1_OK for g in gs):
                            rel = x
                        continue
                    if any(g >> hid & 1 and step9.f1(g, leaf)[2] >= step9.F1_OK for g in gs):
                        joined = x
                        break
                rec = {"leaf": names[leaf], "variant": v, "k": k, "released": rel is not None, "joined": joined is not None}
                if rel is not None and joined is not None:
                    rec.update(events=joined - rel, leaf_events=sum(1 for y in range(rel + 1, joined + 1) if names[leaf] in ctx.hot[y]),
                               seconds=ctx.t[joined] - ctx.t[rel])
                out.append(rec)
    return out


def order_same(ctx, tab, f):
    ref = {}
    n = len(ctx.clients)
    for v in VARIANTS:
        for k in KS:
            ref[(v, k)] = sorted((g, s) for g, s, _ in read_groups(tab.c, v, k, n, f, {}))
    same = {}
    for i in range(4):
        o = list(range(len(ctx.obs)))
        if i == 0:
            o = o[::-1]
        else:
            random.Random(zlib.crc32(f"{i}|{len(o)}".encode())).shuffle(o)
        t2 = S1.Table()
        for y in o:
            t2.add(ctx.obs[y])
        same[i] = all(sorted((g, s) for g, s, _ in read_groups(t2.c, v, k, n, f, {})) == ref[(v, k)] for v in VARIANTS for k in KS)
    return all(same.values())


def phase2(args):
    p, fdef = args
    try:
        out = {"run": p["run"], "cell": p["cell"], "block": p["block"], "aqm": p["aqm"], "rep": p["rep"], "levels": p["levels"],
               "ordinary": p["ordinary"]}
        if p["aqm"] == "fq_codel":
            out["fq"] = {dfn: fq_score(p, dfn, fdef[dfn]) for dfn in DEFS}
            return out
        for dfn in DEFS + ("truth",):
            ctx = Ctx2(p, dfn, truth_src=dfn == "truth")
            f = fdef["O1" if dfn == "truth" else dfn]
            t0 = time.time()
            res, tab = replay(ctx, f)
            out[dfn] = {"sets": res, "late": late(ctx, f), "order_identical": order_same(ctx, tab, f),
                        "seconds": time.time() - t0, "distinct": len(tab.c)}
        # ECG and h3 (their own events; detector and truth onsets)
        for src, evkey, h3key in (("v2-owd", "events", "h3"), ("truth", "truth_events", "h3_truth")):
            ctx = Ctx2(p, "O1", truth_src=src == "truth")
            ecg = [(x, [ctx.bm(g) for g in e["groups"] if len(g) >= 2]) for x, e in enumerate(p[evkey])]
            h3 = []
            for e in p[h3key]:
                x = ctx.by_t.get(round(e["t0"], 3))
                if x is None and ctx.t:
                    x = int(np.argmin([abs(t - e["t0"]) for t in ctx.t]))
                h3.append((x, [ctx.bm(g) for g in e["groups"] if len(g) >= 2]))
            out[f"ecg|{src}"] = method_score(ctx, ecg)
            out[f"h3|{src}"] = method_score(ctx, h3)
        return out
    except Exception as ex:   # noqa: BLE001
        import traceback
        return {"run": p["run"], "error": repr(ex), "tb": traceback.format_exc()[-2000:]}


def fq_score(p, dfn, f):
    """Same-link reading: link sets = per-event constrained sets (fq_truth, >= 2 clients) seen in >= 2 events (M)."""
    ctx = Ctx2(p, dfn)
    cons = Counter(frozenset(e["fq_truth"] or []) for e in p["events"] if e.get("fq_truth") and len(e["fq_truth"]) >= 2)
    link = [ctx.bm(s) for s, n in cons.items() if n >= 2]
    tab = S1.Table()
    acc = defaultdict(lambda: {"f1": [], "spur": [], "groups": []})
    n = len(ctx.clients)
    for x, o in enumerate(ctx.obs):
        tab.add(o)
        cache = {}
        for v in VARIANTS:
            for k in KS:
                gs = [g for g, _, _ in read_groups(tab.c, v, k, n, f, cache)]
                a = acc[f"{v}|{k}"]
                bests = set()
                fs = []
                for t in link:
                    b = max(((step9.f1(g, t)[2], g) for g in gs), default=(0.0, None))
                    fs.append(b[0])
                    if b[1] is not None:
                        bests.add(b[1])
                a["f1"].append(float(np.mean(fs)) if fs else math.nan)
                a["spur"].append(sum(g not in bests for g in gs))
                a["groups"].append(len(gs))
    return {k: {"link_f1": float(np.nanmean(v["f1"])) if v["f1"] else math.nan, "spur": float(np.mean(v["spur"])),
                "groups": float(np.mean(v["groups"]))} for k, v in acc.items()} | {"link_sets": len(link)}


# ── Part D: model ────────────────────────────────────────────────────────

def synth_job(args):
    p, dfn, rr, mode, mdl, f, seed = args
    rng = random.Random(seed)
    ctx = Ctx2(p, "O1", truth_src=True)
    n = len(ctx.clients)
    rep = lambda b: sum(((1 << rr) - 1) << (i * rr) for i in range(n) if b >> i & 1)   # noqa: E731
    leaves = [rep(b) for b in ctx.leaves]
    T = {nm: rep(b) for nm, b in ctx.T.items()}
    obs = []
    for x, e in enumerate(p["truth_events"]):
        if len(e["O1"]) < 2:
            continue
        lv = p["levels"][e["hot"][0]] if len(e["hot"]) == 1 else "leaf"
        md = mdl.get(lv) or mdl["leaf"]
        if mode == "joint":
            i = rng.randrange(len(md["pe_miss"]))
            mf, ff = md["pe_miss"][i], md["pe_fi"][i]
        else:
            mf, ff = md["m"], md["f"]
        b = rep(ctx.obs[x])
        o = 0
        for i in range(n * rr):
            if b >> i & 1:
                if rng.random() >= mf:
                    o |= 1 << i
            elif rng.random() < ff:
                o |= 1 << i
        obs.append(o)
    tab = S1.Table()
    res = defaultdict(lambda: {"leaf": [], "spur": []})
    t_read = []
    for x, o in enumerate(obs):
        tab.add(o)
        if x % 5 == 4 or x == len(obs) - 1:
            cache = {}
            t1 = time.time()
            for v in VARIANTS:
                for k in KS:
                    gs = [g for g, _, _ in read_groups(tab.c, v, k, n * rr, f, cache)]
                    bests = set()
                    for t in T.values():
                        bb = max(((step9.f1(g, t)[2], g) for g in gs), default=(0.0, None))
                        if bb[1] is not None:
                            bests.add(bb[1])
                    res[f"{v}|{k}"]["leaf"].append(float(np.mean([max((step9.f1(g, t)[2] for g in gs), default=0.0) for t in leaves])))
                    res[f"{v}|{k}"]["spur"].append(sum(g not in bests for g in gs))
            t_read.append(time.time() - t1)
    return {"run": p["run"], "def": dfn, "r": rr, "mode": mode, "leaf_sizes": sorted({S1.pc(t) for t in leaves}),
            "distinct": len(tab.c), "read_s": float(np.mean(t_read)) if t_read else 0.0,
            **{k: {"leaf_end": v["leaf"][-1], "leaf_mean": float(np.mean(v["leaf"])), "spur_end": v["spur"][-1],
                   "spur_mean": float(np.mean(v["spur"]))} for k, v in res.items()}}


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "rows":
        KDIR = Path(sys.argv[2])
        R = load_rows()
        with Pool(10) as pool:
            P = list(pool.imap_unordered(phase1, R))
        err = [p for p in P if "error" in p]
        for e in err:
            print("phase1 error", e["run"], e["tb"], file=sys.stderr)
        P = [p for p in P if "error" not in p]
        B = partB(P)
        fdef = {}
        for dfn in DEFS:
            fi = sum(v["fi"] for (d_, lv, a), v in B.items() if d_ == dfn and lv == "leaf")
            nn = sum(v["nn"] for (d_, lv, a), v in B.items() if d_ == dfn and lv == "leaf")
            fdef[dfn] = fi / nn if nn else 0.0
        model = {}
        for dfn in DEFS:
            per = defaultdict(lambda: {"miss": 0, "n": 0, "fi": 0, "nn": 0, "pe_miss": [], "pe_fi": []})
            for (d_, lv, a), v in B.items():
                if d_ != dfn:
                    continue
                for kk in ("miss", "n", "fi", "nn"):
                    per[lv][kk] += v[kk]
                per[lv]["pe_miss"] += v["pe_miss"]
                per[lv]["pe_fi"] += v["pe_fi"]
            model[dfn] = {lv: {"m": v["miss"] / v["n"], "f": v["fi"] / v["nn"] if v["nn"] else 0.0, "pe_miss": v["pe_miss"],
                               "pe_fi": v["pe_fi"]} for lv, v in per.items()}
        json.dump({"f": fdef, "B": {"|".join(k): {kk: vv for kk, vv in v.items()} for k, v in B.items()}, "model": model},
                  open(HERE / "model10.json", "w"))
        with open(HERE / "phase1.jsonl", "w") as fh:
            for p in P:
                fh.write(json.dumps({k: v for k, v in p.items() if k != "events"} | {"events": p["events"]}) + "\n")
        with Pool(10) as pool, open(HERE / "rows10.jsonl", "w") as fh:
            for res in pool.imap_unordered(phase2, [(p, fdef) for p in P]):
                fh.write(json.dumps(res) + "\n")
                fh.flush()
    elif cmd == "synth":
        M = json.load(open(HERE / "model10.json"))
        P = [json.loads(x) for x in open(HERE / "phase1.jsonl")]
        base = [p for p in P if p["block"] in ("C7", "C9", "C11") and p["aqm"] == "pfifo"]
        jobs = [(p, dfn, rr, mode, M["model"][dfn], M["f"][dfn], zlib.crc32(f"{p['run']}|{dfn}|{rr}|{mode}".encode()))
                for p in base for dfn in DEFS for rr in (5, 25, 100) for mode in ("independent", "joint")]
        with Pool(10) as pool, open(HERE / "synth10.jsonl", "w") as fh:
            for res in pool.imap_unordered(synth_job, jobs):
                fh.write(json.dumps(res) + "\n")
                fh.flush()
