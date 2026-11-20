**Agree after the application-limited patch (ack-matched, primary):** F1 calm mean (0 -> 17 / 22 pairs), onset spread p50 (13 / 14; v1 already 12 / 14 under the same tick criterion, so the patch is not what fixed it), detection delay p50 (13 / 14), GT3 precision / recall (14 / 14, 13 / 14), SETS leaf F1 and pair precision (equal to the testbed within a few hundredths). **Still do not agree:** keyframe queue peak (4 / 22; simulation 0.67 x the testbed, median), F1 calm sigma (5 / 22; 0.62 x), onset spread p90 (8 / 14; wider at G-SIZE), and D1-bw's reaction time, which went from "fires all the time" (v1) to **2.5 x late** (0 / 14). The detector has an easier job in calm time in the simulation (fewer sub-threshold excursions, a narrower F1), so false-alarm rates must not be taken from it. The gap to mvfst is reported, not closed.

# Simulation stage B2: re-run with the application-limited patch (2026-11-18)

Earlier stage B (before the patch, "v1"): [../sim-stageB-2026-11-18/README.md](../sim-stageB-2026-11-18/README.md).
Patch and its one-run check: [../../simulation/patches/README.md](../../simulation/patches/README.md),
../sim-stageB-2026-11-18/applimited-check.md (deleted 2026-11-19; its result is summarised in section 3 here).
Per-pair tables (reps side by side): [tables-matched.md](tables-matched.md) (primary), [tables-spec.md](tables-spec.md)
(second row); SETS, spread p90, calm rows: [extra.md](extra.md) (`simulation/simlab/stageb2_extra.py`); raw rows
`rows-matched.jsonl`, `rows-spec.jsonl`, `calm.json`.

## 1. Validity

| item | value |
|---|---|
| cells | the same 11 cells x 2 reps as v1 (CALM 4 / 8 clients x pfifo / codel; S-BURST T-BASE x pfifo / codel / pie; H-HIERL T-SPLIT4L x pfifo / codel; G-SIZE T-LEAFn 16 / 24 x pfifo), testbed counterparts K1 r1 / r2 |
| runs planned / completed / failed | ack-matched 22 / 22 / 0; spec-ACK 22 / 22 / 0; no scoring failure |
| code version | all 44 runs: quicsim binary `cb92cacb8758f83b`, libns3 internet `21eecfc6eeaf93bd` (patched), sources `89818abcef92b4a7` (includes the patch file); one build for both ACK profiles |
| change against v1 | only the patch (ns-3 `TcpSocketBase::Send`: the application-limited check before the new data is added, as Linux). FLAG P1 (NOTES.md): this is a change to ns-3 |
| events delivered against plan | exact by construction (as v1) |
| GT-Q health | ok on all 44 (lost 0, identity ok) |
| wall clock | ack-matched 36 min end to end (8.5 min simulation, the rest frozen scoring), spec-ACK 61 min (includes guard pauses), 1 core each; longest single run 76 s; peak memory 0.46 GB |
| disk | 8.5 GB (matched) + 8.9 GB (spec) + tick cache 3.0 GB; free 163 GB after |
| measured load and share against target | the frozen v3 check (`v3_gate.check_load_share`) on every simulation run: **ok on all 38 egresses of the 22 ack-matched runs**; load 0.503-0.709 against U 0.5 / 0.7, video share 0.306-0.310 against s 0.30; within 0.008 of the testbed counterpart everywhere ([load-share.md](load-share.md)) |

## 2. Agreement table (spec section 5 limits; spread and delay p50: 30 % or one tick, user 2026-11-18)

Counts are pairs inside the limit (14 stimulus pairs, 22 for the calm rows). Values: median over pairs.

| measure | limit | v1 matched | **B2 matched** | B2 spec | testbed median | sim median: v1 / **B2 matched** / B2 spec |
|---|---|---|---|---|---|---|
| keyframe queue peak in calm time (p50 of per-GOP maxima) | 20 % | 0 / 22 | **4 / 22** | 3 / 22 | 5.05 ms | 0.44 / **3.93** / 3.63 ms |
| detector F1 calm mean | 30 % | 0 / 22 | **17 / 22** | 10 / 22 | 2.16 ms | 0.49 / **2.74** / 1.35 ms |
| detector F1 calm sigma | 30 % | 0 / 22 | **5 / 22** | 0 / 22 | 1.49 ms | 0.26 / **0.88** / 0.68 ms |
| detection delay p50 (v2-owd on GT3-A) | 30 % or 1 tick | 12 / 14 | **13 / 14** | 14 / 14 | 161 ms | 134 / **147** / 134 ms |
| GT3 precision | >= 0.98 | 14 / 14 | **14 / 14** | 14 / 14 | 1.00 | 1.00 |
| GT3 recall | +- 0.05 | 13 / 14 | **13 / 14** | 14 / 14 | 1.00 | 1.00 |
| onset spread p50 | 30 % or 1 tick | 12 / 14 | **13 / 14** | 13 / 14 | 49.5 ms | 33 / **33** / 49.5 ms |
| onset spread p90 | 30 % or 1 tick | 9 / 14 | **8 / 14** | 6 / 14 | 147 ms | 149 / **135** / 147 ms |
| D1-bw reaction (delay p50) | 30 % | 2 / 14 | **0 / 14** | 0 / 14 | 506 ms | 0 / **1837** / 1665 ms |

The v1 counts here are recomputed from v1's rows under the same tick criterion (v1's own tables use the plain 30 %
limit: spread p50 7 / 14 there). **Correction to the summary given in chat on 2026-11-18:** it set v1 under the plain
limit next to B2 under the tick limit and showed spread p50 as "7 -> 13"; like for like it is 12 -> 13 (spec-ACK 14 ->
13). The patch did not fix spread p50; the tick criterion did. F1 mean is the row the patch fixed. Per pair, simulation over testbed (B2 matched; min / median / max): keyframe peak
0.43 / 0.67 / 0.87, F1 mean 0.56 / 1.06 / 1.33, F1 sigma 0.49 / 0.62 / 0.93, D1-bw delay 1.38 / 2.47 / 4.79.

ack-matched against spec-ACK: ack-matched is closer on F1 mean (17 against 10), F1 sigma (5 against 0) and spread p90
(8 against 6); spec-ACK on recall and delay (one pair each). ack-matched stays the primary profile, as decided.

Not limited (tables): delay p90 testbed 288 ms, simulation 210 ms; GOP drops per client-minute 3.2 against 0.8; video
rate in stimulus windows / nominal 0.67 against 0.80; D1-bw precision 0.97 against 0.93, recall 0.97 against 0.84,
false alarms 0.09 against 0.35 / min. GT3 source B (testbed side): as in v1.

## 3. What the patch changed in BBR (one-run check and all 44 runs)

| quantity (median per client) | testbed (mvfst) | v1 sim | B2 sim (matched) |
|---|---|---|---|
| share of ACK rows marked app-limited | 0.85 | 0.013 | 0.94 |
| time in ProbeBW / STARTUP | 0.93 / 0.056 | 0.99 / 0.001 | 0.94 / 0.053 |
| pacing gain in effect at keyframe writes | 1.20 | 1.24 | 1.24 |
| BBR bandwidth estimate / video rate (A1 calm-base r1, sub-a, b, d) | 4.8-6.1 x | 1.3-1.7 x | 5.6-8.4 x |
| keyframe pacing spread, calm cells (median per egress) | 2.6-4.0 ms | 67-76 ms | 6.2-7.8 ms |
| keyframe pacing spread, cells with surges | 23-31 ms | 66-73 ms | 19-31 ms |

The mechanism the v1 report named is fixed: the flow is marked app-limited, the estimate stays near the path's rate,
keyframes leave in a few ms, and the keyframe queue forms (0.3 ms -> 4-13 ms). What remains:

- **Calm spread 1.5-2.5 x the testbed's, bandwidth estimate 1.1-1.4 x.** The simulation marks *more* ACKs app-limited
  than mvfst (0.94 against 0.85), so the remaining difference is not where the mark is set (see section 7 for the
  pre-declared attempt).
- **Keyframe peak 0.67 x even where the spread matches.** At G-SIZE (16 / 24 clients) the pacing spread is the same on
  both sides (27-29 ms), the keyframes of all clients are written in the same millisecond on both sides (phase
  0.7-0.9 ms testbed, 0.0 ms simulation), keyframe sizes are equal (7.4 kB median), and still the peak is 10.6 against
  18-19 ms. So part of the gap lies after the sender's pacing decision. Candidates, **not measured**: mvfst writes
  several packets per pacer tick (burst writes) where ns-3 sends one segment per pacing interval; the testbed's veth /
  netem path adds batching. FLAG: unresolved; it bounds what the simulation can say about queue size.

## 4. Additions requested on acceptance

### 4.1 SETS grouping (frozen SETS on frozen-detector onsets, k = 2 / 3)

Leaf F1; pair precision; pair recall per cell and rep in [extra.md](extra.md). Summary over the 14 stimulus pairs
(medians):

| | testbed | v1 matched | B2 matched | B2 spec |
|---|---|---|---|---|
| leaf F1, k = 2 | 0.95 | 0.95 | 0.95 | 0.95 |
| leaf F1, k = 3 | 0.90 | 0.90 | 0.90 | 0.90 |
| pair precision, k = 2 | 1.00 (0.97-1.00) | 1.00 | 1.00 (0.93-1.00) | 1.00 (0.99-1.00) |
| pair recall, k = 2 | 0.81 (0.53-1.00) | 0.98 (0.56-1.00) | 0.89 (0.71-1.00) | 0.87 (0.65-1.00) |
| pair recall, k = 3 | 0.90 (0.62-1.00) | 0.98 (0.52-1.00) | 0.98 (0.69-1.00) | 0.97 (0.65-1.00) |

Leaf F1 and pair precision agree. Pair recall is higher in the simulation in most cells (fewer pairs split by an
onset arriving outside the group's window), consistent with the narrower calm noise (4.3). G-SIZE: equal (0.92-1.00
both sides). FLAG: pair recall from the simulation is optimistic by about 0.08 in the median for both k, more in single cells (A4 pfifo r1: 0.53 against 1.00).

### 4.2 Onset spread p90: direction per cell (ms, simulation - testbed, r1 / r2)

| cell | testbed | B2 matched | B2 spec | v1 matched |
|---|---|---|---|---|
| A2 S-BURST pfifo | 99 / 152 | -33 / -33 | +53 / 0 | -56 / -76 |
| A2 S-BURST codel | 231 / 142 | 0 / +10 | -92 / +10 | +10 / +49 |
| A2 S-BURST pie | 119 / 142 | **+145** / -33 | +43 / -10 | -10 / -56 |
| A4 H-HIERL pfifo | 99 / 152 | 0 / **-53** | -33 / -66 | -33 / +13 |
| A4 H-HIERL codel | 132 / 119 | -33 / -20 | -66 / -53 | -33 / +13 |
| G1 G-SIZE n16 | 208 / 175 | **+274 / +76** | -66 / +30 | -33 / -10 |
| G1 G-SIZE n24 | 294 / 247 | **+135** / +23 | +46 / -16 | -66 / -50 |

Bold: outside the limit (B2 matched). The sixth failing pair (A2 pfifo r1, 66 against 99 ms) is exactly one tick, at
the limit's edge; it counts as a fail under the rule as written. Direction (B2 matched): **wider at G-SIZE** (3 of 4
pairs fail, all wider, by 0.4-1.3 x the testbed's value) and in one A2 pie pair; narrower by one or two ticks
elsewhere. v1 was narrower almost everywhere. Reading: with the patch, keyframes leave the sender faster, but onsets at
the 16 / 24-client leaf spread further; a tail effect of a few late members (p50 agrees in every G-SIZE pair). FLAG:
G-SIZE is the layout closest to stage C, so event formation at scale must be read with this in mind (section 6).

### 4.3 Calm behaviour: does the detector have an easier job in the simulation?

Definitions fixed before the numbers ([extra.md](extra.md) header): calm ticks as in section 2; calm alarms = frozen
v2-owd episodes whose alarm falls in calm time; sub-threshold event = a run of calm ticks with score >= theta_off
(0.125) that never reaches theta_on (0.25); keyframe-aligned = the event's first tick within 3 ticks after a keyframe
write of the same client. (Declared as 2 ticks; on the first testbed run checked, every event started 67-71 ms after a
keyframe, just outside 66 ms, because the 33.0 ms tick grid drifts against the 33.3 ms frame grid; changed to 3 ticks
before any table was produced. Chance level about 10 %.)

| median over 22 pairs | testbed | v1 matched | B2 matched |
|---|---|---|---|
| calm alarms / min (pooled clients) | 0.000 (3 pairs > 0: 0.02-0.03) | 0.000 | 0.000 (none) |
| sub-threshold events / client-minute | 0.61 | 0.00 | 0.46 |
| CALM cells only (8 pairs) | 0.60-1.79 | 0 | 0.46-0.93 |
| G-SIZE (4 pairs) | 0.62-2.54 | 0-0.05 | 0.74-1.58 |
| share keyframe-aligned (CALM cells) | 0.64-1.00 | - | 0.33-0.77 |
| detector score p99 in calm ticks (CALM cells) | 0.051-0.061 | 0.000-0.024 | 0.058-0.064 |

**Yes, the detector's job is easier in the simulation.**
- Sub-threshold excursions are 0.4-0.8 x the testbed's, so the score comes near the threshold less often.
- F1 calm sigma is 0.62 x, so the same keyframe queue is less noisy around its mean.
- Fewer of the excursions are tied to keyframes (0.33-0.77 against 0.64-1.00). The testbed's near-misses are mostly
  keyframe queue spikes that the simulation reproduces at 0.67 x height.
- At the run lengths here neither side has more than a handful of calm alarms. So the false-alarm rate cannot be
  calibrated from these cells at all: the simulation's 0.00 is not evidence of a lower rate.

Also seen: after surges, on the testbed the 5 Mb/s client's episodes run past window end + 3 s (A2: score held at its
cap for ~10 s of calm time per run); in the simulation they end inside it. This is a slower recovery on the testbed,
not extra alarms. The simulation's episodes are shorter after overload (consistent with the shorter delay p90:
210 against 288 ms).

## 5. What the simulation may and may not be used for (as it stands)

**May be used for (each row agrees within its pre-declared limit in most pairs, with the stated caveats):**
- grouping at scale: SETS leaf F1, pair precision. Pair recall is optimistic by ~0.1 at small layouts and equal at
  G-SIZE;
- detection precision / recall / delay p50 against GT3 (13-14 / 14);
- onset spread p50 (13 / 14; also 12 / 14 before the patch). The p90 tail is wider at G-SIZE (4.2), so it is reported side by side, not as a
  calibrated value.

**May not be used for:**
- **false-alarm rates.** Calm noise is narrower (F1 sigma 0.62 x, sub-threshold excursions 0.4-0.8 x), and the calm
  alarm count is near zero on both sides at these lengths;
- **the keyframe queue size** (0.67 x, 4 / 22), or anything derived from it: the 0.121 s U prediction, F1 levels as
  absolute values;
- **D1-bw.** Its delay is 2.5 x late (1.4-4.8 x) and its recall lower (0.84 against 0.97). This error favours our
  method in any comparison, so **D1-bw must not be reported from the simulation**, neither as a baseline nor as a
  ratio;
- QUIC-specific behaviour, player harm (TCP head-of-line blocking), fq_codel / cake, jitter, loss: as in v1, not modelled.

## 6. Deviations and decisions

- The application-limited patch (FLAG P1, NOTES.md): one change to ns-3, Linux placement; decided by the user
  2026-11-18.
- ack-matched primary, spec-ACK as a second row in stage B only (user 2026-11-18).
- Spread and delay p50: 30 % or one tick, whichever is wider (user 2026-11-18; NOTES.md deviation D-tick).
- Calm keyframe alignment window 3 ticks instead of the first-declared 2 (4.3; definition fault, fixed before any table).
- SETS: as v1 (R1's level T100 path, the testbed counterpart's ECG configuration on both sides).
- Unchanged from v1: GT3 source A on both sides, `qdiscs.txt` written from the plan, calm-time definition.

## 7. Pre-declared attempt at the mvfst gap

The user pre-declared one attempt: patch 2, a mark at the end of every write round as mvfst does, as a separate
patch, ack-matched only, with a fixed decision rule. Status and result: [../sim-stageB3-mvfst-drain/README.md](../sim-stageB3-mvfst-drain/README.md).

## 8. What these runs cannot tell

- Why the keyframe peak is 0.67 x where the pacing spread matches (3, candidates not measured).
- Calm false-alarm rates (4.3).
- Anything above 24 clients (item 5: the 300-client test run).

## 9. Corrections (2026-11-19, after acceptance)

### 9.1 CoDel drops recorded twice (recorder fault; fixed)

The egress monitor counted a packet that CoDel took from its queue and then dropped as both dequeued and dropped. It
also wrote a "dequeue" and a "drop" row for that packet (ns-3 fires "Dequeue" before "DropAfterDequeue"). Only the
recording was wrong; the simulated network is unchanged.

- **Affected runs:** A2-sburst-codel and A4-hhier-codel (both reps, both ACK profiles; calm CoDel runs have no drops
  after dequeue).
- **Affected outputs:** router-trace, router-metrics transmitted_bytes, tracer-counts, and what derives from them
  (gtq-health, truth/gtq*).
- **Before / after:** residual enq - deq - drop -17k to -38k per egress before, 0 after; the drop counts are unchanged.
  Tables: `../sim-stageB2-codelfix/codel-before-after.md`.
- **Gate:** all 44 runs re-run (`simulation/runs/stageB2-codelfix`). pfifo runs byte-identical in every file. CoDel
  runs changed only in the router-trace / router-metrics files and what derives from them (gtq-health, truth/gtq*,
  the GT-Q line of scored.json). File lists: `../sim-stageB2-codelfix/diff-vs-B2-*.md`.
- **Effect on this report:** none. No value in the agreement table moved; it reads queue samples, sender records and
  GT3, not the router trace.

### 9.2 PIE runs not reproducible with the build of item 5; PIE given a fixed random stream

Item 5 replaced global routing by nix-vector routing. Global routing created a random-variable object per node
(ns-3 global-routing.cc:90). ns-3 numbers random streams in creation order unless a stream is set, and quicsim set
none. Removing those objects therefore shifted PIE's stream and changed its drop sequence. The item-5 byte regression
covered only two pfifo runs, so it did not see this.

- **The PIE rows of this report, as accepted before 2026-11-19, cannot be reproduced with the current build.**
- **Fix:** PIE and RED now get a stream fixed by the plan (`kStreamQueue` + the egress index), so their draws no longer
  depend on which other objects exist. Shown: the same PIE run with global routing switched back on is byte-identical.
- **BBR left as it was:** BBR also draws (its ProbeBW cycle index). Fixing its stream changed the S-BURST, H-HIERL and
  G-SIZE pfifo / CoDel runs, so per the user's rule it is not applied and is reported. Today BBR's draws do not depend
  on the routing objects: a pfifo run with global routing on is byte-identical.
- **Gate:** the BBR-sensitive pfifo / CoDel runs (A2-sburst, A4-hhier, G1-n16 matched; A2-sburst spec) are
  byte-identical to the 9.1 runs. The 4 PIE runs (`simulation/runs/stageB2-piestreams`) are the new reference.

PIE rows, old (as accepted) and new, every moved value marked: `../sim-stageB2-piestreams/pie-before-after.md`.
Agreement verdicts:

| profile | PIE verdict cells | ok before | ok after | verdicts that changed |
|---|---|---|---|---|
| ack-matched (primary) | 18 | 10 | 10 | none |
| spec ACK (second row) | 18 | 12 | 11 | GT3 recall, A2-sburst-pie-r1: 0.900 -> 0.791 against the testbed's 0.935 (ok -> FAIL) |

- **No accepted conclusion changes.** The primary profile's verdicts are unchanged, and the spec-ACK row's GT3 recall
  count becomes 13 / 14 instead of 14 / 14.
- **PIE runs are seed-sensitive in single values:** for example A2-sburst-pie-r1 spread p90 264 -> 66 ms, with only
  the drop sequence changed. Single PIE values are not to be read as precise.

### 9.3 Regression gate from now on

At least one run per queue type used anywhere in the simulation (pfifo, CoDel, PIE; RED if it is ever used), and the
scenario types where BBR enters ProbeBW (S-BURST, H-HIERL, G-SIZE), not two pfifo runs.

### 9.4 BBR's random stream fixed; new B2 reference (user 2026-11-19, evening)

BBR draws its ProbeBW cycle index from a random variable. That variable now has a fixed stream, and so does every
other random variable in the simulation (NOTES.md "Randomness"). This changed the S-BURST, H-HIERL and G-SIZE runs.
**The new reference for all 44 runs is simulation/runs/stageB2-streams.**

- **Gate:** the final build is byte-identical to that set on 7 runs (one per queue type plus the BBR-sensitive
  scenarios), also with unrelated random variables added and with global routing.
- **Agreement, accepted B2 against the new reference:** `../sim-stageB2-streams/b2-before-after.md`.

| measure | ack-matched (primary) ok, old -> new | spec ACK ok, old -> new |
|---|---|---|
| keyframe peak | 4 -> 4 / 22 | 3 -> 4 |
| F1 calm mean / sigma | 17 -> 17, 5 -> 5 / 22 | 10 -> 10, 0 -> 0 |
| detection delay p50 | 13 -> 13 / 14 | 14 -> 14 |
| GT3 precision / recall | 14 -> 14, 13 -> 13 / 14 | 14 -> 14, 14 -> 13 |
| onset spread p50 | 13 -> **14** / 14 | 13 -> 13 |
| onset spread p90 | 8 -> **7** / 14 | 6 -> 10 |
| D1-bw delay p50 | 0 -> 0 / 14 | 0 -> 0 |

- Medians, primary profile:
  - keyframe peak 0.78 x the testbed (unchanged);
  - F1 sigma 0.59 x (unchanged);
  - D1-bw 3.63 x late (unchanged);
  - delay p50 147 -> 141 ms (testbed 161);
  - spread p90 135 -> 142 ms (testbed 147).
- SETS leaf F1 / pair precision (k = 2): 0.947 / 0.998 -> 0.946 / 0.997 (testbed 0.932 / 0.999).
- **No accepted conclusion changes.** Single cells move by run-to-run noise: six spread p90 verdicts flip in each
  direction across the profiles.
