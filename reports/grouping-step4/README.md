# Step 4: the half test (variant h) on top of Step 3 variant c (2026-11-13)

Read-only, development set (K*, C1, M*, J1; G0 for negatives), single-queue AQMs
(pfifo, pie, red, codel), N1–N5 not opened, no ECG engine change. Code:
`scripts/grouping_step4.py` (constants and tags in its docstring); `grouping_step2.events_of`
got an `ecg_intervals` switch for (f). Run on `.runs/2026-11-10_1946_v2`:

```
python3 scripts/grouping_step4.py run    .runs/2026-11-10_1946_v2 reports/grouping-step4/step4-rows.jsonl    # then gzip
python3 scripts/grouping_step4.py run-f  .runs/2026-11-10_1946_v2 reports/grouping-step4/step4f-rows.jsonl   # then gzip
python3 scripts/grouping_step4.py sum    reports/grouping-step4/step4-rows.jsonl.gz reports/grouping-step4/step4f-rows.jsonl.gz
python3 scripts/grouping_step4.py plots  .runs/2026-11-10_1946_v2 reports/grouping-step4/step4-rows.jsonl.gz reports/grouping-step4
```

Files: `step4-rows.jsonl.gz` (c1–c3, h1–h3, ECG views, late-joiner replays, E and S
trajectories), `step4f-rows.jsonl.gz`, `step4-summary.md` (all tables (a)–(f)),
`step4-traj1..6.png` (E top row, S bottom row, h1 / h2 / h3; base M1 burstcap, split K1
hier, depth K6, J1 hierjit20, M6 indepfast, G0 calmuneven). 152 runs (128 with
windows, 24 G0), 3791 events.

Constants as Step 3, plus HALF_MIN 4 (P) and these FLAG choices of mine: n_eff of an
S increment = n_eff of the member's residual against its own half; at a split, members
with S = 0 outside the stored halves go to the larger child (none happened); S uses
the state at the start of the event and the split is checked after the evidence
update; "correct group" in (b) = every group the client is a member of holds only its
leaf; reliability (d) correct = the client's leaf is the group's majority leaf (ties
wrong); time bins of (b); close time = event interval end; late joiner = first client
of a leaf (>= 3 clients) by name, released when the rest are members of one common
group.

## Stop condition of the brief: one-leaf and mixed groups overlap in (c)

The brief says: if one-leaf and mixed groups overlap in (c), stop and say so. They do.

| h3 | groups | tested | split | events creation → split p50 / p90 | split = leaf boundary |
|---|---|---|---|---|---|
| one leaf (over its life) | 205 | 124 | **26 (21 % of tested)** | 4 / 7 | 0 |
| mixed | 79 | 43 | 31 (72 % of tested) | 2 / 58 | 27 |

- A false split rate of 21 % of tested one-leaf groups is not "near α". The false
  splits come 1–3 events after the halves are stored.
- All 26 are on the single-queue base topology (K2, M1–M6 non-indep): 4 clients at
  1000 / 2500 / 2500 / 5000 kb/s. The split differs from run to run (a+b | c+d,
  b+d | a+c, a+d | b+c), so it is not a stable bitrate split.
- Per-event S increments (h3):

  | group | p1 / p10 / p50 / p90 / p99 (nats) | share with abs. value ≥ b/3 |
  |---|---|---|
  | one leaf | −49 / −17 / 0.4 / 20 / 72 | 0.83 |
  | mixed | −1952 / −326 / −6 / 310 / 710 | 0.97 |

  The mixed tails are 15 times wider, but the central parts overlap. The typical
  one-leaf increment (±20 nats) is three times b (6.5–6.8). Two or three same-sign
  increments are enough to cross ±b.
- Why the one-leaf increments are this large, as far as I can see. These are
  observations, not proposed rules.
  1. With 4 members the halves are 2 + 2. The leave-one-out template of the tested
     member's own half is a single other client's curve, while the other half is a
     median of 2. The two sides are not equally noisy.
  2. n_eff (~100 per event) multiplies any small, systematic per-client difference
     into tens of nats, as in Step 1c.
- The test also freezes. 96 of 124 tested one-leaf groups (and 10 of 43 mixed)
  reached a sign pattern with fewer than 2 members on one side. After that the brief's
  rule ("both halves need >= 2 congested members") skips the group forever (flat S
  lines in `step4-traj1.png`). In a 4-member group one test event is usually enough
  to get there. That freeze is the reason the false-split rate is not higher; it is
  not a property of the test.
- 103 of 284 groups never had 4 congested members and were never tested. Their
  memberships are false at declaration 0.03 and at some close 0.10 (h3).

Per the brief I add no rule to separate them. The other tables below were requested
in the same brief, so I report them.

## (a) Step 3 table, c / h / ECG

False-membership rate over all positives (declared / at some close; n memberships).
ECG with the same definitions on its own nodes (missing in Step 3, now added):

| | c1 | c2 | c3 | h1 | h2 | h3 | ECG |
|---|---|---|---|---|---|---|---|
| declared | 0.30 | 0.20 | 0.18 | 0.22 | 0.14 | **0.10** | 0.09 |
| at some close | 0.41 | 0.30 | 0.28 | 0.31 | 0.25 | **0.21** | 0.14 |
| n | 914 | 731 | 702 | 1230 | 1021 | 895 | 800 |
| wrong lasted, events p50 / p90 | 3 / 12 | 4 / 16 | 3 / 12 | 2 / 5 | 1 / 5 | 2 / 7 | |

The half test roughly halves the declared rate and the duration of wrong memberships
(p90 12 → 7 events). It is still 10–20 times α and not below ECG. Single-group
families: 0 wrong in every variant. h has more memberships there (M1 112 → 160)
because a false split ends the parent's memberships and starts the children's.

Pair precision at the last event / pooled over closes (c3 / h3 / ECG):

| family | c3 | h3 | ECG |
|---|---|---|---|
| K1 | 1.00 / 0.95 | 1.00 / 0.98 | 1.00 / 0.94 |
| K6 | 1.00 / 0.92 | 1.00 / 0.98 | 1.00 / 0.60 |
| C1 | 0.60 / 0.72 | 0.65 / 0.77 (R 0.81) | 1.00 / 1.00 (cov 0.21) |
| J1 jit5 / jit10 / jit20 | 1.00 / 0.70, 0.81, 0.91 | 1.00 / 0.95, 0.95, 0.94 | 1.00 / 0.92, 0.75, 0.92 |
| J1 same / random phase | 1.00 / 0.89, 0.97 | 1.00 / 0.96, 1.00 | 1.00 / 0.85, 0.86 |
| M6 indepfast / indepslow | 1.00 / 0.90, 0.98 | 1.00 / 0.96, 0.98 | 1.00 / 0.76, 0.49 |
| single-group families | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |

Events to membership p50: h equals c (m1 1, m2 2, m3 3–4; ECG 2–5).

Mixed groups (h3) separate or split in p50 2 events in K1 / J1 / M6 indep
(c3: 6–12 in K1 / J1). Their splits are on the leaf boundary in 27 of 31.

sub-ctrl: never above 0.

Negatives, topology truth: h3 203 right / 0 wrong (c3 221 / 0, h1 217 / 4, h2 191 / 3,
ECG 25 / 0).

Cost (h): template comparisons per event p50 10, p90 21 (c: 6 / 21); state (E and S)
p90 12, max 32 entries; at most 5 groups.

Per-AQM rows, events to membership per family, and the mixed-group table are in
`step4-summary.md`.

## (b) Accuracy by events seen (all positives, h3; `step4-summary.md` has all variants and ECG)

| events of the client's leaf seen | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | more |
|---|---|---|---|---|---|---|---|---|---|
| member | 0.01 | 0.03 | 0.24 | 0.81 | 0.93 | 0.92 | 0.97 | 0.98 | 0.98 |
| correct (of members) | 0.83 | 1.00 | 0.89 | 0.96 | 0.97 | 0.98 | 0.97 | 0.97 | 0.97 |
| pair P | 0.67 | 1.00 | 0.87 | 0.96 | 0.98 | 0.98 | 0.98 | 0.97 | 0.97 |
| multi-group families: correct / pair P | 0.83 / 0.67 | 1.00 / 1.00 | 0.89 / 0.87 | 0.92 / 0.90 | 0.92 / 0.93 | 0.93 / 0.94 | 0.92 / 0.91 | 0.90 / 0.89 | 0.96 / 0.96 |
| c3 multi-group: correct / pair P | 0.83 / 0.67 | 0.89 / 0.83 | 0.41 / 0.53 | 0.58 / 0.61 | 0.66 / 0.74 | 0.79 / 0.78 | 0.72 / 0.71 | 0.65 / 0.66 | 0.92 / 0.90 |
| ECG multi-group: correct / pair P | 0.40 / 0.43 | 0.42 / 0.48 | 0.30 / 0.47 | 0.43 / 0.53 | 0.29 / 0.46 | 0.38 / 0.51 | 0.54 / 0.57 | 0.48 / 0.55 | 0.88 / 0.84 |

From the third event on, h3 is at 0.89–0.98 correct, while c3 on the multi-group
families is at 0.41–0.79. That is "near 1 from the third event" only for the
single-group families. On the multi-group families it stays at 0.90–0.93 between
events 4 and 8. By seconds since the client's first event, h3 multi-group is at 0.98
in 0–10 s (few members), 0.82 in 10–30 s, 0.91 in 30–60 s, then 0.96–0.98. Tables by
seconds since the run start are in the summary.

## (c) Half test behaviour

Above (stop condition). S trajectories are in the bottom row of `step4-traj1..6.png`:

- base (traj1): one test, then frozen with one member positive and three negative.
- K1 split (traj2): the mixed group is split in its first tested event, on the leaf
  boundary.
- J1 jit20 (traj4): a correct split at event 2; a later one-leaf group frozen with all
  three S below −b and no positive side.

## (d) Confidence score p = 1 / (1 + exp(−E))

Positives, every (client, group) entry with E > 0 at every close, share correct:

| p bin | c1 | c2 | c3 | h1 | h2 | h3 |
|---|---|---|---|---|---|---|
| 0.5–0.7 | 0.23 (40) | 0.33 (36) | 0.27 (41) | 0.74 (66) | 0.79 (109) | 0.85 (162) |
| 0.7–0.9 | 0.69 | 0.39 | 0.86 | 0.62 | 0.87 | 0.88 |
| 0.9–0.99 | 0.63 | 0.82 | 0.75 | 0.80 | 0.88 | 0.81 |
| 0.99–0.999 | 0.86 | 0.80 | 0.83 | 0.86 | 0.84 | 0.94 |
| > 0.999 | 0.93 (18 573) | 0.94 | 0.94 | 0.98 (19 668) | 0.98 | 0.98 (17 717) |

Not close to the diagonal and not even monotone: the bins from 0.7 to 0.999 are
correct 0.62–0.94, and the top bin (> 0.999, holding ~85 % of all entries) is correct
0.93–0.98, i.e. 20–70 times more errors than p says. The low bins of h are
under-confident (0.5–0.7 is correct 0.74–0.85). **p can be reported as a score only,
not as a probability.** E reaches thousands of nats (n_eff × ln ratio over many
events), so almost every entry sits in the top bin.

## (e) Late joiner (replay)

150 cases (leaves with >= 3 clients, positives). In h3, 5 were never released: the
rest of the leaf never became members of one group.

| | c3 | h3 |
|---|---|---|
| its group the only one (98): joined, events p50 / p90, seconds p50 / p90, ever wrong | 96, 4 / 4, 52 / 108 s, 0 | 96, 4 / 4, 52 / 108 s, 0 |
| another group active (47): joined, events, seconds, ever wrong | 47, 3 / 12, 49 / 207 s, 22 | 47, 2 / 3, 44 / 151 s, 19 |

When no other group is active, the late joiner needs exactly the m-event clip ramp:
4 events at m = 3, never wrong. With another group active, the half test shortens
the tail (p90 12 → 3 events), but 19–22 of 47 joiners are a member of a wrong group
at some point (h1: 44 of 48). Other m in the summary.

## (f) Without the oracle: ECG event intervals, h3

windows.json gives 3547 events, the ECG intervals (t0 −1 s, +2 s) give 5141. Lost: 57
windows events with no overlapping ECG event. Merged: 796 ECG events overlap two or
more windows events.

| | windows.json | ECG intervals |
|---|---|---|
| last-event pair P: all families | 1.00 except C1 0.65 | 1.00 except K3 0.75 |
| pooled-closes P, multi-group families | 0.77–1.00 | 0.89–0.99 (C1 0.98) |
| false memberships declared / close | K1 0.21 / 0.44, K6 0.15 / 0.46, J1 0.00–0.38 / 0.00–0.71, M6 indep 0.09–0.34 / 0.23–0.70 | K1 0.23 / 0.52, K6 0.37 / 0.89, J1 0.08–0.36 / 0.31–0.72, M6 indep 0.23–0.24 / 0.50–0.70, K3 0.25 / 0.25 |
| events to membership p50 | 2–6 | 0–4 |

Headline numbers are of the same order. The oracle timing does not carry the result,
but false memberships get somewhat worse on K6 and M6 indepslow, and K3 gets one
false pair. C1 gets better, because ECG events are short and do not pull in the
neighbouring long burst.

## (g) C1: the group that never separates

Not the known limit. In all three C1 runs (27 events each) the leaves congest apart
in 18 events: 9 a only and 9 b only, ground truth. The other 9 are upstream events
(r1->r2: both leaves share one queue). Order: `babaaabbaaUbaUaUUUbbUUbbUUa`.

What goes wrong:
1. The long bursts and the ±1 s event margin pull the other leaf into the event.
   Event 0 is a b-only window, but all 6 clients are congested in it, so a merged
   group is born at the first event. The same happens at event 26 (pfifo): a new
   all-six group at E = b/3, still a candidate at the end.
2. Upstream events (U, 9 of the last 17) are one queue for both leaves. The a and b
   templates are the same curve there, so the cross-group evidence (not clipped,
   because the alternative is another group) is noise times n_eff. That is how b3
   ends up a member of the a group (pfifo) with E 19, and how red ends with 4 mixed
   groups. Under the same-leaf truth this is wrong. Under the topology truth (shared
   r1->r2 queue) it is right; that is the parked "truth by shared congested egress"
   item.
3. The half test missed it:
   - pfifo: the a group with b3 is 3 + 1, so one half never has 2 congested members
     and it is never tested;
   - red: halves were stored at event 17, a U event with no leaf structure, so the
     stored split was {a2, a3, b1} | {a1, b2, b3} and the group was split on it
     (event 20);
   - pie: split at event 19 on the leaf boundary ({b2, b3} | {a1, a2, a3}).

## Limitations

- No decay; event intervals from windows.json except (f).
- Families K1 / K6 / C1 have 1 run per AQM, J1 2 per type.
- Membership counts in h include children after a split (a split ends and restarts
  memberships).
- S trajectories were first recorded after a split removed the parent; fixed before
  the final run (plots only, no number changed).
