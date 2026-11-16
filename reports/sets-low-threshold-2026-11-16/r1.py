#!/usr/bin/env python3
"""R1: grouping on lower detector on-thresholds (replay on the existing v3 runs; nothing frozen changes).

    nice -n 19 .venv/bin/python3 reports/sets-low-threshold-2026-11-16/r1.py rows [--jobs 4]   # rows.jsonl
    .venv/bin/python3 reports/sets-low-threshold-2026-11-16/r1.py report > tables.md
    .venv/bin/python3 reports/sets-low-threshold-2026-11-16/r1.py plots                        # 3 timelines

Onset sources (off = on / 2, the frozen span rule; P): T100 0.25 (frozen), T75 0.1875, T50 0.125, T25 0.0625.
The frozen detector's score is recomputed from the run's saved tick files (shadow_v2_frozen.episodes, v2 OWD,
hold); only shadow_v2_step3.THETA_ON is set to the level for that call. The onset log is built by the frozen
grouping adapter (grouping_adapter.build, source "v2-owd", warm-up det_eval.WARMUP_S, the run's ECG config),
exactly as the frozen grouping-d150-v2-owd/onsets.jsonl, and replayed through the frozen SetsEngine.

Variants: V0 frozen SETS on T100; V1 frozen SETS on T75 / T50 / T25 onsets only; V2 "weak confirms strong" on
T75 / T50 / T25: the frozen table and groups, a group reported only if at least one observation counting toward
it (frozen rule: |S'-S| <= extra and |S-S'| <= qmiss(|S|, m)) is strong. Strong observation (T): the event has a
member whose episode at this level contains a T100 alarm start of the same flow.
Scoring: grouping_score.Score / truth_sets / strict_hot unchanged, at every event close.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
LEVELS = {"T100": 0.25, "T75": 0.1875, "T50": 0.125, "T25": 0.0625}   # (P)
CALM_BLOCKS = ("C1a", "C1b")
KEY_TICK_S = 0.033          # (S) one tick
GOP_S = 1.0                 # (S) phase 0 for every client (synchronized keyframes)
MISS_WIN_S = 0.3            # (M) = delta_max: "onset in a neighbouring event"
STIM_TAIL_S = 2.0           # (M) as grouping_score
ROWS = HERE / "rows.jsonl"


# ---------------------------------------------------------------- per run

def onsets_at(rd: Path, th: float):
    import det_eval as d
    import grouping_adapter as ga
    import shadow_v2_step3 as s3
    from grouping import Config
    m = json.loads((rd / "grouping-d150-v2-owd" / "metrics.json").read_text()) \
        if (rd / "grouping-d150-v2-owd" / "metrics.json").exists() else None
    cfg = Config.from_dict(m["config"]) if m else Config()
    keep = s3.THETA_ON
    s3.THETA_ON = th
    try:
        records, _, onsets = ga.build(rd, cfg, 0.0, d.WARMUP_S, 0.0, "v2-owd")
    finally:
        s3.THETA_ON = keep
    return cfg, records, onsets


def topo_sets(plan: dict) -> dict:
    """egress name -> (level, clients) from the plan (shaped egresses)."""
    import grouping_score as gs
    return {n: (gs.LEVEL(n), frozenset(set(e["clients"]) - {gs.CTRL})) for n, e in plan["egress"].items()
            if e.get("shaped", True)}


def classify_set(members: frozenset, topo: dict, hot: set) -> str:
    leaves = [c for n, (lv, c) in topo.items() if lv == "leaf"]
    if any(members <= c for c in leaves):
        return "leaf"
    ups = [n for n, (lv, c) in topo.items() if lv != "leaf" and members <= c]
    if any(n in hot for n in ups) or (ups and not hot):
        return "upstream"
    return "coincidence"


def run_level(rd: Path, level: str, strong_eps: dict | None) -> dict:
    import det_eval as d
    import grouping_adapter as ga
    import grouping_score as gs
    from grouping import sets as S
    from grouping.sets_engine import replay_records
    plan = json.loads((rd / "v3-plan.json").read_text())
    run = d.Run(rd)
    cfg, records, onsets = onsets_at(rd, LEVELS[level])
    calm = plan["block"] in CALM_BLOCKS
    clients = sorted({c for e in plan["egress"].values() for c in e["clients"]} - {gs.CTRL})
    topo = topo_sets(plan)
    hop_name = {e["hop"]: n for n, e in plan["egress"].items()}
    geps = {hop_name[h]: v for h, v in ga.gt1_hop_episodes(run).items() if h in hop_name}
    wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    ts = gs.truth_sets(rd, run, plan) if not calm else {}
    eps = defaultdict(list)
    for o in onsets:
        eps[o["flow"]].append((o["t_arrival"], o["end"], o["t_onset"]))

    def episode_strong(flow, t_arr):
        if strong_eps is None:
            return True
        for a, b, _ in eps[flow]:
            if a <= t_arr <= b + 1e-9:
                return any(a - 1e-9 <= x <= b + 1e-9 for x in strong_eps.get(flow, []))
        return False

    sc = {(v, k): gs.Score(ts, clients) for v in ("V", "V2") for k in (2, 3)} if not calm else {}
    strong = Counter()
    ev_rows = []
    final = {}

    def hot_at(t0):
        names = gs.strict_hot(geps, t0 + gs.NEG_SPAN[0], t0 + gs.NEG_SPAN[1])
        return {gs.LEVEL(n) for n in names}, names

    def v2_filter(eng, groups):
        if strong_eps is None:
            return groups
        m, _ = S.estimate_m(eng.table, eng.scfg)
        out = []
        for g in groups:
            gm = frozenset(g.members)
            q = S.qmiss(len(gm), m, eng.scfg)
            if any(strong[t] > 0 and len(t - gm) <= eng.scfg.extra and len(gm - t) <= q for t in eng.table):
                out.append(g)
        return out

    def on_close(eng, e):
        members = frozenset(m.flow for m in e.members) - {gs.CTRL}
        is_strong = any(episode_strong(m.flow, m.t_arrival) for m in e.members if m.flow != gs.CTRL)
        if len(members) >= eng.scfg.min_set:
            strong[members] += int(is_strong)
        hl, hn = hot_at(e.t0)
        on = [m.t_arrival for m in e.members if m.flow != gs.CTRL]
        t_on = {m.flow: next((x for a, b, x in eps[m.flow] if abs(a - m.t_arrival) < 1e-6), m.t_arrival)
                for m in e.members if m.flow != gs.CTRL}
        phase = [((x % GOP_S) + GOP_S / 2) % GOP_S - GOP_S / 2 for x in t_on.values()]
        key = sum(abs(p) <= KEY_TICK_S for p in phase) > len(phase) / 2 if phase else False
        in_win = any(w["start"] - 1.0 <= e.t0 <= w["end"] + STIM_TAIL_S for w in wins)
        # missed members (Step 10 style): clients behind a hot leaf egress not in the event
        missed = []
        for n in hn:
            if n in topo and topo[n][0] == "leaf":
                for c in topo[n][1] - members:
                    already = any(a < e.t0 - 1e-9 and b >= e.t0 for a, b, _ in eps[c])
                    split = any(abs(x - e.t0) <= MISS_WIN_S for a, b, x in eps[c]) and not already
                    missed.append("already in alarm" if already else "split event" if split else "other")
        ev_rows.append({"t0": round(e.t0, 3), "n": len(members), "strong": bool(is_strong), "key": bool(key),
                        "in_window": bool(in_win),
                        "set": classify_set(members, topo, hn) if len(members) >= 2 else "single",
                        "missed": missed})
        if not calm:
            for k in (2, 3):
                gr = eng.groups(k)
                sc[("V", k)].close(eng.now, hl, hn, [frozenset(g.members) for g in gr])
                sc[("V2", k)].close(eng.now, hl, hn, [frozenset(g.members) for g in v2_filter(eng, gr)])
        final["eng"] = eng

    replay_records(records, cfg, exclude={gs.CTRL}, on_close=on_close)
    out = {"run": rd.name, "cell": rd.name.rsplit("-r", 1)[0][3:], "block": plan["block"], "aqm": plan["aqm"],
           "rep": plan["rep"], "level": level, "calm": calm, "duration": run.duration, "n_clients": len(clients),
           "n_onsets": len([o for o in onsets if o["flow"] != gs.CTRL]), "events": ev_rows,
           "first_stim": {n: min((w["start"] for w in wins if w.get("target") == n), default=None) for n in topo}}
    if not calm:
        out["truth"] = ts
        out["methods"] = {f"{v} k{k}": s.summary() for (v, k), s in sc.items()}
    eng = final.get("eng")
    if eng is not None:
        out["n_sets"] = len(eng.table)
        out["final"] = {}
        for k in (2, 3):
            gr = eng.groups(k)
            for v, gg in (("V", gr), ("V2", v2_filter(eng, gr))):
                out["final"][f"{v} k{k}"] = [{"members": list(g.members), "support": g.support,
                                              "kind": classify_set(frozenset(g.members), topo, set())} for g in gg]
    out["late"] = late_joiner(rd, plan, cfg, records, ts, eps, strong_eps) if not calm else []
    return out


def late_joiner(rd, plan, cfg, records, ts, eps, strong_eps) -> list[dict]:
    """grouping_score's late joiner, SETS only (V; V2 is the same replay with the strong filter not applied)."""
    import grouping_score as gs
    from grouping.sets_engine import replay_records
    late = []
    for n, info in ts.items():
        if info["level"] != "leaf" or len(info["members"]) < 3:
            continue
        L = frozenset(info["members"])
        hid = max(info["members"])
        rest = L - {hid}
        for k in (2, 3):
            st = {"rel": None, "join": None, "x": 0}

            def check(groups, t):
                st["x"] += 1
                if st["join"] is not None:
                    return
                if st["rel"] is None:
                    if any(gs._f1(g, rest)[2] >= gs.F1_OK for g in groups):
                        st["rel"] = (st["x"], t)
                elif any(hid in g and gs._f1(g, L)[2] >= gs.F1_OK for g in groups):
                    st["join"] = (st["x"], t)
            hide = lambda eng, o: o.flow == hid and st["rel"] is None   # noqa: E731
            replay_records(records, cfg, exclude={gs.CTRL}, hide=hide,
                           on_close=lambda eng, e: check([frozenset(g.members) for g in eng.groups(k)], eng.now))
            rec = {"leaf": n, "method": f"V k{k}", "released": st["rel"] is not None, "joined": st["join"] is not None}
            if st["rel"] and st["join"]:
                rec.update(events=st["join"][0] - st["rel"][0], seconds=st["join"][1] - st["rel"][1])
            late.append(rec)
    return late


def run_all_levels(rd: Path) -> list[dict]:
    try:
        _, _, on100 = onsets_at(rd, LEVELS["T100"])
        strong = defaultdict(list)
        for o in on100:
            strong[o["flow"]].append(o["t_arrival"])
        rows = []
        for lv in LEVELS:
            rows.append(run_level(rd, lv, None if lv == "T100" else strong))
        return rows
    except Exception as e:   # noqa: BLE001
        import traceback
        return [{"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2500:]}]


def runs() -> list[Path]:
    import grouping_score as gs
    out = gs.runs_of(KDIR)
    out += [p for p in sorted(KDIR.iterdir()) if p.is_dir() and p.name.startswith("v3-") and p.name.split("-")[1]
            in CALM_BLOCKS]
    return out


def cmd_rows(jobs: int) -> None:
    rs = runs()
    print(f"{len(rs)} runs x {len(LEVELS)} levels", flush=True)
    with ROWS.open("w") as fh, Pool(jobs) as pool:
        for i, rows in enumerate(pool.imap_unordered(run_all_levels, rs), 1):
            for r in rows:
                fh.write(json.dumps(r, default=str) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {rows[0]['run']}{' ERROR ' + rows[0]['error'] if 'error' in rows[0] else ''}",
                  flush=True)


def main(argv: list[str]) -> int:
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 4)
    elif argv[0] == "report":
        import r1_report
        r1_report.report(ROWS)
    elif argv[0] == "plots":
        import r1_report
        r1_report.plots(ROWS)
    elif argv[0] == "one":
        for r in run_all_levels(KDIR / argv[1]):
            print(json.dumps({k: v for k, v in r.items() if k not in ("events", "truth", "methods", "final", "late")},
                             default=str)[:600])
            if "error" in r:
                print(r["tb"])
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main(sys.argv[1:]))
