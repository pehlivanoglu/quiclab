#!/usr/bin/env python3
"""Stage B: the section-5 measures on every testbed / simulation pair, reps side by side.

    python3 simulation/simlab/stageb_compare.py [matched|spec] [applimited|v1]   # -> reports/sim-stageB2-applimited/ (or the v1 folder)

Read-only on testbed runs: only pure functions of the frozen code are called in-process
(gt3.run_truth / view_of, gt_score.score, the R2 baseline rule d1, gt1.router_egresses,
det_eval), and the frozen detector through simlab/frozen.py (tick cache under reports/sim-cache).

Measures (spec section 5; the user's addition of 2026-11-18 first):
  onset spread       per leaf and stimulus (windows.json: target, expected members): first alarm
                     onset (frozen episode t_onset) of each member in [start - 1 s, start + 10 s];
                     spread = max - min over the members with an onset (>= 2); p50 / p90 / p99
  keyframe q peak    per sampled egress except the control client's: queue delay (backlog x 8 / C,
                     5 ms queue CSV) maximum per 1 s GOP block in calm time; p50 / p90 of the block maxima
  F1 calm            the frozen detector's F1 (queue delay, ms) on unmasked ticks in calm time,
                     pooled over video clients: mean, sigma
  GT3 (source A)     both sides from per-packet OWD (spec 4: frame times are distorted by TCP HOL;
                     FLAG: the frozen detector tables use source B); v2-owd and D1-bw scored with
                     gt_score: precision, recall, false alarms / min, delay p50 / p90
  D1-bw reaction     D1-bw's delay p50 on GT3-A (the R2 definition: BBR bandwidth estimate below
                     0.9 x its 5 s max)
  no limit           GOP drops per client-minute, video rate in stimulus windows / nominal
Calm time: outside every stimulus window widened by [-1 s, +3 s], after the 5 s warm-up.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(QUICLAB / "reports" / "detector-r2-2026-11-16"))
sys.path.insert(0, str(QUICLAB / "reports" / "sets-low-threshold-2026-11-16"))
import frozen  # noqa: E402  (patches the tick cache before anything else imports it)
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import r2  # noqa: E402
import stageb  # noqa: E402

OUT_DIR = {"v1": QUICLAB / "reports" / "sim-stageB-2026-11-18", "applimited": QUICLAB / "reports" / "sim-stageB2-applimited",
           "codelfix": QUICLAB / "reports" / "sim-stageB2-codelfix",
           "streams": QUICLAB / "reports" / "sim-stageB2-streams",
           "pie-streams": QUICLAB / "reports" / "sim-stageB2-piestreams"}
CTRL = "sub-ctrl"
LIMITS = {   # spec section 5 (P); relative limits as fractions
    "q_peak_p50_ms": ("rel", 0.20), "f1_mean": ("rel", 0.30), "f1_sigma": ("rel", 0.30),
    "v2_delay_p50_ms": ("rel_or_tick", 0.30), "gt3_p": ("min", 0.98), "gt3_r": ("abs", 0.05),
    "spread_p50_ms": ("rel_or_tick", 0.30), "spread_p90_ms": ("rel_or_tick", 0.30), "d1bw_delay_p50_ms": ("rel", 0.30),
}
# User decision 2026-11-18 (deviation, recorded in NOTES.md): onset spread and detection delay are quantised to the
# detector's tick; agreement = within 30 % OR within one tick, whichever is wider. No other criterion changes.
TICK_MS = 33.0


def windows(rd: Path) -> list[dict]:
    p = rd / "grouping" / "windows.json"
    return json.loads(p.read_text()) if p.exists() else []


def calm_mask(t: np.ndarray, wins: list[dict], duration: float) -> np.ndarray:
    m = (t >= d.WARMUP_S) & (t <= duration - d.SHUTDOWN_S)
    for w in wins:
        m &= ~((t >= w["start"] - 1.0) & (t <= w["end"] + 3.0))
    return m


def pct(x, q):
    return float(np.percentile(x, q)) if len(x) else math.nan


def measure(rd: Path, side: str, cfg_from: Path) -> dict:
    run = d.Run(rd)
    wins = windows(rd)
    video = [s for s in run.subs if s != CTRL]
    out: dict = {"run": rd.name, "clients": len(video)}

    # detector episodes and onset spread
    eps = frozen.episodes(rd)
    spreads, hits = [], []
    for w in wins:
        members = [m for m in w.get("expected", []) if m in eps]
        on = [min((o for a, b, o in eps[m] if w["start"] - 1.0 <= o <= w["start"] + 10.0), default=None) for m in members]
        on = [o for o in on if o is not None]
        hits.append(len(on) / max(1, len(members)))
        if len(on) >= 2:
            spreads.append(1000 * (max(on) - min(on)))
    out.update(spread_n=len(spreads), spread_p50_ms=pct(spreads, 50), spread_p90_ms=pct(spreads, 90),
               spread_p99_ms=pct(spreads, 99), stim_member_hit=float(np.mean(hits)) if hits else math.nan)

    # keyframe queue peak in calm time, per sampled egress
    caps = d.capacity_series(run)
    qpk = {}
    for hop, csv in gt1.router_egresses(run):
        if hop[1] == CTRL:
            continue
        qcsv = csv.with_name(csv.stem + "-queue.csv")
        if not qcsv.exists():
            continue
        q = pd.read_csv(qcsv)
        t = np.array([run.t_mono_us(x / 1000) for x in q.timestamp_mono_ns.values])
        cap = d.value_at(caps[hop], 0.0) * 1e6
        delay = q.queue_backlog_bytes.values * 8 / cap * 1000
        m = calm_mask(t, wins, run.duration)
        if not m.any():
            continue
        blocks = pd.Series(delay[m]).groupby(np.floor(t[m]).astype(int)).max()
        qpk[f"{hop[0]}->{hop[1]}"] = {"p50": float(blocks.median()), "p90": float(blocks.quantile(0.9)), "n": len(blocks)}
    out["q_peak"] = qpk
    out["q_peak_p50_ms"] = float(np.median([v["p50"] for v in qpk.values()])) if qpk else math.nan

    # F1 in calm time
    ticks = frozen.fz.tick_files(run, "OWD")
    f1 = []
    for s in video:
        tk = pd.read_csv(ticks[s], usecols=["t", "F1", "masked", "no_data"])
        m = calm_mask(tk.t.values, wins, run.duration) & ~tk.masked.astype(bool).values & ~tk.no_data.astype(bool).values
        f1.append(tk.F1.values[m])
    f1 = np.concatenate(f1) if f1 else np.array([])
    f1 = f1[~np.isnan(f1)]
    out.update(f1_mean=float(f1.mean()) if len(f1) else math.nan, f1_sigma=float(f1.std()) if len(f1) else math.nan)

    # GT3 source A; v2-owd and D1-bw
    ea, la = gt3.run_truth(run, gt3.Params(), source="A")
    view = {s: v for s, v in gt3.view_of(run, ea, la, need_path=True).items() if s != CTRL}
    starts = {("v2-owd", s): [a for a, _, _ in eps.get(s, [])] for s in video}
    for s in video:
        starts[("D1-bw", s)] = [a for a, _ in r2.d1(run, s).get("D1-bw", [])]   # d1 returns (start, end) spans
    sc = gt_score.score(run, view, starts, ("v2-owd", "D1-bw"))
    for name, key in (("v2-owd", "v2"), ("D1-bw", "d1bw")):
        t = sc[name]
        p = t["tp"] / (t["tp"] + t["fp"]) if t["tp"] + t["fp"] else math.nan
        out.update({f"{key}_episodes": t["episodes"], f"{key}_p": p,
                    f"{key}_r": t["detected"] / t["episodes"] if t["episodes"] else math.nan,
                    f"{key}_fa_min": t["fp"] / (t["clear_s"] / 60) if t["clear_s"] else math.nan,
                    f"{key}_delay_p50_ms": 1000 * pct(t["latency"], 50), f"{key}_delay_p90_ms": 1000 * pct(t["latency"], 90)})
    out["gt3_p"], out["gt3_r"] = out["v2_p"], out["v2_r"]

    # no-limit rows: GOP drops per client-minute, video rate in stimulus windows
    minutes = run.duration / 60
    gops = [pd.read_csv(run.sender_file(s, "drops"))["gop"].nunique() for s in video]
    out["gop_drops_per_client_min"] = float(np.mean(gops)) / minutes
    rates = []
    for s in video:
        fr = pd.read_csv(rd / "clients" / f"{s}-frames.csv", usecols=["size", "recv_us"])
        t = np.array([run.t_unix_us(x) for x in fr.recv_us.values])
        nominal = run.topology["subscribers"][s]["rate_kbps"] * 1000
        for w in wins:
            if s in w.get("expected", []):
                m = (t >= w["start"]) & (t < w["end"])
                rates.append(fr["size"].values[m].sum() * 8 / (w["end"] - w["start"]) / nominal)
    out["rate_in_stimulus"] = float(np.mean(rates)) if rates else math.nan

    # GT3 from frames (source B), testbed side only: the size of the source difference (FLAG)
    if side == "testbed":
        eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
        vb = {s: v for s, v in gt3.view_of(run, eb, lb, need_path=True).items() if s != CTRL}
        t = gt_score.score(run, vb, starts, ("v2-owd",))["v2-owd"]
        out["gt3B_p"] = t["tp"] / (t["tp"] + t["fp"]) if t["tp"] + t["fp"] else math.nan
        out["gt3B_r"] = t["detected"] / t["episodes"] if t["episodes"] else math.nan

    out["keyframe"] = keyframe_table(rd, side, wins)
    out["bbr"] = bbr_stats(run, video)
    out["sets"] = sets_scores(rd, cfg_from)
    return out


def keyframe_table(rd: Path, side: str, wins: list[dict]) -> dict:
    """Part 2's keyframe table (reports/v3-score/part2.py): per egress, keyframe peak (v3_gate.keyframe_peaks),
    keyframe pacing spread (median over the egress's clients of v3_emission key_ms_p50) and the prediction
    0.121 s U (minus the spread). Testbed: the run's own v3-checks.json / v3-emission.json (read only);
    simulation: the same functions on the simulation folder."""
    import v3_emission
    import v3_gate
    plan = json.loads((rd / "v3-plan.json").read_text())
    if side == "testbed":
        kp = json.loads((rd / "v3-checks.json").read_text()).get("keyframe_peaks") or {}
        em = json.loads((rd / "v3-emission.json").read_text()) if (rd / "v3-emission.json").exists() else {}
    else:
        kp = v3_gate.keyframe_peaks(rd, plan, wins)
        em = v3_emission.run_emission(rd)
    out = {}
    for name, k in kp.items():
        e = plan["egress"][name]
        spread = [em[c]["key_ms_p50"] for c in e["clients"] if c in em and em[c].get("key_ms_p50") is not None]
        ref = 121 * (plan["s"] if plan["s"] is not None else 1.0) * plan["U"]
        sp = float(np.median(spread)) if spread else math.nan
        out[name] = {"hop": e["hop"], "p50": k["p50"], "p90": k["p90"], "max": k["max"], "ref_ms": round(ref, 1),
                     "spread_ms": round(sp, 1), "ref_minus_spread_ms": round(ref - sp, 1)}
    out["_pacing_ms_p50"] = {c: v.get("pacing_bps_p50") for c, v in em.items() if isinstance(v, dict)}
    return out


def bbr_stats(run: d.Run, video: list[str]) -> dict:
    """Per client: share of time per BBR mode (acks.csv phase, held until the next ACK row), share of app-limited
    ACK rows, and the pacing gain in effect when each keyframe is written (cc.csv pacing_bps / bw_est_bps, last
    row at or before the frame's write time)."""
    out = {}
    for s in video:
        a = pd.read_csv(run.sender_file(s, "acks"), usecols=["mono_us", "phase", "app_limited"])
        t = a.mono_us.values / 1e6
        dt = np.diff(t, append=t[-1])
        share = pd.Series(dt).groupby(a.phase.values).sum()
        share = (share / share.sum()).round(4).to_dict()
        cc = pd.read_csv(run.sender_file(s, "cc"), usecols=["t_us", "pacing_bps", "bw_est_bps"])
        fr = pd.read_csv(run.sender_file(s, "frames"), usecols=["keyframe", "write_us"])
        kw = fr.write_us.values[fr.keyframe.values == 1]
        i = np.searchsorted(cc.t_us.values, kw, side="right") - 1
        ok = (i >= 0) & (cc.bw_est_bps.values[np.clip(i, 0, None)] > 0)
        gain = cc.pacing_bps.values[i[ok]] / cc.bw_est_bps.values[i[ok]]
        out[s] = {"mode_share": share, "app_limited_rows": round(float(a.app_limited.mean()), 4),
                  "key_gain_p50": round(float(np.median(gain)), 3) if len(gain) else None,
                  "key_gain_p10": round(float(np.percentile(gain, 10)), 3) if len(gain) else None,
                  "key_gain_p90": round(float(np.percentile(gain, 90)), 3) if len(gain) else None}
    return out


def sets_scores(rd: Path, cfg_from: Path) -> dict:
    """Frozen SETS (k = 2, 3) on frozen-detector onsets, scored by grouping_score: R1's level T100 path
    (reports/sets-low-threshold-2026-11-16/r1.py run_level), with the ECG config of the testbed counterpart for
    both sides (the simulation has no live grouping output)."""
    import grouping_adapter as ga
    import shadow_v2_step3 as s3
    import r1
    from grouping import Config
    m = cfg_from / "grouping-d150-v2-owd" / "metrics.json"
    cfg = Config.from_dict(json.loads(m.read_text())["config"]) if m.exists() else Config()

    def onsets_at(rd2: Path, th: float):
        keep = s3.THETA_ON
        s3.THETA_ON = th
        try:
            records, _, onsets = ga.build(rd2, cfg, 0.0, d.WARMUP_S, 0.0, "v2-owd")
        finally:
            s3.THETA_ON = keep
        return cfg, records, onsets

    orig, r1.onsets_at = r1.onsets_at, onsets_at
    try:
        res = r1.run_level(rd, "T100", None)
    finally:
        r1.onsets_at = orig
    return {k: v for k, v in res.get("methods", {}).items() if k.startswith("V k")} | {"n_onsets": res.get("n_onsets")}


def agree(key: str, tb: float, sim: float) -> str:
    kind, lim = LIMITS[key]
    if any(isinstance(v, float) and math.isnan(v) for v in (tb, sim)):
        return "n/a"
    if kind == "rel":
        ok = abs(sim - tb) <= lim * abs(tb) if tb else sim == tb
    elif kind == "rel_or_tick":
        ok = abs(sim - tb) <= max(lim * abs(tb), TICK_MS)
    elif kind == "abs":
        ok = abs(sim - tb) <= lim
    else:
        ok = sim >= lim
    return "ok" if ok else "FAIL"


def main(argv: list[str]) -> None:
    ack = argv[0] if argv else "matched"
    run_set = argv[1] if len(argv) > 1 else "applimited"
    OUT = OUT_DIR[run_set]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, tb, sim, seed in stageb.runs(ack, run_set):
        if not (sim / "sim" / "scored.json").exists():
            print(f"{name}: not run yet, skipped", flush=True)
            continue
        try:
            rows.append({"name": name, "seed": seed, "ack": ack, "testbed": measure(tb, "testbed", tb),
                         "sim": measure(sim, "sim", tb)})
        except Exception as e:  # noqa: BLE001
            rows.append({"name": name, "seed": seed, "error": repr(e)})
        print(f"{name}: done", flush=True)
    with (OUT / f"rows-{ack}.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, default=float) + "\n")
    # tables: one row per run pair, testbed | sim | verdict
    lines = []
    for key in LIMITS:
        lines += [f"\n### {key} (limit: {LIMITS[key][0]} {LIMITS[key][1]})\n", "| run | testbed | sim | agreement |", "|---|---|---|---|"]
        for r in rows:
            if "error" in r:
                lines.append(f"| {r['name']} | error | {r['error'][:80]} | |")
                continue
            tb, sm = r["testbed"].get(key, math.nan), r["sim"].get(key, math.nan)
            lines.append(f"| {r['name']} | {tb:.3f} | {sm:.3f} | {agree(key, tb, sm)} |")
    extra = ("gt3B_p", "gt3B_r", "spread_p99_ms", "spread_n", "stim_member_hit", "v2_delay_p90_ms", "v2_fa_min", "d1bw_p", "d1bw_r",
             "gop_drops_per_client_min", "rate_in_stimulus")
    for key in extra:
        lines += [f"\n### {key} (no limit)\n", "| run | testbed | sim |", "|---|---|---|"]
        for r in rows:
            if "error" not in r:
                lines.append(f"| {r['name']} | {r['testbed'].get(key, math.nan):.3f} | {r['sim'].get(key, math.nan):.3f} |")
    (OUT / f"tables-{ack}.md").write_text("\n".join(lines) + "\n")
    print(f"{len(rows)} pairs -> {OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
