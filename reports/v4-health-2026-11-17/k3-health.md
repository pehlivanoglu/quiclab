# K3 health check after the campaign (2026-11-19 05:10, read only)

K3: 202 planned, **194 ran and finished** (all have v3-checks.json), **8 never ran**. v4-checks: no failure.

## 8 runs never ran: planner name bug

`v4-I1-{calm,hhier}-ip1.2-pfifo-r1/r2`, `v4-I1-sburst-ip1.2-{pfifo,codel}-r1/r2` stopped at start:
`Error: invalid run id 'v4-I1-calm-ip1.2-pfifo-r1': must match ^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$`
(quiclab/runtime.py; the cell name `ip{r:g}` in scripts/v4_suite.py:772-774 gives "ip1.2"). No folder, no data.
Valset (frozen) lists them as unfinished: 2 main, 4 robustness, 2 excluded. Nothing changed; the user decides.
K1, K2 and the K5 plan (147 names) have no such name.

## Batch overlap 2026-11-18 22:19 - 2026-11-19 05:10 (rule 3)

From .batch-history.log, seconds of a running batch inside each run (0 s = guard started and paused in the same
second):

| run | overlap | cpu idle min | failing checks | other replicates |
|---|---|---|---|---|
| C1-hhier-copa-codel-r2, I1-calm-ip6-pfifo-r2, M-sburst-m1-q100-pfifo-r2 | 0 s | 0.75-0.85 | none | none |
| L5-fbcold-def-codel-r3..r10 | 41-63 s | 0.71-0.86 | 1, 5 | 1, 5 in all (by design) |
| L5-fbcold-def-pie-r4..r10 | 2-4 s | 0.87-0.89 | 1, 5 | 1, 5 in all |
| L6-ppar-def-pfifo-r3 | 4 s | 0.842 | none | none |
| L7-hycombo-surge-pfifo-r1 | 3 s | 0.556 | 4 | 4 in r2, r3 (no batch); L7 planned "health unverified" |
| L9-sbnsb-sb-pfifo-r3 | ~6 min | 0.765 | 5 | 5 in r1, r2 |
| L9-sbnsb-nsb-pfifo-r3 | ~6 min | 0.813 | 5, 6 | r1 5, 6 (no batch); r2 5 |

No check failed or was newly flagged under overlap in this period: **nothing added to the re-run list** (still 3).

## Health flags without any batch (not rule 3; listed only)

| run | check | detail | cpu idle min |
|---|---|---|---|
| C1-sjoin-copa-pfifo-r2 (22:24, robustness table) | 4 | router-eth2 drop rows 81650 vs kernel 81649, 1 unmatched enqueue (same kind as L11-spause r2); r1 passes | 0.947 |
| M-sburst-m11-bw4x1-pfifo-r2 (robustness) | 5 | window at 15 s, u 1.3: measured non-video 0.787 vs planned 0.845; r1 passes | 0.941 |
| M-sburst-m3-bgmix-{pfifo,codel}-r2 (robustness) | 6 | 1 Hz peak/median 18.0 / 16.4; r1 passes 6 | 0.919 / 0.714 |
| C1-amixed-copa-pfifo-r1/r2 | 4 | private egress shaper effect (-404 us), as K1 A7 / K2 N8 | 0.84 |
| L7-hycombo-{surge,cap}-pfifo r1-r3 | 4 | all six: gap within tol 0.95, jitter -54..-89 / 37-41 us, cpu idle 0.53-0.56 | planned "health unverified" |

Earlier K3 flags (before 22:19) unchanged: L1-fbload-def-pie-r1 (check 4, lost events 1968; before any batch),
L2-fbcross-x80-codel-r2 and L11-spause-def-pfifo-r2 (re-run list).

## One-drop counter mismatch, with and without a batch (description; user 2026-11-19)

The same mismatch now appears twice: L11-spause-def-pfifo-r2 (batches overlapping, CPU idle 0.716) and
C1-sjoin-copa-pfifo-r2 (no batch, CPU idle 0.947). In both the router trace has exactly one more drop row than the
kernel's qdisc drop counter on the target hop (97921 vs 97920; 81650 vs 81649), dequeue counts agree, no event was
lost, and one enqueue row has no matching dequeue or kernel-counted drop. So one packet's fate is recorded twice or
inconsistently by the tracer (a drop row the kernel does not count, for a packet whose enqueue is otherwise
unmatched); it is a tracer / counter accounting issue at a single packet, not lost tracing under load, and the batch is
not needed for it. What it can affect: only analyses built on the router trace of that hop (GT-Q queue reconstruction
and the drop counts of GT-H) can be off by one packet (about 1 in 10^5 drop rows); an episode boundary could move only
if that single drop stood alone. Detector and grouping inputs are client-side and are not affected. Frequency across
K1-K3 (559 finished runs): 2 runs, both K3; no other run has a drop-row excess. The other counter mismatches in K1-K3
(K2 X2-huneven-uneven-codel-r4, K3 L1-fbload-def-pie-r1, L2-fbcross-x80-codel-r2) are the other kind: rows missing
with lost tracer events (1968-4856), not this one. Both runs are on the re-run list; the originals are kept, flagged.
