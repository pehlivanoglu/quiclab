# Gate: PASS

Gating checks: 1_load_share, 2_ecn, 3_mtu, 4_health, 5_surge, 6_phase (scripts/v3_gate.py). Runs: 9.

| run | 1 load_share | 2 ecn | 3 mtu | 4 health | 5 surge | 6 phase |
|---|---|---|---|---|---|---|
| v3-G1-calm-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G1-calm-legacy-pfifo-r1 | ok | ok | ok | ok | - | - |
| v3-G2-calm-split4-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-tree16-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-uneven-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-access-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-rev-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G3-sburst-s030u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-G3-sburst-s030u070-fq_codel-r1 | ok | ok | ok | ok | ok | ok |

## Load and share per egress (target U, s)

| run | egress | hop | load (U) | share / 0.96 (s) |
|---|---|---|---|---|
| v3-G1-calm-s030u070-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-G1-calm-legacy-pfifo-r1 | main | router->switch | 0.669 (0.65) | 1.008 (1.0) |
| v3-G2-calm-split4-pfifo-r1 | up | r1->r2 | 0.706 (0.7) | 0.308 (0.3) |
| v3-G2-calm-split4-pfifo-r1 | a | r2->switch-a | 0.708 (0.7) | 0.307 (0.3) |
| v3-G2-calm-split4-pfifo-r1 | b | r2->switch-b | 0.707 (0.7) | 0.308 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | root | rr->r0 | 0.708 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | X | r0->r1 | 0.711 (0.7) | 0.308 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | Y | r0->r2 | 0.71 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | A | r1->switch-a | 0.71 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | B | r1->switch-b | 0.709 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | C | r2->switch-c | 0.712 (0.7) | 0.308 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | D | r2->switch-d | 0.709 (0.7) | 0.309 (0.3) |
| v3-G2-calm-uneven-pfifo-r1 | A | r2->switch-a | 0.705 (0.7) | 0.307 (0.3) |
| v3-G2-calm-uneven-pfifo-r1 | B | r2->switch-b | 0.709 (0.7) | 0.307 (0.3) |
| v3-G2-calm-uneven-pfifo-r1 | C | r2->switch-c | 0.707 (0.7) | 0.308 (0.3) |
| v3-G2-calm-access-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-G2-calm-rev-pfifo-r1 | main | r1->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-G3-sburst-s030u070-pfifo-r1 | main | router->switch | 0.71 (0.7) | 0.312 (0.3) |
| v3-G3-sburst-s030u070-fq_codel-r1 | main | router->switch | 0.713 (0.7) | 0.316 (0.3) |

## Keyframe queueing peak (calm, 200 ms after each keyframe; not gating)

| run | egress | hop | n | p50 / p90 / max ms | 0.121 s U ms |
|---|---|---|---|---|---|
| v3-G1-calm-s030u070-pfifo-r1 | main | router->switch | 103 | 22.3 / 27.1 / 34.1 | 25.4 |
| v3-G1-calm-legacy-pfifo-r1 | main | router->switch | 103 | 42.4 / 56.3 / 57.8 | None |
| v3-G2-calm-split4-pfifo-r1 | up | r1->r2 | 103 | 22.6 / 26.9 / 29.9 | 25.4 |
| v3-G2-calm-split4-pfifo-r1 | a | r2->switch-a | 103 | 11.4 / 14.7 / 24.8 | 25.4 |
| v3-G2-calm-split4-pfifo-r1 | b | r2->switch-b | 103 | 11.5 / 14.3 / 24.8 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | root | rr->r0 | 103 | 22.1 / 26.1 / 29.4 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | X | r0->r1 | 103 | 11.3 / 14.3 / 17.0 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | Y | r0->r2 | 103 | 11.1 / 14.4 / 17.4 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | A | r1->switch-a | 103 | 7.5 / 11.1 / 16.2 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | B | r1->switch-b | 103 | 6.7 / 10.8 / 15.2 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | C | r2->switch-c | 103 | 8.4 / 12.3 / 23.2 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | D | r2->switch-d | 103 | 7.0 / 11.1 / 15.6 | 25.4 |
| v3-G2-calm-uneven-pfifo-r1 | A | r2->switch-a | 103 | 22.7 / 28.1 / 35.3 | 25.4 |
| v3-G2-calm-uneven-pfifo-r1 | B | r2->switch-b | 103 | 22.5 / 26.4 / 31.0 | 25.4 |
| v3-G2-calm-uneven-pfifo-r1 | C | r2->switch-c | 103 | 21.6 / 25.3 / 33.1 | 25.4 |
| v3-G2-calm-access-pfifo-r1 | main | router->switch | 103 | 22.4 / 26.9 / 37.3 | 25.4 |
| v3-G2-calm-rev-pfifo-r1 | main | r1->switch | 103 | 17.6 / 22.0 / 33.9 | 25.4 |
| v3-G3-sburst-s030u070-pfifo-r1 | main | router->switch | 178 | 8.1 / 12.7 / 17.5 | 25.4 |
| v3-G3-sburst-s030u070-fq_codel-r1 | main | router->switch | 178 | 10.0 / 13.9 / 20.0 | 25.4 |

## Installed AQM leaves (`tc qdisc show`, handle 20:; `ecn` must not appear; cake has no ECN switch)

- v3-G1-calm-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G1-calm-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G1-calm-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G1-calm-legacy-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-G1-calm-legacy-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-G1-calm-legacy-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 100p`
- v3-G2-calm-split4-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-split4-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-split4-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-G2-calm-split4-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-split4-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-G2-calm-split4-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-G2-calm-tree16-pfifo-r1 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-tree16-pfifo-r1 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-G2-calm-tree16-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-G2-calm-tree16-pfifo-r1 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-G2-calm-tree16-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-tree16-pfifo-r1 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-tree16-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-tree16-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-uneven-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-uneven-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-G2-calm-access-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-access-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G2-calm-access-pfifo-r1 ra/ra-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 ra/ra-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-access-pfifo-r1 rb/rb-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 rb/rb-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-access-pfifo-r1 rc/rc-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 rc/rc-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-access-pfifo-r1 rd/rd-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 rd/rd-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-rev-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-rev-pfifo-r1 r0/r0-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-rev-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-rev-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 42p`
- v3-G2-calm-rev-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G3-sburst-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G3-sburst-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G3-sburst-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G3-sburst-s030u070-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-G3-sburst-s030u070-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-G3-sburst-s030u070-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`

## Check 4 per traced egress (target = gated; info = reported only)

| run | hop | role | dequeues | unmatched deq / enq (allowed) | max per 200 ms deq / enq | 4a | backlogged gaps | within max(10 %, 15 us) (within 10 %) | jitter us p1 / p99 | 20 ms windows within 5 % (n) | 4b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v3-G1-calm-s030u070-pfifo-r1 | pub->router | info | 181880 | 0 / 0 (9.09) | 0 / 0 | ok | 110820 | 0.9999 (0.8847) | -9.37 / 1.55 | nan (0) | ok |
| v3-G1-calm-s030u070-pfifo-r1 | router->sub-ctrl | info | 33879 | 0 / 0 (3) | 0 / 0 | ok | 18255 | 0.8628 (0.8627) | -201.39 / 1.78 | nan (0) | FAIL |
| v3-G1-calm-s030u070-pfifo-r1 | router->switch | target | 467091 | 0 / 0 (23.35) | 0 / 0 | ok | 272342 | 0.9998 (0.9997) | -1.53 / 1.57 | 1.0 (393) | ok |
| v3-G1-calm-legacy-pfifo-r1 | pub->router | info | 181427 | 0 / 0 (9.07) | 0 / 0 | ok | 76181 | 0.9997 (0.8137) | -9.62 / 1.65 | nan (0) | ok |
| v3-G1-calm-legacy-pfifo-r1 | router->sub-ctrl | info | 33933 | 1 / 0 (3) | 1 / 0 | ok | 19728 | 0.9018 (0.9018) | -201.32 / 1.53 | nan (0) | FAIL |
| v3-G1-calm-legacy-pfifo-r1 | router->switch | target | 146871 | 0 / 0 (7.34) | 0 / 0 | ok | 134580 | 1.0000 (0.9999) | -2.08 / 2.22 | 1.0 (1767) | ok |
| v3-G2-calm-split4-pfifo-r1 | pub->r1 | info | 292803 | 0 / 0 (14.64) | 0 / 0 | ok | 195154 | 0.9995 (0.8025) | -8.89 / 3.74 | nan (0) | ok |
| v3-G2-calm-split4-pfifo-r1 | r1->sub-ctrl | info | 33998 | 0 / 0 (3) | 0 / 0 | ok | 18577 | 0.8822 (0.8821) | -201.18 / 2.08 | nan (0) | FAIL |
| v3-G2-calm-split4-pfifo-r1 | r1->r2 | target | 809463 | 0 / 0 (40.47) | 0 / 0 | ok | 482101 | 0.9994 (0.9974) | -2.28 / 2.29 | 1.0 (382) | ok |
| v3-G2-calm-split4-pfifo-r1 | r2->switch-a | target | 406002 | 0 / 0 (20.3) | 0 / 0 | ok | 225962 | 0.9996 (0.9993) | -2.27 / 2.29 | 1.0 (379) | ok |
| v3-G2-calm-split4-pfifo-r1 | r2->switch-b | target | 405178 | 0 / 0 (20.26) | 0 / 0 | ok | 224711 | 0.9997 (0.9993) | -2.23 / 2.23 | 1.0 (389) | ok |
| v3-G2-calm-tree16-pfifo-r1 | pub->rr | info | 328512 | 0 / 0 (16.43) | 0 / 0 | ok | 195240 | 0.9939 (0.5767) | -9.12 / 11.98 | nan (0) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r0->r1 | target | 438546 | 0 / 0 (21.93) | 0 / 0 | ok | 246839 | 0.9987 (0.9963) | -4.49 / 4.31 | 1.0 (400) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r0->r2 | target | 437938 | 0 / 0 (21.9) | 0 / 0 | ok | 244703 | 0.9987 (0.9964) | -4.45 / 4.23 | 1.0 (393) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r1->switch-a | target | 218879 | 2 / 0 (10.94) | 2 / 0 | ok | 103423 | 0.9990 (0.9986) | -4.3 / 4.12 | 1.0 (340) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r1->switch-b | target | 218573 | 0 / 0 (10.93) | 0 / 0 | ok | 103530 | 0.9990 (0.9985) | -4.29 / 4.09 | 1.0 (322) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r2->switch-c | target | 219564 | 0 / 0 (10.98) | 0 / 0 | ok | 106189 | 0.9990 (0.9985) | -4.37 / 4.11 | 1.0 (360) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r2->switch-d | target | 218509 | 0 / 0 (10.93) | 0 / 0 | ok | 108874 | 0.9994 (0.9989) | -4.29 / 4.14 | 1.0 (337) | ok |
| v3-G2-calm-tree16-pfifo-r1 | rr->sub-ctrl | info | 33912 | 0 / 0 (3) | 0 / 0 | ok | 20628 | 0.9048 (0.9046) | -199.85 / 3.07 | nan (0) | FAIL |
| v3-G2-calm-tree16-pfifo-r1 | rr->r0 | target | 874249 | 0 / 0 (43.71) | 0 / 0 | ok | 528086 | 0.9979 (0.9895) | -4.61 / 4.63 | 1.0 (382) | ok |
| v3-G2-calm-uneven-pfifo-r1 | pub->r1 | info | 502317 | 0 / 0 (25.12) | 0 / 0 | ok | 412477 | 0.9987 (0.6649) | -9.01 / 7.27 | nan (0) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r1->sub-ctrl | info | 33989 | 0 / 0 (3) | 0 / 0 | ok | 19795 | 0.9149 (0.9148) | -200.49 / 1.91 | nan (0) | FAIL |
| v3-G2-calm-uneven-pfifo-r1 | r1->r2 | info | 468339 | 0 / 0 (23.42) | 0 / 0 | ok | 5634 | 0.9997 (0.5818) | -3.96 / 4.56 | nan (0) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r2->switch-a | target | 316329 | 0 / 0 (15.82) | 0 / 0 | ok | 180769 | 0.9998 (0.9996) | -3.62 / 3.35 | 1.0 (401) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r2->switch-b | target | 429851 | 0 / 0 (21.49) | 0 / 0 | ok | 250452 | 0.9996 (0.9987) | -3.67 / 3.51 | 1.0 (414) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r2->switch-c | target | 709615 | 0 / 0 (35.48) | 0 / 0 | ok | 421457 | 0.9993 (0.9971) | -3.37 / 3.24 | 1.0 (381) | ok |
| v3-G2-calm-access-pfifo-r1 | pub->router | info | 181776 | 0 / 0 (9.09) | 0 / 0 | ok | 113521 | 0.9978 (0.7725) | -9.18 / 5.67 | nan (0) | ok |
| v3-G2-calm-access-pfifo-r1 | ra->sub-a | info | 15260 | 0 / 0 (3) | 0 / 0 | ok | 348 | 0.5058 (0.5058) | -406.14 / 1.99 | nan (0) | not evaluated |
| v3-G2-calm-access-pfifo-r1 | rb->sub-b | info | 34013 | 0 / 0 (3) | 0 / 0 | ok | 10899 | 0.9940 (0.9940) | -5.01 / 3.34 | nan (0) | ok |
| v3-G2-calm-access-pfifo-r1 | rc->sub-c | info | 33912 | 0 / 0 (3) | 0 / 0 | ok | 8174 | 0.9916 (0.9916) | -8.41 / 3.44 | nan (0) | ok |
| v3-G2-calm-access-pfifo-r1 | rd->sub-d | info | 64736 | 0 / 0 (3.24) | 0 / 0 | ok | 37579 | 0.9952 (0.9952) | -4.38 / 3.54 | 1.0 (17) | ok |
| v3-G2-calm-access-pfifo-r1 | router->sub-ctrl | info | 33889 | 0 / 0 (3) | 0 / 0 | ok | 18596 | 0.8874 (0.8873) | -200.37 / 2.87 | nan (0) | FAIL |
| v3-G2-calm-access-pfifo-r1 | router->switch | target | 466972 | 0 / 0 (23.35) | 0 / 0 | ok | 272227 | 0.9993 (0.9984) | -2.6 / 2.61 | 1.0 (399) | ok |
| v3-G2-calm-rev-pfifo-r1 | pub->r0 | info | 181999 | 0 / 0 (9.1) | 0 / 0 | ok | 113918 | 0.9992 (0.7860) | -9.2 / 2.99 | nan (0) | ok |
| v3-G2-calm-rev-pfifo-r1 | r0->sub-ctrl | info | 33882 | 0 / 0 (3) | 0 / 0 | ok | 18394 | 0.8337 (0.8337) | -200.18 / 1.94 | nan (0) | FAIL |
| v3-G2-calm-rev-pfifo-r1 | r0->r1 | info | 148124 | 0 / 0 (7.41) | 0 / 0 | ok | 132273 | 0.9999 (0.9986) | -2.26 / 2.26 | 1.0 (1) | ok |
| v3-G2-calm-rev-pfifo-r1 | r1->switch | target | 467214 | 0 / 0 (23.36) | 0 / 0 | ok | 271085 | 0.9997 (0.9993) | -2.01 / 2.04 | 1.0 (409) | ok |
| v3-G3-sburst-s030u070-pfifo-r1 | pub->router | info | 482655 | 0 / 0 (24.13) | 0 / 0 | ok | 183916 | 0.9998 (0.7891) | -9.52 / 1.8 | nan (0) | ok |
| v3-G3-sburst-s030u070-pfifo-r1 | router->sub-ctrl | info | 94395 | 0 / 0 (4.72) | 0 / 0 | ok | 61275 | 0.8931 (0.8931) | -201.43 / 1.37 | nan (0) | FAIL |
| v3-G3-sburst-s030u070-pfifo-r1 | router->switch | target | 1466716 | 0 / 0 (73.34) | 0 / 0 | ok | 1080766 | 0.9998 (0.9998) | -1.44 / 1.49 | 1.0 (5822) | ok |
| v3-G3-sburst-s030u070-fq_codel-r1 | pub->router | info | 482372 | 0 / 0 (24.12) | 0 / 0 | ok | 206830 | 0.9995 (0.7090) | -9.66 / 2.89 | nan (0) | ok |
| v3-G3-sburst-s030u070-fq_codel-r1 | router->sub-ctrl | info | 94687 | 1 / 0 (4.73) | 1 / 0 | ok | 66867 | 0.9071 (0.9071) | -199.62 / 1.69 | nan (0) | FAIL |
| v3-G3-sburst-s030u070-fq_codel-r1 | router->switch | target | 1470595 | 0 / 0 (73.53) | 0 / 0 | ok | 918376 | 0.9998 (0.9992) | -3.0 / 3.04 | 1.0 (705) | ok |

## Health, surge, phase-lock details

- v3-G1-calm-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9427; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.21}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G1-calm-legacy-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9362; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-split4-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8816; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.65, '30Hz': 0.55}, 'b': {'1Hz': 2.33, '30Hz': 3.08}, 'up': {'1Hz': 2.01, '30Hz': 4.14}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-tree16-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 2 (targets 2); cpu idle min 0.7869; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 5.37, '30Hz': 3.21}, 'B': {'1Hz': 2.42, '30Hz': 1.12}, 'C': {'1Hz': 3.7, '30Hz': 2.92}, 'D': {'1Hz': 3.41, '30Hz': 1.91}, 'X': {'1Hz': 0.57, '30Hz': 3.86}, 'Y': {'1Hz': 2.31, '30Hz': 0.66}, 'root': {'1Hz': 4.06, '30Hz': 1.78}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-uneven-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8967; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.18, '30Hz': 4.19}, 'B': {'1Hz': 0.57, '30Hz': 3.93}, 'C': {'1Hz': 5.08, '30Hz': 1.95}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-access-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8704; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.19}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-rev-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.9045; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.24}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G3-sburst-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.938; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.5}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, np.float64(0.939), np.float64(1.1265), np.float64(0.8498)), (1.05, 0.84, np.float64(0.8482), np.float64(1.0857), np.float64(1.0763)), (1.3, 1.09, np.float64(1.0808), np.float64(1.2121), np.float64(0.5952)), (1.15, 0.94, np.float64(0.9408), np.float64(1.155), np.float64(0.971)), (1.3, 1.09, np.float64(1.0827), np.float64(1.1775), np.float64(0.4294)), (1.15, 0.94, np.float64(0.9308), np.float64(1.0988), np.float64(0.7617)), (1.05, 0.84, np.float64(0.8453), np.float64(1.0609), np.float64(0.9777)), (1.05, 0.84, np.float64(0.8352), np.float64(1.0851), np.float64(1.1326)), (1.05, 0.84, np.float64(0.8421), np.float64(1.0825), np.float64(1.0896)), (1.15, 0.94, np.float64(0.9389), np.float64(1.1432), np.float64(0.9263)), (1.05, 0.84, np.float64(0.838), np.float64(1.0551), np.float64(0.9839)), (1.3, 1.09, np.float64(1.0877), np.float64(1.1842), np.float64(0.4374)), (1.15, 0.94, np.float64(0.9537), np.float64(1.1322), np.float64(0.8091)), (1.3, 1.09, np.float64(1.0928), np.float64(1.1871), np.float64(0.4276)), (1.3, 1.09, np.float64(1.0806), np.float64(1.2248), np.float64(0.6536)), (1.05, 0.84, np.float64(0.8348), np.float64(1.0337), np.float64(0.9013)), (1.3, 1.09, np.float64(1.0883), np.float64(1.2055), np.float64(0.5312)), (1.15, 0.94, np.float64(0.9348), np.float64(1.1151), np.float64(0.8171))]; fq collisions None; errors []
- v3-G3-sburst-s030u070-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9252; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, np.float64(0.939), np.float64(1.1712), np.float64(1.0359)), (1.05, 0.84, np.float64(0.8482), np.float64(1.049), np.float64(0.8956)), (1.3, 1.09, np.float64(1.0808), np.float64(1.2274), np.float64(0.654)), (1.15, 0.94, np.float64(0.9408), np.float64(1.0954), np.float64(0.6898)), (1.3, 1.09, np.float64(1.0827), np.float64(1.2221), np.float64(0.6218)), (1.15, 0.94, np.float64(0.9308), np.float64(1.0914), np.float64(0.7168)), (1.05, 0.84, np.float64(0.8453), np.float64(1.0327), np.float64(0.8363)), (1.05, 0.84, np.float64(0.8352), np.float64(1.0294), np.float64(0.8665)), (1.05, 0.84, np.float64(0.8421), np.float64(1.0306), np.float64(0.841)), (1.15, 0.94, np.float64(0.9389), np.float64(1.0883), np.float64(0.6669)), (1.05, 0.84, np.float64(0.838), np.float64(1.019), np.float64(0.8076)), (1.3, 1.09, np.float64(1.0877), np.float64(1.2351), np.float64(0.6578)), (1.15, 0.94, np.float64(0.9537), np.float64(1.1263), np.float64(0.77)), (1.3, 1.09, np.float64(1.0928), np.float64(1.2313), np.float64(0.6182)), (1.3, 1.09, np.float64(1.0806), np.float64(1.2278), np.float64(0.6566)), (1.05, 0.84, np.float64(0.8348), np.float64(1.0168), np.float64(0.8118)), (1.3, 1.09, np.float64(1.0883), np.float64(1.204), np.float64(0.5164)), (1.15, 0.94, np.float64(0.9348), np.float64(1.0907), np.float64(0.6956))]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 21, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1095329, 'in_pinned_class': 1564, 'flows': ['10.101.0.1:5218']}}; errors []
