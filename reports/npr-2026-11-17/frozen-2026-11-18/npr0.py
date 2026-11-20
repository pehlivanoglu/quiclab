#!/usr/bin/env python3
"""NPR STEP 0: do the assumptions of a profile-based grouping hold? Replay only; the frozen detector and frozen SETS
are not changed. Truth is used for evaluation only.

    nice -n 19 .venv/bin/python3 reports/npr-step0-2026-11-17/npr0.py rows [--jobs 2]   # rows.jsonl
    .venv/bin/python3 reports/npr-step0-2026-11-17/npr0.py report > tables.md

Runs: v3 stimulus runs (calm C1a / C1b excluded) and K1 blocks G1-G3, A4-A7.

Matrix X (client x event). Events = the frozen event formation: SetsEngine (grouping.sets_engine.replay_records,
frozen Config) on the frozen v2-owd onset log (grouping_adapter.build, source "v2-owd", as R1 T100); one event per
close, t0 = its anchor. Clients = the run's subscribers (sessions) minus sub-ctrl.
  1  = an event member;
  NA = not a member and could not produce a new onset (first match wins, in this order):
       "absent"   the session had not joined or had left at t0 (grouping_adapter.sessions_of);
       "no-ack"   no ACK received by the sender for it in [t0 - DELTA_S, t0 + CLOSE_S] (acks.csv);
       "in-alarm" an onset episode of it (t_onset, end) started before t0 - DELTA_S and is still on at t0 (its onset
                  belongs to another event; t_onset as the frozen formation anchors events on it);
  0  = otherwise.
Truth per event: hot egresses = grouping_score.strict_hot on GT1 hop episodes over t0 + NEG_SPAN (the common
scorer's rule); leaves and upper sets = grouping_score.truth_sets. A leaf is "on" when it or an egress whose set
contains it is hot (FLAG: the model's "leaf on"; per-flow queues make this weaker, fq cells reported apart).

The frozen tick files (shadow_v2_frozen.tick_files) are built under CACHE, never inside a run folder.
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

V3 = ROOT / ".runs" / "2026-11-14_1818_v3"
K1 = ROOT / ".runs" / "2026-11-16_0105_v4-K1"
K1_BLOCKS = ("G1", "G2", "G3", "A4", "A5", "A6", "A7")
CALM_BLOCKS = ("C1a", "C1b")
DELTA_S = 0.15              # (T) frozen event formation: +-150 ms around t0
CLOSE_S = 1.3               # (T) frozen event formation: close at t0 + 1.3 s
CACHE = HERE / "cache"      # tick files of runs that have none (K1)
ROWS = HERE / "rows.jsonl"


def _patch_tick_files():
    """shadow_v2_frozen.tick_files, with its output under CACHE / <campaign> / <run> instead of the run folder."""
    import tempfile

    import det_eval as d
    import owd_mode
    import shadow_v2_frozen as fz
    import shadow_v2_step1 as s1

    def tick_files(run, mode):
        owd = mode == "OWD"
        base = run.path / "shadow-v2"
        if not (base / ("ticks-frozen-owd" if owd else "ticks-frozen")).exists():
            base = CACHE / run.path.parent.name / run.path.name / "shadow-v2"
        out = base / ("ticks-frozen-owd" if owd else "ticks-frozen")
        files = {s: out / f"{s}.csv" for s in run.subs}
        if all(f.exists() for f in files.values()):
            return files
        if base.is_relative_to(run.path):
            raise RuntimeError(f"refusing to build tick files inside {run.path}")
        dump = base / ("v1-samples-owd" if owd else "v1-samples")
        if not all((dump / f"{s}.csv").exists() for s in run.subs):
            with tempfile.TemporaryDirectory() as tmp:
                acks = {s: owd_mode.owd_acks(run, s, Path(tmp)) for s in run.subs} if owd else None
                d.replay(run, d.TUNED, samples_to=dump, acks=acks, grouping="none")
        out.mkdir(parents=True, exist_ok=True)
        no_truth = np.zeros(1, dtype=int)
        for s, f in files.items():
            rate = run.topology["subscribers"][s]["rate_kbps"] * 1000
            s1.ticks_for(run, s, dump, no_truth, rate, s1.tick_s(run)).to_csv(f, index=False)
        return files

    fz.tick_files = tick_files


def ack_times(run, s) -> np.ndarray:
    import pandas as pd
    f = run.sender_file(s, "acks")
    if not f.exists():
        return np.array([])
    a = pd.read_csv(f, usecols=["mono_us"])
    return np.sort(np.array([run.t_mono_us(x) for x in a.mono_us.values]))


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
    import r1
    from grouping.sets_engine import replay_records
    _patch_tick_files()
    plan = json.loads((rd / "v3-plan.json").read_text())
    run = d.Run(rd)
    cfg, records, onsets = r1.onsets_at(rd, r1.LEVELS["T100"])
    sess = ga.sessions_of(run)
    clients = sorted(s for s in run.subs if s != gs.CTRL)
    ts = gs.truth_sets(rd, run, plan)
    hop_name = {e["hop"]: n for n, e in plan["egress"].items()}
    geps = {hop_name[h]: v for h, v in ga.gt1_hop_episodes(run).items() if h in hop_name}
    acks = {s: ack_times(run, s) for s in clients}
    eps = {s: [] for s in clients}
    for o in onsets:
        if o["flow"] in eps:
            eps[o["flow"]].append((o["t_onset"], o["end"]))
    events = []

    def on_close(eng, e):
        t0 = e.t0
        ones = sorted({m.flow for m in e.members} - {gs.CTRL})
        na = {}
        for c in clients:
            if c in ones:
                continue
            j, lv = sess.get(c, (0.0, None))
            if t0 < j or (lv is not None and t0 >= lv):
                na[c] = "absent"
                continue
            a = acks[c]
            k = np.searchsorted(a, t0 - DELTA_S)
            if not (k < len(a) and a[k] <= t0 + CLOSE_S):
                na[c] = "no-ack"
                continue
            if any(x < t0 - DELTA_S and y >= t0 for x, y in eps[c]):
                na[c] = "in-alarm"
        hot = sorted(gs.strict_hot(geps, t0 + gs.NEG_SPAN[0], t0 + gs.NEG_SPAN[1]))
        events.append({"t0": round(t0, 4), "ones": ones, "na": na, "hot": hot})

    replay_records(records, cfg, exclude={gs.CTRL}, on_close=on_close)
    return {"run": rd.name, "campaign": rd.parent.name, "block": plan["block"], "type": plan["type"],
            "variant": plan.get("variant"), "aqm": plan["aqm"], "rep": plan["rep"], "topology": plan.get("topology"),
            "clients": clients, "truth": {n: {"members": sorted(v["members"]), "level": v["level"]} for n, v in ts.items()},
            "events": events}


def runs() -> list[Path]:
    out = [p for p in sorted(V3.iterdir()) if p.is_dir() and p.name.startswith("v3-") and (p / "events.csv").exists()
           and p.name.split("-")[1] not in CALM_BLOCKS]
    out += [p for p in sorted(K1.iterdir()) if p.is_dir() and p.name.startswith("v4-")
            and p.name.split("-")[1] in K1_BLOCKS and (p / "events.csv").exists()]
    return out


def cmd_rows(jobs: int, only: str | None) -> None:
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}")]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rs = [r for r in runs() if (not only or only in r.name) and r.name not in done]
    print(f"{len(rs)} runs ({len(done)} already done)", flush=True)
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(worker, rs), 1):
            fh.write(json.dumps(row, default=lambda o: None if (isinstance(o, float) and not math.isfinite(o))
                                else (o.tolist() if hasattr(o, "tolist") else str(o))) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {row['run']}{' ERROR ' + row['error'] if 'error' in row else ''}", flush=True)


def main(argv: list[str]) -> int:
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2,
                 argv[argv.index("--only") + 1] if "--only" in argv else None)
    elif argv[0] == "one":
        p = V3 / argv[1] if (V3 / argv[1]).exists() else K1 / argv[1]
        row = worker(p)
        if "error" in row:
            print(row["tb"])
        else:
            print(len(row["events"]), "events;", row["truth"])
            for e in row["events"][:6]:
                print(e)
    elif argv[0] == "report":
        import npr0_report
        npr0_report.report(ROWS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
