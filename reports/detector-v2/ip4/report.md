# Shadow v2 report

192 runs, campaigns 2026-11-08_det-base, 2026-11-08_det-access, 2026-11-08_det-split; git 61a24d9-dirty.

## Fitted values (frozen rules, re-derived on these campaigns)

- RTT: floors F1 0.3171, F2 0.3979, F3 0.004303, F4 0.004136; G_ref v2 67.2, v2-fixed 75.5; v2-fixed scale F1 mu 3.277 sigma 3.771, F2 mu -0.0205 sigma 4.312, F3 mu -0.008994 sigma 0.04832, F4 mu 0.01814 sigma 0.05036, L mu 0.0001618 sigma 0.005913
- OWD: floors F1 0.2731, F2 0.3682, F3 0.004279, F4 0.004138; G_ref v2 67.7, v2-fixed 77.9; v2-fixed scale F1 mu 1.503 sigma 3.181, F2 mu -0.06983 sigma 4.119, F3 mu -0.008922 sigma 0.04725, F4 mu 0.01795 sigma 0.05028, L mu 0.000162 sigma 0.005916

## Overall (all runs pooled)

| truth | detector | episodes | precision | recall | FA / min | latency p50 (ms) | p90 (ms) |
|---|---|---|---|---|---|---|---|
| GT1 | v2 | 26543 | 0.98 | 0.36 | 0.09 | 256 | 630 |
| GT1 | v2-fixed | 26543 | 0.98 | 0.38 | 0.07 | 265 | 593 |
| GT1 | bbr | 26543 | 0.83 | 0.33 | 0.72 | 736 | 1815 |
| GT1 | gcc | 26543 | 0.96 | 0.33 | 0.13 | 929 | 1302 |
| GT2 | v2 | 20903 | 0.97 | 0.42 | 0.09 | 250 | 744 |
| GT2 | v2-fixed | 20903 | 0.98 | 0.43 | 0.06 | 259 | 809 |
| GT2 | bbr | 20903 | 0.80 | 0.37 | 0.68 | 756 | 2169 |
| GT2 | gcc | 20903 | 0.96 | 0.36 | 0.09 | 933 | 1450 |
| GT3 | v2 | 9374 | 0.97 | 0.82 | 0.27 | 231 | 448 |
| GT3 | v2-fixed | 9374 | 0.97 | 0.84 | 0.28 | 240 | 429 |
| GT3 | bbr | 9374 | 0.87 | 0.74 | 1.15 | 723 | 1897 |
| GT3 | gcc | 9374 | 0.99 | 0.80 | 0.06 | 904 | 1227 |
| GT3 (B) owd-cmp | v2 RTT | 17055 | 0.99 | 0.69 | 0.07 | 255 | 630 |
| GT3 (B) owd-cmp | v2 OWD | 17055 | 0.99 | 0.69 | 0.04 | 257 | 632 |
| GT3 (B) owd-cmp | v2-fixed RTT | 17055 | 0.99 | 0.71 | 0.05 | 261 | 613 |
| GT3 (B) owd-cmp | v2-fixed OWD | 17055 | 0.99 | 0.71 | 0.04 | 266 | 607 |
| GT3 (B) owd-cmp | gcc RTT | 17055 | 0.99 | 0.69 | 0.04 | 960 | 1552 |
| GT3 (B) owd-cmp | gcc OWD | 17055 | 0.99 | 0.68 | 0.04 | 971 | 1617 |
