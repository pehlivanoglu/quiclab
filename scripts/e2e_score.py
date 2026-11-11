#!/usr/bin/env python3
"""End-to-end scores that join the detector and the grouping on the same
event (campaign v2 review, "overall performance"):

    python3 scripts/e2e_score.py RUN... [--source shadow-owd] [--out e2e.md]

Per shared stimulus window (>= 2 expected clients, hit by the GT1 router truth):
  n_expected, n_alarmed    expected clients whose detector alarm (the grouping
                           adapter's onsets, <run>/<grouping dir>/onsets.jsonl)
                           starts inside [start, end + 2 s];
  ecg_case                 the case of the first ECG event whose members
                           include an expected client and whose t0 falls in the
                           window (A / A-superset / GLOBAL / C / D / SOLO), or none;
  attributed               the event's members are a subset of the expected set
                           (no outsider was pulled in);
  t_group_s                seconds from the window start until the pairwise
                           decision says SAME for every expected pair (the
                           first event close at or after the start that does), or
                           null when it never happens in the run.
Alarm precision, two ways (same windows, same truth):
  single      every alarm start of a client: true when inside a GT1 window the
              client was expected in (+ 2 s), false otherwise;
  grouped     only the alarm starts that an ECG event joined with >= 1 other
              member (case A / A-superset / GLOBAL / C): the group-confirmed alarms.
  Both with the median latency from the window start.
Negatives (runs without windows): false alarms per minute over all clients,
false groups = confirmed leaves with >= 2 members at the end, per minute of run.
Writes <run>/<grouping dir>/e2e.json; the campaign driver aggregates them.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402

RECOVERY_S = d.BURST_RECOVERY_S
GROUP_CASES = ("A", "A-superset", "GLOBAL", "C")


def ecg_dir(src: str, tag: str = "") -> str:
    return "grouping" + (f"-{tag}" if tag else "") + ("" if src == "shadow" else f"-{src}")


def onsets_of(gdir: Path) -> dict[str, list[tuple[float, float]]]:
    """Flow -> [(t_arrival, end)] from the adapter's onset log."""
    out = defaultdict(list)
    path = gdir / "onsets.jsonl"
    if not path.exists():
        return {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if r.get("kind") == "onset":
            o = r["onset"] if "onset" in r else r
            flow = o.get("flow")
            t = o.get("t_arrival", o.get("t"))
            if flow is not None and t is not None:
                out[flow].append((float(t), float(o.get("end", t))))
    return dict(out)


def first_same_close(pairs_t: list[dict], pairs: list[str], t_from: float) -> float | None:
    for e in pairs_t:
        if e["t"] >= t_from and all(e["pairs"].get(p) == "SAME" for p in pairs):
            return e["t"]
    return None


def score_run(run_dir: Path, src: str = "shadow-owd", tag: str = "") -> dict | None:
    gdir = run_dir / ecg_dir(src, tag)
    m_path, pt_path = gdir / "metrics.json", gdir / "pairs_t.json"
    if not m_path.exists():
        return None
    m = json.loads(m_path.read_text())
    pairs_t = json.loads(pt_path.read_text()) if pt_path.exists() else []
    onsets = onsets_of(gdir)
    duration = float(d.Run(run_dir).duration)
    bursts = m.get("bursts", [])
    shared = [b for b in bursts if len(b.get("expected", [])) >= 2 and b.get("hit")]
    events = m.get("events", [])
    rows = []
    for b in shared:
        lo, hi = b["start"], b["end"] + RECOVERY_S
        expected = set(b["expected"])
        alarmed = {f for f in expected if any(lo <= t <= hi for t, _ in onsets.get(f, []))}
        ev = next((e for e in events if lo - 1.0 <= e["t0"] <= hi and expected & set(e["members"])), None)
        exp_sorted = sorted(expected)
        pairs = [f"{f}|{g}" for i, f in enumerate(exp_sorted) for g in exp_sorted[i + 1:]]
        t_group = first_same_close(pairs_t, pairs, b["start"])
        rows.append({"start": b["start"], "end": b["end"], "target": b.get("target"), "n_expected": len(expected),
                     "n_alarmed": len(alarmed), "ecg_case": ev["case"] if ev else None,
                     "attributed": (set(ev["members"]) <= expected) if ev else None,
                     "members": sorted(ev["members"]) if ev else [],
                     "t_group_s": round(t_group - b["start"], 3) if t_group is not None else None})
    # alarm precision: single vs group-confirmed, every client, every alarm start
    windows_of = defaultdict(list)
    for b in bursts:
        for f in b.get("expected", []):
            windows_of[f].append((b["start"], b["end"] + RECOVERY_S))
    grouped_members = {(f, e["t0"]) for e in events if e["case"] in GROUP_CASES and len(e["members"]) >= 2
                       for f in e["members"]}
    single = {"tp": 0, "fp": 0, "lat": []}
    grouped = {"tp": 0, "fp": 0, "lat": []}
    for f, starts in onsets.items():
        for t, _ in starts:
            win = next((w for w in windows_of.get(f, []) if w[0] <= t <= w[1]), None)
            in_group = any(abs(t0 - t) <= 1.0 for g, t0 in grouped_members if g == f)
            for tally, use in ((single, True), (grouped, in_group)):
                if not use:
                    continue
                if win:
                    tally["tp"] += 1
                    tally["lat"].append(t - win[0])
                else:
                    tally["fp"] += 1

    def summary(t):
        n = t["tp"] + t["fp"]
        return {"alarms": n, "tp": t["tp"], "fp": t["fp"], "precision": t["tp"] / n if n else None,
                "latency_p50_s": round(statistics.median(t["lat"]), 3) if t["lat"] else None}
    leaves = [l for l in m.get("leaves", {}).values() if l.get("kind") == "leaf" and l.get("confirmed")
              and len(l.get("members", [])) >= 2]
    minutes = max(duration - d.WARMUP_S, 1e-9) / 60
    out = {"run": run_dir.name, "source": src, "negative": not bursts,
           "shared_windows": rows,
           "detected_all": sum(r["n_alarmed"] == r["n_expected"] for r in rows),
           "attributed_ok": sum(bool(r["attributed"]) for r in rows),
           "grouped_cases": sum(r["ecg_case"] in GROUP_CASES for r in rows),
           "t_group_p50_s": statistics.median([r["t_group_s"] for r in rows if r["t_group_s"] is not None])
           if any(r["t_group_s"] is not None for r in rows) else None,
           "alarm_single": summary(single), "alarm_grouped": summary(grouped),
           "false_alarms_per_min": round(single["fp"] / minutes, 3),
           "false_groups": len(leaves) if not bursts else None,
           "false_groups_per_min": round(len(leaves) / minutes, 3) if not bursts else None}
    (gdir / "e2e.json").write_text(json.dumps(out, indent=1))
    return out


def fmt(v) -> str:
    return "-" if v is None else f"{v:.2f}" if isinstance(v, float) else str(v)


def table(results: list[dict], cell_of=lambda r: r["run"]) -> list[str]:
    """Markdown rows per cell (median over the results of a cell)."""
    by = defaultdict(list)
    for r in results:
        by[cell_of(r)].append(r)
    lines = ["| cell | n | shared windows | all members detected | attributed to the group | grouped case | "
             "t_group p50 s | single alarm P / lat s | grouped alarm P / lat s | FA/min | false groups/min |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]

    def med(xs):
        xs = [x for x in xs if x is not None]
        return statistics.median(xs) if xs else None
    for cell, rs in sorted(by.items()):
        n_w = sum(len(r["shared_windows"]) for r in rs)
        lines.append(f"| {cell} | {len(rs)} | {n_w} | {sum(r['detected_all'] for r in rs)} | "
                     f"{sum(r['attributed_ok'] for r in rs)} | {sum(r['grouped_cases'] for r in rs)} | "
                     f"{fmt(med([r['t_group_p50_s'] for r in rs]))} | "
                     f"{fmt(med([r['alarm_single']['precision'] for r in rs]))} / "
                     f"{fmt(med([r['alarm_single']['latency_p50_s'] for r in rs]))} | "
                     f"{fmt(med([r['alarm_grouped']['precision'] for r in rs]))} / "
                     f"{fmt(med([r['alarm_grouped']['latency_p50_s'] for r in rs]))} | "
                     f"{fmt(med([r['false_alarms_per_min'] for r in rs]))} | "
                     f"{fmt(med([r['false_groups_per_min'] for r in rs]))} |")
    return lines


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--source", default="shadow-owd")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    results = [r for r in (score_run(p, a.source, a.tag) for p in a.runs) if r]
    lines = table(results)
    print("\n".join(lines))
    if a.out:
        a.out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
