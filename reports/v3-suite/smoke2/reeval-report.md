# Gate: PASS

Gating checks: 1_load_share, 2_ecn, 3_mtu, 4_health, 5_surge, 6_phase (scripts/v3_gate.py). Runs: 7.

| run | 1 load_share | 2 ecn | 3 mtu | 4 health | 5 surge | 6 phase |
|---|---|---|---|---|---|---|
| v3-SMOKE-calm-access-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |

## Load and share per egress (target U, s)

| run | egress | hop | load (U) | share / 0.96 (s) |
|---|---|---|---|---|
| v3-SMOKE-calm-access-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-rev-pfifo-r1 | main | r1->switch | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-s030u070-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.307 (0.3) |
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
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.307 (0.3) |

## Keyframe queueing peak (calm, 200 ms after each keyframe; not gating)

| run | egress | hop | n | p50 / p90 / max ms | 0.121 s U ms |
|---|---|---|---|---|---|
| v3-SMOKE-calm-access-pfifo-r1 | main | router->switch | 43 | 22.9 / 26.2 / 29.6 | 25.4 |
| v3-SMOKE-calm-rev-pfifo-r1 | main | r1->switch | 43 | 19.3 / 22.6 / 25.8 | 25.4 |
| v3-SMOKE-calm-s030u070-pfifo-r1 | main | router->switch | 43 | 21.8 / 25.4 / 30.5 | 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | up | r1->r2 | 43 | 22.9 / 25.7 / 27.9 | 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | a | r2->switch-a | 43 | 11.7 / 15.0 / 33.1 | 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | b | r2->switch-b | 43 | 11.7 / 13.5 / 25.1 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | root | rr->r0 | 43 | 22.4 / 25.2 / 27.8 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | X | r0->r1 | 43 | 11.3 / 13.8 / 16.5 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | Y | r0->r2 | 43 | 11.3 / 14.9 / 17.8 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | A | r1->switch-a | 43 | 7.1 / 10.8 / 14.9 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | B | r1->switch-b | 43 | 7.5 / 12.6 / 17.0 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | C | r2->switch-c | 43 | 8.1 / 10.6 / 13.9 | 25.4 |
| v3-SMOKE-calm-tree16-pfifo-r1 | D | r2->switch-d | 43 | 7.1 / 11.3 / 19.4 | 25.4 |
| v3-SMOKE-calm-uneven-pfifo-r1 | A | r2->switch-a | 43 | 23.3 / 27.8 / 32.4 | 25.4 |
| v3-SMOKE-calm-uneven-pfifo-r1 | B | r2->switch-b | 43 | 22.4 / 26.5 / 30.4 | 25.4 |
| v3-SMOKE-calm-uneven-pfifo-r1 | C | r2->switch-c | 43 | 22.8 / 26.0 / 28.7 | 25.4 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | router->switch | 65 | 14.2 / 24.6 / 29.4 | 25.4 |

## Installed AQM leaves (`tc qdisc show`, handle 20:; `ecn` must not appear; cake has no ECN switch)

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
- v3-SMOKE-sburst-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-SMOKE-sburst-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-SMOKE-sburst-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`

## Check 4 per traced egress (target = gated; info = reported only)

| run | hop | role | dequeues | unmatched deq / enq (allowed) | max per 200 ms deq / enq | 4a | backlogged gaps | within max(10 %, 15 us) (within 10 %) | jitter us p1 / p99 | 20 ms windows within 5 % (n) | 4b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v3-SMOKE-calm-access-pfifo-r1 | pub->router | info | 91021 | 0 / 0 (4.55) | 0 / 0 | ok | 51807 | nan (0.7566) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | ra->sub-a | info | 7652 | 0 / 0 (3) | 0 / 0 | ok | 69 | nan (0.2464) | nan / nan | nan (0) | not evaluated |
| v3-SMOKE-calm-access-pfifo-r1 | rb->sub-b | info | 16998 | 0 / 0 (3) | 0 / 0 | ok | 3364 | nan (0.9860) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rc->sub-c | info | 17020 | 0 / 0 (3) | 0 / 0 | ok | 2977 | nan (0.9738) | nan / nan | 1.0 (1) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rd->sub-d | info | 32405 | 0 / 0 (3) | 0 / 0 | ok | 19556 | nan (0.9977) | nan / nan | 1.0 (8) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | router->sub-ctrl | info | 16964 | 0 / 0 (3) | 0 / 0 | ok | 7177 | nan (0.7594) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | router->switch | target | 234140 | 0 / 0 (11.71) | 0 / 0 | ok | 136759 | 0.9993 (0.9983) | -2.64 / 2.63 | 1.0 (210) | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | pub->r0 | info | 91049 | 0 / 0 (4.55) | 0 / 0 | ok | 60886 | nan (0.7974) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r0->sub-ctrl | info | 16926 | 0 / 0 (3) | 0 / 0 | ok | 9375 | nan (0.8767) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r0->r1 | info | 74125 | 0 / 0 (3.71) | 0 / 0 | ok | 65495 | nan (0.9988) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r1->switch | target | 234199 | 0 / 0 (11.71) | 0 / 0 | ok | 135718 | 0.9997 (0.9993) | -2.0 / 1.98 | 1.0 (209) | ok |
| v3-SMOKE-calm-s030u070-pfifo-r1 | pub->router | info | 90976 | 0 / 0 (4.55) | 0 / 0 | ok | 52633 | nan (0.8851) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-s030u070-pfifo-r1 | router->sub-ctrl | info | 16976 | 0 / 0 (3) | 0 / 0 | ok | 7814 | nan (0.8830) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-s030u070-pfifo-r1 | router->switch | target | 234076 | 0 / 0 (11.7) | 0 / 0 | ok | 136360 | 0.9998 (0.9996) | -1.52 / 1.56 | 1.0 (216) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | pub->r1 | info | 146341 | 0 / 0 (7.32) | 0 / 0 | ok | 93630 | nan (0.7897) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-split4-pfifo-r1 | r1->sub-ctrl | info | 16904 | 0 / 0 (3) | 0 / 0 | ok | 7056 | nan (0.8481) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-split4-pfifo-r1 | r1->r2 | target | 405317 | 0 / 0 (20.27) | 0 / 0 | ok | 240863 | 0.9995 (0.9976) | -2.34 / 2.35 | 1.0 (190) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | r2->switch-a | target | 203170 | 0 / 0 (10.16) | 0 / 0 | ok | 112870 | 0.9996 (0.9991) | -2.47 / 2.41 | 1.0 (199) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | r2->switch-b | target | 203067 | 0 / 0 (10.15) | 0 / 0 | ok | 112840 | 0.9996 (0.9992) | -2.4 / 2.37 | 1.0 (201) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | pub->rr | info | 164872 | 0 / 0 (8.24) | 0 / 0 | ok | 92110 | nan (0.5881) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | r0->r1 | target | 219795 | 0 / 0 (10.99) | 0 / 0 | ok | 124016 | 0.9988 (0.9966) | -4.57 / 4.38 | 1.0 (205) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r0->r2 | target | 219615 | 0 / 0 (10.98) | 0 / 0 | ok | 122491 | 0.9986 (0.9967) | -4.35 / 4.16 | 1.0 (212) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r1->switch-a | target | 109561 | 0 / 0 (5.48) | 0 / 0 | ok | 51442 | 0.9989 (0.9985) | -4.18 / 4.03 | 1.0 (179) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r1->switch-b | target | 109418 | 0 / 0 (5.47) | 0 / 0 | ok | 52264 | 0.9989 (0.9983) | -4.25 / 4.16 | 1.0 (192) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r2->switch-c | target | 109944 | 0 / 0 (5.5) | 0 / 0 | ok | 52484 | 0.9991 (0.9986) | -4.4 / 4.09 | 1.0 (182) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r2->switch-d | target | 109349 | 0 / 0 (5.47) | 0 / 0 | ok | 50620 | 0.9988 (0.9981) | -4.29 / 4.17 | 1.0 (176) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | rr->sub-ctrl | info | 17019 | 0 / 0 (3) | 0 / 0 | ok | 9909 | nan (0.8824) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | rr->r0 | target | 438224 | 0 / 0 (21.91) | 0 / 0 | ok | 264682 | 0.9979 (0.9896) | -4.63 / 4.55 | 1.0 (194) | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | pub->r1 | info | 251492 | 0 / 0 (12.57) | 0 / 0 | ok | 197492 | nan (0.6790) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r1->sub-ctrl | info | 17053 | 0 / 0 (3) | 0 / 0 | ok | 10305 | nan (0.9365) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r1->r2 | info | 234443 | 0 / 0 (11.72) | 0 / 0 | ok | 2075 | nan (0.6068) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-a | target | 158646 | 0 / 0 (7.93) | 0 / 0 | ok | 90442 | 0.9998 (0.9996) | -3.59 / 3.25 | 1.0 (212) | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-b | target | 215328 | 0 / 0 (10.77) | 0 / 0 | ok | 125286 | 0.9996 (0.9989) | -3.57 / 3.35 | 1.0 (205) | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-c | target | 355206 | 0 / 0 (17.76) | 0 / 0 | ok | 210546 | 0.9994 (0.9974) | -3.29 / 3.16 | 1.0 (197) | ok |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | pub->router | info | 134799 | 0 / 0 (6.74) | 0 / 0 | ok | 65401 | nan (0.8400) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | router->sub-ctrl | info | 25432 | 0 / 0 (3) | 0 / 0 | ok | 12951 | nan (0.8939) | nan / nan | nan (0) | FAIL |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | router->switch | target | 357740 | 0 / 0 (17.89) | 0 / 0 | ok | 218150 | 0.9998 (0.9997) | -1.54 / 1.57 | 1.0 (507) | ok |

## Health, surge, phase-lock details

- v3-SMOKE-calm-access-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8749; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.37}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-rev-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.943; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.4}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9348; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.45}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-split4-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.9042; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.53, '30Hz': 4.43}, 'b': {'1Hz': 2.05, '30Hz': 1.9}, 'up': {'1Hz': 2.57, '30Hz': 2.12}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-tree16-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.7936; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 2.79, '30Hz': 2.96}, 'B': {'1Hz': 4.43, '30Hz': 4.7}, 'C': {'1Hz': 2.36, '30Hz': 6.04}, 'D': {'1Hz': 2.7, '30Hz': 2.88}, 'X': {'1Hz': 0.32, '30Hz': 4.45}, 'Y': {'1Hz': 3.42, '30Hz': 2.78}, 'root': {'1Hz': 2.61, '30Hz': 1.45}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-uneven-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8914; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 0.97, '30Hz': 5.25}, 'B': {'1Hz': 0.32, '30Hz': 4.29}, 'C': {'1Hz': 2.74, '30Hz': 4.76}}; surge []; fq collisions None; errors []
- v3-SMOKE-sburst-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9593; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.65, '30Hz': 1.93}}; surge [('router->switch', 1.15, 1.132)]; fq collisions None; errors []
