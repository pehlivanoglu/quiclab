testbed: `.runs/2026-11-16_0105_v4-K2/v4-N6-hhier-bgbursty-pfifo-r1`

simulation: `simulation/runs/ppbp/sim-X-N6-hhier-bgbursty-pfifo-r1`

| source | mean_mbps cfg | hurst cfg | bursts tb / sim | burst list identical | burst s p50/p90/p99 tb | burst s p50/p90/p99 sim | KS burst length | rate Mb/s tb / sim | rate diff % | Hurst tb / sim | 100 ms bins tb / sim |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bg-up | 23.22 | 0.8 | 22397 / 22397 | yes | 0.23/0.74/3.46 | 0.23/0.74/3.46 | 0.0 | 20.529 / 20.529 | 0.0 | 0.827 / 0.817 | 9662 / 9690 |
| bg-a | 11.611 | 0.8 | 11477 / 11477 | yes | 0.23/0.72/3.92 | 0.23/0.72/3.92 | 0.0 | 10.949 / 10.949 | 0.0 | 0.843 / 0.837 | 9661 / 9690 |
| bg-b | 11.611 | 0.8 | 11160 / 11160 | yes | 0.24/0.77/4.29 | 0.24/0.77/4.29 | 0.0 | 11.598 / 11.598 | 0.0 | 0.880 / 0.880 | 9661 / 9690 |
