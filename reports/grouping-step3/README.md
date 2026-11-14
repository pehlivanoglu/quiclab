# Part 1 (procedure fix) and Step 3: carrying groups across events (2026-11-12)

Read-only, development set (K*, C1, M*, J1; G0 for negatives), single-queue AQMs
(pfifo, pie, red, codel), N1–N5 not opened, no ECG engine change. Code:
`scripts/grouping_step3.py` (constants and tags in its docstring). Run on
`.runs/2026-11-10_1946_v2`:

```
python3 scripts/grouping_step3.py part1      .runs/2026-11-10_1946_v2 reports/grouping-step3/part1-rows.jsonl   # then gzip
python3 scripts/grouping_step3.py part1-sum  reports/grouping-step3/part1-rows.jsonl.gz reports/grouping-step2/step2-rows.jsonl.gz
python3 scripts/grouping_step3.py step3      .runs/2026-11-10_1946_v2 reports/grouping-step3/step3-rows.jsonl   # then gzip
python3 scripts/grouping_step3.py step3-sum  reports/grouping-step3/step3-rows.jsonl.gz --variant m|c
python3 scripts/grouping_step3.py plots      .runs/2026-11-10_1946_v2 reports/grouping-step3/step3-rows.jsonl.gz reports/grouping-step3 --variant m|c
```

Files: `part1-rows.jsonl.gz` / `part1-summary.md`; `step3-rows.jsonl.gz` (both
variants, m = 1, 2, 3, full E trajectories) / `step3-summary-m.md` /
`step3-summary-c.md`; `step3-traj1..6-{m,c}.png` (base, split, depth, J1 jit20 =
realised sd 12.6 ms, independent timing, G0 calmuneven). 147 runs with windows or G0
for Part 1 (3547 events with windows, 244 negative); 152 runs for Step 3 (128 with
windows, 24 G0, 3791 events). Part 1 counts run names with at least one event (the
same name in K3 and M3 counts once); Step 3 also lists the 4 runs without any event
(calm030 pfifo / pie / red, K3 revcross pfifo).

Constants: ALPHA 0.01 (T), b = ln(1/α) + ln N (N = clients in the run, P: 6.55 nats
for N = 7, 6.80 for N = 9), m = 1, 2, 3 (T), no decay (limitation), INTERCHANGE 1.2
(FLAG), SPLIT_MIN 4 (T); FLAG choices of mine: event intervals as step 2; the 2-split
of side measurement (b) is a seeded two-template reassignment (no exhaustive search);
false-membership scoring (two versions, below). Step 2 constants unchanged.

## Part 1: fixed procedure

Class 0 start, each data template from the split step (seed = worst-fitting
participant, plus its nearest), ≥ 2 members, split while G > 0. `part1-summary.md`
has it side by side with the old step 2 procedure (initial median) at penalty 0 and 1
on the same events.

- Over all events it is the same as the old procedure at penalty 0: exact 0.74, pair
  P 0.94, R 0.84, 575 over-splits, congested clients in class 0: 0.00. The initial
  median was not what limited the x0 numbers.
- Group of 2 (the step 2b D failure): congested-in-class-0 goes to 0.00 (was 0.49 at
  x1), but now quiet clients join the pair: single group / size 2 exact 0.53, pair P
  0.44, quiet in class 0 0.58. Concurrent / nested with a size-2 group: exact
  0.44 / 0.60.
- Single group, size ≥ 3: exact 0.68 with 488 over-splits (no acceptance rule: any
  positive gain splits).
- Negatives: 222 of 244 events get a data template.

For Step 3 only the congested set matters (not class 0): congested clients in class 0
are 0.00–0.01 in every class, quiet clients outside class 0 are 0.18 overall (0.37 on
J1 random phase).

## A defect in step 5 as written, and the two versions

When two active groups have the same contributors (the same congested clients with
E > 0), their leave-one-out templates are identical, so dE = n_eff · ln(f / f) = 0
exactly for both. Step 5 ("gained positive evidence for no active group") then puts
those clients into a new group, which is again identical, and so on: one duplicate
group per event. In K1 hier pfifo (m = 2) the set {b1, b2, b3} was created 26 times.
Over the positives variant m has 874 groups, up to 76 in one run and 75 active in one
event; side measurement (a) counts are inflated by these duplicates (10⁴–10⁵
"interchangeable" pairs).

- **variant m**: the brief as written.
- **variant c**: in step 5, dE = 0 counts as gained (`x >= 0` instead of `x > 0`).
  Between two active groups dE is antisymmetric (ln(f₂/f₁) vs ln(f₁/f₂)), so dE = 0
  only happens for identical templates; nothing else changes.

I tried a broader rule first ("a congested client still in an active group is not
new"); it stops merged groups from ever separating (K1: one 6-client group to the end,
9 false SAME pairs), because a separated leaf group only appears through step 5. Not
kept.

Variant c: 199 groups (≤ 6 per run), evidence-update comparisons per event p90 21
(variant m: 98). Final pair results are almost identical between the two variants.
Numbers below are variant c unless stated.

## Results against the reading rules

### Precision, false memberships, speed

| family (runs) | final pair P / R / cov (c2) | every-close P (c1 / c2 / c3) | ECG every-close P | events to membership p50 (c1 / c2 / c3) | ECG |
|---|---|---|---|---|---|
| single group families: K2, K3, K5, M1–M6 (no indep) | 1.00 / 1.00 / 0.53–0.60 | 1.00 | 1.00 | 1 / 2 / 4 (K5: 3 / 4 / 6) | 2–4 |
| K1 split (3) | 1.00 / 1.00 / 0.71 | 0.90 / 0.92 / 0.94–0.96 | 0.86–1.00 | 1 / 2 / 3 | 5 |
| K6 depth (1) | 1.00 / 1.00 / 0.78 | 0.83 / 0.90 / 0.92 | 0.60 | 0 / 0 / 2 | 4 |
| C1 burstlongsplit (3) | 0.46–1.00 / 1.00 / 0.71 | 0.63–0.94 | 1.00 | 0 / 2 / 2 | 2 |
| J1 (10; jit 5 / 10 / 20, same / random phase) | 1.00 / 0.92–1.00 / 0.71 | 0.67–0.97 | 0.75–0.92 | 1 / 2–3 / 3–4 | 2–4 |
| M6 independent timing (8) | 1.00 / 1.00 / 0.71 | 0.70–0.95 / 0.74–0.98 / 0.75–1.00 | 0.46–0.88 | 1 / 2–3 / 3–4 | 2–4 |

(per AQM rows in `step3-summary-c.md`; "0" events = the client became a member in an
event its own group did not take part in, i.e. through a merged group.)

Realised false-membership rate (positives), α = 0.01:

| | c1 | c2 | c3 | m1 | m2 | m3 |
|---|---|---|---|---|---|---|
| at declaration (majority leaf, ties wrong) | 0.30 | 0.20 | 0.18 | 0.19 | 0.19 | 0.18 |
| per close (group holds a member of another leaf) | 0.41 | 0.30 | 0.28 | | | |
| single-group families only | 0 / 408 | 0 / 392 | 0 / 392 | 0 | 0 | 0 |

All wrong memberships are in the multi-group families (K1, K6, C1, J1, M6 indep):
there 0.37–0.75 of memberships are wrong at some close. Wrong memberships last p50
2–16 events (tens to hundreds of seconds); p90 up to the whole run in J1 / K1
(`step3-summary-c.md`).

**Reading.** Precision at the last event is at or near 1 (exception C1 pfifo / red,
0.40–0.67), and membership comes in fewer events than ECG at m ≤ 2 (ECG p50 2–5).
But the false-membership rate is 20–40 times α, so the rule "false memberships at or
below α" is not met. The cause is visible in the trajectories:

1. The first event of a run that touches two leaves (shifted windows within the 1 s
   margin, concurrent, upstream, or the first independent-timing overlap) makes one
   merged group (step 5: no split inside the event).
2. As long as that group is the only active one, every congested client's evidence
   is "better than flat", clipped to +b/m, and the absent leaf's clients get −b/m.
   So after m events with mostly one leaf, those clients are declared members of the
   merged group. The clip limits the rate, not the direction: alt = class 0 gives
   evidence for congestion, not for this group.
3. A competing group only appears when class 0 fits better than the merged template
   (step 5), usually on an event where the other leaf is quiet. Until then nothing
   can move a client out except −b/m steps.

Two smaller observations:
- ECG uses its own event list (more, shorter events) and its every-close P is lower
  in K6 / M6 indep / J1 jit5, higher in C1.
- m = 1 declares a group in one event: every first-event merge becomes a declared
  wrong membership (first membership right 0.00 in K1, K6, J1 jit 5–20, M6 indep).

### Groups that start merged

| | c1 | c2 | c3 |
|---|---|---|---|
| merged groups (of all groups) | 41 / 199 | 40 / 193 | 42 / 197 |
| separated (one leaf at a later close) | 31 | 32 | 32 |
| events to separate p50 / p90 | 2–13 / 6–28 by family | 1–12 / 4–19 | 1–12 / 3–16 |
| never: removed | 9 | 7 | 9 |
| never: still merged at the end | 1 | 1 | 1 |

The one never-separated group is C1 (burstlongsplit, upstream-heavy): it is why C1's
final P is 0.40–0.67. After separation the old merged group usually survives as a
near-duplicate of one leaf group (same contributors, dE ≈ 0, E frozen; the flat lines
in `step3-traj2-c.png`). That costs nothing in pair terms, but it is the main source
of side measurement (a).

### sub-ctrl

Never above 0 in any group, either variant, any m.

### Negatives (G0), topology truth of step 2b

SAME pairs after the last event: c1 214 right / 11 wrong, c2 207 / 3, c3 221 / 0
(variant m the same order: 219 / 11, 207 / 3, 221 / 0); ECG 25 / 0. The wrong ones
are calmsplit red (3) and calmuneven red / calmtree8 red at m = 1. Groups form in
every calm G0 run except calm030 (one group of the 4 base clients in calm065 / 090 /
cbr090 / randloss, 3–5 groups in tree8 / uneven), so Step 3 states many more shared
queues than ECG does, and almost all of them are physically right (the step 2b C
result: calm periods carry shared-queue evidence).

### J1 and independent timing

In the table above. Every-close P by jitter (c2): jit5 0.77, jit10 0.76, jit20 0.87,
same phase 0.87, random phase 0.95; the ordering by jitter is not monotonic (2 runs
each; the first-event merge dominates). Independent timing (M6 indep): final P 1.00
on all 8 runs, every-close P 0.74–0.98 (c2), merged groups separate in p50 2–3 events.

### Side measurement (a): interchangeable templates

With variant c, events with ≥ 2 active groups: K1 ~205, J1 93–147 per family,
K6 64, M6 indep 102–443. Interchangeable pairs are mostly **same-leaf vs same-leaf**
(the separated merged group and the leaf group it duplicates), e.g. K1 136 of 139,
J1 random phase 74 of 74. Pairs of different leaves (a vs b) are rare: C1 4, J1 jit10
7, K1 3, M6 indepfast 13 (m = 2). All of them "share a recorded egress", but that
column is not informative here: every client in K1 / C1 / J1 / K6 shares the
upstream r1->r2 egress. So the stall that (a) shows is the duplicate-group stall, not
a shared upstream. The topologies with a real shared upstream in the positives (K1 a+up,
K6 levels) have few upstream events (27 nested events in total).

### Side measurement (b): split consistency

| m (c) | group | groups | top-split share p10 / p50 / p90 | top split = a true leaf |
|---|---|---|---|---|
| 2 | one true leaf | 95 | 0.41 / 0.57 / 0.80 | 0 |
| 2 | mixes two leaves | 35 | 0.48 / 0.67 / 1.00 | 28 |

A one-leaf group's best 2-split changes from event to event and is never a leaf. A
mixed group's split recurs more often and is the true leaf boundary in 28 of 35
groups (m = 1: 31 / 35; m = 3: 28 / 35). That is the across-event signal the
merged-group problem above needs, but it is a measurement only; nothing uses it.

### Cost

Variant c: state after a close p50 6, p90 9, max 24 (client, group) entries; at most
5–6 groups. Template comparisons per event: Part 1 procedure p50 77 (p10 50, p90 125),
evidence update p50 6, p90 21. Variant m: up to 228 entries and 76 groups.

## Limitations and reading checks

- No decay (brief); runs are 5–16 min.
- Event intervals come from windows.json (oracle timing, ±1 s margin); with the
  detector the first-event merges could be more or fewer.
- Clip reading: I clip when the smallest f is class 0 (the literal "if alt is class
  0"), also when another group is active. That happened 15 300–15 700 times (variant
  c). The other reading (clip only when no other group is active) was not run.
- Families K1 / K6 / C1 have 1 run per AQM, J1 2 runs per type: small samples.
- ECG events to membership are counted on the Step 3 event list (events of the
  client's true group whose start is at or before ECG's first member close: node set,
  L ≥ A). ECG's own `membership_events` (its event count) is in the rows.
