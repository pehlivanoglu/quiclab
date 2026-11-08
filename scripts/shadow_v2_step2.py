#!/usr/bin/env python3
"""Shadow v2, Step 2: tick length, F3 variants, per-flow normalization (spec v1.0 section 12).

    python3 scripts/shadow_v2_step2.py .runs/<campaign> [...]    # -> reports/detector-v2/step2.md, step2-*.csv

Decisions applied (user, 2026-11-08, after Step 1): F2 keeps W_g = 2 ticks; F3 is
swept over W_g in {2, 10, 30} ticks plus the min-filtered variant F3' (growth of
the tick's minimum pending bytes, W_g = 2), selected by AUC @200 ms together
with the keyframe response (z < 2); F1 is a score feature. Calm ticks are the
Step 1 stand-in (GT3 CLEAR, unmasked, with data, >= 1 s from any GT3 episode)
because the detector's own score does not exist yet.

Estimators, both causal and updated on calm ticks only, both initialised from
the first T_warm = 3 s of calm ticks (arming):
  (a) EWMA mean and variance, tau = 60 s
  (b) stochastic median / MAD: m += a*s*sign(x - m), mad += a*s*sign(|x - m| - mad),
      s = 1.4826 * mad, a = T / tau
z = (x - mu) / max(sigma, floor); floor = 10 % of the median end-of-run sigma over
pfifo-r1 flows (first pass), then fixed (second pass).
"""

from __future__ import annotations

import math
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import shadow_v2_step1 as s1  # noqa: E402

ROOT = s1.ROOT
OUT = s1.OUT
TICKS = (0.033, 0.050, 0.066)
F3_VARIANTS = {"F3 W_g=2": ("P", 2), "F3 W_g=10": ("P", 10), "F3 W_g=30": ("P", 30), "F3' min, W_g=2": ("P_min", 2)}
TAU_S, T_WARM_S, T_STALE_S, Z_MAX = 60.0, 3.0, 60.0, 4.0
FEATS = ("F1", "F2", "F3sel", "F4")


def load(run_dir: Path, T: float) -> dict | None:
    sub = "ticks" if abs(T - 0.033) < 1e-9 else f"ticks-{round(T * 1000)}ms"
    folder = run_dir / "shadow-v2" / sub
    run = d.Run(run_dir)
    first = folder / f"{run.subs[0]}.csv"
    if not first.exists() or "P_min" not in pd.read_csv(first, nrows=0).columns:
        s1.worker(run_dir, T)  # (re)build the tick files with the current feature set
    flows = {}
    for s in run.subs:
        f = folder / f"{s}.csv"
        if f.exists():
            df = pd.read_csv(f)
            for name, (col, w) in F3_VARIANTS.items():
                P = df[col].to_numpy()
                df[name] = (P - np.concatenate((np.full(w, np.nan), P[:-w]))) * 8 / (df.d.to_numpy() * w * T)
            flows[s] = df
    kf = {s: np.array([run.t_unix_us(x) for x in pd.read_csv(run.sender_file(s, "frames")).query("keyframe == 1")["send_us"]])
          for s in flows}
    eps = defaultdict(list)
    for e in pd.read_csv(run_dir / "truth" / "gt3.csv").itertuples() if (run_dir / "truth" / "gt3.csv").stat().st_size > 80 else []:
        eps[e.flow].append((e.t_on, e.t_end))
    rates = {s: c["rate_kbps"] * 1000 for s, c in run.topology["subscribers"].items()}
    return {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir), "flows": flows, "kf": kf,
            "eps": dict(eps), "rates": rates, "T": T}


def causal_z(x: np.ndarray, calm: np.ndarray, kind: str, T: float, floor: float):
    """Causal per-flow z; returns (z, armed_index or None, stale_flags, end_sigma)."""
    n = len(x)
    z = np.full(n, np.nan)
    stale = np.zeros(n, dtype=bool)
    a = T / TAU_S
    warm_ticks = int(round(T_WARM_S / T))
    calm_idx = np.flatnonzero(calm & np.isfinite(x))
    if len(calm_idx) < warm_ticks:
        return z, None, stale, float("nan")
    armed = int(calm_idx[warm_ticks - 1])
    init = x[calm_idx[:warm_ticks]]
    if kind == "ewma":
        mu, var = float(np.mean(init)), float(np.var(init))
    else:
        mu = float(np.median(init))
        mad = float(np.median(np.abs(init - mu)))
    last_calm = armed
    for k in range(armed, n):
        if kind == "ewma":
            sig = math.sqrt(max(var, 0.0))
        else:
            sig = 1.4826 * mad
        s_eff = max(sig, floor)
        if np.isfinite(x[k]):
            z[k] = (x[k] - mu) / s_eff
        if calm[k] and np.isfinite(x[k]):
            last_calm = k
            if kind == "ewma":
                delta = x[k] - mu
                mu += a * delta
                var += a * (delta * (x[k] - mu) - var)
            else:
                mu += a * s_eff * np.sign(x[k] - mu)
                mad += a * s_eff * np.sign(abs(x[k] - mu) - mad)
                mad = max(mad, 0.0)
        stale[k] = (k - last_calm) * T > T_STALE_S
    end_sigma = math.sqrt(max(var, 0.0)) if kind == "ewma" else 1.4826 * mad
    return z, armed, stale, end_sigma


def keyframe_peak(df: pd.DataFrame, z: np.ndarray, kf_t: np.ndarray, T: float) -> list[float]:
    calm = df.calm.to_numpy()
    out = []
    for tk in kf_t:
        k0 = int(tk / T)
        hi = k0 + int(round(0.4 / T))
        if k0 - 2 >= 0 and hi < len(df) and calm[k0 - 2:hi].all():
            seg = z[k0 - 2:hi]
            if np.isfinite(seg).any():
                out.append(float(np.nanmax(seg)))
    return out


def _flow_path(run_dir: Path, T: float, sid: str) -> Path:
    sub = "ticks" if abs(T - 0.033) < 1e-9 else f"ticks-{round(T * 1000)}ms"
    return run_dir / "shadow-v2" / sub / f"{sid}.csv"


def _with_f3(df: pd.DataFrame, T: float, f3sel: str) -> pd.DataFrame:
    col, w = F3_VARIANTS[f3sel]
    P = df[col].to_numpy()
    df["F3sel"] = (P - np.concatenate((np.full(w, np.nan), P[:-w]))) * 8 / (df.d.to_numpy() * w * T)
    return df


def end_sigmas(args) -> dict:
    run_dir, T, sid, kind, f3sel = args
    df = _with_f3(pd.read_csv(_flow_path(run_dir, T, sid)), T, f3sel)
    return {f: causal_z(df[f].to_numpy(), df.calm.to_numpy(), kind, T, 0.0)[3] for f in FEATS}


def flow_record(args) -> dict | None:
    run_dir, T, sid, kind, f3sel, floors, meta, eps = args
    df = _with_f3(pd.read_csv(_flow_path(run_dir, T, sid)), T, f3sel)
    calm, t = df.calm.to_numpy(), df.t.to_numpy()
    rec = dict(meta)
    for f in FEATS:
        z, armed, stale, _ = causal_z(df[f].to_numpy(), calm, kind, T, floors[f])
        if armed is None:
            return None
        zc = np.clip(z, -Z_MAX, Z_MAX)
        after = np.arange(len(df)) > armed
        ok = calm & after & np.isfinite(z)
        rec[f"{f} exc"] = float(np.mean(np.abs(z[ok]) > 3)) if ok.sum() > 100 else np.nan
        w3 = (t > t[armed]) & (t <= t[armed] + 3) & calm
        rec[f"{f} arm3s"] = float(np.nanmean(np.abs(zc[w3]))) if np.isfinite(zc[w3]).any() else np.nan
        post = np.zeros(len(df), dtype=bool)
        for a, b in eps:
            post |= (t > b) & (t <= b + 2)
        rec[f"{f} post2s"] = float(np.nanmean(np.abs(zc[post]))) if post.any() and np.isfinite(zc[post]).any() else np.nan
        rec[f"{f} stale"] = float(np.mean(stale[after]))
        rec["armed_at"] = float(t[armed])
    return rec


def _f(x, k=2):
    return "-" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{k}f}"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    run_dirs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists() and r.name.endswith("-r1"))
    with ProcessPoolExecutor(max_workers=12) as pool:
        data = {T: list(pool.map(load, run_dirs, [T] * len(run_dirs))) for T in TICKS}
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    table = s1.table
    L = ["# Shadow v2, Step 2: tick, F3 variant, normalization", "",
         f"{len(run_dirs)} r1 runs; freeze set = pfifo-r1. Ticks {', '.join(f'{T * 1000:g}' for T in TICKS)} ms; "
         f"tau {TAU_S:g} s, warm-up {T_WARM_S:g} s of calm ticks, stale after {T_STALE_S:g} s without a calm tick, "
         f"z clip {Z_MAX:g}. git {git}.", ""]

    # ── A. F3 variant selection at T = 33 ms ────────────────────────────────
    base = data[0.033]
    pf = [r for r in base if r["aqm"] == "pfifo"]
    rows = []
    for name in F3_VARIANTS:
        cells = {"all pfifo": [fl for r in pf for fl in r["flows"].values()],
                 "all AQMs": [fl for r in base for fl in r["flows"].values()],
                 "fq_codel competition": [fl for r in base if r["aqm"] == "fq_codel" and r["scn"] in s1.WEAK["fq_codel competition"][1] for fl in r["flows"].values()]}
        aucs = {}
        for cell, flows in cells.items():
            pos, neg = [], []
            for r in base:
                for s, df in r["flows"].items():
                    if not any(df is x for x in flows):
                        continue
                    x = df[name].to_numpy()
                    neg.append(x[df.calm.to_numpy()])
                    for a, _ in r["eps"].get(s, []):
                        if a >= d.WARMUP_S:
                            m = (df.t.to_numpy() > a) & (df.t.to_numpy() <= a + 0.2) & ~df.masked.to_numpy()
                            pos.append(x[m])
            aucs[cell] = s1.auc(np.concatenate(pos) if pos else np.array([]), np.concatenate(neg) if neg else np.array([]))
        peaks = []
        for r in pf:
            for s, df in r["flows"].items():
                z = s1.zscore(df, name)
                peaks += keyframe_peak(df, z, r["kf"][s], 0.033)
        calm_mad = np.median([s1.mad_sigma(df.loc[df.calm, name].to_numpy()) for r in pf for df in r["flows"].values()])
        rows.append([name, _f(aucs["all pfifo"]), _f(aucs["all AQMs"]), _f(aucs["fq_codel competition"]),
                     _f(np.median(peaks), 1), _f(np.percentile(peaks, 90), 1), len(peaks), _f(calm_mad, 3)])
    L += ["## A. F3 variant (T = 33 ms): AUC @200 ms after GT3 onset, and keyframe response in calm periods (batch z)", "",
          table(["variant", "AUC all pfifo", "AUC all AQMs", "AUC fq_codel competition", "keyframe peak z p50", "p90",
                 "keyframes", "calm MAD sigma"], rows), "",
          "Selection rule (decision 1): highest AUC among variants whose keyframe peak z p50 < 2.", ""]
    sel = None
    for row in rows:
        if row[4] != "-" and float(row[4]) < 2 and (sel is None or float(row[1]) > float(sel[1])):
            sel = row
    if sel is None:
        sel = max(rows, key=lambda r: float(r[1]) if r[1] != "-" else -1)
        L += [f"No variant keeps the keyframe peak below 2; falling back to the highest AUC: **{sel[0]}**.", ""]
    else:
        L += [f"Selected: **{sel[0]}**.", ""]
    f3sel = sel[0]

    # ── B. estimators, floors, calm exceedance (per T) ──────────────────────
    results = {}
    with ProcessPoolExecutor(max_workers=12) as pool:
        for T in TICKS:
            runs = data[T]
            for r in runs:
                for df in r["flows"].values():
                    df["F3sel"] = df[f3sel]
            for kind in ("ewma", "mad"):
                jobs = [(run_dirs[i], T, s, kind, f3sel) for i, r in enumerate(runs) if r["aqm"] == "pfifo" for s in r["flows"]]
                sig = defaultdict(list)
                for out in pool.map(end_sigmas, jobs):
                    for f, v in out.items():
                        if np.isfinite(v) and v > 0:
                            sig[f].append(v)
                floors = {f: 0.1 * float(np.median(sig[f])) if sig[f] else 0.0 for f in FEATS}
                jobs = [(run_dirs[i], T, s, kind, f3sel, floors,
                         {"aqm": r["aqm"], "scn": r["scn"], "rate": r["rates"][s], "flow": f"{r['name']}/{s}"},
                         [x for x in r["eps"].get(s, []) if x[0] >= d.WARMUP_S])
                        for i, r in enumerate(runs) for s in r["flows"]]
                recs = [x for x in pool.map(flow_record, jobs) if x is not None]
                results[(T, kind)] = (pd.DataFrame(recs), floors)
                print(f"T {T * 1000:g} ms {kind}: {len(recs)} flows, floors " + ", ".join(f"{f} {v:.4f}" for f, v in floors.items()), file=sys.stderr, flush=True)

    def exc_table(T, kind):
        df, floors = results[(T, kind)]
        rows = []
        for f in FEATS:
            by_rate = df.groupby("rate")[f"{f} exc"].median()
            by_aqm = df.groupby("aqm")[f"{f} exc"].median()
            spread_rate = by_rate.max() / max(by_rate.min(), 1e-9)
            spread_aqm = by_aqm.max() / max(by_aqm.min(), 1e-9)
            rows.append([f, _f(floors[f], 4), f"{100 * df[f'{f} exc'].median():.2f} %",
                         ", ".join(f"{k / 1e6:g}: {100 * v:.2f}" for k, v in by_rate.items()), _f(spread_rate, 1),
                         ", ".join(f"{k}: {100 * v:.2f}" for k, v in by_aqm.items()), _f(spread_aqm, 1),
                         f"{100 * df[f'{f} stale'].mean():.1f} %", _f(df[f"{f} arm3s"].median()), _f(df[f"{f} post2s"].median())])
        return table(["feature", "floor", "calm |z| > 3 median flow", "by rate Mb/s (%)", "max/min", "by AQM (%)", "max/min",
                      "time stats_stale", "mean |zc| 3 s after arming", "mean |zc| 2 s after episodes"], rows)

    L += ["## B. Normalization at T = 33 ms: calm exceedance P(|z| > 3) on calm ticks after arming (Gaussian reference 0.27 %)", ""]
    for kind, label in (("ewma", "(a) EWMA mean / variance, tau 60 s"), ("mad", "(b) stochastic median / MAD, tau 60 s")):
        L += [f"### {label}", "", exc_table(0.033, kind), ""]
    df33 = results[(0.033, "mad")][0]
    L += [f"Arming time (first 3 s of calm ticks) median {df33['armed_at'].median():.1f} s after run start; flows never armed: "
          f"{sum(1 for r in base for s in r['flows']) - len(df33)} of {sum(1 for r in base for s in r['flows'])}.", ""]

    # ── C. tick sweep ───────────────────────────────────────────────────────
    rows = []
    for T in TICKS:
        for kind in ("ewma", "mad"):
            df, _ = results[(T, kind)]
            pos_auc = {}
            for f in ("F1", "F2", "F3sel"):
                pos, neg = [], []
                for r in data[T]:
                    for s, fl in r["flows"].items():
                        if r["aqm"] != "pfifo":
                            continue
                        x = fl[f].to_numpy()
                        neg.append(x[fl.calm.to_numpy()])
                        for a, _ in r["eps"].get(s, []):
                            if a >= d.WARMUP_S:
                                m = (fl.t.to_numpy() > a) & (fl.t.to_numpy() <= a + 0.2) & ~fl.masked.to_numpy()
                                pos.append(x[m])
                pos_auc[f] = s1.auc(np.concatenate(pos), np.concatenate(neg))
            rows.append([f"{T * 1000:g}", kind, *(f"{100 * df[f'{f} exc'].median():.2f} %" for f in FEATS),
                         *(_f(pos_auc[f]) for f in ("F1", "F2", "F3sel")), f"{100 * df['F1 stale'].mean():.1f} %"])
    L += ["## C. Tick length sweep (pfifo-r1 AUC @200 ms; exceedance = median flow, all AQMs)", "",
          table(["T ms", "estimator", *(f"{f} |z|>3" for f in FEATS), "AUC F1", "AUC F2", f"AUC {f3sel}", "stale time"], rows), ""]

    # ── D. verdicts ─────────────────────────────────────────────────────────
    df_e, df_m = results[(0.033, "ewma")][0], results[(0.033, "mad")][0]
    worst = {}
    for kind, df in (("ewma", df_e), ("mad", df_m)):
        sp = []
        for f in FEATS:
            br, ba = df.groupby("rate")[f"{f} exc"].median(), df.groupby("aqm")[f"{f} exc"].median()
            sp.append(max(br.max() / max(br.min(), 1e-9), ba.max() / max(ba.min(), 1e-9)))
        worst[kind] = max(sp)
    L += ["## D. Verdicts", "",
          f"- Pass criterion 'calm exceedance within 2x across flows and AQMs': EWMA worst max/min {worst['ewma']:.1f}, "
          f"median/MAD worst max/min {worst['mad']:.1f} -> " + ", ".join(f"{k} {'PASS' if v <= 2 else 'FAIL'}" for k, v in worst.items()) + ".",
          f"- F3 variant: {f3sel} (table A).",
          "- Estimator choice and T: see tables B and C; the report states the numbers, the choice is recorded in the next step's header.", ""]
    for (T, kind), (df, floors) in results.items():
        df.to_csv(OUT / f"step2-{round(T * 1000)}ms-{kind}.csv", index=False)
    (OUT / "step2.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
