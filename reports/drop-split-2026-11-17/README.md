# Pre-drop / post-drop split (K5-sender note, 1.5; v3 runs, 2026-11-17)

**Answer: no. The headline detector and grouping results do not depend on the sender's drops.** On single-queue
cells (C blocks, r1 / r2):
- The frozen detector's first alarm comes before the first GOP drop in 99-100 % of the windows that have a drop,
  by a median of 2.0 s (p10 1.2-1.3 s). 99 % of the onsets SETS uses in those windows are also before the drop.
- Restricted to the part of drop windows before t_drop, v2-owd has GT3 P 1.00, R 0.99, delay p50 212 / 204 ms,
  GT-Q P 1.00, on at t_harm 1.00: the same as or better than over all windows (P 1.00, R 0.92, p50 218 / 208 ms).
- In windows with no drop (the mild ones: u 1.05 and 2 s windows dominate) the detector is somewhat slower and
  misses more onsets (R 0.87 / 0.84, p50 250 / 237 ms, FA 0.03 / 0.05 per min), as expected for weaker congestion.
- The ranking against the baselines holds in every part: v2-owd is ~120-135 ms earlier than GCC and ~20-60 ms
  earlier than the best simple threshold (D3) at p50, with fewer false alarms.
- Grouping (frozen SETS, common scorer, single-queue): pair P 0.998 / 0.979 over all windows, 1.000 / 0.987 in
  no-drop windows, 0.996 / 0.974 before t_drop (k = 2; k = 3: 0.985 / 0.966, 0.989 / 0.983, 0.980 / 0.956). All
  pass the 0.93 condition. Pair recall is lower in no-drop windows (0.85 against 0.88), again the milder windows.
- After t_drop few new GT3 onsets remain (639 / 621 of ~10 000): the queue has been building for ~2 s, so the episodes
  started earlier. Those few are scored worse by every detector; that part is not a headline number.

How often drops happen: 33 % of the stimulus windows have none (BBR, both reps). By intensity: u 1.05 62-64 %,
u 1.15 29-30 %, u 1.3 13 % without a drop; by duration: 2 s windows 55-57 %, 5 s 25-27 %, 10 s 16-17 %. PIE and
RED have the most windows without a drop (0.65 and 0.61-0.83), fq_codel the fewest (0.19-0.23). Full tables:
[tables.md](tables.md).

fq_codel / cake: the alarm comes before the drop in 96-97 % of drop windows, the SETS onsets in 83-84 %. The
detector numbers are again the same or better before t_drop. Grouping on fq cells is weak in every part (pair P
0.33-0.48, same-link truth; R1 reported 0.26 / 0.34 for all closes), with no pattern by drop.

Runs with no drop in any window: 9 single-queue runs (C15 random loss, C5 tcp codel, C6 join), pair P 1.000 /
1.000 but few closes (43 / 54) and low recall; 4 fq / cake runs with too few events to score.

## Definitions

- Stimulus window = grouping/windows.json, span [start, end + 2 s] (grouping_score's tail). t_drop = the first
  sender drop (publishers/pub/<sub>-drops.csv) of any client listed as behind the window's congested egress
  ("expected", sub-ctrl excluded) inside the span; none if no drop.
- Each client's time is put in one part by the windows that list it: after t_drop, before t_drop, or in a window
  with no drop (priority in that order where windows overlap).
- Detector scoring: gt_score.score's rules, unchanged, restricted to the part. GT3 episodes counted by their onset;
  for "before t_drop" the TP alarm must also start before t_drop. False alarms per minute of CLEAR time inside the
  part. These FA rates are over CLEAR time inside windows only, so they are higher than R2's whole-run rates.
  GT-Q P from gtq_score.score_run on the alarm starts in the part. GT-H: harmful 600 ms episodes with t_harm in the
  part, covered by an alarm span.
- Grouping: the frozen SetsEngine replayed on the frozen v2-owd onset log (as R1 T100); the engine sees every event,
  only the scorer is fed the closes whose t0 is in the part (window membership by t0 in [start - 1 s, end + 2 s]).
- Detectors: v2-owd (frozen), D2-gcc and D3-10ms-200ms as in R2.
- Batch: nice 19; 4 workers 13:52-13:57, then 2 workers (the new limit) until 14:14. Nothing written inside run
  folders. Campaign overlap check: .runs/2026-11-16_0105_v4-K2/batch-overlap.md.

Code: [ds.py](ds.py), [ds_report.py](ds_report.py); rows.jsonl (one row per run).
