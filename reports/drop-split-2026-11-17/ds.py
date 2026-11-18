#!/usr/bin/env python3
"""Pre-drop / post-drop split (existing v3 runs; nothing frozen changes).

    nice -n 19 .venv/bin/python3 reports/drop-split-2026-11-17/ds.py rows [--jobs 4] [--only NAME]   # rows.jsonl
    .venv/bin/python3 reports/drop-split-2026-11-17/ds.py report > tables.md

For every stimulus window (grouping/windows.json): t_drop = the first sender GOP-drop (publishers/pub/<sub>-drops.csv)
of any client behind the congested egress (window "expected", sub-ctrl excluded) in [start, end + TAIL_S]; none if
no drop. Window span = [start, end + TAIL_S] (TAIL_S = grouping_score's 2 s stimulus tail).

Each flow's time is put in one category by the windows that contain it and list the flow as expected:
  post   inside a window with a drop, at or after its t_drop
  pre    inside a window with a drop, before its t_drop
  nodrop inside a window without a drop
(priority post > pre > nodrop where windows overlap); "all" = any window span. Outside all windows: not scored.

Detectors: v2-owd (frozen), D2-gcc and D3-10ms-200ms (as R2, reports/detector-r2-2026-11-16/r2.py).
Scoring = gt_score.score's rules restricted to a category (unchanged otherwise):
  GT3 source B episodes counted when their onset is in the category; a TP alarm must start in
  [t_on - 1 s, min(end, t_on + 10 s)] and, for "pre", before t_drop; false alarms = unmatched starts in CLEAR cells
  of the category, per minute of the category's CLEAR time.
  GT-Q precision = gtq_score.score_run on the alarm starts that fall in the category (merging, collars and gray
  unchanged). GT-H = harmful GT-H 600 episodes whose t_harm_600 is in the category and is covered by an alarm span.
Grouping: the frozen SetsEngine replayed on the frozen v2-owd onset log (grouping_adapter.build, as R1 T100); the
common scorer grouping_score.Score is fed only the event closes whose t0 lies in the category (window membership
by t0 in [start - 1 s, end + TAIL_S], as grouping_score; the engine itself sees every event, unchanged).
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reports" / "detector-r2-2026-11-16"))
sys.path.insert(0, str(ROOT / "reports" / "sets-low-threshold-2026-11-16"))

KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
TAIL_S = 2.0                        # (M) grouping_score's stimulus tail
CATS = ("all", "nodrop", "pre", "post")
DETS = ("v2-owd", "D2-gcc", "D3-10ms-200ms")
ROWS = HERE / "rows.jsonl"


def first_drops(run, subs) -> dict[str, np.ndarray]:
    """Per client: sorted run-clock times of its sender drops."""
    import pandas as pd
    out = {}
    for s in subs:
        f = run.sender_file(s, "drops")
        if f.exists():
            t = pd.read_csv(f, usecols=["t_us"]).t_us.to_numpy()
            out[s] = np.sort(np.array([run.t_unix_us(x) for x in t])) if len(t) else np.array([])
        else:
            out[s] = np.array([])
    return out


def window_drops(wins, drops) -> list[dict]:
    out = []
    for w in wins:
        lo, hi = w["start"], w["end"] + TAIL_S
        exp = [c for c in w.get("expected", []) if c != "sub-ctrl"]
        td = math.inf
        for c in exp:
            d = drops.get(c, np.array([]))
            k = np.searchsorted(d, lo)
            if k < len(d) and d[k] <= hi:
                td = min(td, float(d[k]))
        out.append({**w, "lo": lo, "hi": hi, "clients": exp, "t_drop": None if td == math.inf else td})
    return out


def cat_of(wd, s, t, lo_pad=0.0):
    """Category of client s at time t (None outside every window that lists s)."""
    best = None
    rank = {"nodrop": 0, "pre": 1, "post": 2}
    for w in wd:
        if s not in w["clients"] or not (w["lo"] - lo_pad <= t <= w["hi"]):
            continue
        c = "nodrop" if w["t_drop"] is None else ("pre" if t < w["t_drop"] else "post")
        if best is None or rank[c] > rank[best]:
            best = c
    return best


def drop_limit(wd, s, t):
    """For a 'pre' time: the earliest t_drop among the drop windows of s containing t."""
    return min((w["t_drop"] for w in wd if s in w["clients"] and w["t_drop"] is not None and w["lo"] <= t <= w["hi"]),
               default=math.inf)


def in_cat(wd, s, t, c, lo_pad=0.0):
    x = cat_of(wd, s, t, lo_pad)
    return x is not None if c == "all" else x == c


def score_masked(run, view, starts, wd) -> dict:
    """gt_score.score's rules, restricted per category."""
    import det_eval as d
    import gt_bands
    import gt_score as g
    out = {c: {} for c in CATS}
    for name in DETS:
        tal = {c: {"episodes": 0, "tp": 0, "fp": 0, "clear_s": 0.0, "latency": []} for c in CATS}
        for s, (eps, code) in view.items():
            alarms = sorted(a for a in starts.get((name, s), []) if a >= d.WARMUP_S)
            k0 = int(d.WARMUP_S / g.GRID_S)
            for k in range(k0, len(code)):
                if code[k] == g.RANK[gt_bands.CLEAR]:
                    t = (k + 0.5) * g.GRID_S
                    for c in CATS:
                        if in_cat(wd, s, t, c):
                            tal[c]["clear_s"] += g.GRID_S
            used = set()
            for a, b in eps:
                if a < d.WARMUP_S:
                    continue
                lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
                hit = next((x for x in alarms if lo <= x <= hi), None)
                used.update(x for x in alarms if lo <= x <= hi)
                for c in CATS:
                    if not in_cat(wd, s, a, c):
                        continue
                    h = hit
                    if c == "pre":
                        lim = drop_limit(wd, s, a)
                        h = next((x for x in alarms if lo <= x <= min(hi, lim - 1e-9)), None)
                    tal[c]["episodes"] += 1
                    if h is not None:
                        tal[c]["tp"] += 1
                        tal[c]["latency"].append(max(0.0, h - a))
            for x in alarms:
                if x in used or any(a <= x <= b for a, b in eps):
                    continue
                if code[min(len(code) - 1, int(x / g.GRID_S))] != g.RANK[gt_bands.CLEAR]:
                    continue
                for c in CATS:
                    if in_cat(wd, s, x, c):
                        tal[c]["fp"] += 1
        for c in CATS:
            out[c][name] = tal[c]
    return out


def gtq_masked(rd, starts, wd) -> dict | None:
    import gtq
    import gtq_score
    if not (rd / "truth" / "gtq.csv").exists():
        return None
    gtq_score.DETECTORS = DETS
    keep = gtq.write
    gtq.write = lambda *a, **k: None   # never overwrite the run's truth/gtq-score-episodes.csv
    out = {}
    try:
        for c in CATS:
            st = {(n, s): [t for t in v if in_cat(wd, s, t, c)] for (n, s), v in starts.items()}
            res = gtq_score.score_run(rd, st)
            if res is None:
                return None
            agg = {n: [0, 0] for n in DETS}
            for t in res[1]:
                agg[t["detector"]][0] += t["alarms_matched"]
                agg[t["detector"]][1] += t["fp"]
            out[c] = agg
    finally:
        gtq.write = keep
    return out


def harm_masked(rd, spans, wd) -> dict:
    import det_eval as d
    out = {c: {n: [0, 0] for n in DETS} for c in CATS}
    if not (rd / "truth" / "gtq.csv").exists():
        return out
    for e in d.rows(rd / "truth" / "gtq.csv"):
        if e.get("direction") != "forward" or e.get("harmful_600") != "1":
            continue
        th, s = float(e["t_harm_600"]), e["flow"]
        if th < d.WARMUP_S:
            continue
        for c in CATS:
            if not in_cat(wd, s, th, c):
                continue
            for n in DETS:
                out[c][n][1] += 1
                out[c][n][0] += any(a <= th <= b for a, b in spans.get((n, s), []))
    return out


def grouping(rd, run, plan, wd) -> dict | None:
    import grouping_adapter as ga
    import grouping_score as gs
    import r1
    from grouping.sets_engine import replay_records
    if plan["block"] in r1.CALM_BLOCKS or not wd:
        return None
    cfg, records, onsets = r1.onsets_at(rd, r1.LEVELS["T100"])
    clients = sorted({c for e in plan["egress"].values() for c in e["clients"]} - {gs.CTRL})
    hop_name = {e["hop"]: n for n, e in plan["egress"].items()}
    geps = {hop_name[h]: v for h, v in ga.gt1_hop_episodes(run).items() if h in hop_name}
    ts = gs.truth_sets(rd, run, plan)
    sc = {(c, k): gs.Score(ts, clients) for c in CATS for k in (2, 3)}
    n_close = {c: 0 for c in CATS}

    def cat_t0(t0):
        # window membership of a close by t0 in [start - 1 s, end + tail]; a client-free view (any window)
        best, rank = None, {"nodrop": 0, "pre": 1, "post": 2}
        for w in wd:
            if not (w["start"] - 1.0 <= t0 <= w["hi"]):
                continue
            c = "nodrop" if w["t_drop"] is None else ("pre" if t0 < w["t_drop"] else "post")
            if best is None or rank[c] > rank[best]:
                best = c
        return best

    def on_close(eng, e):
        c0 = cat_t0(e.t0)
        if c0 is None:
            return
        names = gs.strict_hot(geps, e.t0 + gs.NEG_SPAN[0], e.t0 + gs.NEG_SPAN[1])
        hl = {gs.LEVEL(n) for n in names}
        for k in (2, 3):
            gr = [frozenset(g.members) for g in eng.groups(k)]
            for c in ("all", c0):
                sc[(c, k)].close(eng.now, hl, names, gr)
        n_close["all"] += 1
        n_close[c0] += 1

    replay_records(records, cfg, exclude={gs.CTRL}, on_close=on_close)
    # onsets SETS uses, inside a window of their own flow: before / after t_drop
    on_split = {"pre": 0, "post": 0, "nodrop": 0}
    for o in onsets:
        if o["flow"] == gs.CTRL:
            continue
        c = cat_of(wd, o["flow"], o["t_onset"], lo_pad=1.0)
        if c:
            on_split[c] += 1
    return {"methods": {f"{c} k{k}": s.summary() for (c, k), s in sc.items()}, "closes": n_close,
            "onsets": on_split}


def worker(rd: Path) -> dict:
    try:
        return _worker(rd)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path) -> dict:
    import det_eval as d
    import gt3
    import r2
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    r2._setup()
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    subs = [s for s in run.subs if s != "sub-ctrl"]
    wd = window_drops(wins, first_drops(run, subs))
    spans: dict = {}
    for s, df in r2.flows(run).items():
        r = s3.run_cusum(df, r2.FROZEN_LABEL, fz.FROZEN["OWD"]["g_ref"]["v2"], False)
        spans[("v2-owd", s)] = [(a, b) for a, b, _ in s5.on_spans(r, s3.THETA_ON)]
        spans[("D3-10ms-200ms", s)] = r2.d3(df)["D3-10ms-200ms"]
    for s in run.subs:
        spans[("D2-gcc", s)] = r2.d2(run, s)["D2-gcc"]
    starts = {k: [a for a, _ in v] for k, v in spans.items()}
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    view = gt3.view_of(run, eb, lb, need_path=True)
    # per window: first v2-owd alarm start of an expected client in [start - 1 s, hi]; before t_drop?
    wrows = []
    for w in wd:
        fa = min((a for c in w["clients"] for a in starts.get(("v2-owd", c), []) if w["start"] - 1.0 <= a <= w["hi"]),
                 default=None)
        wrows.append({k: w.get(k) for k in ("start", "end", "kind", "target", "u", "d", "hop", "stimulus_type",
                                             "concurrent", "t_drop")} | {"n_clients": len(w["clients"]),
                                                                          "first_alarm": fa})
    parts = rd.name.split("-")
    return {"run": rd.name, "block": parts[1], "type": parts[2], "variant": parts[3], "aqm": parts[4],
            "rep": int(parts[5][1:]), "cc": "copa" if "copa" in rd.name else "bbr", "windows": wrows,
            "score": score_masked(run, view, starts, wd), "gtq": gtq_masked(rd, starts, wd),
            "harm": harm_masked(rd, spans, wd), "grouping": grouping(rd, run, plan, wd)}


def runs() -> list[Path]:
    return sorted(p for p in KDIR.iterdir() if p.is_dir() and p.name.startswith("v3-") and (p / "events.csv").exists())


def cmd_rows(jobs: int, only: str | None) -> None:
    done = set()
    if ROWS.exists():   # resume: keep finished rows, drop a torn last line
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
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 4,
                 argv[argv.index("--only") + 1] if "--only" in argv else None)
    elif argv[0] == "one":
        row = worker(KDIR / argv[1])
        print(row["tb"] if "error" in row else json.dumps({k: row[k] for k in ("windows", "gtq", "harm")},
                                                          default=str)[:3000])
        if "error" not in row:
            for c in CATS:
                print(c, {n: {k: v for k, v in t.items() if k != "latency"} for n, t in row["score"][c].items()})
            print(row["grouping"] and {k: row["grouping"][k] for k in ("closes", "onsets")})
    elif argv[0] == "report":
        import ds_report
        ds_report.report(ROWS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
