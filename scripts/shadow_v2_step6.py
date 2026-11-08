#!/usr/bin/env python3
"""Shadow v2, Step 6: generalization with frozen parameters (spec v1.0 section 12).

    python3 scripts/shadow_v2_step6.py .runs/<campaign> [...]   # -> reports/detector-v2/step6.md, step6.csv

Detectors (frozen; user decisions: hold kept, rebase dropped, loss gate level+cap): v2 = "fuse d +hold gate:level+cap",
v2-fixed = "fuse d fixed +hold gate:level+cap" (scripts/shadow_v2_step3.py). G_ref and the v2-fixed scale fitted on the
calm pfifo-r1 runs only, as before; nothing else is fitted. score = G / (2 G_ref) in [0, 1]; theta_on 0.25, off below 0.125 for T_clear.
v1 (shadow tuned:full, no grouping) appears only as the internal reference for weak cells and harm.

Truth: GT3 + path queue. Recall two ways: gt_score (an alarm STARTS in [t_on - 1 s, min(end, t_on + 10 s)])
and alarm-on (the alarm is on at some point of that window).

Harm at playout buffer B (200, 400, 600 ms): the client frames.csv is replayed through a port of the
qvideo Playback model (first frame plays at arrival + B, one frame interval per frame, a late frame
shifts the schedule; frames never received are sender skips). The port reproduces the recorded late_us
(B = 600 ms) on every client file; the mismatch count is in the report. t_h = first missed deadline in
[t_on, t_end + 2 s] of a GT3 episode. Lead time = t_h - first time the alarm is on in [t_on - 1 s, t_h]
(an alarm already on before t_on - 1 s counts from t_on - 1 s). Harmless alarm = no missed deadline in
[alarm start, alarm end + 2 s].

Pass (spec): no negative scenario (calm030, calm065, calm090, calmcbr090, randloss) above 0.3 FA / min;
every weak cell improved or explained.
"""

from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import gt1  # noqa: E402
import gt_bands  # noqa: E402
import gt3  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_results as res_mod  # noqa: E402
import shadow_v2_step3 as s3  # noqa: E402
import shadow_v2_step5 as s5  # noqa: E402

DETS = {"v2": "fuse d: s1+s2+s3+sL +hold gate:level+cap", "v2-fixed": "fuse d fixed +hold gate:level+cap"}
REF = "v1 (reference)"
THETA = s3.THETA_ON
BUFFERS_MS = (200, 400, 600)
HARM_TAIL_S = 2.0
FRAME_US = 1_000_000 // 30
NEGATIVE = ("calm030", "calm065", "calm090", "calmcbr090", "randloss")
WEAK = [("fq_codel", "burstudp"), ("fq_codel", "tcpcubic"), ("fq_codel", "tcpbbr"), ("fq_codel", "onoff"),
        ("fq_codel", "splitudp"), ("pfifo", "burstcapshallow"), ("red", "tcpcubic"), ("pfifo", "burstlong"),
        ("pfifo", "calm090")]
N_BOOT = 1000


def playback_late(df: pd.DataFrame, buffer_us: int) -> np.ndarray:
    """Lateness per frame row (arrival order) under qvideo's Playback model with this buffer."""
    idx = df["index"].to_numpy(dtype=np.int64)
    recv = df["recv_us"].to_numpy(dtype=np.int64)
    received = np.unique(idx)
    started = False
    k0 = play0 = contig = 0
    pending: set[int] = set()
    out = np.zeros(len(idx), dtype=np.int64)
    for i, (k, arr) in enumerate(zip(idx.tolist(), recv.tolist())):
        if not started:
            started, k0, play0, contig = True, k, arr + buffer_us, k
        elif k < k0 or k <= contig:
            continue
        else:
            p = int(np.searchsorted(received, k))
            prev = int(received[p - 1]) if p > 0 else k
            pending.update(j for j in range(max(prev + 1, contig + 1), k))  # sender skips right before k
            pending.add(k)
            while contig + 1 in pending:
                contig += 1
                pending.discard(contig)
        late = arr - (play0 + (k - k0) * FRAME_US)
        if late > 0:
            play0 += late
        out[i] = late
    return out


def harm_times(run, sid) -> tuple[dict[int, list[float]], int]:
    """Per buffer: run times of missed playout deadlines; plus the B = 600 ms mismatch count vs late_us."""
    df = pd.read_csv(run.path / "clients" / f"{sid}-frames.csv")
    out, mismatch = {}, 0
    for b in BUFFERS_MS:
        late = playback_late(df, b * 1000)
        if b == 600:
            mismatch = int((late != df["late_us"].to_numpy()).sum())
        recv = df["recv_us"].to_numpy(dtype=np.int64)
        out[b] = sorted(run.t_unix_us(int(r - x)) for r, x in zip(recv, late) if x > 0)
    return out, mismatch


def v1_spans(run) -> dict[str, list[tuple[float, float]]]:
    ev = sorted((e for e in d.replay(run, d.TUNED, grouping="none") if e["variant"] == "full"
                 and e["event"] in ("pre_signal_on", "pre_signal_off")), key=lambda e: e["t"])
    out, open_ = defaultdict(list), {}
    for e in ev:
        s = e["subscriber"]
        if e["event"] == "pre_signal_on" and s not in open_:
            open_[s] = e["t"]
        elif e["event"] == "pre_signal_off" and s in open_:
            out[s].append((open_.pop(s), e["t"]))
    for s, a in open_.items():
        out[s].append((a, run.duration))
    return out


def loss_windows(run) -> list[tuple[float, float]]:
    """Injected random-loss windows (link events with loss_pct > 0), run time."""
    out, start = [], None
    for r in d.rows(run.path / "events.csv"):
        if r["event"] != "link" or "loss_pct=" not in r["detail"]:
            continue
        pct = float(r["detail"].split("loss_pct=")[1].split()[0])
        t = float(r["applied_s"] or r["at_s"])
        if pct > 0 and start is None:
            start = t
        elif pct == 0 and start is not None:
            out.append((start, t))
            start = None
    if start is not None:
        out.append((start, run.duration))
    return out


def on_in(spans, lo, hi):
    """First time an alarm span is on within [lo, hi], or None."""
    c = [max(x, lo) for x, y in spans if x <= hi and y >= lo]
    return min(c) if c else None


def worker(args) -> dict:
    run_dir, g_ref = args
    run = d.Run(run_dir)
    flows = s3.load_flows(run_dir)
    e1, _ = gt1.run_truth(run, gt1.Params())
    e3, l3 = gt3.run_truth(run, gt3.Params())
    view = gt3.view_of(run, e3, l3, need_path=True)
    lw = loss_windows(run)
    paths = {s: {f"{a}->{b}" for a, b in d.path_hops(run, run.pub, s)} for s in flows}
    harms, mism = {}, 0
    for s in flows:
        harms[s], m = harm_times(run, s)
        mism += m
    ep_meta = {(x["flow"], round(x["t_on"], 3)): x for x in e3}
    spans_all = {label: {s: s5.on_spans(s3.run_cusum(df, feat, g_ref[feat], False), THETA) for s, df in flows.items()}
                 for label, feat in DETS.items()}
    v1 = v1_spans(run)
    spans_all[REF] = {s: [(a, b, a) for a, b in v1.get(s, [])] for s in flows}
    out = {"name": run_dir.name, "aqm": run.aqm, "scn": d.scenario_name(run_dir), "topo": run_dir.parent.name.split("_det-")[-1],
           "rep": run_dir.name.rsplit("-", 1)[-1], "mismatch": mism, "v": {}, "v1_missed_harm": []}
    for label, spans in spans_all.items():
        starts = {(label, s): [a for a, _, _ in sp] for s, sp in spans.items()}
        v = {"score": gt_score.score(run, view, starts, (label,))[label], "ep_n": 0, "ep_on": 0,
             "lead": {b: [] for b in BUFFERS_MS}, "harm_eps": {b: 0 for b in BUFFERS_MS}, "harm_missed": {b: 0 for b in BUFFERS_MS},
             "alarms": 0, "harmless": {b: 0 for b in BUFFERS_MS}, "fa": [], "miss": []}
        for s, (eps, code) in view.items():
            if s not in spans:
                continue
            sp = [(x, y) for x, y, _ in spans[s]]
            for a, b in eps:
                if a < d.WARMUP_S:
                    continue
                lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
                hit = on_in(sp, lo, hi) is not None
                v["ep_n"] += 1
                v["ep_on"] += hit
                if not hit:
                    meta = next((x for (f, t), x in ep_meta.items() if f == s and abs(t - a) < 0.05), {})
                    v["miss"].append({"dur": b - a, "gt1_path": any(e["hop"] in paths[s] and e["start_s"] <= b and e["end_s"] >= a for e in e1),
                                      "peak_q": meta.get("peak_q", float("nan")), "trigger": meta.get("trigger", "?")})
                for B in BUFFERS_MS:
                    th = next((h for h in harms[s][B] if a <= h <= b + HARM_TAIL_S), None)
                    if th is None:
                        continue
                    v["harm_eps"][B] += 1
                    t_al = on_in(sp, lo, th)
                    if t_al is None:
                        v["harm_missed"][B] += 1
                        if label == REF and B == 600:
                            out["v1_missed_harm"].append({"client": s, "t_on": a, "dur": b - a, "t_h": th})
                    else:
                        v["lead"][B].append(th - t_al)
            # false alarms exactly as gt_score counts them, classified by the GT1 queue at that moment
            used = set()
            for a, b in eps:
                if a >= d.WARMUP_S:
                    used.update(x for x, _ in sp if a - d.PRE_ONSET_LEAD_S <= x <= min(b, a + d.SEARCH_S))
            for x, y in sp:
                if x < d.WARMUP_S:
                    continue
                v["alarms"] += 1
                for B in BUFFERS_MS:
                    v["harmless"][B] += not any(x <= h <= y + HARM_TAIL_S for h in harms[s][B])
                if x in used or any(a <= x <= b for a, b in eps):
                    continue
                if code[min(len(code) - 1, int(x / gt_score.GRID_S))] == gt_score.RANK[gt_bands.CLEAR]:
                    on_path = any(e["hop"] in paths[s] and e["start_s"] <= x <= e["end_s"] for e in e1)
                    elsewhere = any(e["start_s"] <= x <= e["end_s"] for e in e1)
                    v["fa"].append({"cls": "GT1 queue on path" if on_path else "GT1 queue elsewhere" if elsewhere else "no GT1 queue",
                                    "loss": any(a <= x <= b + 1.0 for a, b in lw)})
        out["v"][label] = v
    # which v1-missed harmful episodes v2 / v2-fixed caught before harm
    for m in out["v1_missed_harm"]:
        for label in DETS:
            sp = [(x, y) for x, y, _ in spans_all[label][m["client"]]]
            t_al = on_in(sp, m["t_on"] - d.PRE_ONSET_LEAD_S, m["t_h"])
            m[label] = None if t_al is None else m["t_h"] - t_al
    return out


def _f(x, k=2):
    return "-" if x is None or x != x else f"{x:.{k}f}"


def _q(v, q, k=0, scale=1000.0):
    v = [x for x in v if x == x]
    return "-" if not v else f"{np.percentile(v, q * 100) * scale:.{k}f}"


def on_recall(rs, label):
    n = sum(r["v"][label]["ep_n"] for r in rs)
    return sum(r["v"][label]["ep_on"] for r in rs) / n if n else float("nan")


def boot(rs, label, rng):
    """95 % intervals over runs (not client-episodes) for recall, alarm-on recall, FA / min, latency p90."""
    vals = []
    for _ in range(N_BOOT):
        smp = [rs[i] for i in rng.integers(0, len(rs), len(rs))]
        s = gt_score.summarize([r["v"][label]["score"] for r in smp])
        vals.append((s["recall"], on_recall(smp, label), s["fa_per_min"], s["latency_p90_ms"]))
    a = np.array(vals, dtype=float)
    return [f"{np.nanpercentile(a[:, i], 2.5):.{k}f}-{np.nanpercentile(a[:, i], 97.5):.{k}f}" for i, k in enumerate((2, 2, 2, 0))]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    run_dirs = sorted(r for c in argv for r in Path(c).iterdir() if (r / "events.csv").exists())
    calm_dirs = [r for r in run_dirs if r.name.endswith("-r1") and "-pfifo-" in r.name and r.name.split("-")[1] in s3.CALM_RUNS]
    s3.FIXED_STATS.update(s3.fixed_stats(calm_dirs))
    g_ref = {feat: res_mod.fit_g_ref(feat, calm_dirs) for feat in DETS.values()}
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, [(rd, g_ref) for rd in run_dirs]))
    git = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=s3.ROOT, capture_output=True, text=True).stdout.strip()
    stamp = s3.ROOT / ".runs" / "2026-11-05_TRUTH-SETTINGS.md"
    table = s3.s1.table
    rng = np.random.default_rng(1)
    labels = (*DETS, REF)

    def pooled(rs, label):
        return gt_score.summarize([r["v"][label]["score"] for r in rs])

    L = ["# Shadow v2, Step 6: generalization (frozen parameters)", "",
         f"{len(res)} runs, theta_on {THETA}, theta_off {THETA / 2}. Frozen: hold kept, rebase dropped, loss gate level+cap. "
         + ", ".join(f"{k} G_ref {g_ref[f]:.1f}" for k, f in DETS.items())
         + f" (calm pfifo-r1 only). Playback port vs recorded late_us (B 600 ms): {sum(r['mismatch'] for r in res)} mismatching frames. "
         + f"git {git}. Truth: " + (stamp.read_text().splitlines()[3] if stamp.exists() else "see TRUTH-SETTINGS") + ".", ""]

    cols = ["precision", "recall", "recall (alarm on)", "FA / min CLEAR", "latency p50 (ms)", "p90 (ms)"]

    def cells(rs, label):
        s = pooled(rs, label)
        return [_f(s["precision"]), _f(s["recall"]), _f(on_recall(rs, label)), _f(s["fa_per_min"]),
                _f(s["late_latency_p50_ms"], 0), _f(s["latency_p90_ms"], 0)]

    rows = [[label, *cells(res, label), *boot(res, label, rng)] for label in DETS]
    L += ["## 1. Overall (GT3 + path queue)", "",
          "95 % intervals: bootstrap over runs (1000 resamples). Two repeats per cell limit the per-cell resolution.", "",
          table(["detector", *cols, "recall 95 %", "alarm-on recall 95 %", "FA / min 95 %", "p90 95 % (ms)"], rows), ""]
    rows = []
    for split, key in (("freeze set (pfifo-r1)", lambda r: r["aqm"] == "pfifo" and r["rep"] == "r1"),
                       ("held out: other AQMs r1", lambda r: r["aqm"] != "pfifo" and r["rep"] == "r1"),
                       ("held out: every r2", lambda r: r["rep"] == "r2")):
        rs = [r for r in res if key(r)]
        rows += [[split, len(rs), label, *cells(rs, label)] for label in DETS]
    L += ["## 2. Freeze set vs held out", "", table(["set", "runs", "detector", *cols], rows), ""]

    aqms = sorted({r["aqm"] for r in res})
    scns = sorted({r["scn"] for r in res})
    for label in DETS:
        rows = []
        for scn in scns:
            row = [scn]
            for aqm in aqms:
                rs = [r for r in res if r["scn"] == scn and r["aqm"] == aqm]
                if not rs:
                    row.append("")
                    continue
                s = pooled(rs, label)
                row.append(f"{_f(s['recall'])} / {_f(on_recall(rs, label))} / {_f(s['fa_per_min'])}")
            rows.append(row)
        L += [f"## 3. {label}: scenario x AQM (recall / alarm-on recall / FA per min; both repeats, all topologies)", "",
              table(["scenario", *aqms], rows), ""]

    rows, worst = [], {}
    for scn in NEGATIVE:
        for aqm in aqms:
            rs = [r for r in res if r["scn"] == scn and r["aqm"] == aqm]
            if not rs:
                continue
            fa = {label: pooled(rs, label)["fa_per_min"] for label in DETS}
            for label in DETS:
                worst[label] = max(worst.get(label, 0.0), fa[label])
            ev = []
            for label in DETS:
                f = [c for r in rs for c in r["v"][label]["fa"]]
                n = max(1, len(f))
                ev.append(f"{len(f)}: {sum(c['cls'] == 'GT1 queue on path' for c in f) / n:.0%} GT1 on path"
                          + (f", {sum(c['loss'] for c in f) / n:.0%} in a loss window" if scn == "randloss" else ""))
            rows.append([scn, aqm, len(rs), *(_f(fa[label]) for label in DETS),
                         *("FAIL" if fa[label] > 0.3 else "pass" for label in DETS), *ev])
    L += ["## 4. Negative scenarios: FA / min CLEAR (pass: <= 0.3)", "",
          "Evidence: false alarms, share with a GT1 queue on the client's path at the alarm, and for randloss the share "
          "inside an injected loss window (+ 1 s).", "",
          table(["scenario", "AQM", "runs", *(f"{k} FA / min" for k in DETS), *(f"{k}" for k in DETS),
                 *(f"{k} false alarms" for k in DETS)], rows), "",
          "Worst cell: " + ", ".join(f"{k} {_f(v)}" for k, v in worst.items()) + ".", ""]
    rows = []
    for label in DETS:
        for scope, rs in (("all scenarios", res), ("negative scenarios", [r for r in res if r["scn"] in NEGATIVE])):
            fa = [c for r in rs for c in r["v"][label]["fa"]]
            n = max(1, len(fa))
            rows.append([label, scope, len(fa), *(f"{sum(c['cls'] == k for c in fa) / n:.2f}" for k in
                                                  ("GT1 queue on path", "GT1 queue elsewhere", "no GT1 queue"))])
    L += ["## 5. False alarms by the GT1 (router queue) state at the alarm (reviewer addendum)", "",
          "A false alarm here is an alarm start in GT3 CLEAR time outside every GT3 episode window (gt_score rule).", "",
          table(["detector", "scope", "false alarms", "GT1 queue on the client's path", "GT1 queue elsewhere", "no GT1 queue"], rows), ""]

    rows = []
    for aqm, scn in WEAK:
        rs = [r for r in res if r["scn"] == scn and r["aqm"] == aqm]
        if not rs:
            continue
        ref = pooled(rs, REF)
        row = [f"{scn} {aqm}", pooled(rs, "v2")["episodes"], f"{_f(ref['recall'])} / {_f(ref['fa_per_min'])} / {_f(ref['late_latency_p50_ms'], 0)}"]
        for label in DETS:
            s = pooled(rs, label)
            rec_ok = s["recall"] >= ref["recall"] - 0.02
            fa_ok = s["fa_per_min"] <= ref["fa_per_min"] + 0.1
            verdict = "better" if rec_ok and fa_ok else "recall better, FA worse" if rec_ok else "recall worse" if fa_ok else "worse"
            row.append(f"{_f(s['recall'])} ({_f(on_recall(rs, label))}) / {_f(s['fa_per_min'])} / {_f(s['late_latency_p50_ms'], 0)}: {verdict}")
        for label in DETS:
            miss = [m for r in rs for m in r["v"][label]["miss"]]
            if not miss:
                row.append("no misses")
                continue
            short = sum(m["dur"] < 0.5 for m in miss) / len(miss)
            gp = sum(m["gt1_path"] for m in miss) / len(miss)
            trig = defaultdict(int)
            for m in miss:
                trig[m["trigger"]] += 1
            row.append(f"{len(miss)} missed: {short:.0%} < 0.5 s, {gp:.0%} GT1 on path, peak q p50 "
                       f"{np.nanmedian([m['peak_q'] for m in miss]):.0f} ms, trigger " + ", ".join(f"{k} {v}" for k, v in sorted(trig.items())))
        for label in DETS:
            f = [c for r in rs for c in r["v"][label]["fa"]]
            row.append(f"{len(f)} FA, {sum(c['cls'] == 'GT1 queue on path' for c in f) / max(1, len(f)):.0%} GT1 on path")
        rows.append(row)
    L += ["## 6. Weak cells (recall (alarm-on recall) / FA per min / latency p50 ms: verdict vs v1)", "",
          "v1 = shadow tuned:full without grouping, internal reference only. Verdict: recall (gt_score) ok when >= v1 - 0.02, "
          "FA ok when <= v1 + 0.1 per min. Miss evidence: episodes with no alarm on in the window; FA evidence: GT1 queue "
          "on the client's path at the false alarm.", "",
          table(["cell", "episodes", f"{REF}", *DETS, *(f"{k} miss evidence" for k in DETS), *(f"{k} FA evidence" for k in DETS)], rows), ""]

    rows = []
    for B in BUFFERS_MS:
        for label in labels:
            he = sum(r["v"][label]["harm_eps"][B] for r in res)
            hm = sum(r["v"][label]["harm_missed"][B] for r in res)
            lead = [x for r in res for x in r["v"][label]["lead"][B]]
            al = sum(r["v"][label]["alarms"] for r in res)
            hl = sum(r["v"][label]["harmless"][B] for r in res)
            rows.append([B, label, he, _f(1 - hm / he if he else float("nan")), hm, _q(lead, 0.1), _q(lead, 0.5), _q(lead, 0.9),
                         _f(sum(x < 0.2 for x in lead) / len(lead) if lead else float("nan")), _f(hl / al if al else float("nan"))])
    L += ["## 7. Lead time before harm at three playout buffers", "",
          "Harm = first missed playout deadline in [t_on, t_end + 2 s] of a GT3 episode (playback replay at buffer B). "
          "Lead = harm time - first time the alarm is on in [t_on - 1 s, harm]. Harmless = alarm with no missed deadline "
          "in [start, end + 2 s] (includes alarms on real congestion the buffer absorbed).", "",
          table(["B (ms)", "detector", "GT3 episodes with harm", "alarm before harm", "missed", "lead p10 (ms)", "p50", "p90",
                 "lead < 200 ms share", "harmless alarm share"], rows), ""]

    miss = [{**m, "run": r["name"]} for r in res for m in r["v1_missed_harm"]]
    rows = [[m["run"], m["client"], _f(m["t_on"], 1), _f(m["dur"], 2), *(("missed" if m[k] is None else f"{m[k] * 1000:.0f} ms before") for k in DETS)]
            for m in sorted(miss, key=lambda m: (m["run"], m["t_on"]))]
    caught = {k: sum(m[k] is not None for m in miss) for k in DETS}
    L += ["## 8. Harmful GT3 episodes v1 missed (B 600 ms; reviewer addendum)", "",
          f"{len(miss)} episodes. Caught before harm: " + ", ".join(f"{k} {v}" for k, v in caught.items()) + ".", "",
          table(["run", "client", "t_on (s)", "duration (s)", *(f"{k}" for k in DETS)], rows), "",
          "Note (reviewer addendum): gcc is not scored here. Its replay applies a 500 ms detection floor, so the Step 0 "
          "gcc latency is not comparable with v1 / v2 decision times.", ""]
    (s3.OUT / "step6.md").write_text("\n".join(L))
    pd.DataFrame([[r["name"], r["aqm"], r["scn"], r["topo"], r["rep"], k, v["score"]["episodes"], v["score"]["detected"], v["ep_on"],
                   v["score"]["tp"], v["score"]["fp"], v["score"]["clear_s"], *(v["harm_eps"][B] for B in BUFFERS_MS),
                   *(v["harm_missed"][B] for B in BUFFERS_MS)] for r in res for k, v in r["v"].items()],
                 columns=["run", "aqm", "scenario", "topology", "rep", "detector", "episodes", "detected", "alarm_on", "tp", "fp", "clear_s",
                          *(f"harm_eps_{B}" for B in BUFFERS_MS), *(f"harm_missed_{B}" for B in BUFFERS_MS)]).to_csv(s3.OUT / "step6.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
