
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
| sim-B-A2-sburst-def-pfifo-r1 | 1.859 | 1.229 | FAIL |
| sim-B-A2-sburst-def-pfifo-r2 | 2.021 | 1.173 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 2.153 | 1.609 | FAIL |
| sim-B-A2-sburst-def-codel-r2 | 1.997 | 1.203 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 2.011 | 0.938 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1.859 | 0.933 | FAIL |
| sim-B-A4-hhier-def-pfifo-r1 | 2.452 | 1.370 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 2.693 | 1.503 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 2.589 | 1.907 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 2.672 | 1.759 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 19.181 | 10.982 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 17.889 | 10.794 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 19.041 | 10.866 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 18.441 | 10.577 | FAIL |

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
| sim-B-A2-sburst-def-pfifo-r1 | 0.628 | 0.549 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 0.678 | 0.499 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.671 | 0.612 | ok |
| sim-B-A2-sburst-def-codel-r2 | 0.675 | 0.524 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.744 | 0.461 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.607 | 0.466 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.966 | 1.205 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 2.054 | 1.322 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 2.029 | 1.579 | ok |
| sim-B-A4-hhier-def-codel-r2 | 2.086 | 1.626 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 3.203 | 3.477 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 3.150 | 3.429 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 3.218 | 3.440 | ok |
| sim-B-G1-sburst-n24-pfifo-r2 | 3.185 | 3.359 | ok |

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
| sim-B-A2-sburst-def-pfifo-r1 | 0.657 | 0.591 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 0.686 | 0.593 | ok |
| sim-B-A2-sburst-def-codel-r1 | 0.711 | 0.597 | ok |
| sim-B-A2-sburst-def-codel-r2 | 0.685 | 0.599 | ok |
| sim-B-A2-sburst-def-pie-r1 | 0.856 | 0.569 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.672 | 0.594 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.473 | 0.807 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 1.513 | 0.903 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 1.469 | 0.885 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 1.602 | 1.002 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 2.935 | 1.874 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 2.782 | 1.772 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 2.883 | 1.795 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 2.793 | 1.733 | FAIL |

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
| sim-B-A2-sburst-def-pfifo-r1 | 112.700 | 111.000 | ok |
| sim-B-A2-sburst-def-pfifo-r2 | 95.600 | 113.500 | ok |
| sim-B-A2-sburst-def-codel-r1 | 173.500 | 141.000 | ok |
| sim-B-A2-sburst-def-codel-r2 | 163.900 | 133.500 | ok |
| sim-B-A2-sburst-def-pie-r1 | 172.800 | 138.500 | ok |
| sim-B-A2-sburst-def-pie-r2 | 157.700 | 133.000 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 165.200 | 133.000 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 178.200 | 141.500 | ok |
| sim-B-A4-hhier-def-codel-r1 | 207.300 | 155.000 | ok |
| sim-B-A4-hhier-def-codel-r2 | 217.700 | 169.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 129.200 | 154.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r2 | 144.700 | 150.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 130.200 | 170.000 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 145.100 | 141.000 | ok |

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
| sim-B-A2-sburst-def-pie-r1 | 0.935 | 0.847 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 0.837 | 0.847 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-pfifo-r2 | 1.000 | 1.000 | ok |
| sim-B-A4-hhier-def-codel-r1 | 0.997 | 0.994 | ok |
| sim-B-A4-hhier-def-codel-r2 | 1.000 | 0.982 | ok |
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
| sim-B-G1-sburst-n24-pfifo-r1 | 99.000 | 66.000 | ok |
| sim-B-G1-sburst-n24-pfifo-r2 | 132.000 | 99.000 | ok |

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
| sim-B-A2-sburst-def-pfifo-r1 | 99.000 | 42.900 | FAIL |
| sim-B-A2-sburst-def-pfifo-r2 | 151.800 | 141.900 | ok |
| sim-B-A2-sburst-def-codel-r1 | 231.000 | 95.700 | FAIL |
| sim-B-A2-sburst-def-codel-r2 | 141.900 | 174.900 | ok |
| sim-B-A2-sburst-def-pie-r1 | 118.800 | 85.800 | ok |
| sim-B-A2-sburst-def-pie-r2 | 141.900 | 141.900 | ok |
| sim-B-A4-hhier-def-pfifo-r1 | 99.000 | 151.800 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 151.800 | 66.000 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 132.000 | 85.800 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 118.800 | 99.000 | ok |
| sim-B-G1-sburst-n16-pfifo-r1 | 207.900 | 366.300 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 174.900 | 224.400 | ok |
| sim-B-G1-sburst-n24-pfifo-r1 | 293.700 | 402.600 | FAIL |
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
| sim-B-A2-sburst-def-pfifo-r1 | 506.929 | 1477.962 | FAIL |
| sim-B-A2-sburst-def-pfifo-r2 | 504.802 | 1285.370 | FAIL |
| sim-B-A2-sburst-def-codel-r1 | 1170.275 | 2215.258 | FAIL |
| sim-B-A2-sburst-def-codel-r2 | 1153.339 | 2185.012 | FAIL |
| sim-B-A2-sburst-def-pie-r1 | 1216.657 | 1735.691 | FAIL |
| sim-B-A2-sburst-def-pie-r2 | 1099.929 | 1768.795 | FAIL |
| sim-B-A4-hhier-def-pfifo-r1 | 505.818 | 1629.632 | FAIL |
| sim-B-A4-hhier-def-pfifo-r2 | 499.609 | 1596.561 | FAIL |
| sim-B-A4-hhier-def-codel-r1 | 1765.520 | 3672.980 | FAIL |
| sim-B-A4-hhier-def-codel-r2 | 1795.822 | 3689.483 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r1 | 432.298 | 1825.928 | FAIL |
| sim-B-G1-sburst-n16-pfifo-r2 | 384.721 | 1846.780 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r1 | 412.665 | 1915.725 | FAIL |
| sim-B-G1-sburst-n24-pfifo-r2 | 388.273 | 1913.201 | FAIL |

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
| sim-B-A2-sburst-def-pfifo-r1 | 235.950 | 66.000 |
| sim-B-A2-sburst-def-pfifo-r2 | 362.340 | 329.340 |
| sim-B-A2-sburst-def-codel-r1 | 340.560 | 247.170 |
| sim-B-A2-sburst-def-codel-r2 | 247.170 | 362.340 |
| sim-B-A2-sburst-def-pie-r1 | 712.800 | 241.560 |
| sim-B-A2-sburst-def-pie-r2 | 274.560 | 329.340 |
| sim-B-A4-hhier-def-pfifo-r1 | 413.160 | 339.900 |
| sim-B-A4-hhier-def-pfifo-r2 | 365.640 | 206.580 |
| sim-B-A4-hhier-def-codel-r1 | 437.580 | 339.900 |
| sim-B-A4-hhier-def-codel-r2 | 397.320 | 239.580 |
| sim-B-G1-sburst-n16-pfifo-r1 | 285.780 | 528.000 |
| sim-B-G1-sburst-n16-pfifo-r2 | 225.390 | 390.390 |
| sim-B-G1-sburst-n24-pfifo-r1 | 363.000 | 495.000 |
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
| sim-B-A2-sburst-def-pfifo-r1 | 206.700 | 183.500 |
| sim-B-A2-sburst-def-pfifo-r2 | 189.600 | 170.000 |
| sim-B-A2-sburst-def-codel-r1 | 251.800 | 207.400 |
| sim-B-A2-sburst-def-codel-r2 | 288.700 | 197.700 |
| sim-B-A2-sburst-def-pie-r1 | 223.000 | 184.000 |
| sim-B-A2-sburst-def-pie-r2 | 195.600 | 190.000 |
| sim-B-A4-hhier-def-pfifo-r1 | 258.200 | 189.500 |
| sim-B-A4-hhier-def-pfifo-r2 | 299.700 | 215.000 |
| sim-B-A4-hhier-def-codel-r1 | 287.300 | 201.400 |
| sim-B-A4-hhier-def-codel-r2 | 312.700 | 226.500 |
| sim-B-G1-sburst-n16-pfifo-r1 | 554.700 | 352.600 |
| sim-B-G1-sburst-n16-pfifo-r2 | 423.200 | 331.300 |
| sim-B-G1-sburst-n24-pfifo-r1 | 557.200 | 331.000 |
| sim-B-G1-sburst-n24-pfifo-r2 | 403.000 | 358.200 |

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
| sim-B-A2-sburst-def-pfifo-r1 | 0.910 | 0.931 |
| sim-B-A2-sburst-def-pfifo-r2 | 0.972 | 0.970 |
| sim-B-A2-sburst-def-codel-r1 | 0.942 | 0.908 |
| sim-B-A2-sburst-def-codel-r2 | 0.955 | 0.950 |
| sim-B-A2-sburst-def-pie-r1 | 0.985 | 0.883 |
| sim-B-A2-sburst-def-pie-r2 | 0.905 | 0.915 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.965 | 0.972 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.951 | 0.958 |
| sim-B-A4-hhier-def-codel-r1 | 0.983 | 0.944 |
| sim-B-A4-hhier-def-codel-r2 | 0.975 | 0.955 |
| sim-B-G1-sburst-n16-pfifo-r1 | 1.000 | 0.937 |
| sim-B-G1-sburst-n16-pfifo-r2 | 0.997 | 0.927 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.998 | 0.937 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.998 | 0.923 |

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
| sim-B-A2-sburst-def-pfifo-r2 | 0.972 | 0.889 |
| sim-B-A2-sburst-def-codel-r1 | 0.903 | 0.819 |
| sim-B-A2-sburst-def-codel-r2 | 0.875 | 0.792 |
| sim-B-A2-sburst-def-pie-r1 | 0.857 | 0.800 |
| sim-B-A2-sburst-def-pie-r2 | 0.779 | 0.765 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.976 | 0.917 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.979 | 0.893 |
| sim-B-A4-hhier-def-codel-r1 | 0.884 | 0.646 |
| sim-B-A4-hhier-def-codel-r2 | 0.917 | 0.620 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.997 | 0.830 |
| sim-B-G1-sburst-n16-pfifo-r2 | 1.000 | 0.844 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.991 | 0.854 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.991 | 0.859 |

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
| sim-B-A2-sburst-def-pfifo-r1 | 8.239 | 2.955 |
| sim-B-A2-sburst-def-pfifo-r2 | 8.328 | 2.747 |
| sim-B-A2-sburst-def-codel-r1 | 8.328 | 5.194 |
| sim-B-A2-sburst-def-codel-r2 | 8.765 | 5.102 |
| sim-B-A2-sburst-def-pie-r1 | 1.701 | 2.687 |
| sim-B-A2-sburst-def-pie-r2 | 1.657 | 2.311 |
| sim-B-A4-hhier-def-pfifo-r1 | 4.164 | 1.726 |
| sim-B-A4-hhier-def-pfifo-r2 | 5.295 | 1.744 |
| sim-B-A4-hhier-def-codel-r1 | 6.563 | 4.025 |
| sim-B-A4-hhier-def-codel-r2 | 6.306 | 3.710 |
| sim-B-G1-sburst-n16-pfifo-r1 | 3.336 | 0.750 |
| sim-B-G1-sburst-n16-pfifo-r2 | 3.227 | 0.883 |
| sim-B-G1-sburst-n24-pfifo-r1 | 3.157 | 0.657 |
| sim-B-G1-sburst-n24-pfifo-r2 | 3.249 | 0.749 |

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
| sim-B-A2-sburst-def-pfifo-r1 | 0.594 | 0.803 |
| sim-B-A2-sburst-def-pfifo-r2 | 0.614 | 0.807 |
| sim-B-A2-sburst-def-codel-r1 | 0.586 | 0.698 |
| sim-B-A2-sburst-def-codel-r2 | 0.598 | 0.718 |
| sim-B-A2-sburst-def-pie-r1 | 0.863 | 0.791 |
| sim-B-A2-sburst-def-pie-r2 | 0.878 | 0.812 |
| sim-B-A4-hhier-def-pfifo-r1 | 0.678 | 0.803 |
| sim-B-A4-hhier-def-pfifo-r2 | 0.663 | 0.799 |
| sim-B-A4-hhier-def-codel-r1 | 0.571 | 0.672 |
| sim-B-A4-hhier-def-codel-r2 | 0.578 | 0.683 |
| sim-B-G1-sburst-n16-pfifo-r1 | 0.768 | 0.880 |
| sim-B-G1-sburst-n16-pfifo-r2 | 0.778 | 0.882 |
| sim-B-G1-sburst-n24-pfifo-r1 | 0.774 | 0.877 |
| sim-B-G1-sburst-n24-pfifo-r2 | 0.779 | 0.881 |
