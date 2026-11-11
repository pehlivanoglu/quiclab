#!/usr/bin/env python3
"""Offline study (read-only, no new runs) behind the 2026-11-11 grouping rule
discussion: episode ends, in-episode agreement, the event window, events to
membership, and the noise robustness of the agreement metrics.

    python3 scripts/grouping_episode_study.py pairs   CAMPAIGN OUT/pairs.jsonl
    python3 scripts/grouping_episode_study.py summary OUT/pairs.jsonl
    python3 scripts/grouping_episode_study.py member  CAMPAIGN OUT/member.jsonl
    python3 scripts/grouping_episode_study.py member-summary OUT/member.jsonl
    python3 scripts/grouping_episode_study.py noise   CAMPAIGN OUT/noise.jsonl
    python3 scripts/grouping_episode_study.py noise-summary OUT/noise.jsonl

CAMPAIGN is a grouping campaign directory; only the development set is read
(K*, C1, M*; never the held-out N*). Source v2-owd (the primary onset source).

Delay runs: 5-ACK rolling median of the OWD queue delay (shadow-v2/v1-samples-owd)
>= 10 ms, sub-threshold gaps shorter than g merged (g = 0, 200, 300 ms); the run
that contains the alarm (or starts <= 0.5 s after it). Its start / end are the
"delay" start / end (mirror of the adapter's onset backdate).

Pair classes, per shared GT1-hit window W (>= 2 expected):
  SAME         both expected in W, W overlaps no window of another hop with a disjoint set
  SAME-conc    both expected in W, W overlaps such a window (a+b, A+C ...)
  DIFF-conc    x expected in W, y expected in W' (disjoint sets, other hop), |W.start - W'.start| <= 50 ms
  DIFF-shift   same, start difference > 50 ms (a+b@0.5, a+b@2)
  DIFF-nested  y's overlapping window also expects x (shared parent egress congested too)
  DIFF-false   y alarmed inside W but is expected in no overlapping window
In-episode metrics on a 50 ms grid over the union of the two g=200 delay runs:
Pearson r, mean absolute difference (ms), peak ratio, peak time difference.
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import json
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402

SRC = "v2-owd"
QD = 10.0
RECOV = 2.0
GAPS = (0.0, 0.2, 0.3)
NATURAL = ("tcpbbr", "tcpcubic", "ppbp")
A = 4.553876891600541   # ln((1 - beta_err) / alpha_err), grouping Config defaults


def read_jsonl(path: Path) -> list[dict]:
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return [json.loads(line) for line in fh]


def fam(aqm: str) -> str:
    return "FIFO" if aqm in ("pfifo", "red", "pie") else "fq/cake" if aqm in ("fq_codel", "cake") else aqm


def dev_runs(campaign: Path):
    for g in sorted(campaign.iterdir()):
        if not g.is_dir() or g.name[0] not in "KMC":
            continue
        for rd in sorted(g.iterdir()):
            gd = rd / f"grouping-{SRC}"
            if (gd / "metrics.json").exists():
                yield g.name, rd, gd


def base_of(group: str, rd: Path) -> dict:
    return {"group": group, "run": rd.name, "cls": "natural" if rd.name.split("-")[1] in NATURAL else "scripted",
            "fam": fam(rd.name.split("-")[-2])}


def delay_run(ts: np.ndarray, v: np.ndarray, t: float, g: float) -> tuple[float, float] | None:
    i = int(np.searchsorted(ts, t, side="right")) - 1
    if i < 0 or v[i] < QD:
        j = max(i + 1, 0)
        while j < len(ts) and ts[j] <= t + 0.5 and v[j] < QD:
            j += 1
        if j >= len(ts) or ts[j] > t + 0.5:
            return None
        i = j
    above = v >= QD
    a = i
    while True:
        while a > 0 and above[a - 1]:
            a -= 1
        k = a - 1
        while k >= 0 and not above[k] and ts[a] - ts[k] < g:
            k -= 1
        if k >= 0 and above[k] and ts[a] - ts[k] < g:
            a = k
            continue
        break
    b = i
    while True:
        while b + 1 < len(ts) and above[b + 1]:
            b += 1
        k = b + 1
        while k < len(ts) and not above[k] and ts[k] - ts[b] < g:
            k += 1
        if k < len(ts) and above[k] and ts[k] - ts[b] < g:
            b = k
            continue
        break
    return float(ts[a]), float(ts[b + 1] if b + 1 < len(ts) else ts[b])


def raw_delay(run: d.Run, rd: Path) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    out = {}
    for f in (rd / "shadow-v2" / "v1-samples-owd").glob("*.csv"):
        x = pd.read_csv(f, usecols=["mono_us", "queue_delay_ms"]).dropna()
        out[f.stem] = (np.asarray(run.t_mono_us(x.mono_us.values), float), x.queue_delay_ms.values.astype(float))
    return out


def smooth(v: np.ndarray) -> np.ndarray:
    return pd.Series(v).rolling(5, min_periods=1, center=True).median().values


def load_onsets(gd: Path):
    ons, obs = defaultdict(list), defaultdict(list)
    for line in (gd / "onsets.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["kind"] == "onset":
            ons[r["flow"]].append((r["t_arrival"], r["t_onset"]))
        elif r["kind"] == "obs":
            obs[r["flow"]].append((r["t"], r["in_episode"]))
    return ons, obs


def window_pairs(m: dict):
    """(window, conc flag, klass(x, y)) for every shared GT1-hit window."""
    wins = [b for b in m["bursts"] if b.get("hit")]

    def overl(w, u):
        return u is not w and u["start"] <= w["end"] and u["end"] >= w["start"] and u.get("hop") != w.get("hop")
    for w in wins:
        if len(w.get("expected", [])) < 2:
            continue
        exp = set(w["expected"])
        conc = any(overl(w, u) and not (exp & set(u["expected"])) for u in wins)

        def klass(x, y, w=w, exp=exp, conc=conc):
            if y in exp:
                return "SAME-conc" if conc else "SAME"
            ov = [u for u in wins if overl(w, u) and y in u["expected"]]
            if not ov:
                return "DIFF-false"
            if any(x in u["expected"] for u in ov):
                return "DIFF-nested"
            return "DIFF-conc" if min(abs(u["start"] - w["start"]) for u in ov) <= 0.05 else "DIFF-shift"
        yield w, conc, klass


def in_episode(qd: dict, a: str, b: str, lo: float, hi: float) -> dict:
    if hi - lo < 0.3:
        return {}
    grid = np.arange(lo, hi, 0.05)
    ya, yb = np.interp(grid, *qd[a]), np.interp(grid, *qd[b])
    out = {"mad_ms": float(np.mean(np.abs(ya - yb)))}
    top = max(ya.max(), yb.max())
    if ya.std() > 0 and yb.std() > 0:
        out["corr"] = float(np.corrcoef(ya, yb)[0, 1])
    if top > 0:
        out["nmad"] = out["mad_ms"] / top
        out["peak_ratio"] = float(min(ya.max(), yb.max()) / top)
    out["peak_dt"] = float(abs(grid[ya.argmax()] - grid[yb.argmax()]))
    return out


# ── pairs: ends, window, in-episode metrics ─────────────────────────────

def cmd_pairs(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd, gd in dev_runs(campaign):
        m = json.loads((gd / "metrics.json").read_text())
        if not any(len(b.get("expected", [])) >= 2 and b.get("hit") for b in m["bursts"]):
            continue
        base = base_of(group, rd)
        run = d.Run(rd)
        gt1 = pd.read_csv(rd / "truth" / "gt1.csv")
        ons, obs = load_onsets(gd)
        qd = {f: (t, smooth(v)) for f, (t, v) in raw_delay(run, rd).items()}

        def alarm_end(f, t):
            o = obs[f]
            i = bisect.bisect_right([x[0] for x in o], t)
            while i < len(o) and o[i][1]:
                i += 1
            return o[i][0] if i < len(o) else None
        for w, conc, klass in window_pairs(m):
            ep = gt1[(gt1.hop == w.get("hop")) & (gt1.start_s <= w["end"] + RECOV) & (gt1.end_s >= w["start"])]
            r_end = float(ep.end_s.max()) if len(ep) else None
            exp = set(w["expected"])
            info = {}
            for f in run.subs:
                c = [x for x in ons.get(f, []) if w["start"] <= x[0] <= w["end"] + RECOV]
                if not c:
                    continue
                t_al, t_on = c[0]
                rec = {"on": t_on, "al": t_al, "al_end": alarm_end(f, t_al)}
                if f in qd:
                    for g in GAPS:
                        dr = delay_run(*qd[f], t_al, g)
                        rec[f"ds{int(g * 1000)}"], rec[f"de{int(g * 1000)}"] = dr if dr else (None, None)
                info[f] = rec
            for f in exp & set(info):
                out.write(json.dumps({**base, "kind": "member", "conc": conc, "r_end": r_end, "flow": f,
                                      **info[f]}) + "\n")
            xs = sorted(exp & set(info))
            pairs = [(a, b) for i, a in enumerate(xs) for b in xs[i + 1:]]
            pairs += [(a, b) for a in xs for b in sorted(info) if b not in exp]
            for a, b in pairs:
                A_, B_ = info[a], info[b]
                rec = {**base, "kind": "pair", "klass": klass(a, b), "w_start": w["start"], "a": a, "b": b,
                       "d_on": abs(A_["on"] - B_["on"])}
                for k in ["al_end"] + [f"{p}{int(g * 1000)}" for p in ("ds", "de") for g in GAPS]:
                    if A_.get(k) is not None and B_.get(k) is not None:
                        rec["d_" + k] = abs(A_[k] - B_[k])
                if A_.get("ds200") is not None and B_.get("ds200") is not None:
                    rec.update(in_episode(qd, a, b, min(A_["ds200"], B_["ds200"]), max(A_["de200"], B_["de200"])))
                out.write(json.dumps(rec) + "\n")
    out.close()


def q(xs, p, s=1000):
    return round(float(np.quantile(xs, p)) * s) if xs else "-"


def qr(xs, p):
    return f"{np.quantile(xs, p):.2f}" if xs else "-"


def cmd_summary(path: Path) -> None:
    recs = read_jsonl(path)
    P, M = defaultdict(list), defaultdict(list)
    for r in recs:
        (P if r["kind"] == "pair" else M)[(r["cls"], r["fam"], r.get("klass", ""))].append(r)
    print("## A. pair spreads |dt| ms p50/p90")
    for k in sorted(P):
        rs = P[k]

        def col(f):
            v = [r[f] for r in rs if f in r]
            return f"{q(v, .5)}/{q(v, .9)}"
        print(" ".join(k), f"n={len(rs)}", "| onset", col("d_on"), "| d-start(g200)", col("d_ds200"),
              "| alarm end", col("d_al_end"), "| d-end g0", col("d_de0"), "g200", col("d_de200"), "g300", col("d_de300"))
    print("## B. in-episode (g200 runs): corr p10/p50/p90 | MAD ms p50/p90 | peak ratio p10/p50 | peak dt ms p50/p90")
    for k in sorted(P):
        rs = P[k]
        c = [r["corr"] for r in rs if "corr" in r]
        mad = [r["mad_ms"] for r in rs if "mad_ms" in r]
        pr = [r["peak_ratio"] for r in rs if r.get("peak_ratio") is not None]
        pdt = [r["peak_dt"] for r in rs if "peak_dt" in r]
        print(" ".join(k), f"n={len(c)}", "| corr", qr(c, .1), qr(c, .5), qr(c, .9), "| MAD", q(mad, .5, 1),
              q(mad, .9, 1), "| peak ratio", qr(pr, .1), qr(pr, .5), "| peak dt", q(pdt, .5), q(pdt, .9))
    print("## C. window sweep: share of pairs with start difference <= delta (onset | d-start g200)")
    for k in sorted(P):
        rs = P[k]
        on = np.array([r["d_on"] for r in rs])
        ds = np.array([r["d_ds200"] for r in rs if "d_ds200" in r])
        print(" ".join(k), f"n={len(rs)}", " ".join(
            f"{dl}ms {np.mean(on <= dl / 1000):.2f}|{(np.mean(ds <= dl / 1000) if len(ds) else 0):.2f}"
            for dl in (100, 150, 200, 300)))
    print("## D. member end minus router GT1 end, ms p10/p50/p90")
    for k in sorted(M):
        rs = [r for r in M[k] if r["r_end"] is not None]

        def lag(f):
            v = [r[f] - r["r_end"] for r in rs if r.get(f) is not None]
            return f"{q(v, .1)}/{q(v, .5)}/{q(v, .9)}"
        print(" ".join(k[:2]), f"n={len(rs)}", "| alarm end", lag("al_end"), "| d-end g0", lag("de0"),
              "g200", lag("de200"), "g300", lag("de300"))


# ── member: events to membership, from the engine's evidence log ────────

def cmd_member(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd, gd in dev_runs(campaign):
        if not (gd / "evidence.jsonl").exists():
            continue
        m = json.loads((gd / "metrics.json").read_text())
        wins = [b for b in m["bursts"] if len(b.get("expected", [])) >= 2 and b.get("hit")]
        recs = [json.loads(line) for line in (gd / "evidence.jsonl").read_text().splitlines()]
        confirm_t, firstmove = {}, {}
        for r in recs:
            if r["type"] == "tree" and r.get("op") == "confirm":
                confirm_t.setdefault(r["node"], r["t"])
            if r["type"] == "tree" and r.get("op") == "move" and r["flow"] not in firstmove:
                firstmove[r["flow"]] = r
        for f, mv in firstmove.items():
            n, t_mem = mv["to"], mv["t"]
            ev = [r for r in recs if r["type"] == "event" and f in r["members"] and r["t"] <= t_mem]
            evid = [r for r in recs if r["type"] == "evidence" and r.get("flow") == f and r["t"] <= t_mem]
            pos = [r for r in evid if r["w"] > 0 and r["node"] == n]
            neg = [r for r in evid if r["w"] < 0]
            loss, last = 0.0, None
            for r in evid:
                if r["node"] != n or r["kind"] != "cand":
                    continue
                if last is not None:
                    loss += max(0.0, last - r["L_before"])
                last = r["L_after"]
            exp_w = [w for w in wins if f in w["expected"]]
            out.write(json.dumps({
                **base_of(group, rd), "flow": f, "node": n, "t_member": t_mem,
                "t_report": max(t_mem, confirm_t[n]) if n in confirm_t else None,
                "first_win": min((w["start"] for w in exp_w), default=None),
                "n_win_before": sum(w["start"] <= t_mem for w in exp_w),
                "n_ev": len(ev), "cases": dict(Counter(r["case"] for r in ev)),
                "n_pos": len(pos), "w_pos": [round(r["w"], 3) for r in pos],
                "comps": [r.get("components", {}) for r in pos], "pos_cases": [r["case"] for r in pos],
                "n_neg": len(neg), "w_neg": round(sum(r["w"] for r in neg), 3),
                "decay_loss": round(loss, 3), "L_at_move": mv["L"]}) + "\n")
    out.close()


def dist(xs) -> str:
    c = Counter(xs)
    return " ".join(f"{k}:{c[k]}" for k in sorted(c)) + f"  (median {np.median(xs):.1f})" if xs else "-"


def cmd_member_summary(path: Path) -> None:
    R = read_jsonl(path)
    for fm in ("FIFO", "fq/cake", "mixab"):
        rs = [r for r in R if r["fam"] == fm]
        if not rs:
            continue
        comps = [c for r in rs for c in r["comps"]]
        w = [x for r in rs for x in r["w_pos"]]
        cs = Counter()
        for r in rs:
            cs.update(r["cases"])
        why = Counter("2 positive entries" if r["n_pos"] <= 2 else "negative evidence" if r["n_neg"] else
                      "decay (gap > 60 s)" if r["decay_loss"] > 0.45 else
                      "reduced weight" if any(x < 2.5 for x in r["w_pos"]) else "other" for r in rs)
        lat = [r["t_member"] - r["first_win"] for r in rs if r["first_win"] is not None]
        print(f"== {fm}: {len(rs)} (run, flow) memberships")
        print("  positive entries to membership:", dist([r["n_pos"] for r in rs]))
        print("  events taken part in:          ", dist([r["n_ev"] for r in rs]))
        print("  shared windows expected in:    ", dist([r["n_win_before"] for r in rs]))
        print("  cases of those events:", dict(cs))
        print(f"  positive weight: n={len(w)} capped={np.mean([c.get('capped', False) for c in comps]):.2f} "
              f"median={np.median(w):.2f} base median={np.median([c['base'] for c in comps]):.2f} "
              f"c_lag<1={np.mean([c.get('c_lag', 1) < 0.999 for c in comps]):.2f} "
              f"c_mag<1={np.mean([c.get('c_mag', 1) < 1 for c in comps]):.2f}  (A = {A:.2f}, cap = {0.55 * A:.2f})")
        print(f"  with negative evidence: {np.mean([r['n_neg'] > 0 for r in rs]):.2f}; "
              f"decay loss median {np.median([r['decay_loss'] for r in rs]):.2f} p90 "
              f"{np.quantile([r['decay_loss'] for r in rs], .9):.2f}")
        print("  more than two positive entries, why:", dict(why))
        print(f"  t_member - first shared window: p50 {np.median(lat):.1f} s, p90 {np.quantile(lat, .9):.1f} s")
    print("== FIFO per group: memberships | positive entries median | windows median | events median | cases")
    by = defaultdict(list)
    for r in R:
        if r["fam"] == "FIFO":
            by[r["group"]].append(r)
    for g, rs in sorted(by.items()):
        cs = Counter()
        for r in rs:
            cs.update(r["cases"])
        print(f"  {g} {len(rs)} | {np.median([r['n_pos'] for r in rs])} | {np.median([r['n_win_before'] for r in rs])}"
              f" | {np.median([r['n_ev'] for r in rs])} | {dict(cs)}")


# ── noise: robustness of corr / level difference to per-client delay jitter ─

NOISE_MS = (0, 5, 10, 20)
NOISE_KINDS = ("iid", "corr200")   # per-ACK white noise; noise low-passed with a 200 ms time constant
KEEP = ("SAME", "SAME-conc", "DIFF-conc")


def noise_series(t: np.ndarray, sigma: float, kind: str, rng: np.random.Generator) -> np.ndarray:
    z = rng.standard_normal(len(t))
    if kind == "iid" or len(t) < 2:
        return sigma * z
    out = np.empty(len(t))
    out[0] = z[0]
    dt = np.diff(t, prepend=t[0])
    for i in range(1, len(t)):
        a = np.exp(-max(dt[i], 0.0) / 0.2)
        out[i] = a * out[i - 1] + np.sqrt(1 - a * a) * z[i]
    return sigma * out


def cmd_noise(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd, gd in dev_runs(campaign):
        if fam(rd.name.split("-")[-2]) != "FIFO":
            continue
        m = json.loads((gd / "metrics.json").read_text())
        if not any(len(b.get("expected", [])) >= 2 and b.get("hit") for b in m["bursts"]):
            continue
        base = base_of(group, rd)
        run = d.Run(rd)
        ons, _ = load_onsets(gd)
        raw = raw_delay(run, rd)
        clean = {f: (t, smooth(v)) for f, (t, v) in raw.items()}
        noisy = {}
        for kind in NOISE_KINDS:
            for s in NOISE_MS:
                rng = np.random.default_rng([zlib.crc32(rd.name.encode()), s, NOISE_KINDS.index(kind)])
                noisy[(kind, s)] = {f: (t, smooth(np.maximum(v + noise_series(t, s, kind, rng), 0.0)) if s else smooth(v))
                                    for f, (t, v) in raw.items()}
        for w, conc, klass in window_pairs(m):
            exp = set(w["expected"])
            runs = {}
            for f in run.subs:
                c = [x for x in ons.get(f, []) if w["start"] <= x[0] <= w["end"] + RECOV]
                if c and f in clean:
                    dr = delay_run(*clean[f], c[0][0], 0.2)   # windows from the clean series (metric robustness only)
                    if dr:
                        runs[f] = dr
            xs = sorted(exp & set(runs))
            pairs = [(a, b) for i, a in enumerate(xs) for b in xs[i + 1:]]
            pairs += [(a, b) for a in xs for b in sorted(runs) if b not in exp]
            for a, b in pairs:
                k = klass(a, b)
                if k not in KEEP:
                    continue
                lo, hi = min(runs[a][0], runs[b][0]), max(runs[a][1], runs[b][1])
                rec = {**base, "klass": k, "a": a, "b": b}
                for (kind, s), series in noisy.items():
                    for key, v in in_episode(series, a, b, lo, hi).items():
                        if key in ("corr", "mad_ms", "nmad"):
                            rec[f"{key}|{kind}|{s}"] = v
                out.write(json.dumps(rec) + "\n")
    out.close()


def auc(pos: list[float], neg: list[float]) -> float | None:
    """P(a SAME pair scores better than a DIFF-conc pair); pos/neg already oriented
    so that larger is 'more SAME'."""
    if not pos or not neg:
        return None
    x = np.concatenate([pos, neg])
    r = pd.Series(x).rank().values
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cmd_noise_summary(path: Path) -> None:
    R = read_jsonl(path)
    same = [r for r in R if r["klass"] in ("SAME", "SAME-conc") and r["cls"] == "scripted"]
    nat = [r for r in R if r["klass"] == "SAME" and r["cls"] == "natural"]
    diff = [r for r in R if r["klass"] == "DIFF-conc"]
    print(f"FIFO pairs: SAME scripted {len(same)}, SAME natural {len(nat)}, DIFF-conc {len(diff)} "
          f"(groups {dict(Counter(r['group'] for r in diff))})")
    print("AUC SAME vs DIFF-conc (0.5 = no separation) and pass rates at thresholds fixed on the clean data")
    thr = {}
    for kind in NOISE_KINDS:
        print(f"-- noise {kind}")
        for s in NOISE_MS:
            def col(rs, key):
                return [r[f"{key}|{kind}|{s}"] for r in rs if f"{key}|{kind}|{s}" in r]
            line = [f"sigma {s:>2} ms"]
            for key, sign in (("corr", 1), ("mad_ms", -1), ("nmad", -1)):
                a_ = auc([sign * x for x in col(same, key)], [sign * x for x in col(diff, key)])
                line.append(f"AUC {key} {a_:.2f}")
            if s == 0:   # thresholds keeping 80 % of the scripted SAME pairs on clean data
                thr[kind] = {"corr": np.quantile(col(same, "corr"), .2), "nmad": np.quantile(col(same, "nmad"), .8)}
            t = thr[kind]

            def passes(rs):
                ok = [r for r in rs if f"corr|{kind}|{s}" in r and f"nmad|{kind}|{s}" in r]
                return np.mean([r[f"corr|{kind}|{s}"] >= t["corr"] for r in ok]), \
                    np.mean([r[f"nmad|{kind}|{s}"] <= t["nmad"] for r in ok]), \
                    np.mean([r[f"corr|{kind}|{s}"] >= t["corr"] and r[f"nmad|{kind}|{s}"] <= t["nmad"] for r in ok])
            ps, pn, pd_ = passes(same), passes(nat), passes(diff)
            line.append(f"| pass corr>={t['corr']:.2f}: SAME {ps[0]:.2f} nat {pn[0]:.2f} DIFF {pd_[0]:.2f}")
            line.append(f"| nMAD<={t['nmad']:.3f}: SAME {ps[1]:.2f} nat {pn[1]:.2f} DIFF {pd_[1]:.2f}")
            line.append(f"| both: SAME {ps[2]:.2f} nat {pn[2]:.2f} DIFF {pd_[2]:.2f}")
            print(" ".join(line))


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("pairs", "summary", "member", "member-summary", "noise", "noise-summary"))
    ap.add_argument("paths", nargs="+", type=Path)
    a = ap.parse_args(argv)
    if a.cmd in ("pairs", "member", "noise"):
        {"pairs": cmd_pairs, "member": cmd_member, "noise": cmd_noise}[a.cmd](a.paths[0], a.paths[1])
    else:
        {"summary": cmd_summary, "member-summary": cmd_member_summary, "noise-summary": cmd_noise_summary}[a.cmd](a.paths[0])


if __name__ == "__main__":
    main(sys.argv[1:])
