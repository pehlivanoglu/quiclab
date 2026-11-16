# Synchronized-keyframe mini campaign (2026-11-13/14)

Runs: `.runs/2026-11-13_2238_grp-sync`, pfifo, phase_ms 0 for every client, 2 reps:
base calm065, base burstcap, K1 hier, C1 burstlongsplit, K6 depth. 10 runs in 2 h 10 min
wall, none failed. Staggered comparison: the same scenarios in `.runs/2026-11-10_1946_v2`,
**r1 only** (the old campaign has one rep per cell).

Existing scripts, unchanged:
- `baseline_scores.py ecg` / `detector`;
- `grouping_step4.py run-f` (h3, ECG event intervals);
- `grouping_step5.py run` (B1–B3);
- `grouping_step2.py calm`.

Their rows are in this folder. Two helpers here call them and change nothing:
- `raw_signals.py`: GT1 episodes per egress; v2-owd alarm starts relative to the client's
  own keyframes (FLAG: 200 ms window; 0.20 is the share for starts unrelated to
  keyframes); ECG onset spread per burst.
- `compare.py`: the per-scenario tables in `compare.md`.

## Check A

Spread across all clients, ms (p50 / p90 / max):

| run | scheduled | written to transport | first packet |
|---|---|---|---|
| calm065 r1 | 0.58 / 0.84 / 1.0 | 0.59 / 0.89 / 161 | 0.59 / 0.91 / 161 |
| calm065 r2 | 0.66 / 1.27 / 1.9 | 0.67 / 1.43 / 321 | 0.72 / 1.82 / 321 |

- The scheduled spread is <= 2 ms in every sync run; staggered runs: 750 / 800 ms.
- The written and packet maxima come from one client at a time whose BBR is in
  PROBE_RTT (cwnd cut, send buffer 10–147 kB): about 5 % of keyframes in calm065. That
  is transport state, not the sender schedule.
- In burst runs the written spread reaches ~1 s (sender backlog during bursts). C1 has
  a written p50 of 557 ms because every client is > 50 ms late on 28–45 % of its
  keyframes during the long bursts, in the staggered run too.

## Per scenario (details: `compare.md`)

### base calm065

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| GT1 episodes / min (router->switch) | 2.6 | 6.8 | 5.2 |
| queue peaks >= 5 ms: per min, peak p50 / p90 ms | 644, 9.7 / 20.5 | 532, 12.5 / 41.7 | 540, 12.3 / 38.9 |
| clients behind the queue in one class (step 2b C) | 0.76 | 1.00 | 1.00 |
| v2-owd alarms / client-min; share on a keyframe | 0.52; 0.00 | 0.10; 0.00 | **1.04; 0.60** |

Synchronized keyframes make fewer but about twice as large shared peaks, and 2–2.6
times more GT1 episodes in a calm run. Step 2 groups the clients behind the queue in
every peak. The detector fired on keyframe bursts in sync r2 only (0.56 false alarms
per minute, 60 % of alarm starts within 200 ms of a keyframe); r1 had almost no alarms.

### base burstcap

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| detector v2-owd vs GT1: R / P / FA per min | 0.60 / 1.00 / 0 | 0.26 / 1.00 / 0 | 0.28 / 1.00 / 0 |
| GT1 episodes / min | 6.6 | 15.2 | 14.0 |
| ECG final P / R / cov | 1 / 1 / 0.60 | 1 / 1 / 0.60 | 1 / 1 / 0.60 |
| h3: final P, false memberships, one-leaf false splits | 1.00, 0/4, 0/1 | 1.00, 0/4, 0/1 | 1.00, 0/4, 0/1 |
| B2 one-leaf: own rate; members outside [0.3, 0.7] | 0.48; 0/4 | 0.50; **4/4** | 0.27; **2/4** |
| B3 one-leaf (any eps) | one queue | one queue | one queue |

- The detector recall falls to less than half, but its alarm count is unchanged (3.0–3.2 per
  client-minute, 0.28–0.30 of them on a keyframe, staggered 0.23). GT1 doubled: the
  shared keyframe queues add standing-queue episodes that the detector does not alarm
  on. The recall drop is mostly a larger truth denominator.
- B2 votes stay member-biased with phases equal (one group of 4 per run, 82 votes).

### K1 hier

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| detector R / P / FA per min | 0.50 / 0.99 / 0.06 | 0.20 / 1.00 / 0.02 | 0.19 / 1.00 / 0.00 |
| GT1 / min: r1->r2 \| leaf a \| leaf b | 1.6 \| 7.0 \| 6.5 | **13.1** \| 7.0 \| 8.2 | **14.4** \| 7.4 \| 7.2 |
| ECG final P / R / cov, membership events | 1 / 1 / 0.71, 5 | 1 / 1 / 0.71, 4 | 1 / 1 / 0.71, 2 |
| h3: final P, pooled P, false memberships decl / close | 1.00, 0.94, 11 / 23 of 33 | 1.00, 0.93, 12 / 21 of 34 | 1.00, 0.93, 10 / 16 of 20 |
| B1 own: leaf congested; upstream only | 1.00; 0.68 | 1.00; **0.50** | 1.00; 0.62 |

The shared upstream r1->r2 has 8–9 times more GT1 episodes. Votes in upstream-only
events move to about 0.5. Grouping results are unchanged.

### C1 burstlongsplit

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| detector R / P / FA per min | 0.22 / 0.94 / 0.11 | 0.09 / 0.99 / 0.02 | 0.09 / 0.98 / 0.04 |
| ECG final P / R / cov | 1 / 1 / 0.48 | 1 / 1 / **0.05** | 1 / 1 / 0.48 |
| h3: final P, pooled P, false memberships decl / close | 1.00, 0.98, 1 / 4 of 9 | **0.75, 0.65, 14 / 32 of 39** | 1.00, 0.75, 13 / 27 of 40 |
| B1 own: leaf congested; upstream only | 1.00; 0.87 | 1.00; **0.29** | 1.00; **0.13** |

In upstream-only events, synchronized clients prefer the other leaf's template. h3
builds many more mixed memberships. Under the topology truth these are right (shared
r1->r2 queue); under the same-leaf truth they are wrong.

### K6 depth

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| detector R / P / FA per min | 0.29 / 0.99 / 0.05 | 0.14 / 1.00 / 0.02 | 0.12 / 1.00 / 0.02 |
| GT1 / min: root rr->r0 \| r0->r1 \| r0->r2 | 0.6 \| 1.4 \| 2.2 | **11.2** \| 3.1 \| 5.4 | **13.8** \| 2.5 \| 4.6 |
| ECG final P / R / cov, tree | 1 / 1 / 0.78, ok | 1 / 1 / **0.42, no** | 1 / 1 / 0.78, ok |
| h3: final P, pooled P, false memberships decl / close | 1.00, 0.97, 7 / 17 of 19 | **0.67, 0.44, 72 / 104 of 121** | **0.36, 0.35, 71 / 103 of 121** |
| B1 own: leaf congested; upstream only; eps | 0.99; 0.82; 0.002 | 0.98; 0.65; 0.016 | 0.98; 0.57; 0.019 |

All 8 clients' keyframes meet at the root queue, which now has a standing queue 11–14
times per minute (staggered 0.6). h3 forms groups over the root and keeps merging
leaves. Its precision at the last event drops to 0.36–0.67 in both reps. ECG stays at
P 1.00 but loses coverage and the correct tree in r1.

## Across the five scenarios

1. **Truth changes most.** Synchronized keyframes create real shared queues every GOP:
   2–2.6× more GT1 episodes on single queues, 8–23× more on the shared upstream / root
   egresses (K1, K6). Detector recall against GT1 falls to 40–45 % of the staggered value everywhere, with
   unchanged alarm rates and precision, because the new episodes are short keyframe
   queues it does not alarm on.
2. **Detector on keyframes.** The share of alarm starts within 200 ms of a keyframe is
   0.15–0.30 in burst runs, staggered and sync alike (unrelated: 0.20). In calm065
   sync r2 it is 0.60, with 0.56 false alarms per minute.
3. **Votes between groups.** Where a leaf queue is congested they stay near-certain
   (0.98–1.00; eps 0 on K1 / C1, 0.016–0.019 on K6, 0.0098 pooled). Where only the
   shared queue is congested they move from 0.68–0.87 (staggered) to 0.13–0.65, i.e.
   to 0.5 or below. This is consistent with the reviewer's reading: phase decided those
   votes when the queue was shared.
4. **Votes inside one leaf (B2, base only)** stay member-biased with equal phases (4 / 4
   and 2 / 4 members outside [0.3, 0.7] against 0 / 4 staggered; 4 members per run).
   Phase was not the only property driving them; bitrate (1000 / 2500 / 2500 / 5000)
   is the remaining candidate, untested. B3 called "one queue" in every case.
5. **Grouping.** h3 gets much worse where a shared upstream or root queue now forms
   every GOP (K6 final P 0.36–0.67, C1 pooled P 0.65–0.75). It is unchanged on K1 and
   the base topology. ECG keeps precision 1.00 everywhere but loses coverage and the
   tree in one rep each of C1 / K6.

**Rep 1 vs rep 2:**
- Headline numbers agree within each scenario except:
  - calm065 detector alarms: 0.10 vs 1.04 per client-minute;
  - ECG coverage on C1 (0.05 vs 0.48) and K6 (0.42 vs 0.78; tree no / ok);
  - h3 K6 final P 0.67 vs 0.36;
  - B2 base members outside [0.3, 0.7]: 4 / 4 vs 2 / 4.
- So the base-topology and ECG-coverage findings need more reps.

**Unexpected:**
- The root queue of K6 becomes a standing queue many times per minute with
  synchronized keyframes.
- Upstream-only votes in C1 go well below 0.5.
- The remaining runs were not pointless: every scenario changed something.

## What this cannot tell us

- One AQM (pfifo): no RED, PIE or CoDel, which treat short keyframe queues
  differently.
- Two reps per scenario, staggered side one rep. Rep-to-rep differences above are as
  large as some sync-stag differences.
- The B2 one-leaf test has one 4-client group per run (8 members in all). Bitrate vs
  any other per-client property cannot be separated, and access delays are equal.
- Five scenarios on three topologies: no uneven, tree8-calm, access or jitter (J1)
  topology with sync phases, and no other calm or negative types than calm065.
- The same-leaf truth calls the new shared-queue groups wrong. Their physical
  correctness (topology truth, as in Step 5 Part A) is not scored here.
- No tuning; these are the frozen v1.2 / h3 / v2 settings.

## Addendum: B2 / B3 on the mixed groups (K1, C1, K6)

Mixed = the group's members span two leaves (same-leaf truth); halves = boundary when
the stored halves are exactly the two leaves. B3 at eps measured here (0.0098); wrong
call for a mixed group = "one queue".

| scenario | run | mixed groups | B2 own, halves = boundary (votes) | B2 own, wrong halves (votes) | B3: boundary groups one / two / undecided | B3: wrong-halves groups one / two / undecided |
|---|---|---|---|---|---|---|
| K1 | stag r1 | 4 | 1.00 (22) | - | 0 / 1 / 2 | - |
| K1 | sync r1 | 4 | 0.92 (36) | - | 0 / 0 / 4 | - |
| K1 | sync r2 | 3 | 0.84 (37) | - | 1 / 0 / 1 | - |
| C1 | stag r1 | 2 | 1.00 (12) | - | 0 / 0 / 2 | - |
| C1 | sync r1 | 7 | 0.56 (61) | 0.62 (8) | 3 / 0 / 3 | 1 / 0 / 0 |
| C1 | sync r2 | 6 | 0.77 (65) | - | 3 / 1 / 1 | - |
| K6 | stag r1 | 5 | 1.00 (14) | 1.00 (10) | 0 / 0 / 2 | 0 / 0 / 2 |
| K6 | sync r1 | 18 | 0.87 (270) | 0.30 (272) | 2 / 3 / 8 | 2 / 0 / 2 |
| K6 | sync r2 | 19 | 0.83 (212) | 0.59 (166) | 1 / 3 / 7 | 4 / 0 / 1 |

With synchronized keyframes, two leaves that share a congested upstream / root queue
every GOP vote less clearly for their own half (0.56–0.92 instead of 1.00). B3 calls
some correctly halved mixed groups "one queue": C1 3 of 6, K6 1–2 of 11–13. These are
wrong by the same-leaf truth; physically the leaves do share a congested queue.
