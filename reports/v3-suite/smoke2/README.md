# Smoke 2 (.runs/2026-11-14_1801_v3-smoke, raw tracepoints): one failure left

Report copy: [smoke-report.md](smoke-report.md). Gap analysis: [gap_jitter.py](gap_jitter.py) ->
[gap-jitter.md](gap-jitter.md).

## The raw-tracepoint change removed the missed events

| topology | unmatched deq / enq, all egresses (smoke 1 -> 2) | recursion_misses per tracer | check 4 |
|---|---|---|---|
| base | 4 / 8 -> 0 / 0 | 38 -> 0 | ok -> ok |
| split4 | 16 / 48 -> 0 / 0 | 223 -> 0 | ok -> ok |
| tree16 | 50 / 140 -> 0 / 0 | 667 -> 0 | FAIL -> FAIL (4b only) |
| uneven | 59 / 119 -> 0 / 0 | 599 -> 0 | FAIL -> ok |
| access | 28 / 38 -> 0 / 0 | 158 -> 0 | FAIL -> ok |
| rev | 14 / 21 -> 0 / 0 | 90 -> 0 | ok -> ok |
| S-BURST | 8 / 23 -> 0 / 0 | 102 -> 0 | ok -> ok |

So the classic-tracepoint recursion guard explained every unmatched packet. 6 of the 7 smoke
runs now pass every check. Accounting passes on every bottleneck egress, so the stop rule
(accounting still failing) does not apply.

## The one failure: T-TREE16 root rr -> r0, service timing (4b)

98.96 % of 264 682 backlogged gaps are within +-10 % (rule: >= 99 %). The 20 ms windows are
fine (194 of 194 within +-5 %), there are 0 unmatched packets, and CPU idle min is 0.79.

| hop | C Mb/s | packet time us | +-10 % band us | within 10 % | gap - ideal us, p1 / p99 |
|---|---|---|---|---|---|
| rr->r0 | 98.1 | 101 | 10.1 | 0.9896 | -4.6 / 4.5 |
| r0->r1, r0->r2 | 49.05 | 203 | 20.3 | 0.9965-0.9967 | -4.6 / 4.4 |
| leaves A-D | 24.52 | 405 | 40.5 | 0.9981-0.9986 | -4.3 / 4.2 |

The dequeue-time jitter is the same few microseconds on every link, whatever its rate. Early and
late gaps are equally common (0.5 % each at the root), and a late gap is followed by a shorter
one (median ratio 0.94), so throughput over 20 ms is exact. On a ~100 Mb/s link, +-10 % of a
packet time is only +-10 us, so about 1 % of gaps fall outside. It is a timing-resolution limit
of the per-packet rule, not a service problem. Smoke 1 showed the same (0.9900).

## Options (yours)

1. Spec 3.4 fallback, as written: rerun the smoke with s = 0.35 for T-TREE16 only (root
   84.1 Mb/s, band +-11.8 us). From the table, the share would be about 99.1-99.2 %: a marginal pass.
   `TREE16_S=0.35 bash scripts/run_v3_smoke.sh`
2. Keep s = 0.30 and give the per-gap rule an absolute floor (e.g. within max(10 %, N us)). That
   is a new constant, so it is your number.
3. Keep s = 0.30 and gate 4b on the 20 ms windows only for links above some rate, keeping the
   per-gap share as information.

## Decision of 2026-11-14: per-gap tolerance max(10 %, 15 us); smoke 2 re-evaluated (no new run)

[reeval-report.md](reeval-report.md): **Gate: PASS**. All 7 runs pass checks 1-6 (check 5 on the
S-BURST run; the others have no surge). The tolerance share was recomputed from the packet
traces, because smoke 2's health files predate the rule (v3_gate._service_from_trace).
T-TREE16 root rr->r0: 99.79 % of 264 682 backlogged gaps within max(10 %, 15 us) (99.0 %
needed; 98.96 % with plain +-10 %); jitter p1 / p99 -4.63 / +4.55 us; 20 ms windows 194 / 194
within +-5 %; 0 unmatched packets. The other tree16 targets are at 99.86-99.91 %.

Smoke 1 vs 2 ([compare12.md](compare12.md), script [compare12.py](compare12.py)):

- The sojourn floor on router->switch is identical (min / p1 / p5 = 0.4 us), so the probe
  points did not move.
  - p99 / mean: calm 21.24 / 2.67 -> 20.54 / 2.62 ms; S-BURST 41.35 / 5.01 -> 41.30 / 4.93 ms.
  - p50: 1.03 -> 0.99 ms and 1.29 -> 1.15 ms.
- The tracer-independent tc queue (5 ms backlog / C) moves by the same order and in both
  directions: mean 1.72 -> 1.76 and 3.41 -> 3.39 ms. So these differences are run to run, not
  a shift of the measurement.
- Load, share and keyframe peaks, every bottleneck egress: largest change 0.002 (load), 0.002
  (share), 1.1 ms (keyframe peak p50; median 0.4 ms).
