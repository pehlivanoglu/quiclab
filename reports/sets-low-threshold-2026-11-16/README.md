# R1: grouping on lower detector on-thresholds (2026-11-16)

Replay on the existing v3 runs (`.runs/2026-11-14_1818_v3`): 42 grouping runs (34 single-queue, 8 fq_codel) and
42 calm runs (C1a, C1b). No emulation; nothing frozen changed (detector, frozen SETS, adapter, scorer). Every
value is rep 1 / rep 2. Full tables: [tables.md](tables.md). Code: [r1.py](r1.py) (replay), [r1_report.py](r1_report.py)
(tables, timelines). The project document `claude/replay-studies-spec.md` is not on this machine. The brief
given in chat is used as R1; section 0 of that document was not read.

**Check:** V0 reproduces the frozen numbers exactly (pair P 0.99 / 0.97, leaf F1 0.83 / 0.84, spurious 0.79 / 0.71,
run-clock p50 102 / 84 s; same onset count as the frozen onset log).

## Headline

### 1. Pre-set condition: pair precision ≥ 0.93 in both reps, k = 2 and k = 3 (single-queue cells)

| variant | pair P k2 | pair P k3 | result |
|---|---|---|---|
| V0 frozen (T100) | 0.993 / 0.970 | 0.978 / 0.955 | **PASS** |
| V1 T75 | 0.990 / 0.965 | 0.976 / 0.953 | **PASS** |
| V1 T50 | 0.821 / 0.927 | 0.827 / 0.930 | **FAIL** |
| V1 T25 | 0.713 / 0.706 | 0.715 / 0.706 | **FAIL** |
| V2 T75 | 0.990 / 0.965 | 0.976 / 0.953 | **PASS** (identical to V1 T75) |
| V2 T50 | 0.868 / 0.940 | 0.864 / 0.945 | **FAIL** |
| V2 T25 | 0.713 / 0.699 | 0.712 / 0.707 | **FAIL** |

At T50, rep 2 sits just above or just below 0.93 while rep 1 is far below. That is a fail either way. No cause
was looked for, so the size of the gap is "not reliable".

### 2. Seconds to the first correct leaf group (F1 ≥ 0.9), single-queue cells, k = 2

**Correction to the frozen report's reading.** The "seconds" the frozen scorer reports (102 / 84) are the
close's time on the run clock, not the time since congestion began. The new column measures from the start of
the first stimulus window that targets that leaf.

| variant | events p50 / p90 | run clock s p50 / p90 | since first stimulus s p50 / p90 |
|---|---|---|---|
| V0 frozen | 3 / 3, 6 / 8 | 102 / 84, 287 / 201 | **68 / 50, 224 / 139** |
| V1 = V2 T75 | 3 / 3, 6 / 7 | 84 / 84, 287 / 201 | 67 / 49, 256 / 139 |
| V1 = V2 T50 (fails 1) | 4 / 3, 8 / 7 | 83 / 82, 272 / 160 | 43 / 47, 208 / 98 |
| V1 T25 (fails 1) | 4 / 3, 14 / 15 | 44 / 73, 139 / 186 | 24 / 41, 124 / 136 |

The k = 3 rows are in tables.md §2. The only variant that passes (T75) is not faster than frozen: since first
stimulus, p50 is 67 / 49 against 68 / 50. T50 is faster in rep 1 (43 against 68 s) but fails the pair-precision
condition.

### 3. Calm runs: what lower thresholds produce without congestion

| level | events / flow-minute | k2 groups, single-leaf base | split4 (2 runs) | tree16 (2 runs) | uneven, no shared shaped link (2 runs) |
|---|---|---|---|---|---|
| T100 | 0.13 | 8 leaf | none | none | none |
| T75 | 0.36 | 15 leaf | none | none | none |
| T50 | 1.93 | 40 leaf | 4 leaf + 5 upstream | 1 leaf + 29 upstream | 6 leaf + **12 coincidence** |
| T25 | 6.69 | 49 leaf | 3 + 10 | 5 + 101 | 18 + **72 coincidence** |

On T-BASE every group is "leaf" trivially, because all four clients share the one queue. In those runs the
groups are physically right: the shared queue is the synchronized keyframe queue. On T-UNEVEN the up link is
unshaped, so "coincidence" groups are false.

V2 reports none of the multi-leaf calm groups: there is no strong observation there. Its base-topology groups
fall to 23 (T50) and 15 (T25).

So grouping without congestion "works" only in the sense that keyframes synchronize every client's queue
pulse. The groups follow the keyframe queue, not a congestion: correct on one queue, upstream sets on
trees, false sets where clients share no queue.

## Where the extra events come from (stimulus runs)

| level | events / flow-minute | in a stimulus window | phase < 200 ms after a GOP boundary: in windows / outside | weak (V2) | sets: leaf / upstream / coincidence |
|---|---|---|---|---|---|
| T100 | 0.57 | 0.99 | 0.27 / 0.50 | 0.01 | 0.68 / 0.25 / 0.08 |
| T75 | 0.64 | 0.96 | 0.29 / 0.69 | 0.12 | 0.66 / 0.25 / 0.09 |
| T50 | 1.09 | 0.74 | 0.41 / **0.86** | 0.49 | 0.58 / 0.31 / 0.11 |
| T25 | 2.94 | 0.52 | 0.60 / **0.88** | 0.80 | 0.41 / 0.43 / 0.16 |

A uniform phase would give 0.20.

- Outside the stimulus windows, 86-88 % of the T50 / T25 events start within 200 ms after a GOP boundary; in the
  calm runs, 79-81 % at every level.
- Inside the windows the share rises from 0.27 (T100) to 0.41 (T50). Of the ~1180 events T50 adds inside windows,
  about 72 % are GOP-aligned (estimate from the two shares).
- **Reading:** below T75 the added events are mostly keyframe pulses. Every keyframe briefly lifts every client's
  score (timeline-keyframe.png).
- The brief's keyframe rule (members' onsets within one tick of the boundary) undercounts: 0.05-0.06. The score
  peaks come 50-150 ms after the boundary, which is why the 200 ms phase rule (T) is reported next to it.

## Missed members, by cause (clients behind a congested leaf egress not in the event)

| level | missed | split event | already in alarm | other |
|---|---|---|---|---|
| T100 | 4801 | 0.15 | 0.48 | 0.37 |
| T75 | 5337 | 0.12 | 0.53 | 0.35 |
| T50 | 7504 | 0.10 | 0.62 | 0.29 |
| T25 | 14595 | 0.06 | 0.77 | 0.17 |

Lower thresholds make episodes longer: off is half of on, so a client is already in alarm more often when a
new event starts. "Already in alarm" grows from 48 % to 77 % of the misses.

## Other results (tables.md)

- **Common scorer, single-queue cells (§5):**
  - Leaf F1 hardly moves (0.79-0.85 at every level).
  - Spurious groups per close grow: k2 0.79 / 0.71 at T100, 2.04 / 2.01 at T50 (V2 1.15 / 1.60), 7.4 / 10.1 at T25.
  - Pair recall falls: 0.91 / 0.92 at T100, 0.51 / 0.55 at T50.
- **fq_codel, same-link truth (§7):** pair P falls further, from 0.26 / 0.34 at T100 to 0.16 / 0.19 at T50 and 0.09 / 0.11 at T25.
- **Late joiner (§8):** joined 67 / 69 at T100, 62 at T50, 53 at T25.
- **Distinct sets in the table at the end of a run (§9):** 9.8 at T100, 22 at T50, 98 at T25 (single-queue).

## Definitions and choices (constants tagged in the code)

- **Levels (P):** on 0.25 / 0.1875 / 0.125 / 0.0625, off = on / 2. The span rule (shadow_v2_step5.on_spans) is
  frozen; only `THETA_ON` is set for the call. The onset log is built by the frozen adapter (source `v2-owd`).
- **V2 (T):**
  - An event is strong if one of its members' episodes at this level contains a T100 alarm start of the same flow.
  - A group is reported if a strong observation counts toward it under the frozen matching rule.
  - At T75, 88 % of events are strong, so V2 = V1 there.
- **Event classes:**
  - "in window": t0 within [start − 1 s, end + 2 s] of a truth stimulus window.
  - Sets against the topology (shaped egresses):
    - leaf: inside one leaf;
    - upstream: inside a shared non-leaf egress that is congested at t0 (GT1, strict rule), or any such egress in calm runs;
    - coincidence: otherwise.
- **Missed-member causes:**
  - "already in alarm": the client's episode at this level started before t0 and is on at t0;
  - "split event": an onset of the client within ±0.3 s (delta_max) of t0;
  - other: neither.
- **Timeline examples:**
  - [timeline-keyframe.png](timeline-keyframe.png): C10 codel r2, T50 event at 13.02 s, GOP-aligned, outside windows.
  - [timeline-coincidence.png](timeline-coincidence.png): C11 codel r1, 245.02 s. Three clients from different
    leaves on a keyframe pulse; no shared shaped link.
  - [timeline-helpful-weak.png](timeline-helpful-weak.png): C8 pfifo r2, 287.45 s. **Not a helpful example.**
    It is the decaying tail of an earlier alarm, counted "in window" by the +2 s margin. No weak event was found
    that arrives before the T100 alarm, off the GOP phase, and leads to an earlier correct group; T50 has 28 weak
    two-member leaf events that are in a window and off the GOP phase, in all 34 single-queue runs.

## Verdict against the three questions

1. **Condition:** only T75 passes, for both V1 and V2. T50 and T25 fail in both variants.
2. **Time:** T75 gives no shortening (68 / 50 → 67 / 49 s since first stimulus). The shortenings at T50 / T25 come
   with failed pair precision.
3. **Source of the extra events:** below T75, mostly keyframe pulses (86-88 % GOP-aligned outside windows). V2 removes
   the false calm groups but does not save T50's pair precision (0.87 / 0.94).
