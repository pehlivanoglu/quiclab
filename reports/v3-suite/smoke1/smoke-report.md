# Smoke: FAIL

Gating checks: 1_load_share, 2_ecn, 3_mtu, 4_health, 6_phase (scripts/v3_gate.py). Runs: 7.

| run | 1 load_share | 2 ecn | 3 mtu | 4 health | 5 surge | 6 phase |
|---|---|---|---|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-calm-access-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | ok | ok | ok | FAIL | ok | ok |

## Load and share per egress (target U, s)

| run | egress | hop | load (U) | share / 0.96 (s) |
|---|---|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-split4-pfifo-r1 | up | r1->r2 | 0.707 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-split4-pfifo-r1 | a | r2->switch-a | 0.708 (0.7) | 0.307 (0.3) |
| v3-SMOKE-calm-split4-pfifo-r1 | b | r2->switch-b | 0.709 (0.7) | 0.307 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | root | rr->r0 | 0.71 (0.7) | 0.309 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | X | r0->r1 | 0.712 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | Y | r0->r2 | 0.711 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | A | r1->switch-a | 0.71 (0.7) | 0.309 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | B | r1->switch-b | 0.708 (0.7) | 0.31 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | C | r2->switch-c | 0.713 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-tree16-pfifo-r1 | D | r2->switch-d | 0.71 (0.7) | 0.309 (0.3) |
| v3-SMOKE-calm-uneven-pfifo-r1 | A | r2->switch-a | 0.708 (0.7) | 0.307 (0.3) |
| v3-SMOKE-calm-uneven-pfifo-r1 | B | r2->switch-b | 0.71 (0.7) | 0.307 (0.3) |
| v3-SMOKE-calm-uneven-pfifo-r1 | C | r2->switch-c | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-access-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.307 (0.3) |
| v3-SMOKE-calm-rev-pfifo-r1 | main | r1->switch | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.309 (0.3) |

## Keyframe queueing peak (calm, 200 ms after each keyframe; not gating)

| run | egress | hop | n | p50 / p90 / max ms | 0.121 s U ms |
|---|---|---|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | main | router->switch | 43 | 22.9 / 26.4 / 29.9 | 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | up | r1->r2 | 43 | 22.1 / 25.8 / 28.6 | 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | a | r2->switch-a | 43 | 11.3 / 14.1 / 17.7 | 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | b | r2->switch-b | 43 | 12.2 / 14.1 / 27.8 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | root | rr->r0 | 43 | 21.8 / 25.0 / 27.2 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | X | r0->r1 | 43 | 11.1 / 13.8 / 15.1 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | Y | r0->r2 | 43 | 12.0 / 14.4 / 15.8 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | A | r1->switch-a | 43 | 6.3 / 9.7 / 12.9 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | B | r1->switch-b | 43 | 7.4 / 12.0 / 16.5 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | C | r2->switch-c | 43 | 7.8 / 10.7 / 11.7 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | D | r2->switch-d | 43 | 6.9 / 11.0 / 14.9 | 25.4 |
| v3-SMOKE-calm-uneven-pfifo-r1 | A | r2->switch-a | 43 | 23.2 / 27.3 / 41.5 | 25.4 |
| v3-SMOKE-calm-uneven-pfifo-r1 | B | r2->switch-b | 43 | 23.4 / 26.9 / 29.1 | 25.4 |
| v3-SMOKE-calm-uneven-pfifo-r1 | C | r2->switch-c | 43 | 22.6 / 25.4 / 29.1 | 25.4 |
| v3-SMOKE-calm-access-pfifo-r1 | main | router->switch | 43 | 22.0 / 26.0 / 34.9 | 25.4 |
| v3-SMOKE-calm-rev-pfifo-r1 | main | r1->switch | 43 | 19.6 / 22.3 / 27.5 | 25.4 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | router->switch | 65 | 14.6 / 24.0 / 30.1 | 25.4 |

## Installed AQM leaves (`tc qdisc show`, handle 20:; `ecn` must not appear; cake has no ECN switch)

- v3-SMOKE-calm-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-calm-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-calm-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-SMOKE-calm-split4-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-calm-split4-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-calm-split4-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-SMOKE-calm-split4-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-split4-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-SMOKE-calm-split4-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-SMOKE-calm-tree16-pfifo-r1 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-calm-tree16-pfifo-r1 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-calm-tree16-pfifo-r1 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-SMOKE-calm-tree16-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-tree16-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-SMOKE-calm-tree16-pfifo-r1 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-SMOKE-calm-tree16-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-tree16-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-SMOKE-calm-tree16-pfifo-r1 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-SMOKE-calm-tree16-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-tree16-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-SMOKE-calm-tree16-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-SMOKE-calm-uneven-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-calm-uneven-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-calm-uneven-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-uneven-pfifo-r1 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-SMOKE-calm-uneven-pfifo-r1 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-SMOKE-calm-uneven-pfifo-r1 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-SMOKE-calm-access-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-calm-access-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-calm-access-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-SMOKE-calm-access-pfifo-r1 ra/ra-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-access-pfifo-r1 ra/ra-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-SMOKE-calm-access-pfifo-r1 rb/rb-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-access-pfifo-r1 rb/rb-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-SMOKE-calm-access-pfifo-r1 rc/rc-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-access-pfifo-r1 rc/rc-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-SMOKE-calm-access-pfifo-r1 rd/rd-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-access-pfifo-r1 rd/rd-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-SMOKE-calm-rev-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-calm-rev-pfifo-r1 r0/r0-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-calm-rev-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-SMOKE-calm-rev-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 42p`
- v3-SMOKE-calm-rev-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-SMOKE-sburst-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-sburst-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-sburst-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`

## Health, surge, phase-lock details

- v3-SMOKE-calm-s030u070-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'router-eth1']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/7 (0.000e+00/7.681e-05, 0/1), router-eth1 3/0 (1.759e-04/0.000e+00, 1/0), router-eth2 1/1 (4.271e-06/4.271e-06, 1/1); recursion misses {'pub': 38, 'router': 38} vs unmatched 12; gaps within 10 % pub-eth0 0.87468, router-eth1 0.87415, router-eth2 0.99967; 20 ms within 5 % pub-eth0 nan (0), router-eth1 nan (0), router-eth2 1.0 (208); cpu idle min 0.9473; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.41}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-split4-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'r1-eth1']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/20 (0.000e+00/1.367e-04, 0/2), r1-eth1 0/1 (0.000e+00/5.896e-05, 0/1), r1-eth2 11/13 (2.715e-05/3.208e-05, 2/1), r2-eth2 3/7 (1.477e-05/3.446e-05, 1/1), r2-eth4 2/7 (9.852e-06/3.448e-05, 1/1); recursion misses {'pub': 223, 'r1': 223, 'r2': 223} vs unmatched 64; gaps within 10 % pub-eth0 0.79829, r1-eth1 0.83719, r1-eth2 0.99746, r2-eth2 0.99932, r2-eth4 0.99919; 20 ms within 5 % pub-eth0 nan (0), r1-eth1 nan (0), r1-eth2 1.0 (193), r2-eth2 1.0 (208), r2-eth4 1.0 (201); cpu idle min 0.9157; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.53, '30Hz': 4.2}, 'b': {'1Hz': 2.05, '30Hz': 1.96}, 'up': {'1Hz': 2.57, '30Hz': 2.29}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-tree16-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'r0-eth2', 'r0-eth4', 'r2-eth4', 'rr-eth1', 'rr-eth2']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/51 (0.000e+00/3.102e-04, 0/3), r0-eth2 10/17 (4.553e-05/7.740e-05, 1/2), r0-eth4 3/23 (1.367e-05/1.048e-04, 1/2), r1-eth2 4/2 (3.651e-05/1.826e-05, 1/1), r1-eth4 0/3 (0.000e+00/2.745e-05, 0/1), r2-eth2 4/4 (3.641e-05/3.641e-05, 1/1), r2-eth4 4/6 (3.663e-05/5.494e-05, 1/1), rr-eth1 2/2 (1.181e-04/1.181e-04, 1/1), rr-eth2 23/32 (5.253e-05/7.309e-05, 2/2); recursion misses {'pub': 667, 'rr': 667, 'r0': 667, 'r1': 667, 'r2': 667} vs unmatched 190; gaps within 10 % pub-eth0 0.5767, r0-eth2 0.99657, r0-eth4 0.99648, r1-eth2 0.99809, r1-eth4 0.99835, r2-eth2 0.99818, r2-eth4 0.99829, rr-eth1 0.75872, rr-eth2 0.98999; 20 ms within 5 % pub-eth0 nan (0), r0-eth2 1.0 (204), r0-eth4 1.0 (209), r1-eth2 1.0 (158), r1-eth4 1.0 (172), r2-eth2 1.0 (190), r2-eth4 1.0 (175), rr-eth1 nan (0), rr-eth2 1.0 (195); cpu idle min 0.8025; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 2.78, '30Hz': 3.02}, 'B': {'1Hz': 4.43, '30Hz': 4.68}, 'C': {'1Hz': 2.36, '30Hz': 6.65}, 'D': {'1Hz': 2.7, '30Hz': 2.74}, 'X': {'1Hz': 0.32, '30Hz': 4.21}, 'Y': {'1Hz': 3.42, '30Hz': 2.87}, 'root': {'1Hz': 2.6, '30Hz': 1.53}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-uneven-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'r1-eth1', 'r1-eth2', 'r2-eth1', 'r2-eth3']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/65 (0.000e+00/2.584e-04, 0/3), r1-eth1 8/3 (4.708e-04/1.766e-04, 2/1), r1-eth2 25/23 (1.066e-04/9.806e-05, 2/4), r2-eth1 4/8 (2.521e-05/5.041e-05, 1/1), r2-eth3 10/11 (4.645e-05/5.110e-05, 2/2), r2-eth5 12/9 (3.377e-05/2.533e-05, 1/1); recursion misses {'pub': 599, 'r1': 599, 'r2': 599} vs unmatched 178; gaps within 10 % pub-eth0 0.69297, r1-eth1 0.92597, r1-eth2 0.58431, r2-eth1 0.99944, r2-eth3 0.99862, r2-eth5 0.9973; 20 ms within 5 % pub-eth0 nan (0), r1-eth1 nan (0), r1-eth2 nan (0), r2-eth1 1.0 (208), r2-eth3 1.0 (210), r2-eth5 1.0 (200); cpu idle min 0.8866; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 0.97, '30Hz': 5.08}, 'B': {'1Hz': 0.32, '30Hz': 4.34}, 'C': {'1Hz': 2.74, '30Hz': 4.79}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-access-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'ra-eth1', 'rb-eth1', 'rc-eth1', 'router-eth1', 'router-eth2']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/33 (0.000e+00/3.628e-04, 0/2), ra-eth1 0/1 (0.000e+00/1.294e-04, 0/1), rb-eth1 1/0 (5.870e-05/0.000e+00, 1/0), rc-eth1 1/0 (5.906e-05/0.000e+00, 1/0), rd-eth1 0/1 (0.000e+00/3.089e-05, 0/1), router-eth1 7/0 (4.131e-04/0.000e+00, 2/0), router-eth2 19/3 (8.116e-05/1.281e-05, 2/1); recursion misses {'pub': 158, 'router': 158, 'ra': 158, 'rb': 158, 'rc': 158, 'rd': 158} vs unmatched 66; gaps within 10 % pub-eth0 0.74675, ra-eth1 0.47761, rb-eth1 0.99465, rc-eth1 0.97353, rd-eth1 0.99791, router-eth1 0.79174, router-eth2 0.99821; 20 ms within 5 % pub-eth0 nan (0), ra-eth1 nan (0), rb-eth1 nan (0), rc-eth1 nan (0), rd-eth1 1.0 (9), router-eth1 nan (0), router-eth2 1.0 (205); cpu idle min 0.8878; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.39}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-rev-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'r0-eth1', 'r0-eth2']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/16 (0.000e+00/1.758e-04, 0/2), r0-eth1 0/0 (0.000e+00/0.000e+00, 0/0), r0-eth2 11/2 (1.486e-04/2.701e-05, 2/1), r1-eth2 3/3 (1.281e-05/1.281e-05, 1/1); recursion misses {'pub': 90, 'r0': 90, 'r1': 90} vs unmatched 35; gaps within 10 % pub-eth0 0.80464, r0-eth1 0.79328, r0-eth2 0.99833, r1-eth2 0.99946; 20 ms within 5 % pub-eth0 nan (0), r0-eth1 nan (0), r0-eth2 1.0 (1), r1-eth2 1.0 (214); cpu idle min 0.9414; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.4}}; surge []; fq collisions None; errors []
- v3-SMOKE-sburst-s030u070-pfifo-r1: lost 0; egresses failing ['pub-eth0', 'router-eth1']; unmatched deq/enq (ratio, max per 200 ms) pub-eth0 0/19 (0.000e+00/1.398e-04, 0/1), router-eth1 2/0 (7.859e-05/0.000e+00, 1/0), router-eth2 6/4 (1.671e-05/1.114e-05, 1/1); recursion misses {'pub': 102, 'router': 102} vs unmatched 31; gaps within 10 % pub-eth0 0.86366, router-eth1 0.93043, router-eth2 0.99948; 20 ms within 5 % pub-eth0 nan (0), router-eth1 nan (0), router-eth2 1.0 (527); cpu idle min 0.9454; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.66, '30Hz': 1.92}}; surge [('router->switch', 1.15, 1.125)]; fq collisions None; errors []

## Emission times (re-measured, not gating)

Per run and client: median BBR pacing (Mb/s), keyframe and P-frame emission (ms), calm GOPs:

- v3-SMOKE-calm-s030u070-pfifo-r1: emission sub-a 24.0 Mb/s key 4.46 P 0.0; sub-b 103.06 Mb/s key 3.51 P 0.0; sub-c 68.44 Mb/s key 4.9 P 1.13; sub-ctrl 84.72 Mb/s key 4.62 P 0.0; sub-d 131.66 Mb/s key 4.82 P 1.16
- v3-SMOKE-calm-split4-pfifo-r1: emission a1 23.34 Mb/s key 4.61 P 0.0; a2 23.67 Mb/s key 4.4 P 0.0; a3 78.22 Mb/s key 3.48 P 0.0; a4 101.61 Mb/s key 6.02 P 1.16; b1 28.45 Mb/s key 3.68 P 0.0; b2 32.94 Mb/s key 3.2 P 0.0; b3 63.53 Mb/s key 4.95 P 1.15; b4 126.99 Mb/s key 5.92 P 1.16; sub-ctrl 51.65 Mb/s key 6.19 P 1.18
- v3-SMOKE-calm-tree16-pfifo-r1: emission a1 19.03 Mb/s key 2.82 P 0.0; a2 22.68 Mb/s key 4.61 P 0.0; a3 22.77 Mb/s key 4.64 P 0.0; a4 53.42 Mb/s key 6.22 P 1.15; b1 14.64 Mb/s key 3.45 P 0.0; b2 22.29 Mb/s key 4.78 P 0.0; b3 19.47 Mb/s key 5.49 P 0.0; b4 56.81 Mb/s key 5.95 P 1.15; c1 21.31 Mb/s key 2.36 P 0.0; c2 25.14 Mb/s key 4.34 P 0.0; c3 20.2 Mb/s key 5.28 P 0.0; c4 63.7 Mb/s key 5.16 P 1.15; d1 18.07 Mb/s key 2.78 P 0.0; d2 24.34 Mb/s key 4.51 P 0.0; d3 21.18 Mb/s key 5.5 P 0.0; d4 54.1 Mb/s key 6.03 P 1.14; sub-ctrl 46.84 Mb/s key 7.25 P 1.17
- v3-SMOKE-calm-uneven-pfifo-r1: emission a1 84.24 Mb/s key 4.65 P 0.0; a2 153.55 Mb/s key 4.8 P 0.0; b1 16.53 Mb/s key 3.33 P 0.0; b2 26.7 Mb/s key 3.88 P 0.0; b3 22.33 Mb/s key 4.81 P 0.0; b4 75.96 Mb/s key 4.4 P 0.0; b5 141.47 Mb/s key 4.89 P 1.15; c1 13.37 Mb/s key 3.76 P 0.0; c2 15.06 Mb/s key 3.68 P 0.0; c3 18.67 Mb/s key 5.53 P 0.0; c4 16.44 Mb/s key 6.57 P 0.0; c5 35.43 Mb/s key 2.92 P 0.0; c6 120.65 Mb/s key 3.54 P 0.0; c7 69.23 Mb/s key 4.75 P 0.0; c8 66.92 Mb/s key 4.79 P 1.14; c9 152.22 Mb/s key 4.78 P 0.0; sub-ctrl 78.53 Mb/s key 4.64 P 1.13
- v3-SMOKE-calm-access-pfifo-r1: emission sub-a 33.32 Mb/s key 3.21 P 0.0; sub-b 81.01 Mb/s key 3.53 P 0.0; sub-c 60.1 Mb/s key 5.78 P 1.16; sub-ctrl 46.1 Mb/s key 7.31 P 1.22; sub-d 116.52 Mb/s key 6.15 P 1.18
- v3-SMOKE-calm-rev-pfifo-r1: emission sub-a 30.36 Mb/s key 3.58 P 0.0; sub-b 67.44 Mb/s key 5.09 P 1.13; sub-c 77.0 Mb/s key 4.56 P 0.0; sub-ctrl 45.93 Mb/s key 7.02 P 1.14; sub-d 143.12 Mb/s key 4.85 P 1.12

```
{
 "runs": [
  {
   "run": "v3-SMOKE-calm-s030u070-pfifo-r1:sub-d",
   "keyframes": 54,
   "key_ms_p50": 4.82,
   "key_ms_p90": 7.0,
   "p_frames": 1548,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.18
  },
  {
   "run": "v3-SMOKE-calm-split4-pfifo-r1:a4",
   "keyframes": 54,
   "key_ms_p50": 5.96,
   "key_ms_p90": 8.31,
   "p_frames": 1540,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.22
  },
  {
   "run": "v3-SMOKE-calm-split4-pfifo-r1:b4",
   "keyframes": 53,
   "key_ms_p50": 5.88,
   "key_ms_p90": 7.28,
   "p_frames": 1542,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.22
  },
  {
   "run": "v3-SMOKE-calm-uneven-pfifo-r1:a2",
   "keyframes": 54,
   "key_ms_p50": 4.77,
   "key_ms_p90": 7.02,
   "p_frames": 1552,
   "p_ms_p50": 0.0,
   "p_ms_p90": 1.23
  },
  {
   "run": "v3-SMOKE-calm-uneven-pfifo-r1:b5",
   "keyframes": 54,
   "key_ms_p50": 4.87,
   "key_ms_p90": 6.15,
   "p_frames": 1556,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.23
  },
  {
   "run": "v3-SMOKE-calm-uneven-pfifo-r1:c9",
   "keyframes": 54,
   "key_ms_p50": 4.04,
   "key_ms_p90": 5.96,
   "p_frames": 1555,
   "p_ms_p50": 0.0,
   "p_ms_p90": 1.23
  },
  {
   "run": "v3-SMOKE-calm-access-pfifo-r1:sub-d",
   "keyframes": 54,
   "key_ms_p50": 6.09,
   "key_ms_p90": 8.17,
   "p_frames": 1553,
   "p_ms_p50": 1.18,
   "p_ms_p90": 1.26
  },
  {
   "run": "v3-SMOKE-calm-rev-pfifo-r1:sub-d",
   "keyframes": 52,
   "key_ms_p50": 4.84,
   "key_ms_p90": 6.34,
   "p_frames": 1540,
   "p_ms_p50": 1.13,
   "p_ms_p90": 1.23
  }
 ],
 "pooled": {
  "key_ms_p50": 4.92,
  "p_ms_p50": 1.16
 }
}
```

```
# Keyframe departure from the publisher (existing synchronized runs)

| run | pub link Mb/s | clients | calm GOPs | span first->last packet ms p50 / p90 / max | summed keyframes / pub link ms (p50) |
|---|---|---|---|---|---|
| .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-s030u070-pfifo-r1 | 1000 | 5 | 48 | 6.7 / 34.0 / 158.9 | 1.8 |
| .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-split4-pfifo-r1 | 1000 | 9 | 48 | 8.4 / 92.7 / 281.4 | 2.8 |
| .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-tree16-pfifo-r1 | 1000 | 17 | 48 | 9.4 / 34.8 / 177.5 | 3.0 |
| .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-uneven-pfifo-r1 | 1000 | 17 | 48 | 33.5 / 80.3 / 254.3 | 4.9 |
| .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-access-pfifo-r1 | 1000 | 5 | 48 | 8.7 / 34.4 / 83.6 | 1.8 |
| .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-rev-pfifo-r1 | 1000 | 5 | 48 | 8.6 / 34.4 / 176.5 | 1.8 |

## Per client: median rank of the first packet among the clients, keyframe emission time p50/p90 ms, BBR pacing Mb/s (median)

- .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-s030u070-pfifo-r1: sub-a rank 2.0 emis 4.5/14.4 pacing 24.0; sub-b rank 2.0 emis 3.5/14.9 pacing 103.1; sub-c rank 2.0 emis 4.9/32.9 pacing 68.4; sub-ctrl rank 3.0 emis 4.6/6.1 pacing 84.7; sub-d rank 2.5 emis 4.8/32.9 pacing 131.7
- .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-split4-pfifo-r1: a1 rank 3.0 emis 4.6/7.9 pacing 23.3; a2 rank 3.5 emis 4.4/7.8 pacing 23.7; a3 rank 5.0 emis 3.5/32.5 pacing 96.0; a4 rank 4.0 emis 6.0/33.1 pacing 101.6; b1 rank 4.5 emis 3.7/14.3 pacing 28.5; b2 rank 4.0 emis 3.2/4.7 pacing 32.9; b3 rank 5.0 emis 4.9/32.5 pacing 63.5; b4 rank 4.0 emis 5.9/32.0 pacing 127.9; sub-ctrl rank 4.0 emis 6.2/8.7 pacing 51.6
- .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-tree16-pfifo-r1: a1 rank 7.0 emis 2.8/32.8 pacing 19.0; a2 rank 5.5 emis 4.6/7.8 pacing 22.7; a3 rank 9.0 emis 4.6/7.4 pacing 22.8; a4 rank 7.5 emis 6.2/16.3 pacing 53.4; b1 rank 8.0 emis 3.5/32.8 pacing 14.6; b2 rank 9.5 emis 4.8/17.1 pacing 22.3; b3 rank 5.0 emis 5.5/8.4 pacing 19.5; b4 rank 8.0 emis 5.9/15.9 pacing 56.8; c1 rank 7.5 emis 2.4/33.3 pacing 21.3; c2 rank 7.0 emis 4.3/6.9 pacing 25.0; c3 rank 9.5 emis 5.3/8.0 pacing 20.2; c4 rank 8.0 emis 5.2/15.5 pacing 63.7; d1 rank 9.0 emis 2.8/33.3 pacing 18.1; d2 rank 8.5 emis 4.5/7.0 pacing 24.3; d3 rank 8.5 emis 5.5/8.6 pacing 21.2; d4 rank 9.0 emis 6.0/15.7 pacing 54.1; sub-ctrl rank 6.5 emis 7.3/11.2 pacing 46.8
- .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-uneven-pfifo-r1: a1 rank 8.5 emis 4.6/7.6 pacing 84.2; a2 rank 7.5 emis 4.8/32.8 pacing 153.6; b1 rank 9.0 emis 3.3/33.0 pacing 15.7; b2 rank 4.5 emis 3.9/6.1 pacing 26.7; b3 rank 9.0 emis 4.8/15.8 pacing 22.3; b4 rank 8.0 emis 4.4/6.5 pacing 76.0; b5 rank 8.5 emis 4.9/16.1 pacing 141.5; c1 rank 10.0 emis 3.8/33.1 pacing 14.2; c2 rank 9.0 emis 3.7/33.2 pacing 15.7; c3 rank 8.0 emis 5.5/9.0 pacing 18.7; c4 rank 10.0 emis 6.6/11.4 pacing 16.4; c5 rank 7.0 emis 2.9/6.0 pacing 35.4; c6 rank 7.0 emis 3.5/32.7 pacing 120.6; c7 rank 8.5 emis 4.7/32.3 pacing 69.2; c8 rank 6.0 emis 4.8/7.3 pacing 66.9; c9 rank 8.5 emis 4.8/14.7 pacing 152.2; sub-ctrl rank 6.0 emis 4.6/6.7 pacing 78.7
- .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-access-pfifo-r1: sub-a rank 1.0 emis 3.2/6.4 pacing 33.3; sub-b rank 2.0 emis 3.5/14.2 pacing 81.0; sub-c rank 2.0 emis 5.8/32.8 pacing 60.1; sub-ctrl rank 3.0 emis 7.3/10.3 pacing 46.1; sub-d rank 2.0 emis 6.2/15.9 pacing 117.2
- .runs/2026-11-14_1730_v3-smoke/v3-SMOKE-calm-rev-pfifo-r1: sub-a rank 2.0 emis 3.6/33.3 pacing 30.4; sub-b rank 2.0 emis 5.1/32.7 pacing 67.4; sub-c rank 2.0 emis 4.6/33.0 pacing 77.0; sub-ctrl rank 2.0 emis 7.0/17.3 pacing 45.9; sub-d rank 2.0 emis 4.9/15.0 pacing 143.1
```

