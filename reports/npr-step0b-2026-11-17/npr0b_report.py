"""NPR STEP 0b tables (npr0b.py rows.jsonl). STEP 0's per-leaf view (npr0_report.per_event) on each candidate's
events. Single-queue and fq_codel / cake cells apart; reps side by side."""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "npr-step0-2026-11-17"))
import npr0_report as N   # noqa: E402

CANDS = ("E0", "E1-0.5", "E1-1", "E1-2", "E2", "E3", "E4-1", "E4-2")
CONSTANTS = {"E2": 0, "E3": 0, "E1-0.5": 1, "E1-1": 1, "E1-2": 1, "E4-1": 1, "E4-2": 1, "E0": 2}
ORDER = ("E2", "E3", "E1-0.5", "E1-1", "E1-2", "E4-1", "E4-2")   # the note's tie-break: E2 / E3, then smaller W
MAJ_ON, SIB_MIN = 0.02, 0.30   # (P) the note's selection rule
f_ = N.f_


def view(r, c):
    return {"truth": r["truth"], "events": r["cands"][c], "aqm": r["aqm"], "rep": r["rep"], "type": r["type"],
            "campaign": r["campaign"]}


def stats(rows):
    """Pooled majority errors, m, f, rho and the middle-band share over the given candidate views."""
    on_n = on_e = off_n = off_e = 0
    miss = nn_on = inc = nn_off = 0
    num = den = d2 = 0.0
    mid = mid_n = 0
    for r in rows:
        per_leaf = defaultdict(list)
        for n, info, i, on, kind, k, nn, x in N.per_event(r):
            if nn == 0:
                continue
            if on:
                on_n += 1
                on_e += k < nn / 2
                miss += nn - k
                nn_on += nn
                if nn >= 2:
                    per_leaf[n].append((k, nn))
            else:
                off_n += 1
                off_e += k >= nn / 2
                inc += k
                nn_off += nn
            if k >= 1:
                mid_n += 1
                mid += N.MID[0] <= k / nn <= N.MID[1]
        for ev in per_leaf.values():
            K, M = sum(e[0] for e in ev), sum(e[1] for e in ev)
            p = K / M
            num += sum((e[0] - e[1] * p) ** 2 for e in ev)
            if 0 < p < 1:
                den += sum(e[1] * p * (1 - p) for e in ev)
                d2 += sum(e[1] * (e[1] - 1) * p * (1 - p) for e in ev)
    return {"on_n": on_n, "on_err": on_e / on_n if on_n else None, "off_n": off_n,
            "off_err": off_e / off_n if off_n else None, "m": miss / nn_on if nn_on else None,
            "f": inc / nn_off if nn_off else None, "rho": (num - den) / d2 if d2 else None,
            "mid": mid / mid_n if mid_n else None}


def sibling(rows):
    tot = one = 0
    for r in rows:
        L = N.leaf_views(r)
        names = sorted(L)
        pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if L[a]["anc"] == L[b]["anc"]]
        if not pairs:
            continue
        ons = defaultdict(dict)
        for n, info, i, on, kind, k, nn, x in N.per_event(r):
            ons[i][n] = on
        for a, b in pairs:
            for i in ons:
                if ons[i][a] or ons[i][b]:
                    tot += 1
                    one += ons[i][a] != ons[i][b]
    return one / tot if tot else None, tot


def selection(R):
    print("## Selection (single-queue cells, r1 / r2)\n")
    print(f"Rule (P): majority-vote error on truly congested leaves <= {MAJ_ON}; exactly-one-sibling share >= "
          f"{SIB_MIN}; false-inclusion (off) error not above E0's. Pooled over leaf sizes.\n")
    print("| candidate | on error | off error | exactly one sibling on | m | f | rho | k/n in [0.25, 0.75] | pass |")
    print("|---|---|---|---|---|---|---|---|---|")
    res = {}
    base = {}
    for c in CANDS:
        v = {rep: stats([view(r, c) for r in R if r["rep"] == rep and N.cls(r) == "single"]) for rep in (1, 2)}
        s = {rep: sibling([view(r, c) for r in R if r["rep"] == rep and N.cls(r) == "single"])[0] for rep in (1, 2)}
        if c == "E0":
            base = v
        ok = all(v[rep]["on_err"] is not None and v[rep]["on_err"] <= MAJ_ON and s[rep] is not None and
                 s[rep] >= SIB_MIN and v[rep]["off_err"] <= base[rep]["off_err"] + 1e-12 for rep in (1, 2))
        res[c] = ok and c != "E0"
        cell = lambda key, d=3: " / ".join(f_(v[rep][key], d) for rep in (1, 2))   # noqa: E731
        print(f"| {c} | {cell('on_err')} | {cell('off_err')} | {' / '.join(f_(s[rep], 3) for rep in (1, 2))} | "
              f"{cell('m')} | {cell('f', 4)} | {cell('rho')} | {cell('mid')} | {'PASS' if res[c] else ('-' if c == 'E0' else 'fail')} |")
    passed = [c for c in ORDER if res.get(c)]
    print(f"\nPassing: {passed or 'none'}. Selected (fewest constants, E2 / E3 first, then smaller W): "
          f"**{passed[0] if passed else 'none'}**.\n")
    return passed


def by_size(R, cl):
    print(f"## 0b.1 By leaf size ({'single-queue' if cl == 'single' else 'fq_codel / cake'} cells; r1 / r2)\n")
    print("| candidate | leaf size | on events | on error | off error | m | f | rho | k/n in [0.25, 0.75] |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in CANDS:
        sizes = sorted({len(v["members"]) for r in R if N.cls(r) == cl for v in r["truth"].values() if v["level"] == "leaf"})
        for s in sizes:
            v = {}
            for rep in (1, 2):
                rows = []
                for r in R:
                    if r["rep"] != rep or N.cls(r) != cl:
                        continue
                    vr = view(r, c)
                    vr["truth"] = {n: x for n, x in r["truth"].items() if x["level"] != "leaf" or len(x["members"]) == s}
                    rows.append(vr)
                v[rep] = stats(rows)
            if not (v[1]["on_n"] or v[2]["on_n"]):
                continue
            cell = lambda key, d=3: " / ".join(f_(v[rep][key], d) for rep in (1, 2))   # noqa: E731
            print(f"| {c} | {s} | {v[1]['on_n']} / {v[2]['on_n']} | {cell('on_err')} | {cell('off_err')} | {cell('m')} | "
                  f"{cell('f', 4)} | {cell('rho')} | {cell('mid')} |")
    print()


def shape(R):
    print("## 0b.2 Event shape, 0b.3 cost of merging, 0b.5 latency (single-queue cells, pooled reps)\n")
    print("Events per flow-minute = member-events / (clients x run minutes). Duration and latency from the first "
          "onset's aligned time t0: close (member set final), last join (aligned), last arrival (when the last "
          "member's alarm reached the sender). Absorbs = frozen E0 events with t0 inside [t0, close].\n")
    print("| candidate | events | events / flow-min | members p50 / p90 | duration (close - t0) p50 / p90 / max s | "
          "absorbs p50 / p90 / max | mixed events | exactly one sibling on | last join - t0 p50 / p90 | "
          "last arrival - t0 p50 / p90 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for c in CANDS:
        ev = [(r, e) for r in R if N.cls(r) == "single" for e in r["cands"][c]]
        fm = sum(len(r["clients"]) * r["duration"] / 60 for r in R if N.cls(r) == "single")
        mem = [len(e["ones"]) for _, e in ev]
        dur = [e["close"] - e["t0"] for _, e in ev]
        ab = [e["absorbs"] for _, e in ev if "absorbs" in e]
        lj = [e["last_join"] - e["t0"] for _, e in ev]
        la = [e["last_arr"] - e["t0"] for _, e in ev]
        q = lambda a, p: f"{np.percentile(a, p):.2f}" if a else "-"   # noqa: E731
        sib, _ = sibling([view(r, c) for r in R if N.cls(r) == "single"])
        print(f"| {c} | {len(ev)} | {sum(mem) / fm:.3f} | {q(mem, 50)} / {q(mem, 90)} | {q(dur, 50)} / {q(dur, 90)} / "
              f"{max(dur):.1f} | " + (f"{q(ab, 50)} / {q(ab, 90)} / {max(ab)}" if ab else "-") +
              f" | {np.mean([e['mixed'] for _, e in ev]):.3f} | {f_(sib, 3)} | {q(lj, 50)} / {q(lj, 90)} | "
              f"{q(la, 50)} / {q(la, 90)} |")
    print()
    print("fq_codel / cake cells, same columns:\n")
    print("| candidate | on error r1 / r2 | off error r1 / r2 | m | rho | mixed events | exactly one sibling on |")
    print("|---|---|---|---|---|---|---|")
    for c in CANDS:
        v = {rep: stats([view(r, c) for r in R if r["rep"] == rep and N.cls(r) == "fq"]) for rep in (1, 2)}
        ev = [e for r in R if N.cls(r) == "fq" for e in r["cands"][c]]
        sib, _ = sibling([view(r, c) for r in R if N.cls(r) == "fq"])
        cell = lambda key, d=3: " / ".join(f_(v[rep][key], d) for rep in (1, 2))   # noqa: E731
        print(f"| {c} | {cell('on_err')} | {cell('off_err')} | {cell('m')} | {cell('rho')} | "
              f"{np.mean([e['mixed'] for e in ev]):.3f} | {f_(sib, 3)} |")
    print()


def probe(R):
    P = [p for r in R for p in r.get("probe", [])]
    print(f"## 0b.4 T-BASE: truth off, all four members have an onset ({len(P)} E0 events)\n")
    if not P:
        print("None.\n")
        return
    ph = [x for p in P for x in p["phase_s"] if x == x]
    al = np.mean([0 <= x <= 0.2 for x in ph])
    print(f"All {len(P)}: GT1 strict cover p50 {np.median([p['gt1_strict_cover'] for p in P]):.2f} (strict-hot needs "
          f">= 0.5); with any GT1 episode within [t0 - 0.5, t0 + 1.5]: {np.mean([bool(p['gt1_episodes']) for p in P]):.2f}; "
          f"GT3 episode for >= 1 member: {np.mean([p['gt3_clients'] > 0 for p in P]):.2f}; GT-Q episode: "
          f"{np.mean([p['gtq_episodes'] > 0 for p in P]):.2f}, harmful 600: {np.mean([p['gtq_harmful_600'] > 0 for p in P]):.2f}; "
          f"F1 max p50 {np.nanmedian([x for p in P for x in p['f1_max_ms']]):.1f} ms; onset within 0-200 ms after a "
          f"keyframe: {al:.2f}.\n")
    rnd = random.Random(1)
    S = rnd.sample(P, min(20, len(P)))
    print("Sample of 20 (seed 1):\n")
    print("| run | t0 | GT1 strict cover | GT1 episodes near | GT3 members | GT-Q episodes (max sojourn ms, harmful) | "
          "F1 max per member ms | onset phase after keyframe s |")
    print("|---|---|---|---|---|---|---|---|")
    for p in sorted(S, key=lambda p: (p["run"], p["t0"])):
        print(f"| {p['run'][3:]} | {p['t0']} | {p['gt1_strict_cover']} | {p['gt1_episodes'][:2]} | {p['gt3_clients']} | "
              f"{p['gtq_episodes']} ({f_(p['gtq_max_sojourn_ms'], 1)}, {p['gtq_harmful_600']}) | {p['f1_max_ms']} | "
              f"{p['phase_s']} |")
    print()


def report(path: Path) -> None:
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    print("# NPR STEP 0b tables (npr0b_report.py)\n")
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    selection2(R)
    print("## Selection under the original rule (for the record)\n")
    selection(R)
    shape(R)
    probe(R)
    by_size(R, "single")
    by_size(R, "fq")


# ---------------------------------------------------------------- re-specified selection (user, 2026-11-17)

MAJ_ON2, FI_TOL = 0.02, 0.005   # (P) the user's re-specified rule


def stats2(rows):
    """Condition 1 with "truly congested" = strict-hot (or an ancestor) OR at least half of the leaf's onsets in the
    event are gtq_score true positives; condition 3 = mean per-event share of members whose alarm start is a gtq_score
    false positive (events of runs with usable GT-Q)."""
    on_n = on_e = 0
    fi = []
    for r in rows:
        L = N.leaf_views(r)
        for e in r["events"]:
            q = e.get("q")
            if q is not None and e["ones"]:
                fi.append(sum(q.get(c) == "fp" for c in e["ones"]) / len(e["ones"]))
            H = set(e["hot"])
            ones = set(e["ones"])
            for n, info in L.items():
                x = {c: 1 if c in ones else ("NA" if c in e["na"] else 0) for c in info["members"]}
                nn = sum(v in (0, 1) for v in x.values())
                k = sum(v == 1 for v in x.values())
                if nn == 0:
                    continue
                hot = n in H or any(a in H for a in info["anc"])
                tp = sum(1 for c in info["members"] if c in ones and q is not None and q.get(c) == "tp")
                if hot:   # condition 1 restored to strict-hot only (user, 2026-11-17); tp kept for the record
                    on_n += 1
                    on_e += k < nn / 2
    return {"on_n": on_n, "on_err": on_e / on_n if on_n else None,
            "fi": float(np.mean(fi)) if fi else None, "fi_n": len(fi)}


def gap_to_final(R, c):
    d = [e["close"] - e["t0"] for r in R if N.cls(r) == "single" for e in r["cands"][c]]
    return float(np.median(d)) if d else None


def selection2(R):
    print("## Selection, re-specified rule (single-queue cells, r1 / r2)\n")
    print(f"Condition 1: majority-vote error on strict-hot congested leaves <= {MAJ_ON2} (pre-set definition, restored). Condition 2: exactly-one-sibling "
          f"share >= {SIB_MIN} (strict-hot, unchanged). Condition 3: mean false-inclusion share (members whose alarm "
          f"start is a gtq_score false positive / members) not above E0's by more than {FI_TOL} in either rep. The old "
          f"strict-hot off error is shown for the record.\n")
    print("| candidate | on error (new) | false-inclusion share | events with GT-Q | sibling separation | old off error "
          "(strict-hot) | member set final p50 s | pass |")
    print("|---|---|---|---|---|---|---|---|")
    base, res = {}, {}
    for c in CANDS:
        v = {rep: stats2([view(r, c) for r in R if r["rep"] == rep and N.cls(r) == "single"]) for rep in (1, 2)}
        old = {rep: stats([view(r, c) for r in R if r["rep"] == rep and N.cls(r) == "single"]) for rep in (1, 2)}
        s = {rep: sibling([view(r, c) for r in R if r["rep"] == rep and N.cls(r) == "single"])[0] for rep in (1, 2)}
        if c == "E0":
            base = v
        ok = all(v[rep]["on_err"] is not None and v[rep]["on_err"] <= MAJ_ON2 and s[rep] is not None
                 and s[rep] >= SIB_MIN and v[rep]["fi"] <= base[rep]["fi"] + FI_TOL + 1e-12 for rep in (1, 2))
        res[c] = (ok and c != "E0", s)
        print(f"| {c} | {' / '.join(f_(v[rep]['on_err'], 3) for rep in (1, 2))} | "
              f"{' / '.join(f_(v[rep]['fi'], 4) for rep in (1, 2))} | {v[1]['fi_n']} / {v[2]['fi_n']} | "
              f"{' / '.join(f_(s[rep], 3) for rep in (1, 2))} | {' / '.join(f_(old[rep]['off_err'], 3) for rep in (1, 2))} | "
              f"{f_(gap_to_final(R, c), 2)} | {'PASS' if res[c][0] else ('reference' if c == 'E0' else 'fail')} |")
    passed = [c for c in CANDS if res[c][0]]
    tier = lambda c: 0 if c in ("E2", "E3") else 1   # noqa: E731
    pick = sorted(passed, key=lambda c: (tier(c), -min(res[c][1].values()) if tier(c) == 0 else 0, gap_to_final(R, c)))
    print(f"\nPassing: {passed or 'none'}. Selected (fewest constants; E2 vs E3 by sibling separation; then the shorter "
          f"time to a final member set): **{pick[0] if pick else 'none'}**.\n")
    return pick[0] if pick else None
