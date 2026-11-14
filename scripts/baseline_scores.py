#!/usr/bin/env python3
"""Reference numbers on the development set (read-only; no engine or detector change):

    python3 scripts/baseline_scores.py detector CAMPAIGN OUT/detector-rows.jsonl     # one row per run
    python3 scripts/baseline_scores.py detector-summary OUT/detector-rows.jsonl.gz
    python3 scripts/baseline_scores.py detector-runs OUT/detector-rows.jsonl.gz      # one line per run
    python3 scripts/baseline_scores.py ecg CAMPAIGN OUT/ecg-rows.jsonl              # v2-owd only, parallel
    python3 scripts/baseline_scores.py ecg-summary OUT/ecg-rows.jsonl.gz

detector: the frozen Shadow v2 (scripts/shadow_v2_frozen.py: fusion d, hold, loss
gate level+cap, theta_on 0.25, ip4 fit) on the RTT ticks ("v2") and on the OWD
ticks ("v2-owd"), scored with scripts/gt_score.py against GT1, GT2 (link views)
and GT3 (client OWD + loss episodes with a GT1 / GT2 queue on the path) (a client sees the episodes / labels of the router egresses on its
path), defaults of the canonical truth settings. Development set only: every
campaign directory whose name does not start with N (never N1-N5).
ecg: ECG v1.2 (Config defaults, delta 0.150 s since 2026-11-11) on the v2-owd onsets
(grouping_adapter.process, outputs in <run>/grouping-d150-v2-owd/): leaf precision / recall, coverage, final
tree correct, events a flow took part in before membership; per campaign x AQM,
primary onset source v2-owd.
"""

from __future__ import annotations

import argparse
import gzip
import json
import statistics
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_flowbot  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_frozen  # noqa: E402

TRUTHS = ("GT1", "GT1 interval 350", "GT1 per-queue", "GT1 per-queue interval 350", "GT2", "GT2 P_on 350", "GT3", "FlowBot GT")
SOURCES = {"v2 (RTT)": ("v2", "RTT"), "v2-owd (OWD)": ("v2", "OWD")}


def dev_run_dirs(campaign: Path) -> list[Path]:
    return [rd for g in sorted(campaign.iterdir()) if g.is_dir() and not g.name.startswith("N")
            for rd in sorted(g.glob("grp-*")) if (rd / "events.csv").exists()]


def read_jsonl(path: Path) -> list[dict]:
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return [json.loads(line) for line in fh]


def per_flow_view(run, eps: list[dict], labs: list[dict], flow: dict) -> dict | None:
    """GT1 client view where every pinned fq_codel / cake egress contributes the client's
    own queue (flow = gt1.run_flow_labels) and every other egress its aggregate queue.
    None when the run has no per-flow record."""
    if not flow:
        return None
    pinned = {k.split("|")[0] for k in flow}
    out = {}
    for s in run.subs:
        sid = run.sid_of.get(s, s) if hasattr(run, "sid_of") else s
        hops = [f"{a}->{b}" for a, b in d.path_hops(run, run.pub, s)]
        ep = [(e["hop"], e["start_s"], e["end_s"]) for e in eps if e["hop"] in hops and e["hop"] not in pinned]
        lb = [x for x in labs if x["hop"] in hops and x["hop"] not in pinned]
        for h in hops:
            if h in pinned and f"{h}|{sid}" in flow:
                fe, fl = flow[f"{h}|{sid}"]
                ep += [(h, e["start_s"], e["end_s"]) for e in fe]
                lb += [{**x, "hop": h} for x in fl]
        out[s] = gt_score.client_view(run, ep, lb)[s]
    return out


def detector_row(rd: Path) -> dict:
    run = ga.load_run(rd)
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params())
    e1l, l1l = gt1.run_truth(run, gt1.Params(interval_s=0.35))
    e2l, l2l = gt2.run_truth(run, gt2.Params(p_on=0.35))
    views = {"GT1": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             "GT1 interval 350": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1l], l1l),
             "GT2 P_on 350": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2l], l2l),
             "GT2": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2),
             # GT3: the client's own OWD + loss episodes that coincide with a GT1 / GT2 queue on its path
             # (the canonical "GT3 + path queue" view of the Shadow v2 reports)
             "GT3": gt3.view_of(run, e3, l3, need_path=True)}
    ef, lf = gt_flowbot.run_truth(run)
    views["FlowBot GT"] = gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in ef], lf)
    for tag, prm, (ee, ll) in (("GT1 per-queue", gt1.Params(), (e1, l1)),
                               ("GT1 per-queue interval 350", gt1.Params(interval_s=0.35), (e1l, l1l))):
        v = per_flow_view(run, ee, ll, gt1.run_flow_labels(run, prm))
        if v is not None:
            views[tag] = v
    out = {"campaign": rd.parent.name, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "score": {}}
    for label, (det, mode) in SOURCES.items():
        try:
            eps = shadow_v2_frozen.episodes(run, det, mode=mode, hold=True)
        except Exception as e:   # noqa: BLE001 - one missing tick file must not drop the run
            out["score"][label] = {"error": repr(e)}
            continue
        starts = {(label, s): [a for a, _, _ in spans] for s, spans in eps.items()}
        out["score"][label] = {truth: gt_score.score(run, view, starts, (label,))[label] for truth, view in views.items()}
    return out


def cmd_detector(campaign: Path, out_path: Path, procs: int) -> None:
    runs = dev_run_dirs(campaign)
    with Pool(procs) as pool, out_path.open("w") as out:
        for row in pool.imap_unordered(detector_row, runs):
            out.write(json.dumps(row, default=float) + "\n")
            out.flush()
            print(row["run"], flush=True)


ECG_DIR = "grouping-d150-v2-owd"   # separate output dir: the campaign's own grouping-* dirs are left as they are


def ecg_row(rd: Path) -> dict:
    from argparse import Namespace
    from grouping import Config
    cfg = Config.from_dict({"theta_J": 0.6, "theta_cov": 0.6})   # the campaign's ENGINE_SET (no effect in v1.2)
    a = Namespace(out=ECG_DIR, onsets="v2-owd", backdate_max=1.0, backdate_qd_ms=10.0, warmup=d.WARMUP_S,
                  spread_only=False)
    row = {"campaign": rd.parent.name, "run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2],
           "delta": cfg.delta}
    try:
        row["ecg"] = ga.process(rd, cfg, a)
    except Exception as e:   # noqa: BLE001
        row["ecg"] = {"error": repr(e)}
    return row


def cmd_ecg(campaign: Path, out_path: Path, procs: int) -> None:
    runs = [rd for rd in dev_run_dirs(campaign) if (rd / "grouping" / "windows.json").exists()]
    with Pool(procs) as pool, out_path.open("w") as out:
        for row in pool.imap_unordered(ecg_row, runs):
            out.write(json.dumps(row, default=str) + "\n")
            out.flush()
            print(row["run"], "error" if "error" in row["ecg"] else "ok", flush=True)


def fam(aqm: str) -> str:
    return "FIFO-like (pfifo/red/pie/codel)" if aqm in ("pfifo", "red", "pie", "codel") else aqm


def fmt(x, f=".2f"):
    return "-" if x is None or x != x else format(x, f)


def cmd_detector_summary(path: Path) -> None:
    R = read_jsonl(path)
    print("# Detector baselines on the development set (frozen Shadow v2, RTT vs OWD ticks)\n")
    print(f"{len(R)} runs. Scored with gt_score (detected = an alarm start in [t_on - 1 s, min(t_end, t_on + 10 s)]; "
          "false alarm = an alarm start in CLEAR time; AMBIGUOUS ignored).\n")
    for key, title in ((lambda r: fam(r["aqm"]), "AQM family"), (lambda r: r["campaign"], "campaign")):
        print(f"## By {title}\n")
        print("| group | source | truth | runs | episodes | recall | precision | FA / CLEAR min | latency p50 / p90 ms "
              "| recall < 0.5 s / 0.5-1 / 1-2 / >= 2 s | run mean recall / precision |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        by = defaultdict(list)
        for r in R:
            by[key(r)].append(r)
        for g in sorted(by):
            for src in SOURCES:
                for truth in TRUTHS:
                    t = [r["score"][src][truth] for r in by[g] if truth in r["score"].get(src, {})]
                    if not t:
                        continue
                    s = gt_score.summarize(t)
                    per = [gt_score.summarize([x]) for x in t]
                    mr = [p["recall"] for p in per if p["recall"] == p["recall"]]
                    mp = [p["precision"] for p in per if p["precision"] == p["precision"]]
                    print(f"| {g} | {src} | {truth} | {len(t)} | {s['episodes']} | {fmt(s['recall'])} | {fmt(s['precision'])} "
                          f"| {fmt(s['fa_per_min'])} | {fmt(s['latency_p50_ms'], '.0f')} / {fmt(s['latency_p90_ms'], '.0f')} "
                          f"| {' / '.join(fmt(x) for x in s['bin_recall'])} "
                          f"| {fmt(statistics.mean(mr) if mr else None)} / {fmt(statistics.mean(mp) if mp else None)} |")
        print()
    errs = [(r["run"], src) for r in R for src, v in r["score"].items() if "error" in v]
    if errs:
        print(f"Errors: {errs}\n")


def cmd_detector_runs(path: Path) -> None:
    """One line per run: recall / precision / false alarms per CLEAR minute / latency p50 / p90 for
    GT1, GT2, GT3 (OWD ticks = v2-owd, the primary source), then the RTT ticks for comparison."""
    R = sorted(read_jsonl(path), key=lambda r: (r["campaign"], r["run"]))
    for src in SOURCES:
        print(f"## {src}: per run\n")
        print("recall / precision / false alarms per CLEAR minute / latency p50 / p90 ms\n")
        print("| campaign | run | " + " | ".join(TRUTHS) + " |\n|" + "---|" * (len(TRUTHS) + 2))
        for r in R:
            cells = []
            for truth in TRUTHS:
                t = r["score"].get(src, {}).get(truth)
                if not t:
                    cells.append("-")
                    continue
                s_ = gt_score.summarize([t])
                cells.append(f"{fmt(s_['recall'])} / {fmt(s_['precision'])} / {fmt(s_['fa_per_min'])} / "
                             f"{fmt(s_['latency_p50_ms'], '.0f')} / {fmt(s_['latency_p90_ms'], '.0f')}")
            print(f"| {r['campaign']} | {r['run']} | " + " | ".join(cells) + " |")
        print()


def cmd_ecg_summary(path: Path) -> None:
    R = read_jsonl(path)
    errs = [r["run"] for r in R if "error" in r["ecg"]]
    print("# ECG v1.2 baselines (delta 0.150 s, v2-owd onsets, GT1 truth, development set)\n")
    print(f"{len(R)} runs scored ({len(errs)} errors{': ' + ', '.join(errs) if errs else ''}). Leaf P / R and coverage: "
          "medians over runs; tree correct and false SAME pairs: counts; events to membership: median over every "
          "(run, flow) that became a member. Negatives (G0) have no truth pairs: only false SAME pairs count there.\n")
    print("| campaign | AQM | runs | leaf P | leaf R | coverage | tree correct | false SAME pairs | events to membership p50 |")
    print("|---|---|---|---|---|---|---|---|---|")
    groups = defaultdict(lambda: defaultdict(list))
    for r in R:
        if "error" not in r["ecg"]:
            groups[r["campaign"]][r["aqm"]].append(r["ecg"])
    for g in sorted(groups):
        for aqm, es in sorted(groups[g].items()):
            def med(key):
                v = [x[key] for x in es if x.get(key) is not None]
                return statistics.median(v) if v else None
            ev = [n for x in es for n in (x.get("membership_events") or {}).values()]
            print(f"| {g} | {aqm} | {len(es)} | {fmt(med('precision'))} | {fmt(med('recall'))} | {fmt(med('coverage'))} "
                  f"| {sum(bool(x.get('tree_correct')) for x in es)}/{len(es)} | {sum(x.get('fp') or 0 for x in es)} "
                  f"| {fmt(statistics.median(ev) if ev else None, '.0f')} |")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("detector", "detector-summary", "detector-runs", "ecg", "ecg-summary"))
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args(argv)
    if a.cmd == "detector":
        cmd_detector(a.paths[0], a.paths[1], a.procs)
    elif a.cmd == "detector-runs":
        cmd_detector_runs(a.paths[0])
    elif a.cmd == "ecg":
        cmd_ecg(a.paths[0], a.paths[1], a.procs)
    elif a.cmd == "detector-summary":
        cmd_detector_summary(a.paths[0])
    else:
        cmd_ecg_summary(a.paths[0])


if __name__ == "__main__":
    main(sys.argv[1:])
