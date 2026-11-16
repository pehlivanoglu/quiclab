#!/usr/bin/env python3
"""Suite v3: the load in every stimulus window, split into its parts (decision 2026-11-14).

u is the intensity of the stimulus with the video at its calm rate, so a surge cell u
offers background + surge = U(1 - s) + (u - U) of C on its target. The video's reaction is an
outcome: it is measured, never sized for. Per window (grouping/windows.json) this writes
<run>/v3-stimuli.csv:

  u_nominal       the cell's u (names keep it)
  nonvideo_load   background + stimulus arriving at the target egress / C
  video_load      the video arriving at the target egress / C
  total_load      everything arriving / C (= the two above, plus a few non-IPv4 frames)
  video_calm      the video arriving in calm time (outside every window +- 1 s, after warm-up) / C
  video_rel_calm  video_load / video_calm
  planned_nonvideo U(1 - s) + (u - U) for surges and ramps (the ramp's peak; the window holds the
                  ramp too, so ramps are not gated), else empty
  capacity_ratio  capacity in force at the window's start / C (capacity drops)

C = the egress's calm capacity C_e (plan). "Arriving" = enqueue time in the GT-Q packet trace
(dequeued and dropped packets, skb length as tc counts it). Video = source address of the run's
publisher. Egresses without a trace fall back to the senders' logs (qtraffic *-sent.csv x
UDP_WIRE for non-video, publisher <client>-sent.csv / 0.96 for video); `source` says which.

    .venv/bin/python3 scripts/v3_stimuli.py <run> [...]                 # write and print
    .venv/bin/python3 scripts/v3_stimuli.py --reaction <campaign>       # post-campaign video table
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402

CALM_MARGIN_S = 1.0
QUIC_TO_ROUTER = 1 / 0.96          # (M) docs/scenario-catalog.md: router bytes / publisher QUIC bytes
FIELDS = ("start", "end", "kind", "stimulus_type", "target", "hop", "cell", "u_nominal", "d", "planned_nonvideo",
          "nonvideo_load", "video_load", "total_load", "video_calm", "video_rel_calm", "capacity_ratio", "source")


def _trace_file(rd: Path, hop: str) -> Path | None:
    meta = rd / "router-trace" / "interfaces.csv"
    if not meta.exists():
        return None
    for r in csv.DictReader(meta.open()):
        if r["hop"] == hop:
            p = rd / "router-trace" / f"{r['iface']}-packets.csv"
            return p if p.exists() else None
    return None


def _arrivals(run: d.Run, rd: Path, hop: str, pub_ip: str, clients: list[str]):
    """(t, bytes, is_video) of the packets arriving at the egress, or None without a trace."""
    p = _trace_file(rd, hop)
    if p is None:
        return None
    x = pd.read_csv(p, usecols=["kind", "t_enq_ns", "saddr", "len"], dtype={"saddr": str}, keep_default_na=False)
    x = x[(x.kind.isin(["dequeue", "drop"])) & (x.t_enq_ns >= 0)]
    t = (x.t_enq_ns.to_numpy(dtype=np.int64) - run.epoch_mono_ns) / 1e9
    return t, x.len.to_numpy(dtype=float), (x.saddr == pub_ip).to_numpy()


def _logs(run: d.Run, rd: Path, route: str | None, clients: list[str]):
    """Fallback: (t, bytes, is_video) from the senders' own logs."""
    import v3_suite
    ts, bs, vs = [], [], []
    ids = {e["id"] for e in run.scenario.get("events", []) if e.get("route") == route} if route else set()
    for i in ids:
        f = rd / "traffic" / f"{i}-sent.csv"
        if f.exists():
            s = pd.read_csv(f)
            ts.append(np.array([run.t_unix_us(v) for v in s.t_us]))
            bs.append(s.sent_bytes.to_numpy(dtype=float) * v3_suite.UDP_WIRE)
            vs.append(np.zeros(len(s), dtype=bool))
    for sid in clients:
        f = run.sender_file(sid, "sent")
        if f.exists():
            s = pd.read_csv(f, usecols=["send_mono_us", "bytes"])
            ts.append(np.array([run.t_mono_us(v) for v in s.send_mono_us]))
            bs.append(s.bytes.to_numpy(dtype=float) * QUIC_TO_ROUTER)
            vs.append(np.ones(len(s), dtype=bool))
    if not ts:
        return np.array([]), np.array([]), np.array([], dtype=bool)
    return np.concatenate(ts), np.concatenate(bs), np.concatenate(vs)


def run_stimuli(rd: Path) -> list[dict]:
    rd = Path(rd)
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    wins = json.loads((rd / "grouping" / "windows.json").read_text())
    from quiclab.config.schema import load_topology
    from quiclab.runtime import node_loopback_ips
    pub_ip = node_loopback_ips(load_topology(rd / "topology.yaml"))[run.pub]
    egress = {e["hop"]: (name, e) for name, e in plan["egress"].items()}
    caps = d.capacity_series(run)
    s, U = plan.get("s"), plan["U"]
    busy = [(w["start"] - CALM_MARGIN_S, w["end"] + CALM_MARGIN_S) for w in wins]
    cache: dict[str, tuple] = {}
    out = []
    for w in wins:
        hop = w.get("hop")
        if not hop:
            continue
        name, e = egress.get(hop, (None, None))
        if e is None:   # a private egress (access link): its capacity from the scenario
            a, b = hop.split("->")
            base = d.value_at(caps.get((a, b), [(0.0, np.nan)]), 0.0)
            e = {"C_e_mbps": base, "clients": w["expected"], "shaped": True}
        if hop not in cache:
            arr = _arrivals(run, rd, hop, pub_ip, e["clients"])
            src = "trace"
            if arr is None:
                route = f"bg-{name}" if name else None
                arr, src = _logs(run, rd, route, e["clients"]), "logs"
            t, by, vid = arr
            calm = (t > d.WARMUP_S + 5) & (t < run.duration - 2)
            for a, b in busy:
                calm &= ~((t >= a) & (t <= b))
            grid = np.arange(d.WARMUP_S + 5, run.duration - 2, 0.01)   # calm seconds on a 10 ms grid
            free = np.ones(len(grid), dtype=bool)
            for a, b in busy:
                free &= ~((grid >= a) & (grid <= b))
            span = max(1e-9, free.sum() * 0.01)
            C = e["C_e_mbps"] * 1e6 / 8
            cache[hop] = (t, by, vid, C, by[calm & vid].sum() / (C * span), src)
        t, by, vid, C, vcalm, src = cache[hop]
        m = (t >= w["start"]) & (t < w["end"])
        dur = w["end"] - w["start"]
        nv, vv = by[m & ~vid].sum() / (C * dur), by[m & vid].sum() / (C * dur)
        u = w.get("u")
        s_e, U_e = e.get("s", s), e.get("U", U)   # suite v4: per-egress target point where the plan has one
        planned = round(U_e * (1 - s_e) + (u - U_e), 4) if (u is not None and s_e is not None
                                                      and w.get("stimulus_type") in ("surge", "ramp")) else None
        a_, b_ = hop.split("->")
        cap_now = d.value_at(caps.get((a_, b_), [(0.0, e["C_e_mbps"])]), w["start"] + 0.01)
        out.append({"start": w["start"], "end": w["end"], "kind": w["kind"], "stimulus_type": w.get("stimulus_type"),
                    "target": w["target"], "hop": hop, "cell": w["cell"], "u_nominal": u, "d": w.get("d"),
                    "planned_nonvideo": planned, "nonvideo_load": round(nv, 4), "video_load": round(vv, 4),
                    "total_load": round(nv + vv, 4), "video_calm": round(vcalm, 4),
                    "video_rel_calm": round(vv / vcalm, 4) if vcalm > 0 else None,
                    "capacity_ratio": round(cap_now / e["C_e_mbps"], 4) if e["C_e_mbps"] else None, "source": src})
    return out


def write(rd: Path) -> list[dict]:
    rows = run_stimuli(rd)
    with (Path(rd) / "v3-stimuli.csv").open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDS)
        wr.writeheader()
        wr.writerows(rows)
    return rows


def load(rd: Path) -> list[dict]:
    p = Path(rd) / "v3-stimuli.csv"
    if not p.exists():
        return write(rd)
    num = lambda v: None if v in ("", None) else float(v)   # noqa: E731
    rows = list(csv.DictReader(p.open()))
    for r in rows:
        for k in ("start", "end", "u_nominal", "d", "planned_nonvideo", "nonvideo_load", "video_load", "total_load",
                  "video_calm", "video_rel_calm", "capacity_ratio"):
            r[k] = num(r[k])
    return rows


REACTION_BLOCKS = (("C2", "BG-CBR surge"), ("C5", "TCP surge"), ("M3", "BG-BURSTY / BG-MIX surge"))


def reaction_table(kdir: Path) -> str:
    """Video load relative to calm during stimuli, by nominal u (C5: by TCP cell), for C2 vs C5
    vs M3 (bgbursty, bgmix), per AQM; rep 1 and rep 2 side by side (median over the windows)."""
    cells: dict[tuple, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for rd in sorted(p for p in Path(kdir).iterdir() if p.is_dir() and p.name.startswith("v3-")):
        parts = rd.name.split("-")
        block, variant, aqm, rep = parts[1], parts[3], parts[4], int(parts[5][1:])
        if block not in {b for b, _ in REACTION_BLOCKS} or not (rd / "events.csv").exists():
            continue
        for r in load(rd):
            if r["video_rel_calm"] is None or r["stimulus_type"] not in ("surge", "tcp"):
                continue
            key_u = f"u {r['u_nominal']:g}" if r["u_nominal"] is not None else r["cell"]
            cells[(block, variant, aqm, key_u)][rep].append(r["video_rel_calm"])
    L = ["# Video load relative to calm during stimuli", "",
         "Median over the stimulus windows of the video arriving at the target / its calm rate "
         "(v3-stimuli.csv). C2 and M3 by nominal u; C5 (TCP) by its cell (cc, n, d). Reps side by side; "
         "n = windows.", "", "| block | stimulus | variant | AQM | u / cell | rep 1 (n) | rep 2 (n) |",
         "|---|---|---|---|---|---|---|"]
    names = dict(REACTION_BLOCKS)
    for (block, variant, aqm, key_u), reps in sorted(cells.items()):
        f = lambda v: f"{np.median(v):.2f} ({len(v)})" if v else "-"   # noqa: E731
        L.append(f"| {block} | {names[block]} | {variant} | {aqm} | {key_u} | {f(reps.get(1, []))} | {f(reps.get(2, []))} |")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> None:
    if argv[:1] == ["--reaction"]:
        text = reaction_table(Path(argv[1]))
        (Path(argv[1]) / "video-reaction.md").write_text(text)
        print(text)
        return
    for rd in map(Path, argv):
        for r in write(rd):
            print(rd.name, {k: r[k] for k in ("stimulus_type", "u_nominal", "d", "planned_nonvideo", "nonvideo_load",
                                              "video_rel_calm", "total_load")})


if __name__ == "__main__":
    main(sys.argv[1:])
