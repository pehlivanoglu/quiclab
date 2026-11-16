#!/usr/bin/env python3
"""Step 8 (2026-11-15): are the per-event observed sets the true nested sets, and do the true sets recur?
Measurement only on the v3 runs; the detector, ECG v1.2, h3 (step 4 replay, m = 3), the step 2 within-event
split (grouping_step3.partition_fixed) and the scoring helpers are called unchanged.

    .venv/bin/python3 reports/step8-2026-11-15/step8.py rows .runs/2026-11-14_1818_v3   # -> rows.jsonl
    .venv/bin/python3 reports/step8-2026-11-15/report.py > reports/step8-2026-11-15/tables.md

Per run and onset source (v2-owd, truth: ECG v1.2 output grouping-d150-<source>), per ECG event:
  observed set   the event's members (clients with an onset in it), sub-ctrl excluded;
  congested      shaped plan egresses whose queue-log episodes (diag.qlog_episodes: gt1's CoDel rule on the
                 per-packet trace) cover >= half of [t0 - 1, t0 + 2] (step 7 STRICT) (M); runs whose GT-Q
                 health is invalid use the GT1 episodes instead (FLAG; Q1: identical on pfifo / codel);
  truth set      union of the clients behind the congested egresses;
  true sets      "clients behind e" for every shaped plan egress (the nested family);
  split classes  partition_fixed on the observed clients' curves of that event (s2.events_of, ECG
                 intervals), class 0 dropped;
  closes         ECG groups with L >= A after each event (step 6 ecg_closes) and h3 groups (replay4, m = 3)
                 after each event.
fq_codel (E): per event also the clients behind the stimulated egress(es) whose own sub-queue has a
queue-log episode overlapping [t0 - 1, t0 + 2] (Q4 rule).
"""

from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "reports" / "v3-grouping-diag"))
import diag  # noqa: E402

s7, s6, s4, s3, s2, ga, d = diag.s7, diag.s6, diag.s4, diag.s3, diag.s2, diag.ga, diag.d
CELLS = ("v3-C7-", "v3-C8-", "v3-C9-", "v3-C10-", "v3-C11-", "v3-C13-", "v3-M7-")
SRC = {"v2-owd": "grouping-d150-v2-owd", "truth": "grouping-d150-truth"}
VIEWS = Path(os.environ.get("STEP8_VIEWS", "/tmp/claude-1001/-home-ubuntu-Research-Repos-multirelay/"
                            "5363924b-068f-4123-bf1c-f65ab759cae3/scratchpad/views8"))
CTRL = "sub-ctrl"


def view(rd: Path, src: str) -> Path:
    """Run folder whose grouping-d150-v2-owd is the source's ECG output (the step 4 / 6 readers use that name)."""
    if src == "v2-owd":
        return rd
    v = VIEWS / src / rd.name
    if not v.exists():
        v.mkdir(parents=True)
        real = rd.resolve()
        for p in real.iterdir():
            (v / p.name).symlink_to(real / SRC[src] if p.name == SRC["v2-owd"] else p)
    return v


def level_of(name: str) -> str:
    return {"root": "root", "X": "mid", "Y": "mid", "up": "up"}.get(name, "leaf")


def qlog(rd: Path, run, hops, fq: bool):
    valid = (rd / "truth" / "gtq-status.csv").exists() and d.rows(rd / "truth" / "gtq-status.csv")[0]["valid"] == "1"
    if not valid:
        g = ga.gt1_hop_episodes(run)
        return {h: g.get(h, []) for h in hops}, None, "gt1 (GT-Q invalid)"
    pc = {} if fq else None
    eps, _ = diag.qlog_episodes(run, set(hops), per_client=pc)
    return eps, pc, "qlog"


def run_src(rd: Path, src: str, Q, pc, fam, hop_of, plan):
    v = view(rd, src)
    run, truth, subs, windows, events = s4.load_events(v, ecg_intervals=True)
    leaf = {s: frozenset(x) for s, x in truth["leaf"].items() if x}
    same = truth["pairs_leaf"]
    m, evs, closes = s6.ecg_closes(v, run, leaf)
    by_lo = {round(e[0]["lo"], 6): e for e in events}
    st = diag.stimuli(rd)
    out = []
    for x, e in enumerate(evs):
        lo, hi = e["t0"] + s2.NEG_SPAN[0], e["t0"] + s2.NEG_SPAN[1]
        obs = sorted(set(e["members"]) - {CTRL})
        hot = sorted(n for n, h in hop_of.items() if s7.strict_hot({h: Q.get(h, [])}, lo, hi))
        ev = by_lo.get(round(lo, 6))
        classes = None
        if ev is not None:
            qs = {s: q for s, q in ev[1].items() if s in obs}
            if len(qs) >= 2:
                res = s3.partition_fixed(qs)
                classes = [sorted(c) for c in res["classes"]]
        row = {"x": x, "t0": e["t0"], "case": e.get("case"), "obs": obs, "hot": hot,
               "stim": sorted({s_["target"] for s_ in diag.stim_at(st, e["t0"])}),
               "classes": classes, "groups": [sorted(set(g) - {CTRL}) for g in closes[x].values()]}
        if pc is not None:
            tg = sorted({s_["hop"] for s_ in diag.stim_at(st, e["t0"])})
            row["fq_truth"] = sorted({c for h in tg for c in fam_by_hop(fam, hop_of, h)
                                      if any(a <= hi and b >= lo for a, b in pc.get(h, {}).get(c, []))})
            row["fq_targets"] = sorted(n for n, h in hop_of.items() if h in tg)
        out.append(row)
    h3 = []
    if events:
        h = s4.replay4(events, subs, same, leaf, 3, True)
        bb = round(h["b"], 2)
        for ev_, t in zip(events, h["traj"]):
            gs = [sorted(set(i for i, e_ in r_.items() if e_ >= bb) - {CTRL}) for r_ in t.values()]
            h3.append({"t0": ev_[0]["lo"] - s2.NEG_SPAN[0], "groups": [g for g in gs if g]})
    return {"events": out, "h3": h3, "n_ecg": len(evs)}


def fam_by_hop(fam, hop_of, h):
    for n, hh in hop_of.items():
        if hh == h:
            return fam[n]
    return []


def one(rd: Path):
    try:
        run = d.Run(rd)
        plan = json.loads((rd / "v3-plan.json").read_text())
        fam = {n: sorted(set(e["clients"]) - {CTRL}) for n, e in plan["egress"].items() if e.get("shaped", True)}
        hop_of = {n: plan["egress"][n]["hop"] for n in fam}
        fq = plan["aqm"] == "fq_codel"
        Q, pc, qsrc = qlog(rd, run, set(hop_of.values()), fq)
        out = {"run": rd.name, "cell": rd.name.rsplit("-r", 1)[0][3:], "block": plan["block"], "aqm": plan["aqm"],
               "rep": plan["rep"], "fam": fam, "levels": {n: level_of(n) for n in fam}, "queue_truth": qsrc,
               "clients": sorted(set(c for v in fam.values() for c in v))}
        for src in SRC:
            out[src] = run_src(rd, src, Q, pc, fam, hop_of, plan)
        return out
    except Exception as e:   # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-1500:]}


if __name__ == "__main__":
    kdir = Path(sys.argv[2])
    runs = [p for p in sorted(kdir.iterdir()) if p.is_dir() and p.name.startswith(CELLS)]
    with Pool(8) as pool, open(HERE / "rows.jsonl", "w") as fh:
        for r in pool.imap_unordered(one, runs):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
