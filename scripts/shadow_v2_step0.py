#!/usr/bin/env python3
"""Shadow v2, Step 0: where and why shadow v1 is weak, every number from this script.

    python3 scripts/shadow_v2_step0.py OUT_PREFIX .runs/<campaign> [...]
    # OUT_PREFIX.md (report), OUT_PREFIX-baseline.csv, OUT_PREFIX-false-alarms.csv;
    # per freeze run (det-*-pfifo-r1): <run>/shadow-v2/v1-samples/<sub>.csv (v1 per-ACK state, no grouping)

Sections: 0.1 replay repeatability; 0.2 baseline table (detectors x grouping
"topology" (oracle) / "none" x GT1 / GT2 / GT3); 0.3 weak cells; 0.4 latency
decomposition (observability floor = first ACK of a packet sent at or after
t_on); 0.5 warning margin before harm (harm = first frame missing its playout
deadline with the 600 ms buffer, client frames.csv late_us > 0); 0.6 false
alarms (CLEAR time under GT3); 0.7 the verified ("confirmed") layer; 0.8 ACK
spacing (the physical floor for any detector).

Detectors: v1 = det_eval.TUNED (shadow, shadow_verified), shadow_m4, gcc on the
m4 replay, gcc on the tuned replay ("tuned:gcc", pure GCC rule), bbr, and the
single-signal variants. Scoring: gt_score (TP = first alarm in [t_on - 1 s,
min(end, t_on + 10 s)], AMBIGUOUS / NO_DATA ignored, CLEAR = FP).
"""

from __future__ import annotations

import csv
import statistics
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_bands  # noqa: E402
import gt_score  # noqa: E402

DETS = {"shadow": ("tuned:full", "pre_signal_on"), "shadow_verified": ("tuned:full", "verified_on"),
        "shadow_m4": ("full", "pre_signal_on"), "gcc": ("gcc", "pre_signal_on"),
        "gcc_tuned": ("tuned:gcc", "pre_signal_on"), "bbr": ("", "bbr_bw_drop"),
        **{v: (v, "pre_signal_on") for v in d.VARIANTS[2:]}}
MAIN = ("shadow", "shadow_verified", "shadow_m4", "gcc", "gcc_tuned", "bbr")
GROUPINGS = ("none", "topology")
TRUTHS = ("GT1", "GT2", "GT3")
WEAK = [("fq_codel", "burstudp"), ("fq_codel", "tcpcubic"), ("fq_codel", "tcpbbr"), ("fq_codel", "onoff"),
        ("fq_codel", "splitudp"), ("pfifo", "burstcapshallow"), ("red", "tcpcubic"), ("pfifo", "burstlong"),
        ("pfifo", "calm090")]
HARM_TAIL_S = 2.0


def events_of(run, grouping):
    ev = [{**e, "variant": f"tuned:{e['variant']}"} for e in d.replay(run, d.TUNED, grouping=grouping) if e["variant"]]
    return ev + d.replay(run, d.PARAMS, grouping=grouping)


def starts_of(ev, subs):
    out = defaultdict(list)
    for e in ev:
        for name, (variant, kind) in DETS.items():
            if e["variant"] == variant and e["event"] == kind:
                out[(name, e["subscriber"])].append(e["t"])
    return out


def first_ack_after(run, sid, t_on_list):
    """Per onset: run time of the first ACK whose acked packet was sent at or after t_on."""
    acks = d.rows(run.sender_file(sid, "acks"))
    sent = np.array([run.t_mono_us(int(r["sent_mono_us"])) for r in acks])
    ack = np.array([run.t_mono_us(int(r["mono_us"])) for r in acks])
    order = np.argsort(sent)
    sent, ack = sent[order], ack[order]
    out = []
    for t in t_on_list:
        k = np.searchsorted(sent, t)
        out.append(float(np.min(ack[k:k + 200])) if k < len(ack) else None)
    return out


def harm_times(run, sid):
    """Run times of playout deadlines missed (frame late_us > 0)."""
    out = []
    for r in d.rows(run.path / "clients" / f"{sid}-frames.csv"):
        late = int(r["late_us"] or 0)
        if late > 0:
            out.append(run.t_unix_us(int(r["recv_us"]) - late))
    return sorted(out)


def worker(run_dir: Path) -> dict:
    run = d.Run(run_dir)
    res = {"name": run.path.name, "aqm": run.aqm, "scn": d.scenario_name(run.path),
           "topo": run.path.parent.name.split("_det-")[-1], "score": {}, "repeat": None}
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params(), path_queues=False)
    views = {"GT1": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             "GT2": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2),
             "GT3": gt3.view_of(run, e3, l3)}
    evs = {g: events_of(run, g) for g in GROUPINGS}
    for g in GROUPINGS:
        st = starts_of(evs[g], run.subs)
        for t in TRUTHS:
            res["score"][(g, t)] = gt_score.score(run, views[t], st, tuple(DETS))
    if run.path.name.endswith("-pfifo-r1"):
        res["repeat"] = evs["none"][:len(evs["none"])] == events_of(run, "none")
    ev = evs["none"]
    st = starts_of(ev, run.subs)
    gt3_code = {s: views["GT3"][s][1] for s in run.subs}
    # 0.4 latency decomposition and 0.5 harm margin, shadow (no grouping) vs GT3
    decomp, margins, alarms_per_ep = [], [], []
    for s in run.subs:
        eps = [(e["t_on"], e["t_end"]) for e in e3 if e["flow"] == s and e["t_on"] >= d.WARMUP_S]
        if not eps:
            continue
        floors = first_ack_after(run, s, [a for a, _ in eps])
        harms = harm_times(run, s)
        alarms = sorted(st.get(("shadow", s), []))
        for (a, b), fl in zip(eps, floors):
            hit = next((x for x in alarms if a - d.PRE_ONSET_LEAD_S <= x <= min(b, a + d.SEARCH_S)), None)
            alarms_per_ep.append((b - a, sum(1 for x in alarms if a - d.PRE_ONSET_LEAD_S <= x <= b)))
            if hit is not None and fl is not None and hit >= a:
                decomp.append((fl - a, hit - fl, hit - a))
            harm = next((h for h in harms if a <= h <= b + HARM_TAIL_S), None)
            if harm is not None:
                margins.append((harm - a, None if hit is None else harm - hit))
    # 0.6 false alarms, 0.7 verified layer
    fas, verified = [], Counter()
    on = [e for e in ev if e["variant"] == "tuned:full" and e["event"] == "pre_signal_on" and e["t"] >= d.WARMUP_S]
    ver = [e for e in ev if e["variant"] == "tuned:full" and e["event"] == "verified_on" and e["t"] >= d.WARMUP_S]
    for e in on:
        s, t = e["subscriber"], e["t"]
        in_ep = any(x["flow"] == s and x["t_on"] - d.PRE_ONSET_LEAD_S <= t <= x["t_end"] for x in e3)
        code = gt3_code[s][min(len(gt3_code[s]) - 1, int(t / gt_score.GRID_S))]
        cls = "in GT3 episode" if in_ep else {0: "CLEAR", 1: "AMBIGUOUS", -1: "NO_DATA", 2: "in GT3 episode"}[int(code)]
        nxt = next((v["t"] for v in ver if v["subscriber"] == s and t <= v["t"] <= t + 3.0), None)
        verified[(cls, nxt is not None)] += 1
        if cls == "CLEAR":
            near = [x for x in e3 if x["flow"] == s]
            gap = min((min(abs(t - x["t_on"]), abs(t - x["t_end"])) for x in near), default=float("nan"))
            fas.append({"run": run.path.name, "aqm": run.aqm, "scenario": res["scn"], "client": s, "t": t,
                        "evidence": e.get("evidence", ""), "verified": int(nxt is not None),
                        "gt1_episode_on_path": int(any(x["start_s"] <= t <= x["end_s"] for x in e1)),
                        "s_to_nearest_gt3_episode": round(gap, 3), "t_mod_gop_s": round(t % 1.0, 3)})
    res.update(decomp=decomp, margins=margins, alarms_per_ep=alarms_per_ep, fas=fas, verified=verified)
    # 0.8 ACK spacing
    gaps = []
    for s in run.subs:
        m = np.array([int(r["mono_us"]) for r in d.rows(run.sender_file(s, "acks"))]) / 1000
        if len(m) > 1:
            gaps.append((s, float(np.median(np.diff(m))), float(np.percentile(np.diff(m), 90))))
    res["ack_gaps"] = gaps
    # raw v1 per-ACK state on the freeze set (Step 1 input)
    if run.path.name.endswith("-pfifo-r1"):
        d.replay(run, d.TUNED, samples_to=run.path / "shadow-v2" / "v1-samples", grouping="none")
    return res


def _f(x, k=2):
    return "-" if x is None or x != x else f"{x:.{k}f}"


def _q(v, q, k=0, scale=1.0):
    v = sorted(x for x in v if x is not None and x == x)
    return "-" if not v else f"{v[min(len(v) - 1, int(q * len(v)))] * scale:.{k}f}"


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    prefix = Path(argv[0])
    runs = sorted(r for c in argv[1:] for r in Path(c).iterdir() if (r / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    T = gt1._table
    L = ["# Shadow v2 Step 0: v1 baseline", "", f"{len(res)} runs. Truth defaults: GT1 {gt1.Params().tag()}; "
         f"GT2 {gt2.Params().tag()}; GT3 {gt3.Params().tag()}. v1 = det_eval.TUNED. Reference grouping for v2 = none.", ""]

    rep = [r["repeat"] for r in res if r["repeat"] is not None]
    L += ["## 0.1 Replay repeatability", "", f"det-*-pfifo-r1 runs replayed twice (no grouping): identical event lists "
          f"in {sum(rep)}/{len(rep)}.", ""]

    def pooled(rs, g, t, det):
        return gt_score.summarize([r["score"][(g, t)][det] for r in rs])

    hdr = ["truth", "grouping", "detector", "episodes", "precision", "recall", "recall >= 1 s",
           "latency p50 after t_on (ms)", "latency p90", "share alarmed before t_on", "FA / min CLEAR"]
    rows, csv_rows = [], []
    for t in TRUTHS:
        for g in GROUPINGS:
            for det in DETS:
                s = pooled(res, g, t, det)
                row = [t, g, det, s["episodes"], _f(s["precision"]), _f(s["recall"]), _f(s["recall_long"]),
                       _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0), _f(s["early_share"]),
                       _f(s["fa_per_min"])]
                csv_rows.append(["all", *row])
                if det in MAIN:
                    rows.append(row)
    for aqm in sorted({r["aqm"] for r in res}):
        for t in TRUTHS:
            for g in GROUPINGS:
                for det in DETS:
                    s = pooled([r for r in res if r["aqm"] == aqm], g, t, det)
                    csv_rows.append([aqm, t, g, det, s["episodes"], _f(s["precision"]), _f(s["recall"]),
                                     _f(s["recall_long"]), _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0),
                                     _f(s["early_share"]), _f(s["fa_per_min"])])
    L += ["## 0.2 Baseline (all runs pooled; per AQM and single-signal variants in the CSV)", "", T(hdr, rows), ""]

    rows = []
    for aqm, scn in WEAK:
        rs = [r for r in res if r["aqm"] == aqm and r["scn"] == scn]
        if not rs:
            continue
        for det in ("shadow", "gcc_tuned", "bbr"):
            for g in GROUPINGS:
                s = pooled(rs, g, "GT3", det)
                rows.append([f"{scn} {aqm}", det, g, _f(s["precision"]), _f(s["recall"]),
                             _f(s["late_latency_p50_ms"], 0), _f(s["fa_per_min"])])
    ds = [r for r in res if r["scn"] == "delaystep"]
    L += ["## 0.3 Weak cells (GT3)", "", T(["cell", "detector", "grouping", "precision", "recall", "latency p50 (ms)",
                                            "FA / min"], rows), "",
          "delaystep FA / min CLEAR under GT3, no grouping: " + ", ".join(
              f"{det} {_f(pooled(ds, 'none', 'GT3', det)['fa_per_min'])}" for det in ("shadow", "gcc_tuned", "bbr")), ""]
    long = [(dur, n) for r in res if r["scn"] == "burstlong" for dur, n in r["alarms_per_ep"]]
    L += ["Flapping, burstlong, shadow (no grouping): alarm starts per GT3 episode "
          f"p50 {_q([n for _, n in long], 0.5)}, p90 {_q([n for _, n in long], 0.9)}, max {_q([n for _, n in long], 1.0)}; "
          f"per minute of episode {sum(n for _, n in long) / max(1e-9, sum(x for x, _ in long) / 60):.1f}.", ""]

    rows = []
    for aqm in sorted({r["aqm"] for r in res}):
        dc = [x for r in res if r["aqm"] == aqm for x in r["decomp"]]
        rows.append([aqm, len(dc), _q([x[0] for x in dc], 0.5, 0, 1000), _q([x[0] for x in dc], 0.9, 0, 1000),
                     _q([x[1] for x in dc], 0.5, 0, 1000), _q([x[1] for x in dc], 0.9, 0, 1000),
                     _q([x[2] for x in dc], 0.5, 0, 1000), _q([x[2] for x in dc], 0.9, 0, 1000)])
    L += ["## 0.4 Latency decomposition (shadow, no grouping, GT3 episodes detected after t_on)", "",
          "floor = first ACK of a packet sent at or after t_on, minus t_on (no detector can know earlier); "
          "decision = alarm - that ACK.", "",
          T(["aqm", "detections", "floor p50 (ms)", "floor p90", "decision p50", "decision p90", "total p50", "total p90"], rows), ""]

    rows = []
    for aqm in sorted({r["aqm"] for r in res}):
        m = [x for r in res if r["aqm"] == aqm for x in r["margins"]]
        warned = [x[1] for x in m if x[1] is not None]
        rows.append([aqm, len(m), _q([x[0] for x in m], 0.5, 0, 1000), f"{sum(1 for x in warned if x > 0)}/{len(m)}",
                     _q(warned, 0.1, 0, 1000), _q(warned, 0.5, 0, 1000), _q(warned, 0.9, 0, 1000)])
    L += ["## 0.5 Warning margin before harm (shadow, no grouping)", "",
          "Harm = first missed playout deadline (600 ms buffer) of the client in [t_on, t_end + 2 s] of a GT3 episode.", "",
          T(["aqm", "GT3 episodes with harm", "harm - t_on p50 (ms)", "alarm before harm", "margin p10 (ms)",
             "p50", "p90"], rows), ""]

    fas = [x for r in res for x in r["fas"]]
    by_scn = Counter(x["scenario"] for x in fas)
    by_ev = Counter(x["evidence"] for x in fas)
    L += ["## 0.6 False alarms (shadow, no grouping; alarm start in GT3 CLEAR time)", "",
          f"Total {len(fas)}; with a GT1 queue episode on the path at that moment: "
          f"{sum(x['gt1_episode_on_path'] for x in fas)}; verified later: {sum(x['verified'] for x in fas)}.", "",
          "By scenario: " + ", ".join(f"{k} {v}" for k, v in by_scn.most_common()), "",
          "By evidence: " + ", ".join(f"{k or '-'} {v}" for k, v in by_ev.most_common(8)), "",
          f"Distance to the nearest GT3 episode of the same client: p50 {_q([x['s_to_nearest_gt3_episode'] for x in fas], 0.5, 2)} s, "
          f"p90 {_q([x['s_to_nearest_gt3_episode'] for x in fas], 0.9, 2)} s.", ""]

    ver = Counter()
    for r in res:
        ver.update(r["verified"])
    rows = [[cls, ver[(cls, True)] + ver[(cls, False)], ver[(cls, True)],
             _f(ver[(cls, True)] / max(1, ver[(cls, True)] + ver[(cls, False)]))]
            for cls in ("in GT3 episode", "AMBIGUOUS", "NO_DATA", "CLEAR")]
    L += ["## 0.7 Verified layer (shadow pre-signal alarms followed by verified_on within 3 s)", "",
          T(["alarm falls in", "alarms", "verified", "share verified"], rows), ""]

    g = [x for r in res for x in r["ack_gaps"]]
    by = defaultdict(list)
    for s, p50, p90 in g:
        by[s].append((p50, p90))
    L += ["## 0.8 ACK spacing per client (the physical floor: one to two ACK gaps)", "",
          T(["client", "ACK gap p50 (ms, median over runs)", "ACK gap p90 (ms)"],
            [[s, f"{statistics.median(x for x, _ in v):.1f}", f"{statistics.median(y for _, y in v):.1f}"]
             for s, v in sorted(by.items())]), ""]
    prefix.with_suffix(".md").write_text("\n".join(L))
    with prefix.with_name(prefix.name + "-baseline.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["aqm", *hdr])
        w.writerows(csv_rows)
    with prefix.with_name(prefix.name + "-false-alarms.csv").open("w", newline="") as f:
        if fas:
            w = csv.DictWriter(f, fieldnames=list(fas[0]))
            w.writeheader()
            w.writerows(fas)
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
