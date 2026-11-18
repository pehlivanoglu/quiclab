# R2: detector baselines and ablation (2026-11-16)

**Answer.** Yes. The frozen detector (v2-owd) is earlier than BBR's own reaction (D1) and than libwebrtc's GCC
(D2), at higher precision. On the single-queue cells (pfifo, codel, pie, red; C blocks; r1 / r2):

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 / p90 ms |
|---|---|---|---|---|---|
| **v2-owd (frozen)** | **1.00 / 1.00** | 0.91 / 0.92 | **0.98 / 0.99** | **0.02 / 0.00** | **228 / 223, 484 / 455** |
| D1-bw: BBR bandwidth estimate drops | 0.83 / 0.85 | 0.88 / 0.89 | 0.95 / 0.95 | 1.52 / 1.44 | 806 / 779, 2172 / 2108 |
| D1-pacing | 0.35 / 0.37 | 0.91 / 0.92 | 0.97 / 0.97 | 14.1 / 14.1 | 455 / 495, 1490 / 1382 |
| D1-cwnd | 0.45 / 0.46 | 0.90 / 0.91 | 0.99 / 0.99 | 9.4 / 9.6 | 304 / 304, 1324 / 1079 |
| D2-gcc (libwebrtc) | 0.96 / 0.96 | **0.94 / 0.95** | 0.95 / 0.96 | 0.36 / 0.34 | 354 / 353, 517 / 506 |
| D3-10ms-200ms (best simple threshold) | 0.99 / 0.99 | 0.95 / 0.96 | 0.98 / 0.99 | 0.09 / 0.08 | 277 / 276, **368 / 359** |
| D4-rfc8382 | 0.70 / 0.72 | 0.18 / 0.18 | 0.98 / 0.98 | 0.63 / 0.61 | 1299 / 1182 |
| D5-v1 (Shadow v1) | 1.00 / 1.00 | 0.95 / 0.95 | 0.96 / 0.97 | 0.01 / 0.01 | 407 / 400, 980 / 968 |

**Against BBR's own reaction (D1).** The detector is ~560 ms earlier (p50) than BBR's bandwidth estimate. That
estimate is BBR's slowest-moving state: it is a max over ~10 round trips. BBR's pacing and cwnd do move earlier,
but they swing all the time and give 9-14 false alarms per minute.

**Against GCC (D2).** The detector is ~125 ms earlier at p50, with 17x fewer false alarms (0.02 against 0.35 / min)
and P 1.00 against 0.96. GCC has slightly higher onset-based recall (0.94-0.95 against 0.91-0.92). Its p90 is close
to ours (510 against 470 ms).

**The honest caveat: the best simple threshold.**
- The rule "our queue-delay feature F1 > 10 ms for 200 ms" (D3) is a strong baseline.
- It has higher recall (0.95-0.96) and a better p90 (360 against 470 ms), but more false alarms (0.08-0.09 against
  0.00-0.02) and a slower p50 (277 against 225 ms).
- It is the best of 9 grid cells chosen on these same runs (generous on purpose), and it reads F1, which is already
  the detector's own feature (OWD minus a running base).

**Fewer false alarms at the same speed is what the CUSUM buys; most of the speed comes from F1 itself.**

Rows not shown here: per AQM, fq_codel / cake, the microbenchmarks, the D3 grid and delay by stimulus type are all
in the appendix below. Code: [r2.py](r2.py), [gcc.py](gcc.py), [r2_report.py](r2_report.py). Replay of all
203 v3 runs, no emulation, frozen detector unchanged. Scoring is reports/v3-detector's, unchanged.

## What the ablation says (single-queue cells; one change each; G_ref refitted per variant)

| variant | GT3 R | alarm-on R | FA / min | delay p50 ms | on at t_harm |
|---|---|---|---|---|---|
| v2-owd (frozen, G_ref 67.7 from ip4) | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.00 | 228 / 223 | 1.00 |
| abl:ref (same structure, G_ref 56.5 refit on v3 calm) | 0.91 / 0.92 | 0.98 / 0.99 | 0.04 / 0.02 | 201 / 198 | 1.00 |
| F1 only | 0.90 / 0.91 | 0.98 / 0.99 | 0.04 / 0.05 | 243 / 243 | 1.00 |
| F2 only | 0.75 / 0.77 | 0.81 / 0.84 | 0.02 / 0.01 | 218 / 207 | 0.82 |
| F3 only | 0.91 / 0.93 | 0.98 / 0.99 | 0.07 / 0.09 | 461 / 459 | 1.00 |
| L only | 0.90 / 0.91 | 0.97 / 0.98 | 0.01 / 0.01 | 675 / 653 | 0.95 |
| without F2 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.01 | 303 / 304 | 1.00 |
| without F3 | 0.91 / 0.91 | 0.98 / 0.99 | 0.02 / 0.01 | 238 / 232 | 0.99-1.00 |
| without loss | 0.91 / 0.92 | 0.98 / 0.99 | 0.16 / 0.12 | 169 / 166 | 1.00 |
| without loss gate | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.01 | 229 / 224 | 1.00 |
| without hold | **0.95 / 0.96** | 0.98 / 0.99 | 0.01 / 0.01 | 226 / 222 | **0.94** (fq_codel 0.69-0.76) |
| without BBR masks | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.01 | 202 / 201 | 1.00 |

What each part does:
- **F1** carries most of the evidence and the onset (next section).
- **F2** makes the detector ~75 ms earlier (without it the p50 is 303 ms); alone it misses a quarter of the episodes.
- **F3** adds little on these BBR runs (without it: 238 against 228 ms).
- **Loss:** without it the detector is ~60 ms faster but has 0.12-0.16 false alarms per minute against 0.00-0.02. Its negative part (no loss = calm
  evidence) is what keeps G down.
- **Loss gate:** no effect on these cells. On the random-loss runs (C15) it barely matters either: 0.11 / 0.20
  without it against 0.08 / 0.20 with it, on the refitted reference. L alone gives 0.45-0.49 false alarms per minute
  there.
- **Hold:**
  - It lowers onset-based recall: one held alarm covers several GT3 episodes, which then count as missed starts.
  - It keeps the alarm on at harm onset: 1.00 against 0.94, and on fq_codel 0.98 against 0.69-0.76.
- **BBR masks:** no measurable effect on v3. On the Copa runs they are inactive anyway.
- **G_ref:** the frozen G_ref is conservative for v3. The same rule on v3 calm runs gives 56.5, and with it the
  detector is ~25 ms earlier at 0.02-0.04 false alarms per minute (FLAG; no change proposed).

## Per-signal contribution (frozen v2-owd), the user's question

| CC | AQM | alarm starts | share of G at alarm: F1 / F2 / F3 / loss | first signal to z >= 1 after a GT3 onset: F1 / F2 / F3 / L |
|---|---|---|---|---|
| BBR | pfifo | 7903 | 0.84 / 0.36 / -0.02 / -0.18 | 0.70 / 0.11 / 0.19 / 0.00 |
| BBR | codel | 4530 | 0.89 / 0.43 / -0.03 / -0.30 | 0.70 / 0.10 / 0.19 / 0.00 |
| BBR | pie | 1110 | 0.90 / 0.46 / -0.05 / -0.31 | 0.66 / 0.08 / 0.16 / 0.10 |
| BBR | red | 143 | 0.88 / 0.42 / -0.09 / -0.21 | 0.75 / 0.11 / 0.14 / 0.00 |
| BBR | fq_codel | 1760 | 0.57 / 0.33 / 0.14 / -0.04 | 0.71 / 0.11 / 0.17 / 0.01 |
| Copa (M13) | pfifo | 144 | 0.93 / 0.32 / -0.00 / -0.24 | 0.76 / 0.07 / 0.16 / 0.00 |
| Copa (M13) | codel | 144 | 0.99 / 0.34 / -0.02 / -0.31 | 0.74 / 0.02 / 0.23 / 0.00 |

By stimulus type (BBR, all AQMs), share of G at alarm F1 / F2 / F3 / loss and first signal F1 / F2 / F3:
- surge: 0.83 / 0.39 / -0.01 / -0.21; 0.70 / 0.11 / 0.19
- ramp: 1.29 / 0.20 / -0.13 / -0.37; 0.73 / 0.11 / 0.14
- tcp: 0.61 / 0.42 / 0.08 / -0.11; 0.64 / 0.02 / 0.33
- surge + capdrop: 0.75 / 0.47 / -0.02 / -0.21; 0.71 / 0.08 / 0.19
- join: 0.81 / 0.23 / 0.06 / -0.10; 0.90 / 0.01 / 0.08

Reading:
- **"BBR: delay signals first" holds.** F1 (queue delay) is the first signal in ~70 % of onsets and carries ~85 % of
  G at alarm start. F2 adds ~40 %. The loss term is negative on average: a congestion onset has no loss yet, so the
  calm evidence pulls G down.
- **"Copa: sender backlog first" does not hold.** On Copa, F3 is first in 16-23 % of onsets (BBR: 19 %) and its
  share of G is about zero. F1 is first in 75 % and carries 93-99 %.
  - **Why, from mvfst's Copa (quic/congestion_control/Copa.{h,cpp}, the pinned commit):**
    - Default mode only, delta = 0.05. There is no competitive mode in mvfst; the paper switches to one against
      buffer-filling cross traffic.
    - Queuing delay = latest RTT - min RTT over 10 s.
    - Target rate = 1 / (delta x d_q) packets per second.
    - Loss does not reduce cwnd; only persistent congestion does.
    - App-limited is unsupported (`setAppLimited()` is empty, Copa.cpp:438), so cwnd can grow while the video
      does not use it; this likely adds to the 4-5x allowance below.
  - **Consequence for low-rate video:** at the ~40-60 ms queue a 50 ms pfifo allows, the target is ~4.6 Mb/s. That
    is above the 1-2.5 Mb/s renditions, so Copa never limits those clients below the video rate.
  - **Measured on M13 pfifo r1 (stimulus windows; the cwnd-allowed rate is cwnd x 8 / srtt):**
    - The 1 Mb/s client keeps 4-5x the video rate allowed, and its sender backlog stays 0 (p90). F3 cannot rise:
      the queue and the losses are in the network, so F1 sees them and Copa resends the losses. That is the earlier
      "sends 1.2-1.55x its calm rate".
    - The 5 Mb/s client is held at ~0.9x its rate, and its backlog does build (p90 ~620 kB).
    - BBR at the same point limits harder: the 1 Mb/s client gets 0.9-2.2x (backlog p90 110 kB) and the 5 Mb/s
      client 0.3-1.3x.
  - So for the 1 Mb/s client this is how Copa behaves by design for a low-rate, application-limited flow in a shallow
    buffer, plus mvfst's simplifications. A full paper Copa would most likely not throttle it either (target ~4.6
    Mb/s). Label the results "mvfst Copa, default mode", not Copa in general.
  - **For the 2.5 and 5 Mb/s clients the backlog does build, and F3 is still ~0: our sender queue limit caps it**
    (next section). The "Copa: backlog first" hypothesis cannot be tested with send_buffer_ms = 1000.
- **F3 matters most where the queue is not in our path:** fq_codel (0.14 of G) and competing TCP (first in 33 % of
  onsets). Elsewhere F3 is ~0.
- The median lead of the first signal over the second is 0 ticks: in most onsets two signals cross in the same 33 ms
  tick.

## Sender queue limit: why F3 stays near 0 (user's finding)

**The sender bounds its backlog and drops.** qvideo-server puts a frame queue in front of QUIC
(`qvideo/src/SendQueue.h`, `Server.cpp` pump()):
- Limit `send_buffer_ms` = 1000 ms of media (schema default, used in every v3 run).
- A frame older than the limit is dropped **with the rest of its GOP** (GOP = 1 s), including the GOP's frames not
  yet produced; sending resumes at the next keyframe.
- Frames go to QUIC only while QUIC's unsent bytes are below one cwnd.
- So backlog = queue + QUIC unsent is bounded at about 1 s of media plus one cwnd: max 1.2-1.3x the cap (cap = 1 s
  x rendition rate) on every flow that reaches it.

**What that does to F3.** F3 is the growth of P = inflight + backlog over W_g = 30 ticks (~1 s), divided by the
delivered rate. Under overload the backlog rises at most to the cap, then a GOP drop removes a large part of it at
once. The backlog is a sawtooth, and its 1 s slope is negative a large part of the loaded time:

| flow (pfifo r1) | GOP drops / run | backlog fall at a drop, p50 | backlog max | 1 s slope < 0 while backlog > 0.3 x max |
|---|---|---|---|---|
| Copa 5 Mb/s (M13 sub-d) | 47 | 383 kB | 788 kB | 32 % |
| Copa 2.5 Mb/s (M13 sub-b) | 10 | 203 kB | 381 kB | 19 % |
| BBR 2.5 Mb/s (C2 sub-c) | 46 | 226 kB | 376 kB | 42 % |

So F3 can rise for at most ~1 s before the cap, and each drop pushes it negative. That is why its share of G is ~0
or negative everywhere, not only on Copa.

**Same stimulus point, M13 (Copa) against C2 s030u070 (BBR), pfifo / codel, mean over flows and reps:**

| CC | AQM | rate Mb/s | bytes dropped | GOP drops / run | backlog p90 / cap | max / cap |
|---|---|---|---|---|---|---|
| Copa | pfifo | 1.0 | 0.000 | 0 | 0.00 | 0.17 |
| Copa | pfifo | 2.5 | 0.015 | 8.5 | 0.23 | 1.23 |
| Copa | pfifo | 5.0 | 0.087 | 49 | 0.75 | 1.25 |
| Copa | codel | 1.0 | 0.015 | 9.5 | 0.05 | 1.32 |
| Copa | codel | 2.5 | 0.086 | 46 | 0.64 | 1.25 |
| Copa | codel | 5.0 | 0.135 | 60 | 0.74 | 1.23 |
| BBR | pfifo | 1.0 | 0.020 | 10.5 | 0.41 | 1.25 |
| BBR | pfifo | 2.5 | 0.091 | 44 | 0.65 | 1.25 |
| BBR | pfifo | 5.0 | 0.11 | 50 | 0.81 | 1.31 |
| BBR | codel | 1.0 | 0.064 | 30 | 0.68 | 1.31 |
| BBR | codel | 2.5 | 0.10 | 49 | 0.71 | 1.28 |
| BBR | codel | 5.0 | 0.10 | 48 | 0.68 | 1.41 |

F3 share of G at alarm start by client rate (same runs, pfifo + codel pooled):

| CC | 1 Mb/s | 2.5 Mb/s | 5 Mb/s |
|---|---|---|---|
| Copa | 0.03 | 0.00 | -0.08 |
| BBR | -0.01 | -0.03 | -0.08 |

Reading:
- **For 2.5 and 5 Mb/s clients the user's explanation holds**, on both CCs: the backlog reaches the cap (max 1.2-1.4x),
  9-13 % of the bytes are dropped in ~50 GOP drops per run, and F3's share is 0 to -0.08. The client with the most
  backlog (5 Mb/s) has the most negative F3. Copa's 5 Mb/s client builds as much backlog as BBR's, so "Copa:
  backlog first" was not tested: the limit removes the signal before it can lead.
- **For the 1 Mb/s Copa client on pfifo the limit is not the cause:** no drops, backlog 0 (max 0.17 of the cap).
  There Copa's cwnd (4-5x the video rate, section above) keeps the backlog empty.
- Over all v3 flows (send_queue.csv): BBR 5 Mb/s flows drop 7 % of bytes and 91 % of them drop at least once; 1 Mb/s
  flows 1.8 %, 52 %.
- **Not changed:** the frozen detector and the v3 data. A test of F3 without the limit needs new runs with
  `send_buffer_ms` = 0 (unlimited; the queue is then in QUIC) or a larger value. That changes the testbed, so it is
  the user's decision (FLAG).

Code and data: [send_queue.py](send_queue.py), [send_queue.csv](send_queue.csv) (one row per flow, all 640 v3 video
flows). The sawtooth table is from the run's cc.csv (50 ms) and drops.csv.

## Definitions, choices and caveats

- **Scoring:** reports/v3-detector/score_runs.py's truths and gt_score, unchanged. GT3 source B: P = TP / (TP + FP),
  R = onset-based (first alarm start in [t_on - 1 s, min(end, t_on + 10 s)]), alarm-on R (an alarm span overlaps that
  window), FA per minute of CLEAR time. GT-Q P from gtq_score. "On at t_harm" as reports/v3-score/harm.py: an alarm
  span covers t_harm_600. This is a span measure, so it favours detectors that keep their alarm on (hold). GCC's
  overuse state is short (it flips at every trendline update), so its low "on at t_harm" (0.15) is not a miss count.
- **D1 (FLAG):**
  - Rule: the BBR state below 0.9 x its max over the last 5 s (shadow v1's bbrDropFraction / bbrDropLookbackUs).
  - bw: BBR's bandwidth estimate per ACK (acks.csv).
  - pacing: cc.csv every 50 ms, first the max over one ProbeBW gain cycle = 8 x min RTT (T, FLAG; it was used
    without being shown to the user first).
  - cwnd: cc.csv.
- **D2:** libwebrtc main (2026-11-16), every constant from the cited source files (gcc.py header). Input:
  - only the packets whose arrival time is known, i.e. the largest acked packet of each ACK. 86-92 % of the
    5 ms groups have one; in 85-99 % of those it is the group's last packet.
  - The 8-14 % empty groups are skipped. This can only slow GCC, a small bias against it.
  - D2-gcc-frame (appendix) uses the client's frame delivery times; it is worse (more false alarms, later).
- **D2-v1-gcc-floorX (the "200 / 350 ms" item):** the old v1 replay's GCC variant with the v1 detector's
  `floor_window_ms` = X. It is a trailing-minimum window on the delay; 500 was the m4 setting, 0 the tuned one. It
  delays GCC by up to ~700 ms: p50 1018 at 500 ms, 897 at 350, 767 at 200, 335 at 0. That is the "500 ms detection
  floor" of the earlier notes. With 0 it is close to D2-gcc (335 against 354 ms).
- **D3 (P):** X 5 / 10 / 20 ms, Y 100 / 200 / 500 ms, full grid in the appendix. Best cell by pooled GT3 F1 on the same
  runs (generous on purpose).
- **D4:**
  - RFC 8382 section 3.3.1 step 1 per flow, on per-ACK OWD samples. Constants: T 0.35 s, N 50, M 30, c_s 0.1, c_h 0.3.
  - p_l 0.05 comes from the FlowBot repo's sbd.py (FLAG): the RFC gives no value.
  - It is a bottleneck-state test with a 17.5 s history, not an onset detector. Its state is on most of the time
    (alarm-on 0.98) and its starts rarely fall inside an onset window (R 0.18).
- **Ablation G_ref (FLAG):** refitted per variant with the frozen rule (the smallest multiple of the calm max G with
  <= 0.1 FA/min of GT3 CLEAR time). The fit runs on v3 C1a calm-s030u070-pfifo-r1 and calm-s065u070-pfifo-r1, the
  stand-ins for calm030 / calm065: the ip4 calm runs used for the frozen fit are no longer on disk. gref.json.
- **Contribution:**
  - Share of G = per-signal score sums over the excursion from the last G = 0 to the alarm tick, divided by G at the
    alarm; ticks where the hold rule zeroed a negative step are excluded; loss = the step minus F1 + F2 + F3.
  - First signal = the first tick at which zc = s_f / 2 + 1 >= 1, within 300 ticks after a GT3 onset.
- **Batch:** nice 19, 4 workers, during K1 (allowed by the spec after A1).
- **Side effect, fixed:** the first batch let gtq_score.score_run overwrite each run's truth/gtq-score-episodes.csv
  with the R2 detector set. No script reads that file. r2.py no longer writes it, and
  [restore_gtq_episodes.py](restore_gtq_episodes.py) rewrote it with the four frozen detectors, as
  reports/v3-detector produced it.

## Appendix: all tables

Generated by `r2.py report` (r2_report.py) from rows.jsonl.

### Baselines

#### Single-queue AQM cells (C blocks: pfifo, codel, pie, red)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.00 | 228 / 223 | 484 / 455 | 0.99 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |
| D1-bw | 0.83 / 0.85 | 0.88 / 0.89 | 0.95 / 0.95 | 1.52 / 1.44 | 806 / 779 | 2172 / 2108 | 0.96 / 0.96 | 0.73 / 0.74 | 11492 / 12031 |
| D1-pacing | 0.35 / 0.37 | 0.91 / 0.92 | 0.97 / 0.97 | 14.09 / 14.06 | 455 / 495 | 1490 / 1382 | 0.37 / 0.38 | 0.76 / 0.77 | 11492 / 12031 |
| D1-cwnd | 0.45 / 0.46 | 0.90 / 0.91 | 0.99 / 0.99 | 9.43 / 9.64 | 304 / 304 | 1324 / 1079 | 0.72 / 0.71 | 0.83 / 0.85 | 11492 / 12031 |
| D2-gcc | 0.96 / 0.96 | 0.94 / 0.95 | 0.95 / 0.96 | 0.36 / 0.34 | 354 / 353 | 517 / 506 | 0.99 / 0.99 | 0.15 / 0.15 | 11492 / 12031 |
| D2-gcc-frame | 0.91 / 0.92 | 0.95 / 0.95 | 0.96 / 0.96 | 0.78 / 0.75 | 498 / 520 | 989 / 1040 | 0.81 / 0.81 | 0.68 / 0.66 | 11492 / 12031 |
| D2-v1-gcc-floor500 | 1.00 / 1.00 | 0.90 / 0.91 | 0.90 / 0.91 | 0.02 / 0.03 | 1018 / 1002 | 1656 / 1622 | 1.00 / 1.00 | 0.42 / 0.44 | 11492 / 12031 |
| D2-v1-gcc-floor350 | 1.00 / 0.99 | 0.91 / 0.92 | 0.91 / 0.92 | 0.03 / 0.04 | 897 / 882 | 1506 / 1452 | 1.00 / 1.00 | 0.46 / 0.48 | 11492 / 12031 |
| D2-v1-gcc-floor200 | 0.99 / 0.99 | 0.92 / 0.93 | 0.92 / 0.94 | 0.05 / 0.06 | 767 / 757 | 1337 / 1316 | 1.00 / 1.00 | 0.49 / 0.51 | 11492 / 12031 |
| D2-v1-gcc-floor0 | 0.94 / 0.94 | 0.95 / 0.96 | 0.95 / 0.96 | 0.54 / 0.50 | 335 / 334 | 485 / 477 | 0.99 / 0.99 | 0.52 / 0.55 | 11492 / 12031 |
| D4-rfc8382 | 0.70 / 0.72 | 0.18 / 0.18 | 0.98 / 0.98 | 0.63 / 0.61 | 1299 / 1182 | 3349 / 3082 | 0.59 / 0.59 | 0.93 / 0.92 | 11492 / 12031 |
| D4-rfc8382-noloss | 0.84 / 0.85 | 0.39 / 0.41 | 0.71 / 0.72 | 0.65 / 0.63 | 3383 / 3299 | 5433 / 5382 | 0.74 / 0.74 | 0.49 / 0.48 | 11492 / 12031 |
| D5-v1 | 1.00 / 1.00 | 0.95 / 0.95 | 0.96 / 0.97 | 0.01 / 0.01 | 407 / 400 | 980 / 968 | 1.00 / 1.00 | 0.81 / 0.81 | 11492 / 12031 |

#### pfifo (C blocks)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.90 / 0.92 | 0.96 / 0.98 | 0.02 / 0.00 | 236 / 228 | 542 / 492 | 0.99 / 1.00 | 1.00 / 1.00 | 5311 / 5607 |
| D1-bw | 0.81 / 0.84 | 0.89 / 0.91 | 0.98 / 0.98 | 1.67 / 1.52 | 455 / 442 | 1371 / 1190 | 0.96 / 0.97 | 0.86 / 0.87 | 5311 / 5607 |
| D1-pacing | 0.33 / 0.35 | 0.90 / 0.92 | 0.98 / 0.98 | 14.93 / 15.18 | 417 / 462 | 1332 / 1132 | 0.36 / 0.37 | 0.88 / 0.88 | 5311 / 5607 |
| D1-cwnd | 0.43 / 0.45 | 0.91 / 0.92 | 1.00 / 1.00 | 9.78 / 9.89 | 238 / 247 | 1270 / 885 | 0.73 / 0.72 | 0.88 / 0.89 | 5311 / 5607 |
| D2-gcc | 0.93 / 0.94 | 0.93 / 0.95 | 0.94 / 0.95 | 0.60 / 0.58 | 341 / 337 | 547 / 540 | 0.99 / 0.98 | 0.06 / 0.06 | 5311 / 5607 |
| D2-gcc-frame | 0.90 / 0.91 | 0.94 / 0.94 | 0.95 / 0.95 | 0.89 / 0.83 | 697 / 690 | 1107 / 1116 | 0.80 / 0.81 | 0.61 / 0.58 | 5311 / 5607 |
| D2-v1-gcc-floor500 | 1.00 / 0.99 | 0.88 / 0.90 | 0.89 / 0.90 | 0.03 / 0.04 | 853 / 843 | 1159 / 1122 | 1.00 / 1.00 | 0.35 / 0.37 | 5311 / 5607 |
| D2-v1-gcc-floor350 | 0.99 / 0.99 | 0.89 / 0.91 | 0.90 / 0.91 | 0.04 / 0.07 | 766 / 755 | 1072 / 1033 | 1.00 / 0.99 | 0.37 / 0.38 | 5311 / 5607 |
| D2-v1-gcc-floor200 | 0.99 / 0.99 | 0.90 / 0.92 | 0.90 / 0.92 | 0.08 / 0.09 | 661 / 656 | 960 / 910 | 1.00 / 0.99 | 0.36 / 0.37 | 5311 / 5607 |
| D2-v1-gcc-floor0 | 0.91 / 0.92 | 0.93 / 0.95 | 0.94 / 0.96 | 0.79 / 0.74 | 324 / 321 | 515 / 493 | 0.98 / 0.98 | 0.32 / 0.34 | 5311 / 5607 |
| D4-rfc8382 | 0.62 / 0.67 | 0.13 / 0.13 | 0.99 / 0.99 | 0.63 / 0.58 | 849 / 850 | 1933 / 1549 | 0.54 / 0.55 | 0.97 / 0.96 | 5311 / 5607 |
| D4-rfc8382-noloss | 0.84 / 0.87 | 0.42 / 0.45 | 0.75 / 0.77 | 0.65 / 0.59 | 3082 / 3065 | 4816 / 4833 | 0.74 / 0.76 | 0.53 / 0.53 | 5311 / 5607 |
| D5-v1 | 1.00 / 1.00 | 0.92 / 0.94 | 0.95 / 0.96 | 0.01 / 0.01 | 408 / 403 | 1010 / 933 | 1.00 / 1.00 | 0.84 / 0.83 | 5311 / 5607 |

#### codel (C blocks)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.94 / 0.95 | 1.00 / 1.00 | 0.01 / 0.01 | 224 / 221 | 442 / 424 | 1.00 / 1.00 | 1.00 / 1.00 | 5202 / 5464 |
| D1-bw | 0.87 / 0.87 | 0.87 / 0.87 | 0.93 / 0.93 | 1.23 / 1.26 | 1279 / 1239 | 2377 / 2449 | 0.94 / 0.95 | 0.62 / 0.64 | 5202 / 5464 |
| D1-pacing | 0.41 / 0.42 | 0.92 / 0.92 | 0.97 / 0.97 | 12.78 / 12.71 | 554 / 553 | 1591 / 1504 | 0.40 / 0.40 | 0.65 / 0.67 | 5202 / 5464 |
| D1-cwnd | 0.49 / 0.50 | 0.89 / 0.90 | 0.99 / 0.99 | 8.67 / 9.19 | 499 / 482 | 1329 / 1193 | 0.71 / 0.69 | 0.78 / 0.82 | 5202 / 5464 |
| D2-gcc | 0.98 / 0.99 | 0.96 / 0.97 | 0.96 / 0.97 | 0.16 / 0.15 | 366 / 366 | 482 / 483 | 1.00 / 1.00 | 0.22 / 0.24 | 5202 / 5464 |
| D2-gcc-frame | 0.93 / 0.93 | 0.97 / 0.96 | 0.98 / 0.97 | 0.66 / 0.68 | 420 / 426 | 689 / 856 | 0.83 / 0.82 | 0.72 / 0.72 | 5202 / 5464 |
| D2-v1-gcc-floor500 | 1.00 / 1.00 | 0.92 / 0.92 | 0.92 / 0.92 | 0.01 / 0.02 | 1267 / 1260 | 1809 / 1775 | 1.00 / 1.00 | 0.49 / 0.52 | 5202 / 5464 |
| D2-v1-gcc-floor350 | 1.00 / 1.00 | 0.93 / 0.94 | 0.93 / 0.94 | 0.01 / 0.02 | 1135 / 1132 | 1627 / 1652 | 1.00 / 1.00 | 0.54 / 0.60 | 5202 / 5464 |
| D2-v1-gcc-floor200 | 1.00 / 1.00 | 0.95 / 0.95 | 0.95 / 0.95 | 0.02 / 0.04 | 990 / 989 | 1436 / 1411 | 1.00 / 1.00 | 0.62 / 0.67 | 5202 / 5464 |
| D2-v1-gcc-floor0 | 0.97 / 0.97 | 0.97 / 0.97 | 0.97 / 0.97 | 0.33 / 0.30 | 344 / 340 | 454 / 464 | 0.99 / 0.99 | 0.72 / 0.78 | 5202 / 5464 |
| D4-rfc8382 | 0.77 / 0.77 | 0.24 / 0.23 | 0.97 / 0.97 | 0.68 / 0.69 | 1516 / 1515 | 3583 / 3399 | 0.64 / 0.63 | 0.87 / 0.87 | 5202 / 5464 |
| D4-rfc8382-noloss | 0.84 / 0.85 | 0.38 / 0.38 | 0.69 / 0.71 | 0.67 / 0.70 | 3999 / 3766 | 5865 / 5699 | 0.72 / 0.71 | 0.51 / 0.48 | 5202 / 5464 |
| D5-v1 | 1.00 / 1.00 | 0.98 / 0.98 | 0.98 / 0.99 | 0.01 / 0.01 | 408 / 400 | 922 / 956 | 1.00 / 1.00 | 0.82 / 0.84 | 5202 / 5464 |

#### pie (C blocks)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 0.98 / 1.00 | 0.81 / 0.80 | 1.00 / 0.99 | 0.08 / 0.00 | 213 / 212 | 491 / 408 | 0.98 / 1.00 | 1.00 / 0.99 | 895 / 879 |
| D1-bw | 0.73 / 0.74 | 0.86 / 0.84 | 0.95 / 0.94 | 1.94 / 1.79 | 1095 / 1136 | 2282 / 2407 | 0.95 / 0.94 | 0.67 / 0.64 | 895 / 879 |
| D1-pacing | 0.25 / 0.26 | 0.86 / 0.85 | 0.95 / 0.94 | 15.50 / 14.45 | 469 / 494 | 1640 / 1692 | 0.35 / 0.36 | 0.70 / 0.67 | 895 / 879 |
| D1-cwnd | 0.33 / 0.34 | 0.91 / 0.89 | 1.00 / 1.00 | 10.95 / 10.46 | 499 / 522 | 1427 / 1355 | 0.71 / 0.71 | 0.80 / 0.79 | 895 / 879 |
| D2-gcc | 0.99 / 0.99 | 0.90 / 0.89 | 0.90 / 0.90 | 0.07 / 0.08 | 348 / 352 | 596 / 569 | 1.00 / 1.00 | 0.17 / 0.13 | 895 / 879 |
| D2-gcc-frame | 0.89 / 0.89 | 0.93 / 0.91 | 0.95 / 0.95 | 0.71 / 0.68 | 423 / 405 | 1118 / 980 | 0.78 / 0.80 | 0.74 / 0.76 | 895 / 879 |
| D2-v1-gcc-floor500 | 1.00 / 1.00 | 0.85 / 0.86 | 0.88 / 0.89 | 0.00 / 0.00 | 1060 / 1047 | 1429 / 1323 | 1.00 / 1.00 | 0.40 / 0.41 | 895 / 879 |
| D2-v1-gcc-floor350 | 1.00 / 1.00 | 0.87 / 0.87 | 0.90 / 0.91 | 0.00 / 0.00 | 970 / 945 | 1329 / 1273 | 1.00 / 1.00 | 0.47 / 0.46 | 895 / 879 |
| D2-v1-gcc-floor200 | 1.00 / 1.00 | 0.88 / 0.89 | 0.91 / 0.92 | 0.00 / 0.00 | 853 / 814 | 1205 / 1185 | 1.00 / 1.00 | 0.52 / 0.49 | 895 / 879 |
| D2-v1-gcc-floor0 | 0.96 / 0.96 | 0.90 / 0.90 | 0.92 / 0.93 | 0.25 / 0.26 | 330 / 334 | 597 / 535 | 1.00 / 1.00 | 0.53 / 0.53 | 895 / 879 |
| D4-rfc8382 | 0.60 / 0.55 | 0.12 / 0.10 | 1.00 / 1.00 | 0.49 / 0.47 | 1182 / 1299 | 3139 / 2604 | 0.61 / 0.51 | 0.96 / 0.94 | 895 / 879 |
| D4-rfc8382-noloss | 0.76 / 0.74 | 0.31 / 0.26 | 0.51 / 0.44 | 0.58 / 0.57 | 1857 / 1791 | 5433 / 4652 | 0.74 / 0.70 | 0.27 / 0.29 | 895 / 879 |
| D5-v1 | 1.00 / 1.00 | 0.91 / 0.89 | 0.93 / 0.93 | 0.01 / 0.01 | 394 / 398 | 1084 / 1130 | 1.00 / 1.00 | 0.68 / 0.65 | 895 / 879 |

#### red (C blocks)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 1.00 / 0.99 | 1.00 / 0.99 | 0.00 / 0.00 | 210 / 176 | 543 / 402 | 1.00 / 1.00 | 1.00 / 1.00 | 84 / 81 |
| D1-bw | 0.79 / 0.80 | 0.90 / 0.88 | 0.94 / 0.94 | 1.39 / 1.17 | 580 / 541 | 1761 / 1974 | 0.97 / 0.93 | 0.89 / 0.93 | 84 / 81 |
| D1-pacing | 0.32 / 0.29 | 0.89 / 0.91 | 0.98 / 0.96 | 11.07 / 11.93 | 339 / 352 | 1371 / 1557 | 0.38 / 0.37 | 0.91 / 0.90 | 84 / 81 |
| D1-cwnd | 0.45 / 0.41 | 0.96 / 0.93 | 1.00 / 1.00 | 6.89 / 7.17 | 237 / 225 | 637 / 743 | 0.81 / 0.81 | 0.91 / 0.90 | 84 / 81 |
| D2-gcc | 1.00 / 0.99 | 1.00 / 1.00 | 1.00 / 1.00 | 0.00 / 0.07 | 315 / 306 | 594 / 467 | 1.00 / 1.00 | 0.00 / 0.00 | 84 / 81 |
| D2-gcc-frame | 0.90 / 0.87 | 0.99 / 1.00 | 0.99 / 1.00 | 0.63 / 0.78 | 676 / 601 | 871 / 898 | 0.82 / 0.84 | 0.71 / 0.73 | 84 / 81 |
| D2-v1-gcc-floor500 | 1.00 / 1.00 | 0.99 / 1.00 | 0.99 / 1.00 | 0.00 / 0.00 | 814 / 832 | 1226 / 995 | 1.00 / 1.00 | 0.43 / 0.43 | 84 / 81 |
| D2-v1-gcc-floor350 | 1.00 / 1.00 | 0.99 / 1.00 | 0.99 / 1.00 | 0.00 / 0.00 | 737 / 749 | 1045 / 892 | 1.00 / 1.00 | 0.26 / 0.43 | 84 / 81 |
| D2-v1-gcc-floor200 | 1.00 / 1.00 | 0.99 / 1.00 | 0.99 / 1.00 | 0.00 / 0.00 | 649 / 676 | 918 / 848 | 1.00 / 1.00 | 0.17 / 0.40 | 84 / 81 |
| D2-v1-gcc-floor0 | 0.98 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 0.14 / 0.00 | 310 / 290 | 573 / 433 | 1.00 / 1.00 | 0.14 / 0.17 | 84 / 81 |
| D4-rfc8382 | 0.68 / 0.67 | 0.15 / 0.12 | 1.00 / 0.96 | 0.42 / 0.33 | 967 / 1165 | 2273 / 3206 | 0.65 / 0.62 | 1.00 / 1.00 | 84 / 81 |
| D4-rfc8382-noloss | 0.88 / 0.91 | 0.55 / 0.63 | 0.60 / 0.67 | 0.42 / 0.33 | 3875 / 3199 | 4449 / 4066 | 0.88 / 0.88 | 0.23 / 0.27 | 84 / 81 |
| D5-v1 | 1.00 / 1.00 | 0.98 / 0.96 | 0.98 / 0.96 | 0.00 / 0.00 | 432 / 456 | 1329 / 1314 | 1.00 / 1.00 | 0.83 / 0.70 | 84 / 81 |

#### Per-flow-queue AQM cells (fq_codel, cake; detector truth = own sub-queue)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 0.99 / 0.99 | 0.92 / 0.95 | 0.97 / 0.97 | 0.04 / 0.02 | 237 / 223 | 623 / 669 | 0.98 / 0.98 | 0.98 / 0.99 | 1567 / 1598 |
| D1-bw | 0.89 / 0.89 | 0.86 / 0.88 | 0.88 / 0.90 | 0.34 / 0.37 | 852 / 825 | 2574 / 2328 | 0.94 / 0.95 | 0.59 / 0.60 | 1567 / 1598 |
| D1-pacing | 0.33 / 0.33 | 0.91 / 0.90 | 0.94 / 0.92 | 6.19 / 6.24 | 601 / 621 | 1211 / 1231 | 0.78 / 0.81 | 0.63 / 0.64 | 1567 / 1598 |
| D1-cwnd | 0.29 / 0.30 | 0.96 / 0.98 | 1.00 / 1.00 | 7.67 / 7.76 | 205 / 189 | 357 / 328 | 0.84 / 0.84 | 0.76 / 0.77 | 1567 / 1598 |
| D2-gcc | 0.83 / 0.85 | 0.96 / 0.97 | 0.96 / 0.97 | 0.66 / 0.60 | 341 / 311 | 564 / 556 | 0.99 / 0.99 | 0.26 / 0.23 | 1567 / 1598 |
| D2-gcc-frame | 0.84 / 0.84 | 0.91 / 0.91 | 0.92 / 0.91 | 0.58 / 0.60 | 803 / 883 | 1519 / 1543 | 0.76 / 0.77 | 0.46 / 0.45 | 1567 / 1598 |
| D2-v1-gcc-floor500 | 1.00 / 1.00 | 0.83 / 0.82 | 0.83 / 0.82 | 0.00 / 0.00 | 1055 / 1026 | 1684 / 1532 | 0.99 / 0.99 | 0.07 / 0.07 | 1567 / 1598 |
| D2-v1-gcc-floor350 | 1.00 / 1.00 | 0.88 / 0.89 | 0.89 / 0.90 | 0.00 / 0.01 | 857 / 833 | 1509 / 1430 | 1.00 / 1.00 | 0.14 / 0.13 | 1567 / 1598 |
| D2-v1-gcc-floor200 | 1.00 / 1.00 | 0.92 / 0.93 | 0.92 / 0.93 | 0.00 / 0.00 | 685 / 666 | 1207 / 1253 | 1.00 / 1.00 | 0.23 / 0.21 | 1567 / 1598 |
| D2-v1-gcc-floor0 | 0.64 / 0.66 | 0.96 / 0.97 | 0.97 / 0.97 | 1.79 / 1.68 | 344 / 306 | 599 / 591 | 0.99 / 0.99 | 0.35 / 0.31 | 1567 / 1598 |
| D4-rfc8382 | 0.68 / 0.69 | 0.43 / 0.43 | 0.93 / 0.93 | 0.67 / 0.66 | 1348 / 1466 | 3199 / 2682 | 0.78 / 0.80 | 0.85 / 0.87 | 1567 / 1598 |
| D4-rfc8382-noloss | 0.64 / 0.63 | 0.36 / 0.34 | 0.51 / 0.45 | 0.68 / 0.66 | 2466 / 2283 | 5165 / 4666 | 0.77 / 0.79 | 0.41 / 0.35 | 1567 / 1598 |
| D5-v1 | 1.00 / 1.00 | 0.91 / 0.93 | 0.92 / 0.93 | 0.01 / 0.01 | 370 / 345 | 957 / 1015 | 0.99 / 0.98 | 0.76 / 0.76 | 1567 / 1598 |

#### Microbenchmarks (M blocks)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.97 / 0.96 | 0.99 / 0.99 | 0.03 / 0.02 | 214 / 206 | 520 / 440 | 0.99 / 0.99 | 1.00 / 1.00 | 5906 / 5951 |
| D1-bw | 0.86 / 0.86 | 0.86 / 0.87 | 0.96 / 0.97 | 1.49 / 1.50 | 552 / 545 | 1833 / 1917 | 0.96 / 0.95 | 0.82 / 0.80 | 5588 / 5627 |
| D1-pacing | 0.43 / 0.44 | 0.88 / 0.88 | 0.98 / 0.98 | 11.77 / 11.32 | 439 / 469 | 1547 / 1442 | 0.39 / 0.39 | 0.83 / 0.80 | 5906 / 5951 |
| D1-cwnd | 0.49 / 0.49 | 0.90 / 0.90 | 1.00 / 1.00 | 9.34 / 9.39 | 223 / 248 | 1178 / 1232 | 0.68 / 0.68 | 0.92 / 0.91 | 5906 / 5951 |
| D2-gcc | 0.96 / 0.96 | 0.98 / 0.97 | 0.98 / 0.97 | 0.38 / 0.39 | 329 / 329 | 519 / 500 | 1.00 / 1.00 | 0.12 / 0.14 | 5906 / 5951 |
| D2-gcc-frame | 0.92 / 0.92 | 0.95 / 0.95 | 0.96 / 0.96 | 0.86 / 0.81 | 563 / 579 | 1083 / 1163 | 0.81 / 0.80 | 0.65 / 0.62 | 5906 / 5951 |
| D2-v1-gcc-floor500 | 0.99 / 1.00 | 0.92 / 0.91 | 0.92 / 0.92 | 0.05 / 0.04 | 912 / 920 | 1483 / 1463 | 0.99 / 0.99 | 0.52 / 0.42 | 5906 / 5951 |
| D2-v1-gcc-floor350 | 0.99 / 0.99 | 0.93 / 0.93 | 0.93 / 0.94 | 0.06 / 0.06 | 806 / 806 | 1327 / 1343 | 0.99 / 0.99 | 0.56 / 0.47 | 5906 / 5951 |
| D2-v1-gcc-floor200 | 0.99 / 0.99 | 0.95 / 0.95 | 0.95 / 0.95 | 0.09 / 0.07 | 691 / 682 | 1197 / 1178 | 0.98 / 0.98 | 0.57 / 0.51 | 5906 / 5951 |
| D2-v1-gcc-floor0 | 0.93 / 0.94 | 0.98 / 0.97 | 0.98 / 0.98 | 0.71 / 0.67 | 315 / 312 | 493 / 472 | 0.99 / 0.99 | 0.55 / 0.52 | 5906 / 5951 |
| D4-rfc8382 | 0.85 / 0.79 | 0.23 / 0.17 | 0.96 / 0.96 | 0.43 / 0.45 | 1200 / 1382 | 3199 / 4118 | 0.67 / 0.61 | 0.91 / 0.91 | 5906 / 5951 |
| D4-rfc8382-noloss | 0.92 / 0.91 | 0.47 / 0.50 | 0.54 / 0.58 | 0.43 / 0.47 | 3715 / 3548 | 5150 / 4700 | 0.85 / 0.81 | 0.19 / 0.23 | 5906 / 5951 |
| D5-v1 | 1.00 / 1.00 | 0.97 / 0.97 | 0.98 / 0.98 | 0.00 / 0.00 | 419 / 403 | 952 / 890 | 1.00 / 1.00 | 0.88 / 0.88 | 5906 / 5951 |

#### D3 simple thresholds on F1 (single-queue cells): full grid (r1 / r2)

| X ms | Y ms | GT3 P | GT3 R | FA / min | delay p50 | p90 | F1 (pooled) |
|---|---|---|---|---|---|---|---|
| 5 | 100 | 0.39 / 0.41 | 0.96 / 0.97 | 12.91 / 12.71 | 125 / 130 | 194 / 193 | 0.563 |
| 5 | 200 | 0.76 / 0.77 | 0.96 / 0.97 | 2.61 / 2.59 | 242 / 242 | 308 / 302 | 0.852 |
| 5 | 500 | 0.98 / 0.98 | 0.94 / 0.96 | 0.12 / 0.16 | 546 / 547 | 624 / 616 | 0.966 |
| 10 | 100 | 0.92 / 0.92 | 0.96 / 0.97 | 0.75 / 0.77 | 174 / 173 | 253 / 243 | 0.942 |
| 10 | 200 | 0.99 / 0.99 | 0.95 / 0.96 | 0.09 / 0.08 | 277 / 276 | 368 / 359 | 0.973 |
| 10 | 500 | 1.00 / 1.00 | 0.94 / 0.95 | 0.02 / 0.04 | 578 / 577 | 686 / 678 | 0.971 |
| 20 | 100 | 0.99 / 0.99 | 0.95 / 0.96 | 0.08 / 0.10 | 235 / 231 | 432 / 376 | 0.972 |
| 20 | 200 | 1.00 / 1.00 | 0.94 / 0.96 | 0.03 / 0.03 | 336 / 332 | 550 / 501 | 0.972 |
| 20 | 500 | 1.00 / 1.00 | 0.93 / 0.94 | 0.02 / 0.02 | 637 / 633 | 871 / 838 | 0.966 |

Best cell for the baseline (highest pooled GT3 F1, deliberately generous): **D3-10ms-200ms** (0.973).

#### Frozen detector next to the best D3 cell

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.00 | 228 / 223 | 484 / 455 | 0.99 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |
| D3-10ms-200ms | 0.99 / 0.99 | 0.95 / 0.96 | 0.98 / 0.99 | 0.09 / 0.08 | 277 / 276 | 368 / 359 | 0.99 / 0.99 | 0.82 / 0.82 | 11492 / 12031 |

#### Delay by stimulus type and AQM, pooled reps (p50 ms; GT3 R in brackets)

| type | AQM | v2-owd | D1-bw | D2-gcc | D2-v1-gcc-floor0 | D5-v1 |
|---|---|---|---|---|---|---|
| join | pfifo | 106 (0.30) | 382 (0.57) | 0 (0.51) | 0 (0.54) | 2513 (0.27) |
| join | codel | 283 (0.40) | 1796 (0.43) | 0 (0.90) | 0 (0.93) | 628 (0.68) |
| join | fq_codel | 128 (0.31) | 3675 (0.08) | 482 (1.00) | 506 (1.00) | 497 (0.23) |
| ramp | pfifo | 391 (0.99) | 788 (0.89) | 395 (0.99) | 362 (0.99) | 1115 (0.99) |
| ramp | codel | 378 (1.00) | 1783 (0.92) | 430 (0.99) | 407 (0.99) | 1072 (0.98) |
| ramp | pie | 446 (0.77) | 1358 (0.82) | 426 (0.88) | 415 (0.90) | 834 (0.84) |
| ramp | fq_codel | 325 (0.99) | 1942 (0.90) | 273 (1.00) | 0 (1.00) | 808 (1.00) |
| surge | pfifo | 233 (0.91) | 447 (0.90) | 343 (0.94) | 325 (0.94) | 400 (0.94) |
| surge | codel | 222 (0.95) | 1254 (0.88) | 367 (0.97) | 344 (0.97) | 402 (0.98) |
| surge | pie | 215 (0.80) | 1085 (0.84) | 358 (0.89) | 337 (0.89) | 393 (0.91) |
| surge | red | 195 (0.99) | 565 (0.89) | 308 (1.00) | 291 (1.00) | 434 (0.97) |
| surge | fq_codel | 228 (0.93) | 806 (0.88) | 323 (0.97) | 321 (0.97) | 351 (0.93) |
| surge | cake | - (0.00) | 0 (0.80) | - (0.00) | - (0.00) | - (0.00) |
| surge+capdrop | pfifo | 185 (0.98) | 499 (0.93) | 322 (0.98) | 299 (0.98) | 406 (0.98) |
| surge+capdrop | codel | 173 (1.00) | 1405 (0.85) | 326 (1.00) | 315 (1.00) | 399 (1.00) |
| surge+capdrop | pie | 204 (0.87) | 1301 (0.87) | 345 (0.92) | 328 (0.92) | 416 (0.90) |
| surge+capdrop | fq_codel | 205 (1.00) | 964 (0.91) | 340 (1.00) | 322 (1.00) | 371 (0.99) |
| tcp | pfifo | 167 (1.00) | 334 (0.96) | 270 (0.99) | 251 (0.99) | 333 (0.93) |
| tcp | codel | 182 (0.95) | 1798 (0.90) | 298 (0.97) | 283 (0.97) | 346 (0.80) |
| tcp | pie | 176 (0.87) | 1175 (0.92) | 289 (0.92) | 280 (0.94) | 334 (0.87) |
| tcp | fq_codel | 301 (0.89) | 2538 (0.48) | 344 (0.91) | 407 (0.85) | 438 (0.39) |

### Ablation of the frozen detector (one change each; G_ref refitted per variant)

G_ref (refit on v3 calm pfifo-r1 s030u070 / s065u070): abl:ref 56.5, abl:F1-only 62.0, abl:F2-only 38.9, abl:F3-only 37.6, abl:L-only 40.1, abl:no-F2 58.7, abl:no-F3 77.2, abl:no-loss 56.5, abl:no-gate 67.8, abl:no-hold 56.5, abl:no-masks 56.3; frozen v2-owd 67.7 (ip4 fit).

#### Single-queue AQM cells

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.00 | 228 / 223 | 484 / 455 | 0.99 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |
| abl:ref | 0.99 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.04 / 0.02 | 201 / 198 | 442 / 409 | 0.99 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |
| abl:F1-only | 0.99 / 0.99 | 0.90 / 0.91 | 0.98 / 0.99 | 0.04 / 0.05 | 243 / 243 | 354 / 363 | 0.99 / 0.99 | 1.00 / 1.00 | 11492 / 12031 |
| abl:F2-only | 1.00 / 1.00 | 0.75 / 0.77 | 0.81 / 0.84 | 0.02 / 0.01 | 218 / 207 | 675 / 624 | 0.99 / 1.00 | 0.82 / 0.82 | 11492 / 12031 |
| abl:F3-only | 0.99 / 0.99 | 0.91 / 0.93 | 0.98 / 0.99 | 0.07 / 0.09 | 461 / 459 | 860 / 841 | 0.96 / 0.96 | 1.00 / 1.00 | 11492 / 12031 |
| abl:L-only | 1.00 / 1.00 | 0.90 / 0.91 | 0.97 / 0.98 | 0.01 / 0.01 | 675 / 653 | 1604 / 1583 | 1.00 / 0.99 | 0.95 / 0.95 | 11492 / 12031 |
| abl:no-F2 | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.01 | 303 / 304 | 522 / 503 | 0.99 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |
| abl:no-F3 | 1.00 / 1.00 | 0.91 / 0.91 | 0.98 / 0.99 | 0.02 / 0.01 | 238 / 232 | 468 / 457 | 0.99 / 1.00 | 0.99 / 1.00 | 11492 / 12031 |
| abl:no-loss | 0.98 / 0.99 | 0.91 / 0.92 | 0.98 / 0.99 | 0.16 / 0.12 | 169 / 166 | 358 / 332 | 0.98 / 0.99 | 1.00 / 1.00 | 11492 / 12031 |
| abl:no-gate | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.01 | 229 / 224 | 483 / 454 | 0.99 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |
| abl:no-hold | 1.00 / 1.00 | 0.95 / 0.96 | 0.98 / 0.99 | 0.01 / 0.01 | 226 / 222 | 591 / 566 | 1.00 / 1.00 | 0.94 / 0.94 | 11492 / 12031 |
| abl:no-masks | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 / 0.99 | 0.02 / 0.01 | 202 / 201 | 404 / 393 | 1.00 / 1.00 | 1.00 / 1.00 | 11492 / 12031 |

#### fq_codel / cake

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 0.99 / 0.99 | 0.92 / 0.95 | 0.97 / 0.97 | 0.04 / 0.02 | 237 / 223 | 623 / 669 | 0.98 / 0.98 | 0.98 / 0.99 | 1567 / 1598 |
| abl:ref | 0.97 / 0.98 | 0.92 / 0.95 | 0.97 / 0.98 | 0.09 / 0.07 | 218 / 208 | 598 / 570 | 0.97 / 0.98 | 0.98 / 0.99 | 1567 / 1598 |
| abl:F1-only | 0.95 / 0.95 | 0.89 / 0.93 | 0.98 / 0.98 | 0.16 / 0.17 | 301 / 291 | 656 / 742 | 0.91 / 0.90 | 0.98 / 0.98 | 1567 / 1598 |
| abl:F2-only | 0.99 / 0.99 | 0.89 / 0.92 | 0.95 / 0.95 | 0.04 / 0.03 | 276 / 268 | 738 / 755 | 0.95 / 0.96 | 0.98 / 0.98 | 1567 / 1598 |
| abl:F3-only | 0.98 / 0.96 | 0.90 / 0.93 | 0.95 / 0.95 | 0.07 / 0.12 | 378 / 369 | 900 / 888 | 0.95 / 0.93 | 0.98 / 0.99 | 1567 / 1598 |
| abl:L-only | 0.99 / 0.99 | 0.90 / 0.93 | 0.96 / 0.96 | 0.03 / 0.02 | 344 / 338 | 807 / 883 | 1.00 / 0.99 | 0.98 / 0.99 | 1567 / 1598 |
| abl:no-F2 | 0.99 / 1.00 | 0.92 / 0.94 | 0.97 / 0.97 | 0.02 / 0.01 | 255 / 248 | 648 / 696 | 0.98 / 0.99 | 0.98 / 0.99 | 1567 / 1598 |
| abl:no-F3 | 0.99 / 0.99 | 0.91 / 0.93 | 0.96 / 0.97 | 0.03 / 0.02 | 251 / 242 | 649 / 707 | 0.97 / 0.96 | 0.98 / 0.99 | 1567 / 1598 |
| abl:no-loss | 0.92 / 0.92 | 0.93 / 0.95 | 0.98 / 0.98 | 0.26 / 0.28 | 208 / 200 | 564 / 565 | 0.96 / 0.97 | 0.98 / 0.99 | 1567 / 1598 |
| abl:no-gate | 0.99 / 0.99 | 0.92 / 0.95 | 0.97 / 0.97 | 0.04 / 0.02 | 236 / 223 | 606 / 623 | 0.98 / 0.98 | 0.98 / 0.99 | 1567 / 1598 |
| abl:no-hold | 0.99 / 0.99 | 0.96 / 0.96 | 0.96 / 0.97 | 0.03 / 0.04 | 228 / 231 | 717 / 743 | 0.99 / 0.99 | 0.76 / 0.69 | 1567 / 1598 |
| abl:no-masks | 0.98 / 0.98 | 0.93 / 0.97 | 0.98 / 0.99 | 0.07 / 0.06 | 217 / 205 | 467 / 424 | 0.98 / 0.99 | 1.00 / 1.00 | 1567 / 1598 |

#### Random loss (C15): loss-gate ablation (no GT3 episodes expected; FA / min is the result)

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 0.00 / 0.00 | - / - | - / - | 0.04 / 0.16 | - / - | - / - | 1.00 / 0.60 | - / - | 0 / 0 |
| abl:ref | 0.00 / 0.00 | - / - | - / - | 0.08 / 0.20 | - / - | - / - | 1.00 / 0.50 | - / - | 0 / 0 |
| abl:no-gate | 0.00 / 0.00 | - / - | - / - | 0.11 / 0.20 | - / - | - / - | 0.50 / 0.45 | - / - | 0 / 0 |
| abl:no-loss | 0.00 / 0.00 | - / - | - / - | 0.08 / 0.20 | - / - | - / - | 1.00 / 0.71 | - / - | 0 / 0 |
| abl:L-only | 0.00 / 0.00 | - / - | - / - | 0.49 / 0.45 | - / - | - / - | 0.30 / 0.21 | - / - | 0 / 0 |

#### Microbenchmarks

| detector | GT3 P | GT3 R | alarm-on R | FA / min | delay p50 ms | p90 ms | GT-Q P | on at t_harm | episodes |
|---|---|---|---|---|---|---|---|---|---|
| v2-owd | 1.00 / 1.00 | 0.97 / 0.96 | 0.99 / 0.99 | 0.03 / 0.02 | 214 / 206 | 520 / 440 | 0.99 / 0.99 | 1.00 / 1.00 | 5906 / 5951 |
| abl:ref | 0.99 / 1.00 | 0.97 / 0.97 | 0.99 / 0.99 | 0.05 / 0.05 | 192 / 176 | 460 / 400 | 0.99 / 0.99 | 1.00 / 1.00 | 5906 / 5951 |
| abl:F1-only | 0.99 / 0.99 | 0.97 / 0.96 | 0.99 / 1.00 | 0.07 / 0.06 | 247 / 242 | 509 / 468 | 0.98 / 0.97 | 1.00 / 1.00 | 5906 / 5951 |
| abl:F2-only | 0.99 / 1.00 | 0.78 / 0.78 | 0.79 / 0.80 | 0.04 / 0.04 | 195 / 191 | 624 / 462 | 0.99 / 0.99 | 0.76 / 0.79 | 5906 / 5951 |
| abl:F3-only | 0.98 / 0.98 | 0.97 / 0.96 | 0.99 / 0.99 | 0.18 / 0.20 | 422 / 426 | 1054 / 956 | 0.91 / 0.91 | 0.97 / 0.98 | 5906 / 5951 |
| abl:L-only | 1.00 / 1.00 | 0.95 / 0.94 | 0.97 / 0.97 | 0.00 / 0.01 | 487 / 489 | 1484 / 1456 | 1.00 / 1.00 | 0.94 / 0.94 | 5906 / 5951 |
| abl:no-F2 | 1.00 / 1.00 | 0.98 / 0.97 | 0.99 / 0.99 | 0.02 / 0.02 | 288 / 276 | 600 / 564 | 1.00 / 0.99 | 1.00 / 1.00 | 5906 / 5951 |
| abl:no-F3 | 1.00 / 1.00 | 0.97 / 0.96 | 0.99 / 0.99 | 0.01 / 0.01 | 222 / 209 | 550 / 473 | 1.00 / 1.00 | 1.00 / 0.99 | 5906 / 5951 |
| abl:no-loss | 0.99 / 0.99 | 0.97 / 0.97 | 0.99 / 1.00 | 0.12 / 0.13 | 164 / 157 | 428 / 367 | 0.99 / 0.98 | 1.00 / 1.00 | 5906 / 5951 |
| abl:no-gate | 1.00 / 1.00 | 0.98 / 0.96 | 0.99 / 0.99 | 0.03 / 0.02 | 214 / 206 | 508 / 440 | 0.99 / 0.99 | 1.00 / 1.00 | 5906 / 5951 |
| abl:no-hold | 1.00 / 1.00 | 0.98 / 0.97 | 0.99 / 0.99 | 0.02 / 0.01 | 205 / 202 | 558 / 494 | 1.00 / 1.00 | 0.97 / 0.94 | 5906 / 5951 |
| abl:no-masks | 1.00 / 1.00 | 0.98 / 0.97 | 0.99 / 1.00 | 0.03 / 0.02 | 190 / 179 | 416 / 393 | 1.00 / 1.00 | 1.00 / 1.00 | 5906 / 5951 |

#### Calm runs: false alarms per minute (GT3 CLEAR time)

| detector | FA / min r1 / r2 |
|---|---|
| v2-owd | 0.01 / 0.00 |
| D1-bw | 0.06 / 0.06 |
| D1-pacing | 0.88 / 0.88 |
| D1-cwnd | 3.95 / 3.91 |
| D2-gcc | 0.26 / 0.33 |
| D2-gcc-frame | 1.21 / 1.10 |
| D2-v1-gcc-floor500 | 0.00 / 0.00 |
| D2-v1-gcc-floor350 | 0.01 / 0.00 |
| D2-v1-gcc-floor200 | 0.04 / 0.04 |
| D2-v1-gcc-floor0 | 0.19 / 0.25 |
| D4-rfc8382 | 0.57 / 0.57 |
| D4-rfc8382-noloss | 0.56 / 0.56 |
| D5-v1 | 0.00 / 0.00 |
| abl:ref | 0.02 / 0.04 |
| abl:F1-only | 0.12 / 0.14 |
| abl:F2-only | 0.00 / 0.00 |
| abl:F3-only | 0.09 / 0.11 |
| abl:L-only | 0.02 / 0.02 |
| abl:no-F2 | 0.03 / 0.03 |
| abl:no-F3 | 0.01 / 0.01 |
| abl:no-loss | 0.14 / 0.23 |
| abl:no-gate | 0.01 / 0.00 |
| abl:no-hold | 0.01 / 0.02 |
| abl:no-masks | 0.04 / 0.02 |

### Per-signal contribution (frozen v2-owd)

Share of G at alarm start from each signal (mean over alarm starts; G summed over the excursion since G was last 0, ticks where the hold rule zeroed a negative step excluded; loss = the gated loss term). First signal to reach z >= 1 after a GT3 onset (within 300 ticks), and its median lead over the next one (ticks of 33 ms).

| CC | AQM | stimulus | alarms | F1 | F2 | F3 | loss | onsets | first: F1 | F2 | F3 | L | none | lead of first, ticks p50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bbr | all | calm | 79 | 0.52 | 0.20 | 0.24 | 0.03 | 361 | 0.37 | 0.18 | 0.45 | 0.00 | 0.00 | 1.0 |
| bbr | all | join | 161 | 0.81 | 0.23 | 0.06 | -0.10 | 287 | 0.90 | 0.01 | 0.08 | 0.01 | 0.00 | 0.0 |
| bbr | all | loss | 6 | 0.49 | 0.42 | 0.04 | 0.05 | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| bbr | all | ramp | 298 | 1.29 | 0.20 | -0.13 | -0.37 | 687 | 0.73 | 0.11 | 0.14 | 0.02 | 0.00 | 1.0 |
| bbr | all | reverse | 142 | 0.73 | 0.38 | 0.03 | -0.14 | 283 | 0.75 | 0.09 | 0.16 | 0.00 | 0.00 | 0.0 |
| bbr | all | surge | 14451 | 0.83 | 0.39 | -0.01 | -0.21 | 35280 | 0.70 | 0.11 | 0.19 | 0.00 | 0.00 | 0.0 |
| bbr | all | surge+capdrop | 382 | 0.75 | 0.47 | -0.02 | -0.21 | 824 | 0.71 | 0.08 | 0.19 | 0.02 | 0.00 | 0.0 |
| bbr | all | tcp | 523 | 0.61 | 0.42 | 0.08 | -0.11 | 542 | 0.64 | 0.02 | 0.33 | 0.01 | 0.00 | 0.0 |
| bbr | cake | all | 1 | 0.32 | 0.25 | 0.10 | 0.33 | 5 | 0.20 | 0.40 | 0.40 | 0.00 | 0.00 | 6.0 |
| bbr | codel | all | 4530 | 0.89 | 0.43 | -0.03 | -0.30 | 12861 | 0.70 | 0.10 | 0.19 | 0.00 | 0.00 | 0.0 |
| bbr | fq_codel | all | 1760 | 0.57 | 0.33 | 0.14 | -0.04 | 3160 | 0.71 | 0.11 | 0.17 | 0.01 | 0.00 | 0.0 |
| bbr | mixab | all | 595 | 0.81 | 0.38 | 0.02 | -0.21 | 1353 | 0.76 | 0.08 | 0.17 | 0.00 | 0.00 | 0.0 |
| bbr | pfifo | all | 7903 | 0.84 | 0.36 | -0.02 | -0.18 | 18946 | 0.70 | 0.11 | 0.19 | 0.00 | 0.00 | 0.0 |
| bbr | pie | all | 1110 | 0.90 | 0.46 | -0.05 | -0.31 | 1774 | 0.66 | 0.08 | 0.16 | 0.10 | 0.00 | 0.0 |
| bbr | red | all | 143 | 0.88 | 0.42 | -0.09 | -0.21 | 165 | 0.75 | 0.11 | 0.14 | 0.00 | 0.00 | 0.0 |
| copa | all | surge | 288 | 0.96 | 0.33 | -0.01 | -0.28 | 642 | 0.75 | 0.04 | 0.21 | 0.00 | 0.00 | 0.0 |
| copa | codel | all | 144 | 0.99 | 0.34 | -0.02 | -0.31 | 402 | 0.74 | 0.02 | 0.23 | 0.00 | 0.00 | 0.0 |
| copa | pfifo | all | 144 | 0.93 | 0.32 | -0.00 | -0.24 | 240 | 0.76 | 0.07 | 0.16 | 0.00 | 0.00 | 0.0 |
