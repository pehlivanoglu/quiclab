#!/usr/bin/env python3
"""Step 4 of the 2026-11-13 brief: the half test (variant h) on top of Step 3 variant c,
and its measurements (a)-(g). Read-only, development set (K*, C1, M*, J1; G0 negatives),
single-queue AQMs, N1-N5 never opened, no ECG engine change.

    python3 scripts/grouping_step4.py run     CAMPAIGN OUT/step4-rows.jsonl          # c and h, m = 1, 2, 3; (e) late joiner
    python3 scripts/grouping_step4.py run-f   CAMPAIGN OUT/step4f-rows.jsonl         # (f): h, m = 3 on ECG event intervals
    python3 scripts/grouping_step4.py sum     OUT/step4-rows.jsonl.gz [OUT/step4f-rows.jsonl.gz]
    python3 scripts/grouping_step4.py plots   CAMPAIGN OUT/step4-rows.jsonl.gz OUT/

Variant c (Step 3, base): see grouping_step3.py. Variant h adds, per group k, a signed
S[i, k] per member and stored halves (A, B):
  * a group with >= HALF_MIN congested members (congested clients with E > 0) and no
    stored halves stores the event's best 2-split (step 3 side measurement b) as (A, B)
    and adds nothing;
  * otherwise members are assigned by the sign of S (0: stored half); with >= 2
    congested members per half, every congested member gets
    S += n_eff * ln(f(i, s_B) / f(i, s_A)), half templates = pointwise median of the
    half's congested members, leave-one-out for the tested member;
  * >= 2 members with S >= b and >= 2 with S <= -b: the group is replaced by an A child
    and a B child (members by sign, keep E; parent recorded); children start untested.

Constants (origin tag):
  ALPHA 0.01 (T), b = ln(1/ALPHA) + ln(N) (P), M_VALUES 1, 2, 3 (T) - as step 3;
  HALF_MIN 4 (P, brief: two per half);
  n_eff of the S increment = n_eff of the member's residual against its own half's
    template (unassigned member: half A) (FLAG);
  members with S = 0 outside the stored halves at a split go to the larger child (FLAG);
  S is computed with the state at the start of the event, the split is checked after the
    evidence update, new group and pruning of the event (FLAG: order);
  correct group (b) = member of >= 1 group and every group it is a member of has only
    members (E >= b) of its own leaf (FLAG);
  reliability (d): an entry (E > 0) is correct when the client's leaf is the majority
    leaf of the group's E > 0 entries, ties wrong (FLAG);
  time bins (b): since first event of the leaf 0/10/30/60/120/300 s, since run start
    0/60/120/240/480 s (FLAG); count bins 1..8, "more" (T);
  close time of an event = its interval end (hi) (FLAG);
  late joiner (e): hidden = first client of a leaf with >= 3 clients by name (T); the
    rest is "declared" when all its clients are members of one common group; the hidden
    client takes part from the next event; correct group = majority leaf = its leaf (FLAG);
  (f): ECG event intervals (-1 s, +2 s around t0, step 2 NEG_SPAN) for every run (FLAG).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grouping_step3 as s3  # noqa: E402

s2, ts, ga, d, gt1 = s3.s2, s3.ts, s3.ga, s3.d, s3.gt1
ALPHA, M_VALUES = s3.ALPHA, s3.M_VALUES
HALF_MIN = 4
ECG_DIR = s3.ECG_DIR
COUNT_BINS = [str(i) for i in range(1, 9)] + ["more"]
SINCE_FIRST = (0, 10, 30, 60, 120, 300)
SINCE_START = (0, 60, 120, 240, 480)
P_BINS = ((0.5, 0.7), (0.7, 0.9), (0.9, 0.99), (0.99, 0.999), (0.999, 1.01))
f2, pq, q3, family, prf, pooled = s3.f2, s3.pq, s3.q3, s3.family, s3.prf, s3.pooled


def tbin(x: float, edges) -> str:
    lab = None
    for e in edges:
        if x >= e:
            lab = e
    return f">= {edges[-1]}" if lab == edges[-1] else f"{lab}-{edges[edges.index(lab) + 1]}"


def cbin(n: int) -> str:
    return str(n) if n <= 8 else "more"


def pbin(p: float) -> str | None:
    for lo, hi in P_BINS:
        if lo <= p < hi:
            return f"{lo}-{min(hi, 1)}"
    return None


def sigmoid(e: float) -> float:
    return 1.0 / (1.0 + math.exp(-e)) if e < 50 else 1.0


def pure_in(mem, leaf, lf) -> bool:
    return bool(lf) and all(leaf.get(j) == lf for j in mem)


class Acc:
    """Per-run accumulators for (b) and (d)."""

    def __init__(self):
        self.b = defaultdict(lambda: [0, 0, 0, 0, 0])   # key -> clients, members, correct, tp, fp
        self.d = defaultdict(lambda: [0, 0])            # p bin -> entries, correct

    def close(self, members_of, leaf, same, seen, first_t, t_close, t_run0):
        """members_of: client -> list of member sets (E >= b, or ECG node co-members)."""
        for i, lf in leaf.items():
            n = seen.get(i, 0)
            if n < 1:
                continue
            groups = members_of.get(i, [])
            mem = bool(groups)
            ok = mem and all(pure_in(g, leaf, lf) for g in groups)
            partners = {j for g in groups for j in g if j != i}
            tp = sum(same.get("|".join(sorted((i, j))), False) for j in partners)
            for key in (("n", cbin(n)), ("first", tbin(t_close - first_t[i], SINCE_FIRST)),
                        ("start", tbin(t_close - t_run0, SINCE_START))):
                a = self.b["|".join(key)]
                a[0] += 1
                a[1] += mem
                a[2] += ok
                a[3] += tp
                a[4] += len(partners) - tp

    def to_json(self):
        return {"b": dict(self.b), "d": dict(self.d)}


# ═══ replay: variant c (half=False) and h (half=True) ═══════════════════

def replay4(events, subs, same, leaf, m, half, run_t0=0.0, hide=None, hook=None):
    """events: list of (row, qs, tp_all, part1 result). hide = (client, rest) for (e)."""
    N = len(subs)
    b = math.log(1 / ALPHA) + math.log(N)
    clip = b / m
    E: dict[int, dict[str, float]] = {}
    S: dict[int, dict[str, float]] = {}
    halves: dict[int, tuple[set, set] | None] = {}
    groups: dict[int, dict] = {}
    nxt = 0
    closes, traj, straj, cost = [], [], [], []
    member_since, mixed, memberships = {}, defaultdict(list), []
    took_part, first_t, first_member = Counter(), {}, {}
    acc = Acc()
    hidden = hide[0] if hide else None
    released_at, joiner = None, None
    for ev, (row, qs, tp_all, res) in enumerate(events):
        if hidden is not None and released_at is None:
            qs = {s: q for s, q in qs.items() if s != hidden}
            if hidden in res["participants"]:
                res = s3.partition_fixed(qs) if len(qs) >= 2 else {"P": None, "participants": [], "zero": [], "comparisons": 0}
        P = res["P"]
        parts = res["participants"]
        cong = set(parts) - set(res["zero"])
        for s_, v in tp_all.items():
            if v:
                took_part[s_] += 1
                first_t.setdefault(s_, row["lo"] + s2.MARGIN)
        active = {k: sorted(i for i in cong if E[k].get(i, 0) > 0) for k in E}
        active = {k: v for k, v in active.items() if len(v) >= 2}
        if hook:   # step 5: read-only observer (halves as stored before this event)
            hook(ev, row, qs, active, {k: halves.get(k) for k in active})
        cache = {}

        def tmpl(key, mem):
            if key not in cache:
                cache[key] = ts.template(qs, set(mem))[0] if mem else None
            return cache[key]
        comps = 0
        fk = {}
        for i in parts:
            for k in active:
                s = tmpl((k, i if i in active[k] else None), [x for x in active[k] if x != i])
                fk[(i, k)] = s3.fit_r(qs[i], s) if s is not None else (None, None)
                comps += 1
        dE = {}
        for i in parts:
            for k in active:
                f_own, ne = fk[(i, k)]
                if not f_own:
                    continue
                alt, alt_k = P.f0[i], 0
                for k2 in active:
                    if k2 != k and fk[(i, k2)][0] is not None and fk[(i, k2)][0] < alt:
                        alt, alt_k = fk[(i, k2)][0], k2
                x = ne * math.log(alt / f_own)
                if alt_k == 0:
                    x = max(-clip, min(clip, x))
                dE[(i, k)] = x
        # half test (variant h): increments with the state at the start of the event
        dS = {}
        if half:
            for k, mem in active.items():
                if len(mem) < HALF_MIN:
                    continue
                g = groups[k]
                if halves.get(k) is None:
                    side = s3.best_two_split(qs, mem)
                    if side:
                        halves[k] = (set(side), set(mem) - set(side))
                        g["halves_stored"] = ev
                    continue
                A, B = halves[k]

                def side_of(i):
                    v = S[k].get(i, 0.0)
                    return "A" if v > 0 else "B" if v < 0 else ("A" if i in A else "B" if i in B else None)
                sa = [i for i in mem if side_of(i) == "A"]
                sb = [i for i in mem if side_of(i) == "B"]
                if len(sa) < 2 or len(sb) < 2:
                    g.setdefault("half_skipped", 0)
                    g["half_skipped"] += 1
                    continue
                lv = {leaf.get(i) for i in mem}
                ev_mixed = len(lv) > 1 or None in lv
                for i in mem:
                    tA = tmpl((k, "A", i if i in sa else None), [x for x in sa if x != i])
                    tB = tmpl((k, "B", i if i in sb else None), [x for x in sb if x != i])
                    if tA is None or tB is None:
                        continue
                    rA, rB = s2.f_fit(qs[i], tA), s2.f_fit(qs[i], tB)
                    comps += 2
                    if not rA or not rB or rA[0] <= 0 or rB[0] <= 0:
                        continue
                    own = rB if side_of(i) == "B" else rA
                    ne = ts.n_eff(own[1]) if len(own[1]) >= 3 else float(len(own[1]))
                    dS[(i, k)] = ne * math.log(rB[0] / rA[0])
                    g.setdefault("incs", []).append([ev, round(dS[(i, k)], 2), bool(ev_mixed), leaf.get(i) and sorted(leaf[i])])
                g["tested"] = g.get("tested", 0) + 1
        # apply evidence, new group, pruning (variant c)
        for (i, k), x in dE.items():
            E[k][i] = E[k].get(i, 0.0) + x
        for (i, k), x in dS.items():
            S[k][i] = S[k].get(i, 0.0) + x
        gained = {i for (i, k), x in dE.items() if x >= 0}
        new = sorted(i for i in cong if i not in gained)
        if len(new) >= 2:
            E[nxt], S[nxt], halves[nxt] = {i: clip for i in new}, {}, None
            groups[nxt] = {"born": ev, "t": row["lo"], "members": new, "class": row["class"], "parent": None}
            nxt += 1
        for k in list(E):
            E[k] = {i: e for i, e in E[k].items() if e > 0}
            S[k] = {i: v for i, v in S[k].items() if i in E[k]}
            if len(E[k]) < 2:
                del E[k], S[k], halves[k]
                groups[k]["removed"] = ev
        s_snap = {str(k): {i: round(v, 2) for i, v in r_.items()} for k, r_ in S.items() if r_}   # before a split removes the parent
        # split (variant h)
        if half:
            for k in list(E):
                pos_ = [i for i, v in S[k].items() if v >= b]
                neg_ = [i for i, v in S[k].items() if v <= -b]
                if len(pos_) < 2 or len(neg_) < 2:
                    continue
                A, B = halves[k] or (set(), set())
                ca, cb, undecided = {}, {}, 0
                for i, e in E[k].items():
                    v = S[k].get(i, 0.0)
                    if v > 0 or (v == 0 and i in A):
                        ca[i] = e
                    elif v < 0 or (v == 0 and i in B):
                        cb[i] = e
                    else:
                        undecided += 1
                        (ca if len(ca) >= len(cb) else cb)[i] = e
                kids = []
                for part in (ca, cb):
                    E[nxt], S[nxt], halves[nxt] = dict(part), {}, None
                    groups[nxt] = {"born": ev, "t": row["lo"], "members": sorted(part), "class": "split", "parent": k}
                    kids.append(nxt)
                    nxt += 1
                g = groups[k]
                g.update({"split_at": ev, "children": kids, "split_sides": [sorted(ca), sorted(cb)],
                          "split_undecided": undecided, "removed": ev})
                del E[k], S[k], halves[k]
        # memberships
        now = {(i, k) for k, r_ in E.items() for i, e in r_.items() if e >= b}
        for key in now - set(member_since):
            i, k = key
            lab = s3.majority([j for j, e in E[k].items() if e >= b], leaf)
            member_since[key] = (ev, row["lo"], bool(leaf.get(i)) and leaf.get(i) == lab)
            if i not in first_member:
                first_member[i] = (took_part[i], member_since[key][2], ev)
        for key in set(member_since) - now:
            e0, t0, ok = member_since.pop(key)
            w = mixed.pop(key, [])
            memberships.append({"client": key[0], "group": key[1], "from": e0, "to": ev, "dur_events": ev - e0,
                                "dur_s": row["lo"] - t0, "right": ok, "mixed_closes": len(w),
                                "mixed_s": (w[-1] - w[0]) if w else 0.0})
        mem_sets = {k: [j for j, e in r_.items() if e >= b] for k, r_ in E.items()}
        for (i, k) in now:
            if not leaf.get(i) or any(leaf.get(j) != leaf.get(i) for j in mem_sets[k]):
                mixed[(i, k)].append(row["lo"])
        # (b), (d)
        members_of = defaultdict(list)
        for k, ms in mem_sets.items():
            for i in ms:
                members_of[i].append(ms)
        acc.close(members_of, leaf, same, took_part, first_t, row["hi"], run_t0)
        for k, r_ in E.items():
            lab = s3.majority(list(r_), leaf)
            for i, e in r_.items():
                pb = pbin(sigmoid(e))
                if pb:
                    acc.d[pb][0] += 1
                    acc.d[pb][1] += bool(leaf.get(i)) and leaf.get(i) == lab
        # (e) late joiner
        if hidden is not None:
            if released_at is None:
                if any(set(hide[1]) <= set(ms) for ms in mem_sets.values()):
                    released_at = ev
                    joiner = {"released_event": ev, "released_t": row["hi"], "events": 0, "joined": None,
                              "wrong_ever": False, "other_active": False}
            elif ev > released_at:
                if tp_all.get(hidden):
                    joiner["events"] += 1
                own = [k for k, ms in mem_sets.items() if hidden in ms]
                for k in own:
                    if s3.majority(mem_sets[k], leaf) != leaf.get(hidden):
                        joiner["wrong_ever"] = True
                others = [k for k in active if not any(j in hide[1] for j in active[k])]
                joiner["other_active"] |= bool(others)
                if joiner["joined"] is None and any(s3.majority(mem_sets[k], leaf) == leaf.get(hidden) for k in own):
                    joiner["joined"] = {"events": joiner["events"], "s": row["hi"] - joiner["released_t"],
                                        "ev": ev}
        cost.append({"part1": res["comparisons"], "update": comps, "active": len(active),
                     "state": sum(len(v) for v in E.values()) + sum(len(v) for v in S.values()), "groups": len(E)})
        closes.append(s3.pair_counts(E, b, subs, same))
        traj.append({str(k): {i: round(e, 2) for i, e in r_.items()} for k, r_ in E.items()})
        straj.append(s_snap)
    if hidden is not None:
        return joiner
    last_t = events[-1][0]["hi"] if events else 0
    for (i, k), (e0, t0, ok) in member_since.items():
        w = mixed.get((i, k), [])
        memberships.append({"client": i, "group": k, "from": e0, "to": None, "dur_events": len(events) - e0,
                            "dur_s": last_t - t0, "right": ok, "mixed_closes": len(w),
                            "mixed_s": (w[-1] - w[0]) if w else 0.0})
    for k, g in groups.items():
        lv = [leaf.get(i) for i in g["members"]]
        g["merged"] = len(set(lv)) > 1 or any(not x for x in lv)
        # leaves over the group's life (E > 0 entries at any close)
        life = {leaf.get(i) for t in traj for i in t.get(str(k), {})}
        g["life_mixed"] = len(life) > 1 or None in life
        g["separated_after"] = None
        if g["merged"]:
            for e2 in range(g["born"] + 1, len(traj)):
                r_ = traj[e2].get(str(k))
                if r_ is None:
                    break
                ls = {leaf.get(i) for i in r_}
                if len(ls) == 1 and all(ls):
                    g["separated_after"] = e2 - g["born"]
                    break
        if "split_sides" in g:
            sides = [{leaf.get(i) for i in s_} for s_ in g["split_sides"]]
            g["split_is_leaf_boundary"] = all(len(x) == 1 and None not in x for x in sides) and sides[0] != sides[1]
    return {"b": b, "closes": closes, "traj": traj, "straj": straj, "groups": {str(k): v for k, v in groups.items()},
            "memberships": memberships, "first_member": first_member, "took_part_total": dict(took_part),
            "ctrl_ever": any("sub-ctrl" in r_ for t in traj for r_ in t.values()), "cost": cost, "acc": acc.to_json()}


# ═══ ECG views for (a), (b), (d)-style numbers ══════════════════════════

def ecg_view4(rd: Path, subs, same, leaf, events, run_t0):
    m = json.loads((rd / ECG_DIR / "metrics.json").read_text())
    from grouping import Config
    A = Config.from_dict(m["config"]).A
    base = s3.ecg_view(rd, subs, same, [(e[0]["lo"] + s2.MARGIN, {s for s, v in e[2].items() if v}) for e in events])
    by_t = defaultdict(dict)
    for f, ser in m["series"].items():
        for t, node, L in ser:
            by_t[t][f] = (node, L)
    starts = [(e[0]["lo"] + s2.MARGIN, {s for s, v in e[2].items() if v}) for e in events]
    acc = Acc()
    since, mixed, memberships = {}, defaultdict(list), []
    first_t = {}
    for t0, took in starts:
        for s in took:
            first_t.setdefault(s, t0)
    times = sorted(by_t)
    for x, t in enumerate(times):
        snap = by_t[t]
        nodes = defaultdict(list)
        for f, (node, L) in snap.items():
            if node is not None and L >= A:
                nodes[node].append(f)
        now = {(f, node) for node, ms in nodes.items() for f in ms}
        for key in now - set(since):
            f, node = key
            since[key] = (x, t, bool(leaf.get(f)) and leaf.get(f) == s3.majority(nodes[node], leaf))
        for key in set(since) - now:
            e0, t0, ok = since.pop(key)
            w = mixed.pop(key, [])
            memberships.append({"right": ok, "mixed_closes": len(w), "dur_events": x - e0, "dur_s": t - t0})
        for (f, node) in now:
            if not leaf.get(f) or any(leaf.get(j) != leaf.get(f) for j in nodes[node]):
                mixed[(f, node)].append(t)
        seen = {s: sum(1 for t0, took in starts if t0 <= t and s in took) for s in leaf}
        members_of = defaultdict(list)
        for ms in nodes.values():
            for f in ms:
                members_of[f].append(ms)
        acc.close(members_of, leaf, same, seen, first_t, t, run_t0)
    for key, (e0, t0, ok) in since.items():
        w = mixed.get(key, [])
        memberships.append({"right": ok, "mixed_closes": len(w), "dur_events": len(times) - e0, "dur_s": None})
    base.update({"memberships": memberships, "acc": acc.to_json()})
    return base


# ═══ per run ═══════════════════════════════════════════════════════════

def load_events(rd: Path, ecg_intervals: bool = False):
    run = ga.load_run(rd)
    group = rd.parent.name
    truth = json.loads((rd / ECG_DIR / "truth.json").read_text())
    subs = sorted(run.subs)
    windows = [] if group == "G0" else json.loads((rd / "grouping" / "windows.json").read_text())
    events = []
    for row, qs, tp in s2.events_of(rd, ecg_intervals=ecg_intervals):
        res = s3.partition_fixed(qs)
        tp_all = s2.truth_partition(windows, row["lo"] + s2.MARGIN, row["hi"] - s2.MARGIN, subs)
        events.append((row, qs, tp_all, res))
    events.sort(key=lambda e: e[0]["lo"])
    return run, truth, subs, windows, events


def strip(x: dict, keep_traj: bool) -> dict:
    if not keep_traj:
        x = {k: v for k, v in x.items() if k not in ("traj", "straj")}
    return x


def base_row(rd, run, truth, subs, events):
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    recorded = {f"{a}->{b}" for (a, b), _ in gt1.router_egresses(run)}
    run_hops = {s: sorted({f"{a}->{b}" for a, b in d.path_hops(run, run.pub, s)} & recorded) for s in subs}
    row = {"campaign": rd.parent.name, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "n_clients": len(subs), "n_events": len(events),
           "events": [{"lo": e[0]["lo"], "hi": e[0]["hi"], "class": e[0]["class"],
                       "congested": sorted(set(e[3]["participants"]) - set(e[3]["zero"])),
                       "truth_congested": sorted(s for s, v in e[2].items() if v)} for e in events],
           "leaf": {s: sorted(v) for s, v in leaf.items()}, "run_hops": run_hops}
    if rd.parent.name == "G0":
        row["gt1_hops"] = sorted(h for h, v in ga.gt1_hop_episodes(run).items() if v)
    return row, leaf


def step4_run(rd: Path) -> dict:
    run, truth, subs, windows, events = load_events(rd)
    row, leaf = base_row(rd, run, truth, subs, events)
    same = truth["pairs_leaf"]
    for m in M_VALUES:
        for v, half in (("c", False), ("h", True)):
            row[f"{v}{m}"] = replay4(events, subs, same, leaf, m, half)
    try:
        row["ecg"] = ecg_view4(rd, subs, same, leaf, events, 0.0)
    except FileNotFoundError:
        row["ecg"] = None
    # (e) late joiner
    late = []
    leaves = defaultdict(list)
    for s, l in leaf.items():
        leaves[l].append(s)
    if rd.parent.name != "G0":
        for l, cl in sorted(leaves.items(), key=lambda x: sorted(x[0])):
            if len(cl) < 3:
                continue
            hid = sorted(cl)[0]
            rest = sorted(set(cl) - {hid})
            for m in M_VALUES:
                for v, half in (("c", False), ("h", True)):
                    j = replay4(events, subs, same, leaf, m, half, hide=(hid, rest))
                    late.append({"variant": f"{v}{m}", "hidden": hid, "leaf": sorted(l), "result": j})
    row["late"] = late
    return row


def step4f_run(rd: Path) -> dict:
    out = {}
    for tag, ecg_iv in (("windows", False), ("ecg", True)):
        run, truth, subs, windows, events = load_events(rd, ecg_intervals=ecg_iv)
        row, leaf = base_row(rd, run, truth, subs, events)
        x = replay4(events, subs, truth["pairs_leaf"], leaf, 3, True)
        out[tag] = {"n_events": len(events), "intervals": [(e[0]["lo"], e[0]["hi"]) for e in events],
                    "h3": strip(x, False)}
        out.update({k: row[k] for k in ("campaign", "run", "type", "aqm", "leaf")})
        if tag == "windows":
            # windows events (with margin) for the lost / merged count
            out["win_events"] = [(e[0]["lo"] + s2.MARGIN, e[0]["hi"] - s2.MARGIN) for e in events]
    return out


def _write(fn, runs, out):
    with Pool(10) as pool, out.open("w") as fh:
        for r in pool.imap_unordered(fn, runs):
            fh.write(json.dumps(r) + "\n")
            print(r["run"], flush=True)


def cmd_run(campaign: Path, out: Path) -> None:
    _write(step4_run, s2.runs_of(campaign, s2.CAMPAIGN_DIRS), out)


def cmd_run_f(campaign: Path, out: Path) -> None:
    _write(step4f_run, [rd for rd in s2.runs_of(campaign, s2.CAMPAIGN_DIRS) if rd.parent.name != "G0"], out)


# ═══ summary ═══════════════════════════════════════════════════════════

VARS = [f"{v}{m}" for v in "ch" for m in M_VALUES]


def fm_rates(ms):
    """(n, wrong at declaration, wrong at some close)."""
    return len(ms), sum(not x["right"] for x in ms), sum(x["mixed_closes"] > 0 for x in ms)


def rate(a, n):
    return f2(a / n if n else None)


def sec_a(R, pos, neg, byfa, byf):
    print("## (a) Step 3 table, variants c and h, ECG\n")
    print("### Pair precision / recall / coverage (last event; pooled over event closes)\n")
    print("| family | AQM | runs | " + " | ".join(f"{v} last | {v} closes" for v in VARS) + " | ECG last | ECG closes |")
    print("|---|---|---|" + "---|" * (2 * len(VARS) + 2))
    for k in sorted(byfa):
        rs = byfa[k]
        cells = []
        for v in VARS:
            cells += [" / ".join(map(f2, prf(pooled(r[v]["closes"][-1] for r in rs if r[v]["closes"])))),
                      " / ".join(map(f2, prf(pooled(c for r in rs for c in r[v]["closes"]))))]
        ec = [r["ecg"] for r in rs if r["ecg"]]
        cells += [" / ".join(map(f2, prf(pooled(e["closes"][-1] for e in ec if e["closes"])))),
                  " / ".join(map(f2, prf(pooled(c for e in ec for c in e["closes"]))))]
        print(f"| {k[0]} | {k[1]} | {len(rs)} | " + " | ".join(cells) + " |")
    print("\n### False-membership rate (declared / at some close), memberships n\n")
    print("Same definitions for ECG: membership = (client, ECG node) with the client a member (node set, L >= A) at an "
          "ECG close; judged at declaration by the node's majority leaf, and per close (node holds a member of another leaf).\n")
    print("| family | " + " | ".join(f"{v} n | {v} decl | {v} close" for v in VARS) + " | ECG n | ECG decl | ECG close |")
    print("|---|" + "---|" * (3 * len(VARS) + 3))
    tot = defaultdict(lambda: [0, 0, 0])
    for k in sorted(byf):
        cells = []
        for v in VARS + ["ecg"]:
            ms = [x for r in byf[k] if r.get(v) for x in r[v]["memberships"]]
            n, a, c = fm_rates(ms)
            t = tot[v]
            t[0], t[1], t[2] = t[0] + n, t[1] + a, t[2] + c
            cells += [str(n), rate(a, n), rate(c, n)]
        print(f"| {k} | " + " | ".join(cells) + " |")
    print("| **all positives** | " + " | ".join(f"{tot[v][0]} | {rate(tot[v][1], tot[v][0])} | {rate(tot[v][2], tot[v][0])}"
                                               for v in VARS + ["ecg"]) + " |")
    print("\nWrong memberships (at some close): how long, events p50 / p90 (all positives): "
          + "; ".join(f"{v} {pq([x['mixed_closes'] for r in pos for x in r[v]['memberships'] if x['mixed_closes']])}"
                      for v in VARS) + ".\n")
    print("### Events to membership per client (p50 / p90; never)\n")
    print("| family | " + " | ".join(f"{v}" for v in VARS) + " | ECG |")
    print("|---|" + "---|" * (len(VARS) + 1))
    for k in sorted(byf):
        rs = byf[k]
        cells = []
        for v in VARS:
            fm = [x[0] for r in rs for s, x in r[v]["first_member"].items() if r["leaf"].get(s)]
            never = sum(1 for r in rs for s, n in r[v]["took_part_total"].items()
                        if n and r["leaf"].get(s) and s not in r[v]["first_member"])
            cells.append(f"{pq(fm)}; {never}")
        ev = [n for r in rs if r["ecg"] for s, n in r["ecg"]["events_to_member"].items() if r["leaf"].get(s)]
        never = sum(1 for r in rs if r["ecg"] for s, n in r["c1"]["took_part_total"].items()
                    if n and r["leaf"].get(s) and s not in r["ecg"]["events_to_member"])
        cells.append(f"{pq(ev)}; {never}")
        print(f"| {k} | " + " | ".join(cells) + " |")
    print("\n### Mixed groups (first members from two or more leaves)\n")
    print("c: separated = a later close where the group's E > 0 entries are one leaf. h: the same, or the group was split "
          "(h split = into an A child and a B child; 'boundary' = both children one leaf, different leaves).\n")
    print("| family | " + " | ".join(f"{v} mixed / separated / events p50 / p90" + (" / split / boundary" if v[0] == "h" else "")
                                     for v in VARS) + " |")
    print("|---|" + "---|" * len(VARS))
    for k in sorted(byf):
        cells = []
        for v in VARS:
            gs = [g for r in byf[k] for g in r[v]["groups"].values() if g["merged"]]
            ev = []
            for g in gs:
                e = [x for x in (g["separated_after"], (g["split_at"] - g["born"]) if "split_at" in g else None) if x is not None]
                if e:
                    ev.append(min(e))
            c = f"{len(gs)} / {len(ev)} / {pq(ev)}"
            if v[0] == "h":
                sp = [g for g in gs if "split_at" in g]
                c += f" / {len(sp)} / {sum(bool(g.get('split_is_leaf_boundary')) for g in sp)}"
            cells.append(c)
        print(f"| {k} | " + " | ".join(cells) + " |")
    print("\n### sub-ctrl\n")
    print("; ".join(f"{v}: E > 0 in {sum(r[v]['ctrl_ever'] for r in R)} runs" for v in VARS) + ".\n")
    print("### Negatives (G0), topology truth of step 2b (SAME pairs at the end, right / wrong)\n")
    print("| type | AQM | " + " | ".join(VARS) + " | ECG |")
    print("|---|---|" + "---|" * (len(VARS) + 1))
    tot = Counter()
    for r in sorted(neg, key=lambda x: (x["type"], x["aqm"])):
        hops = set(r["gt1_hops"])
        cells = []
        for v in VARS:
            x = r[v]
            last = x["traj"][-1] if x["traj"] else {}
            ok = bad = 0
            for r_ in last.values():
                mem = sorted(i for i, e in r_.items() if e >= x["b"])
                for a_ in range(len(mem)):
                    for c_ in mem[a_ + 1:]:
                        good = bool(set(r["run_hops"].get(mem[a_], [])) & set(r["run_hops"].get(c_, [])) & hops)
                        ok += good
                        bad += not good
            tot[(v, 0)] += ok
            tot[(v, 1)] += bad
            cells.append(f"{ok} / {bad}")
        eo = eb = 0
        if r["ecg"]:
            for p, w in r["ecg"]["pairs_final"].items():
                if w["decided"] == "SAME":
                    a_, c_ = p.split("|")
                    good = bool(set(r["run_hops"].get(a_, [])) & set(r["run_hops"].get(c_, [])) & hops)
                    eo += good
                    eb += not good
        tot[("ecg", 0)] += eo
        tot[("ecg", 1)] += eb
        print(f"| {r['type']} | {r['aqm']} | " + " | ".join(cells) + f" | {eo} / {eb} |")
    print("| **total** | | " + " | ".join(f"{tot[(v, 0)]} / {tot[(v, 1)]}" for v in VARS + ["ecg"]) + " |\n")
    print("### Cost\n")
    for v in VARS:
        c = [x for r in R for x in r[v]["cost"]]
        print(f"- {v}: template comparisons per event (evidence + half test) p50 / p90 {pq([x['update'] for x in c])}; "
              f"state entries (E and S) p50 / p90 / max {pq([x['state'] for x in c])} / {max(x['state'] for x in c)}; "
              f"groups max {max(x['groups'] for x in c)}")
    print(f"- Part 1 procedure (all variants): p10 / p50 / p90 {q3([x['part1'] for r in R for x in r['c1']['cost']], '.0f')}\n")


def acc_table(rows, keyfn, kind, order, title):
    print(f"#### {title}\n")
    print("| bin | " + " | ".join(f"{v} clients / member / correct / pair P" for v in VARS + ["ecg"]) + " |")
    print("|---|" + "---|" * (len(VARS) + 1))
    for b_ in order:
        cells = []
        for v in VARS + ["ecg"]:
            a = [0, 0, 0, 0, 0]
            for r in rows:
                x = r.get(v)
                if not x:
                    continue
                y = x["acc"]["b"].get(f"{kind}|{b_}")
                if y:
                    a = [p + q for p, q in zip(a, y)]
            cells.append(f"{a[0]} / {rate(a[1], a[0])} / {rate(a[2], a[1])} / {rate(a[3], a[3] + a[4])}")
        print(f"| {b_} | " + " | ".join(cells) + " |")
    print()


def sec_b(pos, byf):
    print("## (b) Accuracy by events seen\n")
    print("Per event close and client with a leaf: member = member (E >= b) of some group; correct = every group it is a "
          "member of holds only members of its leaf (share of members); pair P over its SAME partners. ECG: its own closes, "
          "events seen = step 4 events of the client's leaf that started before the close.\n")
    tb1 = [f"{a}-{b}" for a, b in zip(SINCE_FIRST, SINCE_FIRST[1:])] + [f">= {SINCE_FIRST[-1]}"]
    tb2 = [f"{a}-{b}" for a, b in zip(SINCE_START, SINCE_START[1:])] + [f">= {SINCE_START[-1]}"]
    multi = [r for r in pos if r["campaign"] in ("K1", "K6", "C1", "J1") or r["type"].startswith("indep")]
    single = [r for r in pos if r not in multi]
    for lab, rs in (("all positives", pos), ("multi-group families (K1, K6, C1, J1, M6 indep)", multi),
                    ("single-group families", single)):
        print(f"### {lab}\n")
        acc_table(rs, None, "n", COUNT_BINS, "by events of the client's leaf seen")
        acc_table(rs, None, "first", tb1, "by seconds since the client's first such event")
        acc_table(rs, None, "start", tb2, "by seconds since the start of the run")


def leaf_kind(g, run_leaf):
    return "mixed" if g["life_mixed"] else "one leaf"


def sec_c(pos):
    print("## (c) Half test behaviour (variant h)\n")
    print("Group type over its life: 'one leaf' = every E > 0 entry at every close has the same leaf; 'mixed' otherwise "
          "(a client without a leaf counts as another leaf). Increments are per tested congested member and event; "
          "'event mixed' = the event's congested members span two leaves.\n")
    for m in M_VALUES:
        v = f"h{m}"
        gs = [(r, g) for r in pos for g in r[v]["groups"].values()]
        print(f"### {v}\n")
        print("| group type | groups | tested (>= 1 event with S increments) | halves stored, never tested | never 4 congested "
              "| split | events from creation to split p50 / p90 | split = leaf boundary |")
        print("|---|---|---|---|---|---|---|---|")
        for lab in ("one leaf", "mixed"):
            sel = [g for r, g in gs if leaf_kind(g, r["leaf"]) == lab]
            sp = [g for g in sel if "split_at" in g]
            print(f"| {lab} | {len(sel)} | {sum(g.get('tested', 0) > 0 for g in sel)} | "
                  f"{sum('halves_stored' in g and not g.get('tested') for g in sel)} | {sum('halves_stored' not in g for g in sel)} "
                  f"| {len(sp)} | {pq([g['split_at'] - g['born'] for g in sp])} | {sum(bool(g.get('split_is_leaf_boundary')) for g in sp)} |")
        print("\nFalse splits (one-leaf groups split), events from halves stored to split:",
              pq([g["split_at"] - g["halves_stored"] for r, g in gs if leaf_kind(g, r["leaf"]) == "one leaf" and "split_at" in g]),
              "; tested one-leaf groups:", sum(1 for r, g in gs if leaf_kind(g, r["leaf"]) == "one leaf" and g.get("tested")), "\n")
        print("Per-event S increment (nats):\n")
        print("| group type | event | increments | p1 / p10 / p50 / p90 / p99 | share |dS| >= b/3 |\n|---|---|---|---|---|")
        bb = math.log(100) + math.log(7)
        for lab in ("one leaf", "mixed"):
            for evm in (False, True):
                inc = [x[1] for r, g in gs if leaf_kind(g, r["leaf"]) == lab for x in g.get("incs", []) if x[2] == evm]
                if not inc:
                    continue
                p = np.percentile(inc, [1, 10, 50, 90, 99])
                print(f"| {lab} | {'mixed' if evm else 'one leaf'} | {len(inc)} | " + " / ".join(f"{x:.1f}" for x in p)
                      + f" | {np.mean(np.abs(inc) >= bb / 3):.2f} |")
        print("\nMixed groups: |S| per member at the last tested event, by whether its leaf is the majority of the group "
              "(sign is arbitrary, so only |S|): see rows.\n")
        never = [g for r, g in gs if "halves_stored" not in g]
        nk = {(r["run"], r["campaign"], k) for r in pos for k, g in r[v]["groups"].items() if "halves_stored" not in g}
        ms = [x for r in pos for x in r[v]["memberships"] if (r["run"], r["campaign"], str(x["group"])) in nk]
        n, a, c = fm_rates(ms)
        print(f"Groups never tested (never >= {HALF_MIN} congested members): {len(never)} of {len(gs)}; their memberships "
              f"{n}, false at declaration {rate(a, n)}, at some close {rate(c, n)}.\n")


def sec_d(R):
    print("## (d) Confidence score p = 1 / (1 + exp(-E))\n")
    print("Every (client, group) entry with E > 0 at every event close (positives and G0). Correct = the client's leaf is "
          "the group's majority leaf (G0 has no leaves: all G0 entries count as wrong, so G0 is shown apart).\n")
    for lab, rs in (("positives", [r for r in R if r["campaign"] != "G0"]),):
        print(f"### {lab}\n")
        print("| p bin | " + " | ".join(f"{v} entries / correct" for v in VARS) + " |")
        print("|---|" + "---|" * len(VARS))
        for lo, hi in P_BINS:
            key = f"{lo}-{min(hi, 1)}"
            cells = []
            for v in VARS:
                a = [0, 0]
                for r in rs:
                    y = r[v]["acc"]["d"].get(key)
                    if y:
                        a = [a[0] + y[0], a[1] + y[1]]
                cells.append(f"{a[0]} / {rate(a[1], a[0])}")
            print(f"| {key} | " + " | ".join(cells) + " |")
        print()


def sec_e(pos):
    print("## (e) Late joiner (replay)\n")
    print("Per run and leaf with >= 3 clients: the first client by name is hidden until the rest of the leaf are all "
          "members of one common group, then takes part. Events = events of its leaf after release; seconds from the "
          "release close. 'other active' = another group (none of the rest in it) was active at some event after release.\n")
    print("| variant | case | cases | released | joined the correct group | events p50 / p90 | seconds p50 / p90 | ever in a wrong group |")
    print("|---|---|---|---|---|---|---|---|")
    for v in VARS:
        L = [x for r in pos for x in r["late"] if x["variant"] == v]
        for lab, sel in (("another group active", lambda j: j and j["other_active"]),
                         ("its group the only one", lambda j: j and not j["other_active"]),
                         ("never released", lambda j: j is None)):
            xs = [x["result"] for x in L if sel(x["result"])]
            if lab == "never released":
                print(f"| {v} | {lab} | {len(xs)} | - | - | - | - | - |")
                continue
            jn = [j["joined"] for j in xs if j["joined"]]
            print(f"| {v} | {lab} | {len(xs)} | {len(xs)} | {len(jn)} | {pq([j['events'] for j in jn])} | "
                  f"{pq([j['s'] for j in jn], '.1f')} | {sum(j['wrong_ever'] for j in xs)} |")
    print()


def sec_f(Fpath):
    F = s2.read_jsonl(Fpath)
    print("## (f) Variant h, m = 3: windows.json intervals vs ECG event intervals\n")
    lost = merged = total = 0
    for r in F:
        ecg = r["ecg"]["intervals"]
        for a, b in r["win_events"]:
            total += 1
            cov = [e for e in ecg if e[0] <= b and e[1] >= a]
            lost += not cov
        for lo, hi in ecg:
            merged += sum(1 for a, b in r["win_events"] if lo <= b and hi >= a) >= 2
    print(f"{len(F)} runs (positives). windows.json events {total} (sum), ECG events {sum(r['ecg']['n_events'] for r in F)}; "
          f"windows events with no overlapping ECG event (lost) {lost}; ECG events overlapping >= 2 windows events (merged) "
          f"{merged}.\n")
    print("| family | windows: last P / R / cov | ECG iv: last P / R / cov | windows: closes P | ECG iv: closes P | "
          "windows: false memb decl / close | ECG iv: false memb decl / close | windows: events to membership p50 / p90 | ECG iv |")
    print("|---|---|---|---|---|---|---|---|---|")
    byf = defaultdict(list)
    for r in F:
        byf[family(r)].append(r)
    for k in sorted(byf):
        rs = byf[k]
        cells = []
        for tag in ("windows", "ecg"):
            xs = [r[tag]["h3"] for r in rs]
            cells.append(" / ".join(map(f2, prf(pooled(x["closes"][-1] for x in xs if x["closes"])))))
        for tag in ("windows", "ecg"):
            xs = [r[tag]["h3"] for r in rs]
            cells.append(f2(prf(pooled(c for x in xs for c in x["closes"]))[0]))
        for tag in ("windows", "ecg"):
            n, a, c = fm_rates([m for r in rs for m in r[tag]["h3"]["memberships"]])
            cells.append(f"{rate(a, n)} / {rate(c, n)} (n {n})")
        for tag in ("windows", "ecg"):
            fm = [x[0] for r in rs for s, x in r[tag]["h3"]["first_member"].items() if r["leaf"].get(s)]
            cells.append(pq(fm))
        print(f"| {k} | " + " | ".join(cells) + " |")
    print()


def cmd_sum(path: Path, fpath: Path | None) -> None:
    R = s2.read_jsonl(path)
    pos = [r for r in R if r["campaign"] != "G0"]
    neg = [r for r in R if r["campaign"] == "G0"]
    byfa, byf = defaultdict(list), defaultdict(list)
    for r in pos:
        byfa[(family(r), r["aqm"])].append(r)
        byf[family(r)].append(r)
    print("# Step 4: half test (variant h) vs Step 3 variant c and ECG\n")
    print(f"{len(R)} runs ({len(pos)} with windows, {len(neg)} G0), {sum(r['n_events'] for r in R)} events. "
          f"Variants c1..c3 = Step 3 variant c with m = 1..3; h1..h3 = c plus the half test. ECG = v1.2, delta 0.15 s, v2-owd.\n")
    sec_a(R, pos, neg, byfa, byf)
    sec_b(pos, byf)
    sec_c(pos)
    sec_d(R)
    sec_e(pos)
    if fpath:
        sec_f(fpath)


# ═══ plots ═════════════════════════════════════════════════════════════

def cmd_plots(campaign: Path, path: Path, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    R = {r["run"] + "@" + r["campaign"]: r for r in s2.read_jsonl(path)}
    want = [("base", "M1", "grp-burstcap-pfifo-r1"), ("split", "K1", "grp-hier-pfifo-r1"), ("depth", "K6", "grp-depth-pfifo-r1"),
            ("J1 hierjit20 (realised sd 12.6 ms)", "J1", "grp-hierjit20-pfifo-r1"),
            ("independent timing", "M6", "grp-indepfast-pfifo-r1"), ("G0 calmuneven (no leaf truth)", "G0", "grp-calmuneven-pfifo-r1")]
    for n, (lab, g, run) in enumerate(want, 1):
        r = R.get(f"{run}@{g}")
        if not r:
            continue
        leaf = {s: frozenset(v) for s, v in r["leaf"].items()}
        fig, axes = plt.subplots(2, len(M_VALUES), figsize=(13, 6.5), sharex=True)
        for col, m in enumerate(M_VALUES):
            x = r[f"h{m}"]
            for row_i, (key, ylab) in enumerate((("traj", "E[i, k] nats"), ("straj", "S[i, k] nats"))):
                ax = axes[row_i, col]
                series = defaultdict(lambda: [[], []])
                for ev, st in enumerate(x[key]):
                    for k, r_ in st.items():
                        for i, e in r_.items():
                            series[(i, k)][0].append(ev)
                            series[(i, k)][1].append(e)
                for (i, k), (xs, ys) in series.items():
                    mem = list(x["traj"][xs[-1]].get(k, {})) or [i]
                    lk = s3.majority(mem, leaf)
                    right = bool(leaf.get(i)) and leaf.get(i) == lk
                    ax.plot(xs, ys, ".-", lw=0.7, ms=2, color="C2" if right else "C3", alpha=0.7)
                for gk, gg in x["groups"].items():
                    if "split_at" in gg:
                        ax.axvline(gg["split_at"], color="C0", lw=0.6, ls=":")
                for yv in ((x["b"],) if key == "traj" else (x["b"], -x["b"])):
                    ax.axhline(yv, color="0.3", ls="--", lw=0.8)
                ax.set_yscale("symlog", linthresh=1)
                if col == 0:
                    ax.set_ylabel(ylab)
                if row_i == 0:
                    ax.set_title(f"h{m}: {len(x['groups'])} groups, {sum('split_at' in v for v in x['groups'].values())} splits",
                                 fontsize=8)
                else:
                    ax.set_xlabel("event")
        fig.suptitle(f"{lab}: {g} {run} (green: entry in the client's true group, red: wrong; dotted: split)", fontsize=9)
        fig.tight_layout()
        f = out_dir / f"step4-traj{n}.png"
        fig.savefig(f, dpi=105)
        plt.close(fig)
        print(f)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("run", "run-f", "sum", "plots"))
    ap.add_argument("paths", nargs="+", type=Path)
    a = ap.parse_args(argv)
    {"run": lambda: cmd_run(*a.paths[:2]), "run-f": lambda: cmd_run_f(*a.paths[:2]),
     "sum": lambda: cmd_sum(a.paths[0], a.paths[1] if len(a.paths) > 1 else None),
     "plots": lambda: cmd_plots(*a.paths[:3])}[a.cmd]()


if __name__ == "__main__":
    main(sys.argv[1:])
