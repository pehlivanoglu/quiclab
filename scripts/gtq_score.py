#!/usr/bin/env python3
"""Score detector alarms against GT-Q and GT-H (spec v1.2 section 6.2 matching),
as NEW files only; the existing GT1 / GT2 / GT3 tables are untouched.

    python3 scripts/gtq_score.py .runs/<campaign> [...]
        -> <run>/truth/gtq-score-episodes.csv per run with a valid GT-Q,
           <campaign>/gtq-detector-table.{csv,md}

Alarms: gt_score.alarm_starts (the same replays as every other table), alarm
starts after the warm-up, starts closer than W merged into one alarm. The
detectors emit alarm starts, not a continuous score, so there is no theta sweep
here: one operating point per detector (the frozen detector settings).

Matching per flow (roles fixed by the spec, section 0.2):
  collar of a GT-Q episode: [t0 - W, t1 + d_obs + W]
  TP episode: a non-gray forward episode with an alarm inside its collar; FN otherwise
  FP alarm: in no collar and no gray interval (fp_reverse: inside a reverse episode only)
  alarms only in gray intervals are ignored
  precision (GT-Q) = alarms in a collar / (those + FP alarms)
  recall (GT-H, headline) = TP harmful episodes / harmful episodes, B = 600 ms
  recall (GT-Q) = TP / non-gray forward episodes
  strict GT-H precision: an alarm whose collars are all non-harmful counts as FP
  latency L_obs = t_alarm - t_obs (first alarm in the collar), L_0 = t_alarm - t0,
  L_stim = t_alarm - t_stim, lead_B = t_harm_B - t_alarm; missed episodes are
  censored at t1 + c_post (reported as counts; median / p95 over detected ones)
CIs: bootstrap over runs (2000 resamples, 95 % percentile).
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402
import gt_score  # noqa: E402
import gtq  # noqa: E402

DETECTORS = tuple(det_eval.DETECTORS)  # the same set as gt_tables.py
BOOT = 2000
EP_FIELDS = ("detector", "flow", "episode_id", "resource", "t0", "t1", "harmful_300", "harmful_600", "harmful_1000",
             "hit", "t_alarm", "L_obs_ms", "L_0_ms", "L_stim_ms", "lead_300_ms", "lead_600_ms", "lead_1000_ms",
             "censor_ms", "alarms_in_collar")


def _f(v: str) -> float:
    return float(v) if v not in ("", None) else math.nan


def merge_alarms(starts: list[float], gap: float) -> list[float]:
    out: list[float] = []
    for t in sorted(starts):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out


def score_run(run_dir: Path, starts: dict | None = None) -> tuple[list[dict], list[dict]] | None:
    """(episode rows, alarm tallies per detector x flow) or None without a valid GT-Q."""
    truth = run_dir / "truth"
    if not (truth / "gtq.csv").exists():
        return None
    run = det_eval.Run(run_dir)
    eps = det_eval.rows(truth / "gtq.csv")
    gray = det_eval.rows(truth / "gtq-gray.csv") if (truth / "gtq-gray.csv").exists() else []
    if starts is None:
        starts = gt_score.alarm_starts(run, DETECTORS)
    ep_rows, tallies = [], []
    for name in DETECTORS:
        for sid in run.subs:
            fwd = [e for e in eps if e["flow"] == sid and e["direction"] == "forward"]
            rev = [(float(e["t0"]), float(e["t1"])) for e in eps if e["flow"] == sid and e["direction"] == "reverse"]
            gr = [(float(g["t_start"]), float(g["t_end"])) for g in gray if g["flow"] == sid and g["direction"] == "forward"]
            W = min((float(e["W_ms"]) / 1e3 for e in fwd), default=0.1)
            alarms = merge_alarms([t for t in starts.get((name, sid), []) if t >= det_eval.WARMUP_S], W)
            collars = []
            for e in fwd:
                Wi, d_obs = float(e["W_ms"]) / 1e3, _f(e["d_obs_ms"]) / 1e3
                collars.append((float(e["t0"]) - Wi, float(e["t1"]) + (0 if math.isnan(d_obs) else d_obs) + Wi, e))
            matched, fp, fp_rev, ignored, fp_strict = 0, 0, 0, 0, 0
            for t in alarms:
                hits = [e for lo, hi, e in collars if lo <= t <= hi]
                if hits:
                    matched += 1
                    if not any(e["harmful_600"] == "1" for e in hits):
                        fp_strict += 1
                elif any(a <= t <= b for a, b in gr):
                    ignored += 1
                else:
                    fp += 1
                    fp_rev += any(a <= t <= b for a, b in rev)
            for lo, hi, e in collars:
                inside = [t for t in alarms if lo <= t <= hi]
                first = inside[0] if inside else math.nan
                t_obs, t0, t_stim = _f(e["t_obs"]), float(e["t0"]), _f(e["t_stim"])
                row = {"detector": name, "flow": sid, "episode_id": e["episode_id"], "resource": e["resource"],
                       "t0": e["t0"], "t1": e["t1"], **{f"harmful_{b}": e[f"harmful_{b}"] for b in gtq.BUDGETS_MS},
                       "hit": int(bool(inside)), "t_alarm": first,
                       "L_obs_ms": (first - t_obs) * 1e3, "L_0_ms": (first - t0) * 1e3,
                       "L_stim_ms": (first - t_stim) * 1e3,
                       "censor_ms": math.nan if inside else (hi - (t0 if math.isnan(t_obs) else t_obs)) * 1e3,
                       "alarms_in_collar": len(inside)}
                for b in gtq.BUDGETS_MS:
                    row[f"lead_{b}_ms"] = (_f(e[f"t_harm_{b}"]) - first) * 1e3 if e[f"harmful_{b}"] == "1" else math.nan
                ep_rows.append(row)
            tallies.append({"run": run_dir.name, "aqm": run.aqm, "detector": name, "flow": sid,
                            "alarms": len(alarms), "alarms_matched": matched, "fp": fp, "fp_reverse": fp_rev,
                            "ignored_gray": ignored, "fp_strict_gth600": fp + fp_strict,
                            "flow_hours": max(0.0, run.duration - det_eval.WARMUP_S - det_eval.SHUTDOWN_S) / 3600})
    gtq.write(truth / "gtq-score-episodes.csv", ep_rows, EP_FIELDS)
    return ep_rows, tallies


def _ratio(a: float, b: float) -> float:
    return a / b if b else math.nan


def _metrics(eps: list[dict], tal: list[dict]) -> dict:
    hit = lambda rows: sum(int(r["hit"]) for r in rows)  # noqa: E731
    harmful = {b: [r for r in eps if str(r[f"harmful_{b}"]) == "1"] for b in gtq.BUDGETS_MS}
    matched = sum(t["alarms_matched"] for t in tal)
    fp = sum(t["fp"] for t in tal)
    strict = sum(t["fp_strict_gth600"] for t in tal)
    hours = sum(t["flow_hours"] for t in tal)
    lobs = np.array([float(r["L_obs_ms"]) for r in eps if int(r["hit"]) and not math.isnan(float(r["L_obs_ms"]))])
    lobs_h = np.array([float(r["L_obs_ms"]) for r in harmful[600] if int(r["hit"])
                       and not math.isnan(float(r["L_obs_ms"]))])
    lead = np.array([float(r["lead_600_ms"]) for r in harmful[600] if int(r["hit"])])
    q = lambda a, x: round(float(np.quantile(a, x)), 1) if len(a) else ""  # noqa: E731
    return {
        "precision_gtq": _ratio(matched, matched + fp),
        "recall_gth600": _ratio(hit(harmful[600]), len(harmful[600])),
        "recall_gtq": _ratio(hit(eps), len(eps)),
        "recall_gth300": _ratio(hit(harmful[300]), len(harmful[300])),
        "recall_gth1000": _ratio(hit(harmful[1000]), len(harmful[1000])),
        "precision_gth600_strict": _ratio(matched + fp - strict, matched + fp),
        "fa_per_flow_hour": _ratio(fp, hours),
        "fp_reverse": sum(t["fp_reverse"] for t in tal),
        "L_obs_p50_ms": q(lobs, 0.5), "L_obs_p95_ms": q(lobs, 0.95),
        "L_obs_gth_p50_ms": q(lobs_h, 0.5), "L_obs_gth_p95_ms": q(lobs_h, 0.95),
        "lead600_p50_ms": q(lead, 0.5), "alarm_before_harm": _ratio(int((lead > 0).sum()), len(harmful[600])),
        "episodes": len(eps), "gth600_episodes": len(harmful[600]), "censored": len(eps) - hit(eps),
    }


def _counts(eps: list[dict], tal: list[dict]) -> np.ndarray:
    """Per-run sums the bootstrap resamples: matched, fp, episodes, hit, gth600, gth600 hit."""
    h = [r for r in eps if str(r["harmful_600"]) == "1"]
    return np.array([sum(t["alarms_matched"] for t in tal), sum(t["fp"] for t in tal), len(eps),
                     sum(int(r["hit"]) for r in eps), len(h), sum(int(r["hit"]) for r in h)], dtype=float)


def _boot(by_run: dict[str, tuple[list, list]], rng) -> dict[str, tuple[float, float]]:
    """95 % percentile intervals of precision (GT-Q), recall (GT-H 600), recall (GT-Q), runs resampled."""
    c = np.array([_counts(*v) for v in by_run.values()])
    pick = rng.integers(0, len(c), size=(BOOT, len(c)))
    tot = c[pick].sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        vals = {"precision_gtq": tot[:, 0] / (tot[:, 0] + tot[:, 1]),
                "recall_gth600": tot[:, 5] / tot[:, 4], "recall_gtq": tot[:, 3] / tot[:, 2]}
    out = {}
    for k, v in vals.items():
        v = v[~np.isnan(v)]
        out[k] = (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) if len(v) else (math.nan, math.nan)
    return out


def _score_one(run_dir: Path):
    res = score_run(run_dir)
    if res is None:
        return None
    eps, tal = res
    return run_dir, tal[0]["aqm"] if tal else "?", eps, tal


def report(campaigns: list[Path], out: Path | None = None) -> list[dict]:
    """campaigns: folders holding run dirs. Cells: per AQM, per campaign folder, and all."""
    from concurrent.futures import ProcessPoolExecutor
    rng = np.random.default_rng(1)
    runs = [p for c in campaigns for p in sorted(c.iterdir()) if (p / "truth" / "gtq.csv").exists()]
    per: dict[tuple[str, str, str], dict[str, tuple[list, list]]] = defaultdict(dict)
    with ProcessPoolExecutor(max_workers=12) as pool:
        for res in pool.map(_score_one, runs):
            if res is None:
                continue
            run_dir, aqm, eps, tal = res
            key = f"{run_dir.parent.parent.name}/{run_dir.parent.name}/{run_dir.name}"
            for name in DETECTORS:
                cell = ([r for r in eps if r["detector"] == name], [t for t in tal if t["detector"] == name])
                per[("aqm", aqm, name)][key] = cell
                per[("group", run_dir.parent.name, name)][key] = cell
                per[("all", "all", name)][key] = cell
    table = []
    for (level, cell_name, name), by_run in sorted(per.items()):
        eps = [r for c in by_run.values() for r in c[0]]
        tal = [t for c in by_run.values() for t in c[1]]
        row = {"level": level, "cell": cell_name, "detector": name, "runs": len(by_run), **_metrics(eps, tal)}
        for key, (lo, hi) in _boot(by_run, rng).items():
            row[f"{key}_ci"] = "" if math.isnan(lo) else f"[{lo:.2f}, {hi:.2f}]"
        table.append(row)
    out = out or (campaigns[0] if len(campaigns) == 1 else campaigns[0].parent)
    gtq.write(out / "gtq-detector-table.csv", table, list(table[0]) if table else ("level",))
    cols = ("cell", "detector", "runs", "episodes", "gth600_episodes", "precision_gtq", "precision_gtq_ci",
            "recall_gth600", "recall_gth600_ci", "recall_gtq", "recall_gth300", "recall_gth1000",
            "precision_gth600_strict", "fa_per_flow_hour", "L_obs_p50_ms", "L_obs_p95_ms", "L_obs_gth_p50_ms",
            "lead600_p50_ms", "alarm_before_harm")
    fmt = lambda v: f"{v:.3f}" if isinstance(v, float) and not math.isnan(v) else ("-" if isinstance(v, float) else str(v))  # noqa: E731
    lines = ["# Detectors vs GT-Q / GT-H (new table; GT1/GT2/GT3 tables unchanged)", "",
             "Precision vs GT-Q, headline recall vs GT-H at B = 600 ms, second recall vs GT-Q; "
             "alarms = gt_score.alarm_starts merged within W. CIs: runs resampled (2000).", ""]
    for level in ("all", "aqm", "group"):
        lines += [f"## {level}", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        lines += ["| " + " | ".join(fmt(r[c]) for c in cols) + " |" for r in table if r["level"] == level]
        lines.append("")
    (out / "gtq-detector-table.md").write_text("\n".join(lines) + "\n")
    return table


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    out = None
    if "--out" in argv:
        i = argv.index("--out")
        out = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    report([Path(a) for a in argv], out)


if __name__ == "__main__":
    main(sys.argv[1:])
