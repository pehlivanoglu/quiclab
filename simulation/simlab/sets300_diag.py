#!/usr/bin/env python3
"""SETS / NPR at the 300-client leaf: analysis only, no new simulation (user 2026-11-19, items 1a / 1b).

    PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 19 \
        .venv/bin/python3 simulation/simlab/sets300_diag.py [run dir] [--npr-b]

Input: the run's frozen v2-owd onsets at T100 (tick files already in reports/sim-cache via frozen.py), read only.
1a  the frozen SETS engine on its own events (E0, grouping.sets_engine.replay_records, default Config as stage B):
    per close the observed set, what is missing from the leaf (no onset in this stimulus / onset in another event
    of the same stimulus), the stored table (distinct sets, the m estimate, the q bound), the groups at k = 2 / 3,
    and whether the observation counts toward an earlier stored set (and under which m / q).
1b  the frozen candidates (reports/npr-2026-11-17/frozen-2026-11-18/candidates.py, imported read-only, nothing
    written there) on E1-0.5 events (npr0b.form_window, W 0.5 s, aligned onsets t_onset - mrtt/2, NA by the
    STEP 0 rules): SETS@E1-0.5 (k = 2 / 3) as the reference row, NPR-A, then NPR-B (--npr-b). Per close: groups,
    leaf F1 (best group), pair precision / recall, false split; per candidate: first close with a group of F1 >= 0.9
    and with the exact leaf, CPU time.
Writes reports/sim-scale300/sets-diag.json and prints the tables (markdown).
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
FROZEN_NPR = QUICLAB / "reports" / "npr-2026-11-17" / "frozen-2026-11-18"
sys.path.insert(0, str(HERE))
import scale_ext  # noqa: E402,F401
import frozen  # noqa: E402,F401  (tick files from reports/sim-cache; never into run folders)
import stageb_compare  # noqa: E402,F401  (sys.path for r1, grouping_adapter, det_eval)
sys.path[:0] = [str(FROZEN_NPR), str(QUICLAB)]   # as candidates.py: the frozen copies first

RUN = QUICLAB / "simulation" / "runs" / "scale300" / "sim-Cs-G1-sburst-n300-pfifo-r1"
OUT = QUICLAB / "reports" / "sim-scale300" / "sets-diag.json"
DELTA_S = 0.15        # npr0b: the ACK test window before t0
F1_OK = 0.9


def f1(g, t):
    i = len(g & t)
    if not i:
        return 0.0
    p, r = i / len(g), i / len(t)
    return 2 * p * r / (p + r)


def close_stats(groups, leaf, clients):
    """groups at one close -> n, best leaf F1, exact, pair TP/FP/FN, ungrouped leaf members, false split."""
    best = max((f1(g, leaf) for g in groups), default=0.0)
    small = {}
    for c in clients:
        cg = [g for g in groups if c in g]
        if cg:
            small[c] = min(cg, key=lambda g: (len(g), sorted(g)))
    sizes = Counter(small[c] for c in leaf if c in small)   # leaf members per smallest group
    grouped = sum(sizes.values())
    tp = sum(n * (n - 1) // 2 for n in sizes.values())
    fn = grouped * (grouped - 1) // 2 - tp
    out_leaf = Counter(small[c] for c in clients if c in small and c not in leaf)
    fp = sum(sizes[g] * n for g, n in out_leaf.items())   # one leaf: only pairs leaf x non-leaf can be false
    return {"groups": len(groups), "leaf_f1": round(best, 4), "exact": any(g == leaf for g in groups),
            "tp": tp, "fp": fp, "fn": fn, "ungrouped": len(leaf) - grouped, "false_split": len(sizes) >= 2}


def load(rd: Path):
    import det_eval as d
    import grouping_score as gs
    import r1
    plan = json.loads((rd / "v3-plan.json").read_text())
    run = d.Run(rd)
    cfg, records, onsets = r1.onsets_at(rd, r1.LEVELS["T100"])
    ts = gs.truth_sets(rd, run, plan)
    leaves = [frozenset(v["members"]) for v in ts.values() if v["level"] == "leaf"]
    assert len(leaves) == 1, "one-leaf run expected"
    clients = sorted(s for s in run.subs if s != gs.CTRL)
    wins = json.loads((rd / "grouping" / "windows.json").read_text())
    return plan, run, cfg, records, onsets, ts, leaves[0], clients, wins


def stim_of(t, wins):
    for i, w in enumerate(wins):
        if w["start"] - 1.0 <= t <= w["start"] + 10.0:
            return i
    return None


def part_1a(rd, cfg, records, onsets, leaf, wins):
    from grouping import sets as S
    from grouping.sets_engine import replay_records
    import grouping_score as gs
    stim_on = {}   # stimulus -> flows with an onset in [start - 1, start + 10]
    for o in onsets:
        i = stim_of(o["t_onset"], wins)
        if i is not None and o["flow"] != gs.CTRL:
            stim_on.setdefault(i, set()).add(o["flow"])
    rows, prev = [], []

    def on_close(eng, e):
        obs = frozenset(m.flow for m in e.members) - {gs.CTRL}
        i = stim_of(e.t0, wins)
        on = stim_on.get(i, set())
        table = Counter(eng.table)
        m, _ = S.estimate_m(table, eng.scfg) if table else (0.0, 0)
        g2 = [frozenset(g.members) for g in S.groups(table, 2, eng.scfg)] if table else []
        g3 = [frozenset(g.members) for g in S.groups(table, 3, eng.scfg)] if table else []
        # does this observation count toward an earlier stored set (the frozen rule, at the current m)?
        hit = []
        for t in prev:
            q = S.qmiss(len(t), m, eng.scfg)
            if len(obs - t) <= eng.scfg.extra and len(t - obs) <= q:
                hit.append({"stored_size": len(t), "q": q, "missing_vs_stored": len(t - obs), "extra": len(obs - t)})
        rows.append({"close": len(rows) + 1, "t0": round(e.t0, 3), "stim": i, "size": len(obs),
                     "missing": len(leaf - obs), "missing_no_onset": len(leaf - obs - on),
                     "missing_other_event": len((leaf - obs) & on), "distinct_sets": len(table),
                     "m": round(m, 5), "q_leaf": S.qmiss(len(leaf), m, eng.scfg),
                     "counts_toward_earlier": hit[:3], "n_counts_toward_earlier": len(hit),
                     "k2": close_stats(g2, leaf, sorted(leaf)), "k3": close_stats(g3, leaf, sorted(leaf))})
        if len(obs) >= eng.scfg.min_set:
            prev.append(obs)

    t = time.process_time()
    replay_records(records, cfg, on_close=on_close)
    return rows, time.process_time() - t


def e1_events(rd, run, cfg, records, onsets, clients):
    import grouping_adapter as ga
    import npr0
    import npr0b
    half = {}
    for kind, _t, obj in records:
        if kind == "meta":
            half[obj.flow] = getattr(obj, "mrtt", 0.0) / 2 if cfg.align_mode == "half_mrtt" else 0.0
    sess = ga.sessions_of(run)
    acks = {s: npr0.ack_times(run, s) for s in clients}
    ons = sorted(({"flow": o["flow"], "t": o["t_onset"] - half.get(o["flow"], 0.0), "e": o["end"] - half.get(o["flow"], 0.0),
                   "arr": o["t_arrival"]} for o in onsets if o["flow"] in acks), key=lambda o: (o["t"], o["flow"]))
    eps = {c: [(o["t"], o["e"]) for o in ons if o["flow"] == c] for c in clients}
    ev = npr0b.form_window(ons, 0.5)

    def na_of(t0, close, members):   # npr0b STEP 0 rules, E1: in alarm since before t0 and still on at t0
        na = {}
        for c in clients:
            if c in members:
                continue
            j, lv = sess.get(c, (0.0, None))
            if t0 < j or (lv is not None and t0 >= lv):
                na[c] = "absent"
                continue
            a = acks[c]
            k = np.searchsorted(a, t0 - DELTA_S)
            if not (k < len(a) and a[k] <= close):
                na[c] = "no-ack"
                continue
            if any(x < t0 and y >= t0 for x, y in eps[c]):
                na[c] = "in-alarm"
        return na

    return [{"t0": e["t0"], "close": e["close"], "ones": sorted(e["m"]), "na": na_of(e["t0"], e["close"], e["m"])} for e in ev]


def part_1b(events, leaf, clients, npr_b: bool, wins):
    import candidates as C
    out = {}
    names = [("SETS@E1-0.5", 2), ("SETS@E1-0.5", 3), ("NPR-A", None)] + ([("NPR-B", None)] if npr_b else [])
    for name, k in names:
        t = time.process_time()
        series = C.run(name, events, clients, k=k)
        cpu = time.process_time() - t
        per = [close_stats(gs_, leaf, clients) | {"close": i + 1, "t0": round(e["t0"], 3), "stim": stim_of(e["t0"], wins),
                                                  "size": len(e["ones"]), "na": len(e["na"])}
               for i, (e, gs_) in enumerate(zip(events, series))]
        first_ok = next((p for p in per if p["leaf_f1"] >= F1_OK), None)
        first_ex = next((p for p in per if p["exact"]), None)
        tp, fp, fn = (sum(p[x] for p in per) for x in ("tp", "fp", "fn"))
        out[f"{name}" + (f" k={k}" if k else "")] = {
            "cpu_s": round(cpu, 2), "closes": len(per),
            "first_f1_ok": first_ok and {x: first_ok[x] for x in ("close", "t0", "stim")},
            "first_exact": first_ex and {x: first_ex[x] for x in ("close", "t0", "stim")},
            "mean_leaf_f1": round(float(np.mean([p["leaf_f1"] for p in per])), 4),
            "pair_p": round(tp / (tp + fp), 4) if tp + fp else None, "pair_r": round(tp / (tp + fn), 4) if tp + fn else None,
            "false_split_closes": sum(p["false_split"] for p in per), "per_close": per}
    return out


def main(argv):
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT
    argv = [x for i, x in enumerate(argv) if x != "--out" and (i == 0 or argv[i - 1] != "--out")]
    rd = Path(next((a for a in argv if not a.startswith("--")), RUN))
    plan, run, cfg, records, onsets, ts, leaf, clients, wins = load(rd)
    res = {"run": rd.name, "leaf_size": len(leaf), "stimuli": len(wins)}
    res["1a"], res["1a_cpu_s"] = part_1a(rd, cfg, records, onsets, leaf, wins)
    events = e1_events(rd, run, cfg, records, onsets, clients)
    res["e1_events"] = [{"t0": round(e["t0"], 3), "size": len(e["ones"]), "na": Counter(e["na"].values())} for e in events]
    res["1b"] = part_1b(events, leaf, clients, "--npr-b" in argv, wins)
    out.write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(f"written {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
