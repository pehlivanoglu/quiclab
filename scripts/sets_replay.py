#!/usr/bin/env python3
"""Replay check of the frozen SETS v1 configuration (grouping/FREEZE-sets-v1.md) on the v3 runs.

    .venv/bin/python3 scripts/sets_replay.py fixture   # build tests/data/sets_v1_expected.json from the
                                                        # Step 9 / Step 10 outputs (reports/step9-*, step10-*)
    .venv/bin/python3 scripts/sets_replay.py check [.runs/2026-11-14_1818_v3]   # replay every run, compare

The check replays each run's ECG onset log (grouping-d150-v2-owd/onsets.jsonl, detector onsets) through
grouping.SetsEngine with the run's own ECG config, reads the groups at every event close for k = 2 and 3, and
recomputes the Step 10 scores of "O1 + old matching": leaf precision / recall / F1 / exact (best-matching group
per leaf, mean over closes and leaves) and the same-leaf pair counts from each client's smallest group (summed
over closes), plus the end-of-run groups (members, support, mean Jaccard). Everything must equal the stored
Step 9 / Step 10 values; then the pooled pair precision / recall per rep are printed.
"""

from __future__ import annotations

import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIXTURE = ROOT / "tests" / "data" / "sets_v1_expected.json"
KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
CTRL = "sub-ctrl"


def fixture() -> None:
    p1 = {json.loads(x)["run"]: json.loads(x) for x in open(ROOT / "reports/step10-2026-11-15/phase1.jsonl")}
    r10 = {json.loads(x)["run"]: json.loads(x) for x in open(ROOT / "reports/step10-2026-11-15/rows10.jsonl")}
    r9 = {json.loads(x)["run"]: json.loads(x) for x in open(ROOT / "reports/step9-2026-11-15/rows9.jsonl")}
    out = {}
    for run, p in sorted(p1.items()):
        if p["aqm"] == "fq_codel":
            continue
        leaves = {n: v for n, v in p["ordinary"].items() if p["levels"][n] == "leaf"}
        out[run] = {"block": p["block"], "rep": p["rep"], "clients": p["clients"], "leaves": leaves,
                    "true_sets": p["ordinary"], "levels": {n: p["levels"][n] for n in p["ordinary"]}}
        for k in (2, 3):
            s = r10[run]["O1"]["sets"][f"old|{k}|None"]
            out[run][f"k{k}"] = {"pairs": s["pairs"], "leaf": s["levels"].get("leaf"),
                                 "end_groups": [[g["members"], g["support"], g["jaccard"]]
                                                for g in r9[run]["v2-owd"]["detail"][f"quantile|{k}|False"]]}
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"{len(out)} runs -> {FIXTURE}")


def _f1(g, t):
    i = len(g & t)
    if not i:
        return 0.0, 0.0, 0.0
    p, r = i / len(g), i / len(t)
    return p, r, 2 * p * r / (p + r)


def replay_run(args):
    """Scores of one run recomputed from a SetsEngine replay (Step 9 Scorer definitions)."""
    run, exp, kdir = args
    from grouping import Config
    from grouping.sets_engine import replay_log
    gdir = Path(kdir) / run / "grouping-d150-v2-owd"
    cfg = Config.from_dict(json.loads((gdir / "metrics.json").read_text())["config"])
    clients = exp["clients"]
    rank = {c: i for i, c in enumerate(clients)}
    key = lambda g: tuple(sorted((rank[c] for c in g), reverse=True))   # noqa: E731  (Step 9 bitmask order)
    leaves = [frozenset(v) for v in exp["leaves"].values()]
    acc = {k: {"pairs": [0] * 6, "leaf": [0.0] * 4, "n": 0} for k in (2, 3)}

    def on_close(eng, e):
        for k in (2, 3):
            gs = [frozenset(g.members) for g in eng.groups(k)]
            a = acc[k]
            for t in leaves:
                best = max(((_f1(g, t), g) for g in gs), key=lambda z: z[0][2], default=((0.0, 0.0, 0.0), None))
                (p, r, f), g = best
                if g is None:
                    p = 0.0
                for i, v in enumerate((p, r, f, float(g == t))):
                    a["leaf"][i] += v
                a["n"] += 1
            small = {}
            for c in clients:
                cg = [g for g in gs if c in g]
                if cg:
                    small[c] = min(cg, key=lambda g: (len(g), key(g)))
            for i, a_ in enumerate(clients):
                for b_ in clients[i + 1:]:
                    same = any(a_ in t and b_ in t for t in leaves)
                    if a_ not in small or b_ not in small:
                        a["pairs"][4] += 1
                    elif small[a_] == small[b_]:
                        a["pairs"][0 if same else 1] += 1
                    else:
                        a["pairs"][2 if same else 3] += 1

    eng = replay_log(gdir / "onsets.jsonl", cfg, exclude={CTRL}, on_close=on_close)
    out = {"run": run}
    for k in (2, 3):
        a = acc[k]
        out[f"k{k}"] = {"pairs": a["pairs"], "leaf": [x / a["n"] for x in a["leaf"]] if a["n"] else None,
                        "end_groups": [[list(g.members), g.support, round(g.jaccard, 3)] for g in eng.groups(k)]}
    return out


def compare(exp, got, tol=1e-9):
    bad = []
    for k in ("k2", "k3"):
        e, g = exp[k], got[k]
        if [int(x) for x in e["pairs"]] != [int(x) for x in g["pairs"]]:
            bad.append(f"{k} pairs {e['pairs']} != {g['pairs']}")
        if (e["leaf"] is None) != (g["leaf"] is None) or (e["leaf"] and any(abs(a - b) > tol for a, b in zip(e["leaf"], g["leaf"]))):
            bad.append(f"{k} leaf {e['leaf']} != {g['leaf']}")
        if [[sorted(m), s, j] for m, s, j in e["end_groups"]] != [[sorted(m), s, j] for m, s, j in g["end_groups"]]:
            bad.append(f"{k} end groups differ")
    return bad


def check(kdir: Path) -> int:
    exp = json.loads(FIXTURE.read_text())
    with Pool(10) as pool:
        got = {g["run"]: g for g in pool.imap_unordered(replay_run, [(r, e, str(kdir)) for r, e in exp.items()])}
    fails = 0
    for run in sorted(exp):
        bad = compare(exp[run], got[run])
        if bad:
            fails += 1
            print("MISMATCH", run, "; ".join(bad))
    print(f"{len(exp) - fails} of {len(exp)} runs reproduce the Step 9 / Step 10 values exactly")
    for k in ("k2", "k3"):
        for rep in (1, 2):
            p = [sum(got[r][k]["pairs"][i] for r in got if exp[r]["rep"] == rep) for i in range(6)]
            leaf = [got[r][k]["leaf"][2] for r in got if exp[r]["rep"] == rep and got[r][k]["leaf"]]
            print(f"{k} rep {rep}: pair P {p[0] / (p[0] + p[1]):.3f} R {p[0] / (p[0] + p[2]):.3f}; "
                  f"leaf F1 mean over runs {sum(leaf) / len(leaf):.3f}")
    return fails


if __name__ == "__main__":
    if sys.argv[1] == "fixture":
        fixture()
    else:
        sys.exit(1 if check(Path(sys.argv[2]) if len(sys.argv) > 2 else KDIR) else 0)
