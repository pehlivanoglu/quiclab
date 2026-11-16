# Check 4 per traced egress: 2026-11-14_1730_v3-smoke

| run | hop | unmatched deq (ratio) | unmatched enq (ratio) | max per 200 ms deq / enq | gaps within 10 % | gap p99 | 20 ms windows within 5 % (n) | ok |
|---|---|---|---|---|---|---|---|---|
| v3-SMOKE-calm-access-pfifo-r1 | pub->router | 0 (0.000e+00) | 33 (3.628e-04) | 0 / 2 | 0.7468 | 1.649 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | ra->sub-a | 0 (0.000e+00) | 1 (1.294e-04) | 0 / 1 | 0.4776 | 1.003 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rb->sub-b | 1 (5.870e-05) | 0 (0.000e+00) | 1 / 0 | 0.9947 | 1.008 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rc->sub-c | 1 (5.906e-05) | 0 (0.000e+00) | 1 / 0 | 0.9735 | 1.008 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | rd->sub-d | 0 (0.000e+00) | 1 (3.089e-05) | 0 / 1 | 0.9979 | 1.008 | 1.0 (9) | ok |
| v3-SMOKE-calm-access-pfifo-r1 | router->sub-ctrl | 7 (4.131e-04) | 0 (0.000e+00) | 2 / 0 | 0.7917 | 1.013 | nan (0) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | router->switch | 19 (8.116e-05) | 3 (1.281e-05) | 2 / 1 | 0.9982 | 1.014 | 1.0 (205) | FAIL |
| v3-SMOKE-calm-access-pfifo-r1 | recursion_misses per tracer [158], unmatched total 66, cpu idle min 0.8878 | | | | | | | |
| v3-SMOKE-calm-rev-pfifo-r1 | pub->r0 | 0 (0.000e+00) | 16 (1.758e-04) | 0 / 2 | 0.8046 | 1.363 | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r0->sub-ctrl | 0 (0.000e+00) | 0 (0.000e+00) | 0 / 0 | 0.7933 | 1.008 | nan (0) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r0->r1 | 11 (1.486e-04) | 2 (2.701e-05) | 2 / 1 | 0.9983 | 1.023 | 1.0 (1) | FAIL |
| v3-SMOKE-calm-rev-pfifo-r1 | r1->switch | 3 (1.281e-05) | 3 (1.281e-05) | 1 / 1 | 0.9995 | 1.011 | 1.0 (214) | ok |
| v3-SMOKE-calm-rev-pfifo-r1 | recursion_misses per tracer [90], unmatched total 35, cpu idle min 0.9414 | | | | | | | |
| v3-SMOKE-calm-s030u070-pfifo-r1 | pub->router | 0 (0.000e+00) | 7 (7.681e-05) | 0 / 1 | 0.8747 | 1.274 | nan (0) | FAIL |
| v3-SMOKE-calm-s030u070-pfifo-r1 | router->sub-ctrl | 3 (1.759e-04) | 0 (0.000e+00) | 1 / 0 | 0.8741 | 1.006 | nan (0) | FAIL |
| v3-SMOKE-calm-s030u070-pfifo-r1 | router->switch | 1 (4.271e-06) | 1 (4.271e-06) | 1 / 1 | 0.9997 | 1.009 | 1.0 (208) | ok |
| v3-SMOKE-calm-s030u070-pfifo-r1 | recursion_misses per tracer [38], unmatched total 12, cpu idle min 0.9473 | | | | | | | |
| v3-SMOKE-calm-split4-pfifo-r1 | pub->r1 | 0 (0.000e+00) | 20 (1.367e-04) | 0 / 2 | 0.7983 | 1.483 | nan (0) | FAIL |
| v3-SMOKE-calm-split4-pfifo-r1 | r1->sub-ctrl | 0 (0.000e+00) | 1 (5.896e-05) | 0 / 1 | 0.8372 | 1.009 | nan (0) | FAIL |
| v3-SMOKE-calm-split4-pfifo-r1 | r1->r2 | 11 (2.715e-05) | 13 (3.208e-05) | 2 / 1 | 0.9975 | 1.023 | 1.0 (193) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | r2->switch-a | 3 (1.477e-05) | 7 (3.446e-05) | 1 / 1 | 0.9993 | 1.011 | 1.0 (208) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | r2->switch-b | 2 (9.852e-06) | 7 (3.448e-05) | 1 / 1 | 0.9992 | 1.011 | 1.0 (201) | ok |
| v3-SMOKE-calm-split4-pfifo-r1 | recursion_misses per tracer [223], unmatched total 64, cpu idle min 0.9157 | | | | | | | |
| v3-SMOKE-calm-tree16-pfifo-r1 | pub->rr | 0 (0.000e+00) | 51 (3.102e-04) | 0 / 3 | 0.5767 | 2.477 | nan (0) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | r0->r1 | 10 (4.553e-05) | 17 (7.740e-05) | 1 / 2 | 0.9966 | 1.025 | 1.0 (204) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | r0->r2 | 3 (1.367e-05) | 23 (1.048e-04) | 1 / 2 | 0.9965 | 1.025 | 1.0 (209) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | r1->switch-a | 4 (3.651e-05) | 2 (1.826e-05) | 1 / 1 | 0.9981 | 1.011 | 1.0 (158) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r1->switch-b | 0 (0.000e+00) | 3 (2.745e-05) | 0 / 1 | 0.9983 | 1.011 | 1.0 (172) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r2->switch-c | 4 (3.641e-05) | 4 (3.641e-05) | 1 / 1 | 0.9982 | 1.012 | 1.0 (190) | ok |
| v3-SMOKE-calm-tree16-pfifo-r1 | r2->switch-d | 4 (3.663e-05) | 6 (5.494e-05) | 1 / 1 | 0.9983 | 1.011 | 1.0 (175) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | rr->sub-ctrl | 2 (1.181e-04) | 2 (1.181e-04) | 1 / 1 | 0.7587 | 1.012 | nan (0) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | rr->r0 | 23 (5.253e-05) | 32 (7.309e-05) | 2 / 2 | 0.9900 | 1.056 | 1.0 (195) | FAIL |
| v3-SMOKE-calm-tree16-pfifo-r1 | recursion_misses per tracer [667], unmatched total 190, cpu idle min 0.8025 | | | | | | | |
| v3-SMOKE-calm-uneven-pfifo-r1 | pub->r1 | 0 (0.000e+00) | 65 (2.584e-04) | 0 / 3 | 0.6930 | 1.928 | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r1->sub-ctrl | 8 (4.708e-04) | 3 (1.766e-04) | 2 / 1 | 0.9260 | 1.011 | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r1->r2 | 25 (1.066e-04) | 23 (9.806e-05) | 2 / 4 | 0.5843 | 2.045 | nan (0) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-a | 4 (2.521e-05) | 8 (5.041e-05) | 1 / 1 | 0.9994 | 1.013 | 1.0 (208) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-b | 10 (4.645e-05) | 11 (5.110e-05) | 2 / 2 | 0.9986 | 1.019 | 1.0 (210) | FAIL |
| v3-SMOKE-calm-uneven-pfifo-r1 | r2->switch-c | 12 (3.377e-05) | 9 (2.533e-05) | 1 / 1 | 0.9973 | 1.029 | 1.0 (200) | ok |
| v3-SMOKE-calm-uneven-pfifo-r1 | recursion_misses per tracer [599], unmatched total 178, cpu idle min 0.8866 | | | | | | | |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | pub->router | 0 (0.000e+00) | 19 (1.398e-04) | 0 / 1 | 0.8637 | 1.272 | nan (0) | FAIL |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | router->sub-ctrl | 2 (7.859e-05) | 0 (0.000e+00) | 1 / 0 | 0.9304 | 1.007 | nan (0) | FAIL |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | router->switch | 6 (1.671e-05) | 4 (1.114e-05) | 1 / 1 | 0.9995 | 1.009 | 1.0 (527) | ok |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | recursion_misses per tracer [102], unmatched total 31, cpu idle min 0.9454 | | | | | | | |
