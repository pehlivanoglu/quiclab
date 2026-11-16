# T-HAYES check 4b: tracer timestamp noise or link service jitter? (smoke 1, offline)

Lag-1 correlation of consecutive gap errors inside busy chains: about -0.5 = independent timestamp noise (a late stamp lengthens one gap and shortens the next); HTB catch-up after a late release is also negative, so the sign does not separate the two. 'pair sum' = e_i + e_(i+1), us.

| run | traced routers | CPU idle min | egress (role) | busy gaps | within max(10 %, 15 us) | error p1 / p99 us | lag-1 corr | pair-sum p1 / p99 us |
|---|---|---|---|---|---|---|---|---|
| hayes | 12 | 0.5728 | r0->l12 | 40308 | 0.942 | -43.6 / 37.1 | -0.45 | -42.3 / 35.7 |
| hayes | 12 | 0.5728 | r0->l34 | 18158 | 0.9665 | -46.3 / 40.9 | -0.37 | -48.4 / 36.4 |
| hayes | 12 | 0.5728 | r1->l13 | 24822 | 0.9717 | -33.7 / 30.9 | -0.42 | -33.0 / 30.0 |
| hayes | 12 | 0.5728 | r1->l24 | 23999 | 0.9714 | -33.3 / 31.3 | -0.37 | -32.5 / 29.6 |
| hayes | 12 | 0.5728 | r2->l14 | 18619 | 0.9752 | -39.0 / 23.8 | -0.31 | -27.4 / 23.3 |
| hayes | 12 | 0.5728 | r2->l23 | 19636 | 0.9764 | -34.5 / 23.1 | -0.39 | -26.3 / 21.7 |
| hayes | 12 | 0.5728 | r3->r4 | 40122 | 0.9627 | -49.1 / 17.7 | -0.37 | -21.0 / 16.3 |
| split4l | 3 | 0.8978 | r1->r2 | 97926 | 0.9993 | -2.4 / 2.3 | -0.38 | -2.3 / 2.3 |
| split4l | 3 | 0.8978 | r2->switch-a | 39903 | 0.9995 | -2.5 / 2.5 | -0.34 | -2.5 / 2.6 |
| split4l | 3 | 0.8978 | r2->switch-b | 38556 | 0.9995 | -2.5 / 2.5 | -0.37 | -2.6 / 2.6 |
| par-k6 | 3 | 0.8555 | r2->switch-a | 45263 | 0.9991 | -6.5 / 5.6 | -0.38 | -6.9 / 4.9 |
| par-k6 | 3 | 0.8555 | r2->switch-b | 45958 | 0.9988 | -6.8 / 5.6 | -0.37 | -7.1 / 5.1 |
| par-k6 | 3 | 0.8555 | r2->switch-c | 45818 | 0.9991 | -6.7 / 5.7 | -0.40 | -6.9 / 5.2 |
| par-k6 | 3 | 0.8555 | r2->switch-d | 45755 | 0.9988 | -7.1 / 5.9 | -0.29 | -7.5 / 5.3 |
| par-k6 | 3 | 0.8555 | r2->switch-e | 45655 | 0.9989 | -7.0 / 5.9 | -0.27 | -7.3 / 5.2 |
| par-k6 | 3 | 0.8555 | r2->switch-f | 45707 | 0.9988 | -7.1 / 5.7 | -0.37 | -7.5 / 4.8 |
| base-n16 | 2 | 0.9413 | router->switch | 112573 | 0.9995 | -1.8 / 1.8 | -0.27 | -1.9 / 1.9 |
| teacup | 3 | 0.8369 | r1->r2 | 117201 | 0.9995 | -2.4 / 2.5 | -0.29 | -2.5 / 2.5 |
| teacup | 3 | 0.8369 | r2->switch-a | 69858 | 0.9998 | -2.7 / 2.8 | -0.42 | -2.8 / 2.9 |
| teacup | 3 | 0.8369 | r2->switch-b | 70013 | 0.9998 | -2.6 / 2.7 | -0.31 | -2.7 / 2.8 |
