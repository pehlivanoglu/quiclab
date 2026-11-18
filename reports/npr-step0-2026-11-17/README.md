# NPR STEP 0: do the assumptions hold? (2026-11-17)

**Answer: no, not on the frozen events as they are.**
- On single-queue cells the majority vote of a truly congested leaf is wrong in 5-27 % of its events. Independent
  misses with the measured miss rate would predict 0-4 %.
- Misses are strongly correlated within an event: rho 0.4-0.8, variance 2-30x the binomial value, growing with
  the leaf size.
- **The cause is the event formation, not the detector.** 94-100 % of the "true 0" members of a congested leaf (all
  sizes except 3) have their onset in a neighbouring event within 2 s. A leaf's onsets are spread over more than
  the frozen ±150 ms / 300 ms windows, so whole sub-groups land in the next or the previous event. Members with no
  onset nearby are 0-6 %.
- With those members handled (merged into one event, or set NA), the profiles of single-queue leaves would be
  close to clean. That is a choice the note does not specify (FLAG 1).
- fq_codel / cake cells do not fit the model under any choice: miss rate 0.3-0.7, rho below 0, majority error 15-75
  %. Per-flow queues make members of one link disagree.

Data: 263 runs (v3 161: 140 single-queue, 21 fq; K1 G1-G3 and A4-A7 102: 87 single-queue, 15 fq), 10 003 events.
Frozen v2-owd onsets, frozen SETS event formation, nothing changed. Full tables: [tables.md](tables.md).

## 0.1 Within-leaf agreement

Single-queue cells, events where at least one member of the leaf has 1:

| leaf size | events | k / n in [0.25, 0.75] | k = n | k / n p10 / p50 |
|---|---|---|---|---|
| 2 | 443 | 0.08 | 0.92 | 1.00 / 1.00 |
| 4 | 6187 | 0.16 | 0.84 | 0.50 / 1.00 |
| 5 | 406 | 0.11 | 0.78 | 0.50 / 1.00 |
| 8 | 260 | 0.10 | 0.77 | 0.33 / 1.00 |
| 9 | 427 | 0.08 | 0.80 | 0.67 / 1.00 |
| 12 | 137 | 0.13 | 0.69 | 0.12 / 1.00 |
| 16 | 296 | 0.19 | 0.53 | 0.13 / 1.00 |
| 24 | 149 | 0.10 | 0.59 | 0.06 / 1.00 |
| 40 | 172 | 0.17 | 0.44 | 0.05 / 0.97 |

- The distribution is bimodal: mostly k = n, with a second mode near 0 for large leaves (p10 0.05-0.13 at 16-40).
  Those are the fragments: one or two members in an event, the rest in the next one.
- By event type: "only this leaf", "this leaf and others" and "only upstream" look alike (k = n in 75-93 % up to size
  9). "No congested egress" events (truth: no hot egress on the leaf's path) are mostly at size 4, i.e. T-BASE: 649
  events, 0.53 in the middle band, but k = n in 0.47. Congestion below the scorer's strict-hot rule (R1: keyframe-
  driven onsets) is seen by all members and labelled "off" by the truth (FLAG 2).
- fq cells: k / n in the middle band 0.51-0.82, k = n only 0.18-0.49.

## 0.2 Majority-vote error

Single-queue cells, on events (r1 / r2 shown; r3-r5 are K1 only, in tables.md):

| leaf size | on error r1 / r2 | predicted (independent) | m r1 / r2 | off error r1 / r2 | f |
|---|---|---|---|---|---|
| 2 | 0.074 / 0.009 | 0.028 / 0.002 | 0.14 / 0.03 | 0.006 / 0.000 | 0.00 |
| 4 | 0.082 / 0.064 | 0.009 / 0.005 | 0.10 / 0.08 | **0.150 / 0.147** | 0.16 |
| 5 | 0.075 / 0.104 | 0.010 / 0.020 | 0.10 / 0.12 | 0 / 0 | 0 |
| 8 | 0.107 / 0.047 | 0.002 / 0.003 | 0.10 / 0.08 | 0 / 0 | 0.01 |
| 9 | 0.095 / 0.208 | 0.004 / 0.032 | 0.10 / 0.20 | 0 / 0 | 0 |
| 12 | 0.188 / 0.070 | 0.008 / 0.005 | 0.20 / 0.10 | 0 / 0 | 0.01 |
| 16 | 0.227 / 0.202 | 0.006 / 0.004 | 0.20 / 0.20 | - | - |
| 24 | 0.196 / 0.196 | 0.009 / 0.001 | 0.18 / 0.15 | - | - |
| 40 | 0.246 / 0.143 | 0.019 / 0.006 | 0.25 / 0.13 | - | - |

- On error is 5-25x the independence prediction everywhere.
- The off error is 0 except at size 4 (0.15-0.19, all reps): the T-BASE "no congested egress" events of 0.1, a truth
  issue rather than false inclusion (FLAG 2). Off events are few for large leaves (G1 runs have one leaf).
- Not reliable: size 9 r1 0.095 against r2 0.208; size 12 and 40 r1 against r2. The cells are small (43-144 events)
  and m differs between reps by the same factor.

## 0.3 Burstiness

Variance ratio and rho (beta-binomial, method of moments), single-queue, r1 / r2:
- pfifo: size 4 2.59 / 2.58, rho 0.54 / 0.54; size 9 rho 0.64 / 0.75; size 16 0.49 / 0.62; size 40 0.55 / 0.61.
- codel: size 4 rho 0.61 / 0.47; size 9 0.77 / 0.72; size 40 0.62 / 0.50.
- pie: size 4 rho 0.69 / 0.54. red: size 4 0.48 / 0.31.
- K1 r3-r5 agree (rho 0.4-1.0).
- Size 2 is noisy (rho -0.08 to 1.0, 21-55 events): not reliable.
- fq_codel: rho -0.80 to -0.01 (variance below binomial): members anti-correlated, one sub-queue at a time.

rho is clearly above 0 on single-queue cells, so V-bb is warranted by the note's own rule. But the correlation comes
from the split events (next section), not from a member-level miss process.

## 0.4 NA accounting

Members of truly on leaves that SETS counts as missed (not in the event):

| cells | events | members not 1 | NA: in alarm | NA: no ACK | NA: absent | true 0 |
|---|---|---|---|---|---|---|
| single, events with k >= 1 | 7869 | 8488 | 3776 (0.44) | 0 | 7 | 4705 (0.55) |
| single, all on events | 9285 | 14781 | 8901 (0.60) | 0 | 7 | 5873 (0.40) |
| fq, events with k >= 1 | 1622 | 2183 | 805 (0.37) | 0 | 4 | 1374 (0.63) |

Where the remaining true 0 goes (single-queue, on events): the member's onset lands in another event within 2 s.

| leaf size | true-0 members | onset in a later event (<= 2 s) | only in an earlier event (<= 2 s) | neither |
|---|---|---|---|---|
| 2 | 80 | 0.88 | 0.12 | 0.00 |
| 3 | 67 | 0.33 | 0.12 | 0.55 |
| 4 | 1918 | 0.74 | 0.24 | 0.03 |
| 8 | 203 | 0.60 | 0.38 | 0.01 |
| 9 | 528 | 0.74 | 0.26 | 0.00 |
| 16 | 893 | 0.40 | 0.60 | 0.00 |
| 40 | 1184 | 0.52 | 0.42 | 0.06 |

- No-ACK never applies (the video never stops while a client is present). Absent is rare (churn and join runs).
- "In alarm" is 44-60 % of the members SETS counts as missed: the NA rule removes almost half of them.
- Size 3 (67 members, r2 only) is the one exception, with 55 % "neither": not reliable.

## 0.5 Separation of sibling leaves

Share of events with at least one of two sibling leaves on in which exactly one is on (truth):

| scenario | pairs | events | exactly one on (p10 / p50 per pair) |
|---|---|---|---|
| huneven | 42 | 2902 | 0.78 (0.74 / 0.78) |
| gsize2 | 6 | 204 | 0.70 (0.68 / 0.70) |
| llong | 4 | 51 | 0.69 |
| hdepth | 8 | 273 | 0.57 |
| hhier | 27 | 1714 | 0.46 (0.40 / 0.44) |
| hindep | 14 | 912 | 0.42 (0.35 / 0.43) |
| hhier / hindep, fq | 5 | 541 | 0.41-0.47 |

Every sibling pair is separated in at least ~35 % of its events (p10), so the cross-event information to split
siblings exists in every scenario type.

## 0.6 Dependence between events

- Single-queue: lag-1 autocorrelation of a leaf's on / off sequence is about 0 at size 4 (r1 0.02, r2 -0.03, 78-84
  leaves). It is 0.1-0.35 in small cells of 2-12 members (2-5 leaves, not reliable). The miss count has no
  autocorrelation (|lag 1| <= 0.2, mostly < 0.1).
- fq cells: on / off lag 1 0.2-0.6 (a congested sub-queue stays congested over consecutive events).
- Treating events as independent is acceptable on single-queue cells.

## Choices the note did not specify (FLAG)

1. **Split events.** A congested leaf's onsets spread over several frozen events. The choice: treat a member whose
   onset lies in a neighbouring event within W s as NA (or merge events within W), with W (P) e.g. 1-2 s; or keep
   them 0, which gives the correlated misses above. This decides whether profiles are clean.
2. **Truth "on".** A leaf is on when it or an egress containing it is strict-hot (the common scorer's rule over
   t0 + NEG_SPAN). Congestion below that rule counts as off, which explains the size-4 off error. An alternative is
   the looser GT1 episode overlap.
3. **NA windows (T / M).** No ACK in [t0 - 0.15 s, t0 + 1.3 s]; in alarm = an onset episode with t_onset < t0 -
   0.15 s and end >= t0 (t_onset because the frozen formation anchors events on it; t_arrival would make some
   of these 0).
4. **Group size** = the true leaf size, not the number of non-NA members.
5. **Majority with even n:** "at least half" for off errors and "fewer than half" for on errors, as the note says;
   events with n = 0 skipped.
6. **Sibling** = leaves with the same set of ancestors; denominator of 0.5 = events with at least one of the pair on.
7. **Reps:** v3 r1 / r2 and K1 r1 / r2 share a label; K1 adds r3-r5 (A blocks five seeds, G blocks three).
8. **Predictions** in 0.2 use m and f per cell class, leaf size and rep.

## Method

- [npr0.py](npr0.py) builds X per run from the frozen onset log (grouping_adapter.build, v2-owd, as R1 T100) and the
  frozen SetsEngine closes, plus the truth (grouping_score.truth_sets, strict_hot on GT1 hop episodes).
- [npr0_report.py](npr0_report.py) builds the tables.
- K1 runs had no frozen tick files: built under cache/ in this folder (the frozen code would have written them into
  the run folders; it was redirected, and a guard refuses to write inside a run folder).
- Batch: nice 19, 2 workers, 17:19-17:42. Nothing written inside run folders (checked with find -newermt).
