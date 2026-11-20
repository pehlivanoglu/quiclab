| plan | non-bottleneck directions | worst peak / rate today (hop, peak, rate) | over 1 today | worst after (100 Gb/s) | bottleneck directions | bottleneck peak / capacity max |
|---|---|---|---|---|---|---|
| n100-L10 | 124 | 0.59 (tx-up->r1, 592 / 1000) | 0:  | 0.006 | 11 | 2.24 |
| n100-L50 | 108 | 0.59 (tx-up->r1, 592 / 1000) | 0:  | 0.006 | 3 | 2.50 |
| n100-L100 | 106 | 0.59 (tx-l01->r2, 592 / 1000) | 0:  | 0.006 | 2 | 1.70 |
| n100-uneven | 118 | 0.59 (tx-up->r1, 588 / 1000) | 0:  | 0.006 | 8 | 2.50 |
| n300-L10 | 364 | 1.78 (r2->rx-up, 1777 / 1000) | 2: r2->rx-up, tx-up->r1 | 0.018 | 31 | 2.50 |
| n300-L50 | 316 | 1.78 (r2->rx-up, 1777 / 1000) | 2: r2->rx-up, tx-up->r1 | 0.018 | 7 | 1.70 |
| n300-L100 | 310 | 1.78 (r2->rx-up, 1777 / 1000) | 2: r2->rx-up, tx-up->r1 | 0.018 | 4 | 2.25 |
| n300-uneven | 320 | 1.77 (r2->rx-up, 1773 / 1000) | 4: r2->rx-up, tx-l08->r2, tx-up->r1, switch-l08->rx-l08 | 0.018 | 9 | 2.35 |
| n1000-L10 | 1204 | 5.92 (r2->rx-up, 5922 / 1000) | 3: pub->r1, r2->rx-up, tx-up->r1 | 0.059 | 101 | 2.50 |
| n1000-L50 | 1044 | 5.92 (r2->rx-up, 5922 / 1000) | 3: r2->rx-up, pub->r1, tx-up->r1 | 0.059 | 21 | 2.50 |
| n1000-L100 | 1024 | 5.92 (r2->rx-up, 5922 / 1000) | 7: r2->rx-up, switch-l06->rx-l06, pub->r1, tx-l02->r2 ... | 0.059 | 11 | 2.50 |
| n1000-uneven | 1042 | 5.91 (r2->rx-up, 5915 / 1000) | 9: r2->rx-up, tx-l18->r2, switch-l18->rx-l18, pub->r1 ... | 0.059 | 20 | 2.50 |
| plan-n300 | 304 | 1.18 (tx-main->router, 1184 / 1000) | 2: tx-main->router, switch->rx-main | 0.012 | 1 | 1.70 |
