
### q_peak_p50_ms (limit: rel 0.2)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.859 | 1.204 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 2.153 | 1.474 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 2.011 | 0.931 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1.859 | 0.931 | FAIL |
| sim-B-A4-hhier-def-pfifo-r1 | 2.452 | 1.408 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 2.589 | 1.959 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 19.181 | 11.038 | FAIL |

### f1_mean (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.628 | 0.530 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.671 | 0.673 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.744 | 0.408 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.607 | 0.441 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.966 | 1.227 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 2.029 | 1.655 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 3.203 | 3.430 | ok |

### f1_sigma (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.657 | 0.580 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.711 | 0.655 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.856 | 0.524 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.672 | 0.575 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.473 | 0.859 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 1.469 | 0.921 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 2.935 | 1.838 | FAIL |

### v2_delay_p50_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 112.700 | 123.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 173.500 | 150.500 | ok |
| sim-B-A2-sburst-def-pie-r1 | 172.800 | 141.000 | ok |
| sim-B-A2-sburst-def-pie-r2 | 157.700 | 134.000 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 165.200 | 137.500 | ok |
| sim-B-A4-hhier-def-codel-r1 | 207.300 | 156.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 129.200 | 164.500 | ok |

### gt3_p (limit: min 0.98)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 1.000 | ok |

### gt3_r (limit: abs 0.05)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.935 | 0.828 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.837 | 0.837 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 0.997 | 0.988 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 1.000 | ok |

### spread_p50_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 49.500 | 33.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 33.000 | 33.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 49.500 | 33.000 | ok |
| sim-B-A2-sburst-def-pie-r2 | 33.000 | 33.000 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 33.000 | 33.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 33.000 | 33.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 99.000 | 99.000 | ok |

### spread_p90_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 99.000 | 66.000 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 231.000 | 231.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 118.800 | 66.000 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 141.900 | 155.100 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 99.000 | 99.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 132.000 | 99.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 207.900 | 481.800 | FAIL |

### d1bw_delay_p50_ms (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 506.929 | 1378.899 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 1170.275 | 2288.951 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 1216.657 | 1641.692 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1099.929 | 1592.837 | FAIL |
| sim-B-A4-hhier-def-pfifo-r1 | 505.818 | 1675.321 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 1765.520 | 3479.219 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 432.298 | 1946.462 | FAIL |

### gt3B_p (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | nan |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | nan |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | nan |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | nan |

### gt3B_r (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.952 | nan |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r1 | 0.860 | nan |
| sim-B-A2-sburst-def-pie-r2 | 0.877 | nan |
| sim-B-A4-hhier-def-pfifo-r1 | 0.987 | nan |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | nan |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | nan |

### spread_p99_ms (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 235.950 | 202.950 |
| sim-B-A2-sburst-def-codel-r1 | 340.560 | 313.170 |
| sim-B-A2-sburst-def-pie-r1 | 712.800 | 202.950 |
| sim-B-A2-sburst-def-pie-r2 | 274.560 | 472.560 |
| sim-B-A4-hhier-def-pfifo-r1 | 413.160 | 206.580 |
| sim-B-A4-hhier-def-codel-r1 | 437.580 | 364.320 |
| sim-B-G1-sburst-n16-pfifo-r1 | 285.780 | 582.780 |

### spread_n (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-codel-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pie-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pie-r2 | 18.000 | 18.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 75.000 | 75.000 |
| sim-B-A4-hhier-def-codel-r1 | 75.000 | 75.000 |
| sim-B-G1-sburst-n16-pfifo-r1 | 18.000 | 18.000 |

### stim_member_hit (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | 1.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | 1.000 |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 1.000 |

### v2_delay_p90_ms (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 206.700 | 189.900 |
| sim-B-A2-sburst-def-codel-r1 | 251.800 | 222.400 |
| sim-B-A2-sburst-def-pie-r1 | 223.000 | 200.200 |
| sim-B-A2-sburst-def-pie-r2 | 195.600 | 189.500 |
| sim-B-A4-hhier-def-pfifo-r1 | 258.200 | 188.000 |
| sim-B-A4-hhier-def-codel-r1 | 287.300 | 200.600 |
| sim-B-G1-sburst-n16-pfifo-r1 | 554.700 | 354.000 |

### v2_fa_min (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-codel-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pie-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pie-r2 | 0.000 | 0.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A4-hhier-def-codel-r1 | 0.000 | 0.000 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.000 | 0.000 |

### d1bw_p (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.910 | 0.893 |
| sim-B-A2-sburst-def-codel-r1 | 0.942 | 0.932 |
| sim-B-A2-sburst-def-pie-r1 | 0.985 | 0.892 |
| sim-B-A2-sburst-def-pie-r2 | 0.905 | 0.899 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.965 | 0.965 |
| sim-B-A4-hhier-def-codel-r1 | 0.983 | 0.961 |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 0.908 |

### d1bw_r (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.986 | 0.931 |
| sim-B-A2-sburst-def-codel-r1 | 0.903 | 0.764 |
| sim-B-A2-sburst-def-pie-r1 | 0.857 | 0.759 |
| sim-B-A2-sburst-def-pie-r2 | 0.779 | 0.721 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.976 | 0.914 |
| sim-B-A4-hhier-def-codel-r1 | 0.884 | 0.648 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.997 | 0.854 |

### gop_drops_per_client_min (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 8.239 | 2.597 |
| sim-B-A2-sburst-def-codel-r1 | 8.328 | 5.149 |
| sim-B-A2-sburst-def-pie-r1 | 1.701 | 2.955 |
| sim-B-A2-sburst-def-pie-r2 | 1.657 | 2.180 |
| sim-B-A4-hhier-def-pfifo-r1 | 4.164 | 1.633 |
| sim-B-A4-hhier-def-codel-r1 | 6.563 | 3.854 |
| sim-B-G1-sburst-n16-pfifo-r1 | 3.336 | 0.739 |

### rate_in_stimulus (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A2-sburst-def-pfifo-r1 | 0.594 | 0.794 |
| sim-B-A2-sburst-def-codel-r1 | 0.586 | 0.705 |
| sim-B-A2-sburst-def-pie-r1 | 0.863 | 0.785 |
| sim-B-A2-sburst-def-pie-r2 | 0.878 | 0.779 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.678 | 0.811 |
| sim-B-A4-hhier-def-codel-r1 | 0.571 | 0.667 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.768 | 0.891 |
