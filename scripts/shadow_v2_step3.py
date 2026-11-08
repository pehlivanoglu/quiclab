#!/usr/bin/env python3
"""Shadow v2, Step 3: one CUSUM per feature (F1, F2, F3, F5), G_ref from calm runs,
operating curves against v1's single-signal variants (spec v1.0 sections 8, 10, 12).

    python3 scripts/shadow_v2_step3.py .runs/<campaign> [...]   # -> reports/detector-v2/step3.md, step3-*.csv, step3/*.png

Settings fixed by Steps 1-2 and the user's decisions: T = 33 ms, F2 W_g = 2 ticks,
F3 W_g = 30 ticks, EWMA normalization (tau 60 s) with the Step 2 floors, option (a)
for the exceedance spread (G_ref is fitted on the noisiest calm flows and nothing
else is rescaled). Per feature and tick:

    z = (x - mu) / max(sigma, floor), zc = clip(z, -4, 4), s = delta (zc - delta / 2), delta = 2
    loss: s_L = l log(p1 / p0) + (n - l) log((1 - p1) / (1 - p0)), p1 = max(0.02, 4 p0), gated by a
          positive F2 or F3 score in the last 3 ticks
    G = clip(G + s, 0, 2 G_ref); masked or no-data tick: s = 0, G held
    score = G / (2 G_ref), linear in G and never clamped (0 <= G <= 2 G_ref)
    calm tick (statistics and p0 update): unmasked, has data, score < 0.125 over the trailing 1 s
    arming: 3 s of calm ticks; before that score = 0

G_ref per feature (section 10): fitted on calm030 and calm065 of det-*-pfifo-r1 only;
lower bound = max G reached there; chosen = smallest multiple of that bound at which
the evaluator (theta_on 0.25, i.e. G = G_ref / 2, theta_off 0.125, T_clear = max(300 ms, 2 srtt)) gives
<= 0.1 false alarms per minute of CLEAR time on those runs. Everything else is held out.
ProbeRTT: both variants (G kept / G reset to 0 when probe_rtt starts) are reported.
"""

from __future__ import annotations

import math
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_step1 as s1  # noqa: E402

ROOT, OUT, T = s1.ROOT, s1.OUT, s1.T
F3_W = 30
# Step 2 rule (10 % of the median end-of-run EWMA sigma over pfifo-r1 flows), EWMA, 33 ms (F3 = W_g 30 variant).
# F4 re-derived after its unit fix (drain time was P * 8 / R with R in bytes, 8x too large): 0.0634 -> 0.0079.
FLOORS = {"F1": 0.4713, "F2": 0.6280, "F3": 0.0066, "F4": 0.0079}
FEATURES = ("F1", "F2", "F3", "F5")
VARIANTS = ("keep", "reset")  # G across probe_rtt
DELTA, Z_MAX, TAU_S, T_WARM_S, S_FREEZE, LAG_S = 2.0, 4.0, 60.0, 3.0, 0.125, 1.0
THETA_ON = 0.25  # main operating point (G = G_ref / 2); theta_off = THETA_ON / 2
THETAS = tuple(round(0.025 * k, 3) for k in range(2, 21))  # 0.05 .. 0.50
V1 = {"gradient_only": "F2", "offered_only": "F3", "backlog_only": "F3", "deficit_only": "F3", "loss_only": "F5",
      "shadow": None, "gcc": None, "bbr": None}
CALM_RUNS = ("calm030", "calm065")
# Loss scoring variants (Step 3b, user 2026-11-08): the spec's per-tick log-likelihood saturates G on a
# keyframe loss burst. "rate" = loss fraction over a trailing window, normalised like F1-F3 (EWMA z,
# clip, delta); "scale" = the spec LLR times a factor; "cap" = the spec LLR with at most N lost per tick.
LOSS = {"F5": ("llr", None), "F5 rate 100ms": ("rate", 0.1), "F5 rate 200ms": ("rate", 0.2),
        "F5 rate 300ms": ("rate", 0.3), "F5 llr x0.1": ("scale", 0.1), "F5 llr x0.3": ("scale", 0.3),
        "F5 llr cap 3": ("cap", 3)}
# Step 4 fusion variants; the loss term is "F5 rate 100ms" (Step 3b), gated by a positive F2 / F3 score.
FUSION = {"fuse a: s2+s3+sL": ("sum", ("F2", "F3")), "fuse b: cov{F2,F3}+sL": ("cov", ("F2", "F3")),
          "fuse c: max(s2,s3)+sL": ("max", ("F2", "F3")), "fuse d: s1+s2+s3+sL": ("sum", ("F1", "F2", "F3")),
          "fuse e: cov{F1,F2,F3}+sL": ("cov", ("F1", "F2", "F3"))}
for _name, _spec in FUSION.items():
    LOSS[_name] = ("fuse", _spec)
# v2-fixed: same features / CUSUM / fusion, but mu and sigma are one global constant per feature
# (pooled calm ticks of the calm pfifo-r1 runs), never learned per flow; arms at the first unmasked tick.
LOSS["fuse d fixed"] = ("fuse", FUSION["fuse d: s1+s2+s3+sL"])
FIXED = {"fuse d fixed"}
FIXED_STATS: dict[str, tuple[float, float]] = {}
# Step 5 rules (spec sections 7, 8): hold = no decay while F1 / F4 are elevated or a loss happened within
# T_clear; rebase = after T_RB of elevated-but-flat F1 with no pending growth and calm loss, the delay base
# moves up to the current level and G resets. Names are variants of fusion (d) and of its fixed-scale form.
HOLD, REBASE = set(), set()
for _base, _fixed in (("fuse d: s1+s2+s3+sL", False), ("fuse d fixed", True)):
    for _suffix, _hold, _rb in ((" +hold", True, False), (" +hold +rebase", True, True)):
        LOSS[_base + _suffix] = ("fuse", FUSION["fuse d: s1+s2+s3+sL"])
        HOLD.add(_base + _suffix) if _hold else None
        REBASE.add(_base + _suffix) if _rb else None
        FIXED.add(_base + _suffix) if _fixed else None
# Loss-gate variants (2026-11-08, user: change only the gate). The loss term s_L counts positively only when
# the gate is open (closed: only its negative part). Kinds: growth = F2 or F3 score > 0 in the last 3 ticks
# (the Step 4 gate); level = z(F1) >= 1 in the last 3 ticks (a queue is standing); level2 = z(F1) >= 2;
# either / both = growth or / and level; open = no gate; off = no loss term at all; "+cap" = additionally the
# positive loss contribution inside one excursion of G (since G last was 0) is capped at G_ref / 4, half of
# the alarm level (theta_on 0.25 = G_ref / 2), so loss alone cannot raise an alarm.
# "-holdloss" = the hold rule's "loss within T_clear" clause removed (hold then needs z(F1) or z(F4) >= 1).
GATE: dict[str, tuple[str, bool, bool]] = {}
GATE_KINDS = (("growth", False, True), ("level", False, True), ("level2", False, True), ("either", False, True),
              ("both", False, True), ("open", False, True), ("off", False, True), ("growth", True, True),
              ("level", True, True), ("either", True, True), ("growth", False, False), ("level", False, False),
              ("level", True, False))
for _base, _fixed in (("fuse d: s1+s2+s3+sL", False), ("fuse d fixed", True)):
    for _kind, _cap, _hl in GATE_KINDS:
        _name = f"{_base} +hold gate:{_kind}{'+cap' if _cap else ''}{'' if _hl else ' -holdloss'}"
        LOSS[_name] = ("fuse", FUSION["fuse d: s1+s2+s3+sL"])
        HOLD.add(_name)
        FIXED.add(_name) if _fixed else None
        GATE[_name] = (_kind, _cap, _hl)
T_RB_S = 1.0
SHRINK = 0.5  # covariance shrinkage toward the diagonal (spec section 8)
LOSS_FLOOR = 1e-3  # 0.1 % loss: numerical floor of the loss-rate sigma
# F3's rate normaliser d_k (EWMA tau 10 s of the delivered rate, from the rendition x 1.03) is updated only on
# the detector's own quiet ticks (score < S_FREEZE over the trailing 1 s), not masked, with data. The Step 1
# tick files also carry a "d" frozen on GT3 CONGESTED (a truth leak, Step 1 stand-in); CAUSAL_D = False
# reproduces it.
CAUSAL_D = True
TAU_D = 10.0
NAME = "step3"
EXTRA_CELLS: list[tuple[str, str | None, tuple[str, ...]]] = []  # (label, aqm or None, scenarios): per-cell tables
CELL_THETAS = (0.15, 0.25, 0.4, 0.5)
GREF_MULT = (1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0)


# ── per-flow CUSUM ───────────────────────────────────────────────────────

def run_cusum(df: pd.DataFrame, feature: str, g_ref: float | None, reset_probe: bool) -> dict:
    """Causal single-feature CUSUM over one flow's tick frame.
    g_ref None = fitting pass: no cap, freeze from the running max (score unknown); returns G."""
    n = len(df)
    t = df.t.to_numpy()
    masked, nodata = df.masked.to_numpy(), df.no_data.to_numpy()
    probe = df.probe_rtt.to_numpy()
    x = {f: df[f].to_numpy().copy() for f in ("F1", "F2", "F3", "F4")}
    lost, sent = df.l.to_numpy(), df.n.to_numpy()
    causal_d = CAUSAL_D and "rate" in df
    if causal_d:
        P_arr, rate_arr, v_d, a_d = df.P.to_numpy(), df.rate.to_numpy(), float(df.d0.iloc[0]), T / TAU_D
    kind, param = LOSS.get(feature, (None, None))
    fuse = param if kind == "fuse" else None
    if kind in ("rate", "fuse"):
        w = max(1, int(round((param if kind == "rate" else 0.1) / T)))
        cl, cs = np.concatenate(([0.0], np.cumsum(lost))), np.concatenate(([0.0], np.cumsum(sent)))
        idx = np.arange(1, n + 1)
        lo = np.maximum(0, idx - w)
        wl, ws = cl[idx] - cl[lo], cs[idx] - cs[lo]
        x["L"] = np.where(ws >= 1, np.minimum(wl, ws) / np.maximum(ws, 1), np.nan)
    warm = int(round(T_WARM_S / T))
    lag = int(round(LAG_S / T))
    a = T / TAU_S
    feats = ("F1", "F2", "F3", "F4") + (("L",) if kind in ("rate", "fuse") else ())
    hold_on, rebase_on = feature in HOLD, feature in REBASE
    rb_offset, rebases = 0.0, []
    rb_n = int(round(T_RB_S / T))
    last_loss_t = -math.inf
    gate_kind, gate_cap, hold_loss = GATE.get(feature, ("growth", False, True))
    cap_l = g_ref / 4 if (gate_cap and g_ref) else math.inf
    g_loss = 0.0  # positive loss contribution in the current excursion of G
    zc_now = {f: 0.0 for f in feats}
    cov_f = fuse[1] if fuse and fuse[0] == "cov" else ()
    C = np.eye(len(cov_f)) if cov_f else None  # EWMA calm covariance of zc over cov_f  # F2 / F3 always run for the loss gate
    mu = {f: 0.0 for f in feats}
    var = {f: 0.0 for f in feats}
    init = {f: [] for f in feats}
    fixed = feature in FIXED
    if fixed:
        assert FIXED_STATS, "FIXED_STATS must be set (fixed_stats()) before running a fixed variant"
        for f in feats:
            mu[f], var[f] = FIXED_STATS[f][0], FIXED_STATS[f][1] ** 2
    armed = None
    calm_count = 0
    calm_lost = calm_sent = 0.0
    G = np.zeros(n)
    S = np.zeros(n)
    zc1_hist, zc3_hist = np.full(n, np.nan), np.full(n, np.nan)
    srtt_arr = df.srtt.to_numpy() if "srtt" in df else np.full(n, np.nan)
    score = np.zeros(n)
    s_f = {f: np.zeros(n) for f in feats}
    g = 0.0
    cap = 2 * g_ref if g_ref else math.inf
    for k in range(n):
        if masked[k] or nodata[k]:
            G[k] = g
            score[k] = g / (2 * g_ref) if g_ref else 0.0
            continue
        recent_quiet = (k == 0) or (score[max(0, k - lag):k].max() < S_FREEZE) if g_ref else True
        calm = recent_quiet
        if causal_d:
            if calm:
                v_d += a_d * (rate_arr[k] - v_d)
            x["F3"][k] = (P_arr[k] - P_arr[k - F3_W]) * 8 / (v_d * F3_W * T) if k >= F3_W else np.nan
        if armed is None and fixed:
            armed = k
        if armed is None:
            if calm:
                calm_count += 1
                for f in feats:
                    if np.isfinite(x[f][k]):
                        init[f].append(x[f][k])
                calm_lost += lost[k]
                calm_sent += sent[k]
                if calm_count >= warm:
                    armed = k
                    for f in feats:
                        v = np.array(init[f])
                        mu[f], var[f] = (float(v.mean()), float(v.var())) if len(v) else (0.0, 0.0)
            G[k] = 0.0
            continue
        # scores
        for f in feats:
            sig = max(math.sqrt(max(var[f], 0.0)), FLOORS.get(f, LOSS_FLOOR))
            if np.isfinite(x[f][k]):
                zc = max(-Z_MAX, min(Z_MAX, (x[f][k] - mu[f]) / sig))
                s_f[f][k] = DELTA * (zc - DELTA / 2)
                zc_now[f] = zc
            else:
                zc_now[f] = 0.0
        zc1_hist[k], zc3_hist[k] = zc_now["F1"], zc_now["F3"]
        if kind in ("rate", "fuse"):
            j0 = max(0, k - 2)
            growth = any(s_f["F2"][j] > 0 or s_f["F3"][j] > 0 for j in range(j0, k + 1))
            z1w = zc1_hist[j0:k + 1]
            z1max = float(np.nanmax(z1w)) if np.isfinite(z1w).any() else -math.inf
            level, level2 = z1max >= DELTA / 2, z1max >= DELTA
            gate = {"growth": growth, "level": level, "level2": level2, "either": growth or level,
                    "both": growth and level, "open": True, "off": False}[gate_kind]
            s_l = s_f["L"][k]
            pos = max(0.0, s_l) if gate and gate_kind != "off" else 0.0
            if gate_cap:
                pos = min(pos, max(0.0, cap_l - g_loss))
            s_k = pos + (min(0.0, s_l) if gate_kind != "off" else 0.0)
            if kind == "fuse":
                mode, fs = fuse
                if mode == "sum":
                    s_k += sum(s_f[f][k] for f in fs)
                elif mode == "max":
                    s_k += max(s_f[f][k] for f in fs)
                else:
                    Cs = (1 - SHRINK) * C + SHRINK * np.diag(np.diag(C))
                    dv = np.full(len(fs), DELTA)
                    zv = np.array([zc_now[f] for f in fs])
                    s_k += float(dv @ np.linalg.solve(Cs, zv - DELTA / 2))
        elif kind is not None:
            # n_k is sent bytes / 1200 (an estimate), so lost can exceed it in a tick: clamp the rates.
            p0 = min(0.5, max(calm_lost / calm_sent if calm_sent else 0.0, 1e-3))
            p1 = min(0.9, max(0.02, 4 * p0))
            gate = any(s_f["F2"][j] > 0 or s_f["F3"][j] > 0 for j in range(max(0, k - 2), k + 1))
            l_k = min(lost[k], sent[k], param) if kind == "cap" else min(lost[k], sent[k])
            s_k = (l_k * math.log(p1 / p0) + (sent[k] - l_k) * math.log((1 - p1) / (1 - p0))) if gate and sent[k] > 0 else 0.0
            if kind == "scale":
                s_k *= param
        else:
            s_k = s_f[feature][k]
        if lost[k] > 0:
            last_loss_t = t[k]
        if hold_on and s_k < 0:
            t_clear = max(0.3, 2 * (srtt_arr[k] / 1000 if np.isfinite(srtt_arr[k]) else 0.0))
            if zc_now["F1"] >= DELTA / 2 or zc_now["F4"] >= DELTA / 2 or (hold_loss and t[k] - last_loss_t <= t_clear):
                s_k = 0.0
        if rebase_on and k - armed >= rb_n:
            w = slice(k - rb_n + 1, k + 1)
            z1w, z3w = zc1_hist[w], zc3_hist[w]
            f1w = x["F1"][w]
            sig1 = max(math.sqrt(max(var["F1"], 0.0)), FLOORS["F1"])
            p0_now = max(calm_lost / calm_sent if calm_sent else 0.0, 1e-3)
            sent_w, lost_w = sent[w].sum(), lost[w].sum()
            if (np.all(z1w >= DELTA / 2) and np.all(np.abs(z3w) < DELTA / 2) and np.isfinite(f1w).all()
                    and np.std(f1w) < sig1 and (sent_w == 0 or lost_w / sent_w <= 2 * p0_now)):
                shift = float(np.median(f1w))
                rb_offset += shift
                x["F1"][k + 1:] -= shift
                rebases.append((float(t[k]), shift))
                g, s_k = 0.0, 0.0
        if reset_probe and probe[k] and not probe[k - 1]:
            g = 0.0
        g = min(cap, max(0.0, g + s_k))
        if kind == "fuse":
            g_loss = 0.0 if g == 0.0 else g_loss + pos
        G[k], S[k] = g, s_k
        score[k] = g / (2 * g_ref) if g_ref else 0.0
        # statistics update on calm ticks (never for the fixed variant)
        if calm and not fixed:
            for f in feats:
                if np.isfinite(x[f][k]):
                    delta = x[f][k] - mu[f]
                    mu[f] += a * delta
                    var[f] += a * (delta * (x[f][k] - mu[f]) - var[f])
            calm_lost += lost[k]
            calm_sent += sent[k]
            if cov_f:
                zv = np.array([zc_now[f] for f in cov_f])
                C += a * (np.outer(zv, zv) - C)
    return {"G": G, "score": score, "armed": armed, "t": t, "srtt": df.srtt.to_numpy(), "rebases": rebases, "s_f": s_f}


def loss_rate(df: pd.DataFrame, window_s: float = 0.1) -> np.ndarray:
    lost, sent = df.l.to_numpy(), df.n.to_numpy()
    n, w = len(df), max(1, int(round(window_s / T)))
    cl, cs = np.concatenate(([0.0], np.cumsum(lost))), np.concatenate(([0.0], np.cumsum(sent)))
    idx = np.arange(1, n + 1)
    lo = np.maximum(0, idx - w)
    wl, ws = cl[idx] - cl[lo], cs[idx] - cs[lo]
    return np.where(ws >= 1, np.minimum(wl, ws) / np.maximum(ws, 1), np.nan)


def fixed_stats(calm_dirs: list[Path]) -> dict[str, tuple[float, float]]:
    """Pooled calm mean and std per feature over the calm ticks of the given runs (v2-fixed scale)."""
    vals = {f: [] for f in ("F1", "F2", "F3", "F4", "L")}
    for rd in calm_dirs:
        for df in load_flows(rd).values():
            m = df.calm.to_numpy()
            for f in ("F1", "F2", "F3", "F4"):
                vals[f].append(df[f].to_numpy()[m])
            vals["L"].append(loss_rate(df)[m])
    out = {}
    for f, v in vals.items():
        x = np.concatenate(v)
        x = x[np.isfinite(x)]
        out[f] = (float(x.mean()), max(float(x.std()), FLOORS.get(f, LOSS_FLOOR)))
    return out


def episodes(res: dict, theta: float) -> tuple[list[float], list[float]]:
    """(t_arrival list, t_onset list) with theta_off = theta / 2 held for T_clear."""
    score, G, t, srtt = res["score"], res["G"], res["t"], res["srtt"]
    on, arrivals, onsets, below_since = False, [], [], None
    for k in range(len(t)):
        if not on and score[k] >= theta:
            on = True
            arrivals.append(float(t[k]))
            zero = np.flatnonzero(G[:k] == 0)
            onsets.append(float(t[zero[-1]]) if len(zero) else float(t[0]))
            below_since = None
        elif on:
            if score[k] < theta / 2:
                below_since = t[k] if below_since is None else below_since
                t_clear = max(0.3, 2 * (srtt[k] / 1000 if np.isfinite(srtt[k]) else 0.0))
                if t[k] - below_since >= t_clear:
                    on = False
            else:
                below_since = None
    return arrivals, onsets


# ── workers ──────────────────────────────────────────────────────────────

def f3_of(P: np.ndarray, d_k: np.ndarray) -> np.ndarray:
    return (P - np.concatenate((np.full(F3_W, np.nan), P[:-F3_W]))) * 8 / (d_k * F3_W * T)


def d_unfrozen(df: pd.DataFrame) -> np.ndarray:
    """d_k updated on every unmasked tick with data (no score freeze): used outside run_cusum (calm-run statistics)."""
    v, a, out = float(df.d0.iloc[0]), T / TAU_D, np.empty(len(df))
    for k, (r, m, nd) in enumerate(zip(df.rate.to_numpy(), df.masked.to_numpy(), df.no_data.to_numpy())):
        if not m and not nd:
            v += a * (r - v)
        out[k] = v
    return out


def load_flows(run_dir: Path) -> dict[str, pd.DataFrame]:
    run = d.Run(run_dir)
    out = {}
    for s in run.subs:
        f = run_dir / "shadow-v2" / "ticks" / f"{s}.csv"
        if f.exists():
            df = pd.read_csv(f)
            causal = CAUSAL_D and "rate" in df
            df["F3"] = f3_of(df["P"].to_numpy(), d_unfrozen(df) if causal else df.d.to_numpy())
            out[s] = df
    return out


def fit_worker(run_dir: Path) -> dict:
    """Pass A on a calm run: per feature / variant, the max G after arming and the per-flow results."""
    flows = load_flows(run_dir)
    out = {"name": run_dir.name, "res": {}}
    for f in FEATURES:
        for v in VARIANTS:
            out["res"][(f, v)] = {s: run_cusum(df, f, None, v == "reset") for s, df in flows.items()}
    return out


def eval_worker(args) -> dict:
    run_dir, g_ref = args
    run = d.Run(run_dir)
    flows = load_flows(run_dir)
    e3, l3 = gt3.run_truth(run, gt3.Params())
    view = gt3.view_of(run, e3, l3, need_path=True)
    kf = {s: np.array([run.t_unix_us(x) for x in pd.read_csv(run.sender_file(s, "frames")).query("keyframe == 1")["send_us"]]) for s in flows}
    out = {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir), "score": {}, "kf_peak": defaultdict(list),
           "mean_score": {}, "clear_min": 0.0}
    for f in FEATURES:
        for v in VARIANTS:
            res = {s: run_cusum(df, f, g_ref[(f, v)], v == "reset") for s, df in flows.items()}
            # keyframe peak score in calm (GT3 CLEAR) periods, and mean score on the run
            for s, r in res.items():
                calm = flows[s].calm.to_numpy()
                for tk in kf[s]:
                    k0 = int(tk / T)
                    hi = k0 + int(0.5 / T)
                    if 0 <= k0 and hi < len(r["score"]) and calm[k0:hi].all():
                        out["kf_peak"][(f, v)].append(float(r["score"][k0:hi].max()))
                out["mean_score"][(f, v, s)] = float(np.mean(r["score"][r["armed"]:])) if r["armed"] is not None else float("nan")
            for th in THETAS:
                starts = {(f"{f}/{v}", s): episodes(r, th)[0] for s, r in res.items()}
                out["score"][(f, v, th)] = gt_score.score(run, view, starts, (f"{f}/{v}",))[f"{f}/{v}"]
    v1 = gt_score.alarm_starts(run, tuple(V1), grouping="none")
    out["v1"] = gt_score.score(run, view, v1, tuple(V1))
    return out


def _f(x, k=2):
    return "-" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{k}f}"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    run_dirs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists() and r.name.endswith("-r1"))
    calm_dirs = [r for r in run_dirs if r.name.split("-")[1] in CALM_RUNS and "-pfifo-" in r.name]
    if any(f in FIXED for f in FEATURES):
        FIXED_STATS.update(fixed_stats(calm_dirs))
    table = s1.table
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    L = ["# Shadow v2, Step 3: single-feature CUSUM and G_ref", "",
         f"{len(run_dirs)} r1 runs; G_ref fitted on {', '.join(r.name for r in calm_dirs)} only. T {T * 1000:g} ms, "
         f"delta {DELTA:g}, z_max {Z_MAX:g}, EWMA tau {TAU_S:g} s, floors {FLOORS}, F3 W_g {F3_W} ticks, s_freeze {S_FREEZE}. git {git}.", ""]
    if FIXED_STATS:
        L += ["Fixed (global) scale for the fixed variants, pooled calm ticks of the calm pfifo-r1 runs: "
              + ", ".join(f"{f} mu {m:.4g} sigma {sg:.4g}" for f, (m, sg) in FIXED_STATS.items()), ""]

    # ── pass A: G_ref ──
    with ProcessPoolExecutor(max_workers=12) as pool:
        fits = list(pool.map(fit_worker, calm_dirs))
    g_ref, rows = {}, []
    for f in FEATURES:
        for v in VARIANTS:
            gmax = max(float(np.max(r["G"][r["armed"]:])) for fit in fits for r in fit["res"][(f, v)].values() if r["armed"] is not None)
            chosen, fa_at = None, {}
            for m in GREF_MULT:
                cand = m * gmax if gmax > 0 else 1.0
                fa = clear = 0.0
                for fit, rd in zip(fits, calm_dirs):
                    run = d.Run(rd)
                    e3, l3 = gt3.run_truth(run, gt3.Params())
                    view = gt3.view_of(run, e3, l3, need_path=True)
                    flows = load_flows(rd)
                    starts = {}
                    for s, df in flows.items():
                        r = run_cusum(df, f, cand, v == "reset")
                        starts[("x", s)] = episodes(r, THETA_ON)[0]
                    tl = gt_score.score(run, view, starts, ("x",))["x"]
                    fa += tl["fp"]
                    clear += tl["clear_s"]
                fa_at[m] = fa / (clear / 60) if clear else float("nan")
                if chosen is None and fa_at[m] <= 0.1:
                    chosen = cand
            if chosen is None:
                chosen = GREF_MULT[-1] * gmax
            g_ref[(f, v)] = chosen
            rows.append([f, v, _f(gmax, 1), _f(chosen, 1), _f(chosen / gmax if gmax else float("nan"), 2),
                         ", ".join(f"x{m:g}: {fa_at[m]:.2f}" for m in GREF_MULT)])
    L += [f"## 1. G_ref from the calm pfifo-r1 runs (theta_on {THETA_ON})", "",
          table(["feature", "probe_rtt", "max G on calm runs", "G_ref", "G_ref / max G", "FA per min at G_ref = multiple x max G"], rows), "",
          "Theory check (independent Gaussian ticks): mean run length to a false alarm ~ e^h ticks with h = 2 theta_on G_ref "
          "in log-likelihood units: " + ", ".join(f"{f}/{v} h={2 * THETA_ON * g:.1f} -> e^h = {math.exp(2 * THETA_ON * g):.0f} ticks = {math.exp(2 * THETA_ON * g) * T / 60:.1f} min"
                                               for (f, v), g in g_ref.items() if 2 * THETA_ON * g < 40) + ". Measured spacing is in table 2.", ""]

    # ── pass B: evaluation ──
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(eval_worker, [(rd, g_ref) for rd in run_dirs]))
    pf = [r for r in res if r["aqm"] == "pfifo"]

    def pooled(rs, key):
        return gt_score.summarize([r["score"][key] for r in rs])

    def pooled_v1(rs, det):
        return gt_score.summarize([r["v1"][det] for r in rs])

    curves = []
    for label, rs in (("pfifo-r1 (freeze set)", pf), ("all r1 (held-out AQMs included)", res)):
        rows = []
        for f in FEATURES:
            for v in VARIANTS:
                for th in THETAS:
                    s = pooled(rs, (f, v, th))
                    rows.append([f, v, th, s["episodes"], _f(s["precision"]), _f(s["recall"]), _f(s["fa_per_min"]),
                                 _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0),
                                 _f(60 / (s["fa_per_min"] * T) if s["fa_per_min"] else float("nan"), 0)])
                    curves.append([label, f, v, th, s["precision"], s["recall"], s["fa_per_min"], s["late_latency_p50_ms"], s["latency_p90_ms"]])
        vrows = []
        for det in V1:
            s = pooled_v1(rs, det)
            vrows.append([det, V1[det] or "-", s["episodes"], _f(s["precision"]), _f(s["recall"]), _f(s["fa_per_min"]),
                          _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0)])
        L += [f"## 2. Operating curves, {label} (truth GT3 with a GT1 / GT2 queue on the path)", "",
              table(["feature", "probe_rtt", "theta_on", "episodes", "precision", "recall", "FA / min CLEAR", "latency p50 after t_on (ms)",
                     "latency p90", "measured ticks between FAs"], rows), "",
              "v1 single-signal variants and baselines on the same runs and truth (grouping none):", "",
              table(["detector", "v2 counterpart", "episodes", "precision", "recall", "FA / min", "latency p50", "p90"], vrows), ""]
    pd.DataFrame(curves, columns=["set", "feature", "probe_rtt", "theta", "precision", "recall", "fa_per_min", "lat_p50", "lat_p90"]).to_csv(OUT / f"{NAME}-curves.csv", index=False)

    # pass check on the freeze set: at the FA rate of the v1 counterpart, recall and latency
    rows = []
    for det, base_f in V1.items():
        if base_f is None:
            continue
        v1s = pooled_v1(pf, det)
        for f, v in ((f, v) for f in FEATURES if f == base_f or f.startswith(base_f + " ") for v in VARIANTS):
            best = None
            for th in THETAS:
                s = pooled(pf, (f, v, th))
                if s["fa_per_min"] == s["fa_per_min"] and s["fa_per_min"] <= v1s["fa_per_min"] * 1.05 and (best is None or s["recall"] > best[1]["recall"]):
                    best = (th, s)
            if best is None:
                rows.append([f, v, det, _f(v1s["fa_per_min"]), "-", "no theta reaches v1's FA rate", "-", "-", "FAIL"])
                continue
            th, s = best
            ok = s["recall"] >= v1s["recall"] - 0.02 and (s["latency_p90_ms"] <= v1s["latency_p90_ms"] or s["latency_p90_ms"] != s["latency_p90_ms"])
            rows.append([f, v, det, f"{v1s['fa_per_min']:.2f} / {v1s['recall']:.2f} / {v1s['late_latency_p50_ms']:.0f} / {v1s['latency_p90_ms']:.0f}",
                         th, f"{s['fa_per_min']:.2f} / {s['recall']:.2f} / {s['late_latency_p50_ms']:.0f} / {s['latency_p90_ms']:.0f}",
                         _f(s["recall"] - v1s["recall"]), _f((s["latency_p90_ms"] - v1s["latency_p90_ms"]) if s["latency_p90_ms"] == s["latency_p90_ms"] else float("nan"), 0),
                         "PASS" if ok else "FAIL"])
    L += ["## 3. Pass check on the freeze set: v2 feature at the v1 counterpart's false-alarm rate", "",
          table(["feature", "probe_rtt", "v1 counterpart", "v1: FA/min / recall / lat p50 / p90", "theta", "v2: FA/min / recall / lat p50 / p90",
                 "recall diff", "p90 diff (ms)", "verdict (recall >= v1 - 0.02 and p90 <= v1)"], rows), ""]

    for label, aqm, scns in EXTRA_CELLS:
        rs = [r for r in res if (aqm is None or r["aqm"] == aqm) and r["scn"] in scns]
        rows = []
        for f in FEATURES:
            for th in CELL_THETAS:
                s_ = pooled(rs, (f, "keep", th))
                rows.append([f, th, s_["episodes"], _f(s_["precision"]), _f(s_["recall"]), _f(s_["fa_per_min"]),
                             _f(s_["late_latency_p50_ms"], 0), _f(s_["latency_p90_ms"], 0)])
        for det in V1:
            s_ = pooled_v1(rs, det)
            rows.append([f"v1 {det}", "-", s_["episodes"], _f(s_["precision"]), _f(s_["recall"]), _f(s_["fa_per_min"]),
                         _f(s_["late_latency_p50_ms"], 0), _f(s_["latency_p90_ms"], 0)])
        L += [f"## 3b. Cell: {label} ({len(rs)} runs, all reps in the campaigns given)", "",
              table(["detector", "theta_on", "episodes", "precision", "recall", "FA / min", "latency p50", "p90"], rows), ""]

    # keyframe peaks and calm090 mean score
    rows = []
    for f in FEATURES:
        for v in VARIANTS:
            peaks = [x for r in pf for x in r["kf_peak"][(f, v)]]
            c90 = [r["mean_score"][k] for r in res if r["scn"] == "calm090" for k in r["mean_score"] if k[0] == f and k[1] == v]
            c65 = [r["mean_score"][k] for r in res if r["scn"] == "calm065" for k in r["mean_score"] if k[0] == f and k[1] == v]
            rows.append([f, v, len(peaks), _f(np.median(peaks)) if peaks else "-", _f(np.percentile(peaks, 99)) if peaks else "-",
                         _f(np.nanmean(c65)), _f(np.nanmean(c90)), _f(np.nanmax(c90)) if c90 else "-"])
    L += ["## 4. Keyframe peak score in calm periods (pfifo-r1) and mean score on calm runs (all r1)", "",
          table(["feature", "probe_rtt", "keyframes", "peak score p50", "p99", "mean score calm065", "mean score calm090", "max flow mean calm090"], rows), "",
          "Decision 5: a keyframe p99 above 0.5 makes the min-filter on F3 / F4 mandatory. Decision 2: calm090 shows the price of a level feature (F1).", ""]

    # plot
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    cv = pd.DataFrame(curves, columns=["set", "feature", "probe_rtt", "theta", "precision", "recall", "fa_per_min", "lat_p50", "lat_p90"])
    cv = cv[(cv.set.str.startswith("pfifo")) & (cv.probe_rtt == "keep")]
    for f in FEATURES:
        c = cv[cv.feature == f].sort_values("theta")
        axes[0].plot(c.fa_per_min, c.recall, marker=".", label=f"v2 {f}")
        axes[1].plot(c.fa_per_min, c.lat_p90, marker=".", label=f"v2 {f}")
    for det in V1:
        s = pooled_v1(pf, det)
        axes[0].plot([s["fa_per_min"]], [s["recall"]], "x", ms=8, label=f"v1 {det}")
        axes[1].plot([s["fa_per_min"]], [s["latency_p90_ms"]], "x", ms=8, label=f"v1 {det}")
    for ax, yl in zip(axes, ("recall", "latency p90 after t_on (ms)")):
        ax.set_xscale("log"); ax.set_xlabel("false alarms per minute of CLEAR time"); ax.set_ylabel(yl); ax.grid(alpha=0.3)
    axes[0].legend(fontsize=7, ncol=2)
    fig.suptitle("Step 3, pfifo-r1: single-feature CUSUM over theta_on vs v1 single-signal variants")
    fig.tight_layout(); (OUT / NAME).mkdir(exist_ok=True); fig.savefig(OUT / NAME / "curves.png", dpi=110); plt.close(fig)
    L += ["Plot: step3/curves.png.", ""]
    (OUT / f"{NAME}.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
