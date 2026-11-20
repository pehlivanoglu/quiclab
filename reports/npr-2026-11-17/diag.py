#!/usr/bin/env python3
"""Diagnosis of the corrected test's loss of power (user, 2026-11-18), E1-0.5, single-queue cells.

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/diag.py > reports/npr-2026-11-17/diag.md

Item 1 (from rows-v2-E1-0.5.jsonl, no recomputation): pair precision and leaf F1 by the number of true leaves in the
run (2, 3, >= 4) and by whether the run stimulates a shared upstream link (a non-leaf truth set with a stimulus).
Item 4: the first test (rows-E1-0.5.jsonl) on the same runs next to the corrected one: false-split share, pair P.
Item 2 (targeted replay, only the runs with a merged pair): for every pair of true leaves that the corrected test
leaves inside one reported leaf group at the end of the run (alpha 0.05, V-bin):
  - log E trajectory of the oracle split that separates them (leaf A's members against the rest of the group,
    the alternative fitted on past events exactly as the test does, but with this fixed split), and of the split the
    test proposed at the top of that group;
  - the null's fitted (pi, m0, f0) for the group at the end;
  - per event: log P1 (oracle split, past fit), log P0 (null MLE at the end), the true state (which leaves were on);
  - how many of the group's events have exactly one of the two merged leaves on.
Item 3 inputs: the same oracle split with the null fitted on past events only (predictive, not in-sample): if that
E reaches 1 / alpha where the in-sample one does not, the in-sample null explains the loss (b); if the oracle E stays
low with the predictive null too while the group holds >= 3 leaves, the two-leaf alternative is the problem (a).
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "scripts"), str(ROOT)]
import npr      # noqa: E402
import step12   # noqa: E402

FQ = ("fq_codel", "cake")
ALPHA = 0.05


def leaves_of(row):
    return {n: set(v["members"]) for n, v in row["truth"].items() if v["level"] == "leaf"}


def upstream_stimulated(row, stim):
    T = {n: set(v["members"]) for n, v in row["truth"].items()}
    L = leaves_of(row)
    return any(stim.get(n) is not None and n not in L and len([l for l in L.values() if l <= T[n]]) >= 2 for n in T)


def item1(rows_new, rows_old):
    import step12_report as S
    out = ["## 1. Corrected test by the number of true leaves and a stimulated shared upstream (single-queue, r1 / r2)\n",
           "| group | runs | leaf F1 corrected | pair P corrected | pair P first test | leaf F1 first test |",
           "|---|---|---|---|---|---|"]
    old = {r["run"]: r for r in rows_old}
    keys = defaultdict(list)
    for r in rows_new:
        if r["aqm"] in FQ or not r.get("methods"):
            continue
        n = len(leaves_of(r))
        nk = "2 leaves" if n == 2 else "3 leaves" if n == 3 else "1 leaf" if n == 1 else ">= 4 leaves"
        up = "shared upstream stimulated" if upstream_stimulated(r, r["first_stim"]) else "no stimulated shared upstream"
        keys[(nk, "all")].append(r)
        keys[(nk, up)].append(r)
    for k in sorted(keys):
        rs = keys[k]
        v = [S.pooled([r for r in rs if r["rep"] == rep], "NPR-bin a0.05") for rep in (1, 2)]
        o = [S.pooled([old[r["run"]] for r in rs if r["rep"] == rep and r["run"] in old], "NPR-bin a0.05") for rep in (1, 2)]
        f = lambda x, key: S.f_(x[key]) if x else "-"   # noqa: E731
        out.append(f"| {k[0]}, {k[1]} | {len(rs)} | {' / '.join(f(x, 'F') for x in v)} | {' / '.join(f(x, 'pP') for x in v)} | "
                   f"{' / '.join(f(x, 'pP') for x in o)} | {' / '.join(f(x, 'F') for x in o)} |")
    return "\n".join(out) + "\n"


def item4(rows_new, rows_old):
    import step12_report as S
    runs = {r["run"] for r in rows_new}
    old = [r for r in rows_old if r["run"] in runs]
    out = ["## 4. Both ends of the trade-off (same runs, single-queue, r1 / r2)\n",
           "| test | alpha | false-split share (single-leaf runs / every leaf alone) | pair P | leaf F1 | pair R |",
           "|---|---|---|---|---|---|"]
    for lab, R in (("first", old), ("corrected", rows_new)):
        for a in ("0.05", "0.01", "0.1"):
            m = f"NPR-bin a{a}"
            v = [S.pooled([r for r in R if r["aqm"] not in FQ and r.get("methods") and r["rep"] == rep], m) for rep in (1, 2)]
            cal = []
            for whole in (True, None):
                x = [c[f"split_{a}"] for r in R for c in r.get("calibration", []) if c["perm"] == 0 and r["aqm"] not in FQ
                     and (whole is None or c["whole_run"])]
                cal.append(f"{np.mean(x):.3f}" if x else "-")
            out.append(f"| {lab} | {a} | {' / '.join(cal)} | {' / '.join(S.f_(x['pP']) for x in v)} | "
                       f"{' / '.join(S.f_(x['F']) for x in v)} | {' / '.join(S.f_(x['pR']) for x in v)} |")
    return "\n".join(out) + "\n"


def lp_vec(k, n, on, m, f):
    return npr._lp_on(k, n, m) if on else npr._lp_off(k, n, f)


def alt_factor_fixed(pre, split, xe):
    """log P1(x_e) with a FIXED split, pi_s / m1 / f1 fitted on the prefix as the test does."""
    m1, f1 = npr.half_rates(pre, (split, ~split))
    pis = npr.pi_states(pre[split], pre[~split])
    kn = []
    for msk in (split, ~split):
        x = xe[msk]
        kn.append((float(np.nansum(x)), float(np.sum(~np.isnan(x)))))
    terms = []
    for (s1, s2), w in pis.items():
        t = math.log(w)
        for (k, n), s in zip(kn, (s1, s2)):
            if n:
                t += lp_vec(k, n, s, m1, f1)
        terms.append(t)
    return float(logsumexp(terms))


def null_lp(k, n, params):
    pi, m, f = params
    return float(np.logaddexp(math.log(pi) + npr._lp_on(k, n, m), math.log1p(-pi) + npr._lp_off(k, n, f)))


def trajectory(X, split):
    """Per event of the group (non-empty): log P1 (fixed split, past fit), log P0 in-sample at each t (MLE on 1..t)
    and predictive (MLE on 1..t-1); returns lists and the log E trajectories."""
    cols = [j for j in range(X.shape[1]) if (~np.isnan(X[:, j])).any()]
    lp1, lp0_pred, ks, ns, logE_in, logE_pred = [], [], [], [], [], []
    num = 0.0
    den_pred = 0.0
    for i, j in enumerate(cols):
        xe = X[:, j]
        k, n = float(np.nansum(xe)), float(np.sum(~np.isnan(xe)))
        if i == 0:
            ks.append(k), ns.append(n), lp1.append(None), lp0_pred.append(None)
            continue
        pre = X[:, cols[:i]]
        a = alt_factor_fixed(pre, split, xe)
        _, prm, _ = npr.em_null(np.array(ks[1:] or [k]), np.array(ns[1:] or [n])) if len(ks) > 1 else (None, None, None)
        p0p = null_lp(k, n, prm) if prm else a           # predictive null (past fit); first factor neutral
        num += a
        den_pred += p0p
        ks.append(k), ns.append(n), lp1.append(a), lp0_pred.append(p0p)
        ll0, _, _ = npr.em_null(np.array(ks[1:]), np.array(ns[1:]))
        logE_in.append(num - ll0)
        logE_pred.append(num - den_pred)
    return cols, lp1, lp0_pred, logE_in, logE_pred


def item2(rows_new, src):
    out = ["## 2. Pairs of true leaves left merged by the corrected test (alpha 0.05, V-bin, end of run)\n"]
    summary = []
    for r in rows_new:
        if r["aqm"] in FQ or not r.get("final"):
            continue
        L = leaves_of(r)
        groups = [set(g) for g in r["final"]["bin"]["0.05"]]
        reported_leaves = [g for g in groups if not any(h < g for h in groups)]   # smallest groups
        for g in reported_leaves:
            inside = [n for n, mem in L.items() if len(mem & g) >= max(1, len(mem) / 2)]
            if len(inside) < 2:
                continue
            row = src[r["run"]]
            ev = [e for e in row["cands"]["E1-0.5"] if e["ones"]]
            members = sorted(g)
            X = np.array([step12.matrix_col(e, members) for e in ev]).T
            Ln = {n: L[n] & g for n in inside}
            ons = []
            for e in ev:
                H = set(e["hot"])
                anc = {n: [a for a, v in row["truth"].items() if a != n and L[n] < set(v["members"])] for n in inside}
                ons.append({n: (n in H or any(a in H for a in anc[n])) for n in inside})
            # null at the end
            cols = [j for j in range(X.shape[1]) if (~np.isnan(X[:, j])).any()]
            kk = np.array([np.nansum(X[:, j]) for j in cols[1:]])
            nn = np.array([np.sum(~np.isnan(X[:, j])) for j in cols[1:]])
            ll0, prm, si = npr.em_null(kk, nn) if len(kk) else (None, None, None)
            # proposed top split of the group at the end
            prop = npr.propose(X[:, cols])
            res_prop = trajectory(X, prop[0]) if prop is not None else None
            for a_i, A in enumerate(inside):
                for B in inside[a_i + 1:]:
                    split = np.array([c in Ln[A] for c in members])
                    c_, lp1, lp0p, logE_in, logE_pred = trajectory(X, split)
                    one = sum(1 for j in cols if ons[j][A] != ons[j][B])
                    both = sum(1 for j in cols if ons[j][A] and ons[j][B])
                    rec = {"run": r["run"], "rep": r["rep"], "aqm": r["aqm"], "n_leaves_run": len(L),
                           "leaves_in_group": len(inside), "pair": (A, B), "group_size": len(members),
                           "events": len(cols), "exactly_one_on": one, "both_on": both,
                           "logE_oracle_insample_end": logE_in[-1] if logE_in else None,
                           "logE_oracle_insample_max": max(logE_in) if logE_in else None,
                           "logE_oracle_predictive_end": logE_pred[-1] if logE_pred else None,
                           "logE_proposed_insample_end": res_prop[3][-1] if res_prop and res_prop[3] else None,
                           "logE_proposed_insample_max": max(res_prop[3]) if res_prop and res_prop[3] else None,
                           "null_end": {"pi": prm[0], "m0": prm[1], "f0": prm[2], "start": si} if prm else None,
                           "traj_oracle_insample": [round(x, 2) for x in logE_in],
                           "traj_oracle_predictive": [round(x, 2) for x in logE_pred],
                           "traj_proposed_insample": [round(x, 2) for x in res_prop[3]] if res_prop else None,
                           "per_event": [{"t0": ev[j]["t0"], "logP1_oracle": None if lp1[i] is None else round(lp1[i], 2),
                                          "logP0_predictive": None if lp0p[i] is None else round(lp0p[i], 2),
                                          "logP0_end_fit": round(null_lp(float(np.nansum(X[:, j])),
                                                                          float(np.sum(~np.isnan(X[:, j]))), prm), 2) if prm else None,
                                          "on": [n for n in inside if ons[j][n]]} for i, j in enumerate(cols)]}
                    summary.append(rec)
    (HERE / "diag-merged-pairs.json").write_text(json.dumps(summary, indent=1, default=str))
    thr = math.log(1 / ALPHA)
    out.append(f"{len(summary)} merged pairs (detail per event in [diag-merged-pairs.json](diag-merged-pairs.json)). "
               f"log(1 / alpha) = {thr:.2f}.\n")
    out.append("| leaves in the merged group | pairs | events with exactly one of the two on, p50 | oracle split log E "
               "end, in-sample null p50 / share >= threshold | oracle split log E end, predictive null p50 / share | "
               "proposed split log E end, in-sample p50 | null m0 / f0 p50 |")
    out.append("|---|---|---|---|---|---|---|")
    for key, sel in (("2", lambda s: s["leaves_in_group"] == 2), (">= 3", lambda s: s["leaves_in_group"] >= 3)):
        xs = [s for s in summary if sel(s)]
        if not xs:
            continue
        med = lambda a: float(np.median([v for v in a if v is not None])) if any(v is not None for v in a) else float("nan")   # noqa: E731
        sh = lambda a: np.mean([v is not None and v >= thr for v in a])   # noqa: E731
        oi = [s["logE_oracle_insample_end"] for s in xs]
        op = [s["logE_oracle_predictive_end"] for s in xs]
        pp = [s["logE_proposed_insample_end"] for s in xs]
        out.append(f"| {key} | {len(xs)} | {med([s['exactly_one_on'] for s in xs]):.0f} | {med(oi):.1f} / {sh(oi):.2f} | "
                   f"{med(op):.1f} / {sh(op):.2f} | {med(pp):.1f} | "
                   f"{med([s['null_end']['m0'] if s['null_end'] else None for s in xs]):.3f} / "
                   f"{med([s['null_end']['f0'] if s['null_end'] else None for s in xs]):.3f} |")
    return "\n".join(out) + "\n"


def main():
    new = [json.loads(x) for x in open(HERE / "rows-v2-E1-0.5.jsonl")]
    new = [r for r in new if "error" not in r]
    old = [json.loads(x) for x in open(HERE / "rows-E1-0.5.jsonl")]
    old = [r for r in old if "error" not in r]
    src = {}
    for line in open(ROOT / "reports/npr-step0b-2026-11-17/rows.jsonl"):
        r = json.loads(line)
        if "error" not in r:
            src[r["run"]] = r
    print("# Diagnosis of the corrected test's loss of power (E1-0.5)\n")
    for r in new + old:            # step12 rows carry no truth: take it from the 0b rows (same runs)
        if r["run"] in src:
            r["truth"] = src[r["run"]]["truth"]
    print(item4(new, old))
    print(item1(new, old))
    print(item2(new, src))


if __name__ == "__main__":
    main()
