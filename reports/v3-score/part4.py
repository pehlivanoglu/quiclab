#!/usr/bin/env python3
"""Part 4: grouping, from grp-rows.jsonl (per run and onset source: step7.a_row, step7.b_row,
grouping_step5.step5_run, all unchanged) and the ECG outputs <run>/grouping-d150-<source>/metrics.json.
ECG v1.2 (delta 0.150 s) and h3 (step 4 replay, m = 3, ECG event intervals) with three onset sources:
v2-owd, v2-fixed-owd, truth. Reps side by side; `*` = reps differ by more than the largest rep difference of
the other cells of the block for that metric (>= 2 others): not reliable.

    .venv/bin/python3 reports/v3-score/part4.py .runs/2026-11-14_1818_v3 > reports/v3-score/part4.md

Per-close precision: pairs decided SAME at the closes that the same-leaf truth calls right / all decided
(step 6 judge_closes, pooled over closes). False memberships: memberships judged at declaration wrong by the
same-leaf truth; "strict per-event" = of those, the ones whose client shares no egress congested in that
event (strict rule of step 7: GT1 covers >= half of the interval) with half of the other members.
Coverage per close: share of decided pairs at each close (pairs_t), median over the second half of the run.
Events / seconds to membership: per flow that became a member, ECG's membership_events and the time from the
flow's first event to the first close with L >= A (M).
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))   # the grouping package (Config)
kdir = Path(sys.argv[1])
SRC = ("v2-owd", "v2-fixed-owd", "truth")
R = defaultdict(dict)          # (cell, source) -> rep -> row
for x in open(HERE / "grp-rows.jsonl"):
    r = json.loads(x)
    if "run" not in r:
        continue
    R[(r["run"].rsplit("-r", 1)[0][3:], r["source"])][int(r["run"].rsplit("-r", 1)[1])] = r
f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731
ratio = lambda a, b: a / b if b else math.nan   # noqa: E731


def to_member(rd: Path, src: str):
    m = json.loads((rd / f"grouping-d150-{src}" / "metrics.json").read_text())
    from grouping import Config
    A = Config.from_dict(m["config"]).A
    evs, out_e, out_s = m["events"], [], []
    for fl, ser in m["series"].items():
        first = next((e["t"] for e in evs if fl in e["members"]), None)
        t_mem = next((s_[0] for s_ in ser if s_[1] is not None and s_[2] is not None and s_[2] >= A), None)
        if first is not None and t_mem is not None:
            out_s.append(t_mem - first)
            out_e.append(m["membership_events"].get(fl))
    return out_e, out_s


def metrics(r, rd, src):
    a, b, s5 = r.get("a", {}), r.get("b", {}), r.get("s5", {})
    if "error" in a or "error" in b:
        return None
    e = a["ecg"]
    pairs_g, mem_g = e["gen"]
    pairs_s, mem_s = e["strict"]
    ct = b["cov_t"][len(b["cov_t"]) // 2:]
    out = {"ecg_P": e["final"]["precision"], "ecg_R": e["final"]["recall"], "ecg_cov": e["final"]["coverage"],
           "ecg_close_P": ratio(pairs_g.get("right", 0), pairs_g.get("right", 0) + pairs_g.get("wrong", 0)),
           "ecg_close_cov": float(np.median(ct)) if ct else math.nan, "tree": b["tree"], "merge": b["merge_end"],
           "correct_share": float(np.mean(b["correct_t"])) if b["correct_t"] else math.nan,
           "lost": b["loss"], "regained": b["regain"], "ecg_mem": mem_g.get("declared", 0),
           "ecg_mem_wrong": mem_g.get("wrong", 0), "ecg_mem_wrong_strict": mem_s.get("wrong", 0) - mem_s.get("shared", 0),
           "events": e["events"], "n_leaves": b["n_truth_leaves"]}
    h = a.get("h3")
    if h:
        out.update(h3_P=h["last"][0] if h["last"] else math.nan, h3_R=h["last"][1] if h["last"] else math.nan,
                   h3_cov=h["last"][2] if h["last"] else math.nan, h3_close_P=h["pooled_P"],
                   h3_mem=h["mem"][0], h3_mem_wrong=h["mem"][1],
                   h3_mem_wrong_strict=h["strict"][1].get("wrong", 0) - h["strict"][1].get("shared", 0))
    b1 = a.get("b1") or {}
    out["b1"] = b1
    G = s5.get("B2_groups") or {}
    one = [v for v in s5.get("B2") or [] if G.get(str(v[1])) and not G[str(v[1])]["life_mixed"]]
    out["b2_one_n"], out["b2_one_own"] = len(one), sum(v[3] for v in one)
    try:
        ev, sec = to_member(rd, src)
        out["mem_events"] = float(np.median([x for x in ev if x is not None])) if ev else math.nan
        out["mem_sec"] = float(np.median(sec)) if sec else math.nan
    except Exception:   # noqa: BLE001
        out["mem_events"] = out["mem_sec"] = math.nan
    return out


M = {}
for (cell, src), reps in R.items():
    M[(cell, src)] = {rep: metrics(r, kdir / r["run"], src) for rep, r in reps.items()}
    M[(cell, src)] = {k: v for k, v in M[(cell, src)].items() if v}

BLOCK_ORDER = ["C7", "C8", "C9", "C10", "C11", "C12", "C13", "M6", "M7", "M8", "C2"]
cells = sorted({c for c, _ in M}, key=lambda c: (BLOCK_ORDER.index(c.split("-")[0]), c))


def flags(src, key):
    by = defaultdict(dict)
    for c in cells:
        m = M.get((c, src), {})
        if 1 in m and 2 in m and m[1].get(key) is not None and m[2].get(key) is not None:
            a, b = float(m[1][key]), float(m[2][key])
            if not (math.isnan(a) or math.isnan(b)):
                by[c.split("-")[0]][c] = abs(a - b)
    out = set()
    for dd in by.values():
        for c, v in dd.items():
            o = [x for k, x in dd.items() if k != c]
            if len(o) >= 2 and v > max(o) + 1e-12:
                out.add(c)
    return out


def two(c, src, key, k=2, fl=None):
    m = M.get((c, src), {})
    s = " / ".join(("-" if rep not in m or m[rep].get(key) is None else
                    (f(float(m[rep][key]), k) if not isinstance(m[rep][key], bool) else ("yes" if m[rep][key] else "no")))
                   for rep in (1, 2))
    return s + ("*" if fl and c in fl else "")


print("# Part 4: grouping (ECG v1.2 and h3, three onset sources)\n")
print("Cells: H-HIER C7 (s 0.30) and C8 (s 0.65), H-DEPTH C9, H-INDEP C10, H-UNEVEN C11, A-MIXED C12, L-LONG C13; "
      "microbenchmarks M6 (staggered phases, T-BASE), M7 (noroot), M8 (mixab); C2 pfifo = the default single-leaf point "
      "next to M6. Every value: rep 1 / rep 2.\n")
for src in SRC:
    print(f"## 4a / 4b. Onset source {src}\n")
    fl = {k: flags(src, k) for k in ("ecg_P", "ecg_R", "ecg_cov", "h3_close_P", "h3_P", "correct_share")}
    print("| cell | ECG final P | ECG final R | ECG final cov | ECG per-close P | ECG per-close cov (2nd half) | tree correct | "
          "siblings merged | closes with correct tree | memberships lost / regained | h3 last P / R / cov r1 | h3 last P / R / cov r2 | "
          "h3 per-close P | ECG events |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        m = M.get((c, src), {})
        lr = " / ".join(f"{m[r]['lost']}-{m[r]['regained']}" if r in m else "-" for r in (1, 2))
        h3 = lambda r: f"{f(m[r].get('h3_P'))} / {f(m[r].get('h3_R'))} / {f(m[r].get('h3_cov'))}" if r in m else "-"   # noqa: E731
        print(f"| {c} | {two(c, src, 'ecg_P', fl=fl['ecg_P'])} | {two(c, src, 'ecg_R', fl=fl['ecg_R'])} | "
              f"{two(c, src, 'ecg_cov', fl=fl['ecg_cov'])} | {two(c, src, 'ecg_close_P')} | {two(c, src, 'ecg_close_cov')} | "
              f"{two(c, src, 'tree')} | {two(c, src, 'merge')} | {two(c, src, 'correct_share', fl=fl['correct_share'])} | {lr} | "
              f"{h3(1)} | {h3(2)} | {two(c, src, 'h3_close_P', fl=fl['h3_close_P'])} | {two(c, src, 'events', 0)} |")
    print()
    print(f"False memberships and time to membership ({src}):\n")
    print("| cell | ECG memberships | ECG wrong (same-leaf) | ECG wrong (strict per-event) | h3 memberships | h3 wrong (same-leaf) | "
          "h3 wrong (strict per-event) | events to membership p50 | seconds to membership p50 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        print(f"| {c} | {two(c, src, 'ecg_mem', 0)} | {two(c, src, 'ecg_mem_wrong', 0)} | {two(c, src, 'ecg_mem_wrong_strict', 0)} | "
              f"{two(c, src, 'h3_mem', 0)} | {two(c, src, 'h3_mem_wrong', 0)} | {two(c, src, 'h3_mem_wrong_strict', 0)} | "
              f"{two(c, src, 'mem_events', 1)} | {two(c, src, 'mem_sec', 1)} |")
    print()

print("## 4c. Step 5 votes (v2-owd onsets)\n")
print("B1 own-vote rate by event type (step 5 types: O = own leaf egress congested, X = the other leaf's, U = a shared "
      "upstream; '-' = not), pooled over the cell's runs per rep: rate (votes).\n")
types = sorted({t for (c, s), m in M.items() if s == "v2-owd" for r in m.values() for t in r["b1"]})
print("| cell | " + " | ".join(types) + " | B2 own rate in one-leaf groups (votes) |")
print("|---|" + "---|" * len(types) + "---|")
for c in cells:
    m = M.get((c, "v2-owd"), {})
    cellv = []
    for t in types:
        cellv.append(" / ".join(f"{f(ratio(m[r]['b1'][t][1], m[r]['b1'][t][0]))} ({m[r]['b1'][t][0]})" if r in m and t in m[r]["b1"] else "-"
                                for r in (1, 2)))
    b2 = " / ".join(f"{f(ratio(m[r]['b2_one_own'], m[r]['b2_one_n']))} ({m[r]['b2_one_n']})" if r in m else "-" for r in (1, 2))
    print(f"| {c} | " + " | ".join(cellv) + f" | {b2} |")
