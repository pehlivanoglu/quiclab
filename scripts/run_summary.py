#!/usr/bin/env python3
"""Side-by-side summary of quiclab runs, to compare repeats or load levels.

    python3 scripts/run_summary.py .runs/run-a .runs/run-b [...]

Per run: every subscriber's stalls, stall time, mean goodput, max frame OWD
and the sender's max backlog; per PPBP source the realized offered load,
received load and loss; per router egress the queue p50/p99 and drops.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path


def rows(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def stream_start_us(run: Path) -> int:
    epoch = next(r for r in rows(run / "events.csv") if r["event"] == "epoch")
    return int(epoch["detail"].split("stream_start_unix_us=")[1].split()[0])


def subscribers(run: Path) -> dict[str, dict[str, float]]:
    t0 = stream_start_us(run)
    out = {}
    for playback in sorted((run / "clients").glob("*-playback.csv")):
        sid = playback.name[: -len("-playback.csv")]
        play = rows(playback)
        frames = rows(run / "clients" / f"{sid}-frames.csv")
        cc_files = list((run / "publishers").glob(f"*/{sid}-cc.csv"))
        steady = [r for r in play if int(r["t_us"]) >= t0 + 5_000_000] or play
        drops = list((run / "publishers").glob(f"*/{sid}-drops.csv"))
        out[sid] = {
            "stalls": int(play[-1]["stalls"]),
            "skipped": int(play[-1].get("skipped_frames") or 0),
            "dropped": len(rows(drops[0])) if drops else 0,
            "stall_ms": int(play[-1]["stall_ms"]),
            "goodput_mbps": statistics.fmean(int(r["goodput_bps"]) for r in steady) / 1e6,
            "max_owd_ms": max((int(r["owd_us"]) for r in frames), default=0) / 1000,
            "max_backlog_kb": max((int(r["backlog_bytes"]) for r in rows(cc_files[0])), default=0) / 1000
            if cc_files else 0.0,
        }
    return out


def ppbp(run: Path) -> dict[str, dict[str, float]]:
    out = {}
    for bursts in sorted((run / "traffic").glob("*-bursts.csv")):
        name = bursts.name[: -len("-bursts.csv")]
        b, recv = rows(bursts), rows(run / "traffic" / f"{name}-recv.csv")
        span = max(float(x["start_s"]) + float(x["duration_s"]) for x in b) if b else 1.0
        packets = sum(int(x["packets"]) for x in recv)
        lost = sum(int(x["lost"]) for x in recv)
        out[name] = {
            "offered_mbps": sum(float(x["duration_s"]) * float(x["rate_mbps"]) for x in b) / span,
            "recv_mbps": sum(int(x["bytes"]) for x in recv) * 8 / span / 1e6,
            "loss_pct": 100 * lost / max(1, packets + lost),
            "bursts": len(b),
        }
    return out


def queues(run: Path) -> dict[str, dict[str, float]]:
    out = {}
    for path in sorted((run / "router-metrics").glob("*/*-queue.csv")):
        q = sorted(int(r["queue_packets"]) for r in rows(path))
        if q:
            out[f"{path.parent.name}/{path.name[:-len('-queue.csv')]}"] = {
                "p50": statistics.median(q), "p99": q[int(0.99 * (len(q) - 1))],
                "drops": int(rows(path)[-1]["drops"]),
            }
    return out


def table(title: str, data: list[dict[str, dict[str, float]]], runs: list[Path]) -> None:
    keys = sorted({k for d in data for k in d})
    if not keys:
        return
    fields = list(next(iter(next(d for d in data if d).values())).keys())
    print(f"\n== {title}")
    print(f"{'':16}" + "".join(f"{run.name:>{16 * len(fields)}}" for run in runs))
    print(f"{'':16}" + "".join(f"{f:>16}" for _ in runs for f in fields))
    for key in keys:
        cells = []
        for d in data:
            values = d.get(key)
            cells += [f"{values[f]:>16.2f}" if values else f"{'-':>16}" for f in fields]
        print(f"{key:16}" + "".join(cells))


def main() -> None:
    runs = [Path(arg) for arg in sys.argv[1:]]
    if not runs or not all((run / "events.csv").exists() for run in runs):
        sys.exit(__doc__)
    table("subscribers", [subscribers(r) for r in runs], runs)
    table("PPBP cross traffic", [ppbp(r) for r in runs], runs)
    table("router queues (packets)", [queues(r) for r in runs], runs)


if __name__ == "__main__":
    main()
