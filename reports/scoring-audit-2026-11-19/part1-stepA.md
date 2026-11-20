# Scoring audit, Part 1, step A: items a, b, d, e (code reading only, 2026-11-19)

Read from the code as it runs today. No rule changed, nothing replayed. "Deviation" column: against section 8 of
docs/paper-notes-ground-truth.md, because claude/gt-modification-brief.md (spec v1.2) is not in the repository yet;
to be redone against v1.2 when the user places it.

Headline scorers: GT-L (= GT3 in code, source B) through scripts/gt_score.py `score()` (P, R, FA/min, delay) and
reports/v3-detector/score_runs.py `alarm_on()` (alarm-on R); GT-Q / GT-H through scripts/gtq_score.py `score_run()`
(GT-Q P, GT-H recall, L_obs, lead); "on at t_harm" through reports/detector-r2-2026-11-16/r2.py `on_at_harm()` (as
reports/v3-score/harm.py). Constants in scripts/det_eval.py.

## a. Time tolerances per truth

| truth / number | before onset | after onset / end | where | set how | could flatter |
|---|---|---|---|---|---|
| GT-L P, R (onset recall), delay | alarm start from t_on - 1.0 s | until min(t_end, t_on + 10 s) | gt_score.py:109; det_eval.py:73 `PRE_ONSET_LEAD_S = 1.0`, :74 `SEARCH_S = 10.0` | hand-set (det_eval window) | R and P: an alarm up to 1 s before onset or up to 10 s after it (inside the episode) is a TP. |
| GT-L alarm-on R | alarm span overlapping [t_on - 1 s, min(t_end, t_on + 10 s)] | same | score_runs.py:48 | hand-set (same window) | alarm-on R: a span that merely overlaps the window counts, incl. one opened before onset (held alarm). |
| GT-L: other alarm starts inside an episode | - | whole episode [t_on, t_end] | gt_score.py:123 | rule | P / FA: alarm starts inside an episode but outside the window are neither TP nor FP (ignored). |
| GT-Q P (collar) | t0 - W | t1 + d_obs + W | gtq_score.py:83 | W derived (gtq.py:450: max(largest base RTT through r, frame interval of f) x w_scale 1.0); d_obs measured per episode | GT-Q P: any alarm start anywhere in the collar is matched, including late in a long episode, and up to d_obs + W after its end. |
| GT-Q alarm merging | starts closer than W merged | - | gtq_score.py:79 (`merge_alarms`) | derived (W of the flow, min over its episodes) | GT-Q P: flapping alarms count once (fewer FPs as well as fewer matched). |
| GT-H recall | t0 - W | t1 + d_obs + W (same collar, any alarm start) | gtq_score.py:83, 98-100 | as GT-Q | GT-H recall: a start anywhere in the collar, also after t_harm, counts as a hit. |
| on at t_harm | none: the span must cover t_harm_600 | none | r2.py:453; harm.py header (A) | rule | a span measure: an alarm held on from an earlier episode covers t_harm (favours hold; R2 README says so). |
| lead_600 | - | first alarm start in the collar | gtq_score.py:107-108 | rule | only detected episodes; a start after t_harm gives a negative lead (kept). |

## b. Calm time for false alarms

| number | calm time = | tail after stimulus / episode | where | could flatter |
|---|---|---|---|---|
| GT-L FA / min | cells labelled CLEAR, after the 5 s warm-up; FP = alarm start in a CLEAR cell that is in no episode and in no TP window | no fixed tail. AMBIGUOUS (0.15 s rolling min of queue delay >= 5 ms) and NO_DATA (+-0.25 s around a netem delay change, or no OWD) are neither calm nor FP | gt_score.py:100, 123-127; gt3.py:161, 214-216 (`p_amb 0.15`, `d_stay_ms 5`, `exclude_s 0.25`) | FA / min: alarm starts in AMBIGUOUS / NO_DATA time and inside episodes are not counted (numerator). The denominator also shrinks to CLEAR time only, which raises FA / min, so the net direction is not fixed. |
| GT-Q FP | every alarm start (merged within W, after warm-up) in no collar and in no gray interval | collar tail d_obs + W after t1 (see a) | gtq_score.py:86-94 | GT-Q P: gray-zone alarms ignored. |
| the "+3 s" | not in the emulation scorers above. It is the simulation's Stage B calm definition: outside every stimulus window widened by [-1 s, +3 s] after the 5 s warm-up | [-1 s, +3 s] around stimulus windows | reports/sim-stageB-2026-11-18/README.md:154 | sim Stage B F1 / queue rows only. Separately, det_eval.py:645 `BURST_RECOVERY_S = 2.0` (det_matrix's older burst scoring; not used by the headline tables). |

## d. Truth onset used for delay

| truth | onset used | persistence test satisfied at | where | could flatter |
|---|---|---|---|---|
| GT-L | start of the 0.5 s persistence run: the first window whose 0.5 s rolling min of queue delay is >= 10 ms gives onset t[i] - 0.5 s + dt (back-dated); the episode's t_on = earliest channel onset at its start window | t[i] (0.5 s later) | gt3.py:167, 206 (`p_min 0.5`, `d_enter_ms 10`) | does not flatter delay (earliest onset). But delay is clamped: latency = max(0, alarm - t_on) (gt_score.py:115), so alarms up to 1 s early count as 0 ms, which lowers delay p50 / p90. |
| GT-Q | t0 = enqueue time of the first busy packet of a busy run lasting >= W (or a drop time); headline latency L_obs = alarm - t_obs, where t_obs = when the first affected packet becomes observable at the sender (ACK of it, or t_deq + base OWD + base return delay) | t0 + W (standing test) | gtq.py header lines 26-40; gtq_score.py:103 | L_obs is measured from t_obs (later than t0), so it is smaller than L_0 = alarm - t0 (also stored). The reports quote L_obs p50 / p95. |
| W | not an onset: the per-flow tolerance max(RTT, frame interval) | - | gtq.py:450 | see a. |

## e. Missed episodes and the delay statistics

| number | missed episodes | episodes with the alarm already on | where | could flatter |
|---|---|---|---|---|
| GT-L delay p50 / p90 | dropped: only detected episodes enter `latency` | an alarm started > 1 s before t_on and still on has no start in the window: a miss for onset R, a hit for alarm-on R; not in the delay | gt_score.py:110-119; score_runs.py:48-49 | delay p50 / p90 look better than with censoring (misses would be the longest delays). |
| GT-Q L_obs p50 / p95 | not in the quantiles: missed episodes get censor_ms and are reported as counts; quantiles over detected only | as GT-L: a held alarm without a new start in the collar is a miss | gtq_score.py:105, 129-131 | same: no censored values in the quantiles (paper notes item 8: Kaplan-Meier not drawn yet). |
| lead_600 | only detected harmful episodes | as above | gtq_score.py:107-108, 145 | lead p50 over detected only. |

Counts (how many episodes are held-on, early, missed) come with step B (replay).

## Deviations against paper notes section 8 (stand-in for v1.2)

- Item 8 says missed episodes are "counted as censored": they are counted, but the quantiles are over detected
  episodes only (gtq_score.py:129-131). No conflict in the wording; the Kaplan-Meier CDF is still not drawn.
- The GT-L window (1 s before, 10 s after) and the CLEAR-only calm time are not in section 8; GT-L is described
  there as a reference column with constants chosen 2026-11-07/08.
- Everything else read (collar, gray, merge within W, t_obs) matches section 8 / the gtq_score.py header.
