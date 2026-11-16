#!/usr/bin/env python3
"""Grouping diagnostics on the v3 campaign (2026-11-15). Measurement only: the detector, ECG v1.2, h3
(step 4 replay, m = 3), GT1 and the scoring helpers (step 4 / 5 / 6 / 7) are called unchanged.

    .venv/bin/python3 reports/v3-grouping-diag/diag.py rows .runs/2026-11-14_1818_v3   # -> rows.jsonl
    .venv/bin/python3 reports/v3-grouping-diag/diag.py report > reports/v3-grouping-diag/tables.md

Q1 (C9 H-DEPTH, control C7 pfifo). Per ECG event, interval [t0 - 1, t0 + 2] (step 7), per egress of the
plan (root, X, Y, A-D): congested by
  gt1       the GT1 hop episodes (ga.gt1_hop_episodes, router counters), as used so far;
  qlog      the same CoDel persistent-queue rule on the per-packet router trace (GT-Q logging):
            sojourn = t_deq - t_enq (netem delay removed as gtq.py does); an episode is a run of consecutive
            dequeued packets with sojourn >= 5 ms entering, >= 2.5 ms staying (gt1 TARGET and band), the
            queue never empty in between (t_enq[i] <= t_deq[i-1]), lasting >= 150 ms from the first
            entering arrival to the last staying arrival (gt1 INTERVAL); episodes closer than 150 ms merge
            (T: the gt1 constants); fq_codel: per client sub-queue (gtq.fq_index, the client's mode index),
            union over the clients (M);
  generous  an episode overlaps the interval; strict: episodes cover >= half of it (step 7 STRICT).
Strict false memberships = wrong (same-leaf) minus those sharing a congested egress with >= half of the
other members (step 6 judge_closes, unchanged) with gt1 vs qlog per-event sets.
Wrong pairs split by where the two paths separate (C9: same mid router = siblings, else across) and by
the levels congested (qlog strict) on the pair's paths in that event.
B1 votes typed "---" by gt1 (step 5 b1_votes, unchanged): which egresses the gt1 rule does see congested
in that event, relative to the pair (own leaf / other leaf / shared upstream = the three step 5 slots;
own or other mid = not a slot of the step 5 type).
Q2 (C7, C9, C13). First ten ECG events per rep with the stimulus active at t0 (v3-stimuli.csv); events of
the client's own leaf until membership (ECG events during a stimulus whose cell names the client's leaf
egress); group birth (h3: replay4 groups; ECG: first close with that node), mixed at birth, closes to
separate. h3 replayed offline with rep 1's events in rep 2's stimulus order (events of the same stimulus
cell taken in their own order; the rest appended) and the reverse.
Q3 (C13). Final wrong groups, birth / merge closes and purity per close; per stimulus window ECG events,
onsets per client (onsets.jsonl, kind onset) and events mixing both leaves; undecided clients.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "reports" / "step7-2026-11-14"))
sys.path.insert(0, str(ROOT / "scripts"))
import step7 as s7  # noqa: E402

s6, s5, s4, s3, s2, ga, d, gt1 = s7.s6, s7.s5, s7.s4, s7.s3, s7.s2, s7.ga, s7.d, s7.gt1
import gtq  # noqa: E402
from quiclab import router_trace as rt  # noqa: E402

TARGET_MS, BAND_MS, INTERVAL_S = 5.0, 2.5, 0.15   # (T) gt1
KDIR = None
Q1_CELLS = ("v3-C9-hdepth-tree16-", "v3-C7-hhier-s030-pfifo-")
Q2_CELLS = ("v3-C7-hhier-", "v3-C9-hdepth-", "v3-C13-llong-")


# ── queue-log truth ──────────────────────────────────────────────────────

def qlog_runs(t_enq, t_deq):
    """CoDel persistent-queue episodes on one dequeue sequence (sorted by t_deq)."""
    n = len(t_deq)
    if n < 2:
        return []
    soj = (t_deq - t_enq) * 1e3
    stay = soj >= BAND_MS
    link = np.zeros(n, bool)
    link[1:] = stay[1:] & stay[:-1] & (t_enq[1:] <= t_deq[:-1])   # queue not empty in between
    idx = np.flatnonzero(stay)
    if not len(idx):
        return []
    seg = np.cumsum(stay & ~link)[idx]
    cut = np.flatnonzero(np.diff(seg)) + 1
    first = np.concatenate([[0], cut])
    last = np.concatenate([cut - 1, [len(idx) - 1]])
    t_ent = np.where(soj[idx] >= TARGET_MS, t_enq[idx], np.inf)
    t0 = np.minimum.reduceat(t_ent, first)
    t1 = t_enq[idx][last]
    keep = np.isfinite(t0) & (t1 - t0 >= INTERVAL_S)
    merged = []
    for a, b in zip(t0[keep], t1[keep]):
        if merged and a - merged[-1][1] < INTERVAL_S:
            merged[-1][1] = max(merged[-1][1], float(b))
        else:
            merged.append([float(a), float(b)])
    return [tuple(x) for x in merged]


def qlog_episodes(run, hops_wanted, per_client=None):
    """{hop: episodes} (fq_codel: union over the clients' sub-queues); with per_client = {} also fills
    per_client[hop][client] = episodes of the client's own sub-queue (shared queue for other AQMs)."""
    ips = gtq.loopbacks(run)
    out, stats = {}, {}
    for iface, hop, path in gtq.traced(run):
        h = f"{hop[0]}->{hop[1]}"
        if h not in hops_wanted:
            continue
        table = rt.read_packets(path)
        to_s = lambda ns: (ns.astype(np.int64) - run.epoch_mono_ns) / 1e9  # noqa: E731
        delays = gtq.delay_series(run, hop)
        if any(x for _, x in delays):
            has = table["t_enq_ns"] >= 0
            extra = rt.step_at(delays, to_s(table.loc[has, "t_enq_ns"].to_numpy())) * 1e9
            table.loc[has, "t_enq_ns"] = table.loc[has, "t_enq_ns"] + extra.astype(np.int64)
        deq = table[(table["kind"] == "dequeue") & (table["t_enq_ns"] >= 0)]
        aqm, _ = gtq.aqm_of(run, hop)
        seqs, owners = [], []
        if aqm in gtq.FQ_AQMS:
            index = gtq.fq_index(deq["prio"].to_numpy(), deq["hash"].to_numpy())
            for sid in run.subs:
                pub = run.topology["subscribers"][sid].get("connects_to", run.pub)
                m = ((deq["saddr"] == ips[pub]) & (deq["daddr"] == ips[sid]) & (deq["proto"] == 17)).to_numpy()
                if m.sum() == 0:
                    continue
                vals, cnt = np.unique(index[m], return_counts=True)
                seqs.append(deq[index == vals[np.argmax(cnt)]])
                owners.append([sid])
        else:
            seqs.append(deq)
            owners.append([sid for sid in run.subs if ((deq["saddr"] == ips[run.topology["subscribers"][sid].get(
                "connects_to", run.pub)]) & (deq["daddr"] == ips[sid])).any()])
        eps = []
        for sq, own in zip(seqs, owners):
            sq = sq.sort_values("t_deq_ns")
            e_ = qlog_runs(to_s(sq["t_enq_ns"].to_numpy()), to_s(sq["t_deq_ns"].to_numpy()))
            eps += e_
            if per_client is not None:
                for sid in own:
                    per_client.setdefault(h, {})[sid] = e_
        eps.sort()
        out[h] = eps
        sq = deq.sort_values("t_deq_ns")
        td, soj = to_s(sq["t_deq_ns"].to_numpy()), (sq["t_deq_ns"].to_numpy() - sq["t_enq_ns"].to_numpy()) / 1e6
        stats[h] = (td, soj)
        del table
    return out, stats


def hot_gen(eps, lo, hi):
    return {h for h, v in eps.items() if any(a <= hi and b >= lo for a, b in v)}


# ── shared per-run state ─────────────────────────────────────────────────

def stimuli(rd):
    rows = d.rows(rd / "v3-stimuli.csv") if (rd / "v3-stimuli.csv").exists() else []
    return [{"start": float(r["start"]), "end": float(r["end"]), "target": r["target"], "cell": r["cell"], "hop": r["hop"],
             "d": float(r["d"]) if r.get("d") else None} for r in rows]


def stim_at(st, t):
    return [s for s in st if s["start"] - 0.5 <= t <= s["end"] + 1.0]


def load(rd):
    run, truth, subs, windows, events = s4.load_events(rd, ecg_intervals=True)
    leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
    same = truth["pairs_leaf"]
    leaf_hop = {s: h for s, h in truth.get("topology_group", {}).items() if h != s}
    delay = s2.egress_delay(run)
    hops = {s: s2.path_egresses(run, s, delay) for s in subs}
    plan = json.loads((rd / "v3-plan.json").read_text())
    m, evs, closes = s6.ecg_closes(rd, run, leaf)
    h = s4.replay4(events, subs, same, leaf, 3, True) if events else None
    hcl = []
    if h:
        bb = round(h["b"], 2)
        hcl = [{g: [i for i, e in r_.items() if e >= bb] for g, r_ in t.items()} for t in h["traj"]]
        hcl = [{g: ms for g, ms in c.items() if ms} for c in hcl]
    return dict(run=run, truth=truth, subs=subs, events=events, leaf=leaf, same=same, leaf_hop=leaf_hop, delay=delay,
                hops=hops, plan=plan, m=m, evs=evs, closes=closes, h=h, hcl=hcl, st=stimuli(rd))


def levels(plan):
    lv = {}
    for name, e in plan["egress"].items():
        if not e.get("shaped", True):
            continue
        lv[e["hop"]] = "root" if name == "root" else ("mid" if name in ("X", "Y", "up") else "leaf")
    return lv


def leaf_name(plan, c):
    for name, e in plan["egress"].items():
        if name not in ("root", "X", "Y", "up") and c in e["clients"]:
            return name
    return None


# ── Q1 ───────────────────────────────────────────────────────────────────

def q1(rd):
    S = load(rd)
    run, plan = S["run"], S["plan"]
    lv = levels(plan)
    eg = set(lv)
    g_eps = {h: v for h, v in ga.gt1_hop_episodes(run).items() if h in eg}
    q_eps, qstats = qlog_episodes(run, eg)
    lohi = [(e["t0"] + s2.NEG_SPAN[0], e["t0"] + s2.NEG_SPAN[1]) for e in S["evs"]]
    ver = {"gt1": g_eps, "qlog": q_eps}
    hot = {(v, k): [(hot_gen(E, lo, hi) if k == "gen" else s7.strict_hot(E, lo, hi)) & eg for lo, hi in lohi]
           for v, E in ver.items() for k in ("gen", "strict")}
    # a. per-event sets and disagreement per level
    per_event, dis = [], defaultdict(Counter)
    for x, (lo, hi) in enumerate(lohi):
        row = {"t0": S["evs"][x]["t0"], "case": S["evs"][x].get("case"), "n": len(S["evs"][x]["members"]),
               "stim": [s["cell"] for s in stim_at(S["st"], S["evs"][x]["t0"])]}
        for key, sets in hot.items():
            row["|".join(key)] = sorted(sets[x])
        for k in ("gen", "strict"):
            a, b = hot[("gt1", k)][x], hot[("qlog", k)][x]
            for h in eg:
                dis[(k, lv[h])][("gt1+" if h in a else "gt1-") + ("q+" if h in b else "q-")] += 1
        # queue levels in the event: max sojourn and share of time >= 5 ms per egress
        qs = {}
        for h, (td, soj) in qstats.items():
            mm = (td >= lo) & (td <= hi)
            qs[h] = [round(float(soj[mm].max()), 1) if mm.any() else 0.0,
                     round(float(np.mean(soj[mm] >= TARGET_MS)), 2) if mm.any() else 0.0]
        row["q"] = qs
        per_event.append(row)
    # b. B1 votes typed '---' by gt1
    rules = s5.make_rules(S["delay"], ga.gt1_hop_episodes(run))
    rates = {s: (run.topology["subscribers"].get(s) or {}).get("rate_kbps") for s in S["subs"]}
    votes = s5.b1_votes(S["events"], S["leaf"], S["leaf_hop"], S["hops"], rules, rates) if S["events"] else []
    vt = Counter()
    blank = []
    for v in votes:
        ev, i, l2s, own_vote, _, typ = v[:6]
        if typ != "---":
            continue
        row = S["events"][ev][0]
        hg = rules["gt1"](row["lo"], row["hi"]) & eg
        hq = hot_gen(q_eps, row["lo"], row["hi"]) & eg
        oth = l2s.split("+")
        mine = S["hops"][i] & eg
        theirs = S["hops"].get(oth[0], set()) & eg
        shared = set.intersection(*[S["hops"].get(j, set()) for j in [i] + oth]) & eg
        own_mid = {h for h in mine - theirs if lv[h] == "mid"}
        oth_mid = {h for h in theirs - mine if lv[h] == "mid"}
        sep = "siblings" if any(lv[h] == "mid" for h in shared) else "across"
        cls = ("gt1 sees nothing" if not hg else
               "+".join(sorted({"own mid" for _ in [1] if own_mid & hg} | {"other mid" for _ in [1] if oth_mid & hg}
                               | {"other" for _ in [1] if hg - own_mid - oth_mid})))
        vt[(sep, cls, "qlog sees " + ("+".join(sorted({lv[h] for h in hq})) or "nothing"))] += 1
        blank.append(ev)
    blank_ev = sorted(set(blank))
    b_rows = []
    for ev in blank_ev:
        row = S["events"][ev][0]
        t = row["lo"] - s2.NEG_SPAN[0]
        b_rows.append({"ev": ev, "t": round(t, 2), "stim": [(s["cell"], s["target"]) for s in stim_at(S["st"], t)],
                       "gt1": sorted(rules["gt1"](row["lo"], row["hi"]) & eg),
                       "qlog_gen": sorted(hot_gen(q_eps, row["lo"], row["hi"]) & eg),
                       "qlog_strict": sorted(s7.strict_hot(q_eps, row["lo"], row["hi"]) & eg)})
    # c. strict re-score
    hl = [(e[0]["lo"], e[0]["hi"]) for e in S["events"]]
    hh = {(v, k): [(hot_gen(E, lo, hi) if k == "gen" else s7.strict_hot(E, lo, hi)) for lo, hi in hl]
          for v, E in ver.items() for k in ("gen", "strict")}
    score = {}
    for v in ver:
        for k in ("gen", "strict"):
            score[f"ecg|{v}|{k}"] = s6.judge_closes(S["closes"], hot[(v, k)], S["leaf"], S["same"], S["hops"])
            if S["hcl"]:
                score[f"h3|{v}|{k}"] = s6.judge_closes(S["hcl"], hh[(v, k)], S["leaf"], S["same"], S["hops"])
    # d. wrong pairs by separation level and congested levels (qlog strict)
    split = {}
    for meth, cl, hs in (("ecg", S["closes"], hot[("qlog", "strict")]), ("h3", S["hcl"], hh[("qlog", "strict")])):
        c = Counter()
        for x, groups in enumerate(cl):
            H = hs[x] if x < len(hs) else set()
            for ms in groups.values():
                ms = sorted(ms)
                for p, a in enumerate(ms):
                    for b in ms[p + 1:]:
                        if S["same"].get(f"{a}|{b}", False) or "sub-ctrl" in (a, b):
                            continue
                        com = S["hops"][a] & S["hops"][b] & eg
                        sep = "siblings (same mid)" if any(lv[h] == "mid" for h in com) else "across mids"
                        if com & H:
                            cat = "shared " + "+".join(sorted({lv[h] for h in com & H})) + " congested"
                        else:
                            on = (S["hops"][a] | S["hops"][b]) & eg & H
                            cat = "not shared; congested on paths: " + ("+".join(sorted({lv[h] for h in on})) or "none")
                        c[(sep, cat)] += 1
        split[meth] = {"|".join(k): v for k, v in c.items()}
    return {"run": rd.name, "rep": plan["rep"], "aqm": plan["aqm"], "n_events": len(lohi),
            "dis": {"|".join(k): dict(v) for k, v in dis.items()},
            "vote_types": Counter(v[5] for v in votes), "blank_votes": {"|".join(k): n for k, n in vt.items()},
            "blank_events": b_rows, "score": score, "pairs": split,
            "ep_counts": {v: {h: len(E.get(h, [])) for h in sorted(eg)} for v, E in ver.items()},
            "per_event": per_event}


# ── Q2 / Q3 ──────────────────────────────────────────────────────────────

def stim_cell(st, t):
    s = stim_at(st, t)
    return s[0]["cell"] if s else "none"


def groups_life(closes, leaf):
    """Per group id: birth close, members at birth, mixed at birth, closes until pure (None = never)."""
    born, out = {}, {}
    for x, groups in enumerate(closes):
        for g, ms in groups.items():
            if g not in born:
                born[g] = x
                lv = {leaf.get(i) for i in ms}
                out[g] = {"born": x, "members": sorted(ms), "mixed": len(lv) > 1 or None in lv, "separated_after": None,
                          "last": x}
            else:
                out[g]["last"] = x
                lv = {leaf.get(i) for i in ms}
                if out[g]["mixed"] and out[g]["separated_after"] is None and len(lv) == 1 and None not in lv:
                    out[g]["separated_after"] = x - born[g]
    return out


def prf_last(closes, same, subs):
    if not closes:
        return None
    c = closes[-1]
    tp = fp = 0
    for ms in c.values():
        ms = sorted(ms)
        for p, a in enumerate(ms):
            for b in ms[p + 1:]:
                tp += same.get(f"{a}|{b}", False)
                fp += not same.get(f"{a}|{b}", False)
    return {"P": tp / (tp + fp) if tp + fp else None, "pairs": tp + fp}


def q2(rd):
    S = load(rd)
    plan, leaf, st = S["plan"], S["leaf"], S["st"]
    evs = S["evs"]
    first10 = [{"t0": round(e["t0"], 2), "case": e.get("case"), "stim": stim_cell(st, e["t0"]),
                "members": dict(Counter(leaf_name(plan, i) or i for i in e["members"]))} for e in evs[:10]]
    # b. own-leaf events until membership (ECG first close as member; h3 first_member)
    own_ev = {}
    for c in S["subs"]:
        ln = leaf_name(plan, c)
        own_ev[c] = [x for x, e in enumerate(evs) if ln and ln in stim_cell(st, e["t0"]).split("+")]
    ecg_mem = {}
    for x, groups in enumerate(S["closes"]):
        for ms in groups.values():
            for i in ms:
                ecg_mem.setdefault(i, x)
    ecg_b = {c: {"close": x, "t": evs[x]["t0"], "own_leaf_events": sum(y <= x for y in own_ev[c]),
                 "member_events": S["m"]["membership_events"].get(c)} for c, x in ecg_mem.items()}
    h3_b = {}
    if S["h"]:
        hl = [e[0]["lo"] - s2.NEG_SPAN[0] for e in S["events"]]
        for c, (took, right, ev) in S["h"]["first_member"].items():
            ln = leaf_name(plan, c)
            h3_b[c] = {"ev": ev, "t": hl[ev], "right": right, "took_part": took,
                       "own_leaf_events": sum(1 for t in hl[:ev + 1] if ln and ln in stim_cell(st, t).split("+"))}
    # c. group birth
    ecg_g = groups_life(S["closes"], leaf)
    for g in ecg_g.values():
        g["stim"] = stim_cell(st, evs[g["born"]]["t0"])
        g["case"] = evs[g["born"]].get("case")
    h3_g = {}
    if S["h"]:
        hl = [e[0]["lo"] - s2.NEG_SPAN[0] for e in S["events"]]
        for k, g in S["h"]["groups"].items():
            h3_g[k] = {"born": g["born"], "members": g["members"], "mixed": g["merged"], "life_mixed": g["life_mixed"],
                       "separated_after": g["separated_after"], "class": g["class"], "parent": g["parent"],
                       "removed": g.get("removed"), "split_at": g.get("split_at"), "stim": stim_cell(st, hl[g["born"]])}
    out = {"run": rd.name, "rep": plan["rep"], "aqm": plan["aqm"], "cell": rd.name.rsplit("-r", 1)[0], "first10": first10,
           "ecg_b": ecg_b, "h3_b": h3_b, "ecg_groups": ecg_g, "h3_groups": h3_g,
           "h3_last": s4.prf(Counter(S["h"]["closes"][-1])) if S["h"] and S["h"]["closes"] else None,
           "ecg_final": {k: S["m"]["pairwise"].get(k) for k in ("precision", "recall", "coverage")},
           "order": [stim_cell(st, e[0]["lo"] - s2.NEG_SPAN[0]) for e in S["events"]]}
    if rd.name.startswith("v3-C13-"):
        out["q3"] = q3(rd, S)
    return out


def q3(rd, S):
    plan, leaf, st, evs = S["plan"], S["leaf"], S["st"], S["evs"]
    m = S["m"]
    # a. final groups (ECG nodes with members) and purity per close
    fin = defaultdict(list)
    for f, v in m["final"].items():
        if v.get("member") and v.get("node") is not None:
            fin[v["node"]].append(f)
    life = groups_life(S["closes"], leaf)
    ecg_wrong = []
    for node, ms in fin.items():
        lv = Counter(leaf_name(plan, i) for i in ms)
        g = life.get(node) or life.get(str(node)) or {}
        traj = []
        for x, c in enumerate(S["closes"]):
            mm = c.get(node) or c.get(str(node))
            if mm:
                cnt = Counter(leaf_name(plan, i) for i in mm)
                traj.append((x, round(evs[x]["t0"], 1), stim_cell(st, evs[x]["t0"]), dict(cnt)))
        ecg_wrong.append({"node": node, "members": dict(lv), "wrong": len(lv) > 1, "born": g.get("born"),
                          "born_t": round(evs[g["born"]]["t0"], 1) if g.get("born") is not None else None,
                          "born_stim": stim_cell(st, evs[g["born"]]["t0"]) if g.get("born") is not None else None,
                          "traj": traj})
    h3_final = []
    if S["hcl"]:
        hl = [e[0]["lo"] - s2.NEG_SPAN[0] for e in S["events"]]
        last = S["hcl"][-1]
        for k, ms in last.items():
            g = S["h"]["groups"][k]
            traj = []
            for x, c in enumerate(S["hcl"]):
                if k in c:
                    traj.append((x, round(hl[x], 1), stim_cell(st, hl[x]), dict(Counter(leaf_name(plan, i) for i in c[k]))))
            h3_final.append({"group": k, "members": dict(Counter(leaf_name(plan, i) for i in ms)),
                             "wrong": len({leaf_name(plan, i) for i in ms}) > 1, "born": g["born"], "class": g["class"],
                             "parent": g["parent"], "born_members": dict(Counter(leaf_name(plan, i) for i in g["members"])),
                             "born_stim": stim_cell(st, hl[g["born"]]), "traj": traj})
    # b. per stimulus window
    on = [json.loads(x) for x in open(rd / "grouping-d150-v2-owd" / "onsets.jsonl") if '"onset"' in x]
    on = [o for o in on if o.get("kind") == "onset"]
    win = []
    for s in st:
        lo, hi = s["start"] - 0.5, s["end"] + 2.0
        ev = [e for e in evs if lo <= e["t0"] <= hi]
        per = Counter(o["flow"] for o in on if lo <= o["t_onset"] <= hi)
        cl = [c for c in S["subs"] if c != "sub-ctrl"]
        exp = [c for c in cl if s["cell"] == "up" or leaf_name(plan, c) == s["cell"]]
        win.append({"start": s["start"], "d": s["d"], "cell": s["cell"], "ecg_events": len(ev),
                    "onsets_per_expected_client": round(float(np.mean([per[c] for c in exp])), 2) if exp else None,
                    "onsets_other_clients": sum(per[c] for c in cl if c not in exp),
                    "events_both_leaves": sum(len({leaf_name(plan, i) for i in e["members"]} - {None}) > 1 for e in ev),
                    "event_sizes": [len(e["members"]) for e in ev]})
    # c. undecided clients
    und = []
    for f, v in m["final"].items():
        if f == "sub-ctrl":
            continue
        if not v.get("member"):
            und.append({"client": f, "leaf": leaf_name(plan, f), "L": round(v.get("L") or 0, 2),
                        "node": v.get("node"), "cand": v.get("cand"), "onsets": sum(o["flow"] == f for o in on),
                        "events": sum(f in e["members"] for e in evs), "member_events": m["membership_events"].get(f)})
    return {"ecg_final_groups": ecg_wrong, "h3_final_groups": h3_final, "windows": win, "undecided": und,
            "leaves": {k: v for k, v in m.get("leaves", {}).items()}}


def permute(order_from, order_to):
    """indices of events_to reordered to follow the stimulus-cell sequence order_from; unmatched appended."""
    pools = defaultdict(list)
    for i, c in enumerate(order_to):
        pools[c].append(i)
    out = []
    for c in order_from:
        if pools[c]:
            out.append(pools[c].pop(0))
    rest = sorted(i for v in pools.values() for i in v)
    return out + rest


def q2d(pair):
    """h3 replayed with rep 1's events in rep 2's stimulus order and the reverse."""
    r1, r2 = pair
    out = {"cell": r1.name.rsplit("-r", 1)[0]}
    L = {}
    for rd in (r1, r2):
        run, truth, subs, windows, events = s4.load_events(rd, ecg_intervals=True)
        leaf = {s: frozenset(v) for s, v in truth["leaf"].items() if v}
        st = stimuli(rd)
        order = [stim_cell(st, e[0]["lo"] - s2.NEG_SPAN[0]) for e in events]
        L[rd] = (subs, truth["pairs_leaf"], leaf, events, order)
    for a, b, tag in ((r1, r2, "rep1 events, rep2 order"), (r2, r1, "rep2 events, rep1 order"),
                      (r1, r1, "rep1 as recorded"), (r2, r2, "rep2 as recorded")):
        subs, same, leaf, events, order = L[a]
        ix = permute(L[b][4], order) if a != b else list(range(len(events)))
        # time slots kept in recorded order (replay4 uses lo / hi only for bookkeeping bins and durations)
        ev = [({**events[i][0], "lo": events[k][0]["lo"], "hi": events[k][0]["hi"]},) + tuple(events[i][1:])
              for k, i in enumerate(ix)]
        h = s4.replay4(ev, subs, same, leaf, 3, True)
        mem = [x for x in h["first_member"].values()]
        out[tag] = {"last": s4.prf(Counter(h["closes"][-1])) if h["closes"] else None,
                    "pooled_P": s4.prf(s4.pooled(h["closes"]))[0],
                    "groups": len(h["groups"]), "mixed_at_birth": sum(g["merged"] for g in h["groups"].values()),
                    "first_member_ev_p50": float(np.median([x[2] for x in mem])) if mem else None,
                    "first_member_wrong": sum(not x[1] for x in mem), "n_first": len(mem),
                    "first10": [order[i] for i in ix[:10]]}
    return out


# ── Q4: fq_codel under the per-flow truth ────────────────────────────────

Q4_CELLS = ("v3-C7-hhier-s030-fq_codel-", "v3-C9-hdepth-tree16-fq_codel-", "v3-C10-hindep-s030-fq_codel-",
            "v3-C12-amixed-access-fq_codel-")
JACCARD = 0.5   # (M) pair same: co-constrained in >= half of the events in which either was constrained


def q4(rd):
    S = load(rd)
    run, plan, leaf, st = S["run"], S["plan"], S["leaf"], S["st"]
    subs = [c for c in S["subs"] if c != "sub-ctrl"]
    targets = {s_["hop"] for s_ in st}
    pc = {}
    qlog_episodes(run, targets, per_client=pc)
    behind = {h: sorted(c for c in subs if h in S["hops"].get(c, set()) or h in {f"{a}->{b}" for a, b in d.path_hops(run, run.pub, c)})
              for h in targets}
    ov = lambda E, lo, hi: any(a <= hi and b >= lo for a, b in E)   # noqa: E731
    cov = lambda E, lo, hi: sum(max(0.0, min(b, hi) - max(a, lo)) for a, b in E) >= 0.5 * (hi - lo)   # noqa: E731
    ev_rows, Cs = [], []
    for e in S["evs"]:
        lo, hi = e["t0"] + s2.NEG_SPAN[0], e["t0"] + s2.NEG_SPAN[1]
        hs = sorted({s_["hop"] for s_ in stim_at(st, e["t0"])})
        bh = sorted({c for h in hs for c in behind.get(h, [])})
        C = sorted({c for h in hs for c in behind.get(h, []) if ov(pc.get(h, {}).get(c, []), lo, hi)})
        Cst = sorted({c for h in hs for c in behind.get(h, []) if cov(pc.get(h, {}).get(c, []), lo, hi)})
        Cs.append(set(C))
        ev_rows.append({"t0": round(e["t0"], 2), "targets": hs, "cell": stim_cell(st, e["t0"]), "behind": len(bh),
                        "constrained": len(C), "constrained_strict": len(Cst), "ecg_members": len(e["members"]),
                        "members_constrained": len(set(e["members"]) & set(C))})
    # run-level per-flow pair truth
    n_c = Counter(c for C in Cs for c in C)
    same = {}
    for x, a in enumerate(S["subs"]):
        for b in S["subs"][x + 1:]:
            both = sum(a in C and b in C for C in Cs)
            either = sum(a in C or b in C for C in Cs)
            v = bool(either) and both / either >= JACCARD
            same[f"{a}|{b}"] = same[f"{b}|{a}"] = v
    ever = {c for c in subs if n_c[c]}

    def score_pairs(dec):
        """dec: {(a, b): 'SAME' | 'DIFF' | 'UNCERTAIN'}; pairs with a never-constrained client count only when SAME."""
        tp = fp = fn = tn = unc = 0
        for (a, b), v in dec.items():
            if "sub-ctrl" in (a, b):
                continue
            t = same[f"{a}|{b}"]
            rel = a in ever and b in ever
            if v == "SAME":
                tp += t
                fp += not t
            elif not rel:
                continue                       # never constrained and left out: correct, not counted
            elif v == "UNCERTAIN":
                unc += 1
            else:
                fn += t
                tn += not t
        dec_n = tp + fp + fn + tn
        return {"P": tp / (tp + fp) if tp + fp else None, "R": tp / (tp + fn) if tp + fn else None,
                "cov": dec_n / (dec_n + unc) if dec_n + unc else None, "same_pairs": sum(
                    same[f"{a}|{b}"] for x, a in enumerate(subs) for b in subs[x + 1:])}
    ecg_dec = {tuple(k.split("|")): v["decided"] for k, v in S["m"]["pairwise"]["pairs"].items()}
    out = {"run": rd.name, "rep": plan["rep"], "aqm": plan["aqm"], "cell": rd.name.rsplit("-r", 1)[0][3:],
           "ever_constrained": sorted(ever), "n_clients": len(subs), "events": ev_rows,
           "ecg_leaf": {k: S["m"]["pairwise"].get(k) for k in ("precision", "recall", "coverage")},
           "ecg_flow": score_pairs(ecg_dec)}
    if S["h"]:
        bb = S["h"]["b"]
        E = S["h"]["traj"][-1]
        mem = defaultdict(set)
        for k, r_ in E.items():
            for i, e in r_.items():
                if e >= round(bb, 2):
                    mem[i].add(k)
        dec = {}
        for x, a in enumerate(S["subs"]):
            for b in S["subs"][x + 1:]:
                dec[(a, b)] = "UNCERTAIN" if not mem[a] or not mem[b] else ("SAME" if mem[a] & mem[b] else "DIFF")
        out["h3_leaf"] = s4.prf(Counter(S["h"]["closes"][-1])) if S["h"]["closes"] else None
        out["h3_flow"] = score_pairs(dec)
    # false memberships at declaration: same-leaf (step 6 judge_closes) and per-flow (pair truth majority)
    for meth, cl in (("ecg", S["closes"]), ("h3", S["hcl"])):
        seen, n, wl, wf = set(), 0, 0, 0
        for groups in cl:
            for g, ms in groups.items():
                for i in ms:
                    if (i, g) in seen:
                        continue
                    seen.add((i, g))
                    n += 1
                    lf = leaf.get(i)
                    wl += not (bool(lf) and lf == s3.majority(ms, leaf))
                    others = [j for j in ms if j != i]
                    wf += not (i in ever and others and sum(same.get(f"{i}|{j}", False) for j in others) >= len(others) / 2)
            for key in list(seen):
                if key[1] not in groups or key[0] not in groups[key[1]]:
                    seen.discard(key)
        out[f"{meth}_mem"] = {"declared": n, "wrong_leaf": wl, "wrong_flow": wf}
    return out


def lambda_q4(x):
    return safe(q4, x)


def safe(f, x):
    try:
        return f(x)
    except Exception as e:   # noqa: BLE001
        import traceback
        return {"run": str(x), "error": repr(e), "tb": traceback.format_exc()[-1500:]}


def main_rows(kdir):
    runs = sorted(p for p in kdir.iterdir() if p.is_dir())
    r1 = [p for p in runs if p.name.startswith(Q1_CELLS)]
    r2 = [p for p in runs if p.name.startswith(Q2_CELLS)]
    pairs = []
    by = defaultdict(dict)
    for p in r2:
        by[p.name.rsplit("-r", 1)[0]][p.name.rsplit("-r", 1)[1]] = p
    pairs = [(v["1"], v["2"]) for v in by.values() if "1" in v and "2" in v]
    with open(HERE / "rows.jsonl", "w") as fh, Pool(8) as pool:
        for r in pool.imap_unordered(lambda_q1, r1):
            fh.write(json.dumps({"q": 1, **r}, default=list) + "\n")
            fh.flush()
        for r in pool.imap_unordered(lambda_q2, r2):
            fh.write(json.dumps({"q": 2, **r}, default=list) + "\n")
            fh.flush()
        for r in pool.imap_unordered(lambda_q2d, pairs):
            fh.write(json.dumps({"q": "2d", **r}, default=list) + "\n")
            fh.flush()


def lambda_q1(x):
    return safe(q1, x)


def lambda_q2(x):
    return safe(q2, x)


def lambda_q2d(x):
    return safe(q2d, x)


if __name__ == "__main__":
    if sys.argv[1] == "rows4":
        kdir = Path(sys.argv[2])
        runs = [p for p in sorted(kdir.iterdir()) if p.is_dir() and p.name.startswith(Q4_CELLS)]
        with Pool(8) as pool, open(HERE / "rows4.jsonl", "w") as fh:
            for r in pool.imap_unordered(lambda_q4, runs):
                fh.write(json.dumps(r, default=list) + "\n")
    elif sys.argv[1] == "rows2d":
        rows = [json.loads(x) for x in open(HERE / "rows.jsonl") if x.strip()]
        keep = [r for r in rows if r["q"] != "2d"]
        kdir = Path(sys.argv[2])
        by = defaultdict(dict)
        for p in sorted(kdir.iterdir()):
            if p.is_dir() and p.name.startswith(Q2_CELLS):
                by[p.name.rsplit("-r", 1)[0]][p.name.rsplit("-r", 1)[1]] = p
        pairs = [(v["1"], v["2"]) for v in by.values() if "1" in v and "2" in v]
        with Pool(9) as pool:
            new = list(pool.imap_unordered(lambda_q2d, pairs))
        with open(HERE / "rows.jsonl", "w") as fh:
            for r in keep + [{"q": "2d", **x} for x in new]:
                fh.write(json.dumps(r, default=list) + "\n")
    elif sys.argv[1] == "rows":
        main_rows(Path(sys.argv[2]))
    elif sys.argv[1] == "one":
        r = {"1": q1, "2": q2}[sys.argv[2]](Path(sys.argv[3]))
        print(json.dumps(r, default=list)[:3000])
