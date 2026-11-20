#!/usr/bin/env python3
"""D1: every false split of STEP 2 (old test npr_v1, original event order, alpha 0.05 and the other alphas noted),
both formations. Per false split: the leaf, the two halves by client with access delay (plan access_delay_ms) and
bitrate (topology rate_kbps), the events whose half-profiles differ up to the first accepting read (the evidence),
and for each such event whether the leaf's 0-members have their onset in a later event within LATE_S of this
event's close (cut by the event window: late responders)."""
import json, sys
from pathlib import Path
import numpy as np
import yaml
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "scripts"), str(ROOT)]
import npr_v1 as npr
import step12
LATE_S = 1.0   # (M) "falls into the next event"


def first_split(seq, mem):
    rd = npr.Reader(mem)
    for i, e in enumerate(seq):
        rd.add(step12.matrix_col(e, mem))
        r = rd.read((0.05, 0.01, 0.1))
        g = r["groups"][0.05]
        if len(g) > 1:
            return i, g, r
    return None, None, None


def main():
    src = [json.loads(x) for x in open(ROOT / "reports/npr-step0b-2026-11-17/rows.jsonl")]
    out = []
    for cand in ("E1-0.5", "E3"):
        res = {json.loads(x)["run"]: json.loads(x) for x in open(HERE / f"rows-{cand}.jsonl")}
        for row in src:
            r = res.get(row["run"])
            if not r:
                continue
            for c in r.get("calibration", []):
                if c["perm"] != 0 or not c["split_0.05"]:
                    continue
                mem = sorted(row["truth"][c["leaf"]]["members"])
                ev = [e for e in row["cands"][cand] if e["ones"] and set(e["ones"]) & set(mem)]
                sub = [{**e, "ones": [x for x in e["ones"] if x in mem], "na": {x: y for x, y in e["na"].items() if x in mem}}
                       for e in ev]
                i, groups, _ = first_split(sub, mem)
                if i is None:
                    continue
                halves = [g for g in groups if len(g) < len(mem)]
                h1 = set(halves[0]) if halves else set()
                rd = ROOT / ".runs" / row["campaign"] / row["run"]
                topo = yaml.safe_load((rd / "topology.yaml").read_text())
                plan = json.loads((rd / "v3-plan.json").read_text())
                acc = plan.get("access_delay_ms", {})
                cl = {x: {"half": 1 if x in h1 else 2, "access_ms": acc.get(x),
                          "rate_kbps": topo["subscribers"].get(x, {}).get("rate_kbps")} for x in mem}
                evid = []
                for j, e in enumerate(sub[:i + 1]):
                    z = []
                    for half in (h1, set(mem) - h1):
                        xs = [1 if x in e["ones"] else None if x in e["na"] else 0 for x in half]
                        nn = [v for v in xs if v is not None]
                        z.append(None if not nn else int(sum(nn) >= len(nn) / 2))
                    if None in z or z[0] == z[1]:
                        continue
                    zeros = [x for x in mem if x not in e["ones"] and x not in e["na"]]
                    later = [x for x in zeros if any(x in f["ones"] and e["t0"] < f["t0"] <= e["close"] + LATE_S
                                                     for f in ev[j + 1:j + 6])]
                    evid.append({"t0": e["t0"], "ones": e["ones"], "zeros": zeros, "na": sorted(e["na"]),
                                 "zeros_in_next_event": later})
                out.append({"formation": cand, "run": row["run"], "aqm": row["aqm"], "leaf": c["leaf"], "size": len(mem),
                            "whole_run": c["whole_run"], "split_at_event": i + 1, "events": len(sub),
                            "split_0.01": c["split_0.01"], "clients": cl, "evidence": evid})
    (HERE / "d1-false-splits.json").write_text(json.dumps(out, indent=1))
    print(len(out), "false splits")


if __name__ == "__main__":
    main()
