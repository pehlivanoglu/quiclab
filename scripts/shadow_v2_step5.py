#!/usr/bin/env python3
"""Shadow v2, Step 5: hold rule, rebase, episode behaviour, onset spread (spec v1.0 section 12).

    python3 scripts/shadow_v2_step5.py .runs/<campaign> [...]   # -> reports/detector-v2/step5.md, step5.csv

Variants of v2 and v2-fixed (fusion d): base, +hold, +hold +rebase (scripts/shadow_v2_step3.py).
G_ref per variant from the calm pfifo-r1 runs as before. All 200 runs, theta_on 0.25, theta_off 0.125 for
T_clear (score = G / (2 G_ref)). Metrics:
  - overall precision / recall / FA / latency against GT3 + path queue
  - burstlong: coverage = share of GT3 episode time with the alarm on; alarm starts per episode-minute,
    counted from t_on; pass: coverage >= 0.9 and <= 3 starts per episode-minute
  - rebase: how often it fires, and how often it fires inside a GT3 episode (the risk of erasing real
    congestion), per scenario; delaystep false alarms per minute (old runs; the scenario left the matrix)
  - onset spread across clients of one injected event (burstcap, splitcap, bursttiny): max - min of the
    alarm arrival and of t_onset over the clients that alarmed within [start - 1 s, end + 2 s]
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
import gt_score  # noqa: E402
import shadow_v2_results as res_mod  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402

VARIANTS = {"v2": "fuse d: s1+s2+s3+sL", "v2 +hold": "fuse d: s1+s2+s3+sL +hold",
            "v2 +hold +rebase": "fuse d: s1+s2+s3+sL +hold +rebase", "v2-fixed": "fuse d fixed",
            "v2-fixed +hold": "fuse d fixed +hold", "v2-fixed +hold +rebase": "fuse d fixed +hold +rebase"}
THETA = s3.THETA_ON
SPREAD_SCN = ("burstcap", "splitcap", "bursttiny")


def on_spans(r: dict, th: float) -> list[tuple[float, float, float]]:
    """(arrival, end, onset) per alarm episode; off after score < th / 2 for T_clear."""
    score, G, t, srtt = r["score"], r["G"], r["t"], r["srtt"]
    out, on, start, onset, below = [], False, None, None, None
    for k in range(len(t)):
        if not on and score[k] >= th:
            on, start, below = True, t[k], None
            zero = np.flatnonzero(G[:k] == 0)
            onset = float(t[zero[-1]]) if len(zero) else float(t[0])
        elif on:
            if score[k] < th / 2:
                below = t[k] if below is None else below
                if t[k] - below >= max(0.3, 2 * (srtt[k] / 1000 if np.isfinite(srtt[k]) else 0.0)):
                    out.append((float(start), float(t[k]), onset))
                    on = False
            else:
                below = None
    if on:
        out.append((float(start), float(t[-1]), onset))
    return out


def worker(args) -> dict:
    run_dir, g_ref = args
    run = d.Run(run_dir)
    flows = s3.load_flows(run_dir)
    e3, l3 = gt3.run_truth(run, gt3.Params())
    view = gt3.view_of(run, e3, l3, need_path=True)
    bursts = gt1._bursts(run.path)
    paths = {s: det_eval_paths(run, s) for s in flows}
    out = {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir), "v": {}}
    for label, feat in VARIANTS.items():
        res = {s: s3.run_cusum(df, feat, g_ref[feat], False) for s, df in flows.items()}
        spans = {s: on_spans(r, THETA) for s, r in res.items()}
        starts = {(label, s): [a for a, _, _ in sp] for s, sp in spans.items()}
        v = {"score": gt_score.score(run, view, starts, (label,))[label], "cov_on": 0.0, "cov_ep": 0.0, "starts_ep": 0,
             "rebases": 0, "rebases_in_ep": 0, "ep_n": 0, "ep_on": 0, "spread_arr": [], "spread_on": [], "onset_err": []}
        for s, (eps, _) in view.items():
            if s not in spans:
                continue
            for a, b in eps:
                if a < d.WARMUP_S:
                    continue
                v["cov_ep"] += b - a
                v["ep_n"] += 1
                lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
                v["ep_on"] += any(x <= hi and y >= lo for x, y, _ in spans[s])
                v["cov_on"] += sum(max(0.0, min(b, y) - max(a, x)) for x, y, _ in spans[s])
                v["starts_ep"] += sum(1 for x, _, _ in spans[s] if a <= x <= b)
            for t_rb, _ in res[s]["rebases"]:
                v["rebases"] += 1
                v["rebases_in_ep"] += any(a <= t_rb <= b for a, b in eps)
        if out["scn"] in SPREAD_SCN:
            for bst in bursts:
                arr, ons = [], []
                for s, sp in spans.items():
                    if bst["hop"] not in paths[s]:
                        continue
                    hit = [(x, o) for x, _, o in sp if bst["start"] - 1 <= x <= bst["end"] + 2]
                    if hit:
                        arr.append(hit[0][0]); ons.append(hit[0][1])
                        v["onset_err"].append(hit[0][1] - bst["start"])
                if len(arr) >= 2:
                    v["spread_arr"].append(max(arr) - min(arr)); v["spread_on"].append(max(ons) - min(ons))
        out["v"][label] = v
    return out


def det_eval_paths(run, s):
    return set(d.path_hops(run, run.pub, s))


def _f(x, k=2):
    return "-" if x is None or x != x else f"{x:.{k}f}"


def _q(v, q, k=0, scale=1000.0):
    v = [x for x in v if x == x]
    return "-" if not v else f"{np.percentile(v, q * 100) * scale:.{k}f}"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    run_dirs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists())
    calm_dirs = [r for r in run_dirs if r.name.endswith("-r1") and "-pfifo-" in r.name and r.name.split("-")[1] in s3.CALM_RUNS]
    s3.FIXED_STATS.update(s3.fixed_stats(calm_dirs))
    g_ref = {feat: res_mod.fit_g_ref(feat, calm_dirs) for feat in VARIANTS.values()}
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, [(rd, g_ref) for rd in run_dirs]))
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=s3.ROOT, capture_output=True, text=True).stdout.strip()
    table = s3.s1.table
    L = ["# Shadow v2, Step 5: hold, rebase, episodes", "",
         f"{len(res)} runs, theta_on {THETA}, theta_off {THETA / 2}. G_ref (calm pfifo-r1): "
         + ", ".join(f"{k} {g_ref[f]:.1f}" for k, f in VARIANTS.items()) + f". git {git}.", ""]

    def pooled(rs, label):
        return gt_score.summarize([r["v"][label]["score"] for r in rs])

    rows = []
    for label in VARIANTS:
        s = pooled(res, label)
        on_rec = sum(r["v"][label]["ep_on"] for r in res) / max(1, sum(r["v"][label]["ep_n"] for r in res))
        rows.append([label, _f(s["precision"]), _f(s["recall"]), _f(on_rec), _f(s["fa_per_min"]), _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0)])
    L += ["## 1. Overall, all 200 runs (GT3 + path queue)", "",
          "recall = an alarm STARTS in [t_on - 1 s, min(end, t_on + 10 s)] (gt_score rule); recall (alarm on) = the alarm is ON "
          "at some point of that window, whether it started there or earlier. With the hold rule one alarm spans several "
          "GT3 episodes of one long event, which the first rule counts as misses.", "",
          table(["variant", "precision", "recall", "recall (alarm on)", "FA / min CLEAR", "latency p50 (ms)", "p90 (ms)"], rows), ""]

    rows = []
    for label in VARIANTS:
        rs = [r for r in res if r["scn"] == "burstlong"]
        cov = sum(r["v"][label]["cov_on"] for r in rs) / max(1e-9, sum(r["v"][label]["cov_ep"] for r in rs))
        spm = sum(r["v"][label]["starts_ep"] for r in rs) / max(1e-9, sum(r["v"][label]["cov_ep"] for r in rs) / 60)
        s = pooled(rs, label)
        on_rec = sum(r["v"][label]["ep_on"] for r in rs) / max(1, sum(r["v"][label]["ep_n"] for r in rs))
        rows.append([label, _f(s["recall"]), _f(on_rec), _f(cov), _f(spm, 1), "PASS" if cov >= 0.9 and spm <= 3 else "FAIL"])
    L += ["## 2. burstlong: coverage and alarm starts per episode-minute (pass: >= 0.9 and <= 3)", "",
          table(["variant", "recall", "recall (alarm on)", "coverage", "starts per episode-minute", "verdict"], rows), ""]

    rows = []
    for label in (k for k in VARIANTS if "rebase" in k):
        by = defaultdict(lambda: [0, 0])
        for r in res:
            by[r["scn"]][0] += r["v"][label]["rebases"]; by[r["scn"]][1] += r["v"][label]["rebases_in_ep"]
        tot, inep = sum(v[0] for v in by.values()), sum(v[1] for v in by.values())
        top = ", ".join(f"{k} {v[0]} ({v[1]} in ep.)" for k, v in sorted(by.items(), key=lambda kv: -kv[1][0])[:6] if v[0])
        ds = pooled([r for r in res if r["scn"] == "delaystep"], label)
        base = pooled([r for r in res if r["scn"] == "delaystep"], label.replace(" +rebase", ""))
        rows.append([label, tot, inep, top, f"{_f(base['fa_per_min'])} -> {_f(ds['fa_per_min'])}"])
    L += ["## 3. Rebase: firings, firings inside a GT3 episode (erases real congestion), delaystep FA / min without -> with", "",
          table(["variant", "rebases", "inside a GT3 episode", "top scenarios", "delaystep FA / min (hold -> hold + rebase)"], rows), ""]

    rows = []
    for label in VARIANTS:
        for scn in SPREAD_SCN:
            rs = [r for r in res if r["scn"] == scn]
            sa = [x for r in rs for x in r["v"][label]["spread_arr"]]
            so = [x for r in rs for x in r["v"][label]["spread_on"]]
            oe = [x for r in rs for x in r["v"][label]["onset_err"]]
            rows.append([label, scn, len(sa), _q(sa, 0.5), _q(sa, 0.9), _q(so, 0.5), _q(so, 0.9), _q(oe, 0.1), _q(oe, 0.5), _q(oe, 0.9)])
    L += ["## 4. Onset spread across the clients of one injected event (ms)", "",
          table(["variant", "scenario", "events with >= 2 clients alarming", "arrival spread p50", "p90", "t_onset spread p50", "p90",
                 "t_onset - event start p10", "p50", "p90"], rows), ""]
    (s3.OUT / "step5.md").write_text("\n".join(L))
    pd.DataFrame([[r["name"], r["aqm"], r["scn"], k, v["score"]["episodes"], v["score"]["detected"], v["score"]["tp"], v["score"]["fp"],
                   v["cov_on"], v["cov_ep"], v["starts_ep"], v["rebases"], v["rebases_in_ep"]] for r in res for k, v in r["v"].items()],
                 columns=["run", "aqm", "scenario", "variant", "episodes", "detected", "tp", "fp", "cov_on_s", "cov_ep_s", "starts_in_ep",
                          "rebases", "rebases_in_ep"]).to_csv(s3.OUT / "step5.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
