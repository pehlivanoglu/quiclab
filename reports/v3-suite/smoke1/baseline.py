#!/usr/bin/env python3
"""Smoke 1 (classic tracepoints) under the check-4 rules of 2026-11-14 (third version), per
topology: unmatched packets (all traced egresses / bottleneck targets) and recursion_misses per
tracer. Reads the run folders only; writes baseline.json here (the "before" column of the next
smoke report, scripts/v3_suite.py smoke_tracer_compare).

    .venv/bin/python3 reports/v3-suite/smoke1/baseline.py .runs/2026-11-14_1730_v3-smoke
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import v3_gate  # noqa: E402


def summary(kdir: Path) -> dict:
    out = {}
    for rd in sorted(p for p in kdir.iterdir() if p.name.startswith("v3-") and (p / "gtq-health.csv").exists()):
        plan, wins, h = v3_gate._plan(rd), v3_gate._windows(rd), v3_gate._health(rd)
        r = v3_gate.check_health(rd, h, plan, wins)
        eg = r["egress"].values()
        topo = rd.name.split("-")[3] if rd.name.split("-")[2] == "calm" else "sburst-" + rd.name.split("-")[3]
        out[topo] = {
            "run": rd.name, "check4_ok": r["ok"],
            "targets_failing": [f"{v['hop']} ({'4a' if not v['accounting_ok'] else ''}{'4b' if v['service_ok'] is False else ''})"
                                for v in eg if v["ok"] is False],
            "unmatched_deq_all": sum(max(0, v["unmatched_deq"]) for v in eg),
            "unmatched_enq_all": sum(max(0, v["unmatched_enq"]) for v in eg),
            "unmatched_deq_targets": sum(max(0, v["unmatched_deq"]) for v in eg if v["role"] == "target"),
            "unmatched_enq_targets": sum(max(0, v["unmatched_enq"]) for v in eg if v["role"] == "target"),
            "recursion_misses_per_tracer": sorted(set(r["recursion_misses"].values())),
            "tracers": len(r["recursion_misses"])}
    return out


if __name__ == "__main__":
    res = summary(Path(sys.argv[1]))
    (Path(__file__).parent / "baseline.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        print(k, v)
