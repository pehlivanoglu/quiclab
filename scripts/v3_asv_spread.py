#!/usr/bin/env python3
"""Suite v3, S-JOIN: emission time of one frame of a real 5000 kb/s client in calm.

    .venv/bin/python3 scripts/v3_asv_spread.py <run>[:client,client] ...   (default client sub-d)

Needs the GT-Q per-packet sender log (<client>-pkts.csv), i.e. runs from 2026-11-14 on.

Per frame of the client (sender frames.csv + per-packet pkts.csv): emission time =
last - first packet sent in [write of the frame, write of the next frame). Frames
whose packets run up to the next write (they may continue into it) are skipped
and counted. Prints medians (keyframes, P-frames) per run and pooled;
the medians become AsvSpec.key_spread_ms / p_spread_ms (scripts/v3_suite.py ASV_*).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402


SPILL_MS = 1.0   # (M) a frame whose packets reach this close to the next write may continue into it: skipped


def frame_spreads(run_dir: Path, sid: str) -> tuple[list[float], list[float]]:
    run = det_eval.Run(run_dir)
    fr = pd.read_csv(run.sender_file(sid, "frames"))
    pk = pd.read_csv(run.sender_file(sid, "pkts"), usecols=["send_mono_us"])
    ts = np.sort(np.array([run.t_mono_us(x) for x in pk.send_mono_us]))
    write = np.array([run.t_unix_us(x) for x in fr.write_us])
    key = fr.keyframe.values == 1
    out_k, out_p = [], []
    for i in range(len(fr) - 1):
        if not det_eval.WARMUP_S <= write[i] <= run.duration - det_eval.SHUTDOWN_S:
            continue
        a, b = np.searchsorted(ts, [write[i], write[i + 1]], side="left")
        if b - a < 1 or (write[i + 1] - ts[b - 1]) * 1000 < SPILL_MS:
            continue
        (out_k if key[i] else out_p).append((ts[b - 1] - ts[a]) * 1000)
    return out_k, out_p


def main(argv: list[str]) -> None:
    pooled_k, pooled_p, rows = [], [], []
    for arg in argv:
        path, _, who = arg.partition(":")
        rd = Path(path)
        for sid in (who.split(",") if who else ["sub-d"]):
            k, p = frame_spreads(rd, sid)
            pooled_k += k
            pooled_p += p
            rows.append({"run": f"{rd.name}:{sid}", "keyframes": len(k),
                         "key_ms_p50": round(float(np.median(k)), 2), "key_ms_p90": round(float(np.percentile(k, 90)), 2),
                         "p_frames": len(p), "p_ms_p50": round(float(np.median(p)), 2),
                         "p_ms_p90": round(float(np.percentile(p, 90)), 2)})
    print(json.dumps({"runs": rows, "pooled": {"key_ms_p50": round(float(np.median(pooled_k)), 2),
                                               "p_ms_p50": round(float(np.median(pooled_p)), 2)}}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
