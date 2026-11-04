#!/usr/bin/env python3
"""Phase 3 step 0: build an ECG onset log from a quiclab run, measure the
cross-client onset spread per burst, run the ECG engine and score it against
the run's burst truth. Grouping-only tooling: it reads the detector outputs
and never writes under <run>/detector or <run>/baselines.

    python scripts/grouping_adapter.py .runs/<campaign>/det-burstcap-pfifo-r1 [more runs...]
    python scripts/grouping_adapter.py RUN... --spread-only
    python scripts/grouping_adapter.py RUN... --set delta=0.3 theta_J=0.6 theta_cov=0.6
    python scripts/grouping_adapter.py RUN... --onsets owd      # oracle delay detector
    python scripts/grouping_adapter.py RUN... --onsets truth    # burst truth as onsets

Per run, under <run>/grouping/ (shadow) or <run>/grouping-<onsets>/ (oracles):
onsets.jsonl (meta / obs / onset records), truth.json, spread.csv,
evidence.jsonl, metrics.json, pairs_t.json (pairwise decision after every
event close), L.png.

Mechanism A -> Onset, three sources (--onsets):
  shadow  the frozen shadow detector (tuned:full) pre_signal_on/off events
          from moqx_shadow_replay, merged into episodes (gaps < 1 s);
          t_arrival = episode start (alarm time); t_onset = start of the
          sustained queue-delay rise (rolling median of the per-ACK
          queue_delay_ms >= --backdate-qd-ms) that ends at the alarm, looked
          back at most --backdate-max seconds; equal to t_arrival when the
          samples show no rise.
  owd     oracle delay detector: det_eval.measured_bands on the client's exact
          OWD log (<sub>-owd.csv): a standing queue >= 10 ms for >= 0.5 s is
          an episode, its first bin the onset. A perfect sender would learn it
          one RTT after the send-time bin, so t_onset = t_arrival = bin + mrtt
          (same residual as the shadow source after the engine's -mrtt/2
          alignment). No detection delay, no misses; the real cross-flow
          onset spread stays.
  truth   detector/bursts.csv: every client the truth labels "hit" gets one
          onset per burst at the burst start, t_onset = t_arrival = start +
          mrtt/2 (aligned onset = burst start, spread 0). The idealized upper
          bound: tests the tree logic alone.
Observability: sent.csv -> bytes in the trailing 200 ms >= obs_fraction *
rendition * 0.2 s (sent_rate mode) or acks.csv -> inflight >= 0.5 cwnd and
not app-limited (cwnd mode), per 20 ms window; in_episode from the episodes.
Truth: pairs are "same" when both clients are hit by at least one common
burst (detector/bursts.csv); without bursts.csv, the topology's first router
egress (det_eval's group_of) is used.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
from grouping import Config, FlowMeta, ObsSample, Onset, replay  # noqa: E402
from grouping.engine import Engine  # noqa: E402
from grouping.invariants import Invariants  # noqa: E402

SHADOW_VARIANT, ON, OFF = "full", "pre_signal_on", "pre_signal_off"   # det_eval.replay(run, TUNED): variant "full" is the tuned setting
OBS_WINDOW = 0.020
TRAIL_S = 0.2


def merge_episodes(out: list[list[float]], warmup: float, merge_s: float = d.ALARM_MERGE_S) -> list[tuple[float, float]]:
    merged: list[list[float]] = []
    for s, e in out:
        if merged and s - merged[-1][1] < merge_s:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(s, e) for s, e in merged if s >= warmup]


def episodes_of(events: list[dict], sid: str, warmup: float) -> list[tuple[float, float]]:
    """(start, end) shadow alarm episodes of one client, flaps closer than ALARM_MERGE_S merged."""
    out, start = [], None
    for e in sorted((e for e in events if e["subscriber"] == sid and e["variant"] == SHADOW_VARIANT),
                    key=lambda e: e["t"]):
        if e["event"] == ON and start is None:
            start = e["t"]
        elif e["event"] == OFF and start is not None:
            out.append([start, e["t"]])
            start = None
    if start is not None:
        out.append([start, math.inf])
    return merge_episodes(out, warmup)


def owd_episodes(run: d.Run, sid: str, warmup: float) -> list[tuple[float, float]]:
    """Oracle delay detector: contiguous 'congested' bands of det_eval.measured_bands
    on the client's exact OWD log; bin times are send times."""
    pts = []
    for r in d.rows(run.sender_file(sid, "owd")):
        t = run.t_mono_us(int(r["bin_mono_us"]))
        if 0 <= t <= run.duration - d.SHUTDOWN_S:
            pts.append((t, int(r["owd_min_us"]) / 1000 if r["owd_min_us"] else None,
                        int(r["packets_sent"]), int(r["packets_timed"])))
    bands = d.measured_bands(pts, d.delay_changes(run, sid))
    out, start, last = [], None, None
    for t, band in bands:
        if band == "congested":
            if start is None:
                start = t
            last = t
        elif band != "none" and start is not None:   # 'none' bins (nothing sent) do not end a queue
            out.append([start, t])
            start = None
    if start is not None:
        out.append([start, last])
    return merge_episodes(out, warmup)


def truth_episodes(truth: dict, sid: str, warmup: float) -> list[tuple[float, float]]:
    """Burst truth as a detector: one episode per burst that hit the client."""
    return merge_episodes([[b["start"], b["end"]] for b in truth["bursts"] if sid in b["hit"]], warmup, merge_s=0.0)


def backdate(samples: pd.DataFrame, t_arr: float, max_back: float, qd_ms: float) -> float:
    """Start of the sustained queue-delay rise that ends at the alarm: the
    earliest sample of the contiguous run (rolling median over 5 ACKs of
    queue_delay_ms >= qd_ms) that contains t_arr; t_arr when there is none."""
    w = samples[(samples.t >= t_arr - max_back) & (samples.t <= t_arr + 0.05)]
    if len(w) < 3:
        return t_arr
    qd = w.queue_delay_ms.rolling(5, min_periods=1, center=True).median().values
    pos = qd >= qd_ms
    t = w.t.values
    i = int(np.searchsorted(t, t_arr, side="right")) - 1
    if i < 0 or not pos[i]:
        return t_arr
    while i > 0 and pos[i - 1]:
        i -= 1
    return float(t[i])


def sent_rate_obs(run: d.Run, sid: str, rendition_bps: float, fraction: float, t_end: float) -> np.ndarray:
    s = pd.read_csv(run.sender_file(sid, "sent"), usecols=["send_mono_us", "bytes"])
    t = run.t_mono_us(s.send_mono_us.values)
    edges = np.arange(0, t_end + OBS_WINDOW, OBS_WINDOW)
    per_win = np.histogram(t, bins=edges, weights=s.bytes.values)[0]
    k = int(round(TRAIL_S / OBS_WINDOW))
    trailing = np.convolve(per_win, np.ones(k), mode="full")[:len(per_win)]
    return trailing >= fraction * rendition_bps / 8 * TRAIL_S


def owd_timed_obs(run: d.Run, sid: str, t_end: float) -> np.ndarray:
    """Windows whose trailing 200 ms holds at least one OWD bin with a receive
    timestamp: where the oracle detector has data (an oracle gap is not silence)."""
    o = pd.read_csv(run.sender_file(sid, "owd"), usecols=["bin_mono_us", "packets_timed"])
    t = run.t_mono_us(o.bin_mono_us.values[o.packets_timed.values > 0])
    edges = np.arange(0, t_end + OBS_WINDOW, OBS_WINDOW)
    per_win = np.histogram(t, bins=edges)[0]
    k = int(round(TRAIL_S / OBS_WINDOW))
    return np.convolve(per_win, np.ones(k), mode="full")[:len(per_win)] > 0


def cwnd_obs(run: d.Run, sid: str, t_end: float) -> np.ndarray:
    a = pd.read_csv(run.sender_file(sid, "acks"), usecols=["mono_us", "app_limited", "cwnd_bytes", "inflight_bytes"])
    a["t"] = run.t_mono_us(a.mono_us.values)
    a["w"] = (a.t // OBS_WINDOW).astype(int)
    g = a.groupby("w").agg(applim=("app_limited", "max"), infl=("inflight_bytes", "max"), cwnd=("cwnd_bytes", "max"))
    n = int(math.ceil(t_end / OBS_WINDOW)) + 1
    out = np.zeros(n, dtype=bool)
    ok = g[(g.applim == 0) & (g.infl >= 0.5 * g.cwnd)].index.values
    out[ok[(ok >= 0) & (ok < n)]] = True
    return out


def build(run_dir: Path, cfg: Config, backdate_max: float, warmup: float, qd_ms: float,
          source: str = "shadow") -> tuple[list, dict, list[dict]]:
    run = d.Run(run_dir)
    truth = truth_of(run)
    t_end = run.duration
    rendition = {s: float(run.topology["subscribers"][s]["rate_kbps"]) * 1000 for s in run.subs}
    mrtt = {}
    for s in run.subs:
        a = pd.read_csv(run.sender_file(s, "acks"), usecols=["min_rtt_us"])
        mrtt[s] = float(a.min_rtt_us.min()) / 1e6
    onsets = []
    if source == "shadow":
        with tempfile.TemporaryDirectory() as tmp:
            events = d.replay(run, d.TUNED, samples_to=Path(tmp))
            samples = {}
            for s in run.subs:
                f = Path(tmp) / f"{s}.csv"
                if f.exists():
                    df = pd.read_csv(f, usecols=["mono_us", "queue_delay_ms"])
                    df["t"] = run.t_mono_us(df.mono_us.values)
                    samples[s] = df
        eps = {s: episodes_of(events, s, warmup) for s in run.subs}
        for s in run.subs:
            for start, end in eps[s]:
                t_on = backdate(samples[s], start, backdate_max, qd_ms) if s in samples else start
                onsets.append({"flow": s, "t_arrival": start, "t_onset": t_on, "end": end})
    elif source == "owd":
        eps = {s: owd_episodes(run, s, warmup) for s in run.subs}
        for s in run.subs:
            for start, end in eps[s]:
                t = start + mrtt[s]
                onsets.append({"flow": s, "t_arrival": t, "t_onset": t, "end": end + mrtt[s]})
    elif source == "truth":
        if not truth["bursts"]:
            raise RuntimeError(f"{run_dir.name}: no burst hit labels, --onsets truth needs detector/bursts.csv")
        eps = {s: truth_episodes(truth, s, warmup) for s in run.subs}
        for s in run.subs:
            for start, end in eps[s]:
                t = start + mrtt[s] / 2
                onsets.append({"flow": s, "t_arrival": t, "t_onset": t, "end": end + mrtt[s] / 2})
    else:
        raise ValueError(source)
    eps = {s: [(o["t_arrival"], o["end"]) for o in onsets if o["flow"] == s] for s in run.subs}
    records: list = [("meta", 0.0, FlowMeta(s, mrtt[s], False, rendition[s])) for s in run.subs]
    for o in onsets:
        records.append(("onset", o["t_arrival"], Onset(o["flow"], o["t_onset"], o["t_arrival"])))
    n = int(math.ceil(t_end / OBS_WINDOW)) + 1
    for s in run.subs:
        obs = sent_rate_obs(run, s, rendition[s], cfg.obs_fraction, t_end) if cfg.obs_mode == "sent_rate" \
            else cwnd_obs(run, s, t_end)
        if source == "owd":
            cov = owd_timed_obs(run, s, t_end)
            obs = obs & cov[:len(obs)]
        starts = np.array([a for a, _ in eps[s]])
        ends = np.array([b for _, b in eps[s]])
        for i in range(n):
            t = round(i * OBS_WINDOW, 6)
            j = int(np.searchsorted(starts, t, side="right")) - 1
            in_ep = bool(j >= 0 and t < ends[j])
            ob = bool(i < len(obs) and obs[i] and t >= warmup)
            records.append(("obs", t, ObsSample(s, t, ob, in_ep)))
    order = {"meta": 0, "obs": 1, "onset": 2}
    records.sort(key=lambda r: (r[1], order[r[0]], r[2].flow))
    truth["episodes"] = {s: [(a, b) for a, b in eps[s]] for s in run.subs}
    truth["onset_source"] = source
    return records, truth, onsets


def leaf_groups(hit_sets: list[set[str]], same: dict[str, set[str]], subs: list[str]) -> dict[str, frozenset]:
    """Tightest group of a client: the intersection of every hit set that
    contains it. On a split topology an upstream burst hits A ∪ B, a downstream
    one A or B, so leaf(a1) = A and leaf(b1) = B: the pair shares a link (pairs)
    but not a leaf (pairs_leaf). Single bottleneck: both relations coincide.
    Without hit sets (topology truth) the group is the client's `same` set.
    A client in no group gets the empty set."""
    if not hit_sets:
        return {s: frozenset(same[s] | {s}) if same[s] else frozenset() for s in subs}
    out = {}
    for s in subs:
        sets = [h for h in hit_sets if s in h]
        out[s] = frozenset(set.intersection(*sets)) if sets else frozenset()
    return out


def congested_bins(run: d.Run, sid: str) -> np.ndarray:
    """Times of the OWD bins det_eval.measured_bands marks congested (standing
    queue >= 10 ms for >= 0.5 s, or loss) on the client's exact OWD log."""
    pts = []
    for r in d.rows(run.sender_file(sid, "owd")):
        t = run.t_mono_us(int(r["bin_mono_us"]))
        if 0 <= t <= run.duration - d.SHUTDOWN_S:
            pts.append((t, int(r["owd_min_us"]) / 1000 if r["owd_min_us"] else None,
                        int(r["packets_sent"]), int(r["packets_timed"])))
    return np.array([t for t, band in d.measured_bands(pts, d.delay_changes(run, sid)) if band == "congested"])


def measured_bursts(run: d.Run, windows: list[dict]) -> list[dict]:
    """Burst records (same shape as bursts.csv's) from the campaign's stimulus
    windows and the OWD oracle: a client is hit when it has a congested bin in
    [start, end + BURST_RECOVERY_S]. `expected` is what the plan intended."""
    cong = {s: congested_bins(run, s) for s in run.subs}
    out = []
    for i, w in enumerate(windows):
        lo, hi = w["start"], w["end"] + d.BURST_RECOVERY_S
        hit = sorted(s for s in run.subs if ((cong[s] >= lo) & (cong[s] <= hi)).any())
        out.append({"burst": i, "start": w["start"], "end": w["end"], "hit": hit, "uncertain": [],
                    "kind": w.get("kind"), "target": w.get("target"), "expected": w.get("expected", [])})
    return out


def truth_of(run: d.Run) -> dict:
    paths = {s: d.path_hops(run, run.pub, s) for s in run.subs}
    group_of = {s: f"{p[1][0]}->{p[1][1]}" if len(p) > 1 else s for s, p in paths.items()}
    truth = {"run": run.path.name, "subs": run.subs, "topology_group": group_of, "bursts": [], "pairs": {}}
    bursts_csv = run.path / "detector" / "bursts.csv"
    windows_json = run.path / "grouping" / "windows.json"
    same = defaultdict(set)
    if windows_json.exists():
        # Grouping campaign run: stimulus windows from the plan, hits measured on the OWD oracle.
        truth["bursts"] = measured_bursts(run, json.loads(windows_json.read_text()))
        for b in truth["bursts"]:
            for x in b["hit"]:
                same[x] |= set(b["hit"])
        truth["source"] = "windows.json + OWD oracle (both congested in a common stimulus window)"
    elif bursts_csv.exists():
        b = pd.read_csv(bursts_csv)
        for (burst, start, end), g in b.groupby(["burst", "start", "end"]):
            hit = sorted(g[g["class"] == "hit"].subscriber)
            unc = sorted(g[g["class"] == "uncertain"].subscriber)
            truth["bursts"].append({"burst": int(burst), "start": float(start), "end": float(end), "hit": hit,
                                    "uncertain": unc})
            for x in hit:
                same[x] |= set(hit)
        truth["source"] = "bursts.csv (both hit by a common burst)"
    if not any(same.values()) and not windows_json.exists():
        # No hit labels (TCP scenarios score "uncertain"): fall back to topology.
        # Campaign runs keep their measured truth even when nothing was hit
        # (reverse-path stimuli): every pair is then DIFFERENT.
        for s in run.subs:
            same[s] = {x for x in run.subs if group_of[x] == group_of[s] and group_of[s] != s}
        truth["source"] = "topology (same first router egress)"
        truth["bursts"] = []
    leaf = leaf_groups([set(b["hit"]) for b in truth["bursts"] if b["hit"]], same, run.subs)
    truth["leaf"] = {s: sorted(l) for s, l in leaf.items()}
    truth["pairs_leaf"] = {}
    subs = sorted(run.subs)
    for i, f in enumerate(subs):
        for g in subs[i + 1:]:
            truth["pairs"][f"{f}|{g}"] = g in same[f]
            truth["pairs_leaf"][f"{f}|{g}"] = bool(leaf[f]) and leaf[f] == leaf[g]
    return truth


def spread_rows(truth: dict, onsets: list[dict]) -> list[dict]:
    """Per burst: spread of t_arrival and of t_onset across the hit clients."""
    rows = []
    by_flow = defaultdict(list)
    for o in onsets:
        by_flow[o["flow"]].append(o)
    for b in truth.get("bursts", []):
        arr, on = [], []
        for s in b["hit"]:
            cand = [o for o in by_flow[s] if b["start"] <= o["t_arrival"] <= b["end"] + d.BURST_RECOVERY_S]
            if cand:
                o = min(cand, key=lambda o: o["t_arrival"])
                arr.append(o["t_arrival"])
                on.append(o["t_onset"])
        if len(arr) >= 2:
            rows.append({"burst": b["burst"], "start": b["start"], "n_hit": len(b["hit"]), "n_detected": len(arr),
                         "spread_arrival_ms": round((max(arr) - min(arr)) * 1e3, 1),
                         "spread_onset_ms": round((max(on) - min(on)) * 1e3, 1),
                         "first_arrival_ms": round((min(arr) - b["start"]) * 1e3, 1),
                         "first_onset_ms": round((min(on) - b["start"]) * 1e3, 1),
                         "backdate_ms": round(statistics.median(a - o for a, o in zip(arr, on)) * 1e3, 1)})
    return rows


def pair_metrics(res: replay.Result, truth: dict, key: str = "pairs_leaf") -> dict:
    """ECG SAME (same leaf, both confirmed) against truth[key]: pairs_leaf (same
    tightest group) or pairs (hit by a common burst, i.e. share some link)."""
    pairs = res.pairs()
    tp = fp = fn = tn = unc = 0
    detail = {}
    for (f, g), dec in pairs.items():
        same = truth[key][f"{f}|{g}"]
        detail[f"{f}|{g}"] = {"decided": dec, "truth_same": same}
        if dec == "UNCERTAIN":
            unc += 1
        elif dec == "SAME":
            tp += same
            fp += not same
        else:
            fn += same
            tn += not same
    dec_n = tp + fp + fn + tn
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "uncertain": unc,
            "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None,
            "coverage": dec_n / len(pairs) if pairs else None, "pairs": detail}


def out_dir(run_dir: Path, a) -> Path:
    return run_dir / (a.out or ("grouping" if a.onsets == "shadow" else f"grouping-{a.onsets}"))


def process(run_dir: Path, cfg: Config, a) -> dict:
    out = out_dir(run_dir, a)
    out.mkdir(exist_ok=True)
    records, truth, onsets = build(run_dir, cfg, a.backdate_max, a.warmup, a.backdate_qd_ms, a.onsets)
    rows = spread_rows(truth, onsets)
    with (out / "spread.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["burst"])
        w.writeheader()
        w.writerows(rows)
    summary = {"run": run_dir.name, "onsets": len(onsets), "bursts_measured": len(rows)}
    if rows:
        for k in ("spread_arrival_ms", "spread_onset_ms", "first_arrival_ms", "first_onset_ms", "backdate_ms"):
            vals = sorted(r[k] for r in rows)
            summary[k] = {"p50": vals[len(vals) // 2], "p90": vals[min(len(vals) - 1, int(0.9 * len(vals)))]}
    if a.spread_only:
        return summary
    from grouping import synth
    synth.write_log(records, out / "onsets.jsonl")
    holder = {}

    def factory(_r, cfg_, log=None):
        eng = Engine(cfg_, log)
        holder["inv"] = Invariants(eng)
        return eng
    res = replay.run(records, cfg, log_path=out / "evidence.jsonl", engine_factory=factory)
    pm = pair_metrics(res, truth, "pairs_leaf")
    pm_link = pair_metrics(res, truth, "pairs")
    metrics = {"run": run_dir.name, "onset_source": a.onsets, "config": cfg.to_dict(), "cases": dict(res.cases),
               "pairwise": pm, "pairwise_link": pm_link, "spans": replay.span_stats(res), "leaves": res.leaves,
               "final": res.final["flows"], "spread": summary, "truth_source": truth["source"],
               "truth_leaf": truth["leaf"], "invariants_checked": holder["inv"].n_checked,
               "events": res.events, "bursts": truth["bursts"]}
    replay.dump(metrics, out / "metrics.json")
    (out / "pairs_t.json").write_text(json.dumps(res.pairs_t()))
    (out / "truth.json").write_text(json.dumps(truth, indent=1))
    replay.plot_L(res, out / "L.png", f"{run_dir.name}: {a.onsets} onsets -> ECG (delta={cfg.delta}, theta={cfg.theta_J})")
    summary.update({"cases": dict(res.cases), "precision": pm["precision"], "recall": pm["recall"],
                    "coverage": pm["coverage"], "uncertain": pm["uncertain"],
                    "leaves": {n: l["members"] for n, l in res.leaves.items() if l["kind"] == "leaf" and l["members"]}})
    return summary


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--onsets", choices=("shadow", "owd", "truth"), default="shadow", help="Mechanism A source")
    ap.add_argument("--out", help="subdirectory under each run (default grouping, grouping-owd, grouping-truth)")
    ap.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE", help="engine config overrides")
    ap.add_argument("--backdate-max", type=float, default=1.0, help="max look-back for the backlog onset (s)")
    ap.add_argument("--backdate-qd-ms", type=float, default=10.0, help="queue delay that counts as backlog (ms)")
    ap.add_argument("--warmup", type=float, default=d.WARMUP_S, help="ignore onsets before this run time (s)")
    ap.add_argument("--spread-only", action="store_true", help="only measure the per-burst onset spread")
    a = ap.parse_args(argv)
    over = {}
    for it in a.set:
        k, v = it.split("=", 1)
        try:
            over[k] = json.loads(v)
        except json.JSONDecodeError:
            over[k] = v
    cfg = Config.from_dict(over)
    runs = [r for pat in a.runs for r in (sorted(Path().glob(str(pat))) if any(c in str(pat) for c in "*?[") else [pat])]
    rows = []
    for r in runs:
        if not (r / "events.csv").exists():
            print(f"skip {r}: not a run", file=sys.stderr)
            continue
        try:
            s = process(r, cfg, a)
        except RuntimeError as e:
            print(f"skip {e}", file=sys.stderr)
            continue
        rows.append(s)
        sp = s.get("spread_onset_ms")
        print(f"{s['run']}: onsets={s['onsets']} bursts={s['bursts_measured']}"
              + (f" spread arrival p50={s['spread_arrival_ms']['p50']} p90={s['spread_arrival_ms']['p90']}"
                 f" | onset p50={sp['p50']} p90={sp['p90']} | backdate p50={s['backdate_ms']['p50']} ms" if sp else "")
              + ("" if a.spread_only else f"\n    cases={s['cases']} pairs P={s['precision']} R={s['recall']} "
                 f"cov={s['coverage']} leaves={s['leaves']}"), flush=True)
    if len(rows) > 1 and rows[0].get("spread_onset_ms"):
        def agg(k, q):
            return statistics.median(r[k][q] for r in rows if k in r)
        print(f"\nall runs (median of per-run values): arrival spread p50={agg('spread_arrival_ms', 'p50'):.0f} "
              f"p90={agg('spread_arrival_ms', 'p90'):.0f} ms | backdated onset spread p50={agg('spread_onset_ms', 'p50'):.0f} "
              f"p90={agg('spread_onset_ms', 'p90'):.0f} ms | backdate p50={agg('backdate_ms', 'p50'):.0f} ms")
    if not a.spread_only and rows:
        P = [r["precision"] for r in rows if r.get("precision") is not None]
        R = [r["recall"] for r in rows if r.get("recall") is not None]
        C = [r["coverage"] for r in rows if r.get("coverage") is not None]
        print(f"pairwise over {len(rows)} runs: precision median={statistics.median(P) if P else None} "
              f"recall median={statistics.median(R) if R else None} coverage median={statistics.median(C) if C else None}")


if __name__ == "__main__":
    main(sys.argv[1:])
