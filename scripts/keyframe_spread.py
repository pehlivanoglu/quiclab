#!/usr/bin/env python3
"""Keyframe send spread across clients of one run (check A of the synchronized-phase
campaign, 2026-11-13). Read-only.

    python3 scripts/keyframe_spread.py RUN_DIR [RUN_DIR ...]      # prints, writes <run>/grouping/keyframe-spread.json

For every keyframe index that two or more clients share, the spread = latest - earliest
client time, for three timestamps of the publisher (qvideo-server):
  scheduled   frames.csv send_us   (the live schedule: start + phase + k / fps)
  written     frames.csv write_us  (handed to the QUIC transport)
  packet      the first packet in sent.csv at or after the write time (approximate:
              sent.csv has no frame id, so a packet of an earlier frame still in the
              send queue can stand in for the keyframe's first packet)
Groups: all clients ("across renditions") and every rendition (same rate_kbps) with
two or more clients ("within rendition"). Reported as n keyframes, p50 / p90 / max ms.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402

STAMPS = ("scheduled", "written", "packet")


def client_keyframes(run: det_eval.Run, sid: str) -> pd.DataFrame | None:
    """index -> scheduled, written, packet (run seconds) for one client's keyframes."""
    fr_path, sent_path = run.sender_file(sid, "frames"), run.sender_file(sid, "sent")
    if not fr_path.exists():
        return None
    fr = pd.read_csv(fr_path)
    fr = fr[fr.keyframe == 1]
    out = pd.DataFrame({"scheduled": [run.t_unix_us(x) for x in fr.send_us],
                        "written": [run.t_unix_us(x) for x in fr.write_us]}, index=fr["index"].values)
    if sent_path.exists():
        sent = np.sort(np.array([run.t_mono_us(x) for x in pd.read_csv(sent_path, usecols=["send_mono_us"]).send_mono_us]))
        i = np.searchsorted(sent, out["written"].values, side="left")
        out["packet"] = np.where(i < len(sent), sent[np.minimum(i, len(sent) - 1)], np.nan)
    else:
        out["packet"] = np.nan
    return out


def spread(frames: dict[str, pd.DataFrame], clients: list[str]) -> dict:
    common = set.intersection(*[set(frames[c].index) for c in clients])
    out = {"clients": clients, "keyframes": len(common)}
    for st in STAMPS:
        v = []
        for k in sorted(common):
            t = [frames[c].at[k, st] for c in clients]
            if not any(np.isnan(t)):
                v.append((max(t) - min(t)) * 1000)
        out[st] = ({"p50_ms": round(float(np.percentile(v, 50)), 3), "p90_ms": round(float(np.percentile(v, 90)), 3),
                    "max_ms": round(float(max(v)), 3)} if v else None)
    return out


def run_spread(run_dir: Path) -> dict:
    run = det_eval.Run(run_dir)
    subs = run.topology["subscribers"]
    frames = {s: f for s in run.subs if (f := client_keyframes(run, s)) is not None}
    phases = {s: (subs.get(s) or {}).get("phase_ms", 0) for s in frames}
    res = {"run": run_dir.name, "phases_ms": phases, "groups": {}}
    if len(frames) >= 2:
        res["groups"]["across renditions"] = spread(frames, sorted(frames))
    by_rate = defaultdict(list)
    for s in frames:
        by_rate[(subs.get(s) or {}).get("rate_kbps")].append(s)
    for rate, cl in sorted(by_rate.items(), key=lambda x: x[0] or 0):
        if len(cl) >= 2:
            res["groups"][f"within {rate} kb/s"] = spread(frames, sorted(cl))
    return res


def line(res: dict) -> str:
    g = res["groups"].get("across renditions")
    if not g:
        return f"{res['run']}: keyframe spread n/a"
    return f"{res['run']}: keyframe spread across clients (p50/p90/max ms) " + ", ".join(
        f"{st} {g[st]['p50_ms']}/{g[st]['p90_ms']}/{g[st]['max_ms']}" if g[st] else f"{st} n/a" for st in STAMPS)


def write(run_dir: Path) -> dict:
    res = run_spread(run_dir)
    (run_dir / "grouping").mkdir(exist_ok=True)
    (run_dir / "grouping" / "keyframe-spread.json").write_text(json.dumps(res, indent=1))
    return res


def main(argv: list[str]) -> None:
    for p in argv:
        res = write(Path(p))
        print(line(res))
        for name, g in res["groups"].items():
            print(f"  {name} ({len(g['clients'])} clients, {g['keyframes']} keyframes): " + ", ".join(
                f"{st} {g[st]['p50_ms']}/{g[st]['p90_ms']}/{g[st]['max_ms']}" if g[st] else f"{st} n/a" for st in STAMPS))


if __name__ == "__main__":
    main(sys.argv[1:])
