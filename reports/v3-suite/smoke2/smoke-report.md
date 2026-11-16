# Smoke: FAIL

Gating checks: 1_load_share, 2_ecn, 3_mtu, 4_health, 6_phase (scripts/v3_gate.py). Runs: 7.

| run | 1 load_share | 2 ecn | 3 mtu | 4 health | 5 surge | 6 phase |
|---|---|---|---|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | ok | ok | ok | FAIL | - | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-access-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |

## Load and share per egress (target U, s)

| run | egress | hop | load (U) | share / 0.96 (s) |
|---|---|---|---|---|
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
| v3-SMOKE-calm-access-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-calm-rev-pfifo-r1 | main | r1->switch | 0.708 (0.7) | 0.308 (0.3) |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.307 (0.3) |

## Keyframe queueing peak (calm, 200 ms after each keyframe; not gating)

| run | egress | hop | n | p50 / p90 / max ms | 0.121 s U ms |
|---|---|---|---|---|---|
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
| v3-SMOKE-calm-access-pfifo-r1 | main | router->switch | 43 | 22.9 / 26.2 / 29.6 | 25.4 |
| v3-SMOKE-calm-rev-pfifo-r1 | main | r1->switch | 43 | 19.3 / 22.6 / 25.8 | 25.4 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | router->switch | 65 | 14.2 / 24.6 / 29.4 | 25.4 |

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

## Check 4 per traced egress (target = gated; info = reported only)

| run | hop | role | dequeues | unmatched deq / enq (allowed) | max per 200 ms deq / enq | 4a | backlogged gaps | within 10 % | 20 ms windows within 5 % (n) | 4b |
|---|---|---|---|---|---|---|---|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | pub->router | info | 90976 | 0 / 0 (4.55) | 0 / 0 | ok | 52633 | 0.8851 | nan (0) | FAIL |
| v3-SMOKE-calm-s030u070-pfifo-r1 | router->sub-ctrl | info | 16976 | 0 / 0 (3) | 0 / 0 | ok | 7814 | 0.8830 | nan (0) | FAIL |
| v3-SMOKE-calm-s030u070-pfifo-r1 | router->switch | target | 234076 | 0 / 0 (11.7) | 0 / 0 | ok | 136360 | 0.9996 | 1.0 (216) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | pub->r1 | info | 146341 | 0 / 0 (7.32) | 0 / 0 | ok | 93630 | 0.7897 | nan (0) | FAIL |
| v3-SMOKE-calm-split4-pfifo-r1 | r1->sub-ctrl | info | 16904 | 0 / 0 (3) | 0 / 0 | ok | 7056 | 0.8481 | nan (0) | FAIL |
| v3-SMOKE-calm-split4-pfifo-r1 | r1->r2 | target | 405317 | 0 / 0 (20.27) | 0 / 0 | ok | 240863 | 0.9976 | 1.0 (190) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | r2->switch-a | target | 203170 | 0 / 0 (10.16) | 0 / 0 | ok | 112870 | 0.9991 | 1.0 (199) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | r2->switch-b | target | 203067 | 0 / 0 (10.15) | 0 / 0 | ok | 112840 | 0.9992 | 1.0 (201) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | pub->rr | info | 164872 | 0 / 0 (8.24) | 0 / 0 | ok | 92110 | 0.5881 | nan (0) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | r0->r1 | target | 219795 | 0 / 0 (10.99) | 0 / 0 | ok | 124016 | 0.9966 | 1.0 (205) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r0->r2 | target | 219615 | 0 / 0 (10.98) | 0 / 0 | ok | 122491 | 0.9967 | 1.0 (212) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r1->switch-a | target | 109561 | 0 / 0 (5.48) | 0 / 0 | ok | 51442 | 0.9985 | 1.0 (179) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r1->switch-b | target | 109418 | 0 / 0 (5.47) | 0 / 0 | ok | 52264 | 0.9983 | 1.0 (192) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r2->switch-c | target | 109944 | 0 / 0 (5.5) | 0 / 0 | ok | 52484 | 0.9986 | 1.0 (182) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r2->switch-d | target | 109349 | 0 / 0 (5.47) | 0 / 0 | ok | 50620 | 0.9981 | 1.0 (176) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | rr->sub-ctrl | info | 17019 | 0 / 0 (3) | 0 / 0 | ok | 9909 | 0.8824 | nan (0) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | rr->r0 | target | 438224 | 0 / 0 (21.91) | 0 / 0 | ok | 264682 | 0.9896 | 1.0 (194) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | pub->r1 | info | 251492 | 0 / 0 (12.57) | 0 / 0 | ok | 197492 | 0.6790 | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r1->sub-ctrl | info | 17053 | 0 / 0 (3) | 0 / 0 | ok | 10305 | 0.9365 | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r1->r2 | info | 234443 | 0 / 0 (11.72) | 0 / 0 | ok | 2075 | 0.6068 | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-a | target | 158646 | 0 / 0 (7.93) | 0 / 0 | ok | 90442 | 0.9996 | 1.0 (212) | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-b | target | 215328 | 0 / 0 (10.77) | 0 / 0 | ok | 125286 | 0.9989 | 1.0 (205) | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-c | target | 355206 | 0 / 0 (17.76) | 0 / 0 | ok | 210546 | 0.9974 | 1.0 (197) | ok |
| v3-SMOKE-calm-access-pfifo-r1 | pub->router | info | 91021 | 0 / 0 (4.55) | 0 / 0 | ok | 51807 | 0.7566 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | ra->sub-a | info | 7652 | 0 / 0 (3) | 0 / 0 | ok | 69 | 0.2464 | nan (0) | not evaluated |
| v3-SMOKE-calm-access-pfifo-r1 | rb->sub-b | info | 16998 | 0 / 0 (3) | 0 / 0 | ok | 3364 | 0.9860 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rc->sub-c | info | 17020 | 0 / 0 (3) | 0 / 0 | ok | 2977 | 0.9738 | 1.0 (1) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rd->sub-d | info | 32405 | 0 / 0 (3) | 0 / 0 | ok | 19556 | 0.9977 | 1.0 (8) | ok |
| v3-SMOKE-calm-access-pfifo-r1 | router->sub-ctrl | info | 16964 | 0 / 0 (3) | 0 / 0 | ok | 7177 | 0.7594 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | router->switch | target | 234140 | 0 / 0 (11.71) | 0 / 0 | ok | 136759 | 0.9983 | 1.0 (210) | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | pub->r0 | info | 91049 | 0 / 0 (4.55) | 0 / 0 | ok | 60886 | 0.7974 | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r0->sub-ctrl | info | 16926 | 0 / 0 (3) | 0 / 0 | ok | 9375 | 0.8767 | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r0->r1 | info | 74125 | 0 / 0 (3.71) | 0 / 0 | ok | 65495 | 0.9988 | nan (0) | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | r1->switch | target | 234199 | 0 / 0 (11.71) | 0 / 0 | ok | 135718 | 0.9993 | 1.0 (209) | ok |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | pub->router | info | 134799 | 0 / 0 (6.74) | 0 / 0 | ok | 65401 | 0.8400 | nan (0) | FAIL |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | router->sub-ctrl | info | 25432 | 0 / 0 (3) | 0 / 0 | ok | 12951 | 0.8939 | nan (0) | FAIL |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | router->switch | target | 357740 | 0 / 0 (17.89) | 0 / 0 | ok | 218150 | 0.9997 | 1.0 (507) | ok |

## Health, surge, phase-lock details

- v3-SMOKE-calm-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9348; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.45}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-split4-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.9042; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.53, '30Hz': 4.43}, 'b': {'1Hz': 2.05, '30Hz': 1.9}, 'up': {'1Hz': 2.57, '30Hz': 2.12}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-tree16-pfifo-r1: lost 0; target egresses failing ['rr-eth2']; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.7936; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 2.79, '30Hz': 2.96}, 'B': {'1Hz': 4.43, '30Hz': 4.7}, 'C': {'1Hz': 2.36, '30Hz': 6.04}, 'D': {'1Hz': 2.7, '30Hz': 2.88}, 'X': {'1Hz': 0.32, '30Hz': 4.45}, 'Y': {'1Hz': 3.42, '30Hz': 2.78}, 'root': {'1Hz': 2.61, '30Hz': 1.45}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-uneven-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8914; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 0.97, '30Hz': 5.25}, 'B': {'1Hz': 0.32, '30Hz': 4.29}, 'C': {'1Hz': 2.74, '30Hz': 4.76}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-access-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8749; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.37}}; surge []; fq collisions None; errors []
- v3-SMOKE-calm-rev-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.943; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.97, '30Hz': 1.4}}; surge []; fq collisions None; errors []
- v3-SMOKE-sburst-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9593; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.65, '30Hz': 1.93}}; surge [('router->switch', 1.15, 1.132)]; fq collisions None; errors []

## Tracer: smoke 1 (classic tracepoints) -> this smoke (raw tracepoints)

Unmatched dequeues / enqueues over all traced egresses and over the bottleneck targets; recursion_misses per tracer (every tracer sees the same nested events); check 4 (third rules).

| topology | tracers | unmatched deq / enq, all | unmatched deq / enq, targets | recursion_misses per tracer | check 4 | failing targets (now) |
|---|---|---|---|---|---|---|
| access | 6 -> 6 | 28 / 38 -> 0 / 0 | 19 / 3 -> 0 / 0 | [158] -> [0] | FAIL -> ok | - |
| rev | 3 -> 3 | 14 / 21 -> 0 / 0 | 3 / 3 -> 0 / 0 | [90] -> [0] | ok -> ok | - |
| s030u070 | 2 -> 2 | 4 / 8 -> 0 / 0 | 1 / 1 -> 0 / 0 | [38] -> [0] | ok -> ok | - |
| sburst-s030u070 | 2 -> 2 | 8 / 23 -> 0 / 0 | 6 / 4 -> 0 / 0 | [102] -> [0] | ok -> ok | - |
| split4 | 3 -> 3 | 16 / 48 -> 0 / 0 | 16 / 27 -> 0 / 0 | [223] -> [0] | ok -> ok | - |
| tree16 | 5 -> 5 | 50 / 140 -> 0 / 0 | 48 / 87 -> 0 / 0 | [667] -> [0] | FAIL -> FAIL | rr->r0 (4b) |
| uneven | 3 -> 3 | 59 / 119 -> 0 / 0 | 26 / 28 -> 0 / 0 | [599] -> [0] | FAIL -> ok | - |

## Emission times (re-measured, not gating)

Per run and client: median BBR pacing (Mb/s), keyframe and P-frame emission (ms), calm GOPs:

- v3-SMOKE-calm-s030u070-pfifo-r1: emission sub-a 29.25 Mb/s key 3.53 P 0.0; sub-b 83.29 Mb/s key 3.53 P 0.0; sub-c 71.94 Mb/s key 3.75 P 0.0; sub-ctrl 47.71 Mb/s key 6.72 P 1.18; sub-d 134.1 Mb/s key 5.18 P 1.16
- v3-SMOKE-calm-split4-pfifo-r1: emission a1 26.49 Mb/s key 3.99 P 0.0; a2 22.77 Mb/s key 4.61 P 0.0; a3 58.84 Mb/s key 5.96 P 1.14; a4 130.42 Mb/s key 6.16 P 1.18; b1 31.21 Mb/s key 3.68 P 0.0; b2 22.38 Mb/s key 4.66 P 0.0; b3 53.32 Mb/s key 5.86 P 1.13; b4 102.96 Mb/s key 6.64 P 1.19; sub-ctrl 42.16 Mb/s key 7.48 P 1.25
- v3-SMOKE-calm-tree16-pfifo-r1: emission a1 13.58 Mb/s key 3.73 P 0.0; a2 26.99 Mb/s key 4.49 P 0.0; a3 21.72 Mb/s key 4.84 P 0.0; a4 54.6 Mb/s key 6.08 P 1.16; b1 13.61 Mb/s key 3.77 P 0.0; b2 24.74 Mb/s key 4.49 P 0.0; b3 22.04 Mb/s key 4.69 P 0.0; b4 56.32 Mb/s key 6.03 P 1.15; c1 12.88 Mb/s key 3.96 P 0.0; c2 24.8 Mb/s key 4.45 P 0.0; c3 22.21 Mb/s key 4.73 P 0.0; c4 64.36 Mb/s key 5.05 P 1.14; d1 16.64 Mb/s key 3.06 P 0.0; d2 24.35 Mb/s key 4.54 P 0.0; d3 17.93 Mb/s key 5.69 P 0.0; d4 60.79 Mb/s key 6.26 P 1.19; sub-ctrl 62.15 Mb/s key 4.91 P 1.16
- v3-SMOKE-calm-uneven-pfifo-r1: emission a1 92.2 Mb/s key 3.56 P 0.0; a2 135.94 Mb/s key 4.79 P 1.16; b1 18.64 Mb/s key 3.14 P 0.0; b2 25.71 Mb/s key 3.97 P 0.0; b3 19.64 Mb/s key 5.26 P 0.0; b4 65.33 Mb/s key 6.21 P 1.17; b5 199.21 Mb/s key 3.72 P 0.0; c1 15.92 Mb/s key 4.08 P 0.0; c2 15.54 Mb/s key 3.27 P 0.0; c3 19.66 Mb/s key 5.15 P 0.0; c4 22.63 Mb/s key 6.49 P 0.0; c5 30.53 Mb/s key 3.83 P 0.0; c6 85.54 Mb/s key 4.18 P 0.0; c7 55.01 Mb/s key 6.85 P 1.15; c8 53.32 Mb/s key 6.08 P 1.15; c9 204.72 Mb/s key 3.68 P 0.0; sub-ctrl 79.13 Mb/s key 3.95 P 0.0
- v3-SMOKE-calm-access-pfifo-r1: emission sub-a 31.81 Mb/s key 3.38 P 0.0; sub-b 65.89 Mb/s key 4.9 P 1.14; sub-c 59.94 Mb/s key 5.92 P 1.16; sub-ctrl 46.49 Mb/s key 7.05 P 1.15; sub-d 137.3 Mb/s key 4.77 P 1.16
- v3-SMOKE-calm-rev-pfifo-r1: emission sub-a 23.56 Mb/s key 4.45 P 0.0; sub-b 75.38 Mb/s key 4.7 P 1.11; sub-c 68.58 Mb/s key 4.69 P 0.0; sub-ctrl 60.68 Mb/s key 5.72 P 1.14; sub-d 115.61 Mb/s key 5.95 P 1.16

```
{
 "runs": [
  {
   "run": "v3-SMOKE-calm-s030u070-pfifo-r1:sub-d",
   "keyframes": 53,
   "key_ms_p50": 4.83,
   "key_ms_p90": 7.07,
   "p_frames": 1540,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.2
  },
  {
   "run": "v3-SMOKE-calm-split4-pfifo-r1:a4",
   "keyframes": 54,
   "key_ms_p50": 6.01,
   "key_ms_p90": 7.66,
   "p_frames": 1549,
   "p_ms_p50": 1.18,
   "p_ms_p90": 1.27
  },
  {
   "run": "v3-SMOKE-calm-split4-pfifo-r1:b4",
   "keyframes": 53,
   "key_ms_p50": 6.4,
   "key_ms_p90": 9.03,
   "p_frames": 1546,
   "p_ms_p50": 1.19,
   "p_ms_p90": 1.28
  },
  {
   "run": "v3-SMOKE-calm-uneven-pfifo-r1:a2",
   "keyframes": 54,
   "key_ms_p50": 4.78,
   "key_ms_p90": 6.88,
   "p_frames": 1550,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.23
  },
  {
   "run": "v3-SMOKE-calm-uneven-pfifo-r1:b5",
   "keyframes": 53,
   "key_ms_p50": 3.68,
   "key_ms_p90": 4.87,
   "p_frames": 1554,
   "p_ms_p50": 0.0,
   "p_ms_p90": 1.2
  },
  {
   "run": "v3-SMOKE-calm-uneven-pfifo-r1:c9",
   "keyframes": 54,
   "key_ms_p50": 3.65,
   "key_ms_p90": 4.62,
   "p_frames": 1556,
   "p_ms_p50": 0.0,
   "p_ms_p90": 1.15
  },
  {
   "run": "v3-SMOKE-calm-access-pfifo-r1:sub-d",
   "keyframes": 54,
   "key_ms_p50": 4.77,
   "key_ms_p90": 6.41,
   "p_frames": 1550,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.24
  },
  {
   "run": "v3-SMOKE-calm-rev-pfifo-r1:sub-d",
   "keyframes": 54,
   "key_ms_p50": 5.93,
   "key_ms_p90": 8.1,
   "p_frames": 1543,
   "p_ms_p50": 1.16,
   "p_ms_p90": 1.23
  }
 ],
 "pooled": {
  "key_ms_p50": 4.82,
  "p_ms_p50": 1.15
 }
}
```

```
# Keyframe departure from the publisher (existing synchronized runs)

| run | pub link Mb/s | clients | calm GOPs | span first->last packet ms p50 / p90 / max | summed keyframes / pub link ms (p50) |
|---|---|---|---|---|---|
| .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-s030u070-pfifo-r1 | 1000 | 5 | 48 | 8.0 / 44.7 / 241.7 | 1.8 |
| .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-split4-pfifo-r1 | 1000 | 9 | 48 | 9.5 / 34.5 / 228.0 | 2.8 |
| .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-tree16-pfifo-r1 | 1000 | 17 | 48 | 10.3 / 139.7 / 247.1 | 3.0 |
| .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-uneven-pfifo-r1 | 1000 | 17 | 48 | 34.1 / 130.2 / 267.0 | 4.9 |
| .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-access-pfifo-r1 | 1000 | 5 | 48 | 8.8 / 33.9 / 203.8 | 1.8 |
| .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-rev-pfifo-r1 | 1000 | 5 | 48 | 7.5 / 34.5 / 200.9 | 1.8 |

## Per client: median rank of the first packet among the clients, keyframe emission time p50/p90 ms, BBR pacing Mb/s (median)

- .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-s030u070-pfifo-r1: sub-a rank 2.0 emis 3.5/5.2 pacing 29.2; sub-b rank 2.0 emis 3.5/32.8 pacing 83.3; sub-c rank 2.0 emis 3.7/14.1 pacing 71.9; sub-ctrl rank 2.0 emis 6.7/8.9 pacing 47.7; sub-d rank 2.0 emis 5.2/33.0 pacing 134.1
- .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-split4-pfifo-r1: a1 rank 5.0 emis 4.0/6.7 pacing 26.5; a2 rank 3.5 emis 4.6/9.3 pacing 22.8; a3 rank 4.0 emis 6.0/33.0 pacing 58.8; a4 rank 4.0 emis 6.2/33.0 pacing 130.9; b1 rank 4.0 emis 3.7/5.7 pacing 31.2; b2 rank 5.0 emis 4.7/7.3 pacing 22.4; b3 rank 4.0 emis 5.9/33.2 pacing 53.3; b4 rank 3.5 emis 6.6/17.4 pacing 103.0; sub-ctrl rank 3.0 emis 7.5/11.0 pacing 42.2
- .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-tree16-pfifo-r1: a1 rank 8.0 emis 3.7/32.8 pacing 16.6; a2 rank 8.5 emis 4.5/7.9 pacing 27.0; a3 rank 6.0 emis 4.8/7.9 pacing 21.7; a4 rank 8.0 emis 6.1/16.0 pacing 54.6; b1 rank 6.5 emis 3.8/32.6 pacing 13.6; b2 rank 7.0 emis 4.5/7.1 pacing 24.7; b3 rank 7.0 emis 4.7/7.2 pacing 22.0; b4 rank 9.0 emis 6.0/32.5 pacing 56.3; c1 rank 8.5 emis 4.0/32.7 pacing 12.9; c2 rank 8.0 emis 4.5/7.1 pacing 24.8; c3 rank 9.0 emis 4.7/8.5 pacing 22.2; c4 rank 9.0 emis 5.0/15.1 pacing 64.4; d1 rank 7.5 emis 3.1/32.3 pacing 16.6; d2 rank 9.0 emis 4.5/16.0 pacing 24.3; d3 rank 8.5 emis 5.7/8.6 pacing 17.9; d4 rank 8.0 emis 6.3/16.1 pacing 60.8; sub-ctrl rank 8.0 emis 4.9/8.0 pacing 65.3
- .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-uneven-pfifo-r1: a1 rank 7.0 emis 3.6/4.9 pacing 92.2; a2 rank 10.0 emis 4.8/33.0 pacing 135.9; b1 rank 7.0 emis 3.1/33.3 pacing 19.0; b2 rank 6.0 emis 4.0/6.4 pacing 25.7; b3 rank 6.0 emis 5.3/8.8 pacing 19.6; b4 rank 6.0 emis 6.2/16.0 pacing 65.3; b5 rank 9.0 emis 3.7/14.3 pacing 203.9; c1 rank 8.5 emis 4.1/33.3 pacing 15.9; c2 rank 7.5 emis 3.3/33.4 pacing 15.5; c3 rank 7.0 emis 5.1/7.9 pacing 19.7; c4 rank 10.0 emis 6.5/17.6 pacing 22.7; c5 rank 10.0 emis 3.8/6.1 pacing 30.5; c6 rank 7.5 emis 4.2/33.0 pacing 85.5; c7 rank 9.0 emis 6.8/32.5 pacing 55.0; c8 rank 8.0 emis 6.1/32.6 pacing 53.3; c9 rank 6.0 emis 3.7/13.7 pacing 204.7; sub-ctrl rank 9.0 emis 4.0/33.1 pacing 93.0
- .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-access-pfifo-r1: sub-a rank 2.0 emis 3.4/5.4 pacing 31.8; sub-b rank 2.0 emis 4.9/32.5 pacing 65.9; sub-c rank 2.0 emis 5.9/32.6 pacing 59.9; sub-ctrl rank 2.0 emis 7.1/10.4 pacing 46.5; sub-d rank 2.0 emis 4.8/7.5 pacing 139.1
- .runs/2026-11-14_1801_v3-smoke/v3-SMOKE-calm-rev-pfifo-r1: sub-a rank 2.0 emis 4.5/15.9 pacing 23.6; sub-b rank 1.0 emis 4.7/14.3 pacing 75.4; sub-c rank 2.0 emis 4.7/14.8 pacing 68.6; sub-ctrl rank 1.0 emis 5.7/15.9 pacing 60.7; sub-d rank 2.0 emis 5.9/33.4 pacing 115.6
```

