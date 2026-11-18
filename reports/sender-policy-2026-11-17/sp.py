#!/usr/bin/env python3
"""Sender policy on the v3 runs (K5-sender note, Part 1): 1.2 (drop windows without a harmful GT-H episode) and
1.4 (alarm against drop). Nothing frozen changes; nothing is written inside run folders.

    nice -n 19 .venv/bin/python3 reports/sender-policy-2026-11-17/sp.py rows [--jobs 2]   # rows.jsonl
    .venv/bin/python3 reports/sender-policy-2026-11-17/sp.py report

Window span (M): [start, hi], hi = the first sender-stats sample (cc.csv, 50 ms) at or after the window end where
every expected client's oldest queued frame is younger than half the limit (send_buffer_ms / 2 = 500 ms), capped
at end + CAP_S. A GOP drop event = the first drop of one (client, GOP) in drops.csv. t_drop = the first GOP drop
event of any expected client (window "expected", sub-ctrl excluded) in the span.
1.4 per detector (v2-owd frozen; D1-bw, D2-gcc, D3-10ms-200ms as R2):
  window lead = t_drop - the first alarm start of any expected client in [start - 1 s, t_drop] (none: no alarm);
  per drop event of client c at t: "alarm on" = an alarm span of c covers t; "no alarm before" = no alarm start
  of c in [start - 1 s, t].
1.2: GT-H (scripts/gtq.py frame_table / deadline_misses) counts head-dropped frames as misses at t_gen + B. Count of
drop windows with no harmful_600 forward GT-Q episode of an expected client whose t_harm_600 is in [start - 1, hi].
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

KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
HALF_LIMIT_US = 500_000     # (M) send_buffer_ms / 2
CAP_S = 30.0                # (M) longest tail after the window end
DETS = ("v2-owd", "D1-bw", "D2-gcc", "D3-10ms-200ms")
ROWS = HERE / "rows.jsonl"


def gop_drops(run, s):
    """(t, gop, n frames, bytes, partial) per GOP drop event; partial = some frame of that GOP was handed to QUIC."""
    import pandas as pd
    f = run.sender_file(s, "drops")
    if not f.exists():
        return []
    d = pd.read_csv(f)
    if not len(d):
        return []
    fr = pd.read_csv(run.sender_file(s, "frames"), usecols=["index", "keyframe"])
    keys = np.sort(fr["index"][fr.keyframe == 1].to_numpy())
    G = int(np.min(np.diff(keys))) if len(keys) > 1 else 30      # frames per GOP
    sent_gops = set((fr["index"].to_numpy() // G).tolist())
    out = []
    for g, x in d.groupby("gop"):
        out.append({"t": run.t_unix_us(float(x.t_us.min())), "gop": int(g), "frames": len(x),
                    "bytes": int(x["size"].sum()), "partial": int(g) in sent_gops})
    return sorted(out, key=lambda e: e["t"])


def queue_age(run, s):
    import pandas as pd
    c = pd.read_csv(run.sender_file(s, "cc"), usecols=["t_us", "queue_age_us"])
    return np.array([run.t_unix_us(x) for x in c.t_us.values]), c.queue_age_us.to_numpy(dtype=float)


def span_end(w, qa):
    """The time by which every expected client's oldest queued frame is back below half the limit (>= end)."""
    hi = w["end"]
    for c in w["clients"]:
        if c not in qa:
            continue
        t, age = qa[c]
        k = int(np.searchsorted(t, w["end"]))
        ok = np.flatnonzero(age[k:] < HALF_LIMIT_US)
        hi = max(hi, float(t[k + ok[0]]) if len(ok) else w["end"] + CAP_S)
    return min(hi, w["end"] + CAP_S)


def worker(rd: Path) -> dict:
    try:
        return _worker(rd)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path) -> dict:
    import det_eval as d
    import r2
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    r2._setup()
    run = d.Run(rd)
    wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    subs = [s for s in run.subs if s != "sub-ctrl"]
    drops = {s: gop_drops(run, s) for s in subs}
    qa = {s: queue_age(run, s) for s in subs}
    spans: dict = {}
    for s, df in r2.flows(run).items():
        r = s3.run_cusum(df, r2.FROZEN_LABEL, fz.FROZEN["OWD"]["g_ref"]["v2"], False)
        spans[("v2-owd", s)] = [(a, b) for a, b, _ in s5.on_spans(r, s3.THETA_ON)]
        spans[("D3-10ms-200ms", s)] = r2.d3(df)["D3-10ms-200ms"]
    for s in subs:
        spans[("D1-bw", s)] = r2.d1(run, s).get("D1-bw", [])
        spans[("D2-gcc", s)] = r2.d2(run, s)["D2-gcc"]
    harm = []
    if (rd / "truth" / "gtq.csv").exists():
        for e in d.rows(rd / "truth" / "gtq.csv"):
            if e.get("direction") == "forward" and e.get("harmful_600") == "1":
                harm.append((e["flow"], float(e["t_harm_600"])))
    wrows = []
    for w in wins:
        w = {**w, "clients": [c for c in w.get("expected", []) if c != "sub-ctrl"]}
        hi = span_end(w, qa)
        ev = [(c, e) for c in w["clients"] for e in drops.get(c, []) if w["start"] <= e["t"] <= hi]
        ev.sort(key=lambda z: z[1]["t"])
        t_drop = ev[0][1]["t"] if ev else None
        row = {k: w.get(k) for k in ("start", "end", "kind", "u", "d", "hop", "stimulus_type")}
        row |= {"hi": hi, "n_clients": len(w["clients"]), "t_drop": t_drop, "n_drop_events": len(ev),
                "harm_in_span": any(c in w["clients"] and w["start"] - 1.0 <= t <= hi for c, t in harm)
                if (rd / "truth" / "gtq.csv").exists() else None}
        if ev:
            det = {}
            for n in DETS:
                fa = min((a for c in w["clients"] for a, _ in spans.get((n, c), []) if w["start"] - 1.0 <= a <= t_drop),
                         default=None)
                on = before = 0
                for c, e in ev:
                    sp = spans.get((n, c), [])
                    on += any(a <= e["t"] <= b for a, b in sp)
                    before += any(w["start"] - 1.0 <= a <= e["t"] for a, _ in sp)
                det[n] = {"lead": None if fa is None else t_drop - fa, "on": on, "before": before}
            row["det"] = det
        wrows.append(row)
    parts = rd.name.split("-")
    return {"run": rd.name, "block": parts[1], "type": parts[2], "variant": parts[3], "aqm": parts[4],
            "rep": int(parts[5][1:]), "cc": "copa" if "copa" in rd.name else "bbr", "windows": wrows,
            "gtq": (rd / "truth" / "gtq.csv").exists()}


def runs() -> list[Path]:
    return sorted(p for p in KDIR.iterdir() if p.is_dir() and p.name.startswith("v3-") and (p / "events.csv").exists())


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


def report(path: Path) -> None:
    R = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    bad = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r and r["type"] != "calm"]
    if bad:
        print(f"Runs with errors: {[(b['run'], b['error']) for b in bad]}\n")
    single = ("pfifo", "codel", "pie", "red")
    print("## 1.2 Drop windows without a harmful GT-H 600 episode\n")
    print("| AQM group | rep | drop windows (GT-Q valid) | without a harmful episode | share |\n|---|---|---|---|---|")
    for name, sel in (("single-queue", lambda r: r["aqm"] in single), ("fq_codel / cake", lambda r: r["aqm"] in ("fq_codel", "cake")),
                      ("all", lambda r: True)):
        for rep in (1, 2):
            ws = [w for r in R if sel(r) and r["rep"] == rep and r["gtq"] for w in r["windows"] if w["t_drop"] is not None]
            n = sum(not w["harm_in_span"] for w in ws)
            print(f"| {name} | r{rep} | {len(ws)} | {n} | {n / len(ws):.3f} |" if ws else f"| {name} | r{rep} | 0 | - | - |")
    print()
    print("## 1.4 Alarm against drop (windows with at least one GOP drop)\n")
    for name, sel in (("Single-queue AQM", lambda r: r["aqm"] in single), ("fq_codel / cake", lambda r: r["aqm"] in ("fq_codel", "cake")),
                      ("Copa (M13)", lambda r: r["cc"] == "copa")):
        print(f"#### {name}\n")
        print("| detector | drop windows | alarm before the first drop | lead to first drop p10 / p50 / p90 s | "
              "drop events | alarm on at the drop | no alarm before the drop |")
        print("|---|---|---|---|---|---|---|")
        for n in DETS:
            cells = []
            for rep in (1, 2):
                ws = [w for r in R if sel(r) and r["rep"] == rep for w in r["windows"] if w.get("det")]
                leads = [w["det"][n]["lead"] for w in ws if w["det"][n]["lead"] is not None]
                ev = sum(w["n_drop_events"] for w in ws)
                on = sum(w["det"][n]["on"] for w in ws)
                bef = sum(w["det"][n]["before"] for w in ws)
                q = (lambda p: f"{np.percentile(leads, p):.2f}") if leads else (lambda p: "-")
                cells.append((len(ws), len(leads) / len(ws) if ws else None, f"{q(10)} / {q(50)} / {q(90)}", ev,
                              on / ev if ev else None, (ev - bef) / ev if ev else None))
            f = lambda x: "-" if x is None else f"{x:.2f}"   # noqa: E731
            print(f"| {n} | {cells[0][0]} / {cells[1][0]} | {f(cells[0][1])} / {f(cells[1][1])} | {cells[0][2]} ; "
                  f"{cells[1][2]} | {cells[0][3]} / {cells[1][3]} | {f(cells[0][4])} / {f(cells[1][4])} | "
                  f"{f(cells[0][5])} / {f(cells[1][5])} |")
        print()
    print("#### Lead of v2-owd over the first drop by AQM and intensity, pooled reps (p50 s; windows)\n")
    print("| AQM | u 1.05 | u 1.15 | u 1.3 |\n|---|---|---|---|")
    by = defaultdict(list)
    for r in R:
        for w in r["windows"]:
            if w.get("det") and w["det"]["v2-owd"]["lead"] is not None:
                by[(r["aqm"], w.get("u"))].append(w["det"]["v2-owd"]["lead"])
    for a in ("pfifo", "codel", "pie", "red", "fq_codel"):
        print(f"| {a} | " + " | ".join(f"{np.median(by[(a, u)]):.2f} ({len(by[(a, u)])})" if by[(a, u)] else "-"
                                       for u in (1.05, 1.15, 1.3)) + " |")
    print()


def main(argv: list[str]) -> int:
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2,
                 argv[argv.index("--only") + 1] if "--only" in argv else None)
    elif argv[0] == "one":
        row = worker(KDIR / argv[1])
        print(row["tb"] if "error" in row else json.dumps(row["windows"][:4], default=str, indent=1))
    elif argv[0] == "report":
        report(ROWS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
