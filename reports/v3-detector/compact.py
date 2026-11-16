#!/usr/bin/env python3
"""Compact per-cell table (main detector, reps pooled by summing counts): every truth in one row.

    .venv/bin/python3 reports/v3-detector/compact.py > reports/v3-detector/compact.md
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import summarize as S  # noqa: E402

rows, _ = S.load()
by = defaultdict(list)
for r in rows:
    by[(r["block"], r["type"], r["variant"], r["aqm"])].append(r)
print("| block | scenario | variant | AQM | GT1 ep / R / R-on | GT2 ep / R | GT3 ep / P / R / R-on / FA min | lat p50 / p90 ms | "
      "GT-Q P / R | GT-H600 ep / R |")
print("|---|---|---|---|---|---|---|---|---|---|")
for k in sorted(by, key=S.border):
    rs = by[k]
    g1, g2, g3 = (S.gsum(rs, t, S.MAIN) for t in S.TRUTHS)
    q = S.qsum([r for r in rs if r.get("gtq")], S.MAIN)
    f = S.f
    print(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {g1['episodes']} / {f(g1['recall'])} / {f(g1['alarm_on_recall'])} | "
          f"{g2['episodes']} / {f(g2['recall'])} | {g3['episodes']} / {f(g3['precision'])} / {f(g3['recall'])} / "
          f"{f(g3['alarm_on_recall'])} / {f(g3['fa_per_min'])} | {f(g3['latency_p50_ms'], 0)} / {f(g3['latency_p90_ms'], 0)} | "
          + (f"{f(q['precision_gtq'])} / {f(q['recall_gtq'])} | {q['gth600_episodes']} / {f(q['recall_gth600'])} |" if q else "- | - |"))
