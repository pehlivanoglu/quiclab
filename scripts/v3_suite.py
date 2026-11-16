#!/usr/bin/env python3
"""Scenario and Topology Suite v3 (spec: reports/v3-suite/spec.md): planner and campaign runner.

    .venv/bin/python3 scripts/v3_suite.py --plan-only                   # plan everything, print the budget, run nothing
    .venv/bin/python3 scripts/v3_suite.py --run                         # gate, then core, then micro (new folder)
    .venv/bin/python3 scripts/v3_suite.py --run --campaign .runs/<dir>  # resume: finished runs are kept
    .venv/bin/python3 scripts/v3_suite.py --smoke --run                 # smoke test (spec 8.8)
    .venv/bin/python3 scripts/v3_suite.py --held-out --plan-only        # N1-N5 on v3 (do not run before the freeze)

Everything new lives here (and in scripts/v3_gate.py for the checks); the existing
planners, topologies and scenarios are untouched. Constants are tagged
(S) spec value, (M) measured, (T) chosen by me / tunable, (FLAG) needs your decision.

Sizing (spec 1), per bottleneck egress e with video demand D_e (sum of client
rates x 1.03 behind e):  C_e = D_e / (s U),  BG_e = D_e (1 - s) / s.
Rates in this file are "router" rates: what tc counts on the egress (IP + UDP /
TCP + Ethernet header). qtraffic's rate is UDP payload, so a background or surge
of router rate R is sent at R / UDP_WIRE.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import random
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# ---------------------------------------------------------------- constants

S_DEFAULT, U_DEFAULT = 0.30, 0.70           # (S) default operating point
WIRE = 1.03                                  # (S) video wire rate / rendition rate (det_matrix.WIRE_OVERHEAD)
UDP_WIRE = (1200 + 20 + 8 + 14) / 1200       # (M) tc bytes per UDP payload byte: IP + UDP + Ethernet header
TCP_WIRE = (1448 + 52 + 14) / 1448           # (M) tc bytes per TCP goodput byte (MSS 1448, timestamps)
BG_FLOW_MBPS = 2.5                           # (S) BG-CBR flow size; also the surge flow size
PKT_BITS = 12000                             # (S) ms_to_pkts: 1500 B packets
PFIFO_MS, PFIFO_MIN_PKTS = 50.0, 20          # (S) pfifo "1 BDP"
RED_MIN_MS, RED_MAX_MS, RED_LIMIT_MS = 15.0, 45.0, 150.0   # (S)
MAX_LINK_MBPS, MAX_TOTAL_MBPS = 100.0, 300.0                # (S) constraints
MAX_FLOW_SHARE, MAX_FLOW_SHARE_WIDE = 0.15, 0.25            # (S) instrumented flow / bottleneck capacity
U3, D3 = (1.05, 1.15, 1.3), (2.0, 5.0, 10.0)                # (S) stimulus grids
WARMUP_S, GAP_S, TAIL_S = 15.0, (10.0, 15.0), 10.0          # (S)
CALM_S = 120.0                                               # (S)
NARROW_MS, WIDE_MS = (5.0, 7.5, 12.5, 20.0), (5.0, 15.0, 30.0, 45.0)   # (S) one-way access delays
FEED_MS = 5.0                                # (S) pub -> first router, each way
FEED_MBPS = 1000.0                           # (S) pub -> first router (100 Mb/s queued synchronized keyframes)
CTRL_KBPS, CTRL_MBPS, CTRL_MS = 2500, 50.0, 20.0             # (S) sub-ctrl, as today
SRC_SINK_MBPS = 1000.0                       # (S) tx-<e> / rx-<e> links
ACCESS_MBPS = 25.0                           # (S) T-ACCESS access egress
REV_MBPS = 10.0                              # (S) T-REV reverse target r1 -> r0, as today
LEGACY_C, LEGACY_U, LEGACY_PKTS = 17.5, 0.65, 100            # (S) today's base
TREE16_FALLBACK_S = 0.35                     # (S) if T-TREE16 fails health at s 0.30
RAMP_UP_S, RAMP_HOLD_S, RAMP_STEP_S = 5.0, 5.0, 0.5           # (S)
JOIN_UP_S, JOIN_HOLD_S, JOIN_DOWN_S = 15.0, 15.0, 10.0       # (S)
ASV_KEY_MS, ASV_P_MS = 5.85, 1.16            # (M) median emission time of a 5000 kb/s keyframe / P-frame,
                                             #     reports/v3-suite/asv-spread.json (scripts/v3_asv_spread.py)
LOSS_PCT, LOSS_S = (0.5, 1.0, 2.0), 10.0     # (S)
INDEP_MEAN_S, INDEP_MIN_S, INDEP_DURATION_S = 15.0, 5.0, 600.0   # (S)
SPARSE_GAP_S = (45.0, 75.0)                  # (S)
JOIN_T, JOIN_SUB = 60.0, "sub-d"             # (S) A-MIXED
PPBP_BURST_MBPS, PPBP_MEAN_BURST_S, PPBP_HURST = 2.0, 0.5, 0.8   # (T) today's det-ppbp burst parameters
MIX_SHARES = {"tcp": 0.5, "onoff": 0.3, "cbr": 0.2}          # (S) BG-MIX
ONOFF_ON_S, ONOFF_OFF_S = 2.0, 2.0           # (S)
MIX_FLOW_MBPS = BG_FLOW_MBPS                 # (T) mean rate per BG-MIX TCP flow (sets the TCP flow counts)
M12_JITTER_MS = 10.0                         # (S) M12; distribution normal as J1 (T)
BUDGET_H = 20.5                              # (S) emulated hours
SPEC_LISTED_VIOLATIONS = {                   # cells the spec lists although they break a constraint: kept (user, 2026-11-14)
    "legacy": "sub-d 5.15 Mb/s = 29 % of 17.5 Mb/s (> 25 %)",
    "s065u085": "sub-d 5.15 Mb/s = 25.1 % of 20.5 Mb/s (> 25 %)",
    "bw4x12": "12000 kb/s client = 27 % of 46.4 Mb/s (> 25 %)",
}

RUNS = ROOT / ".runs"
CLIENTS_STD = {"sub-a": 1000, "sub-b": 2500, "sub-c": 2500, "sub-d": 5000}
CLIENTS_LOW = {"sub-a": 500, "sub-b": 1000, "sub-c": 1000, "sub-d": 2500}
BASE_ROWS = {   # (S) table 3.1: variant -> (s, U, client set); legacy separately
    "s030u070": (0.30, 0.70, "std"), "s030u050": (0.30, 0.50, "std"), "s030u085": (0.30, 0.85, "std"),
    "s065u050": (0.65, 0.50, "std"), "s065u070": (0.65, 0.70, "std"), "s065u085": (0.65, 0.85, "std"),
    "s010u070": (0.10, 0.70, "low"), "s010u085": (0.10, 0.85, "low"),
}


def ms_to_pkts(c_mbps: float, ms: float) -> int:
    return math.ceil(c_mbps * 1e6 * ms / 1000 / PKT_BITS)


def wire(kbps: float) -> float:
    return kbps / 1000 * WIRE


# ---------------------------------------------------------------- topologies

@dataclass
class Egress:
    name: str
    hop: tuple[str, str]
    clients: list[str]
    demand: float                 # D_e, router Mb/s
    cap: float                    # C_e
    bg: float                     # BG_e (router Mb/s; 0 = none)
    shaped: bool = True           # False: unshaped 1000 Mb/s, no AQM (noroot up, uneven r1->r2)

    @property
    def route(self) -> str:
        return f"bg-{self.name}"


@dataclass
class Topo:
    """One v3 topology at one operating point: the topology YAML (as a dict), the
    scenario's links and the per-egress sizing."""
    kind: str
    variant: str
    s: float | None
    U: float
    rates: dict[str, int]         # instrumented client -> kb/s
    uplink: dict[str, str]        # client -> node before it
    leaf_of: dict[str, str]       # client -> egress name of its leaf
    egress: dict[str, Egress]
    topo: dict
    links: list[dict]
    routers: list[str]
    access: dict[str, tuple[str, str]] = field(default_factory=dict)   # client -> access egress (T-ACCESS)
    rev: tuple[str, str] | None = None                                   # T-REV reverse target
    delays: dict[str, float] = field(default_factory=dict)              # client -> one-way access delay

    def bottlenecks(self) -> list[Egress]:
        return [e for e in self.egress.values() if e.shaped]


def _size(demand: float, s: float, U: float) -> tuple[float, float]:
    return round(demand / (s * U), 2), round(demand * (1 - s) / s, 3)


class Builder:
    """Topology + scenario links of one v3 topology; nodes are added as the tree is described."""

    def __init__(self, fps: int = 30, ip_ratio: float = 4.0, cc: str = "bbr", seed: int = 1,
                 delays: tuple[float, ...] = NARROW_MS, delay_scale: float = 1.0, phases: str = "sync",
                 jitter: str | None = None):
        self.pub = {"cc_algo": cc, "fps": fps, "ip_ratio": ip_ratio, "seed": seed}
        self.subs: dict[str, dict] = {}
        self.routers: list[str] = []
        self.switches: list[str] = []
        self.links: list[dict] = []          # topology wiring
        self.cond: list[dict] = []           # scenario links
        self.senders: list[str] = []
        self.receivers: list[str] = []
        self.routes: dict[str, dict] = {}
        self.delays, self.scale, self.phases, self.jitter = delays, delay_scale, phases, jitter
        self.client_delay: dict[str, float] = {}

    def router(self, *ids: str) -> None:
        self.routers += ids

    def switch(self, *ids: str) -> None:
        self.switches += ids

    def link(self, a: str, b: str, fwd: dict | None = None, rev: dict | None = None) -> None:
        self.links.append({"from": a, "to": b})
        c = {"from": a, "to": b}
        if fwd:
            c["forward"] = fwd
        if rev:
            c["reverse"] = rev
        if fwd or rev:
            self.cond.append(c)

    def feed(self, first: str) -> None:
        d = FEED_MS * self.scale
        self.link("pub", first, {"bandwidth_mbps": FEED_MBPS, "delay_ms": d}, {"delay_ms": d})
        self.subs["sub-ctrl"] = {"connects_to": "pub", "rate_kbps": CTRL_KBPS}
        d = CTRL_MS * self.scale
        self.link(first, "sub-ctrl", {"bandwidth_mbps": CTRL_MBPS, "delay_ms": d}, {"delay_ms": d})

    def clients(self, up: str, rates: dict[str, int], bandwidth: float | None = None) -> None:
        """Clients on node `up`; access delays cycle through the delay set in order."""
        for i, (sid, kbps) in enumerate(rates.items()):
            d = self.delays[i % len(self.delays)] * self.scale
            self.client_delay[sid] = d
            fwd = {"delay_ms": d}
            rev = {"delay_ms": d}
            if bandwidth:
                fwd["bandwidth_mbps"] = bandwidth
            if self.jitter == "fwd":
                fwd.update(jitter_ms=M12_JITTER_MS, jitter_distribution="normal", jitter_keep_order=True)
            elif self.jitter == "rev":
                rev.update(jitter_ms=M12_JITTER_MS, jitter_distribution="normal", jitter_keep_order=True)
            self.subs[sid] = {"connects_to": "pub", "rate_kbps": kbps, "phase_ms": 0}
            self.link(up, sid, fwd, rev)

    def bottleneck(self, a: str, b: str, cap: float | None, name: str, bg: float) -> None:
        """Egress a -> b at `cap` (None: unshaped 1000 Mb/s, no tx/rx pair); a shaped egress gets
        its own tx/rx pair, the path of its background (if any) and of its stimuli."""
        self.link(a, b, {"bandwidth_mbps": cap if cap else SRC_SINK_MBPS})
        if cap:
            tx, rx = f"tx-{name}", f"rx-{name}"
            self.senders.append(tx)
            self.receivers.append(rx)
            full = {"bandwidth_mbps": SRC_SINK_MBPS}
            self.link(tx, a, full, full)
            self.link(b, rx, full, full)
            self.routes[f"bg-{name}"] = {"path": [tx, a, b, rx]}

    def endpoints(self, name: str, path: list[str]) -> None:
        """An extra traffic route (T-REV reverse path): sender before path[1], receiver after path[-2]."""
        tx, rx = path[0], path[-1]
        full = {"bandwidth_mbps": SRC_SINK_MBPS}
        self.senders.append(tx)
        self.receivers.append(rx)
        self.link(tx, path[1], full, full)
        self.link(path[-2], rx, full, full)
        self.routes[name] = {"path": path}

    def topology(self) -> dict:
        if self.phases == "stag":
            for i, sid in enumerate(s for s in self.subs if s != "sub-ctrl"):
                self.subs[sid]["phase_ms"] = (250 * i) % 1000
        t = {"publishers": {"pub": self.pub}, "subscribers": self.subs,
             "routers": {r: {"queue_metrics": {"enabled": True, "interval_ms": 25, "queue_interval_ms": 5}}
                         for r in self.routers},
             "switches": {s: {} for s in self.switches}, "links": self.links}
        if self.routes:
            t["traffic"] = {"senders": [{"id": x} for x in self.senders],
                            "receivers": [{"id": x} for x in self.receivers], "routes": self.routes}
        return t


def build(kind: str, variant: str = "", *, s: float | None = None, U: float = U_DEFAULT, rep: int = 1,
          bg: bool = True, **opts) -> Topo:
    """The v3 topology `kind` (base, access, split4, tree16, uneven, rev, large) at (s, U).
    s None = legacy (T-BASE only). opts: Builder options, rates (base client override),
    noroot (split4), pfifo_ms is not a topology property (see aqm_queues)."""
    rates_override = opts.pop("rates", None)
    b = Builder(seed=rep, **opts)
    egress: dict[str, Egress] = {}
    leaf_of: dict[str, str] = {}
    access: dict[str, tuple[str, str]] = {}
    rev = None

    def add(name: str, a: str, bnode: str, clients: list[str], shaped: bool = True,
            point: tuple[float, float] | None = None) -> None:
        d = round(sum(wire(rates[c]) for c in clients), 4)
        if not shaped:
            egress[name] = Egress(name, (a, bnode), clients, d, SRC_SINK_MBPS, 0.0, False)
            b.bottleneck(a, bnode, None, name, 0)
            return
        ss, uu = point or (s, U)
        if ss is None:
            c, g = LEGACY_C, 0.0
        else:
            c, g = _size(d, ss, uu)
        if not bg:
            g = 0.0
        egress[name] = Egress(name, (a, bnode), clients, d, c, g)
        b.bottleneck(a, bnode, c, name, g)

    if kind in ("base", "access", "rev", "large"):
        if kind == "large":
            rates = rates_override or {f"sub-{c}": r for c, r in zip("abcdefgh", (500, 1000, 1000, 2500, 2500,
                                                                                   2500, 5000, 5000))}
        else:
            rates = rates_override or dict(CLIENTS_STD)
        first = "r0" if kind == "rev" else "router"
        mid = "r1" if kind == "rev" else "router"
        b.router(*(["r0", "r1"] if kind == "rev" else ["router"]))
        b.switch("switch")
        b.feed(first)
        if kind == "rev":
            b.link("r0", "r1", None, {"bandwidth_mbps": REV_MBPS})
            rev = ("r1", "r0")
            b.endpoints("rshared", ["tx-rev", "r1", "r0", "rx-rev"])
        add("main", mid, "switch", list(rates))
        if kind == "access":
            ups = {sid: f"r{sid[-1]}" for sid in rates}
            for sid, r in ups.items():
                b.router(r)
                b.link("switch", r)
                b.clients(r, {sid: rates[sid]}, bandwidth=ACCESS_MBPS)
                access[sid] = (r, sid)
            # the access delays cycle over the four clients as on a leaf
            for i, sid in enumerate(rates):
                dd = b.delays[i % len(b.delays)] * b.scale
                b.client_delay[sid] = dd
                for c in b.cond:
                    if (c["from"], c["to"]) == (ups[sid], sid):
                        c["forward"]["delay_ms"] = c["reverse"]["delay_ms"] = dd
        else:
            b.clients("switch", rates)
        leaf_of = {sid: "main" for sid in rates}
        uplink = {sid: (access[sid][0] if sid in access else "switch") for sid in rates}
    elif kind == "split4":
        one = {"1": 1000, "2": 1000, "3": 2500, "4": 5000}
        rates = {f"{x}{i}": r for x in "ab" for i, r in one.items()}
        b.router("r1", "r2")
        b.switch("switch-a", "switch-b")
        b.feed("r1")
        add("up", "r1", "r2", list(rates), shaped=variant != "noroot")
        for x in "ab":
            add(x, "r2", f"switch-{x}", [c for c in rates if c[0] == x])
            b.clients(f"switch-{x}", {c: r for c, r in rates.items() if c[0] == x})
        leaf_of = {c: c[0] for c in rates}
        uplink = {c: f"switch-{c[0]}" for c in rates}
    elif kind == "tree16":
        one = {"1": 500, "2": 1000, "3": 1000, "4": 2500}
        rates = {f"{x}{i}": r for x in "abcd" for i, r in one.items()}
        b.router("rr", "r0", "r1", "r2")
        b.switch("switch-a", "switch-b", "switch-c", "switch-d")
        b.feed("rr")
        add("root", "rr", "r0", list(rates))
        add("X", "r0", "r1", [c for c in rates if c[0] in "ab"])
        add("Y", "r0", "r2", [c for c in rates if c[0] in "cd"])
        for x, r in (("a", "r1"), ("b", "r1"), ("c", "r2"), ("d", "r2")):
            add(x.upper(), r, f"switch-{x}", [c for c in rates if c[0] == x])
            b.clients(f"switch-{x}", {c: v for c, v in rates.items() if c[0] == x})
        leaf_of = {c: c[0].upper() for c in rates}
        uplink = {c: f"switch-{c[0]}" for c in rates}
    elif kind == "uneven":
        groups = {"a": (2500, 5000), "b": (500, 1000, 1000, 2500, 5000),
                  "c": (500, 500, 1000, 1000, 1000, 2500, 2500, 2500, 5000)}
        rates = {f"{x}{i + 1}": r for x, rs in groups.items() for i, r in enumerate(rs)}
        b.router("r1", "r2")
        b.switch("switch-a", "switch-b", "switch-c")
        b.feed("r1")
        add("up", "r1", "r2", list(rates), shaped=False)
        for x in groups:
            add(x.upper(), "r2", f"switch-{x}", [c for c in rates if c[0] == x])
            b.clients(f"switch-{x}", {c: r for c, r in rates.items() if c[0] == x})
        leaf_of = {c: c[0].upper() for c in rates}
        uplink = {c: f"switch-{c[0]}" for c in rates}
    else:
        raise ValueError(kind)
    return Topo(kind, variant, s, U, rates, uplink, leaf_of, egress, b.topology(), b.cond, b.routers,
                access, rev, b.client_delay)


def constraint_check(t: Topo) -> list[str]:
    """Violations of spec 1 (strings; empty = fine)."""
    out = []
    wide = t.s is None or (t.s or 0) >= 0.65
    limit = MAX_FLOW_SHARE_WIDE if wide else MAX_FLOW_SHARE
    for e in t.bottlenecks():
        if e.cap > MAX_LINK_MBPS:
            out.append(f"{e.name} {e.cap:g} Mb/s > {MAX_LINK_MBPS:g}")
        for c in e.clients:
            share = wire(t.rates[c]) / e.cap
            if share > limit + 1e-9:
                out.append(f"{c} {wire(t.rates[c]):.2f} Mb/s = {share:.1%} of {e.name} {e.cap:g} Mb/s (> {limit:.0%})")
    # (user decision 2026-11-14) the flow-share rule does not apply to a client's private access link
    total = sum(e.demand + e.bg for e in t.bottlenecks()) + sum(wire(t.rates[s]) for s in t.access)
    if total > MAX_TOTAL_MBPS:
        out.append(f"total through router egresses {total:.1f} Mb/s > {MAX_TOTAL_MBPS:g}")
    return out


# ---------------------------------------------------------------- AQM (spec 2.3)

def egress_caps(t: Topo) -> dict[tuple[str, str], float]:
    """Capacity of every router egress (htb rate; link_defaults 100 Mb/s where none is set)."""
    caps = {}
    cond = {(c["from"], c["to"]): c for c in t.links}
    for link in t.topo["links"]:
        a, b = link["from"], link["to"]
        c = cond.get((a, b), {})
        caps[(a, b)] = c.get("forward", {}).get("bandwidth_mbps", 100.0)
        caps[(b, a)] = c.get("reverse", {}).get("bandwidth_mbps", 100.0)
    return {h: v for h, v in caps.items() if h[0] in t.routers}


def queue(aqm: str, cap: float, pfifo_ms: float, legacy: bool = False) -> dict:
    if aqm == "pfifo":
        return {"aqm": "pfifo", "queue_limit_packets": LEGACY_PKTS if legacy else
                max(PFIFO_MIN_PKTS, ms_to_pkts(cap, pfifo_ms))}
    if aqm in ("codel", "pie", "fq_codel"):
        return {"aqm": aqm, "ecn": False}            # kernel default limit
    if aqm == "red":
        return {"aqm": "red", "ecn": False, "queue_limit_packets": ms_to_pkts(cap, RED_LIMIT_MS),
                "red_min_bytes": round(cap * 1e6 * RED_MIN_MS / 1000 / 8),
                "red_max_bytes": round(cap * 1e6 * RED_MAX_MS / 1000 / 8)}
    if aqm == "cake":
        return {"aqm": "cake"}
    raise ValueError(aqm)


def aqm_routers(t: Topo, aqm: str, pfifo_ms: float = PFIFO_MS) -> dict:
    """Scenario `routers:`: every router egress listed with its own queue; source / sink
    and unshaped egresses carry none. aqm 'mixab': r1 pfifo, r2 -> switch-a pfifo,
    r2 -> switch-b fq_codel (the rest of r2 pfifo)."""
    unshaped = {e.hop for e in t.egress.values() if not e.shaped}
    out: dict[str, dict] = {}
    for r in t.routers:
        egress = {}
        for (a, b), cap in sorted(egress_caps(t).items()):
            if a != r:
                continue
            if b.startswith(("tx-", "rx-")) or (a, b) in unshaped:
                egress[b] = {}
                continue
            name = aqm
            if aqm == "mixab":
                name = "fq_codel" if (a, b) == ("r2", "switch-b") else "pfifo"
            egress[b] = queue(name, cap, pfifo_ms, legacy=t.s is None)
        base = queue("pfifo" if aqm == "mixab" else aqm, 100.0, pfifo_ms, legacy=t.s is None)
        out[r] = {**base, "egress": egress}
    return out


# ---------------------------------------------------------------- background (spec 2.5)

def background(t: Topo, mode: str, rep: int, duration: float) -> list[dict]:
    events = []
    for i, e in enumerate(t.bottlenecks()):
        if e.bg <= 0:
            continue
        seed = rep * 1000 + i
        if mode == "cbr":
            events.append(cbr_event(f"bg-{e.name}", e.route, e.bg, duration, seed))
        elif mode == "bursty":
            events.append({"at_s": 0, "type": "ppbp", "id": f"bg-{e.name}", "route": e.route, "duration_s": duration,
                           "mean_mbps": round(e.bg / UDP_WIRE, 3), "burst_mbps": PPBP_BURST_MBPS,
                           "mean_burst_s": PPBP_MEAN_BURST_S, "hurst": PPBP_HURST, "seed": seed})
        elif mode == "mix":
            rng = random.Random(seed)
            tcp = MIX_SHARES["tcp"] * e.bg
            n_tcp = max(2, 2 * round(tcp / MIX_FLOW_MBPS / 2))        # even: half CUBIC, half BBR
            for k in range(n_tcp):
                events.append({"at_s": 0, "type": "bg", "id": f"bg-{e.name}-t{k}", "route": e.route,
                               "duration_s": duration, "rate_mbps": round(tcp / n_tcp / TCP_WIRE, 3),
                               "process": "tcp", "cc": "cubic" if k % 2 == 0 else "bbr"})
            onoff = MIX_SHARES["onoff"] * e.bg
            n_on = max(1, round(onoff / MIX_FLOW_MBPS))
            for k in range(n_on):
                events.append({"at_s": 0, "type": "bg", "id": f"bg-{e.name}-o{k}", "route": e.route,
                               "duration_s": duration, "rate_mbps": round(onoff / n_on / TCP_WIRE, 3),
                               "process": "tcp", "cc": "cubic" if k % 2 == 0 else "bbr",
                               "on_s": ONOFF_ON_S, "off_s": ONOFF_OFF_S,
                               "phase_s": round(rng.uniform(0, ONOFF_ON_S + ONOFF_OFF_S), 3)})
            events.append(cbr_event(f"bg-{e.name}-c", e.route, MIX_SHARES["cbr"] * e.bg, duration, seed))
        else:
            raise ValueError(mode)
    return events


def cbr_event(eid: str, route: str, router_mbps: float, duration: float, seed: int) -> dict:
    n = max(4, round(router_mbps / BG_FLOW_MBPS))
    return {"at_s": 0, "type": "bg", "id": eid, "route": route, "duration_s": duration,
            "rate_mbps": round(router_mbps / UDP_WIRE, 4), "process": "poisson", "flow_weights": [1.0] * n,
            "seed": seed}


def surge_weights(router_mbps: float) -> list[float]:
    """Flows of 2.5 Mb/s, the last one fractional (spec 4)."""
    n = int(router_mbps // BG_FLOW_MBPS)
    rest = round(router_mbps - n * BG_FLOW_MBPS, 4)
    return [BG_FLOW_MBPS] * n + ([rest] if rest > 1e-3 else []) or [1.0]


# ---------------------------------------------------------------- stimuli (spec 4)

def _window(start, end, kind, target, cell, expected, stimulus_type, hop, **extra) -> dict:
    return {"start": round(start, 3), "end": round(end, 3), "kind": kind, "target": target, "cell": cell,
            "expected": sorted(expected), "stimulus_type": stimulus_type, "concurrent": False, "hop": hop, **extra}


class Stim:
    """Event and window factory for one run."""

    def __init__(self, t: Topo, rep: int):
        self.t, self.rep, self.n = t, rep, 0
        self.events: list[dict] = []
        self.windows: list[dict] = []

    def _id(self, kind: str, tgt: str) -> str:
        self.n += 1
        return f"{kind}{self.n}-{tgt}"

    def _hop(self, e: Egress) -> str:
        return f"{e.hop[0]}->{e.hop[1]}"

    def surge(self, tgt: str, at: float, u: float, d: float, cell: str, ramp: bool = False) -> None:
        e = self.t.egress[tgt]
        extra = (u - self.t.U) * e.cap
        ev = {"at_s": round(at, 3), "type": "bursts", "id": self._id("ramp" if ramp else "surge", tgt),
              "route": e.route, "process": "poisson", "flow_weights": surge_weights(extra),
              "seed": self.rep * 100000 + self.n,
              "bursts": [{"start_s": 0, "duration_s": d, "rate_mbps": round(extra / UDP_WIRE, 4)}],
              "label": f"{'ramp' if ramp else 'surge'} u={u} d={d} {tgt}"}
        if ramp:
            ev.update(ramp_up_s=RAMP_UP_S, ramp_step_s=RAMP_STEP_S)
        self.events.append(ev)
        self.windows.append(_window(at, at + d, "ramp" if ramp else "surge", tgt, cell, e.clients,
                                    "ramp" if ramp else "surge", self._hop(e), u=u, d=d,
                                    extra_mbps=round(extra, 3)))

    def tcp(self, tgt: str, at: float, n: int, cc: str, d: float, cell: str) -> None:
        e = self.t.egress[tgt]
        self.events.append({"at_s": round(at, 3), "type": "flow", "kind": "tcp", "id": self._id("tcp", tgt),
                            "route": e.route, "duration_s": d, "cc": cc, "parallel": n,
                            "label": f"tcp n={n} cc={cc} d={d} {tgt}"})
        self.windows.append(_window(at, at + d, "tcp", tgt, cell, e.clients, "tcp", self._hop(e), u=None, d=d,
                                    tcp_flows=n, cc=cc))

    def join(self, tgt: str, at: float, u: float, cell: str) -> float:
        """ASV ramp at the next GOP boundary; returns its end."""
        e = self.t.egress[tgt]
        at = float(math.ceil(at))
        d = JOIN_UP_S + JOIN_HOLD_S + JOIN_DOWN_S
        extra = (u - self.t.U) * e.cap
        self.events.append({"at_s": at, "type": "bursts", "id": self._id("join", tgt), "route": e.route,
                            "process": "asv", "asv": {"rendition_kbps": 5000, "key_spread_ms": ASV_KEY_MS,
                                                      "p_spread_ms": ASV_P_MS},
                            "ramp_up_s": JOIN_UP_S, "ramp_down_s": JOIN_DOWN_S, "ramp_step_s": 1.0,
                            "bursts": [{"start_s": 0, "duration_s": d, "rate_mbps": round(extra / UDP_WIRE, 4)}],
                            "label": f"join u={u} d={d:g} {tgt}"})
        self.windows.append(_window(at, at + d, "join", tgt, cell, e.clients, "join", self._hop(e), u=u, d=d,
                                    extra_mbps=round(extra, 3)))
        return at + d

    def capdrop(self, tgt: str, at: float, u: float, d: float, cell: str) -> None:
        if tgt in self.t.egress:
            e = self.t.egress[tgt]
            a, b, base, low = e.hop[0], e.hop[1], e.cap, round(self.t.U * e.cap / u, 3)
            expected, hop, kind = e.clients, self._hop(e), "cap"
        else:   # a client's access egress: demand / u
            a, b = self.t.access[tgt]
            base, low = ACCESS_MBPS, round(wire(self.t.rates[tgt]) / u, 3)
            expected, hop, kind = [tgt], f"{a}->{b}", "access"
        self.events += [{"at_s": round(at, 3), "type": "link", "from": a, "to": b, "bandwidth_mbps": low,
                         "label": f"burst u={u} d={d} {tgt}"},
                        {"at_s": round(at + d, 3), "type": "link", "from": a, "to": b, "bandwidth_mbps": base,
                         "label": "burst-end"}]
        self.windows.append(_window(at, at + d, kind, tgt, cell, expected, "capdrop", hop, u=u, d=d))

    def legacy_udp(self, at: float, u: float, d: float, cell: str) -> None:
        """C3b: today's burstudp rule (UDP at u x capacity - demand, paced) on the v3 grid."""
        e = self.t.egress["main"]
        rate = u * e.cap - e.demand
        self.events.append({"at_s": round(at, 3), "type": "bursts", "id": self._id("udp", "main"), "route": e.route,
                            "bursts": [{"start_s": 0, "duration_s": d, "rate_mbps": round(rate, 3)}],
                            "label": f"udp u={u} d={d} main"})
        self.windows.append(_window(at, at + d, "udp", "main", cell, e.clients, "udp", self._hop(e), u=u, d=d))

    def revburst(self, at: float, u: float, d: float, cell: str) -> None:
        self.events.append({"at_s": round(at, 3), "type": "bursts", "id": self._id("rev", "rev"), "route": "rshared",
                            "process": "poisson", "flow_weights": surge_weights(u * REV_MBPS),
                            "seed": self.rep * 100000 + self.n,
                            "bursts": [{"start_s": 0, "duration_s": d, "rate_mbps": round(u * REV_MBPS / UDP_WIRE, 4)}],
                            "label": f"rev u={u} d={d}"})
        self.windows.append(_window(at, at + d, "rev", "rev", cell, [], "revburst", None, u=u, d=d))

    def loss(self, sid: str, at: float, pct: float, cell: str) -> None:
        a = self.t.uplink[sid]
        self.events += [{"at_s": round(at, 3), "type": "link", "from": a, "to": sid, "loss_pct": pct,
                         "label": f"loss p={pct} d={LOSS_S:g} {sid}"},
                        {"at_s": round(at + LOSS_S, 3), "type": "link", "from": a, "to": sid, "loss_pct": 0,
                         "label": "loss-end"}]
        self.windows.append(_window(at, at + LOSS_S, "loss", sid, cell, [sid], "loss", f"{a}->{sid}",
                                    loss_pct=pct, d=LOSS_S))


def flag_concurrent(windows: list[dict]) -> list[dict]:
    for w in windows:
        w["concurrent"] = any(v is not w and v["target"] != w["target"] and v["start"] - 1.0 <= w["end"]
                              and w["start"] - 1.0 <= v["end"] for v in windows)
    return sorted(windows, key=lambda w: (w["start"], w["target"]))


# ---------------------------------------------------------------- scenario types (spec 5)

def sequence(st: Stim, cells: list, rng: random.Random, make, gap=GAP_S, t0: float = WARMUP_S) -> float:
    """Cells in order, one after another with U(gap) between; make(st, t, cell) -> span. Returns duration."""
    t = t0
    for cell in cells:
        span = make(st, t, cell)
        t += span + rng.uniform(*gap)
    return round(t - gap[0] + TAIL_S)


def combined(st: Stim, t: float, cell) -> float:
    """surge cell (u, d, 'a+b@0.5'): parts at their offsets."""
    u, d, name = cell
    span = d
    for part in name.split("+"):
        tgt, _, off = part.partition("@")
        st.surge(tgt, t + float(off or 0), u, d, name)
        span = max(span, float(off or 0) + d)
    return span


def indep(st: Stim, targets: list[str], rng: random.Random, duration: float = INDEP_DURATION_S,
          make=None) -> float:
    for tgt in targets:
        t = WARMUP_S + max(INDEP_MIN_S, rng.expovariate(1 / INDEP_MEAN_S))
        while True:
            u, d = rng.choice(U3), rng.choice(D3)
            if t + d > duration - TAIL_S:
                break
            (make or (lambda st_, tgt_, t_, u_, d_: st_.surge(tgt_, t_, u_, d_, tgt_)))(st, tgt, t, u, d)
            t += d + max(INDEP_MIN_S, rng.expovariate(1 / INDEP_MEAN_S))
    return duration


def plan_type(rtype: str, t: Topo, rep: int, smoke: bool = False, stim: str = "surge") -> tuple[list, list, float]:
    """(events, windows, duration) of one scenario type on topology t, seed = rep."""
    rng = random.Random(f"v3-{rtype}-{rep}")
    st = Stim(t, rep)
    grid = [(u, d) for u in U3 for d in D3]
    if rtype == "calm":
        duration = 60.0 if smoke else CALM_S
    elif rtype == "sburst":
        if smoke:
            st.surge("main", WARMUP_S + 30, 1.15, 5.0, "smoke")
            duration = 90.0
        else:
            cells = grid * 2
            rng.shuffle(cells)
            if stim == "capdrop":
                make = lambda s_, t_, c: (s_.capdrop("main", t_, c[0], c[1], f"u={c[0]} d={c[1]}"), c[1])[1]  # noqa
            elif stim == "legacy":
                make = lambda s_, t_, c: (s_.legacy_udp(t_, c[0], c[1], f"u={c[0]} d={c[1]}"), c[1])[1]  # noqa
            else:
                make = lambda s_, t_, c: (s_.surge("main", t_, c[0], c[1], f"u={c[0]} d={c[1]}"), c[1])[1]  # noqa
            duration = sequence(st, cells, rng, make)
    elif rtype == "sramp":
        cells = list(U3) * 3
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, lambda s_, t_, u: (s_.surge("main", t_, u, RAMP_UP_S + RAMP_HOLD_S,
                                                                         f"u={u}", ramp=True),
                                                                RAMP_UP_S + RAMP_HOLD_S)[1])
    elif rtype == "stcp":
        cells = [(cc, n, d) for cc in ("cubic", "bbr") for n in (2, 4) for d in (5.0, 10.0)] * 2
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, lambda s_, t_, c: (s_.tcp("main", t_, c[1], c[0], c[2],
                                                                       f"{c[0]} n={c[1]} d={c[2]}"), c[2])[1])
    elif rtype == "sjoin":
        cells = [1.05, 1.15] * 2
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, lambda s_, t_, u: s_.join("main", t_, u, f"u={u}") - t_)
    elif rtype == "hhier":
        noroot = not t.egress["up"].shaped
        singles = ["a", "b"] if noroot else ["up", "a", "b"]
        combos = ["a+b", "a+b@0.5", "a+b@2"] + ([] if noroot else ["a+up"])
        cells = [(u, d, x) for x in singles for u, d in grid]
        cells += [(u, d, x) for x in combos for u in (1.15, 1.3) for d in D3]
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, combined)
    elif rtype == "hdepth":
        cells = [(u, d, x) for x in ("A", "B", "C", "D", "X", "Y", "root", "A+C") for u in (1.15, 1.3) for d in D3]
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, combined)
    elif rtype == "hindep":
        duration = indep(st, ["up", "a", "b"], rng)
    elif rtype == "huneven":
        duration = indep(st, ["A", "B", "C"], rng)
    elif rtype == "amixed":
        cells = [(u, d, "main") for u, d in grid] + [(1.3, d, c) for c in sorted(t.access) for d in D3]
        rng.shuffle(cells)
        tt, pending = WARMUP_S, list(cells)
        while pending:   # the joining client has no private events before it joins (+10 s)
            pick = next(c for c in pending if tt > JOIN_T + 10 or c[2] != JOIN_SUB)
            pending.remove(pick)
            u, d, tgt = pick
            if tgt == "main":
                st.surge("main", tt, u, d, "shared")
            else:
                st.capdrop(tgt, tt, u, d, "private")
            tt += d + rng.uniform(*GAP_S)
        st.events.append({"at_s": JOIN_T, "type": "join", "subscriber": JOIN_SUB})
        duration = round(tt - GAP_S[0] + TAIL_S)
    elif rtype == "llong":
        cells = [(u, d, x) for x in ("up", "a", "b") for u in (1.15, 1.3) for d in (10.0, 30.0)]
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, combined)
    elif rtype == "rrev":
        cells = [("fwd", u, d) for u, d in grid]
        cells += [("rev", u, (2.0, 5.0)[i % 2]) for i, u in enumerate(list(U3) * 3)]
        rng.shuffle(cells)

        def make(s_, t_, c):
            if c[0] == "fwd":
                s_.surge("main", t_, c[1], c[2], "fwd")
            else:
                s_.revburst(t_, c[1], c[2], "rev")
            return c[2]
        duration = sequence(st, cells, rng, make)
    elif rtype == "nloss":
        clients = sorted(t.rates)
        cells = [p for p in LOSS_PCT for _ in range(3)]
        rng.shuffle(cells)
        order = []
        while len(order) < len(cells):
            batch = list(clients)
            rng.shuffle(batch)
            if order and batch[0] == order[-1]:
                batch.reverse()
            order += batch
        it = iter(order)
        duration = sequence(st, cells, rng, lambda s_, t_, p: (s_.loss(next(it), t_, p, f"p={p}"), LOSS_S)[1])
    elif rtype == "sstress":
        cells = [(2.0, d) for d in (2.0, 5.0)] * 2 + [(u, d) for u in (1.3, 2.0) for d in (0.2, 0.5)] * 3
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, lambda s_, t_, c: (s_.surge("main", t_, c[0], c[1],
                                                                         f"u={c[0]} d={c[1]}"), c[1])[1])
    elif rtype == "ssparse":
        cells = list(grid)
        rng.shuffle(cells)
        duration = sequence(st, cells, rng, lambda s_, t_, c: (s_.surge("main", t_, c[0], c[1],
                                                                         f"u={c[0]} d={c[1]}"), c[1])[1],
                            gap=SPARSE_GAP_S)
    elif rtype == "n3cross":   # held-out N3: tcp or surge, independent timing on up, a, b
        def make(s_, tgt, t_, u, d):
            if rng.random() < 0.5:
                s_.surge(tgt, t_, u, d, f"{tgt}:surge")
            else:
                s_.tcp(tgt, t_, rng.choice((2, 4)), "cubic", d, f"{tgt}:tcp")
        duration = indep(st, ["up", "a", "b"], rng, make=make)
    elif rtype == "n4trace":
        duration = plan_trace(st, t, rng)
    elif rtype == "n5churn":
        duration = plan_churn(st, t, rng)
    else:
        raise ValueError(rtype)
    return st.events, flag_concurrent(st.windows), float(duration)


def plan_trace(st: Stim, t: Topo, rng: random.Random) -> float:
    """Held-out N4 on T-ACCESS: every access egress replays a different scaled cellular trace
    (the grouping campaign's N4 law and helpers, unchanged: 200 ms steps, mean 2 x the
    client's wire rate), shared surges on `main` with U(10, 15) s gaps. Private truth
    windows: the trace below the client's wire rate, dips closer than 1 s merged."""
    import numpy as np
    import grouping_campaign as gc
    duration = INDEP_DURATION_S
    tt = WARMUP_S
    while True:
        u, d = rng.choice(U3), rng.choice(D3)
        if tt + d > duration - TAIL_S:
            break
        st.surge("main", tt, u, d, "shared")
        tt += d + rng.uniform(*GAP_S)
    names = sorted(x for x in json.loads((gc.TRACES / "index.json").read_text())
                   if not any(e in x for e in gc.TRACE_EXCLUDE))
    rng.shuffle(names)
    step = gc.TRACE_STEP_S
    for i, c in enumerate(sorted(t.access)):
        a, b = t.access[c]
        name = names[i % len(names)]
        offset = round(rng.uniform(0, len(gc.load_trace(name)) * step), 1)
        seg = gc.trace_segment(name, offset, duration)
        w = wire(t.rates[c])
        mult, below, adjusted = gc.scale_trace(seg, w)
        cap = np.maximum(np.round(seg * mult, 3), gc.TRACE_MIN_MBPS)
        prev = None
        for k, rate in enumerate(cap):
            if rate != prev and k * step < duration:
                st.events.append({"at_s": round(k * step, 3), "type": "link", "from": a, "to": b,
                                  "bandwidth_mbps": float(rate), "label": "trace"})
                prev = rate
        under = cap < w
        gap = int(round(gc.TRACE_MERGE_S / step))
        k = 0
        while k < len(under):
            if under[k]:
                j = k
                while True:
                    nxt = next((x for x in range(j + 1, min(j + 1 + gap, len(under))) if under[x]), None)
                    if nxt is None:
                        break
                    j = nxt
                st.windows.append(_window(k * step, (j + 1) * step, "access", c, "private", [c], "trace", f"{a}->{b}"))
                k = j + 1
            else:
                k += 1
    st.events.sort(key=lambda e: e["at_s"])
    return duration


def plan_churn(st: Stim, t: Topo, rng: random.Random) -> float:
    """Held-out N5 on v3 `large`: clients alternate on / off (the grouping campaign's churn
    law, unchanged); shared surges sized to the clients that are on."""
    import grouping_campaign as gc
    duration = 900.0
    sessions = gc.churn_sessions(sorted(t.rates), rng, duration)
    for sid, ss in sessions.items():
        for k, (on, off) in enumerate(ss):
            if not (k == 0 and on == 0):
                st.events.append({"at_s": round(on, 3), "type": "join", "subscriber": sid})
            if off is not None:
                st.events.append({"at_s": round(off, 3), "type": "leave", "subscriber": sid})
    tt = WARMUP_S
    e = t.egress["main"]
    while tt < duration - 30:
        u, d = rng.choice(U3), rng.choice(D3)
        on = [s for s, ss in sessions.items() if any(a <= tt and (b is None or b > tt + d) for a, b in ss)]
        st.surge("main", tt, u, d, "shared")
        st.windows[-1]["expected"] = sorted(on)
        tt += d + rng.uniform(*GAP_S)
    return duration


# ---------------------------------------------------------------- campaign matrix (spec 6)

@dataclass
class Cell:
    block: str
    rtype: str
    variant: str
    kind: str
    aqms: tuple[str, ...]
    s: float | None = S_DEFAULT
    U: float = U_DEFAULT
    bg_mode: str = "cbr"
    rtt: str = "narrow"
    pfifo_ms: float = PFIFO_MS
    stim: str = "surge"
    build_opts: dict = field(default_factory=dict)
    reps: tuple[int, ...] = (1, 2)
    note: str = ""


def base_row(variant: str) -> dict:
    if variant == "legacy":
        return {"s": None, "U": LEGACY_U}
    s, U, cset = BASE_ROWS[variant]
    return {"s": s, "U": U, "build_opts": {"rates": dict(CLIENTS_LOW if cset == "low" else CLIENTS_STD)}}


GATE = [Cell("G1", "calm", "s030u070", "base", ("pfifo",), reps=(1,)),
        Cell("G1", "calm", "legacy", "base", ("pfifo",), reps=(1,), **base_row("legacy")),
        *[Cell("G2", "calm", k, k, ("pfifo",), reps=(1,)) for k in ("split4", "tree16", "uneven", "access", "rev")],
        Cell("G3", "sburst", "s030u070", "base", ("pfifo", "fq_codel"), reps=(1,))]

CORE = [
    *[Cell("C1a", "calm", v, "base", ("pfifo", "codel"), **base_row(v)) for v in (*BASE_ROWS, "legacy")],
    *[Cell("C1b", "calm", k, k, ("pfifo",)) for k in ("split4", "tree16", "uneven")],
    Cell("C2", "sburst", "s030u070", "base", ("pfifo", "codel", "pie", "fq_codel", "red", "cake")),
    *[Cell("C3a", "sburst", v, "base", ("pfifo", "codel"), **base_row(v)) for v in ("s010u070", "s065u070")],
    Cell("C3b", "sburst", "legacy", "base", ("pfifo",), stim="legacy", **base_row("legacy")),
    Cell("C4", "sramp", "s030u070", "base", ("pfifo", "codel", "pie", "fq_codel")),
    Cell("C5", "stcp", "s030u070", "base", ("pfifo", "codel", "pie", "fq_codel")),
    Cell("C6", "sjoin", "s030u070", "base", ("pfifo", "codel", "fq_codel")),
    Cell("C7", "hhier", "s030", "split4", ("pfifo", "codel", "pie", "fq_codel")),
    Cell("C8", "hhier", "s065", "split4", ("pfifo",), s=0.65),
    Cell("C9", "hdepth", "tree16", "tree16", ("pfifo", "codel", "fq_codel")),
    Cell("C10", "hindep", "s030", "split4", ("pfifo", "codel", "fq_codel")),
    Cell("C11", "huneven", "uneven", "uneven", ("pfifo", "codel")),
    Cell("C12", "amixed", "access", "access", ("pfifo", "codel", "pie", "fq_codel")),
    Cell("C13", "llong", "s030", "split4", ("pfifo", "codel")),
    Cell("C14", "rrev", "rev", "rev", ("pfifo", "fq_codel")),
    Cell("C15", "nloss", "s030u070", "base", ("pfifo", "codel")),
]

MICRO = [
    *[Cell("M1", "sburst", f"q{ms:g}", "base", ("pfifo",), pfifo_ms=ms) for ms in (100.0, 300.0)],
    Cell("M2", "sburst", "capdrop", "base", ("pfifo", "codel"), stim="capdrop"),
    *[Cell("M3", "sburst", f"bg{m}", "base", ("pfifo", "codel"), bg_mode=m) for m in ("bursty", "mix")],
    Cell("M4", "sburst", "rttx05", "base", ("pfifo",), rtt="x0.5", pfifo_ms=25.0, build_opts={"delay_scale": 0.5}),
    Cell("M4", "sburst", "rttx4", "base", ("pfifo",), rtt="x4", pfifo_ms=200.0, build_opts={"delay_scale": 4.0}),
    Cell("M4", "sburst", "rttwide", "base", ("pfifo",), rtt="wide", pfifo_ms=100.0, build_opts={"delays": WIDE_MS}),
    *[Cell("M5", "sburst", f"fps{f}", "base", ("pfifo", "codel"), build_opts={"fps": f}) for f in (15, 60)],
    *[Cell("M6", r, "stag", "base", ("pfifo",), build_opts={"phases": "stag"}) for r in ("sburst", "calm")],
    Cell("M7", "hhier", "noroot", "split4", ("pfifo",)),
    Cell("M8", "hhier", "mixab", "split4", ("mixab",)),
    Cell("M9", "sstress", "s030u070", "base", ("pfifo", "codel")),
    *[Cell("M10", "sburst", f"ip{r}", "base", ("pfifo",), build_opts={"ip_ratio": float(r)}) for r in (2, 8)],
    Cell("M11", "sburst", "bw4x1", "base", ("pfifo",), s=0.65, build_opts={"rates": {f"sub-{c}": 1000 for c in "abcd"}}),
    Cell("M11", "sburst", "bw4x8", "base", ("pfifo",), s=0.65, build_opts={"rates": {f"sub-{c}": 8000 for c in "abcd"}}),
    Cell("M11", "sburst", "bw4x12", "base", ("pfifo",), s=0.65,
         build_opts={"rates": {"sub-a": 1000, "sub-b": 2500, "sub-c": 5000, "sub-d": 12000}}),
    *[Cell("M12", "sburst", f"jit{x}", "base", ("pfifo",), build_opts={"jitter": x}) for x in ("fwd", "rev")],
    Cell("M13", "sburst", "copa", "base", ("pfifo", "codel"), build_opts={"cc": "copa"}),
    Cell("M14", "ssparse", "s030u070", "base", ("pfifo",)),
]

HELD_OUT = [   # spec 6.4: regenerate N1-N5 on v3; 5 reps as campaign v2; NOT run in this campaign
    Cell("N1", "hindep", "split4", "split4", ("pfifo", "pie", "fq_codel"), reps=(1, 2, 3, 4, 5)),
    Cell("N2", "huneven", "uneven", "uneven", ("pfifo", "pie", "fq_codel"), reps=(1, 2, 3, 4, 5)),
    Cell("N3", "n3cross", "split4", "split4", ("pfifo", "fq_codel"), reps=(1, 2, 3, 4, 5)),
    Cell("N4", "n4trace", "access", "access", ("pfifo", "fq_codel"), reps=(1, 2, 3, 4, 5)),
    Cell("N5", "n5churn", "large", "large", ("pfifo", "fq_codel"), reps=(1, 2, 3, 4, 5)),
]
HELD_OUT_SEED_BASE = 100    # (T) held-out seeds 101..105, never the development seeds 1, 2


def smoke_cells() -> list[Cell]:
    cells = [Cell("SMOKE", "calm", k if k != "base" else "s030u070", k, ("pfifo",), reps=(1,))
             for k in ("base", "split4", "tree16", "uneven", "access", "rev")]
    return cells + [Cell("SMOKE", "sburst", "s030u070", "base", ("pfifo",), reps=(1,))]


def run_name(c: Cell, aqm: str, rep: int) -> str:
    return f"v3-{c.block}-{c.rtype}-{c.variant}-{aqm}-r{rep}"


def git_commit() -> str:
    out = subprocess.run(["git", "-C", str(ROOT), "describe", "--always", "--dirty"], capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


@dataclass
class Planned:
    name: str
    cell: Cell
    aqm: str
    rep: int
    duration: float
    scenario: Path
    topology: Path
    violations: list[str]


def topo_of(c: Cell, rep: int, s_override: dict | None = None) -> Topo:
    opts = dict(c.build_opts)
    s = (s_override or {}).get(c.kind, c.s)
    return build(c.kind, c.variant, s=s, U=c.U, rep=rep, **opts)


def plan_run(c: Cell, aqm: str, rep: int, gen: Path, smoke: bool = False, s_override: dict | None = None,
             seed_base: int = 0) -> Planned:
    seed = seed_base + rep
    t = topo_of(c, seed, s_override)
    events, windows, duration = plan_type(c.rtype, t, seed, smoke=smoke, stim=c.stim)
    events = background(t, c.bg_mode, seed, duration) + events
    if c.rtype == "nloss":   # live loss edits need netem loss on those directions from t = 0
        for cond in t.links:
            if cond["to"] in t.rates and cond["from"] == t.uplink[cond["to"]]:
                cond["forward"]["loss_pct"] = 0
    data = {"duration_s": duration,
            "link_defaults": {"forward": {"bandwidth_mbps": 100}, "reverse": {"bandwidth_mbps": 100}},
            "links": t.links, "routers": aqm_routers(t, aqm, c.pfifo_ms), "events": events}
    name = run_name(c, aqm, rep)
    gen.mkdir(parents=True, exist_ok=True)
    scen, topo = gen / f"{name}.yaml", gen / f"{name}-topology.yaml"
    scen.write_text(yaml.safe_dump(data, sort_keys=False))
    topo.write_text(yaml.safe_dump(t.topo, sort_keys=False))
    (gen / f"{name}-windows.json").write_text(json.dumps(windows, indent=1))
    violations = constraint_check(t)
    meta = {"campaign": "v3", "block": c.block, "type": c.rtype, "variant": c.variant, "topology": c.kind,
            "aqm": aqm, "rep": rep, "seed": seed, "video_seed": seed, "duration_s": duration,
            "s": t.s, "U": t.U, "bg_mode": c.bg_mode if t.s is not None else "none", "rtt_set": c.rtt,
            "pfifo_limit_ms": c.pfifo_ms, "stimulus": c.stim, "phase": c.build_opts.get("phases", "sync"),
            "egress": {e.name: {"hop": f"{e.hop[0]}->{e.hop[1]}", "C_e_mbps": e.cap, "BG_e_mbps": e.bg,
                                "D_e_mbps": e.demand, "clients": e.clients, "shaped": e.shaped,
                                "keyframe_peak_ref_ms": round(121 * t.s * t.U, 1) if t.s else None}
                       for e in t.egress.values()},
            "access_delay_ms": t.delays, "asv": {"key_spread_ms": ASV_KEY_MS, "p_spread_ms": ASV_P_MS},
            "constraint_violations": violations, "git": git_commit(),
            "phases_ms": {sid: sub.get("phase_ms", 0) for sid, sub in t.topo["subscribers"].items()}}
    (gen / f"{name}-plan.json").write_text(json.dumps(meta, indent=1))
    return Planned(name, c, aqm, rep, duration, scen, topo, violations)


def validate(p: Planned) -> None:
    from quiclab.config.scenario import load_scenario
    from quiclab.config.schema import load_topology
    load_scenario(p.scenario, load_topology(p.topology))


def plan_all(gen: Path, cells: list[Cell], smoke: bool = False, s_override: dict | None = None,
             seed_base: int = 0) -> list[Planned]:
    """Rep-major order inside the given cell list (all rep 1, then all rep 2)."""
    reps = sorted({r for c in cells for r in c.reps})
    out = []
    for rep in reps:
        for c in cells:
            if rep in c.reps:
                for aqm in c.aqms:
                    out.append(plan_run(c, aqm, rep, gen, smoke, s_override, seed_base))
    return out


def check_violations(plans: list[Planned]) -> list[str]:
    """Constraint violations not in SPEC_LISTED_VIOLATIONS (those fail the planner)."""
    bad = []
    for p in plans:
        if p.violations and p.cell.variant not in SPEC_LISTED_VIOLATIONS:
            bad.append(f"{p.name}: " + "; ".join(p.violations))
    return bad


def budget(core: list[Planned], micro: list[Planned], gate: list[Planned]) -> tuple[list[Planned], list[str]]:
    """Drop microbenchmark blocks from the bottom until gate + core + micro <= BUDGET_H."""
    order = [c.block for c in MICRO]
    blocks = list(dict.fromkeys(order))
    dropped = []
    keep = list(micro)
    total = lambda ps: sum(p.duration for p in ps) / 3600   # noqa: E731
    while total(gate) + total(core) + total(keep) > BUDGET_H and blocks:
        b = blocks.pop()
        dropped.append(b)
        keep = [p for p in keep if p.cell.block != b]
    return keep, dropped


# ---------------------------------------------------------------- host settings

def cpu_governor() -> dict:
    govs = sorted({p.read_text().strip() for p in Path("/sys/devices/system/cpu").glob("cpu*/cpufreq/scaling_governor")})
    out = {"governors": govs or ["unavailable (no cpufreq in this host / VM)"], "set_performance": False}
    if govs and govs != ["performance"]:
        out["note"] = "not set by the suite (needs root: sudo cpupower frequency-set -g performance)"
    return out


# ---------------------------------------------------------------- running

def run_one(p: Planned, kdir: Path) -> bool:
    import gt1
    import gt2
    import gt3
    import det_eval
    import keyframe_spread
    from quiclab.runtime import remove_partial_run, run_finished
    run_dir = kdir / p.name
    if run_finished(run_dir):
        return True
    remove_partial_run(run_dir)
    print(f"== {p.name} ({p.duration:.0f} s)", flush=True)
    env = {**__import__("os").environ, "QUICLAB_GTQ_LOGGING": "1"}
    status = subprocess.run([sys.executable, "-m", "quiclab", "--runs-dir", str(kdir), "run", "-c", str(p.topology),
                             "-s", str(p.scenario), "--run-id", p.name], cwd=ROOT, env=env)
    if status.returncode != 0:
        print(f"!! {p.name} failed ({status.returncode})", flush=True)
        return False
    (run_dir / "grouping").mkdir(exist_ok=True)
    for suffix, dst in (("-windows.json", "windows.json"), ("-plan.json", "plan.json")):
        shutil.copy(kdir / "_gen" / f"{p.name}{suffix}", run_dir / "grouping" / dst)
    shutil.copy(kdir / "_gen" / f"{p.name}-plan.json", run_dir / "v3-plan.json")
    try:
        det_eval.score(run_dir)
    except (Exception, SystemExit) as e:  # noqa: BLE001
        print(f"   det_eval.score failed: {e!r}", flush=True)
    for mod in (gt1, gt2, gt3):
        try:
            mod.score(run_dir, mod.Params())
        except Exception as e:  # noqa: BLE001
            print(f"   {mod.__name__}.score failed: {e!r}", flush=True)
    try:
        print("   " + keyframe_spread.line(keyframe_spread.write(run_dir)), flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"   keyframe spread failed: {e!r}", flush=True)
    try:   # load parts per stimulus window: nominal u, non-video, video, total, video / calm
        import v3_stimuli
        v3_stimuli.write(run_dir)
    except Exception as e:  # noqa: BLE001
        print(f"   stimulus loads failed: {e!r}", flush=True)
    try:   # per-client pacing and emission times (not gating; the rep report shows them)
        import v3_emission
        print("   " + v3_emission.line(v3_emission.write(run_dir)), flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"   emission failed: {e!r}", flush=True)
    try:
        import v3_gate
        res = v3_gate.run_checks(run_dir)
        print("   " + v3_gate.line(res), flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"   v3 checks failed: {e!r}", flush=True)
        traceback.print_exc()
    return True


def manifest_update(kdir: Path, **kv) -> dict:
    path = kdir / "manifest.yaml"
    m = yaml.safe_load(path.read_text()) if path.exists() else {"runs": {}}
    for k, v in kv.items():
        if k == "runs":
            m.setdefault("runs", {}).update(v)
        else:
            m[k] = v
    path.write_text(yaml.safe_dump(m, sort_keys=False))
    return m


def run_campaign(kdir: Path, gate: list[Planned], core: list[Planned], micro: list[Planned]) -> int:
    import v3_gate
    manifest_update(kdir, started=manifest_update(kdir).get("started") or datetime.datetime.now().isoformat(
        timespec="seconds"), git=git_commit(), host=cpu_governor())
    report = kdir / "gate-report.md"
    passed = report.exists() and report.read_text().startswith("# Gate: PASS")
    if not passed:
        for p in gate:
            ok = run_one(p, kdir)
            manifest_update(kdir, runs={p.name: "done" if ok else "failed"})
        verdict, text = v3_gate.gate_report([kdir / p.name for p in gate])
        report.write_text(text)
        print(f"gate: {'PASS' if verdict else 'FAIL'} -> {report}", flush=True)
        if not verdict:
            manifest_update(kdir, stopped="gate failed")
            return 3
    for p in core + micro:
        ok = run_one(p, kdir)
        manifest_update(kdir, runs={p.name: "done" if ok else "failed"})
    manifest_update(kdir, finished=datetime.datetime.now().isoformat(timespec="seconds"))
    try:
        v3_gate.campaign_summary(kdir)
    except Exception as e:  # noqa: BLE001
        print(f"campaign summary failed: {e!r}", flush=True)
    return 0


SMOKE1_BASELINE = ROOT / "reports" / "v3-suite" / "smoke1" / "baseline.json"


def smoke_tracer_compare(kdir: Path) -> str:
    """Per topology: unmatched packets and recursion_misses in smoke 1 (classic tracepoints,
    reports/v3-suite/smoke1/baseline.json) next to this smoke (raw tracepoints, 2026-11-14)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("smoke1_baseline", SMOKE1_BASELINE.with_name("baseline.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    after = mod.summary(kdir)
    before = json.loads(SMOKE1_BASELINE.read_text()) if SMOKE1_BASELINE.exists() else {}
    f = lambda d, k: "-" if not d else d.get(k)   # noqa: E731
    L = ["", "## Tracer: smoke 1 (classic tracepoints) -> this smoke (raw tracepoints)", "",
         "Unmatched dequeues / enqueues over all traced egresses and over the bottleneck targets; "
         "recursion_misses per tracer (every tracer sees the same nested events); check 4 (third rules).", "",
         "| topology | tracers | unmatched deq / enq, all | unmatched deq / enq, targets | recursion_misses per tracer | "
         "check 4 | failing targets (now) |", "|---|---|---|---|---|---|---|"]
    for topo in sorted(set(before) | set(after)):
        b, a = before.get(topo, {}), after.get(topo, {})
        L.append(f"| {topo} | {f(b, 'tracers')} -> {f(a, 'tracers')} | "
                 f"{f(b, 'unmatched_deq_all')} / {f(b, 'unmatched_enq_all')} -> {f(a, 'unmatched_deq_all')} / "
                 f"{f(a, 'unmatched_enq_all')} | {f(b, 'unmatched_deq_targets')} / {f(b, 'unmatched_enq_targets')} -> "
                 f"{f(a, 'unmatched_deq_targets')} / {f(a, 'unmatched_enq_targets')} | "
                 f"{f(b, 'recursion_misses_per_tracer')} -> {f(a, 'recursion_misses_per_tracer')} | "
                 f"{'ok' if b.get('check4_ok') else 'FAIL' if b else '-'} -> "
                 f"{'ok' if a.get('check4_ok') else 'FAIL' if a else '-'} | {', '.join(a.get('targets_failing') or []) or '-'} |")
    return "\n".join(L) + "\n"


def smoke_emission(kdir: Path, calm: list[Planned]) -> str:
    """Spec follow-up (2026-11-14): S-JOIN emission times of the 5000 kb/s clients and the
    keyframe departure from the publisher, re-measured on the smoke's CALM runs (pub link
    1000 Mb/s). Not gating; ASV_KEY_MS / ASV_P_MS are updated by hand from this."""
    runs = [kdir / p.name for p in calm if (kdir / p.name / "events.csv").exists()]
    args = []
    for rd in runs:
        subs = yaml.safe_load((rd / "topology.yaml").read_text())["subscribers"]
        five = [sid for sid, sub in subs.items() if sub.get("rate_kbps") == 5000]
        if five:
            args.append(f"{rd}:{','.join(five)}")
    import v3_emission
    out = ["", "## Emission times (re-measured, not gating)", "",
           "Per run and client: median BBR pacing (Mb/s), keyframe and P-frame emission (ms), calm GOPs:", ""]
    out += [f"- {p.name}: {v3_emission.line(v3_emission.load(kdir / p.name))}"
            for p in calm if (kdir / p.name / "events.csv").exists()]
    out += [""]
    for cmd in ([sys.executable, str(ROOT / "scripts" / "v3_asv_spread.py"), *args],
                [sys.executable, str(ROOT / "reports" / "v3-suite" / "publisher" / "keyframe_departure.py"),
                 *map(str, runs)]):
        if len(cmd) > 2:
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
            out += ["```", (r.stdout or r.stderr).strip(), "```", ""]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- plan-only output

def print_plan(gate, core, micro, dropped, unexpected, s_override) -> None:
    def hours(ps):
        return sum(p.duration for p in ps) / 3600

    print("# Suite v3 plan\n")
    print(f"git {git_commit()}; host CPU governor: {cpu_governor()}\n")
    for title, ps in (("Gate", gate), ("Core", core), ("Micro", micro)):
        print(f"## {title}: {len(ps)} runs, {hours(ps):.2f} h emulated\n")
        print("| block | runs | hours |\n|---|---|---|")
        for b in dict.fromkeys(p.cell.block for p in ps):
            bs = [p for p in ps if p.cell.block == b]
            print(f"| {b} | {len(bs)} | {hours(bs):.2f} |")
        print()
    print(f"**Total: {len(gate) + len(core) + len(micro)} runs, {hours(gate) + hours(core) + hours(micro):.2f} h "
          f"emulated** (budget {BUDGET_H} h). Dropped micro blocks: {dropped or 'none'}. "
          f"T-TREE16 s override: {s_override or 'none'}.\n")
    print("## Per-egress sizing (every topology and point)\n")
    print("| topology | variant | s | U | egress | hop | D_e | C_e | BG_e | BG flows | pfifo limit pkts | "
          "keyframe peak ref ms | constraints |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    seen = set()
    for p in gate + core + micro:
        key = (p.cell.kind, p.cell.variant, p.cell.s, json.dumps(p.cell.build_opts, sort_keys=True))
        if key in seen:
            continue
        seen.add(key)
        t = topo_of(p.cell, 1, s_override)
        for e in t.egress.values():
            nflows = max(4, round(e.bg / BG_FLOW_MBPS)) if e.bg else 0
            lim = queue("pfifo", e.cap, p.cell.pfifo_ms, legacy=t.s is None)["queue_limit_packets"]
            print(f"| {t.kind} | {p.cell.variant} | {t.s if t.s is not None else 'legacy'} | {t.U} | {e.name} | "
                  f"{e.hop[0]}->{e.hop[1]} | {e.demand:.3f} | {e.cap:g}{'' if e.shaped else ' (unshaped)'} | "
                  f"{e.bg:g} | {nflows} | {lim if e.shaped else '-'} | "
                  f"{round(121 * t.s * t.U, 1) if t.s and e.shaped else '-'} | "
                  f"{'; '.join(constraint_check(t)) or 'ok'} |")
    print("\n## Constraint flags\n")
    for v, why in SPEC_LISTED_VIOLATIONS.items():
        print(f"- kept (listed by the spec; user decision 2026-11-14): {v}: {why}")
    for u in unexpected:
        print(f"- VIOLATION (not listed): {u}")
    print("\n## Runs\n")
    print("| # | run | duration s |\n|---|---|---|")
    for i, p in enumerate(gate + core + micro, 1):
        print(f"| {i} | {p.name} | {p.duration:.0f} |")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--run", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="the smoke plan (spec 8.8) instead of the campaign")
    ap.add_argument("--held-out", action="store_true", help="N1-N5 on v3 instead of the campaign")
    ap.add_argument("--campaign", type=Path, help="campaign folder (resume); default a new .runs/<ts>_v3")
    ap.add_argument("--tree16-s", type=float, default=None,
                    help=f"s for T-TREE16 only (fallback {TREE16_FALLBACK_S} if it fails health at 0.30)")
    a = ap.parse_args(argv)
    s_override = {"tree16": a.tree16_s} if a.tree16_s else None
    tag = "v3-heldout" if a.held_out else "v3-smoke" if a.smoke else "v3"
    kdir = a.campaign or RUNS / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_{tag}"
    gen = kdir / "_gen"
    if a.smoke:
        plans = plan_all(gen, smoke_cells(), smoke=True, s_override=s_override)
        for p in plans:
            validate(p)
        if a.plan_only:
            return 0
        import v3_gate
        for p in plans:
            run_one(p, kdir)
        verdict, text = v3_gate.gate_report([kdir / p.name for p in plans], smoke=True)
        (kdir / "smoke-report.md").write_text(text + smoke_tracer_compare(kdir)
                                              + smoke_emission(kdir, [p for p in plans if p.cell.rtype == "calm"]))
        print(f"smoke: {'PASS' if verdict else 'FAIL'} -> {kdir / 'smoke-report.md'}")
        return 0 if verdict else 3
    if a.held_out:
        plans = plan_all(gen, HELD_OUT, s_override=s_override, seed_base=HELD_OUT_SEED_BASE)
        for p in plans:
            validate(p)
        print(f"held-out v3: {len(plans)} runs, {sum(p.duration for p in plans) / 3600:.2f} h, written to {gen}")
        if a.run:
            for p in plans:
                run_one(p, kdir)
        return 0
    gate = plan_all(gen, GATE, s_override=s_override)
    core = plan_all(gen, CORE, s_override=s_override)
    micro_all = plan_all(gen, MICRO, s_override=s_override)
    micro, dropped = budget(core, micro_all, gate)
    for p in gate + core + micro:
        validate(p)
    unexpected = check_violations(gate + core + micro)
    if a.plan_only:
        print_plan(gate, core, micro, dropped, unexpected, s_override)
        return 2 if unexpected else 0
    if unexpected:
        print("constraint violations not listed by the spec:\n" + "\n".join(unexpected))
        return 2
    kdir.mkdir(parents=True, exist_ok=True)
    manifest_update(kdir, dropped_micro=dropped, tree16_s=a.tree16_s or S_DEFAULT,
                    planned_hours=round(sum(p.duration for p in gate + core + micro) / 3600, 2))
    return run_campaign(kdir, gate, core, micro)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
