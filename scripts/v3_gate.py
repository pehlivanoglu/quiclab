#!/usr/bin/env python3
"""Suite v3 run checks (spec 6.1 gate checks 1-6, plus the non-gating keyframe peak and
fq_codel collision report). Reads only what a run already wrote; changes nothing.

    .venv/bin/python3 scripts/v3_gate.py check <run> [<run> ...]       # one line per run
    .venv/bin/python3 scripts/v3_gate.py gate <run> [<run> ...]        # gate-report markdown on stdout
    .venv/bin/python3 scripts/v3_gate.py summary <campaign>            # <campaign>/run-checks.{jsonl,md}, rep-compare.md

Checks:
 1 calm load on every shaped bottleneck egress within LOAD_TOL of U; video share / 0.96
   (QUIC bytes vs router bytes, scenario_catalog) within SHARE_TOL of s (legacy: of 1).
 2 ECN marks = 0 on every router egress (router-metrics ecn_marks).
 3 no skb larger than the MTU at a traced egress (GT-Q `oversize`) and offloads off on
   every interface (<run>/offloads.csv).
 4 GT-Q health (rules of 2026-11-14, see check_health), gated on the run's bottleneck targets:
   rows = kernel counters; unmatched packets <= max(3, 5e-5 x dequeues) per kind and <= 2 per
   200 ms window; with >= 1000 backlogged gaps: gaps within max(10 %, 15 us) of ideal for >= 99 % and
   20 ms windows within +-5 % for >= 99 %; lost events 0 and CPU idle >= 35 % for the run.
 5 per surge window: background + surge arriving at the target (v3_stimuli) within SURGE_TOL of
   the planned U(1 - s) + (u - U); u is the stimulus intensity, the video's reaction is an outcome.
 6 background not phase-locked: power of the background's 5 ms byte counts (qtraffic
   *-sent5.csv, summed per egress) at 1 Hz and 30 Hz (3 bins) not above PEAK_FACTOR x the
   median of the bins within 0.5 Hz.
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
import gt1  # noqa: E402
import scenario_catalog  # noqa: E402

LOAD_TOL, SHARE_TOL, SURGE_TOL = 0.03, 0.03, 0.05     # (S)
SHARE_HEADER = 0.96                                    # (M) docs/scenario-catalog.md: video-only egress shows 0.96
CPU_IDLE_MIN = 0.35                                    # (S)
GAP_SHARE, WIN_SHARE = 0.99, 0.99                      # (S) check 4b (2026-11-14): +-10 % per gap, +-5 % per 20 ms
MIN_GAPS = 1000                                        # (S) check 4b evaluated only with this many backlogged gaps
PEAK_FACTOR = 10.0                                     # (T) "a peak above its neighbours", as a number (accepted 2026-11-14)
PEAK_WINDOW_S = 0.2                                    # (S) keyframe queueing peak: 200 ms after the keyframe
CALM_MARGIN_S = 1.0                                    # (S) as scenario_catalog
FQ_FLOWS = 1024                                        # kernel default fq_codel flows (2.3 check a)


def _plan(rd: Path) -> dict:
    for p in (rd / "v3-plan.json", rd / "grouping" / "plan.json"):
        if p.exists():
            return json.loads(p.read_text())
    return {}


def _windows(rd: Path) -> list[dict]:
    p = rd / "grouping" / "windows.json"
    return json.loads(p.read_text()) if p.exists() else []


def _health(rd: Path) -> dict:
    p = rd / "gtq-health.csv"
    return {r["key"]: r["value"] for r in csv.DictReader(p.open())} if p.exists() else {}


def _num(x, default=np.nan):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def check_load_share(rd: Path, plan: dict) -> dict:
    res = scenario_catalog.calm_load(rd)
    out, ok = {}, True
    if "error" in res:
        return {"ok": False, "error": res["error"]}
    s_target = plan.get("s") if plan.get("s") is not None else 1.0
    for name, e in plan.get("egress", {}).items():
        if not e.get("shaped", True):
            continue
        m = res["egress"].get(e["hop"])
        if m is None:
            out[name] = {"ok": False, "why": "no calm samples"}
            ok = False
            continue
        share = m["video_share"] / SHARE_HEADER if m["video_share"] else None
        good = abs(m["load"] - plan["U"]) <= LOAD_TOL and share is not None and abs(share - s_target) <= SHARE_TOL
        out[name] = {"hop": e["hop"], "load": m["load"], "U": plan["U"], "share": round(share, 3) if share else None,
                     "s": s_target, "ok": good}
        ok &= good
    return {"ok": ok, "egress": out}


AQM_KINDS = ("pfifo", "codel", "pie", "fq_codel", "red", "cake", "dualpi2")


def qdisc_lines(rd: Path) -> list[tuple[str, str, str]]:
    """(node, iface, `tc qdisc show` line) of every AQM leaf (handle 20:) the run installed
    (<run>/qdiscs.txt, written by the backend after shaping)."""
    p = rd / "qdiscs.txt"
    if not p.exists():
        return []
    out, node, iface = [], "", ""
    for line in p.read_text().splitlines():
        if line.startswith("== "):
            node, iface = line[3:].split()[:2]
        elif line.startswith("qdisc ") and " 20: " in line and line.split()[1] in AQM_KINDS:
            out.append((node, iface, line.strip()))
    return out


def check_ecn(rd: Path) -> dict:
    """Check 2: no ECN mark on any egress, and no AQM leaf installed with ecn on (tc prints
    the word `ecn`; cake has no ECN switch and prints none: listed apart)."""
    lines = qdisc_lines(rd)
    configured = [f"{n}/{i}: {l}" for n, i, l in lines if "ecn" in l.split()]
    cake = [f"{n}/{i}" for n, i, l in lines if l.split()[1] == "cake"]
    marks = {}
    for p in sorted((rd / "router-metrics").glob("*/*.csv")):
        if p.name.endswith(("-queue.csv", "-flows.csv")):
            continue
        marks[p.stem] = int(pd.read_csv(p, usecols=["ecn_marks"]).ecn_marks.sum())
    return {"ok": all(v == 0 for v in marks.values()) and not configured and bool(lines),
            "nonzero": {k: v for k, v in marks.items() if v}, "ecn_configured": configured,
            "cake_no_ecn_switch": cake, "aqm_lines": len(lines)}


def check_mtu(rd: Path, h: dict) -> dict:
    over = {k[:-len(".oversize")]: int(_num(v, 0)) for k, v in h.items() if k.endswith(".oversize")}
    off_bad = []
    p = rd / "offloads.csv"
    if p.exists():
        for r in csv.DictReader(p.open()):
            if any(r[k] not in ("off", "") for k in r if k not in ("node", "iface")):
                off_bad.append(f"{r['node']}/{r['iface']}")
    return {"ok": bool(over) and all(v == 0 for v in over.values()) and p.exists() and not off_bad,
            "oversize": {k: v for k, v in over.items() if v}, "offloads_recorded": p.exists(),
            "offloads_not_off": off_bad, "traced": len(over)}


def target_hops(plan: dict, wins: list[dict]) -> set[str]:
    """The run's bottleneck targets: every shaped bottleneck egress of the plan, plus the
    egresses of private stimuli (T-ACCESS access egresses with capacity-drop / trace windows)."""
    hops = {e["hop"] for e in (plan.get("egress") or {}).values() if e.get("shaped", True)}
    hops |= {w["hop"] for w in wins if w.get("kind") == "access" and w.get("hop")}
    return hops


def _service_from_trace(rd: Path, iface: str, hop: str) -> dict:
    """router_trace.service_stats recomputed from <iface>-packets.csv (for runs whose health file
    predates the per-gap tolerance): the gated share and the jitter quantiles."""
    from quiclab import router_trace as rt
    from quiclab.config.scenario import load_scenario
    from quiclab.config.schema import load_topology
    sc = load_scenario(rd / "scenario.yaml", load_topology(rd / "topology.yaml"))
    h = tuple(hop.split("->"))
    sv = rt.service_stats(rt.read_packets(rd / "router-trace" / f"{iface}-packets.csv"), d.Run(rd).epoch_mono_ns,
                          rt.capacity_timeline(sc, h), rt.delay_timeline(sc, h))
    return {"gap_within_tol": sv["gap_within_tol"], "jitter_us_p1": round(sv["jitter_us_p1"], 2),
            "jitter_us_p99": round(sv["jitter_us_p99"], 2), "recomputed": True}


def check_health(rd: Path, h: dict, plan: dict | None = None, wins: list[dict] | None = None) -> dict:
    """Check 4 (user rules 2026-11-14, third version), from gtq-health.csv.
    Gating, on bottleneck-target egresses only (target_hops):
      4a  rows = kernel counters; unmatched dequeues and unmatched enqueues each
          <= max(3, 5e-5 x dequeues); <= 2 of either kind in any 200 ms window;
      4b  only with >= MIN_GAPS backlogged gaps (else "not evaluated"): gap within
          max(10 %, 15 us) of the previous packet's serialization time for >= GAP_SHARE of gaps
          (router_trace.GAP_TOL_FLOOR_NS; the plain +-10 % share is information), and bytes per backlogged
          20 ms window within +-5 % of C x 20 ms for >= WIN_SHARE of windows.
    Global: bpftrace lost events 0; host CPU idle >= CPU_IDLE_MIN in every second.
    Every other traced egress (publisher, sub-ctrl, ...) is reported, not gated."""
    from quiclab import router_trace as rt
    lost = int(_num(h.get("lost_events"), -1))
    hop_of = {}
    meta = rd / "router-trace" / "interfaces.csv"
    if meta.exists():
        hop_of = {r["iface"]: r["hop"] for r in csv.DictReader(meta.open())}
    targets = target_hops(plan or {}, wins or [])
    ifaces = sorted(k[:-len(".rows_match")] for k in h if k.endswith(".rows_match"))
    per, ok = {}, lost == 0 and bool(ifaces)
    for i in ifaces:
        g = lambda key, default=np.nan: _num(h.get(f"{i}.{key}"), default)   # noqa: E731
        deq = int(g("deq", 0))
        allowed = rt.unmatched_allowed(deq)
        row = {"hop": hop_of.get(i, i), "role": "target" if hop_of.get(i) in targets else "info",
               "rows_match": int(g("rows_match", 0)), "dequeues": deq, "allowed": round(allowed, 2),
               "unmatched_deq": int(g("unmatched_deq", -1)), "unmatched_deq_max_200ms": int(g("unmatched_deq_max_200ms", -1)),
               "unmatched_enq": int(g("unmatched_enq", -1)), "unmatched_enq_max_200ms": int(g("unmatched_enq_max_200ms", -1)),
               "gaps": int(g("interdeq_gaps", 0)), "gap_within10": g("interdeq_within10"), "gap_p99": g("interdeq_ratio_p99"),
               "gap_within_tol": g("interdeq_within_tol"), "jitter_us_p1": g("interdeq_jitter_us_p1"),
               "jitter_us_p99": g("interdeq_jitter_us_p99"),
               "win20_n": int(g("win20_n", 0)), "win20_within5": g("win20_within5")}
        acct = (row["rows_match"] == 1 and all(0 <= row[f"unmatched_{k}"] <= allowed for k in ("deq", "enq"))
                and all(0 <= row[f"unmatched_{k}_max_200ms"] <= rt.UNMATCHED_MAX_200MS for k in ("deq", "enq")))
        if np.isnan(row["gap_within_tol"]) and row["role"] == "target" and row["gaps"] >= MIN_GAPS:
            row.update(_service_from_trace(rd, i, row["hop"]))   # health file from before the tolerance rule
        if row["gaps"] < MIN_GAPS:
            svc = None
        else:
            svc = bool(row["gap_within_tol"] >= GAP_SHARE and (row["win20_n"] == 0 or row["win20_within5"] >= WIN_SHARE))
        row.update(accounting_ok=acct, service_ok=svc,
                   service="not evaluated" if svc is None else ("ok" if svc else "FAIL"))
        row["ok"] = bool(acct and svc is not False) if row["role"] == "target" else None
        per[i] = row
        if row["role"] == "target":
            ok &= row["ok"]
    if not any(r["role"] == "target" for r in per.values()):
        ok = False
    idle = _num(h.get("cpu_idle_min"))
    ok = bool(ok and not np.isnan(idle) and idle >= CPU_IDLE_MIN)
    misses = {k[:-len(".recursion_misses")]: int(_num(v, -1)) for k, v in h.items() if k.endswith(".recursion_misses")}
    return {"ok": ok, "lost_events": lost, "cpu_idle_min": idle, "egress": per,
            "bad": [i for i, r in per.items() if r["ok"] is False], "recursion_misses": misses,
            "unmatched_total": sum(max(0, r["unmatched_deq"]) + max(0, r["unmatched_enq"]) for r in per.values()),
            "unmatched_targets": sum(max(0, r["unmatched_deq"]) + max(0, r["unmatched_enq"]) for r in per.values()
                                     if r["role"] == "target"),
            "invalid_reasons": h.get("invalid_reasons", "")}


def _egress_csv(run: d.Run) -> dict[str, Path]:
    return {f"{a}->{b}": p for (a, b), p in gt1.router_egresses(run)}


def check_surge(rd: Path, plan: dict, wins: list[dict]) -> dict:
    """Check 5 (decision 2026-11-14): u is the stimulus intensity, so per surge window the
    background + surge arriving at the target (v3_stimuli: GT-Q trace, enqueue times) must be
    within SURGE_TOL of the planned U(1 - s) + (u - U). The realized total and the video's
    reaction are outcomes: written to <run>/v3-stimuli.csv, not gated."""
    import v3_stimuli
    rows = [r for r in v3_stimuli.load(rd) if r["stimulus_type"] == "surge" and r["planned_nonvideo"] is not None]
    if not rows:
        return {"ok": None}
    out, ok = [], True
    for r in rows:
        good = abs(r["nonvideo_load"] - r["planned_nonvideo"]) <= SURGE_TOL
        out.append({"hop": r["hop"], "start": r["start"], "u": r["u_nominal"], "d": r["d"],
                    "planned_nonvideo": r["planned_nonvideo"], "measured": r["nonvideo_load"],
                    "total": r["total_load"], "video_rel_calm": r["video_rel_calm"], "source": r["source"],
                    "ok": bool(good)})
        ok &= good
    return {"ok": bool(ok), "windows": out}


def check_phase_lock(rd: Path, plan: dict) -> dict:
    run = d.Run(rd)
    per: dict[str, list[Path]] = defaultdict(list)
    for p in (rd / "traffic").glob("bg-*-sent5.csv"):
        per[p.name[3:-len("-sent5.csv")].split("-")[0]].append(p)
    if not per:
        return {"ok": None, "why": "no background with 5 ms logs"}
    out, ok = {}, True
    lo, hi = d.WARMUP_S + 10, run.duration - 10
    for egress, files in sorted(per.items()):
        bins = None
        for f in files:
            x = pd.read_csv(f)
            t = np.array([run.t_unix_us(v) for v in x.t_us])
            keep = (t >= lo) & (t < hi)
            idx = np.floor((t[keep] - lo) / 0.005).astype(int)
            b = np.bincount(idx, weights=x.sent_bytes.values[keep], minlength=int((hi - lo) / 0.005) + 1)
            bins = b if bins is None else bins[:len(b)] + b[:len(bins)]
        spec = np.abs(np.fft.rfft(bins - bins.mean())) ** 2
        freq = np.fft.rfftfreq(len(bins), 0.005)
        res = {}
        for f0 in (1.0, 30.0):
            i = int(np.argmin(np.abs(freq - f0)))
            near = (np.abs(freq - f0) <= 0.5) & (np.abs(np.arange(len(freq)) - i) > 1)
            ratio = float(spec[i - 1:i + 2].max() / np.median(spec[near])) if near.any() else float("nan")
            res[f"{f0:g}Hz"] = round(ratio, 2)
            ok &= ratio <= PEAK_FACTOR
        out[egress] = res
    return {"ok": bool(ok), "peak_over_median": out}


def keyframe_peaks(rd: Path, plan: dict, wins: list[dict]) -> dict:
    """Queue delay (5 ms queue CSV, backlog / C_e) in the 200 ms after each keyframe (phase 0: whole
    seconds of the stream), calm time only: p50 / p90 / max of the per-keyframe peaks, per egress."""
    run = d.Run(rd)
    busy = [(w["start"] - CALM_MARGIN_S, w["end"] + CALM_MARGIN_S) for w in wins]
    csvs = _egress_csv(run)
    out = {}
    for name, e in plan.get("egress", {}).items():
        p = csvs.get(e["hop"])
        if not e.get("shaped", True) or p is None:
            continue
        fine = p.with_name(p.stem + "-queue.csv")
        r = pd.read_csv(fine if fine.exists() else p, usecols=["timestamp_mono_ns", "queue_backlog_bytes"])
        t = np.array([run.t_mono_us(v / 1000) for v in r.timestamp_mono_ns])
        q = r.queue_backlog_bytes.values * 8 / (e["C_e_mbps"] * 1e6) * 1000
        peaks = []
        for k in range(int(d.WARMUP_S) + 10, int(run.duration) - 2):
            if any(a <= k + PEAK_WINDOW_S and k <= b for a, b in busy):
                continue
            m = (t >= k) & (t < k + PEAK_WINDOW_S)
            if m.any():
                peaks.append(float(q[m].max()))
        if peaks:
            out[name] = {"hop": e["hop"], "n": len(peaks), "p50": round(float(np.median(peaks)), 1),
                         "p90": round(float(np.percentile(peaks, 90)), 1), "max": round(max(peaks), 1),
                         "ref_ms": e.get("keyframe_peak_ref_ms")}
    return out


def fq_collisions(rd: Path, plan: dict) -> dict | None:
    """fq_codel: background packets (unpinned, prio 0) whose flow hash lands in a pinned client
    class. Needs the skb hash in the GT-Q trace; 'unverifiable' when the trace holds none."""
    if plan.get("aqm") not in ("fq_codel", "mixab"):
        return None
    ids_p = rd / "router-metrics" / "flow-ids.json"
    if not ids_p.exists():
        return {"status": "no flow-ids.json"}
    pinned = {int(v.split(":")[1], 16) for v in json.loads(ids_p.read_text()).values()}
    out = {}
    for p in sorted((rd / "router-trace").glob("*-packets.csv")):
        x = pd.read_csv(p, usecols=["kind", "hash", "prio", "daddr", "dport"])
        x = x[(x.kind == "dequeue") & (x.prio == 0)]
        if not len(x) or (x.hash == 0).all():
            out[p.stem[:-len("-packets")]] = "unverifiable (no skb hash in the trace)"
            continue
        bucket = ((x.hash.astype(np.uint64) * np.uint64(FQ_FLOWS)) >> np.uint64(32)).astype(int) + 1
        hit = x[bucket.isin(pinned)]
        out[p.stem[:-len("-packets")]] = {"bg_packets": int(len(x)), "in_pinned_class": int(len(hit)),
                                         "flows": sorted({f"{a}:{b}" for a, b in zip(hit.daddr, hit.dport)})[:10]}
    return out


def run_checks(rd: Path) -> dict:
    rd = Path(rd)
    plan, wins, h = _plan(rd), _windows(rd), _health(rd)
    out = {"run": rd.name, "plan": {k: plan.get(k) for k in ("block", "type", "variant", "aqm", "rep", "s", "U")}}
    for name, fn in (("1_load_share", lambda: check_load_share(rd, plan)), ("2_ecn", lambda: check_ecn(rd)),
                     ("3_mtu", lambda: check_mtu(rd, h)), ("4_health", lambda: check_health(rd, h, plan, wins)),
                     ("5_surge", lambda: check_surge(rd, plan, wins)), ("6_phase", lambda: check_phase_lock(rd, plan)),
                     ("keyframe_peaks", lambda: keyframe_peaks(rd, plan, wins)),
                     ("fq_collisions", lambda: fq_collisions(rd, plan))):
        try:
            out[name] = fn()
        except Exception as e:  # noqa: BLE001
            out[name] = {"ok": False, "error": repr(e)}
    (rd / "v3-checks.json").write_text(json.dumps(out, indent=1, default=str))
    return out


def _mark(c) -> str:
    v = c.get("ok") if isinstance(c, dict) else None
    return "-" if v is None else ("ok" if v else "FAIL")


def line(res: dict) -> str:
    parts = [f"{k.split('_')[0]} {_mark(res.get(k, {}))}" for k in
             ("1_load_share", "2_ecn", "3_mtu", "4_health", "5_surge", "6_phase")]
    ls = res.get("1_load_share", {}).get("egress", {})
    loads = ", ".join(f"{n} {v.get('load')}/{v.get('share')}" for n, v in ls.items())
    return f"v3 checks: {'; '.join(parts)}; load/share {loads}"


def gate_report(run_dirs: list[Path], smoke: bool = False) -> tuple[bool, str]:
    """(pass, markdown). Gate: checks 1-6 must hold on every run (5 only where there are surges).
    Smoke (spec 8.8): checks 1-4 and 6; 5 is reported."""
    gating = ("1_load_share", "2_ecn", "3_mtu", "4_health", "6_phase") if smoke else \
        ("1_load_share", "2_ecn", "3_mtu", "4_health", "5_surge", "6_phase")
    results = []
    for rd in run_dirs:
        rd = Path(rd)
        if not (rd / "events.csv").exists():
            results.append({"run": rd.name, "missing": True})
            continue
        results.append(run_checks(rd))
    verdict = all(not r.get("missing") and all(r.get(k, {}).get("ok") is not False for k in gating) for r in results)
    title = "Smoke" if smoke else "Gate"
    L = [f"# {title}: {'PASS' if verdict else 'FAIL'}", "",
         f"Gating checks: {', '.join(gating)} (scripts/v3_gate.py). Runs: {len(results)}.", "",
         "| run | " + " | ".join(k.split("_", 1)[0] + " " + k.split("_", 1)[1] for k in
                                ("1_load_share", "2_ecn", "3_mtu", "4_health", "5_surge", "6_phase")) + " |",
         "|---|---|---|---|---|---|---|"]
    for r in results:
        if r.get("missing"):
            L.append(f"| {r['run']} | run missing or failed | | | | | |")
            continue
        L.append(f"| {r['run']} | " + " | ".join(_mark(r.get(k, {})) for k in
                 ("1_load_share", "2_ecn", "3_mtu", "4_health", "5_surge", "6_phase")) + " |")
    L += ["", "## Load and share per egress (target U, s)", "",
          "| run | egress | hop | load (U) | share / 0.96 (s) |", "|---|---|---|---|---|"]
    for r in results:
        for n, v in (r.get("1_load_share", {}).get("egress") or {}).items():
            L.append(f"| {r['run']} | {n} | {v.get('hop')} | {v.get('load')} ({v.get('U')}) | {v.get('share')} "
                     f"({v.get('s')}) |")
    L += ["", "## Keyframe queueing peak (calm, 200 ms after each keyframe; not gating)", "",
          "| run | egress | hop | n | p50 / p90 / max ms | 0.121 s U ms |", "|---|---|---|---|---|---|"]
    for r in results:
        for n, v in (r.get("keyframe_peaks") or {}).items():
            if isinstance(v, dict) and "p50" in v:
                L.append(f"| {r['run']} | {n} | {v['hop']} | {v['n']} | {v['p50']} / {v['p90']} / {v['max']} | "
                         f"{v['ref_ms']} |")
    L += ["", "## Installed AQM leaves (`tc qdisc show`, handle 20:; `ecn` must not appear; cake has no "
          "ECN switch)", ""]
    for rd, r in zip(run_dirs, results):
        for n, i, ln in qdisc_lines(Path(rd)):
            L.append(f"- {r['run']} {n}/{i}: `{ln}`")
    L += ["", "## Check 4 per traced egress (target = gated; info = reported only)", "",
          "| run | hop | role | dequeues | unmatched deq / enq (allowed) | max per 200 ms deq / enq | 4a | "
          "backlogged gaps | within max(10 %, 15 us) (within 10 %) | jitter us p1 / p99 | 20 ms windows within 5 % (n) | 4b |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        h = r.get("4_health") or {}
        for i, v in (h.get("egress") or {}).items():
            L.append(f"| {r['run']} | {v['hop']} | {v['role']} | {v['dequeues']} | {v['unmatched_deq']} / "
                     f"{v['unmatched_enq']} ({v['allowed']:g}) | {v['unmatched_deq_max_200ms']} / "
                     f"{v['unmatched_enq_max_200ms']} | {'ok' if v['accounting_ok'] else 'FAIL'} | {v['gaps']} | "
                     f"{v['gap_within_tol']:.4f} ({v['gap_within10']:.4f}) | {v['jitter_us_p1']} / {v['jitter_us_p99']} | "
                     f"{v['win20_within5']} ({v['win20_n']}) | {v['service']} |")
    L += ["", "## Health, surge, phase-lock details", ""]
    for r in results:
        if r.get("missing"):
            continue
        h = r.get("4_health", {})
        L.append(f"- {r['run']}: lost {h.get('lost_events')}; target egresses failing {h.get('bad')}; "
                 f"recursion misses {h.get('recursion_misses')}; unmatched total {h.get('unmatched_total')} "
                 f"(targets {h.get('unmatched_targets')}); cpu idle min {h.get('cpu_idle_min')}; "
                 f"ECN {r.get('2_ecn', {}).get('nonzero')}; oversize {r.get('3_mtu', {}).get('oversize')}, "
                 f"offloads not off {r.get('3_mtu', {}).get('offloads_not_off')}; "
                 f"phase {r.get('6_phase', {}).get('peak_over_median')}; "
                 f"surge (u, planned non-video, measured, total, video / calm) "
                 f"{[(w.get('u'), w.get('planned_nonvideo'), w.get('measured'), w.get('total'), w.get('video_rel_calm')) for w in r.get('5_surge', {}).get('windows', [])]}; "
                 f"fq collisions {r.get('fq_collisions')}; errors "
                 f"{[k for k, v in r.items() if isinstance(v, dict) and 'error' in v]}")
    return verdict, "\n".join(L) + "\n"


def rep_compare(kdir: Path, rows: list[dict]) -> str:
    """Rep 1 vs rep 2 for the headline numbers of the v3 checks (calm load and keyframe-peak p50
    per egress). A cell is flagged when |r1 - r2| exceeds the largest |r1 - r2| of the other
    cells of its block for that metric (needs >= 2 other cells; otherwise '-'); flagged cells
    get the per-client pacing / emission table of both reps next to them (v3_emission)."""
    import re
    import v3_emission
    by: dict[str, dict[int, dict]] = defaultdict(dict)
    for r in rows:
        m = re.match(r"(.+)-r(\d+)$", r["run"])
        if m:
            by[m.group(1)][int(m.group(2))] = r
    cells = {c: v for c, v in by.items() if 1 in v and 2 in v}
    metric_vals: dict[tuple[str, str], dict[str, tuple[float, float]]] = defaultdict(dict)
    for c, v in cells.items():
        block = c.split("-")[1]
        for name, e in (v[1].get("1_load_share", {}).get("egress") or {}).items():
            e2 = (v[2].get("1_load_share", {}).get("egress") or {}).get(name)
            if e2 and e.get("load") is not None and e2.get("load") is not None:
                metric_vals[(block, f"load {name}")][c] = (e["load"], e2["load"])
        for name, e in (v[1].get("keyframe_peaks") or {}).items():
            e2 = (v[2].get("keyframe_peaks") or {}).get(name)
            if isinstance(e, dict) and isinstance(e2, dict) and "p50" in e and "p50" in e2:
                metric_vals[(block, f"keyframe peak p50 ms {name}")][c] = (e["p50"], e2["p50"])
    L = ["# Suite v3: rep 1 vs rep 2", "", "Flag: |r1 - r2| above the largest |r1 - r2| of the other cells of the "
         "block for that metric. Nothing is averaged.", "",
         "| block | cell | metric | r1 | r2 | abs diff | largest abs diff, other cells | flag |",
         "|---|---|---|---|---|---|---|---|"]
    flagged = set()
    for (block, metric), vals in sorted(metric_vals.items()):
        diffs = {c: abs(a - b) for c, (a, b) in vals.items()}
        for c, (a, b) in sorted(vals.items()):
            others = [d for k, d in diffs.items() if k != c]
            ref = max(others) if len(others) >= 2 else None
            flag = "-" if ref is None else ("**disagree**" if diffs[c] > ref else "")
            if flag == "**disagree**":
                flagged.add(c)
            L.append(f"| {block} | {c} | {metric} | {a} | {b} | {diffs[c]:.3f} | "
                     f"{'-' if ref is None else f'{ref:.3f}'} | {flag} |")
    L += ["", "## Per-client pacing and emission of the flagged cells (r1 / r2)", ""]
    for c in sorted(flagged):
        L += [f"### {c}", "", "| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |", "|---|---|---|---|---|",
              *v3_emission.side_by_side(v3_emission.load(Path(kdir) / f"{c}-r1"),
                                        v3_emission.load(Path(kdir) / f"{c}-r2")), ""]
    return "\n".join(L) + "\n"


def campaign_summary(kdir: Path) -> None:
    """Every finished run's checks; flags runs off target (kept) and the health extremes."""
    rows = []
    for rd in sorted(p for p in Path(kdir).iterdir() if p.is_dir() and p.name.startswith("v3-")):
        f = rd / "v3-checks.json"
        rows.append(json.loads(f.read_text()) if f.exists() else run_checks(rd))
    with (Path(kdir) / "run-checks.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, default=str) + "\n")
    _, text = gate_report([Path(kdir) / r["run"] for r in rows])
    idle = [r.get("4_health", {}).get("cpu_idle_min") for r in rows]
    p99 = [v.get("gap_p99", np.nan) for r in rows for v in (r.get("4_health", {}).get("egress") or {}).values()]
    off = [r["run"] for r in rows if r.get("1_load_share", {}).get("ok") is False]
    head = [f"# Suite v3 run checks ({len(rows)} runs)", "",
            f"- runs with load / share off target (marked, kept): {off or 'none'}",
            f"- worst CPU idle: {np.nanmin([x for x in idle if x is not None] or [np.nan])}",
            f"- worst inter-dequeue p99: {np.nanmax(p99 or [np.nan])}", ""]
    (Path(kdir) / "run-checks.md").write_text("\n".join(head) + text.split("\n", 2)[2])
    (Path(kdir) / "rep-compare.md").write_text(rep_compare(kdir, rows))
    import v3_stimuli
    (Path(kdir) / "video-reaction.md").write_text(v3_stimuli.reaction_table(kdir))


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("check", "gate", "summary"):
        print(__doc__)
        return 2
    if argv[0] == "check":
        for rd in argv[1:]:
            print(f"{Path(rd).name}: {line(run_checks(Path(rd)))}")
        return 0
    if argv[0] == "gate":
        verdict, text = gate_report([Path(x) for x in argv[1:]])
        print(text)
        return 0 if verdict else 3
    campaign_summary(Path(argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
