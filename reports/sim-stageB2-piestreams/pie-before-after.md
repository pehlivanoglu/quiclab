
## matched: 2 runs matching 'pie'

### Packet identity per egress (tracer counts): enq / deq / drop, residual enq - deq - drop

| run | egress | before | residual before | after | residual after |
|---|---|---|---|---|---|
| sim-B-A2-sburst-def-pie-r1 | pub-eth0 | 488838 / 488838 / 0 | 0 | 482964 / 482964 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r1 | router-eth1 | 91685 / 91685 / 0 | 0 | 91685 / 91685 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r1 | router-eth2 | 1804668 / 1684685 / 119983 | 0 | 1798794 / 1684738 / 114056 | 0 |
| sim-B-A2-sburst-def-pie-r2 | pub-eth0 | 498169 / 498169 / 0 | 0 | 504748 / 504748 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r2 | router-eth1 | 93919 / 93919 / 0 | 0 | 93919 / 93919 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r2 | router-eth2 | 1837005 / 1719518 / 117487 | 0 | 1843584 / 1720595 / 122989 | 0 |

### Run-wide packet balance (light check item 4: unacked video + lost background - drops)

| run | before: balance / drops | after: balance / drops |
|---|---|---|
| sim-B-A2-sburst-def-pie-r1 | 627 / 119983 | 529 / 114056 |
| sim-B-A2-sburst-def-pie-r2 | 598 / 117487 | 631 / 122989 |

### Simulation-side values that moved (all others identical)

| run | value | before | after |
|---|---|---|---|
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.app_limited_rows | 0.9062 | 0.919 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.drain | None | 0.0019 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.probe_bw | 0.95 | 0.9435 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.probe_rtt | 0.0012 | 0.0019 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.startup | 0.0488 | 0.0527 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.app_limited_rows | 0.8667 | 0.8665 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.mode_share.probe_bw | 0.9398 | 0.9421 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.mode_share.probe_rtt | 0.0107 | 0.0092 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.mode_share.startup | 0.0495 | 0.0487 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-c.app_limited_rows | 0.8613 | 0.8673 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-c.mode_share.probe_bw | 0.9391 | 0.9395 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-c.mode_share.startup | 0.0485 | 0.0481 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.app_limited_rows | 0.8458 | 0.8302 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.mode_share.probe_bw | 0.9387 | 0.9385 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.mode_share.probe_rtt | 0.0128 | 0.0134 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.mode_share.startup | 0.0485 | 0.048 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_delay_p50_ms | 1681 | 1642 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_delay_p90_ms | 2727 | 2428 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_fa_min | 1.298 | 1.473 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_p | 0.9054 | 0.8919 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_r | 0.7701 | 0.7586 * |
| sim-B-A2-sburst-def-pie-r1 | f1_mean | 0.4171 | 0.4081 * |
| sim-B-A2-sburst-def-pie-r1 | f1_sigma | 0.532 | 0.5243 * |
| sim-B-A2-sburst-def-pie-r1 | gop_drops_per_client_min | 2.552 | 2.955 * |
| sim-B-A2-sburst-def-pie-r1 | keyframe.main.max | 4 | 4.1 * |
| sim-B-A2-sburst-def-pie-r1 | keyframe.main.p50 | 0.6 | 0.7 * |
| sim-B-A2-sburst-def-pie-r1 | keyframe.main.p90 | 1.5 | 1.3 * |
| sim-B-A2-sburst-def-pie-r1 | keyframe.main.ref_minus_spread_ms | -12.4 | -13.1 * |
| sim-B-A2-sburst-def-pie-r1 | keyframe.main.spread_ms | 30.6 | 31.3 * |
| sim-B-A2-sburst-def-pie-r1 | q_peak.router->switch.p50 | 0.9323 | 0.931 * |
| sim-B-A2-sburst-def-pie-r1 | q_peak.router->switch.p90 | 2.14 | 2.009 * |
| sim-B-A2-sburst-def-pie-r1 | q_peak_p50_ms | 0.9323 | 0.931 * |
| sim-B-A2-sburst-def-pie-r1 | rate_in_stimulus | 0.7962 | 0.7851 * |
| sim-B-A2-sburst-def-pie-r1 | sets.V k2.robust.other | 0.95 | 0.8421 * |
| sim-B-A2-sburst-def-pie-r1 | sets.V k2.robust_n.other | 20 | 19 * |
| sim-B-A2-sburst-def-pie-r1 | sets.V k2.spur | 0.25 | 0 * |
| sim-B-A2-sburst-def-pie-r1 | sets.V k3.robust.other | 0.9 | 0.8421 * |
| sim-B-A2-sburst-def-pie-r1 | sets.V k3.robust_n.other | 20 | 19 * |
| sim-B-A2-sburst-def-pie-r1 | sets.V k3.spur | 0.25 | 0 * |
| sim-B-A2-sburst-def-pie-r1 | spread_p50_ms | 33 | 33 * |
| sim-B-A2-sburst-def-pie-r1 | spread_p90_ms | 264 | 66 * |
| sim-B-A2-sburst-def-pie-r1 | spread_p99_ms | 455.7 | 202.9 * |
| sim-B-A2-sburst-def-pie-r1 | v2_delay_p50_ms | 144.5 | 141 * |
| sim-B-A2-sburst-def-pie-r1 | v2_delay_p90_ms | 204.7 | 200.2 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.app_limited_rows | 0.9155 | 0.919 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.mode_share.probe_bw | 0.951 | 0.9394 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.mode_share.startup | 0.0477 | 0.0593 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.app_limited_rows | 0.8674 | 0.8547 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.mode_share.probe_bw | 0.9439 | 0.9437 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.mode_share.probe_rtt | 0.0093 | 0.0088 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.mode_share.startup | 0.0468 | 0.0475 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.app_limited_rows | 0.8844 | 0.8674 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.mode_share.probe_bw | 0.9418 | 0.9413 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.mode_share.startup | 0.0469 | 0.0473 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.app_limited_rows | 0.8429 | 0.8478 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.mode_share.probe_bw | 0.9409 | 0.9374 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.mode_share.probe_rtt | 0.0126 | 0.0155 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.mode_share.startup | 0.0465 | 0.0471 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_delay_p50_ms | 1633 | 1593 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_delay_p90_ms | 2263 | 2168 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_episodes | 84 | 86 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_fa_min | 1.394 | 1.247 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_p | 0.8947 | 0.8986 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_r | 0.8095 | 0.7209 * |
| sim-B-A2-sburst-def-pie-r2 | f1_mean | 0.4284 | 0.4406 * |
| sim-B-A2-sburst-def-pie-r2 | f1_sigma | 0.5798 | 0.5752 * |
| sim-B-A2-sburst-def-pie-r2 | gop_drops_per_client_min | 2.616 | 2.18 * |
| sim-B-A2-sburst-def-pie-r2 | gt3_r | 0.8571 | 0.8372 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.max | 4.4 | 3.8 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.p90 | 1.6 | 1.7 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.ref_minus_spread_ms | -12.3 | -11.1 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.spread_ms | 30.4 | 29.3 * |
| sim-B-A2-sburst-def-pie-r2 | q_peak.router->switch.p50 | 0.8012 | 0.931 * |
| sim-B-A2-sburst-def-pie-r2 | q_peak.router->switch.p90 | 2.787 | 2.141 * |
| sim-B-A2-sburst-def-pie-r2 | q_peak_p50_ms | 0.8012 | 0.931 * |
| sim-B-A2-sburst-def-pie-r2 | rate_in_stimulus | 0.8039 | 0.7793 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k2.robust.other | 0.9474 | 0.95 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k2.robust_n.other | 19 | 20 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k2.spur | 0.2632 | 0.5 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k3.robust.other | 0.8947 | 0.9 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k3.robust_n.other | 19 | 20 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k3.spur | 0.2632 | 0.5 * |
| sim-B-A2-sburst-def-pie-r2 | spread_p50_ms | 33 | 33 * |
| sim-B-A2-sburst-def-pie-r2 | spread_p90_ms | 108.9 | 155.1 * |
| sim-B-A2-sburst-def-pie-r2 | spread_p99_ms | 268.9 | 472.6 * |
| sim-B-A2-sburst-def-pie-r2 | v2_delay_p50_ms | 132 | 134 * |
| sim-B-A2-sburst-def-pie-r2 | v2_episodes | 84 | 86 * |
| sim-B-A2-sburst-def-pie-r2 | v2_r | 0.8571 | 0.8372 * |

### Agreement verdicts that changed (tables-matched.md)

| metric | run | before: testbed / sim / verdict | after |
|---|---|---|---|
| q_peak_p50_ms | sim-B-A2-sburst-def-pie-r1 | 2.011 / 0.932 / FAIL | 2.011 / 0.931 / FAIL |
| q_peak_p50_ms | sim-B-A2-sburst-def-pie-r2 | 1.859 / 0.801 / FAIL | 1.859 / 0.931 / FAIL |
| f1_mean | sim-B-A2-sburst-def-pie-r1 | 0.744 / 0.417 / FAIL | 0.744 / 0.408 / FAIL |
| f1_mean | sim-B-A2-sburst-def-pie-r2 | 0.607 / 0.428 / ok | 0.607 / 0.441 / ok |
| f1_sigma | sim-B-A2-sburst-def-pie-r1 | 0.856 / 0.532 / FAIL | 0.856 / 0.524 / FAIL |
| f1_sigma | sim-B-A2-sburst-def-pie-r2 | 0.672 / 0.580 / ok | 0.672 / 0.575 / ok |
| v2_delay_p50_ms | sim-B-A2-sburst-def-pie-r1 | 172.800 / 144.500 / ok | 172.800 / 141.000 / ok |
| v2_delay_p50_ms | sim-B-A2-sburst-def-pie-r2 | 157.700 / 132.000 / ok | 157.700 / 134.000 / ok |
| gt3_r | sim-B-A2-sburst-def-pie-r2 | 0.837 / 0.857 / ok | 0.837 / 0.837 / ok |
| spread_p90_ms | sim-B-A2-sburst-def-pie-r1 | 118.800 / 264.000 / FAIL | 118.800 / 66.000 / FAIL |
| spread_p90_ms | sim-B-A2-sburst-def-pie-r2 | 141.900 / 108.900 / ok | 141.900 / 155.100 / ok |
| d1bw_delay_p50_ms | sim-B-A2-sburst-def-pie-r1 | 1216.657 / 1680.773 / FAIL | 1216.657 / 1641.692 / FAIL |
| d1bw_delay_p50_ms | sim-B-A2-sburst-def-pie-r2 | 1099.929 / 1632.529 / FAIL | 1099.929 / 1592.837 / FAIL |
| spread_p99_ms | sim-B-A2-sburst-def-pie-r1 | 712.800 / 455.730 / 455.730 | 712.800 / 202.950 / 202.950 * |
| spread_p99_ms | sim-B-A2-sburst-def-pie-r2 | 274.560 / 268.950 / 268.950 | 274.560 / 472.560 / 472.560 * |
| v2_delay_p90_ms | sim-B-A2-sburst-def-pie-r1 | 223.000 / 204.700 / 204.700 | 223.000 / 200.200 / 200.200 * |
| d1bw_p | sim-B-A2-sburst-def-pie-r1 | 0.985 / 0.905 / 0.905 | 0.985 / 0.892 / 0.892 * |
| d1bw_p | sim-B-A2-sburst-def-pie-r2 | 0.905 / 0.895 / 0.895 | 0.905 / 0.899 / 0.899 * |
| d1bw_r | sim-B-A2-sburst-def-pie-r1 | 0.857 / 0.770 / 0.770 | 0.857 / 0.759 / 0.759 * |
| d1bw_r | sim-B-A2-sburst-def-pie-r2 | 0.779 / 0.810 / 0.810 | 0.779 / 0.721 / 0.721 * |
| gop_drops_per_client_min | sim-B-A2-sburst-def-pie-r1 | 1.701 / 2.552 / 2.552 | 1.701 / 2.955 / 2.955 * |
| gop_drops_per_client_min | sim-B-A2-sburst-def-pie-r2 | 1.657 / 2.616 / 2.616 | 1.657 / 2.180 / 2.180 * |
| rate_in_stimulus | sim-B-A2-sburst-def-pie-r1 | 0.863 / 0.796 / 0.796 | 0.863 / 0.785 / 0.785 * |
| rate_in_stimulus | sim-B-A2-sburst-def-pie-r2 | 0.878 / 0.804 / 0.804 | 0.878 / 0.779 / 0.779 * |

## spec: 2 runs matching 'pie'

### Packet identity per egress (tracer counts): enq / deq / drop, residual enq - deq - drop

| run | egress | before | residual before | after | residual after |
|---|---|---|---|---|---|
| sim-B-A2-sburst-def-pie-r1 | pub-eth0 | 488887 / 488887 / 0 | 0 | 491314 / 491314 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r1 | router-eth1 | 91690 / 91690 / 0 | 0 | 91690 / 91690 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r1 | router-eth2 | 1804712 / 1685845 / 118867 | 0 | 1807139 / 1687137 / 120002 | 0 |
| sim-B-A2-sburst-def-pie-r2 | pub-eth0 | 502377 / 502377 / 0 | 0 | 500673 / 500673 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r2 | router-eth1 | 93923 / 93923 / 0 | 0 | 93923 / 93923 / 0 | 0 |
| sim-B-A2-sburst-def-pie-r2 | router-eth2 | 1841209 / 1720391 / 120818 | 0 | 1839505 / 1719000 / 120505 | 0 |

### Run-wide packet balance (light check item 4: unacked video + lost background - drops)

| run | before: balance / drops | after: balance / drops |
|---|---|---|
| sim-B-A2-sburst-def-pie-r1 | 724 / 118867 | 619 / 120002 |
| sim-B-A2-sburst-def-pie-r2 | 668 / 120818 | 642 / 120505 |

### Simulation-side values that moved (all others identical)

| run | value | before | after |
|---|---|---|---|
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.app_limited_rows | 0.9361 | 0.9382 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.probe_bw | 0.9461 | 0.94 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.probe_rtt | 0.0049 | 0.0063 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-a.mode_share.startup | 0.0489 | 0.0537 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.app_limited_rows | 0.9209 | 0.9219 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.key_gain_p50 | 0.99 | 1.237 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.mode_share.probe_bw | 0.9454 | 0.9447 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.mode_share.probe_rtt | 0.005 | 0.0053 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-b.mode_share.startup | 0.0496 | 0.0501 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-c.app_limited_rows | 0.9367 | 0.9309 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-c.mode_share.probe_bw | 0.9454 | 0.9417 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-c.mode_share.startup | 0.0478 | 0.0516 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.app_limited_rows | 0.927 | 0.9204 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.mode_share.probe_bw | 0.949 | 0.9487 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.mode_share.probe_rtt | 0.002 | 0.0021 * |
| sim-B-A2-sburst-def-pie-r1 | bbr.sub-d.mode_share.startup | 0.049 | 0.0492 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_delay_p50_ms | 1721 | 1663 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_delay_p90_ms | 2518 | 2341 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_episodes | 80 | 91 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_fa_min | 0.4409 | 0.4383 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_p | 0.9714 | 0.9726 * |
| sim-B-A2-sburst-def-pie-r1 | d1bw_r | 0.85 | 0.7802 * |
| sim-B-A2-sburst-def-pie-r1 | f1_mean | 0.4517 | 0.4553 * |
| sim-B-A2-sburst-def-pie-r1 | f1_sigma | 0.2777 | 0.2845 * |
| sim-B-A2-sburst-def-pie-r1 | gop_drops_per_client_min | 3 | 2.328 * |
| sim-B-A2-sburst-def-pie-r1 | gt3_r | 0.9 | 0.7912 * |
| sim-B-A2-sburst-def-pie-r1 | keyframe.main.max | 6.5 | 7.3 * |
| sim-B-A2-sburst-def-pie-r1 | q_peak.router->switch.p50 | 2.145 | 2.274 * |
| sim-B-A2-sburst-def-pie-r1 | q_peak.router->switch.p90 | 4.957 | 5.289 * |
| sim-B-A2-sburst-def-pie-r1 | q_peak_p50_ms | 2.145 | 2.274 * |
| sim-B-A2-sburst-def-pie-r1 | rate_in_stimulus | 0.7784 | 0.8017 * |
| sim-B-A2-sburst-def-pie-r1 | spread_p50_ms | 33 | 49.5 * |
| sim-B-A2-sburst-def-pie-r1 | spread_p99_ms | 587.1 | 422.7 * |
| sim-B-A2-sburst-def-pie-r1 | v2_delay_p50_ms | 146.5 | 143.5 * |
| sim-B-A2-sburst-def-pie-r1 | v2_delay_p90_ms | 192.6 | 186.8 * |
| sim-B-A2-sburst-def-pie-r1 | v2_episodes | 80 | 91 * |
| sim-B-A2-sburst-def-pie-r1 | v2_r | 0.9 | 0.7912 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.app_limited_rows | 0.9429 | 0.9403 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.mode_share.probe_bw | 0.9453 | 0.9448 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.mode_share.probe_rtt | 0.0068 | 0.008 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-a.mode_share.startup | 0.048 | 0.0473 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.app_limited_rows | 0.9176 | 0.9277 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.mode_share.probe_bw | 0.9478 | 0.9461 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.mode_share.probe_rtt | 0.0051 | 0.0063 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-b.mode_share.startup | 0.0471 | 0.0475 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.app_limited_rows | 0.9332 | 0.9324 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.mode_share.probe_bw | 0.9461 | 0.9445 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.mode_share.probe_rtt | 0.0069 | 0.0077 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-c.mode_share.startup | 0.0469 | 0.0479 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.app_limited_rows | 0.9347 | 0.924 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.mode_share.probe_bw | 0.9491 | 0.9489 * |
| sim-B-A2-sburst-def-pie-r2 | bbr.sub-d.mode_share.probe_rtt | 0.0034 | 0.0036 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_delay_p50_ms | 1648 | 1639 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_delay_p90_ms | 2353 | 2200 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_episodes | 89 | 83 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_fa_min | 0.6352 | 0.4112 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_p | 0.9565 | 0.9714 * |
| sim-B-A2-sburst-def-pie-r2 | d1bw_r | 0.7416 | 0.8193 * |
| sim-B-A2-sburst-def-pie-r2 | f1_mean | 0.4409 | 0.4355 * |
| sim-B-A2-sburst-def-pie-r2 | f1_sigma | 0.278 | 0.2857 * |
| sim-B-A2-sburst-def-pie-r2 | gop_drops_per_client_min | 2.573 | 2.878 * |
| sim-B-A2-sburst-def-pie-r2 | gt3_r | 0.809 | 0.8675 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.max | 7.4 | 7.7 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.p50 | 1.7 | 1.6 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.p90 | 4.1 | 4.2 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.ref_minus_spread_ms | -4.1 | -5.3 * |
| sim-B-A2-sburst-def-pie-r2 | keyframe.main.spread_ms | 22.3 | 23.5 * |
| sim-B-A2-sburst-def-pie-r2 | q_peak.router->switch.p50 | 2 | 1.872 * |
| sim-B-A2-sburst-def-pie-r2 | q_peak.router->switch.p90 | 4.493 | 5.093 * |
| sim-B-A2-sburst-def-pie-r2 | q_peak_p50_ms | 2 | 1.872 * |
| sim-B-A2-sburst-def-pie-r2 | rate_in_stimulus | 0.8093 | 0.8193 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k2.robust.other | 0.9474 | 0.95 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k2.robust_n.other | 19 | 20 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k2.spur | 0.2632 | 0.05 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k3.robust.other | 0.8947 | 0.9 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k3.robust_n.other | 19 | 20 * |
| sim-B-A2-sburst-def-pie-r2 | sets.V k3.spur | 0.2632 | 0.05 * |
| sim-B-A2-sburst-def-pie-r2 | spread_p50_ms | 49.5 | 66 * |
| sim-B-A2-sburst-def-pie-r2 | spread_p90_ms | 132 | 141.9 * |
| sim-B-A2-sburst-def-pie-r2 | spread_p99_ms | 159.4 | 247.2 * |
| sim-B-A2-sburst-def-pie-r2 | v2_episodes | 89 | 83 * |
| sim-B-A2-sburst-def-pie-r2 | v2_r | 0.809 | 0.8675 * |

### Agreement verdicts that changed (tables-spec.md)

| metric | run | before: testbed / sim / verdict | after |
|---|---|---|---|
| q_peak_p50_ms | sim-B-A2-sburst-def-pie-r1 | 2.011 / 2.145 / ok | 2.011 / 2.274 / ok |
| q_peak_p50_ms | sim-B-A2-sburst-def-pie-r2 | 1.859 / 2.000 / ok | 1.859 / 1.872 / ok |
| f1_mean | sim-B-A2-sburst-def-pie-r1 | 0.744 / 0.452 / FAIL | 0.744 / 0.455 / FAIL |
| f1_mean | sim-B-A2-sburst-def-pie-r2 | 0.607 / 0.441 / ok | 0.607 / 0.435 / ok |
| f1_sigma | sim-B-A2-sburst-def-pie-r1 | 0.856 / 0.278 / FAIL | 0.856 / 0.285 / FAIL |
| f1_sigma | sim-B-A2-sburst-def-pie-r2 | 0.672 / 0.278 / FAIL | 0.672 / 0.286 / FAIL |
| v2_delay_p50_ms | sim-B-A2-sburst-def-pie-r1 | 172.800 / 146.500 / ok | 172.800 / 143.500 / ok |
| gt3_r | sim-B-A2-sburst-def-pie-r1 | 0.935 / 0.900 / ok | 0.935 / 0.791 / FAIL * |
| gt3_r | sim-B-A2-sburst-def-pie-r2 | 0.837 / 0.809 / ok | 0.837 / 0.867 / ok |
| spread_p50_ms | sim-B-A2-sburst-def-pie-r1 | 49.500 / 33.000 / ok | 49.500 / 49.500 / ok |
| spread_p50_ms | sim-B-A2-sburst-def-pie-r2 | 33.000 / 49.500 / ok | 33.000 / 66.000 / ok |
| spread_p90_ms | sim-B-A2-sburst-def-pie-r2 | 141.900 / 132.000 / ok | 141.900 / 141.900 / ok |
| d1bw_delay_p50_ms | sim-B-A2-sburst-def-pie-r1 | 1216.657 / 1720.756 / FAIL | 1216.657 / 1663.154 / FAIL |
| d1bw_delay_p50_ms | sim-B-A2-sburst-def-pie-r2 | 1099.929 / 1647.750 / FAIL | 1099.929 / 1639.243 / FAIL |
| spread_p99_ms | sim-B-A2-sburst-def-pie-r1 | 712.800 / 587.070 / 587.070 | 712.800 / 422.730 / 422.730 * |
| spread_p99_ms | sim-B-A2-sburst-def-pie-r2 | 274.560 / 159.390 / 159.390 | 274.560 / 247.170 / 247.170 * |
| v2_delay_p90_ms | sim-B-A2-sburst-def-pie-r1 | 223.000 / 192.600 / 192.600 | 223.000 / 186.800 / 186.800 * |
| d1bw_p | sim-B-A2-sburst-def-pie-r1 | 0.985 / 0.971 / 0.971 | 0.985 / 0.973 / 0.973 * |
| d1bw_p | sim-B-A2-sburst-def-pie-r2 | 0.905 / 0.957 / 0.957 | 0.905 / 0.971 / 0.971 * |
| d1bw_r | sim-B-A2-sburst-def-pie-r1 | 0.857 / 0.850 / 0.850 | 0.857 / 0.780 / 0.780 * |
| d1bw_r | sim-B-A2-sburst-def-pie-r2 | 0.779 / 0.742 / 0.742 | 0.779 / 0.819 / 0.819 * |
| gop_drops_per_client_min | sim-B-A2-sburst-def-pie-r1 | 1.701 / 3.000 / 3.000 | 1.701 / 2.328 / 2.328 * |
| gop_drops_per_client_min | sim-B-A2-sburst-def-pie-r2 | 1.657 / 2.573 / 2.573 | 1.657 / 2.878 / 2.878 * |
| rate_in_stimulus | sim-B-A2-sburst-def-pie-r1 | 0.863 / 0.778 / 0.778 | 0.863 / 0.802 / 0.802 * |
| rate_in_stimulus | sim-B-A2-sburst-def-pie-r2 | 0.878 / 0.809 / 0.809 | 0.878 / 0.819 / 0.819 * |
