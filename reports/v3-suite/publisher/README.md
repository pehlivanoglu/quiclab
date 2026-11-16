# Publisher link and keyframe departure (2026-11-14)

Script: [keyframe_departure.py](keyframe_departure.py); output: [keyframe-departure.md](keyframe-departure.md)
and [keyframe-departure.json](keyframe-departure.json). Existing synchronized runs with per-packet
sender logs (night campaign 2026-11-14), calm GOPs only (outside stimulus windows +- 1 s).

## The 5.85 ms came from a 1000 Mb/s publisher link, not 100 Mb/s

The S-JOIN emission times (keyframe 5.85 ms, P 1.16 ms) were measured on G0 calmuneven. The
uneven topology's scenario already sets pub -> r1 to **1000 Mb/s**. On the base and split runs,
where pub -> first router is 100 Mb/s, keyframes do not leave at 100 Mb/s. They leave at each
connection's BBR pacing rate:

| topology (runs) | pub link | GOP span, first -> last keyframe packet of any client, ms p50 / p90 | summed keyframes / pub link, ms | per-client keyframe emission p50, ms | BBR pacing p50, Mb/s |
|---|---|---|---|---|---|
| base (G0 randloss r1, r2; M1 burstcap pie r1) | 100 | 64-69 / 124-225 | 17.5-17.6 | 1000 kb/s 27-45; 2500 kb/s 39-48; 5000 kb/s 44-51 | 2.2-3.6; 5.5-6.8; 11.3-13.9 |
| split (K1 hier pie r1, codel r2; C1 burstlongsplit pfifo r3) | 100 | 62-66 / 127-256 | 25.0-25.3 | a1/b1 29-37; a2/b2 38-44; a3/b3 50-51 | 2.0-2.6; 4.5-6.3; 9.1-11.5 |
| uneven (G0 calmuneven r1, r2) | 1000 | 45-58 / 143-151 | 9.5 | mostly 3-8 ms, some 25-37 ms (see below) | 11-242 |

The per-client numbers match keyframe bytes / pacing rate. For example, a 5000 kb/s keyframe
(~76 kB) at 11.5 Mb/s takes ~53 ms, and 50-51 ms is measured. The instrumented clients' summed
pacing is ~25-40 Mb/s, so the 100 Mb/s link did not set their keyframe rate. sub-ctrl, however,
paces at 72-102 Mb/s in 4 of the 6 runs (M1, K1 x2, C1; its keyframe leaves in ~3.5 ms). During
those milliseconds the 100 Mb/s link can be the limit. Whether a queue formed there is not
known: that egress was not traced.

Method note: the keyframe's end is the packet that brings the payload sent since its write to
the keyframe size, minus one packet. The tail of a keyframe can ride in the next frame's first
packet. An earlier version that cut at the next frame's write, or did not allow for that tail,
put the end at ~33 ms.

## The r1:a1 outlier

calmuneven, a1 (5000 kb/s): r1 keyframe emission p50 36.6 ms with pacing 15.0 Mb/s; r2 4.7 ms
with pacing 150 Mb/s. Same topology, same 1000 Mb/s publisher link. Other connections show the
same split: b5 (8000 kb/s) at 23-25 Mb/s takes 36-37 ms in both reps; c3 r1 at 11.6 Mb/s takes
25.8 ms. The outlier is the connection's BBR bandwidth estimate (pacing rate), which differs
between reps, **not the publisher link**.

So the emission time of a 5000 kb/s keyframe is not one number. It is ~5 ms or ~35-50 ms
depending on the connection's pacing state. The pooled median 5.85 ms came from the fast mode.

## Changes

- Every v3 topology: pub -> first router 1000 Mb/s, delay unchanged (5 ms each way)
  (`FEED_MBPS` in scripts/v3_suite.py).
- GT-Q tracer: publisher egresses are traced like router egresses (rate-shaped, on a
  subscriber's forward path, delay-only netem):
  `mininet_backend.gtq_trace_interfaces`. For every topology from now on, not only v3. The
  publisher's queue shows up in router-trace/ and in gtq.py's truth as a queue without AQM.
- Smoke test: smoke-report.md now ends with the ASV emission times of every 5000 kb/s client
  and the keyframe departure table, both re-measured on the smoke's CALM runs. ASV_KEY_MS /
  ASV_P_MS are not changed automatically.
