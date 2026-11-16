#!/usr/bin/env python3
"""Alarm at harm onset, GT-Q time coverage with a random-alarm precision baseline, and the fq_codel GT-H
counting question. Runs with a valid GT-Q only (truth/gtq.csv present; 201 / 203). Measurement only: the
frozen detectors, truth/gtq.csv, gtq-gray.csv and the gtq_score matching rule are used unchanged.

    .venv/bin/python3 reports/v3-score/harm.py .runs/2026-11-14_1818_v3 > reports/v3-score/harm.md
        (per-run rows cached in reports/v3-score/harm-rows.jsonl; delete it to recompute)

A. Per GT-H 600 harmful forward episode (t_harm = t_harm_600, the earliest harm instant, gtq.py):
   on at harm  = an alarm span (frozen v2, hold, OWD) covers t_harm
   lead        = t_harm - start of that span (how long before harm the alarm opened)
   span start in collar / before collar: collar = [t0 - W, t1 + d_obs + W] (gtq_score)
   hit (gtq_score recall) = an alarm START (>= warm-up, merged within W) inside the collar, at any time
   alarm_before_harm (rows.jsonl / RAPOR) = hit and lead_600 > 0 (first start in the collar before t_harm)
   overlap (gth-alarm-on.md, the 99 %) = an alarm span overlaps [t0, t1] at any time
   held from earlier: span started before the collar; the episode whose collar holds that start is the
   "earlier episode", gap = this t0 - its t1.
B. Time coverage per flow over [warm-up, duration] (sub-ctrl excluded; it carries no video):
   episode time = union of forward [t0, t1]; collar time = union of collars; gray = gray intervals outside collars.
   Random alarm (uniform in time, independent of the queue): P(in a collar) = collar / T;
   precision under the gtq_score rule (gray ignored) = collar / (T - gray outside collars).
   Two baselines: uniform over all flow time (pooled), and weighted by the detector's own alarms per flow
   (same number of alarms per flow, placed at random).
C. Merged events: forward episodes of a flow joined when the gap t0_next - t1_prev < G (M: 0.5, 1, 2 s);
   a merged event is harmful if any member is; its collar = [first t0 - W, last t1 + d_obs + W]; recall =
   an alarm start in that collar. Shows how much of the per-episode miss is fragmentation of one queue period.
"""

from __future__ import annotations

import json
import math
import sys
import zlib
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
CACHE = HERE / "harm-rows.jsonl"
DETS = {"v2-owd": ("v2", "OWD"), "v2-fixed-owd": ("v2-fixed", "OWD")}
GAPS = (0.5, 1.0, 2.0)   # (M) merge gaps for C
N_SHIFT = 20             # (M) random circular shifts per flow for D


def _f(v):
    return float(v) if v not in ("", None) else math.nan


def union(iv):
    out = []
    for a, b in sorted(iv):
        if b <= a:
            continue
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def length(iv):
    return sum(b - a for a, b in iv)


def minus(iv, cut):
    """iv minus cut (both unions)."""
    out = []
    for a, b in iv:
        cur = a
        for c, d in cut:
            if d <= cur or c >= b:
                continue
            if c > cur:
                out.append([cur, c])
            cur = max(cur, d)
        if cur < b:
            out.append([cur, b])
    return out


def clip(iv, lo, hi):
    return [[max(a, lo), min(b, hi)] for a, b in iv if min(b, hi) > max(a, lo)]


def one(rd: str):
    import det_eval as d
    import gtq_score
    import shadow_v2_frozen as fz
    rd = Path(rd)
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    eps = d.rows(rd / "truth" / "gtq.csv")
    gray = d.rows(rd / "truth" / "gtq-gray.csv") if (rd / "truth" / "gtq-gray.csv").exists() else []
    spans = {name: fz.episodes(run, det, mode=mode, hold=True) for name, (det, mode) in DETS.items()}
    lo_t, hi_t = d.WARMUP_S, run.duration
    out = {"run": rd.name, "aqm": plan["aqm"], "rep": plan["rep"], "block": plan["block"], "type": plan["type"],
           "harm": [], "cov": [], "merged": []}
    for sid in run.subs:
        fwd = sorted((e for e in eps if e["flow"] == sid and e["direction"] == "forward"), key=lambda e: float(e["t0"]))
        gr = union([(float(g["t_start"]), float(g["t_end"])) for g in gray if g["flow"] == sid and g["direction"] == "forward"])
        W = min((float(e["W_ms"]) / 1e3 for e in fwd), default=0.1)
        col = []
        for e in fwd:
            Wi, dob = float(e["W_ms"]) / 1e3, _f(e["d_obs_ms"]) / 1e3
            col.append((float(e["t0"]) - Wi, float(e["t1"]) + (0 if math.isnan(dob) else dob) + Wi))
        if sid != "sub-ctrl":
            T = hi_t - lo_t
            cu = clip(union(col), lo_t, hi_t)
            epu = clip(union([(float(e["t0"]), float(e["t1"])) for e in fwd]), lo_t, hi_t)
            gout = minus(clip(gr, lo_t, hi_t), cu)
            al = {n: gtq_score.merge_alarms([a for a, _, _ in spans[n].get(sid, []) if a >= lo_t], W) for n in DETS}
            on_t = {n: length(clip(union([(a, b) for a, b, _ in spans[n].get(sid, [])]), lo_t, hi_t)) for n in DETS}
            # D: baselines for "on at t_harm"
            th = [_f(e["t_harm_600"]) for e in fwd if e["harmful_600"] == "1"]
            th = [t for t in th if lo_t <= t <= hi_t]
            rng = np.random.default_rng(zlib.crc32(f"{rd.name}|{sid}".encode()))
            offs = rng.uniform(0, T, N_SHIFT)
            on_ep, shift, obs = {}, {}, {}
            for n in DETS:
                su = clip(union([(a, b) for a, b, _ in spans[n].get(sid, [])]), lo_t, hi_t)
                on_ep[n] = length(minus(epu, minus(epu, su)))
                cover = lambda t: any(a <= t <= b for a, b in su)   # noqa: E731
                obs[n] = sum(cover(t) for t in th)
                shift[n] = [sum(cover(lo_t + ((t - lo_t + o) % T)) for t in th) for o in offs]
            out["cov"].append({"flow": sid, "T": T, "ep": length(epu), "collar": length(cu), "gray_out": length(gout),
                               "n_ep": len(fwd), "n_alarm": {n: len(v) for n, v in al.items()}, "on_time": on_t,
                               "on_ep": on_ep, "n_harm": len(th), "shift": shift, "obs": obs})
        for n in DETS:
            sp = sorted((a, b) for a, b, _ in spans[n].get(sid, []))
            st = gtq_score.merge_alarms([a for a, _ in sp if a >= lo_t], W)
            for i, e in enumerate(fwd):
                if e["harmful_600"] != "1":
                    continue
                th = _f(e["t_harm_600"])
                lo, hi = col[i]
                t0, t1 = float(e["t0"]), float(e["t1"])
                inside = [t for t in st if lo <= t <= hi]
                cov = next(((a, b) for a, b in sp if a <= th <= b), None)
                r = {"det": n, "flow": sid, "t0": t0, "t1": t1, "dur": t1 - t0, "hit": bool(inside),
                     "before": bool(inside) and inside[0] < th, "overlap": any(a <= t1 and b >= t0 for a, b in sp),
                     "on": cov is not None, "lead": th - cov[0] if cov else None,
                     "in_collar": cov is not None and cov[0] >= lo, "after_harm": None, "prev_gap": None,
                     "held_before_t0": None, "span_after_harm": cov[1] - th if cov else None}
                if cov is not None and cov[0] < lo:
                    j = next((k for k in range(i - 1, -1, -1) if col[k][0] <= cov[0] <= col[k][1]), None)
                    r["held_before_t0"] = t0 - cov[0]
                    r["prev_gap"] = t0 - float(fwd[j]["t1"]) if j is not None else None
                if cov is None:
                    nxt = next((a for a, _ in sp if a > th), None)
                    r["after_harm"] = nxt - th if nxt is not None else None
                    r["late_in_collar"] = nxt is not None and nxt <= hi
                out["harm"].append(r)
            # C: merged events
            for G in GAPS:
                ev = []
                for i, e in enumerate(fwd):
                    h = e["harmful_600"] == "1"
                    if ev and float(e["t0"]) - ev[-1]["t1"] < G:
                        ev[-1]["t1"] = float(e["t1"])
                        ev[-1]["hi"] = col[i][1]
                        ev[-1]["harm"] |= h
                        ev[-1]["n"] += 1
                    else:
                        ev.append({"t1": float(e["t1"]), "lo": col[i][0], "hi": col[i][1], "harm": h, "n": 1})
                hv = [x for x in ev if x["harm"]]
                out["merged"].append({"det": n, "flow": sid, "G": G, "events": len(ev), "harm": len(hv),
                                      "hit": sum(any(x["lo"] <= t <= x["hi"] for t in st) for x in hv),
                                      "members": sum(x["n"] for x in hv)})
    return out


def load(kdir: Path):
    if CACHE.exists():
        return [json.loads(x) for x in open(CACHE) if x.strip()]
    runs = [str(p) for p in sorted(kdir.iterdir()) if p.is_dir() and p.name.startswith("v3-") and (p / "truth" / "gtq.csv").exists()]
    with ProcessPoolExecutor(12) as ex:
        res = list(ex.map(one, runs))
    with open(CACHE, "w") as fh:
        for r in res:
            fh.write(json.dumps(r) + "\n")
    return res


def q(xs, p):
    return float(np.percentile(xs, p)) if xs else math.nan


def f(x, k=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"


def main(kdir: Path):
    R = load(kdir)
    det_rows = {json.loads(x)["run"]: json.loads(x) for x in open(ROOT / "reports/v3-detector/rows.jsonl") if x.strip()}
    AQMS = ("pfifo", "codel", "fq_codel", "pie")
    print("# Harm onset, GT-Q time coverage, fq_codel GT-H\n")
    print(f"Runs with a valid GT-Q: {len(R)}. Every value: rep 1 / rep 2 unless marked. Script: reports/v3-score/harm.py.\n")

    # ---------- A ----------
    for det in DETS:
        print(f"## A. Alarm at harm onset, {det} (GT-H 600 harmful forward episodes)\n")
        print("| AQM | harmful | overlap at any time (the 99 %) | hit: start in collar (gtq_score recall) | "
              "alarm_before_harm (hit, first start before t_harm) | on at t_harm | on, span opened in collar | "
              "on, held from before the collar | off at t_harm |")
        print("|---|---|---|---|---|---|---|---|---|")
        for a in AQMS + ("all",):
            cells = []
            for rep in (1, 2):
                H = [h for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a) for h in r["harm"] if h["det"] == det]
                n = len(H)
                cells.append((n, *(sum(h[k] for h in H) / n if n else math.nan for k in ("overlap", "hit", "before", "on")),
                              sum(h["on"] and h["in_collar"] for h in H) / n if n else math.nan,
                              sum(h["on"] and not h["in_collar"] for h in H) / n if n else math.nan,
                              sum(not h["on"] for h in H) / n if n else math.nan))
            print(f"| {a} | " + " | ".join(" / ".join((str(c[i]) if i == 0 else f(c[i])) for c in cells) for i in range(8)) + " |")
        print()
        print(f"How long before harm the alarm had opened (lead = t_harm - span start, episodes on at t_harm), {det}, s:\n")
        print("| AQM | on at t_harm | lead p10 | p25 | p50 | p75 | p90 | lead < 0.2 s | 0.2-1 s | 1-5 s | > 5 s |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for a in AQMS + ("all",):
            vals = []
            for rep in (1, 2):
                L = [h["lead"] for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a) for h in r["harm"] if h["det"] == det and h["on"]]
                bins = [sum(x < 0.2 for x in L), sum(0.2 <= x < 1 for x in L), sum(1 <= x < 5 for x in L), sum(x >= 5 for x in L)]
                vals.append((len(L), *[q(L, p) for p in (10, 25, 50, 75, 90)], *[b / len(L) if L else math.nan for b in bins]))
            print(f"| {a} | " + " | ".join(" / ".join((str(v[i]) if i == 0 else f(v[i])) for v in vals) for i in range(10)) + " |")
        print()
        print(f"Episodes on at t_harm with the span opened BEFORE the collar (held from an earlier alarm), {det}:\n")
        print("| AQM | n | span start in an earlier episode's collar | gap to that episode p50 s | gap p90 s | "
              "held before t0 p50 s | p90 s | episode duration p50 s |")
        print("|---|---|---|---|---|---|---|---|")
        for a in AQMS + ("all",):
            vals = []
            for rep in (1, 2):
                H = [h for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a) for h in r["harm"]
                     if h["det"] == det and h["on"] and not h["in_collar"]]
                g = [h["prev_gap"] for h in H if h["prev_gap"] is not None]
                hb = [h["held_before_t0"] for h in H]
                vals.append((len(H), len(g) / len(H) if H else math.nan, q(g, 50), q(g, 90), q(hb, 50), q(hb, 90),
                             q([h["dur"] for h in H], 50)))
            print(f"| {a} | " + " | ".join(" / ".join((str(v[i]) if i == 0 else f(v[i])) for v in vals) for i in range(7)) + " |")
        print()
        print(f"Episodes off at t_harm, {det}: next alarm start after t_harm\n")
        print("| AQM | off at t_harm | next start inside the collar (late hit) | next start p50 s after t_harm | no later start |")
        print("|---|---|---|---|---|")
        for a in AQMS + ("all",):
            vals = []
            for rep in (1, 2):
                H = [h for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a) for h in r["harm"] if h["det"] == det and not h["on"]]
                nx = [h["after_harm"] for h in H if h["after_harm"] is not None]
                vals.append((len(H), sum(h.get("late_in_collar", False) for h in H) / len(H) if H else math.nan, q(nx, 50),
                             sum(h["after_harm"] is None for h in H)))
            print(f"| {a} | " + " | ".join(" / ".join((str(v[i]) if i in (0, 3) else f(v[i])) for v in vals) for i in range(4)) + " |")
        print()

    # ---------- B ----------
    print("## B. How much of the time GT-Q covers, and the precision of a random alarm\n")
    print("Flow time after warm-up, sub-ctrl excluded. episode = union of forward GT-Q episodes [t0, t1]; collar = union of "
          "collars [t0 - W, t1 + d_obs + W]; gray = gray intervals outside collars. Random precision (uniform) = collar / "
          "(T - gray); random precision (alarm-weighted) = the same per flow, weighted by the detector's alarms on that flow. "
          "Detector precision = gtq_score's (alarms in a collar / (those + FP)), from reports/v3-detector/rows.jsonl.\n")

    def cov_row(sel, det):
        C = [c for r in sel for c in r["cov"]]
        T = sum(c["T"] for c in C)
        if not T:
            return None
        coll, gray, ep = sum(c["collar"] for c in C), sum(c["gray_out"] for c in C), sum(c["ep"] for c in C)
        rp = coll / (T - gray) if T > gray else math.nan
        w = sum(c["n_alarm"][det] for c in C)
        rpw = sum(c["n_alarm"][det] * c["collar"] / (c["T"] - c["gray_out"]) for c in C if c["T"] > c["gray_out"]) / w if w else math.nan
        on = sum(c["on_time"][det] for c in C) / T
        tal = [t for r in sel for t in (det_rows.get(r["run"], {}).get("gtq") or {}).get("tallies", []) if t["detector"] == det]
        m, fp = sum(t["alarms_matched"] for t in tal), sum(t["fp"] for t in tal)
        eph = sum(c["n_ep"] for c in C) / (T / 60)
        return (ep / T, coll / T, gray / T, rp, rpw, m / (m + fp) if m + fp else math.nan, on, eph)

    for det in DETS:
        print(f"### {det}\n")
        print("| runs | AQM | episode share of time | collar share | gray share | random precision (uniform) | "
              "random precision (alarm-weighted) | detector precision | detector alarm-on share of time | GT-Q episodes per flow-minute |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for kind in ("calm", "stimulus", "all"):
            for a in AQMS + ("all",):
                vals = []
                for rep in (1, 2):
                    sel = [r for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a)
                           and (kind == "all" or (r["type"] == "calm") == (kind == "calm"))]
                    vals.append(cov_row(sel, det))
                if all(v is None for v in vals):
                    continue
                print(f"| {kind} | {a} | " + " | ".join(" / ".join("-" if v is None else f(v[i], 1 if i == 7 else 2) for v in vals)
                                                     for i in range(8)) + " |")
        print()

    # ---------- D ----------
    print("## D. Is 'on at t_harm' high only because the alarm is on most of the time?\n")
    print("Harmful GT-H 600 forward episodes with t_harm after warm-up, sub-ctrl excluded. on-share = alarm-on time / flow "
          "time; on-share in queue = alarm-on time inside GT-Q forward episodes / episode time (an alarm that is on "
          "exactly while a queue exists, at random inside it); shift = the flow's own alarm spans kept, harm instants moved "
          "by a random circular offset over [warm-up, duration] (20 offsets per flow, mean and min-max of the pooled share).\n")
    for det in DETS:
        print(f"### {det}\n")
        print("| runs | AQM | harmful | on at t_harm (observed) | on-share of time | on-share in queue time | shift baseline mean (min-max) |")
        print("|---|---|---|---|---|---|---|")
        for kind in ("stimulus", "all"):
            for a in AQMS + ("all",):
                vals = []
                for rep in (1, 2):
                    sel = [r for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a)
                           and (kind == "all" or r["type"] != "calm")]
                    C = [c for r in sel for c in r["cov"]]
                    nh = sum(c["n_harm"] for c in C)
                    T, ep = sum(c["T"] for c in C), sum(c["ep"] for c in C)
                    sh = np.sum([c["shift"][det] for c in C if c["n_harm"]], axis=0) / nh if nh else None
                    vals.append((nh, sum(c["obs"][det] for c in C) / nh if nh else math.nan,
                                 sum(c["on_time"][det] for c in C) / T if T else math.nan,
                                 sum(c["on_ep"][det] for c in C) / ep if ep else math.nan,
                                 f"{f(float(np.mean(sh)))} ({f(float(np.min(sh)))}-{f(float(np.max(sh)))})" if sh is not None else "-"))
                print(f"| {kind} | {a} | " + " | ".join(" / ".join(str(v[i]) if i in (0, 4) else f(v[i]) for v in vals) for i in range(5)) + " |")
        print()

    # ---------- C ----------
    print("## C. Per-episode vs merged-event GT-H 600 recall (alarm start in the collar)\n")
    print("Merged event: forward episodes of a flow with gap < G joined (M). recall = harmful merged events with an alarm start "
          "in the merged collar / harmful merged events.\n")
    for det in DETS:
        print(f"### {det}\n")
        print("| AQM | per-episode recall (harmful n) | " + " | ".join(f"G {g:g} s: recall (harmful events, episodes per event)" for g in GAPS) + " |")
        print("|---|---|" + "---|" * len(GAPS))
        for a in AQMS + ("all",):
            row = []
            H = {rep: [h for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a) for h in r["harm"] if h["det"] == det] for rep in (1, 2)}
            row.append(" / ".join(f"{f(sum(h['hit'] for h in H[rep]) / len(H[rep]) if H[rep] else math.nan)} ({len(H[rep])})" for rep in (1, 2)))
            for g in GAPS:
                cs = []
                for rep in (1, 2):
                    M = [m for r in R if r["rep"] == rep and (a == "all" or r["aqm"] == a) for m in r["merged"] if m["det"] == det and m["G"] == g]
                    hv, hit, mem = sum(m["harm"] for m in M), sum(m["hit"] for m in M), sum(m["members"] for m in M)
                    cs.append(f"{f(hit / hv if hv else math.nan)} ({hv}, {f(mem / hv if hv else math.nan, 1)})")
                row.append(" / ".join(cs))
            print(f"| {a} | " + " | ".join(row) + " |")
        print()


if __name__ == "__main__":
    main(Path(sys.argv[1]))
