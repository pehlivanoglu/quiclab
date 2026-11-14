#!/usr/bin/env python3
"""Does the per-client GT1 truth on fq_codel / cake egresses behave as intended?
(read-only; development set only, N1-N5 not opened)

    python3 reports/perflow-truth-2026-11-12/check.py .runs/2026-11-10_1946_v2 > reports/perflow-truth-2026-11-12/report.md

Per shared stimulus window on a pinned egress: expected clients, clients labelled
congested by the per-client GT1 (own queue stood), and what the aggregate GT1
would have said (every expected client, when the egress's total queue stood).
Per labelled / unlabelled client: its own maximum backlog in the window (from
<iface>-flows.csv) and whether GT3 (its own OWD) saw an episode; per client
bitrate, the share of windows it is labelled in.
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import gt1  # noqa: E402

campaign = Path(sys.argv[1])
rows = []
for g in sorted(campaign.iterdir()):
    if not g.is_dir() or g.name.startswith("N"):
        continue
    for rd in sorted(g.glob("grp-*")):
        if not (rd / "router-metrics" / "flow-ids.json").exists() or not (rd / "grouping" / "windows.json").exists():
            continue
        run = ga.load_run(rd)
        windows = json.loads((rd / "grouping" / "windows.json").read_text())
        hop_eps, per_flow, flow_eps = ga.gt1_hop_episodes(run), ga.gt1_hop_flow_episodes(run), ga.gt3_flow_episodes(run)
        new = ga.measured_bursts(run, windows, hop_eps, hop_flow_episodes=per_flow)
        agg = ga.measured_bursts(run, windows, hop_eps)
        backlog = {}
        for hop, csv in gt1.router_egresses(run):
            f = csv.with_name(csv.stem + "-flows.csv")
            if f.exists():
                t_ns = np.array([int(r["timestamp_mono_ns"]) for r in d.rows(csv)])
                b, _ = gt1.load_flow_samples(run, csv, t_ns)
                t = np.array([run.t_mono_us(x / 1000) for x in t_ns])
                backlog[f"{hop[0]}->{hop[1]}"] = (t, b)
        rate = {s: run.topology["subscribers"][s].get("rate_kbps") for s in run.subs}
        for bn, ba in zip(new, agg):
            if len(bn["expected"]) < 2 or bn["hop"] not in per_flow:
                continue
            lo, hi = bn["start"], bn["end"] + d.BURST_RECOVERY_S
            t, b = backlog.get(bn["hop"], (None, {}))
            for c in bn["expected"]:
                sid = c.split("_")[0] if c not in b else c
                mx = float(b[sid][(t >= lo) & (t <= hi)].max()) if sid in b and t is not None and ((t >= lo) & (t <= hi)).any() else 0.0
                rows.append({"campaign": g.name, "aqm": rd.name.split("-")[-2], "run": rd.name, "client": c,
                             "rate": rate.get(c), "new_hit": c in bn["hit"], "agg_hit": c in ba["hit"],
                             "gt3": ga.overlaps(flow_eps.get(c, []), lo, hi), "own_max_kb": mx / 1000})

print("# Per-client GT1 on fq_codel / cake (development set)\n")
print(f"{len({r['run'] for r in rows})} runs, {len(rows)} (window, expected client) pairs on pinned egresses.\n")
print("## Labels: per-client vs aggregate GT1\n")
print("| AQM | pairs | aggregate says congested | per-client says congested | dropped by per-client | added |")
print("|---|---|---|---|---|---|")
for aqm in sorted({r["aqm"] for r in rows}):
    rs = [r for r in rows if r["aqm"] == aqm]
    print(f"| {aqm} | {len(rs)} | {sum(r['agg_hit'] for r in rs)} | {sum(r['new_hit'] for r in rs)} "
          f"| {sum(r['agg_hit'] and not r['new_hit'] for r in rs)} | {sum(r['new_hit'] and not r['agg_hit'] for r in rs)} |")
print("\n## Is the label consistent with the client's own queue and its own OWD?\n")
print("| AQM | label | pairs | own max backlog kB p10 / p50 / p90 | GT3 (own OWD) episode |")
print("|---|---|---|---|---|")
for aqm in sorted({r["aqm"] for r in rows}):
    for lab in (True, False):
        rs = [r for r in rows if r["aqm"] == aqm and r["new_hit"] == lab]
        if rs:
            v = [r["own_max_kb"] for r in rs]
            print(f"| {aqm} | {'congested' if lab else 'not congested'} | {len(rs)} | "
                  + " / ".join(f"{x:.1f}" for x in np.percentile(v, [10, 50, 90])) + f" | {np.mean([r['gt3'] for r in rs]):.2f} |")
print("\n## Share of windows a client is labelled congested, by client bitrate\n")
print("| AQM | bitrate kb/s | pairs | per-client | aggregate |\n|---|---|---|---|---|")
for aqm in sorted({r["aqm"] for r in rows}):
    by = defaultdict(list)
    for r in rows:
        if r["aqm"] == aqm:
            by[r["rate"]].append(r)
    for k in sorted(by, key=lambda x: x or 0):
        rs = by[k]
        print(f"| {aqm} | {k} | {len(rs)} | {np.mean([r['new_hit'] for r in rs]):.2f} | {np.mean([r['agg_hit'] for r in rs]):.2f} |")
print("\n## By campaign\n")
print("| campaign | AQM | pairs | per-client congested share | aggregate share |\n|---|---|---|---|---|")
by = defaultdict(list)
for r in rows:
    by[(r["campaign"], r["aqm"])].append(r)
for k in sorted(by):
    rs = by[k]
    print(f"| {k[0]} | {k[1]} | {len(rs)} | {np.mean([r['new_hit'] for r in rs]):.2f} | {np.mean([r['agg_hit'] for r in rs]):.2f} |")
