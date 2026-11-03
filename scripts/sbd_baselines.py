#!/usr/bin/env python3
"""Run the shared-bottleneck detection (SBD) baselines DCW, rmcatSBD and dcSBD on quiclab runs.

    python3 scripts/sbd_baselines.py .runs/<campaign>/<run> [...]
        [--owd oracle|est] [--t-unit 0.005|0.01] [--dcw-th 0.8] [--methods dcw,rmcat_sbd,dc_sbd]

These are general SBD baselines, not FlowBot (a separate baseline). The code
comes from the FlowBot repository, which implements them as its comparison
methods; it is vendored unchanged in baselines/sbd/ (see its README.md), and
the input follows FlowBot's format. This script only builds their input table and writes
their output:

  input  [run, flow, time, owd, drop, label], one row per flow and time step:
    owd   per-client OWD in seconds: the oracle (<client>-owd.csv, owd_mean_us)
          or the sender-side estimate (<client>-owd-est.csv, scripts/owd_estimate.py).
          Logs are 5 ms (runs before 2026-11-03: 10 ms). Empty bins hold the last
          value (a sampler reading "current OWD" every t_unit, as FlowBot does).
    drop  1 if the sender declared a loss in that step (acks.csv newly_lost),
          like FlowBot's drop = SLR increased.
    label 0: no grouping truth yet; the methods do not read it.
  output <run>/baselines/<method>-<owd>[-<t_unit>ms].csv (suffix unless 5 ms):
    t_s (window start, run time), window_s, client, label
  Labels group co-bottlenecked clients within one window; the numbers mean
  nothing across windows. Non-bottlenecked clients get labels of their own.

Windows: DCW 1.5 s, SBD 0.35 s (RFC 8382). Only the time span where every
client has OWD data is used.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402
from baselines.sbd.detector import CobottleneckDetector  # noqa: E402

DCW_INTERVAL_S = 1.5
METHODS = ("dcw", "rmcat_sbd", "dc_sbd")


def flow_table(run_dir: Path, owd: str, t_unit: float) -> tuple[pd.DataFrame, list[str]]:
    run = det_eval.Run(run_dir)
    pub = run_dir / "publishers" / run.pub
    series = {}
    for sid in sorted(run.subs):
        if owd == "oracle":
            path, col = pub / f"{sid}-owd.csv", "owd_mean_us"
        else:
            path, col = pub / f"{sid}-owd-est.csv", "est_mean_us"
        if not path.exists():
            sys.exit(f"{path} missing (oracle: runs with OWD logging; est: run scripts/owd_estimate.py)")
        df = pd.read_csv(path, usecols=["bin_mono_us", col])
        t = df.bin_mono_us.map(lambda us: run.t_mono_us(us))
        series[sid] = pd.Series(df[col].to_numpy(dtype=float) / 1e6, index=t.to_numpy())
    # Common span on the t_unit grid, sample-and-hold of the last OWD.
    start = max(s.dropna().index.min() for s in series.values())
    end = min(s.dropna().index.max() for s in series.values())
    grid = np.round(np.arange(np.ceil(start / t_unit) * t_unit, end, t_unit), 6)
    acks = {sid: pd.read_csv(pub / f"{sid}-acks.csv", usecols=["mono_us", "newly_lost"]) for sid in series}
    frames = []
    for i, (sid, s) in enumerate(series.items()):
        held = s.dropna().sort_index()
        idx = np.searchsorted(held.index.to_numpy(), grid, side="right") - 1
        values = held.to_numpy()[np.clip(idx, 0, None)]
        a = acks[sid]
        lost_t = a.mono_us[a.newly_lost > 0].map(lambda us: run.t_mono_us(us)).to_numpy()
        drop = np.zeros(len(grid), dtype=int)
        k = np.floor((lost_t - grid[0]) / t_unit).astype(int)
        drop[k[(k >= 0) & (k < len(grid))]] = 1
        frames.append(pd.DataFrame({"run": run_dir.name, "flow": i, "time": np.round(grid, 3),
                                    "owd": values, "drop": drop, "label": 0}))
    return pd.concat(frames, ignore_index=True), list(series)


def run_methods(run_dir: Path, owd: str, t_unit: float, dcw_th: float, methods: list[str]) -> None:
    df, clients = flow_table(run_dir, owd, t_unit)
    out_dir = run_dir / "baselines"
    out_dir.mkdir(exist_ok=True)
    t_max = df.time.max()
    for method in methods:
        if method == "dcw":
            det = CobottleneckDetector(df, DCW_INTERVAL_S, t_unit=t_unit, model_th=dcw_th)
            seq_len = int(DCW_INTERVAL_S / t_unit)
            selected = det._get_selected_dfs(0, t_max, seq_len)
            y_hats = det.classify(0, t_max, selected, method="dcw", seq_len=seq_len)
            windows = [(round(t, 3), sorted(s.flow.unique()), DCW_INTERVAL_S)
                       for t, s in zip(det.ticks, selected)]
        else:
            det = CobottleneckDetector(df, None, t_unit=t_unit)
            y_hats = det.classify(0, t_max, None, method=method)
            sbd_df = det.get_sbd_df()
            windows = [(round(t, 3), sorted(sbd_df[sbd_df.time == t].flow.unique()), 0.35)
                       for t in sorted(sbd_df.time.unique())]
        assert len(windows) == len(y_hats), (method, len(windows), len(y_hats))
        step = "" if np.isclose(t_unit, 0.005) else f"-{t_unit * 1000:g}ms"
        path = out_dir / f"{method}-{owd}{step}.csv"
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t_s", "window_s", "client", "label"])
            for (t, flows, win), y in zip(windows, y_hats):
                assert len(flows) == len(y), (method, t, flows, y)
                for flow, label in zip(flows, y):
                    w.writerow([t, win, clients[flow], int(label)])
        print(f"{run_dir.name}: {method} -> {path.relative_to(run_dir)} ({len(y_hats)} windows)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--owd", choices=("oracle", "est"), default="oracle")
    ap.add_argument("--t-unit", type=float, default=0.005, help="time step (FlowBot: 0.005); OWD logs are 5 ms (older runs 10 ms)")
    ap.add_argument("--dcw-th", type=float, default=0.8, help="DCW correlation threshold (FlowBot paper: 0.8)")
    ap.add_argument("--methods", default=",".join(METHODS))
    args = ap.parse_args()
    for run in args.runs:
        run_methods(run, args.owd, args.t_unit, args.dcw_th, args.methods.split(","))


if __name__ == "__main__":
    main()
