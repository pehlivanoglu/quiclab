
### q_peak_p50_ms (limit: rel 0.2)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | 13.857 | 12.109 | ok |
| sim-B-A1-calm-base-pfifo-r2 | 13.384 | 10.815 | ok |
| sim-B-A1-calm-base-codel-r1 | 14.800 | 12.109 | ok |
| sim-B-A1-calm-base-codel-r2 | 13.803 | 10.815 | FAIL |
| sim-B-A1-calm-split4l-pfifo-r1 | 5.589 | 4.011 | FAIL |
| sim-B-A1-calm-split4l-pfifo-r2 | 4.889 | 3.932 | ok |
| sim-B-A1-calm-split4l-codel-r1 | 5.413 | 4.011 | FAIL |
| sim-B-A1-calm-split4l-codel-r2 | 5.216 | 3.932 | FAIL |
| sim-B-A2-sburst-def-pfifo-r1 | 1.859 | 1.204 | FAIL |
| sim-B-A2-sburst-def-pfifo-r2 | 2.021 | 1.208 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 2.153 | 1.474 | FAIL |
| sim-B-A2-sburst-def-codel-r2 | 1.997 | 1.348 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 2.011 | 1.063 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1.859 | 0.931 | FAIL |
| sim-B-A4-hhier-def-pfifo-r1 | 2.452 | 1.408 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 2.693 | 1.381 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 2.589 | 1.959 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 2.672 | 1.786 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 19.181 | 11.038 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 17.889 | 10.687 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 19.041 | 10.809 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 18.441 | 10.718 | FAIL |

### f1_mean (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | 2.176 | 2.902 | FAIL |
| sim-B-A1-calm-base-pfifo-r2 | 2.149 | 2.742 | ok |
| sim-B-A1-calm-base-codel-r1 | 2.228 | 2.902 | FAIL |
| sim-B-A1-calm-base-codel-r2 | 2.236 | 2.742 | ok |
| sim-B-A1-calm-split4l-pfifo-r1 | 3.235 | 3.923 | ok |
| sim-B-A1-calm-split4l-pfifo-r2 | 3.159 | 3.917 | ok |
| sim-B-A1-calm-split4l-codel-r1 | 3.199 | 3.923 | ok |
| sim-B-A1-calm-split4l-codel-r2 | 3.311 | 3.917 | ok |
| sim-B-A2-sburst-def-pfifo-r1 | 0.628 | 0.530 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 0.678 | 0.555 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.671 | 0.673 | ok |
| sim-B-A2-sburst-def-codel-r2 | 0.675 | 0.586 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.744 | 0.483 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.607 | 0.445 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.966 | 1.227 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 2.054 | 1.252 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 2.029 | 1.655 | ok |
| sim-B-A4-hhier-def-codel-r2 | 2.086 | 1.673 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 3.203 | 3.430 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 3.150 | 3.385 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 3.218 | 3.418 | ok |
| sim-B-G1-sburst-n24-pfifo-r2 | 3.185 | 3.374 | ok |

### f1_sigma (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | 1.444 | 0.864 | FAIL |
| sim-B-A1-calm-base-pfifo-r2 | 1.434 | 0.708 | FAIL |
| sim-B-A1-calm-base-codel-r1 | 1.549 | 0.864 | FAIL |
| sim-B-A1-calm-base-codel-r2 | 1.435 | 0.708 | FAIL |
| sim-B-A1-calm-split4l-pfifo-r1 | 2.354 | 1.307 | FAIL |
| sim-B-A1-calm-split4l-pfifo-r2 | 2.325 | 1.373 | FAIL |
| sim-B-A1-calm-split4l-codel-r1 | 2.316 | 1.307 | FAIL |
| sim-B-A1-calm-split4l-codel-r2 | 2.347 | 1.373 | FAIL |
| sim-B-A2-sburst-def-pfifo-r1 | 0.657 | 0.580 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 0.686 | 0.641 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.711 | 0.655 | ok |
| sim-B-A2-sburst-def-codel-r2 | 0.685 | 0.624 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.856 | 0.559 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.672 | 0.581 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.473 | 0.859 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 1.513 | 0.896 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 1.469 | 0.921 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 1.602 | 1.009 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 2.935 | 1.838 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 2.782 | 1.761 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 2.883 | 1.788 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 2.793 | 1.729 | FAIL |

### v2_delay_p50_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan | n/a |
| sim-B-A2-sburst-def-pfifo-r1 | 112.700 | 123.000 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 95.600 | 120.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 173.500 | 150.500 | ok |
| sim-B-A2-sburst-def-codel-r2 | 163.900 | 133.500 | ok |
| sim-B-A2-sburst-def-pie-r1 | 172.800 | 141.500 | ok |
| sim-B-A2-sburst-def-pie-r2 | 157.700 | 132.500 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 165.200 | 137.500 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 178.200 | 137.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 207.300 | 156.000 | ok |
| sim-B-A4-hhier-def-codel-r2 | 217.700 | 170.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 129.200 | 164.500 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 144.700 | 150.500 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 130.200 | 174.000 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 145.100 | 150.000 | ok |

### gt3_p (limit: min 0.98)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan | n/a |
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r2 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-codel-r2 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r2 | 1.000 | 1.000 | ok |

### gt3_r (limit: abs 0.05)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan | n/a |
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-codel-r2 | 1.000 | 1.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.935 | 0.867 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.837 | 0.867 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 0.997 | 0.988 | ok |
| sim-B-A4-hhier-def-codel-r2 | 1.000 | 0.997 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r2 | 1.000 | 1.000 | ok |

### spread_p50_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan | n/a |
| sim-B-A2-sburst-def-pfifo-r1 | 49.500 | 33.000 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 49.500 | 33.000 | ok |
| sim-B-A2-sburst-def-codel-r1 | 33.000 | 33.000 | ok |
| sim-B-A2-sburst-def-codel-r2 | 66.000 | 33.000 | ok |
| sim-B-A2-sburst-def-pie-r1 | 49.500 | 33.000 | ok |
| sim-B-A2-sburst-def-pie-r2 | 33.000 | 33.000 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 33.000 | 33.000 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 33.000 | 33.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 33.000 | 33.000 | ok |
| sim-B-A4-hhier-def-codel-r2 | 66.000 | 33.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 99.000 | 99.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 99.000 | 66.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 99.000 | 99.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r2 | 132.000 | 82.500 | FAIL |

### spread_p90_ms (limit: rel_or_tick 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan | n/a |
| sim-B-A2-sburst-def-pfifo-r1 | 99.000 | 66.000 | FAIL |
| sim-B-A2-sburst-def-pfifo-r2 | 151.800 | 118.800 | ok |
| sim-B-A2-sburst-def-codel-r1 | 231.000 | 231.000 | ok |
| sim-B-A2-sburst-def-codel-r2 | 141.900 | 151.800 | ok |
| sim-B-A2-sburst-def-pie-r1 | 118.800 | 66.000 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 141.900 | 141.900 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 99.000 | 99.000 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 151.800 | 99.000 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 132.000 | 99.000 | ok |
| sim-B-A4-hhier-def-codel-r2 | 118.800 | 99.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 207.900 | 481.800 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 174.900 | 250.800 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 293.700 | 429.000 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 247.500 | 270.600 | ok |

### d1bw_delay_p50_ms (limit: rel 0.3)

| run | testbed | sim | agreement |
|---|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-base-codel-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan | n/a |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan | n/a |
| sim-B-A2-sburst-def-pfifo-r1 | 506.929 | 1378.899 | FAIL |
| sim-B-A2-sburst-def-pfifo-r2 | 504.802 | 1117.166 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 1170.275 | 2288.951 | FAIL |
| sim-B-A2-sburst-def-codel-r2 | 1153.339 | 2512.423 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 1216.657 | 1680.610 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1099.929 | 1581.909 | FAIL |
| sim-B-A4-hhier-def-pfifo-r1 | 505.818 | 1675.321 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 499.609 | 1642.518 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 1765.520 | 3479.219 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 1795.822 | 3502.034 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 432.298 | 1946.462 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 384.721 | 1843.466 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 412.665 | 1880.410 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 388.273 | 1831.165 | FAIL |

### gt3B_p (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pfifo-r2 | 1.000 | nan |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-codel-r2 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | nan |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | nan |
| sim-B-A4-hhier-def-pfifo-r2 | 1.000 | nan |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | nan |
| sim-B-A4-hhier-def-codel-r2 | 0.999 | nan |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | nan |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | nan |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.997 | nan |
| sim-B-G1-sburst-n24-pfifo-r2 | 1.000 | nan |

### gt3B_r (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 0.952 | nan |
| sim-B-A2-sburst-def-pfifo-r2 | 0.915 | nan |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | nan |
| sim-B-A2-sburst-def-codel-r2 | 1.000 | nan |
| sim-B-A2-sburst-def-pie-r1 | 0.860 | nan |
| sim-B-A2-sburst-def-pie-r2 | 0.877 | nan |
| sim-B-A4-hhier-def-pfifo-r1 | 0.987 | nan |
| sim-B-A4-hhier-def-pfifo-r2 | 0.962 | nan |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | nan |
| sim-B-A4-hhier-def-codel-r2 | 0.996 | nan |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | nan |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | nan |
| sim-B-G1-sburst-n24-pfifo-r1 | 1.000 | nan |
| sim-B-G1-sburst-n24-pfifo-r2 | 1.000 | nan |

### spread_p99_ms (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 235.950 | 202.950 |
| sim-B-A2-sburst-def-pfifo-r2 | 362.340 | 274.560 |
| sim-B-A2-sburst-def-codel-r1 | 340.560 | 313.170 |
| sim-B-A2-sburst-def-codel-r2 | 247.170 | 280.170 |
| sim-B-A2-sburst-def-pie-r1 | 712.800 | 66.000 |
| sim-B-A2-sburst-def-pie-r2 | 274.560 | 329.340 |
| sim-B-A4-hhier-def-pfifo-r1 | 413.160 | 206.580 |
| sim-B-A4-hhier-def-pfifo-r2 | 365.640 | 396.000 |
| sim-B-A4-hhier-def-codel-r1 | 437.580 | 364.320 |
| sim-B-A4-hhier-def-codel-r2 | 397.320 | 265.320 |
| sim-B-G1-sburst-n16-pfifo-r1 | 285.780 | 582.780 |
| sim-B-G1-sburst-n16-pfifo-r2 | 225.390 | 324.390 |
| sim-B-G1-sburst-n24-pfifo-r1 | 363.000 | 538.560 |
| sim-B-G1-sburst-n24-pfifo-r2 | 527.340 | 390.390 |

### spread_n (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-base-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-base-codel-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-base-codel-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-codel-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-codel-r2 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pfifo-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pfifo-r2 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-codel-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-codel-r2 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pie-r1 | 18.000 | 18.000 |
| sim-B-A2-sburst-def-pie-r2 | 18.000 | 18.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 75.000 | 75.000 |
| sim-B-A4-hhier-def-pfifo-r2 | 75.000 | 75.000 |
| sim-B-A4-hhier-def-codel-r1 | 75.000 | 75.000 |
| sim-B-A4-hhier-def-codel-r2 | 75.000 | 75.000 |
| sim-B-G1-sburst-n16-pfifo-r1 | 18.000 | 18.000 |
| sim-B-G1-sburst-n16-pfifo-r2 | 18.000 | 18.000 |
| sim-B-G1-sburst-n24-pfifo-r1 | 18.000 | 18.000 |
| sim-B-G1-sburst-n24-pfifo-r2 | 18.000 | 18.000 |

### stim_member_hit (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pfifo-r2 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-codel-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-codel-r2 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pie-r1 | 1.000 | 1.000 |
| sim-B-A2-sburst-def-pie-r2 | 1.000 | 1.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 |
| sim-B-A4-hhier-def-pfifo-r2 | 1.000 | 1.000 |
| sim-B-A4-hhier-def-codel-r1 | 1.000 | 1.000 |
| sim-B-A4-hhier-def-codel-r2 | 1.000 | 1.000 |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 1.000 |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | 1.000 |
| sim-B-G1-sburst-n24-pfifo-r1 | 1.000 | 1.000 |
| sim-B-G1-sburst-n24-pfifo-r2 | 1.000 | 1.000 |

### v2_delay_p90_ms (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 206.700 | 189.900 |
| sim-B-A2-sburst-def-pfifo-r2 | 189.600 | 189.400 |
| sim-B-A2-sburst-def-codel-r1 | 251.800 | 222.400 |
| sim-B-A2-sburst-def-codel-r2 | 288.700 | 197.700 |
| sim-B-A2-sburst-def-pie-r1 | 223.000 | 184.000 |
| sim-B-A2-sburst-def-pie-r2 | 195.600 | 190.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 258.200 | 188.000 |
| sim-B-A4-hhier-def-pfifo-r2 | 299.700 | 215.500 |
| sim-B-A4-hhier-def-codel-r1 | 287.300 | 200.600 |
| sim-B-A4-hhier-def-codel-r2 | 312.700 | 226.500 |
| sim-B-G1-sburst-n16-pfifo-r1 | 554.700 | 354.000 |
| sim-B-G1-sburst-n16-pfifo-r2 | 423.200 | 325.400 |
| sim-B-G1-sburst-n24-pfifo-r1 | 557.200 | 349.000 |
| sim-B-G1-sburst-n24-pfifo-r2 | 403.000 | 359.000 |

### v2_fa_min (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-base-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-base-codel-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-base-codel-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-codel-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-codel-r2 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-codel-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-codel-r2 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pie-r1 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pie-r2 | 0.000 | 0.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A4-hhier-def-codel-r1 | 0.000 | 0.000 |
| sim-B-A4-hhier-def-codel-r2 | 0.000 | 0.000 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.000 | 0.000 |
| sim-B-G1-sburst-n16-pfifo-r2 | 0.000 | 0.000 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.000 | 0.000 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.000 | 0.000 |

### d1bw_p (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 0.910 | 0.893 |
| sim-B-A2-sburst-def-pfifo-r2 | 0.972 | 0.932 |
| sim-B-A2-sburst-def-codel-r1 | 0.942 | 0.932 |
| sim-B-A2-sburst-def-codel-r2 | 0.955 | 0.982 |
| sim-B-A2-sburst-def-pie-r1 | 0.985 | 0.907 |
| sim-B-A2-sburst-def-pie-r2 | 0.905 | 0.919 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.965 | 0.965 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.951 | 0.931 |
| sim-B-A4-hhier-def-codel-r1 | 0.983 | 0.961 |
| sim-B-A4-hhier-def-codel-r2 | 0.975 | 0.973 |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 0.908 |
| sim-B-G1-sburst-n16-pfifo-r2 | 0.997 | 0.934 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.998 | 0.924 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.998 | 0.935 |

### d1bw_r (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 0.986 | 0.931 |
| sim-B-A2-sburst-def-pfifo-r2 | 0.972 | 0.944 |
| sim-B-A2-sburst-def-codel-r1 | 0.903 | 0.764 |
| sim-B-A2-sburst-def-codel-r2 | 0.875 | 0.750 |
| sim-B-A2-sburst-def-pie-r1 | 0.857 | 0.819 |
| sim-B-A2-sburst-def-pie-r2 | 0.779 | 0.819 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.976 | 0.914 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.979 | 0.929 |
| sim-B-A4-hhier-def-codel-r1 | 0.884 | 0.648 |
| sim-B-A4-hhier-def-codel-r2 | 0.917 | 0.647 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.997 | 0.854 |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | 0.837 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.991 | 0.840 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.991 | 0.870 |

### gop_drops_per_client_min (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-base-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-base-codel-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-base-codel-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-pfifo-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-pfifo-r2 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-codel-r1 | 0.000 | 0.000 |
| sim-B-A1-calm-split4l-codel-r2 | 0.000 | 0.000 |
| sim-B-A2-sburst-def-pfifo-r1 | 8.239 | 2.597 |
| sim-B-A2-sburst-def-pfifo-r2 | 8.328 | 3.052 |
| sim-B-A2-sburst-def-codel-r1 | 8.328 | 5.149 |
| sim-B-A2-sburst-def-codel-r2 | 8.765 | 5.494 |
| sim-B-A2-sburst-def-pie-r1 | 1.701 | 1.970 |
| sim-B-A2-sburst-def-pie-r2 | 1.657 | 2.573 |
| sim-B-A4-hhier-def-pfifo-r1 | 4.164 | 1.633 |
| sim-B-A4-hhier-def-pfifo-r2 | 5.295 | 1.672 |
| sim-B-A4-hhier-def-codel-r1 | 6.563 | 3.854 |
| sim-B-A4-hhier-def-codel-r2 | 6.306 | 3.798 |
| sim-B-G1-sburst-n16-pfifo-r1 | 3.336 | 0.739 |
| sim-B-G1-sburst-n16-pfifo-r2 | 3.227 | 0.807 |
| sim-B-G1-sburst-n24-pfifo-r1 | 3.157 | 0.858 |
| sim-B-G1-sburst-n24-pfifo-r2 | 3.249 | 0.727 |

### rate_in_stimulus (no limit)

| run | testbed | sim |
|---|---|---|
| sim-B-A1-calm-base-pfifo-r1 | nan | nan |
| sim-B-A1-calm-base-pfifo-r2 | nan | nan |
| sim-B-A1-calm-base-codel-r1 | nan | nan |
| sim-B-A1-calm-base-codel-r2 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r1 | nan | nan |
| sim-B-A1-calm-split4l-pfifo-r2 | nan | nan |
| sim-B-A1-calm-split4l-codel-r1 | nan | nan |
| sim-B-A1-calm-split4l-codel-r2 | nan | nan |
| sim-B-A2-sburst-def-pfifo-r1 | 0.594 | 0.794 |
| sim-B-A2-sburst-def-pfifo-r2 | 0.614 | 0.793 |
| sim-B-A2-sburst-def-codel-r1 | 0.586 | 0.705 |
| sim-B-A2-sburst-def-codel-r2 | 0.598 | 0.718 |
| sim-B-A2-sburst-def-pie-r1 | 0.863 | 0.826 |
| sim-B-A2-sburst-def-pie-r2 | 0.878 | 0.805 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.678 | 0.811 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.663 | 0.804 |
| sim-B-A4-hhier-def-codel-r1 | 0.571 | 0.667 |
| sim-B-A4-hhier-def-codel-r2 | 0.578 | 0.674 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.768 | 0.891 |
| sim-B-G1-sburst-n16-pfifo-r2 | 0.778 | 0.895 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.774 | 0.880 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.779 | 0.894 |
