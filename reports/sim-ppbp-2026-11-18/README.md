**The simulation's PPBP sources match the testbed generator: identical burst lists, realized rate equal to 0.0 %, Hurst estimate within 0.01 on all three sources.**

# PPBP port check (2026-11-18)

User request (stage A acceptance, 2026-11-17): validate the PPBP port against the testbed generator on one
run: mean rate, Hurst estimate, burst length distribution.

Run: K2 `v4-N6-hhier-bgbursty-pfifo-r1` (no testbed run with PPBP is purely calm; N6 has three PPBP background
sources plus surges, which use a different source and do not enter this check). Simulation:
`simulation/runs/ppbp/sim-X-N6-hhier-bgbursty-pfifo-r1`, seed 1, 969 s simulated, 80 s wall, 1 core.
Script: [simulation/simlab/ppbp_check.py](../../simulation/simlab/ppbp_check.py), read-only on both runs.

## Result

| source | mean_mbps cfg | hurst cfg | bursts tb / sim | burst list identical | burst s p50/p90/p99 tb | burst s p50/p90/p99 sim | KS burst length | rate Mb/s tb / sim | rate diff % | Hurst tb / sim |
|---|---|---|---|---|---|---|---|---|---|---|
| bg-up | 23.220 | 0.8 | 22397 / 22397 | yes | 0.23/0.74/3.46 | 0.23/0.74/3.46 | 0.0 | 20.529 / 20.529 | 0.0 | 0.827 / 0.817 |
| bg-a | 11.611 | 0.8 | 11477 / 11477 | yes | 0.23/0.72/3.92 | 0.23/0.72/3.92 | 0.0 | 10.949 / 10.949 | 0.0 | 0.843 / 0.837 |
| bg-b | 11.611 | 0.8 | 11160 / 11160 | yes | 0.24/0.77/4.29 | 0.24/0.77/4.29 | 0.0 | 11.598 / 11.598 | 0.0 | 0.880 / 0.880 |

## What it shows and what not

- Burst lists are identical by construction: the simulation includes `qvideo/src/Ppbp.h` unchanged and is given
  the same parameters and seed. The check confirms the plan passes them through correctly.
- Realized rate and Hurst come from the sent-bytes series (100 ms bins): the simulation's pace loop (1 ms ticks,
  credit capped at 10 ms, as `Traffic.cpp`) produces the same total bytes; the Hurst estimates differ by at most
  0.01 (sleep timing on the testbed vs exact ticks in the simulation).
- Both realize less than the configured mean (bg-up 20.5 vs 23.2 Mb/s): a property of the generator
  (heavy-tailed bursts cut at the run end; one 969 s realization), the same on both. Not a port difference.
- Hurst method: aggregated variance, block sizes 1-64 x 100 ms (0.1-6.4 s). One method, one run; the estimate
  itself is not a validation of the generator's H, only of sim = testbed.
- Not shown: the effect at the bottleneck (queue, drops), which belongs to stage B.
