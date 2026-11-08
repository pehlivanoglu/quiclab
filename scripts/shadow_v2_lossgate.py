#!/usr/bin/env python3
"""Shadow v2: loss-gate experiment (only the gate of the loss term changes).

    python3 scripts/shadow_v2_lossgate.py .runs/<campaign> [...]   # -> reports/detector-v2/lossgate.md, lossgate.csv

Base: v2 and v2-fixed as frozen in Step 6 (fusion d, hold), with F3's rate normaliser made causal
(scripts/shadow_v2_step3.py CAUSAL_D; "legacy" rows reproduce Step 6 with the GT3-frozen normaliser).
Gate kinds and the hold-loss clause: shadow_v2_step3.GATE. Per variant G_ref is refitted on the calm pfifo-r1
runs with the Step 3 rule; nothing else is fitted. theta_on 0.25, theta_off 0.125 for T_clear.

Metrics (GT3 + path queue): precision, recall (gt_score), alarm-on recall, FA / min CLEAR, latency p50 / p90;
FA / min per negative scenario (calm030, calm065, calm090, calmcbr090, randloss) and the share of false alarms
inside an injected loss window; recall on GT3 episodes triggered by loss vs by delay; fq_codel competition
cells (burstudp, tcpcubic, tcpbbr, onoff, splitudp); share of harmful episodes warned before harm at B 200 and
600 ms (scripts/shadow_v2_step6.py playback port). 95 % bootstrap intervals over runs for the main rows.
"""

from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt3  # noqa: E402
import gt_bands  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_results as res_mod  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402
import shadow_v2_step5 as s5  # noqa: E402
import shadow_v2_step6 as s6  # noqa: E402

KINDS = [("legacy", "growth", False, True, False)] + [
    (f"{k}{'+cap' if c else ''}{'' if h else ' -holdloss'}", k, c, h, True) for k, c, h in s3.GATE_KINDS]
BASES = {"v2": "fuse d: s1+s2+s3+sL", "v2-fixed": "fuse d fixed"}
DETS = {f"{b} {label}": (f"{feat} +hold gate:{k}{'+cap' if c else ''}{'' if h else ' -holdloss'}", causal)
        for b, feat in BASES.items() for label, k, c, h, causal in KINDS}
THETA = s3.THETA_ON
BUFS = (200, 600)
COMP = ("burstudp", "tcpcubic", "tcpbbr", "onoff", "splitudp")
N_BOOT = 500
STATS: dict[bool, dict] = {}  # v2-fixed calm scale per normaliser (set before the pool forks)


def use(causal: bool) -> None:
    s3.CAUSAL_D = causal
    s3.FIXED_STATS.clear()
    s3.FIXED_STATS.update(STATS[causal])


def fit(args):
    name, (feat, causal), calm_dirs = args
    use(causal)
    return name, res_mod.fit_g_ref(feat, calm_dirs)


def worker(args) -> dict:
    run_dir, g_ref = args
    run = d.Run(run_dir)
    e1, _ = gt1.run_truth(run, gt1.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params())
    view = gt3.view_of(run, e3, l3, need_path=True)
    lw = s6.loss_windows(run)
    subs = list(view)
    harms = {s: s6.harm_times(run, s)[0] for s in subs}
    trig = {(x["flow"], round(x["t_on"], 2)): x["trigger"] for x in e3}
    out = {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir), "rep": run_dir.name.rsplit("-", 1)[-1], "v": {}}
    flows_by = {}
    for name, (feat, causal) in DETS.items():
        use(causal)
        if causal not in flows_by:
            flows_by[causal] = s3.load_flows(run_dir)
        flows = flows_by[causal]
        spans = {s: s5.on_spans(s3.run_cusum(df, feat, g_ref[name], False), THETA) for s, df in flows.items()}
        starts = {(name, s): [a for a, _, _ in sp] for s, sp in spans.items()}
        v = {"score": gt_score.score(run, view, starts, (name,))[name], "ep_n": 0, "ep_on": 0,
             "trig": defaultdict(lambda: [0, 0]), "harm": {B: [0, 0] for B in BUFS}, "fa": 0, "fa_loss": 0}
        for s, (eps, code) in view.items():
            if s not in spans:
                continue
            sp = [(x, y) for x, y, _ in spans[s]]
            used = set()
            for a, b in eps:
                if a < d.WARMUP_S:
                    continue
                lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
                on = s6.on_in(sp, lo, hi) is not None
                v["ep_n"] += 1
                v["ep_on"] += on
                tg = next((tr for (f, t0), tr in trig.items() if f == s and abs(t0 - a) < 0.05), "?")
                v["trig"][tg][0] += 1
                v["trig"][tg][1] += any(lo <= x <= hi for x, _ in sp)
                used.update(x for x, _ in sp if lo <= x <= hi)
                for B in BUFS:
                    th = next((h for h in harms[s][B] if a <= h <= b + s6.HARM_TAIL_S), None)
                    if th is not None:
                        v["harm"][B][0] += 1
                        v["harm"][B][1] += s6.on_in(sp, lo, th) is not None
            for x, _ in sp:
                if x < d.WARMUP_S or x in used or any(a <= x <= b for a, b in eps):
                    continue
                if code[min(len(code) - 1, int(x / gt_score.GRID_S))] == gt_score.RANK[gt_bands.CLEAR]:
                    v["fa"] += 1
                    v["fa_loss"] += any(a <= x <= b + 1.0 for a, b in lw)
        v["trig"] = dict(v["trig"])
        out["v"][name] = v
    return out


def _f(x, k=2):
    return "-" if x is None or x != x else f"{x:.{k}f}"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    run_dirs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists())
    calm_dirs = [r for r in run_dirs if r.name.endswith("-r1") and "-pfifo-" in r.name and r.name.split("-")[1] in s3.CALM_RUNS]
    for causal in (False, True):
        s3.CAUSAL_D = causal
        STATS[causal] = s3.fixed_stats(calm_dirs)
    with ProcessPoolExecutor(max_workers=12) as pool:
        g_ref = dict(pool.map(fit, [(n, spec, calm_dirs) for n, spec in DETS.items()]))
        res = list(pool.map(worker, [(rd, g_ref) for rd in run_dirs]))
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=s3.ROOT, capture_output=True, text=True).stdout.strip()
    table = s3.s1.table
    rng = np.random.default_rng(1)

    def pooled(rs, n):
        return gt_score.summarize([r["v"][n]["score"] for r in rs])

    def ratio(rs, n, key, i=None):
        if i is None:
            num = sum(r["v"][n][key[0]] for r in rs); den = sum(r["v"][n][key[1]] for r in rs)
        else:
            num = sum(r["v"][n][key][i][1] for r in rs); den = sum(r["v"][n][key][i][0] for r in rs)
        return num / den if den else float("nan")

    def trig_rec(rs, n, tg):
        a = sum(r["v"][n]["trig"].get(tg, [0, 0])[0] for r in rs)
        b = sum(r["v"][n]["trig"].get(tg, [0, 0])[1] for r in rs)
        return b / a if a else float("nan")

    def fa_of(rs, n):
        return pooled(rs, n)["fa_per_min"]

    neg = {scn: [r for r in res if r["scn"] == scn] for scn in s6.NEGATIVE}
    comp = [r for r in res if r["aqm"] == "fq_codel" and r["scn"] in COMP]
    rows, csv = [], []
    for n in DETS:
        s = pooled(res, n)
        rl = neg["randloss"]
        fa_rl = sum(r["v"][n]["fa"] for r in rl)
        worst = max(fa_of([r for r in rs if r["aqm"] == a], n) for rs in neg.values() for a in {r["aqm"] for r in rs})
        cs = pooled(comp, n)
        row = [n, _f(g_ref[n], 1), _f(s["precision"]), _f(s["recall"]), _f(ratio(res, n, ("ep_on", "ep_n"))), _f(s["fa_per_min"]),
               _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0), _f(fa_of(rl, n)),
               _f(sum(r["v"][n]["fa_loss"] for r in rl) / fa_rl if fa_rl else float("nan")),
               *(_f(fa_of(neg[x], n)) for x in ("calm030", "calm065", "calm090", "calmcbr090")), _f(worst),
               _f(trig_rec(res, n, "loss")), _f(trig_rec(res, n, "delay")), _f(cs["recall"]), _f(cs["fa_per_min"]),
               *(_f(ratio(res, n, "harm", B)) for B in BUFS)]
        rows.append(row)
        csv.append(row)
    head = ["detector", "G_ref", "precision", "recall", "recall (alarm on)", "FA / min", "lat p50", "p90", "randloss FA / min",
            "randloss FA in loss window", "calm030 FA", "calm065 FA", "calm090 FA", "calmcbr090 FA", "worst negative cell FA",
            "recall loss-triggered GT3", "recall delay-triggered GT3", "fq_codel comp. recall", "fq_codel comp. FA",
            "warned before harm B200", "B600"]
    L = ["# Shadow v2: loss-gate experiment", "",
         f"{len(res)} runs, theta_on {THETA}, theta_off {THETA / 2}. Only the gate of the loss term (and, in the -holdloss rows, "
         "the hold rule's loss clause) changes; G_ref refitted per row on the calm pfifo-r1 runs. 'legacy' = Step 6 with the "
         "GT3-frozen F3 normaliser (truth leak); every other row uses the causal normaliser. "
         f"git {git}.", "",
         "Gates: growth = F2 or F3 score > 0 in the last 3 ticks (Step 4); level = z(F1) >= 1 in the last 3 ticks; "
         "level2 = z(F1) >= 2; either / both = growth or / and level; open = no gate; off = no loss term; +cap = positive loss "
         "contribution per excursion of G capped at G_ref / 4 (half the alarm level); -holdloss = hold without its "
         "'loss within T_clear' clause.", "",
         table(head, rows), ""]
    # bootstrap for the base, the legacy row and the three rows with the lowest worst-negative FA at recall >= base - 0.02
    rows = []
    for b in BASES:
        for n in [x for x in DETS if x.startswith(b + " ")]:
            vals = []
            for _ in range(N_BOOT):
                smp = [res[i] for i in rng.integers(0, len(res), len(res))]
                ss = pooled(smp, n)
                rl = [r for r in smp if r["scn"] == "randloss"]
                vals.append((ss["recall"], ratio(smp, n, ("ep_on", "ep_n")), ss["fa_per_min"], fa_of(rl, n) if rl else np.nan))
            a = np.array(vals, dtype=float)
            rows.append([n, *(f"{np.nanpercentile(a[:, i], 2.5):.2f}-{np.nanpercentile(a[:, i], 97.5):.2f}" for i in range(4))])
    L += ["## 95 % bootstrap intervals over runs", "",
          table(["detector", "recall", "alarm-on recall", "FA / min", "randloss FA / min"], rows), ""]
    (s3.OUT / "lossgate.md").write_text("\n".join(L))
    pd.DataFrame(csv, columns=head).to_csv(s3.OUT / "lossgate.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
