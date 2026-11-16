# v4 smoke 1 (.runs/2026-11-16_0000_v4-smoke): diagnosis

Result: **FAIL**. 18 of 22 gated runs are clean on every check. **n_max = 40**: n = 24, 32 and 40
all pass health, with CPU idle >= 0.93.

## Passed

- Every new topology's calm load and share are on target (e.g. T-SPLIT4L 0.508 / 0.308 on up, 0.507 /
  0.309 on the leaves).
- pause: no frame produced in the window; resumes at the keyframe at the window end
  (50.000092 s for a pause ending at 50 s).
- persist: check 5 ok.
- T-TEACUP and its rev variant: ok.
- T-HAYES path check, after a bug fix (see below): every group crosses exactly its four links. All
  seven links carry exactly the planned clients (GT-Q destinations of publisher packets).

## Failures

| run | failing check | cause | status |
|---|---|---|---|
| T-HAYES calm | v4 path: error | **my bug**: v4_checks opened `<router>-<iface>-packets.csv`; the file is `<iface>-packets.csv` | fixed; re-checked offline on this run: path ok |
| g-shorttcp | v4 salvo: 8 / 130 flows not connected (errno 115) | **my bug**: qtraffic set a 100 ms send timeout before `connect`, so a connect whose SYN met the overloaded queue gave up with EINPROGRESS | fixed (timeout set after connect), qtraffic rebuilt, loopback test passes; needs one emulated rerun |
| T-HAYES calm | check 4b on all 7 target egresses (gaps within tolerance 0.94-0.98 < 0.99; gap jitter p1 / p99 about -45 / +40 us vs +-2.5 us elsewhere) | **unknown**. CPU idle min 0.57 (above 0.35), lost events 0, recursion misses 0. T-HAYES has 12 traced routers (others 2-7). Hypothesis, not tested: tracer load on the dequeue timestamps | open, needs a diagnosis run |
| T-LEAF4 calm (n 4, C 9.8 Mb/s) | check 4b, 20 ms windows within +-5 %: 0.984 (251 windows) < 0.99 | **check resolution**: at 9.8 Mb/s a 20 ms window holds about 16 packets, so one packet is 6 % (more than 5 %). The rule cannot pass reliably below about 12 Mb/s (20 packets per window). Gaps check: 0.9997 | **FLAG**: G1 n = 4 is in K1 and its gate |
| FB-COLD | check 1 (calm load 0.37-0.53) and check 5 (non-video 0.97 / 0.97 / 1.04 / 0.98 vs planned 1.05) | **by construction**: "calm" is only 31-43 s, right after the 30 s overload. The background is BG-BURSTY (PPBP, H 0.8): a 30 s mean varies by about +-10 %, and check 5 assumes a steady background | **FLAG**: FB-COLD is in the K3 gate |
| BG-ONOFF calm, 90 s | check 1 on leaf b: load 0.469 (other egresses 0.507 / 0.508) | **randomness**: 5 on / off sources per leaf over 90 s; the realised on-time differs from 50 % | proposal: scale each source so its realised mean is exact (the spec's "same mean BG_e") |

## Decisions needed before K1 / K3

1. **T-LEAF4 check 4b (blocks K1):** apply the 20 ms window rule only where a window holds at least
   20 packets (C >= 12 Mb/s), or lengthen the window there (40 ms at 9.8 Mb/s). The gap rule stays.
   Without a decision, the K1 gate fails on the n = 4 CALM.
2. **FB-COLD in the K3 gate:** gate the cold stimulus with BG-CBR (the stimulus is what is checked),
   while the campaign keeps BG-BURSTY. Or exempt checks 1 and 5 for FB-COLD.
3. **BG-ONOFF:** make each source's mean exact by scaling its on-rate to its realised on-time.
4. **T-HAYES 4b:** run a diagnosis before K3, for example the same CALM with tracing on the targets
   only, to test the tracer-load hypothesis.

K1 uses none of T-HAYES, FB-COLD, BG-ONOFF or salvo, so only decision 1 blocks K1.

## Decisions (2026-11-16)

1. T-LEAF4 4b window rule: **done** (user, 2026-11-16): a 4b window holds at least 25 full packets,
   so it is 20 ms at >= 15 Mb/s and longer below (router_trace.window_ns, WIN_MIN_PKTS 25 (T); the health
   file records `win_ms`; the gate recomputes from the trace for older health files). Re-checked offline:
   T-LEAF4 1.0 with 30.6 ms windows, v3 M11 bw4x1 r1 / r2 1.0 with 33.2 ms; runs at >= 15 Mb/s unchanged.
   Earlier text (window rule was open): Affected cells (C < 12 Mb/s, < 20 packets per 20 ms): K1 G1 n = 4
   (6 runs) and its gate CALM (9.81 Mb/s), K3 M11 bw4x1 (2 runs, 9.05 Mb/s). Every other shaped egress of
   K1-K3 is >= 12.9 Mb/s. Same artefact already in v3: both v3 M11 bw4x1 runs fail 4b on the 20 ms
   windows (0.963 / 0.961), unnoticed because microbenchmarks were not gated.
2. FB-COLD in the K3 gate with BG-CBR: done (campaign keeps BG-BURSTY).
3. BG-ONOFF exact mean: done (each source's on rate = mean x duration / realised on-time).
4. T-HAYES 4b: diagnose **offline** on this smoke run's GT-Q trace, **after the campaigns** (user).
   What the data already shows: the 20 ms windows on the T-HAYES targets are within +-5 % in 100 % of
   windows (rate right at 20 ms), and the per-gap error is symmetric (p1 about -45 us, p99 about +40 us).
   Planned test: lag-1 correlation of consecutive gap errors (strongly negative = timestamp noise, a late
   stamp followed by an early one; near zero = real service jitter), per traced router, against the
   number of tracers. If it is timestamp noise, record that 4b gaps on T-HAYES measure the tracer, not
   the link.
