#!/usr/bin/env python3
"""Validation of the hysteresis / don't-care bands (GT1, GT2) and of the
GT3 spec truth against the current OWD truth, with detector scoring per section 7.

    python3 scripts/gt_bands_report.py OUT.md .runs/<campaign> [...]

Sections: 1 fragmentation (tcpcubic, onoff, ramp), 2 runs without injected events (calm*, randloss)
with AMBIGUOUS share, 3 burstcap onsets unchanged, 4 AMBIGUOUS share per AQM
(flag > 30 %), 5 detector ranking per AQM for every truth variant, 6 band sweep
on det-*-pfifo-r1 only (freeze set), 7 GT3 current vs the GT3 spec truth.
"""

from __future__ import annotations

import statistics
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402
import gt_bands  # noqa: E402
import gt_score  # noqa: E402

GT1_VARIANTS = {"GT1 no bands": gt1.Params(q_band_ms=0, util_band=0), "GT1": gt1.Params(),
                "GT1 q_band 1.5": gt1.Params(q_band_ms=1.5), "GT1 q_band 3.5": gt1.Params(q_band_ms=3.5),
                "GT1 util_band 0.03": gt1.Params(util_band=0.03), "GT1 util_band 0.10": gt1.Params(util_band=0.10)}
GT2_VARIANTS = {"GT2 no bands": gt2.Params(util_band=0, rho_band=0), "GT2": gt2.Params(),
                "GT2 util_band 0.03": gt2.Params(util_band=0.03), "GT2 util_band 0.10": gt2.Params(util_band=0.10),
                "GT2 rho_band 0.02": gt2.Params(rho_band=0.02), "GT2 rho_band 0.10": gt2.Params(rho_band=0.10)}
GT3_VARIANTS = {"GT3": gt3.Params()}  # the GT3 spec truth (scripts/gt3.py)
FRAG, NEG = ("tcpcubic", "onoff", "ramp"), ("calm030", "calm065", "calm090", "randloss")
FLAG = 0.30
SLACK, RECOVERY = gt1.ONSET_SLACK_S, gt1.BURST_RECOVERY_S


def events(bursts, eps):
    """Per event: episodes overlapping it, episodes starting in [start - slack, end + recovery], lag of the first."""
    out = []
    for b in bursts:
        hop = f"{b['hop'][0]}->{b['hop'][1]}"
        during = [e for e in eps if e[0] == hop and e[1] <= b["end"] and e[2] >= b["start"] - SLACK]
        window = [e for e in eps if e[0] == hop and b["start"] - SLACK <= e[1] <= b["end"] + RECOVERY]
        out.append({"n": len(during), "n_window": len(window),
                    "lag": min(e[1] for e in during) - b["start"] if during else None,
                    "t_on": min(e[1] for e in during) if during else None})
    return out


def worker(run_dir: Path) -> dict:
    run = det_eval.Run(run_dir)
    bursts = gt1._bursts(run.path)
    starts = gt_score.alarm_starts(run)
    res = {"name": run.path.name, "aqm": run.aqm, "scn": det_eval.scenario_name(run.path), "variants": {}}
    lo, hi = det_eval.WARMUP_S, run.duration - det_eval.SHUTDOWN_S
    for name, p in [*GT1_VARIANTS.items(), *GT2_VARIANTS.items()]:
        if name.startswith("GT1"):
            raw, labels = gt1.run_truth(run, p)
            eps = [(e["hop"], e["start_s"], e["end_s"]) for e in raw]
        else:
            raw, labels = gt2.run_truth(run, p)
            eps = [(e["queue_id"], e["t_on"], e["t_end"]) for e in raw]
        by_hop = defaultdict(list)
        for x in labels:
            by_hop[x["hop"]].append((x["t_start"], x["t_end"], x["label"]))
        amb = {h: gt_bands.share(v, lo, hi)[gt_bands.AMBIGUOUS] for h, v in by_hop.items()}
        top = max(amb, key=amb.get) if amb else ""
        view = gt_score.client_view(run, eps, labels)
        res["variants"][name] = {"n": len(eps), "dur": sum(b - a for _, a, b in eps), "events": events(bursts, eps),
                                 "amb_hop": top, "amb": amb.get(top, 0.0), "score": gt_score.score(run, view, starts)}
    cur = gt3.current(run)
    if cur:
        res["variants"]["GT3 current"] = {"eps": cur[0], "score": gt_score.score(run, gt3.as_view(run, cur), starts)}
        for name, p in GT3_VARIANTS.items():
            eps3, labels3 = gt3.run_truth(run, p, path_queues=False)
            res["variants"][name] = {"eps": {s: [(e["t_on"], e["t_end"]) for e in eps3 if e["flow"] == s] for s in run.subs},
                                     "score": gt_score.score(run, gt3.view_of(run, eps3, labels3), starts)}
    return res


def _q(v, q):
    v = sorted(x for x in v if x is not None)
    return f"{v[min(len(v) - 1, int(q * len(v)))]:.3f}" if v else "-"


def _f(x, d=3):
    return "-" if x != x else f"{x:.{d}f}"


table = gt1._table


def frag_section(res):
    rows = []
    for gt in ("GT1", "GT2"):
        cells = defaultdict(lambda: defaultdict(list))
        for r in res:
            if r["scn"] in FRAG:
                for v in (f"{gt} no bands", gt):
                    cells[(r["scn"], r["aqm"])][v].append(r["variants"][v])
        for (scn, aqm), by in sorted(cells.items()):
            a, b = by[f"{gt} no bands"], by[gt]
            ev_a = [e for x in a for e in x["events"]]
            ev_b = [e for x in b for e in x["events"]]
            da, db = sum(x["dur"] for x in a), sum(x["dur"] for x in b)
            rows.append([gt, scn, aqm, len(ev_a), f"{statistics.mean(e['n_window'] for e in ev_a):.2f}" if ev_a else "-",
                         f"{statistics.mean(e['n_window'] for e in ev_b):.2f}" if ev_b else "-",
                         sum(1 for e in ev_a if e["n"] > 1), sum(1 for e in ev_b if e["n"] > 1),
                         f"{da:.1f}", f"{db:.1f}", f"{100 * (db - da) / da:+.1f} %" if da else "-"])
    return table(["GT", "scenario", "aqm", "events", "episodes / event before", "after", "split events before", "after",
                  "total episode time before (s)", "after (s)", "change"], rows)


def neg_section(res):
    rows = []
    for r in sorted(res, key=lambda r: r["name"]):
        if r["scn"] in NEG:
            v = r["variants"]
            rows.append([r["name"], r["aqm"], v["GT1 no bands"]["n"], v["GT1"]["n"], f"{100 * v['GT1']['amb']:.0f} %",
                         v["GT2 no bands"]["n"], v["GT2"]["n"], f"{100 * v['GT2']['amb']:.0f} %"])
    return table(["run", "aqm", "GT1 episodes before", "GT1 after", "GT1 AMBIGUOUS (busiest hop)", "GT2 episodes before",
                  "GT2 after", "GT2 AMBIGUOUS (busiest hop)"], rows)


def onset_section(res):
    rows = []
    for r in sorted(res, key=lambda r: r["name"]):
        if r["scn"] != "burstcap":
            continue
        row = [r["name"], r["aqm"]]
        for gt in ("GT1", "GT2"):
            a, b = r["variants"][f"{gt} no bands"]["events"], r["variants"][gt]["events"]
            diffs = [y["t_on"] - x["t_on"] for x, y in zip(a, b) if x["t_on"] is not None and y["t_on"] is not None]
            row += [f"{sum(1 for x in a if x['n'])}/{len(a)}", f"{sum(1 for x in b if x['n'])}/{len(b)}",
                    sum(1 for d in diffs if abs(d) < 1e-6), f"{max((abs(d) for d in diffs), default=0):.3f}"]
        rows.append(row)
    return table(["run", "aqm", "GT1 caught before", "after", "same t_on", "max |t_on diff| (s)",
                  "GT2 caught before", "after", "same t_on", "max |t_on diff| (s)"], rows)


def amb_section(res):
    rows, flagged = [], []
    by = defaultdict(lambda: defaultdict(list))
    for r in res:
        for gt in ("GT1", "GT2"):
            v = r["variants"][gt]
            by[r["aqm"]][gt].append(v["amb"])
            if v["amb"] > FLAG:
                flagged.append(f"{r['name']} {gt} {v['amb_hop']} {100 * v['amb']:.0f} %")
    for aqm, g in sorted(by.items()):
        rows.append([aqm] + [x for gt in ("GT1", "GT2") for x in
                             (f"{100 * statistics.mean(g[gt]):.1f} %", f"{100 * max(g[gt]):.0f} %", sum(1 for v in g[gt] if v > FLAG))])
    return table(["aqm", "GT1 AMBIGUOUS mean", "max", "runs > 30 %", "GT2 AMBIGUOUS mean", "max", "runs > 30 %"], rows), flagged


def ranking_section(res):
    """Rank detectors by F1 per AQM and truth variant; a flip = order differs from the default variant of that GT."""
    names = [*GT1_VARIANTS, *GT2_VARIANTS, "GT3 current", *GT3_VARIANTS]
    rows, flips = [], []
    for aqm in sorted({r["aqm"] for r in res}):
        pooled, order = {}, {}
        for name in names:
            pooled[name] = {d: gt_score.summarize([r["variants"][name]["score"][d] for r in res
                                                   if r["aqm"] == aqm and name in r["variants"]]) for d in gt_score.SCORED}
            f1 = {d: pooled[name][d]["f1"] if pooled[name][d]["f1"] == pooled[name][d]["f1"] else -1 for d in gt_score.SCORED}
            order[name] = sorted(f1, key=lambda d: -f1[d])
        for name in names:
            base = {"GT1": "GT1", "GT2": "GT2"}.get(name.split()[0], "GT3 current")
            flip = order[name] != order[base]
            if flip:
                f1s = ", ".join(f"{d} {pooled[name][d]['f1']:.3f}" for d in order[name])
                flips.append(f"{aqm}: {name} ranks {' > '.join(order[name])} (F1 {f1s}) vs {base}: {' > '.join(order[base])}")
            rows.append([aqm, name, " > ".join(order[name]) + (" (FLIP)" if flip else "")] +
                        [f"{_f(pooled[name][d]['f1'], 3)} / {_f(pooled[name][d]['precision'], 2)} / "
                         f"{_f(pooled[name][d]['recall'], 3)} / {_f(pooled[name][d]['fa_per_min'], 2)} / "
                         f"{_f(pooled[name][d]['latency_p50_ms'], 0)}" for d in gt_score.SCORED])
    return table(["aqm", "truth", "ranking by F1"] + [f"{d}: F1 / P / R / FA per min / lat p50 ms" for d in gt_score.SCORED],
                 rows), flips


def sweep_section(res):
    freeze = [r for r in res if r["name"].endswith("-pfifo-r1")]
    rows = []
    for name in [*GT1_VARIANTS, *GT2_VARIANTS]:
        neg = sum(r["variants"][name]["n"] for r in freeze if r["scn"] in NEG)
        ev = [e for r in freeze for e in r["variants"][name]["events"]]
        frag = [e for r in freeze if r["scn"] in FRAG for e in r["variants"][name]["events"]]
        rows.append([name, neg, f"{sum(1 for e in ev if e['n'])}/{len(ev)}", sum(1 for e in ev if e["n"] > 1),
                     f"{statistics.mean(e['n_window'] for e in frag):.2f}" if frag else "-",
                     _q([e["lag"] for e in ev], 0.5), _q([e["lag"] for e in ev], 0.9),
                     f"{100 * statistics.mean(r['variants'][name]['amb'] for r in freeze):.1f} %"])
    return table(["variant", "episodes in runs without injected events", "events caught", "split events", "episodes / event (tcpcubic, onoff, ramp)",
                  "lag p50 (s)", "lag p90", "AMBIGUOUS mean"], rows)


def gt3_section(res):
    rows = []
    by = defaultdict(list)
    for r in res:
        if "GT3 current" in r["variants"]:
            by[r["aqm"]].append(r)
    for aqm, runs in sorted(by.items()):
        for name in GT3_VARIANTS:
            n_old = n_new = matched = 0
            off, dur_old, dur_new = [], 0.0, 0.0
            for r in runs:
                old, new = r["variants"]["GT3 current"]["eps"], r["variants"][name]["eps"]
                for s in old:
                    o, c = old[s], new.get(s, [])
                    n_old += len(o)
                    n_new += len(c)
                    dur_old += sum(b - a for a, b in o)
                    dur_new += sum(b - a for a, b in c)
                    for a, b in o:
                        hit = [x for x, y in c if x <= b and y >= a]
                        if hit:
                            matched += 1
                            off.append(min(hit) - a)
            rows.append([aqm, name, n_old, n_new, matched, _q(off, 0.1), _q(off, 0.5), _q(off, 0.9),
                         f"{dur_old:.0f}", f"{dur_new:.0f}"])
    return table(["aqm", "candidate", "episodes current", "episodes candidate", "current matched by candidate",
                  "t_on(candidate) - t_on(current) p10 (s)", "p50", "p90", "episode time current (s)", "candidate (s)"], rows)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    out = Path(argv[0])
    runs = sorted(d for c in argv[1:] for d in Path(c).iterdir() if (d / "events.csv").exists())
    with ProcessPoolExecutor(max_workers=12) as pool:
        res = list(pool.map(worker, runs))
    amb, flagged = amb_section(res)
    rank, flips = ranking_section(res)
    text = "\n".join([
        "# Ground-truth bands: validation", "",
        f"Campaigns: {', '.join(Path(c).name for c in argv[1:])} ({len(res)} runs). Defaults: GT1 {gt1.Params().tag()}; "
        f"GT2 {gt2.Params().tag()}. 'Before' = the same truth with its bands set to 0. AMBIGUOUS includes short active runs "
        "that failed persistence (above the entry threshold, not an episode).", "",
        "## 1. Fragmentation: episodes per scripted event before / after bands", "", frag_section(res), "",
        "## 2. Runs without injected events: CONGESTED episodes and AMBIGUOUS share", "", neg_section(res), "",
        "## 3. burstcap: onsets unchanged by bands", "", onset_section(res), "",
        "## 4. AMBIGUOUS share of time (busiest hop per run) by AQM; runs above 30 % are low-confidence truth", "", amb, "",
        "Flagged: " + ("; ".join(flagged) if flagged else "none"), "",
        "## 5. Detector ranking per AQM (section 7 scoring; ranking by F1 of precision and episode recall)", "", rank, "",
        "Ranking flips (vs the default banded GT1 / GT2, and vs the current GT3):", "",
        *(f"- {f}" for f in flips or ["none"]), "",
        "## 6. Band sweep on det-*-pfifo-r1 only (freeze set)", "", sweep_section(res), "",
        "## 7. GT3: current OWD truth vs the K/N candidate (comparison only; det_eval unchanged)", "", gt3_section(res), "",
    ])
    out.write_text(text)
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
