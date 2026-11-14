#!/usr/bin/env python3
"""Grouping performance tables of the 2026-11-11 status report (moved from a session
scratch folder; kept as run). Step 1: collect per-run metrics of the development set:

    python3 reports/grouping-perf-2026-11-11/collect.py OUT/rows.json      # reads .runs/2026-11-10_1946_v2
    python3 reports/grouping-perf-2026-11-11/tables.py OUT/rows.json group|src
"""
import json, sys, statistics, re
from pathlib import Path
sys.path.insert(0, "scripts")
from grouping_baselines import first_sustained
D = Path(".runs/2026-11-10_1946_v2")
SRCS = ["v2-owd", "v2", "owd", "truth"]
rows = []
for g in sorted(D.iterdir()):
    if not g.is_dir() or g.name.startswith("N"): continue
    for run in sorted(g.iterdir()):
        if not run.is_dir(): continue
        m_ = re.match(r"(grp|det)-(.+)-(\w+?)-r\d+$", run.name)
        if not m_: continue
        typ, aqm = m_.group(2), m_.group(3)
        for s in SRCS:
            gd = run / f"grouping-{s}"
            mp = gd / "metrics.json"
            if not mp.exists(): continue
            m = json.loads(mp.read_text())
            pw = m["pairwise"]; pl = m["pairwise_link"]
            pairs = pw["pairs"]
            n = len(pairs)
            truth = {p: v["truth_same"] for p, v in pairs.items()}
            dec = {p: v["decided"] for p, v in pairs.items()}
            correct_final = sum((dec[p] == "SAME") == truth[p] and dec[p] != "UNCERTAIN" for p in pairs)
            decided = sum(dec[p] != "UNCERTAIN" for p in pairs)
            shared = [b for b in m["bursts"] if len(b.get("expected", [])) >= 2 and b.get("hit")]
            t0 = min((b["start"] for b in shared), default=None)
            pt = json.loads((gd / "pairs_t.json").read_text()) if (gd / "pairs_t.json").exists() else []
            tc = first_sustained([(e["t"], all((e["pairs"].get(p) == "SAME") == truth[p] for p in pairs)) for e in pt]) if pt else None
            # leaf confirm latency: confirmed_t - first shared window whose expected set covers >=2 of the leaf's members
            leaf_lat = []; leaf_ev = []
            for l in m["leaves"].values():
                if l.get("kind") != "leaf" or not l.get("confirmed") or len(l.get("members", [])) < 2: continue
                mem = set(l["members"])
                ws = [b["start"] for b in shared if len(mem & set(b["expected"])) >= 2]
                if ws: leaf_lat.append(l["confirmed_t"] - min(ws))
                leaf_ev.append(l.get("confirmed_events"))
            e2e = json.loads((gd / "e2e.json").read_text()) if (gd / "e2e.json").exists() else {}
            rows.append(dict(group=g.name, type=typ, aqm=aqm, src=s, n_pairs=n, tp=pw["tp"], fp=pw["fp"], fn=pw["fn"], tn=pw["tn"],
                             unc=pw.get("uncertain"), cov=pw["coverage"], decided=decided, correct=correct_final,
                             link_tp=pl["tp"], link_fp=pl["fp"], link_fn=pl["fn"],
                             tree=m["tree_correct"], ctrl=m["ctrl_grouped"], cases=m["cases"],
                             n_shared=len(shared), t_first=t0, t_correct=tc, t_correct_rel=(tc - t0) if (tc is not None and t0 is not None) else None,
                             leaf_lat=leaf_lat, leaf_ev=leaf_ev,
                             spread=m.get("spread", {}).get("spread_onset_ms", {}),
                             e2e={k: e2e.get(k) for k in ("detected_all","attributed_ok","grouped_cases","t_group_p50_s","alarm_single","alarm_grouped","false_alarms_per_min","false_groups_per_min")},
                             e2e_rows=e2e.get("shared_windows", [])))
json.dump(rows, open(sys.argv[1], "w"))
print(len(rows))
