#!/usr/bin/env python3
"""GT3 validation (GT3 spec, sections 1-8) and the parameter sweep on det-*-pfifo-r1.

    python3 scripts/gt3_report.py OUT.md .runs/<campaign> [...]
"""

from __future__ import annotations

import statistics
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402

P = gt3.Params()
SWEEP = {"default": P,
         "delay 5/2.5": replace(P, d_enter_ms=5, d_stay_ms=2.5), "delay 20/10": replace(P, d_enter_ms=20, d_stay_ms=10),
         "loss 5/1.5 %": replace(P, l_enter=0.05, l_stay=0.015), "loss 20/6 %": replace(P, l_enter=0.20, l_stay=0.06),
         "base 5 s": replace(P, base_window_s=5), "base 30 s": replace(P, base_window_s=30),
         "min packets 30": replace(P, min_packets=30), "min packets 100": replace(P, min_packets=100)}
NEG = ("calm030", "calm065", "randloss", "delaystep")
DETS = ("shadow", "gcc", "bbr")
SLACK, RECOVERY = gt1.ONSET_SLACK_S, gt1.BURST_RECOVERY_S
table = gt1._table


def _q(v, q, d=3):
    v = sorted(x for x in v if x is not None and x == x)
    return f"{v[min(len(v) - 1, int(q * len(v)))]:.{d}f}" if v else "-"


def fwd_delay(run: det_eval.Run, sid: str) -> tuple[float, float]:
    """(publisher -> client forward propagation, publisher -> first router) in s, scenario values at t = 0."""
    delay = {(l["from"], l["to"]): (l.get("forward") or {}).get("delay_ms", 0.0) for l in run.scenario.get("links", [])}
    hops = det_eval.path_hops(run, run.pub, sid)
    return sum(delay.get(h, 0.0) for h in hops) / 1000, delay.get(hops[0], 0.0) / 1000


def drift(run: det_eval.Run, sid: str) -> float:
    """Slope (ms/min) of the per-second minimum OWD over the run."""
    t, owd, _, _ = gt3.source_a(run.path, sid)
    sec = np.floor(t).astype(int)
    mins = {}
    for s, v in zip(sec, owd):
        if v == v:
            mins[s] = min(mins.get(s, np.inf), v)
    if len(mins) < 10:
        return float("nan")
    x = np.array(sorted(mins))
    return float(np.polyfit(x / 60, np.array([mins[k] for k in x]), 1)[0])


def events_per_client(run, eps):
    """Per (injected event, exposed client): GT3 episodes of the client overlapping it, and starting in its window."""
    out = []
    for b in gt1._bursts(run.path):
        for s in run.subs:
            if b["hop"] not in det_eval.path_hops(run, run.pub, s):
                continue
            mine = [e for e in eps if e["flow"] == s]
            during = [e for e in mine if e["t_on"] <= b["end"] and e["t_end"] >= b["start"] - SLACK]
            window = [e for e in mine if b["start"] - SLACK <= e["t_on"] <= b["end"] + RECOVERY]
            out.append({"n": len(during), "n_window": len(window),
                        "lag": min(e["t_on"] for e in during) - b["start"] if during else None})
    return out


def worker(run_dir: Path) -> dict:
    run = det_eval.Run(run_dir)
    scn = det_eval.scenario_name(run.path)
    res = {"name": run.path.name, "aqm": run.aqm, "scn": scn, "topo": run.path.parent.name.split("_det-")[-1]}
    res["coverage"] = {s: gt3.coverage(run.path, s) for s in run.subs}
    res["drift"] = {s: drift(run, s) for s in run.subs} if scn == "calm030" else {}
    eps, labels = gt3.run_truth(run, P)
    res["eps"] = eps
    res["events"] = events_per_client(run, eps)
    g2 = gt2.run_truth(run, gt2.Params())[0]
    paths = {s: {f"{a}->{b}" for a, b in det_eval.path_hops(run, run.pub, s)} for s in run.subs}
    res["gt2_unmatched"] = res["gt2_pairs"] = 0
    for e in g2:
        for s in run.subs:
            if e["queue_id"] in paths[s] and e["t_on"] >= det_eval.WARMUP_S:
                res["gt2_pairs"] += 1
                if not any(x["flow"] == s and x["t_on"] <= e["t_end"] and x["t_end"] >= e["t_on"] for x in eps):
                    res["gt2_unmatched"] += 1
    offs = []
    for e in eps:
        near = [g for g in g2 if g["queue_id"] in paths[e["flow"]] and g["t_on"] <= e["t_end"] and g["t_end"] >= e["t_on"]]
        if near:
            g = min(near, key=lambda g: abs(g["t_on"] - e["t_on"]))
            fwd, first = fwd_delay(run, e["flow"])
            offs.append((e["t_on"] - g["t_on"], fwd, first))
    res["offsets"] = offs
    eps_b, _ = gt3.run_truth(run, P, source="B", path_queues=False)
    res["eps_b"] = eps_b
    starts = gt_score.alarm_starts(run, DETS)
    cur = gt3.current(run)
    res["score"] = {"old": gt_score.score(run, gt3.as_view(run, cur), starts, DETS) if cur else None,
                    "GT3": gt_score.score(run, gt3.view_of(run, eps, labels), starts, DETS),
                    "GT3 + path queue": gt_score.score(run, gt3.view_of(run, eps, labels, need_path=True), starts, DETS)}
    res["n_old"] = sum(len(v) for v in cur[0].values()) if cur else 0
    res["dur_old"] = sum(b - a for v in cur[0].values() for a, b in v) if cur else 0.0
    if run.path.name.endswith("-pfifo-r1"):
        res["sweep"] = {}
        for name, p in SWEEP.items():
            e, _ = gt3.run_truth(run, p, path_queues=False)
            res["sweep"][name] = {"n": len(e), "ctrl": sum(1 for x in e if x["flow"] == "sub-ctrl"),
                                  "events": events_per_client(run, e)}
    return res


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    runs = sorted(d for c in argv[1:] for d in Path(c).iterdir() if (d / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    L = [f"# GT3 validation", "", f"{len(res)} runs ({', '.join(Path(c).name for c in argv[1:])}). Defaults: {P.tag()}. "
         "Time axis = send time (OWD bins are indexed by send time). Loss = sent but never timestamped by the client.", ""]

    # 1 coverage
    cov = [(r["name"], s, c) for r in res for s, c in r["coverage"].items()]
    low = [x for x in cov if x[2] < P.min_coverage]
    L += ["## 1. Source A availability (timestamped / sent packets per client)", "",
          f"Clients x runs: {len(cov)}; coverage p1 {_q([c for *_, c in cov], 0.01)}, p50 {_q([c for *_, c in cov], 0.5)}, "
          f"min {min(c for *_, c in cov):.3f}. Below 50 % (source B used): {len(low)}"
          + (": " + ", ".join(f"{n} {s} {c:.2f}" for n, s, c in low) if low else "."), "",
          "Coverage counts lost packets as missing, so it is 1 - loss - untimed."]
    by = defaultdict(list)
    for r in res:
        by[r["aqm"]] += list(r["coverage"].values())
    L += ["", table(["aqm", "coverage p5", "p50", "min"], [[a, _q(v, 0.05), _q(v, 0.5), _q(v, 0)] for a, v in sorted(by.items())]), ""]

    # 2 drift
    rows = [[r["name"], s, f"{v:+.4f}"] for r in res for s, v in r["drift"].items()]
    L += ["## 2. Clock drift on calm030 (slope of the per-second minimum OWD, ms/min; limit 1 ms/min)", "",
          table(["run", "client", "slope (ms/min)"], rows), ""]

    # 3 negatives
    rows = []
    for r in sorted(res, key=lambda r: r["name"]):
        if r["scn"] in NEG:
            c = Counter(e["trigger"] for e in r["eps"])
            rows.append([r["name"], r["aqm"], len(r["eps"]), dict(c) or "-",
                         ", ".join(f"{e['flow']} {e['t_on']:.1f}+{e['duration']:.2f}s {e['trigger']} q{e['peak_q']:.0f} "
                                   f"loss {e['loss_rate']}" for e in r["eps"][:4]) + (" ..." if len(r["eps"]) > 4 else "")])
    L += ["## 3. Runs without injected events (no injected event: a truth episode here is real congestion the scenario did not script (keyframe overflow, AQM drops), not an error; detector false alarms count in CLEAR time only)", "", table(["run", "aqm", "episodes", "triggers", "first episodes"], rows), ""]

    # 4 known events + sub-ctrl
    rows = []
    for r in sorted(res, key=lambda r: r["name"]):
        if r["events"] and r["scn"] in ("burstcap",):
            ev = r["events"]
            rows.append([r["name"], r["aqm"], len(ev), sum(1 for x in ev if x["n"]), sum(1 for x in ev if x["n"] > 1),
                         f"{statistics.mean(x['n_window'] for x in ev):.2f}", _q([x["lag"] for x in ev], 0.5),
                         _q([x["lag"] for x in ev], 0.9)])
    ctrl = [(r["name"], sum(1 for e in r["eps"] if e["flow"] == "sub-ctrl")) for r in res if r["scn"] != "delaystep"]
    L += ["## 4. Known events: burstcap, per scripted event x exposed client", "",
          table(["run", "aqm", "event x client", "with an episode", "split (> 1)", "episodes per event (to end + 2 s)",
                 "lag p50 (s)", "lag p90"], rows), "",
          f"sub-ctrl episodes outside delaystep: {sum(n for _, n in ctrl)} in {sum(1 for _, n in ctrl if n)} runs"
          + (": " + ", ".join(f"{a} {n}" for a, n in ctrl if n) if any(n for _, n in ctrl) else "."), ""]

    # 5 triggers by AQM
    trig = defaultdict(Counter)
    for r in res:
        trig[r["aqm"]].update(e["trigger"] for e in r["eps"])
    L += ["## 5. Trigger by AQM (all GT3 episodes)", "",
          table(["aqm", "episodes", "delay", "loss", "both"],
                [[a, sum(c.values()), *(f"{c[k]} ({100 * c[k] / max(1, sum(c.values())):.0f} %)" for k in ("delay", "loss", "both"))]
                 for a, c in sorted(trig.items())]), ""]

    # 6 agreement with GT1 / GT2
    rows = []
    for a in sorted({r["aqm"] for r in res}):
        rs = [r for r in res if r["aqm"] == a]
        n = sum(len(r["eps"]) for r in rs)
        nopath = sum(1 for r in rs for e in r["eps"] if not e["path_queue_episodes"])
        pairs, unm = sum(r["gt2_pairs"] for r in rs), sum(r["gt2_unmatched"] for r in rs)
        offs = [o for r in rs for o in r["offsets"]]
        rows.append([a, n, f"{nopath} ({100 * nopath / max(1, n):.0f} %)", pairs, f"{unm} ({100 * unm / max(1, pairs):.0f} %)",
                     _q([o for o, *_ in offs], 0.1), _q([o for o, *_ in offs], 0.5), _q([o for o, *_ in offs], 0.9),
                     f"{100 * statistics.mean(o >= f for o, f, _ in offs):.0f} %" if offs else "-",
                     f"{100 * statistics.mean(o >= -first for o, _, first in offs):.0f} %" if offs else "-"])
    L += ["## 6. Agreement with GT1 / GT2", "",
          table(["aqm", "GT3 episodes", "with no GT1 / GT2 queue on the path", "GT2 episode x exposed client",
                 "of those with no GT3 episode", "t_on(GT3) - t_on(GT2) p10 (s)", "p50", "p90",
                 ">= forward path delay", ">= -(publisher -> router delay)"], rows), "",
          "GT3's axis is the send time and GT2's the router's clock: a packet sent at t reaches the first router "
          "after the publisher -> router delay, so on these axes GT3 is expected to lead GT2 by that delay, not to "
          "lag by the path delay.", ""]

    # 7 old vs new
    def pooled(rs, truth, det):
        return gt_score.summarize([r["score"][truth][det] for r in rs if r["score"][truth]])
    rows, moved = [], []
    cells = defaultdict(list)
    for r in res:
        cells[(r["aqm"], r["topo"], r["scn"])].append(r)
    for (a, t, s), rs in sorted(cells.items()):
        for d in DETS:
            o, n, np_ = pooled(rs, "old", d), pooled(rs, "GT3", d), pooled(rs, "GT3 + path queue", d)
            dp = n["precision"] - o["precision"] if n["precision"] == n["precision"] and o["precision"] == o["precision"] else float("nan")
            dr = n["recall"] - o["recall"] if n["recall"] == n["recall"] and o["recall"] == o["recall"] else float("nan")
            cell = [a, t, s, d, o["episodes"], n["episodes"],
                    f"{o['precision']:.2f} -> {n['precision']:.2f} ({np_['precision']:.2f})",
                    f"{o['recall']:.2f} -> {n['recall']:.2f} ({np_['recall']:.2f})",
                    f"{o['latency_p50_ms']:.0f} -> {n['latency_p50_ms']:.0f}"]
            rows.append(cell)
            if abs(dp) > 0.05 or abs(dr) > 0.05:
                moved.append(cell)
    over = []
    for a in sorted({r["aqm"] for r in res}):
        rs = [r for r in res if r["aqm"] == a]
        for d in DETS:
            o, n, np_ = pooled(rs, "old", d), pooled(rs, "GT3", d), pooled(rs, "GT3 + path queue", d)
            over.append([a, d, o["episodes"], n["episodes"], np_["episodes"],
                         f"{o['precision']:.3f} / {n['precision']:.3f} / {np_['precision']:.3f}",
                         f"{o['recall']:.3f} / {n['recall']:.3f} / {np_['recall']:.3f}",
                         f"{o['latency_p50_ms']:.0f} / {n['latency_p50_ms']:.0f} / {np_['latency_p50_ms']:.0f}",
                         f"{o['fa_per_min']:.2f} / {n['fa_per_min']:.2f} / {np_['fa_per_min']:.2f}"])
    hdr = ["aqm", "topology", "scenario", "detector", "episodes old", "GT3", "precision old -> GT3 (GT3 + path)",
           "recall old -> GT3 (GT3 + path)", "latency p50 ms old -> GT3"]
    L += ["## 7. Old (det_eval measured truth) vs GT3, scored with the same rules (gt_score)", "",
          "Per AQM (old / GT3 / GT3 + path queue):", "",
          table(["aqm", "detector", "episodes old", "GT3", "GT3 + path", "precision", "recall", "latency p50 ms", "FA / min"], over), "",
          f"Cells (aqm x scenario x detector) whose precision or recall moves by more than 0.05: {len(moved)} of {len(rows)}", "",
          table(hdr, moved), ""]

    # 8 A vs B
    rows = []
    for a in sorted({r["aqm"] for r in res}):
        na = nb = matched = 0
        diffs = []
        for r in (r for r in res if r["aqm"] == a):
            na += len(r["eps"])
            nb += len(r["eps_b"])
            for e in r["eps"]:
                m = [x for x in r["eps_b"] if x["flow"] == e["flow"] and x["t_on"] <= e["t_end"] and x["t_end"] >= e["t_on"]]
                if m:
                    matched += 1
                    diffs.append(min(x["t_on"] for x in m) - e["t_on"])
        rows.append([a, na, nb, f"{matched} ({100 * matched / max(1, na):.0f} %)", _q(diffs, 0.1), _q(diffs, 0.5), _q(diffs, 0.9)])
    L += ["## 8. Source A (5 ms OWD bins) vs B (frame OWD, delta frames, delay channel only)", "",
          table(["aqm", "episodes A", "episodes B", "A episodes matched by B", "t_on(B) - t_on(A) p10 (s)", "p50", "p90"], rows), ""]

    # sweep
    freeze = [r for r in res if "sweep" in r]
    rows = []
    for name in SWEEP:
        neg = {s: sum(r["sweep"][name]["n"] for r in freeze if r["scn"] == s) for s in NEG}
        ev = [x for r in freeze if r["scn"] != "isolate" for x in r["sweep"][name]["events"]]
        rows.append([name, *neg.values(), f"{sum(1 for x in ev if x['n'])}/{len(ev)}", sum(1 for x in ev if x["n"] > 1),
                     sum(r["sweep"][name]["ctrl"] for r in freeze if r["scn"] != "delaystep"),
                     sum(r["sweep"][name]["n"] for r in freeze)])
    L += ["## Parameter sweep (det-*-pfifo-r1 only)", "",
          table(["variant", *NEG, "event x client caught", "split", "sub-ctrl episodes (not delaystep)", "all episodes"], rows), ""]
    Path(argv[0]).write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
