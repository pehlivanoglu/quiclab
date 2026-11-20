# Re-run list (one file; the user starts these together with K5-sender)

Rule 3 (user, 2026-11-18): a campaign run that fails or newly flags a health check while a batch overlapped it is
marked not reliable and listed here, without discussion.

| run | campaign | why | status |
|---|---|---|---|
| v4-T2-sburst-jit5-pfifo-r2 | 2026-11-16_0105_v4-K2 | check 5 (surge) failed in one window (u 1.3 at 154 s: non-video 1.089 vs 1.15) inside a batch window; marked **not reliable**; scored separately | pending |
| v4-L2-fbcross-x80-codel-r2 | 2026-11-16_0105_v4-K3 | check 4 (health) newly failed (r1 passes it) while batches overlapped (NPR variants + sim stage B; guard back-off at 19:01, CPU idle 0.429); rule 3: **not reliable**, no discussion. Checks 1 / 5 fail in r1 and r2 alike (BG-BURSTY, by design) | pending |
| v4-L11-spause-def-pfifo-r2 | 2026-11-16_0105_v4-K3 | check 4 (health) newly failed (r1 passes): target hop router-eth2 drop rows 97921 vs kernel 97920, 1 unmatched enqueue, while NPR variants + sim stage B2 overlapped (CPU idle 0.716 vs r1 0.936); rule 3: **not reliable**, no discussion | pending |
| v4-C1-sjoin-copa-pfifo-r2 | 2026-11-16_0105_v4-K3 | check 4 (health): target hop router-eth2 drop rows 81650 vs kernel 81649, 1 unmatched enqueue (the L11-spause r2 mismatch) with **no batch** overlapping (CPU idle 0.947); r1 passes. User 2026-11-19: re-run; the original is kept, flagged | pending |

Also run with the re-runs (not re-runs; never ran, user 2026-11-19): the 8 K3 I1 runs `v4-I1-*-ip1.2-*` under run id
`ip1p2` (reports/npr-2026-11-17/a4-rules.md, addendum 2026-11-19).
