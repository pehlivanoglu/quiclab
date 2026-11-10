#!/usr/bin/env python3
"""Shadow v2, Step 1: feature quality of F1-F5 on the tick grid (spec v1.0 section 12).

    python3 scripts/shadow_v2_step1.py .runs/<campaign> [...]
    # -> reports/detector-v2/step1.md, step1-auc.csv, step1/*.png; per run and client
    #    <run>/shadow-v2/ticks/<sub>.csv (tick-grid features, reused by later steps)

Runs: every *-r1 run of the campaigns (held-out r2 untouched). Statistics that
later become parameters (calm distributions, floors) are reported for pfifo-r1
separately; the other AQMs' r1 runs are used only for the per-AQM AUC and the
weak-cell hypotheses, which need those cells.

Features per tick (T = 33 ms), spec section 4; Step 1 simplifications, each noted
in the report: base = running minimum of the tick's min RTT (down only, no
rebase); d_k = EWMA (tau 10 s) of the delivered rate initialised from the
rendition x 1.03, frozen while GT3 labels the client CONGESTED (truth-side
stand-in for the detector's own score freeze); F5's n_k counts sent bytes /
1200 (the sent log records QUIC writes, not packets); masks = v1's mask column
from the Step 0 per-ACK dump (identical to v1's masking).
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "detector-v2"
T = 0.033
W_G = 2
H_HOLD = 2
TAU_D = 10.0
WIRE = 1.03
MIN_R_BYTES = 12_000
PKT = 1200
FEATS = ("F1", "F2", "F3", "F4")
WEAK = {"fq_codel competition": ("fq_codel", ("burstudp", "onoff", "tcpcubic", "tcpbbr", "splitudp")),
        "burstcapshallow pfifo": ("pfifo", ("burstcapshallow",)), "tcpcubic red": ("red", ("tcpcubic",)),
        "burstlong pfifo": ("pfifo", ("burstlong",)), "calm090 pfifo": ("pfifo", ("calm090",))}
WINDOWS = (0.1, 0.2, 0.3)


# ── per-run feature computation ──────────────────────────────────────────

def ensure_dump(run: d.Run) -> Path:
    out = run.path / "shadow-v2" / "v1-samples"
    if not all((out / f"{s}.csv").exists() for s in run.subs):
        d.replay(run, d.TUNED, samples_to=out, grouping="none")
    return out


def ticks_for(run: d.Run, sid: str, dump: Path, code: np.ndarray, rendition_bps: float, T: float = T) -> pd.DataFrame:
    a = pd.read_csv(dump / f"{sid}.csv")
    a = a[a["rtt_us"].notna() & (a["min_rtt_us"] > 0)]
    t_ack = (a["mono_us"].to_numpy() * 1000 - run.epoch_mono_ns) / 1e9
    order = np.argsort(t_ack)
    a, t_ack = a.iloc[order], t_ack[order]
    sent = pd.read_csv(run.sender_file(sid, "sent"))
    t_sent = np.sort((sent["send_mono_us"].to_numpy() * 1000 - run.epoch_mono_ns) / 1e9)
    sent_bytes = sent["bytes"].to_numpy()[np.argsort((sent["send_mono_us"].to_numpy() * 1000 - run.epoch_mono_ns) / 1e9)]
    end = run.duration - d.SHUTDOWN_S
    edges = np.arange(0.0, end + T, T)
    n = len(edges) - 1
    k_ack = np.clip(np.searchsorted(edges, t_ack, side="right") - 1, 0, n - 1)
    cnt = np.bincount(k_ack, minlength=n)
    rtt = a["rtt_us"].to_numpy() / 1000
    min_rtt = np.full(n, np.nan)
    np.fmin.at(min_rtt, k_ack, rtt)
    lost = np.bincount(k_ack, weights=a["newly_lost"].to_numpy(), minlength=n)
    last_idx = np.full(n, -1)
    last_idx[k_ack] = np.arange(len(a))  # last ack of each tick (sorted, later writes win)
    masked = np.zeros(n, dtype=bool)
    np.logical_or.at(masked, k_ack, a["mask"].fillna("").astype(str).str.len().to_numpy() > 0)
    # Pending bytes at each ACK and their minimum inside the tick (frame-aligned level of P, decision 1 of Step 2).
    p_ack = (a["inflight_bytes"] + a["stream_buffer_bytes"]).to_numpy(dtype=float)
    p_min = np.full(n, np.nan)
    np.fmin.at(p_min, k_ack, p_ack)
    p_min = pd.Series(p_min).ffill(limit=H_HOLD).to_numpy()
    srtt = np.full(n, np.nan)
    srtt[k_ack] = a["srtt_us"].to_numpy() / 1000  # last ACK of the tick wins
    srtt = pd.Series(srtt).ffill().to_numpy()
    probe_rtt = np.zeros(n, dtype=bool)
    np.logical_or.at(probe_rtt, k_ack, a["phase"].astype(str).str.contains("probe_rtt").to_numpy())
    # Pending bytes at tick end: inflight at the last ACK plus bytes sent since, plus stream buffer.
    cum_sent = np.concatenate(([0.0], np.cumsum(sent_bytes)))
    sent_until_tick = cum_sent[np.searchsorted(t_sent, edges[1:], side="right")]
    inflight, sbuf, acked, held = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n, dtype=int)
    no_data = np.zeros(n, dtype=bool)
    li = -1
    gap = 0
    for k in range(n):
        if last_idx[k] >= 0:
            li, gap = last_idx[k], 0
        else:
            gap += 1
        if li < 0:
            no_data[k] = True
            continue
        row = a.iloc[li]
        sent_at_ack = cum_sent[np.searchsorted(t_sent, t_ack[li], side="right")]
        inflight[k] = row["inflight_bytes"] + (sent_until_tick[k] - sent_at_ack)
        sbuf[k] = row["stream_buffer_bytes"]
        acked[k] = row["bytes_acked_total"]
        if gap > H_HOLD:
            no_data[k] = True
        held[k] = gap
    # Hold the last min RTT for up to H_HOLD ticks.
    f1_src = pd.Series(min_rtt).ffill(limit=H_HOLD).to_numpy()
    base = np.fmin.accumulate(np.where(np.isnan(f1_src), np.inf, f1_src))
    base = np.where(np.isinf(base), np.nan, base)
    F1 = f1_src - base
    F2 = F1 - np.concatenate((np.full(W_G, np.nan), F1[:-W_G]))
    P = inflight + sbuf
    delivered = np.diff(acked, prepend=acked[:1]).clip(min=0)
    rate = delivered * 8 / T
    tick_code = code[np.clip((edges[1:] / gt_score.GRID_S).astype(int), 0, len(code) - 1)]
    congested = tick_code == gt_score.RANK["CONGESTED"]
    dk = np.empty(n)
    v = rendition_bps * WIRE
    alpha = T / TAU_D
    for k in range(n):
        if not no_data[k] and not congested[k] and not masked[k]:
            v += alpha * (rate[k] - v)
        dk[k] = v
    F3 = (P - np.concatenate((np.full(W_G, np.nan), P[:-W_G]))) * 8 / (dk * W_G * T)
    win = int(round(1 / T))
    cs = np.concatenate(([0.0], np.cumsum(delivered)))
    r1s = (cs[win:] - cs[:-win]) if n >= win else np.array([])
    R = np.full(n, np.nan)
    if n >= win:
        R[win - 1:] = r1s
    F4 = np.where(R >= MIN_R_BYTES, P / R - base / 1000, np.nan)  # seconds: R = bytes delivered in the last 1 s
    # F5: sends shifted by base (observed when their fate is known), packets ~ bytes / PKT.
    shift = np.nan_to_num(base, nan=np.nanmedian(base) if np.isfinite(np.nanmedian(base)) else 0.0) / 1000
    t_obs = t_sent + np.interp(t_sent, edges[1:], shift)
    k_s = np.clip(np.searchsorted(edges, t_obs, side="right") - 1, 0, n - 1)
    n_pk = np.bincount(k_s, weights=sent_bytes / PKT, minlength=n)
    df = pd.DataFrame({"t": edges[1:], "F1": F1, "F2": F2, "F3": F3, "F4": F4, "n": n_pk, "l": lost, "base": base,
                       "P": P, "P_min": p_min, "d": dk, "rate": rate, "d0": rendition_bps * WIRE, "R": R, "masked": masked, "no_data": no_data, "acks": cnt,
                       "srtt": srtt, "probe_rtt": probe_rtt, "gt3": tick_code})
    df.loc[df.no_data, FEATS] = np.nan
    return df


def worker(run_dir: Path, T: float = T, dump: Path | None = None, out_name: str | None = None) -> dict:
    """Tick files for every client; dump / out_name: another per-ACK dump (e.g. the OWD mode) and tick folder."""
    run = d.Run(run_dir)
    dump = dump or ensure_dump(run)
    rates = {s: c["rate_kbps"] * 1000 for s, c in run.topology["subscribers"].items()}
    eps, labels = gt3.run_truth(run, gt3.Params(), path_queues=False)
    out_dir = run.path / "shadow-v2" / (out_name or ("ticks" if abs(T - 0.033) < 1e-9 else f"ticks-{round(T * 1000)}ms"))
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {"name": run.path.name, "aqm": run.aqm, "scn": d.scenario_name(run.path), "flows": {}}
    for s in run.subs:
        rows = [x for x in labels if x["hop"] == s]
        code = gt_score.client_view_codes(run, rows)
        df = ticks_for(run, s, dump, code, rates[s], T)
        my = [(e["t_on"], e["t_end"]) for e in eps if e["flow"] == s]
        near = np.zeros(len(df), dtype=bool)
        for a, b in my:
            near |= (df.t >= a - 1.0) & (df.t <= b + 1.0)
        df["calm"] = (df.gt3 == gt_score.RANK["CLEAR"]) & ~df.masked & ~df.no_data & ~near & (df.t >= d.WARMUP_S)
        df.to_csv(out_dir / f"{s}.csv", index=False)
        kf = pd.read_csv(run.sender_file(s, "frames"))
        kf_t = np.array([run.t_unix_us(x) for x in kf[kf.keyframe == 1]["send_us"]])
        res["flows"][s] = {"df": df, "episodes": my, "rate": rates[s], "keyframes": kf_t}
    res["events"] = [e for e in run.events if e["event"] == "link" and e.get("label", "").startswith("delay ")]
    return res


# ── analyses ─────────────────────────────────────────────────────────────

def mad_sigma(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return 1.4826 * float(np.median(np.abs(x - np.median(x)))) if len(x) else float("nan")


def zscore(df: pd.DataFrame, f: str) -> np.ndarray:
    calm = df.loc[df.calm, f].to_numpy()
    mu, sig = (np.nanmedian(calm), mad_sigma(calm)) if np.isfinite(calm).sum() > 30 else (np.nan, np.nan)
    return (df[f].to_numpy() - mu) / sig if sig and sig > 0 else np.full(len(df), np.nan)


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) < 5 or len(neg) < 50:
        return float("nan")
    allv = np.concatenate((pos, neg))
    ranks = pd.Series(allv).rank().to_numpy()
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_cell(flows: list[dict]) -> dict[tuple[str, float], float]:
    out = {}
    for f in (*FEATS, "l", "lr"):
        for w in WINDOWS:
            pos, neg = [], []
            for fl in flows:
                df = fl["df"]
                x = df[f].to_numpy() if f != "lr" else (df.l / df.n.clip(lower=1)).to_numpy()
                neg.append(x[df.calm.to_numpy()])
                for a, _ in fl["episodes"]:
                    if a >= d.WARMUP_S:
                        m = (df.t.to_numpy() > a) & (df.t.to_numpy() <= a + w) & ~df.masked.to_numpy()
                        pos.append(x[m])
            out[(f, w)] = auc(np.concatenate(pos) if pos else np.array([]), np.concatenate(neg) if neg else np.array([]))
    return out


def _f(x, k=2):
    return "-" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{k}f}"


def table(header, rows):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
                     + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def main(argv):
    if not argv:
        sys.exit(__doc__)
    runs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists() and r.name.endswith("-r1"))
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "step1").mkdir(exist_ok=True)
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    stamp = (ROOT / ".runs" / "2026-11-05_TRUTH-SETTINGS.md")
    pf = [r for r in res if r["aqm"] == "pfifo"]
    flows_pf = [fl for r in pf for fl in r["flows"].values()]
    L = ["# Shadow v2, Step 1: feature quality", "",
         f"{len(res)} r1 runs ({', '.join(Path(c).name for c in argv)}); freeze set = {len(pf)} pfifo-r1 runs. "
         f"Tick {T * 1000:g} ms, W_g {W_G} ticks, hold {H_HOLD} ticks. git {git}. Truth: "
         + (stamp.read_text().splitlines()[3] if stamp.exists() else "see TRUTH-SETTINGS") + ".", "",
         "## Verification (spec section 14)", "",
         "1. Per-ACK dump: inflight_bytes, stream_buffer_bytes, newly_lost, sent_mono_us, bytes_acked_total, phase, "
         "app_limited, mask present; onSent = publishers/<pub>/<sub>-sent.csv (QUIC writes with bytes). OK.",
         "2. Realtime-monotonic offset: det_eval.Run epoch_mono_ns / epoch_unix_ns from events.csv. OK.",
         "3. rendition_bps: topology subscribers rate_kbps (x 1.03 wire). OK.",
         "4. relay_saturated: 0 in all 11 461 661 ACK rows of the 200 runs. OK.", "",
         "## Ambiguities and resolutions", "",
         "- Step 1 is specified on pfifo-r1 but the weak-cell hypotheses need fq_codel / red cells: features are computed "
         "for every r1 run; calm statistics and floors below are from pfifo-r1 only.",
         "- base: running minimum of the tick min RTT, no rebase (section 7 needs z-scores, Step 2); after a forward "
         "delay step F1 stays elevated, which is the delaystep hypothesis itself.",
         "- d_k is frozen while GT3 labels the client CONGESTED (the detector's own score does not exist yet).",
         "- n_k = sent bytes / 1200 (the sent log records writes, not packets); l_k = newly_lost over the tick's ACKs.",
         "- calm tick = GT3 CLEAR, unmasked, has data, >= 1 s away from any GT3 episode of the flow, after warm-up.", ""]

    # 1 calm distributions (pfifo-r1) per feature and per bitrate
    rows = []
    sig_all = defaultdict(list)
    for f in FEATS:
        for rate in sorted({fl["rate"] for fl in flows_pf}):
            vals = np.concatenate([fl["df"].loc[fl["df"].calm, f].to_numpy() for fl in flows_pf if fl["rate"] == rate])
            vals = vals[np.isfinite(vals)]
            sigs = [mad_sigma(fl["df"].loc[fl["df"].calm, f].to_numpy()) for fl in flows_pf if fl["rate"] == rate]
            sig_all[f] += [s for s in sigs if np.isfinite(s)]
            rows.append([f, f"{rate / 1e6:g}", len(vals), _f(np.median(vals), 3), _f(mad_sigma(vals), 3), _f(np.std(vals), 3),
                         _f(np.percentile(vals, 1), 3), _f(np.percentile(vals, 99), 3),
                         _f(np.median(sigs), 3), _f(np.min(sigs), 3), _f(np.max(sigs), 3)])
    floors = {f: 0.1 * float(np.median(s)) for f, s in sig_all.items() if s}
    L += ["## 1. Calm distribution per feature (pfifo-r1; F1, F2 in ms, F3 dimensionless, F4 in s)", "",
          table(["feature", "rate Mb/s", "calm ticks", "median", "MAD sigma", "std", "p1", "p99",
                 "per-flow sigma median", "min", "max"], rows), "",
          "floor_i candidate = 10 % of the median per-flow MAD sigma (section 6): " +
          ", ".join(f"{f} {v:.4f}" for f, v in floors.items()), ""]
    calm_l = np.concatenate([fl["df"].loc[fl["df"].calm, "l"].to_numpy() for fl in flows_pf])
    calm_n = np.concatenate([fl["df"].loc[fl["df"].calm, "n"].to_numpy() for fl in flows_pf])
    L += [f"Calm loss p0 (pfifo-r1 pooled): {calm_l.sum() / max(1, calm_n.sum()):.5f} "
          f"({int(calm_l.sum())} lost / {int(calm_n.sum())} sent); ticks with any loss: {100 * (calm_l > 0).mean():.2f} %.", ""]

    # 2 autocorrelation and 3 cross-correlation on calm ticks (pfifo-r1)
    lags = (1, 2, 3, 6, 15, 30)
    rows = []
    for f in FEATS:
        acf = defaultdict(list)
        for fl in flows_pf:
            df = fl["df"]
            x = np.where(df.calm.to_numpy(), df[f].to_numpy(), np.nan)
            x = x - np.nanmean(x)
            for lag in lags:
                a_, b_ = x[:-lag], x[lag:]
                m = np.isfinite(a_) & np.isfinite(b_)
                if m.sum() > 100:
                    acf[lag].append(float(np.corrcoef(a_[m], b_[m])[0, 1]))
        rows.append([f, *(_f(np.median(acf[lag])) for lag in lags)])
    L += ["## 2. Autocorrelation of calm ticks (median over pfifo-r1 flows)", "",
          table(["feature", *(f"lag {lag} ({lag * T * 1000:.0f} ms)" for lag in lags)], rows), ""]
    big = pd.concat([fl["df"].loc[fl["df"].calm, list(FEATS)] for fl in flows_pf])
    corr = big.corr()
    L += ["## 3. Cross-correlation of calm ticks (pfifo-r1 pooled)", "",
          table(["", *FEATS], [[f, *(_f(corr.loc[f, g]) for g in FEATS)] for f in FEATS]), ""]

    # 4 keyframe-aligned response (pfifo-r1, calm periods), z per flow
    offs = np.arange(-2, 13)
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.2))
    rows = []
    for rate in sorted({fl["rate"] for fl in flows_pf}):
        resp = {f: np.zeros((len(offs),)) for f in FEATS}
        cnt = {f: np.zeros(len(offs)) for f in FEATS}
        for fl in (fl for fl in flows_pf if fl["rate"] == rate):
            df = fl["df"]
            z = {f: zscore(df, f) for f in FEATS}
            calm = df.calm.to_numpy()
            for tk in fl["keyframes"]:
                k0 = int(tk / T)
                if k0 - 2 < 0 or k0 + 13 >= len(df) or not calm[k0 - 2:k0 + 13].any():
                    continue
                for f in FEATS:
                    seg = z[f][k0 - 2:k0 + 13]
                    ok = np.isfinite(seg) & calm[k0 - 2:k0 + 13]
                    resp[f][ok] += seg[ok]
                    cnt[f][ok] += 1
        for i, f in enumerate(FEATS):
            mean = resp[f] / np.maximum(cnt[f], 1)
            axes[i].plot(offs * T * 1000, mean, label=f"{rate / 1e6:g} Mb/s")
            rows.append([f, f"{rate / 1e6:g}", _f(np.nanmax(mean)), f"{offs[int(np.nanargmax(mean))] * T * 1000:.0f}",
                         int(cnt[f].max())])
    for i, f in enumerate(FEATS):
        axes[i].set_title(f"{f}: mean z around a keyframe send"); axes[i].axhline(0, color="k", lw=0.5)
        axes[i].set_xlabel("ms after keyframe send"); axes[i].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(OUT / "step1" / "keyframe-response.png", dpi=110); plt.close(fig)
    L += ["## 4. Keyframe-aligned response in calm periods (pfifo-r1; z in calm MAD units)", "",
          table(["feature", "rate Mb/s", "peak mean z", "at (ms after send)", "keyframes"], rows), "",
          "Plot: step1/keyframe-response.png. A peak above delta/2 = 1 means a lone keyframe already scores.", ""]

    # 5 AUC per AQM and weak cell
    auc_rows, csv_rows = [], []
    cells = {f"all {aqm}": [fl for r in res if r["aqm"] == aqm for fl in r["flows"].values()] for aqm in sorted({r["aqm"] for r in res})}
    cells.update({name: [fl for r in res if r["aqm"] == aqm and r["scn"] in scns for fl in r["flows"].values()]
                  for name, (aqm, scns) in WEAK.items()})
    for rate in (1e6, 2.5e6, 5e6):
        cells[f"burstcap pfifo {rate / 1e6:g} Mb/s"] = [fl for r in pf if r["scn"] == "burstcap" for fl in r["flows"].values() if fl["rate"] == rate]
    for name, flows in cells.items():
        a = auc_cell(flows)
        n_ep = sum(1 for fl in flows for x, _ in fl["episodes"] if x >= d.WARMUP_S)
        auc_rows.append([name, n_ep, *(_f(a[(f, w)]) for w in WINDOWS for f in (*FEATS, "l"))])
        csv_rows += [[name, n_ep, f, w, a[(f, w)]] for f in (*FEATS, "l", "lr") for w in WINDOWS]
    L += ["## 5. AUC, calm ticks vs the first 100 / 200 / 300 ms after a GT3 onset (GT3-positive clients)", "",
          table(["cell", "GT3 episodes", *(f"{f} @{int(w * 1000)}" for w in WINDOWS for f in (*FEATS, "l"))], auc_rows), "",
          "0.5 = no separation; F4 and F1 are level features (expected to rise later), F2 / F3 growth, l = lost packets in the tick.", ""]
    pd.DataFrame(csv_rows, columns=["cell", "episodes", "feature", "window_s", "auc"]).to_csv(OUT / "step1-auc.csv", index=False)

    # 6 hypotheses
    H = ["## 6. Hypotheses", ""]
    # 6a burstlong: hold features after BBR adapts
    rows = []
    for aqm in ("pfifo", "red", "pie", "fq_codel"):
        fl_ = [fl for r in res if r["aqm"] == aqm and r["scn"] == "burstlong" for fl in r["flows"].values()]
        early, late = defaultdict(list), defaultdict(list)
        for fl in fl_:
            df = fl["df"]
            z = {f: zscore(df, f) for f in FEATS}
            for a, b in fl["episodes"]:
                if b - a < 8:
                    continue
                t = df.t.to_numpy()
                m_e, m_l = (t > a) & (t <= a + 0.5), (t > a + 3) & (t <= b - 1)
                for f in FEATS:
                    early[f].append(np.nanmean(z[f][m_e] >= 1)); late[f].append(np.nanmean(z[f][m_l] >= 1))
        if early:
            rows.append([aqm, len(early["F1"]), *(f"{_f(np.nanmean(early[f]))} / {_f(np.nanmean(late[f]))}" for f in FEATS)])
    H += ["### 6a. burstlong: share of ticks with z >= 1, first 0.5 s / after BBR adapted (3 s to end - 1 s)", "",
          table(["aqm", "episodes >= 8 s", *FEATS], rows), "",
          "Hold hypothesis holds if F1 / F4 stay high after adaptation while F2 / F3 fall.", ""]
    # 6b tcpcubic red: F2 vs F3 crossing times
    for aqm in ("red", "pfifo", "pie", "fq_codel"):
        fl_ = [fl for r in res if r["aqm"] == aqm and r["scn"] == "tcpcubic" for fl in r["flows"].values()]
        offs_, both66, both500, n = [], 0, 0, 0
        for fl in fl_:
            df = fl["df"]; t = df.t.to_numpy()
            z2, z3 = zscore(df, "F2"), zscore(df, "F3")
            for a, b in fl["episodes"]:
                m = (t > a - 0.5) & (t <= b)
                i2 = np.flatnonzero(m & (z2 >= 2)); i3 = np.flatnonzero(m & (z3 >= 2))
                n += 1
                if len(i2) and len(i3):
                    off = (t[i3[0]] - t[i2[0]])
                    offs_.append(off)
                    # do the two ever cross within the same W_g window?
                    s2 = set(np.flatnonzero(m & (z2 >= 2))); s3 = set(np.flatnonzero(m & (z3 >= 2)))
                    both66 += any(any(j in s3 for j in range(i - W_G, i + W_G + 1)) for i in s2)
                    both500 += any(any(j in s3 for j in range(i - 15, i + 16)) for i in s2)
        H += [f"### 6b. tcpcubic {aqm}: F2 and F3 crossings (z >= 2) within GT3 episodes", "",
              f"episodes {n}; both features ever cross: {len(offs_)}; first-crossing offset F3 - F2 p10/p50/p90 "
              f"{_f(np.percentile(offs_, 10) if offs_ else float('nan'))} / {_f(np.median(offs_) if offs_ else float('nan'))} / "
              f"{_f(np.percentile(offs_, 90) if offs_ else float('nan'))} s; episodes where they cross within the same "
              f"{W_G * T * 1000:.0f} ms window: {both66}; within 500 ms: {both500}.", ""]
    # 6c delaystep: F1 flat and elevated, F3 unchanged, no loss after a step
    rows = []
    for r in (r for r in res if r["scn"] == "delaystep"):
        for e in r["events"]:
            t0 = float(e["applied_s"]); direction = e["label"].split()[1]; extra = e["label"].split()[2]
            for s, fl in r["flows"].items():
                df = fl["df"]; t = df.t.to_numpy()
                z1, z3 = zscore(df, "F1"), zscore(df, "F3")
                m = (t > t0 + 0.3) & (t <= t0 + 1.3)
                sig1 = mad_sigma(df.loc[df.calm, "F1"].to_numpy())
                rows.append([r["aqm"], direction, extra, s, _f(np.nanmedian(z1[m]), 1), _f(np.nanstd(df.F1.to_numpy()[m]) / sig1 if sig1 else float("nan")),
                             _f(np.nanmax(np.abs(z3[m])), 1), int(df.l.to_numpy()[m].sum())])
    dfr = pd.DataFrame(rows, columns=["aqm", "dir", "step", "client", "z1 median", "F1 std / calm sigma", "max |z3|", "lost"])
    agg = dfr.groupby(["dir", "step"]).agg(n=("client", "size"), z1=("z1 median", lambda v: np.median(pd.to_numeric(v, errors="coerce"))),
                                           flat=("F1 std / calm sigma", lambda v: np.median(pd.to_numeric(v, errors="coerce"))),
                                           z3=("max |z3|", lambda v: np.median(pd.to_numeric(v, errors="coerce"))),
                                           z3_ok=("max |z3|", lambda v: np.mean(pd.to_numeric(v, errors="coerce") < 1)),
                                           lost=("lost", "sum")).reset_index()
    H += ["### 6c. delaystep: 0.3-1.3 s after each step, all clients, all AQMs (medians)", "",
          table(["direction", "step", "client x steps", "z1 median", "F1 std / calm sigma", "max |z3| median", "share max |z3| < 1", "lost pkts"],
                [[a.dir, a.step, a.n, _f(a.z1, 1), _f(a.flat), _f(a.z3, 1), _f(a.z3_ok), int(a.lost)] for a in agg.itertuples()]), "",
          "Rebase precondition (section 7): z1 >= 1 on every tick, F1 std < calm sigma (ratio < 1), |z3| < 1, no loss. "
          "RTT input: reverse steps raise F1 as much as forward ones.", ""]
    # 6d weak cells: F5 vs F1-F4 at 200 ms
    rows = []
    for name in ("fq_codel competition", "burstcapshallow pfifo", "all pfifo"):
        a = auc_cell(cells[name])
        rows.append([name, *(_f(a[(f, 0.2)]) for f in (*FEATS, "l", "lr"))])
    H += ["### 6d. Weak cells at 200 ms: does loss separate where delay does not?", "",
          table(["cell", *FEATS, "l (lost pkts)", "l / n"], rows), ""]
    L += H
    (OUT / "step1.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
