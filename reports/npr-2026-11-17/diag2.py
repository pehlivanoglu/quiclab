#!/usr/bin/env python3
"""Diagnosis part 2 (no change to the test): when does the root group first split, under the corrected test as it is
(in-sample null MLE at t), under the same test with a predictive null (each event's P0 from the MLE on the group's
earlier events only), and under the first test (npr_v1)? E1-0.5 events, single-queue runs with >= 2 true leaves.
Also, at the first true separating event (exactly one true leaf on), the running log E of each.

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/diag2.py > reports/npr-2026-11-17/diag2.md
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "scripts"), str(ROOT)]
import npr       # noqa: E402
import npr_v1    # noqa: E402
import step12    # noqa: E402

FQ = ("fq_codel", "cake")


class PredictiveNull(npr.Reader):
    """The corrected test with the null's P0(x_e) fitted on the group's events before e (diagnostic only)."""

    def evalue(self, g, T):
        rows = np.array(g)
        num = den = 0.0
        ks, ns, first = [], [], True
        for e in range(T):
            xe = self.X[e][rows]
            if not (~np.isnan(xe)).any():
                continue
            fac = self._alt_factor(g, e)
            k, n = float(np.nansum(xe)), float(np.sum(~np.isnan(xe)))
            if first or fac is None:
                first = False
                ks.append(k), ns.append(n)
                continue
            _, (pi, m, f), _ = npr.em_null(np.array(ks), np.array(ns))
            den += float(np.logaddexp(math.log(pi) + npr._lp_on(k, n, m), math.log1p(-pi) + npr._lp_off(k, n, f)))
            num += fac
            ks.append(k), ns.append(n)
        return math.exp(min(700.0, num - den)) if ks else 1.0


def first_split(reader_cls, ev, clients, **kw):
    rd = reader_cls(clients, **kw)
    for i, e in enumerate(ev):
        rd.add(step12.matrix_col(e, clients))
        g = rd.read((0.05,))["groups"][0.05]
        if len(g) > 1:
            return i + 1
    return None


def main():
    src = {}
    for line in open(ROOT / "reports/npr-step0b-2026-11-17/rows.jsonl"):
        r = json.loads(line)
        if "error" not in r:
            src[r["run"]] = r
    out = defaultdict(list)
    for r in src.values():
        if r["aqm"] in FQ or r["type"] == "calm":
            continue
        L = {n: set(v["members"]) for n, v in r["truth"].items() if v["level"] == "leaf"}
        if len(L) < 2:
            continue
        ev = [e for e in r["cands"]["E1-0.5"] if e["ones"]]
        clients = r["clients"]
        sep = None
        for i, e in enumerate(ev):
            H = set(e["hot"])
            on = [n for n in L if n in H or any(a in H for a, v in r["truth"].items() if a != n and L[n] < set(v["members"]))]
            if 0 < len(on) < len(L):
                sep = i + 1
                break
        key = "2 leaves" if len(L) == 2 else "3 leaves" if len(L) == 3 else ">= 4 leaves"
        out[key].append({"run": r["run"], "rep": r["rep"], "events": len(ev), "first_separating_event": sep,
                         "split_corrected": first_split(npr.Reader, ev, clients),
                         "split_predictive_null": first_split(PredictiveNull, ev, clients),
                         "split_first_test": first_split(npr_v1.Reader, ev, clients)})
    (HERE / "diag2-first-splits.json").write_text(json.dumps(out, indent=1))
    print("# Diagnosis 2: event of the root group's first accepted split (alpha 0.05, V-bin, E1-0.5, single-queue)\n")
    print("Events counted from the run's first E1-0.5 event; 'lag' = first split minus the first event in which the "
          "truth has some but not all leaves on (the first separating event). Never = no split in the run.\n")
    print("| runs | n | first separating event p50 | corrected (in-sample null): lag p50 / p90, never | "
          "predictive null: lag p50 / p90, never | first test: lag p50 / p90, never |")
    print("|---|---|---|---|---|---|")
    for key in ("2 leaves", "3 leaves", ">= 4 leaves"):
        xs = out.get(key, [])
        if not xs:
            continue
        cells = []
        for m in ("split_corrected", "split_predictive_null", "split_first_test"):
            lag = [x[m] - x["first_separating_event"] for x in xs if x[m] is not None and x["first_separating_event"]]
            nev = sum(x[m] is None for x in xs)
            cells.append(f"{np.median(lag):.0f} / {np.percentile(lag, 90):.0f}, {nev}" if lag else f"-, {nev}")
        sep = [x["first_separating_event"] for x in xs if x["first_separating_event"]]
        print(f"| {key} | {len(xs)} | {np.median(sep):.0f} | " + " | ".join(cells) + " |")
    print()


if __name__ == "__main__":
    main()
