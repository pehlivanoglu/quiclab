#!/usr/bin/env python3
"""Audit of every link direction of a plan folder against its peak offered rate (user 2026-11-19, item 1).

    python3 simulation/simlab/link_audit.py <plan dir> [...]      # plan dirs as stagec_gen / gen_plan write them

Per link direction (a -> b): the rate the simulation gives it (scenario forward / reverse bandwidth, else the
scenario's link_defaults), whether it is a designed bottleneck (a shaped egress of v3-plan.json), and the peak
offered rate (wire Mb/s):
  video   every client whose path from the publisher crosses a -> b, at its wire rate; "keyframe peak" = the same
          with every client sending its keyframe in the same frame interval (sync phases): rate x GOP x ip /
          (GOP - 1 + ip)
  traffic every background / stimulus source whose route crosses a -> b, at the highest sum active at one time
          (bursts and constant sources), x v3.UDP_WIRE
Reverse directions carry ACKs only (not counted). Prints one line per plan: the worst non-bottleneck direction
(peak / rate) before and after the fast-links rule (non-bottleneck directions at FAST_MBPS), and every direction
whose peak exceeds its rate.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB / "scripts"))
import v3_suite as v3  # noqa: E402

FAST_MBPS = 100_000.0    # (P) user 2026-11-19: links that are not a designed bottleneck


def rates(scen: dict) -> dict:
    d = scen.get("link_defaults", {})
    out = {}
    for ln in scen["links"]:
        a, b = ln["from"], ln["to"]
        out[(a, b)] = (ln.get("forward") or {}).get("bandwidth_mbps") or (d.get("forward") or {}).get("bandwidth_mbps")
        out[(b, a)] = (ln.get("reverse") or {}).get("bandwidth_mbps") or (d.get("reverse") or {}).get("bandwidth_mbps")
    return out


def path(adj: dict, src: str, dst: str) -> list[tuple[str, str]]:
    prev, todo = {src: None}, [src]
    while todo:
        x = todo.pop(0)
        for y in adj[x]:
            if y not in prev:
                prev[y] = x
                todo.append(y)
    hops, y = [], dst
    while prev.get(y) is not None:
        hops.append((prev[y], y))
        y = prev[y]
    return hops[::-1]


def audit(pd: Path) -> dict:
    topo = yaml.safe_load((pd / "topology.yaml").read_text())
    scen = yaml.safe_load((pd / "scenario.yaml").read_text())
    plan = json.loads((pd / "v3-plan.json").read_text())
    rate = rates(scen)
    adj = defaultdict(set)
    for ln in topo["links"]:
        adj[ln["from"]].add(ln["to"])
        adj[ln["to"]].add(ln["from"])
    bott = {tuple(e["hop"].split("->")) for e in plan["egress"].values() if e.get("shaped")}
    pub = next(iter(topo["publishers"]))
    p = topo["publishers"][pub]
    gop = max(1, round(p.get("gop_ms", 1000) * p.get("fps", 30) / 1000))
    ip = p.get("ip_ratio", 4.0)
    kf = gop * ip / (gop - 1 + ip)
    video = defaultdict(float)
    for sid, s in topo["subscribers"].items():
        for h in path(adj, s["connects_to"], sid):
            video[h] += v3.wire(s["rate_kbps"])
    pts = defaultdict(list)
    routes = (topo.get("traffic") or {}).get("routes", {})
    for e in scen["events"]:
        if e.get("type") not in ("bursts", "bg") or e.get("route") not in routes:
            continue
        hops = list(zip(routes[e["route"]]["path"], routes[e["route"]]["path"][1:]))
        segs = [(e["at_s"] + b["start_s"], e["at_s"] + b["start_s"] + b["duration_s"], b["rate_mbps"])
                for b in e.get("bursts", [])] or [(e["at_s"], e["at_s"] + e.get("duration_s", 0), e.get("rate_mbps", 0))]
        for h in hops:
            for a, b, r in segs:
                pts[h] += [(a, r * v3.UDP_WIRE), (b, -r * v3.UDP_WIRE)]
    traffic = {}
    for h, ev in pts.items():
        cur = peak = 0.0
        for _, d in sorted(ev, key=lambda x: (x[0], x[1])):
            cur += d
            peak = max(peak, cur)
        traffic[h] = peak
    rows = []
    for h in set(video) | set(traffic):
        r = rate.get(h)
        mean, peak = video[h] + traffic.get(h, 0), video[h] * kf + traffic.get(h, 0)
        rows.append({"hop": f"{h[0]}->{h[1]}", "bottleneck": h in bott, "rate": r, "mean": round(mean, 1),
                     "peak": round(peak, 1), "after": r if h in bott else FAST_MBPS})
    return {"plan": pd.name, "rows": rows}


def main(argv: list[str]) -> None:
    print("| plan | non-bottleneck directions | worst peak / rate today (hop, peak, rate) | over 1 today | worst after (100 Gb/s) | bottleneck directions | bottleneck peak / capacity max |")
    print("|---|---|---|---|---|---|---|")
    for a in argv:
        r = audit(Path(a))
        nb = [x for x in r["rows"] if not x["bottleneck"] and x["rate"]]
        b = [x for x in r["rows"] if x["bottleneck"]]
        w = max(nb, key=lambda x: x["peak"] / x["rate"])
        over = [x for x in nb if x["peak"] > x["rate"]]
        wa = max(x["peak"] / x["after"] for x in nb)
        print(f"| {r['plan']} | {len(nb)} | {w['peak'] / w['rate']:.2f} ({w['hop']}, {w['peak']:.0f} / {w['rate']:.0f}) | "
              f"{len(over)}: {', '.join(x['hop'] for x in over[:4])}{' ...' if len(over) > 4 else ''} | {wa:.3f} | {len(b)} | "
              f"{max(x['peak'] / x['rate'] for x in b):.2f} |")


if __name__ == "__main__":
    main(sys.argv[1:])
