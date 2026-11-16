#!/usr/bin/env python3
"""Raw-signal observations for the synchronized mini campaign (read-only; detector,
ECG and scoring code unchanged, only called).

    .venv/bin/python3 reports/sync-mini-2026-11-14/raw_signals.py RUN_DIR [...] > raw-rows.jsonl

Per run:
  gt1         GT1 standing-queue episodes per router egress: count, per minute, total s
              (gt1.run_truth, canonical Params);
  alarms      Shadow v2 on OWD ticks with hold (shadow_v2_frozen.episodes, the v2-owd
              detector of the baselines): alarm starts per client per minute, and the share
              that start within KF_WINDOW after one of the client's own keyframes
              (scheduled times from frames.csv). With 1 s GOPs a start time unrelated to
              keyframes gives KF_WINDOW / GOP = 0.2 (FLAG: 200 ms window);
  spread      ECG's onset spread across the clients of each shared burst
              (grouping-d150-v2-owd/metrics.json "spread": spread_onset_ms per burst).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import gt1  # noqa: E402
import keyframe_spread as kf  # noqa: E402
import shadow_v2_frozen  # noqa: E402

KF_WINDOW = 0.2   # s (FLAG)


def row(rd: Path) -> dict:
    run = ga.load_run(rd)
    minutes = max(run.duration - d.WARMUP_S, 1) / 60
    eps, _ = gt1.run_truth(run, gt1.Params())
    gt = {}
    for e in eps:
        g = gt.setdefault(e["hop"], {"n": 0, "s": 0.0})
        g["n"] += 1
        g["s"] += e["end_s"] - e["start_s"]
    for g in gt.values():
        g["per_min"] = round(g["n"] / minutes, 2)
        g["s"] = round(g["s"], 1)
    al = shadow_v2_frozen.episodes(run, "v2", mode="OWD", hold=True)
    starts, on_kf = 0, 0
    per_client = {}
    for s, spans in al.items():
        f = kf.client_keyframes(run, s)
        if f is None:
            continue
        k = np.sort(f["scheduled"].values)
        st = [a for a, _, _ in spans if a >= d.WARMUP_S]
        i = np.searchsorted(k, st, side="right") - 1
        near = [bool(j >= 0 and t - k[j] < KF_WINDOW) for t, j in zip(st, i)]
        per_client[s] = {"starts": len(st), "on_keyframe": int(sum(near))}
        starts += len(st)
        on_kf += sum(near)
    m_path = rd / "grouping-d150-v2-owd" / "metrics.json"
    spread = None
    if m_path.exists():
        sp = json.loads(m_path.read_text()).get("spread") or {}
        spread = sp.get("spread_onset_ms")
    return {"campaign": rd.parent.name, "run": rd.name, "minutes": round(minutes, 2), "gt1": gt,
            "alarms": {"starts": starts, "per_min": round(starts / minutes / max(len(per_client), 1), 3),
                       "on_keyframe_share": round(on_kf / starts, 3) if starts else None, "clients": per_client},
            "spread_onset_ms": spread}


def main(argv):
    for p in argv:
        print(json.dumps(row(Path(p))), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
