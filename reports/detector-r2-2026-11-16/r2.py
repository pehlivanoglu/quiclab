#!/usr/bin/env python3
"""R2: detector baselines and ablation (replay-studies-spec.md, R2). Existing v3 runs only; the frozen detector is
not changed (variants are registered at run time in this process, never in scripts/).

    nice -n 19 .venv/bin/python3 reports/detector-r2-2026-11-16/r2.py fit            # G_ref per ablation variant
    nice -n 19 .venv/bin/python3 reports/detector-r2-2026-11-16/r2.py rows --jobs 4  # rows.jsonl, contrib.jsonl
    .venv/bin/python3 reports/detector-r2-2026-11-16/r2.py report   # its output is the appendix of README.md

Scoring is reports/v3-detector/score_runs.py's, unchanged: GT1 / GT2 / GT3 source B through gt_score (TP = first
alarm start in [t_on - 1 s, min(end, t_on + 10 s)], false alarms = starts in CLEAR time), alarm-on recall,
GT-Q / GT-H through gtq_score, and "on at t_harm" as reports/v3-score/harm.py (an alarm span covers t_harm_600).

Detectors (all on the OWD signals of the frozen detector unless stated):
  v2-owd                frozen (scripts/shadow_v2_frozen.py)
  abl:*                 ablation of the frozen structure, one change each; G_ref refitted per variant by the
                        frozen rule (smallest multiple of the calm max G with <= 0.1 FA/min of GT3 CLEAR time) on the
                        v3 calm pfifo-r1 runs s030u070 / s065u070 (FLAG: the ip4 calm runs used for the frozen fit
                        are no longer on disk); abl:ref = the frozen structure refitted the same way
  D1-bw / D1-pacing / D1-cwnd   BBR's own state falls below 0.9 x its max over the last 5 s (v1 rule,
                        shadow/Detector.cpp bbrDropFraction 0.1, bbrDropLookbackUs 5 s; FLAG); pacing first takes
                        the max over the trailing PACING_W (one ProbeBW gain cycle = 8 x min RTT; T, FLAG)
  D2-gcc                libwebrtc GCC delay-based detector (gcc.py), packets with a known arrival time (the largest
                        acked packet of each ACK: acks.csv sent_mono_us + owd_us), 5 ms send-time groups
  D2-gcc-frame          the same on frames (client frames.csv send_us / recv_us; recv = application delivery)
  D2-v1-gcc[-floorX]    the old v1 replay's GCC variant (shadow/ replay, OWD acks), floor_window_ms X in
                        {500 (m4), 350, 200, 0 (TUNED)}: the v1 detector's trailing-minimum window on the delay
  D3-X-Y                F1 (the frozen detector's queue delay, ms) > X for Y continuously; X 5 / 10 / 20 ms,
                        Y 100 / 200 / 500 ms (P)
  D4-rfc8382            RFC 8382 section 3.3.1 step 1 bottleneck test per flow (T 0.35 s, N 50, M 30, c_s 0.1,
                        c_h 0.3 from section 2.2; p_l 0.05 from the FlowBot repo's sbd.py, FLAG: the RFC gives none)
  D4-rfc8382-noloss     the same without the pkt_loss term
  D5-v1                 Shadow v1 (det_eval.TUNED replay, pre_signal_on), OWD acks
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))

KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
CALM_FIT = ("v3-C1a-calm-s030u070-pfifo-r1", "v3-C1a-calm-s065u070-pfifo-r1")   # (FLAG) v3 stand-ins for calm030/065
GREF_FILE = HERE / "gref.json"
BBR_DROP, BBR_LOOKBACK_S = 0.1, 5.0         # (FLAG) v1 rule, shadow/Detector.h bbrDropFraction / bbrDropLookbackUs
PACING_W_CYCLES = 8                         # (T, FLAG) pacing max window = 8 x min RTT (one ProbeBW gain cycle)
D3_X, D3_Y = (5.0, 10.0, 20.0), (0.1, 0.2, 0.5)   # (P)
RFC = {"T": 0.35, "N": 50, "M": 30, "c_s": 0.1, "c_h": 0.3, "p_l": 0.05}   # RFC 8382 sec 2.2; p_l FlowBot sbd.py
V1_FLOORS = (500, 350, 200, 0)              # floor_window_ms rows of the old v1 GCC variant

FROZEN_LABEL = "fuse d: s1+s2+s3+sL +hold gate:level+cap"
ABL = {   # name -> (fusion features, gate kind, gate cap, hold, masks on)
    "abl:ref": (("F1", "F2", "F3"), "level", True, True, True),
    "abl:F1-only": (("F1",), "off", False, True, True),
    "abl:F2-only": (("F2",), "off", False, True, True),
    "abl:F3-only": (("F3",), "off", False, True, True),
    "abl:L-only": ((), "open", False, True, True),
    "abl:no-F2": (("F1", "F3"), "level", True, True, True),
    "abl:no-F3": (("F1", "F2"), "level", True, True, True),
    "abl:no-loss": (("F1", "F2", "F3"), "off", False, True, True),
    "abl:no-gate": (("F1", "F2", "F3"), "open", False, True, True),
    "abl:no-hold": (("F1", "F2", "F3"), "level", True, False, True),
    "abl:no-masks": (("F1", "F2", "F3"), "level", True, True, False),
}


def _setup():
    """Frozen OWD floors, and the ablation labels registered in shadow_v2_step3's tables (this process only)."""
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    fit = fz.FROZEN["OWD"]
    s3.FLOORS.clear()
    s3.FLOORS.update(fit["floors"])
    s3.FIXED_STATS.clear()
    s3.FIXED_STATS.update(fit["stats"])
    for name, (feats, kind, cap, hold, _m) in ABL.items():
        s3.LOSS[name] = ("fuse", ("sum", feats))
        s3.GATE[name] = (kind, cap, True)
        if hold:
            s3.HOLD.add(name)
    return fz, s3


def flows(run):
    fz, s3 = _setup()
    return {s: s3.load_flow(f) for s, f in fz.tick_files(run, "OWD").items()}


def cusum(df, label, gref, masks=True):
    _, s3 = _setup()
    if not masks:
        df = df.copy()
        df["masked"] = False
    return s3.run_cusum(df, label, gref, False)


# ---------------------------------------------------------------- G_ref fit (frozen rule)

def cmd_fit() -> None:
    import det_eval as d
    import gt3
    import gt_score
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    _setup()
    runs = [d.Run(KDIR / n) for n in CALM_FIT]
    fl = {r.path.name: flows(r) for r in runs}
    views = {}
    for r in runs:
        e3, l3 = gt3.run_truth(r, gt3.Params(), source="B")
        views[r.path.name] = gt3.view_of(r, e3, l3, need_path=True)
    out = {}
    for name, (_f, _k, _c, _h, masks) in ABL.items():
        gmax = 0.0
        for r in runs:
            for s, df in fl[r.path.name].items():
                res = cusum(df, name, None, masks)
                if res["armed"] is not None:
                    gmax = max(gmax, float(res["G"][res["armed"]:].max()))
        chosen = s3.GREF_MULT[-1] * gmax
        for m in s3.GREF_MULT:
            fa = clear = 0.0
            for r in runs:
                starts = {("x", s): [a for a, _, _ in s5.on_spans(cusum(df, name, m * gmax, masks), s3.THETA_ON)]
                          for s, df in fl[r.path.name].items()}
                tl = gt_score.score(r, views[r.path.name], starts, ("x",))["x"]
                fa, clear = fa + tl["fp"], clear + tl["clear_s"]
            if clear and fa / (clear / 60) <= 0.1:
                chosen = m * gmax
                break
        out[name] = {"g_ref": round(chosen, 3), "g_max": round(gmax, 3)}
        print(name, out[name], flush=True)
    GREF_FILE.write_text(json.dumps(out, indent=1))


# ---------------------------------------------------------------- baselines

def runs_cross(t, cond):
    """Rising / falling edges of a boolean series on times t -> [(start, end)]."""
    out, start = [], None
    for x, c in zip(t, cond):
        if c and start is None:
            start = x
        elif not c and start is not None:
            out.append((start, x))
            start = None
    if start is not None:
        out.append((start, math.inf))
    return out


def drop_rule(t, x, frac=BBR_DROP, look=BBR_LOOKBACK_S):
    """x below (1 - frac) x its max over the trailing look seconds (monotone deque)."""
    from collections import deque
    dq, cond = deque(), []
    for ti, xi in zip(t, x):
        while dq and dq[-1][1] <= xi:
            dq.pop()
        dq.append((ti, xi))
        while dq[0][0] < ti - look:
            dq.popleft()
        cond.append(xi < (1 - frac) * dq[0][1])
    return runs_cross(t, cond)


def trailing_max(t, x, w):
    from collections import deque
    dq, out = deque(), []
    for ti, xi in zip(t, x):
        while dq and dq[-1][1] <= xi:
            dq.pop()
        dq.append((ti, xi))
        while dq[0][0] < ti - w:
            dq.popleft()
        out.append(dq[0][1])
    return np.array(out)


def d1(run, s):
    import pandas as pd
    a = pd.read_csv(run.sender_file(s, "acks"), usecols=["mono_us", "bbr_bw_bps", "min_rtt_us"])
    a = a[a.bbr_bw_bps > 0]
    out = {}
    if len(a):
        t = np.array([run.t_mono_us(x) for x in a.mono_us.values])
        out["D1-bw"] = drop_rule(t, a.bbr_bw_bps.values.astype(float))
    c = pd.read_csv(run.sender_file(s, "cc"), usecols=["t_us", "pacing_bps", "cwnd_bytes", "min_rtt_us"])
    t = np.array([run.t_unix_us(x) for x in c.t_us.values])
    mrtt = float(np.nanmedian(c.min_rtt_us[c.min_rtt_us > 0])) / 1e6 if (c.min_rtt_us > 0).any() else 0.05
    p = c.pacing_bps.values.astype(float)
    ok = p > 0
    if ok.any():
        out["D1-pacing"] = drop_rule(t[ok], trailing_max(t[ok], p[ok], PACING_W_CYCLES * mrtt))
    w = c.cwnd_bytes.values.astype(float)
    ok = w > 0
    if ok.any():
        out["D1-cwnd"] = drop_rule(t[ok], w[ok])
    out["_pacing_w_s"] = PACING_W_CYCLES * mrtt
    return out


def d2(run, s):
    import gcc
    import pandas as pd
    a = pd.read_csv(run.sender_file(s, "acks"), usecols=["sent_mono_us", "owd_us"]).dropna()
    a = a[(a.owd_us > 0) & (a.sent_mono_us > 0)].drop_duplicates("sent_mono_us")
    pk = [(x / 1000, (x + o) / 1000, 1200) for x, o in zip(a.sent_mono_us.values, a.owd_us.values)]
    st = gcc.detect(pk)
    ep = [(run.t_mono_us(x * 1000), run.t_mono_us(y * 1000) if y != math.inf else math.inf) for x, y in gcc.episodes(st)]
    out = {"D2-gcc": ep}
    f = run.path / "clients" / f"{s}-frames.csv"
    if f.exists():
        fr = pd.read_csv(f, usecols=["send_us", "recv_us", "size"]).dropna()
        st = gcc.detect([(x / 1000, y / 1000, z) for x, y, z in zip(fr["send_us"], fr["recv_us"], fr["size"])])
        out["D2-gcc-frame"] = [(run.t_unix_us(x * 1000), run.t_unix_us(y * 1000) if y != math.inf else math.inf)
                               for x, y in gcc.episodes(st)]
    return out


def d3(df):
    t = df.t.to_numpy()
    f1 = df.F1.to_numpy()
    out = {}
    for X in D3_X:
        cond = np.nan_to_num(f1, nan=-1) > X
        spans = runs_cross(t, cond)
        for Y in D3_Y:
            out[f"D3-{X:g}ms-{int(Y * 1000)}ms"] = [(a + Y, b) for a, b in spans if b - a >= Y]
    return out


def d4(run, s, with_loss=True):
    """RFC 8382 3.3.1 step 1 per flow, on the per-ACK OWD samples; evaluated every T."""
    import pandas as pd
    a = pd.read_csv(run.sender_file(s, "acks"), usecols=["mono_us", "owd_us", "newly_lost"]).dropna()
    a = a[a.owd_us > 0]
    if len(a) < 10:
        return []
    t = np.array([run.t_mono_us(x) for x in a.mono_us.values])
    owd = a.owd_us.values / 1000.0
    lost = a.newly_lost.values
    T, N, M = RFC["T"], RFC["N"], RFC["M"]
    k = np.floor(t / T).astype(int)
    out_t, cond = [], []
    means, skew_b, var_b, cnt, loss_n, pk_n = [], [], [], [], [], []
    pb = False
    for i in range(k.min(), k.max() + 1):
        m = k == i
        x = owd[m]
        prev_mean = means[-1] if means else None
        mean_delay = float(np.mean(means[-M:])) if means else None      # excludes the current interval
        if len(x):
            sb = float(np.sum(x < mean_delay) - np.sum(x > mean_delay)) if mean_delay is not None else 0.0
            vb = float(np.sum(np.abs(x - prev_mean))) if prev_mean is not None else 0.0
            means.append(float(np.mean(x)))
        else:
            sb, vb = 0.0, 0.0
        skew_b.append(sb)
        var_b.append(vb)
        cnt.append(len(x))
        loss_n.append(float(lost[m].sum()))
        pk_n.append(float(len(x)) + float(lost[m].sum()))
        if len(cnt) < M:
            continue
        skew_est = sum(skew_b[-M:]) / max(1, sum(cnt[-M:]))
        pkt_loss = sum(loss_n[-N:]) / max(1.0, sum(pk_n[-N:]))
        pb = skew_est < RFC["c_s"] or (skew_est < RFC["c_h"] and pb) or (with_loss and pkt_loss > RFC["p_l"])
        out_t.append((i + 1) * T)
        cond.append(pb)
    return runs_cross(out_t, cond)


def v1_replay(run, tmp: Path):
    import det_eval as d
    import grouping_adapter as ga
    import owd_mode
    acks = {s: owd_mode.owd_acks(run, s, tmp) for s in run.subs}
    out = defaultdict(dict)
    rows = [("D5-v1", d.TUNED, "full")] + [(f"D2-v1-gcc-floor{f}", {**d.PARAMS, "floor_window_ms": f}, "gcc")
                                          for f in V1_FLOORS]
    for name, params, variant in rows:
        events = d.replay(run, params, acks=acks)
        for s in run.subs:
            ev = sorted((e for e in events if e["subscriber"] == s and e["variant"] == variant), key=lambda e: e["t"])
            sp, start = [], None
            for e in ev:
                if e["event"] == ga.ON and start is None:
                    start = e["t"]
                elif e["event"] == ga.OFF and start is not None:
                    sp.append((start, e["t"]))
                    start = None
            if start is not None:
                sp.append((start, math.inf))
            out[name][s] = sp
    return out


# ---------------------------------------------------------------- per-signal contribution

def contribution(run, s, r, gt3_starts):
    """At each alarm start of the frozen detector: share of G from F1, F2, F3 and gated loss over the excursion
    (last G = 0 to the alarm tick; ticks where the hold rule zeroed a negative step contribute nothing). And after
    each GT3 onset: the first tick each signal reaches z >= 1 (zc = s_f / 2 + 1)."""
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    t, G, sf = np.asarray(r["t"]), np.asarray(r["G"]), r["s_f"]
    feats = ("F1", "F2", "F3")
    out = {"alarms": [], "onsets": []}
    for a, _, onset in s5.on_spans(r, s3.THETA_ON):
        k1 = int(np.searchsorted(t, a))
        zero = np.flatnonzero(G[:k1] == 0)
        k0 = int(zero[-1]) if len(zero) else 0
        con = {f: 0.0 for f in (*feats, "loss")}
        for k in range(k0 + 1, k1 + 1):
            step = G[k] - G[k - 1]
            fused = sum(np.nan_to_num(sf[f][k]) for f in feats)
            if step == 0 and fused < 0:
                continue                                   # hold zeroed a negative step (or no change)
            for f in feats:
                con[f] += float(np.nan_to_num(sf[f][k]))
            con["loss"] += float(step - fused)
        g = float(G[k1]) if k1 < len(G) else float("nan")
        out["alarms"].append({"t": float(a), "G": g, **{f: con[f] / g if g else None for f in con}})
    zc = {f: np.asarray(sf[f]) / 2 + 1 for f in (*feats, "L")}
    for on in gt3_starts:
        k0 = int(np.searchsorted(t, on))
        first = {}
        for f in zc:
            idx = np.flatnonzero(np.nan_to_num(zc[f][k0:k0 + 300], nan=-9) >= 1)
            first[f] = int(idx[0]) if len(idx) else None
        out["onsets"].append({"t": float(on), "first_tick": first})
    return out


# ---------------------------------------------------------------- one run

def worker(rd: Path) -> dict:
    try:
        return _worker(rd)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path) -> dict:
    import det_eval as d
    import gt1
    import gt2
    import gt3
    import gt_score
    import gtq_score
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    _setup()
    gref = json.loads(GREF_FILE.read_text())
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    fl = flows(run)
    spans: dict[str, dict] = defaultdict(dict)
    # frozen + ablation
    frozen = {}
    for s, df in fl.items():
        r = s3.run_cusum(df, FROZEN_LABEL, fz.FROZEN["OWD"]["g_ref"]["v2"], False)
        frozen[s] = r
        spans["v2-owd"][s] = [(a, b) for a, b, _ in s5.on_spans(r, s3.THETA_ON)]
        for name, (_f, _k, _c, _h, masks) in ABL.items():
            spans[name][s] = [(a, b) for a, b, _ in s5.on_spans(cusum(df, name, gref[name]["g_ref"], masks), s3.THETA_ON)]
        for name, sp in d3(df).items():
            spans[name][s] = sp
    pacing_w = {}
    for s in run.subs:
        x = d1(run, s)
        pacing_w[s] = x.pop("_pacing_w_s")
        for name, sp in x.items():
            spans[name][s] = sp
        for name, sp in d2(run, s).items():
            spans[name][s] = sp
        spans["D4-rfc8382"][s] = d4(run, s, True)
        spans["D4-rfc8382-noloss"][s] = d4(run, s, False)
    with tempfile.TemporaryDirectory() as tmp:
        for name, per in v1_replay(run, Path(tmp)).items():
            spans[name].update(per)
    names = tuple(spans)
    starts = {(n, s): [a for a, _ in v] for n, per in spans.items() for s, v in per.items()}
    sp2 = {(n, s): v for n, per in spans.items() for s, v in per.items()}
    # truths and scores (as reports/v3-detector/score_runs.py)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    hop1 = [(e["hop"], e["start_s"], e["end_s"]) for e in e1]
    hop2 = [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2]
    views = {"GT1": gt_score.client_view(run, hop1, l1), "GT2": gt_score.client_view(run, hop2, l2),
             "GT3": gt3.view_of(run, eb, lb, need_path=True)}
    sys.path.insert(0, str(ROOT / "reports" / "v3-detector"))
    import score_runs as sr
    score = {}
    for tname, v in views.items():
        sc = gt_score.score(run, v, starts, names)
        for n in names:
            sc[n].update(sr.alarm_on(v, sp2, n))
        score[tname] = sc
    gq = None
    if (rd / "truth" / "gtq.csv").exists():
        import gtq
        gtq_score.DETECTORS = names
        keep = gtq.write
        gtq.write = lambda *a, **k: None   # score_run would overwrite the run's truth/gtq-score-episodes.csv
        try:
            res = gtq_score.score_run(rd, starts)
        finally:
            gtq.write = keep
        if res is not None:
            gq = res[1]
    harm = on_at_harm(run, rd, sp2, names)
    # contribution (frozen detector)
    g3 = {s: [a for a, _ in eps] for s, (eps, _) in views["GT3"].items()}
    contrib = {s: contribution(run, s, r, [a for a in g3.get(s, []) if a >= d.WARMUP_S]) for s, r in frozen.items()}
    parts = rd.name.split("-")
    cc = "copa" if "copa" in rd.name else "bbr"
    return {"run": rd.name, "block": parts[1], "type": parts[2], "variant": parts[3], "aqm": parts[4],
            "rep": int(parts[5][1:]), "topology": plan["topology"], "cc": cc, "duration_s": run.duration,
            "clients": len(run.subs), "score": score, "gtq": gq, "harm": harm, "pacing_w_s": pacing_w,
            "contrib": contrib, "windows": json.loads((rd / "grouping" / "windows.json").read_text())
            if (rd / "grouping" / "windows.json").exists() else []}


def on_at_harm(run, rd, sp2, names) -> dict:
    import det_eval as d
    if not (rd / "truth" / "gtq.csv").exists():
        return {}
    eps = d.rows(rd / "truth" / "gtq.csv")
    out = {n: [0, 0] for n in names}
    for e in eps:
        if e.get("direction") != "forward" or e.get("harmful_600") != "1":
            continue
        th = float(e["t_harm_600"])
        if th < d.WARMUP_S:
            continue
        for n in names:
            out[n][1] += 1
            out[n][0] += any(a <= th <= b for a, b in sp2.get((n, e["flow"]), []))
    return out


def runs() -> list[Path]:
    return sorted(p for p in KDIR.iterdir() if p.is_dir() and p.name.startswith("v3-") and (p / "events.csv").exists())


def cmd_rows(jobs: int, only: str | None = None) -> None:
    rs = [r for r in runs() if not only or only in r.name]
    out = HERE / "rows.jsonl"
    print(f"{len(rs)} runs", flush=True)
    with out.open("w") as fh, Pool(jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(worker, rs), 1):
            fh.write(json.dumps(row, default=lambda o: None if (isinstance(o, float) and not math.isfinite(o)) else
                                str(o)) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {row['run']}{' ERROR ' + row['error'] if 'error' in row else ''}", flush=True)


def main(argv: list[str]) -> int:
    if argv[0] == "fit":
        cmd_fit()
    elif argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 4,
                 argv[argv.index("--only") + 1] if "--only" in argv else None)
    elif argv[0] == "one":
        row = worker(KDIR / argv[1])
        if "error" in row:
            print(row["tb"])
        else:
            for n, v in row["score"]["GT3"].items():
                print(n, {k: v.get(k) for k in ("tp", "fn", "fp", "episodes", "alarm_on", "clear_s")})
    elif argv[0] == "report":
        import r2_report
        r2_report.report(HERE / "rows.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
