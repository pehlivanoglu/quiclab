#!/usr/bin/env python3
"""Validation set for the frozen grouping candidates (user, 2026-11-18, note A). Assigned from the scenario
definition only: the generated plan and topology in <campaign>/_gen (written before the run), the re-run list and
the manifest's health_unverified list. No run output is read.

    python3 reports/npr-2026-11-17/valset.py      # valset.md + valset.json next to this file

Tables:
  main        single-queue (pfifo / codel / pie), >= 2 leaves in the plan's truth, static membership, BBR only
  robustness  the remaining runs with a usable grouping truth (>= 1 truth set of >= 2 clients and a stimulus)
  excluded    re-run list ("not reliable"), health_unverified, the 263 development runs, no grouping truth
"""

from __future__ import annotations

import glob
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAMPS = {"K1": "2026-11-16_0105_v4-K1", "K2": "2026-11-16_0105_v4-K2", "K3": "2026-11-16_0105_v4-K3"}
NEVER_USED = {"K1": ("A1", "A2", "A3", "A8", "A9"), "K2": None, "K3": None}   # None: every block
FQ = ("fq_codel", "cake")
LEVEL = lambda name: {"root": "root", "X": "mid", "Y": "mid", "up": "up"}.get(name, "leaf")   # noqa: E731  (grouping_score)
# scenario types without a congestion stimulus on the clients' path: negatives, no grouping truth
NO_STIMULUS = {"calm", "g-calm", "negcalm", "dclean", "sshortrfc", "rrevasym", "nloss", "neglossh", "rrev",
               "negpriv"}   # negpriv: private capdrops only (no shared group); neglossh = nloss; rrev: reverse path
# membership or event structure not static (user's list: churn, shifting bottleneck, concurrent events)
NOT_STATIC = {"hchurn": "churn", "hjoin": "join", "sjoin": "join", "hshift": "shifting bottleneck",
              "hconc": "concurrent events", "sbnsb": "concurrent events (NSB: both leaves at once)"}


def classify(plan: dict, topo_text: str):
    eg = {n: e for n, e in plan["egress"].items() if e.get("shaped", True) and len(set(e["clients"]) - {"sub-ctrl"}) >= 2}
    leaves = [n for n in eg if LEVEL(n) == "leaf"]
    copa = bool(re.search(r"\bcopa\b", topo_text, re.I)) or "copa" in str(plan.get("variant", "")).lower()
    reasons = []
    if plan["type"] in NO_STIMULUS or not eg:
        return "none", ["no grouping truth (" + (plan["type"] if plan["type"] in NO_STIMULUS else "no truth set") + ")"]
    if plan["aqm"] in FQ:
        reasons.append(f"per-flow queue ({plan['aqm']}, same-link reading)")
    if len(leaves) < 2:
        reasons.append(f"{len(leaves)} leaf")
    if plan["type"] in NOT_STATIC:
        reasons.append(NOT_STATIC[plan["type"]])
    if copa:
        reasons.append("Copa")
    return ("robustness" if reasons else "main"), reasons


def main():
    dev = {json.loads(x)["run"] for x in open(HERE / "rows-v3-E1-0.5.jsonl")}
    rerun = set(re.findall(r"^\| (v4-[^ |]+) \|", (ROOT / "reports/v4-health-2026-11-17/rerun-list.md").read_text(), re.M))
    unver = set()
    for k, c in CAMPS.items():
        txt = (ROOT / ".runs" / c / "manifest.yaml").read_text()
        m = re.search(r"^health_unverified:\n  runs:\n((?:  - .*\n)+)", txt, re.M)
        if m:
            unver |= {(k, x.strip()[2:]) for x in m.group(1).splitlines()}
    rows = []
    for k, c in CAMPS.items():
        for p in sorted(glob.glob(str(ROOT / ".runs" / c / "_gen" / "*-plan.json"))):
            run = os.path.basename(p)[: -len("-plan.json")]
            plan = json.loads(Path(p).read_text())
            blk = plan["block"]
            if NEVER_USED[k] is not None and blk not in NEVER_USED[k]:
                continue
            topo = Path(p.replace("-plan.json", "-topology.yaml"))
            table, why = classify(plan, topo.read_text() if topo.exists() else "")
            if blk == "GATE":
                table, why = "excluded", ["gate run (campaign acceptance, 90 s; not a campaign cell)"]
            elif run in dev:
                table, why = "excluded", ["development run"]
            elif run in rerun:
                table, why = "excluded", ["not reliable (re-run list)"] + ([f"was {table}"] if table != "none" else [])
            elif (k, run) in unver:
                table, why = "excluded", ["health_unverified"] + ([f"was {table}"] if table != "none" else [])
            elif table == "none":
                table = "excluded"
            done = (ROOT / ".runs" / c / run / "v3-checks.json").exists()
            rows.append({"campaign": k, "run": run, "block": blk, "type": plan["type"], "variant": plan.get("variant"),
                         "aqm": plan["aqm"], "rep": plan["rep"], "topology": plan.get("topology"), "table": table,
                         "why": why, "finished": done})
    (HERE / "valset.json").write_text(json.dumps(rows, indent=1))
    out = ["# Validation set (valset.py; from scenario definitions only)\n",
           "Never-used runs only (K1 A1-A3, A8, A9; K2; K3). Assigned from <campaign>/_gen plan + topology, the re-run "
           "list and the manifest's health_unverified list; no run output read. K3 is still running: unfinished runs "
           "are counted (column 'pending').\n"]
    for t, title in (("main", "Main validation: single-queue, >= 2 leaves, static membership, BBR"),
                     ("robustness", "Robustness: other runs with a usable grouping truth")):
        R = [r for r in rows if r["table"] == t]
        reps = sorted({r["rep"] for r in R})
        out.append(f"## {title}\n")
        out.append("Runs per seed: " + ", ".join(f"r{s} {sum(r['rep'] == s for r in R)}" for s in reps) +
                   f"; total {len(R)} (pending {sum(not r['finished'] for r in R)}).\n")
        out.append("| campaign | block | type / variant / aqm | why here | " + " | ".join(f"r{s}" for s in reps) +
                   " | pending |\n|---|---|---|---|" + "---|" * len(reps) + "---|")
        g = defaultdict(list)
        for r in R:
            g[(r["campaign"], r["block"], f"{r['type']} / {r['variant']} / {r['aqm']}", "; ".join(r["why"]) or "-")].append(r)
        for key in sorted(g, key=lambda z: (z[0], z[1], z[2])):
            v = g[key]
            out.append(f"| {' | '.join(key)} | " + " | ".join(str(sum(x['rep'] == s for x in v)) for s in reps) +
                       f" | {sum(not x['finished'] for x in v)} |")
        out.append("")
    E = [r for r in rows if r["table"] == "excluded"]
    out.append("## Excluded\n")
    c = Counter((r["campaign"], "; ".join(r["why"])) for r in E)
    out.append("| campaign | reason | runs |\n|---|---|---|")
    for (k, w), n in sorted(c.items()):
        out.append(f"| {k} | {w} | {n} |")
    out.append("\nExcluded by name (not reliable / health_unverified): " +
               ", ".join(sorted(r["run"] for r in E if r["why"][0] in ("not reliable (re-run list)", "health_unverified"))) + "\n")
    (HERE / "valset.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
