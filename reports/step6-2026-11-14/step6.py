#!/usr/bin/env python3
"""Step 6 (2026-11-14): grouping-only analysis of the synchronized runs and their staggered
counterparts. Read-only; GT1, the detector and the ECG engine are not changed, existing
functions are only called. No new truth (gt1 only, gt2 / gt3 not needed here).

    .venv/bin/python3 reports/step6-2026-11-14/step6.py run  > reports/step6-2026-11-14/step6-rows.jsonl
    .venv/bin/python3 reports/step6-2026-11-14/step6.py sum  reports/step6-2026-11-14/step6-rows.jsonl > .../step6-summary.md

Runs: sync = mini campaign (.runs/2026-11-13_2238_ip4-sync-keyframes-oldGT, was _grp-sync: calm065, burstcap, K1, C1, K6, r1 r2)
+ overnight P1 (K6, C1 r3 r4); stag = .runs/ip4-not-sync-keyframes-oldGT (was 2026-11-10_1946_v2) r1 + overnight P2 (K1, K6, C1 r2).

Event intervals: ECG event intervals for everything (t0 - 1 s, t0 + 2 s; grouping_step2
NEG_SPAN). Per-event truth: a router egress is "congested in the event" when one of its GT1
episodes (gt1.run_truth, canonical Params) overlaps the interval (FLAG, the gt1 rule of step 5).
A client is behind the recorded egresses on its path (det_eval.path_hops).

Item 1: a pair decided SAME by ECG (each ECG close) or h3 (each close of the step 4 replay,
  m = 3, ECG intervals) that the same-leaf truth calls wrong is "shared in that event" when
  both clients are behind one egress congested in that event. A membership judged at
  declaration is wrong by the same-leaf truth (majority leaf) and "shared in that event" when
  the client shares a congested egress of that event with at least half of the other members
  (FLAG: half).
Item 2: ECG cases per event; share of ECG events with the root / upstream egress congested.
Item 3: per event, every participant's curve minus the pointwise median over all
  participants; Part 1 procedure and Step 5 B1 votes on the remainders, before / after.
  Leaf truth of an event: participants whose leaf egress (topology_group hop) is congested.
Item 4: per egress, peak queueing delay in [T, T + PEAK_S] after each synchronized keyframe
  time T in calm time (outside stimulus windows +- 1 s), next to load x KEY_FRAC s; load =
  transmitted bytes / capacity over the same calm time. Keyframe hand-over: transmit time of
  each keyframe from the sender's sent packets.

Constants: KEY_FRAC 4/33 (P: ip_ratio 4, 30 fps, 1 s GOP -> I = 4 P, GOP = 33 P);
PEAK_S 0.5 s (FLAG: less than one GOP); CALM_MARGIN 1 s (FLAG); half of the other
members (FLAG).
"""

from __future__ import annotations

import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import grouping_step5 as s5  # noqa: E402
import keyframe_spread as kf  # noqa: E402

s4, s3, s2, ts, ga, d, gt1 = s5.s4, s5.s3, s5.s2, s5.ts, s5.ga, s5.d, s5.s2.gt1
KEY_FRAC = 4 / 33
PEAK_S = 0.5
CALM_MARGIN = 1.0
ECG_DIR = "grouping-d150-v2-owd"
MINI, OLD = ROOT / ".runs/2026-11-13_2238_ip4-sync-keyframes-oldGT", ROOT / ".runs/ip4-not-sync-keyframes-oldGT"
NSYNC, NSTAG = ROOT / ".runs/2026-11-14_0240_night-sync", ROOT / ".runs/2026-11-14_0240_night-stag"
SCEN = {"G0": "calm065", "M1": "burstcap", "K1": "hier", "C1": "burstlongsplit", "K6": "depth"}


def run_list():
    out = []
    for k, t in SCEN.items():
        for r in (1, 2):
            out.append(("sync", MINI / k / f"grp-{t}-pfifo-r{r}"))
        out.append(("stag", OLD / k / f"grp-{t}-pfifo-r1"))
    for k in ("K6", "C1"):
        for r in (3, 4):
            out.append(("sync", NSYNC / k / f"grp-{SCEN[k]}-pfifo-r{r}"))
    for k in ("K1", "K6", "C1"):
        out.append(("stag", NSTAG / k / f"grp-{SCEN[k]}-pfifo-r2"))
    return out


def hot_of(eps, lo, hi):
    return {h for h, v in eps.items() if any(a <= hi and b >= lo for a, b in v)}


def shared_with(i, others, hops, hot, need_half=True):
    if not others:
        return False
    n = sum(bool(hops.get(i, set()) & hops.get(j, set()) & hot) for j in others)
    return n >= len(others) / 2 if need_half else n > 0


def judge_closes(closes, hot_per_close, leaf, same, hops):
    """closes: list of {group: [members]}; returns wrong-pair and membership counts."""
    pairs = Counter()
    seen = set()
    mem = Counter()
    for c, groups in enumerate(closes):
        hot = hot_per_close[c]
        for g, ms in groups.items():
            ms = sorted(ms)
            for x, a in enumerate(ms):
                for b in ms[x + 1:]:
                    if not same.get(f"{a}|{b}", False):
                        sh = bool(hops.get(a, set()) & hops.get(b, set()) & hot)
                        pairs["wrong"] += 1
                        pairs["shared" if sh else "not shared"] += 1
                    else:
                        pairs["right"] += 1
            for i in ms:
                if (i, g) in seen:
                    continue
                seen.add((i, g))
                mem["declared"] += 1
                lf = leaf.get(i)
                ok = bool(lf) and lf == s3.majority(ms, leaf)
                if not ok:
                    mem["wrong"] += 1
                    mem["shared" if shared_with(i, [j for j in ms if j != i], hops, hot) else "not shared"] += 1
        for key in list(seen):   # memberships that ended can be declared again later
            if key[1] not in groups or key[0] not in groups[key[1]]:
                seen.discard(key)
    return dict(pairs), dict(mem)


def ecg_closes(rd, run, leaf):
    m = json.loads((rd / ECG_DIR / "metrics.json").read_text())
    from grouping import Config
    A = Config.from_dict(m["config"]).A
    evs = m["events"]
    closes = []
    for x, e in enumerate(evs):
        groups = defaultdict(list)
        for f, ser in m["series"].items():
            hit = ser[x] if x < len(ser) and abs(ser[x][0] - e["t"]) < 1e-6 else next(
                (s_ for s_ in ser if abs(s_[0] - e["t"]) < 1e-6), None)
            if hit and hit[1] is not None and hit[2] >= A:
                groups[hit[1]].append(f)
        closes.append(dict(groups))
    return m, evs, closes


def item4(run, rd, windows, delay, caps):
    """Peak delay after synchronized keyframes per egress in calm time, and load."""
    sub0 = next(s for s in run.subs if run.sender_file(s, "frames").exists())
    kfr = kf.client_keyframes(run, sub0)
    T = np.sort(kfr["scheduled"].values)
    busy = [(w["start"] - CALM_MARGIN, w["end"] + CALM_MARGIN) for w in windows]
    calm = lambda t: (t >= d.WARMUP_S) & (t <= run.duration - d.SHUTDOWN_S) & ~np.any(
        [(t >= a) & (t <= b) for a, b in busy] or [np.zeros_like(t, bool)], axis=0)
    T = T[calm(T) & calm(T + PEAK_S)]
    out = {}
    for hop, csv in gt1.router_egresses(run):
        h = f"{hop[0]}->{hop[1]}"
        if h not in delay:
            continue
        t, q = delay[h]
        r = d.rows(csv)
        tt = np.array([run.t_mono_us(int(x["timestamp_mono_ns"]) / 1000) for x in r])
        tx = np.array([float(x["transmitted_bytes"]) for x in r])
        iv = np.array([float(x["interval_ns"]) / 1e9 for x in r])
        cap = np.array([d.value_at(caps[hop], x) for x in tt]) * 1e6 / 8
        ok = calm(tt) & (iv > 0)
        load = float(np.sum(tx[ok]) / np.sum(cap[ok] * iv[ok])) if ok.any() else None
        peaks = []
        for k in T:
            m = (t >= k) & (t < k + PEAK_S)
            if m.any():
                peaks.append(float(q[m].max()))
        dt = float(np.median(np.diff(t))) if len(t) > 1 else None
        out[h] = {"load": load, "model_ms": load * KEY_FRAC * 1000 if load is not None else None,
                  "peak_ms": [round(x, 2) for x in np.percentile(peaks, [50, 90, 100])] if peaks else None,
                  "keyframes": len(peaks), "sample_ms": round(dt * 1000, 1) if dt else None}
    # keyframe hand-over: write - scheduled, and transmit time (first packet after write until the
    # keyframe's bytes have left), pacing rate around it
    hand = {}
    for s in run.subs:
        f = kf.client_keyframes(run, s)
        if f is None:
            continue
        fr = pd.read_csv(run.sender_file(s, "frames"))
        size = dict(zip(fr["index"][fr.keyframe == 1], fr["size"][fr.keyframe == 1]))
        sent = pd.read_csv(run.sender_file(s, "sent"), usecols=["send_mono_us", "bytes"])
        st = np.array([run.t_mono_us(x) for x in sent.send_mono_us])
        cb = np.cumsum(sent.bytes.values)
        dur = []
        for idx, row_ in f.iterrows():
            w = row_["written"]
            if not calm(np.array([w]))[0]:
                continue
            i0 = np.searchsorted(st, w)
            if i0 >= len(st):
                continue
            base = cb[i0 - 1] if i0 > 0 else 0
            j = np.searchsorted(cb, base + size[idx])
            if j < len(st):
                dur.append((st[j] - st[i0]) * 1000)
        cc = pd.read_csv(run.sender_file(s, "cc"), usecols=["t_us", "pacing_bps"])
        pb = cc.pacing_bps[cc.pacing_bps > 0]
        hand[s] = {"rate_kbps": (run.topology["subscribers"].get(s) or {}).get("rate_kbps"),
                   "keyframe_bytes_p50": float(np.median(list(size.values()))) if size else None,
                   "transmit_ms": [round(x, 1) for x in np.percentile(dur, [50, 90])] if dur else None,
                   "pacing_mbps_p50": round(float(np.median(pb)) / 1e6, 2) if len(pb) else None}
    return {"queues": out, "handover": hand, "calm_keyframes": int(len(T))}


def item3(events, leaf, leaf_hop, hops, rules, rates, eps_gt1):
    """Before / after subtracting the pointwise median over participants."""
    after_events = []
    match = {"before": [], "after": []}
    for row, qs, tp_all, res in events:
        parts = res["participants"]
        if len(parts) < 2:
            after_events.append((row, qs, tp_all, res))
            continue
        common = ts.template(qs, set(parts))[0]
        rem = {s: qs[s] - common for s in parts}
        res2 = s3.partition_fixed(rem) if len(rem) >= 2 else res
        after_events.append((row, rem, tp_all, res2))
        hot = rules["gt1"](row["lo"], row["hi"])
        truth = {s for s in parts if leaf_hop.get(s) in hot}
        for tag, r_ in (("before", res), ("after", res2)):
            cong = set(r_["participants"]) - set(r_["zero"])
            match[tag].append({"n_part": len(parts), "cong": len(cong), "truth": len(truth),
                               "tp": len(cong & truth), "exact": cong == truth})
    b1 = {"before": s5.b1_votes(events, leaf, leaf_hop, hops, rules, rates),
          "after": s5.b1_votes(after_events, leaf, leaf_hop, hops, rules, rates)}
    return {"match": match, "b1": {k: [v[3:6] for v in vs] for k, vs in b1.items()}}


def run_row(arg):
    phase, rd = arg
    run, truth, subs, windows, events = s4.load_events(rd, ecg_intervals=True)
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    same = truth["pairs_leaf"]
    leaf_hop = {s: h for s, h in truth.get("topology_group", {}).items() if h != s}
    delay = s2.egress_delay(run)
    gt1_eps = ga.gt1_hop_episodes(run)
    rules = s5.make_rules(delay, gt1_eps)
    hops = {s: s2.path_egresses(run, s, delay) for s in subs}
    rates = {s: (run.topology["subscribers"].get(s) or {}).get("rate_kbps") for s in subs}
    k = rd.parent.name
    row = {"phase": phase, "campaign": k, "run": rd.name, "rep": int(rd.name.rsplit("-r", 1)[1]),
           "n_step4_events": len(events), "leaf_hops": sorted(set(leaf_hop.values()))}
    # ECG closes and item 1 / 2
    m, evs, closes = ecg_closes(rd, run, leaf)
    hot_e = [hot_of(gt1_eps, e["t0"] + s2.NEG_SPAN[0], e["t0"] + s2.NEG_SPAN[1]) for e in evs]
    row["ecg_pairs"], row["ecg_mem"] = judge_closes(closes, hot_e, leaf, same, hops)
    row["ecg_final"] = {x: m["pairwise"].get(x) for x in ("precision", "recall", "coverage", "tp", "fp", "fn", "tn", "uncertain")}
    row["ecg_final"]["tree_correct"] = m.get("tree_correct")
    row["ecg_final"]["leaves"] = m.get("leaves")
    row["ecg_final"]["members"] = sorted(f for f, v in m["final"].items() if v.get("member"))
    row["ecg_cases"] = dict(Counter(e["case"] for e in evs))
    row["ecg_events"] = len(evs)
    up = [h for h in delay if h not in set(leaf_hop.values())]
    row["ecg_hot_share"] = {h: round(np.mean([h in x for x in hot_e]), 3) if hot_e else None for h in sorted(delay)}
    row["ecg_case_by_hot"] = dict(Counter((e["case"], "upstream/root hot" if (set(up) & hot_e[x]) else "no upstream")
                                          for x, e in enumerate(evs)).items()) if evs else {}
    row["ecg_case_by_hot"] = {f"{a}|{b}": v for (a, b), v in row["ecg_case_by_hot"].items()}
    row["ecg_members_per_event"] = [len(e["members"]) for e in evs]
    row["ecg_coverage_t"] = None
    pt_path = rd / ECG_DIR / "pairs_t.json"
    if pt_path.exists():
        pt = json.loads(pt_path.read_text())
        row["ecg_coverage_t"] = [round(np.mean([v != "UNCERTAIN" for v in s_["pairs"].values()]), 3) for s_ in pt]
    # h3 replay on ECG intervals (existing procedure, m = 3), item 1
    if k != "G0" and events:
        h = s4.replay4(events, subs, same, leaf, 3, True)
        bb = round(h["b"], 2)
        hcl = [{g: [i for i, e in r_.items() if e >= bb] for g, r_ in t.items()} for t in h["traj"]]
        hcl = [{g: ms for g, ms in c.items() if len(ms) >= 1} for c in hcl]
        hot_h = [rules["gt1"](e[0]["lo"], e[0]["hi"]) for e in events]
        row["h3_pairs"], row["h3_mem"] = judge_closes(hcl, hot_h, leaf, same, hops)
        last = h["closes"][-1] if h["closes"] else {}
        pooled = s4.pooled(h["closes"])
        row["h3_final"] = {"last": s4.prf(Counter(last)), "pooled_P": s4.prf(pooled)[0],
                           "groups": len(h["groups"]), "splits": sum("split_at" in g for g in h["groups"].values())}
    # item 3
    if k in ("K1", "C1", "K6") and phase == "sync":
        row["item3"] = item3(events, leaf, leaf_hop, hops, rules, rates, None)
    # item 4
    if k in ("G0", "K1", "K6"):
        caps = {tuple(h_.split("->")): v for h_, v in d.capacity_series(run).items()} if isinstance(
            next(iter(d.capacity_series(run))), str) else d.capacity_series(run)
        row["item4"] = item4(run, rd, windows, delay, caps)
    return row


def main_run():
    with Pool(8) as pool:
        for r in pool.imap_unordered(run_row, run_list()):
            print(json.dumps(r, default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else float(o)), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        main_run()
