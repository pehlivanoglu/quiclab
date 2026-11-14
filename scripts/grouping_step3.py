#!/usr/bin/env python3
"""Step 2 procedure fix (Part 1) and Step 3: carrying groups across events (Part 2)
of the 2026-11-12 brief. Read-only, development set (K*, C1, M*, J1; G0 negatives),
single-queue AQMs (pfifo, pie, red, codel), N1-N5 never opened. No ECG engine change.

    python3 scripts/grouping_step3.py part1      CAMPAIGN OUT/part1-rows.jsonl
    python3 scripts/grouping_step3.py part1-sum  OUT/part1-rows.jsonl.gz [OUT/step2-rows.jsonl.gz]
    python3 scripts/grouping_step3.py step3      CAMPAIGN OUT/step3-rows.jsonl
    python3 scripts/grouping_step3.py step3-sum  OUT/step3-rows.jsonl.gz
    python3 scripts/grouping_step3.py plots      CAMPAIGN OUT/step3-rows.jsonl.gz OUT/

Part 1: every event starts with class 0 only; each data template comes from the split
step (seed = participant fitting its current class worst, plus the participant closest
to the seed); data class >= 2 members; split while the gain is positive (no acceptance
rule; = grouping_step2 split_attempt with penalty 0 and no initial median).

Part 2 state: groups; E[i, k] in nats per client and group (stored only while > 0).
Per event (start-time order): participants and f(i, s) as step 1c / step 2; congested =
not class 0 after the Part 1 procedure; group k active when >= 2 congested clients have
E[i, k] > 0, template = their median (leave-one-out when testing one of them);
dE[i, k] = n_eff * ln(alt / f(i, s_k)), alt = min f over class 0 and the other active
groups' templates; clipped to [-b/m, b/m] when alt is class 0; congested clients with no
positive dE form one new group (>= 2) at E = b/m; member E >= b, candidate 0 < E < b,
dropped E <= 0; group removed below 2 clients with E > 0.

Constants (origin tag):
  ALPHA 0.01 (T, brief); b = ln(1/ALPHA) + ln(N), N = clients in the run (P);
  M_VALUES 1, 2, 3 (T, brief); no decay (limitation, brief);
  event intervals as step 2: windows.json for positives, ECG event intervals for G0 (FLAG);
  INTERCHANGE 1.2 (FLAG, brief: side measurement a); SPLIT_MIN 4 (T, brief: side b);
  2-split of side b = seeded two-template reassignment, at most step 2's MAX_ITER (FLAG);
  majority leaf of a group, ties counted wrong (FLAG: false-membership scoring);
  step 2 constants (BIN, MARGIN, N_MIN, CONC_S, MAX_ITER, MAX_TEMPLATES, OBS_SHARE,
  NEG_SPAN) unchanged, see grouping_step2.py; n_eff, f, dE (M).
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
import grouping_step2 as s2  # noqa: E402

ts, ga, d, gt1 = s2.ts, s2.ga, s2.d, s2.gt1
ALPHA = 0.01
M_VALUES = (1, 2, 3)
INTERCHANGE = 1.2
SPLIT_MIN = 4
ECG_DIR = "grouping-d150-v2-owd"
q3 = s2.q3


# ═══ Part 1: fixed procedure ═══════════════════════════════════════════

def partition_fixed(qs: dict[str, np.ndarray]) -> dict:
    P = s2.Partition(qs)
    parts = sorted(s for s in qs if P.f0[s] is not None)
    classes, attempts, iters = [], [], []
    while len(classes) < s2.MAX_TEMPLATES:
        sp = s2.split_attempt(P, qs, parts, classes)
        if sp is None:
            break
        trial, G, it = sp
        acc = G > 0 and len(trial) > len(classes)
        attempts.append({"G": G, "accepted": acc, "n_classes_before": len(classes)})
        if not acc:
            break
        classes = trial
        iters.append(it)
    zero = sorted(set(parts) - {m for c in classes for m in c})
    return {"classes": classes, "zero": zero, "participants": parts, "attempts": attempts,
            "iterations": iters, "comparisons": P.comparisons, "P": P}


def part1_run(rd: Path) -> list[dict]:
    out = []
    for row, qs, tp in s2.events_of(rd):
        res = partition_fixed(qs)
        row["fix"] = {**{k: res[k] for k in ("classes", "zero", "attempts", "iterations", "comparisons")},
                      **s2.score_partition(res, tp)}
        out.append(row)
    return out


def cmd_part1(campaign: Path, out: Path) -> None:
    with Pool(10) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(part1_run, s2.runs_of(campaign, s2.CAMPAIGN_DIRS)):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def table(rows, key, title, cols):
    """cols: [(label, result key)] side by side on the same events."""
    by = defaultdict(list)
    for r in rows:
        k = key(r)
        if k is not None:
            by[k].append(r)
    print(f"### {title}\n")
    head = "| group | events | " + " | ".join(f"{lab} exact | {lab} pair P | {lab} pair R | {lab} over | {lab} under | "
                                            f"{lab} quiet in 0 | {lab} congested in 0" for lab, _ in cols) + " |"
    print(head)
    print("|" + "---|" * (2 + 7 * len(cols)))
    for k in sorted(by, key=str):
        cells = []
        for _, sc in cols:
            rs = [r[sc] for r in by[k]]
            tp, fp, fn = (sum(x[c] for x in rs) for c in ("tp", "fp", "fn"))
            q, qz = sum(x["quiet"] for x in rs), sum(x["quiet_in_0"] for x in rs)
            c, cz = sum(x["cong"] for x in rs), sum(x["cong_in_0"] for x in rs)
            cells += [f"{np.mean([x['exact'] for x in rs]):.2f}", f"{tp / (tp + fp) if tp + fp else float('nan'):.2f}",
                      f"{tp / (tp + fn) if tp + fn else float('nan'):.2f}", str(sum(x["over"] for x in rs)),
                      str(sum(x["under"] for x in rs)), f"{qz / q if q else float('nan'):.2f}",
                      f"{cz / c if c else float('nan'):.2f}"]
        print(f"| {k} | {len(by[k])} | " + " | ".join(cells) + " |")
    print()


def cmd_part1_sum(path: Path, step2_path: Path | None) -> None:
    R = s2.read_jsonl(path)
    cols = [("fixed", "fix")]
    if step2_path:
        old = {(r["run"], r["event"]): r for r in s2.read_jsonl(step2_path)}
        for r in R:
            o = old.get((r["run"], r["event"]))
            if o:
                r["x0"], r["x1"] = o["x0"], o["x1"]
        R = [r for r in R if "x0" in r] if all("x0" in r for r in R[:1]) else R
        cols += [("step2 x0", "x0"), ("step2 x1", "x1")]
    pos = [r for r in R if r["class"] != "negative"]
    neg = [r for r in R if r["class"] == "negative"]
    print("# Part 1: fixed step 2 procedure (class 0 start, split while gain > 0)\n")
    print(f"{len({r['run'] for r in R})} runs, {len(pos)} events with windows, {len(neg)} negative events. "
          "Reference only for Part 2. Columns 'step2 x0' / 'step2 x1' = the old procedure (initial median of all "
          "participants) with penalty 0 / 1 on the same events.\n")

    def size(r):
        gs = r["fix"]["group_sizes"]
        return None if not gs else ("2" if min(gs) == 2 else "3+")
    table(pos, lambda r: "all", "All events", cols)
    table(pos, lambda r: r["class"], "By event class", cols)
    table(pos, lambda r: f"{r['class']} / smallest true group {size(r)}" if size(r) else None,
          "By event class and group size (smallest true group in the event: 2 vs 3 and more)", cols)
    table(pos, lambda r: r["aqm"], "By AQM", cols)
    print("### Negatives (G0)\n")
    print(f"{len(neg)} events; with a data template: fixed {sum(bool(r['fix']['classes']) for r in neg)}"
          + (f", step2 x0 {sum(bool(r['x0']['classes']) for r in neg)}" if neg and "x0" in neg[0] else "")
          + f"; client placements outside class 0: fixed {sum(sum(len(c) for c in r['fix']['classes']) for r in neg)}.\n")
    it = [i for r in R for i in r["fix"]["iterations"]]
    print(f"Cost: iterations per assignment pass {dict(sorted(Counter(it).items()))} (cap {s2.MAX_ITER}); "
          f"template comparisons per event p10 / p50 / p90 {q3([r['fix']['comparisons'] for r in R], '.0f')}; "
          f"data templates per event {dict(sorted(Counter(len(r['fix']['classes']) for r in R).items()))}.")


# ═══ Part 2: Step 3 replay ═════════════════════════════════════════════

def fit_r(q, s):
    r = s2.f_fit(q, s)
    return (r[0], ts.n_eff(r[1]) if len(r[1]) >= 3 else float(len(r[1]))) if r else (None, None)


def leaf_of(truth: dict) -> dict[str, frozenset]:
    return {s: frozenset(v) for s, v in truth["leaf"].items()}


def majority(members, leaf) -> frozenset | None:
    """Majority leaf among members (ties or empty -> None: every membership counted wrong)."""
    c = Counter(leaf.get(m) for m in members if leaf.get(m))
    if not c:
        return None
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return None
    return top[0][0]


def pair_counts(E: dict, b: float, subs: list[str], same: dict) -> dict:
    """ECG-style pair decisions: SAME = both members (E >= b) of a common group;
    DIFFERENT = both members of some group, none in common; else UNCERTAIN."""
    mem = defaultdict(set)
    for k, row in E.items():
        for i, e in row.items():
            if e >= b:
                mem[i].add(k)
    c = Counter()
    for x, f in enumerate(subs):
        for g in subs[x + 1:]:
            t = same[f"{f}|{g}"]
            if not mem[f] or not mem[g]:
                c["unc"] += 1
            elif mem[f] & mem[g]:
                c["tp" if t else "fp"] += 1
            else:
                c["fn" if t else "tn"] += 1
    return dict(c)


def best_two_split(qs, members):
    """Side b: seed = worst fit to the group's leave-one-out template, plus its nearest
    member; reassign members between the two leave-one-out templates (no class 0)."""
    def loo_fit(i, mem):
        m = [x for x in mem if x != i]
        if not m:
            return None
        s, _ = ts.template(qs, set(m))
        return s2.f_fit(qs[i], s)[0] if s is not None and s2.f_fit(qs[i], s) else None
    fits = {i: loo_fit(i, members) for i in members}
    fits = {i: v for i, v in fits.items() if v is not None}
    if len(fits) < SPLIT_MIN:
        return None
    seed = max(fits, key=lambda i: (fits[i], i))
    near = [(s2.f_fit(qs[j], qs[seed]), j) for j in members if j != seed]
    near = [(r[0], j) for r, j in near if r]
    if not near:
        return None
    a = {seed, min(near)[1]}
    bset = set(members) - a
    for _ in range(s2.MAX_ITER):
        if len(a) < 2 or len(bset) < 2:
            return None
        na, nb = set(), set()
        for i in members:
            fa, fb = loo_fit(i, a), loo_fit(i, bset)
            if fa is None and fb is None:
                continue
            (na if fb is None or (fa is not None and fa <= fb) else nb).add(i)
        if (na, nb) == (a, bset):
            break
        a, bset = na, nb
    if len(a) < 2 or len(bset) < 2:
        return None
    side = min((sorted(a), sorted(bset)), key=lambda x: (len(x), x))
    return side


def replay(events, subs, same, leaf, m, run_hops, covered=False):
    """One run, one m. events: list of (row, qs, tp_all, part1 result)."""
    N = len(subs)
    b = math.log(1 / ALPHA) + math.log(N)
    clip = b / m
    E: dict[int, dict[str, float]] = {}
    groups: dict[int, dict] = {}
    nxt = 0
    closes, traj, cost = [], [], []
    member_since: dict[tuple[str, int], tuple[int, float, bool]] = {}
    mixed = defaultdict(list)
    memberships = []
    took_part = Counter()
    first_member = {}
    clip_alt_other_active = 0
    interchange, splits = [], defaultdict(list)
    for ev, (row, qs, tp_all, res) in enumerate(events):
        P = res["P"]
        parts = res["participants"]
        cong = set(parts) - set(res["zero"])
        for s, v in tp_all.items():
            if v:
                took_part[s] += 1
        active = {k: sorted(i for i in cong if E[k].get(i, 0) > 0) for k in E}
        active = {k: v for k, v in active.items() if len(v) >= 2}
        tmpl_cache = {}

        def tmpl(k, excl):
            key = (k, excl if excl in active[k] else None)
            if key not in tmpl_cache:
                mem = [x for x in active[k] if x != excl]
                tmpl_cache[key] = ts.template(qs, set(mem))[0] if mem else None
            return tmpl_cache[key]
        comps = 0
        fk = {}
        for i in parts:
            for k in active:
                s = tmpl(k, i)
                fk[(i, k)] = fit_r(qs[i], s) if s is not None else (None, None)
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
                    if len(active) > 1:
                        clip_alt_other_active += 1
                    x = max(-clip, min(clip, x))
                dE[(i, k)] = x
        # side a: interchangeable active templates
        ks = sorted(active)
        for x, k in enumerate(ks):
            for l in ks[x + 1:]:
                ok = True
                for i in active[k]:
                    fo, fx = fk[(i, k)][0], fk[(i, l)][0]
                    ok &= fo is not None and fx is not None and fx <= INTERCHANGE * fo
                for i in active[l]:
                    fo, fx = fk[(i, l)][0], fk[(i, k)][0]
                    ok &= fo is not None and fx is not None and fx <= INTERCHANGE * fo
                if ok:
                    mem = set(active[k]) | set(active[l])
                    common = set.intersection(*[run_hops[s] for s in mem]) if mem else set()
                    interchange.append({"event": ev, "groups": [k, l],
                                        "leaves": [sorted(map(sorted, {leaf.get(i) for i in active[k] if leaf.get(i)})),
                                                   sorted(map(sorted, {leaf.get(i) for i in active[l] if leaf.get(i)}))],
                                        "common_recorded_hops": sorted(common), "class": row["class"]})
        # side b: split consistency
        for k, mem in active.items():
            if len(mem) >= SPLIT_MIN:
                sp = best_two_split(qs, mem)
                splits[k].append({"event": ev, "members": mem, "split": sp})
        # apply
        for (i, k), x in dE.items():
            E[k][i] = E[k].get(i, 0.0) + x
        gained = {i for (i, k), x in dE.items() if (x >= 0 if covered else x > 0)}   # variant c: a tie counts as gained
        new = sorted(i for i in cong if i not in gained)
        if len(new) >= 2:
            E[nxt] = {i: clip for i in new}
            groups[nxt] = {"born": ev, "t": row["lo"], "members": new, "class": row["class"],
                           "leaves": sorted({",".join(sorted(leaf.get(i) or [])) for i in new})}
            nxt += 1
        for k in list(E):
            E[k] = {i: e for i, e in E[k].items() if e > 0}
            if len(E[k]) < 2:
                del E[k]
                groups[k]["removed"] = ev
        # memberships (enter / leave), membership events
        now = {(i, k) for k, row_ in E.items() for i, e in row_.items() if e >= b}
        for key in now - set(member_since):
            i, k = key
            lab = majority([j for j, e in E[k].items() if e >= b], leaf)
            member_since[key] = (ev, row["lo"], bool(leaf.get(i)) and leaf.get(i) == lab)
            if i not in first_member:
                first_member[i] = (took_part[i], member_since[key][2], ev)
        for key in set(member_since) - now:
            e0, t0, ok = member_since.pop(key)
            w = mixed.pop(key, [])
            memberships.append({"client": key[0], "group": key[1], "from": e0, "to": ev, "dur_events": ev - e0,
                                "dur_s": row["lo"] - t0, "right": ok, "mixed_closes": len(w),
                                "mixed_s": (w[-1] - w[0]) if w else 0.0})
        # per-close check: member shares the group with a member of another leaf, or has no leaf
        for (i, k) in now:
            mem = [j for j, e in E[k].items() if e >= b]
            if not leaf.get(i) or any(leaf.get(j) != leaf.get(i) for j in mem):
                mixed[(i, k)].append(row["lo"])
        cost.append({"part1": res["comparisons"], "update": comps, "active": len(active),
                     "state": sum(len(v) for v in E.values()), "groups": len(E)})
        closes.append(pair_counts(E, b, subs, same))
        traj.append({str(k): {i: round(e, 2) for i, e in row_.items()} for k, row_ in E.items()})
    last_t = events[-1][0]["hi"] if events else 0
    for (i, k), (e0, t0, ok) in member_since.items():
        w = mixed.get((i, k), [])
        memberships.append({"client": i, "group": k, "from": e0, "to": None, "dur_events": len(events) - e0,
                            "dur_s": last_t - t0, "right": ok, "mixed_closes": len(w), "mixed_s": (w[-1] - w[0]) if w else 0.0})
    # merged groups: born with >= 2 leaves (or a client without a leaf); separation = first close whose entries are one leaf
    for k, g in groups.items():
        lv = [leaf.get(i) for i in g["members"]]
        g["merged"] = len(set(lv)) > 1 or any(not x for x in lv)
        if g["merged"]:
            g["separated_after"] = None
            for ev in range(g["born"] + 1, len(traj)):
                row_ = traj[ev].get(str(k))
                if row_ is None:
                    break
                ls = {leaf.get(i) for i in row_}
                if len(ls) == 1 and all(ls):
                    g["separated_after"] = ev - g["born"]
                    break
            g["active_after_birth"] = sum(1 for ev in range(g["born"] + 1, len(traj)) if str(k) in traj[ev])
    # side b per group
    split_out = []
    for k, sl in splits.items():
        got = [tuple(x["split"]) for x in sl if x["split"]]
        lv = {leaf.get(i) for x in sl for i in x["members"] if leaf.get(i)}
        top = Counter(got).most_common(1)
        split_out.append({"group": k, "events": len(sl), "with_split": len(got), "mixed": len(lv) > 1,
                          "top_share": top[0][1] / len(got) if got else None, "top": list(top[0][0]) if top else None,
                          "top_is_leaf": bool(top) and any(set(top[0][0]) == set(x for y in sl for x in y["members"]) & set(l)
                                                           for l in lv)})
    ctrl = any("sub-ctrl" in row_ for t in traj for row_ in t.values())
    return {"b": b, "closes": closes, "traj": traj, "groups": {str(k): v for k, v in groups.items()},
            "memberships": memberships, "first_member": first_member, "took_part_total": dict(took_part),
            "ctrl_ever": ctrl, "clip_alt_zero_with_other_active": clip_alt_other_active,
            "interchange": interchange, "splits": split_out, "cost": cost}


def ecg_view(rd: Path, subs, same, events_start):
    """ECG v1.2 (delta 0.15, v2-owd) on the same run: pair counts per close, final, and
    events to membership counted on the step 3 events (true group took part, start <= t_member)."""
    m = json.loads((rd / ECG_DIR / "metrics.json").read_text())
    pt = json.loads((rd / ECG_DIR / "pairs_t.json").read_text())
    from grouping import Config
    A = Config.from_dict(m["config"]).A
    closes = []
    for snap in pt:
        c = Counter()
        for p, dec in snap["pairs"].items():
            t = same.get(p, False)
            c["unc" if dec == "UNCERTAIN" else ("tp" if t else "fp") if dec == "SAME" else ("fn" if t else "tn")] += 1
        closes.append(dict(c))
    t_mem = {}
    for f, ser in m["series"].items():
        for t, node, L in ser:
            if node is not None and L >= A:
                t_mem[f] = t
                break
    ev_to = {f: sum(1 for t0, took in events_start if t0 <= t and f in took) for f, t in t_mem.items()}
    return {"closes": closes, "membership_events_own": m.get("membership_events"), "events_to_member": ev_to,
            "pairs_final": m["pairwise"]["pairs"]}


def step3_run(rd: Path) -> dict:
    run = ga.load_run(rd)
    group = rd.parent.name
    truth = json.loads((rd / ECG_DIR / "truth.json").read_text())
    subs = sorted(run.subs)
    same = truth["pairs_leaf"]
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    windows = [] if group == "G0" else json.loads((rd / "grouping" / "windows.json").read_text())
    recorded = {f"{a}->{b}" for (a, b), _ in gt1.router_egresses(run)}
    run_hops = {s: {f"{a}->{b}" for a, b in d.path_hops(run, run.pub, s)} & recorded for s in subs}
    events = []
    for row, qs, tp in s2.events_of(rd):
        res = partition_fixed(qs)
        tp_all = s2.truth_partition(windows, row["lo"] + s2.MARGIN, row["hi"] - s2.MARGIN, subs)
        events.append((row, qs, tp_all, res))
    events.sort(key=lambda e: e[0]["lo"])
    out = {"campaign": group, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "n_clients": len(subs), "n_events": len(events),
           "events": [{"lo": e[0]["lo"], "hi": e[0]["hi"], "class": e[0]["class"], "participants": len(e[3]["participants"]),
                       "congested": sorted(set(e[3]["participants"]) - set(e[3]["zero"])),
                       "truth_congested": sorted(s for s, v in e[2].items() if v)} for e in events],
           "leaf": {s: sorted(v) for s, v in leaf.items()}, "run_hops": {s: sorted(v) for s, v in run_hops.items()}}
    for m in M_VALUES:
        out[f"m{m}"] = replay(events, subs, same, leaf, m, run_hops)
        out[f"c{m}"] = replay(events, subs, same, leaf, m, run_hops, covered=True)
    try:
        out["ecg"] = ecg_view(rd, subs, same, [(e[0]["lo"] + s2.MARGIN, {s for s, v in e[2].items() if v}) for e in events])
    except FileNotFoundError:
        out["ecg"] = None
    if group == "G0":
        hop_eps = ga.gt1_hop_episodes(run)
        out["gt1_hops"] = sorted(h for h, v in hop_eps.items() if v)
    return out


def cmd_step3(campaign: Path, out: Path) -> None:
    runs = s2.runs_of(campaign, s2.CAMPAIGN_DIRS)
    with Pool(10) as pool, out.open("w") as fh:
        for r in pool.imap_unordered(step3_run, runs):
            fh.write(json.dumps(r) + "\n")
            print(r["run"], r["n_events"], flush=True)


# ═══ Step 3 summary ═════════════════════════════════════════════════════

def family(r) -> str:
    if r["campaign"] == "J1":
        return f"J1 {r['type']}"
    if r["campaign"] == "M6" and r["type"].startswith("indep"):
        return f"M6 {r['type']} (independent timing)"
    return r["campaign"]


def prf(c: Counter):
    tp, fp, fn, tn, unc = (c.get(k, 0) for k in ("tp", "fp", "fn", "tn", "unc"))
    n = tp + fp + fn + tn + unc
    return (tp / (tp + fp) if tp + fp else float("nan"), tp / (tp + fn) if tp + fn else float("nan"),
            (n - unc) / n if n else float("nan"))


def pooled(closes) -> Counter:
    c = Counter()
    for x in closes:
        c.update(x)
    return c


def f2(x):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.2f}"


def pq(v, f=".0f"):
    return "-" if not v else f"{np.percentile(v, 50):{f}} / {np.percentile(v, 90):{f}}"


def cmd_step3_sum(path: Path, V: str = "m") -> None:
    R = s2.read_jsonl(path)
    pos = [r for r in R if r["campaign"] != "G0"]
    neg = [r for r in R if r["campaign"] == "G0"]
    print(f"# Step 3: carrying groups across events (measurement), variant {V}\n")
    print("Variant m = the brief as written; variant c = step 5 counts dE = 0 as gained (a tie: two active groups with "
          "identical contributors have identical templates; variant m then creates a duplicate group every event, see README).\n")
    print(f"{len(R)} runs ({len(pos)} with windows, {len(neg)} G0), {sum(r['n_events'] for r in R)} events. "
          f"b = ln(1/{ALPHA:g}) + ln(N): N = 7 -> {math.log(100) + math.log(7):.2f}, N = 9 -> {math.log(100) + math.log(9):.2f} nats. "
          "Pair decisions as ECG: SAME = both members (E >= b) of a common group, DIFFERENT = both members of some "
          "group but none in common, UNCERTAIN otherwise; truth = same leaf (ECG's truth.json pairs_leaf). "
          "'every close' = pairs pooled over all event closes of the run; 'last' = after the last event. ECG = v1.2, "
          "delta 0.15 s, v2-owd onsets, its own event closes.\n")
    print("## Pair precision / recall / coverage\n")
    print("| family | AQM | runs | " + " | ".join(f"m{m} every close P / R / cov | m{m} last P / R / cov" for m in M_VALUES)
          + " | ECG every close P / R / cov | ECG last P / R / cov |")
    print("|---|---|---|" + "---|" * (2 * len(M_VALUES) + 2))
    by = defaultdict(list)
    for r in pos:
        by[(family(r), r["aqm"])].append(r)
    for k in sorted(by):
        rs = by[k]
        cells = []
        for m in M_VALUES:
            a = pooled(c for r in rs for c in r[f"{V}{m}"]["closes"])
            z = pooled(r[f"{V}{m}"]["closes"][-1] for r in rs if r[f"{V}{m}"]["closes"])
            cells += [" / ".join(map(f2, prf(a))), " / ".join(map(f2, prf(z)))]
        ec = [r["ecg"] for r in rs if r["ecg"]]
        a = pooled(c for e in ec for c in e["closes"])
        z = pooled(e["closes"][-1] for e in ec if e["closes"])
        cells += [" / ".join(map(f2, prf(a))), " / ".join(map(f2, prf(z)))]
        print(f"| {k[0]} | {k[1]} | {len(rs)} | " + " | ".join(cells) + " |")
    print("\n## Events to membership per client\n")
    print("Counted on the step 3 event list: events in which the client's true group took part (client expected in a "
          "window of the event), up to and including the event after which the client is first a member (any group). "
          "ECG: the same events, counted up to its first close with the client a member (node set, L >= A). "
          "'right' = the first group's majority leaf is the client's leaf. Clients that never become members are not in "
          "p50 / p90; 'never' counts clients with >= 1 such event.\n")
    print("| family | " + " | ".join(f"m{m} p50 / p90 | m{m} right | m{m} never" for m in M_VALUES)
          + " | ECG p50 / p90 | ECG never |")
    print("|---|" + "---|" * (3 * len(M_VALUES) + 2))
    byf = defaultdict(list)
    for r in pos:
        byf[family(r)].append(r)
    for k in sorted(byf):
        rs = byf[k]
        cells = []
        for m in M_VALUES:
            fm = [(r, s, v) for r in rs for s, v in r[f"{V}{m}"]["first_member"].items() if r["leaf"].get(s)]
            never = sum(1 for r in rs for s, n in r[f"{V}{m}"]["took_part_total"].items()
                        if n and r["leaf"].get(s) and s not in r[f"{V}{m}"]["first_member"])
            cells += [pq([v[0] for _, _, v in fm]), f2(np.mean([v[1] for _, _, v in fm]) if fm else None), str(never)]
        ev = [n for r in rs if r["ecg"] for s, n in r["ecg"]["events_to_member"].items() if r["leaf"].get(s)]
        never = sum(1 for r in rs if r["ecg"] for s, n in r[f"m1"]["took_part_total"].items()
                    if n and r["leaf"].get(s) and s not in r["ecg"]["events_to_member"])
        cells += [pq(ev), str(never)]
        print(f"| {k} | " + " | ".join(cells) + " |")
    print(f"\n## Realised false-membership rate (target alpha = {ALPHA:g})\n")
    print("Membership = (client, group) with E >= b, from the close it is declared until E < b. Wrong = the client's "
          "same-leaf truth differs from the group's majority leaf at declaration (ties and clients without a leaf "
          "count wrong). Duration in events (closes) and seconds of run time.\n")
    print("| family | " + " | ".join(f"m{m} memberships | m{m} wrong | m{m} rate | m{m} wrong lasted events p50 / p90 | "
                                     f"m{m} wrong lasted s p50 / p90" for m in M_VALUES) + " |")
    print("|---|" + "---|" * (5 * len(M_VALUES)))
    for k in sorted(byf):
        rs = byf[k]
        cells = []
        for m in M_VALUES:
            ms = [x for r in rs for x in r[f"{V}{m}"]["memberships"]]
            w = [x for x in ms if not x["right"]]
            cells += [str(len(ms)), str(len(w)), f2(len(w) / len(ms) if ms else None),
                      pq([x["dur_events"] for x in w]), pq([x["dur_s"] for x in w], ".1f")]
        print(f"| {k} | " + " | ".join(cells) + " |")
    print("\nPer-close version (no majority rule): a membership is wrong at a close when the group holds a member "
          "(E >= b) of another leaf, or the client has no leaf. 'ever wrong' = >= 1 such close; lasted = such closes.\n")
    print("| family | " + " | ".join(f"m{m} ever wrong | m{m} rate | m{m} wrong closes p50 / p90 | m{m} span s p50 / p90"
                                     for m in M_VALUES) + " |")
    print("|---|" + "---|" * (4 * len(M_VALUES)))
    for k in sorted(byf):
        cells = []
        for m in M_VALUES:
            ms = [x for r in byf[k] for x in r[f"{V}{m}"]["memberships"]]
            w = [x for x in ms if x["mixed_closes"]]
            cells += [str(len(w)), f2(len(w) / len(ms) if ms else None), pq([x["mixed_closes"] for x in w]),
                      pq([x["mixed_s"] for x in w], ".1f")]
        print(f"| {k} | " + " | ".join(cells) + " |")
    tot = {m: [x for r in pos for x in r[f"{V}{m}"]["memberships"]] for m in M_VALUES}
    print("\nAll positives, per-close version: " + "; ".join(f"m{m} {sum(bool(x['mixed_closes']) for x in v)} / {len(v)} = "
          f"{f2(sum(bool(x['mixed_closes']) for x in v) / len(v) if v else None)}" for m, v in tot.items()))
    print("\nAll positives: " + "; ".join(f"m{m} {sum(not x['right'] for x in v)} / {len(v)} = "
                                          f"{f2(sum(not x['right'] for x in v) / len(v) if v else None)}" for m, v in tot.items()) + "\n")
    print("## Groups that start merged\n")
    print("Merged = the group's first members span two or more leaves, or include a client without a leaf. "
          "Separated = a later close where every client with E > 0 in the group has one and the same leaf.\n")
    print("| family | " + " | ".join(f"m{m} groups | m{m} merged | m{m} separated | m{m} events to separate p50 / p90 | "
                                     f"m{m} never (removed / still merged)" for m in M_VALUES) + " |")
    print("|---|" + "---|" * (5 * len(M_VALUES)))
    for k in sorted(byf):
        rs = byf[k]
        cells = []
        for m in M_VALUES:
            gs = [g for r in rs for g in r[f"{V}{m}"]["groups"].values()]
            mg = [g for g in gs if g["merged"]]
            sp = [g["separated_after"] for g in mg if g["separated_after"] is not None]
            nev = [g for g in mg if g["separated_after"] is None]
            cells += [str(len(gs)), str(len(mg)), str(len(sp)), pq(sp),
                      f"{sum('removed' in g for g in nev)} / {sum('removed' not in g for g in nev)}"]
        print(f"| {k} | " + " | ".join(cells) + " |")
    print("\nMerged groups by the class of their first event (m2):\n")
    print("| first-event class | merged | separated | never: removed | never: still merged (later active events p50) |\n|---|---|---|---|---|")
    mc = defaultdict(list)
    for r in pos:
        for g in r[f"{V}2"]["groups"].values():
            if g["merged"]:
                mc[g["class"]].append(g)
    for k in sorted(mc):
        gs = mc[k]
        still = [g for g in gs if g["separated_after"] is None and "removed" not in g]
        print(f"| {k} | {len(gs)} | {sum(g['separated_after'] is not None for g in gs)} | "
              f"{sum(g['separated_after'] is None and 'removed' in g for g in gs)} | {len(still)} "
              f"({statistics.median([g['active_after_birth'] for g in still]) if still else '-'}) |")
    print("\n## sub-ctrl\n")
    for m in M_VALUES:
        ctrl = [r["run"] for r in R if r[f"{V}{m}"]["ctrl_ever"]]
        mem = [r["run"] for r in R for x in r[f"{V}{m}"]["memberships"] if x["client"] == "sub-ctrl"]
        print(f"- m{m}: sub-ctrl with E > 0 in some group in {len(ctrl)} runs; a member (E >= b) in {len(set(mem))} runs"
              + (f" ({', '.join(sorted(set(mem))[:8])})" if mem else ""))
    print("\n## Negatives (G0), topology truth of step 2b\n")
    print("A pair of members of one group is right when the two clients share a recorded router egress with at least "
          "one GT1 episode in the run (same check as step 2b for ECG's SAME pairs). SAME pairs after the last event.\n")
    print("| type | AQM | " + " | ".join(f"m{m} groups formed | m{m} SAME pairs right / wrong" for m in M_VALUES)
          + " | ECG SAME pairs right / wrong |")
    print("|---|---|" + "---|" * (2 * len(M_VALUES) + 1))
    totn = Counter()
    for r in sorted(neg, key=lambda x: (x["type"], x["aqm"])):
        hops = set(r["gt1_hops"])
        cells = []
        for m in M_VALUES:
            x = r[f"{V}{m}"]
            b = x["b"]
            last = x["traj"][-1] if x["traj"] else {}
            ok = bad = 0
            for row_ in last.values():
                mem = sorted(i for i, e in row_.items() if e >= b)
                for a_ in range(len(mem)):
                    for c_ in mem[a_ + 1:]:
                        good = bool(set(r["run_hops"].get(mem[a_], [])) & set(r["run_hops"].get(c_, [])) & hops)
                        ok += good
                        bad += not good
            totn[(m, "ok")] += ok
            totn[(m, "bad")] += bad
            cells += [str(len(x["groups"])), f"{ok} / {bad}"]
        eo = eb = 0
        if r["ecg"]:
            for p, v in r["ecg"]["pairs_final"].items():
                if v["decided"] == "SAME":
                    a_, c_ = p.split("|")
                    good = bool(set(r["run_hops"].get(a_, [])) & set(r["run_hops"].get(c_, [])) & hops)
                    eo += good
                    eb += not good
        totn[("ecg", "ok")] += eo
        totn[("ecg", "bad")] += eb
        print(f"| {r['type']} | {r['aqm']} | " + " | ".join(cells) + f" | {eo} / {eb} |")
    print("\nTotal SAME pairs right / wrong: " + "; ".join(f"m{m} {totn[(m, 'ok')]} / {totn[(m, 'bad')]}" for m in M_VALUES)
          + f"; ECG {totn[('ecg', 'ok')]} / {totn[('ecg', 'bad')]}.\n")
    print("## Side measurement (a): interchangeable active templates\n")
    print(f"Two active groups in one event whose members all fit the other group's template within x{INTERCHANGE:g} of "
          "their own (both directions). Shared upstream = the members of both groups share a recorded router egress.\n")
    print("| family | m | events with >= 2 active groups | interchangeable pairs | with a shared recorded egress | leaves of the two groups (top 3) |\n|---|---|---|---|---|---|")
    for k in sorted(byf):
        for m in M_VALUES:
            rs = byf[k]
            two = sum(1 for r in rs for x in r[f"{V}{m}"]["cost"] if x["active"] >= 2)
            ic = [x for r in rs for x in r[f"{V}{m}"]["interchange"]]
            if not ic and m != 2:
                continue
            lv = Counter(" vs ".join("+".join("{" + ",".join(l) + "}" for l in side) for side in x["leaves"]) for x in ic)
            print(f"| {k} | {m} | {two} | {len(ic)} | {sum(bool(x['common_recorded_hops']) for x in ic)} | "
                  f"{'; '.join(f'{a} ({n})' for a, n in lv.most_common(3)) or '-'} |")
    print()
    print("## Side measurement (b): split consistency\n")
    print(f"Active groups with >= {SPLIT_MIN} congested members: the event's best 2-split of those members. Per group "
          "with >= 2 such events: share of events whose split equals the group's most common split.\n")
    print("| m | group type | groups | events with a split p50 | top-split share p10 / p50 / p90 | top split = a true leaf |\n|---|---|---|---|---|---|")
    for m in M_VALUES:
        for lab, mixed in (("one true leaf", False), ("mixes two or more leaves", True)):
            sp = [x for r in pos for x in r[f"{V}{m}"]["splits"] if x["mixed"] == mixed and x["with_split"] >= 2]
            print(f"| {m} | {lab} | {len(sp)} | {np.median([x['with_split'] for x in sp]) if sp else '-'} | "
                  f"{q3([x['top_share'] for x in sp])} | {sum(x['top_is_leaf'] for x in sp)} |")
    print("\n## Cost\n")
    for m in M_VALUES:
        c = [x for r in R for x in r[f"{V}{m}"]["cost"]]
        st = [x["state"] for x in c]
        gr = [x["groups"] for x in c]
        print(f"- m{m}: state entries (client, group) after a close p50 / p90 / max {pq(st)} / {max(st) if st else '-'}; "
              f"groups p50 / max {np.median(gr) if gr else '-'} / {max(gr) if gr else '-'}")
    c = [x["part1"] for r in R for x in r[f"{V}1"]["cost"]]
    print(f"- template comparisons per event: Part 1 procedure p10 / p50 / p90 {q3(c, '.0f')}; evidence update "
          + "; ".join(f"m{m} p50 / p90 {pq([x['update'] for r in R for x in r[f'{V}{m}']['cost']])}" for m in M_VALUES)
          + "; active groups per event " + "; ".join(f"m{m} {dict(sorted(Counter(x['active'] for r in R for x in r[f'{V}{m}']['cost']).items()))}" for m in M_VALUES))
    print(f"- clip applied with alt = class 0 while another group was active (reading check): "
          + "; ".join(f"m{m} {sum(r[f'{V}{m}']['clip_alt_zero_with_other_active'] for r in R)}" for m in M_VALUES))


# ═══ plots ═════════════════════════════════════════════════════════════

def cmd_plots(campaign: Path, path: Path, out_dir: Path, V: str = "m") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    R = {r["run"] + "@" + r["campaign"]: r for r in s2.read_jsonl(path)}
    want = [("topology base (one queue)", "M1", "grp-burstcap-pfifo-r1"), ("topology split", "K1", "grp-hier-pfifo-r1"),
            ("topology depth (two levels)", "K6", "grp-depth-pfifo-r1"),
            ("J1 hierjit20 (realised sd 12.6 ms)", "J1", "grp-hierjit20-pfifo-r1"),
            ("independent timing", "M6", "grp-indepfast-pfifo-r1"),
            ("topology uneven (G0 negative, no truth leaf: every entry red)", "G0", "grp-calmuneven-pfifo-r1")]
    picks = [(lab, R[f"{run}@{g}"]) for lab, g, run in want if f"{run}@{g}" in R]
    for n, (lab, r) in enumerate(picks, 1):
        fig, axes = plt.subplots(1, len(M_VALUES), figsize=(13, 3.6), sharey=True)
        for ax, m in zip(axes, M_VALUES):
            x = r[f"{V}{m}"]
            series = defaultdict(lambda: [[], []])
            for ev, st in enumerate(x["traj"]):
                for k, row_ in st.items():
                    for i, e in row_.items():
                        series[(i, k)][0].append(ev)
                        series[(i, k)][1].append(e)
            for (i, k), (xs, ys) in series.items():
                g = x["groups"][k]
                mem = [c for c, e in x["traj"][xs[-1]][k].items()]
                lab_k = majority(mem, {s: frozenset(v) for s, v in r["leaf"].items()})
                right = bool(r["leaf"].get(i)) and frozenset(r["leaf"][i]) == lab_k
                ax.plot(xs, ys, "-", lw=0.8, color="C2" if right else "C3", alpha=0.7)
            ax.axhline(x["b"], color="0.3", ls="--", lw=0.8)
            ax.set_yscale("symlog", linthresh=1)
            ax.set_title(f"m = {m}: {len(x['groups'])} groups", fontsize=8)
            ax.set_xlabel("event")
        axes[0].set_ylabel("E[i, k] nats (green: client's true group, red: wrong group)")
        fig.suptitle(f"{lab}: {r['campaign']} {r['run']}", fontsize=9)
        fig.tight_layout()
        f = out_dir / f"step3-traj{n}-{V}.png"
        fig.savefig(f, dpi=110)
        plt.close(fig)
        print(f)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("part1", "part1-sum", "step3", "step3-sum", "plots"))
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--variant", default="m", choices=("m", "c"))
    a = ap.parse_args(argv)
    {"part1": lambda: cmd_part1(*a.paths[:2]),
     "part1-sum": lambda: cmd_part1_sum(a.paths[0], a.paths[1] if len(a.paths) > 1 else None),
     "step3": lambda: cmd_step3(*a.paths[:2]), "step3-sum": lambda: cmd_step3_sum(a.paths[0], a.variant),
     "plots": lambda: cmd_plots(*a.paths[:3], a.variant)}[a.cmd]()


if __name__ == "__main__":
    main(sys.argv[1:])
