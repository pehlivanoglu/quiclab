# What-if for CC-driven rate adaptation (K5-sender note, 1.8; v3 runs, 2026-11-17)

**Answer: CC-driven adaptation would react after our alarm: BBR's estimate falls below the nominal rate ~0.25-0.6 s
(p50) after the frozen alarm, and before the first GOP drop in 94-99 % of the onsets that lead to one.** The cut
comes first in only 2-6 % of onsets. These are open-loop logs: the video never sent less in these runs, so this
cannot show the closed loop (what the estimate does once the video follows it).

Rule tested: target = x * estimate; a cut is in force while target < nominal (the client's produced media rate).
Estimate: BBR's bandwidth estimate (cc.csv bw_est_bps); Copa cwnd x 8 / srtt. x in {0.7, 0.85, 1.0} (P).

## Calm time: estimate / nominal

BBR, calm runs (C1a / C1b), median over clients: p50 3.0-6.6, p5 1.4-4.9 at every operating point and rate. The
lowest are at s065u085 (2.5 Mb/s: p5 1.42, p50 1.90). The estimate does not move across a GOP (per-100-ms-bin medians
within 1 % of the p50; s065u085 2.5 Mb/s 0.94-1.01).
- Why so high: the transport marks the connection app-limited when it has nothing to send (mvfst
  QuicTransportBaseLite.cpp:1913). BBR then keeps an app-limited sample only when it is at least the current
  maximum (BbrBandwidthSampler.cpp:166-175). Keyframe bursts leave at the bottleneck share and give high samples.
  Lower app-limited samples are dropped, so the estimate holds the burst rate.
Copa (M13 calm stretches, 1-3 client-minutes only): cwnd / srtt is 7-17x nominal (p50), 15-20x for the 1 Mb/s
client. Copa supports no app-limited state (Copa.cpp:438), so its cwnd grows while unused (R2).

False cuts in calm time (entries into the cut state per client-minute; share of calm time cut):

| CC | rate Mb/s | calm client-min | x 0.7 | x 0.85 | x 1.0 |
|---|---|---|---|---|---|
| BBR | 0.5 | 42 | 0.00, 0.00 | 0.00, 0.00 | 0.00, 0.00 |
| BBR | 1.0 | 149 | 0.30, 0.00 | 0.13, 0.00 | 0.05, 0.00 |
| BBR | 2.5 | 165 | 1.72, 0.01 | 0.65, 0.00 | 0.12, 0.00 |
| BBR | 5.0 | 73 | 0.88, 0.01 | 0.10, 0.00 | 0.00, 0.00 |
| Copa | 1.0-5.0 | 5 | 0 | 0 | 0 |

## After a GT3 onset

Per onset with a frozen alarm (alarm in [t_on - 1 s, t_on + 10 s]); r1 / r2:

| CC | AQM, stimulus | x | onsets | cut within 10 s | cut - alarm p50 s | cut before alarm | alarm - t_on p50 s | cut before the first GOP drop (n) |
|---|---|---|---|---|---|---|---|---|
| BBR | all | 0.7 | 17869 / 18234 | 0.96 / 0.95 | 0.60 / 0.58 | 0.04 / 0.04 | 0.23 / 0.22 | 0.99 / 0.99 (13278 / 13748) |
| BBR | all | 0.85 | | 0.92 / 0.92 | 0.63 / 0.62 | 0.03 / 0.02 | | 0.98 / 0.98 |
| BBR | all | 1.0 | | 0.87 / 0.87 | 0.67 / 0.63 | 0.02 / 0.02 | | 0.94 / 0.94 |
| BBR | pfifo surge | 0.85 | 8567 / 8609 | 0.92 / 0.93 | 0.27 / 0.26 | 0.03 / 0.03 | 0.23 / 0.22 | 0.99 / 0.99 |
| BBR | codel surge | 0.85 | 5532 / 5863 | 0.92 / 0.93 | 1.17 / 1.14 | 0.01 / 0.01 | 0.22 / 0.22 | 0.96 / 0.95 |
| Copa | all | 0.85 | 318 / 324 | 0.78 / 0.80 | 0.42 / 0.39 | 0.03 / 0.02 | 0.22 / 0.21 | 0.91 / 0.92 |
| Copa | pfifo surge | 0.85 | 119 / 121 | 0.47 / 0.52 | 0.45 / 0.47 | 0.05 / 0.03 | 0.22 / 0.21 | 0.70 / 0.71 |

Reading:
- **BBR: the cut comes ~0.25 s after our alarm on pfifo, ~1.1 s on codel (p50), 0.6 s pooled.** The frozen alarm is at
  ~0.22 s after the onset, the first GOP drop ~2 s after the alarm (1.4), so the cut usually lands in between.
- The lower x, the more onsets get a cut and the earlier, but the more false cuts in calm (2.5 Mb/s: 1.72 per
  minute at x 0.7 against 0.12 at x 1.0).
- **Copa on pfifo: no cut in about half the onsets.** cwnd / srtt stays above the nominal rate of the low-rate
  clients (R2: Copa allows 4-5x the 1 Mb/s video rate under load). On codel the cut is found in 94-97 %.
- Per AQM and stimulus: [tables.md](tables.md). join and tcp cells are small and the slowest (cut 2-4 s after the
  alarm).

## Downward spiral?

Unlikely for BBR, from the code and the calm data. The closed loop is not shown.
- Once the video sends less, its packets are app-limited. BBR ignores lower app-limited samples, so the estimate
  does not follow the video down: it holds the last non-app-limited maximum.
- It can still rise: an app-limited sample at or above the maximum is kept, and keyframe bursts give such samples.
  The calm estimate sits 3-6x above the video rate for this reason.
- The opposite risk is likelier: the estimate is stale. After congestion ends it may stay low until a burst lifts
  it; during congestion a burst sample can lift it early (oscillation).
- Copa: cwnd / srtt grows while unused, so no spiral, but the cut often never comes for low-rate clients.

## Proposal for Part 2 (P / FLAG; the user decides)

- **x = 0.85.** Cut before the first drop in 98 % of the onsets, at most 0.65 false cuts per client-minute in calm
  (2.5 Mb/s), 92 % of the onsets cut. x = 1.0 misses more (87 %), x = 0.7 cuts too often in calm.
- **Floor = 0.3 x nominal.** Bounds the harm of a stale low estimate; about the gap between two ladder steps
  (e.g. 2.5 -> 1 Mb/s is 0.4, 1 -> 0.5 is 0.5).
- **Recovery rule: none in the first version.** The estimate cannot spiral down from app-limited samples (above).
  The K5 gate's adaptation run checks for stale-low periods (target below nominal while the bottleneck queue is
  empty). If they show, add one estimate-only rule: after N GOPs below nominal, raise the target by one ladder step
  for one GOP (a probe) and keep it unless the estimate cuts again. It reads nothing from our detector or grouping.

Code: [aw.py](aw.py), [aw_report.py](aw_report.py); rows.jsonl. Batch: nice 19, 2 workers; nothing written inside
run folders.
