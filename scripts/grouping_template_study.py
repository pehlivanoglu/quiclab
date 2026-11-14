#!/usr/bin/env python3
"""Step 1 of the move to a template-based grouping (measurement only, read-only):
how much evidence does one congestion episode's delay curve carry about a
client's group?

    python3 scripts/grouping_template_study.py rows    CAMPAIGN OUT/rows.jsonl
    python3 scripts/grouping_template_study.py summary OUT/rows.jsonl.gz > OUT/summary.md
    python3 scripts/grouping_template_study.py plots   CAMPAIGN OUT/rows.jsonl.gz OUT/

Development set only (K*, C1, M*; never N*), single-queue AQMs only (pfifo, pie,
red). Negatives (G0) have no shared windows, so no event and no template.
Ground-truth groups (the windows' expected sets) build the templates: an upper
bound for any algorithm that has to find the groups itself.

Constants and their origin: (T) target we choose, (M) measured per client at run
time, (P) physical / derived, (FLAG) none of these.
  BIN = 5 ms                 (P) the OWD file's send-time grid
  MARGIN = 1.0 s             (FLAG) analysis interval = window +/- MARGIN; sensitivity 0.5, 2.0
  REF = ln(100) + ln(1000)   (T) 11.5 nats reference line (not a threshold)
  MAD_K = 1.4826             (P) MAD -> sigma for a normal
  N_MIN = 10 samples         (FLAG) fewest valid bins for a score (autocorrelation needs some)
  LAG_MAX = 200 ms           (T) alignment search range
  SAT = 0.10                 (FLAG) saturation: template within 10 % of its maximum
  CONC_S = 0.05 s            (FLAG) two windows start together (same rule as grouping_episode_study)
  sigma_i, base_i, n_eff     (M) per client / per event

Definitions as specified (step-1 brief, 2026-11-11):
  q_i(t) = OWD_i(t) - base_i on the 5 ms send-time grid, OWD = per-bin minimum
    (sensitivity: per-bin mean); base_i = minimum of that series before the
    analysis interval.
  template s_G = pointwise median of q_j over the expected members of G with a
    value in that bin; leave-one-out for the tested member.
  sigma_i = MAD_K x MAD of q_i over calm time; calm = outside every window of
    the run, after the warmup ("strict"). Variant "excl": also outside
    [start - MARGIN, end + 2 s] of every window (the drain after a window is not
    calm); both are written, the summary reports both.
  n_eff = n / (1 + 2 x sum of the positive-lag autocorrelations of the residual
    q_i - s, truncated at the first non-positive lag), on the valid bins in time
    order (gaps are closed up: bins without a sample are skipped).
  E(i, s) = (n_eff / n) x [sum q_i^2 - sum (q_i - s)^2] / (2 sigma_i^2) nats,
    over the bins where both q_i and s exist.
Classes (one row each):
  SAME        expected member vs its group's leave-one-out template
  QUIET       client not expected in the window nor in any window overlapping
              the analysis interval, with data, vs the full template
  CONCURRENT  member of W vs its own LOO template and vs the full template of a
              window W' on another hop, disjoint expected set, start within CONC_S
  NESTED      member of a leaf window W inside an upstream window U (W.expected a
              strict subset of U.expected, overlapping): vs the upstream-only
              template (U.expected minus W.expected); plus the one-sided
              violation mean(max(0, s - q_i)) in ms
Alignment (SAME, base config): lag in +/- LAG_MAX maximising the Pearson
correlation of q_i and its template, on the send-time grid and on a receive-time
grid (receive time = ACK row's sent_mono_us + owd_us, per-bin minimum).
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
import warnings
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402

BIN = 0.005
MARGINS = (1.0, 0.5, 2.0)
REF = math.log(100) + math.log(1000)
MAD_K = 1.4826
N_MIN = 10
LAG_MAX = 0.200
SAT = 0.10
CONC_S = 0.05
DRAIN_S = 2.0          # only for the "excl" calm variant (= det_eval.BURST_RECOVERY_S)
AQMS = ("pfifo", "pie", "red")
CONFIGS = [("base", 1.0, "min")] + [(f"margin{m:g}", m, "min") for m in MARGINS[1:]] + [("mean", 1.0, "mean")]


def read_jsonl(path: Path) -> list[dict]:
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return [json.loads(line) for line in fh]


def dev_runs(campaign: Path):
    for g in sorted(campaign.iterdir()):
        if not g.is_dir() or g.name[0] not in "KMCJ":   # J1: development study runs (never N*)
            continue
        for rd in sorted(g.iterdir()):
            if rd.is_dir() and rd.name.startswith("grp-") and rd.name.split("-")[-2] in AQMS \
                    and (rd / "grouping" / "windows.json").exists():
                yield g.name, rd


# ── series ──────────────────────────────────────────────────────────────

def owd_series(run: d.Run, sid: str) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """kind -> (t on the send-time grid, OWD ms with NaN where no packet was timed)."""
    o = pd.read_csv(run.sender_file(sid, "owd"), usecols=["bin_mono_us", "packets_timed", "owd_min_us", "owd_mean_us"])
    t = np.asarray(run.t_mono_us(o.bin_mono_us.values), float)
    timed = o.packets_timed.values > 0
    out = {}
    for kind, col in (("min", "owd_min_us"), ("mean", "owd_mean_us")):
        v = o[col].values.astype(float) / 1000
        v[~timed] = np.nan
        out[kind] = (t, v)
    return out


def recv_points(run: d.Run, sid: str) -> tuple[np.ndarray, np.ndarray]:
    """(receive time s, OWD ms) per ACK row with owd_us; receive = sent + OWD."""
    a = pd.read_csv(run.sender_file(sid, "acks"), usecols=["sent_mono_us", "owd_us"]).dropna()
    return (np.asarray(run.t_mono_us(a.sent_mono_us.values + a.owd_us.values), float),
            a.owd_us.values.astype(float) / 1000)


def recv_series(points: tuple[np.ndarray, np.ndarray], grid: np.ndarray) -> np.ndarray:
    """Per-bin minimum OWD on a receive-time grid (same bin edges as `grid`)."""
    tr, owd = points
    if len(tr) == 0:
        return np.full(len(grid), np.nan)
    idx = np.floor((tr - grid[0]) / BIN + 0.5).astype(int)
    ok = (idx >= 0) & (idx < len(grid))
    out = np.full(len(grid), np.inf)
    np.minimum.at(out, idx[ok], owd[ok])
    out[np.isinf(out)] = np.nan
    return out


def on_grid(t: np.ndarray, v: np.ndarray, grid: np.ndarray) -> np.ndarray:
    idx = np.floor((t - grid[0]) / BIN + 0.5).astype(int)
    out = np.full(len(grid), np.nan)
    ok = (idx >= 0) & (idx < len(grid))
    out[idx[ok]] = v[ok]
    return out


# ── scores ──────────────────────────────────────────────────────────────

def n_eff(r: np.ndarray) -> float:
    n = len(r)
    x = r - r.mean()
    den = float(x @ x)
    if n < 3 or den == 0:
        return float(n)
    s = 0.0
    for k in range(1, n):
        rho = float(x[:-k] @ x[k:]) / den
        if rho <= 0:
            break
        s += rho
    return n / (1 + 2 * s)


def evidence(q: np.ndarray, s: np.ndarray, sigma: float) -> dict | None:
    ok = ~np.isnan(q) & ~np.isnan(s)
    n = int(ok.sum())
    if n < N_MIN or not sigma > 0:
        return None
    qq, ss = q[ok], s[ok]
    r = qq - ss
    ne = n_eff(r)
    e = (ne / n) * (float(qq @ qq) - float(r @ r)) / (2 * sigma * sigma)
    return {"E": e, "n": n, "n_eff": ne, "q_mean": float(qq.mean()), "s_mean": float(ss.mean())}


def template(qs: dict[str, np.ndarray], members) -> tuple[np.ndarray, int]:
    cols = [qs[m] for m in members if m in qs and np.any(~np.isnan(qs[m]))]
    if not cols:
        return None, 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # all-NaN bins stay NaN
        return np.nanmedian(np.vstack(cols), axis=0), len(cols)


def saturation(s: np.ndarray) -> float | None:
    v = s[~np.isnan(s)]
    if len(v) == 0 or v.max() <= 0:
        return None
    return float(np.mean(v >= (1 - SAT) * v.max()))


def best_lag(q: np.ndarray, s: np.ndarray) -> float | None:
    kmax = int(round(LAG_MAX / BIN))
    best, best_k = None, None
    for k in range(-kmax, kmax + 1):
        a = q[max(0, k):len(q) + min(0, k)]
        b = s[max(0, -k):len(s) + min(0, -k)]
        ok = ~np.isnan(a) & ~np.isnan(b)
        if ok.sum() < N_MIN or a[ok].std() == 0 or b[ok].std() == 0:
            continue
        c = float(np.corrcoef(a[ok], b[ok])[0, 1])
        if best is None or c > best:
            best, best_k = c, k
    return None if best_k is None else best_k * BIN


# ── rows ────────────────────────────────────────────────────────────────

def calm_sigma(t: np.ndarray, v: np.ndarray, windows: list[dict], excl: bool) -> float:
    calm = (t >= d.WARMUP_S) & ~np.isnan(v)
    for w in windows:
        lo, hi = (w["start"] - 1.0, w["end"] + DRAIN_S) if excl else (w["start"], w["end"])
        calm &= ~((t >= lo) & (t <= hi))
    x = v[calm]
    if len(x) < N_MIN:
        return float("nan")
    return MAD_K * float(np.median(np.abs(x - np.median(x))))


def expand_windows(run: d.Run, windows: list[dict], hop_eps: dict) -> list[dict]:
    """windows.json entries; a continuous stimulus (ppbp, from_truth) is split into
    the GT1 episodes of its hop, as the grouping truth does."""
    out = []
    for w in windows:
        if w.get("from_truth"):
            out += [{**w, "start": a, "end": b} for a, b in hop_eps.get(w.get("hop"), []) if a <= w["end"] and b >= w["start"]]
        else:
            out.append(w)
    return out


def cmd_rows(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd in dev_runs(campaign):
        run = d.Run(rd)
        hop_eps = ga.gt1_hop_episodes(run)
        windows = expand_windows(run, json.loads((rd / "grouping" / "windows.json").read_text()), hop_eps)
        shared = [w for w in windows if len(w.get("expected", [])) >= 2]
        if not shared:
            continue
        rate = {s: run.topology["subscribers"][s].get("rate_kbps") for s in run.subs}
        series = {s: owd_series(run, s) for s in run.subs if run.sender_file(s, "owd").exists()}
        recv = {s: recv_points(run, s) for s in series}
        sigma = {(s, kind, excl): calm_sigma(*series[s][kind], windows, excl)
                 for s in series for kind in ("min", "mean") for excl in (False, True)}
        base_meta = {"group": group, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2]}
        for wi, w in enumerate(shared):
            exp = set(w["expected"])
            hit = ga.overlaps(hop_eps.get(w.get("hop"), []), w["start"], w["end"] + DRAIN_S)
            wmeta = {**base_meta, "w": wi, "start": w["start"], "end": w["end"], "cell": w.get("cell"),
                     "stimulus": w.get("stimulus_type"), "u": w.get("u"), "d": w.get("d"), "target": w.get("target"),
                     "hop": w.get("hop"), "concurrent": w.get("concurrent"), "gt1_hit": hit}
            for cfg, margin, kind in CONFIGS:
                lo, hi = w["start"] - margin, w["end"] + margin
                grid = np.arange(lo, hi, BIN)
                qs = {}
                for s, ser in series.items():
                    t, v = ser[kind]
                    before = v[(t < lo) & (t >= 0)]
                    if not np.any(~np.isnan(before)):
                        continue
                    qs[s] = on_grid(t, v, grid) - np.nanmin(before)
                if cfg == "base":
                    rq = {}
                    for s in series:
                        rv = recv_series(recv[s], grid)
                        t, v = series[s]["min"]
                        before = v[(t < lo) & (t >= 0)]
                        if np.any(~np.isnan(before)):
                            rq[s] = rv - np.nanmin(before)
                overl = [u for u in shared if u is not w and u["start"] <= hi and u["end"] >= lo]
                busy = set().union(*[set(u["expected"]) for u in overl]) if overl else set()
                full, full_n = template(qs, exp)
                sat_full = saturation(full) if full is not None else None

                def emit(cls, i, s, tsize, extra=None):
                    for excl in (False, True):
                        sg = sigma.get((i, kind, excl), float("nan"))
                        ev = evidence(qs[i], s, sg)
                        if ev is None:
                            continue
                        out.write(json.dumps({**wmeta, "config": cfg, "calm": "excl" if excl else "strict",
                                              "cls": cls, "client": i, "rate_kbps": rate.get(i), "tsize": tsize,
                                              "sigma_ms": sg, "sat": sat_full, "n_samples": int(np.sum(~np.isnan(qs[i]))),
                                              **ev, **(extra or {})}) + "\n")
                # SAME
                for i in sorted(exp & set(qs)):
                    s, ts = template(qs, exp - {i})
                    if s is None:
                        continue
                    extra = {}
                    if cfg == "base":
                        extra["lag_send_s"] = best_lag(qs[i], s)
                        if i in rq:
                            sr, _ = template(rq, exp - {i})
                            extra["lag_recv_s"] = best_lag(rq[i], sr) if sr is not None else None
                    emit("SAME", i, s, ts, extra)
                # QUIET
                if full is not None:
                    for i in sorted(set(qs) - exp - busy):
                        emit("QUIET", i, full, full_n)
                # CONCURRENT
                for u in overl:
                    if u.get("hop") == w.get("hop") or set(u["expected"]) & exp or abs(u["start"] - w["start"]) > CONC_S:
                        continue
                    other, on = template(qs, set(u["expected"]))
                    if other is None:
                        continue
                    for i in sorted(exp & set(qs)):
                        own, ts = template(qs, exp - {i})
                        if own is None:
                            continue
                        for excl in (False, True):
                            sg = sigma.get((i, kind, excl), float("nan"))
                            eo, ex = evidence(qs[i], own, sg), evidence(qs[i], other, sg)
                            if eo is None or ex is None:
                                continue
                            out.write(json.dumps({**wmeta, "config": cfg, "calm": "excl" if excl else "strict",
                                                  "cls": "CONCURRENT", "client": i, "rate_kbps": rate.get(i),
                                                  "tsize": ts, "tsize_other": on, "other_target": u.get("target"),
                                                  "sigma_ms": sg, "sat": sat_full, "n_samples": int(np.sum(~np.isnan(qs[i]))),
                                                  "E_own": eo["E"], "E_other": ex["E"], "diff": eo["E"] - ex["E"],
                                                  "n": eo["n"], "n_eff": eo["n_eff"]}) + "\n")
                # NESTED
                for u in overl:
                    ue = set(u["expected"])
                    if u.get("hop") == w.get("hop") or not exp < ue:
                        continue
                    up, un = template(qs, ue - exp)
                    if up is None:
                        continue
                    for i in sorted(exp & set(qs)):
                        ok = ~np.isnan(qs[i]) & ~np.isnan(up)
                        viol = float(np.mean(np.maximum(0, up[ok] - qs[i][ok]))) if ok.any() else None
                        emit("NESTED", i, up, un, {"viol_ms": viol, "up_target": u.get("target")})
    out.close()


# ── step 1b: scale-free numbers, residual sigma, noise on the curves, template size ──
#
#   python3 scripts/grouping_template_study.py rows1b    CAMPAIGN OUT/rows1b.jsonl
#   python3 scripts/grouping_template_study.py summary1b OUT/rows1b.jsonl.gz > OUT/summary1b.md
#
# Base configuration only (margin 1 s, per-bin minimum OWD). Per row and noise variant:
#   explained fraction EF = 1 - sum (q - s)^2 / sum q^2 (no sigma);
#   CONCURRENT residual ratio RMS(q - s_other) / RMS(q - s_own);
#   sigma_res (M) = MAD_K x MAD of (q_i - s_own) inside the window [start, end];
#   diff_res / diff_calm = E(own) - E(other) with sigma_res / with the calm sigma.
# Noise on the curves (every client, before the templates are rebuilt):
#   iid<k>  independent N(0, k ms) per 5 ms sample;
#   rw<k>   per-client slowly varying offset: Ornstein-Uhlenbeck random walk with
#           stationary sd k ms and time constant RW_TAU_S (FLAG), started from its
#           stationary law at the interval start.
# Template size (CONCURRENT, clean curves): own and other templates from exactly
# 1, 2, 3 randomly chosen clients of each group (own: excluding the tested client);
# a size the group cannot supply is skipped.
NOISE = [("clean", None, 0.0)] + [(f"iid{k}", "iid", float(k)) for k in (5, 10, 20)] \
    + [(f"rw{k}", "rw", float(k)) for k in (5, 10, 20)]
RW_TAU_S = 1.0          # (FLAG) time constant of the slow per-client offset


def noisy(q: np.ndarray, kind: str | None, sd: float, rng: np.random.Generator) -> np.ndarray:
    if kind is None:
        return q
    if kind == "iid":
        return q + rng.normal(0, sd, len(q))
    a = math.exp(-BIN / RW_TAU_S)
    z = rng.normal(0, 1, len(q))
    x = np.empty(len(q))
    x[0] = z[0]
    for i in range(1, len(q)):
        x[i] = a * x[i - 1] + math.sqrt(1 - a * a) * z[i]
    return q + sd * x


def ef(q: np.ndarray, s: np.ndarray) -> float | None:
    ok = ~np.isnan(q) & ~np.isnan(s)
    if ok.sum() < N_MIN:
        return None
    qq, r = q[ok], q[ok] - s[ok]
    den = float(qq @ qq)
    return 1 - float(r @ r) / den if den > 0 else None


def rms(q: np.ndarray, s: np.ndarray) -> float | None:
    ok = ~np.isnan(q) & ~np.isnan(s)
    return float(np.sqrt(np.mean((q[ok] - s[ok]) ** 2))) if ok.sum() >= N_MIN else None


def res_sigma(q: np.ndarray, s: np.ndarray, inside: np.ndarray) -> float:
    ok = ~np.isnan(q) & ~np.isnan(s) & inside
    if ok.sum() < N_MIN:
        return float("nan")
    r = q[ok] - s[ok]
    return MAD_K * float(np.median(np.abs(r - np.median(r))))


def template_lag(a: np.ndarray, b: np.ndarray) -> tuple[float | None, float | None]:
    """(best lag s, correlation at it) between two templates within +/- LAG_MAX."""
    kmax, best = int(round(LAG_MAX / BIN)), (None, None)
    for k in range(-kmax, kmax + 1):
        x = a[max(0, k):len(a) + min(0, k)]
        y = b[max(0, -k):len(b) + min(0, -k)]
        ok = ~np.isnan(x) & ~np.isnan(y)
        if ok.sum() < N_MIN or x[ok].std() == 0 or y[ok].std() == 0:
            continue
        c = float(np.corrcoef(x[ok], y[ok])[0, 1])
        if best[1] is None or c > best[1]:
            best = (k * BIN, c)
    return best


def cmd_rows1b(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd in dev_runs(campaign):
        run = d.Run(rd)
        hop_eps = ga.gt1_hop_episodes(run)
        windows = expand_windows(run, json.loads((rd / "grouping" / "windows.json").read_text()), hop_eps)
        shared = [w for w in windows if len(w.get("expected", [])) >= 2]
        if not shared:
            continue
        series = {s_: owd_series(run, s_)["min"] for s_ in run.subs if run.sender_file(s_, "owd").exists()}
        calm = {s_: calm_sigma(*series[s_], windows, False) for s_ in series}
        meta = {"group": group, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2]}
        for wi, w in enumerate(shared):
            exp = set(w["expected"])
            lo, hi = w["start"] - 1.0, w["end"] + 1.0
            grid = np.arange(lo, hi, BIN)
            inside = (grid >= w["start"]) & (grid <= w["end"])
            q0 = {}
            for s_, (t, v) in series.items():
                before = v[(t < lo) & (t >= 0)]
                if np.any(~np.isnan(before)):
                    q0[s_] = on_grid(t, v, grid) - np.nanmin(before)
            overl = [u for u in shared if u is not w and u["start"] <= hi and u["end"] >= lo]
            conc = [u for u in overl if u.get("hop") != w.get("hop") and not set(u["expected"]) & exp
                    and abs(u["start"] - w["start"]) <= CONC_S]
            nest = [u for u in overl if u.get("hop") != w.get("hop") and exp < set(u["expected"])]
            wm = {**meta, "w": wi, "start": w["start"], "cell": w.get("cell"), "stimulus": w.get("stimulus_type"),
                  "target": w.get("target")}
            seed = zlib.crc32(f"{rd.name}/{wi}".encode())
            for nname, nkind, nsd in NOISE:
                rng = np.random.default_rng([seed, NOISE.index((nname, nkind, nsd))])
                qs = {s_: noisy(q, nkind, nsd, rng) * np.where(np.isnan(q), np.nan, 1.0) for s_, q in sorted(q0.items())}
                for i in sorted(exp & set(qs)):
                    own, ts = template(qs, exp - {i})
                    if own is None:
                        continue
                    sr = res_sigma(qs[i], own, inside)
                    out.write(json.dumps({**wm, "noise": nname, "cls": "SAME", "client": i, "tsize": ts,
                                          "EF": ef(qs[i], own), "sigma_res": sr, "sigma_calm": calm.get(i)}) + "\n")
                    for u in conc:
                        other, on = template(qs, set(u["expected"]))
                        if other is None:
                            continue
                        ro, rx = rms(qs[i], own), rms(qs[i], other)
                        row = {**wm, "noise": nname, "cls": "CONCURRENT", "client": i, "other_target": u.get("target"),
                               "tsize": ts, "tsize_other": on, "EF_own": ef(qs[i], own), "EF_other": ef(qs[i], other),
                               "rms_own": ro, "rms_other": rx, "ratio": (rx / ro) if ro and rx is not None else None,
                               "sigma_res": sr, "sigma_calm": calm.get(i)}
                        for key, sg in (("diff_res", sr), ("diff_calm", calm.get(i))):
                            eo, ex = evidence(qs[i], own, sg), evidence(qs[i], other, sg)
                            row[key] = eo["E"] - ex["E"] if eo and ex else None
                        if nkind is None:
                            full, _ = template(qs, exp)
                            row["tmpl_lag_s"], row["tmpl_corr"] = template_lag(full, other)
                            row["tmpl_rms_ms"] = rms(full, other)
                            sub_rng = np.random.default_rng([seed, 99, zlib.crc32(i.encode())])
                            for k in (1, 2, 3):
                                po, px = sorted(exp - {i}), sorted(u["expected"])
                                if len(po) < k or len(px) < k:
                                    continue
                                so, _ = template(qs, set(sub_rng.choice(po, k, replace=False)))
                                sx, _ = template(qs, set(sub_rng.choice(px, k, replace=False)))
                                if so is None or sx is None:
                                    continue
                                a_, b_ = rms(qs[i], so), rms(qs[i], sx)
                                row[f"ratio_k{k}"] = (b_ / a_) if a_ and b_ is not None else None
                        out.write(json.dumps(row) + "\n")
                    for u in nest:
                        up, un = template(qs, set(u["expected"]) - exp)
                        if up is None:
                            continue
                        ok = ~np.isnan(qs[i]) & ~np.isnan(up)
                        out.write(json.dumps({**wm, "noise": nname, "cls": "NESTED", "client": i, "tsize": un,
                                              "up_target": u.get("target"), "EF": ef(qs[i], up),
                                              "viol_ms": float(np.mean(np.maximum(0, up[ok] - qs[i][ok]))) if ok.any() else None}) + "\n")
    out.close()


def cmd_summary1b(path: Path) -> None:
    R = read_jsonl(path)
    print("# Step 1b: scale-free numbers, residual sigma, noise on the curves, template size\n")
    print(f"{len({r['run'] for r in R})} runs. Rows per noise variant: "
          + ", ".join(f"{n} {sum(r['noise'] == n for r in R)}" for n, _, _ in NOISE) + ".\n")
    clean = [r for r in R if r["noise"] == "clean"]
    print("## A. Explained fraction 1 - sum (q - s)^2 / sum q^2 (clean)\n")
    print("| class | n | p10 / p50 / p90 |\n|---|---|---|")
    for lab, rows, key in (("SAME", [r for r in clean if r["cls"] == "SAME"], "EF"),
                           ("CONCURRENT own", [r for r in clean if r["cls"] == "CONCURRENT"], "EF_own"),
                           ("CONCURRENT other", [r for r in clean if r["cls"] == "CONCURRENT"], "EF_other"),
                           ("NESTED K1 a+up", [r for r in clean if r["cls"] == "NESTED" and r["group"] == "K1"], "EF"),
                           ("NESTED M6 (independent branches)", [r for r in clean if r["cls"] == "NESTED" and r["group"] == "M6"], "EF")):
        v = [r[key] for r in rows if r.get(key) is not None]
        print(f"| {lab} | {len(v)} | {q3(v, '.3f')} |")
    print("\n## A. CONCURRENT residual ratio RMS(q - s_other) / RMS(q - s_own) (clean)\n")
    print("| cell | n | p10 / p50 / p90 | < 1.2 | < 1.5 | own preferred (ratio > 1) |\n|---|---|---|---|---|---|")
    cc = [r for r in clean if r["cls"] == "CONCURRENT" and r.get("ratio") is not None]
    by = defaultdict(list)
    for r in cc:
        by[f"{r['group']} {r['cell']} {r['aqm']}"].append(r["ratio"])
    by["all"] = [r["ratio"] for r in cc]
    for k in sorted(by, key=lambda x: (x != "all", x)):
        v = by[k]
        print(f"| {k} | {len(v)} | {q3(v, '.2f')} | {np.mean(np.array(v) < 1.2):.2f} | {np.mean(np.array(v) < 1.5):.2f} "
              f"| {np.mean(np.array(v) > 1):.2f} |")
    print("\n## B. CONCURRENT E(own) - E(other) with the residual sigma vs the calm sigma (clean)\n")
    v_res = [r["diff_res"] for r in cc if r.get("diff_res") is not None]
    v_calm = [r["diff_calm"] for r in cc if r.get("diff_calm") is not None]
    print("| sigma | n | p10 / p50 / p90 nats | > 11.5 | < 2 |\n|---|---|---|---|---|")
    for lab, v in (("residual (M)", v_res), ("calm (step 1)", v_calm)):
        a = np.array(v)
        print(f"| {lab} | {len(v)} | {q3(v)} | {np.mean(a > REF):.2f} | {np.mean(a < 2):.2f} |")
    sres = [r["sigma_res"] for r in cc if r.get("sigma_res") == r.get("sigma_res")]
    scalm = [r["sigma_calm"] for r in cc if r.get("sigma_calm") is not None]
    print(f"\nsigma ms p10 / p50 / p90: residual {q3(sres, '.2f')}, calm {q3(scalm, '.2f')}\n")
    print("## C. Noise on the curves (templates rebuilt from noisy curves)\n")
    print("| noise | SAME EF p50 | CONCURRENT own preferred | ratio p10 / p50 / p90 | ratio < 1.2 | diff_res p50, > 11.5, < 2 | NESTED K1 EF p50 |")
    print("|---|---|---|---|---|---|---|")
    for n, _, _ in NOISE:
        rs = [r for r in R if r["noise"] == n]
        same = [r["EF"] for r in rs if r["cls"] == "SAME" and r.get("EF") is not None]
        c = [r for r in rs if r["cls"] == "CONCURRENT" and r.get("ratio") is not None]
        rat = [r["ratio"] for r in c]
        dr = np.array([r["diff_res"] for r in c if r.get("diff_res") is not None])
        ne = [r["EF"] for r in rs if r["cls"] == "NESTED" and r["group"] == "K1" and r.get("EF") is not None]
        print(f"| {n} | {np.median(same):.3f} | {np.mean(np.array(rat) > 1):.2f} | {q3(rat, '.2f')} "
              f"| {np.mean(np.array(rat) < 1.2):.2f} | {np.median(dr):.1f}, {np.mean(dr > REF):.2f}, {np.mean(dr < 2):.2f} "
              f"| {np.median(ne):.3f} |")
    print("\n## D. Template size (CONCURRENT, clean; own and other templates from k random clients)\n")
    print("| k | n | ratio p10 / p50 / p90 | own preferred | < 1.2 |\n|---|---|---|---|---|")
    for k in (1, 2, 3):
        v = [r[f"ratio_k{k}"] for r in cc if r.get(f"ratio_k{k}") is not None]
        if v:
            print(f"| {k} | {len(v)} | {q3(v, '.2f')} | {np.mean(np.array(v) > 1):.2f} | {np.mean(np.array(v) < 1.2):.2f} |")
        else:
            print(f"| {k} | 0 | - | - | - |")
    print("\n## E. The two branches' templates (clean, full templates, per event)\n")
    ev = {(r["run"], r["start"], r["target"]): r for r in cc}
    lag = [r["tmpl_lag_s"] * 1000 for r in ev.values() if r.get("tmpl_lag_s") is not None]
    cor = [r["tmpl_corr"] for r in ev.values() if r.get("tmpl_corr") is not None]
    rm = [r["tmpl_rms_ms"] for r in ev.values() if r.get("tmpl_rms_ms") is not None]
    print(f"- best lag between the branch templates ms p10/p50/p90 {q3(lag, '.0f')}; correlation at it {q3(cor, '.2f')}; "
          f"RMS difference ms {q3(rm, '.1f')}; {len(ev)} event sides")


def cmd_plot1b(campaign: Path, path: Path, out_dir: Path) -> None:
    """E: the two branch templates of one concurrent event (K1 a+b and K6 A+C, at the median ratio)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in read_jsonl(path) if r["noise"] == "clean" and r["cls"] == "CONCURRENT" and r.get("ratio")]
    for cell in ("a+b", "A+C"):
        rs = [r for r in rows if r["cell"] == cell and r["aqm"] == "pfifo"]
        if not rs:
            continue
        med = float(np.median([r["ratio"] for r in rs]))
        r = min(rs, key=lambda x: abs(x["ratio"] - med))
        rd = campaign / r["group"] / r["run"]
        run = d.Run(rd)
        windows = expand_windows(run, json.loads((rd / "grouping" / "windows.json").read_text()), ga.gt1_hop_episodes(run))
        shared = [w for w in windows if len(w.get("expected", [])) >= 2]
        w = shared[r["w"]]
        u = next(x for x in shared if x.get("target") == r["other_target"] and abs(x["start"] - w["start"]) <= CONC_S)
        lo, hi = w["start"] - 1.0, w["end"] + 1.0
        grid = np.arange(lo, hi, BIN)
        qs = {}
        for s_ in run.subs:
            t, v = owd_series(run, s_)["min"]
            before = v[(t < lo) & (t >= 0)]
            if np.any(~np.isnan(before)):
                qs[s_] = on_grid(t, v, grid) - np.nanmin(before)
        fig, ax = plt.subplots(figsize=(8, 3.2))
        for win, col in ((w, "C0"), (u, "C3")):
            tm, n = template(qs, set(win["expected"]))
            ax.plot(grid, tm, "-", lw=1, color=col, label=f"template {win['target']} ({', '.join(sorted(win['expected']))})")
        ax.axvspan(w["start"], w["end"], color="0.9", zorder=0)
        ax.set_title(f"{r['run']} {cell} t={w['start']:.1f}s: the two branch templates (ratio at the median {r['ratio']:.2f})",
                     fontsize=8)
        ax.set_xlabel("run time s (send-time grid)")
        ax.set_ylabel("queuing delay ms")
        ax.legend(fontsize=7)
        fig.tight_layout()
        f = out_dir / f"branches-{cell.replace('+', '')}.png"
        fig.savefig(f, dpi=120)
        plt.close(fig)
        print(f)


# ── step 1c: unknown-variance score, no sigma ──────────────────────────
#
#   python3 scripts/grouping_template_study.py rows1c    CAMPAIGN OUT/rows1c.jsonl
#   python3 scripts/grouping_template_study.py summary1c OUT/rows1c.jsonl.gz > OUT/summary1c.md
#
# CONCURRENT only (windows with a concurrent partner, K1 a+b and K6 A+C; J1 too).
#   r_x = q_i - s_x on the bins where q_i, s_own and s_other all exist, each centred
#         by subtracting its own median over those bins (a per-client, per-event
#         offset absorbs baseline error);
#   L   = n_eff x ln( RMS(r_other) / RMS(r_own) ), n_eff from the autocorrelation
#         of r_own (as in step 1);
#   ratio_c = RMS(r_other) / RMS(r_own) (centred), ratio_u = the uncentred 1b ratio.
# Every noise condition of step 1b C; template size k = 1, 2 (random subsets of the
# own group without i and of the other group) on clean curves, iid10 and rw10.
K_NOISE = ("clean", "iid10", "rw10")


def l_score(q: np.ndarray, own: np.ndarray, other: np.ndarray) -> dict | None:
    ok = ~np.isnan(q) & ~np.isnan(own) & ~np.isnan(other)
    if ok.sum() < N_MIN:
        return None
    ro, rx = q[ok] - own[ok], q[ok] - other[ok]
    ro_c, rx_c = ro - np.median(ro), rx - np.median(rx)
    a, b = float(np.sqrt(np.mean(ro_c ** 2))), float(np.sqrt(np.mean(rx_c ** 2)))
    au, bu = float(np.sqrt(np.mean(ro ** 2))), float(np.sqrt(np.mean(rx ** 2)))
    if a <= 0 or b <= 0:
        return None
    ne = n_eff(ro_c)
    return {"L": ne * math.log(b / a), "n_eff": ne, "n": int(ok.sum()), "ratio_c": b / a,
            "ratio_u": (bu / au) if au > 0 else None}


def cmd_rows1c(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd in dev_runs(campaign):
        if group not in ("K1", "K6") and not group.startswith("J"):
            continue
        run = d.Run(rd)
        hop_eps = ga.gt1_hop_episodes(run)
        windows = expand_windows(run, json.loads((rd / "grouping" / "windows.json").read_text()), hop_eps)
        shared = [w for w in windows if len(w.get("expected", [])) >= 2]
        series = {s_: owd_series(run, s_)["min"] for s_ in run.subs if run.sender_file(s_, "owd").exists()}
        meta = {"group": group, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2]}
        for wi, w in enumerate(shared):
            exp = set(w["expected"])
            lo, hi = w["start"] - 1.0, w["end"] + 1.0
            conc = [u for u in shared if u is not w and u["start"] <= hi and u["end"] >= lo and u.get("hop") != w.get("hop")
                    and not set(u["expected"]) & exp and abs(u["start"] - w["start"]) <= CONC_S]
            if not conc:
                continue
            grid = np.arange(lo, hi, BIN)
            q0 = {}
            for s_, (t, v) in series.items():
                before = v[(t < lo) & (t >= 0)]
                if np.any(~np.isnan(before)):
                    q0[s_] = on_grid(t, v, grid) - np.nanmin(before)
            seed = zlib.crc32(f"{rd.name}/{wi}".encode())
            for nname, nkind, nsd in NOISE:
                rng = np.random.default_rng([seed, NOISE.index((nname, nkind, nsd))])
                qs = {s_: noisy(q, nkind, nsd, rng) * np.where(np.isnan(q), np.nan, 1.0) for s_, q in sorted(q0.items())}
                for u in conc:
                    for i in sorted(exp & set(qs)):
                        own, ts = template(qs, exp - {i})
                        other, on = template(qs, set(u["expected"]))
                        if own is None or other is None:
                            continue
                        sc = l_score(qs[i], own, other)
                        if sc is None:
                            continue
                        row = {**meta, "w": wi, "start": w["start"], "cell": w.get("cell"), "target": w.get("target"),
                               "other_target": u.get("target"), "noise": nname, "client": i, "tsize": ts,
                               "tsize_other": on, **sc}
                        if nname in K_NOISE:
                            sub_rng = np.random.default_rng([seed, 99, zlib.crc32(i.encode())])
                            for k in (1, 2):
                                po, px = sorted(exp - {i}), sorted(u["expected"])
                                if len(po) < k or len(px) < k:
                                    continue
                                so, _ = template(qs, set(sub_rng.choice(po, k, replace=False)))
                                sx, _ = template(qs, set(sub_rng.choice(px, k, replace=False)))
                                sk = l_score(qs[i], so, sx) if so is not None and sx is not None else None
                                if sk:
                                    row[f"L_k{k}"], row[f"ratio_k{k}"] = sk["L"], sk["ratio_c"]
                        out.write(json.dumps(row) + "\n")
    out.close()


def cmd_summary1c(path: Path) -> None:
    R = read_jsonl(path)
    groups = sorted({r["group"] for r in R})
    print("# Step 1c: unknown-variance score L = n_eff x ln(RMS(r_other) / RMS(r_own)), centred residuals\n")
    print(f"{len({r['run'] for r in R})} runs ({', '.join(groups)}), CONCURRENT rows per noise condition "
          f"{sum(r['noise'] == 'clean' for r in R)}.\n")
    for scope, keep in (("all", lambda r: True),) + tuple((g, (lambda g_: lambda r: r["group"] == g_)(g)) for g in groups):
        rs = [r for r in R if keep(r)]
        if not rs:
            continue
        print(f"## {scope}\n")
        print("| noise | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p10 / p50 / p90 | ratio (centred) p50 |")
        print("|---|---|---|---|---|---|---|---|")
        for n_, _, _ in NOISE:
            v = [r for r in rs if r["noise"] == n_]
            if not v:
                continue
            L = np.array([r["L"] for r in v])
            print(f"| {n_} | {len(v)} | {q3(L)} | {np.mean(L > REF):.2f} | {np.mean(L < 2):.2f} | {np.mean(L > 0):.2f} "
                  f"| {q3([r['n_eff'] for r in v])} | {np.median([r['ratio_c'] for r in v]):.2f} |")
        print()
        print("Template size (own and other templates from k random clients):\n")
        print("| noise | k | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred |\n|---|---|---|---|---|---|---|")
        for n_ in K_NOISE:
            for k in (1, 2):
                v = np.array([r[f"L_k{k}"] for r in rs if r["noise"] == n_ and r.get(f"L_k{k}") is not None])
                if len(v):
                    print(f"| {n_} | {k} | {len(v)} | {q3(v)} | {np.mean(v > REF):.2f} | {np.mean(v < 2):.2f} | {np.mean(v > 0):.2f} |")
        print()


# ── J1: real jitter and keyframe phases (study runs) ───────────────────
#
#   python3 scripts/grouping_template_study.py rowsj1    CAMPAIGN OUT/rowsj1.jsonl
#   python3 scripts/grouping_template_study.py summaryj1 OUT/rowsj1.jsonl.gz OUT/rows1c.jsonl.gz > OUT/summaryj1.md
#   python3 scripts/grouping_template_study.py plotj1    CAMPAIGN OUT/rowsj1.jsonl.gz OUT/
#
# Runs: CAMPAIGN/J1/* and the no-jitter baseline CAMPAIGN/K1/grp-hier-pfifo-r*.
# a+b windows (CONCURRENT): member vs own leave-one-out template and the other
# branch's template; a+up windows (NESTED): member of the leaf window vs its own
# leave-one-out template ("own") and the upstream-only template (the other
# branch, "other"). Both: the step 1c score L and its centred / uncentred ratios.
# Per run: detector false alarms per minute and alarm precision (v2-owd e2e.json),
# onset spread (metrics spread_onset_ms), and the realised calm OWD spread of the
# jittered clients (MAD_K x MAD outside windows, measured).
REALISED_SD_MS = {"hierjit5": 4.0, "hierjit10": 7.1, "hierjit20": 12.6}   # probe, netem rate method
VARIANT_ORDER = ("hier", "hierjit5", "hierjit10", "hierjit20", "hiersamephase", "hierrandphase")


def j1_runs(campaign: Path):
    for rd in sorted((campaign / "K1").glob("grp-hier-pfifo-r*")):
        yield "K1", rd
    for rd in sorted((campaign / "J1").glob("grp-*")) if (campaign / "J1").exists() else []:
        if (rd / "grouping" / "windows.json").exists():
            yield "J1", rd


def cmd_rowsj1(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for group, rd in j1_runs(campaign):
        run = d.Run(rd)
        windows = json.loads((rd / "grouping" / "windows.json").read_text())
        shared = [w for w in windows if len(w.get("expected", [])) >= 2]
        series = {s_: owd_series(run, s_)["min"] for s_ in run.subs if run.sender_file(s_, "owd").exists()}
        variant = rd.name.split("-")[1]
        gd = rd / "grouping-v2-owd"
        e2e = json.loads((gd / "e2e.json").read_text()) if (gd / "e2e.json").exists() else {}
        met = json.loads((gd / "metrics.json").read_text()) if (gd / "metrics.json").exists() else {}
        calm = {s_: calm_sigma(*series[s_], windows, False) for s_ in series}
        out.write(json.dumps({"kind": "run", "group": group, "run": rd.name, "variant": variant,
                              "fa_per_min": e2e.get("false_alarms_per_min"),
                              "alarm_precision": (e2e.get("alarm_single") or {}).get("precision"),
                              "spread_onset_ms": (met.get("spread") or {}).get("spread_onset_ms"),
                              "calm_sd_ms": {k: v for k, v in calm.items()}}) + "\n")
        for wi, w in enumerate(shared):
            exp = set(w["expected"])
            lo, hi = w["start"] - 1.0, w["end"] + 1.0
            overl = [u for u in shared if u is not w and u["start"] <= hi and u["end"] >= lo and u.get("hop") != w.get("hop")]
            pairs = []
            for u in overl:
                ue = set(u["expected"])
                if not ue & exp and abs(u["start"] - w["start"]) <= CONC_S:
                    pairs.append(("CONCURRENT", u, ue))
                elif exp < ue:
                    pairs.append(("NESTED", u, ue - exp))
            if not pairs:
                continue
            grid = np.arange(lo, hi, BIN)
            qs = {}
            for s_, (t, v) in series.items():
                before = v[(t < lo) & (t >= 0)]
                if np.any(~np.isnan(before)):
                    qs[s_] = on_grid(t, v, grid) - np.nanmin(before)
            for cls, u, other_set in pairs:
                other, on = template(qs, other_set)
                for i in sorted(exp & set(qs)):
                    own, ts = template(qs, exp - {i})
                    if own is None or other is None:
                        continue
                    sc = l_score(qs[i], own, other)
                    if sc is None:
                        continue
                    out.write(json.dumps({"kind": "row", "group": group, "run": rd.name, "variant": variant,
                                          "cls": cls, "cell": w.get("cell"), "w": wi, "start": w["start"],
                                          "target": w.get("target"), "other_target": u.get("target"), "client": i,
                                          "tsize": ts, "tsize_other": on, "EF_own": ef(qs[i], own),
                                          "EF_other": ef(qs[i], other), **sc}) + "\n")
    out.close()


def vlabel(v: str) -> str:
    if v == "hier":
        return "K1 pfifo, no jitter"
    if v in REALISED_SD_MS:
        return f"jitter nominal {v[7:]} ms (realised sd {REALISED_SD_MS[v]} ms)"
    return {"hiersamephase": "same keyframe phases", "hierrandphase": "random keyframe phases"}.get(v, v)


def cmd_summaryj1(path: Path, rows1c: Path | None = None) -> None:
    R = read_jsonl(path)
    runs = [r for r in R if r["kind"] == "run"]
    rows = [r for r in R if r["kind"] == "row"]
    variants = [v for v in VARIANT_ORDER if any(r["variant"] == v for r in runs)]
    print("# J1: real per-client jitter and keyframe phases (template evidence, step 1c score)\n")
    print("Jitter: forward, on every access link a1-b3 after the shared bottleneck, netem normal law with the "
          "order-keeping `rate` method; the realised spread is lower than the nominal value (probe: 4.0 / 7.1 / 12.6 ms "
          "sd for 5 / 10 / 20 ms). Runs per variant: "
          + ", ".join(f"{vlabel(v)} {sum(r['variant'] == v for r in runs)}" for v in variants) + ".\n")
    for cls, cell in (("CONCURRENT", "a+b"), ("NESTED", "a+up")):
        print(f"## {cls} ({cell})\n")
        print("| variant | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p50 | ratio centred p50 | ratio uncentred p50 |")
        print("|---|---|---|---|---|---|---|---|---|")
        for v in variants:
            rs = [r for r in rows if r["variant"] == v and r["cls"] == cls and r["cell"] == cell]
            if not rs:
                continue
            L = np.array([r["L"] for r in rs])
            print(f"| {vlabel(v)} | {len(rs)} | {q3(L)} | {np.mean(L > REF):.2f} | {np.mean(L < 2):.2f} | {np.mean(L > 0):.2f} "
                  f"| {np.median([r['n_eff'] for r in rs]):.0f} | {np.median([r['ratio_c'] for r in rs]):.2f} "
                  f"| {np.median([r['ratio_u'] for r in rs if r.get('ratio_u')]):.2f} |")
        if cls == "CONCURRENT" and rows1c and rows1c.exists():
            inj = [r for r in read_jsonl(rows1c) if r["group"] == "K1" and r["aqm"] == "pfifo"]
            print("\nInjected noise on the K1 pfifo curves (step 1c, same cell):\n")
            print("| noise | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p50 | ratio centred p50 |")
            print("|---|---|---|---|---|---|---|---|")
            for n_, _, _ in NOISE:
                rs = [r for r in inj if r["noise"] == n_]
                if rs:
                    L = np.array([r["L"] for r in rs])
                    print(f"| {n_} | {len(rs)} | {q3(L)} | {np.mean(L > REF):.2f} | {np.mean(L < 2):.2f} | {np.mean(L > 0):.2f} "
                          f"| {np.median([r['n_eff'] for r in rs]):.0f} | {np.median([r['ratio_c'] for r in rs]):.2f} |")
        print()
    print("## Detector per variant (v2-owd; numbers only)\n")
    print("| variant | runs | false alarms / min p50 | alarm precision p50 | onset spread p50 / p90 ms (median over runs) "
          "| measured calm OWD spread ms, jittered clients p50 |")
    print("|---|---|---|---|---|---|")
    for v in variants:
        rs = [r for r in runs if r["variant"] == v]
        fa = [r["fa_per_min"] for r in rs if r.get("fa_per_min") is not None]
        pr = [r["alarm_precision"] for r in rs if r.get("alarm_precision") is not None]
        sp50 = [r["spread_onset_ms"]["p50"] for r in rs if r.get("spread_onset_ms")]
        sp90 = [r["spread_onset_ms"]["p90"] for r in rs if r.get("spread_onset_ms")]
        cs = [x for r in rs for k, x in (r.get("calm_sd_ms") or {}).items() if k != "sub-ctrl" and x == x]
        def m(x, f):
            return format(float(np.median(x)), f) if x else "-"
        print(f"| {vlabel(v)} | {len(rs)} | {m(fa, '.2f')} | {m(pr, '.2f')} | {m(sp50, '.0f')} / {m(sp90, '.0f')} "
              f"| {m(cs, '.1f')} |")


def plot_branches(campaign: Path, r: dict, out: Path, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rd = campaign / r["group"] / r["run"]
    run = d.Run(rd)
    windows = json.loads((rd / "grouping" / "windows.json").read_text())
    shared = [w for w in windows if len(w.get("expected", [])) >= 2]
    w = shared[r["w"]]
    u = next(x for x in shared if x.get("target") == r["other_target"] and abs(x["start"] - w["start"]) <= CONC_S)
    lo, hi = w["start"] - 1.0, w["end"] + 1.0
    grid = np.arange(lo, hi, BIN)
    qs = {}
    for s_ in run.subs:
        t, v = owd_series(run, s_)["min"]
        before = v[(t < lo) & (t >= 0)]
        if np.any(~np.isnan(before)):
            qs[s_] = on_grid(t, v, grid) - np.nanmin(before)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    for win, col in ((w, "C0"), (u, "C3")):
        tm, _ = template(qs, set(win["expected"]))
        ax.plot(grid, tm, "-", lw=1, color=col, label=f"template {win['target']} ({', '.join(sorted(win['expected']))})")
    ax.axvspan(w["start"], w["end"], color="0.9", zorder=0)
    ax.set_title(title, fontsize=8)
    ax.set_xlabel("run time s (send-time grid)")
    ax.set_ylabel("queuing delay ms")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(out)


def cmd_plotj1(campaign: Path, path: Path, out_dir: Path) -> None:
    rows = [r for r in read_jsonl(path) if r["kind"] == "row" and r["cls"] == "CONCURRENT"]
    for v in ("hiersamephase", "hierrandphase"):
        rs = [r for r in rows if r["variant"] == v]
        if not rs:
            continue
        med = float(np.median([r["ratio_c"] for r in rs]))
        r = min(rs, key=lambda x: abs(x["ratio_c"] - med))
        plot_branches(campaign, r, out_dir / f"j1-branches-{v}.png",
                      f"{r['run']} a+b t={r['start']:.1f}s, {vlabel(v)}: the two branch templates "
                      f"(centred ratio at the median {r['ratio_c']:.2f})")


# ── step 2 of the 2026-11-12 brief: step 1c measures on every single-queue dev run ──
#
#   python3 scripts/grouping_template_study.py rows2    CAMPAIGN OUT/rows2.jsonl
#   python3 scripts/grouping_template_study.py summary2 OUT/rows2.jsonl.gz > OUT/summary2.md
#
# Runs: K*, C1, M*, J1 on pfifo / pie / red / codel (codel and J1 were not in step 1:
# "new"). Per shared window, clean curves, base configuration:
#   SAME     member vs its own leave-one-out template; the step 1c score against a
#            flat template (the curve's own median): L_flat = n_eff x ln(RMS(q - median q)
#            / RMS(r_own centred)) (FLAG: the "other" hypothesis of 1c replaced by "no
#            shape"; same unknown-variance form). Also EF (explained fraction, own).
#   QUIET    non-congested client vs the full template: L_flat and EF (should not prefer).
#   CONCURRENT / NESTED  as in step 1c / J1 (L own vs other, EF own / other, ratios).
# Factor of a run = what its scenario varies (FACTOR below); stimulus = the window's
# stimulus_type. All runs use BBR (no Copa run exists: Copa was dropped 2026-11-03).
SINGLE_QUEUE = ("pfifo", "pie", "red", "codel")
FACTOR = {"burstcapq05": "queue depth 0.5 BDP", "burstcapq15": "queue depth 1.5 BDP", "burstcapq20": "queue depth 2 BDP",
          "burstcap": "reference (1 BDP, 25 fps, base mix)", "burstcaplowrtt": "RTT low", "burstcaphighrtt": "RTT high",
          "fps15": "frame rate 15", "fps60": "frame rate 60", "bw1": "bitrate 1 Mb/s", "bw8": "bitrate 8 Mb/s",
          "bwmix": "bitrate mix", "gapfast": "event density high (gaps 2-5 s)", "gapslow": "event density low (45-75 s)",
          "indepfast": "independent timing, mean 10 s", "indepslow": "independent timing, mean 60 s",
          "ramp": "gradual onset (ramp)", "burstlong": "long episodes (10-60 s)", "bursttiny": "tiny bursts",
          "burstudp": "UDP stimulus", "tcpcubic": "TCP cubic stimulus", "tcpbbr": "TCP BBR stimulus", "ppbp": "ppbp stimulus",
          "revjit5": "reverse jitter 5 (ACK reordering)", "revjit10": "reverse jitter 10 (ACK reordering)",
          "revjit20": "reverse jitter 20 (ACK reordering)"}


def l_flat(q: np.ndarray, own: np.ndarray) -> dict | None:
    ok = ~np.isnan(q) & ~np.isnan(own)
    if ok.sum() < N_MIN:
        return None
    r = q[ok] - own[ok]
    r = r - np.median(r)
    f = q[ok] - np.median(q[ok])
    a, b = float(np.sqrt(np.mean(r ** 2))), float(np.sqrt(np.mean(f ** 2)))
    if a <= 0 or b <= 0:
        return None
    ne = n_eff(r)
    return {"L_flat": ne * math.log(b / a), "n_eff": ne, "ratio_flat": b / a}


def cmd_rows2(campaign: Path, out_path: Path) -> None:
    out = out_path.open("w")
    for g in sorted(campaign.iterdir()):
        if not g.is_dir() or g.name[0] not in "KMCJ":
            continue
        for rd in sorted(g.glob("grp-*")):
            aqm = rd.name.split("-")[-2]
            if aqm not in SINGLE_QUEUE or not (rd / "grouping" / "windows.json").exists():
                continue
            run = d.Run(rd)
            hop_eps = ga.gt1_hop_episodes(run)
            windows = expand_windows(run, json.loads((rd / "grouping" / "windows.json").read_text()), hop_eps)
            shared = [w for w in windows if len(w.get("expected", [])) >= 2]
            if not shared:
                continue
            series = {s_: owd_series(run, s_)["min"] for s_ in run.subs if run.sender_file(s_, "owd").exists()}
            typ = rd.name.split("-")[1]
            meta = {"group": g.name, "run": rd.name, "type": typ, "aqm": aqm,
                    "new": aqm == "codel" or g.name == "J1", "factor": FACTOR.get(typ, f"{g.name} {typ}")}
            for wi, w in enumerate(shared):
                exp = set(w["expected"])
                lo, hi = w["start"] - 1.0, w["end"] + 1.0
                grid = np.arange(lo, hi, BIN)
                qs = {}
                for s_, (t, v) in series.items():
                    before = v[(t < lo) & (t >= 0)]
                    if np.any(~np.isnan(before)):
                        qs[s_] = on_grid(t, v, grid) - np.nanmin(before)
                overl = [u for u in shared if u is not w and u["start"] <= hi and u["end"] >= lo]
                busy = set().union(*[set(u["expected"]) for u in overl]) if overl else set()
                wm = {**meta, "w": wi, "cell": w.get("cell"), "stimulus": w.get("stimulus_type")}
                full, _ = template(qs, exp)
                for i in sorted(exp & set(qs)):
                    own, ts = template(qs, exp - {i})
                    if own is None:
                        continue
                    lf = l_flat(qs[i], own)
                    if lf:
                        out.write(json.dumps({**wm, "cls": "SAME", "client": i, "tsize": ts, "EF": ef(qs[i], own), **lf}) + "\n")
                    for u in overl:
                        ue = set(u["expected"])
                        if u.get("hop") == w.get("hop"):
                            continue
                        if not ue & exp and abs(u["start"] - w["start"]) <= CONC_S:
                            cls, oset = "CONCURRENT", ue
                        elif exp < ue:
                            cls, oset = "NESTED", ue - exp
                        else:
                            continue
                        other, _ = template(qs, oset)
                        sc = l_score(qs[i], own, other) if other is not None else None
                        if sc:
                            out.write(json.dumps({**wm, "cls": cls, "client": i, "tsize": ts, "EF_own": ef(qs[i], own),
                                                  "EF_other": ef(qs[i], other), **sc}) + "\n")
                if full is not None:
                    for i in sorted(set(qs) - exp - busy):
                        lf = l_flat(qs[i], full)
                        if lf:
                            out.write(json.dumps({**wm, "cls": "QUIET", "client": i, "EF": ef(qs[i], full), **lf}) + "\n")
    out.close()


def cmd_summary2(path: Path) -> None:
    R = read_jsonl(path)
    runs = {(r["group"], r["run"]) for r in R}
    print("# Step 1c measures on every single-queue development run\n")
    print(f"{len(runs)} runs ({sum(1 for g, r in runs if r.split('-')[-2] == 'codel' or g == 'J1')} new: codel and J1). "
          "All runs use BBR; no Copa run exists.\n")
    def block(rows, key, title, value, extra):
        by = defaultdict(list)
        for r in rows:
            by[key(r)].append(r)
        print(f"### {title}\n")
        print("| group | n | " + value + " p10 / p50 / p90 | > 11.5 | < 2 | prefers own | EF p50 |\n|---|---|---|---|---|---|---|")
        for k in sorted(by, key=str):
            v = np.array([r[extra] for r in by[k]])
            efk = "EF" if "EF" in by[k][0] else "EF_own"
            efv = [r[efk] for r in by[k] if r.get(efk) is not None]
            print(f"| {k} | {len(v)} | {q3(v)} | {np.mean(v > REF):.2f} | {np.mean(v < 2):.2f} | {np.mean(v > 0):.2f} "
                  f"| {np.median(efv):.3f} |")
        print()
    same = [r for r in R if r["cls"] == "SAME"]
    quiet = [r for r in R if r["cls"] == "QUIET"]
    print("## SAME (own leave-one-out template vs a flat line), all runs\n")
    block(same, lambda r: "all", "all", "L_flat", "L_flat")
    block(same, lambda r: "new (codel, J1)" if r["new"] else "covered by step 1", "new vs step 1", "L_flat", "L_flat")
    block(same, lambda r: r["factor"], "by factor", "L_flat", "L_flat")
    block(same, lambda r: r["stimulus"], "by stimulus type", "L_flat", "L_flat")
    block(same, lambda r: r["aqm"], "by AQM", "L_flat", "L_flat")
    print("## QUIET (non-congested client vs the full template, flat alternative)\n")
    block(quiet, lambda r: "all", "all", "L_flat", "L_flat")
    block(quiet, lambda r: r["aqm"], "by AQM", "L_flat", "L_flat")
    for cls in ("CONCURRENT", "NESTED"):
        rs = [r for r in R if r["cls"] == cls]
        print(f"## {cls} (L own vs other)\n")
        if not rs:
            print("none\n")
            continue
        block(rs, lambda r: f"{r['group']} {r['cell']}", "by campaign / cell", "L", "L")
        block(rs, lambda r: r["aqm"], "by AQM", "L", "L")
        new = [r for r in rs if r["new"]]
        print(f"New rows (codel, J1): {len(new)}, from " + ", ".join(
            f"{k} {n}" for k, n in sorted(Counter(f"{r['group']} {r['type']} {r['aqm']}" for r in new).items())) + "\n")


# ── summary ─────────────────────────────────────────────────────────────

def q3(v, f=".1f"):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return "-"
    p = np.quantile(v, [0.1, 0.5, 0.9])
    return " / ".join(format(x, f) for x in p)


def share(v, pred):
    v = [x for x in v if x is not None]
    return f"{np.mean([pred(x) for x in v]):.2f}" if v else "-"


def table(rows, key, value="E", extra_low=False):
    by = defaultdict(list)
    for r in rows:
        by[key(r)].append(r)
    head = "| group | n | p10 / p50 / p90 | > 11.5 |" + (" < 2 |" if extra_low else "")
    lines = [head, "|---|---|---|---|" + ("---|" if extra_low else "")]
    for k in sorted(by, key=lambda x: str(x)):
        v = [r[value] for r in by[k]]
        lines.append(f"| {k} | {len(v)} | {q3(v)} | {share(v, lambda x: x > REF)} |"
                     + (f" {share(v, lambda x: x < 2)} |" if extra_low else ""))
    return "\n".join(lines)


def bucket_ts(n):
    return "1" if n == 1 else "2" if n == 2 else "3+"


def cmd_summary(path: Path) -> None:
    R = read_jsonl(path)
    base = [r for r in R if r["config"] == "base" and r["calm"] == "strict"]
    sat_med = float(np.median([r["sat"] for r in base if r.get("sat") is not None]))
    print("# Step 1: evidence in one episode's delay curve (template study)\n")
    print(f"{len({r['run'] for r in R})} runs, {len({(r['run'], r['w']) for r in base})} shared windows, "
          f"single-queue AQMs. Reference line {REF:.1f} nats. Base config: margin 1 s, per-bin minimum OWD, "
          f"calm = strict. Saturation median split at {sat_med:.2f}.\n")
    for cls, value, low in (("SAME", "E", False), ("QUIET", "E", False), ("CONCURRENT", "diff", True), ("NESTED", "E", False)):
        rs = [r for r in base if r["cls"] == cls]
        print(f"## {cls} ({'E(own) - E(other)' if cls == 'CONCURRENT' else 'E'}, nats)\n")
        print(table(rs, lambda r: "all", value, low) + "\n")
        for name, key in (("stimulus / cell", lambda r: f"{r['stimulus']} {r['cell']}"),
                          ("u, d", lambda r: f"u={r['u']} d={r['d']}"),
                          ("AQM", lambda r: r["aqm"]), ("client bitrate kb/s", lambda r: r["rate_kbps"]),
                          ("template clients", lambda r: bucket_ts(r["tsize"])),
                          ("saturation", lambda r: "saturated" if (r.get("sat") or 0) >= sat_med else "not saturated"),
                          ("GT1 hit", lambda r: r["gt1_hit"]), ("campaign", lambda r: r["group"])):
            if rs:
                print(f"### by {name}\n\n" + table(rs, key, value, low) + "\n")
        if cls == "CONCURRENT" and rs:
            print("E(own) and E(other) separately:\n")
            print(table(rs, lambda r: "E own", "E_own") + "\n")
            print(table(rs, lambda r: "E other", "E_other") + "\n")
        if cls == "NESTED" and rs:
            print(f"One-sided violation mean(max(0, s - q_i)) ms p10/p50/p90: {q3([r['viol_ms'] for r in rs], '.2f')}\n")
    print("## Sensitivity (headline p50 and share > 11.5; CONCURRENT: diff p50, share > 11.5, share < 2)\n")
    print("| config | calm | SAME | QUIET | CONCURRENT | NESTED |\n|---|---|---|---|---|---|")
    for cfg in [c[0] for c in CONFIGS]:
        for calm in ("strict", "excl"):
            cells = []
            for cls, value in (("SAME", "E"), ("QUIET", "E"), ("CONCURRENT", "diff"), ("NESTED", "E")):
                v = [r[value] for r in R if r["config"] == cfg and r["calm"] == calm and r["cls"] == cls]
                if not v:
                    cells.append("-")
                    continue
                c = f"{np.median(v):.1f}, {np.mean(np.array(v) > REF):.2f}"
                if cls == "CONCURRENT":
                    c += f", {np.mean(np.array(v) < 2):.2f}"
                cells.append(c)
            print(f"| {cfg} | {calm} | " + " | ".join(cells) + " |")
    same = [r for r in base if r["cls"] == "SAME"]
    print("\n## Alignment (SAME, best lag in +/- 200 ms)\n")
    for k in ("lag_send_s", "lag_recv_s"):
        v = [r[k] for r in same if r.get(k) is not None]
        if v:
            c = Counter(round(x * 1000) for x in v)
            within = np.mean([abs(x) <= BIN + 1e-9 for x in v])
            print(f"- {k}: n {len(v)}, within one bin (|lag| <= 5 ms) {within:.2f}, p10/p50/p90 ms "
                  f"{q3([x * 1000 for x in v], '.0f')}; most common lags {c.most_common(5)}")
    print("\n## Sample counts\n")
    print(f"- n_eff (SAME) p10/p50/p90: {q3([r['n_eff'] for r in same])}; n: {q3([r['n'] for r in same], '.0f')}; "
          f"n_eff / n: {q3([r['n_eff'] / r['n'] for r in same], '.3f')}")
    print(f"- delay samples per client per episode (SAME): {q3([r['n_samples'] for r in same], '.0f')}")
    by_rate = defaultdict(list)
    for r in same:
        by_rate[r["rate_kbps"]].append(r["n_samples"])
    print("- by bitrate: " + ", ".join(f"{k} kb/s {q3(v, '.0f')}" for k, v in sorted(by_rate.items(), key=lambda x: str(x[0]))))
    print(f"- sigma (calm MAD) ms, strict vs excl: {q3([r['sigma_ms'] for r in same], '.2f')} vs "
          f"{q3([r['sigma_ms'] for r in R if r['config'] == 'base' and r['calm'] == 'excl' and r['cls'] == 'SAME'], '.2f')}")


# ── plots ───────────────────────────────────────────────────────────────

def pick(rows, cls, value, k):
    rs = sorted((r for r in rows if r["cls"] == cls), key=lambda r: r[value])
    if not rs:
        return []
    med = np.median([r[value] for r in rs])
    rs.sort(key=lambda r: abs(r[value] - med))
    out, seen = [], set()
    for r in rs:
        if r["run"] not in seen:
            out.append(r)
            seen.add(r["run"])
        if len(out) == k:
            break
    return out


def cmd_plots(campaign: Path, path: Path, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    R = [r for r in read_jsonl(path) if r["config"] == "base" and r["calm"] == "strict"]
    chosen = [("SAME", r) for r in pick(R, "SAME", "E", 2)] + [("CONCURRENT", r) for r in pick(R, "CONCURRENT", "diff", 2)] \
        + [("NESTED", r) for r in pick(R, "NESTED", "E", 1)]
    for idx, (cls, r) in enumerate(chosen, 1):
        rd = campaign / r["group"] / r["run"]
        run = d.Run(rd)
        windows = expand_windows(run, json.loads((rd / "grouping" / "windows.json").read_text()), ga.gt1_hop_episodes(run))
        shared = [w for w in windows if len(w.get("expected", [])) >= 2]
        w = shared[r["w"]]
        lo, hi = w["start"] - 1.0, w["end"] + 1.0
        grid = np.arange(lo, hi, BIN)
        qs = {}
        for s in run.subs:
            if not run.sender_file(s, "owd").exists():
                continue
            t, v = owd_series(run, s)["min"]
            before = v[(t < lo) & (t >= 0)]
            if np.any(~np.isnan(before)):
                qs[s] = on_grid(t, v, grid) - np.nanmin(before)
        i, exp = r["client"], set(w["expected"])
        fig, ax = plt.subplots(figsize=(8, 3.2))
        ax.plot(grid, qs[i], ".", ms=2, label=f"q {i}")
        own, _ = template(qs, exp - {i})
        if cls == "NESTED":
            up = next(u for u in shared if u.get("target") == r["up_target"] and u["start"] <= hi and u["end"] >= lo)
            s, _ = template(qs, set(up["expected"]) - exp)
            ax.plot(grid, s, "-", lw=1, label=f"upstream-only template ({r['up_target']})")
            title = f"NESTED E={r['E']:.1f} viol={r['viol_ms']:.2f} ms"
        else:
            ax.plot(grid, own, "-", lw=1, label="own LOO template")
            title = f"SAME E={r['E']:.1f}" if cls == "SAME" else ""
            if cls == "CONCURRENT":
                other = next(u for u in shared if u.get("target") == r["other_target"] and abs(u["start"] - w["start"]) <= CONC_S)
                s, _ = template(qs, set(other["expected"]))
                ax.plot(grid, s, "-", lw=1, label=f"other template ({r['other_target']})")
                title = f"CONCURRENT E_own={r['E_own']:.1f} E_other={r['E_other']:.1f} diff={r['diff']:.1f}"
        ax.axvspan(w["start"], w["end"], color="0.9", zorder=0)
        ax.set_title(f"{r['run']} {r['cell']} t={w['start']:.1f}s — {title}", fontsize=8)
        ax.set_xlabel("run time s (send-time grid)")
        ax.set_ylabel("queuing delay ms")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out_dir / f"overlay{idx}-{cls.lower()}.png", dpi=120)
        plt.close(fig)
        print(out_dir / f"overlay{idx}-{cls.lower()}.png")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("rows", "summary", "plots", "rows1b", "summary1b", "plot1b", "rows1c", "summary1c",
                                    "rowsj1", "summaryj1", "plotj1", "rows2", "summary2"))
    ap.add_argument("paths", nargs="+", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "rows":
        cmd_rows(a.paths[0], a.paths[1])
    elif a.cmd == "rows2":
        cmd_rows2(a.paths[0], a.paths[1])
    elif a.cmd == "summary2":
        cmd_summary2(a.paths[0])
    elif a.cmd == "rowsj1":
        cmd_rowsj1(a.paths[0], a.paths[1])
    elif a.cmd == "summaryj1":
        cmd_summaryj1(a.paths[0], a.paths[1] if len(a.paths) > 1 else None)
    elif a.cmd == "plotj1":
        cmd_plotj1(a.paths[0], a.paths[1], a.paths[2])
    elif a.cmd == "rows1c":
        cmd_rows1c(a.paths[0], a.paths[1])
    elif a.cmd == "summary1c":
        cmd_summary1c(a.paths[0])
    elif a.cmd == "rows1b":
        cmd_rows1b(a.paths[0], a.paths[1])
    elif a.cmd == "summary1b":
        cmd_summary1b(a.paths[0])
    elif a.cmd == "plot1b":
        cmd_plot1b(a.paths[0], a.paths[1], a.paths[2])
    elif a.cmd == "summary":
        cmd_summary(a.paths[0])
    else:
        cmd_plots(a.paths[0], a.paths[1], a.paths[2])


if __name__ == "__main__":
    main(sys.argv[1:])
