#!/usr/bin/env python3
"""Grouping campaigns (development set K1-K6, held-out set N1-N5): plan the
runs, run them one after another, and write each campaign's grouping report
as soon as its last run finishes.

    python3 scripts/grouping_campaign.py --plan                       # write the YAMLs, print the budget, run nothing
    python3 scripts/grouping_campaign.py --ks N1,N2,K1,K2,K3,K5,K6,N3,N4,N5   # the whole thing (tmux)
    python3 scripts/grouping_campaign.py --campaign .runs/<dir> --skip-existing   # resume
    python3 scripts/grouping_campaign.py --campaign .runs/<dir> --report-only     # (re)score only
    python3 scripts/grouping_campaign.py --campaign .runs/<dir> --report-only --compare .runs/<old>  # flag worse cells

Grouping-only tooling: the detector is the frozen Shadow v2 (scripts/shadow_v2_frozen.py) and
BBR is the only congestion control. It reuses det_matrix's topology numbers
and AQM table (import only) and the quiclab CLI; it writes
.runs/<ts>_grp/<K>/{_gen, grp-<type>-<aqm>-r<rep>/, manifest.yaml, report.md}.
After every run det_eval.score is attempted (the detector's own report, best
effort) and the run's stimulus windows are copied to <run>/grouping/windows.json:
grouping truth = the plan's expected clients are hit in a window when the
window's router egress (`hop`) shows a GT1 standing-queue episode there
(router counters, independent of the detector's input; GT3 per-client OWD is
the secondary truth). Every window carries `hop`, `stimulus_type` (capdrop |
udp | tcp | trace) and `concurrent` (overlaps, within 1 s, a window on another
bottleneck).

Specification: grouping/campaign-v2-spec.md (scenarios, outputs, pass criteria;
the criteria were written before the held-out runs). Rep = seed, same seed on
every AQM; calm u ~0.65; capacity drops unless said otherwise; default cells
u {1.3, 2.0} x d {1, 2, 4} s; gaps U(10, 15) s unless "independent timing"
(one exponential process per bottleneck, mean 30 s, minimum 5 s, no scripted
simultaneity; accidental overlaps are kept and flagged).

Development set (the rules were developed on these):
  K1 hier   split topology: cells x targets up | a | b | a+b (same instant,
            the scripted worst case) | a+b@0.5 | a+b@2 | a+up. AQMs: 4 uniform
            + mixab (r1 pfifo; branches differ on r2: switch-a pfifo, switch-b
            fq_codel). 3 reps.
  K2 part   detector topology: Poisson on/off capacity drops at one severity
            per run, u in {1.05, 1.1, 1.15, 1.3}. pfifo, fq_codel. 3 reps.
  K3 rev    revasym, revjit10 (detector topology), revcross, revcrossmix
            (detector-rev topology). pfifo, fq_codel, 3 reps; scored with the
            RTT and the OWD detector (sources v2, v2-owd).
  K5 mixed  detector-access topology: 12 shared cap bursts + 16 private access
            drops shuffled; sub-d joins at 60 s; nobody leaves. 4 AQMs, 3 reps.
  K6 depth  tree8 topology (2.5 / 5 Mb/s per leaf since 2026-11-10): targets
            A | B | C | D | X | Y | root | A+C. pfifo, fq_codel, 5 reps.
Held-out set (5 reps each, pass criteria in the spec):
  N1 indep  split topology, independent timing on up, a, b; 600 s. pfifo, pie, fq_codel.
  N2 uneven detector-uneven topology (branches of 2, 5 and 9 clients; type
            uneven6 = reduced branch C of 6), independent timing on A, B, C;
            600 s. pfifo, pie, fq_codel.
  N3 cross  split topology, cross traffic as the stimulus on the existing
            routes: UDP constant rate (offered load u x capacity) or 2 / 4
            Cubic bulk flows for 4 / 8 s, equal probability; independent timing;
            600 s. pfifo, fq_codel.
  N4 trace  detector-access topology: each client's access link replays a
            scaled cellular trace (configs/traces, 200 ms steps, mean 2 x the
            client's bitrate, below the bitrate 5-15 % of the run); shared cap
            drops with U(10, 15) s gaps; 600 s. Private truth windows = the
            trace below the client's wire rate. Shared link pfifo / fq_codel.
  N5 churn  large topology (8 clients): every client alternates on (exp mean
            90 s, min 20) / off (exp mean 30 s, min 5), sessions after the
            first run as <client>_<n>; shared cap drops sized to the demand of
            the clients that are on; 900 s. pfifo, fq_codel.
"""

from __future__ import annotations

import argparse
import atexit
import datetime
import json
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import traceback
from argparse import Namespace
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402
import det_matrix as dm  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import e2e_score  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import grouping_baselines as gb  # noqa: E402
from grouping import Config  # noqa: E402
from quiclab.config.scenario import Scenario, load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.runtime import remove_partial_run, run_finished  # noqa: E402

RUNS = ROOT / ".runs"
# Extra topologies, registered with det_matrix's table (import time only, the file is not changed).
dm.TOPOLOGIES.setdefault("tree8", ("detector-tree8.yaml", "grp-burst-tree8.yaml", {
    "root": ("rr", "r0", None), "X": ("r0", "r1", None), "Y": ("r0", "r2", None),
    "A": ("r1", "switch-a", None), "B": ("r1", "switch-b", None), "C": ("r2", "switch-c", None),
    "D": ("r2", "switch-d", None)}, "root"))
dm.TOPOLOGIES.setdefault("rev", ("detector-rev.yaml", "grp-burst-rev.yaml", {"main": ("r1", "switch", "shared")}, "main"))
for _variant in ("uneven", "uneven6"):
    dm.TOPOLOGIES.setdefault(_variant, (f"detector-{_variant}.yaml", f"grp-burst-{_variant}.yaml", {
        "A": ("r2", "switch-a", None), "B": ("r2", "switch-b", None), "C": ("r2", "switch-c", None)}, "C"))
# Microbenchmark variants of the base topology: publisher frame rate, bitrate mixes.
for _variant in ("fps15", "fps60"):
    dm.TOPOLOGIES.setdefault(_variant, (f"detector-{_variant}.yaml", "det-burst.yaml",
                                        {"main": ("router", "switch", "shared")}, "main"))
for _variant in ("bw1", "bw8", "bwmix"):
    dm.TOPOLOGIES.setdefault(_variant, (f"detector-{_variant}.yaml", f"det-burst-{_variant}.yaml",
                                        {"main": ("router", "switch", "shared")}, "main"))
# Extra det_matrix specs (import time only): queue depth x0.5 / x1.5 / x2 (x0.25 and x4 stay as the
# known limit rows burstcapshallow / burstcapdeep) and long bursts on every split bottleneck.
for _name, _scale in (("burstcapq05", 0.5), ("burstcapq15", 1.5), ("burstcapq20", 2.0)):
    dm.BURST_SCENARIOS.setdefault(_name, {**dm.BURST_SCENARIOS["burstcap"], "queue_scale": _scale})
dm.BURST_SCENARIOS.setdefault("burstlongsplit", {**dm.BURST_SCENARIOS["burstlong"], "targets": ("up", "a", "b")})

U_CAP, D_CAP = (1.1, 1.3, 2.0), (1, 2, 4)   # one severity grid everywhere (v2 review: grouping saw no u 1.1 before)
UNIFORM = ["pfifo", "red", "pie", "fq_codel"]   # the core set of the spec; cake (det_matrix.AQMS) is for the microbenchmarks
MIXED = {"mixa": {"r1": "pfifo", "r2": "fq_codel"}, "mixb": {"r1": "fq_codel", "r2": "pfifo"},
         "mixab": {"r1": "pfifo", "r2": "pfifo"}}
# On top of MIXED: router -> neighbor -> AQM of that one egress.
MIXED_EGRESS = {"mixab": {"r2": {"switch-a": "pfifo", "switch-b": "fq_codel"}}}
REV_ASYM_MS = (5, 40, 80, 120)
REV_LINK, REV_LINK_MBPS = ("r0", "r1"), 10.0     # its reverse direction is the router egress r1 -> r0
K2_U = (1.05, 1.1, 1.15, 1.3)
K2_ON, K2_ON_LONG, K2_OFF, K2_P_LONG, K2_T_END = (1.0, 4.0), (10.0, 20.0), (5.0, 20.0), 0.15, 300.0
JOIN_T, JOIN_SUB = 60.0, "sub-d"          # K5: sub-d joins; since v2 nobody leaves (K5 of 2026-11-06: sub-b left at 240 s)
HIER_TARGETS = ["up", "a", "b", "a+b", "a+b@0.5", "a+b@2", "a+up"]   # v2 dropped a+b@1
# Independent timing (N1-N3): one process per bottleneck, exponential gaps.
INDEP_GAP_MEAN_S, INDEP_GAP_MIN_S, N_DURATION_S = 30.0, 5.0, 600.0
# Event-frequency microbenchmarks: gaps between stimuli (grid timing on base, independent timing on split).
GAPS = {"gapfast": (2.0, 5.0), "gapslow": (45.0, 75.0)}
INDEP_MEANS = {"indepfast": 10.0, "indepslow": 60.0}
MICRO = ["pfifo", "red", "pie", "cake", "codel"]   # microbenchmark AQMs (user decisions: 2026-11-10 fq_codel core only, 2026-11-11 + codel)
CONCURRENT_S = 1.0                        # windows on different bottlenecks closer than this are `concurrent`
TCP_FLOWS, TCP_D = (2, 4), (4, 8)         # N3 TCP bulk: Cubic flows x duration
# N4 trace-driven access links.
TRACES = ROOT / "configs" / "traces"
TRACE_STEP_S, TRACE_MEAN_X, TRACE_BELOW, TRACE_MIN_MBPS = 0.2, 2.0, (0.05, 0.15), 0.1
TRACE_EXCLUDE = ("EVDO", "UMTS")          # the spec names Mahimahi's LTE traces; the 3G ones stay in configs/traces unused
TRACE_MERGE_S = 1.0                       # private dips closer than this are one window (as alarm flaps merge)
TRACE_LAG_MAX_S = 0.05                    # a trace step applied later than this is flagged (a full step late is invisible)
# N5 churn: on / off times per client (exponential with a floor), seconds.
N5_DURATION_S, N5_ON, N5_OFF = 900.0, (90.0, 20.0), (30.0, 5.0)
ENGINE_SET = {"theta_J": 0.6, "theta_cov": 0.6}   # the sweep value used in every real-run result so far
# Detector = the frozen Shadow v2 (scripts/shadow_v2_frozen.py; user decision 2026-11-10). The v1 sources
# "shadow" / "shadow-owd" stay available in grouping_adapter.py but are no longer scored here.
PRIMARY = "v2-owd"                         # the main signal: v2 on sender-side OWD, with the hold rule
COMPARE = ("v2", "v2-owd-nohold", "v2-nohold")   # comparison rows: RTT input, and both without the hold rule
ONSET_SOURCES = (PRIMARY, *COMPARE, "owd", "truth")   # scored on every run

# K -> topology, AQM ids, run types, reps, extra onset sources.
CAMPAIGNS = {
    "K1": {"topology": "split", "aqms": UNIFORM + ["mixab"], "types": ["hier"], "reps": 3},
    "K2": {"topology": "base", "aqms": ["pfifo", "fq_codel"], "types": [f"part{round(u * 100)}" for u in K2_U],
           "reps": 3},
    "K3": {"topology": "base", "aqms": ["pfifo", "fq_codel"],
           "types": ["revasym", "revjit10", "revcross", "revcrossmix"], "reps": 3},
    "K5": {"topology": "access", "aqms": UNIFORM, "types": ["mixed"], "reps": 3},
    "K6": {"topology": "tree8", "aqms": ["pfifo", "fq_codel"], "types": ["depth"], "reps": 5},
    "N1": {"topology": "split", "aqms": ["pfifo", "pie", "fq_codel"], "types": ["indep"], "reps": 5},
    "N2": {"topology": "uneven", "aqms": ["pfifo", "pie", "fq_codel"], "types": ["uneven"], "reps": 5},
    "N3": {"topology": "split", "aqms": ["pfifo", "fq_codel"], "types": ["cross"], "reps": 5},
    "N4": {"topology": "access", "aqms": ["pfifo", "fq_codel"], "types": ["trace"], "reps": 5},
    # No SBD baseline columns: DCW / rmcatSBD / dcSBD need one common time span over
    # long-lived flows (sbd_baselines.flow_table) and cannot follow sessions.
    "N5": {"topology": "large", "aqms": ["pfifo", "fq_codel"], "types": ["churn"], "reps": 5, "baselines": False},
    # Core addition: long bursts on a multi-group topology (a fair grouping comparison with the SBD baselines).
    "C1": {"topology": "split", "aqms": UNIFORM, "types": ["burstlongsplit"], "reps": 3},
    # Development study (2026-11-11, template grouping step F): the K1 plan on the split
    # topology with real per-client forward jitter on the access links (after the shared
    # bottleneck; netem normal law, packet order kept) and with keyframe phases that do
    # not separate the branches (b on a's phases; phases drawn per run).
    "J1": {"topology": "split", "aqms": ["pfifo"],
           "types": ["hierjit5", "hierjit10", "hierjit20", "hiersamephase", "hierrandphase"], "reps": 2},
    # Negatives: no congestion at all (every alarm / group is false); calm on every multi-group topology too.
    "G0": {"topology": "base", "aqms": UNIFORM + ["cake"],
           "types": ["calm030", "calm065", "calm090", "calmcbr090", "randloss", "calmsplit", "calmtree8", "calmuneven"],
           "reps": 3},
    # Microbenchmarks (base topology, one group, one factor at a time; grouping expects one leaf + sub-ctrl out).
    "M1": {"topology": "base", "aqms": MICRO, "reps": 3,
           "types": ["burstcap", "burstudp", "bursttiny", "ramp", "tcpcubic", "tcpbbr", "ppbp", "burstlong"]},
    "M2": {"topology": "base", "aqms": MICRO, "reps": 3,
           "types": ["burstcaplowrtt", "burstcaphighrtt", "burstcapq05", "burstcapq15", "burstcapq20"]},
    "M3": {"topology": "base", "aqms": MICRO, "reps": 3, "types": ["revjit5", "revjit10", "revjit20"]},
    "M4": {"topology": "base", "aqms": MICRO, "reps": 3, "types": ["fps15", "fps60"]},
    "M5": {"topology": "base", "aqms": MICRO, "reps": 3, "types": ["bw1", "bw8", "bwmix"]},
    "M6": {"topology": "base", "aqms": MICRO, "reps": 3, "types": ["gapfast", "gapslow", "indepfast", "indepslow"]},
}
TYPE_TOPOLOGY = {"revcross": "rev", "revcrossmix": "rev", "uneven6": "uneven6",      # types on another topology
                 "calmsplit": "split", "calmtree8": "tree8", "calmuneven": "uneven",
                 "fps15": "fps15", "fps60": "fps60", "bw1": "bw1", "bw8": "bw8", "bwmix": "bwmix",
                 "indepfast": "split", "indepslow": "split"}
# Types planned by det_matrix's event benchmark (name -> det_matrix scenario), scored by both pipelines.
DM_TYPES = {t: t for t in ("burstcap", "burstudp", "bursttiny", "ramp", "tcpcubic", "tcpbbr", "ppbp", "burstlong",
                           "burstcaplowrtt", "burstcaphighrtt", "burstcapq05", "burstcapq15", "burstcapq20",
                           "burstlongsplit", "calm030", "calm065", "calm090", "calmcbr090", "randloss")}
DM_TYPES.update({"calmsplit": "calm065", "calmtree8": "calm065", "calmuneven": "calm065",
                 "fps15": "burstcap", "fps60": "burstcap", "bw1": "burstcap", "bw8": "burstcap", "bwmix": "burstcap"})
HELD_OUT = ("N1", "N2", "N3", "N4", "N5")   # grouping scores only with --score-held-out (after the rule freeze)
GROUPS = {"core": ("K1", "K2", "K3", "K5", "K6", "C1", "N1", "N2", "N3", "N4", "N5"),
          "negatives": ("G0",), "micro": ("M1", "M2", "M3", "M4", "M5", "M6"), "study": ("J1",)}
HIER_VARIANTS = ("hierjit5", "hierjit10", "hierjit20", "hiersamephase", "hierrandphase")   # J1: the K1 plan


# ---------------------------------------------------------------- planning

def _cap_event(n: dict, tgt: str, at: float, u: float, d: float, label: str) -> list[dict]:
    h = n["hops"][tgt]
    return [{"at_s": round(at, 3), "type": "link", **h["link"], "bandwidth_mbps": round(h["demand"] / u, 3),
             "label": label},
            {"at_s": round(at + d, 3), "type": "link", **h["link"], "bandwidth_mbps": h["base"], "label": "burst-end"}]


def _window(start: float, end: float, kind: str, target: str, cell: str, expected: list[str],
            stimulus_type: str = "capdrop", **extra) -> dict:
    return {"start": round(start, 3), "end": round(end, 3), "kind": kind, "target": target, "cell": cell,
            "expected": sorted(expected), "stimulus_type": stimulus_type, "concurrent": False, **extra}


def flag_concurrent(windows: list[dict]) -> list[dict]:
    """`concurrent`: the window overlaps, within CONCURRENT_S, a window on another target."""
    for w in windows:
        w["concurrent"] = any(v["target"] != w["target"] and v["start"] - CONCURRENT_S <= w["end"]
                              and w["start"] - CONCURRENT_S <= v["end"] for v in windows)
    return windows


def cap_cells(targets: list[str], rng: random.Random, repeats: int = 1) -> list[tuple[float, float, str]]:
    cells = [(u, d, t) for u in U_CAP for d in D_CAP for t in targets] * repeats
    rng.shuffle(cells)
    return cells


def cap_sequence(n: dict, cells: list[tuple[float, float, str]], rng: random.Random,
                 t0: float = dm.WARMUP_S, gap: tuple[float, float] = dm.GAP_S) -> tuple[list[dict], list[dict], float]:
    """Capacity drops for cells (u, d, target); target 'a+b' = both at once,
    'a+b@0.5' = b 0.5 s after a. One window per link, labelled with the cell."""
    events, windows, t = [], [], t0
    for u, d, cell in cells:
        parts = cell.split("+")
        span = d
        for p in parts:
            tgt, _, off = p.partition("@")
            off = float(off or 0)
            events += _cap_event(n, tgt, t + off, u, d, f"burst u={u} d={d} {tgt}")
            windows.append(_window(t + off, t + off + d, "cap", tgt, cell, list(n["hops"][tgt]["clients"])))
            span = max(span, off + d)
        t += span + rng.uniform(*gap)
    return events, windows, round(t - gap[0] + dm.TAIL_S)


def plan_hier(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    return cap_sequence(n, cap_cells(HIER_TARGETS, rng), rng)


def plan_depth(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    return cap_sequence(n, cap_cells(["A", "B", "C", "D", "X", "Y", "root", "A+C"], rng), rng)


def plan_part(n: dict, seed: int, u: float) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    h = n["hops"][n["default"]]
    events, windows, t = [], [], dm.WARMUP_S
    while True:
        on = rng.uniform(*(K2_ON_LONG if rng.random() < K2_P_LONG else K2_ON))
        if t + on > K2_T_END - dm.TAIL_S:
            break
        events += _cap_event(n, n["default"], t, u, on, f"burst u={u} d={on:.3f}")
        windows.append(_window(t, t + on, "cap", n["default"], f"u={u}", list(h["clients"])))
        t += on + rng.uniform(*K2_OFF)
    return events, windows, K2_T_END


def plan_revcross(n: dict, seed: int, mix: bool) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    h = n["hops"][n["default"]]
    cells = [(u, d, "rev") for u in U_CAP for d in D_CAP] * 2
    if mix:
        cells += [(u, d, n["default"]) for u in U_CAP for d in D_CAP] * 2
    rng.shuffle(cells)
    events, rev, windows, t = [], [], [], dm.WARMUP_S
    for u, d, tgt in cells:
        if tgt == "rev":
            rev.append({"start_s": round(t, 3), "duration_s": d, "rate_mbps": round(u * REV_LINK_MBPS, 3)})
            windows.append(_window(t, t + d, "rev", "rev", "rev", []))
        else:
            events += _cap_event(n, tgt, t, u, d, f"burst u={u} d={d}")
            windows.append(_window(t, t + d, "cap", tgt, "fwd", list(h["clients"])))
        t += d + rng.uniform(*dm.GAP_S)
    events.append({"at_s": 0, "type": "bursts", "id": "udp-rev", "route": "rshared", "bursts": rev})
    return events, windows, round(t - dm.GAP_S[0] + dm.TAIL_S)


def plan_revbursts(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    return cap_sequence(n, cap_cells([n["default"]], rng, repeats=2), rng)


def plan_mixed(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    clients = sorted(n["clients"])
    cells = [(u, d, n["default"]) for u in U_CAP for d in D_CAP] * 2   # 12 shared windows (6 were too few to judge)
    cells += [(u, d, c) for u in U_CAP for d in (2, 4) for c in clients]
    rng.shuffle(cells)
    # The joining client has no access events before it joins.
    events, windows, t = [], [], dm.WARMUP_S
    pending = list(cells)
    while pending:
        pool = [c for c in pending if t > JOIN_T + 10 or c[2] != JOIN_SUB]
        u, d, tgt = pool[0]
        pending.remove(pool[0])
        if tgt in n["hops"]:
            events += _cap_event(n, tgt, t, u, d, f"burst u={u} d={d}")
            windows.append(_window(t, t + d, "cap", tgt, "shared", list(n["hops"][tgt]["clients"])))
        else:
            link, rate = {"from": n["uplink"][tgt], "to": tgt}, n["clients"][tgt]
            events += [{"at_s": round(t, 3), "type": "link", **link, "bandwidth_mbps": round(rate / u, 3),
                        "label": f"burst u={u} d={d} {tgt}"},
                       {"at_s": round(t + d, 3), "type": "link", **link, "bandwidth_mbps": n["access"],
                        "label": "burst-end"}]
            windows.append(_window(t, t + d, "access", tgt, "private", [tgt]))
        t += d + rng.uniform(*dm.GAP_S)
    events.append({"at_s": JOIN_T, "type": "join", "subscriber": JOIN_SUB})
    return events, windows, round(t - dm.GAP_S[0] + dm.TAIL_S)


# ---- held-out set

def indep_sequence(targets: list[str], seed: int, duration: float, make,
                   mean_gap: float = INDEP_GAP_MEAN_S) -> tuple[list[dict], list[dict]]:
    """Independent timing: one stimulus process per target with its own seeded
    stream, random phase, exponential gaps (mean INDEP_GAP_MEAN_S, floor
    INDEP_GAP_MIN_S). make(rng, target, t, k) -> (events, window, d) draws the
    cell. Simultaneity is never scripted; overlaps are kept and flagged."""
    events, windows = [], []
    for i, tgt in enumerate(targets):
        rng = random.Random(seed * 1000 + i)
        t, k = dm.WARMUP_S + rng.uniform(0, mean_gap), 0
        while True:
            ev, w, d = make(rng, tgt, t, k)
            if t + d > duration - dm.TAIL_S:
                break
            events += ev
            windows.append(w)
            k += 1
            t += d + max(INDEP_GAP_MIN_S, rng.expovariate(1 / mean_gap))
    events.sort(key=lambda e: e["at_s"])
    return events, flag_concurrent(sorted(windows, key=lambda w: w["start"]))


def plan_indep(n: dict, seed: int, mean_gap: float = INDEP_GAP_MEAN_S) -> tuple[list[dict], list[dict], float]:
    """N1 / N2 (and M6 indepfast / indepslow): capacity drops with independent timing on every bottleneck."""
    def make(rng, tgt, t, k):
        u, d = rng.choice(U_CAP), rng.choice(D_CAP)
        return (_cap_event(n, tgt, t, u, d, f"burst u={u} d={d} {tgt}"),
                _window(t, t + d, "cap", tgt, tgt, list(n["hops"][tgt]["clients"]), u=u), d)
    events, windows = indep_sequence(sorted(n["hops"]), seed, N_DURATION_S, make, mean_gap)
    return events, windows, N_DURATION_S


def plan_gaps(n: dict, seed: int, gap: tuple[float, float]) -> tuple[list[dict], list[dict], float]:
    """M6 gapfast / gapslow: the burstcap grid twice on the base bottleneck with another gap distribution."""
    rng = random.Random(seed)
    return cap_sequence(n, cap_cells([n["default"]], rng, repeats=2), rng, gap=gap)


def plan_cross(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    """N3: cross traffic on the bottleneck's traffic route as the stimulus. UDP
    constant rate (offered load u x capacity, so rate = u x cap - video demand)
    or TCP bulk (TCP_FLOWS Cubic flows for TCP_D s; u uncontrolled, the
    achieved load is measured afterwards), equal probability."""
    def make(rng, tgt, t, k):
        h = n["hops"][tgt]
        if rng.random() < 0.5:
            u, d = rng.choice(U_CAP), rng.choice(D_CAP)
            burst = {"route": h["route"], "burst": {"start_s": round(t, 3), "duration_s": d,
                                                    "rate_mbps": round(u * h["base"] - h["demand"], 3)}}
            return [{"at_s": round(t, 3), **burst}], _window(t, t + d, "udp", tgt, f"{tgt}:udp", list(h["clients"]),
                                                            "udp", u=u), d
        flows, d = rng.choice(TCP_FLOWS), rng.choice(TCP_D)
        ev = {"at_s": round(t, 3), "type": "flow", "kind": "tcp", "id": f"tcp-{tgt}-{k}", "route": h["route"],
              "duration_s": d, "cc": "cubic", "parallel": flows, "label": f"tcp x{flows} d={d} {tgt}"}
        return [ev], _window(t, t + d, "tcp", tgt, f"{tgt}:tcp", list(h["clients"]), "tcp", u=None,
                             tcp_flows=flows), d
    events, windows = indep_sequence(sorted(n["hops"]), seed, N_DURATION_S, make)
    udp: dict[str, list[dict]] = defaultdict(list)
    for e in [e for e in events if "burst" in e]:
        udp[e["route"]].append(e["burst"])
    events = [e for e in events if "burst" not in e]
    for route, bursts in sorted(udp.items()):
        events.append({"at_s": 0, "type": "bursts", "id": f"udp-{route}", "route": route,
                       "bursts": sorted(bursts, key=lambda b: b["start_s"])})
    return events, windows, N_DURATION_S


def load_trace(name: str) -> np.ndarray:
    return np.loadtxt(TRACES / f"{name}.csv", delimiter=",", skiprows=1, usecols=1)


def scale_trace(steps: np.ndarray, wire_mbps: float) -> tuple[float, float, bool]:
    """Multiplier so the segment's mean is TRACE_MEAN_X x the client's wire rate;
    when the time below the wire rate then falls outside TRACE_BELOW, the
    multiplier is re-set so 10 % of the steps are below (adjusted = True)."""
    mult = TRACE_MEAN_X * wire_mbps / float(steps.mean())
    below = float((steps * mult < wire_mbps).mean())
    adjusted = not TRACE_BELOW[0] <= below <= TRACE_BELOW[1]
    if adjusted:
        q = float(np.quantile(steps, 0.10))
        if q > 0:
            mult = wire_mbps / q
            below = float((steps * mult < wire_mbps).mean())
    return mult, below, adjusted


def trace_segment(name: str, offset_s: float, duration: float) -> np.ndarray:
    """duration / TRACE_STEP_S steps of the trace from offset_s, wrapped around when short."""
    steps = load_trace(name)
    k = int(round(duration / TRACE_STEP_S))
    start = int(round(offset_s / TRACE_STEP_S)) % len(steps)
    return steps[(start + np.arange(k)) % len(steps)]


def plan_trace(n: dict, seed: int) -> tuple[list[dict], list[dict], float, dict]:
    """N4: shared capacity drops (U(10, 15) s gaps, random default cells) plus
    every client's access link replaying a different scaled cellular trace in
    TRACE_STEP_S steps. Private truth windows: the trace below the wire rate."""
    rng = random.Random(seed)
    h = n["hops"][n["default"]]
    events, windows, t = [], [], dm.WARMUP_S
    while True:
        u, d = rng.choice(U_CAP), rng.choice(D_CAP)
        if t + d > N_DURATION_S - dm.TAIL_S:
            break
        events += _cap_event(n, n["default"], t, u, d, f"burst u={u} d={d}")
        windows.append(_window(t, t + d, "cap", n["default"], "shared", list(h["clients"]), u=u))
        t += d + rng.uniform(*dm.GAP_S)
    names = sorted(x for x in json.loads((TRACES / "index.json").read_text()) if not any(e in x for e in TRACE_EXCLUDE))
    rng.shuffle(names)
    meta = {}
    for i, c in enumerate(sorted(n["clients"])):
        name = names[i % len(names)]
        offset = round(rng.uniform(0, len(load_trace(name)) * TRACE_STEP_S), 1)
        seg = trace_segment(name, offset, N_DURATION_S)
        wire = n["clients"][c]
        mult, below, adjusted = scale_trace(seg, wire)
        cap = np.maximum(np.round(seg * mult, 3), TRACE_MIN_MBPS)
        link = {"from": n["uplink"][c], "to": c}
        prev = None
        for k, rate in enumerate(cap):
            if rate != prev:
                events.append({"at_s": round(k * TRACE_STEP_S, 3), "type": "link", **link,
                               "bandwidth_mbps": float(rate), "label": "trace"})
                prev = rate
        under = cap < wire
        gap = int(round(TRACE_MERGE_S / TRACE_STEP_S))
        k = 0
        while k < len(under):
            if under[k]:
                j = k
                while True:   # extend over the dip and any dip within TRACE_MERGE_S
                    nxt = next((i for i in range(j + 1, min(j + 1 + gap, len(under))) if under[i]), None)
                    if nxt is None:
                        break
                    j = nxt
                windows.append(_window(k * TRACE_STEP_S, (j + 1) * TRACE_STEP_S, "access", c, "private", [c], "trace"))
                k = j + 1
            else:
                k += 1
        meta[c] = {"trace": name, "offset_s": offset, "multiplier": round(mult, 4), "wire_mbps": round(wire, 3),
                   "mean_mbps": round(float(cap.mean()), 3), "below_fraction": round(below, 4),
                   "target_below": list(TRACE_BELOW), "adjusted": adjusted, "n_private_windows": int(sum(
                       1 for w in windows if w["target"] == c and w["cell"] == "private"))}
    events.sort(key=lambda e: e["at_s"])
    return events, flag_concurrent(sorted(windows, key=lambda w: w["start"])), N_DURATION_S, meta


def churn_sessions(clients: list[str], rng: random.Random, duration: float) -> dict[str, list[tuple[float, float | None]]]:
    """Per client: (join, leave) sessions; all start on at 0; on ~ exp(N5_ON),
    off ~ exp(N5_OFF) with floors; a session needs N5_ON floor seconds before the tail."""
    end = duration - dm.TAIL_S
    out = {}
    for c in clients:
        sessions, t = [], 0.0
        while True:
            leave = t + max(N5_ON[1], rng.expovariate(1 / N5_ON[0]))
            if leave > end - N5_ON[1]:
                sessions.append((t, None))
                break
            sessions.append((t, round(leave, 3)))
            t = round(leave + max(N5_OFF[1], rng.expovariate(1 / N5_OFF[0])), 3)
            if t > end - N5_ON[1]:
                break
        out[c] = sessions
    return out


def plan_churn(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    """N5: clients join and leave (sessions after the first run as <client>@<k>);
    shared capacity drops sized to the demand of the clients that are on;
    `expected` = the sessions on for the whole window."""
    rng = random.Random(seed)
    clients = sorted(n["clients"])
    sessions = churn_sessions(clients, rng, N5_DURATION_S)
    events = []
    for c, ss in sessions.items():
        for k, (join, leave) in enumerate(ss, start=1):
            if k > 1:
                events.append({"at_s": join, "type": "join", "subscriber": c})
            if leave is not None:
                events.append({"at_s": leave, "type": "leave", "subscriber": c})
    h = n["hops"][n["default"]]
    windows, t = [], dm.WARMUP_S
    while True:
        u, d = rng.choice(U_CAP), rng.choice(D_CAP)
        if t + d > N5_DURATION_S - dm.TAIL_S:
            break
        on = [(c, k) for c, ss in sessions.items() for k, (join, leave) in enumerate(ss, start=1)
              if join <= t and (leave is None or leave >= t + d)]
        demand = sum(n["clients"][c] for c, _ in on)
        if demand > 0:
            events += [{"at_s": round(t, 3), "type": "link", **h["link"], "bandwidth_mbps": round(demand / u, 3),
                        "label": f"burst u={u} d={d}"},
                       {"at_s": round(t + d, 3), "type": "link", **h["link"], "bandwidth_mbps": h["base"],
                        "label": "burst-end"}]
            windows.append(_window(t, t + d, "cap", n["default"], "shared",
                                   [Scenario.session_id(c, k) for c, k in on], u=u,
                                   demand_on_mbps=round(demand, 3), n_on=len(on)))
        t += d + rng.uniform(*dm.GAP_S)
    events.sort(key=lambda e: e["at_s"])
    return events, windows, N5_DURATION_S


def windows_from_events(events: list[dict], n: dict) -> list[dict]:
    """Stimulus windows of det_matrix-planned events: "burst u=.. d=.." link
    events until their "burst-end" (capacity drops, ramps above u = 1), UDP
    `bursts`, TCP `flow` events; constant flows from t = 0 (calmcbr), loss and
    delay steps and calm runs give none (negatives)."""
    hop_of = {(h["link"]["from"], h["link"]["to"]): name for name, h in n["hops"].items()}
    route_of = {h["route"]: name for name, h in n["hops"].items() if h.get("route")}
    many = len(n["hops"]) > 1
    windows = []
    links = [e for e in events if e["type"] == "link"]
    for i, e in enumerate(links):
        label = e.get("label") or ""
        if not label.startswith("burst u="):
            continue
        key = (e["from"], e["to"])
        if key not in hop_of:
            continue
        end = next((x["at_s"] for x in links[i + 1:] if (x["from"], x["to"]) == key and x.get("label") == "burst-end"),
                   None)
        if end is None:
            continue
        fields = dict(f.split("=") for f in label.split()[1:] if "=" in f)
        tgt = hop_of[key]
        windows.append(_window(e["at_s"], end, "cap", tgt, tgt if many else "cap", list(n["hops"][tgt]["clients"]),
                               u=float(fields.get("u", 0)), d=float(fields.get("d", 0))))
    for e in events:
        if e["type"] == "bursts" and e["route"] in route_of:
            tgt = route_of[e["route"]]
            for b in e["bursts"]:
                start = e["at_s"] + b["start_s"]
                windows.append(_window(start, start + b["duration_s"], "udp", tgt, f"{tgt}:udp" if many else "udp",
                                       list(n["hops"][tgt]["clients"]), "udp", rate_mbps=b["rate_mbps"]))
        elif e["type"] == "flow" and e.get("kind") == "tcp" and e["route"] in route_of:
            tgt = route_of[e["route"]]
            windows.append(_window(e["at_s"], e["at_s"] + e["duration_s"], "tcp", tgt, f"{tgt}:tcp" if many else "tcp",
                                   list(n["hops"][tgt]["clients"]), "tcp", u=None, tcp_flows=e.get("parallel", 1)))
    return sorted(windows, key=lambda w: (w["start"], w["target"]))


def plan_dm(name: str, n: dict, seed: int, topology: str) -> tuple[list[dict], list[dict], float]:
    """A det_matrix scenario as a campaign type: the same events the detector
    matrix ran, plus the windows the grouping truth needs. Event-benchmark names
    are generated (seed = rep); hand-written ones (ppbp) come from their YAML and
    get one whole-run window that the truth splits into the GT1 episodes of the
    hop (`from_truth`): the stimulus is continuous, congestion comes and goes."""
    if name in dm.BURST_SCENARIOS:
        events, duration = dm.burst_events(name, seed, topology)
        return events, windows_from_events(events, n), duration
    data = dm.scenario_data(name, topology, seed)
    events, duration = data["events"], float(data["duration_s"])
    h = n["hops"][n["default"]]
    windows = [_window(dm.WARMUP_S, duration - dm.TAIL_S, name, n["default"], name, list(h["clients"]), name,
                       from_truth=True)]
    return events, windows, duration


def plan_type(rtype: str, n: dict, seed: int, topology: str = "base") -> tuple[list[dict], list[dict], float, dict]:
    """(events, windows, duration_s, run metadata) of one run type."""
    meta: dict = {}
    if rtype in DM_TYPES:
        out = plan_dm(DM_TYPES[rtype], n, seed, topology)
    elif rtype in GAPS:
        out = plan_gaps(n, seed, GAPS[rtype])
    elif rtype in INDEP_MEANS:
        out = plan_indep(n, seed, INDEP_MEANS[rtype])
    elif rtype == "hier" or rtype in HIER_VARIANTS:
        out = plan_hier(n, seed)
    elif rtype == "depth":
        out = plan_depth(n, seed)
    elif rtype.startswith("part"):
        out = plan_part(n, seed, int(rtype[4:]) / 100)
    elif rtype == "revcross":
        out = plan_revcross(n, seed, mix=False)
    elif rtype == "revcrossmix":
        out = plan_revcross(n, seed, mix=True)
    elif rtype == "revasym" or rtype.startswith("revjit"):
        out = plan_revbursts(n, seed)
    elif rtype == "mixed":
        out = plan_mixed(n, seed)
    elif rtype in ("indep", "uneven", "uneven6"):
        out = plan_indep(n, seed)
    elif rtype == "cross":
        out = plan_cross(n, seed)
    elif rtype == "trace":
        *out, meta = plan_trace(n, seed)
        meta = {"traces": meta}
    elif rtype == "churn":
        out = plan_churn(n, seed)
    else:
        raise ValueError(rtype)
    events, windows, duration = out
    for w in windows:   # the stimulated router egress, for the GT1 truth (None: reverse-path stimuli)
        if w["target"] in n["hops"]:
            link = n["hops"][w["target"]]["link"]
            w["hop"] = f"{link['from']}->{link['to']}"
        elif w["target"] in n["uplink"]:
            w["hop"] = f"{n['uplink'][w['target']]}->{w['target']}"
        else:
            w["hop"] = None
    return events, flag_concurrent(windows), duration, meta


def apply_links(data: dict, rtype: str, n: dict) -> None:
    """Per-type changes to the base links (reverse delays / jitter / reverse capacity)."""
    shared = sorted(n["clients"])
    for link in data["links"]:
        if link["to"] in shared and link["from"] == n["uplink"][link["to"]]:
            rev = link.setdefault("reverse", {})
            if rtype == "revasym":
                rev["delay_ms"] = REV_ASYM_MS[shared.index(link["to"]) % len(REV_ASYM_MS)]
            elif rtype.startswith("revjit"):   # order kept since 2026-11-12 (earlier runs: ACK reordering)
                rev.update(jitter_ms=float(rtype[6:]), jitter_keep_order=True)
            if rtype.startswith("hierjit"):   # J1: forward jitter on the access link, after the shared bottleneck
                fwd = link.setdefault("forward", {})
                fwd.update(jitter_ms=float(rtype[7:]), jitter_distribution="normal", jitter_keep_order=True)
    if rtype in ("revcross", "revcrossmix"):
        data["links"].append({"from": REV_LINK[0], "to": REV_LINK[1], "reverse": {"bandwidth_mbps": REV_LINK_MBPS}})


def apply_aqm(data: dict, aqm: str, n: dict) -> None:
    """Set the AQM on every router, keeping the base file's queue limits (router
    wide and per egress) and the mixed variants' per-router / per-egress AQMs."""
    cap_to = {h["link"]["to"]: h["base"] for h in n["hops"].values()}

    def queue(name: str, limit: int | None, cap: float | None = None) -> dict:
        out = {"aqm": name, "queue_limit_packets": limit, **dm.AQMS[name]}
        if name == "red":   # thresholds at the egress's own capacity when known, else the smallest bottleneck's
            out.update(dm.red_thresholds({"hops": {"x": {"base": cap}}} if cap else n, limit))
        return out

    per_router, per_egress = MIXED.get(aqm, {}), MIXED_EGRESS.get(aqm, {})
    for rid, router in data["routers"].items():
        name = per_router.get(rid, aqm if aqm in dm.AQMS else "pfifo")
        limit = router.get("queue_limit_packets")
        base_egress = {peer: q.get("queue_limit_packets") for peer, q in (router.get("egress") or {}).items()}
        router.clear()
        router.update(queue(name, limit))
        egress = {peer: queue(name, lim, cap_to.get(peer)) for peer, lim in base_egress.items()}
        for peer, q in per_egress.get(rid, {}).items():
            egress[peer] = queue(q, base_egress.get(peer, limit), cap_to.get(peer))
        if egress:
            router["egress"] = egress


def topology_of(k: str, rtype: str) -> str:
    return TYPE_TOPOLOGY.get(rtype, CAMPAIGNS[k]["topology"])


def scenario_for(k: str, rtype: str, aqm: str, rep: int, kdir: Path) -> tuple[Path, Path, float]:
    """Write <kdir>/_gen/<run_id>.yaml and -windows.json; return (scenario, topology file, duration)."""
    topology = topology_of(k, rtype)
    topo_file, base_file, *_ = dm.TOPOLOGIES[topology]
    n = dm.topology_numbers(topology)
    if rtype in DM_TYPES:
        # det_matrix's own base: capacities per base_u, RTT scale, queue scale, editable loss.
        data = dm.scenario_data(DM_TYPES[rtype], topology, seed=rep)
    else:
        data = yaml.safe_load((ROOT / "configs" / "scenarios" / base_file).read_text())
    events, windows, duration, meta = plan_type(rtype, n, seed=rep, topology=topology)
    data["events"], data["duration_s"] = events, duration
    apply_links(data, rtype, n)
    apply_aqm(data, aqm, n)
    gen = kdir / "_gen"
    gen.mkdir(parents=True, exist_ok=True)
    rid = run_id(rtype, aqm, rep)
    out = gen / f"{rid}.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False))
    (gen / f"{rid}-windows.json").write_text(json.dumps(windows, indent=1))
    topo_path = ROOT / "configs" / "topologies" / topo_file
    if rtype in ("hiersamephase", "hierrandphase"):
        topo_path, meta = phase_topology(topo_path, rtype, rep, gen / f"{rid}-topology.yaml"), {**meta}
        meta["phases_ms"] = {sid: s_.get("phase_ms", 0) for sid, s_ in yaml.safe_load(topo_path.read_text())["subscribers"].items()}
    (gen / f"{rid}-plan.json").write_text(json.dumps({
        "campaign": k, "type": rtype, "topology": topology, "aqm": aqm, "rep": rep, "seed": rep,
        "duration_s": duration, "git": git_commit(), **meta}, indent=1))
    return out, topo_path, duration


def phase_topology(base: Path, rtype: str, rep: int, out: Path) -> Path:
    """J1 keyframe-phase variants of the split topology, written next to the scenario:
    hiersamephase  each b client takes the phase of the a client with the same index
                   (b1 = a1, ...), so both branches send their keyframes together;
    hierrandphase  every client draws its phase uniformly in [0, gop_ms) (seed = rep)."""
    topo = yaml.safe_load(base.read_text())
    subs = topo["subscribers"]
    if rtype == "hiersamephase":
        for sid in subs:
            twin = "a" + sid[1:] if sid.startswith("b") else None
            if twin in subs:
                subs[sid]["phase_ms"] = subs[twin].get("phase_ms", 0)
    else:
        gop = int(next(iter(topo["publishers"].values())).get("gop_ms", 1000))
        rng = random.Random(f"hierrandphase-{rep}")
        for sid in sorted(subs):
            subs[sid]["phase_ms"] = rng.randrange(gop)
    out.write_text(yaml.safe_dump(topo, sort_keys=False))
    return out


def run_id(rtype: str, aqm: str, rep: int) -> str:
    return f"grp-{rtype}-{aqm}-r{rep}"


def cells_of(k: str, reps: int | None = None) -> list[tuple[str, str, int]]:
    c = CAMPAIGNS[k]
    reps = reps or c["reps"]
    return [(rtype, aqm, rep) for rep in range(1, reps + 1) for aqm in c["aqms"] for rtype in c["types"]]


# ---------------------------------------------------------------- running

def git_commit() -> str:
    out = subprocess.run(["git", "-C", str(ROOT), "describe", "--always", "--dirty"], capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def run_campaign(k: str, kdir: Path, reps: int | None, skip_existing: bool, dry: bool, only: str = "") -> float:
    """Plan (and unless dry, run) every cell of K whose run id contains `only`;
    returns the planned seconds of emulation."""
    kdir.mkdir(parents=True, exist_ok=True)
    reps = reps or CAMPAIGNS[k]["reps"]
    man_path = kdir / "manifest.yaml"
    manifest = yaml.safe_load(man_path.read_text()) if man_path.exists() else {
        "campaign": k, "held_out": k in HELD_OUT, "started": datetime.datetime.now().isoformat(timespec="seconds"),
        "finished": None, "git": git_commit(), "reps": reps, "aqms": CAMPAIGNS[k]["aqms"],
        "types": CAMPAIGNS[k]["types"], "runs": {}}
    manifest["aqms"], manifest["types"] = CAMPAIGNS[k]["aqms"], CAMPAIGNS[k]["types"]   # cells added later (e.g. codel)
    total = 0.0
    for rtype, aqm, rep in cells_of(k, reps):
        rid = run_id(rtype, aqm, rep)
        if only and only not in rid:
            continue
        scenario, topo_file, duration = scenario_for(k, rtype, aqm, rep, kdir)
        load_scenario(scenario, load_topology(topo_file))   # schema check before anything runs
        total += duration
        if dry:
            continue
        run_dir = kdir / rid
        if skip_existing and run_finished(run_dir):
            manifest["runs"].setdefault(rid, "kept")
            continue
        if skip_existing:
            remove_partial_run(run_dir)
        print(f"== {k} {rid} ({duration:.0f} s)", flush=True)
        status = subprocess.run([sys.executable, "-m", "quiclab", "--runs-dir", str(kdir), "run", "-c", str(topo_file),
                                 "-s", str(scenario), "--run-id", rid], cwd=ROOT)
        if status.returncode != 0:
            print(f"!! {rid} failed ({status.returncode}); skipped", flush=True)
            manifest["runs"][rid] = f"failed ({status.returncode})"
        else:
            (run_dir / "grouping").mkdir(exist_ok=True)
            shutil.copy(kdir / "_gen" / f"{rid}-windows.json", run_dir / "grouping" / "windows.json")
            shutil.copy(kdir / "_gen" / f"{rid}-plan.json", run_dir / "grouping" / "plan.json")
            try:
                det_eval.score(run_dir)
            except (Exception, SystemExit) as e:  # best effort here; score again later with det_eval.py score
                print(f"   det_eval.score failed on {rid}: {e!r}", flush=True)
            for mod in (gt1, gt2, gt3):   # router / demand / per-client truths (<run>/truth/), as det_matrix does
                try:
                    mod.score(run_dir, mod.Params())
                except Exception as e:
                    print(f"   {mod.__name__}.score failed on {rid}: {e!r}", flush=True)
            try:
                print("   " + infra_line(infra_check(run_dir)), flush=True)
            except Exception as e:
                print(f"   infra check failed on {rid}: {e!r}", flush=True)
            manifest["runs"][rid] = f"done {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}"
        man_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    if not dry:
        manifest["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
        man_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return total


# ---------------------------------------------------------------- infrastructure check

def link_lag(rows: list[dict], label: str | None = None) -> dict | None:
    """applied_s - at_s of the applied link events (optionally one label): did the
    scenario runner keep up? n, p50, p99, max in seconds."""
    lags = sorted(float(r["applied_s"]) - float(r["at_s"]) for r in rows
                  if r["event"] == "link" and r.get("status") == "applied" and r.get("at_s") not in ("", None)
                  and (label is None or r.get("label") == label))
    if not lags:
        return None
    return {"n": len(lags), "p50": round(lags[len(lags) // 2], 4), "p99": round(lags[int(0.99 * (len(lags) - 1))], 4),
            "max": round(lags[-1], 4)}


def pin_check(run: det_eval.Run) -> dict | None:
    """Per-flow router counters (fq_codel / cake egresses, docs/per-flow-queue-counters.md):
    every client behind a recorded egress shows up as its pinned class at least
    once, and the egress transmitted bytes (a misclassification would drop
    silently). None when the run recorded no per-flow classes."""
    out = {"egresses": 0, "missing": [], "silent": []}
    for hop, csv in gt1.router_egresses(run):
        flows = csv.with_name(csv.stem + "-flows.csv")
        rows = det_eval.rows(flows) if flows.exists() else []
        if not rows:   # the file is written for every client-facing egress; rows only under fq_codel / cake
            continue
        out["egresses"] += 1
        hop_id = f"{hop[0]}->{hop[1]}"
        subs = run.topology["subscribers"]
        # pins are per subscriber address: a re-joined session <sid>_<n> shows up as its subscriber
        behind = {Scenario.session_of(s, subs)[0] for s in subs if hop in det_eval.path_hops(run, run.pub, s)}
        seen = {r["flow"] for r in rows if r["flow"]}
        out["missing"] += [f"{hop_id}:{s}" for s in sorted(behind - seen)]
        if behind and not sum(int(r["transmitted_bytes"]) for r in det_eval.rows(csv)):   # a cross-traffic-only
            out["silent"].append(hop_id)                                                   # egress may idle
    return out if out["egresses"] else None


def infra_check(run_dir: Path) -> dict:
    """Did the run do what the plan says, without looking at any grouping result:
    finished, clients / sessions present with sender files, event errors, link
    event lag (trace replay keeps its 200 ms steps?), windows in which the OWD
    oracle saw the expected clients congested, clients never hit, control
    client congestion. Written to <run>/grouping/infra.json."""
    run = ga.load_run(run_dir)
    rows = run.events
    truth = ga.truth_of(run)
    windows = json.loads((run_dir / "grouping" / "windows.json").read_text()) \
        if (run_dir / "grouping" / "windows.json").exists() else []
    bursts = truth["bursts"]
    shared = [b for b in bursts if len(b["expected"]) >= 2]
    private = [b for b in bursts if len(b["expected"]) == 1]
    expected_any = {c for b in bursts for c in b["expected"]}
    hit_any = {c for b in bursts for c in b["hit"]}
    errors = [{k: r.get(k) for k in ("event", "at_s", "target", "error")} for r in rows if r.get("error")]
    missing = [s for s in run.subs for suffix in ("acks", "owd") if not run.sender_file(s, suffix).exists()]
    planned_sessions = sorted(f for f in ga.sessions_of(run) if ga.is_later_session(f, run.topology["subscribers"]))
    out = {"run": run_dir.name, "finished": run_finished(run_dir), "duration_s": run.duration,
           "clients": len(run.subs), "sessions_planned": len(planned_sessions),
           "sessions_found": len([f for f in run.subs if ga.is_later_session(f, run.topology["subscribers"])]),
           "sender_files_missing": sorted(set(missing)),
           "errors": len(errors), "first_errors": errors[:5],
           "link_events": sum(r["event"] == "link" for r in rows),
           "lag_all": link_lag(rows), "lag_trace": link_lag(rows, "trace"),
           "windows": len(windows), "windows_hit": sum(bool(b["hit"]) for b in bursts),
           "shared_windows": len(shared), "shared_hit2": sum(len(b["hit"]) >= 2 for b in shared),
           "shared_hit_all": sum(set(b["hit"]) == set(b["expected"]) for b in shared),
           "private_windows": len(private), "private_hit": sum(bool(b["hit"]) for b in private),
           "clients_never_hit": sorted(expected_any - hit_any),
           "ctrl_congested_bins": int(len(ga.congested_bins(run, ga.CTRL))) if ga.CTRL in run.subs else None,
           "pins": pin_check(run)}
    (run_dir / "grouping").mkdir(exist_ok=True)
    (run_dir / "grouping" / "infra.json").write_text(json.dumps(out, indent=1))
    return out


def infra_line(i: dict) -> str:
    lag = i["lag_trace"] or i["lag_all"] or {}
    flags = []
    if not i["finished"]:
        flags.append("UNFINISHED")
    if i["errors"]:
        flags.append(f"{i['errors']} event errors")
    if i["sender_files_missing"]:
        flags.append(f"missing files {i['sender_files_missing']}")
    if i["lag_trace"] and i["lag_trace"]["max"] > TRACE_LAG_MAX_S:
        flags.append(f"trace tc apply delay p99/max {i['lag_trace']['p99']}/{i['lag_trace']['max']} s > {TRACE_LAG_MAX_S}")
    if i["sessions_planned"] != i["sessions_found"]:
        flags.append(f"sessions {i['sessions_found']}/{i['sessions_planned']}")
    if i["clients_never_hit"]:
        flags.append(f"never hit {i['clients_never_hit']}")
    pins = i.get("pins")
    if pins and pins["missing"]:
        flags.append(f"pinned flow never seen {pins['missing']}")
    if pins and pins["silent"]:
        flags.append(f"fq/cake egress transmitted nothing {pins['silent']}")
    return (f"{i['run']}: clients {i['clients']}, windows hit {i['windows_hit']}/{i['windows']}, shared >=2 hit "
            f"{i['shared_hit2']}/{i['shared_windows']}, private hit {i['private_hit']}/{i['private_windows']}, "
            f"link events {i['link_events']} tc apply delay (applied - planned) p99/max {lag.get('p99', '-')}/{lag.get('max', '-')} s, ctrl congested "
            f"bins {i['ctrl_congested_bins']}" + (" | " + "; ".join(flags) if flags else " | ok"))


def pin_cell(pins: dict | None) -> str:
    return "-" if not pins else f"{pins['egresses']}; {pins['missing'] or 'none'}; {pins['silent'] or 'none'}"


def infra_report(k: str, kdir: Path) -> None:
    """<kdir>/infra.md: one line per finished run (no grouping score)."""
    runs = sorted(p for p in kdir.glob("grp-*") if (p / "events.csv").exists())
    checks = []
    for r in runs:
        try:
            checks.append(infra_check(r))
        except Exception as e:
            checks.append({"run": r.name, "error": repr(e)})
    lines = [f"# Infrastructure check {k}", "", f"{len(runs)} runs, generated {datetime.datetime.now():%Y-%m-%d %H:%M}. "
             "No grouping result is read here" + (" (held-out set: scored only with --score-held-out after the rule freeze)."
                                                  if k in HELD_OUT else "."), "",
             "| run | finished | clients | sessions found/planned | errors | link events | tc apply delay p99 / max s (applied - planned; trace if any) | "
             "windows hit | shared >=2 hit / all hit | private hit | never hit | ctrl congested bins | missing files "
             "| per-flow pins (egresses; missing; silent) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in checks:
        if "error" in i:
            lines.append(f"| {i['run']} | check failed: {i['error']} | | | | | | | | | | |")
            continue
        lag = i["lag_trace"] or i["lag_all"] or {}
        lines.append(f"| {i['run']} | {i['finished']} | {i['clients']} | {i['sessions_found']}/{i['sessions_planned']} "
                     f"| {i['errors']} | {i['link_events']} | {lag.get('p99', '-')} / {lag.get('max', '-')} "
                     f"| {i['windows_hit']}/{i['windows']} | {i['shared_hit2']}/{i['shared_hit_all']}/{i['shared_windows']} "
                     f"| {i['private_hit']}/{i['private_windows']} | {i['clients_never_hit']} | {i['ctrl_congested_bins']} "
                     f"| {i['sender_files_missing']} | {pin_cell(i.get('pins'))} |")
    (kdir / "infra.md").write_text("\n".join(lines) + "\n")
    print(f"infra: {kdir / 'infra.md'}", flush=True)
    for i in checks:
        if "error" not in i:
            print("  " + infra_line(i), flush=True)


# ---------------------------------------------------------------- reporting

def ecg_dir(src: str, tag: str = "") -> str:
    """<run>/grouping[-<tag>][-<src>]: the adapter's output dir for one onset source."""
    return "grouping" + (f"-{tag}" if tag else "") + ("" if src == "shadow" else f"-{src}")


def score_run(run_dir: Path, cfg: Config, tag: str = "", sources: tuple[str, ...] = ONSET_SOURCES,
              with_baselines: bool = True) -> dict:
    out = {"run": run_dir.name, "ecg": {}}
    windows_json = run_dir / "grouping" / "windows.json"
    negative = windows_json.exists() and not json.loads(windows_json.read_text())
    for src in sources:
        if src == "truth" and negative:   # truth onsets come from the stimulus windows; a negative run has none
            out["ecg"][src] = {"skipped": "negative run: no stimulus window, no truth onsets"}
            continue
        a = Namespace(out=ecg_dir(src, tag), onsets=src, backdate_max=1.0, backdate_qd_ms=10.0,
                      warmup=det_eval.WARMUP_S, spread_only=False)
        try:
            out["ecg"][src] = ga.process(run_dir, cfg, a)
        except SystemExit as e:  # shadow onsets without the replay binary: the other sources still count
            out["ecg"][src] = {"error": str(e)}
        except Exception as e:
            out["ecg"][src] = {"error": repr(e)}
            traceback.print_exc()
    if not with_baselines:
        return out
    try:
        out["baselines"] = gb.process(run_dir, Namespace(methods=gb.METHODS, owd="oracle", dcw_th=0.8,
                                                         ecg=[ecg_dir(s, tag) for s in sources],
                                                         out_name=f"baselines{'-' + tag if tag else ''}.json"))
    except Exception as e:
        out["baselines"] = {"error": repr(e)}
        traceback.print_exc()
    return out


def case_matrix(run_dir: Path, src: str, tag: str = "") -> Counter:
    """(cell, case) counts: every ECG event mapped to the stimulus window whose
    start is nearest (within 3 s); events without one count under 'none'."""
    m_path = run_dir / ecg_dir(src, tag) / "metrics.json"
    w_path = run_dir / "grouping" / "windows.json"
    if not m_path.exists() or not w_path.exists():
        return Counter()
    m, windows = json.loads(m_path.read_text()), json.loads(w_path.read_text())
    out = Counter()
    for e in m["events"]:
        near = min(windows, key=lambda w: abs(w["start"] - e["t0"]), default=None)
        cell = near["cell"] if near and abs(near["start"] - e["t0"]) <= 3.0 else "none"
        if near is not None and cell != "none" and near.get("concurrent"):
            cell += " (concurrent)"
        out[(cell, e["case"])] += 1
    return out


def fmt(v) -> str:
    return "-" if v is None else f"{v:.2f}" if isinstance(v, float) else str(v)


def med(vals: list) -> float | None:
    vals = [v for v in vals if isinstance(v, (int, float)) and v is not None]
    return statistics.median(vals) if vals else None


def cell_of(run_name: str) -> tuple[str, str]:
    parts = run_name.split("-")
    return parts[1], "-".join(parts[2:-1])


def shadow_of(r: dict, key: str, src: str = PRIMARY):
    return r["ecg"].get(src, {}).get(key)


def compare_cells(results: list[dict], old_dir: Path | None, tol: float = 0.05) -> dict[tuple[str, str], str]:
    """Per (type, aqm): 'worse' when the median shadow precision or recall fell by
    more than tol against the old campaign's results(-v12).json, else ''."""
    if old_dir is None:
        return {}
    old_file = next((f for f in (old_dir / "results-v12.json", old_dir / "results.json") if f.exists()), None)
    if old_file is None:
        return {}
    old = defaultdict(list)
    for r in json.loads(old_file.read_text()):
        old[cell_of(r["run"])].append(r)
    new = defaultdict(list)
    for r in results:
        new[cell_of(r["run"])].append(r)
    out = {}
    for cell, rs in new.items():
        if cell not in old:
            continue
        flags = []
        for key in ("precision", "recall"):
            a, b = med([shadow_of(r, key) for r in rs]), med([shadow_of(r, key) for r in old[cell]])
            if a is not None and b is not None and a < b - tol:
                flags.append(f"{key} {b:.2f} -> {a:.2f}")
        out[cell] = "worse: " + ", ".join(flags) if flags else "same or better"
    return out


def criteria(k: str, results: list[dict], src: str = PRIMARY) -> list[str]:
    """Pass criteria of grouping/campaign-v2-spec.md section 7 on one onset source
    (PRIMARY = v2-owd; the COMPARE sources are printed as comparisons)."""
    def shadow_of(r, key, s=src):   # noqa: F811 - the source is fixed for this block
        return r["ecg"].get(s, {}).get(key)
    by_cell = defaultdict(list)
    for r in results:
        by_cell[cell_of(r["run"])].append(r)
    lines = []

    def runs(aqms):
        return [(cell, r) for cell, rs in sorted(by_cell.items()) if cell[1] in aqms for r in rs]

    def check(name, pairs, ok_fn, detail_fn):
        bad = [(cell, r["run"], detail_fn(r)) for cell, r in pairs if not ok_fn(r)]
        verdict = "PASS" if pairs and not bad else ("no runs" if not pairs else "FAIL")
        lines.append(f"- {verdict}: {name} ({len(pairs) - len(bad)}/{len(pairs)} runs)")
        lines.extend(f"  - {run}: {detail}" for _, run, detail in bad)

    def pr(r):
        return f"P={fmt(shadow_of(r, 'precision'))} R={fmt(shadow_of(r, 'recall'))} cov={fmt(shadow_of(r, 'coverage'))} " \
               f"fp={shadow_of(r, 'fp')} tree_correct={shadow_of(r, 'tree_correct')} ctrl_grouped={shadow_of(r, 'ctrl_grouped')}"

    def ge(r, key, x):
        v = shadow_of(r, key)
        return v is not None and v >= x
    if k in HELD_OUT:
        lines.append(f"## Pass criteria ({k}, {src} source{'' if src == PRIMARY else ', comparison'}; spec section 7)")
        lines.append("")
    if k == "N1":
        fifo = runs(("pfifo", "pie"))
        check("pfifo/pie: zero confirmed cross-branch pairs, both leaves correct, P and R >= 0.95", fifo,
              lambda r: shadow_of(r, "fp") == 0 and shadow_of(r, "tree_correct") is True
              and ge(r, "precision", 0.95) and ge(r, "recall", 0.95), pr)
        lines.append("- fq_codel (no threshold): confirmed cross-branch pairs per run: "
                     + ", ".join(f"{r['run']}={shadow_of(r, 'fp')}" for _, r in runs(("fq_codel",))))
    elif k == "N2":
        check("pfifo/pie: three groups correct, P and R >= 0.95, coverage >= 0.7, sub-ctrl ungrouped",
              runs(("pfifo", "pie")),
              lambda r: shadow_of(r, "tree_correct") is True and ge(r, "precision", 0.95) and ge(r, "recall", 0.95)
              and ge(r, "coverage", 0.7) and shadow_of(r, "ctrl_grouped") is False, pr)
    elif k == "N3":
        check("pfifo: final tree = the split topology's two leaves (udp and tcp windows in the case matrix)",
              runs(("pfifo",)), lambda r: shadow_of(r, "tree_correct") is True, pr)
    elif k == "N4":
        def solo_share(r):   # among private windows that produced an event; silent ones are reported, not judged
            pw = shadow_of(r, "private_windows") or {}
            return pw["solo"] / (pw["solo"] + pw["grouped"]) if pw.get("solo", 0) + pw.get("grouped", 0) else None
        check("shared group P and R >= 0.9, >= 90 % of private windows with an event end as solo events, sub-ctrl ungrouped",
              runs(("pfifo", "fq_codel")),
              lambda r: ge(r, "precision", 0.9) and ge(r, "recall", 0.9) and (solo_share(r) or 0) >= 0.9
              and shadow_of(r, "ctrl_grouped") is False,
              lambda r: pr(r) + f" private_solo={fmt(solo_share(r))} private={shadow_of(r, 'private_windows')}")
    elif k == "N5":
        check("sub-ctrl ungrouped; no session a confirmed member while off", runs(("pfifo", "fq_codel")),
              lambda r: shadow_of(r, "ctrl_grouped") is False and (shadow_of(r, "off_membership") or 0) == 0,
              lambda r: pr(r) + f" off_membership={shadow_of(r, 'off_membership')}")
        for _, r in runs(("pfifo", "fq_codel")):
            st = shadow_of(r, "session_stats") or {}
            lines.append(f"- {r['run']}: sessions with >= 3 events {st.get('sessions_3_events')}, of them members "
                         f"{st.get('members')}; membership event index p50 {fmt(st.get('event_index_p50'))}")
    elif k == "G0":
        # No shared bottleneck: every pair is DIFFERENT, so a confirmed wrong pair is any pair reported
        # SAME (sub-ctrl included). Single-member leaves group nobody (user decision 2026-11-11).
        check("negatives: no confirmed wrong pair (false SAME pairs = 0, sub-ctrl included)",
              runs(tuple(CAMPAIGNS["G0"]["aqms"])), lambda r: shadow_of(r, "fp") == 0, pr)
    elif k in GROUPS["micro"]:
        check("microbenchmark: one leaf = the four clients, sub-ctrl ungrouped (report only on fq-like AQMs)",
              runs(("pfifo", "red", "pie")),
              lambda r: shadow_of(r, "tree_correct") is True and shadow_of(r, "ctrl_grouped") is False, pr)
    elif k in CAMPAIGNS:
        lines.append(f"## {k}: development set, report only (cells worse than the previous campaign are flagged "
                     "in the first table when --compare is given)")
    if src == PRIMARY:
        lines.append("- All fq_codel cells: no pass threshold; scored against both truths (leaf and link columns).")
    return lines


def acks_reordered(run_dir: Path) -> bool:
    """A run whose reverse (ACK) path had netem jitter without order keeping."""
    sc = yaml.safe_load((run_dir / "scenario.yaml").read_text()) if (run_dir / "scenario.yaml").exists() else {}
    return any((l.get("reverse") or {}).get("jitter_ms") and not (l.get("reverse") or {}).get("jitter_keep_order")
               for l in sc.get("links", []))


def report(k: str, kdir: Path, cfg: Config, over: dict | None = None, tag: str = "",
           compare: Path | None = None) -> None:
    sfx = f"-{tag}" if tag else ""
    sources = ONSET_SOURCES
    with_baselines = CAMPAIGNS.get(k, {}).get("baselines", True)
    runs = sorted(p for p in kdir.glob("grp-*") if run_finished(p))
    results = [score_run(r, cfg, tag, sources, with_baselines) for r in runs]
    (kdir / f"results{sfx}.json").write_text(json.dumps(results, indent=1, default=str))
    scoring = {"scored": datetime.datetime.now().isoformat(timespec="seconds"), "engine_git": git_commit(),
               "config": cfg.to_dict(), "sources": sources, "primary": PRIMARY}
    (kdir / f"scoring{sfx}.json").write_text(json.dumps(scoring, indent=1, default=str))
    worse = compare_cells(results, compare / k if compare else None)
    lines = [f"# Grouping campaign {k}" + (f" ({tag})" if tag else "") + (" — held-out" if k in HELD_OUT else
                                                                          " — development set"), "",
             f"{len(runs)} runs, engine overrides {over if over is not None else ENGINE_SET}, engine tree "
             f"`{scoring['engine_git']}` at scoring time (the runs' plan.json holds the planning tree), "
             f"onset sources {', '.join(sources)} (primary {PRIMARY}; comparison {', '.join(COMPARE)}), truth = stimulus "
             f"windows x OWD oracle x plan (pairs_leaf; link = pairs). Generated {datetime.datetime.now():%Y-%m-%d %H:%M}."
             + ("" if with_baselines else " No SBD baseline columns: the baselines need one common span over "
                                         "long-lived flows and cannot follow sessions."), ""]
    reordered = sorted(r.name for r in runs if acks_reordered(r))
    if reordered:
        lines += [f"Note: {len(reordered)} reverse-jitter run(s) with ACK reordering (plain netem on the ACK path, "
                  "before the order-keeping method; grouping/README.md, \"Reverse jitter runs\"): "
                  + ", ".join(reordered), ""]
    lines += criteria(k, results) + [""]
    if k in HELD_OUT:
        for src in COMPARE:
            lines += criteria(k, results, src) + [""]
    # 1. per type x AQM: medians over reps
    lines += [f"## Final grouping per type x AQM (median over reps; leaf precision / recall, t_correct s; "
              f"cov = share of pairs decided per source; link = {PRIMARY} P / R against 'share a link'; GT3 = {PRIMARY} "
              f"leaf P / R against the per-client OWD truth (fq_codel: the router truth counts every expected client); "
              f"cross = confirmed cross-group pairs ({PRIMARY} fp, median / max); ctrl = runs with sub-ctrl in a leaf; "
              "tree = runs whose confirmed leaves equal the truth groups; ev->member = median events a flow took "
              "part in before it was reported a member)", "",
              "| type | aqm | n | " + " | ".join(f"ECG {s}" for s in sources)
              + f" | cov | link P / R | GT3 P / R | cross | ctrl | tree | ev->member | DCW | rmcatSBD | dcSBD | spread p50/p90 ms ({PRIMARY}) |"
              + (" compare |" if worse else ""),
              "|---|---|---|" + "---|" * len(sources) + "---|---|---|---|---|---|---|---|---|---|---|" + ("---|" if worse else "")]
    by_cell = defaultdict(list)
    for r in results:
        by_cell[cell_of(r["run"])].append(r)

    def cell_str(rs, name):
        P = med([((r.get("baselines") or {}).get("methods") or {}).get(name, {}).get("final", {}).get("vs_leaf", {})
                 .get("precision") for r in rs])
        R = med([((r.get("baselines") or {}).get("methods") or {}).get(name, {}).get("final", {}).get("vs_leaf", {})
                 .get("recall") for r in rs])
        T = med([((r.get("baselines") or {}).get("methods") or {}).get(name, {}).get("t_correct") for r in rs])
        return f"{fmt(P)} / {fmt(R)}, {fmt(T)}"
    for (rtype, aqm), rs in sorted(by_cell.items()):
        sp = [shadow_of(r, "spread_onset_ms") for r in rs]
        sp = [x for x in sp if x]
        spread = f"{med([x['p50'] for x in sp]):.0f} / {med([x['p90'] for x in sp]):.0f}" if sp else "-"
        cov = " / ".join(fmt(med([shadow_of(r, "coverage", src) for r in rs])) for src in sources)
        link = f"{fmt(med([shadow_of(r, 'precision_link') for r in rs]))} / {fmt(med([shadow_of(r, 'recall_link') for r in rs]))}"
        gt3 = f"{fmt(med([shadow_of(r, 'precision_gt3') for r in rs]))} / {fmt(med([shadow_of(r, 'recall_gt3') for r in rs]))}"
        fps = [shadow_of(r, "fp") for r in rs if shadow_of(r, "fp") is not None]
        cross = f"{med(fps)} / {max(fps)}" if fps else "-"
        ctrl = f"{sum(shadow_of(r, 'ctrl_grouped') is True for r in rs)}/{len(rs)}"
        tree = f"{sum(shadow_of(r, 'tree_correct') is True for r in rs)}/{len(rs)}"
        evm = med([v for r in rs for v in (shadow_of(r, "membership_events") or {}).values()])
        lines.append(f"| {rtype} | {aqm} | {len(rs)} | "
                     + " | ".join(cell_str(rs, f"ecg:{ecg_dir(src, tag)}") for src in sources)
                     + f" | {cov} | {link} | {gt3} | {cross} | {ctrl} | {tree} | {fmt(evm)} | "
                     + " | ".join(cell_str(rs, n) if with_baselines else "n/a" for n in ("dcw", "rmcat_sbd", "dc_sbd"))
                     + f" | {spread} |" + (f" {worse.get((rtype, aqm), '-')} |" if worse else ""))
    # 2. case matrix per type and source (concurrent windows as their own rows)
    for src in sources:
        lines += ["", f"## ECG event cases per stimulus cell ({src} onsets, summed over AQMs and reps; "
                      "'(concurrent)' = windows overlapping another bottleneck's)", ""]
        per_type = defaultdict(Counter)
        for r in runs:
            per_type[cell_of(r.name)[0]] += case_matrix(r, src, tag)
        cases = sorted({c for cm in per_type.values() for _, c in cm})
        lines += ["| type | cell | " + " | ".join(cases) + " |", "|---|---|" + "---|" * len(cases)]
        for rtype, cm in sorted(per_type.items()):
            for cell in sorted({c for c, _ in cm}):
                lines.append(f"| {rtype} | {cell} | " + " | ".join(str(cm[(cell, c)]) for c in cases) + " |")
    # 3. per run
    lines += ["", "## Per run", "", "| run | source | cases | leaf P / R | link P / R | cov | fp | ctrl | tree | leaves | "
              "ev->member | spread p50/p90 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        for src in sources:
            s_ = r["ecg"].get(src, {})
            if "error" in s_ or "skipped" in s_:
                lines.append(f"| {r['run']} | {src} | {'error: ' + s_['error'] if 'error' in s_ else s_['skipped']} "
                             "| | | | | | | | | |")
                continue
            sp = s_.get("spread_onset_ms")
            lines.append(f"| {r['run']} | {src} | {s_.get('cases')} | {fmt(s_.get('precision'))} / {fmt(s_.get('recall'))} "
                         f"| {fmt(s_.get('precision_link'))} / {fmt(s_.get('recall_link'))} | {fmt(s_.get('coverage'))} "
                         f"| {s_.get('fp')} | {s_.get('ctrl_grouped')} | {s_.get('tree_correct')} | {s_.get('leaves')} "
                         f"| {s_.get('membership_events')} | {f'{sp['p50']:.0f} / {sp['p90']:.0f}' if sp else '-'} |")
    # 4. end to end: the same windows seen by the detector and the grouping (primary source)
    e2e = [r for r in (e2e_score.score_run(p, PRIMARY, tag) for p in runs) if r]
    lines += ["", f"## End to end ({PRIMARY}; shared windows hit by GT1: detector alarms of the members, ECG case, "
                  "group time; alarm precision single vs group-confirmed; negatives: FA and false groups per minute)", ""]
    lines += e2e_score.table(e2e, lambda r: " / ".join(cell_of(r["run"])))
    # 5. detector side (det_eval's own tables, model truth), per type x AQM
    lines += ["", "## Detector (det_eval score, model truth; the GT1/GT2/GT3 tables are the detector pipeline's)", ""]
    for (rtype, aqm), rs in sorted(by_cell.items()):
        dirs = [kdir / r["run"] for r in rs if (kdir / r["run"] / "detector" / "detections.csv").exists()]
        if not dirs:
            continue
        try:
            rows_ = det_eval.summarize(dirs, ["shadow", "gcc", "bbr"])
        except Exception as e:   # a scenario the detector tables do not cover
            lines.append(f"- {rtype} / {aqm}: {e!r}")
            continue
        lines += [f"### {rtype} / {aqm} ({len(dirs)} runs, {rows_[0]['onsets']} onsets)", "",
                  "| detector | " + " | ".join(k for k in rows_[0] if k not in {"detector", "onsets"}) + " |",
                  "|---" * (len(rows_[0]) - 1) + "|"]
        lines += ["| " + " | ".join("-" if v is None else str(v) for k, v in row.items() if k != "onsets") + " |"
                  for row in rows_]
        lines.append("")
    (kdir / f"report{sfx}.md").write_text("\n".join(lines) + "\n")
    print(f"report: {kdir / f'report{sfx}.md'}", flush=True)


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ks", default="N1,N2,K1,K2,K3,K5,K6,C1,N3,N4,N5,G0,M1,M2,M3,M4,M5,M6",
                    help="campaigns in run order (core, then negatives, then microbenchmarks)")
    ap.add_argument("--reps", type=int, default=None, help="override the campaigns' own rep counts (K 3, K6 and N 5)")
    ap.add_argument("--compare", type=Path, help="older campaign dir: flag cells whose primary-source P/R got worse")
    ap.add_argument("--only", default="", help="run only the cells whose run id contains this text (smoke runs)")
    ap.add_argument("--score-held-out", action="store_true",
                    help="produce grouping reports for N1-N5 (only after the rule freeze; until then they get infra.md)")
    ap.add_argument("--campaign", type=Path, help="existing .runs/<dir> to resume or report")
    ap.add_argument("--name", default="grp")
    ap.add_argument("--plan", action="store_true", help="write the YAMLs and the budget, run nothing")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE", help="engine overrides for the reports")
    ap.add_argument("--v12", action="store_true", help="(default since 2026-11-10) apply Config.V12 on top of --set")
    ap.add_argument("--v11", action="store_true", help="apply Config.V11 (brief v1.1 rules) for reproduction")
    ap.add_argument("--tag", default="", help="suffix for the output dirs and report (grouping-<tag>, report-<tag>.md)")
    a = ap.parse_args(argv)
    over = dict(ENGINE_SET)
    if a.v12:
        over.update(Config.V12)
    if a.v11:
        over.update(Config.V11)
    for it in a.set:
        key, v = it.split("=", 1)
        over[key] = json.loads(v)
    cfg = Config.from_dict(over)
    ks = a.ks.split(",")
    unknown = [k for k in ks if k not in CAMPAIGNS]
    if unknown:
        sys.exit(f"unknown campaigns {unknown}; known: {sorted(CAMPAIGNS)}")
    if not a.plan and not a.report_only and not det_eval.REPLAY.exists():
        print(f"WARNING: {det_eval.REPLAY} missing: no shadow onsets. The owd and truth sources still work; "
              "afterwards run det_eval.py score on the runs, then --report-only.", flush=True)
    if a.plan and not a.campaign:   # a budget check leaves no campaign dir behind (it only writes _gen files)
        campaign = Path(tempfile.mkdtemp(prefix="grp-plan-"))
        atexit.register(shutil.rmtree, campaign, True)
    else:
        campaign = a.campaign or RUNS / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_{a.name}"
    campaign.mkdir(parents=True, exist_ok=True)
    print(f"campaign: {campaign}", flush=True)
    budget = 0.0
    for k in ks:
        kdir = campaign / k
        scorable = k not in HELD_OUT or a.score_held_out
        if a.report_only:
            infra_report(k, kdir)
            if scorable:
                report(k, kdir, cfg, over, a.tag, a.compare)
            else:
                print(f"{k}: held-out, grouping not scored (pass --score-held-out after the rule freeze)", flush=True)
            continue
        secs = run_campaign(k, kdir, a.reps, a.skip_existing, dry=a.plan, only=a.only)
        budget += secs
        n = len([c for c in cells_of(k, a.reps) if not a.only or a.only in run_id(*c)])
        print(f"{k}: {n} runs, {secs / 3600:.1f} h of emulation (+ ~1 min setup each)", flush=True)
        if not a.plan:
            infra_report(k, kdir)
            if scorable:
                report(k, kdir, cfg, over, a.tag, a.compare)
            else:
                print(f"{k}: held-out, grouping not scored (pass --score-held-out after the rule freeze)", flush=True)
    if a.plan:
        print(f"total: {budget / 3600:.1f} h of emulation")


if __name__ == "__main__":
    main(sys.argv[1:])
