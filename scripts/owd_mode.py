#!/usr/bin/env python3
"""Shadow and GCC on sender-side one-way delay instead of RTT, against GT1, GT2 and GT3.

    python3 scripts/owd_mode.py OUT_PREFIX .runs/<campaign> [...]   # OUT_PREFIX.md + .csv

OWD mode input (built per run in a temporary directory, nothing written to the
run): the per-ACK record publishers/<pub>/<sub>-acks.csv with
    rtt_us     := OWD of the acked packet + R0
    min_rtt_us := trailing 10 s minimum of that value (BBR's min-RTT window)
where the OWD comes from the client's receive timestamps carried in its ACKs
(<sub>-owd.csv, minimum of the packet's 5 ms send-time bin; the sender has these
timestamps live) and R0 = min RTT - min OWD over the first 10 s, so delay
values keep the RTT scale. srtt_us (time scales only) and every other column
are unchanged. Reverse-path delay therefore no longer enters the delay
signals. BBR's own bw-drop events do not use delay and are the same in both modes.

Truths: GT1, GT2 (router side, independent of both modes), GT3 from the client
frame log (source B: application receive times, not the ACK timestamps the OWD
mode reads), and GT3 source A for reference only (it shares the receive
timestamps with the OWD mode).
"""

from __future__ import annotations

import csv
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402

BASE_S = 10.0
MODES = ("shadow", "gcc")
ROWS = ("shadow RTT", "shadow OWD", "gcc RTT", "gcc OWD", "bbr")
TRUTHS = ("GT1", "GT2", "GT3 frames (B)", "GT3 ACK timestamps (A, shares input with OWD mode)")


def owd_acks(run: det_eval.Run, sid: str, out: Path) -> Path:
    """Write the OWD-mode copy of a client's per-ACK record to out; return its path.

    OWD per ACK: the `owd_us` column when the recording has it (runs since
    2026-11-10: the largest newly acked packet's own receive timestamp, exactly
    what the sender knows at that ACK), else the 5 ms send-time bin minimum of
    <sub>-owd.csv at or before the ACK's send time (older runs; that bin may
    include packets acked later, a few ms of lookahead)."""
    acks = pd.read_csv(run.sender_file(sid, "acks"), dtype={"phase": str})
    if "owd_us" in acks.columns and acks["owd_us"].notna().any():
        sample = pd.to_numeric(acks["owd_us"], errors="coerce").to_numpy(dtype=float)
    else:
        owd = pd.read_csv(run.sender_file(sid, "owd"))
        owd = owd[owd["owd_min_us"].notna()]
        bins = owd["bin_mono_us"].to_numpy()
        vals = owd["owd_min_us"].to_numpy(dtype=float)
        idx = np.searchsorted(bins, acks["sent_mono_us"].to_numpy() // 5000 * 5000, side="right") - 1
        sample = np.where(idx >= 0, vals[np.clip(idx, 0, None)], np.nan)  # the bin at or before the send time
    t = acks["mono_us"].to_numpy()
    early = t <= t[0] + BASE_S * 1e6
    rtt = pd.to_numeric(acks["rtt_us"], errors="coerce").to_numpy()
    r0 = np.nanmin(rtt[early]) - np.nanmin(sample[early]) if early.any() else 0.0
    delay = sample + r0
    s = pd.Series(delay, index=pd.to_datetime(t, unit="us"))
    floor = s.rolling(f"{int(BASE_S)}s", min_periods=1).min().to_numpy()
    ok = ~np.isnan(delay)
    acks["rtt_us"] = np.where(ok, np.round(delay), np.nan)
    acks["min_rtt_us"] = np.where(np.isnan(floor), acks["min_rtt_us"], np.round(floor))
    acks["rtt_us"] = acks["rtt_us"].astype("Int64")
    acks["min_rtt_us"] = acks["min_rtt_us"].astype("int64")
    path = out / f"{sid}-acks.csv"
    acks.to_csv(path, index=False)
    return path


def worker(run_dir: Path) -> dict:
    run = det_eval.Run(run_dir)
    rtt = gt_score.alarm_starts(run, ("shadow", "gcc", "bbr"))
    with tempfile.TemporaryDirectory() as tmp:
        acks = {s: owd_acks(run, s, Path(tmp)) for s in run.subs}
        owd = gt_score.alarm_starts(run, MODES, acks=acks)
    starts = {}
    for (det, s), v in rtt.items():
        starts[(f"{det} RTT" if det in MODES else det, s)] = v
    for (det, s), v in owd.items():
        starts[(f"{det} OWD", s)] = v
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B", path_queues=False)
    ea, la = gt3.run_truth(run, gt3.Params(), source="A", path_queues=False)
    views = {TRUTHS[0]: gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             TRUTHS[1]: gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2),
             TRUTHS[2]: gt3.view_of(run, eb, lb), TRUTHS[3]: gt3.view_of(run, ea, la)}
    return {"topology": run.path.parent.name.split("_det-")[-1], "scenario": det_eval.scenario_name(run.path),
            "aqm": run.aqm, "score": {t: gt_score.score(run, v, starts, ROWS) for t, v in views.items()}}


def _f(x, d=2):
    return "-" if x != x else f"{x:.{d}f}"


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    prefix = Path(argv[0])
    runs = sorted(d for c in argv[1:] for d in Path(c).iterdir() if (d / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    T = gt1._table
    cols = ["episodes", "precision", "recall", "recall of episodes >= 2 s", "latency p50 after t_on (ms)", "FA / min CLEAR"]

    def cells(rs, truth, det):
        s = gt_score.summarize([r["score"][truth][det] for r in rs])
        return [s["episodes"], _f(s["precision"]), _f(s["recall"]), _f(s["bin_recall"][-1]),
                _f(s["late_latency_p50_ms"], 0), _f(s["fa_per_min"])]

    L = ["# Shadow / GCC: RTT vs sender-side OWD", "", __doc__.split("\n\n", 1)[1], ""]
    csv_rows = []
    groups = {"overall": {"all": res}, "topology": defaultdict(list), "scenario": defaultdict(list)}
    for r in res:
        groups["topology"][r["topology"]].append(r)
        groups["scenario"][f"{r['topology']}/{r['scenario']}"].append(r)
    for truth in TRUTHS:
        L += [f"## {truth}", ""]
        for level in ("overall", "topology"):
            rows = [[k, d, *cells(v, truth, d)] for k, v in sorted(groups[level].items()) for d in ROWS]
            csv_rows += [[truth, level, *x] for x in rows]
            L += [f"### {level}", "", T([level, "detector", *cols], rows), ""]
        rows = []
        for k, v in sorted(groups["scenario"].items()):
            row = [k]
            for d in ROWS:
                s = gt_score.summarize([r["score"][truth][d] for r in v])
                row.append(f"{_f(s['precision'])} / {_f(s['recall'])} / {_f(s['late_latency_p50_ms'], 0)}")
                csv_rows.append([truth, "scenario", k, d, *cells(v, truth, d)])
            rows.append(row)
        L += ["### scenario (precision / recall / latency p50 after t_on ms)", "", T(["scenario", *ROWS], rows), ""]
    prefix.with_suffix(".md").write_text("\n".join(L))
    with prefix.with_suffix(".csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["truth", "level", "group", "detector", *cols])
        w.writerows(csv_rows)
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
