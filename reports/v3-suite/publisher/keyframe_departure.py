#!/usr/bin/env python3
"""How long do the synchronized keyframes of all clients take to leave the publisher?

    .venv/bin/python3 reports/v3-suite/publisher/keyframe_departure.py [--json <file>] <run> [...] > <file>.md

Per GOP (phase 0 everywhere: every client's keyframe is written at the same instant) and per
client: the keyframe starts with the first packet sent (sender <client>-pkts.csv) at or after
its write and ends at the packet that brings the payload sent since the write to the
keyframe's size minus one packet (the tail can share the next frame's first packet, sent
only when that frame is written; so the end is exact to one packet); payload = packet size
- a per-packet overhead (median over the run's GOPs
of (packet bytes - frame bytes) / packets). One stream per GOP, frames in order, so the
keyframe's bytes leave first; a keyframe longer than one frame interval is not cut.
GOP span = last keyframe packet of any client - first of any client. Model:
summed keyframe bytes on the wire (packet sizes + 42 B UDP / IP / Ethernet) / pub -> first
router capacity. Calm GOPs only (outside every stimulus window +- 1 s). Also per client: the
median keyframe emission time and the median rank of its first packet among the clients
(0 = first to start), to see whether a client that is served last gets a long emission time.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402

WIRE_EXTRA = 42   # router skb->len - QUIC packet size (router_trace.QUIC_OVERHEAD_BYTES)


def feed_mbps(rd: Path) -> float:
    sc = yaml.safe_load((rd / "scenario.yaml").read_text())
    topo = yaml.safe_load((rd / "topology.yaml").read_text())
    pub = next(iter(topo["publishers"]))
    for link in sc.get("links", []):
        if link["from"] == pub:
            return float((link.get("forward") or {}).get("bandwidth_mbps")
                         or sc["link_defaults"]["forward"]["bandwidth_mbps"])
    return float(sc["link_defaults"]["forward"]["bandwidth_mbps"])


def analyse(rd: Path) -> dict:
    run = det_eval.Run(rd)
    wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    busy = [(w["start"] - 1, w["end"] + 1) for w in wins]
    per, pacing, overheads = {}, {}, {}
    for sid in run.subs:
        fp, pp = run.sender_file(sid, "frames"), run.sender_file(sid, "pkts")
        if not (fp.exists() and pp.exists()):
            continue
        fr = pd.read_csv(fp)
        pk = pd.read_csv(pp, usecols=["send_mono_us", "size"]).sort_values("send_mono_us")
        ts = np.array([run.t_mono_us(x) for x in pk.send_mono_us])
        sz = pk["size"].values
        w = np.array([run.t_unix_us(x) for x in fr.write_us])
        keys = np.flatnonzero(fr.keyframe.values == 1)
        size = fr["size"].values.astype(float)
        cum = np.r_[0, np.cumsum(sz)]
        # per-packet overhead (QUIC header, AEAD tag, frame headers): median over GOPs of
        # (packet bytes - frame bytes) / packets; payload of a packet = size - overhead
        oh = []
        for g, i in enumerate(keys[:-1]):
            a, b = np.searchsorted(ts, [w[i], w[keys[g + 1]]], side="left")
            if b > a:
                oh.append((cum[b] - cum[a] - size[i:keys[g + 1]].sum()) / (b - a))
        overhead = float(np.median(oh)) if oh else 0.0
        pay = np.r_[0, np.cumsum(sz - overhead)]
        rows = {}
        for g, i in enumerate(keys[:-1]):
            a, b = np.searchsorted(ts, [w[i], w[keys[g + 1]]], side="left")
            if b <= a:
                continue
            # last keyframe packet: within one packet of the keyframe's size (its tail may ride in
            # the next frame's first packet, which leaves only when that frame is written)
            full = float(np.median(sz)) - overhead
            k = int(np.searchsorted(pay, pay[a] + size[i] - full - 1e-6, side="left"))
            k = min(max(k, a), b - 1)
            rows[int(round(w[i]))] = (ts[a], ts[k], int(cum[k + 1] - cum[a]) + WIRE_EXTRA * (k + 1 - a))
        overheads[sid] = round(overhead, 1)
        per[sid] = rows
        cc = run.sender_file(sid, "cc")
        if cc.exists():
            x = pd.read_csv(cc, usecols=["t_us", "pacing_bps"])
            tt = np.array([run.t_unix_us(v) for v in x.t_us])
            pacing[sid] = float(np.median(x.pacing_bps.values[(tt > det_eval.WARMUP_S + 5) & (x.pacing_bps.values > 0)]))
    cap = feed_mbps(rd)
    gops = sorted(set.intersection(*[set(r) for r in per.values()])) if per else []
    spans, models, ranks, emis = [], [], {s: [] for s in per}, {s: [] for s in per}
    for g in gops:
        if g < det_eval.WARMUP_S + 5 or g > run.duration - 3 or any(a <= g <= b for a, b in busy):
            continue
        first = {s: per[s][g][0] for s in per}
        last = {s: per[s][g][1] for s in per}
        spans.append((max(last.values()) - min(first.values())) * 1000)
        models.append(sum(per[s][g][2] for s in per) * 8 / (cap * 1e6) * 1000)
        order = sorted(per, key=lambda s: first[s])
        for k, s in enumerate(order):
            ranks[s].append(k)
            emis[s].append((last[s] - first[s]) * 1000)
    q = lambda x, p: round(float(np.percentile(x, p)), 1) if len(x) else None   # noqa: E731
    return {"run": f"{rd.parent.parent.name[-10:]}/{rd.parent.name}/{rd.name}", "feed_mbps": cap,
            "clients": len(per), "gops": len(spans), "overhead_B_per_packet": overheads,
            "span_ms_p50_p90_max": [q(spans, 50), q(spans, 90), round(max(spans), 1) if spans else None],
            "model_ms_p50": q(models, 50),
            "per_client": {s: {"rank_p50": q(ranks[s], 50), "emission_ms_p50": q(emis[s], 50),
                               "emission_ms_p90": q(emis[s], 90),
                               "pacing_mbps_p50": round(pacing[s] / 1e6, 1) if s in pacing else None}
                           for s in sorted(per)}}


def main(argv: list[str]) -> None:
    js = None
    if argv[:1] == ["--json"]:
        js, argv = Path(argv[1]), argv[2:]
    out = [analyse(Path(a)) for a in argv]
    print("# Keyframe departure from the publisher (existing synchronized runs)\n")
    print("| run | pub link Mb/s | clients | calm GOPs | span first->last packet ms p50 / p90 / max | "
          "summed keyframes / pub link ms (p50) |")
    print("|---|---|---|---|---|---|")
    for r in out:
        print(f"| {r['run']} | {r['feed_mbps']:g} | {r['clients']} | {r['gops']} | "
              f"{' / '.join(map(str, r['span_ms_p50_p90_max']))} | {r['model_ms_p50']} |")
    print("\n## Per client: median rank of the first packet among the clients, keyframe emission time p50/p90 ms, BBR pacing Mb/s (median)\n")
    for r in out:
        print(f"- {r['run']}: " + "; ".join(f"{s} rank {v['rank_p50']} emis {v['emission_ms_p50']}/{v['emission_ms_p90']} "
                                            f"pacing {v['pacing_mbps_p50']}" for s, v in r["per_client"].items()))
    if js:
        js.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
