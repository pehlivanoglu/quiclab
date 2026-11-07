#!/usr/bin/env python3
"""GT2: demand-exceeds-capacity truth per bottleneck queue (resource level).

    python3 scripts/gt2.py score .runs/<run> [...]      # <run>/truth/gt2.csv
    python3 scripts/gt2.py report .runs/<campaign>       # validation -> <campaign>/gt2-report.md
    options: --p-on S --p-off S --kn FRACTION (e.g. 0.6667) --util-floor X

Question per router egress: was offered load at or above capacity,
persistently, and when did that start? AQM-agnostic: arrivals, departures and
drops, not queue delay (Dhamdhere et al., SIGCOMM 2018: congestion from the
link's own utilization data, transients excluded). Per interval i of the 25 ms
router-metrics CSV (offered_bytes / transmitted_bytes / drops are per-interval
deltas there):

    A = offered * 8 / dt, D = transmitted * 8 / dt, C = capacity integral / dt
    util = D / C, rho = A / C, drop = drops
    active = util >= max(util_floor, 1 - MTU*8 / (C dt)) and (rho >= 1 or drop > 0)

The matchall counter sits in front of the qdisc, so offered includes packets
the qdisc later drops (checked: offered - transmitted = drops x mean packet size
within 4 %). Persistence: an episode needs K of N consecutive intervals active,
N = round(P_on / dt), K = ceil(kn * N) (4 of 6 at 25 ms). t_on = end of the
first active interval of the qualifying window (the sample time that first saw
it, as in GT1); uncertainty one interval (sample_dt). t_x = earliest interval
in [t_on - P_on, t_on] with rho >= 1, else t_on. The episode runs while active
intervals follow each other with gaps < P_off; t_end = end of its last active
interval. Episodes ending before the warm-up are dropped.

Not available here: the 5 ms queue CSV has no offered / transmitted bytes (no
GT2 at 5 ms; the sampling check thins 25 ms to 50 ms instead), and the ACK
path is not sampled (cause "reverse" never occurs). Packets offered for
drop_rate = offered bytes / mean packet size in the queue (backlog / qlen).
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt_bands  # noqa: E402

MTU = gt1.MTU
SEVERITY = ((1.1, "mild"), (1.5, "moderate"), (math.inf, "severe"))
CAUSES = {"capacity": "capacity_drop", "udp": "cross_udp", "tcp": "cross_tcp", "ramp": "ramp"}
FIELDS = ("queue_id", "episode_id", "t_on", "t_x", "t_end", "duration", "peak_rho", "mean_rho", "drop_rate",
          "severity", "cause", "exposed_flows", "sample_dt")


@dataclass(frozen=True)
class Params:
    p_on: float = 0.15
    p_off: float = 0.3  # 300 ms (decided 2026-11-07): TCP sawtooth no longer splits an episode
    kn: float = 4 / 6
    util_floor: float = 0.90
    mtu: int = MTU
    util_band: float = 0.05  # hysteresis (gt_bands): stay while util >= util_th - band
    rho_band: float = 0.05   # and rho >= 1 - band (or a drop)

    def tag(self) -> str:
        return (f"P_on={self.p_on * 1000:g} P_off={self.p_off * 1000:g} K/N={self.kn:.2f} floor={self.util_floor:g}"
                f" util_band={self.util_band:g} rho_band={self.rho_band:g}")


# ── core ──────────────────────────────────────────────────────────────────

def intervals(t: np.ndarray, offered: np.ndarray, sent: np.ndarray, drops: np.ndarray,
              caps: list[tuple[float, float]], p: Params) -> dict[str, np.ndarray]:
    """Per interval (t[i-1], t[i]], i >= 1: rho, util, drops, active. Byte arrays are per-interval deltas."""
    t0, t1 = t[:-1], t[1:]
    dt = t1 - t0
    cap_bits = np.array([gt1.capacity_integral(caps, a, b) for a, b in zip(t0, t1)])
    rho = offered[1:] * 8 / cap_bits
    util = sent[1:] * 8 / cap_bits
    th = np.maximum(p.util_floor, 1 - p.mtu * 8 / cap_bits)
    drop = drops[1:]
    enter = (util >= th) & ((rho >= 1.0) | (drop > 0))
    stay = (util >= th - p.util_band) & ((rho >= 1.0 - p.rho_band) | (drop > 0))
    return {"t0": t0, "t1": t1, "dt": dt, "rho": rho, "util": util, "drop": drop,
            "active": gt_bands.hysteresis(enter, stay), "util_lo": th - p.util_band, "offered": offered[1:]}


def gt2_episodes(iv: dict[str, np.ndarray], p: Params) -> list[dict]:
    """Episodes from per-interval arrays (see intervals)."""
    active, t1, t0, rho = iv["active"], iv["t1"], iv["t0"], iv["rho"]
    n = len(active)
    if not n:
        return []
    dt_nom = float(np.median(iv["dt"]))
    big_n = max(1, round(p.p_on / dt_nom))
    k = max(1, math.ceil(p.kn * big_n - 1e-9))
    counts = np.convolve(active.astype(int), np.ones(big_n, dtype=int), "full")[big_n - 1:]  # window starting at i
    qualifies = counts >= k
    episodes, i = [], 0
    while i < n:
        if not qualifies[i]:
            i += 1
            continue
        start = i + int(np.argmax(active[i:i + big_n]))
        last, j = start, start + 1
        while j < n and t0[j] - t1[last] < p.p_off - 1e-9:
            if active[j]:
                last = j
            j += 1
        lo = np.searchsorted(t1, t1[start] - p.p_on, side="left")
        excess = [m for m in range(lo, start + 1) if rho[m] >= 1.0]
        span = slice(start, last + 1)
        episodes.append({"start": start, "last": last, "t_on": float(t1[start]),
                         "t_x": float(t1[excess[0]]) if excess else float(t1[start]),
                         "t_end": float(t1[last]), "peak_rho": float(rho[span].max()),
                         "mean_rho": float(rho[span].mean()), "drops": int(iv["drop"][span].sum()),
                         "offered_bytes": float(iv["offered"][span].sum()), "sample_dt": dt_nom})
        i = last + 1
    return episodes


def interval_labels(iv: dict[str, np.ndarray], episodes: list[dict]) -> np.ndarray:
    """Per interval: CONGESTED inside an episode, else AMBIGUOUS / CLEAR by util against util_th - band."""
    in_episode = np.zeros(len(iv["active"]), dtype=bool)
    for e in episodes:
        in_episode[e["start"]:e["last"] + 1] = True
    return gt_bands.labels(in_episode, iv["util"], iv["util_lo"])


def severity(peak_rho: float) -> str:
    return next(name for limit, name in SEVERITY if peak_rho < limit)


def thin(t, offered, sent, drops, backlog, factor: int):
    """Every factor-th sample, per-interval counters summed: the same run seen at factor x dt."""
    keep = np.arange(0, len(t), factor)
    # Sample i's counters cover (t[i-1], t[i]]: kept sample keep[j] sums x[keep[j-1]+1 .. keep[j]].
    summed = [np.concatenate(([x[0]], np.add.reduceat(x[:keep[-1] + 1], keep[:-1] + 1))) if len(keep) > 1 else x[:1]
              for x in (offered, sent, drops)]
    return (t[keep], *summed, backlog[keep])


# ── run access ────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _samples(run_dir: Path, csv: Path):
    """(t, offered, sent, drops, backlog, mean packet size) from a 25 ms CSV, run clock."""
    run = det_eval.Run(run_dir)
    rows = det_eval.rows(csv)
    t = np.array([run.t_mono_us(int(r["timestamp_mono_ns"]) / 1000) for r in rows])
    keep = (t >= 0) & (t <= run.duration - det_eval.SHUTDOWN_S)
    col = lambda name: np.array([int(r[name]) for r in rows], dtype=float)[keep]  # noqa: E731
    qlen, backlog = col("queue_packets"), col("queue_backlog_bytes")
    size = float((backlog[qlen > 0] / qlen[qlen > 0]).mean()) if (qlen > 0).any() else 1200.0
    return t[keep], col("offered_bytes"), col("transmitted_bytes"), col("drops"), backlog, size


def cause_spans(run: det_eval.Run) -> dict[str, list[tuple[float, float, str]]]:
    """Scripted activity per hop "a->b": (start, end, cause)."""
    scn = det_eval.scenario_name(run.path)
    spans = defaultdict(list)
    for b in gt1._bursts(run.path):
        kind = "onoff" if scn == "onoff" and b["kind"] == "udp" else CAUSES.get(b["kind"], b["kind"])
        spans[f"{b['hop'][0]}->{b['hop'][1]}"].append((b["start"], b["end"], kind))
    caps = det_eval.capacity_series(run)
    for (a, b), series in caps.items():  # capacity below its initial value (capacity / ramp scenarios)
        base, start = series[0][1], None
        for when, bw in series[1:] + [(run.duration, base)]:
            if bw < base and start is None:
                start = when
            elif bw >= base and start is not None:
                spans[f"{a}->{b}"].append((start, when, "ramp" if scn == "ramp" else "capacity_drop"))
                start = None
    for flow in det_eval.cross_series(run):
        ev = next(e for e in run.scenario["events"] if e.get("id") == flow["id"])
        if ev["type"] == "bursts" or (ev["type"] == "flow" and ev["kind"] == "tcp"):
            continue  # per burst / per flow already from burst_truth
        applied = next(float(e["applied_s"]) for e in run.events if e["target"] == flow["id"])
        end = applied + float(ev.get("duration_s", run.duration))
        for a, b in flow["hops"]:
            spans[f"{a}->{b}"].append((applied, end, "cross_ppbp" if ev["type"] == "ppbp" else "cross_udp"))
    return spans


def cause_of(spans: list[tuple[float, float, str]], t_on: float, p_on: float) -> str:
    """Scripted activity on the hop running at t_on or starting within P_on before it; else endogenous."""
    hit = sorted({c for a, b, c in spans if a - gt1.ONSET_SLACK_S <= t_on and (t_on <= b or t_on - a <= p_on)})
    return "+".join(hit) or "endogenous"


def run_truth(run: det_eval.Run, p: Params, thin_factor: int = 1) -> tuple[list[dict], list[dict]]:
    """GT2 episodes and label spans (per interval (t[i-1], t[i]]) of every sampled egress."""
    caps = det_eval.capacity_series(run)
    spans = cause_spans(run)
    paths = {s: det_eval.path_hops(run, run.pub, s) for s in run.subs}
    out, labs = [], []
    for hop, csv in gt1.router_egresses(run):
        t, offered, sent, drops, backlog, size = _samples(run.path, csv)
        if thin_factor > 1:
            t, offered, sent, drops, backlog = thin(t, offered, sent, drops, backlog, thin_factor)
        hop_id = f"{hop[0]}->{hop[1]}"
        exposed = ";".join(s for s in run.subs if hop in paths[s])
        iv = intervals(t, offered, sent, drops, caps[hop], p)
        eps = gt2_episodes(iv, p)
        labs += [{"hop": hop_id, "t_start": round(a, 4), "t_end": round(b, 4), "label": x}
                 for a, b, x in gt_bands.spans(iv["t0"], iv["t1"], interval_labels(iv, eps))]
        for n, e in enumerate(e for e in eps if e["t_end"] >= det_eval.WARMUP_S):
            packets = e["offered_bytes"] / size
            out.append({"queue_id": hop_id, "episode_id": n + 1, "t_on": round(e["t_on"], 4), "t_x": round(e["t_x"], 4),
                        "t_end": round(e["t_end"], 4), "duration": round(e["t_end"] - e["t_on"], 4),
                        "peak_rho": round(e["peak_rho"], 3), "mean_rho": round(e["mean_rho"], 3),
                        "drop_rate": round(e["drops"] / packets, 4) if packets else 0.0,
                        "severity": severity(e["peak_rho"]), "cause": cause_of(spans[hop_id], e["t_on"], p.p_on),
                        "exposed_flows": exposed, "sample_dt": round(e["sample_dt"], 4)})
    return sorted(out, key=lambda e: (e["t_on"], e["queue_id"])), labs


def run_episodes(run: det_eval.Run, p: Params, thin_factor: int = 1) -> list[dict]:
    return run_truth(run, p, thin_factor)[0]


def score(run_dir: Path, p: Params) -> None:
    run = det_eval.Run(run_dir)
    eps, labs = run_truth(run, p)
    det_eval.write_csv(run_dir / "truth" / "gt2-labels.csv", labs)
    path = run_dir / "truth" / "gt2.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:  # header even when empty: no episodes is a result
        f.write(",".join(FIELDS) + "\n")
        for e in eps:
            f.write(",".join(str(e[k]) for k in FIELDS) + "\n")
    print(f"{run_dir.name}: aqm={run.aqm} gt2_episodes={len(eps)}")


# ── validation ────────────────────────────────────────────────────────────

NEGATIVES = ("calm030", "calm065", "randloss")
FLAPPING = ("tcpcubic", "onoff")
_q, _table = gt1._q, gt1._table


def event_match(run: det_eval.Run, eps: list[dict]) -> list[dict]:
    """Per injected event: GT2 episodes on its hop overlapping [start - slack, end], onset lag of the first."""
    out = []
    for b in gt1._bursts(run.path):
        hop = f"{b['hop'][0]}->{b['hop'][1]}"
        during = [e for e in eps if e["queue_id"] == hop and e["t_on"] <= b["end"]
                  and e["t_end"] >= b["start"] - gt1.ONSET_SLACK_S]
        window = [e for e in eps if e["queue_id"] == hop and b["start"] - gt1.ONSET_SLACK_S <= e["t_on"]
                  <= b["end"] + gt1.BURST_RECOVERY_S]
        out.append({"hop": hop, "start": b["start"], "end": b["end"], "n": len(during), "n_window": len(window),
                    "lag": min(e["t_on"] for e in during) - b["start"] if during else None})
    return out


def calibration(runs: list[det_eval.Run]) -> str:
    """Measured departure rate / nominal capacity in intervals the queue cannot have emptied (backlog >= dt)."""
    rows = []
    for run in runs:
        caps = det_eval.capacity_series(run)
        for hop, csv in gt1.router_egresses(run):
            t, offered, sent, drops, backlog, _ = _samples(run.path, csv)
            iv = intervals(t, offered, sent, drops, caps[hop], Params())
            cap_now = np.array([det_eval.value_at(caps[hop], x) for x in iv["t1"]])
            same = np.array([det_eval.value_at(caps[hop], a) == c for a, c in zip(iv["t0"], cap_now)])
            saturated = same & (backlog[:-1] * 8 / (cap_now * 1e6) >= iv["dt"])
            for c in sorted(set(cap_now[saturated])):
                u = iv["util"][saturated & (cap_now == c)]
                if len(u) >= 20:
                    gap = float(np.median(u)) - 1
                    rows.append([run.path.name, run.aqm, f"{hop[0]}->{hop[1]}", f"{c:g}", len(u),
                                 f"{np.median(u):.4f}", f"{np.percentile(u, 5):.3f}", f"{np.percentile(u, 95):.3f}",
                                 f"{100 * gap:+.2f} %", "yes" if abs(gap) > 0.02 else "no"])
    return _table(["run", "aqm", "hop", "nominal Mb/s", "saturated intervals", "D/C median", "p5", "p95",
                   "gap", "> 2 %"], rows)


def negatives_table(runs: list[det_eval.Run], p: Params) -> str:
    rows = []
    for run in runs:
        eps = run_episodes(run, p)
        rows.append([run.path.name, run.aqm, len(eps),
                     "; ".join(f"{e['queue_id']} {e['t_on']:.2f}-{e['t_end']:.2f} s peak_rho {e['peak_rho']}"
                               f" drop_rate {e['drop_rate']} {e['cause']}" for e in eps[:6])
                     + (" ..." if len(eps) > 6 else "") or "-"])
    return _table(["run", "aqm", "episodes", "first episodes"], rows)


def events_table(runs: list[det_eval.Run], p: Params) -> str:
    rows = []
    for run in runs:
        m = event_match(run, run_episodes(run, p))
        if not m:
            continue
        lags = [x["lag"] for x in m if x["lag"] is not None]
        rows.append([run.path.name, run.aqm, len(m), sum(1 for x in m if x["n"]), sum(1 for x in m if x["n"] > 1),
                     sum(1 for x in m if x["lag"] is not None and 0 <= x["lag"] <= 0.05),
                     _q(lags, 0.5), _q(lags, 0.9), f"{min(lags):.3f}" if lags else "-", f"{max(lags):.3f}" if lags else "-",
                     f"{np.mean([x['n_window'] for x in m]):.2f}"])
    return _table(["run", "aqm", "events", "caught", "split (> 1 episode)", "t_on within 0-50 ms", "lag p50 (s)",
                   "p90", "min", "max", "episodes per event (window to end + 2 s)"], rows)


def sampling_table(runs: list[det_eval.Run], p: Params) -> str:
    rows = []
    for run in runs:
        a, b = run_episodes(run, p), run_episodes(run, p, thin_factor=2)
        diffs = []
        for e in a:
            same = [f for f in b if f["queue_id"] == e["queue_id"] and f["t_on"] <= e["t_end"] and f["t_end"] >= e["t_on"]]
            if same:
                diffs.append(min(f["t_on"] for f in same) - e["t_on"])
        rows.append([run.path.name, run.aqm, len(a), len(b), len(diffs), _q(diffs, 0.5), _q(diffs, 0.9),
                     f"{max(abs(x) for x in diffs):.3f}" if diffs else "-"])
    return _table(["run", "aqm", "episodes 25 ms", "episodes 50 ms", "matched", "t_on diff p50 (50 - 25, s)", "p90",
                   "max |diff|"], rows)


def agreement_table(runs: list[det_eval.Run], p: Params, gt1_interval: float) -> str:
    """Per AQM: GT1 (INTERVAL = P_on) vs GT2 episodes on the same hop, overlap-matched."""
    agg = defaultdict(lambda: {"both": 0, "gt1": 0, "gt2": 0, "off": []})
    for run in runs:
        e1 = gt1.run_episodes(run, gt1.Params(interval_s=gt1_interval))
        e2 = run_episodes(run, p)
        a = agg[run.aqm]
        for e in e2:
            same = [f for f in e1 if f["hop"] == e["queue_id"] and f["start_s"] <= e["t_end"] and f["end_s"] >= e["t_on"]]
            if same:
                a["both"] += 1
                a["off"].append(min(f["start_s"] for f in same) - e["t_on"])
            else:
                a["gt2"] += 1
        a["gt1"] += sum(1 for f in e1 if not any(e["queue_id"] == f["hop"] and f["start_s"] <= e["t_end"]
                                                 and f["end_s"] >= e["t_on"] for e in e2))
    rows = [[aqm, a["both"], a["gt2"], a["gt1"], _q(a["off"], 0.1), _q(a["off"], 0.5), _q(a["off"], 0.9)]
            for aqm, a in sorted(agg.items())]
    return _table(["aqm", "GT2 episodes also in GT1", "GT2 only", "GT1 only", "t_on(GT1) - t_on(GT2) p10 (s)",
                   "p50", "p90"], rows)


def flapping_table(runs: list[det_eval.Run], p: Params) -> str:
    rows = []
    for run in runs:
        for poff in sorted({p.p_off, 0.15, 0.3}):
            m = event_match(run, run_episodes(run, replace(p, p_off=poff)))
            if m:
                per = [x["n_window"] for x in m]
                rows.append([run.path.name, run.aqm, f"{poff * 1000:g}", len(m), f"{np.mean(per):.2f}", max(per),
                             sum(1 for x in per if x > 2)])
    return _table(["run", "aqm", "P_off (ms)", "events", "episodes per event mean", "max", "events with > 2"], rows)


def sweep_table(neg: list[det_eval.Run], ev: list[det_eval.Run], base: Params) -> str:
    variants = [base]
    for key, values in (("p_on", (0.1, 0.15, 0.35)), ("p_off", (0.1, 0.15, 0.3)), ("kn", (3 / 6, 4 / 6, 5 / 6)),
                        ("util_floor", (0.90, 0.95))):
        variants += [replace(base, **{key: v}) for v in values if replace(base, **{key: v}) != base]
    rows = []
    for p in variants:
        n_neg = sum(len(run_episodes(r, p)) for r in neg)
        m = [x for r in ev for x in event_match(r, run_episodes(r, p))]
        lags = [x["lag"] for x in m if x["lag"] is not None]
        rows.append([p.tag(), n_neg, f"{sum(1 for x in m if x['n'])}/{len(m)}", sum(1 for x in m if x["n"] > 1),
                     _q(lags, 0.5), _q(lags, 0.9), f"{np.mean([x['n_window'] for x in m]):.2f}" if m else "-"])
    return _table(["params", "episodes in runs without injected events", "events caught", "split", "lag p50", "lag p90",
                   "episodes per event"], rows)


def report(campaign: Path, p: Params) -> str:
    runs = [det_eval.Run(d) for d in sorted(campaign.iterdir()) if (d / "events.csv").exists()]
    scn = det_eval.scenario_name
    freeze = [r for r in runs if r.path.name.endswith("-pfifo-r1")]
    lines = [f"# GT2 validation: {campaign.name}", "", f"Params: {p.tag()}; MTU {p.mtu}; warm-up "
             f"{det_eval.WARMUP_S:g} s excluded. Parameters are frozen from det-*-pfifo-r1 runs only (sections 2, 3, 7); "
             "the other AQMs and reps are reported, not used for choosing.", ""]
    long = [r for r in runs if scn(r.path) == "burstlong" and r.path.name.endswith("-r1")]
    if long:
        lines += ["## 1. Capacity calibration (burstlong r1 per AQM; saturated = backlog cannot drain within the interval)",
                  "", calibration(long), ""]
    neg = [r for r in runs if scn(r.path) in NEGATIVES]
    if neg:
        lines += ["## 2. Runs without injected events (no injected event: a truth episode here is real congestion the scenario did not script (keyframe overflow, AQM drops), not an error; detector false alarms count in CLEAR time only)", "", negatives_table(neg, p), ""]
    ev = [r for r in runs if gt1._bursts(r.path)]
    if ev:
        lines += ["## 3. Known events (caught = an episode on the hop overlaps the event; lag = t_on - event start)",
                  "", events_table(ev, p), ""]
    split = [r for r in runs if len(gt1.router_egresses(r)) > 2]
    if split:
        lines += ["## 4. Sampling error: 25 ms vs the same counters thinned to 50 ms "
                  "(the 5 ms queue CSV has no offered / transmitted bytes)", "", sampling_table(split, p), ""]
    lines += [f"## 5. Agreement with GT1 (GT1 INTERVAL = P_on = {p.p_on * 1000:g} ms; GT3 not built yet)", "",
              agreement_table(runs, p, p.p_on), ""]
    flap = [r for r in runs if scn(r.path) in FLAPPING]
    if flap:
        lines += ["## 6. Flapping (episodes per scripted event, window to end + 2 s)", "", flapping_table(flap, p), ""]
    neg_f = [r for r in freeze if scn(r.path) in NEGATIVES]
    ev_f = [r for r in freeze if gt1._bursts(r.path)]
    if neg_f or ev_f:
        lines += ["## 7. Parameter sweep (det-*-pfifo-r1 only)", "", sweep_table(neg_f, ev_f, p), ""]
    text = "\n".join(lines)
    (campaign / "gt2-report.md").write_text(text)
    return text


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[0] not in {"score", "report"}:
        sys.exit(__doc__)
    cmd, rest, kw, dirs = argv[0], argv[1:], {}, []
    flags = {"--p-on": "p_on", "--p-off": "p_off", "--kn": "kn", "--util-floor": "util_floor"}
    while rest:
        a = rest.pop(0)
        if a in flags:
            kw[flags[a]] = float(rest.pop(0))
        else:
            dirs.append(Path(a))
    p = Params(**kw)
    for d in dirs:
        if cmd == "score":
            score(d, p)
        else:
            print(report(d, p))


if __name__ == "__main__":
    main(sys.argv[1:])
