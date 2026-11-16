# Grouping diagnostics on the v3 runs (2026-11-15)

Campaign `.runs/2026-11-14_1818_v3`, existing runs only. Measurement only: the detector, ECG v1.2, h3 (step 4 replay, m = 3), GT1 and the step 4–7 scoring helpers are called unchanged. Every value is rep 1 / rep 2.

Files in this folder:
- Driver `diag.py`, which writes `rows.jsonl`.
- `report.py`, which turns `rows.jsonl` into `tables.md` (the full tables; this file quotes them).

Onset source: v2-owd. ECG events use the interval [t0 − 1 s, t0 + 2 s], as in step 7.

## Q1. Is the truth right on the three-level tree (C9 H-DEPTH)? Cause found: it is not a truth problem.

**Method.** The queue-log truth ("qlog") applies gt1's CoDel rule to the per-packet router trace (GT-Q logging):
- sojourn ≥ 5 ms to enter, ≥ 2.5 ms to stay, and the queue never empty in between;
- the episode must last ≥ 150 ms; episodes closer than 150 ms are merged;
- fq_codel: the rule runs per client sub-queue (M).

All C9 runs and the C7 pfifo control are GT-Q-valid.

**a. gt1 against the queue log.** For every ECG event and each of the 7 egresses, I compared the two truths.
- **pfifo, codel and C7:** the generous and the strict rule both disagree on **0.00** of event × egress cases, at the root, mid and leaf levels alike. Episode counts are identical under pfifo (C9 pfifo r1: 6 / 6 / 12 / 7 / 12 / 6 / 6 on both); under codel they differ by at most two per egress.
- **The mid layer is visible to gt1.** X / Y are congested in 12–15 events per rep, and the queue log says the same.
- **fq_codel**, strict rule, leaf level: 0.11 / 0.07 of cases are "gt1 only". gt1 sums the backlog of all sub-queues, while qlog looks at the clients' own sub-queues.

**b. The ~1100 votes typed `---`.** These are step 5 B1 votes: no own-leaf, other-leaf or shared-upstream congestion. pfifo has 1156 / 1187 of them, codel 1064 / 1154.
- **Where they come from.** Votes arise in 41–47 events per run, and every one of those events falls during a stimulus. gt1 finds an empty congested set in 0–1 of them, and so does qlog.
- **Split of the votes:**
  - ≈ 0.36 have the voter's own mid or the other leaf's mid congested. The step 5 type has no slot for an unshared mid router, so these are a typing gap.
  - ≈ 0.60 have the congested egress elsewhere in the tree (another leaf or the other mid), not on either voter's path. The voters were counted as congested by the event partition while their own path egresses were not, by either truth.
  - 0–48 votes have nothing congested at all.
- So `---` does not mean "no egress congested". It means the step 5 type has no slot for those egresses. It says nothing about gt1.

**c. Strict false memberships, gt1 against qlog.**

| | C9 pfifo | C9 codel | C9 fq_codel | C7 pfifo (control) |
|---|---|---|---|---|
| h3 | 61 / 75 vs **61 / 75** | 76 / 70 vs **76 / 70** | 12 / 22 vs 13 / 26 | 0 / 0 vs 0 / 0 |
| ECG | 5 / 25 vs **5 / 25** | 13 / 16 vs **13 / 16** | 6 / 11 vs 6 / 11 | 0 / 0 vs 0 / 0 |

- The errors do not vanish under the queue-log truth. The same-leaf counts are h3 99 / 142 and ECG 5 / 43 under pfifo, unchanged.

**d. Where the methods merge** (wrong pair × close; qlog strict; C9 pfifo; codel in brackets).
- **h3, siblings.** 62 % / 61 % of h3's wrong pair-closes are siblings, i.e. leaves under the same mid router (codel 65 % / 60 %).
- **h3, shared egress congested.** In 41 % / 45 % of them the pair's shared egress (their mid or the root) is congested in that event (codel 35 % / 37 %). These merges are defensible per event but wrong under the leaf truth.
- **h3, no congestion on either path.** 32 % / 34 % sit in closes with no congestion on either client's path (codel 40 % / 40 %). These are memberships carried over from earlier events.
- **ECG** is not reliable here: the two reps disagree on the level. pfifo r1 has 100 % siblings and r2 67 % across mids; codel is the reverse.

**Reading.**
- C9's errors are real by both truths.
- h3 mostly merges sibling leaves under one mid router, and it does so in events where that mid or the root is congested.
- Why the merge survives later sibling-only events was not traced.

## Q2. Why is rep 1 worse? Cause partly found: event order, and which event comes last.

**a. Event order.** The first ten ECG events per rep are listed in `tables.md` Q2a.
- **Starts.** Rep 1 starts with combined or partial events:
  - C7: a+b@2 events holding 2 a-clients, then 4 b;
  - C9: D, then A+C as partial or solo events;
  - C13: b split into 3 + 1.

  Rep 2 starts with whole-leaf events: C7 b4, b4; C13 a4 b4, then b4, then a4.
- **Ends.** Every rep-1 run (9 / 9 cells) ends with a shared-upstream stimulus (C7 / C13 `up`, C9 `root`). Every rep-2 run ends with a single leaf (`b`, `A`).
  - h3's "last" precision is read at the close right after that last event.
  - The per-close pooled precision is close between reps: C7 pfifo 0.94 / 0.89, codel 0.84 / 0.93, pie 0.96 / 0.90; C13 pfifo 0.88 / 0.86. C13 codel (0.62 / 0.94) is the exception.

**b. Time to first membership, counted in own-leaf events.**
- **ECG** needs more of its own leaf's events in rep 1 (Q2b): C13 3 / 1; C9 2–6 / 0.5–1.5; C7 2.5–4.5 / 2.5 (fq_codel 4 / 6). Its membership-event count is 4–6 / 2 in C7 and C13.
- **h3** is level: C7 2 / 2, C13 1.5–3 / 1.5–2.

**c. Group birth.**
- **h3:** the first group is born mixed in both reps of every cell, and the number of mixed-born groups is similar (C7 pfifo 2 / 4, C9 pfifo 22 / 20).
- **ECG:** no node is born mixed in C7 or C13 in either rep; C9 has 0–1.
- So "groups born mixed" does not separate rep 1 from rep 2.

**d. h3 replayed with the other rep's stimulus order** (same events, permuted offline; last P):

| cell | rep 1 as run | rep 1 events, rep 2 order | rep 2 as run | rep 2 events, rep 1 order |
|---|---|---|---|---|
| C13 pfifo | 0.50 | **1.00** | 1.00 | **0.42** |
| C13 codel | 0.60 | 0.80 | 1.00 (R 1.00, cov 0.78) | 1.00 (R 0.43, cov 0.42) |
| C7 codel | 0.58 | 1.00 | 1.00 | 1.00 |
| C7 pfifo | 0.77 | 0.62 | 1.00 | 1.00 |
| C7 pie | 1.00 | 1.00 | 1.00 | 0.75 |
| C9 pfifo / codel | 0.28 / 0.37 | 0.44 / 0.21 | 0.24 / 0.27 | 0.40 / 0.39 |

- In C13 the failure follows the order, not the events.
- In C7 the effect is mixed. In C9, every order is bad.
- An ECG permutation cannot be done offline. ECG consumes the onset stream and the per-client sent-rate observations on the run's time axis, with decay (10 s period, λ τ 60 s). Re-ordering would mean re-timing all inputs, which amounts to new runs.

**Reading.**
- Rep 1's lower h3 final precision comes largely from the run ending on an upstream event, where h3 groups briefly absorb the other leaf (see Q3a), plus a real order sensitivity (C13).
- ECG's slower membership in rep 1 goes with partial early events. That is shown for one seed pair only.
- Two seeds cannot measure order sensitivity. **New runs:** the same cell with controlled stimulus orders (first event single-leaf vs upstream; last event single-leaf vs upstream), several seeds each.

## Q3. What goes wrong on long events (C13 L-LONG)? Cause found for ECG and h3; coverage partly found.

**a. Failing runs.**
- **ECG rep 2** (P 0.43 under both AQMs) has one leaf node holding all 8 clients (a 4 + b 4).
  - The node was created by the run's first event: an upstream (`up`) stimulus at t 15 with all 8 clients (node `created_t` 16.32).
  - After that, b-only and a-only events alternated: b at t 36.7, a at 60.6, b at 82.2, a at 124.9. Each confirmed one leaf into the same node, and from close #4 on all 8 were members until the end.
  - No later event moved it toward the truth.
- **ECG rep 1** (P 1.00) starts with a b event, so b gets its own node. The a node forms later, at t 312.
- **h3 rep 1** (P 0.50–0.60): the wrong groups are wrong only at the last close (t 373.5), which is an `up` event. The groups were pure before it:
  - codel: {b 2} → {b 2, a 1}, {a 2} → {a 2, b 1};
  - pfifo: {b 4} → {b 4, a 3}.

  In rep 2, h3's group 0 also took one a-client at the `up` events (t 164.9 and 227.5) and dropped it at the next single-leaf event.

**b. Long events give one onset.** Per stimulus window, 10 s or 30 s:
- one ECG event (12–14 per run; one window split into 3 + 1);
- 1.0 onset per expected client, and 0 onsets from other clients;
- both leaves in one ECG event only in `up` windows (4–5 per run).

So a 30 s event carries the same evidence as a 10 s one, and the whole run has 12–14 events to correct an early wrong node.

**c. Coverage 0.58 in rep 1.** One client is undecided; this gives 0.58 instead of 0.78.
- **codel b4:** L 4.25 < A in node 1. It was a member at close #3, dropped at #4 (an a event) and never came back in 9 more closes.
- **pfifo b3:** L 0, no node, although it had 8 onsets and took part in 8 events.
- Why b3 never gained support was not found. It would need ECG's internal evidence trace (`evidence.jsonl`).

**New runs:** whether more events per run would let ECG split a node born from an upstream event (longer runs, or more 10 s events between the long ones).

## Q4. fq_codel under the per-flow truth (C7, C9, C10, C12). Cause partly found.

**Which truth Part 4 used.** The fq_codel rows were scored against the **static same-leaf truth**: ECG `pairwise` uses `same_access(truth_leaf)`, and h3 uses `pairs_leaf`. The "strict per-event" columns used gt1, which for fq_codel is the egress's summed backlog over all sub-queues, so no single client's delay. ECG's `truth_source` string names the per-client GT1 queues, but only for its event truth, not for the pairwise scores.

**Per-flow truth (M).**
- In each ECG event, the constrained set is the clients behind the stimulated egress whose **own sub-queue** has a queue-log episode (the gt1 CoDel rule from Q1) overlapping [t0 − 1, t0 + 2].
- A pair is "same" when the two are co-constrained in ≥ half of the events in which either one is constrained.
- Never-constrained clients are correct when left out; their pairs count only if they were grouped.
- Script: `diag.py rows4`, output `rows4.jsonl`.

**How many of the clients behind the egress are constrained** (median per event; strict ≥ half of the interval in brackets):
- **Leaf stimulus:** C7 2 of 4; C10 2–3 of 4; C9 1 of 4.
- **Upstream stimulus:** C7 / C10 4–5 of 8; C9 root 4–5 of 16.
- **C12:** shared 3 of 4, private 1 of 1.
- **Strict median:** 1–2.
- **No event has every client behind the egress constrained,** except 0–13 events per run. These are the C12 private links and a few shared events.
- **ECG events** have a median of 1 member. 0.60–0.91 of the members were constrained.

**Scores** (P / R / cov, rep 1 ; rep 2):

| cell | ECG same-leaf | ECG per-flow | h3 same-leaf | h3 per-flow | wrong memberships, ECG leaf → flow | h3 leaf → flow |
|---|---|---|---|---|---|---|
| C7 | 1.00/.50/.42 ; 1.00/.50/.28 | 1.00/.17/.54 ; 1.00/.33/.67 | 0/0/.78 ; 0/0/.78 | **.75**/.43/1.00 ; **.25**/.33/1.00 | 9→9 ; 13→12 | 18→12 ; 10→10 |
| C10 | .40/1.00/.28 ; .60/.43/.58 | **1.00**/1.00/1.00 ; .60/.43/.75 | .25/.25/.28 ; 0/0/.78 | **1.00**/.40/1.00 ; **.75**/.33/1.00 | 7→1 ; 3→2 | 4→5 ; 11→4 |
| C9 | 0/0/.26 ; .09/.50/.26 | 0/–/.40 ; .27/1.00/.55 | .12/.60/.57 ; .16/.80/.49 | 0/–/.86 ; .16/1.00/1.00 | 20→36 ; 29→37 | 34→46 ; 41→41 |
| C12 | 1.00/1.00/.60 ; 1.00/1.00/.30 | .50/1.00/1.00 ; 1.00/1.00/.50 | –/–/0 ; 1.00/1.00/.10 | –/–/0 ; 1.00/1.00/.17 | 0→3 ; 1→1 | 0→0 ; 0→1 |

**Reading.**
- **Part of the same-leaf failure is the truth.**
  - Under fq_codel, only about half of the clients behind a stimulated egress are actually constrained in an event (1 of 4 in C9).
  - h3's precision rises in C7 (0 → 0.75 / 0.25) and C10 (0.25 / 0 → 1.00 / 0.75). ECG's rises in C10 rep 1 (0.40 → 1.00).
- **The rest is not.**
  - Recall stays low (ECG 0.17–0.33 in C7, h3 0.33–0.43).
  - C9 is no better under the per-flow truth: ECG wrong memberships go 20 → 36 and 29 → 37.
  - The C7 h3 reps disagree (0.75 / 0.25): not reliable.
- **Caveat on the truth itself.** The constrained set changes from event to event, so a stable per-flow group hardly exists. The run-level pair rule (≥ half co-constrained) is a choice (M); a per-event scoring could rank the methods differently.

## Summary

| question | status | deciding numbers | needs new runs |
|---|---|---|---|
| Q1 C9 truth | **found: not a truth problem** | gt1 vs queue-log disagreement 0.00 at every level (pfifo, codel); strict false memberships unchanged (h3 61 / 75, 76 / 70; ECG 5 / 25, 13 / 16); `---` = the step 5 type has no slot for an unshared mid router or an egress off both paths | no. Why h3 keeps sibling merges is not traced (offline is possible) |
| Q2 rep 1 worse | **partly found** | every rep-1 run ends on an upstream event, and h3 "last P" is read there; offline order swap moves C13 h3 P 0.50 ↔ 1.00; ECG needs more own-leaf events in rep 1 (C13 3 / 1) after partial early events | yes: controlled stimulus orders and more seeds (ECG cannot be permuted offline) |
| Q4 fq_codel per-flow | **partly found** | Part 4 = static same-leaf truth; per event only 1–3 of 4 (C9: 1) behind the egress constrained; per-flow truth lifts h3 P in C7 (0 → .75 / .25) and C10 (→ 1.00 / .75), but recall stays .17–.43 and C9 does not improve | no for the re-score; a per-event scoring choice is open |
| Q3 C13 long events | **found (ECG, h3); partly (coverage)** | ECG rep 2: one node of 8 born from the first `up` event, never split by alternating single-leaf events; h3 rep 1: pure groups absorb the other leaf at the final `up` event; 1 onset and 1 ECG event per stimulus whether 10 s or 30 s | yes, for whether more events would split the node; b3's zero support needs the ECG evidence trace, offline |

Constants: the gt1 TARGET / band / INTERVAL (T); the per-client sub-queue union for fq_codel (M); the stimulus-at-t0 window [start − 0.5 s, end + 1 s] (M); the permutation rule (same-cell events in their own order, the rest appended; time slots kept in recorded order because replay4 uses lo / hi only for bookkeeping) (M).
