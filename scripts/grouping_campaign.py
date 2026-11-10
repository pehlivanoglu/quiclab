#!/usr/bin/env python3
"""Grouping campaigns K1-K6: plan the runs, run them one after another, and
write each campaign's grouping report as soon as its last run finishes.

    python3 scripts/grouping_campaign.py --plan                       # write the YAMLs, print the budget, run nothing
    python3 scripts/grouping_campaign.py --ks K1,K2,K3,K5,K6 --reps 3   # the whole thing (tmux)
    python3 scripts/grouping_campaign.py --campaign .runs/<dir> --skip-existing   # resume
    python3 scripts/grouping_campaign.py --campaign .runs/<dir> --report-only     # (re)score only

Grouping-only tooling: the shadow detector stays frozen (det_eval TUNED) and
BBR is the only congestion control. It reuses det_matrix's topology numbers
and AQM table (import only) and the quiclab CLI; it writes
.runs/<ts>_grp/<K>/{_gen, grp-<type>-<aqm>-r<rep>/, manifest.yaml, report.md}.
After every run det_eval.score is attempted (the detector's own report, best
effort) and the run's stimulus windows are copied to <run>/grouping/windows.json:
grouping truth = a client is hit in a window when the OWD oracle shows a
standing queue there AND the plan expected that client (two simultaneous
events on different links cannot be told apart by the oracle alone).

Campaigns (rep = seed, same seed on every AQM; calm u ~0.65; capacity drops
unless said otherwise; gaps U(10, 15) s):
  K1 hier   split topology: cells u {1.3, 2.0} x d {1, 2, 4} x targets
            up | a | b | a+b (same instant) | a+b@0.5 | a+b@1 | a+b@2 (b later)
            | a+up (serial). AQMs: 4 uniform + mixa (r1 pfifo, r2 fq_codel)
            + mixb (r1 fq_codel, r2 pfifo) + mixab (r1 pfifo; branches differ
            on r2: switch-a pfifo, switch-b fq_codel). Hierarchy, false GLOBAL
            on simultaneous independent events, delta_max / hold on offsets.
  K2 part   detector topology: Poisson on/off capacity drops on the shared
            link at one severity per run, u in {1.05, 1.1, 1.15, 1.3}; on
            U(1, 4) s (15 % of them U(10, 20) s), off U(5, 20) s. pfifo (one
            shared queue: every client is hit), fq_codel (per-flow queues: only
            clients above their fair share are hit, so u sets the hit set; UDP
            would not congest any client there). Partial events: which share of
            a leaf alarms at light load (theta).
  K3 rev    detector topology: revasym (reverse delays 5/40/80/120 ms per
            client, forward unchanged) and revjit10 (10 ms reverse jitter on
            every access link) with cap bursts; detector-rev topology:
            revcross (UDP bursts on the ACK path only, router egress r1 -> r0
            at 10 Mb/s, no forward congestion) and revcrossmix (the same
            interleaved with forward cap bursts). pfifo (ACKs share the queue
            with the bursts), fq_codel (ACKs isolated: a no-reverse-queue control).
  K5 mixed  detector-access topology: cap bursts on the shared link + access
            router egress drops per client (private) in one shuffled sequence;
            sub-d joins at 60 s, sub-b leaves at 240 s. 4 AQMs.
  K6 depth  tree8 topology: targets A | B | C | D | X (A+B) | Y (C+D) | root
            | A+C (same instant). pfifo, fq_codel.
"""

from __future__ import annotations

import argparse
import datetime
import json
import random
import shutil
import statistics
import subprocess
import sys
import traceback
from argparse import Namespace
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402
import det_matrix as dm  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import grouping_baselines as gb  # noqa: E402
from grouping import Config  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.runtime import remove_partial_run, run_finished  # noqa: E402

RUNS = ROOT / ".runs"
# Extra topologies, registered with det_matrix's table (import time only, the file is not changed).
dm.TOPOLOGIES.setdefault("tree8", ("detector-tree8.yaml", "grp-burst-tree8.yaml", {
    "root": ("rr", "r0", None), "X": ("r0", "r1", None), "Y": ("r0", "r2", None),
    "A": ("r1", "switch-a", None), "B": ("r1", "switch-b", None), "C": ("r2", "switch-c", None),
    "D": ("r2", "switch-d", None)}, "root"))
dm.TOPOLOGIES.setdefault("rev", ("detector-rev.yaml", "grp-burst-rev.yaml", {"main": ("r1", "switch", "shared")}, "main"))

U_CAP, D_CAP = (1.3, 2.0), (1, 2, 4)
UNIFORM = list(dm.AQMS)
MIXED = {"mixa": {"r1": "pfifo", "r2": "fq_codel"}, "mixb": {"r1": "fq_codel", "r2": "pfifo"},
         "mixab": {"r1": "pfifo", "r2": "pfifo"}}
# On top of MIXED: router -> neighbor -> AQM of that one egress.
MIXED_EGRESS = {"mixab": {"r2": {"switch-a": "pfifo", "switch-b": "fq_codel"}}}
REV_ASYM_MS = (5, 40, 80, 120)
REV_LINK, REV_LINK_MBPS = ("r0", "r1"), 10.0     # its reverse direction is the router egress r1 -> r0
K2_U = (1.05, 1.1, 1.15, 1.3)
K2_ON, K2_ON_LONG, K2_OFF, K2_P_LONG, K2_T_END = (1.0, 4.0), (10.0, 20.0), (5.0, 20.0), 0.15, 300.0
JOIN_T, LEAVE_T, JOIN_SUB, LEAVE_SUB = 60.0, 240.0, "sub-d", "sub-b"
ENGINE_SET = {"theta_J": 0.6, "theta_cov": 0.6}   # the sweep value used in every real-run result so far
ONSET_SOURCES = ("shadow", "owd", "truth")

# K -> topology, AQM ids, run types.
CAMPAIGNS = {
    "K1": {"topology": "split", "aqms": UNIFORM + list(MIXED), "types": ["hier"]},
    "K2": {"topology": "base", "aqms": ["pfifo", "fq_codel"], "types": [f"part{round(u * 100)}" for u in K2_U]},
    "K3": {"topology": "base", "aqms": ["pfifo", "fq_codel"],
           "types": ["revasym", "revjit10", "revcross", "revcrossmix"]},
    "K5": {"topology": "access", "aqms": UNIFORM, "types": ["mixed"]},
    "K6": {"topology": "tree8", "aqms": ["pfifo", "fq_codel"], "types": ["depth"]},
}
TYPE_TOPOLOGY = {"revcross": "rev", "revcrossmix": "rev"}   # types that need another topology than the campaign's


# ---------------------------------------------------------------- planning

def _cap_event(n: dict, tgt: str, at: float, u: float, d: float, label: str) -> list[dict]:
    h = n["hops"][tgt]
    return [{"at_s": round(at, 3), "type": "link", **h["link"], "bandwidth_mbps": round(h["demand"] / u, 3),
             "label": label},
            {"at_s": round(at + d, 3), "type": "link", **h["link"], "bandwidth_mbps": h["base"], "label": "burst-end"}]


def _window(start: float, end: float, kind: str, target: str, cell: str, expected: list[str]) -> dict:
    return {"start": round(start, 3), "end": round(end, 3), "kind": kind, "target": target, "cell": cell,
            "expected": sorted(expected)}


def cap_cells(targets: list[str], rng: random.Random, repeats: int = 1) -> list[tuple[float, float, str]]:
    cells = [(u, d, t) for u in U_CAP for d in D_CAP for t in targets] * repeats
    rng.shuffle(cells)
    return cells


def cap_sequence(n: dict, cells: list[tuple[float, float, str]], rng: random.Random,
                 t0: float = dm.WARMUP_S) -> tuple[list[dict], list[dict], float]:
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
        t += span + rng.uniform(*dm.GAP_S)
    return events, windows, round(t - dm.GAP_S[0] + dm.TAIL_S)


def plan_hier(n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    rng = random.Random(seed)
    return cap_sequence(n, cap_cells(["up", "a", "b", "a+b", "a+b@0.5", "a+b@1", "a+b@2", "a+up"], rng), rng)


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
    # The joining client has no access events before it joins, the leaving one
    # none after it leaves: the leaver's cells are forced early enough to fit.
    slot = D_CAP[-1] + dm.GAP_S[1]
    events, windows, t = [], [], dm.WARMUP_S
    pending = list(cells)
    while pending:
        leaving = [c for c in pending if c[2] == LEAVE_SUB]
        if leaving and t >= LEAVE_T - 10 - slot * len(leaving):
            pool = leaving
        else:
            pool = [c for c in pending if (t > JOIN_T + 10 or c[2] != JOIN_SUB) and (t < LEAVE_T - 10 or c[2] != LEAVE_SUB)]
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
    events += [{"at_s": JOIN_T, "type": "join", "subscriber": JOIN_SUB},
               {"at_s": LEAVE_T, "type": "leave", "subscriber": LEAVE_SUB}]
    return events, windows, round(max(t - dm.GAP_S[0], LEAVE_T + 30) + dm.TAIL_S)


def plan_type(rtype: str, n: dict, seed: int) -> tuple[list[dict], list[dict], float]:
    if rtype == "hier":
        return plan_hier(n, seed)
    if rtype == "depth":
        return plan_depth(n, seed)
    if rtype.startswith("part"):
        return plan_part(n, seed, int(rtype[4:]) / 100)
    if rtype == "revcross":
        return plan_revcross(n, seed, mix=False)
    if rtype == "revcrossmix":
        return plan_revcross(n, seed, mix=True)
    if rtype == "revasym" or rtype.startswith("revjit"):
        return plan_revbursts(n, seed)
    if rtype == "mixed":
        return plan_mixed(n, seed)
    raise ValueError(rtype)


def apply_links(data: dict, rtype: str, n: dict) -> None:
    """Per-type changes to the base links (reverse delays / jitter / reverse capacity)."""
    shared = sorted(n["clients"])
    for link in data["links"]:
        if link["to"] in shared and link["from"] == n["uplink"][link["to"]]:
            rev = link.setdefault("reverse", {})
            if rtype == "revasym":
                rev["delay_ms"] = REV_ASYM_MS[shared.index(link["to"]) % len(REV_ASYM_MS)]
            elif rtype.startswith("revjit"):
                rev["jitter_ms"] = float(rtype[6:])
    if rtype in ("revcross", "revcrossmix"):
        data["links"].append({"from": REV_LINK[0], "to": REV_LINK[1], "reverse": {"bandwidth_mbps": REV_LINK_MBPS}})


def apply_aqm(data: dict, aqm: str, n: dict) -> None:
    def queue(name: str, limit: int | None) -> dict:
        out = {"aqm": name, "queue_limit_packets": limit, **dm.AQMS[name]}
        if name == "red":
            out.update(dm.red_thresholds(n, limit))
        return out

    per_router, per_egress = MIXED.get(aqm, {}), MIXED_EGRESS.get(aqm, {})
    for rid, router in data["routers"].items():
        name = per_router.get(rid, aqm if aqm in dm.AQMS else "pfifo")
        limit = router.get("queue_limit_packets")
        router.clear()
        router.update(queue(name, limit))
        if rid in per_egress:
            router["egress"] = {peer: queue(q, limit) for peer, q in per_egress[rid].items()}


def topology_of(k: str, rtype: str) -> str:
    return TYPE_TOPOLOGY.get(rtype, CAMPAIGNS[k]["topology"])


def scenario_for(k: str, rtype: str, aqm: str, rep: int, kdir: Path) -> tuple[Path, Path, float]:
    """Write <kdir>/_gen/<run_id>.yaml and -windows.json; return (scenario, topology file, duration)."""
    topology = topology_of(k, rtype)
    topo_file, base_file, *_ = dm.TOPOLOGIES[topology]
    n = dm.topology_numbers(topology)
    data = yaml.safe_load((ROOT / "configs" / "scenarios" / base_file).read_text())
    events, windows, duration = plan_type(rtype, n, seed=rep)
    data["events"], data["duration_s"] = events, duration
    apply_links(data, rtype, n)
    apply_aqm(data, aqm, n)
    gen = kdir / "_gen"
    gen.mkdir(parents=True, exist_ok=True)
    out = gen / f"{run_id(rtype, aqm, rep)}.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False))
    (gen / f"{run_id(rtype, aqm, rep)}-windows.json").write_text(json.dumps(windows, indent=1))
    return out, ROOT / "configs" / "topologies" / topo_file, duration


def run_id(rtype: str, aqm: str, rep: int) -> str:
    return f"grp-{rtype}-{aqm}-r{rep}"


def cells_of(k: str, reps: int) -> list[tuple[str, str, int]]:
    c = CAMPAIGNS[k]
    return [(rtype, aqm, rep) for rep in range(1, reps + 1) for aqm in c["aqms"] for rtype in c["types"]]


# ---------------------------------------------------------------- running

def git_commit() -> str:
    out = subprocess.run(["git", "-C", str(ROOT), "describe", "--always", "--dirty"], capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def run_campaign(k: str, kdir: Path, reps: int, skip_existing: bool, dry: bool) -> float:
    """Plan (and unless dry, run) every cell of K; returns the planned seconds of emulation."""
    kdir.mkdir(parents=True, exist_ok=True)
    man_path = kdir / "manifest.yaml"
    manifest = yaml.safe_load(man_path.read_text()) if man_path.exists() else {
        "campaign": k, "started": datetime.datetime.now().isoformat(timespec="seconds"), "finished": None,
        "git": git_commit(), "reps": reps, "aqms": CAMPAIGNS[k]["aqms"], "types": CAMPAIGNS[k]["types"], "runs": {}}
    total = 0.0
    for rtype, aqm, rep in cells_of(k, reps):
        rid = run_id(rtype, aqm, rep)
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
            try:
                det_eval.score(run_dir)
            except (Exception, SystemExit) as e:  # best effort here; score again later with det_eval.py score
                print(f"   det_eval.score failed on {rid}: {e!r}", flush=True)
            manifest["runs"][rid] = f"done {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}"
        man_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    if not dry:
        manifest["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
        man_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return total


# ---------------------------------------------------------------- reporting

def ecg_dir(src: str, tag: str = "") -> str:
    """<run>/grouping[-<tag>][-<src>]: the adapter's output dir for one onset source."""
    return "grouping" + (f"-{tag}" if tag else "") + ("" if src == "shadow" else f"-{src}")


def score_run(run_dir: Path, cfg: Config, tag: str = "") -> dict:
    out = {"run": run_dir.name, "ecg": {}}
    for src in ONSET_SOURCES:
        a = Namespace(out=ecg_dir(src, tag), onsets=src, backdate_max=1.0, backdate_qd_ms=10.0,
                      warmup=det_eval.WARMUP_S, spread_only=False)
        try:
            out["ecg"][src] = ga.process(run_dir, cfg, a)
        except SystemExit as e:  # shadow onsets without the replay binary: the other sources still count
            out["ecg"][src] = {"error": str(e)}
        except Exception as e:
            out["ecg"][src] = {"error": repr(e)}
            traceback.print_exc()
    try:
        out["baselines"] = gb.process(run_dir, Namespace(methods=gb.METHODS, owd="oracle", dcw_th=0.8,
                                                         ecg=[ecg_dir(s, tag) for s in ONSET_SOURCES],
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
        out[(cell, e["case"])] += 1
    return out


def fmt(v) -> str:
    return "-" if v is None else f"{v:.2f}" if isinstance(v, float) else str(v)


def med(vals: list) -> float | None:
    vals = [v for v in vals if isinstance(v, (int, float)) and v is not None]
    return statistics.median(vals) if vals else None


def report(k: str, kdir: Path, cfg: Config, over: dict | None = None, tag: str = "") -> None:
    sfx = f"-{tag}" if tag else ""
    runs = sorted(p for p in kdir.glob("grp-*") if run_finished(p))
    results = [score_run(r, cfg, tag) for r in runs]
    (kdir / f"results{sfx}.json").write_text(json.dumps(results, indent=1, default=str))
    lines = [f"# Grouping campaign {k}" + (f" ({tag})" if tag else ""), "",
             f"{len(runs)} runs, engine overrides {over if over is not None else ENGINE_SET}, "
             f"onset sources {', '.join(ONSET_SOURCES)}, truth = stimulus windows x OWD oracle x plan "
             f"(pairs_leaf). Generated {datetime.datetime.now():%Y-%m-%d %H:%M}.", ""]
    # 1. per type x AQM: medians over reps
    lines += ["## Final grouping per type x AQM (median over reps; leaf precision / recall, t_correct s; "
              "cov = share of pairs decided, shadow / owd / truth)", "",
              "| type | aqm | n | ECG shadow | ECG owd | ECG truth | cov | DCW | rmcatSBD | dcSBD | spread p50/p90 ms (shadow) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    by_cell = defaultdict(list)
    for r in results:
        parts = r["run"].split("-")
        by_cell[(parts[1], "-".join(parts[2:-1]))].append(r)

    def cell_str(rs, name):
        P = med([((r.get("baselines") or {}).get("methods") or {}).get(name, {}).get("final", {}).get("vs_leaf", {})
                 .get("precision") for r in rs])
        R = med([((r.get("baselines") or {}).get("methods") or {}).get(name, {}).get("final", {}).get("vs_leaf", {})
                 .get("recall") for r in rs])
        T = med([((r.get("baselines") or {}).get("methods") or {}).get(name, {}).get("t_correct") for r in rs])
        return f"{fmt(P)} / {fmt(R)}, {fmt(T)}"
    for (rtype, aqm), rs in sorted(by_cell.items()):
        sp = [r["ecg"].get("shadow", {}).get("spread_onset_ms") for r in rs]
        sp = [s for s in sp if s]
        spread = f"{med([s['p50'] for s in sp]):.0f} / {med([s['p90'] for s in sp]):.0f}" if sp else "-"
        ecg_names = [f"ecg:{ecg_dir(s, tag)}" for s in ONSET_SOURCES]
        cov = " / ".join(fmt(med([r["ecg"].get(s, {}).get("coverage") for r in rs])) for s in ONSET_SOURCES)
        lines.append(f"| {rtype} | {aqm} | {len(rs)} | " + " | ".join(cell_str(rs, n) for n in ecg_names)
                     + f" | {cov} | " + " | ".join(cell_str(rs, n) for n in ("dcw", "rmcat_sbd", "dc_sbd"))
                     + f" | {spread} |")
    # 2. case matrix per type and source
    for src in ONSET_SOURCES:
        lines += ["", f"## ECG event cases per stimulus cell ({src} onsets, summed over AQMs and reps)", ""]
        per_type = defaultdict(Counter)
        for r in runs:
            per_type[r.name.split("-")[1]] += case_matrix(r, src, tag)
        cases = sorted({c for cm in per_type.values() for _, c in cm})
        lines += ["| type | cell | " + " | ".join(cases) + " |", "|---|---|" + "---|" * len(cases)]
        for rtype, cm in sorted(per_type.items()):
            for cell in sorted({c for c, _ in cm}):
                lines.append(f"| {rtype} | {cell} | " + " | ".join(str(cm[(cell, c)]) for c in cases) + " |")
    # 3. per run
    lines += ["", "## Per run", "", "| run | source | cases | leaf P / R | cov | leaves | spread p50/p90 |",
              "|---|---|---|---|---|---|---|"]
    for r in results:
        for src in ONSET_SOURCES:
            s = r["ecg"].get(src, {})
            if "error" in s:
                lines.append(f"| {r['run']} | {src} | error: {s['error']} | | | | |")
                continue
            sp = s.get("spread_onset_ms")
            lines.append(f"| {r['run']} | {src} | {s.get('cases')} | {fmt(s.get('precision'))} / {fmt(s.get('recall'))} "
                         f"| {fmt(s.get('coverage'))} | {s.get('leaves')} | "
                         f"{f'{sp['p50']:.0f} / {sp['p90']:.0f}' if sp else '-'} |")
    (kdir / f"report{sfx}.md").write_text("\n".join(lines) + "\n")
    print(f"report: {kdir / f'report{sfx}.md'}", flush=True)


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ks", default="K1,K2,K3,K5,K6")
    ap.add_argument("--reps", type=int, default=3)
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
    campaign = a.campaign or RUNS / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_{a.name}"
    campaign.mkdir(parents=True, exist_ok=True)
    print(f"campaign: {campaign}", flush=True)
    budget = 0.0
    for k in ks:
        kdir = campaign / k
        if a.report_only:
            report(k, kdir, cfg, over, a.tag)
            continue
        secs = run_campaign(k, kdir, a.reps, a.skip_existing, dry=a.plan)
        budget += secs
        n = len(cells_of(k, a.reps))
        print(f"{k}: {n} runs, {secs / 3600:.1f} h of emulation (+ ~1 min setup each)", flush=True)
        if not a.plan:
            report(k, kdir, cfg, over, a.tag)
    if a.plan:
        print(f"total: {budget / 3600:.1f} h of emulation")


if __name__ == "__main__":
    main(sys.argv[1:])
