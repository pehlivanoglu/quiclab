# Step 5: measurement only (Part A, B1–B3) (2026-11-13)

Read-only, development set (K*, C1, M*, J1 positives), single-queue AQMs, N1–N5
not opened, no procedure or state change. Event intervals: ECG event intervals for
every run (the brief's decision). Part A also rescores the existing Step 4 rows, which
keep their windows.json timing.

Code: `scripts/grouping_step5.py` (constants and tags in its docstring). It uses
`grouping_step4.replay4`, which got one read-only `hook` argument; state and outputs
are unchanged.

```
python3 scripts/grouping_step5.py run .runs/2026-11-10_1946_v2 reports/grouping-step4/step4-rows.jsonl.gz reports/grouping-step5/step5-rows.jsonl   # then gzip
python3 scripts/grouping_step5.py sum reports/grouping-step5/step5-rows.jsonl.gz > reports/grouping-step5/step5-summary.md
```

Files: `step5-rows.jsonl.gz` (per run: Part A memberships under both truths, B1 votes,
B2 votes and stored halves) and `step5-summary.md` (all tables, per family and AQM).
128 runs, 5 141 ECG-interval events.

## A rule of the brief that does not work here, and the added version

The 5 ms rule of Step 2b ("any sample >= 5 ms inside the interval") is saturated on
3 s ECG intervals. On every multi-leaf topology both leaf egresses and the shared
upstream r1->r2 are "congested" in 91–100 % of events: K1 pfifo r1->r2 0.91, switch-a /
switch-b 0.99; C1 0.97 / 1.00; J1 jit20 0.99. Under this rule 13 366 of 13 891 B1
votes fall in the "all three congested" type, and the brief's event types are empty.

I report this rule as written (**peak5**) and one added rule (**gt1**, FLAG): a GT1
standing-queue episode (CoDel, target 5 ms, interval 150 ms) on the egress overlaps
the event interval. Under gt1 the shared upstream is congested in 20–62 % of events,
leaf egresses in 46–82 %.

## Part A: same-leaf errors that are physically right

| all positives | c3 (windows) | h3 (windows) | ECG | c3 (ECG iv) | h3 (ECG iv) |
|---|---|---|---|---|---|
| memberships | 702 | 930 | 800 | 789 | 1152 |
| wrong by same-leaf, declared / at some close | 0.18 / 0.28 | 0.10 / 0.20 | 0.09 / 0.14 | 0.16 / 0.27 | 0.11 / 0.23 |
| wrong by both truths, peak5 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| wrong by both truths, gt1 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.01 | 0.00 / 0.00 |
| share of same-leaf errors physically right (gt1, declared / close) | 0.99 / 0.99 | 0.99 / 0.99 | 1.00 / 1.00 | 0.96 / 0.98 | 0.96 / 0.98 |

Per family and AQM in the summary; the pattern is the same in every row.

**Reading, with a caveat.** By the letter of the brief, almost every same-leaf error of
all three methods is physically right, so the 0.09–0.10 floor would be a truth
artefact. But the second truth is weak in these topologies. A pair becomes "linked"
for good after one event in which its shared egress was congested. On K1 / C1 / J1 /
K6 / M6 indep every pair shares r1->r2 (or r0->r1 / r0->r2), and that egress has a GT1
episode in 20–62 % of events. So after the first few events every pair is linked, and
the second truth accepts almost any grouping of those clients. Part A therefore says
"the errors are clients that share a queue that does congest", not "the algorithm
picks the shared queue when it is the congested one".

A per-close version (shared egress congested in the current event) would separate
these two readings. It is not computed.

c3 (windows) reproduces Step 4 exactly (702 / 0.18 / 0.28). h3 (windows) has 930
memberships against 895 in Step 4, at the same rates; the cause is that Part A
rebuilds memberships from the stored, rounded E trajectories.

## B1: votes between true-leaf groups

Each congested client votes "own" when its curve fits its own leaf's leave-one-out
median better than another active leaf's median. A leaf is active with >= 2 congested
clients (FLAG; no algorithm state is used). Templates are uneven as specified: the
own leaf is the median of n - 1 curves, the other leaf the median of n.

| type (gt1): O own leaf / X other leaf / U shared upstream congested | votes | own rate |
|---|---|---|
| O-- own leaf only | 991 | 1.00 |
| OX- both leaves | 6 064 | 1.00 |
| --U shared upstream only | 1 432 | **0.76** (expected 0.5) |
| OXU, O-U, -XU, -X-, --- | 5 409 | 0.98–1.00 |

- **eps (M)** = wrong-vote rate on O-- and OX- = 26 / 7 055 = **0.0037**. Wrong votes
  are not persistent: lag-1 correlation within a sequence 0.07 (raw 0.11). 1 sequence
  has 2 wrong votes in a row, against 0.09 expected. 7 of the 26 wrong votes come from
  one client (J1 hierjit20 r2, b2). By family 0.98–1.00, by AQM 0.99–1.00, by bitrate
  class 0.99–1.00.
- **Shared upstream only (--U)** is not a coin flip: own rate 0.76 overall.
  - By family: J1 random phase 1.00, C1 0.86, M6 indep 0.83–0.84, K6 0.82, K1 0.77,
    J1 jitter 0.58–0.68, J1 same phase 0.10.
  - By AQM: red 0.91, codel 0.87, pie 0.79, pfifo 0.69.
  - Bitrate classes 0.74–0.79.

  So in events where only the upstream has a standing queue, the curves still carry
  leaf-specific structure (leaf queues below the GT1 threshold, own keyframes). In J1
  same phase they carry the opposite: the clients prefer the other leaf. The uneven
  template sizes (2 vs 3 curves) also enter here.

## B2: votes between the stored halves (h3 on ECG intervals, equal-size templates)

Both half templates are medians of c = min(own half − 1, other half) curves, drawn
with a fixed seed. Halves stay as stored, and the storing event gives no votes. All
one-leaf groups with votes are 4-member groups on the base topology, so c = 1:
one curve against one curve.

| | votes | own rate | events: all voters own / expected 0.5^n | lag-1 within member, centred / raw |
|---|---|---|---|---|
| one leaf (153 groups) | 6 513 | **0.54** | 0.22 / 0.09 | 0.03 / 0.20 |
| mixed, halves = leaf boundary (54) | 480 | 0.98 | 0.96 / 0.13 | −0.06 / 0.16 |
| mixed, halves not boundary (9) | 565 | 0.53 | 0.33 / 0.24 | 0.09 / 0.20 |

**One-leaf votes are systematic, not coin flips.**

- **Members:** a member's own rate across events (members with >= 10 votes) has p10 /
  p50 / p90 0.28 / 0.50 / 0.80. 34 % of members lie outside [0.3, 0.7], against 10 %
  expected for fair coins. Some members side with their half in most events, others
  against it. That is why the raw lag-1 (0.20) is high while the centred one (0.03) is
  not: the persistence is a per-member bias, not an event-to-event memory.
- **Within an event:** all voters vote own in 22 % of events, 2.4 times 0.5^n. Part of
  this is by construction. With 2 + 2 halves and c = 1, members i and j of a half both
  vote own when their curves are close to each other, so their votes share one
  distance. 0.5^n is not the right null for votes inside one event.
- **What drives it: keyframe phase.**
  - The base-topology clients have keyframe phases 0 / 250 / 500 / 750 ms
    (`phase_ms` in the topology; access links have no delay or jitter, so access delay
    is equal).
  - When a member's half partner is farther in phase than both members of the other
    half, it votes own 0.68; otherwise 0.42.
  - The sharpest case is equal bitrates: bw8 (all 8 000 kb/s) 0.36 and bw1 (all
    1 000 kb/s) 0.67, depending only on how the stored halves pair the phases.
  - Bitrate is confounded with phase in the mixed-rate runs: own rate by stored rate
    pairing ranges 0.29–0.61, and members whose partner is closer in rate vote own
    only 0.37. I cannot separate a bitrate effect from the phase effect with these
    runs.
- By bitrate class: <= 1000 0.57, 2500 0.55, >= 5000 0.50.

**Mixed groups.** With the right stored halves the votes are near-certain (own 0.98,
all-own 0.96). With wrong halves they are close to 0.5 (0.53), as expected for fixed
halves.

## B3: sequential test on the B2 votes (offline)

| eps | one leaf (153): one queue / **two queues (wrong)** / undecided | mixed, right halves (54): **one queue (wrong)** / two / undecided | mixed, wrong halves (9): one / two / undecided | events to decision p50 / p90 (one leaf) |
|---|---|---|---|---|
| B1 (M) = 0.0037 | 119 / **4** / 30 | **0** / 11 / 43 | 6 / 0 / 3 | 1 / 4 |
| 0.05 | 105 / **8** / 40 | **0** / 11 / 43 | 5 / 0 / 4 | 2 / 6 |
| 0.10 | 90 / **11** / 52 | **0** / 11 / 43 | 5 / 0 / 4 | 4 / 8 |
| 0.20 | 68 / **16** / 69 | **0** / 6 / 48 | 2 / 0 / 7 | 6 / 13 |

- One-leaf groups wrongly called "two queues": 2.6 % at eps from B1, 5 %, 7 % and 10 %
  at 0.05 / 0.10 / 0.20.
- Mixed groups with the right halves are never called "one queue", but 43 of 54 stay
  undecided. h3 itself splits these groups within 1–2 events, so few votes accumulate
  (decided ones take 3–4 events).
- Mixed groups with wrong halves drift to "one queue" in 5–6 of 9: the expected
  weakness of fixed halves.
- The test adds votes inside an event as independent. The within-event dependence
  above makes that optimistic.

## Reading against the brief

- **B2 one-leaf votes are off 0.5 per member and persistent per member.** The votes
  inherit the clients' systematic differences, and the property that drives it here
  is the keyframe phase (bitrate confounded, access delay equal). Per the brief I stop
  here. The B3 wrong "two queues" rate of 2.6–10 % is reported, but it rests on votes
  that are not fair coins.
- **B1 between true leaves** behaves as a near-certain vote where a leaf queue is
  congested (eps 0.0037, no persistence). Where only the shared upstream is congested
  it is not a coin flip (0.76, and 0.10 with aligned phases).
- **Part A:** by the brief's definition the 0.09–0.10 floor is a truth artefact for all
  three methods (96–100 % of same-leaf errors are physically right). The second truth
  is too lenient here to say more; see the caveat above.

## Limitations

- B1 / B2 run on ECG intervals only; Part A covers both timings.
- J1 has 2 runs per type, K1 / K6 / C1 one per AQM.
- All one-leaf B2 groups are 4-member base-topology groups (c = 1). Larger one-leaf
  groups never had stored halves with voters.
- Keyframe phase is the only per-client property I could vary in these runs; access
  delay is equal everywhere on the base topology.
