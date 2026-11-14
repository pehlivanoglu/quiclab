#!/usr/bin/env python3
"""Step 5 of the 2026-11-13 brief: measurement only, no new procedure, no state change.
Read-only, development set (K*, C1, M*, J1), single-queue AQMs, N1-N5 never opened.
Event intervals: ECG event intervals for every run (decision of the brief); the Part A
rescoring of the existing Step 4 rows keeps their windows.json timing.

    python3 scripts/grouping_step5.py run  CAMPAIGN STEP4_ROWS.jsonl.gz OUT/step5-rows.jsonl
    python3 scripts/grouping_step5.py sum  OUT/step5-rows.jsonl.gz

Part A: second truth for memberships. A pair (i, j) is "linked" once there was an
  event so far in which both took part and a router egress on both paths had a queue
  >= Q_TARGET_MS (5 ms, step 2b) inside the event interval. A membership (i, k) at a
  close is physically right when i is linked to at least half of k's other members
  (E >= b; ECG: node co-members).
B1: votes between true-leaf groups (no algorithm state): in an event, a leaf group is
  active with >= 2 congested clients (Part 1 procedure); each congested client of an
  active leaf votes "own" when its curve fits its own leaf's leave-one-out median
  better than another active leaf's median. Event type per vote from router queues
  (>= 5 ms in the interval): own leaf egress, the other leaf's egress, a shared
  upstream egress of the two.
B2: votes between the stored halves of h3 groups (h3 replayed on ECG intervals, state
  untouched): own half vs other half, both templates the median of c curves,
  c = min(own congested half - 1, other congested half), members drawn with a fixed
  seed; the event in which the halves were stored gives no votes.
B3: offline SPRT on the B2 votes: own ln(0.5 / (1 - eps)), other ln(0.5 / eps), stop
  at +b (one queue) or -b (two queues), checked after each event.

Constants (origin tag):
  Q_TARGET_MS 5 ms (T, step 2b); ALPHA 0.01, b = ln(1/ALPHA) + ln(N) (T / P);
  "took part" = congested by the Part 1 procedure (c / h) or an ECG event member (FLAG);
  physically right = linked to >= half of the other members (FLAG);
  active leaf group in B1 = >= 2 congested clients of the leaf (FLAG);
  event types (B1): own leaf only / both leaves / shared upstream (no leaf egress) /
    other (any other combination) (FLAG);
  bitrate classes <= 1000 / 2500 / >= 5000 kb/s (P: the scenarios' rates);
  B2 seed = crc32(run, event, group, client) (FLAG); eps from B1 (M) and 0.05 / 0.10 /
    0.20 (FLAG); run-length expectation by exact DP at the pooled eps (M).
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import sys
import zlib
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grouping_step4 as s4  # noqa: E402

s3, s2, ts, ga, d = s4.s3, s4.s2, s4.ts, s4.ga, s4.d
ALPHA = 0.01
Q_TARGET_MS = s2.Q_TARGET_MS
ECG_DIR = s4.ECG_DIR
EPS_FIXED = (0.05, 0.10, 0.20)
STEP4: dict = {}


def rate_class(r) -> str:
    if r is None:
        return "?"
    return "<= 1000" if r <= 1000 else "2500" if r <= 2500 else ">= 5000"


def hot_hops(delay, lo, hi) -> set[str]:
    return {h for h, (t, q) in delay.items() if np.any((t >= lo) & (t <= hi) & (q >= Q_TARGET_MS))}


def make_rules(delay, gt1_eps):
    """Two congestion rules per hop and interval: 'peak5' = any sample >= 5 ms (the brief,
    step 2b); 'gt1' = a GT1 standing-queue episode overlaps the interval (FLAG: added
    because peak5 is true for 91-100 % of ECG events on every egress)."""
    return {"peak5": lambda lo, hi: hot_hops(delay, lo, hi),
            "gt1": lambda lo, hi: {h for h, v in gt1_eps.items() if any(a <= hi and b >= lo for a, b in v)}}


# ═══ Part A: second truth ══════════════════════════════════════════════

def judge(closes, took, hot, hops, leaf):
    """closes[e] = {group: [members]} after event e; took[e] = set of clients that took
    part in event e; hot[e] = congested hops of event e. Returns memberships with the
    two truths at declaration and per close."""
    linked = set()
    since, out = {}, []
    for e, groups in enumerate(closes):
        tk = sorted(took[e])
        for x, i in enumerate(tk):
            for j in tk[x + 1:]:
                if hops.get(i, set()) & hops.get(j, set()) & hot[e]:
                    linked.add((i, j))
        now = {}
        for k, mem in groups.items():
            for i in mem:
                others = [j for j in mem if j != i]
                lf = leaf.get(i)
                same_decl = bool(lf) and lf == s3.majority(mem, leaf)
                same_close = bool(lf) and all(leaf.get(j) == lf for j in mem)
                nl = sum(tuple(sorted((i, j))) in linked for j in others)
                phys = bool(others) and nl >= len(others) / 2
                now[(i, k)] = (same_decl, same_close, phys)
        for key, (sd, sc, ph) in now.items():
            if key not in since:
                since[key] = {"decl_same_wrong": not sd, "decl_phys_wrong": not ph, "close_same_wrong": False,
                              "close_both_wrong": False}
            m = since[key]
            if not sc:
                m["close_same_wrong"] = True
                if not ph:
                    m["close_both_wrong"] = True
        for key in set(since) - set(now):
            out.append(since.pop(key))
    out += list(since.values())
    return out


def closes_from_traj(traj, b):
    """traj stores E rounded to 2 decimals; E reaches exactly b after m clipped steps, so
    compare with b rounded the same way (rounding is monotone)."""
    bb = round(b, 2)
    return [{k: [i for i, e in r_.items() if e >= bb] for k, r_ in t.items()} for t in traj]


def part_a(rd, run, rules, hops, leaf, events_now, h_now, c_now):
    out = defaultdict(dict)
    key = f"{rd.parent.name}/{rd.name}"
    old = STEP4.get(key)
    for rn, rule in rules.items():
        if old:   # existing step 4 rows (windows.json timing)
            hot = [rule(e["lo"], e["hi"]) for e in old["events"]]
            took = [set(e["congested"]) for e in old["events"]]
            for v in ("c3", "h3"):
                out[f"{v} (windows)"][rn] = judge(closes_from_traj(old[v]["traj"], old[v]["b"]), took, hot, hops, leaf)
        hot = [rule(e[0]["lo"], e[0]["hi"]) for e in events_now]
        took = [set(e[3]["participants"]) - set(e[3]["zero"]) for e in events_now]
        for v, x in (("c3 (ECG iv)", c_now), ("h3 (ECG iv)", h_now)):
            out[v][rn] = judge(closes_from_traj(x["traj"], x["b"]), took, hot, hops, leaf)
    # ECG: its own events and closes
    m = json.loads((rd / ECG_DIR / "metrics.json").read_text())
    from grouping import Config
    A = Config.from_dict(m["config"]).A
    evs = m["events"]
    closes, took = [], []
    for x, e in enumerate(evs):
        groups = defaultdict(list)
        for f, ser in m["series"].items():
            if x < len(ser) and abs(ser[x][0] - e["t"]) < 1e-6:
                t, node, L = ser[x]
            else:
                hit = [s_ for s_ in ser if abs(s_[0] - e["t"]) < 1e-6]
                if not hit:
                    continue
                t, node, L = hit[0]
            if node is not None and L >= A:
                groups[node].append(f)
        closes.append(dict(groups))
        took.append(set(e["members"]))
    for rn, rule in rules.items():
        hot = [rule(e["t0"] + s2.NEG_SPAN[0], e["t0"] + s2.NEG_SPAN[1]) for e in evs]
        out["ECG"][rn] = judge(closes, took, hot, hops, leaf)
    return dict(out)


# ═══ B1: votes between true-leaf groups ═══════════════════════════════

def b1_votes(events, leaf, leaf_hop, hops, rules, rates):
    votes = []
    for ev, (row, qs, tp_all, res) in enumerate(events):
        cong = set(res["participants"]) - set(res["zero"])
        by_leaf = defaultdict(list)
        for i in cong:
            if leaf.get(i):
                by_leaf[leaf[i]].append(i)
        act = {l: sorted(v) for l, v in by_leaf.items() if len(v) >= 2}
        if len(act) < 2:
            continue
        hot = {rn: rule(row["lo"], row["hi"]) for rn, rule in rules.items()}
        med = {l: ts.template(qs, set(v))[0] for l, v in act.items()}
        for l, mem in act.items():
            for i in mem:
                own = ts.template(qs, set(mem) - {i})[0]
                fo = s2.f_fit(qs[i], own)
                if not fo:
                    continue
                for l2, mem2 in act.items():
                    if l2 == l:
                        continue
                    fx = s2.f_fit(qs[i], med[l2])
                    if not fx:
                        continue
                    h_own, h_oth = leaf_hop.get(i), leaf_hop.get(mem2[0])
                    up = (set.intersection(*[hops.get(j, set()) for j in mem + mem2]) - {h_own, h_oth})
                    typs = []
                    for rn in ("peak5", "gt1"):
                        o, x_, u = h_own in hot[rn], h_oth in hot[rn], bool(up & hot[rn])
                        typs.append(f"{'O' if o else '-'}{'X' if x_ else '-'}{'U' if u else '-'}")
                    votes.append([ev, i, "+".join(sorted(l2)), int(fo[0] < fx[0]), typs[0], typs[1],
                                  rate_class(rates.get(i))])
    return votes


# ═══ B2: votes between stored halves (h3 on ECG intervals) ══════════════

def run_h3_with_votes(rd, events, subs, same, leaf, rates):
    votes, stored = [], {}

    def hook(ev, row, qs, active, halves):
        for k, hv in halves.items():
            if hv is None:
                continue
            A, B = hv
            stored.setdefault(k, (sorted(A), sorted(B)))
            mem = active[k]
            for i in mem:
                if i not in A and i not in B:
                    continue
                own, oth = (A, B) if i in A else (B, A)
                oc = sorted(x for x in mem if x in own and x != i)
                xc = sorted(x for x in mem if x in oth)
                c = min(len(oc), len(xc))
                if c < 1:
                    continue
                rng = random.Random(zlib.crc32(f"{rd.name}|{ev}|{k}|{i}".encode()))
                so, sx = ts.template(qs, set(rng.sample(oc, c)))[0], ts.template(qs, set(rng.sample(xc, c)))[0]
                fo, fx = s2.f_fit(qs[i], so), s2.f_fit(qs[i], sx)
                if not fo or not fx:
                    continue
                votes.append([ev, int(k), i, int(fo[0] < fx[0]), c, len(A) + len(B), rate_class(rates.get(i))])
    h = s4.replay4(events, subs, same, leaf, 3, True, hook=hook)
    groups = {}
    for k, g in h["groups"].items():
        if int(k) in stored:
            A, B = stored[int(k)]
            la, lb = {leaf.get(i) for i in A}, {leaf.get(i) for i in B}
            groups[k] = {"halves": [A, B], "life_mixed": g["life_mixed"], "born": g["born"],
                         "halves_boundary": len(la) == 1 and len(lb) == 1 and None not in la | lb and la != lb,
                         "split_at": g.get("split_at")}
    return h, votes, groups


def step5_run(rd: Path) -> dict:
    run, truth, subs, windows, events = s4.load_events(rd, ecg_intervals=True)
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    leaf_hop = {s: h for s, h in truth.get("topology_group", {}).items() if h != s}
    delay = s2.egress_delay(run)
    rules = make_rules(delay, ga.gt1_hop_episodes(run))
    hops = {s: s2.path_egresses(run, s, delay) for s in subs}
    rates = {s: run.topology["subscribers"].get(s, {}).get("rate_kbps") for s in subs}
    same = truth["pairs_leaf"]
    h, b2, groups = run_h3_with_votes(rd, events, subs, same, leaf, rates)
    c = s4.replay4(events, subs, same, leaf, 3, False)
    row = {"campaign": rd.parent.name, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "n_clients": len(subs), "n_events": len(events), "leaf": {s: sorted(v) for s, v in leaf.items()},
           "rates": rates, "b": math.log(1 / ALPHA) + math.log(len(subs))}
    row["A"] = part_a(rd, run, rules, hops, leaf, events, h, c)
    row["B1"] = b1_votes(events, leaf, leaf_hop, hops, rules, rates)
    row["B2"] = b2
    row["B2_groups"] = groups
    return row


def _init(path: str) -> None:
    global STEP4
    STEP4 = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["campaign"] != "G0":
                STEP4[f"{r['campaign']}/{r['run']}"] = {"events": r["events"],
                                                        **{v: {"traj": r[v]["traj"], "b": r[v]["b"]} for v in ("c3", "h3")}}


def cmd_run(campaign: Path, step4_rows: Path, out: Path) -> None:
    runs = [rd for rd in s2.runs_of(campaign, s2.CAMPAIGN_DIRS) if rd.parent.name != "G0"]
    with Pool(10, initializer=_init, initargs=(str(step4_rows),)) as pool, out.open("w") as fh:
        for r in pool.imap_unordered(step5_run, runs):
            fh.write(json.dumps(r) + "\n")
            print(r["run"], flush=True)


# ═══ summary ═══════════════════════════════════════════════════════════

METHODS = ("c3 (windows)", "h3 (windows)", "ECG", "c3 (ECG iv)", "h3 (ECG iv)")
TYPE_NAMES = {"O--": "own leaf only", "OX-": "both leaves", "--U": "shared upstream only"}
f2, family = s4.f2, s4.family


def rt(a, n):
    return f2(a / n if n else None)


def sec_a(R):
    print("## Part A: same-leaf errors that are physically right\n")
    print("Per membership (client, group): 'same' = wrong by the same-leaf truth; 'both' = wrong by the same-leaf truth "
          "and by the physical truth (not linked to >= half of the other members through a congested shared egress in "
          "an event both took part in); diff = same - both = same-leaf errors that are physically right. Rates over "
          "memberships. decl = judged when declared; close = at some close (for 'both': at the same close).\n")
    for rn in ("peak5", "gt1"):
        print(f"### Congestion rule {rn}\n")
        print("| family | AQM | " + " | ".join(f"{m}: n / same decl / both decl / same close / both close" for m in METHODS) + " |")
        print("|---|---|" + "---|" * len(METHODS))
        by = defaultdict(list)
        for r in R:
            by[(family(r), r["aqm"])].append(r)
        tot = defaultdict(Counter)
        for k in sorted(by):
            cells = []
            for m in METHODS:
                ms = [x for r in by[k] for x in r["A"].get(m, {}).get(rn, [])]
                c = Counter(n=len(ms), sd=sum(x["decl_same_wrong"] for x in ms),
                            bd=sum(x["decl_same_wrong"] and x["decl_phys_wrong"] for x in ms),
                            sc=sum(x["close_same_wrong"] for x in ms), bc=sum(x["close_both_wrong"] for x in ms))
                tot[m].update(c)
                cells.append(f"{c['n']} / {rt(c['sd'], c['n'])} / {rt(c['bd'], c['n'])} / {rt(c['sc'], c['n'])} / {rt(c['bc'], c['n'])}")
            if any(not c.startswith("0 ") for c in cells):
                print(f"| {k[0]} | {k[1]} | " + " | ".join(cells) + " |")
        print("| **all** | | " + " | ".join(f"{tot[m]['n']} / {rt(tot[m]['sd'], tot[m]['n'])} / {rt(tot[m]['bd'], tot[m]['n'])} / "
                                          f"{rt(tot[m]['sc'], tot[m]['n'])} / {rt(tot[m]['bc'], tot[m]['n'])}" for m in METHODS) + " |\n")
        print("Share of same-leaf errors that are physically right (diff / same): " + "; ".join(
            f"{m} decl {rt(tot[m]['sd'] - tot[m]['bd'], tot[m]['sd'])}, close {rt(tot[m]['sc'] - tot[m]['bc'], tot[m]['sc'])}"
            for m in METHODS) + ".\n")


def lag1(seqs):
    """(raw pooled lag-1 correlation, within-sequence centred pooled correlation, pairs)."""
    a, b, ac, bc = [], [], [], []
    for s in seqs:
        if len(s) < 2:
            continue
        mu = float(np.mean(s))
        for x, y in zip(s, s[1:]):
            a.append(x)
            b.append(y)
            ac.append(x - mu)
            bc.append(y - mu)
    if len(a) < 3:
        return None, None, len(a)
    raw = float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else None
    den = math.sqrt(sum(x * x for x in ac) * sum(y * y for y in bc))
    cen = sum(x * y for x, y in zip(ac, bc)) / den if den > 0 else None
    return raw, cen, len(a)


def p_run2(n, eps):
    """P(at least one run of >= 2 wrong votes in n Bernoulli(eps) votes)."""
    no_last, last = 1.0, 0.0   # P(no run so far, last vote right / wrong)
    for _ in range(n):
        no_last, last = (no_last + last) * (1 - eps), no_last * eps
    return 1 - (no_last + last)


def has_run2(s):
    return any(x == 0 and y == 0 for x, y in zip(s, s[1:]))


def sec_b1(R):
    print("## B1: votes between true-leaf groups\n")
    print("Type code per vote: O = the voter's leaf egress congested, X = the other leaf's egress congested, U = a "
          "shared upstream egress of the two leaves congested ('-' = not), under each congestion rule. Expected own-vote "
          "rate: near 1 for O-- (own leaf only) and OX- (both leaves), near 0.5 for --U (shared upstream only).\n")
    V = [(r, v) for r in R for v in r["B1"]]
    for rn, col in (("peak5", 4), ("gt1", 5)):
        c = defaultdict(lambda: [0, 0])
        for r, v in V:
            c[v[col]][0] += 1
            c[v[col]][1] += v[3]
        print(f"### By type, rule {rn}\n")
        print("| type | votes | own-vote rate |\n|---|---|---|")
        for k in sorted(c, key=lambda x: -c[x][0]):
            print(f"| {k} {('(' + TYPE_NAMES[k] + ')') if k in TYPE_NAMES else ''} | {c[k][0]} | {rt(c[k][1], c[k][0])} |")
        print()
    exp1 = [(r, v) for r, v in V if v[5] in ("O--", "OX-")]
    up = [(r, v) for r, v in V if v[5] == "--U"]
    eps = 1 - sum(v[3] for _, v in exp1) / len(exp1) if exp1 else None
    print(f"**eps (M)** = wrong-vote rate on O-- and OX- under gt1 = {f2(eps)} ({len(exp1)} votes; peak5 has too few "
          f"such votes to estimate it).\n")
    for lab, key in (("family", lambda r, v: family(r)), ("AQM", lambda r, v: r["aqm"]),
                     ("bitrate class of the voter", lambda r, v: v[6])):
        print(f"### By {lab} (rule gt1)\n")
        print("| group | O-- / OX- votes | own rate | --U votes | own rate |\n|---|---|---|---|---|")
        a, b = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        for r, v in exp1:
            a[key(r, v)][0] += 1
            a[key(r, v)][1] += v[3]
        for r, v in up:
            b[key(r, v)][0] += 1
            b[key(r, v)][1] += v[3]
        for k in sorted(set(a) | set(b)):
            print(f"| {k} | {a[k][0]} | {rt(a[k][1], a[k][0])} | {b[k][0]} | {rt(b[k][1], b[k][0])} |")
        print()
    seqs = defaultdict(list)
    for r, v in exp1:
        seqs[(r["campaign"], r["run"], v[1], v[2])].append((v[0], v[3]))
    S = [[x for _, x in sorted(s)] for s in seqs.values()]
    raw, cen, n = lag1(S)
    obs = sum(has_run2(s) for s in S)
    expv = sum(p_run2(len(s), eps) for s in S) if eps is not None else None
    print("### Independence of wrong votes (O-- and OX-, gt1)\n")
    print(f"Sequences (run, client, other leaf) {len(S)}, vote pairs {n}. Lag-1 correlation raw {f2(raw)}, within-sequence "
          f"centred {f2(cen)}. Sequences with >= 2 wrong votes in a row: {obs}; expected at independent eps {f2(eps)}: "
          f"{f2(expv)}.\n")
    wr = Counter()
    for (cmp_, run, cl, ol), s in seqs.items():
        w = sum(1 - x for _, x in s)
        if w:
            wr[(cmp_, run, cl)] += w
    print("Clients with the most wrong votes: " + ", ".join(f"{k[0]} {k[1]} {k[2]} ({n_})" for k, n_ in wr.most_common(8)) + ".\n")
    return eps


def sec_b2(R):
    print("## B2: votes between the stored halves (h3, ECG intervals, equal-size templates)\n")
    rows = []
    for r in R:
        G = r["B2_groups"]
        for v in r["B2"]:
            g = G.get(str(v[1]))
            if g:
                rows.append((r, v, g))
    def block(sel, title):
        n = len(sel)
        own = sum(v[3] for _, v, _ in sel)
        print(f"- {title}: votes {n}, own-vote rate {rt(own, n)}")
    for lab, mixed in (("one leaf", False), ("mixed", True)):
        sel = [x for x in rows if x[2]["life_mixed"] == mixed]
        print(f"### {lab} groups ({len({(r['run'], r['campaign'], v[1]) for r, v, _ in sel})} groups with votes)\n")
        block(sel, "all")
        if mixed:
            block([x for x in sel if x[2]["halves_boundary"]], "stored halves = true leaf boundary")
            block([x for x in sel if not x[2]["halves_boundary"]], "stored halves not the leaf boundary")
        print()
        print("| bitrate class | votes | own rate |\n|---|---|---|")
        c = defaultdict(lambda: [0, 0])
        for _, v, _ in sel:
            c[v[6]][0] += 1
            c[v[6]][1] += v[3]
        for k in sorted(c):
            print(f"| {k} | {c[k][0]} | {rt(c[k][1], c[k][0])} |")
        print("\n| group size (stored halves) | votes | own rate | template size c p50 |\n|---|---|---|---|")
        c = defaultdict(list)
        for _, v, _ in sel:
            c[v[5]].append(v)
        for k in sorted(c):
            print(f"| {k} | {len(c[k])} | {rt(sum(x[3] for x in c[k]), len(c[k]))} | {np.median([x[4] for x in c[k]]):.0f} |")
        for sub, cond in ((("all", lambda g: True),) + ((("halves = boundary", lambda g: g["halves_boundary"]),
                                                       ("halves not boundary", lambda g: not g["halves_boundary"])) if mixed else ())):
            ev = defaultdict(list)
            for r, v, g in sel:
                if cond(g):
                    ev[(r["campaign"], r["run"], v[1], v[0])].append(v[3])
            ev = [x for x in ev.values() if len(x) >= 2]
            allown = sum(all(x) for x in ev)
            expct = sum(0.5 ** len(x) for x in ev)
            seq = defaultdict(list)
            for r, v, g in sel:
                if cond(g):
                    seq[(r["campaign"], r["run"], v[1], v[2])].append((v[0], v[3]))
            raw, cen, n = lag1([[x for _, x in sorted(s)] for s in seq.values()])
            print(f"\n{sub}: events with >= 2 voting members {len(ev)}; all vote own in {allown} "
                  f"({rt(allown, len(ev))}); expected at 0.5^n {f2(expct)} ({rt(expct, len(ev))}). Lag-1 correlation of a "
                  f"member's votes: raw {f2(raw)}, within-sequence centred {f2(cen)} ({n} pairs).")
        print()
    return rows


def sprt(groups_votes, b, eps):
    lo_own, lo_oth = math.log(0.5 / (1 - eps)), math.log(0.5 / eps)
    s, n_ev = 0.0, 0
    for ev in sorted(groups_votes):
        n_ev += 1
        for x in groups_votes[ev]:
            s += lo_own if x else lo_oth
        if s >= b:
            return "one queue", n_ev
        if s <= -b:
            return "two queues", n_ev
    return "undecided", n_ev


def sec_b3(R, eps_m):
    print("## B3: sequential test on the B2 votes\n")
    eps_list = ([("B1 (M)", eps_m)] if eps_m else []) + [(f"{e:g}", e) for e in EPS_FIXED]
    print(f"own vote ln(0.5 / (1 - eps)), other vote ln(0.5 / eps); stop at +b (one queue) / -b (two queues), checked "
          f"after each event with votes. b per run (6.55 for N = 7). eps: " + ", ".join(f"{a} = {f2(e)}" for a, e in eps_list) + ".\n")
    G = []
    for r in R:
        per = defaultdict(lambda: defaultdict(list))
        for v in r["B2"]:
            per[str(v[1])][v[0]].append(v[3])
        for k, g in r["B2_groups"].items():
            if k in per:
                G.append((r, g, per[k]))
    print("| eps | group type | groups | one queue | two queues | undecided | events to decision p50 / p90 |")
    print("|---|---|---|---|---|---|---|")
    for lab, e in eps_list:
        for gl, cond in (("one leaf", lambda g: not g["life_mixed"]),
                         ("mixed, halves = leaf boundary", lambda g: g["life_mixed"] and g["halves_boundary"]),
                         ("mixed, halves not boundary", lambda g: g["life_mixed"] and not g["halves_boundary"])):
            res = [sprt(v, r["b"], e) for r, g, v in G if cond(g)]
            dec = [n for x, n in res if x != "undecided"]
            c = Counter(x for x, _ in res)
            print(f"| {lab} | {gl} | {len(res)} | {c['one queue']} | {c['two queues']} | {c['undecided']} | "
                  f"{s4.pq(dec) if dec else '-'} |")
    print("\nWrong calls: one leaf -> 'two queues'; mixed -> 'one queue'.\n")


def cmd_sum(path: Path) -> None:
    R = s2.read_jsonl(path)
    print("# Step 5: measurement (Part A, B1-B3)\n")
    print(f"{len(R)} runs with windows (positives), ECG event intervals, {sum(r['n_events'] for r in R)} events.\n")
    sec_a(R)
    eps = sec_b1(R)
    sec_b2(R)
    sec_b3(R, eps)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("run", "sum"))
    ap.add_argument("paths", nargs="+", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        cmd_run(*a.paths[:3])
    else:
        cmd_sum(a.paths[0])


if __name__ == "__main__":
    main(sys.argv[1:])
