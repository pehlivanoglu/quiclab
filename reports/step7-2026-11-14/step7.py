#!/usr/bin/env python3
"""Step 7 (2026-11-14): scoring of the overnight P3-P7 runs (Part A) and ECG instability (Part B).
Measurement only; GT1, the detector and the ECG engine unchanged; gt1 is the only truth used.
Reuses the Step 6 helpers (reports/step6-2026-11-14/step6.py) and the existing scripts' functions.

    .venv/bin/python3 reports/step7-2026-11-14/step7.py a > reports/step7-2026-11-14/a-rows.jsonl
    .venv/bin/python3 reports/step7-2026-11-14/step7.py b > reports/step7-2026-11-14/b-rows.jsonl

Part A per run (ECG event intervals): ECG and h3 (step 4 replay, m = 3) wrong pairs / memberships
split by the per-event truth in two versions:
  generous  an egress is congested in an event when any GT1 episode overlaps the interval (step 6);
  strict    when its GT1 episodes cover at least half of the interval (FLAG: one half; brief A4).
Also: ECG final metrics, h3 headline, egress congestion shares in ECG events, Step 5 B1 votes,
negatives scored with the topology truth of step 2b (pair right when the two clients share a
recorded egress with a GT1 episode in the run), and keyframe queues (step 6 item 4, plus spike
duration = time with delay >= 5 ms in [T, T + 0.5 s] (FLAG: GT1 target), drops in that window).
Part B per run: ECG at every close: coverage (pairs_t), leaf partition correct (FLAG: the flows'
leaf-node groups equal the truth leaves of >= 2 clients and nobody else is a member; ECG's internal
nodes are not in the per-close output), membership losses / regains, and for memberships that end
below A: dL per close by the case of that close's event.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "reports" / "step6-2026-11-14"))
import step6 as s6  # noqa: E402

s5, s4, s3, s2, ts, ga, d, gt1, kf = s6.s5, s6.s4, s6.s3, s6.s2, s6.ts, s6.ga, s6.d, s6.gt1, s6.kf
STRICT = 0.5
Q_MS = 5.0
ECG_DIR = s6.ECG_DIR
MINI, OLD, NS, NT = s6.MINI, s6.OLD, s6.NSYNC, s6.NSTAG


def part_a_runs():
    out = []
    add = lambda ph, rd: out.append((ph, rd)) if rd.exists() else None
    for k, t in (("M1", "burstcap"), ("K1", "hier"), ("C1", "burstlongsplit"), ("K6", "depth")):
        for r in (1, 2):
            add("sync", MINI / k / f"grp-{t}-pfifo-r{r}")
    for k, t in (("K6", "depth"), ("C1", "burstlongsplit")):
        for r in (3, 4):
            add("sync", NS / k / f"grp-{t}-pfifo-r{r}")
    for k in sorted(NS.iterdir()):
        if k.is_dir():
            for rd in sorted(k.glob("grp-*")):
                if (rd.parent.name, rd.name.rsplit("-r", 1)[1]) not in (("K6", "3"), ("K6", "4"), ("C1", "3"), ("C1", "4")) \
                        or "pfifo" not in rd.name:
                    add("sync", rd)
    for k, t, aqms in (("M1", "burstcap", ("pfifo", "codel", "pie")), ("K1", "hier", ("pfifo", "pie")),
                       ("C1", "burstlongsplit", ("pfifo", "pie")), ("K6", "depth", ("pfifo",)),
                       ("M6", "indepfast", ("pfifo",)), ("M6", "indepslow", ("pfifo",)),
                       ("G0", "randloss", ("pfifo",)), ("G0", "calmuneven", ("pfifo",))):
        for a in aqms:
            add("stag", OLD / k / f"grp-{t}-{a}-r1")
    for r in (1, 2):
        add("stag", OLD / "J1" / f"grp-hierjit20-pfifo-r{r}")
    for k, t in (("K1", "hier"), ("K6", "depth"), ("C1", "burstlongsplit")):
        add("stag", NT / k / f"grp-{t}-pfifo-r2")
    seen, uniq = set(), []
    for ph, rd in out:
        if rd not in seen:
            seen.add(rd)
            uniq.append((ph, rd))
    return uniq


def strict_hot(eps, lo, hi):
    out = set()
    for h, v in eps.items():
        cov = sum(max(0.0, min(b, hi) - max(a, lo)) for a, b in v)
        if cov >= STRICT * (hi - lo):
            out.add(h)
    return out


def item4x(run, rd, windows, delay):
    """Step 6 item 4 plus spike duration and drops after each keyframe (calm time)."""
    caps = d.capacity_series(run)
    base = s6.item4(run, rd, windows, delay, caps)
    sub0 = next(s for s in run.subs if run.sender_file(s, "frames").exists())
    T = np.sort(kf.client_keyframes(run, sub0)["scheduled"].values)
    busy = [(w["start"] - s6.CALM_MARGIN, w["end"] + s6.CALM_MARGIN) for w in windows]
    calm = lambda t: (t >= d.WARMUP_S) & (t <= run.duration - d.SHUTDOWN_S) & ~np.any(
        [(t >= a) & (t <= b) for a, b in busy] or [np.zeros_like(t, bool)], axis=0)
    T = T[calm(T) & calm(T + s6.PEAK_S)]
    for hop, csv in gt1.router_egresses(run):
        h = f"{hop[0]}->{hop[1]}"
        q = base["queues"].get(h)
        if q is None or h not in delay:
            continue
        t, dl = delay[h]
        fine = csv.with_name(csv.stem + "-queue.csv")
        src = fine if fine.exists() else csv
        r = pd.read_csv(src, usecols=["timestamp_mono_ns", "drops"])
        tt = np.array([run.t_mono_us(x / 1000) for x in r.timestamp_mono_ns])
        dr = r.drops.values.astype(float)
        dr = np.diff(dr, prepend=dr[0]) if np.all(np.diff(dr) >= 0) else dr   # cumulative counter -> per sample
        dur, drops = [], []
        dt = float(np.median(np.diff(t))) if len(t) > 1 else 0.0
        for k in T:
            m = (t >= k) & (t < k + s6.PEAK_S)
            dur.append(float(np.sum(dl[m] >= Q_MS)) * dt * 1000)
            mm = (tt >= k) & (tt < k + s6.PEAK_S)
            drops.append(float(np.sum(np.maximum(dr[mm], 0))))
        q["spike_ms"] = [round(x, 1) for x in np.percentile(dur, [50, 90])] if dur else None
        q["drops_per_keyframe"] = round(float(np.mean(drops)), 3) if drops else None
        q["keyframes_with_drops"] = round(float(np.mean([x > 0 for x in drops])), 3) if drops else None
    tx = [v["transmit_ms"][0] for v in base["handover"].values() if v.get("transmit_ms") and v["rate_kbps"]]
    base["transmit_p50_median_ms"] = float(np.median(tx)) if tx else None
    return base


def topo_pairs(groups_final, hops, gt1_eps):
    hot_run = {h for h, v in gt1_eps.items() if v}
    ok = bad = 0
    for ms in groups_final.values():
        ms = sorted(ms)
        for x, a in enumerate(ms):
            for b in ms[x + 1:]:
                g = bool(hops.get(a, set()) & hops.get(b, set()) & hot_run)
                ok += g
                bad += not g
    return {"right": ok, "wrong": bad}


def a_row(arg):
    phase, rd = arg
    run, truth, subs, windows, events = s4.load_events(rd, ecg_intervals=True)
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    same = truth["pairs_leaf"]
    leaf_hop = {s: h for s, h in truth.get("topology_group", {}).items() if h != s}
    delay = s2.egress_delay(run)
    eps = ga.gt1_hop_episodes(run)
    rules = s5.make_rules(delay, eps)
    hops = {s: s2.path_egresses(run, s, delay) for s in subs}
    rates = {s: (run.topology["subscribers"].get(s) or {}).get("rate_kbps") for s in subs}
    k = rd.parent.name
    row = {"phase": phase, "campaign": k, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "rep": int(rd.name.rsplit("-r", 1)[1]), "folder": rd.parent.parent.name, "leaf_hops": sorted(set(leaf_hop.values()))}
    m, evs, closes = s6.ecg_closes(rd, run, leaf)
    lohi = [(e["t0"] + s2.NEG_SPAN[0], e["t0"] + s2.NEG_SPAN[1]) for e in evs]
    hot_g = [s6.hot_of(eps, lo, hi) for lo, hi in lohi]
    hot_s = [strict_hot(eps, lo, hi) for lo, hi in lohi]
    row["ecg"] = {"gen": s6.judge_closes(closes, hot_g, leaf, same, hops),
                  "strict": s6.judge_closes(closes, hot_s, leaf, same, hops),
                  "final": {x: m["pairwise"].get(x) for x in ("precision", "recall", "coverage")},
                  "tree": m.get("tree_correct"), "events": len(evs), "cases": dict(Counter(e["case"] for e in evs)),
                  "hot_share_gen": {h: round(float(np.mean([h in x for x in hot_g])), 3) for h in sorted(delay)} if evs else {},
                  "hot_share_strict": {h: round(float(np.mean([h in x for x in hot_s])), 3) for h in sorted(delay)} if evs else {}}
    if k == "G0":
        fin = defaultdict(list)
        for f, v in m["final"].items():
            if v.get("member") and v.get("node") is not None:
                fin[v["node"]].append(f)
        row["ecg"]["topo"] = topo_pairs(fin, hops, eps)
    if events:
        h = s4.replay4(events, subs, same, leaf, 3, True)
        bb = round(h["b"], 2)
        hcl = [{g: [i for i, e in r_.items() if e >= bb] for g, r_ in t.items()} for t in h["traj"]]
        hcl = [{g: ms for g, ms in c.items() if ms} for c in hcl]
        hg = [rules["gt1"](e[0]["lo"], e[0]["hi"]) for e in events]
        hs = [strict_hot(eps, e[0]["lo"], e[0]["hi"]) for e in events]
        ms_ = h["memberships"]
        row["h3"] = {"gen": s6.judge_closes(hcl, hg, leaf, same, hops), "strict": s6.judge_closes(hcl, hs, leaf, same, hops),
                     "last": s4.prf(Counter(h["closes"][-1])) if h["closes"] else None,
                     "pooled_P": s4.prf(s4.pooled(h["closes"]))[0],
                     "mem": [len(ms_), sum(not x["right"] for x in ms_), sum(x["mixed_closes"] > 0 for x in ms_)],
                     "groups": len(h["groups"]), "splits": sum("split_at" in g for g in h["groups"].values())}
        if k == "G0":
            row["h3"]["topo"] = topo_pairs(hcl[-1] if hcl else {}, hops, eps)
        v = s5.b1_votes(events, leaf, leaf_hop, hops, rules, rates)
        b1 = defaultdict(lambda: [0, 0])
        for x in v:
            b1[x[5]][0] += 1
            b1[x[5]][1] += x[3]
        row["b1"] = dict(b1)
    if k in ("K6", "K6R", "M1", "K1", "C1"):
        try:
            row["item4"] = item4x(run, rd, windows, delay)
        except Exception as e:   # noqa: BLE001
            row["item4"] = {"error": repr(e)}
    return row


# ═══ Part B ═════════════════════════════════════════════════════════════

def part_b_runs():
    out = []
    for ph, base in (("sync", MINI), ("sync", NS), ("stag", NT), ("stag", OLD)):
        for k in sorted(base.iterdir()):
            if not k.is_dir() or k.name.startswith("N"):
                continue
            for rd in sorted(k.glob("grp-*")):
                if (rd / ECG_DIR / "metrics.json").exists():
                    out.append((ph, rd))
    return out


def b_row(arg):
    phase, rd = arg
    truth = json.loads((rd / ECG_DIR / "truth.json").read_text())
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    tleaves = {frozenset(v) for v in leaf.values() if len(v) >= 2}
    m = json.loads((rd / ECG_DIR / "metrics.json").read_text())
    from grouping import Config
    A = Config.from_dict(m["config"]).A
    evs = m["events"]
    flows = sorted(m["series"])
    n = len(evs)

    def at(f, x):
        ser = m["series"][f]
        if x < len(ser) and abs(ser[x][0] - evs[x]["t"]) < 1e-6:
            return ser[x]
        return next((s_ for s_ in ser if abs(s_[0] - evs[x]["t"]) < 1e-6), None)
    member = {f: [] for f in flows}
    Ls = {f: [] for f in flows}
    nodes = []
    correct = []
    merged_first = None
    for x in range(n):
        groups = defaultdict(set)
        for f in flows:
            s_ = at(f, x)
            ok = bool(s_ and s_[1] is not None and s_[2] >= A)
            member[f].append(ok)
            Ls[f].append(s_[2] if s_ else None)
            if ok:
                groups[s_[1]].add(f)
        part = {frozenset(g) for g in groups.values()}
        correct.append(bool(tleaves) and part == tleaves)
        if merged_first is None:
            for g in groups.values():
                if len({leaf.get(f) for f in g if leaf.get(f)}) >= 2:
                    merged_first = {"close": x, "t": evs[x]["t"], "case": evs[x]["case"], "members": sorted(evs[x]["members"]),
                                    "group": sorted(g)}
                    break
    pt = json.loads((rd / ECG_DIR / "pairs_t.json").read_text()) if (rd / ECG_DIR / "pairs_t.json").exists() else []
    cov = [round(float(np.mean([v != "UNCERTAIN" for v in s_["pairs"].values()])), 3) for s_ in pt]
    loss = regain = 0
    for f in flows:
        seq = member[f]
        had = False
        for a, b in zip(seq, seq[1:]):
            if a and not b:
                loss += 1
                had = True
            elif b and not a and had:
                regain += 1
    # memberships that end below A: dL by case of the close's event
    drops = {}
    for f in flows:
        if any(member[f]) and not member[f][-1]:
            by = defaultdict(lambda: [0, 0.0, 0, 0.0])   # neg steps, neg sum, of them in-event, ...
            L = Ls[f]
            for x in range(1, n):
                if L[x] is None or L[x - 1] is None:
                    continue
                dl = L[x] - L[x - 1]
                if dl < 0:
                    c = evs[x]["case"]
                    part_ = f in evs[x]["members"]
                    by[c][0] += 1
                    by[c][1] += dl
                    if part_:
                        by[c][2] += 1
                        by[c][3] += dl
            drops[f] = {"L_end": L[-1], "L_max": max(v for v in L if v is not None), "first_member": member[f].index(True),
                        "last_member": n - 1 - member[f][::-1].index(True), "by_case": {c: v for c, v in by.items()},
                        "L_tail": [round(v, 2) if v is not None else None for v in L[-12:]],
                        "cases_tail": [evs[x]["case"] for x in range(max(0, n - 12), n)]}
    # final sibling merge
    fin = defaultdict(set)
    for f, v in m["final"].items():
        if v.get("member") and v.get("node") is not None:
            fin[v["node"]].add(f)
    merge_end = any(len({leaf.get(f) for f in g if leaf.get(f)}) >= 2 for g in fin.values())
    return {"phase": phase, "folder": rd.parent.parent.name, "campaign": rd.parent.name, "run": rd.name,
            "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2], "rep": int(rd.name.rsplit("-r", 1)[1]),
            "n_truth_leaves": len(tleaves), "A": A, "events": n,
            "final": {x: m["pairwise"].get(x) for x in ("precision", "recall", "coverage")}, "tree": m.get("tree_correct"),
            "merge_end": merge_end, "merged_first": merged_first, "cov_t": cov, "correct_t": correct,
            "loss": loss, "regain": regain, "drops": drops, "cases": [e["case"] for e in evs]}


def main():
    cmd = sys.argv[1]
    fn, runs = (a_row, part_a_runs()) if cmd == "a" else (b_row, part_b_runs())
    with Pool(10 if cmd == "a" else 12) as pool:
        for r in pool.imap_unordered(fn, runs):
            print(json.dumps(r, default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else float(o)), flush=True)


if __name__ == "__main__":
    main()
