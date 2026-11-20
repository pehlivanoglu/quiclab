
### q_peak_p50_ms (limit: rel 0.2)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.859 | 2.334 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 2.153 | 3.731 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 2.011 | 2.274 | ok |
| sim-B-A2-sburst-def-pie-r2 | 1.859 | 1.872 | ok |

### f1_mean (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.628 | 0.468 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.671 | 0.575 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.744 | 0.455 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.607 | 0.435 | ok |

### f1_sigma (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.657 | 0.292 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 0.711 | 0.279 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 0.856 | 0.285 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.672 | 0.286 | FAIL |

### v2_delay_p50_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 112.700 | 123.500 | ok |
| sim-B-A2-sburst-def-codel-r1 | 173.500 | 143.500 | ok |
| sim-B-A2-sburst-def-pie-r1 | 172.800 | 143.500 | ok |
| sim-B-A2-sburst-def-pie-r2 | 157.700 | 134.000 | ok |

### gt3_p (limit: min 0.98)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | 1.000 | ok |

### gt3_r (limit: abs 0.05)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.935 | 0.791 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.837 | 0.867 | ok |

### spread_p50_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 49.500 | 49.500 | ok |
| sim-B-A2-sburst-def-codel-r1 | 33.000 | 33.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 49.500 | 49.500 | ok |
| sim-B-A2-sburst-def-pie-r2 | 33.000 | 66.000 | ok |

### spread_p90_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 99.000 | 151.800 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 231.000 | 138.600 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 118.800 | 161.700 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 141.900 | 141.900 | ok |

### d1bw_delay_p50_ms (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 506.929 | 1262.568 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 1170.275 | 2593.838 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 1216.657 | 1663.154 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1099.929 | 1639.243 | FAIL |

### gt3B_p (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | nan |

### gt3B_r (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.952 | nan |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r1 | 0.860 | nan |
| sim-B-A2-sburst-def-pie-r2 | 0.877 | nan |

### spread_p99_ms (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 235.950 | 225.390 |
| sim-B-A2-sburst-def-codel-r1 | 340.560 | 422.730 |
| sim-B-A2-sburst-def-pie-r1 | 712.800 | 422.730 |
| sim-B-A2-sburst-def-pie-r2 | 274.560 | 247.170 |

### spread_n (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-codel-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pie-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pie-r2 | 18.000 | 18.000 |

### stim_member_hit (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | 1.000 |

### v2_delay_p90_ms (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 206.700 | 182.000 |
| sim-B-A2-sburst-def-codel-r1 | 251.800 | 188.800 |
| sim-B-A2-sburst-def-pie-r1 | 223.000 | 186.800 |
| sim-B-A2-sburst-def-pie-r2 | 195.600 | 188.500 |

### v2_fa_min (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-codel-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pie-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pie-r2 | 0.000 | 0.000 |

### d1bw_p (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.910 | 0.972 |
| sim-B-A2-sburst-def-codel-r1 | 0.942 | 0.982 |
| sim-B-A2-sburst-def-pie-r1 | 0.985 | 0.973 |
| sim-B-A2-sburst-def-pie-r2 | 0.905 | 0.971 |

### d1bw_r (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.986 | 0.958 |
| sim-B-A2-sburst-def-codel-r1 | 0.903 | 0.750 |
| sim-B-A2-sburst-def-pie-r1 | 0.857 | 0.780 |
| sim-B-A2-sburst-def-pie-r2 | 0.779 | 0.819 |

### gop_drops_per_client_min (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 8.239 | 3.134 |
| sim-B-A2-sburst-def-codel-r1 | 8.328 | 6.269 |
| sim-B-A2-sburst-def-pie-r1 | 1.701 | 2.328 |
| sim-B-A2-sburst-def-pie-r2 | 1.657 | 2.878 |

### rate_in_stimulus (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.594 | 0.773 |
| sim-B-A2-sburst-def-codel-r1 | 0.586 | 0.672 |
| sim-B-A2-sburst-def-pie-r1 | 0.863 | 0.802 |
| sim-B-A2-sburst-def-pie-r2 | 0.878 | 0.819 |
