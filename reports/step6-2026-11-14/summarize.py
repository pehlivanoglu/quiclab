#!/usr/bin/env python3
"""Tables of Step 6 from step6-rows.jsonl (every rep in its own row; nothing pooled across reps).

    .venv/bin/python3 reports/step6-2026-11-14/summarize.py reports/step6-2026-11-14/step6-rows.jsonl > .../step6-summary.md
"""

from __future__ import annotations

import json
import sys
from collections import Counter

import numpy as np

ORDER = ["G0", "M1", "K1", "C1", "K6"]
NAME = {"G0": "base calm065", "M1": "base burstcap", "K1": "K1 hier", "C1": "C1 burstlongsplit", "K6": "K6 depth"}


def f2(x, f=".2f"):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else format(x, f)


def share(a, n):
    return f"{a}/{n} ({f2(a / n if n else None)})"


def key(r):
    return (ORDER.index(r["campaign"]), r["phase"] != "sync", r["rep"])


def main(path):
    R = sorted((json.loads(x) for x in open(path) if x.strip()), key=key)
    print("# Step 6 tables\n")
    print("Every row is one run. sync = phase 0 for all clients; stag = staggered phases. Pair counts are "
          "pair-closes (a wrong pair counted at every close at which it is decided SAME).\n")

    print("## Headline per run\n")
    print("| scenario | phase | rep | ECG final P / R / cov, tree | ECG events; GLOBAL share | h3 final P / R / cov; pooled P | "
          "ECG wrong pair-closes shared in that event | h3 wrong pair-closes shared |")
    print("|---|---|---|---|---|---|---|---|")
    for r in R:
        e = r["ecg_final"]
        c = r["ecg_cases"]
        n = r["ecg_events"]
        h = r.get("h3_final")
        hp = r.get("h3_pairs") or {}
        ep = r["ecg_pairs"]
        print(f"| {NAME[r['campaign']]} | {r['phase']} | {r['rep']} | {f2(e['precision'])} / {f2(e['recall'])} / {f2(e['coverage'])}, "
              f"{'ok' if e['tree_correct'] else 'no'} | {n}; {f2(c.get('GLOBAL', 0) / n if n else None)} | "
              + (f"{f2(h['last'][0])} / {f2(h['last'][1])} / {f2(h['last'][2])}; {f2(h['pooled_P'])}" if h else "-")
              + f" | {share(ep.get('shared', 0), ep.get('wrong', 0))} | "
              + (share(hp.get('shared', 0), hp.get('wrong', 0)) if h else "-") + " |")
    print()

    print("## Item 1: wrong by the same-leaf truth, shared in that event or not\n")
    print("| scenario | phase | rep | ECG pair-closes: wrong / shared / not shared | ECG memberships: declared / wrong / shared / not | "
          "h3 pair-closes: wrong / shared / not | h3 memberships: declared / wrong / shared / not |")
    print("|---|---|---|---|---|---|---|")
    for r in R:
        if r["campaign"] == "G0":
            continue
        ep, em = r["ecg_pairs"], r["ecg_mem"]
        hp, hm = r.get("h3_pairs") or {}, r.get("h3_mem") or {}
        g = lambda x, k: x.get(k, 0)
        print(f"| {NAME[r['campaign']]} | {r['phase']} | {r['rep']} | {g(ep, 'wrong')} / {g(ep, 'shared')} / {g(ep, 'not shared')} | "
              f"{g(em, 'declared')} / {g(em, 'wrong')} / {g(em, 'shared')} / {g(em, 'not shared')} | "
              f"{g(hp, 'wrong')} / {g(hp, 'shared')} / {g(hp, 'not shared')} | "
              f"{g(hm, 'declared')} / {g(hm, 'wrong')} / {g(hm, 'shared')} / {g(hm, 'not shared')} |")
    print()

    print("## Item 2: ECG events by case\n")
    print("| scenario | phase | rep | events | A | B | C | D | SOLO | GLOBAL | GLOBAL with upstream/root congested | "
          "members per event p50 | upstream / root congested share of events | final coverage; members at the end |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in R:
        c, n = r["ecg_cases"], r["ecg_events"]
        cb = r["ecg_case_by_hot"]
        up = {h: v for h, v in r["ecg_hot_share"].items() if h not in r["leaf_hops"] and v}
        mp = r["ecg_members_per_event"]
        print(f"| {NAME[r['campaign']]} | {r['phase']} | {r['rep']} | {n} | " + " | ".join(
            f"{f2(c.get(x, 0) / n if n else None)}" for x in ("A", "B", "C", "D", "SOLO", "GLOBAL"))
              + f" | {cb.get('GLOBAL|upstream/root hot', 0)}/{c.get('GLOBAL', 0)} | {f2(np.median(mp) if mp else None, '.0f')} | "
              + ", ".join(f"{h} {f2(v)}" for h, v in sorted(up.items())) + f" | {f2(r['ecg_final']['coverage'])}; "
              f"{len(r['ecg_final']['members'])} |")
    print()
    print("Coverage over ECG closes (every 10th close):\n")
    for r in R:
        if r["campaign"] in ("C1", "K6") and r["ecg_coverage_t"]:
            ct = r["ecg_coverage_t"]
            print(f"- {NAME[r['campaign']]} {r['phase']} r{r['rep']}: " + " ".join(f2(x) for x in ct[::10]) + f" | last {f2(ct[-1])}")
    print()

    print("## Item 3: subtracting the common component (sync K1, C1, K6)\n")
    print("Per event: congested = not class 0 after the Part 1 procedure; leaf truth = participants whose leaf egress "
          "has a GT1 episode in the event. P / R = congested vs leaf truth over all events; exact = share of events "
          "where the two sets are equal.\n")
    print("| scenario | rep | before: congested p50 / leaf truth p50, P / R, exact | after: congested p50, P / R, exact | "
          "B1 own before: O-- / OX- / --U (votes) | B1 own after: O-- / OX- / --U (votes) |")
    print("|---|---|---|---|---|---|")
    for r in R:
        it = r.get("item3")
        if not it:
            continue
        cells = []
        for tag in ("before", "after"):
            ms = it["match"][tag]
            tp, cg, tr = sum(x["tp"] for x in ms), sum(x["cong"] for x in ms), sum(x["truth"] for x in ms)
            cells.append(f"{f2(np.median([x['cong'] for x in ms]), '.0f')}"
                         + (f" / {f2(np.median([x['truth'] for x in ms]), '.0f')}" if tag == "before" else "")
                         + f", {f2(tp / cg if cg else None)} / {f2(tp / tr if tr else None)}, {f2(np.mean([x['exact'] for x in ms]))}")
        for tag in ("before", "after"):
            c = {}
            for vote, _, t in it["b1"][tag]:
                c.setdefault(t, [0, 0])
                c[t][0] += 1
                c[t][1] += vote
            cells.append(" / ".join(f"{f2(c[t][1] / c[t][0]) if t in c else '-'} ({c.get(t, [0])[0]})" for t in ("O--", "OX-", "--U")))
        print(f"| {NAME[r['campaign']]} | {r['rep']} | " + " | ".join(cells) + " |")
    print()

    print("## Item 4: keyframe queue peaks (calm time)\n")
    print("Peak = maximum egress queueing delay in [T, T + 0.5 s] after each keyframe time T; model = load x 4/33 s.\n")
    print("| scenario | phase | rep | egress | load | model ms | peak p50 / p90 / max ms | peak / model (p50) | sample ms |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in R:
        it = r.get("item4")
        if not it:
            continue
        for h, q in sorted(it["queues"].items()):
            if not q["load"] or q["load"] < 0.1:
                continue
            p = q["peak_ms"]
            print(f"| {NAME[r['campaign']]} | {r['phase']} | {r['rep']} | {h} | {f2(q['load'])} | {f2(q['model_ms'], '.0f')} | "
                  f"{p[0]:.1f} / {p[1]:.1f} / {p[2]:.1f} | {f2(p[0] / q['model_ms'] if q['model_ms'] else None)} | {q['sample_ms']} |")
    print("\nKeyframe hand-over (sync r1 of each scenario): keyframe size, transmit time from the first packet after "
          "the write until its bytes have left (p50 / p90), pacing rate p50:\n")
    for r in R:
        it = r.get("item4")
        if it and r["phase"] == "sync" and r["rep"] == 1:
            print(f"- {NAME[r['campaign']]}: " + "; ".join(
                f"{s} {v['rate_kbps']} kb/s, {f2(v['keyframe_bytes_p50'] / 1000 if v['keyframe_bytes_p50'] else None, '.1f')} kB, "
                f"{v['transmit_ms'][0] if v['transmit_ms'] else '-'} / {v['transmit_ms'][1] if v['transmit_ms'] else '-'} ms, "
                f"{v['pacing_mbps_p50']} Mb/s" for s, v in sorted(it["handover"].items())))


if __name__ == "__main__":
    main(sys.argv[1])
