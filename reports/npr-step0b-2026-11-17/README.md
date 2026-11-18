# NPR STEP 0b: event formation candidates (2026-11-17)

## Final selection (user's final rule, 2026-11-17): every candidate passes; **E3 is selected**

Condition 1 restored to its pre-set form (strict-hot only); condition 2 unchanged; condition 3 re-specified
(gtq_score on the member's own onset, within E0 + 0.005). Single-queue cells, r1 / r2:

| candidate | 1: on error (strict-hot) | 2: sibling separation | 3: false-inclusion share | constants | member set final p50 / p90 s | result |
|---|---|---|---|---|---|---|
| E0 (frozen) | 0.085 / 0.070 | 0.612 / 0.616 | 0.0004 / 0.0007 | reference | 1.31 / 1.32 | reference |
| E1-0.5 | 0.010 / 0.010 | 0.629 / 0.628 | 0.0004 / 0.0008 | W | 0.50 / 0.50 | pass |
| E1-1 | 0.000 / 0.002 | 0.647 / 0.646 | 0.0004 / 0.0009 | W | 1.00 / 1.00 | pass |
| E1-2 | 0.000 / 0.002 | 0.653 / 0.649 | 0.0005 / 0.0002 | W | 2.00 / 2.00 | pass |
| E2 | 0.000 / 0.001 | 0.668 / 0.659 | 0.0005 / 0.0001 | none | 7.42 / 14.20 | pass |
| **E3** | 0.001 / 0.001 | **0.682 / 0.669** | 0.0005 / 0.0001 | none | 6.26 / 11.70 | **pass, selected** |
| E4-1 | 0.001 / 0.002 | 0.612 / 0.616 | 0.0004 / 0.0007 | W | 1.31 (+1 s for NA) | pass |
| E4-2 | 0.000 / 0.002 | 0.612 / 0.616 | 0.0004 / 0.0007 | W | 1.31 (+2 s for NA) | pass |

- Selection as written: fewest constants -> E2 and E3 (no time constant, no cap: every event closes when its
  members' alarms end; max duration 48.8 s E2, 32.2 s E3). Between them, the higher sibling separation in both reps:
  E3 (0.682 / 0.669 against 0.668 / 0.659).
- STEP 1-3 run on E3 (primary) and on E1-0.5 (second, labelled as such: its member set is final after 0.5 s
  against 6-7 s for E3).
- The two earlier rule versions follow for the record.

## Re-specified rule (user, 2026-11-17): no candidate passes; none is selected. STEP 1-3 not started.

Single-queue cells, r1 / r2 (rows recomputed with each member's gtq_score class; 254 of 263 runs have usable GT-Q):

| candidate | on error (new "truly congested") | false-inclusion share | sibling separation | old off error (strict-hot) | member set final p50 s |
|---|---|---|---|---|---|
| E0 | 0.113 / 0.098 | 0.0004 / 0.0007 | 0.612 / 0.616 | 0.098 / 0.087 | 1.31 |
| E1-0.5 | 0.051 / 0.046 | 0.0004 / 0.0008 | 0.629 / 0.628 | 0.107 / 0.094 | 0.50 |
| E1-1 | 0.038 / 0.039 | 0.0004 / 0.0009 | 0.647 / 0.646 | 0.137 / 0.125 | 1.00 |
| E1-2 | 0.038 / 0.041 | 0.0005 / 0.0002 | 0.653 / 0.649 | 0.166 / 0.170 | 2.00 |
| E2 | 0.039 / 0.036 | 0.0005 / 0.0001 | 0.668 / 0.659 | 0.316 / 0.340 | 7.42 |
| E3 | 0.040 / 0.036 | 0.0005 / 0.0001 | 0.682 / 0.669 | 0.300 / 0.313 | 6.26 |
| E4-1 | 0.036 / 0.033 | 0.0004 / 0.0007 | 0.612 / 0.616 | 0.102 / 0.094 | 1.31 |
| E4-2 | 0.031 / 0.033 | 0.0004 / 0.0007 | 0.612 / 0.616 | 0.115 / 0.100 | 1.31 |

- Condition 3 (false inclusion within E0 + 0.005) and condition 2 (sibling >= 0.30) now pass for every candidate.
- **Condition 1 fails for every candidate (0.031-0.051 > 0.02).** The cause is the new "truly congested" rule:
  - The gtq_score branch ("at least half of the leaf's onsets are true positives") adds 223-250 leaf-events per
    rep that strict-hot does not, about 8 % of the on events.
  - Their majority-vote error is 44-47 %.
  - Almost all of those errors (98-114 per rep) are leaves where exactly one member has an onset: that client's own
    flow has a real GT-Q episode while the other members stay silent. "Half of one onset" makes the whole leaf
    "truly congested".
- On the strict-hot leaf-events alone the on error is E1-0.5 0.010 / 0.010, E4-1 0.001 / 0.002, E4-2 and E1-1/2,
  E2, E3 <= 0.002, against E0 0.085 / 0.070.
- The rule is applied as written and not changed; the decision is the user's.
- In E2 / E3 no cap is needed: every event closes when its members' alarms end (max 48.8 s and 32.2 s); there is no
  cap to report.

The first report (original rule) follows unchanged.

**No candidate passes the pre-set rule; none is selected. Stopped here, as the note says.**
- Every candidate meets the first two conditions on single-queue cells, both reps:
  - majority-vote error on truly congested leaves 0.000-0.010 (E0: 0.085 / 0.070);
  - exactly-one-sibling share 0.61-0.69 (rule >= 0.30).
- Every candidate fails the third: its false-inclusion (off) error is above E0's (0.098 / 0.087).
- Closest: E4-1 at 0.102 / 0.094 (+0.004 / +0.007) and E1-0.5 at 0.107 / 0.094 (+0.009 / +0.007).
- **All of the off error on single-queue cells sits on the 4-member leaves.** Every other size has 0.000 under every
  candidate except E2 / E3.
- On the T-BASE runs those off events are real short congestion that the strict-hot truth rule labels off (0b.4).
  The selection therefore turns on that truth rule (item 2 of STEP 0), not on false inclusion by the method.
  The rule was pre-set; it is applied as written, and changing it is the user's decision.

Data: the STEP 0 runs (263: v3 161, K1 G1-G3 and A4-A7 102), frozen v2-owd onsets. E0 and E4 use the frozen
SetsEngine events. Full tables: [tables.md](tables.md).

## Selection table (single-queue, r1 / r2, pooled over leaf sizes)

| candidate | on error | off error | exactly one sibling on | m | f | rho | result |
|---|---|---|---|---|---|---|---|
| E0 (frozen) | 0.085 / 0.070 | 0.098 / 0.087 | 0.612 / 0.616 | 0.123 / 0.098 | 0.086 / 0.082 | 0.55 / 0.56 | reference |
| E1-0.5 | 0.010 / 0.010 | 0.107 / 0.094 | 0.629 / 0.628 | 0.010 / 0.011 | 0.097 / 0.090 | 0.44 / 0.36 | fail (off) |
| E1-1 | 0.000 / 0.002 | 0.137 / 0.125 | 0.647 / 0.646 | 0.001 / 0.004 | 0.129 / 0.118 | 0.21 / 0.21 | fail (off) |
| E1-2 | 0.000 / 0.002 | 0.166 / 0.170 | 0.653 / 0.649 | 0.000 / 0.004 | 0.165 / 0.168 | 0.37 / 0.23 | fail (off) |
| E2 | 0.000 / 0.001 | 0.316 / 0.340 | 0.668 / 0.659 | 0.000 / 0.003 | 0.313 / 0.352 | 0.38 / 0.23 | fail (off) |
| E3 | 0.001 / 0.001 | 0.300 / 0.313 | 0.682 / 0.669 | 0.001 / 0.003 | 0.302 / 0.322 | 0.42 / 0.24 | fail (off) |
| E4-1 | 0.001 / 0.002 | 0.102 / 0.094 | 0.612 / 0.616 | 0.001 / 0.004 | 0.090 / 0.084 | 0.02 / -0.09 | fail (off) |
| E4-2 | 0.000 / 0.002 | 0.115 / 0.100 | 0.612 / 0.616 | 0.000 / 0.003 | 0.094 / 0.089 | - / -0.08 | fail (off) |

Where the off error comes from (single-queue, r1 / r2, by leaf size):

| leaf size | E0 | E1-0.5 | E4-1 |
|---|---|---|---|
| 4 | 0.158 / 0.149 | 0.169 / 0.153 | 0.164 / 0.161 |
| every other size (2, 3, 5, 8, 9, 12, 16, 24, 40) | 0.000-0.007 | 0.000-0.007 | 0.000-0.007 (one size-40 r1 cell 0.333 with 3 off events) |

On error by size (single-queue): E0 0.05-0.26; E1-0.5 0.000-0.013 (size 3 r2 0.094); E4-1 0.000-0.001 (size 3 r2
0.062). Size 3 has 53-66 events in r2 only: not reliable. So both fix the split events (STEP 0) at every leaf size.

## 0b.2 / 0b.3 / 0b.5: shape, cost of merging, latency (single-queue, pooled reps)

| candidate | events | members p50 / p90 | duration p50 / p90 / max s | absorbs E0 events p50 / p90 / max | mixed events | last join - t0 p50 / p90 s | member set final (close - t0) p50 / p90 s |
|---|---|---|---|---|---|---|---|
| E0 | 7542 | 4 / 9 | 1.31 / 1.32 / 11.2 | - | 0.030 | 0.03 / 0.09 | 1.31 / 1.32 |
| E1-0.5 | 6654 | 4 / 9 | 0.50 / 0.50 / 0.5 | 1 / 2 / 4 | 0.054 | 0.06 / 0.21 | 0.50 / 0.50 |
| E1-1 | 6357 | 4 / 10 | 1.0 | 1 / 2 / 5 | 0.075 | 0.06 / 0.27 | 1.00 |
| E1-2 | 6221 | 4 / 12 | 2.0 | 1 / 2 / 5 | 0.099 | 0.06 / 0.38 | 2.00 |
| E2 | 5613 | 4 / 16 | 7.4 / 14.2 / 48.8 | 1 / 2 / 9 | 0.164 | 0.07 / 2.03 | 7.4 / 14.2 |
| E3 | 5672 | 4 / 16 | 6.3 / 11.7 / 32.2 | 1 / 2 / 6 | 0.161 | 0.07 / 1.73 | 6.3 / 11.7 |
| E4-1, E4-2 | as E0 | as E0 | as E0 | - | 0.030 | 0.03 / 0.09 | 1.31 / 1.32 (+ W to know the NA) |

- Events per flow-minute: 2.68 for every candidate (the onsets are the same; only their grouping into events
  changes).
- Mixed events (members of two leaves with no common congested egress during the event): 3 % for E0, 5 % for
  E1-0.5, up to 16 % for E2 / E3. E2 and E3 last as long as the alarms (hold), absorb unrelated onsets and raise f
  to 0.30-0.35.
- E4's latency: the member set is final at the frozen close, but a member's NA status needs the neighbouring events
  within W, so it is known at t0 + W + 1.3 s.
- Latency the grouping would inherit, first onset to final member set: E1-0.5 0.5 s, E0 / E4 1.3 s, E1-1 1 s, E1-2
  2 s, E2 / E3 6-7 s (p50).
- The sibling separation stays at 0.61-0.69 for every candidate (rule >= 0.30); merging does not erase it.

fq_codel / cake (reported, not expected to fit): on error 0.12-0.31, off error 0.12-0.46, rho -0.13 to -0.39 under
every candidate (tables.md).

## 0b.4 The T-BASE "truth off, all four members have an onset" events

66 E0 events on 4-member leaves. All 66:
- GT1 strict cover p50 0.25 (strict-hot needs >= 0.5 of [t0 - 1, t0 + 2]). A GT1 episode within [t0 - 0.5,
  t0 + 1.5] in 98 %.
- A GT-Q episode for the members in 100 %; harmful at 600 ms in 42 %.
- A GT3 episode for at least one member in 86 %.
- Frozen F1 (queue delay) max p50 53 ms.
- The onset lies 0-200 ms after a keyframe in only 24 %.

So these are real congestion episodes of 0.3-1.4 s, shorter than half the strict-hot span, mostly not keyframe-driven
and often harmful. In the sample of 20 most come from M9 (sstress: short stress bursts), then the PIE C2 runs, C6 (join) and the M3 / G1
background variants. Sample of 20 (seed 1) in [tables.md](tables.md), e.g.:

| run | t0 | GT1 strict cover | GT1 episode | GT-Q (max sojourn ms, harmful) | F1 max ms | phase after keyframe s |
|---|---|---|---|---|---|---|
| C2-sburst-s030u070-pie-r2 | 154.03 | 0.41 | 154.02-155.25 | 175.5, 4 | 172-175 | 0.04 |
| M9-sstress-s030u070-codel-r1 | 203.34 | 0.30 | 203.30-204.20 | 183.3, 3 | 183 | 0.35 |
| M9-sstress-s030u070-pfifo-r2 | 196.37 | 0.19 | 196.34-196.92 | 41.5, 3 | 41.5 | 0.38-0.42 |
| C6-sjoin-s030u070-pfifo-r1 | 127.99 | 0.42 | 128.02-128.59 | 41.9, 0 | 40-42 | 0.01-0.07 |

## Definitions and choices (FLAG where the note left a choice)

- Aligned onset time t_al = t_onset - mrtt / 2, as the frozen Config (align_mode "half_mrtt"). Episodes are shifted the
  same way.
- E1: t0 = the first onset of the event; later onsets with t_al in [t0, t0 + W] join; the event closes at t0 + W.
- E2 / E3 close (FLAG): E2 when every member is out of alarm (last episode end), E3 when at most half are. No cap;
  the durations above (max 48.8 s) show what a cap would bound.
- A flow joins an event at most once; a second onset of a member opens a new event (FLAG; rare).
- Offline order by t_al; the frozen engine is causal on arrival. The latency column uses close times, so the order
  does not change it.
- NA rules as STEP 0, with "split" added for E4. In alarm at the opening: E0 / E4 episode before t0 - 0.15 s, E1-E3
  before t0.
- Truth "on" (strict-hot over t0 + NEG_SPAN) as STEP 0. "Mixed" uses any GT1 episode overlapping [t0, close] on an
  egress that contains both leaves.
- Rule details: pooled over leaf sizes; "both reps" = r1 and r2 (K1 r3-r5 not used for selection); E4-W with the
  same off-error test as the others.

## Method

- [npr0b.py](npr0b.py) builds the eight candidates' events per run plus the 0b.4 probe; tables by
  [npr0b_report.py](npr0b_report.py), reusing STEP 0's per-leaf code.
- First batch 18:04-18:19. 30 runs failed on E0 events with only sub-ctrl as member (`max()` of an empty set); they
  were fixed (such events are skipped) and recomputed from scratch 18:19-18:21. Final rows: 263, 0 errors.
- Nice 19, 2 workers; K1 tick files from STEP 0's cache. Nothing written inside run folders.
