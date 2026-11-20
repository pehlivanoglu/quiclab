#!/usr/bin/env python3
"""Validation of health_lite.py against the frozen GT-Q health check (user 2026-11-19, W4). Writes nothing into any
run folder: health_lite.check() is called directly; negative tests run on copies outside quiclab/.

    nice -n 19 .venv/bin/python3 simulation/simlab/health_lite_check.py b2 <scratch dir>     # light: B2 + regress-d1
    nice -n 19 .venv/bin/python3 simulation/simlab/health_lite_check.py run300 <scratch dir> # heavy-ish: no campaign

Per run: the frozen verdict (gtq-health.csv gt_q_invalid) next to the light verdict, item by item:
  2 accounting   on runs with the totals file (regress-d1 sample run): totals = tracer-counts.csv, exactly
  3 service      light busy-interval median / share next to the frozen interdeq_within_tol of the same egress
  4 balance      unacked video + lost background - drops
Acceptance: the light check passes on every run where the frozen check passes; every negative test is caught.
Negative tests (copies of the regress-d1 "none" run, which has the totals and no trace):
  truncated sender file   one client's -sent.csv cut in the middle of a line
  missing counter row     one egress's -totals.csv removed
  wrong capacity          the scenario's capacity of one leaf link x 1.25 (the run was simulated at the old value)
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import health_lite as hl  # noqa: E402

RUNS = QUICLAB / "simulation" / "runs"


def frozen(rd: Path) -> dict:
    p = rd / "gtq-health.csv"
    if not p.exists():
        return {}
    return {r["key"]: r["value"] for r in csv.DictReader(p.open())}


def row(rd: Path, label: str) -> dict:
    fz = frozen(rd)
    lt = hl.check(rd)
    out = {"run": label, "frozen_ok": fz.get("gt_q_invalid") == "0" if fz else None, "lite_ok": lt["ok"],
           "items": {k: v["ok"] for k, v in lt.items() if k != "ok"}}
    tc = rd / "router-trace" / "tracer-counts.csv"
    got, _ = hl.totals(rd)
    if got and tc.exists():
        trc = {r["iface"]: r for r in csv.DictReader(tc.open())}
        out["totals_eq_tracer"] = all(str(got[i][k]) == trc[i][k] for i in trc if i in got
                                      for k in ("n_enq", "n_deq", "n_drop"))
        out["totals_compared"] = sorted(set(trc) & set(got))
    svc = lt["3_service_rate"].get("egress", {})
    out["service"] = {i: (v.get("median"), v.get("within_tol"), fz.get(f"{i}.interdeq_within_tol"))
                      for i, v in svc.items() if v.get("busy", 0) >= hl.RATE_MIN_BUSY}
    s4 = lt["4_sender_records"]
    out["balance"] = (s4.get("balance"), s4.get("drops"))
    return out


def negatives(base: Path, scratch: Path) -> list[dict]:
    res = []

    def fresh(name):
        d = scratch / "neg" / name / base.name
        shutil.copytree(base, d)
        return d

    d = fresh("truncated-sender")
    f = sorted((d / "publishers").glob("*/*-sent.csv"))[0]
    raw = f.read_bytes()
    f.write_bytes(raw[: len(raw) // 2 + 7])
    r = hl.check(d)
    res.append({"test": "truncated sender file", "file": f.name, "caught": r["4_sender_records"]["ok"] is False,
                "overall": r["ok"]})

    d = fresh("missing-counter-row")
    f = sorted((d / "router-metrics").glob("*/*-totals.csv"))[0]
    f.unlink()
    r = hl.check(d)
    res.append({"test": "missing counter row", "file": f.name, "caught": r["2_accounting"]["ok"] is False,
                "overall": r["ok"]})

    d = fresh("wrong-capacity")
    plan = json.loads((d / "v3-plan.json").read_text())
    leaf = next(n for n in sorted(plan["egress"]) if n not in ("up",) and plan["egress"][n].get("shaped"))
    a, b = plan["egress"][leaf]["hop"].split("->")
    sc = yaml.safe_load((d / "scenario.yaml").read_text())
    hit = 0
    for ln in sc["links"]:
        if (ln.get("from"), ln.get("to")) == (a, b) and ln.get("forward", {}).get("bandwidth_mbps"):
            ln["forward"]["bandwidth_mbps"] = round(ln["forward"]["bandwidth_mbps"] * 1.25, 3)
            hit += 1
    (d / "scenario.yaml").write_text(yaml.safe_dump(sc, sort_keys=False))
    r = hl.check(d)
    res.append({"test": "wrong capacity (x1.25)", "egress": f"{leaf} {a}->{b}", "links_edited": hit,
                "caught": r["3_service_rate"]["ok"] is False, "overall": r["ok"]})
    return res


def main(argv: list[str]) -> int:
    kind, scratch = argv[0], Path(argv[1])
    scratch.mkdir(parents=True, exist_ok=True)
    rows_ = []
    if kind == "b2":
        prefix = argv[2] if len(argv) > 2 else str(RUNS / "stageB2-applimited") + "/"   # e.g. .../stageB2-streams/streams-
        for ack in ("matched", "spec"):
            for rd in sorted(Path(prefix + ack).iterdir()):
                if (rd / "sim" / "meta.json").exists():
                    rows_.append(row(rd, f"B2 {ack} {rd.name}"))
        for m in ("matched", "sample", "none"):
            for rd in sorted((RUNS / "regress-d1" / m).iterdir()):
                rows_.append(row(rd, f"regress-d1 {m} {rd.name}"))
        neg = negatives(RUNS / "regress-d1" / "none" / "sim-B-A4-hhier-def-pfifo-r1", scratch)
    else:
        rd = RUNS / "scale300" / "sim-Cs-G1-sburst-n300-pfifo-r1"
        rows_.append(row(rd, f"scale300 {rd.name}"))
        neg = []
    (scratch / f"health-lite-check-{kind}.json").write_text(json.dumps({"rows": rows_, "negatives": neg}, indent=1,
                                                                       default=str))
    print("| run | frozen | light | items 1-6 | totals = tracer | busy-rate median / share (frozen interdeq within tol) | balance / drops |")
    print("|---|---|---|---|---|---|---|")
    fail = 0
    for r in rows_:
        items = "".join({True: "o", False: "X", None: "-"}[v] for v in r["items"].values())
        svc = "; ".join(f"{i} {m} / {s} ({f})" for i, (m, s, f) in r["service"].items())
        print(f"| {r['run']} | {r['frozen_ok']} | {r['lite_ok']} | {items} | {r.get('totals_eq_tracer', '-')} | {svc} | "
              f"{r['balance'][0]} / {r['balance'][1]} |")
        if r["frozen_ok"] is not False and not r["lite_ok"]:
            fail += 1
        if r.get("totals_eq_tracer") is False:
            fail += 1
    for n in neg:
        print(f"\nnegative: {n}")
        fail += not n["caught"]
    print(f"\n{'ACCEPT' if not fail else 'NOT ACCEPTED'}: {fail} problem(s)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
