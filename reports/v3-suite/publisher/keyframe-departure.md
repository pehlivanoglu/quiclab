# Keyframe departure from the publisher (existing synchronized runs)

| run | pub link Mb/s | clients | calm GOPs | span first->last packet ms p50 / p90 / max | summed keyframes / pub link ms (p50) |
|---|---|---|---|---|---|
| night-sync/G0/grp-randloss-pfifo-r1 | 100 | 5 | 204 | 69.2 / 124.4 / 440.6 | 17.6 |
| night-sync/G0/grp-randloss-pfifo-r2 | 100 | 5 | 209 | 64.0 / 126.3 / 1397.4 | 17.6 |
| night-sync/M1/grp-burstcap-pie-r1 | 100 | 5 | 192 | 65.1 / 225.2 / 768.7 | 17.5 |
| night-sync/K1/grp-hier-pie-r1 | 100 | 7 | 679 | 65.8 / 255.8 / 765.1 | 25.0 |
| night-sync/K1/grp-hier-codel-r2 | 100 | 7 | 682 | 63.8 / 181.2 / 926.5 | 25.0 |
| night-sync/C1/grp-burstlongsplit-pfifo-r3 | 100 | 7 | 295 | 61.6 / 127.4 / 417.8 | 25.3 |
| night-sync/G0/grp-calmuneven-pfifo-r1 | 1000 | 17 | 108 | 57.8 / 142.9 / 328.4 | 9.5 |
| night-sync/G0/grp-calmuneven-pfifo-r2 | 1000 | 17 | 108 | 44.8 / 150.7 / 405.6 | 9.5 |

## Per client: median rank of the first packet among the clients, keyframe emission time p50/p90 ms, BBR pacing Mb/s (median)

- night-sync/G0/grp-randloss-pfifo-r1: sub-a rank 2.0 emis 33.8/66.7 pacing 2.8; sub-b rank 2.0 emis 43.5/74.7 pacing 6.2; sub-c rank 2.0 emis 39.0/71.0 pacing 6.8; sub-ctrl rank 2.0 emis 40.9/72.3 pacing 7.5; sub-d rank 2.0 emis 43.6/87.4 pacing 13.9
- night-sync/G0/grp-randloss-pfifo-r2: sub-a rank 2.0 emis 26.5/53.2 pacing 3.6; sub-b rank 2.0 emis 40.5/74.8 pacing 6.2; sub-c rank 2.0 emis 41.8/70.8 pacing 6.3; sub-ctrl rank 2.0 emis 34.9/75.4 pacing 7.7; sub-d rank 2.0 emis 46.1/88.5 pacing 13.2
- night-sync/M1/grp-burstcap-pie-r1: sub-a rank 2.0 emis 45.2/67.8 pacing 2.2; sub-b rank 2.0 emis 41.8/76.3 pacing 5.7; sub-c rank 2.0 emis 48.1/69.1 pacing 5.5; sub-ctrl rank 2.0 emis 3.5/32.4 pacing 72.1; sub-d rank 2.0 emis 51.0/81.3 pacing 11.3
- night-sync/K1/grp-hier-pie-r1: a1 rank 3.0 emis 37.1/59.5 pacing 2.5; a2 rank 3.0 emis 42.4/68.7 pacing 6.1; a3 rank 4.0 emis 50.4/72.2 pacing 11.5; b1 rank 3.0 emis 33.5/60.2 pacing 2.5; b2 rank 3.0 emis 43.5/68.2 pacing 6.1; b3 rank 3.0 emis 51.1/76.1 pacing 11.5; sub-ctrl rank 3.0 emis 3.5/32.0 pacing 100.0
- night-sync/K1/grp-hier-codel-r2: a1 rank 3.0 emis 34.5/60.5 pacing 2.4; a2 rank 3.0 emis 40.5/65.4 pacing 6.3; a3 rank 3.0 emis 49.8/68.5 pacing 11.3; b1 rank 3.0 emis 33.1/58.6 pacing 2.6; b2 rank 3.0 emis 41.3/60.7 pacing 6.3; b3 rank 3.0 emis 50.7/69.5 pacing 10.9; sub-ctrl rank 3.0 emis 3.4/9.8 pacing 102.4
- night-sync/C1/grp-burstlongsplit-pfifo-r3: a1 rank 3.0 emis 28.9/53.0 pacing 2.0; a2 rank 3.0 emis 38.3/61.0 pacing 4.5; a3 rank 3.0 emis 50.2/67.5 pacing 9.1; b1 rank 3.0 emis 30.3/51.0 pacing 2.0; b2 rank 3.0 emis 38.8/61.5 pacing 4.9; b3 rank 3.0 emis 49.9/67.7 pacing 9.6; sub-ctrl rank 3.0 emis 3.6/33.0 pacing 85.5
- night-sync/G0/grp-calmuneven-pfifo-r1: a1 rank 8.0 emis 36.6/82.9 pacing 15.0; a2 rank 9.0 emis 32.9/64.2 pacing 143.4; b1 rank 8.0 emis 5.5/8.1 pacing 20.9; b2 rank 7.0 emis 4.9/32.8 pacing 77.4; b3 rank 9.0 emis 5.9/33.0 pacing 62.9; b4 rank 8.0 emis 6.4/33.0 pacing 104.9; b5 rank 7.0 emis 36.0/56.4 pacing 23.4; c1 rank 9.0 emis 4.4/6.9 pacing 23.6; c2 rank 7.0 emis 5.8/8.0 pacing 21.1; c3 rank 8.0 emis 25.8/42.4 pacing 11.6; c4 rank 8.0 emis 6.7/32.8 pacing 49.4; c5 rank 9.5 emis 6.0/32.9 pacing 53.0; c6 rank 9.0 emis 5.1/32.7 pacing 147.5; c7 rank 9.0 emis 7.1/32.8 pacing 143.8; c8 rank 8.0 emis 6.7/32.6 pacing 171.1; c9 rank 8.0 emis 7.5/33.5 pacing 240.6; sub-ctrl rank 7.5 emis 5.6/32.8 pacing 65.3
- night-sync/G0/grp-calmuneven-pfifo-r2: a1 rank 8.5 emis 4.7/32.8 pacing 150.0; a2 rank 9.0 emis 32.8/57.4 pacing 133.4; b1 rank 6.0 emis 4.2/7.1 pacing 24.6; b2 rank 8.0 emis 6.3/33.1 pacing 57.8; b3 rank 8.0 emis 5.0/33.0 pacing 72.9; b4 rank 8.5 emis 7.8/33.3 pacing 100.2; b5 rank 8.0 emis 36.8/55.1 pacing 25.4; c1 rank 8.0 emis 3.0/7.5 pacing 35.2; c2 rank 8.0 emis 6.1/9.2 pacing 18.0; c3 rank 8.0 emis 4.8/33.0 pacing 73.4; c4 rank 10.0 emis 5.7/32.7 pacing 58.2; c5 rank 5.5 emis 5.8/33.0 pacing 55.5; c6 rank 6.5 emis 5.3/32.8 pacing 138.2; c7 rank 8.0 emis 5.6/33.2 pacing 132.4; c8 rank 10.0 emis 32.4/45.3 pacing 31.3; c9 rank 8.0 emis 7.4/33.4 pacing 241.6; sub-ctrl rank 9.0 emis 6.1/32.8 pacing 54.4
