"""NPR STEP 1 / STEP 2 tables (step12.py rows.jsonl). Reps side by side; single-queue and fq_codel / cake apart."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

FQ = ("fq_codel", "cake")
PAIR_P_MIN = 0.93


def f_(x, d=3):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def methods_of(R):
    names = []
    for r in R:
        for m in r.get("methods", {}):
            if m not in names:
                names.append(m)
    key = lambda m: (0 if m.startswith("SETS@E0") else 1 if m.startswith("SETS@") else 2, m)   # noqa: E731
    return sorted(names, key=key)


def pooled(R, meth):
    ss = [r["methods"][meth] for r in R if meth in r.get("methods", {})]
    if not ss:
        return None
    leaf = [s["levels"]["leaf"] for s in ss if "leaf" in s["levels"]]
    p = np.sum([s["pairs"] for s in ss], axis=0)
    return {"P": float(np.mean([x[0] for x in leaf])) if leaf else None,
            "R": float(np.mean([x[1] for x in leaf])) if leaf else None,
            "F": float(np.mean([x[2] for x in leaf])) if leaf else None,
            "pP": p[0] / (p[0] + p[1]) if p[0] + p[1] else None, "pR": p[0] / (p[0] + p[2]) if p[0] + p[2] else None,
            "sp": float(np.mean([s["spur"] for s in ss])), "runs": len(ss)}


def times(R, meth):
    """Events and seconds (from the leaf's first own stimulus) to the first close with a correct group (the scorer's
    t_ok: leaf F1 >= F1_OK); leaves never grouped."""
    ev, sec, never = [], [], 0
    for r in R:
        s = r.get("methods", {}).get(meth)
        if not s:
            continue
        for name, (e, t) in s.get("t_ok", {}).items():
            ev.append(e)
            fs = r["first_stim"].get(name)
            if fs is not None:
                sec.append(t - fs)
        never += s.get("n_leaves", 0) - len(s.get("t_ok", {}))
    q = lambda a, p: float(np.percentile(a, p)) if a else None   # noqa: E731
    return {"ev50": q(ev, 50), "ev90": q(ev, 90), "s50": q(sec, 50), "s90": q(sec, 90), "never": never}


def main_table(R, title, sel):
    print(f"### {title}\n")
    print("| method | leaf P | leaf R | leaf F1 | pair P | pair R | spurious / close | first correct group: events "
          "p50 / p90, s from first stimulus p50 / p90 | leaves never | runs |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for m in methods_of(R):
        v = [pooled([r for r in R if sel(r) and r["rep"] == rep], m) for rep in (1, 2)]
        t = [times([r for r in R if sel(r) and r["rep"] == rep], m) for rep in (1, 2)]
        if not any(v):
            continue
        c = lambda k, d=3: " / ".join(f_(x[k], d) if x else "-" for x in v)   # noqa: E731
        tt = " ; ".join(f"{f_(x['ev50'], 0)} / {f_(x['ev90'], 0)}, {f_(x['s50'], 0)} / {f_(x['s90'], 0)}" for x in t)
        print(f"| {m} | {c('P')} | {c('R')} | {c('F')} | {c('pP')} | {c('pR')} | {c('sp', 2)} | {tt} | "
              f"{t[0]['never']} / {t[1]['never']} | {v[0]['runs'] if v[0] else 0} / {v[1]['runs'] if v[1] else 0} |")
    print()


def conditions(R):
    sq = lambda r: r["aqm"] not in FQ and r.get("methods")   # noqa: E731
    cand = next((m.split("@")[1].split(" ")[0] for m in methods_of(R) if m.startswith("SETS@") and "E0" not in m), "?")
    print("## Pre-set conditions (single-queue cells, r1 / r2)\n")
    print(f"pair precision >= {PAIR_P_MIN} in both reps; leaf F1 not below frozen SETS k = 2 on frozen events (SETS@E0 k2).\n")
    print("| method | pair P | leaf F1 | frozen SETS k2 leaf F1 | result |\n|---|---|---|---|---|")
    ref = [pooled([r for r in R if sq(r) and r["rep"] == rep], "SETS@E0 k2") for rep in (1, 2)]
    for m in methods_of(R):
        if not m.startswith("NPR"):
            continue
        v = [pooled([r for r in R if sq(r) and r["rep"] == rep], m) for rep in (1, 2)]
        ok = all(v[i] and v[i]["pP"] is not None and v[i]["pP"] >= PAIR_P_MIN and v[i]["F"] >= ref[i]["F"] - 1e-12
                 for i in (0, 1))
        print(f"| {m} | {' / '.join(f_(x['pP']) for x in v)} | {' / '.join(f_(x['F']) for x in v)} | "
              f"{' / '.join(f_(x['F']) for x in ref)} | {'PASS' if ok else 'fail'} |")
    print()


def split_by(R, key, title, meths):
    print(f"### {title} (single-queue, pooled reps): leaf F1 / pair P\n")
    groups = defaultdict(list)
    for r in R:
        if r["aqm"] in FQ or not r.get("methods"):
            continue
        groups[key(r)].append(r)
    print("| " + title + " | runs | " + " | ".join(meths) + " |")
    print("|---|---|" + "---|" * len(meths))
    for k in sorted(groups, key=str):
        cells = []
        for m in meths:
            v = pooled(groups[k], m)
            cells.append(f"{f_(v['F'], 2)} / {f_(v['pP'], 2)}" if v else "-")
        print(f"| {k} | {len(groups[k])} | " + " | ".join(cells) + " |")
    print()


def calibration(R):
    print("## STEP 2 calibration: share of single-leaf groups split at any read\n")
    print("Single-leaf runs (truth has one leaf) and every true leaf taken alone (its members, the events where one "
          "of them has 1). Original order; 20 random orders: mean share and min-max over the orders. Pass: share <= "
          "alpha.\n")
    print("| set | alpha | leaves | split, original order | 20 orders: mean (min-max) | pass |")
    print("|---|---|---|---|---|---|")
    for name, sel in (("single-leaf runs, single-queue", lambda c, r: c["whole_run"] and r["aqm"] not in FQ),
                      ("every leaf alone, single-queue", lambda c, r: r["aqm"] not in FQ),
                      ("every leaf alone, fq / cake", lambda c, r: r["aqm"] in FQ)):
        for a in (0.05, 0.01, 0.1):
            orig = [c[f"split_{a}"] for r in R for c in r.get("calibration", []) if c["perm"] == 0 and sel(c, r)]
            per = []
            for p in range(1, 21):
                v = [c[f"split_{a}"] for r in R for c in r.get("calibration", []) if c["perm"] == p and sel(c, r)]
                if v:
                    per.append(np.mean(v))
            if not orig:
                continue
            sh = float(np.mean(orig))
            print(f"| {name} | {a} | {len(orig)} | {sh:.3f} | {np.mean(per):.3f} ({min(per):.3f}-{max(per):.3f}) | "
                  f"{'yes' if sh <= a else 'no'} |")
    print()


def long_events(R):
    print("## Long events (single-queue cells)\n")
    print("| rep | events | longer than 5 s | true leaves per long event p50 / p90 / max | long events with >= 2 leaves |")
    print("|---|---|---|---|---|")
    for rep in (1, 2):
        rs = [r for r in R if r["aqm"] not in FQ and r["rep"] == rep]
        d = [x for r in rs for x in r.get("durations", [])]
        lv = [x for r in rs for x in r.get("long_leaves", [])]
        if not d:
            continue
        q = lambda p: f"{np.percentile(lv, p):.0f}" if lv else "-"   # noqa: E731
        print(f"| r{rep} | {len(d)} | {np.mean(np.array(d) > 5.0):.3f} | {q(50)} / {q(90)} / {max(lv) if lv else '-'} | "
              f"{np.mean(np.array(lv) >= 2):.3f} |" if lv else f"| r{rep} | {len(d)} | 0.000 | - | - |")
    print()


def read_time(R):
    print("## Read time (seconds per read, all runs)\n")
    print("| variant | reads | p50 | p90 | max |\n|---|---|---|---|---|")
    for v in ("bin", "bb", "na0"):
        x = [t for r in R for t in r.get("read_s", {}).get(v, [])]
        if x:
            print(f"| {v} | {len(x)} | {np.percentile(x, 50):.4f} | {np.percentile(x, 90):.4f} | {max(x):.3f} |")
    print()


def report(path: Path) -> None:
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    print("# NPR STEP 1 / STEP 2 tables (step12_report.py)\n")
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    conditions(R)
    print("## STEP 1 scores (common scorer, same closes)\n")
    main_table(R, "Single-queue cells", lambda r: r["aqm"] not in FQ and r.get("methods"))
    main_table(R, "fq_codel / cake cells (same-link truth)", lambda r: r["aqm"] in FQ and r.get("methods"))
    meths = [m for m in methods_of(R) if m.endswith("k2") or m.endswith("a0.05")]
    split_by(R, lambda r: r["block"], "block", meths)
    split_by(R, lambda r: r["aqm"], "AQM", meths)
    split_by(R, lambda r: max(r["leaf_sizes"]) if r["leaf_sizes"] else 0, "largest leaf size", meths)
    long_events(R)
    calibration(R)
    read_time(R)
