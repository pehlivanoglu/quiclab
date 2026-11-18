# Sender policy on the v3 runs (K5-sender note, Part 1; 2026-11-17)

Status: 1.1, 1.2, 1.4 and 1.5 done (reported first, as asked). 1.3, 1.6 and 1.7 follow. 1.8 is in
[../adapt-whatif-2026-11-17/](../adapt-whatif-2026-11-17/).

## 1.1 The drop rule, from the code

Confirmed: the drop removes the queued tail of a GOP and never recalls what QUIC already has.
- qvideo/src/SendQueue.h, `dropStale()`:
  - while the frame at the head of the queue is older than the limit (send_buffer_ms = 1000), it drops that frame
    and every queued frame of the same GOP (the queue is FIFO in frame order, so they sit together at the head);
  - it then sets `skippingGop_`, so `push()` also drops that GOP's frames still to be produced;
  - sending resumes with the next GOP's keyframe.
  - If the next GOP's keyframe is also stale, the loop drops that whole GOP too.
- Server.cpp `pump()` hands frames to QUIC only while QUIC's unsent bytes are below one cwnd. Frames already
  written to QUIC (`writeFrame`, the GOP's stream) are not recalled: they are sent, late if need be. QUIC also
  retransmits their losses (stream data is reliable).
- So a drop is always a suffix of one GOP, from the stale frame to the next keyframe: never an isolated frame in
  the middle of a GOP. The frames before it (the prefix) were sent and stay decodable. A drop that starts at the
  keyframe removes the whole GOP.
- The next written frame carries `skippedBefore` (the number of frames dropped just before it), so the client
  knows.

## 1.2 Does GT-H count frames dropped at the sender?

**Yes.** scripts/gtq.py:
- `frame_table()` reads the sender's drops.csv and marks those frames `dropped = True`, with t_gen = drop time -
  age.
- Their receive time is left empty, so `deadline_misses()` counts them as misses at t_gen + B (B = 300 / 600 / 1000
  ms), provided t_gen + B falls before the end of the client's log.
- `harm()` then makes a GT-Q episode harmful when a frame generated in its collar misses.
- A dropped frame is at least 1000 ms old, so it would also have missed the 600 ms budget had it been sent.

Check on the data (windows with at least one GOP drop, GT-Q valid): a harmful GT-H 600 episode of an expected
client has t_harm in the window span in all but 1 of 2 599 windows (r1 0 of 1 254, r2 1 of 1 345).

GT-H does not count frames that were delivered but cannot be decoded because an earlier frame of their GOP was
dropped or late. That is in Part 4's harm list, not in GT-H.

## 1.4 Alarm against drop

Windows with at least one GOP drop; window span until every expected client's send queue is back below half its
limit (oldest frame < 500 ms), at most 30 s after the window end. Single-queue AQM cells, r1 / r2:

| detector | alarm before the first drop | alarm start to first drop p10 / p50 / p90 s | drops with the alarm on | drops with no alarm start before them |
|---|---|---|---|---|
| v2-owd | 0.98 / 0.97 | 1.29 / 2.01 / 4.18 ; 1.25 / 2.00 / 4.00 | 1.00 / 1.00 | 0.03 / 0.04 |
| D1-bw | 0.96 / 0.95 | 1.00 / 1.86 / 4.16 ; 0.99 / 1.85 / 4.04 | 0.85 / 0.85 | 0.10 / 0.09 |
| D2-gcc | 0.99 / 0.98 | 1.23 / 2.01 / 4.21 ; 1.17 / 2.00 / 4.03 | 0.01 / 0.01 | 0.01 / 0.01 |
| D3-10ms-200ms | 0.99 / 0.98 | 1.21 / 1.98 / 4.24 ; 1.15 / 1.96 / 3.99 | 0.83 / 0.83 | 0.01 / 0.02 |

Reading:
- **Every detector alarms ~2 s before the first drop (p50); p10 ~1.0-1.3 s.** The 1 s limit means a drop needs at
  least 1 s of backlog, so even BBR's slow bandwidth estimate (D1-bw) comes first in 95 % of the windows.
- **v2-owd has its alarm on at 100 % of the drop events.** D1-bw and D3 at 83-85 %. GCC's overuse state flips at
  every trendline update, so it is almost never "on" at the instant (1 %), although its alarm started before.
- The "no alarm start before the drop" column counts a drop as uncovered when the client's alarm started before the
  window (held over from earlier congestion). That is why v2-owd, whose hold keeps the alarm on, shows 3-4 %
  there while being on at 100 %.
- Lead by intensity (v2-owd p50, pooled reps): pfifo 4.3 / 2.2 / 1.4 s at u 1.05 / 1.15 / 1.3; codel 4.4 / 2.8 /
  2.0; pie 3.8 / 2.7 (u 1.15 / 1.3); fq_codel 2.5 / 1.9 / 1.8.
- fq_codel / cake: v2-owd before the first drop in 97 / 92 % of windows, p50 1.9 s, on at 100 % of the drops.
- Copa (M13): v2-owd, GCC and D3 alarm before the drop in 100 % of the windows (p50 ~2 s). D1-bw does not apply
  (it reads BBR's state).

Full tables: [tables-1.2-1.4.md](tables-1.2-1.4.md).

## 1.5 Pre-drop / post-drop split

**The headline detector and grouping results do not depend on the sender's drops.** Report:
[../drop-split-2026-11-17/README.md](../drop-split-2026-11-17/README.md). In short, single-queue cells:
- the first alarm comes before the first drop in 99-100 % of drop windows (p50 2.0 s earlier), and 99 % of the
  SETS onsets in those windows are before the drop;
- v2-owd before t_drop: GT3 P 1.00, R 0.99, p50 212 / 204 ms; in windows with no drop: R 0.87 / 0.84, p50 250 /
  237 ms (milder congestion);
- grouping pair P (k = 2): 0.998 / 0.979 over all windows, 1.000 / 0.987 in no-drop windows, 0.996 / 0.974
  before t_drop.

The 1.5 window span is [start, end + 2 s]; 1.4 uses the longer queue-recovery span. That is why 1.4 finds slightly
more drop windows.

Code: [sp.py](sp.py) (1.2, 1.4), ../drop-split-2026-11-17/ds.py (1.5). Batch: nice 19, 2 workers; nothing written
inside run folders.
