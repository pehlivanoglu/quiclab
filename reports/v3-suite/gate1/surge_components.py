#!/usr/bin/env python3
"""Gate check 5 diagnosis: offered load in each surge window, split into its parts.

    .venv/bin/python3 reports/v3-suite/gate1/surge_components.py <run> [...]

Per surge window on `main` (in units of C):
- router offered (router-metrics offered_bytes, what check 5 uses);
- non-video: every qtraffic source on the egress's route (background + surges; <id>-sent.csv
  100 ms bins, UDP payload x UDP_WIRE = router bytes);
- video: the publisher's QUIC bytes to the clients behind the egress (<client>-sent.csv) / 0.96
  (QUIC bytes vs router bytes);
- planned: background U(1 - s) + surge (u - U), and the calm video share s U;
- drops on the egress inside the window.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import v3_suite  # noqa: E402

for rd in map(Path, sys.argv[1:]):
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    e = plan["egress"]["main"]
    C, s, U = e["C_e_mbps"] * 1e6 / 8, plan["s"], plan["U"]
    wins = [w for w in json.loads((rd / "grouping" / "windows.json").read_text()) if w["stimulus_type"] == "surge"]
    csv = dict(((f"{a}->{b}"), p) for (a, b), p in gt1.router_egresses(run))[e["hop"]]
    rm = pd.read_csv(csv, usecols=["timestamp_mono_ns", "interval_ns", "offered_bytes", "drops"])
    t_rm = np.array([run.t_mono_us(v / 1000) for v in rm.timestamp_mono_ns])
    q = {}
    for f in (rd / "traffic").glob("*-sent.csv"):
        x = pd.read_csv(f)
        q[f.name[:-9]] = (np.array([run.t_unix_us(v) for v in x.t_us]), x.sent_bytes.to_numpy() * v3_suite.UDP_WIRE)
    vid = {}
    for sid in e["clients"]:
        x = pd.read_csv(run.sender_file(sid, "sent"), usecols=["send_mono_us", "bytes"])
        vid[sid] = (np.array([run.t_mono_us(v) for v in x.send_mono_us]), x.bytes.to_numpy() / 0.96)
    print(f"## {rd.name} (C {e['C_e_mbps']} Mb/s, s {s}, U {U})\n")
    print("| u | d | router offered | non-video measured (planned) | video measured (calm plan s U) | drops | check 5 |")
    print("|---|---|---|---|---|---|---|")
    for w in sorted(wins, key=lambda w: (w["u"], w["d"], w["start"])):
        a, b = w["start"], w["end"]
        m = (t_rm > a) & (t_rm <= b)
        sec = rm.interval_ns.to_numpy()[m].sum() / 1e9
        off = rm.offered_bytes.to_numpy()[m].sum() / (C * sec)
        nv = sum(by[(t > a) & (t <= b)].sum() for t, by in q.values()) / (C * (b - a))
        vv = sum(by[(t > a) & (t <= b)].sum() for t, by in vid.values()) / (C * (b - a))
        drops = int(rm.drops.to_numpy()[m].sum())
        print(f"| {w['u']} | {w['d']:g} | {off:.3f} | {nv:.3f} ({U * (1 - s) + w['u'] - U:.3f}) | {vv:.3f} ({s * U:.3f}) | "
              f"{drops} | {'ok' if abs(off - w['u']) <= 0.05 else 'FAIL'} |")
    print()
