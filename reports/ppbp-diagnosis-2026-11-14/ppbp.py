#!/usr/bin/env python3
"""Detector diagnosis on the ppbp runs (2026-11-14). Measurement only: the frozen Shadow v2
(scripts/shadow_v2_frozen.py, OWD ticks, hold, loss gate level+cap, theta_on 0.25) is called,
not changed; GT1 / GT3 and the frame-latency harm label (shadow_v2_step0.harm_times) are the
existing ones; no GT-Q / GT-H.

    .venv/bin/python3 reports/ppbp-diagnosis-2026-11-14/ppbp.py run  > .../rows.jsonl
    .venv/bin/python3 reports/ppbp-diagnosis-2026-11-14/ppbp.py sum  .../rows.jsonl > .../summary.md
    .venv/bin/python3 reports/ppbp-diagnosis-2026-11-14/ppbp.py plots .../rows.jsonl .../

Runs: .runs/old-wrong-scenaris/ip4-not-sync-keyframes-oldGT (staggered phases, base topology,
one rep each): M1 ppbp and M1 burstcap on pfifo / red / pie / codel / cake, G0 calm065 /
calm090 / calmcbr090 on pfifo / red / pie / cake / fq_codel.

Detector state (item 2) is re-derived beside the detector from its own outputs: the calm-tick
rule (score over the trailing LAG_S below S_FREEZE, tick not masked, with data), the 3 s
initialisation and the EWMA (tau 60 s) of shadow_v2_step3.run_cusum, applied to F1. Baseline
of the OWD = base (running minimum, column `base`) + mu_F1; noise = max(sigma_F1, floor F1).

Constants (tag):
  duration bins < 0.5 / 0.5-1 / 1-2 / >= 2 s (P: gt_score.BINS); peak queue delay bins
  < 10 / 10-20 / 20-50 / >= 50 ms (FLAG); harm overlap = a missed playout deadline in
  [t_on, t_end + 2 s] (P: shadow_v2_step0.HARM_TAIL_S); "overlap" detection = an alarm span
  overlaps the episode (as step 2 A1); "start" detection = gt_score's rule;
  sensitivity = the sustained F1 level that makes the F1 term alone reach the alarm level
  (theta_on x 2 g_ref) within SENS_S, z = 1 + theta_on g_ref / (SENS_S / T) (M; F2 / F3 onset
  terms ignored, FLAG), SENS_S 1 s and 0.5 s (FLAG);
  missed-episode classes (item 3): never moved = score max in the episode < NEVER (0.05, FLAG);
  crossed late = an alarm starts within 2 s after the episode (FLAG); drained = the score fell
  by at least half from a local maximum inside the episode before reaching theta_on (FLAG);
  other = the rest; examples drawn with random.Random(SEED = 7) (FLAG).
"""

from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_step2 as s2  # noqa: E402
import gt1  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_frozen as sv  # noqa: E402
import shadow_v2_step0 as st0  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402
import shadow_v2_step5 as s5  # noqa: E402

BASE = ROOT / ".runs/old-wrong-scenaris/ip4-not-sync-keyframes-oldGT"
DUR_BINS = gt_score.BINS
Q_BINS = ((0, 10), (10, 20), (20, 50), (50, 1e9))
HARM_TAIL_S = st0.HARM_TAIL_S
NEVER = 0.05
SENS_S = (1.0, 0.5)
SEED = 7
DETS = ("v2", "v2-fixed")


def run_list():
    out = []
    for k, types, aqms in (("M1", ("ppbp", "burstcap"), ("pfifo", "red", "pie", "codel", "cake")),
                           ("G0", ("calm065", "calm090", "calmcbr090"), ("pfifo", "red", "pie", "cake", "fq_codel"))):
        for t in types:
            for a in aqms:
                rd = BASE / k / f"grp-{t}-{a}-r1"
                if rd.exists():
                    out.append(rd)
    return out


def detector(run, det):
    """run_cusum results and alarm spans per flow, exactly as shadow_v2_frozen.episodes builds them."""
    fit = sv.FROZEN["OWD"]
    s3.FLOORS.clear()
    s3.FLOORS.update(fit["floors"])
    s3.FIXED_STATS.clear()
    s3.FIXED_STATS.update(fit["stats"])
    label = sv.LABEL[det] + " +hold" + " gate:level+cap"
    out = {}
    for s, f in sv.tick_files(run, "OWD").items():
        df = s3.load_flow(f)
        r = s3.run_cusum(df, label, fit["g_ref"][det], False)
        out[s] = (df, r, s5.on_spans(r, s3.THETA_ON))
    return out, fit["g_ref"]


def state_f1(df, r, fixed):
    """mu_F1 and sigma_F1 per tick as run_cusum holds them (re-derived from its outputs)."""
    T = s3.tick_of(df)
    n = len(df)
    x = df.F1.to_numpy()
    masked, nodata = df.masked.to_numpy(), df.no_data.to_numpy()
    score = r["score"]
    warm, lag, a = int(round(s3.T_WARM_S / T)), int(round(s3.LAG_S / T)), T / s3.TAU_S
    mu = np.full(n, np.nan)
    var = np.full(n, np.nan)
    if fixed:
        m, sd = s3.FIXED_STATS["F1"]
        return np.full(n, m), np.full(n, max(sd, s3.FLOORS["F1"]))
    armed, cnt, init, m, v = False, 0, [], 0.0, 0.0
    for k in range(n):
        if masked[k] or nodata[k]:
            mu[k], var[k] = (m, v) if armed else (np.nan, np.nan)
            continue
        calm = k == 0 or score[max(0, k - lag):k].max() < s3.S_FREEZE
        if not armed:
            if calm:
                cnt += 1
                if np.isfinite(x[k]):
                    init.append(x[k])
                if cnt >= warm:
                    armed = True
                    arr = np.array(init)
                    m, v = (float(arr.mean()), float(arr.var())) if len(arr) else (0.0, 0.0)
            mu[k], var[k] = (m, v) if armed else (np.nan, np.nan)
            continue
        if calm and np.isfinite(x[k]):
            delta = x[k] - m
            m += a * delta
            v += a * (delta * (x[k] - m) - v)
        mu[k], var[k] = m, v
    return mu, np.maximum(np.sqrt(np.maximum(var, 0)), s3.FLOORS["F1"])


def classify(r, spans, a, b, T):
    t = r["t"]
    sc = r["score"]
    m = (t >= a) & (t <= b)
    if not m.any():
        return "other", {}
    seg = sc[m]
    smax = float(seg.max())
    late = any(b < x <= b + HARM_TAIL_S for x, _, _ in spans)
    info = {"score_max": round(smax, 3)}
    if late:
        return "crossed late", info
    if smax < NEVER:
        return "never moved", info
    # drained: a fall of >= half from a running maximum while below theta_on
    run_max, drained = 0.0, False
    for v in seg:
        run_max = max(run_max, v)
        if run_max >= NEVER and v <= run_max / 2:
            drained = True
            break
    if drained:
        S = r["G"]
        g = S[m]
        dG = np.diff(g, prepend=g[0])
        neg = dG < 0
        sf = {f: r["s_f"][f][m] for f in r["s_f"]}
        contrib = {f: float(np.sum(np.minimum(v, 0)[neg])) for f, v in sf.items()}
        info.update({"drain_ticks": int(neg.sum()), "drain_sum": round(float(dG[neg].sum()), 2),
                     "neg_by_feature": {f: round(v, 2) for f, v in contrib.items()}})
        return "drained", info
    return "other", info


def run_row(rd: Path):
    run = d.Run(rd)
    minutes = max(run.duration - d.WARMUP_S - d.SHUTDOWN_S, 1) / 60
    e1, l1 = gt1.run_truth(run, gt1.Params())
    v1 = gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1)
    e3, l3 = gt3.run_truth(run, gt3.Params())
    v3 = gt3.view_of(run, e3, l3, need_path=True)
    delay = s2.egress_delay(run)
    hops = {s: s2.path_egresses(run, s, delay) for s in run.subs}
    harms = {s: st0.harm_times(run, s) for s in run.subs}
    dets = {}
    g_ref = None
    for det in DETS:
        dets[det], g_ref = detector(run, det)
    row = {"run": rd.name, "campaign": rd.parent.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "minutes": minutes, "clients": len(run.subs)}
    # egress-level GT1
    hop_eps = defaultdict(list)
    for e in e1:
        hop_eps[e["hop"]].append(e["end_s"] - e["start_s"])
    row["gt1_egress"] = {h: {"per_min": round(len(v) / minutes, 2), "dur": [round(x, 3) for x in np.percentile(v, [10, 50, 90])],
                             "on_share": round(sum(v) / (minutes * 60), 3)} for h, v in hop_eps.items()}
    # episodes with attributes
    eps_rows = []
    for truth, view in (("GT1", v1), ("GT3", v3)):
        for s, (eps, code) in view.items():
            for a, b in eps:
                if a < d.WARMUP_S:
                    continue
                pk = 0.0
                for h in hops.get(s, ()):
                    t, q = delay[h]
                    mm = (t >= a) & (t <= b)
                    if mm.any():
                        pk = max(pk, float(q[mm].max()))
                harm = any(a <= x <= b + HARM_TAIL_S for x in harms.get(s, []))
                er = {"truth": truth, "client": s, "a": round(a, 3), "b": round(b, 3), "dur": round(b - a, 3),
                      "peak_ms": round(pk, 1), "harm": harm}
                for det in DETS:
                    df, r, spans = dets[det][s]
                    lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
                    er[f"{det}_start"] = any(lo <= x <= hi for x, _, _ in spans if x >= d.WARMUP_S)
                    er[f"{det}_overlap"] = any(x <= b and y >= a for x, y, _ in spans if x >= d.WARMUP_S)
                    if truth == "GT1" and det == "v2" and not er["v2_start"] and b - a >= 1.0:
                        er["class"], er["class_info"] = classify(r, spans, a, b, s3.tick_of(df))
                eps_rows.append(er)
    row["episodes"] = eps_rows
    # GT1 on-share per client
    row["gt1_client_on"] = {s: round(float(np.mean(code[int(d.WARMUP_S / gt_score.GRID_S):] == gt_score.RANK["CONGESTED"])), 3)
                            for s, (eps, code) in v1.items()}
    # precision / false alarms (gt_score, GT1)
    starts = {(det, s): [x for x, _, _ in dets[det][s][2]] for det in DETS for s in run.subs}
    tal = gt_score.score(run, v1, starts, DETS)
    row["score_gt1"] = {det: {k: tal[det][k] for k in ("episodes", "detected", "tp", "fp", "clear_s")} for det in DETS}
    tal3 = gt_score.score(run, v3, starts, DETS)
    row["score_gt3"] = {det: {k: tal3[det][k] for k in ("episodes", "detected", "tp", "fp", "clear_s")} for det in DETS}
    # detector state (v2 and fixed), per client, sampled per second
    st = {}
    for det in DETS:
        for s in run.subs:
            df, r, spans = dets[det][s]
            mu, sig = state_f1(df, r, det == "v2-fixed")
            base = df["base"].to_numpy()
            gmin = float(np.nanmin(base)) if np.isfinite(base).any() else np.nan
            t = df.t.to_numpy()
            ok = (t >= d.WARMUP_S) & np.isfinite(mu) & np.isfinite(base)
            ref = base + mu - gmin   # baseline above the queue-free delay, ms
            T = s3.tick_of(df)
            zs = {S: 1 + s3.THETA_ON * g_ref[det] / (S / T) for S in SENS_S}
            st[f"{det}|{s}"] = {
                "mu_p50": round(float(np.nanmedian(mu[ok])), 3) if ok.any() else None,
                "sig_p50": round(float(np.nanmedian(sig[ok])), 3) if ok.any() else None,
                "sig_p90": round(float(np.nanpercentile(sig[ok], 90)), 3) if ok.any() else None,
                "above_p50": round(float(np.nanmedian(ref[ok])), 3) if ok.any() else None,
                "above_share": {str(x): round(float(np.mean(ref[ok] > x)), 3) for x in (1, 2, 5, 10)} if ok.any() else None,
                "sens_ms": {str(S): round(float(np.nanmedian(ref[ok] + z * sig[ok])), 2) for S, z in zs.items()} if ok.any() else None,
                "series": [[round(float(t[k]), 1), round(float(ref[k]), 2), round(float(sig[k]), 3)]
                           for k in range(0, len(t), max(1, int(1 / T))) if ok[k]],
            }
    row["state"] = st
    return row


def main_run():
    with Pool(10) as pool:
        for r in pool.imap_unordered(run_row, run_list()):
            print(json.dumps(r, default=float), flush=True)


# ═══ summary ═══════════════════════════════════════════════════════════

def f2(x, f=".2f"):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else format(x, f)


def rec(eps, key):
    return f"{sum(e[key] for e in eps)}/{len(eps)} ({f2(sum(e[key] for e in eps) / len(eps)) if eps else '-'})"


def main_sum(path):
    R = [json.loads(x) for x in open(path) if x.strip()]
    R.sort(key=lambda r: (["ppbp", "burstcap", "calm065", "calm090", "calmcbr090"].index(r["type"]), r["aqm"]))
    print("# ppbp diagnosis: tables\n")
    print("All runs r1 only (one rep per configuration): no rep comparison is possible.\n")
    # 1a
    print("## 1a. GT1 episodes per egress (router->switch = the shared bottleneck)\n")
    print("| type | AQM | episodes per min | duration p10 / p50 / p90 s | share of time on | client-level GT1 on share p50 |")
    print("|---|---|---|---|---|---|")
    for r in R:
        e = r["gt1_egress"].get("router->switch")
        cs = [v for s, v in r["gt1_client_on"].items() if s != "sub-ctrl"]
        print(f"| {r['type']} | {r['aqm']} | " + (f"{e['per_min']} | {' / '.join(f2(x) for x in e['dur'])} | {f2(e['on_share'])}" if e else "0 | - | 0") + f" | {f2(np.median(cs) if cs else None)} |")
    print()
    pk = defaultdict(list)
    for r in R:
        for e in r["episodes"]:
            if e["truth"] == "GT1":
                pk[r["type"]].append(e["peak_ms"])
    print("Peak queue delay of client-level GT1 episodes, p10 / p50 / p90 ms: " + "; ".join(
        f"{t} {' / '.join(f2(x, '.1f') for x in np.percentile(v, [10, 50, 90]))} (n {len(v)})" for t, v in pk.items()) + ".\n")
    # 1b
    for truth in ("GT1", "GT3"):
        print(f"## 1b. Recall by episode duration and peak queue delay, {truth} (v2; start rule | overlap)\n")
        print("| type | AQM | all | " + " | ".join(gt_score.BIN_LABELS) + " | " + " | ".join(f"peak {a}-{b if b < 1e8 else ''} ms" for a, b in Q_BINS) + " |")
        print("|---|---|---|" + "---|" * (len(DUR_BINS) + len(Q_BINS)))
        for r in R:
            if r["type"].startswith("calm"):
                continue
            eps = [e for e in r["episodes"] if e["truth"] == truth and e["client"] != "sub-ctrl"]
            cells = [f"{rec(eps, 'v2_start')} \\| {rec(eps, 'v2_overlap')}"]
            for lo, hi in DUR_BINS:
                sel = [e for e in eps if lo <= e["dur"] < hi]
                cells.append(f"{rec(sel, 'v2_start')} \\| {rec(sel, 'v2_overlap')}" if sel else "-")
            for lo, hi in Q_BINS:
                sel = [e for e in eps if lo <= e["peak_ms"] < hi]
                cells.append(f"{rec(sel, 'v2_start')} \\| {rec(sel, 'v2_overlap')}" if sel else "-")
            print(f"| {r['type']} | {r['aqm']} | " + " | ".join(cells) + " |")
        print()
    # 1c
    print("## 1c. GT1 episodes against frame-latency harm (v2, start rule)\n")
    print("| type | AQM | missed: with harm / without | detected: with harm / without | recall on harmful episodes | recall on harmful >= 1 s |")
    print("|---|---|---|---|---|---|")
    for r in R:
        if r["type"].startswith("calm"):
            continue
        eps = [e for e in r["episodes"] if e["truth"] == "GT1" and e["client"] != "sub-ctrl"]
        m = [e for e in eps if not e["v2_start"]]
        dd = [e for e in eps if e["v2_start"]]
        h = [e for e in eps if e["harm"]]
        hl = [e for e in h if e["dur"] >= 1]
        print(f"| {r['type']} | {r['aqm']} | {sum(e['harm'] for e in m)} / {sum(not e['harm'] for e in m)} | "
              f"{sum(e['harm'] for e in dd)} / {sum(not e['harm'] for e in dd)} | {rec(h, 'v2_start')} | {rec(hl, 'v2_start')} |")
    print()
    # 1d
    print("## 1d. Precision and false alarms (GT1 view, gt_score)\n")
    print("| type | AQM | v2: episodes, recall, precision, FA per client-min | v2-fixed: same |\n|---|---|---|---|")
    for r in R:
        cells = []
        for det in DETS:
            t = r["score_gt1"][det]
            cells.append(f"{t['episodes']}, {f2(t['detected'] / t['episodes'] if t['episodes'] else None)}, "
                         f"{f2(t['tp'] / (t['tp'] + t['fp']) if t['tp'] + t['fp'] else None)}, "
                         f"{f2(t['fp'] / (t['clear_s'] / 60) if t['clear_s'] else None, '.3f')}")
        print(f"| {r['type']} | {r['aqm']} | " + " | ".join(cells) + " |")
    print()
    # 2
    print("## 2. Detector state (v2: learned; v2-fixed: frozen calm statistics)\n")
    print("Per run, median over clients (sub-ctrl excluded) of the per-client medians over time. Baseline above "
          "queue-free = base + mu_F1 - min OWD of the run (ms). Sensitivity = sustained queueing delay above the "
          "queue-free delay that the F1 term alone needs to alarm within 1 s / 0.5 s.\n")
    print("| type | AQM | det | baseline above queue-free p50 ms | share of time above 1 / 2 / 5 / 10 ms | noise sigma p50 / p90 ms | sensitivity 1 s / 0.5 s ms |")
    print("|---|---|---|---|---|---|---|")
    for r in R:
        for det in DETS:
            xs = [v for k, v in r["state"].items() if k.startswith(det + "|") and not k.endswith("sub-ctrl") and v["mu_p50"] is not None]
            if not xs:
                continue
            md = lambda key: float(np.median([x[key] for x in xs]))
            sh = {k_: float(np.median([x["above_share"][k_] for x in xs])) for k_ in ("1", "2", "5", "10")}
            se = {k_: float(np.median([x["sens_ms"][k_] for x in xs])) for k_ in ("1.0", "0.5")}
            print(f"| {r['type']} | {r['aqm']} | {det} | {md('above_p50'):.2f} | " + " / ".join(f"{sh[k_]:.2f}" for k_ in ("1", "2", "5", "10"))
                  + f" | {md('sig_p50'):.2f} / {md('sig_p90'):.2f} | {se['1.0']:.1f} / {se['0.5']:.1f} |")
    print()
    print("## 2d. v2-fixed against v2 by duration (GT1, start rule)\n")
    print("| type | AQM | det | all | " + " | ".join(gt_score.BIN_LABELS) + " |\n|---|---|---|---|" + "---|" * len(DUR_BINS))
    for r in R:
        if r["type"].startswith("calm"):
            continue
        eps = [e for e in r["episodes"] if e["truth"] == "GT1" and e["client"] != "sub-ctrl"]
        for det in DETS:
            print(f"| {r['type']} | {r['aqm']} | {det} | {rec(eps, det + '_start')} | " + " | ".join(
                (lambda sel: rec(sel, det + "_start") if sel else "-")([e for e in eps if lo <= e["dur"] < hi]) for lo, hi in DUR_BINS) + " |")
    print()
    # 3
    print("## 3b. Missed GT1 episodes of >= 1 s (v2, start rule): classes\n")
    print("| type | AQM | missed >= 1 s | never moved | rose and drained | crossed late | other |\n|---|---|---|---|---|---|---|")
    allc = Counter()
    drain = defaultdict(list)
    for r in R:
        eps = [e for e in r["episodes"] if e.get("class")]
        c = Counter(e["class"] for e in eps)
        if r["type"] in ("ppbp", "burstcap"):
            allc.update({(r["type"], k): v for k, v in c.items()})
        for e in eps:
            if e["class"] == "drained":
                drain[r["type"]].append(e["class_info"])
        print(f"| {r['type']} | {r['aqm']} | {len(eps)} | {c['never moved']} | {c['drained']} | {c['crossed late']} | {c['other']} |")
    print("\n## 3c. What drained the statistic (drained class)\n")
    for t, infos in drain.items():
        if not infos:
            continue
        tot = Counter()
        for x in infos:
            for f, v in x["neg_by_feature"].items():
                tot[f] += v
        print(f"- {t}: {len(infos)} episodes; drain ticks per episode p50 {np.median([x['drain_ticks'] for x in infos]):.0f}; "
              f"negative contribution by term (sum over episodes): " + ", ".join(f"{f} {v:.0f}" for f, v in sorted(tot.items(), key=lambda x: x[1])))


# ═══ plots ═════════════════════════════════════════════════════════════

def main_plots(path, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    R = [json.loads(x) for x in open(path) if x.strip()]
    cand = [(r["run"], e) for r in R if r["type"] == "ppbp" for e in r["episodes"] if e.get("class")]
    rng = random.Random(SEED)
    pick = rng.sample(cand, min(10, len(cand)))
    for n, (runname, e) in enumerate(pick, 1):
        rd = BASE / "M1" / runname
        run = d.Run(rd)
        dets, g_ref = detector(run, "v2")
        df, r, spans = dets[e["client"]]
        t = r["t"]
        lo, hi = e["a"] - 5, e["b"] + 5
        m = (t >= lo) & (t <= hi)
        owd = (df["F1"] + df["base"]).to_numpy()
        harms = [x for x in st0.harm_times(run, e["client"]) if lo <= x <= hi]
        fig, ax = plt.subplots(3, 1, figsize=(9, 6), sharex=True)
        ax[0].plot(t[m], owd[m], lw=0.8)
        ax[0].set_ylabel("OWD tick min ms")
        ax[1].plot(t[m], r["G"][m], lw=0.8, color="C1")
        ax[1].axhline(s3.THETA_ON * 2 * g_ref["v2"], ls="--", color="0.3", lw=0.8)
        ax[1].set_ylabel("CUSUM G")
        ax[2].plot(t[m], r["score"][m], lw=0.8, color="C2")
        ax[2].axhline(s3.THETA_ON, ls="--", color="0.3", lw=0.8)
        ax[2].set_ylabel("score")
        for a_ in ax:
            a_.axvspan(e["a"], e["b"], color="C3", alpha=0.15)
            for h in harms:
                a_.axvline(h, color="C4", lw=0.4, alpha=0.6)
        for x, y, _ in spans:
            if x <= hi and y >= lo:
                ax[2].axvspan(max(x, lo), min(y, hi), color="C2", alpha=0.15)
        ax[2].set_xlabel("run time s")
        fig.suptitle(f"{runname} {e['client']}: GT1 {e['a']:.1f}-{e['b']:.1f} s ({e['dur']:.1f} s, peak {e['peak_ms']} ms), "
                     f"class {e['class']}; red = GT1, purple = harm, green = alarm", fontsize=8)
        fig.tight_layout()
        f = Path(out_dir) / f"missed{n}.png"
        fig.savefig(f, dpi=110)
        plt.close(fig)
        print(f, e["class"])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "run":
        main_run()
    elif cmd == "sum":
        main_sum(sys.argv[2])
    else:
        main_plots(sys.argv[2], sys.argv[3])
