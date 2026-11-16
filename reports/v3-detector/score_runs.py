#!/usr/bin/env python3
"""Suite v3 detector scoring, per run (spec 7.2; existing scorers unchanged).

    .venv/bin/python3 reports/v3-detector/score_runs.py .runs/2026-11-14_1818_v3 [--jobs 12]
        -> reports/v3-detector/rows.jsonl (one line per run), stimuli.jsonl (one line per stimulus window)

Detectors: the frozen Shadow v2 (scripts/shadow_v2_frozen.py: fusion d, hold, loss gate level+cap,
theta_on 0.25, the ip4 floors / scale / G_ref; nothing is refitted on v3):
  v2-owd (primary), v2-fixed-owd, v2-rtt, v2-fixed-rtt.
Truths:
  GT1 (CoDel-style standing queue on a router egress of the client's path), GT2 (demand >= capacity on
  such an egress), GT3 source B (the client's own frame-log OWD / loss impact with a GT1 / GT2 queue on
  its path; source B shares nothing with the ACK timestamps the OWD mode uses), all per client by
  exposure, scored by gt_score (TP = first alarm start in [t_on - 1 s, min(end, t_on + 10 s)], AMBIGUOUS /
  NO_DATA ignored, other alarm starts in CLEAR time are false alarms), plus alarm-on recall (an alarm span
  overlaps that window) and, for GT1 / GT2, hop-level recall (gt_score.hop_score);
  GT-Q / GT-H (scripts/gtq.py labels, written here when missing; scripts/gtq_score.py matching).
Stimulus level: per stimulus window (v3-stimuli.csv), the share of the expected clients whose detector
alarms in [start - 1 s, start + 10 s] (the det_eval window), with the window's measured loads.
"""

from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

DETS = {"v2-owd": ("v2", "OWD"), "v2-fixed-owd": ("v2-fixed", "OWD"), "v2-rtt": ("v2", "RTT"),
        "v2-fixed-rtt": ("v2-fixed", "RTT")}
HERE = Path(__file__).resolve().parent


def alarm_on(view: dict, spans: dict, det: str) -> dict:
    import det_eval as d
    ep = on = 0
    for s, (eps, _) in view.items():
        sp = spans.get((det, s), [])
        for a, b in eps:
            if a < d.WARMUP_S:
                continue
            ep += 1
            lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
            on += any(x <= hi and y >= lo for x, y in sp)
    return {"episodes": ep, "alarm_on": on}


def worker(rd: Path) -> dict:
    import det_eval as d
    import gt1
    import gt2
    import gt3
    import gt_score
    import gtq
    import gtq_score
    import shadow_v2_frozen as fz
    import v3_stimuli
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    # detectors
    starts, spans = {}, {}
    for name, (det, mode) in DETS.items():
        for s, eps in fz.episodes(run, det, mode=mode, hold=True).items():
            starts[(name, s)] = [a for a, _, _ in eps]
            spans[(name, s)] = [(a, b) for a, b, _ in eps]
    # GT1 / GT2 / GT3 (source B)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    hop1 = [(e["hop"], e["start_s"], e["end_s"]) for e in e1]
    hop2 = [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2]
    views = {"GT1": gt_score.client_view(run, hop1, l1), "GT2": gt_score.client_view(run, hop2, l2),
             "GT3": gt3.view_of(run, eb, lb, need_path=True)}
    names = tuple(DETS)
    score = {}
    for t, v in views.items():
        sc = gt_score.score(run, v, starts, names)
        if t in ("GT1", "GT2"):
            hs = gt_score.hop_score(run, hop1 if t == "GT1" else hop2, starts, names)
            for n in names:
                sc[n].update(hs[n])
        for n in names:
            sc[n].update(alarm_on(v, spans, n))
        score[t] = sc
    # GT-Q / GT-H
    gq = None
    if not (rd / "truth" / "gtq-status.csv").exists() and not (rd / "truth" / "gtq.csv").exists():
        gtq.score(rd)
    if (rd / "truth" / "gtq.csv").exists():
        gtq_score.DETECTORS = names
        res = gtq_score.score_run(rd, starts)
        if res is not None:
            gq = {"episodes": res[0], "tallies": res[1]}
    status = d.rows(rd / "truth" / "gtq-status.csv")[0] if (rd / "truth" / "gtq-status.csv").exists() else {}
    # stimulus level
    stim = []
    try:
        for w in v3_stimuli.load(rd):
            exp = json.loads((rd / "grouping" / "windows.json").read_text())
            win = next((x for x in exp if abs(x["start"] - w["start"]) < 1e-6 and x["target"] == w["target"]), None)
            clients = (win or {}).get("expected", [])
            hits = {n: sum(any(w["start"] - d.PRE_ONSET_LEAD_S <= a <= w["start"] + d.SEARCH_S
                               for a in starts.get((n, c), [])) for c in clients) for n in names}
            stim.append({**w, "run": rd.name, "clients": len(clients), "hit": hits})
    except Exception as e:  # noqa: BLE001
        stim.append({"run": rd.name, "error": repr(e)})
    parts = rd.name.split("-")
    return {"run": rd.name, "block": parts[1], "type": parts[2], "variant": parts[3], "aqm": parts[4],
            "rep": int(parts[5][1:]), "topology": plan["topology"], "s": plan["s"], "U": plan["U"],
            "bg_mode": plan["bg_mode"], "duration_s": run.duration, "clients": len(run.subs),
            "score": score, "gtq": gq, "gtq_status": status, "stimuli": stim,
            "events": {"GT1": len([e for e in e1 if e["start_s"] >= d.WARMUP_S]),
                       "GT2": len([e for e in e2 if e["t_on"] >= d.WARMUP_S])}}


def _json(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(type(o))


def main(argv: list[str]) -> None:
    kdir = Path(argv[0])
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 12
    runs = sorted(p for p in kdir.iterdir() if p.is_dir() and p.name.startswith("v3-"))
    out, bad = [], []
    with ProcessPoolExecutor(jobs) as ex:
        for rd, fut in [(rd, ex.submit(worker, rd)) for rd in runs]:
            try:
                out.append(fut.result())
                print(f"{rd.name} ok", flush=True)
            except Exception as e:  # noqa: BLE001
                bad.append((rd.name, repr(e)))
                print(f"{rd.name} FAILED {e!r}", flush=True)
    with (HERE / "rows.jsonl").open("w") as fh:
        for r in out:
            st = r.pop("stimuli")
            fh.write(json.dumps(r, default=_json) + "\n")
            r["stimuli"] = st
    with (HERE / "stimuli.jsonl").open("w") as fh:
        for r in out:
            for w in r["stimuli"]:
                fh.write(json.dumps(w, default=_json) + "\n")
    print(f"{len(out)} runs scored, {len(bad)} failed: {bad}")


if __name__ == "__main__":
    main(sys.argv[1:])
