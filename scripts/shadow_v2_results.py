#!/usr/bin/env python3
"""Shadow v2 results: v2 (per-flow normalisation) and v2-fixed (one global scale) on every run.

    python3 scripts/shadow_v2_results.py .runs/<campaign> [...]   # -> reports/detector-v2/results.md, results.csv

Both detectors: tick features F1 (delay level), F2 (delay growth), F3 (pending growth over one GOP),
loss fraction over 100 ms; fusion S = s1 + s2 + s3 + sL; CUSUM with the hold rule; score = G / G_ref. G_ref and the
v2-fixed scale are fitted on the calm pfifo-r1 runs only (scripts/shadow_v2_step3.py); everything
else (other AQMs, every r2) is held out. Score = G / (2 G_ref) in [0, 1]. Operating point theta_on = 0.25 (G = G_ref / 2), off at
0.125 for T_clear. Truths: GT3 with a GT1 / GT2 queue on the path (spec section 11; main), GT1 and GT2
(link level, per client). Detector replay uses no group information.
"""

from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402

DETS = {"v2": "fuse d: s1+s2+s3+sL +hold gate:level+cap", "v2-fixed": "fuse d fixed +hold gate:level+cap"}  # frozen: hold (Step 5), loss gate level+cap
THETAS = (0.15, 0.25, 0.4)
MAIN_THETA = s3.THETA_ON


def worker(args) -> dict:
    run_dir, g_ref = args
    run = d.Run(run_dir)
    first = run_dir / "shadow-v2" / "ticks" / f"{run.subs[0]}.csv"
    if not first.exists() or "srtt" not in pd.read_csv(first, nrows=0).columns:
        s3.s1.worker(run_dir)  # held-out runs: build the per-ACK dump and tick files first
    flows = s3.load_flows(run_dir)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params())
    views = {"GT3 + path queue": gt3.view_of(run, e3, l3, need_path=True),
             "GT1 (link)": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             "GT2 (link)": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2)}
    out = {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir),
           "topo": run_dir.parent.name.split("_det-")[-1], "rep": run_dir.name.rsplit("-", 1)[-1], "score": {}}
    for label, feat in DETS.items():
        res = {s: s3.run_cusum(df, feat, g_ref[feat], False) for s, df in flows.items()}
        for th in THETAS:
            starts = {(label, s): s3.episodes(r, th)[0] for s, r in res.items()}
            for truth, view in views.items():
                out["score"][(label, th, truth)] = gt_score.score(run, view, starts, (label,))[label]
    return out


def fit_g_ref(feat: str, calm_dirs: list[Path]) -> float:
    """Step 3 rule: smallest multiple of the calm-run max G giving <= 0.1 FA/min at theta_on on the calm runs."""
    fits = {rd: {s: s3.run_cusum(df, feat, None, False) for s, df in s3.load_flows(rd).items()} for rd in calm_dirs}
    gmax = max(float(r["G"][r["armed"]:].max()) for f in fits.values() for r in f.values() if r["armed"] is not None)
    for m in s3.GREF_MULT:
        fa = clear = 0.0
        for rd in calm_dirs:
            run = d.Run(rd)
            e3, l3 = gt3.run_truth(run, gt3.Params())
            view = gt3.view_of(run, e3, l3, need_path=True)
            starts = {("x", s): s3.episodes(s3.run_cusum(df, feat, m * gmax, False), s3.THETA_ON)[0] for s, df in s3.load_flows(rd).items()}
            tl = gt_score.score(run, view, starts, ("x",))["x"]
            fa, clear = fa + tl["fp"], clear + tl["clear_s"]
        if clear and fa / (clear / 60) <= 0.1:
            return m * gmax
    return s3.GREF_MULT[-1] * gmax


def _f(x, k=2):
    return "-" if x != x else f"{x:.{k}f}"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    run_dirs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists())
    calm_dirs = [r for r in run_dirs if r.name.endswith("-r1") and "-pfifo-" in r.name and r.name.split("-")[1] in s3.CALM_RUNS]
    s3.FIXED_STATS.update(s3.fixed_stats(calm_dirs))
    g_ref = {feat: fit_g_ref(feat, calm_dirs) for feat in DETS.values()}
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, [(rd, g_ref) for rd in run_dirs]))
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=s3.ROOT, capture_output=True, text=True).stdout.strip()
    stamp = s3.ROOT / ".runs" / "2026-11-05_TRUTH-SETTINGS.md"
    table = s3.s1.table
    L = ["# Shadow v2: results", "",
         f"{len(res)} runs (campaigns {', '.join(Path(c).name for c in argv)}), all AQMs and both repetitions. "
         f"Fitted on the calm pfifo-r1 runs only: G_ref v2 {g_ref[DETS['v2']]:.1f}, v2-fixed {g_ref[DETS['v2-fixed']]:.1f}; "
         "v2-fixed scale " + ", ".join(f"{f} mu {m:.4g} sigma {sg:.4g}" for f, (m, sg) in s3.FIXED_STATS.items())
         + f". Operating point theta_on {MAIN_THETA}. git {git}. Truth: "
         + (stamp.read_text().splitlines()[3] if stamp.exists() else "see TRUTH-SETTINGS") + ".", ""]

    def pooled(rs, label, th, truth):
        return gt_score.summarize([r["score"][(label, th, truth)] for r in rs])

    cols = ["precision", "recall", "FA / min CLEAR", "latency p50 after t_on (ms)", "p90 (ms)", "share alarmed before t_on"]

    def cells(s):
        return [_f(s["precision"]), _f(s["recall"]), _f(s["fa_per_min"]), _f(s["late_latency_p50_ms"], 0),
                _f(s["latency_p90_ms"], 0), _f(s["early_share"])]

    rows = []
    for truth in ("GT3 + path queue", "GT1 (link)", "GT2 (link)"):
        for label in DETS:
            for th in THETAS:
                s = pooled(res, label, th, truth)
                rows.append([truth, label, th, s["episodes"], *cells(s)])
    L += ["## 1. Overall", "", table(["truth", "detector", "theta_on", "episodes", *cols], rows), "",
          "GT1 / GT2 are link-level truths charged to every client behind the queue (short keyframe queues included), "
          "so their recall is low for any detector; the client-level claim rests on GT3.", ""]
    rows = []
    for split, key in (("freeze set (pfifo-r1)", lambda r: r["aqm"] == "pfifo" and r["rep"] == "r1"),
                       ("held out: other AQMs r1", lambda r: r["aqm"] != "pfifo" and r["rep"] == "r1"),
                       ("held out: every r2", lambda r: r["rep"] == "r2")):
        rs = [r for r in res if key(r)]
        for label in DETS:
            s = pooled(rs, label, MAIN_THETA, "GT3 + path queue")
            rows.append([split, len(rs), label, s["episodes"], *cells(s)])
    L += ["## 2. Freeze set vs held-out (GT3 + path queue, theta 0.5)", "", table(["set", "runs", "detector", "episodes", *cols], rows), ""]
    for title, keyf in (("AQM", lambda r: r["aqm"]), ("topology", lambda r: r["topo"])):
        groups = defaultdict(list)
        for r in res:
            groups[keyf(r)].append(r)
        rows = [[g, label, *cells(pooled(rs, label, MAIN_THETA, "GT3 + path queue")), pooled(rs, label, MAIN_THETA, "GT3 + path queue")["episodes"]]
                for g, rs in sorted(groups.items()) for label in DETS]
        L += [f"## 3. Per {title} (GT3 + path queue, theta 0.5)", "", table([title, "detector", *cols, "episodes"], rows), ""]
    groups = defaultdict(list)
    for r in res:
        groups[(r["topo"], r["scn"])].append(r)
    rows = []
    for (topo, scn), rs in sorted(groups.items()):
        row = [topo, scn, pooled(rs, "v2", MAIN_THETA, "GT3 + path queue")["episodes"]]
        for label in DETS:
            s = pooled(rs, label, MAIN_THETA, "GT3 + path queue")
            row.append(f"{_f(s['precision'])} / {_f(s['recall'])} / {_f(s['fa_per_min'])} / {_f(s['late_latency_p50_ms'], 0)}")
        rows.append(row)
    L += ["## 4. Per scenario (GT3 + path queue, theta 0.5; precision / recall / FA per min / latency p50 ms)", "",
          table(["topology", "scenario", "episodes", *DETS], rows), ""]
    rows = []
    for label in DETS:
        s = pooled(res, label, MAIN_THETA, "GT3 + path queue")
        rows.append([label, *(f"{_f(r)} ({n})" for r, n in zip(s["bin_recall"], s["bin_episodes"]))])
    L += ["## 5. Recall by GT3 episode duration (theta 0.5)", "", table(["detector", *(f"{b} (n)" for b in gt_score.BIN_LABELS)], rows), ""]
    (s3.OUT / "results.md").write_text("\n".join(L))
    long_rows = [[r["name"], r["aqm"], r["scn"], r["topo"], r["rep"], label, th, truth, *(v for v in (sc["episodes"], sc["detected"], sc["tp"], sc["fp"], sc["clear_s"]))]
                 for r in res for (label, th, truth), sc in r["score"].items()]
    pd.DataFrame(long_rows, columns=["run", "aqm", "scenario", "topology", "rep", "detector", "theta", "truth", "episodes",
                                     "detected", "tp", "fp", "clear_s"]).to_csv(s3.OUT / "results.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
