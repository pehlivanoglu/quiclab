#!/usr/bin/env python3
"""Tables of Step 7 from a-rows.jsonl and b-rows.jsonl (reps side by side, nothing averaged).

    .venv/bin/python3 reports/step7-2026-11-14/summarize7.py > reports/step7-2026-11-14/step7-summary.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def rows(name):
    return [json.loads(x) for x in open(HERE / name) if x.strip()]


def f2(x, f=".2f"):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else format(x, f)


def shr(j):
    p = (j or [{}])[0] if isinstance(j, list) else j
    return p


def share(pairs):
    w = pairs.get("wrong", 0)
    return f"{f2(pairs.get('shared', 0) / w) if w else '-'} ({w})"


def cfg(r):
    return (r["campaign"], r["type"], r["aqm"], r["phase"])


def rep_key(r):
    return (r["folder"], r["rep"])


def main():
    A = rows("a-rows.jsonl")
    B = rows("b-rows.jsonl")
    by = defaultdict(list)
    for r in A:
        by[cfg(r)].append(r)
    for v in by.values():
        v.sort(key=lambda r: r["rep"])
    print("# Step 7 tables\n")

    # ── A: headline per run
    print("## Part A: per run\n")
    print("| scenario | AQM | phase | rep | h3 last P / R / cov | h3 pooled P | h3 memberships: n / wrong decl / wrong close | "
          "h3 wrong pairs shared: generous (n) | strict | ECG final P / R / cov, tree | ECG wrong pairs shared: generous | strict | "
          "B1 own O-- / OX- / --U | topology truth (G0): ECG / h3 right-wrong |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    order = ["M1", "K1", "C1", "K6", "K6R", "M6", "G0", "J1"]
    for key_ in sorted(by, key=lambda c: (order.index(c[0]) if c[0] in order else 99, c[1], c[2], c[3])):
        for r in by[key_]:
            h = r.get("h3") or {}
            e = r["ecg"]
            b1 = r.get("b1") or {}
            o = lambda t: f"{f2(b1[t][1] / b1[t][0])}" if t in b1 and b1[t][0] else "-"
            topo = ""
            if r["campaign"] == "G0":
                topo = f"{e['topo']['right']}-{e['topo']['wrong']} / " + (f"{h['topo']['right']}-{h['topo']['wrong']}" if h.get("topo") else "-")
            last = h.get("last")
            print(f"| {r['campaign']} {r['type']} | {r['aqm']} | {r['phase']} | {r['rep']} | "
                  + (f"{f2(last[0])} / {f2(last[1])} / {f2(last[2])}" if last else "-")
                  + f" | {f2(h.get('pooled_P'))} | " + ("/".join(str(x) for x in h["mem"]) if h.get("mem") else "-")
                  + f" | {share(h['gen'][0]) if h else '-'} | {share(h['strict'][0]) if h else '-'} | "
                  f"{f2(e['final']['precision'])} / {f2(e['final']['recall'])} / {f2(e['final']['coverage'])}, {'ok' if e['tree'] else 'no'} | "
                  f"{share(e['gen'][0])} | {share(e['strict'][0])} | {o('O--')} / {o('OX-')} / {o('--U')} | {topo} |")
    print()

    # ── A: keyframe queues
    print("## Part A: keyframe queues (calm time)\n")
    print("Peak p50 after a synchronized keyframe; model = load x 4/33 s; paced model = model - median keyframe transmit "
          "time of the run; spike = time with delay >= 5 ms in [T, T + 0.5 s] (p50); drops per keyframe window.\n")
    print("| scenario | AQM | phase | rep | egress | load | model / paced model ms | peak p50 / p90 ms | spike p50 ms | drops per keyframe; share of keyframes with drops |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for key_ in sorted(by, key=lambda c: (order.index(c[0]) if c[0] in order else 99, c[1], c[2], c[3])):
        for r in by[key_]:
            it = r.get("item4")
            if not it or "queues" not in it:
                continue
            tx = it.get("transmit_p50_median_ms") or 0
            for hname, q in sorted(it["queues"].items()):
                if not q["load"] or q["load"] < 0.2:
                    continue
                if hname in r["leaf_hops"] and r["campaign"] not in ("M1",):
                    continue   # leaves below a shared queue: see the rows file
                p = q["peak_ms"]
                print(f"| {r['campaign']} | {r['aqm']} | {r['phase']} | {r['rep']} | {hname} | {f2(q['load'])} | "
                      f"{f2(q['model_ms'], '.0f')} / {f2(max(q['model_ms'] - tx, 0), '.0f')} | {p[0]:.1f} / {p[1]:.1f} | "
                      f"{q.get('spike_ms', [None])[0] if q.get('spike_ms') else '-'} | {q.get('drops_per_keyframe')}; {q.get('keyframes_with_drops')} |")
    print()

    # ── A: congestion share of upstream/root in ECG events
    print("## Part A: upstream / root congested share of ECG events (generous ; strict)\n")
    for key_ in sorted(by, key=lambda c: (order.index(c[0]) if c[0] in order else 99, c[1], c[2], c[3])):
        if key_[0] not in ("K1", "C1", "K6", "K6R", "J1", "M6"):
            continue
        cells = []
        for r in by[key_]:
            up = [h for h in r["ecg"]["hot_share_gen"] if h not in r["leaf_hops"] and r["ecg"]["hot_share_gen"][h] > 0.02]
            cells.append(f"r{r['rep']}: " + ", ".join(f"{h} {f2(r['ecg']['hot_share_gen'][h])} ; {f2(r['ecg']['hot_share_strict'][h])}" for h in up))
        print(f"- {key_[0]} {key_[1]} {key_[2]} {key_[3]}: " + " | ".join(cells))
    print()

    # ── B1
    print("## Part B1: ECG final values across reps (configurations with >= 2 reps)\n")
    print("| scenario | AQM | phase | reps | truth leaves | coverage min-max | P min-max | R min-max | tree correct | sibling merge at end |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    bb = defaultdict(list)
    for r in B:
        bb[(r["campaign"], r["type"], r["aqm"], r["phase"])].append(r)
    multi = {k: v for k, v in bb.items() if len(v) >= 2}
    for k in sorted(multi):
        v = multi[k]
        rng = lambda key_: (lambda xs: f"{f2(min(xs))}-{f2(max(xs))}" if xs else "-")(
            [x["final"][key_] for x in v if x["final"].get(key_) is not None])
        print(f"| {k[0]} {k[1]} | {k[2]} | {k[3]} | {len(v)} | {v[0]['n_truth_leaves']} | {rng('coverage')} | {rng('precision')} | "
              f"{rng('recall')} | {sum(bool(x['tree']) for x in v)}/{len(v)} | {sum(x['merge_end'] for x in v)}/{len(v)} |")
    print()

    # ── B2
    print("## Part B2: inside a run (configurations with >= 2 reps, multi-leaf)\n")
    print("| scenario | AQM | phase | rep | closes | coverage min / median / max over the second half | share of closes with the correct leaf partition | memberships lost / regained |")
    print("|---|---|---|---|---|---|---|---|")
    for k in sorted(multi):
        if multi[k][0]["n_truth_leaves"] < 2:
            continue
        for r in sorted(multi[k], key=lambda x: (x["folder"], x["rep"])):
            ct = r["cov_t"][len(r["cov_t"]) // 2:] or [None]
            ok = [x for x in ct if x is not None]
            print(f"| {k[0]} {k[1]} | {k[2]} | {k[3]} | {r['rep']} | {r['events']} | "
                  + (f"{min(ok):.2f} / {np.median(ok):.2f} / {max(ok):.2f}" if ok else "-")
                  + f" | {f2(np.mean(r['correct_t']) if r['correct_t'] else None)} | {r['loss']} / {r['regain']} |")
    print()

    # ── B3
    print("## Part B3: memberships that end below A\n")
    agg = defaultdict(lambda: [0, 0.0, 0, 0.0])
    n_end = 0
    for r in B:
        for f, x in r["drops"].items():
            n_end += 1
            for c, v in x["by_case"].items():
                for i in range(4):
                    agg[c][i] += v[i]
    print(f"{n_end} memberships (all runs of part B) were declared at some close and are below A at the end. Negative L "
          "steps by the case of the closing event (count, summed dL; of them with the flow in that event):\n")
    print("| case | negative steps | sum dL | steps with the flow in the event | their sum dL |\n|---|---|---|---|---|")
    for c, v in sorted(agg.items(), key=lambda x: x[1][1]):
        print(f"| {c} | {v[0]} | {v[1]:.1f} | {v[2]} | {v[3]:.1f} |")
    print("\nExamples (the runs of step 6):\n")
    for r in B:
        if (r["campaign"], r["type"], r["aqm"]) in (("C1", "burstlongsplit", "pfifo"), ("K6", "depth", "pfifo")) and r["drops"]:
            for f, x in list(r["drops"].items())[:3]:
                print(f"- {r['folder'][-10:]} {r['campaign']} r{r['rep']} {f}: L max {x['L_max']:.1f}, end {x['L_end']:.1f}; "
                      f"last 12 L {x['L_tail']}; cases {''.join(c[0] for c in x['cases_tail'])}")
    print("\nSibling merges (first close at which one ECG node holds clients of two truth leaves):\n")
    for r in B:
        if r["merge_end"] and r["merged_first"]:
            mf = r["merged_first"]
            after = Counter(r["cases"][mf["close"] + 1:])
            print(f"- {r['folder']} {r['campaign']} {r['type']} {r['aqm']} r{r['rep']}: close {mf['close']} (t {mf['t']}), "
                  f"case {mf['case']}, event members {mf['members']}, merged group {mf['group']}; later cases {dict(after)}")


if __name__ == "__main__":
    main()
