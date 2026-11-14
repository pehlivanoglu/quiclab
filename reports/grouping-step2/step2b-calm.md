# Step 2b C: short shared queues in calm runs (no detector)

Queue peak = contiguous time with the egress queue delay >= 5 ms (router-metrics; 5 ms CSV on split / tree8 / uneven, 25 ms on base). Each peak's interval (+/- 0.5 s) goes through the step 2 procedure (penalty x1). Placement right: the clients behind the peaking egress share one data class (together) and no other client is in it (apart).

| type | egress | peaks | per min (this egress) | peak ms p10 / p50 / p90 | duration ms p10 / p50 / p90 | together | together and apart | behind clients left in class 0 | with another egress peaking |
|---|---|---|---|---|---|---|---|---|---|
| calm065 | router->switch | 2254 | 392.0 | 5.8 / 9.3 / 23.9 | 0 / 0 / 50 | 0.78 | 0.78 | 0.11 | 0.00 |
| calmsplit | r1->r2 | 2681 | 466.3 | 5.2 / 6.5 / 18.7 | 0 / 0 / 40 | 0.07 | 0.07 | 0.36 | 1.00 |
| calmsplit | r2->switch-a | 5485 | 953.9 | 5.3 / 6.4 / 11.3 | 0 / 0 / 20 | 0.08 | 0.00 | 0.37 | 1.00 |
| calmsplit | r2->switch-b | 5499 | 956.3 | 5.3 / 6.3 / 11.6 | 0 / 0 / 20 | 0.09 | 0.00 | 0.37 | 1.00 |
| calmtree8 | r0->r1 | 2183 | 379.7 | 5.1 / 6.3 / 12.4 | 0 / 0 / 30 | 0.39 | 0.02 | 0.38 | 1.00 |
| calmtree8 | r0->r2 | 1919 | 333.7 | 5.1 / 6.5 / 14.0 | 0 / 0 / 35 | 0.66 | 0.06 | 0.22 | 1.00 |
| calmtree8 | r1->switch-a | 4387 | 763.0 | 5.1 / 6.9 / 12.8 | 0 / 5 / 30 | 0.47 | 0.02 | 0.42 | 1.00 |
| calmtree8 | r1->switch-b | 3281 | 570.6 | 5.1 / 6.7 / 14.8 | 0 / 0 / 40 | 0.60 | 0.04 | 0.34 | 1.00 |
| calmtree8 | r2->switch-c | 3842 | 668.2 | 5.1 / 6.0 / 13.2 | 0 / 0 / 35 | 0.71 | 0.03 | 0.26 | 1.00 |
| calmtree8 | r2->switch-d | 2224 | 386.8 | 5.1 / 6.3 / 20.2 | 0 / 0 / 65 | 0.74 | 0.08 | 0.24 | 1.00 |
| calmtree8 | rr->r0 | 9480 | 1648.7 | 5.9 / 15.2 / 20.0 | 0 / 10 / 15 | 0.32 | 0.32 | 0.33 | 1.00 |
| calmuneven | r1->r2 | 29 | 7.6 | 5.1 / 5.6 / 7.8 | 0 / 0 / 11 | 0.00 | 0.00 | 0.43 | 1.00 |
| calmuneven | r2->switch-a | 4748 | 825.7 | 5.4 / 6.9 / 14.3 | 0 / 0 / 25 | 0.27 | 0.04 | 0.54 | 1.00 |
| calmuneven | r2->switch-b | 5369 | 933.7 | 5.2 / 6.7 / 13.4 | 0 / 0 / 20 | 0.13 | 0.04 | 0.59 | 1.00 |
| calmuneven | r2->switch-c | 5213 | 906.6 | 5.2 / 6.4 / 11.0 | 0 / 0 / 15 | 0.39 | 0.10 | 0.35 | 1.00 |

Placement by peak size (all calm types, peaks with >= 2 observable clients behind the egress):

| peak ms | peaks | together | together and apart | behind clients in class 0 |
|---|---|---|---|---|
| 5-10 | 43229 | 0.33 | 0.06 | 0.40 |
| 10-20 | 11661 | 0.39 | 0.26 | 0.29 |
| 20-50 | 3577 | 0.43 | 0.22 | 0.28 |
| >= 50 | 127 | 0.61 | 0.38 | 0.21 |
