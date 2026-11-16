#!/usr/bin/env python3
"""Per-scenario tables: synchronized mini campaign (r1, r2) next to the staggered run of the
same scenario (.runs/2026-11-10_1946_v2, r1 only). Reads the rows written by the existing,
unchanged scripts (baseline_scores ecg / detector, grouping_step4 run-f, grouping_step5 run,
grouping_step2 calm) and raw_signals.py. Step 5 helpers are imported, not changed.

    .venv/bin/python3 reports/sync-mini-2026-11-14/compare.py > reports/sync-mini-2026-11-14/compare.md
"""

from __future__ import annotations

import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grouping_step5 as s5  # noqa: E402

SYNC = ROOT / ".runs" / "2026-11-13_2238_grp-sync"
SCEN = [("G0", "calm065", "base calm065"), ("M1", "burstcap", "base burstcap"), ("K1", "hier", "K1 hier"),
        ("C1", "burstlongsplit", "C1 burstlongsplit"), ("K6", "depth", "K6 depth")]
OLD = {"ecg": ROOT / "reports/baselines-2026-11-12/ecg-rows.jsonl.gz",
       "det": ROOT / "reports/baselines-2026-11-12/detector-rows.jsonl.gz",
       "s4f": ROOT / "reports/grouping-step4/step4f-rows.jsonl.gz",
       "s5": ROOT / "reports/grouping-step5/step5-rows.jsonl.gz",
       "calm": ROOT / "reports/grouping-step2/calm-rows.jsonl.gz",
       "raw": HERE / "raw-stag.jsonl"}
NEW = {"ecg": HERE / "ecg-rows.jsonl.gz", "det": HERE / "detector-rows.jsonl.gz", "s4f": HERE / "step4f-rows.jsonl.gz",
       "s5": HERE / "step5-rows.jsonl.gz", "calm": HERE / "calm-rows.jsonl.gz", "raw": HERE / "raw-sync.jsonl"}
EPS_FIXED = (0.05, 0.10, 0.20)


def rows(p: Path):
    if not p.exists():
        return []
    op = gzip.open if p.suffix == ".gz" else open
    with op(p, "rt") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def pick(rs, camp, typ, reps):
    want = {f"grp-{typ}-pfifo-r{r}" for r in reps}
    return {r["run"][-2:]: r for r in rs if r.get("campaign") == camp and r.get("run") in want}


def f2(x, f=".2f"):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else format(x, f)


def det_cell(r):
    s = r["score"].get("v2-owd (OWD)", {}).get("GT1")
    if not s or "episodes" not in s:
        return "-"
    rec = s["detected"] / s["episodes"] if s["episodes"] else None
    prec = s["tp"] / (s["tp"] + s["fp"]) if s["tp"] + s["fp"] else None
    fa = s["fp"] / (s["clear_s"] / 60) if s["clear_s"] else None
    lat = np.median(s["latency"]) * 1000 if s.get("latency") else None
    return f"R {f2(rec)} P {f2(prec)} FA/min {f2(fa)} lat {f2(lat, '.0f')} ms"


def ecg_cell(r):
    e = r["ecg"]
    if "error" in e:
        return "error"
    me = list((e.get("membership_events") or {}).values())
    return (f"P {f2(e.get('precision'))} R {f2(e.get('recall'))} cov {f2(e.get('coverage'))} fp {e.get('fp')} "
            f"tree {'ok' if e.get('tree_correct') else 'no'} mem-ev {f2(np.median(me) if me else None, '.0f')}")


def h3_cell(r):
    x = r["ecg"]["h3"]
    last = s5.s4.prf(Counter(x["closes"][-1])) if x["closes"] else (None,) * 3
    pooled = s5.s4.prf(s5.s4.pooled(x["closes"]))
    ms = x["memberships"]
    dec = sum(not m["right"] for m in ms)
    clo = sum(m["mixed_closes"] > 0 for m in ms)
    one = [g for g in x["groups"].values() if not g["life_mixed"]]
    tested = [g for g in one if g.get("tested")]
    fs = [g for g in one if "split_at" in g]
    return (f"last P/R/cov {f2(last[0])}/{f2(last[1])}/{f2(last[2])}, closes P {f2(pooled[0])}, false memb decl/close "
            f"{dec}/{clo} of {len(ms)}, one-leaf false splits {len(fs)}/{len(tested)} tested")


def b_stats(rs):
    """B1 by gt1 type, eps; B2 one-leaf: own rate, members outside [0.3, 0.7], within-event all-own vs 0.5^n."""
    b1 = defaultdict(lambda: [0, 0])
    for r in rs:
        for v in r["B1"]:
            b1[v[5]][0] += 1
            b1[v[5]][1] += v[3]
    n12 = b1["O--"][0] + b1["OX-"][0]
    eps = 1 - (b1["O--"][1] + b1["OX-"][1]) / n12 if n12 else None
    own = n = 0
    mem = defaultdict(lambda: [0, 0])
    ev = defaultdict(list)
    for r in rs:
        G = r["B2_groups"]
        for v in r["B2"]:
            g = G.get(str(v[1]))
            if not g or g["life_mixed"]:
                continue
            n += 1
            own += v[3]
            mem[(r["run"], v[1], v[2])][0] += 1
            mem[(r["run"], v[1], v[2])][1] += v[3]
            ev[(r["run"], v[1], v[0])].append(v[3])
    rates = [b / a for a, b in mem.values() if a >= 10]
    ev2 = [x for x in ev.values() if len(x) >= 2]
    return {"b1": dict(b1), "eps": eps, "b2_votes": n, "b2_own": own / n if n else None,
            "outside": (np.mean([(x < 0.3 or x > 0.7) for x in rates]), len(rates)) if rates else (None, 0),
            "allown": (sum(all(x) for x in ev2), sum(0.5 ** len(x) for x in ev2), len(ev2))}


def b3(rs, eps):
    out = Counter()
    for r in rs:
        per = defaultdict(lambda: defaultdict(list))
        for v in r["B2"]:
            per[str(v[1])][v[0]].append(v[3])
        for k, g in r["B2_groups"].items():
            if k in per and not g["life_mixed"]:
                res, _ = s5.sprt(per[k], r["b"], eps)
                out[res] += 1
    return out


def b_line(st, rs, eps_list):
    b1 = st["b1"]
    t = lambda k: f"{f2(b1[k][1] / b1[k][0]) if k in b1 and b1[k][0] else '-'} ({b1.get(k, [0])[0]})"
    s = f"B1 own O-- {t('O--')}, OX- {t('OX-')}, --U {t('--U')}; eps {f2(st['eps'], '.4f')}"
    if st["b2_votes"]:
        o, nm = st["outside"]
        a, e, n = st["allown"]
        s += (f" | B2 one-leaf own {f2(st['b2_own'])} ({st['b2_votes']} votes), members outside [0.3,0.7] "
              f"{f2(o)} (n {nm}; fair 0.10), all-own events {a}/{n} vs 0.5^n {f2(e, '.1f')}")
        s += " | B3 one-leaf (one/two/undecided): " + "; ".join(
            f"eps {lab} {c['one queue']}/{c['two queues']}/{c['undecided']}"
            for lab, c in ((lab, b3(rs, e_)) for lab, e_ in eps_list))
    return s


def main():
    old = {k: rows(p) for k, p in OLD.items()}
    new = {k: rows(p) for k, p in NEW.items()}
    eps_here = b_stats([r for r in new["s5"]])["eps"]
    eps_list = ([("here " + f2(eps_here, ".4f"), eps_here)] if eps_here else []) + [(f"{e:g}", e) for e in EPS_FIXED]
    print("# Synchronized keyframes, mini campaign: per-scenario comparison\n")
    print(f"sync = `.runs/2026-11-13_2238_grp-sync` (pfifo, phase 0 for all, r1 + r2); stag = `.runs/2026-11-10_1946_v2` "
          f"(staggered phases, r1 only). ECG event intervals for Step 4 / 5. eps measured here (B1 O-- / OX-, all sync "
          f"runs) = {f2(eps_here, '.4f')}.\n")
    for camp, typ, lab in SCEN:
        print(f"## {lab}\n")
        print("| | " + " | ".join(("stag r1", "sync r1", "sync r2")) + " |\n|---|---|---|---|")
        cols = [("stag", old, (1,)), ("sync", new, (1, 2))]

        def cells(key, fn):
            out = []
            for tag, src, reps in cols:
                got = pick(src[key], camp, typ, reps)
                for r in reps:
                    x = got.get(f"r{r}")
                    try:
                        out.append(fn(x) if x else "-")
                    except Exception as e:   # noqa: BLE001
                        out.append(f"n/a ({type(e).__name__})")
            return out
        ks = {}
        for tag, reps in (("stag", (1,)), ("sync", (1, 2))):
            for r in reps:
                p = (SYNC if tag == "sync" else ROOT / ".runs/2026-11-10_1946_v2") / camp / f"grp-{typ}-pfifo-r{r}" / "grouping" / "keyframe-spread.json"
                if p.exists():
                    ks[(tag, r)] = json.loads(p.read_text())
                else:   # staggered runs predate keyframe_spread: computed here, nothing written into the old run
                    import keyframe_spread as kfs
                    ks[(tag, r)] = kfs.run_spread(p.parents[1]) if p.parents[1].exists() else None
        kcell = []
        for key in (("stag", 1), ("sync", 1), ("sync", 2)):
            g = (ks[key] or {}).get("groups", {}).get("across renditions") if ks[key] else None
            kcell.append(" / ".join(f"{g[st]['p50_ms']:.1f}|{g[st]['max_ms']:.0f}" for st in ("scheduled", "written", "packet"))
                         if g else "(not computed)")
        print("| keyframe spread ms, p50\\|max: scheduled / written / packet | " + " | ".join(kcell) + " |")
        print("| detector v2-owd vs GT1 | " + " | ".join(cells("det", det_cell)) + " |")
        if camp != "G0":
            print("| ECG v1.2 (final) | " + " | ".join(cells("ecg", ecg_cell)) + " |")
            print("| Step 4 h3 (ECG intervals) | " + " | ".join(cells("s4f", h3_cell)) + " |")
        print("| GT1 episodes per min by egress | " + " | ".join(cells("raw", lambda x: ", ".join(
            f"{h} {g['per_min']}" for h, g in sorted(x['gt1'].items()) if g['n']))) + " |")
        print("| alarms per client-min; share within 200 ms after a keyframe (unrelated: 0.20) | " + " | ".join(
            cells("raw", lambda x: f"{x['alarms']['per_min']} ; {f2(x['alarms']['on_keyframe_share'])}")) + " |")
        if camp != "G0":
            print("| onset spread same burst p50 / p90 ms (ECG) | " + " | ".join(cells("raw", lambda x: (
                f"{x['spread_onset_ms']['p50']:.0f} / {x['spread_onset_ms']['p90']:.0f}" if x['spread_onset_ms'] else "-"))) + " |")
        if camp == "G0":
            def calm(x_rows):
                if not x_rows:
                    return "-"
                pk = [r["peak_ms"] for r in x_rows]
                return (f"{len(x_rows)} peaks, {x_rows[0]['per_min']:.0f}/min, peak p50/p90 "
                        f"{np.percentile(pk, 50):.1f}/{np.percentile(pk, 90):.1f} ms, behind together "
                        f"{f2(np.mean([r['together'] for r in x_rows if 'together' in r]))}")
            out = []
            for tag, src, reps in cols:
                for r in reps:
                    out.append(calm([x for x in src["calm"] if x["type"] == "calm065" and x["aqm"] == "pfifo"
                                     and x["run"].endswith(f"-r{r}") and ((tag == "stag") or True)]))
            print("| queue peaks >= 5 ms (step 2b C) | " + " | ".join(out) + " |")
        print()
        if camp != "G0":
            for tag, src, reps in cols:
                got = pick(src["s5"], camp, typ, reps)
                for r in reps:
                    x = got.get(f"r{r}")
                    if x:
                        print(f"- {tag} r{r}: " + b_line(b_stats([x]), [x], eps_list))
            print()


if __name__ == "__main__":
    main()
