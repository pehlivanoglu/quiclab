#!/usr/bin/env python3
"""NPR STEP 0b: event formation candidates (replay, the STEP 0 runs; nothing frozen changes).

    nice -n 19 .venv/bin/python3 reports/npr-step0b-2026-11-17/npr0b.py rows [--jobs 2]   # rows.jsonl
    .venv/bin/python3 reports/npr-step0b-2026-11-17/npr0b.py report > tables.md

Onsets: the frozen v2-owd onset log (grouping_adapter.build, as STEP 0). Aligned onset time t_al = t_onset - mrtt/2
(the frozen Config's align_mode "half_mrtt", mrtt from the log's meta records); alarm episode of an onset =
[t_al, end - mrtt/2] (the same shift).
Candidates (the note's fixed list):
  E0     frozen SetsEngine events (replay_records, frozen Config): |t_al - t0| <= 0.150 s, close t0 + 0.3 + 1.0 s.
  E1-W   t0 = the first onset; later onsets with t_al in [t0, t0 + W] join, W in {0.5, 1, 2} s.
  E2     an onset joins the open event if at least one member is still in alarm at its t_al; otherwise the event
         closes and the onset opens a new one. The event closes when every member is out of alarm (no cap, FLAG).
  E3     as E2 with more than half of the members still in alarm; closes when at most half are.
  E4-W   E0 events; a non-member whose onset lies in another E0 event with |t_al - t0| <= W is NA ("split"),
         W in {1, 2} s.
  Common: a flow is a member of an event at most once; an onset of a flow that is already a member opens a new
  event (E1-E3; FLAG, rare). Onsets are taken in t_al order (offline; the frozen engine is causal on arrival).
NA (STEP 0 rules): absent / no ACK in [t0 - 0.15 s, close] / in alarm at the event's opening (E0, E4: episode
started before t0 - 0.15 s; E1-E3: before t0) and still on at t0. Truth: strict_hot over t0 + NEG_SPAN (STEP 0).
Per event also: close time, last join (t_al and arrival), the E0 events it absorbs (E0 t0 in [t0, close]), and
"mixed" = members from two leaves that share no egress with a GT1 episode overlapping [t0, close] (truth).
0b.4: T-BASE 4-member leaf, E0 events with no hot egress and all four members 1: GT1 / GT3 / GT-Q around t0, the
frozen F1 (queue delay, ms) of the members, the onset phase in the GOP.
"""

from __future__ import annotations

import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reports" / "sets-low-threshold-2026-11-16"))
sys.path.insert(0, str(ROOT / "reports" / "npr-step0-2026-11-17"))

DELTA_S, CLOSE_S = 0.15, 1.3            # (T) frozen formation
CANDS = ("E0", "E1-0.5", "E1-1", "E1-2", "E2", "E3", "E4-1", "E4-2")
ROWS = HERE / "rows.jsonl"


def form_window(ons, W):
    """E1: anchored window after the first onset."""
    ev, cur = [], None
    for o in ons:
        if cur is not None and o["t"] <= cur["t0"] + W and o["flow"] not in cur["m"]:
            cur["m"][o["flow"]] = o
            continue
        if cur is not None:
            ev.append(cur)
        cur = {"t0": o["t"], "m": {o["flow"]: o}}
    if cur is not None:
        ev.append(cur)
    for e in ev:
        e["close"] = e["t0"] + W
    return ev


def _close_at(m: dict, majority: bool) -> float:
    ends = sorted((o["e"] for o in m.values()), reverse=True)
    return ends[len(ends) // 2] if majority else ends[0]


def form_while(ons, majority):
    """E2 (any member in alarm) / E3 (more than half of the members in alarm)."""
    ev, cur = [], None
    for o in ons:
        if cur is not None and o["flow"] not in cur["m"] and o["t"] <= _close_at(cur["m"], majority):
            cur["m"][o["flow"]] = o
            continue
        if cur is not None:
            cur["close"] = _close_at(cur["m"], majority)
            ev.append(cur)
        cur = {"t0": o["t"], "m": {o["flow"]: o}}
    if cur is not None:
        cur["close"] = _close_at(cur["m"], majority)
        ev.append(cur)
    return ev


def gtq_classifier(rd, run):
    """Frozen gtq_score rule per alarm start (score_run): "tp" inside an episode collar [t0 - W, t1 + d_obs + W],
    "gray" inside a gray span, "fp" otherwise; forward episodes of the same flow. v3: the run's frozen truth files;
    K1 (no truth file yet): gtq.run_truth in memory, if gtq.validity passes. None when GT-Q is not usable.
    Each start is classified on its own (score_run first merges starts closer than W; FLAG)."""
    import det_eval as d
    import gtq
    f = rd / "truth" / "gtq.csv"
    if f.exists():
        eps = d.rows(f)
        g = rd / "truth" / "gtq-gray.csv"
        gray = d.rows(g) if g.exists() else []
    else:
        ok, _ = gtq.validity(rd)
        if not ok:
            return None
        eps, gray, _, _ = gtq.run_truth(run)
    fl = lambda v: float("nan") if v in ("", None) else float(v)   # noqa: E731
    col, gr = {}, {}
    for e in eps:
        if e["direction"] != "forward":
            continue
        W, dobs = fl(e["W_ms"]) / 1e3, fl(e["d_obs_ms"]) / 1e3
        col.setdefault(e["flow"], []).append((fl(e["t0"]) - W, fl(e["t1"]) + (0 if math.isnan(dobs) else dobs) + W))
    for x in gray:
        if x["direction"] == "forward":
            gr.setdefault(x["flow"], []).append((fl(x["t_start"]), fl(x["t_end"])))

    def cls(flow, t):
        if any(a <= t <= b for a, b in col.get(flow, [])):
            return "tp"
        if any(a <= t <= b for a, b in gr.get(flow, [])):
            return "gray"
        return "fp"
    return cls


def worker(rd: Path) -> dict:
    try:
        return _worker(rd)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path) -> dict:
    import det_eval as d
    import grouping_adapter as ga
    import grouping_score as gs
    import npr0
    import r1
    from grouping.sets_engine import replay_records
    npr0._patch_tick_files()
    plan = json.loads((rd / "v3-plan.json").read_text())
    run = d.Run(rd)
    cfg, records, onsets = r1.onsets_at(rd, r1.LEVELS["T100"])
    half = {}
    for kind, _t, obj in records:
        if kind == "meta":
            half[obj.flow] = getattr(obj, "mrtt", 0.0) / 2 if cfg.align_mode == "half_mrtt" else 0.0
    sess = ga.sessions_of(run)
    clients = sorted(s for s in run.subs if s != gs.CTRL)
    ts = gs.truth_sets(rd, run, plan)
    T = {n: set(v["members"]) for n, v in ts.items()}
    leaves = {n for n, v in ts.items() if v["level"] == "leaf"}
    leaf_of = {c: n for n in leaves for c in T[n]}
    hop_name = {e["hop"]: n for n, e in plan["egress"].items()}
    geps = {hop_name[h]: v for h, v in ga.gt1_hop_episodes(run).items() if h in hop_name}
    acks = {s: npr0.ack_times(run, s) for s in clients}
    qcls = gtq_classifier(rd, run)
    ons = sorted(({"flow": o["flow"], "t": o["t_onset"] - half.get(o["flow"], 0.0),
                   "e": o["end"] - half.get(o["flow"], 0.0), "arr": o["t_arrival"]}
                  for o in onsets if o["flow"] in acks), key=lambda o: (o["t"], o["flow"]))
    eps = {c: [(o["t"], o["e"]) for o in ons if o["flow"] == c] for c in clients}

    def na_of(t0, close, members, pre):
        na = {}
        for c in clients:
            if c in members:
                continue
            j, lv = sess.get(c, (0.0, None))
            if t0 < j or (lv is not None and t0 >= lv):
                na[c] = "absent"
                continue
            a = acks[c]
            k = np.searchsorted(a, t0 - DELTA_S)
            if not (k < len(a) and a[k] <= close):
                na[c] = "no-ack"
                continue
            if any(x < t0 - pre and y >= t0 for x, y in eps[c]):
                na[c] = "in-alarm"
        return na

    def mixed(members, t0, close):
        ls = sorted({leaf_of[c] for c in members if c in leaf_of})
        for i, a in enumerate(ls):
            for b in ls[i + 1:]:
                common = [n for n, s in T.items() if T[a] <= s and T[b] <= s]
                if not any(x < close and y > t0 for n in common for x, y in geps.get(n, [])):
                    return True
        return False

    # E0: frozen engine events
    e0 = []

    def on_close(eng, e):
        mem = {}
        for m in e.members:
            if m.flow == gs.CTRL:
                continue
            mem[m.flow] = {"flow": m.flow, "t": m.t_al, "arr": m.t_arrival}
        e0.append({"t0": e.t0, "m": mem, "close": eng.now})

    replay_records(records, cfg, exclude={gs.CTRL}, on_close=on_close)
    e0.sort(key=lambda e: e["t0"])
    forms = {"E0": e0, "E1-0.5": form_window(ons, 0.5), "E1-1": form_window(ons, 1.0), "E1-2": form_window(ons, 2.0),
             "E2": form_while(ons, False), "E3": form_while(ons, True)}
    t0s = np.array([e["t0"] for e in e0])
    out = {}
    for name in CANDS:
        base = forms["E0"] if name.startswith("E4") else forms[name]
        W = float(name.split("-")[1]) if name.startswith("E4") else None
        evs = []
        for i, e in enumerate(base):
            if not e["m"]:
                continue                                   # an E0 event of sub-ctrl only
            t0, close = e["t0"], e["close"]
            members = set(e["m"])
            pre = DELTA_S if name in ("E0", "E4-1", "E4-2") else 0.0
            na = na_of(t0, close, members, pre)
            if W is not None:
                for j, f in enumerate(base):
                    if j == i or abs(f["t0"] - t0) > W:
                        continue
                    for c, o in f["m"].items():
                        if c not in members and abs(o["t"] - t0) <= W and c not in na:
                            na[c] = "split"
            hot = sorted(gs.strict_hot(geps, t0 + gs.NEG_SPAN[0], t0 + gs.NEG_SPAN[1]))
            row = {"t0": round(t0, 4), "close": round(close, 4), "ones": sorted(members), "na": na, "hot": hot,
                   "last_join": round(max(o["t"] for o in e["m"].values()), 4),
                   "last_arr": round(max(o["arr"] for o in e["m"].values()), 4),
                   "mixed": mixed(members, t0, close),
                   "q": {c: qcls(c, o["arr"]) for c, o in e["m"].items()} if qcls else None}
            if not name.startswith("E0") and not name.startswith("E4"):
                row["absorbs"] = int(((t0s >= t0 - 1e-9) & (t0s <= close + 1e-9)).sum())
            evs.append(row)
        out[name] = evs
    probe = probe_04(rd, run, plan, ts, e0, out["E0"], geps, half) if plan.get("topology") == "base" else []
    return {"run": rd.name, "campaign": rd.parent.name, "block": plan["block"], "type": plan["type"],
            "variant": plan.get("variant"), "aqm": plan["aqm"], "rep": plan["rep"], "topology": plan.get("topology"),
            "clients": clients, "duration": run.duration,
            "truth": {n: {"members": sorted(v["members"]), "level": v["level"]} for n, v in ts.items()},
            "cands": out, "probe": probe}


def probe_04(rd, run, plan, ts, e0, rows, geps, half):
    """0b.4: E0 events on a 4-member leaf with no hot egress and all members 1."""
    import pandas as pd

    import det_eval as d
    import gt3
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import grouping_score as gs
    leaves = [n for n, v in ts.items() if v["level"] == "leaf" and len(v["members"]) == 4]
    if not leaves:
        return []
    L = set(ts[leaves[0]]["members"])
    cand = [(e, r) for e, r in zip(e0, rows) if not r["hot"] and L <= set(r["ones"])]
    if not cand:
        return []
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    view = gt3.view_of(run, eb, lb, need_path=True)
    gq = d.rows(rd / "truth" / "gtq.csv") if (rd / "truth" / "gtq.csv").exists() else []
    ticks = {s: s3.load_flow(f) for s, f in fz.tick_files(run, "OWD").items() if s in L}
    keys = {}
    for s in L:
        fr = pd.read_csv(run.sender_file(s, "frames"), usecols=["keyframe", "send_us"])
        keys[s] = np.sort(np.array([run.t_unix_us(x) for x in fr.send_us[fr.keyframe == 1].values]))
    hop = next(iter(plan["egress"].values()))["hop"]
    name = next(iter(plan["egress"]))
    out = []
    for e, r in cand:
        t0 = e["t0"]
        lo, hi = t0 + gs.NEG_SPAN[0], t0 + gs.NEG_SPAN[1]
        g1 = geps.get(name, [])
        cover = sum(max(0.0, min(b, hi) - max(a, lo)) for a, b in g1) / (hi - lo)
        g1_any = [(round(a, 3), round(b, 3)) for a, b in g1 if a < t0 + 1.5 and b > t0 - 0.5]
        g3 = {s: any(a < t0 + 1.5 and b > t0 - 0.5 for a, b in view.get(s, ([], None))[0]) for s in L}
        q = [x for x in gq if x["flow"] in L and x["direction"] == "forward"
             and float(x["t0"]) < t0 + 1.5 and float(x["t1"]) > t0 - 0.5]
        f1 = []
        for s in L:
            df = ticks[s]
            w = df[(df.t >= t0) & (df.t <= t0 + 1.5)]
            f1.append(float(np.nanmax(w.F1)) if len(w) and np.isfinite(w.F1).any() else float("nan"))
        ph = []
        for s, o in e["m"].items():
            k = keys[s]
            raw = o["t"] + half.get(s, 0.0)
            i = np.searchsorted(k, raw, side="right") - 1
            ph.append(float(raw - k[i]) if i >= 0 else float("nan"))
        out.append({"run": rd.name, "t0": round(t0, 3), "gt1_strict_cover": round(cover, 3), "gt1_episodes": g1_any,
                    "gt3_clients": sum(g3.values()), "gtq_episodes": len(q),
                    "gtq_max_sojourn_ms": max((float(x["max_sojourn_ms"]) for x in q), default=None),
                    "gtq_harmful_600": sum(x["harmful_600"] == "1" for x in q),
                    "f1_max_ms": [round(x, 1) for x in f1], "phase_s": [round(x, 3) for x in ph], "hop": hop})
    return out


def cmd_rows(jobs: int, only: str | None) -> None:
    import npr0
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}")]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rs = [r for r in npr0.runs() if (not only or only in r.name) and r.name not in done]
    print(f"{len(rs)} runs ({len(done)} already done)", flush=True)
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(worker, rs), 1):
            fh.write(json.dumps(row, default=lambda o: None if (isinstance(o, float) and not math.isfinite(o))
                                else (o.tolist() if hasattr(o, "tolist") else str(o))) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {row['run']}{' ERROR ' + row['error'] if 'error' in row else ''}", flush=True)


def main(argv: list[str]) -> int:
    import npr0
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2,
                 argv[argv.index("--only") + 1] if "--only" in argv else None)
    elif argv[0] == "one":
        p = npr0.V3 / argv[1] if (npr0.V3 / argv[1]).exists() else npr0.K1 / argv[1]
        row = worker(p)
        if "error" in row:
            print(row["tb"])
        else:
            for c, ev in row["cands"].items():
                print(c, len(ev), ev[:2])
            print("probe", row["probe"][:3])
    elif argv[0] == "report":
        import npr0b_report
        npr0b_report.report(ROWS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
