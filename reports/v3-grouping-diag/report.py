#!/usr/bin/env python3
"""Tables from reports/v3-grouping-diag/rows.jsonl (diag.py rows).

    .venv/bin/python3 reports/v3-grouping-diag/report.py > reports/v3-grouping-diag/tables.md
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = [json.loads(x) for x in open(HERE / "rows.jsonl") if x.strip()]
err = [r for r in R if "error" in r]
Q1 = sorted((r for r in R if r["q"] == 1 and "error" not in r), key=lambda r: r["run"])
Q2 = sorted((r for r in R if r["q"] == 2 and "error" not in r), key=lambda r: r["run"])
Q2D = sorted((r for r in R if r["q"] == "2d" and "error" not in r), key=lambda r: r["cell"])
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731
cell = lambda r: r["run"].rsplit("-r", 1)[0][3:]   # noqa: E731

print("# Grouping diagnostics (v3): tables\n")
if err:
    print("Errors: " + "; ".join(f"{e['run']}: {e['error']}" for e in err) + "\n")

# ── Q1a ──
print("## Q1a. Per ECG event and egress: gt1 (router counters) vs qlog (per-packet trace, same CoDel rule)\n")
print("Counts of event x egress; `both` = both congested, `gt1 only`, `qlog only`, `neither`. Rep 1 / rep 2.\n")
for k in ("gen", "strict"):
    print(f"### {'generous (overlap)' if k == 'gen' else 'strict (>= half of the interval)'}\n")
    print("| cell | level | both | gt1 only | qlog only | neither | disagree share |")
    print("|---|---|---|---|---|---|---|")
    cells = defaultdict(dict)
    for r in Q1:
        cells[cell(r)][r["rep"]] = r
    for c, reps in cells.items():
        for lv in ("root", "mid", "leaf"):
            vals = []
            for rep in (1, 2):
                x = reps.get(rep, {}).get("dis", {}).get(f"{k}|{lv}")
                vals.append(x)
            if all(v is None for v in vals):
                continue
            g = lambda key: " / ".join(str((v or {}).get(key, 0)) for v in vals)   # noqa: E731
            sh = " / ".join(f(((v or {}).get("gt1+q-", 0) + (v or {}).get("gt1-q+", 0)) / max(1, sum((v or {}).values())))
                            for v in vals)
            print(f"| {c} | {lv} | {g('gt1+q+')} | {g('gt1+q-')} | {g('gt1-q+')} | {g('gt1-q-')} | {sh} |")
    print()
print("Episodes per egress over the run, gt1 / qlog (rep 1; rep 2):\n")
print("| cell | " + " | ".join(["egress: gt1/qlog r1 ; r2"]) + " |")
print("|---|---|")
for c in sorted({cell(r) for r in Q1}):
    reps = {r["rep"]: r for r in Q1 if cell(r) == c}
    hs = sorted(next(iter(reps.values()))["ep_counts"]["gt1"])
    print(f"| {c} | " + ", ".join(f"{h} {' ; '.join(str(reps[p]['ep_counts']['gt1'].get(h)) + '/' + str(reps[p]['ep_counts']['qlog'].get(h)) for p in (1, 2) if p in reps)}" for h in hs) + " |")
print()

# ── Q1b ──
print("## Q1b. B1 votes the gt1 rule types `---` (no own leaf / other leaf / shared upstream congested)\n")
print("| cell | rep | votes | `---` votes | pair | what gt1 sees in that event | what qlog (generous) sees | votes |")
print("|---|---|---|---|---|---|---|---|")
for r in Q1:
    tot = sum(r["vote_types"].values())
    blank = r["vote_types"].get("---", 0)
    first = True
    for k, n in sorted(r["blank_votes"].items(), key=lambda x: -x[1]):
        sep, g, q = k.split("|")
        print(f"| {cell(r) if first else ''} | {r['rep'] if first else ''} | {tot if first else ''} | {blank if first else ''} | {sep} | {g} | {q} | {n} |")
        first = False
    if first:
        print(f"| {cell(r)} | {r['rep']} | {tot} | {blank} | - | - | - | 0 |")
print()
print("Events behind the `---` votes: stimulus active at t0 (cell) and what each truth calls congested.\n")
print("| cell | rep | events | stimulus cells (events) | gt1 empty | qlog strict empty | qlog strict levels (events) |")
print("|---|---|---|---|---|---|---|")
LV = {"rr->r0": "root", "r0->r1": "X", "r0->r2": "Y", "r1->switch-a": "A", "r1->switch-b": "B", "r2->switch-c": "C",
      "r2->switch-d": "D"}
for r in Q1:
    if not r["run"].startswith("v3-C9"):
        continue
    be = r["blank_events"]
    sc = Counter("+".join(sorted({c for c, _ in e["stim"]})) or "none" for e in be)
    lv = Counter("+".join(LV.get(h, h) for h in e["qlog_strict"]) or "none" for e in be)
    print(f"| {cell(r)} | {r['rep']} | {len(be)} | {', '.join(f'{k} {v}' for k, v in sc.most_common(6))} | "
          f"{sum(not e['gt1'] for e in be)} | {sum(not e['qlog_strict'] for e in be)} | {', '.join(f'{k} {v}' for k, v in lv.most_common(6))} |")
print()

# ── Q1c ──
print("## Q1c. False memberships (same-leaf wrong; strict = wrong minus those sharing a congested egress with >= half the members)\n")
print("| cell | method | memberships r1 / r2 | wrong (same-leaf) r1 / r2 | strict wrong, gt1 r1 / r2 | strict wrong, qlog r1 / r2 | "
      "generous-rule wrong, gt1 / qlog r1 ; r2 | wrong pairs not sharing (strict), gt1 / qlog r1 ; r2 |")
print("|---|---|---|---|---|---|---|---|")
cells = defaultdict(dict)
for r in Q1:
    cells[cell(r)][r["rep"]] = r
for c, reps in cells.items():
    for meth in ("ecg", "h3"):
        def g(rep, ver, k, which):
            s = reps.get(rep, {}).get("score", {}).get(f"{meth}|{ver}|{k}")
            if not s:
                return None
            pairs, mem = s
            if which == "mem":
                return mem.get("declared", 0)
            if which == "wrong":
                return mem.get("wrong", 0)
            if which == "strict":
                return mem.get("wrong", 0) - mem.get("shared", 0)
            if which == "pairs_ns":
                return f"{pairs.get('not shared', 0)}/{pairs.get('wrong', 0)}"
        two = lambda ver, k, w: " / ".join(str(g(rep, ver, k, w)) for rep in (1, 2))   # noqa: E731
        print(f"| {c} | {meth} | {two('gt1', 'strict', 'mem')} | {two('gt1', 'strict', 'wrong')} | {two('gt1', 'strict', 'strict')} | "
              f"{two('qlog', 'strict', 'strict')} | "
              f"{' ; '.join(str(g(rep, 'gt1', 'gen', 'strict')) + ' / ' + str(g(rep, 'qlog', 'gen', 'strict')) for rep in (1, 2))} | "
              f"{' ; '.join(str(g(rep, 'gt1', 'strict', 'pairs_ns')) + ' / ' + str(g(rep, 'qlog', 'strict', 'pairs_ns')) for rep in (1, 2))} |")
print()

# ── Q1d ──
print("## Q1d. Wrong pairs (pair x close) by where the paths separate and what is congested (qlog strict)\n")
for meth in ("h3", "ecg"):
    print(f"### {meth}\n")
    keys = sorted({k for r in Q1 if r["run"].startswith("v3-C9") for k in r["pairs"].get(meth, {})})
    print("| cell | " + " | ".join(k.replace("|", ": ") for k in keys) + " |")
    print("|---|" + "---|" * len(keys))
    for c, reps in cells.items():
        if not c.startswith("C9"):
            continue
        print(f"| {c} | " + " | ".join(" / ".join(str(reps.get(rep, {}).get("pairs", {}).get(meth, {}).get(k, 0)) for rep in (1, 2))
                                     for k in keys) + " |")
    print()

# ── Q2 ──
print("## Q2a. First ten ECG events per rep (stimulus cell active at t0 [ECG case] members by leaf)\n")
for r in Q2:
    if "-pfifo-" not in r["run"]:
        continue
    seq = "; ".join(f"{e['stim']} [{e['case']}] " + ",".join(f"{k}{v}" for k, v in sorted(e["members"].items()))
                    for e in r["first10"])
    print(f"- **{cell(r)} r{r['rep']}**: {seq}")
print()
print("Stimulus order (cells of the stimulus windows, as scheduled) per rep:\n")
# from h3 event order (deduplicated consecutive)
for r in Q2:
    if "-pfifo-" not in r["run"]:
        continue
    o = [x for i, x in enumerate(r["order"]) if i == 0 or x != r["order"][i - 1]]
    print(f"- {cell(r)} r{r['rep']}: {' > '.join(o[:14])}")
print()

print("## Q2b. Time to first membership: own-leaf events, all events, seconds (median over clients; n members)\n")
print("ECG: first close as a member; own-leaf events = ECG events during a stimulus whose cell names the client's leaf. "
      "h3: replay4 first_member (took_part = events the client took part in).\n")
print("| cell | ECG own-leaf events r1 / r2 | ECG member events (ECG count) r1 / r2 | ECG seconds r1 / r2 | h3 own-leaf events r1 / r2 | "
      "h3 events took part r1 / r2 | h3 seconds r1 / r2 | h3 first memberships wrong r1 / r2 |")
print("|---|---|---|---|---|---|---|---|")
C2 = defaultdict(dict)
for r in Q2:
    C2[cell(r)][r["rep"]] = r
med = lambda xs: f(float(np.median(xs)), 1) if xs else "-"   # noqa: E731
for c, reps in sorted(C2.items()):
    def col(src, key):
        return " / ".join(med([v[key] for k, v in reps[rep][src].items() if k != "sub-ctrl" and v.get(key) is not None])
                          if rep in reps else "-" for rep in (1, 2))
    wr = " / ".join(f"{sum(not v['right'] for v in reps[rep]['h3_b'].values())}/{len(reps[rep]['h3_b'])}" if rep in reps else "-"
                    for rep in (1, 2))
    print(f"| {c} | {col('ecg_b', 'own_leaf_events')} | {col('ecg_b', 'member_events')} | {col('ecg_b', 't')} | "
          f"{col('h3_b', 'own_leaf_events')} | {col('h3_b', 'took_part')} | {col('h3_b', 't')} | {wr} |")
print()

print("## Q2c. Groups: born mixed (members of > 1 leaf at birth), separated later, never separated\n")
print("| cell | h3 groups r1 / r2 | h3 born mixed | h3 mixed separated (median events) | h3 mixed never separated | "
      "h3 first group: stimulus, mixed r1 ; r2 | ECG nodes | ECG born mixed | ECG separated (median closes) | ECG first node: stimulus, mixed r1 ; r2 |")
print("|---|---|---|---|---|---|---|---|---|---|")
for c, reps in sorted(C2.items()):
    def gstat(src, rep):
        G = list(reps[rep][src].values()) if rep in reps else []
        mixed = [g for g in G if g["mixed"]]
        sep = [g["separated_after"] for g in mixed if g["separated_after"] is not None]
        first = min(G, key=lambda g: g["born"]) if G else None
        return len(G), len(mixed), (f(float(np.median(sep)), 1) + f" ({len(sep)})") if sep else "- (0)", len(mixed) - len(sep), \
            (f"{first['stim']}, {'mixed' if first['mixed'] else 'pure'}" if first else "-")
    h = {rep: gstat("h3_groups", rep) for rep in (1, 2)}
    e = {rep: gstat("ecg_groups", rep) for rep in (1, 2)}
    j = lambda D, i: " / ".join(str(D[rep][i]) for rep in (1, 2))   # noqa: E731
    print(f"| {c} | {j(h, 0)} | {j(h, 1)} | {j(h, 2)} | {j(h, 3)} | {h[1][4]} ; {h[2][4]} | {j(e, 0)} | {j(e, 1)} | {j(e, 2)} | {e[1][4]} ; {e[2][4]} |")
print()

print("## Q2d. h3 replayed offline with the other rep's stimulus order (same events, permuted)\n")
print("| cell | variant | last P / R / cov | per-close P (pooled) | groups (born mixed) | first membership event p50 | first memberships wrong | first ten stimulus cells |")
print("|---|---|---|---|---|---|---|---|")
for r in Q2D:
    for tag in ("rep1 as recorded", "rep1 events, rep2 order", "rep2 as recorded", "rep2 events, rep1 order"):
        x = r[tag]
        last = x["last"]
        lp = " / ".join(f(v) for v in last) if last else "-"
        print(f"| {r['cell'][3:]} | {tag} | {lp} | {f(x['pooled_P'])} | {x['groups']} ({x['mixed_at_birth']}) | "
              f"{f(x['first_member_ev_p50'], 1)} | {x['first_member_wrong']}/{x['n_first']} | {' > '.join(x['first10'])} |")
print()

# ── Q3 ──
print("## Q3. C13 L-LONG\n")
for r in Q2:
    if "q3" not in r:
        continue
    q = r["q3"]
    print(f"### {cell(r)} r{r['rep']}: ECG final P / R / cov {f(r['ecg_final']['precision'])} / {f(r['ecg_final']['recall'])} / "
          f"{f(r['ecg_final']['coverage'])}; h3 last {' / '.join(f(v) for v in r['h3_last']) if r['h3_last'] else '-'}\n")
    print("ECG final groups (node: members by leaf; born at close, stimulus; membership by close where it changed):\n")
    for g in q["ecg_final_groups"]:
        ch, prev = [], None
        for x, t, s, cnt in g["traj"]:
            if cnt != prev:
                ch.append(f"#{x} t{t} {s}: {cnt}")
                prev = cnt
        print(f"- node {g['node']} {'WRONG' if g['wrong'] else 'right'} {g['members']}; born #{g['born']} t{g['born_t']} ({g['born_stim']}); "
              + " → ".join(ch))
    print("\nh3 groups at the last close:\n")
    for g in q["h3_final_groups"]:
        ch, prev = [], None
        for x, t, s, cnt in g["traj"]:
            if cnt != prev:
                ch.append(f"#{x} t{t} {s}: {cnt}")
                prev = cnt
        print(f"- group {g['group']} {'WRONG' if g['wrong'] else 'right'} {g['members']}; born #{g['born']} ({g['class']}, parent "
              f"{g['parent']}, {g['born_stim']}) with {g['born_members']}; " + " → ".join(ch))
    print("\nStimulus windows:\n")
    print("| start | d s | cell | ECG events | onsets per expected client | onsets of other clients | ECG events with both leaves | event sizes |")
    print("|---|---|---|---|---|---|---|---|")
    for w in q["windows"]:
        print(f"| {w['start']:.1f} | {w['d']:g} | {w['cell']} | {w['ecg_events']} | {w['onsets_per_expected_client']} | "
              f"{w['onsets_other_clients']} | {w['events_both_leaves']} | {w['event_sizes']} |")
    if q["undecided"]:
        print("\nUndecided clients at the end (ECG): " + "; ".join(
            f"{u['client']} (leaf {u['leaf']}, L {u['L']}, node {u['node']}, onsets {u['onsets']}, events {u['events']}, "
            f"membership events {u['member_events']})" for u in q["undecided"]))
    print()

# ── Q4 ──
P4 = HERE / "rows4.jsonl"
if P4.exists():
    R4 = sorted((json.loads(x) for x in open(P4) if x.strip() and '"error"' not in x[:200]), key=lambda r: r["run"])
    C4 = defaultdict(dict)
    for r in R4:
        C4[r["cell"]][r["rep"]] = r
    print("## Q4. fq_codel under the per-flow truth\n")
    print("Part 4 scored these rows against the static same-leaf truth (ECG pairwise: same_access(truth_leaf); h3: pairs_leaf; "
          "strict per-event: gt1 = the egress's summed backlog). Per-flow truth here: per ECG event, the clients behind the "
          "stimulated egress whose own sub-queue has a queue-log episode (gt1 CoDel rule) overlapping [t0 - 1, t0 + 2]; a pair is "
          "the same when co-constrained in >= half of the events in which either was constrained (M); never-constrained clients "
          "are correct when left out (their pairs count only if grouped). Rep 1 / rep 2.\n")
    print("| cell | clients ever constrained | ECG P / R / cov same-leaf | ECG P / R / cov per-flow | h3 P / R / cov same-leaf | "
          "h3 P / R / cov per-flow | ECG memberships: wrong same-leaf / per-flow | h3 memberships: wrong same-leaf / per-flow |")
    print("|---|---|---|---|---|---|---|---|")
    trip = lambda x: "-" if not x else (" / ".join(f(v) for v in x) if isinstance(x, (list, tuple)) else  # noqa: E731
                                        " / ".join(f(x.get(k)) for k in (("precision", "recall", "coverage") if "precision" in x else ("P", "R", "cov"))))
    for c, reps in C4.items():
        g = lambda key: " ; ".join(trip(reps[p].get(key)) if p in reps else "-" for p in (1, 2))   # noqa: E731
        mm = lambda m: " ; ".join(f"{reps[p][m]['declared']}: {reps[p][m]['wrong_leaf']} / {reps[p][m]['wrong_flow']}" if p in reps else "-"  # noqa: E731
                                  for p in (1, 2))
        ev = " / ".join(f"{len(reps[p]['ever_constrained'])} of {reps[p]['n_clients']}" if p in reps else "-" for p in (1, 2))
        print(f"| {c} | {ev} | {g('ecg_leaf')} | {g('ecg_flow')} | {g('h3_leaf')} | {g('h3_flow')} | {mm('ecg_mem')} | {mm('h3_mem')} |")
    print()
    print("Per event: clients behind the stimulated egress that were constrained (generous / strict >= half), and ECG members "
          "that were constrained. Medians over the events with a stimulus; share of events by count constrained.\n")
    print("| cell | rep | events | behind | constrained p50 (strict p50) | events with 0 / 1 / 2 / 3 / all constrained | "
          "ECG members p50 | members constrained share |")
    print("|---|---|---|---|---|---|---|---|")
    for c, reps in C4.items():
        for p in (1, 2):
            if p not in reps:
                continue
            E = [e for e in reps[p]["events"] if e["targets"]]
            if not E:
                continue
            bh = Counter(e["behind"] for e in E).most_common(1)[0][0]
            dist = Counter(min(e["constrained"], 3) if e["constrained"] < e["behind"] else "all" for e in E)
            sh = sum(e["members_constrained"] for e in E) / max(1, sum(e["ecg_members"] for e in E))
            print(f"| {c} | {p} | {len(E)} | {bh} | {f(float(np.median([e['constrained'] for e in E])), 1)} "
                  f"({f(float(np.median([e['constrained_strict'] for e in E])), 1)}) | "
                  f"{' / '.join(str(dist.get(k, 0)) for k in (0, 1, 2, 3, 'all'))} | {f(float(np.median([e['ecg_members'] for e in E])), 1)} | {f(sh)} |")
    print()
    print("By stimulus cell (all reps): median constrained / behind\n")
    print("| cell | stimulus | events r1 / r2 | constrained / behind p50 r1 / r2 |")
    print("|---|---|---|---|")
    for c, reps in C4.items():
        cells = sorted({e["cell"] for p in reps for e in reps[p]["events"] if e["targets"]})
        for sc in cells:
            v = []
            for p in (1, 2):
                E = [e for e in reps.get(p, {}).get("events", []) if e["cell"] == sc and e["targets"]]
                v.append((len(E), f"{f(float(np.median([e['constrained'] for e in E])), 1)} / {E[0]['behind']}" if E else "-"))
            print(f"| {c} | {sc} | {v[0][0]} / {v[1][0]} | {v[0][1]} ; {v[1][1]} |")
    print()
