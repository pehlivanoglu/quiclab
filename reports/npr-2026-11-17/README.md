# NPR STEP 1-3: noisy partition refinement (2026-11-17)

**Answer.**
- On both event formations NPR (V-bin, alpha 0.05) meets the pre-set grouping conditions on single-queue cells and
  beats frozen SETS clearly.
  - PRIMARY, E3 (rule-selected): pair P 0.979 / 0.965, leaf F1 0.968 / 0.958, against frozen SETS k = 2 on frozen
    events 0.858 / 0.863.
  - SECOND, E1-0.5: pair P 0.988 / 0.989, leaf F1 0.965 / 0.965.
- The calibration condition (STEP 2: false splits of single-leaf groups at most alpha) decides between them:
  - **E3 passes at alpha 0.05 and 0.1 and fails at 0.01.** Single-leaf runs 0.041 at 0.05 (20 orders: mean 0.059,
    0.020-0.082); every leaf alone 0.023 (0.026-0.059).
  - **E1-0.5 fails at every alpha** (0.062-0.082 at 0.05).
- V-bb fails pair precision on E3 (0.870 / 0.911); V-na0 passes and is the same as V-bin within 0.01.
- Speed: E1-0.5 groups much faster in seconds (first correct group p90 12-17 s from the leaf's first stimulus,
  against 70-113 s for NPR on E3 and 98-124 s for frozen SETS k = 2). In events, NPR needs 1 at p50 on both.
- fq_codel / cake: as expected, no fit (pair P 0.23-0.31, calibration 0.29-0.37 split).
- Scale (STEP 3, synthetic): NPR-bin holds leaf F1 0.81-0.98 at 100 and 1000 clients at the measured false-inclusion
  level, where SETS k = 2 collapses (0.12-0.45 at 1000 clients); reads take 0.1-0.5 s (p50). V-bb never splits.

All on the 263 STEP 0 runs: v3 and K1 G1-G3 / A4-A7; single-queue tables pool 89 / 88 runs per rep (calm runs and
fq / cake apart). Frozen detector, frozen onsets, frozen SETS code; replay only.

## Pre-set conditions (single-queue, r1 / r2)

| formation | method | pair P (>= 0.93) | leaf F1 (>= frozen SETS k2 0.858 / 0.863) | STEP 2 false splits at alpha (single-leaf runs / every leaf alone) | all three |
|---|---|---|---|---|---|
| E3 | NPR-bin a0.05 | 0.979 / 0.965 | 0.968 / 0.958 | 0.041 / 0.023 (<= 0.05) | **pass** |
| E3 | NPR-bin a0.01 | 0.979 / 0.964 | 0.968 / 0.957 | 0.027 / 0.016 (> 0.01) | fail (calibration) |
| E3 | NPR-bin a0.1 | 0.980 / 0.966 | 0.968 / 0.958 | 0.068 / 0.059 (<= 0.1) | **pass** |
| E3 | NPR-na0 a0.05 | 0.979 / 0.978 | 0.968 / 0.964 | (V-bin only) | pass on 1-2 |
| E3 | NPR-bb a0.05 | 0.870 / 0.911 | 0.951 / 0.948 | (V-bin only) | fail (pair P) |
| E1-0.5 | NPR-bin a0.05 | 0.988 / 0.989 | 0.965 / 0.965 | 0.082 / 0.062 (> 0.05) | fail (calibration) |
| E1-0.5 | NPR-bin a0.01 | | | 0.061 / 0.046 | fail |
| E1-0.5 | NPR-bin a0.1 | | | 0.129 / 0.124 | fail |
| E1-0.5 | NPR-bb a0.05 | 0.932 / 0.938 | 0.957 / 0.954 | | pass on 1-2 |

Calibration was run for V-bin only (FLAG: the note asks per alpha, not per variant). The 20 random event orders give
a spread of about +-0.03 around the original order, so E3 at alpha 0.05 is close to the limit (order mean 0.059 on
single-leaf runs): **not reliable as a margin**, though it passes as specified (original order).

## STEP 1 scores (single-queue cells, r1 / r2)

| formation | method | leaf P | leaf R | leaf F1 | pair P | pair R | spurious / close | first correct group: events p50 / p90; s from first stimulus p50 / p90 | leaves never |
|---|---|---|---|---|---|---|---|---|---|
| frozen E0 | SETS k1 | 0.969 / 0.949 | 0.948 / 0.937 | 0.955 / 0.939 | 0.985 / 0.966 | 0.563 / 0.680 | 1.02 / 0.98 | 1 / 3, 1 / 46 ; 1 / 4, 1 / 58 | 3 / 5 |
| frozen E0 | SETS k2 | 0.863 / 0.869 | 0.855 / 0.861 | 0.858 / 0.863 | 0.996 / 0.977 | 0.903 / 0.923 | 0.58 / 0.56 | 2 / 6, 32 / 124 ; 2 / 7, 32 / 98 | 3 / 5 |
| frozen E0 | SETS k3 | 0.811 / 0.812 | 0.807 / 0.812 | 0.807 / 0.808 | 0.988 / 0.971 | 0.961 / 0.956 | 0.41 / 0.38 | 4 / 7, 50 / 182 ; 4 / 8, 48 / 211 | 4 / 5 |
| E3 | SETS k1 | 0.966 / 0.944 | 0.963 / 0.955 | 0.961 / 0.945 | 0.978 / 0.974 | 0.982 / 0.963 | 0.39 / 0.42 | 1 / 2, 11 / 126 ; 1 / 4, 7 / 121 | 3 / 3 |
| E3 | SETS k2 | 0.874 / 0.875 | 0.882 / 0.893 | 0.875 / 0.879 | 0.964 / 0.964 | 0.990 / 0.974 | 0.32 / 0.35 | 2 / 5, 36 / 162 ; 2 / 6, 27 / 170 | 3 / 3 |
| E3 | SETS k3 | 0.808 / 0.808 | 0.827 / 0.838 | 0.813 / 0.816 | 0.943 / 0.934 | 0.989 / 0.978 | 0.24 / 0.27 | 3 / 7, 61 / 218 ; 3 / 8, 56 / 302 | 3 / 3 |
| E3 | **NPR-bin a0.05** | 0.973 / 0.957 | 0.968 / 0.968 | **0.968 / 0.958** | **0.979 / 0.965** | 0.999 / 0.998 | 0.17 / 0.12 | 1 / 2, 11 / 70 ; 1 / 3, 7 / 113 | 2 / 2 |
| E3 | NPR-na0 a0.05 | 0.972 / 0.965 | 0.968 / 0.968 | 0.968 / 0.964 | 0.979 / 0.978 | 0.996 / 0.997 | 0.18 / 0.13 | 1 / 2, 11 / 70 ; 1 / 2, 7 / 38 | 2 / 2 |
| E3 | NPR-bb a0.05 | 0.951 / 0.943 | 0.968 / 0.968 | 0.951 / 0.948 | 0.870 / 0.911 | 0.993 / 0.999 | 0.13 / 0.11 | 1 / 4, 11 / 93 ; 1 / 4, 7 / 131 | 2 / 2 |
| E1-0.5 | SETS k1 | 0.972 / 0.953 | 0.956 / 0.951 | 0.961 / 0.950 | 0.991 / 0.984 | 0.926 / 0.913 | 0.52 / 0.56 | 1 / 2, 1 / 33 ; 1 / 3, 1 / 46 | 3 / 5 |
| E1-0.5 | SETS k2 | 0.874 / 0.890 | 0.872 / 0.886 | 0.872 / 0.886 | 0.990 / 0.993 | 0.955 / 0.938 | 0.37 / 0.41 | 2 / 4, 25 / 107 ; 2 / 4, 20 / 85 | 3 / 5 |
| E1-0.5 | SETS k3 | 0.815 / 0.825 | 0.816 / 0.829 | 0.814 / 0.825 | 0.980 / 0.971 | 0.961 / 0.946 | 0.28 / 0.30 | 3 / 6, 47 / 171 ; 3 / 7, 42 / 210 | 3 / 5 |
| E1-0.5 | **NPR-bin a0.05** | 0.971 / 0.968 | 0.963 / 0.965 | **0.965 / 0.965** | **0.988 / 0.989** | 0.997 / 0.991 | 0.16 / 0.17 | 1 / 1, 1 / 12 ; 1 / 1, 1 / 17 | 2 / 2 |
| E1-0.5 | NPR-na0 a0.05 | 0.973 / 0.968 | 0.964 / 0.966 | 0.967 / 0.965 | 0.988 / 0.989 | 0.991 / 0.975 | 0.22 / 0.24 | 1 / 1, 1 / 12 ; 1 / 1, 1 / 17 | 2 / 3 |

Gain from the events against gain from the grouping rule (leaf F1, r1 / r2):
- events only (SETS k2: frozen E0 -> E3 / E1-0.5): 0.858 / 0.863 -> 0.875 / 0.879 and 0.872 / 0.886 (+0.01 to
  +0.02);
- grouping rule only (same events, SETS k2 -> NPR): E3 0.875 -> 0.968 and E1-0.5 0.872 -> 0.965 (+0.07 to +0.09).
- **Most of the gain is the grouping rule.** The new events matter for pair recall (SETS k2 0.90 -> 0.96-0.99) and
  for time to group (E1-0.5).
- Alpha changes almost nothing in STEP 1 (+-0.001); its effect is in the calibration.

### By leaf size, AQM and block (single-queue, pooled reps; leaf F1 / pair P)

| largest leaf | runs | frozen SETS k2 | E3 SETS k2 | E3 NPR-bin | E1-0.5 SETS k2 | E1-0.5 NPR-bin |
|---|---|---|---|---|---|---|
| 4 | 168 | 0.86 / 0.98 | 0.87 / 0.93 | 0.96 / 0.93 | 0.87 / 0.97 | 0.96 / 0.97 |
| 8 | 9 | 0.87 / 0.96 | 0.93 / 0.97 | 0.99 / 0.98 | 0.92 / 0.97 | 0.99 / 0.98 |
| 9 | 14 | 0.92 / 1.00 | 0.86 / 0.87 | 0.96 / 0.94 | 0.93 / 1.00 | 0.95 / 0.98 |
| 12 | 3 | 0.81 / 0.87 | 0.89 / 0.96 | 0.96 / 0.94 | 0.89 / 0.96 | 0.96 / 0.94 |
| 16 | 12 | 0.83 / 1.00 | 0.94 / 1.00 | 1.00 / 1.00 | 0.94 / 1.00 | 1.00 / 1.00 |
| 24 | 6 | 0.86 / 1.00 | 0.94 / 1.00 | 0.99 / 1.00 | 0.92 / 1.00 | 0.99 / 1.00 |
| 40 | 6 | 0.88 / 1.00 | 0.94 / 1.00 | 0.99 / 1.00 | 0.93 / 1.00 | 0.99 / 1.00 |

- By AQM, NPR-bin leaf F1 is 0.96-1.00 on pfifo, codel, pie and red under both formations.
- Blocks where E3's merging costs pair precision (independent leaves congested close together):
  - C10 hindep: E3 0.71 against E1-0.5 0.96;
  - A5 hindep: 0.84 against 0.94;
  - mixab M8: 0.86 against 0.88.
- The biggest gains over frozen SETS are where SETS was weakest:
  - C6 join: 0.49 -> 0.90-0.93;
  - C12 / A7 access: 0.68-0.71 -> 0.93-0.95;
  - C13: 0.68 -> 0.92.
- Full tables: [tables-E3.md](tables-E3.md), [tables-E1-0.5.md](tables-E1-0.5.md).

### Long events (single-queue)

| formation | events | longer than 5 s | true leaves per long event p50 / p90 / max | long events with >= 2 true leaves |
|---|---|---|---|---|
| E3 | 2124 / 2126 | 0.654 / 0.666 | 1 / 2 / 4 | 0.293 / 0.302 |
| E1-0.5 | 2421 / 2434 | 0 | - | - |

Two thirds of E3's events last longer than 5 s, and 30 % of those contain onsets from two or more true leaves.

## STEP 2 calibration (V-bin; share of single-leaf groups split at any read)

| formation | set | alpha 0.05: original (20 orders mean, min-max) | 0.01 | 0.1 |
|---|---|---|---|---|
| E3 | single-leaf runs (147) | 0.041 (0.059, 0.020-0.082) | 0.027 (0.040) | 0.068 (0.074) |
| E3 | every leaf alone (307) | 0.023 (0.040, 0.026-0.059) | 0.016 (0.029) | 0.059 (0.055) |
| E1-0.5 | single-leaf runs | 0.082 (0.078, 0.054-0.109) | 0.061 | 0.129 |
| E1-0.5 | every leaf alone | 0.062 (0.068, 0.049-0.085) | 0.046 | 0.124 |
| both | fq_codel / cake leaves (41) | 0.32-0.37 | 0.29-0.37 | 0.32-0.37 |

Read time per read (all reads, single process): p50 0.02 s, p90 0.04-0.05 s. The maxima in the raw table (up to
1085 s) are the batch's pause during the campaign's PIE run (SIGSTOP), not compute.

## STEP 3 (scale): synthetic, 100 and 1000 clients

Model ([step3.py](step3.py)):
- Flat leaves under one root: 100 clients as leaves 10 / 20 / 30 / 40; 1000 clients as 10 / 50 / 100 / 340 / 500.
- 120 events. Each leaf is on with probability 0.25; with probability 0.1 the root is on (every leaf).
- Bursty misses: the per-event hit probability is Beta-distributed with mean 1 - m and correlation rho.
- False inclusion f; NA with probability NA.
- m, rho, NA as measured on each formation: E3 m 0.002, rho 0.33, NA 0.021; E1-0.5 m 0.011, rho 0.40, NA 0.111.
- f = 0.001 (the measured gtq false-inclusion level) and 0.05 (stress; FLAG).
- Reads every 5 events (FLAG: cost), seeds 1 / 2.

Leaf F1 / pair P (seed 1 / seed 2); read time p50 / max in s:

| model | clients | SETS k2 | NPR-bin a0.05 | NPR-bb a0.05 | NPR read time | SETS read time |
|---|---|---|---|---|---|---|
| E3, f 0.001 | 100 | 0.93 / 0.91; 1.00 / 1.00 | **0.98 / 0.98; 0.99 / 0.98** | 0.40 / 0.55; 0.30 / 0.37 | 0.11 / 0.52 | 0.003 / 0.02 |
| E3, f 0.001 | 1000 | 0.44 / 0.45; 0.99 / 1.00 | **0.89 / 0.81; 0.99 / 0.98** | 0.37 / 0.30; 0.47 / 0.39 | 0.23 / 1.13 | 0.007 / 0.04 |
| E3, f 0.05 | 100 | 0.81 / 0.40; 0.70 / 0.71 | 0.91 / 0.80; 0.81 / 0.57 | 0.39 / 0.40 | 0.12 / 0.26 | 0.003 / 0.04 |
| E3, f 0.05 | 1000 | no group (0) | 0.82 / 0.77; 0.98 / 0.94 | 0.29 / 0.29 | 0.34 / 0.84 | 0.005 / 0.02 |
| E1-0.5, f 0.001 | 100 | 0.51 / 0.69; 1.00 / 1.00 | **0.98 / 0.93; 1.00 / 0.98** | 0.64 / 0.40 | 0.14 / 1.19 | 0.002 / 0.04 |
| E1-0.5, f 0.001 | 1000 | 0.12 / 0.18; 0.96 / 0.99 | **0.86 / 0.90; 0.96 / 0.97** | 0.30 / 0.29 | 0.47 / 1.45 | 0.009 / 0.04 |
| E1-0.5, f 0.05 | 100 | no group (0) | 0.93 / 0.93; 0.89 / 0.96 | 0.41 / 0.40 | 0.17 / 0.38 | 0.001 / 0.004 |
| E1-0.5, f 0.05 | 1000 | no group (0) | 0.64 / 0.76; 0.83 / 0.94 | 0.29 / 0.29 | 0.38 / 0.62 | 0.005 / 0.02 |

- **NPR-bin keeps leaf F1 0.81-0.98 with pair P >= 0.94 at the measured false-inclusion level (f 0.001), up to 1000
  clients and leaves of 500.**
  - Under the stress f = 0.05 it degrades (F1 0.64-0.93, pair P 0.57-0.96) but still groups.
  - First correct group within 0-2 reads at p50 (0-10 events).
  - Read time p50 0.1-0.5 s, max 1.4 s at 1000 clients (one Python process).
- **SETS (exact set table) collapses with large leaves.**
  - At 1000 clients, k = 2 gives leaf F1 0.12-0.45, and no group at all under f = 0.05.
  - At 100 clients, E1-0.5's misses (m 0.011, NA 0.11) already cut it to 0.51-0.69.
  - SETS reads are ~50x faster (0.002-0.009 s).
- **V-bb does not split at all** (pair P 0.29-0.47, pair R ~1) in every setting. It also fails pair precision on
  E3's real data. With rho 0.33-0.40 the beta-binomial one-leaf model explains split events cheaply, so the test
  has no power. V-bb is not usable as specified.
- K1 G1-G3 by group size (real runs): see "By leaf size" above. NPR-bin leaf F1 0.99-1.00 at 16 / 24 / 40 members
  on both formations, against frozen SETS k2 0.83-0.88.
- SETS k1 also stays high in the synthetic (0.72-0.99) because the root group (all clients) is a true set there.

## Choices made (FLAG)

1. **m, f per read from the candidate tree.** m and f are pooled over the >= 3-member groups of the candidate tree,
   i.e. the recursive split proposals without any test.
   - Estimating them on the unsplit group mixes the leaves and inflates m and f. On a synthetic two-leaf case that
     gave m 0.38 and the root's E value fell from 3e57 to 2e-31, which removes the test's power.
   - m and f are clipped to [0.001, 0.45].
2. **Predictable plug-in.** Each event's two-leaf factor uses the split, pi_s (+0.5 per state) and m, f of the read
   before that event. Every factor depends only on earlier events, so it is computed once. Without a fittable
   split, the factor is the prefix's one-leaf fit (about 1).
3. **e-BH per recursion level** of one read, at level alpha.
4. **Tie rule and NA members:** the half whose smallest client index is smaller wins a tie; the NA members of e*
   start in g2.
5. **Reported groups:** every tree node with >= 2 members, the root included (the k = 1 counterpart).
6. **V-bb rho** = the mean of the two reps' STEP 0b rho: E3 0.33, E1-0.5 0.40.
7. **Calibration:** V-bin only. Leaves taken alone use the formation's events where one of their members has 1.
8. **Late joiner:** not computed (FLAG). The common scorer's late-joiner test needs a hidden-onset replay that NPR's
   matrix input does not have yet.

Code: [npr.py](npr.py) (method), [step12.py](step12.py) / [step12_report.py](step12_report.py),
[step3.py](step3.py). Batches through ../batch_guard.py (nice 19, 2 cores, paused during weak-spot runs).

## D1. False splits of the first test (STEP 2, original event order): they follow late responders

**Not random: the two halves of a false split are ordered by the members' access delay far more often than chance,
and in E1-0.5 a third of the evidence events had members whose onset fell into the next event.**

54 false splits at alpha 0.05 (detail per split in [d1-false-splits.json](d1-false-splits.json): leaf, halves by client
with access delay and bitrate, evidence events, members cut by the window):

| formation | false splits (single-leaf runs / leaves alone) | AQM | also at alpha 0.01 | halves ordered by access delay (random expectation) | halves ordered by bitrate (random) | evidence events with >= 1 zero-member whose onset falls in the next event within 1 s / with all |
|---|---|---|---|---|---|---|
| E1-0.5 | 34 (22 / 12) | fq_codel 15, pfifo 13, codel 5, pie 1 | 29 | 25 / 34 (16.1) | 30 / 34 (24.2) | 0.36 / 0.27 |
| E3 | 20 (14 / 6) | fq_codel 13, pfifo 6, codel 1 | 17 | 15 / 20 (11.3) | 19 / 20 (16.3) | 0.13 / 0.10 |

- Ordered = every client of one half has an access delay >= every client of the other. The random expectation
  shuffles the same halves over the leaf's members.
- Bitrate ordering is only a little above chance (many leaves have two rates).
- Almost half of the false splits are fq_codel leaves, where no fit was expected. On single-queue cells: E1-0.5 19,
  E3 7.
- Most splits are strong: also accepted at alpha 0.01 (29 of 34 and 17 of 20), so this is not a near-threshold
  effect.
- Leaves of 3 and 4 dominate (29 of 34, 19 of 20).
- Mechanism: in the window formation a late responder's onset lands in the next event; it shows as a 0 in one event
  and a lone 1 in the next. With the first test's pooled m, f taken from the candidate tree, that pattern looked like
  a second leaf. The corrected test (B) should be checked on exactly these cases (part of C).

## D3. Onset spread within one leaf in one stimulus: W as a quantile

Spread = max - min of the members' first onsets (aligned t_onset - mrtt / 2, as the event formation uses) within one
stimulus window, per true leaf the window congests (members with an onset >= 2). 263 runs; full table
[d3-tables.md](d3-tables.md).

| cells | leaf-stimuli | spread p50 / p90 / p95 / p99 ms | share <= 0.5 s / 1 s / 2 s |
|---|---|---|---|
| single-queue r1 / r2 | 2656 / 2679 | 58 / 195 / 290 / 676 ; 58 / 180 / 269 / 719 | 0.983 / 0.994 / 0.997 ; 0.981 / 0.993 / 0.997 |
| by leaf size 2 / 4 / 9 / 16 / 40 | 412 / 5517 / 368 / 216 / 108 | p90 101 / 158 / 198 / 299 / 436; p99 457 / 619 / 488 / 571 / 653 | 0.99 / 0.985 / 0.99 / 0.98 / 0.95 at 0.5 s |
| by RTT spread 0-10 / 10-30 / > 30 ms | 370 / 6889 / 180 | p90 68 / 180 / 328 | 1.00 / 0.98 / 0.98 |
| by intensity u 1.05 / 1.15 / 1.3 | 1772 / 2797 / 2734 | p90 294 / 153 / 124; p99 1017 / 483 / 437 | 0.96 / 0.99 / 0.99 |
| AQM pfifo / codel / pie | 3781 / 2708 / 734 | p90 185 / 189 / 119 | 0.985 / 0.985 / 0.985 |
| fq_codel / cake r1 / r2 | 298 / 225 | p90 2091 / 1812 | 0.68 / 0.67 |

Detector delay (v2-owd GT3 true-positive latency, R2, single-queue): p50 226, p90 465, p99 3260 ms; p90 - p10
320 ms.

**Answer: yes.**
- W = 0.5 s is about the 98th percentile of the measured within-leaf onset spread on single-queue cells (98.1-98.3 %
  of leaf-stimuli fit in it), in both reps.
- The spread is also of the order of the detector's own delay spread (p90 - p10 = 320 ms).
- A rule "W = the p98 of the measured spread" gives 0.5 s here. p95 would give 0.27-0.29 s, p99 0.68-0.72 s.
- The spread grows with leaf size (p90 0.1 s at 2 members, 0.44 s at 40), with the RTT spread and at low
  intensity (u 1.05: p99 1.0 s). So W stated as a quantile holds for the mix of this suite. A deployment with
  larger leaves or wider RTT spread would measure a larger W by the same rule.
- Leaf size 3 (42 leaf-stimuli, G2) is an outlier (p90 985 ms): not reliable.
- D3 needed the per-member onset times, so the onset logs were rebuilt from the frozen tick files (one core, ~20 min;
  nothing written in run folders). Not a new detector run.

## Diagnosis of the corrected test's loss of power (E1-0.5, single-queue; user, 2026-11-18)

Inputs: rows-v2-E1-0.5.jsonl (263 runs, complete) and the first test's rows; two short targeted replays on the runs
with >= 2 true leaves ([diag.md](diag.md), [diag2.md](diag2.md), per-event detail in
[diag-merged-pairs.json](diag-merged-pairs.json) and [diag2-first-splits.json](diag2-first-splits.json)). The test was
not changed.

**4. Both ends of the trade-off (alpha 0.05; r1 / r2):**

| test | false-split share (single-leaf runs / every leaf alone) | pair P | leaf F1 | pair R |
|---|---|---|---|---|
| first test | 0.082 / 0.062 | 0.988 / 0.989 | 0.965 / 0.965 | 0.997 / 0.991 |
| corrected test | **0.007 / 0.007** | **0.930 / 0.871** | 0.952 / 0.934 | 0.993 / 0.996 |

alpha 0.01 and 0.1 give the same corrected numbers within 0.01; false splits are 0.007 at every alpha.

**1. By the number of true leaves (pair P, corrected / first test):**

| runs | n | leaf F1 corrected | pair P corrected | pair P first test |
|---|---|---|---|---|
| 1 leaf | 149 | 0.967 / 0.960 | 1.000 / 1.000 | 1.000 / 1.000 |
| 2 leaves (49 with a stimulated shared upstream) | 51 | 0.930 / 0.856 | **0.820 / 0.675** | 0.946 / 0.970 |
| 3 leaves (none with a stimulated shared upstream) | 14 | 0.887 / 0.921 | 0.950 / 0.831 | 1.000 / 0.975 |
| >= 4 leaves (all with a stimulated shared upstream) | 4 | 0.763 / 0.782 | 0.462 / 0.476 | 0.899 / 0.933 |

**2. Merged pairs.**
- Only 5 pairs of true leaves are still merged at the end of a run, all in 2-leaf groups. Their oracle split (leaf
  A against the rest) has log E 101 at the end (in-sample null), against log(1 / alpha) = 3.0. The pairs have 18
  events (p50) with exactly one of the two leaves on, and the null fit ends at m0 ~0, f0 0.34.
- So the loss of pair precision is not leaves that stay merged: it is **leaves split late**. Pair precision is
  scored at every close, so the reads before the split count against it.
- In those 5 runs the split actually proposed at the end has log E 30, far above 3, but the merged pair lies inside
  one of its halves. The proposal picked another split first, and the next level has not accepted yet (a
  recursion / proposal effect; FLAG).

**Event of the root's first accepted split, counted from the first separating event (some but not all true leaves
on; it is the 1st or 2nd event in these runs):**

| runs | n | corrected (in-sample null): lag p50 / p90, never | same test, predictive null: lag p50 / p90 | first test: lag p50 / p90 |
|---|---|---|---|---|
| 2 leaves | 51 | 5 / 26, 2 never | 2 / 9 | 1 / 2 |
| 3 leaves | 14 | 3 / 8 | 1 / 3 | 1 / 2 |
| >= 4 leaves | 4 | 2 / 10 | 1 / 2 | 1 / 1 |

**3. What explains the loss of power: (b), the in-sample null fit, not (a).**
- The loss is largest where the two-leaf alternative is the correct model: 2-leaf groups, pair P 0.82 / 0.68.
  There the root's first split comes 5 events (p50) and 26 events (p90) after the first separating event.
- With the same alternative but the null fitted only on past events, the lag shrinks to 2 / 9. The first test needs
  1 / 2.
- Groups with 3 or more leaves split sooner (lag 3 / 8 and 2 / 10), not later, so a poor two-leaf model of
  multi-leaf groups is not what slows the test.
- Mechanism: the null's three parameters (pi, m0, f0) are refitted on all events up to t, including the event being
  scored. For few events and a stimulated shared upstream (49 of 51 two-leaf runs: most events have both leaves on),
  the one-leaf mixture fits the data almost as well in hindsight (f0 absorbs the partial events: f0 0.34 at the
  end), while the alternative is scored only out of sample. The ratio grows slowly until enough separating events
  accumulate.
- The >= 4-leaf pair-precision loss (0.46 / 0.48, 4 runs) is at the deeper levels: the root splits within 2 events,
  but the next levels come later. Too few runs to tell (a) from (b) there (not reliable).
- Hypothesis (a) is not supported by these numbers for the root split. A test of "one leaf against the current
  multi-leaf candidate partition" would address deeper levels, but the root-level delay is the null fit.
- The predictive-null variant was measured here for timing only. Its false-split share (STEP 2) was not measured;
  it is not a proposal until that is known.

## C. Corrected test, steps 1-3 (complete; alpha 0.05, single-queue, r1 / r2)

Full tables: [tables-v2-E1-0.5.md](tables-v2-E1-0.5.md) (primary), [tables-v2-E3.md](tables-v2-E3.md),
[tables-step3-v2.md](tables-step3-v2.md); each holds the first run's numbers next to the corrected ones.

| formation | test | pair P | leaf F1 | STEP 2 false splits, single-leaf runs / leaves alone (20 orders mean) | first correct group: events p50 / p90; s p50 / p90 |
|---|---|---|---|---|---|
| E1-0.5 | first | 0.988 / 0.989 | 0.965 / 0.965 | 0.082 / 0.062 (0.078 / 0.068) | 1 / 1, 1 / 12 ; 1 / 1, 1 / 17 |
| E1-0.5 | corrected | 0.930 / 0.871 | 0.952 / 0.934 | 0.007 / 0.007 (0.001 / 0.001) | 1 / 2, 1 / 70 ; 1 / 8, 1 / 269 |
| E3 | first | 0.979 / 0.965 | 0.968 / 0.958 | 0.041 / 0.023 | 1 / 2, 11 / 70 ; 1 / 3, 7 / 113 |
| E3 | corrected | 0.854 / 0.793 | 0.931 / 0.912 | 0.000 / 0.003 | see table |
| frozen E0 | SETS k2 | 0.996 / 0.977 | 0.858 / 0.863 | - | 2 / 6, 32 / 124 ; 2 / 7, 32 / 98 |

- The corrected test meets the false-split condition everywhere and the leaf-F1 condition (above frozen SETS k2),
  but not pair precision >= 0.93 in both reps (E1-0.5 r2 0.871).
- Late joiner (E1-0.5): NPR joins 111 / 111 (r1) and 105 / 105 (r2) released cases, 1 event (p50) and 25 / 16 s
  after release. SETS k2 on the same events: 3 events, 40 s; frozen SETS: 4 events, 50 s.
- Synthetic step 3 with the corrected test: leaf F1 0.70-0.93 and pair P 0.66-0.93, against 0.81-0.98 and >= 0.94
  for the first test at the measured false inclusion. The same loss of power appears at scale. SETS k2 still
  collapses at 1000 clients.

## D2. Window W (sensitivity only; corrected test, alpha 0.05)

| W | pair P | leaf F1 | false splits (single-leaf runs / leaves alone) |
|---|---|---|---|
| 0.5 s | 0.930 / 0.871 | 0.952 / 0.934 | 0.007 / 0.007 |
| 1 s | 0.934 / 0.882 | 0.954 / 0.937 | 0.007 / 0.007 |
| 2 s | 0.925 / 0.875 | 0.954 / 0.936 | 0.000 / 0.000 |

NPR is insensitive to W between 0.5 and 2 s (+-0.01). The choice of W matters for the time to a final member set
(0.5 s vs 2 s), not for the grouping.
