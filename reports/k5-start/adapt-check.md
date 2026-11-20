# K5 gate adaptation check

Run: .runs/2026-11-19_2213_v4-K5/v4-GATE-sburst-adapt-bbr-b1000-on-pfifo-r1 (finished: yes)

| file | rows | rows scale < 1 | share | lowest scale | floor reached (scale <= 0.3) |
|---|---|---|---|---|---|
| publishers/pub/sub-a-adapt.csv | 6731 | 532 | 0.079 | 0.300 | yes |
| publishers/pub/sub-b-adapt.csv | 6732 | 1161 | 0.172 | 0.300 | yes |
| publishers/pub/sub-c-adapt.csv | 6733 | 1377 | 0.205 | 0.300 | yes |
| publishers/pub/sub-ctrl-adapt.csv | 6733 | 79 | 0.012 | 0.300 | yes |
| publishers/pub/sub-d-adapt.csv | 6733 | 1918 | 0.285 | 0.300 | yes |

Verdict: adaptation engaged (scale < 1 in every adapt file).
