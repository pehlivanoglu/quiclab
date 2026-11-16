#!/usr/bin/env python3
"""Scenario and Topology Suite v4 (spec: reports/v4-suite/spec.md): planner and campaign runner.

    .venv/bin/python3 scripts/v4_suite.py --set K1 --plan-only --nmax 40     # plan, budget, per-egress table
    .venv/bin/python3 scripts/v4_suite.py --set K1 --run --nmax <n_max>      # gate, then the campaign (new folder)
    .venv/bin/python3 scripts/v4_suite.py --set K2 --run --campaign .runs/<dir>   # resume
    .venv/bin/python3 scripts/v4_suite.py --smoke --run                      # smoke (spec 7.2), incl. the n_max search
    .venv/bin/python3 scripts/v4_suite.py --held-out --plan-only             # N1-N5 at DEF (prepared, never run here)

Builds on scripts/v3_suite.py (imported, unchanged): sizing, background, AQM settings,
stimuli, the v3 scenario types, the run hooks and the gate checks are v3's. What is new
lives here: the operating points, the new topologies (T-SPLIT4L, T-UNEVENL, T-PARk,
T-LEAFn, T-LEAF16W, T-SPLITn, T-HAYES, T-TEACUP, SB), BG-ONOFF, the stimuli persist /
shorttcp / pause / cold, the new scenario types and the three campaigns. Constants are
tagged (S) spec value, (M) measured, (T) chosen by me, (FLAG) needs your decision.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import v3_suite as v3  # noqa: E402
from v3_suite import (D3, GAP_S, TAIL_S, U3, WARMUP_S, Builder, Egress, Topo, wire)  # noqa: E402

# ---------------------------------------------------------------- constants

POINTS = {"DEF": (0.30, 0.50), "EXT": (0.30, 0.70), "HS50": (0.50, 0.50), "HS70": (0.50, 0.70)}   # (S) table 1
LOW = (500, 1000, 1000, 2500)                       # (S) low rendition set
LEAF_KBPS = 500                                     # (S) T-LEAFn / T-SPLITn client
LEAF_NS = (4, 8, 16, 24)                            # (S) G1 group sizes, plus n_max
NMAX_CANDIDATES = (24, 32, 40)                      # (S) section 2.4
LEAF16W_MS = tuple(5.0 + 6.0 * i for i in range(16))   # (S) 5 .. 95 ms one way, evenly spaced
HAYES_S, HAYES_U = 0.20, 0.50                       # (S, FLAG) 80 % background (theirs > 90 %)
TEACUP_S, TEACUP_U, TEACUP_UP_RATIO = 0.30, 0.80, 2.5   # (S, FLAG) calm 0.80 on the access links
TEACUP_ACCESS_MS = 45.0                             # (S) feed 5 + 45 = 50 ms one way -> base RTT 100 ms
TEACUP_REV_MBPS, TEACUP_REV_LOAD = 10.0, 0.90       # (S) ACK path of up, loaded with UDP
LAG_NEAR_MS, LAG_FAR_MS = 10.0, (50.0, 210.0)       # (S) FB-LAG access delays
PERSIST_S = 30.0                                    # (S) FB-* episode
FB_CALM_S = 30.0                                    # (S) calm between FB episodes
FB_LEVELS = (1.0, 1.1, 1.2, 1.5, 2.0, 2.5)          # (S) FB-LOAD
CROSS_S = {"x20": 0.80, "x40": 0.60, "x60": 0.40, "x80": 0.20}   # (S) FB-CROSS: cross-traffic ratio -> s
COLD_S, COLD_JOIN_S, COLD_D = 45.0, 3.0, 30.0       # (S) run, client starts; (T) the surge lasts 30 s
COLD_JOIN_MIN_S = 0.05                              # (T) a join at exactly 0 would be the initial launch
SALVO_N, SALVO_MEAN_B, SALVO_SHAPE, SALVO_SPREAD_S = 10, 500e3, 1.5, 2.0   # (S) shorttcp: our overload stimulus
RFC_FLOWS, RFC_ON, RFC_BYTES, RFC_IDLE_S, RFC_RUN_S = 10, 2, (30e3, 50e3), 10.0, 300.0
#   (S) S-SHORT-RFC (decision 2026-11-15): RFC 8867 section 5.7 / RFC 8868 section 5.1 short TCP flows: 10 flows
#   (2 start ON, 8 OFF), files uniform 30-50 kB, idle exponential mean 10 s, the whole 300 s run
SALVO_TAIL_S = 10.0                                 # (T) a salvo process lives d + this (late flows are cut)
SALVO_CC = "cubic"                                  # (S)
PAUSE_D = (5.0, 20.0)                               # (S)
ONOFF_MEAN_S, ONOFF_FLOW_MBPS = 1.0, 2.5            # (S) BG-ONOFF
SHIFT_PHASE_S, SHIFT_D, SHIFT_FIRST_S = 60.0, 5.0, 2.0   # (S) phases, surge d; (T) first surge 2 s into a phase
SHIFT_ORDER = ("a", "up", "b", "a+b", "up", "a", "b", "up", "a+b", "up")   # (S)
SHIFT_SUSTAINED = (10.0, 40.0)                      # (T) persist from 10 s into the phase for 40 s (S: 40 s)
CHURN_S = 900.0                                     # (S)
CONC_N, CONC_F = 40, (0.0, 0.25, 0.5, 1.0)          # (S) H-CONC
MILD_LEVELS = (1.05, 1.10, 1.15)                    # (S) S-MILD
DCLEAN_BG_AT, DCLEAN_PLAN_AT = 60.0, 90.0           # (S)
JITTER_LEVELS = (2.0, 5.0, 10.0)                    # (S) T2
REV_ASYM_MS = (5.0, 40.0, 80.0, 120.0)              # (S) old `revasym` reverse access delays (grouping_campaign)
SMOKE_CALM_S, SMOKE_EVENT_S = 60.0, 90.0            # (S) spec 7.2
SPEC_HOURS = {"K1": 23.7, "K2": 23.9, "K3": 21.1}   # (S) section 6 budget
LISTED_VIOLATIONS = {"bw4x12": v3.SPEC_LISTED_VIOLATIONS["bw4x12"]}   # M11 keeps its own s / U (spec 6, K3 M)

BUILDER_KEYS = ("fps", "ip_ratio", "cc", "delays", "delay_scale", "phases", "jitter")
RUNS = v3.RUNS


# ---------------------------------------------------------------- topologies

@dataclass
class Egress4(Egress):
    s: float | None = None        # this egress's target point (T-TEACUP up differs from the run's)
    U: float | None = None


def _point_of(e: Egress, t: Topo) -> tuple[float | None, float]:
    s = getattr(e, "s", None)
    U = getattr(e, "U", None)
    return (t.s if s is None else s), (t.U if U is None else U)


class _New:
    """Sizing helper for the new topologies (as v3.build's add, with a per-egress point)."""

    def __init__(self, seed: int, s: float, U: float, opts: dict):
        self.b = Builder(seed=seed, **{k: opts[k] for k in BUILDER_KEYS if k in opts})
        self.s, self.U = s, U
        self.rates: dict[str, int] = {}
        self.egress: dict[str, Egress4] = {}

    def add(self, name: str, a: str, bnode: str, clients: list[str], shaped: bool = True,
            point: tuple[float, float] | None = None, cap: float | None = None) -> None:
        d = round(sum(wire(self.rates[c]) for c in clients), 4)
        if not shaped:
            self.egress[name] = Egress4(name, (a, bnode), clients, d, v3.SRC_SINK_MBPS, 0.0, False)
            self.b.bottleneck(a, bnode, None, name, 0)
            return
        ss, uu = point or (self.s, self.U)
        c, g = v3._size(d, ss, uu)
        if cap is not None:   # fixed capacity (T-TEACUP up): background by the v3 rule, load follows
            c = round(cap, 2)
            uu = round((d + g) / c, 4)
        self.egress[name] = Egress4(name, (a, bnode), clients, d, c, g, True, ss, uu)
        self.b.bottleneck(a, bnode, c, name, g)

    def leaf_clients(self, up: str, rates: dict[str, int], delays: tuple[float, ...] | None = None) -> None:
        self.rates.update(rates)
        if delays is not None:
            keep = self.b.delays
            self.b.delays = delays
            self.b.clients(up, rates)
            self.b.delays = keep
        else:
            self.b.clients(up, rates)

    def topo(self, kind: str, variant: str, leaf_of: dict, uplink: dict, rev=None) -> Topo:
        return Topo(kind, variant, self.s, self.U, dict(self.rates), uplink, leaf_of, self.egress,
                    self.b.topology(), self.b.cond, self.b.routers, {}, rev, self.b.client_delay)


def _low(prefix: str, n_sets: int = 1) -> dict[str, int]:
    return {f"{prefix}{i + 1}": r for i, r in enumerate(LOW * n_sets)}


def build4(kind: str, variant: str, s: float | None, U: float, seed: int, opts: dict) -> Topo:
    """A v4 topology at (s, U). v3 kinds (base, access, rev, split4, tree16, uneven) are
    built by v3.build unchanged; opts may add fwd_jitter_ms (T2) and rev_asym (R-REVASYM)."""
    opts = dict(opts)
    fwd_jitter = opts.pop("fwd_jitter_ms", None)
    rev_asym = opts.pop("rev_asym", False)
    if kind in ("base", "access", "rev", "split4", "tree16", "uneven", "large"):
        t = v3.build(kind, variant, s=s, U=U, rep=seed, **opts)
        t.egress = {n: Egress4(**vars(e), s=t.s, U=t.U) for n, e in t.egress.items()}
    else:
        t = _build_new(kind, variant, s, U, seed, opts)
    for c in t.links:
        if c["to"] in t.rates and c["from"] == t.uplink[c["to"]]:
            if fwd_jitter:
                c.setdefault("forward", {}).update(jitter_ms=fwd_jitter, jitter_distribution="normal",
                                                   jitter_keep_order=True)
            if rev_asym:
                i = sorted(t.rates).index(c["to"])
                c.setdefault("reverse", {})["delay_ms"] = REV_ASYM_MS[i % len(REV_ASYM_MS)]
    return t


def _build_new(kind: str, variant: str, s: float, U: float, seed: int, opts: dict) -> Topo:
    if kind == "hayes":
        s, U = HAYES_S, HAYES_U
    n = _New(seed, s, U, opts)
    b = n.b
    if kind in ("split4l", "teacup"):
        teacup = kind == "teacup"
        if teacup:
            b.delays = (TEACUP_ACCESS_MS,)
        b.router("r1", "r2")
        b.switch("switch-a", "switch-b")
        b.feed("r1")
        for x in "ab":
            n.rates.update(_low(x))
        leaf_pt = (TEACUP_S, TEACUP_U) if teacup else None
        if teacup:
            c_leaf = v3._size(round(sum(wire(n.rates[c]) for c in _low("a")), 4), TEACUP_S, TEACUP_U)[0]
            n.add("up", "r1", "r2", list(n.rates), point=(TEACUP_S, TEACUP_U), cap=TEACUP_UP_RATIO * c_leaf)
        else:
            n.add("up", "r1", "r2", list(n.rates), shaped=not opts.get("noroot"))
        for x in "ab":
            n.add(x, "r2", f"switch-{x}", list(_low(x)), point=leaf_pt)
            n.leaf_clients(f"switch-{x}", _low(x))
        rev = None
        if teacup and variant.endswith("rev"):
            for c in b.cond:
                if (c["from"], c["to"]) == ("r1", "r2"):
                    c["reverse"] = {"bandwidth_mbps": TEACUP_REV_MBPS}
            b.endpoints("rshared", ["tx-rev", "r2", "r1", "rx-rev"])
            rev = ("r2", "r1")
        t = n.topo(kind, variant, {c: c[0] for c in n.rates}, {c: f"switch-{c[0]}" for c in n.rates}, rev)
        if teacup:
            t.s, t.U = TEACUP_S, TEACUP_U
        return t
    if kind == "unevenl":
        groups = {"a": (1000, 2500), "b": (500, 500, 1000, 1000, 2500),
                  "c": (500, 500, 500, 500, 1000, 1000, 1000, 2500, 2500)}
        b.router("r1", "r2")
        b.switch(*(f"switch-{x}" for x in groups))
        b.feed("r1")
        for x, rs in groups.items():
            n.rates.update({f"{x}{i + 1}": r for i, r in enumerate(rs)})
        n.add("up", "r1", "r2", list(n.rates), shaped=False)
        for x in groups:
            leaf = {c: r for c, r in n.rates.items() if c[0] == x}
            n.add(x.upper(), "r2", f"switch-{x}", list(leaf))
            n.leaf_clients(f"switch-{x}", leaf)
        return n.topo(kind, variant, {c: c[0].upper() for c in n.rates}, {c: f"switch-{c[0]}" for c in n.rates})
    if kind in ("par", "splitn"):
        k = opts.get("k", 2)
        letters = "abcdefgh"[:k]
        per = opts.get("per", 4)
        b.router("r1", "r2")
        b.switch(*(f"switch-{x}" for x in letters))
        b.feed("r1")
        for x in letters:
            if kind == "splitn":
                n.rates.update({f"{x}{i + 1}": LEAF_KBPS for i in range(opts["n"])})
            else:
                n.rates.update(_low(x, per // 4))
        n.add("up", "r1", "r2", list(n.rates), shaped=kind == "splitn")
        for x in letters:
            leaf = {c: r for c, r in n.rates.items() if c[0] == x}
            n.add(x, "r2", f"switch-{x}", list(leaf))
            delays = None
            if opts.get("lag"):
                rng = random.Random(f"v4-lag-{seed}-{x}")
                delays = (LAG_NEAR_MS, LAG_NEAR_MS, round(rng.uniform(*LAG_FAR_MS), 1),
                          round(rng.uniform(*LAG_FAR_MS), 1))
            n.leaf_clients(f"switch-{x}", leaf, delays)
        return n.topo(kind, variant, {c: c[0] for c in n.rates}, {c: f"switch-{c[0]}" for c in n.rates})
    if kind == "hayes":
        return _build_hayes(n)
    raise ValueError(kind)


HAYES_STAGES = (("L12", "L34"), ("L13", "L24"), ("L14", "L23"))      # (S) Hayes et al., LCN 2014, Fig. 4
HAYES_GROUPS = {"g1": 1000, "g2": 1000, "g3": 500, "g4": 500}       # (S) kb/s per client, two clients each


def hayes_links(group: str) -> list[str]:
    """The four links group gk crosses: the stage link whose name holds k, then L1234."""
    k = group[1]
    return [next(name for name in stage if k in name[1:]) for stage in HAYES_STAGES] + ["L1234"]


def _build_hayes(n: _New) -> Topo:
    b = n.b
    b.router("r0", "r1", "r2", "r3", "r4", *(name.lower() for stage in HAYES_STAGES for name in stage))
    b.switch(*(f"switch-{g}" for g in HAYES_GROUPS))
    b.feed("r0")
    for g, kbps in HAYES_GROUPS.items():
        n.rates.update({f"{g}{x}": kbps for x in "ab"})
    members = {g: [c for c in n.rates if c.startswith(g)] for g in HAYES_GROUPS}
    for i, stage in enumerate(HAYES_STAGES):
        for name in stage:
            groups = [g for g in HAYES_GROUPS if name in hayes_links(g)]
            clients = [c for g in groups for c in members[g]]
            node = name.lower()
            n.add(name, f"r{i}", node, clients)
            n.add(f"{name}-out", node, f"r{i + 1}", clients, shaped=False)
    n.add("L1234", "r3", "r4", list(n.rates))
    for g in HAYES_GROUPS:
        b.link("r4", f"switch-{g}")
        n.leaf_clients(f"switch-{g}", {c: n.rates[c] for c in members[g]})
    for g in HAYES_GROUPS:
        nodes = ["pub", "r0"]
        for i, name in enumerate(hayes_links(g)[:3]):
            nodes += [name.lower(), f"r{i + 1}"]
        nodes += ["r4", f"switch-{g}"]
        for c in members[g]:
            b.subs[c]["path"] = nodes + [c]
    t = n.topo("hayes", "", {c: c[:2] for c in n.rates}, {c: f"switch-{c[:2]}" for c in n.rates})
    return t


def constraint_check4(t: Topo, literature: bool) -> list[str]:
    """Spec 1: shaped links <= 100 Mb/s; an instrumented flow <= 15 % of each bottleneck
    it crosses (25 % at s >= 0.50 and in the literature blocks); total <= 300 Mb/s."""
    out = []
    for e in t.bottlenecks():
        s_e, _ = _point_of(e, t)
        limit = v3.MAX_FLOW_SHARE_WIDE if (literature or (s_e or 0) >= 0.50) else v3.MAX_FLOW_SHARE
        if e.cap > v3.MAX_LINK_MBPS:
            out.append(f"{e.name} {e.cap:g} Mb/s > {v3.MAX_LINK_MBPS:g}")
        for c in e.clients:
            share = wire(t.rates[c]) / e.cap
            if share > limit + 1e-9:
                out.append(f"{c} {wire(t.rates[c]):.2f} Mb/s = {share:.1%} of {e.name} {e.cap:g} Mb/s (> {limit:.0%})")
    total = sum(e.demand + e.bg for e in t.bottlenecks()) + sum(wire(t.rates[c]) for c in t.access)
    if t.rev is not None and t.kind == "teacup":
        total += TEACUP_REV_LOAD * TEACUP_REV_MBPS
    if total > v3.MAX_TOTAL_MBPS:
        out.append(f"total through router egresses {total:.1f} Mb/s > {v3.MAX_TOTAL_MBPS:g}")
    return out


# ---------------------------------------------------------------- background (v3 modes + BG-ONOFF)

def background4(t: Topo, mode: str, seed: int, duration: float) -> list[dict]:
    if mode != "onoff":
        return v3.background(t, mode, seed, duration)
    events = []
    for i, e in enumerate(t.bottlenecks()):
        if e.bg <= 0:
            continue
        n = max(4, round(e.bg / ONOFF_FLOW_MBPS))
        mean = e.bg / n
        for k in range(n):
            rng = random.Random(f"v4-onoff-{seed}-{e.name}-{k}")
            periods, tt, on = [], 0.0, rng.random() < 0.5
            while tt < duration:
                span = rng.expovariate(1 / ONOFF_MEAN_S)
                if on:
                    a, d = round(tt, 4), round(min(span, duration - tt), 4)
                    if d > 1e-3:
                        periods.append([a, d])
                tt += span
                on = not on
            if not periods:
                continue
            # on rate scaled to the realised on-time, so each source's mean is exactly BG_e / n
            # (decision 2026-11-16; the nominal on rate is 2 x mean at a 50 % on-time)
            on_time = sum(d for _, d in periods)
            events.append({"at_s": 0, "type": "bg", "id": f"bg-{e.name}-n{k}", "route": e.route,
                           "duration_s": duration, "rate_mbps": round(mean * duration / on_time / v3.UDP_WIRE, 4),
                           "process": "poisson", "flow_weights": [1.0], "seed": seed * 1000 + i * 50 + k,
                           "periods": periods})
    return events


# ---------------------------------------------------------------- stimuli

class Stim4(v3.Stim):
    """v3's event factory with the egress's own point and the new stimuli."""

    def surge(self, tgt: str, at: float, u: float, d: float, cell: str, ramp: bool = False,
              kind: str | None = None, **extra) -> None:
        e = self.t.egress[tgt]
        _, U_e = _point_of(e, self.t)
        add = (u - U_e) * e.cap
        name = kind or ("ramp" if ramp else "surge")
        ev = {"at_s": round(at, 3), "type": "bursts", "id": self._id(name, tgt),
              "route": e.route, "process": "poisson", "flow_weights": v3.surge_weights(add),
              "seed": self.rep * 100000 + self.n,
              "bursts": [{"start_s": 0, "duration_s": d, "rate_mbps": round(add / v3.UDP_WIRE, 4)}],
              "label": f"{name} u={u} d={d} {tgt}"}
        if ramp:
            ev.update(ramp_up_s=v3.RAMP_UP_S, ramp_step_s=v3.RAMP_STEP_S)
        self.events.append(ev)
        self.windows.append(v3._window(at, at + d, name, tgt, cell, e.clients, "ramp" if ramp else "surge",
                                       self._hop(e), u=u, d=d, extra_mbps=round(add, 3), **extra))

    def join(self, tgt: str, at: float, u: float, cell: str) -> float:
        e = self.t.egress[tgt]
        _, U_e = _point_of(e, self.t)
        keep, self.t.U = self.t.U, U_e
        try:
            return super().join(tgt, at, u, cell)
        finally:
            self.t.U = keep

    def capdrop(self, tgt: str, at: float, u: float, d: float, cell: str) -> None:
        if tgt not in self.t.egress:
            return super().capdrop(tgt, at, u, d, cell)
        e = self.t.egress[tgt]
        _, U_e = _point_of(e, self.t)
        a, b, base, low = e.hop[0], e.hop[1], e.cap, round(U_e * e.cap / u, 3)
        self.events += [{"at_s": round(at, 3), "type": "link", "from": a, "to": b, "bandwidth_mbps": low,
                         "label": f"burst u={u} d={d} {tgt}"},
                        {"at_s": round(at + d, 3), "type": "link", "from": a, "to": b, "bandwidth_mbps": base,
                         "label": "burst-end"}]
        self.windows.append(v3._window(at, at + d, "cap", tgt, cell, e.clients, "capdrop", self._hop(e), u=u, d=d))

    def shorttcp(self, tgt: str, at: float, u: float, d: float, cell: str) -> None:
        """Salvos of SALVO_N CUBIC flows (Pareto sizes, mean SALVO_MEAN_B, shape SALVO_SHAPE,
        starts uniform over SALVO_SPREAD_S), repeated until their bytes reach the mean extra
        load (u - U) C_e over d; salvo starts evenly spaced over [0, d - spread]."""
        e = self.t.egress[tgt]
        _, U_e = _point_of(e, self.t)
        add = (u - U_e) * e.cap
        target = add * 1e6 / 8 * d / v3.TCP_WIRE        # goodput bytes over d
        rng = random.Random(f"v4-salvo-{self.rep}-{self.n}")
        xm = SALVO_MEAN_B * (SALVO_SHAPE - 1) / SALVO_SHAPE
        salvos, total = [], 0.0
        while total < target:
            sizes = [max(1, int(xm * rng.paretovariate(SALVO_SHAPE))) for _ in range(SALVO_N)]
            offs = [rng.uniform(0, SALVO_SPREAD_S) for _ in range(SALVO_N)]
            salvos.append(list(zip(offs, sizes)))
            total += sum(sizes)
        span = max(0.0, d - SALVO_SPREAD_S)
        flows = []
        for j, salvo in enumerate(salvos):
            t0 = span * j / max(1, len(salvos) - 1) if len(salvos) > 1 else 0.0
            flows += [{"start_s": round(t0 + off, 4), "bytes": size} for off, size in salvo]
        flows.sort(key=lambda f: f["start_s"])
        self.events.append({"at_s": round(at, 3), "type": "salvo", "id": self._id("salvo", tgt), "route": e.route,
                            "duration_s": d + SALVO_TAIL_S, "flows": flows, "cc": SALVO_CC,
                            "label": f"shorttcp u={u} d={d} {tgt}"})
        self.windows.append(v3._window(at, at + d, "shorttcp", tgt, cell, e.clients, "shorttcp", self._hop(e),
                                       u=u, d=d, extra_mbps=round(add, 3), salvos=len(salvos),
                                       flows=len(flows), planned_bytes=int(total)))

    def pause(self, sid: str, at: float, d: float, cell: str) -> float:
        """The sender stops sending to `sid` from the next GOP boundary for d s; returns the end."""
        at = float(math.ceil(at))
        self.events.append({"at_s": at, "type": "pause", "subscriber": sid, "duration_s": d,
                            "label": f"pause d={d:g} {sid}"})
        self.windows.append(v3._window(at, at + d, "pause", sid, cell, [], "pause", None, d=d))
        return at + d


def _all(t: Topo, leaves: list[str]) -> str:
    return "+".join(leaves)


def leaves_of(t: Topo) -> list[str]:
    """Shaped leaf egresses of a T-PARk / split topology (not up)."""
    return [n for n, e in t.egress.items() if e.shaped and n != "up"]


# ---------------------------------------------------------------- scenario types

V3_TYPES = {"calm", "sburst", "sramp", "stcp", "sjoin", "hhier", "hdepth", "hindep", "huneven", "amixed",
            "llong", "rrev", "nloss", "sstress", "ssparse", "n3cross", "n4trace", "n5churn"}


def plan_type4(rtype: str, t: Topo, seed: int, variant: str = "", stim: str = "surge") -> tuple[list, list, float]:
    """(events, windows, duration) of one v4 scenario type on topology t."""
    if rtype in V3_TYPES:
        return v3.plan_type(rtype, t, seed, stim=stim)
    rng = random.Random(f"v4-{rtype}-{seed}")
    st = Stim4(t, seed)
    grid = [(u, d) for u in U3 for d in D3]

    def on_main(kind=None):
        return lambda s_, t_, c: (s_.surge("main", t_, c[0], c[1], f"u={c[0]} d={c[1]}", kind=kind), c[1])[1]

    def episodes(levels, leaves, kind="persist", d=PERSIST_S):
        tt = WARMUP_S
        for i, lvl in enumerate(levels):
            for x in leaves:
                st.surge(x, tt, lvl, d, f"ep{i + 1} u={lvl}", kind=kind)
            tt += d + FB_CALM_S
        return round(tt - FB_CALM_S + TAIL_S)

    if rtype == "llong2":
        cells = [(u, d, x) for x in ("up", "a", "b") for u in (1.15, 1.3) for d in (10.0, 30.0)] * 2
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, v3.combined)
    elif rtype == "gsize2":
        cells = [(u, d, x) for x in ("up", "a", "b") for u, d in grid]
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, v3.combined)
    elif rtype == "ppar":
        duration = v3.indep(st, leaves_of(t), rng)
    elif rtype == "fbload":
        levels = list(FB_LEVELS) * 2
        rng.shuffle(levels)
        duration = episodes(levels, leaves_of(t))
    elif rtype in ("fbcross", "fblag", "fbscale"):
        duration = episodes([1.1 if rtype == "fbcross" else 1.2] * 8, leaves_of(t))
    elif rtype == "fbcold":
        for x in leaves_of(t):
            st.surge(x, 0.0, 1.2, COLD_D, "cold u=1.2", kind="persist", cold=True)
        for sid in sorted(t.rates):
            st.events.append({"at_s": round(rng.uniform(COLD_JOIN_MIN_S, COLD_JOIN_S), 3), "type": "join",
                              "subscriber": sid})
        duration = COLD_S
    elif rtype == "hycombo":
        links = [n for n, e in t.egress.items() if e.shaped]
        cells = [(u, d, x) for x in links for u in (1.15, 1.3) for d in (5.0, 10.0)]
        rng.shuffle(cells)
        if variant == "cap":
            duration = v3.sequence(st, cells, rng, lambda s_, t_, c: (s_.capdrop(c[2], t_, c[0], c[1], c[2]), c[1])[1])
        else:
            duration = v3.sequence(st, cells, rng, v3.combined)
    elif rtype == "hytb":
        cells = [(u, d, x) for x in ("a", "b", "up") for u in (1.15, 1.3) for d in (5.0, 10.0)] * 2
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, v3.combined)
    elif rtype == "sbnsb":   # identical plan (rng) in SB and NSB; NSB: both leaves at once
        cells = grid * 2
        rng.shuffle(cells)
        tgt = "main" if "main" in t.egress else _all(t, leaves_of(t))
        duration = v3.sequence(st, cells, rng, lambda s_, t_, c: v3.combined(s_, t_, (c[0], c[1], tgt)))
    elif rtype == "hshift":
        for i, tgt in enumerate(SHIFT_ORDER):
            p0 = WARMUP_S + i * SHIFT_PHASE_S
            if variant == "sustained":
                u = rng.choice((1.15, 1.3))
                for part in tgt.split("+"):
                    st.surge(part, p0 + SHIFT_SUSTAINED[0], u, SHIFT_SUSTAINED[1], f"phase{i + 1}:{tgt}", kind="persist")
                continue
            tt = p0 + SHIFT_FIRST_S
            while tt + SHIFT_D <= p0 + SHIFT_PHASE_S:
                u = rng.choice((1.15, 1.3))
                for part in tgt.split("+"):
                    st.surge(part, tt, u, SHIFT_D, f"phase{i + 1}:{tgt}")
                tt += SHIFT_D + rng.uniform(*GAP_S)
        duration = round(WARMUP_S + len(SHIFT_ORDER) * SHIFT_PHASE_S + TAIL_S)
    elif rtype == "spersist":
        cells = [(u, d) for d in (30.0, 60.0, 120.0) for u in (1.1, 1.3)]
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, on_main("persist"), gap=(FB_CALM_S, FB_CALM_S))
    elif rtype == "hchurn":
        duration = v3.indep(st, ["up", "a", "b"], rng, duration=CHURN_S)
        sessions = churn_plan(t)
        for sid, ss in sessions.items():
            for k, (on, off) in enumerate(ss):
                if not (k == 0 and on == 0):
                    st.events.append({"at_s": on, "type": "join", "subscriber": sid})
                if off is not None:
                    st.events.append({"at_s": off, "type": "leave", "subscriber": sid})
        for w in st.windows:
            w["expected"] = sorted(c for c in w["expected"]
                                   if any(a <= w["start"] and (b is None or b >= w["end"]) for a, b in sessions[c]))
    elif rtype == "hconc":
        f = float(variant[1:]) / 100
        cells = [(u, d) for u in (1.15, 1.3) for d in (5.0, 10.0)] * (CONC_N // 4)
        rng.shuffle(cells)
        both = round(f * CONC_N)
        singles = ["a", "b"] * ((CONC_N - both + 1) // 2)
        rng.shuffle(singles)
        tgts = ["a+b"] * both + singles[:CONC_N - both]
        rng.shuffle(tgts)
        duration = v3.sequence(st, [(u, d, x) for (u, d), x in zip(cells, tgts)], rng, v3.combined)
    elif rtype == "hsparse":
        cells = [(u, d, x) for x in ("up", "a", "b") for u in (1.05, 1.15) for d in (5.0, 10.0)]
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, v3.combined, gap=v3.SPARSE_GAP_S)
    elif rtype == "hjoin":
        cells = [(u, x) for x in ("a", "b", "up") for u in (1.05, 1.15)] * 2
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, lambda s_, t_, c: s_.join(c[1], t_, c[0], f"{c[1]} u={c[0]}") - t_)
    elif rtype == "negcalm":
        duration = 600.0
    elif rtype == "negpriv":   # A-MIXED's private capdrops only (twice), the sub-d join kept
        cells = [(1.3, d, c) for c in sorted(t.access) for d in D3] * 2
        rng.shuffle(cells)
        tt, pending = WARMUP_S, list(cells)
        while pending:
            pick = next((c for c in pending if tt > v3.JOIN_T + 10 or c[2] != v3.JOIN_SUB), pending[0])
            if pick[2] == v3.JOIN_SUB and tt <= v3.JOIN_T + 10:
                tt = v3.JOIN_T + 10 + 1e-3
            pending.remove(pick)
            st.capdrop(pick[2], tt, pick[0], pick[1], "private")
            tt += pick[1] + rng.uniform(*GAP_S)
        st.events.append({"at_s": v3.JOIN_T, "type": "join", "subscriber": v3.JOIN_SUB})
        duration = round(tt - GAP_S[0] + TAIL_S)
    elif rtype == "neglossh":
        return v3.plan_type("nloss", t, seed)
    elif rtype == "sshort":
        cells = list(U3) * 3
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, lambda s_, t_, u: (s_.shorttcp("main", t_, u, 10.0, f"u={u}"), 10.0)[1])
    elif rtype == "spause":
        clients = sorted(t.rates)
        who = clients + [rng.choice(clients) for _ in range(6 - len(clients))]
        rng.shuffle(who)
        ds = [PAUSE_D[i % 2] for i in range(6)]
        cells = [("surge", u, d) for u, d in grid * 2] + [("pause", sid, d) for sid, d in zip(who[1:], ds[1:])]
        rng.shuffle(cells)
        during = (who[0], ds[0])   # the one pause during a surge: with the first 10 s surge of the plan

        def make(s_, t_, c):
            nonlocal during
            if c[0] == "pause":
                return s_.pause(c[1], t_, c[2], "pause") - t_
            s_.surge("main", t_, c[1], c[2], f"u={c[1]} d={c[2]}")
            if during and c[2] >= 10.0:
                sid, d = during
                during = None
                at = math.ceil(t_)
                s_.pause(sid, at, min(d, max(1.0, math.floor(t_ + c[2] - at))), "pause-in-surge")
            return c[2]
        duration = v3.sequence(st, cells, rng, make)
    elif rtype == "sdense":
        cells = [(u, 2.0) for u in U3] * 20
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, on_main(), gap=(2.0, 4.0))
    elif rtype == "smild":
        level, duration = float(variant[1:]) / 100, 330.0
        tt = WARMUP_S
        while True:
            d = rng.uniform(10, 20) if rng.random() < 0.15 else rng.uniform(1, 4)
            if tt + d > duration - TAIL_S:
                break
            st.surge("main", tt, level, round(d, 3), f"u={level}")
            tt += d + rng.uniform(5, 20)
    elif rtype == "rrevasym":
        return v3.plan_type("rrev", t, seed)
    elif rtype == "dclean":
        cells = grid * 2
        rng.shuffle(cells)
        duration = v3.sequence(st, cells, rng, on_main(), t0=DCLEAN_PLAN_AT)
    elif rtype == "sshortrfc":   # light bursty TCP, no overload: scored like CALM (no stimulus window)
        duration = RFC_RUN_S
        flows = []
        for k in range(RFC_FLOWS):
            tt = 0.0 if k < RFC_ON else rng.expovariate(1 / RFC_IDLE_S)
            while tt < duration - 1.0:
                flows.append({"start_s": round(tt, 4), "bytes": int(rng.uniform(*RFC_BYTES))})
                # next file after an idle period; a 30-50 kB download lasts milliseconds here (T)
                tt += rng.expovariate(1 / RFC_IDLE_S)
        flows.sort(key=lambda f: f["start_s"])
        st.events.append({"at_s": 0.0, "type": "salvo", "id": "salvo-rfc-main", "route": t.egress["main"].route,
                          "duration_s": duration, "flows": flows, "cc": SALVO_CC,
                          "label": f"shorttcp-rfc flows={RFC_FLOWS} files={len(flows)}"})
    elif rtype == "g-persist":    # gate / smoke runs, 90 s
        st.surge("main", WARMUP_S + 15, 1.3, PERSIST_S, "gate persist", kind="persist")
        duration = SMOKE_EVENT_S
    elif rtype == "g-shorttcp":
        st.shorttcp("main", WARMUP_S + 30, 1.15, 10.0, "gate shorttcp")
        duration = SMOKE_EVENT_S
    elif rtype == "g-pause":
        st.pause(sorted(t.rates)[0], WARMUP_S + 30, PAUSE_D[0], "gate pause")
        duration = SMOKE_EVENT_S
    elif rtype == "g-calm":
        duration = SMOKE_EVENT_S
    elif rtype == "s-calm":
        duration = SMOKE_CALM_S
    else:
        raise ValueError(rtype)
    st.events.sort(key=lambda e: e["at_s"])
    return st.events, v3.flag_concurrent(st.windows), float(duration)


def churn_plan(t: Topo) -> dict[str, list[tuple[float, float | None]]]:
    """H-CHURN (S): per leaf, client 1 present throughout, 2 joins at 120 s, 3 leaves at
    450 s, 4 leaves at 300 s and rejoins at 600 s."""
    out = {}
    for c in sorted(t.rates):
        k = int(c[1:])
        out[c] = {1: [(0.0, None)], 2: [(120.0, None)], 3: [(0.0, 450.0)], 4: [(0.0, 300.0), (600.0, None)]}[k]
    return out


# ---------------------------------------------------------------- campaign matrix

@dataclass
class Cell:
    block: str
    rtype: str
    variant: str
    kind: str
    aqms: tuple[str, ...]
    point: str = "DEF"
    seeds: tuple[int, ...] = (1, 2)
    bg_mode: str = "cbr"
    pfifo_ms: float = v3.PFIFO_MS
    stim: str = "surge"
    opts: dict = field(default_factory=dict)
    s: float | None = None        # explicit point (FB-CROSS, M11); None: POINTS[point]
    U: float | None = None
    literature: bool = False
    note: str = ""

    @property
    def su(self) -> tuple[float, float]:
        s, U = POINTS[self.point]
        return (self.s if self.s is not None else s), (self.U if self.U is not None else U)


def S(n: int) -> tuple[int, ...]:
    return tuple(range(1, n + 1))


AQ6 = ("pfifo", "codel", "pie", "fq_codel", "red", "cake")
PC = ("pfifo", "codel")


def leaf_opts(n: int) -> dict:
    return {"rates": {f"sub-{i + 1:02d}": LEAF_KBPS for i in range(n)}}


def k1(nmax: int) -> list[Cell]:
    ns = list(dict.fromkeys((*LEAF_NS, nmax)))
    return [
        *[Cell("A1", "calm", k, k, PC, seeds=S(3)) for k in ("base", "split4l", "unevenl", "access")],
        Cell("A1", "calm", "par4", "par", PC, seeds=S(3), opts={"k": 4}),
        Cell("A2", "sburst", "def", "base", AQ6, seeds=S(5)),
        *[Cell("A3", r, "def", "base", PC, seeds=S(3)) for r in ("sramp", "stcp", "sjoin")],
        Cell("A4", "hhier", "def", "split4l", ("pfifo", "codel", "pie", "fq_codel"), seeds=S(5)),
        Cell("A5", "hindep", "def", "split4l", ("pfifo", "codel", "fq_codel"), seeds=S(5)),
        Cell("A6", "huneven", "def", "unevenl", PC, seeds=S(5)),
        Cell("A7", "amixed", "def", "access", ("pfifo", "codel", "fq_codel"), seeds=S(5)),
        Cell("A8", "llong2", "def", "split4l", PC, seeds=S(5)),
        Cell("A9", "nloss", "def", "base", ("pfifo",), seeds=S(3)),
        Cell("A9", "rrev", "def", "rev", ("pfifo",), seeds=S(3)),
        *[Cell("G1", "sburst", f"n{n}", "base", PC, point="EXT", seeds=S(3), opts=leaf_opts(n)) for n in ns],
        *[Cell("G2", "gsize2", f"n{n}", "splitn", ("pfifo",), point="EXT", seeds=S(3), opts={"n": n}) for n in (8, 12)],
        Cell("G3", "sburst", "w16", "base", PC, point="EXT", seeds=S(3), pfifo_ms=200.0,
             opts={**leaf_opts(16), "delays": LEAF16W_MS}),
    ]


def k2() -> list[Cell]:
    top = (3, 4, 5)
    return [
        Cell("X1", "hhier", "s030", "split4", ("pfifo", "codel", "pie"), point="EXT", seeds=top),
        *[Cell("X2", r, v, k, PC, point="EXT", seeds=top)
          for r, v, k in (("hindep", "s030", "split4"), ("huneven", "uneven", "uneven"), ("amixed", "access", "access"))],
        Cell("X3", "hdepth", "tree16", "tree16", ("pfifo",), point="EXT", seeds=top),
        Cell("X3", "sburst", "s030u070", "base", ("pie",), point="EXT", seeds=top),
        Cell("X4", "hhier", "ext", "split4l", ("pfifo",), point="EXT", seeds=S(2)),
        *[Cell("X5", "sburst", p.lower(), "base", PC, point=p, seeds=S(3)) for p in ("HS50", "HS70")],
        Cell("X6", "hhier", "hs50", "split4l", PC, point="HS50", seeds=S(3)),
        Cell("N1", "hshift", "def", "split4l", PC, seeds=S(3)),
        Cell("N1", "hshift", "sustained", "split4l", ("pfifo",), seeds=S(2)),
        Cell("N2", "spersist", "def", "base", PC, seeds=S(2)),
        Cell("N3", "hchurn", "def", "split4l", PC, seeds=S(3), note="variant move skipped (no stable identity)"),
        *[Cell("N4", "hconc", f"f{round(f * 100):03d}", "par", ("pfifo",), seeds=S(3), opts={"k": 2}) for f in CONC_F],
        Cell("N5", "hsparse", "def", "split4l", PC, seeds=S(3)),
        *[Cell("N6", "hhier", f"bg{m}", "split4l", ("pfifo",), seeds=S(2), bg_mode=m) for m in ("bursty", "mix")],
        Cell("N7", "hjoin", "def", "split4l", PC, seeds=S(2)),
        Cell("N8", "negcalm", "split4l", "split4l", PC, seeds=S(2)),
        Cell("N8", "negcalm", "par4", "par", PC, seeds=S(2), opts={"k": 4}),
        Cell("N8", "negpriv", "def", "access", PC, seeds=S(2)),
        Cell("N8", "neglossh", "def", "split4l", ("pfifo",), seeds=S(2)),
        *[Cell("T1", "dclean", p.lower(), "base", ("pfifo",), point=p, seeds=S(2)) for p in ("DEF", "EXT", "HS50")],
        *[Cell("T2", "sburst", f"jit{j:g}", "base", PC, seeds=S(2), opts={"fwd_jitter_ms": j}) for j in JITTER_LEVELS],
        Cell("T3", "sdense", "def", "base", ("pfifo",), seeds=S(2)),
        *[Cell("T3", "smild", f"u{round(u * 100)}", "base", PC, seeds=S(2)) for u in MILD_LEVELS],
        Cell("T3", "rrevasym", "def", "rev", ("pfifo",), seeds=S(2), opts={"rev_asym": True}),
    ]


def micro_def() -> list[Cell]:
    """v3 M1-M12, M14 at DEF (same definitions; M7 / M8 on T-SPLIT4L, which fits at DEF)."""
    out = []
    for c in v3.MICRO:
        if c.block == "M13":
            continue
        kind = "split4l" if c.kind == "split4" else c.kind
        opts = dict(c.build_opts) | ({"noroot": True} if c.variant == "noroot" else {})
        point_s, point_U = (c.s, c.U) if c.block == "M11" else (None, None)
        out.append(Cell("M", c.rtype, f"{c.block.lower()}-{c.variant}", kind, c.aqms, seeds=S(2), bg_mode=c.bg_mode,
                        pfifo_ms=c.pfifo_ms, stim=c.stim, opts=opts, s=point_s, U=point_U,
                        note="M11 keeps s 0.65 / U 0.70" if c.block == "M11" else ""))
    return out


def k3() -> list[Cell]:
    lit = {"literature": True}
    return [
        Cell("L1", "fbload", "def", "par", ("pie", "codel", "pfifo"), opts={"k": 4}, bg_mode="bursty", **lit),
        *[Cell("L2", "fbcross", v, "par", ("pie", "codel"), opts={"k": 4}, bg_mode="bursty", s=s_, **lit)
          for v, s_ in CROSS_S.items()],
        Cell("L3", "fblag", "def", "par", ("pie", "codel"), opts={"k": 4, "lag": True}, bg_mode="bursty", **lit),
        *[Cell("L4", "fbscale", v, "par", ("pie",), opts=o, bg_mode="bursty", **lit)
          for v, o in (("par2", {"k": 2}), ("par6", {"k": 6}), ("par4x8", {"k": 4, "per": 8}))],
        Cell("L5", "fbcold", "def", "par", ("pie", "codel"), seeds=S(10), opts={"k": 4}, bg_mode="bursty", **lit),
        Cell("L6", "ppar", "def", "par", PC, seeds=S(3), opts={"k": 4}),
        *[Cell("L7", "hycombo", v, "hayes", ("pfifo",), seeds=S(3), **lit) for v in ("surge", "cap")],
        *[Cell("L8", "hytb", f"bdp{b}", "teacup", ("pfifo",), pfifo_ms=ms, bg_mode="onoff", **lit)
          for b, ms in (("05", 50.0), ("1", 100.0), ("2", 200.0))],
        Cell("L8", "hytb", "rev", "teacup", ("pfifo",), pfifo_ms=100.0, bg_mode="onoff", **lit),
        Cell("L9", "sbnsb", "sb", "base", ("pfifo",), seeds=S(3), bg_mode="mix",
             opts={"rates": {**_low("a"), **_low("b")}}, **lit),
        Cell("L9", "sbnsb", "nsb", "par", ("pfifo",), seeds=S(3), bg_mode="mix", opts={"k": 2}, **lit),
        Cell("L10", "hhier", "bgonoff", "split4l", ("pfifo",), bg_mode="onoff", **lit),
        Cell("L11", "sshort", "def", "base", PC, **lit),
        Cell("L11", "spause", "def", "base", ("pfifo",), **lit),
        Cell("L11", "sshortrfc", "def", "base", PC, **lit),
        *[Cell("C1", "calm", f"copa-{p.lower()}", "base", ("pfifo",), point=p, opts={"cc": "copa"}) for p in ("DEF", "EXT")],
        Cell("C1", "sburst", "copa", "base", ("pfifo", "codel", "fq_codel"), opts={"cc": "copa"}),
        *[Cell("C1", r, "copa", k, ("pfifo",), opts={"cc": "copa"})
          for r, k in (("stcp", "base"), ("sjoin", "base"), ("hindep", "split4l"), ("amixed", "access"))],
        Cell("C1", "hhier", "copa", "split4l", PC, opts={"cc": "copa"}),
        *[c for r in (1.2, 6.0) for c in (
            Cell("I1", "calm", f"ip{r:g}", "base", ("pfifo",), opts={"ip_ratio": r}),
            Cell("I1", "sburst", f"ip{r:g}", "base", PC, opts={"ip_ratio": r}),
            Cell("I1", "hhier", f"ip{r:g}", "split4l", ("pfifo",), opts={"ip_ratio": r}))],
        *micro_def(),
    ]


HELD_OUT = [   # spec 6: prepared, NOT run (N1-N5 at DEF on v4 topologies; seeds 101..105)
    Cell("N1", "hindep", "split4l", "split4l", ("pfifo", "pie", "fq_codel"), seeds=S(5)),
    Cell("N2", "huneven", "unevenl", "unevenl", ("pfifo", "pie", "fq_codel"), seeds=S(5)),
    Cell("N3", "n3cross", "split4l", "split4l", ("pfifo", "fq_codel"), seeds=S(5)),
    Cell("N4", "n4trace", "access", "access", ("pfifo", "fq_codel"), seeds=S(5)),
    Cell("N5", "n5churn", "largel", "base", ("pfifo", "fq_codel"), seeds=S(5),
         opts={"rates": {f"sub-{c}": r for c, r in zip("abcdefgh", LOW * 2)}},
         note="v3 `large` (C 137 Mb/s at DEF) does not fit: low set twice (T)"),
]
HELD_OUT_SEED_BASE = v3.HELD_OUT_SEED_BASE

# topology identity for the gate's "one CALM per topology" (opts that change the wiring or the sizing)
TOPO_OPTS = ("rates", "k", "per", "n", "lag", "delays", "noroot")


def topo_key(c: Cell) -> tuple:
    return c.kind, "rev" if (c.kind == "teacup" and c.variant == "rev") else "", json.dumps({k: c.opts[k] for k in TOPO_OPTS
                                                                       if k in c.opts}, sort_keys=True)


def topo_name(kind: str, variant: str, o: dict) -> str:
    """Readable, unique name of a topology for gate / smoke run names."""
    rates = o.get("rates")
    size = ("" if rates is None else f"n{len(rates)}" if all(c.startswith("sub-") for c in rates) else "sb")
    return "-".join(x for x in (kind, "rev" if (kind == "teacup" and variant == "rev") else "",
                                *(f"{k}{o[k]}" for k in ("k", "per", "n") if k in o), "lag" if o.get("lag") else "",
                                size, "w" if "delays" in o else "", "noroot" if o.get("noroot") else "") if x)


NEW_STIM = {"persist": {"fbload", "fbcross", "fblag", "fbscale", "fbcold", "spersist", "hshift"},
            "shorttcp": {"sshort", "sshortrfc"}, "pause": {"spause"}, "cold": {"fbcold"}}


def gate_cells(cells: list[Cell]) -> list[Cell]:
    """Spec 7.3: one CALM per topology the campaign uses, one event run per new stimulus
    (and per new background mode) it uses; pfifo, one seed."""
    out, seen = [], set()
    for c in cells:
        if c.block == "M":   # v3 microbenchmark variants of T-BASE / T-SPLIT4L (rates, RTT, fps): their topologies are gated
            continue
        if c.kind == "hayes":   # (user, 2026-11-16) T-HAYES fails 4b gaps under 12 traced routers (smoke 1, cause open):
            continue            # not gated; its block runs last, marked "health unverified" (K3_LAST)
        key = topo_key(c)
        if key in seen:
            continue
        seen.add(key)
        v = topo_name(c.kind, c.variant, c.opts)
        out.append(Cell("GATE", "calm", v, c.kind, ("pfifo",), point=c.point, seeds=(1,), s=c.s, U=c.U,
                        opts={k: c.opts[k] for k in TOPO_OPTS if k in c.opts}, literature=c.literature))
    used = {r for c in cells for r in [c.rtype]}
    if used & NEW_STIM["persist"]:
        out.append(Cell("GATE", "g-persist", "base", "base", ("pfifo",), seeds=(1,)))
    if used & NEW_STIM["shorttcp"]:
        out.append(Cell("GATE", "g-shorttcp", "base", "base", ("pfifo",), seeds=(1,)))
    if used & NEW_STIM["pause"]:
        out.append(Cell("GATE", "g-pause", "base", "base", ("pfifo",), seeds=(1,)))
    if used & NEW_STIM["cold"]:
        # BG-CBR in the gate (decision 2026-11-16): the cold stimulus is what is checked; a 30 s mean of
        # BG-BURSTY varies by ~10 % and fails checks 1 / 5 by construction. The campaign keeps BG-BURSTY.
        out.append(Cell("GATE", "fbcold", "gate", "par", ("pfifo",), seeds=(1,), opts={"k": 4}, literature=True))
    if any(c.bg_mode == "onoff" for c in cells):
        out.append(Cell("GATE", "g-calm", "onoff", "split4l", ("pfifo",), seeds=(1,), bg_mode="onoff"))
    return out


def smoke_cells() -> list[Cell]:
    """Spec 7.2: a 60 s CALM per new topology, a 90 s run per new stimulus and background
    mode, the n_max search (90 s at n 24 / 32 / 40)."""
    topos = [("split4l", {}), ("unevenl", {}), ("par", {"k": 2}), ("par", {"k": 4}), ("par", {"k": 6}),
             ("par", {"k": 4, "per": 8}), ("par", {"k": 4, "lag": True}), ("splitn", {"n": 8}), ("splitn", {"n": 12}),
             ("hayes", {}), ("teacup", {}), ("base", {"rates": {**_low("a"), **_low("b")}}),
             *[("base", leaf_opts(n)) for n in (4, 8, 16)], ("base", {**leaf_opts(16), "delays": LEAF16W_MS})]
    out = []
    for kind, o in topos:
        point = "EXT" if kind == "splitn" or (kind == "base" and "rates" in o and len(o["rates"]) != 8) else "DEF"
        v = topo_name(kind, "", o)
        out.append(Cell("SMOKE", "s-calm", v, kind, ("pfifo",), point=point, seeds=(1,), opts=o,
                        pfifo_ms=200.0 if "delays" in o else v3.PFIFO_MS, literature=kind in ("hayes", "teacup")))
    out.append(Cell("SMOKE", "s-calm", "teacup-rev", "teacup", ("pfifo",), seeds=(1,), pfifo_ms=100.0, literature=True))
    for n in NMAX_CANDIDATES:
        out.append(Cell("NMAX", "g-calm", f"n{n}", "base", ("pfifo",), point="EXT", seeds=(1,), opts=leaf_opts(n)))
    for r in ("g-persist", "g-shorttcp", "g-pause"):
        out.append(Cell("SMOKE", r, "base", "base", ("pfifo",), seeds=(1,)))
    out.append(Cell("SMOKE", "fbcold", "smoke", "par", ("pfifo",), seeds=(1,), opts={"k": 4},   # BG-CBR as in the gate
                    literature=True))
    out.append(Cell("SMOKE", "g-calm", "onoff", "split4l", ("pfifo",), seeds=(1,), bg_mode="onoff"))
    return out


CAMPAIGNS = {"K1": k1, "K2": k2, "K3": k3}
K3_LAST = ("L7",)   # (user, 2026-11-16) T-HAYES blocks: after every other K3 run, "health unverified" in the manifest


# ---------------------------------------------------------------- planning

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


def run_name(c: Cell, aqm: str, seed: int) -> str:
    return f"v4-{c.block}-{c.rtype}-{c.variant}-{aqm}-r{seed}"


def topo_of(c: Cell, seed: int) -> Topo:
    s, U = c.su
    return build4(c.kind, c.variant if c.kind in ("teacup", "split4") else "", s, U, seed, c.opts)



def plan_run(c: Cell, aqm: str, seed: int, gen: Path, campaign: str, seed_base: int = 0) -> Planned:
    seed = seed_base + seed
    t = topo_of(c, seed)
    events, windows, duration = plan_type4(c.rtype, t, seed, c.variant, c.stim)
    bg = background4(t, c.bg_mode, seed, duration)
    if c.rtype == "dclean":
        for e in bg:
            e["at_s"], e["duration_s"] = DCLEAN_BG_AT, round(duration - DCLEAN_BG_AT, 3)
    if t.kind == "teacup" and t.rev is not None:   # the ACK path of up loaded to 90 % with UDP
        bg.append(v3.cbr_event("bg-rev", "rshared", TEACUP_REV_LOAD * TEACUP_REV_MBPS, duration, seed * 1000 + 99))
    events = bg + events
    if c.rtype in ("nloss", "neglossh"):   # live loss edits need netem loss on those directions from t = 0
        for cond in t.links:
            if cond["to"] in t.rates and cond["from"] == t.uplink[cond["to"]]:
                cond["forward"]["loss_pct"] = 0
    data = {"duration_s": duration,
            "link_defaults": {"forward": {"bandwidth_mbps": 100}, "reverse": {"bandwidth_mbps": 100}},
            "links": t.links, "routers": v3.aqm_routers(t, aqm, c.pfifo_ms), "events": events}
    name = run_name(c, aqm, seed - seed_base)
    gen.mkdir(parents=True, exist_ok=True)
    scen, topo = gen / f"{name}.yaml", gen / f"{name}-topology.yaml"
    scen.write_text(yaml.safe_dump(data, sort_keys=False))
    topo.write_text(yaml.safe_dump(t.topo, sort_keys=False))
    (gen / f"{name}-windows.json").write_text(json.dumps(windows, indent=1))
    violations = constraint_check4(t, c.literature)
    s, U = t.s, t.U
    meta = {"campaign": f"v4-{campaign}", "block": c.block, "type": c.rtype, "variant": c.variant, "topology": c.kind,
            "topology_opts": {k: v for k, v in c.opts.items() if k != "rates"} | (
                {"clients": len(c.opts["rates"])} if "rates" in c.opts else {}),
            "point": c.point if c.s is None and c.U is None else "custom",
            "aqm": aqm, "rep": seed - seed_base, "seed": seed, "video_seed": seed, "duration_s": duration,
            "s": s, "U": U, "bg_mode": c.bg_mode, "pfifo_limit_ms": c.pfifo_ms, "stimulus": c.stim,
            "phase": c.opts.get("phases", "sync"), "literature": c.literature,
            "egress": {e.name: {"hop": f"{e.hop[0]}->{e.hop[1]}", "C_e_mbps": e.cap, "BG_e_mbps": e.bg,
                                "D_e_mbps": e.demand, "clients": e.clients, "shaped": e.shaped,
                                "s": _point_of(e, t)[0], "U": _point_of(e, t)[1],
                                "keyframe_peak_ref_ms": round(121 * _point_of(e, t)[0] * _point_of(e, t)[1], 1)
                                if e.shaped and _point_of(e, t)[0] else None}
                       for e in t.egress.values()},
            "access_delay_ms": t.delays, "asv": {"key_spread_ms": v3.ASV_KEY_MS, "p_spread_ms": v3.ASV_P_MS},
            "constraint_violations": violations, "git": v3.git_commit(), "note": c.note,
            "subscriber_paths": {sid: sub["path"] for sid, sub in t.topo["subscribers"].items() if "path" in sub},
            "phases_ms": {sid: sub.get("phase_ms", 0) for sid, sub in t.topo["subscribers"].items()}}
    (gen / f"{name}-plan.json").write_text(json.dumps(meta, indent=1))
    return Planned(name, c, aqm, seed - seed_base, duration, scen, topo, violations)


def plan_all(gen: Path, cells: list[Cell], campaign: str, seed_base: int = 0) -> list[Planned]:
    """Queue order (spec 6): all seed 1 in block order, then all seed 2, and so on."""
    seeds = sorted({r for c in cells for r in c.seeds})
    return [plan_run(c, aqm, r, gen, campaign, seed_base) for r in seeds for c in cells if r in c.seeds
            for aqm in c.aqms]


def check_violations(plans: list[Planned]) -> list[str]:
    return [f"{p.name}: " + "; ".join(p.violations) for p in plans
            if p.violations and not any(v in p.cell.variant for v in LISTED_VIOLATIONS)]


# ---------------------------------------------------------------- running

def run_one(p: Planned, kdir: Path) -> bool:
    ok = v3.run_one(p, kdir)
    if ok:
        try:
            import v4_checks
            print("   " + v4_checks.line(v4_checks.run_checks(kdir / p.name)), flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"   v4 checks failed: {e!r}", flush=True)
    return ok


def gate_verdict(run_dirs: list[Path], smoke: bool = False) -> tuple[bool, str]:
    import v3_gate
    import v4_checks
    verdict, text = v3_gate.gate_report(run_dirs, smoke=smoke)
    ok4, text4 = v4_checks.report(run_dirs)
    verdict = verdict and ok4
    title = "Smoke" if smoke else "Gate"
    head, _, rest = text.partition("\n")
    return verdict, f"# {title}: {'PASS' if verdict else 'FAIL'}\n" + rest + text4


def run_campaign(kdir: Path, gate: list[Planned], plans: list[Planned]) -> int:
    v3.manifest_update(kdir, started=v3.manifest_update(kdir).get("started") or datetime.datetime.now().isoformat(
        timespec="seconds"), git=v3.git_commit(), host=v3.cpu_governor())
    report = kdir / "gate-report.md"
    passed = report.exists() and report.read_text().startswith("# Gate: PASS")
    if not passed:
        for p in gate:
            ok = run_one(p, kdir)
            v3.manifest_update(kdir, runs={p.name: "done" if ok else "failed"})
        verdict, text = gate_verdict([kdir / p.name for p in gate])
        report.write_text(text)
        print(f"gate: {'PASS' if verdict else 'FAIL'} -> {report}", flush=True)
        if not verdict:
            v3.manifest_update(kdir, stopped="gate failed")
            return 3
    for p in plans:
        ok = run_one(p, kdir)
        v3.manifest_update(kdir, runs={p.name: "done" if ok else "failed"})
    v3.manifest_update(kdir, finished=datetime.datetime.now().isoformat(timespec="seconds"))
    try:
        import v3_gate
        v3_gate.campaign_summary(kdir)
    except Exception as e:  # noqa: BLE001
        print(f"campaign summary failed: {e!r}", flush=True)
    return 0


def nmax_from(kdir: Path) -> dict:
    """Spec 2.4: the largest n in NMAX_CANDIDATES whose 90 s run passes the health check
    (v3 check 4: CPU idle, inter-dequeue error, tracer)."""
    res = {}
    for n in NMAX_CANDIDATES:
        p = kdir / f"v4-NMAX-g-calm-n{n}-pfifo-r1" / "v3-checks.json"
        h = json.loads(p.read_text()).get("4_health", {}) if p.exists() else {}
        res[n] = {"health_ok": h.get("ok"), "cpu_idle_min": h.get("cpu_idle_min"), "bad": h.get("bad")}
    ok = [n for n in NMAX_CANDIDATES if res[n]["health_ok"]]
    return {"n_max": max(ok) if ok else None, "candidates": res,
            "flag": None if ok else "no candidate passed: n_max below 24 (spec 9 FLAG)"}


# ---------------------------------------------------------------- plan-only output

def print_plan(name: str, gate: list[Planned], plans: list[Planned], unexpected: list[str], nmax: int) -> None:
    hours = lambda ps: sum(p.duration for p in ps) / 3600   # noqa: E731
    print(f"# Suite v4 plan: campaign {name}\n")
    print(f"git {v3.git_commit()}; n_max used for G1: {nmax}\n")
    for title, ps in (("Gate", gate), (name, plans)):
        print(f"## {title}: {len(ps)} runs, {hours(ps):.2f} h emulated\n")
        print("| block | runs | hours |\n|---|---|---|")
        for b in dict.fromkeys(p.cell.block for p in ps):
            bs = [p for p in ps if p.cell.block == b]
            print(f"| {b} | {len(bs)} | {hours(bs):.2f} |")
        print()
    print(f"**Total {name}: {len(gate) + len(plans)} runs, {hours(gate) + hours(plans):.2f} h emulated** "
          f"(spec estimate {SPEC_HOURS.get(name, '-')} h; no cut rule: every block is kept).\n")
    print("## Per-egress sizing (every topology and point of this campaign)\n")
    print("| topology | variant | point (s, U) | egress | hop | D_e | C_e | BG_e | target (s, U) | pfifo pkts | "
          "constraints |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    seen = set()
    for p in gate + plans:
        key = (topo_key(p.cell), p.cell.su, p.cell.pfifo_ms)
        if key in seen:
            continue
        seen.add(key)
        t = topo_of(p.cell, 1)
        for e in t.egress.values():
            s_e, U_e = _point_of(e, t)
            lim = v3.queue("pfifo", e.cap, p.cell.pfifo_ms)["queue_limit_packets"] if e.shaped else "-"
            print(f"| {t.kind} | {p.cell.variant} | {t.s}, {t.U} | {e.name} | {e.hop[0]}->{e.hop[1]} | {e.demand:.3f} | "
                  f"{e.cap:g}{'' if e.shaped else ' (unshaped)'} | {e.bg:g} | {s_e}, {U_e} | {lim} | "
                  f"{'; '.join(constraint_check4(t, p.cell.literature)) or 'ok'} |")
    print("\n## Constraint flags\n")
    for v, why in LISTED_VIOLATIONS.items():
        print(f"- kept (v3 M11 at its own s / U): {v}: {why}")
    for u in unexpected:
        print(f"- VIOLATION (cell to skip, spec 1): {u}")
    if not unexpected:
        print("- no other violation")
    print("\n## Runs\n")
    print("| # | run | duration s |\n|---|---|---|")
    for i, p in enumerate(gate + plans, 1):
        print(f"| {i} | {p.name} | {p.duration:.0f} |")


def validate(p: Planned) -> None:
    v3.validate(p)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--run", action="store_true")
    ap.add_argument("--set", choices=sorted(CAMPAIGNS), help="campaign K1, K2 or K3")
    ap.add_argument("--smoke", action="store_true", help="the smoke plan (spec 7.2) instead of a campaign")
    ap.add_argument("--held-out", action="store_true", help="N1-N5 at DEF (prepared; do not run before the freeze)")
    ap.add_argument("--campaign", type=Path, help="campaign folder (resume); default a new .runs/<ts>_v4-<set>")
    ap.add_argument("--only", default=None, help="smoke: comma-separated substrings of the run names to run")
    ap.add_argument("--nmax", type=int, default=None, help="K1: n_max from the smoke (nmax.json); plan-only default 40")
    a = ap.parse_args(argv)
    if a.smoke:
        kdir = a.campaign or RUNS / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_v4-smoke"
        plans = plan_all(kdir / "_gen", smoke_cells(), "smoke")
        if a.only:
            plans = [p for p in plans if any(x in p.name for x in a.only.split(","))]
        for p in plans:
            validate(p)
        bad = check_violations(plans)
        if a.plan_only:
            print(f"smoke: {len(plans)} runs, {sum(p.duration for p in plans) / 3600:.2f} h; violations: {bad or 'none'}")
            for p in plans:
                print(f"  {p.name} {p.duration:.0f} s")
            return 2 if bad else 0
        for p in plans:
            run_one(p, kdir)
        verdict, text = gate_verdict([kdir / p.name for p in plans if p.cell.block != "NMAX"], smoke=True)
        if any(p.cell.block == "NMAX" for p in plans):
            nm = nmax_from(kdir)
            (kdir / "nmax.json").write_text(json.dumps(nm, indent=1))
            text += f"\n## n_max (spec 2.4)\n\n```\n{json.dumps(nm, indent=1)}\n```\n"
        else:
            nm = {"n_max": "not searched in this smoke"}
        (kdir / "smoke-report.md").write_text(text)
        print(f"smoke: {'PASS' if verdict else 'FAIL'} -> {kdir / 'smoke-report.md'}; n_max {nm['n_max']}")
        return 0 if verdict else 3
    if a.held_out:
        kdir = a.campaign or RUNS / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_v4-heldout"
        plans = plan_all(kdir / "_gen", HELD_OUT, "heldout", seed_base=HELD_OUT_SEED_BASE)
        for p in plans:
            validate(p)
        print(f"held-out v4 (DEF): {len(plans)} runs, {sum(p.duration for p in plans) / 3600:.2f} h, "
              f"written to {kdir / '_gen'}; violations: {check_violations(plans) or 'none'}")
        if a.run:
            for p in plans:
                run_one(p, kdir)
        return 0
    if not a.set:
        ap.error("--set K1|K2|K3 (or --smoke / --held-out)")
    if a.set == "K1" and a.run and a.nmax is None:
        ap.error("K1 needs --nmax (the smoke writes it to <smoke>/nmax.json)")
    nmax = a.nmax or max(NMAX_CANDIDATES)
    cells = CAMPAIGNS[a.set](nmax) if a.set == "K1" else CAMPAIGNS[a.set]()
    kdir = a.campaign or RUNS / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_v4-{a.set}"
    gen = kdir / "_gen"
    gate = plan_all(gen, gate_cells(cells), a.set)
    plans = plan_all(gen, cells, a.set)
    last = [p for p in plans if a.set == "K3" and p.cell.block in K3_LAST]
    plans = [p for p in plans if p not in last] + last
    for p in gate + plans:
        validate(p)
    unexpected = check_violations(gate + plans)
    if a.plan_only:
        print_plan(a.set, gate, plans, unexpected, nmax)
        return 2 if unexpected else 0
    if unexpected:
        print("constraint violations (spec 1: skip and list these cells):\n" + "\n".join(unexpected))
        return 2
    kdir.mkdir(parents=True, exist_ok=True)
    v3.manifest_update(kdir, campaign=f"v4-{a.set}", nmax=nmax if a.set == "K1" else None,
                       planned_hours=round(sum(p.duration for p in gate + plans) / 3600, 2))
    if last:
        v3.manifest_update(kdir, health_unverified={
            "runs": [p.name for p in last],
            "why": "T-HAYES not in the gate: check 4b gaps fail with 12 traced routers in smoke 1 (cause open: tracer "
                   "timestamp noise or HTB catch-up under CPU load; 20 ms windows exact). These runs are last in K3."})
    return run_campaign(kdir, gate, plans)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
