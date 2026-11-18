#!/usr/bin/env python3
"""Check 1 (load share) restricted to the time when every planned client is present and the background is on
(user, 2026-11-17, for N3 hchurn and T1 dclean). The raw check in each run's v3-checks.json is kept as is; this
writes only reports/v4-health-2026-11-17/loadshare-present.md.

Same computation as scripts/scenario_catalog.calm_load (calm time = warm-up and shut-down cut, stimulus windows +-
CALM_MARGIN cut), with two extra conditions on every sample: all planned clients (the plan's egress client lists)
have a session at t (grouping_adapter.sessions_of), and every bg event of the scenario is on at t (FLAG: all bg
events, not only the egress's own). Thresholds from scripts/v3_gate.py (LOAD_TOL, SHARE_TOL, SHARE_HEADER).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def present_mask(run, plan):
    import grouping_adapter as ga
    sess = ga.sessions_of(run)
    planned = sorted({c for e in plan["egress"].values() for c in e["clients"]})
    bg = [(e["at_s"], e["at_s"] + e.get("duration_s", run.duration)) for e in run.scenario.get("events", [])
          if e["type"] == "bg"]

    def ok(t):
        m = np.ones(len(t), bool)
        for c in planned:
            ss = [v for k, v in sess.items() if k == c or k.startswith(c + "_")]
            on = np.zeros(len(t), bool)
            for j, lv in ss:
                on |= (t >= j) & (t < (lv if lv is not None else np.inf))
            m &= on
        for a, b in bg:
            m &= (t >= a) & (t < b)
        return m
    return ok


def check(rd: Path) -> dict:
    import det_eval as d
    import gt1
    import scenario_catalog as sc
    import v3_gate as vg
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    busy = [(w["start"] - sc.CALM_MARGIN, w["end"] + sc.CALM_MARGIN) for w in wins]
    pres = present_mask(run, plan)

    def calm(t):
        ok = (t >= d.WARMUP_S) & (t <= run.duration - d.SHUTDOWN_S) & pres(t)
        for a, b in busy:
            ok &= ~((t >= a) & (t <= b))
        return ok
    caps = d.capacity_series(run)
    sent = {}
    for s in run.subs:
        p = run.sender_file(s, "sent")
        if p.exists():
            x = pd.read_csv(p, usecols=["send_mono_us", "bytes"])
            sent[s] = (np.array([run.t_mono_us(v) for v in x.send_mono_us]), x.bytes.values.astype(float))
    res = {}
    for hop, csv in gt1.router_egresses(run):
        r = pd.read_csv(csv, usecols=["timestamp_mono_ns", "interval_ns", "transmitted_bytes"])
        t = np.array([run.t_mono_us(v / 1000) for v in r.timestamp_mono_ns])
        iv = r.interval_ns.values / 1e9
        tx = r.transmitted_bytes.values.astype(float)
        cap = np.array([d.value_at(caps[hop], v) for v in t]) * 1e6 / 8
        ok = calm(t) & (iv > 0)
        if not ok.any() or not np.sum(cap[ok] * iv[ok]):
            continue
        load = float(np.sum(tx[ok]) / np.sum(cap[ok] * iv[ok]))
        behind = [s for s in run.subs if hop in set(d.path_hops(run, run.pub, s))]
        vb = sum(float(np.sum(b[calm(ts)])) for s in behind if s in sent for ts, b in [sent[s]])
        res[f"{hop[0]}->{hop[1]}"] = {"load": load, "share": vb / float(np.sum(tx[ok])) / vg.SHARE_HEADER if np.sum(tx[ok]) else None,
                                      "seconds": float(np.sum(iv[ok]))}
    out = {}
    for name, e in plan["egress"].items():
        if not e.get("shaped", True):
            continue
        m = res.get(e["hop"])
        u_e, s_e = e.get("U", plan["U"]), e["s"] if e.get("s") is not None else plan.get("s", 1.0)
        if m is None:
            out[name] = {"hop": e["hop"], "ok": False, "why": "no samples with all clients present and bg on"}
            continue
        good = abs(m["load"] - u_e) <= vg.LOAD_TOL and m["share"] is not None and abs(m["share"] - s_e) <= vg.SHARE_TOL
        out[name] = {"hop": e["hop"], "load": round(m["load"], 3), "U": u_e, "share": round(m["share"], 3) if m["share"] else None,
                     "s": s_e, "seconds": round(m["seconds"]), "ok": good}
    raw = json.loads((rd / "v3-checks.json").read_text())["1_load_share"] if (rd / "v3-checks.json").exists() else {}
    return {"run": rd.name, "ok": all(v["ok"] for v in out.values()), "egress": out, "raw_ok": raw.get("ok")}


def main(argv):
    runs = [Path(a) for a in argv]
    lines = ["# Check 1 with all planned clients present and the background on (2026-11-17)", "",
             "Raw check 1 stays in each run's v3-checks.json; this is the restricted evaluation. Code: "
             "[loadshare_present.py](loadshare_present.py).", "",
             "| run | raw check 1 | restricted check 1 | egress: load / U, share / s, seconds used |", "|---|---|---|---|"]
    for rd in runs:
        r = check(rd)
        eg = "; ".join(f"{n} {v.get('load')} / {v.get('U')}, {v.get('share')} / {v.get('s')}, {v.get('seconds')} s"
                       if "load" in v else f"{n} {v['why']}" for n, v in r["egress"].items())
        lines.append(f"| {r['run']} | {'ok' if r['raw_ok'] else 'FAIL'} | {'ok' if r['ok'] else 'FAIL'} | {eg} |")
    out = Path(__file__).resolve().parent / "loadshare-present.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:])
