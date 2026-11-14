# Step 1b: scale-free numbers, residual sigma, noise on the curves, template size

91 runs. Rows per noise variant: clean 10090, iid5 10090, iid10 10090, iid20 10090, rw5 10090, rw10 10090, rw20 10090.

## A. Explained fraction 1 - sum (q - s)^2 / sum q^2 (clean)

| class | n | p10 / p50 / p90 |
|---|---|---|
| SAME | 9341 | 0.973 / 0.996 / 0.999 |
| CONCURRENT own | 198 | 0.992 / 0.996 / 0.998 |
| CONCURRENT other | 198 | 0.592 / 0.853 / 0.959 |
| NESTED K1 a+up | 81 | 0.775 / 0.957 / 0.986 |
| NESTED M6 (independent branches) | 458 | -0.059 / 0.350 / 0.954 |

## A. CONCURRENT residual ratio RMS(q - s_other) / RMS(q - s_own) (clean)

| cell | n | p10 / p50 / p90 | < 1.2 | < 1.5 | own preferred (ratio > 1) |
|---|---|---|---|---|---|
| all | 198 | 2.67 / 5.71 / 10.13 | 0.00 | 0.00 | 1.00 |
| K1 a+b pfifo | 54 | 4.64 / 7.36 / 11.05 | 0.00 | 0.00 | 1.00 |
| K1 a+b pie | 54 | 3.25 / 4.61 / 8.52 | 0.00 | 0.00 | 1.00 |
| K1 a+b red | 54 | 2.10 / 3.61 / 6.18 | 0.00 | 0.00 | 1.00 |
| K6 A+C pfifo | 36 | 3.97 / 6.65 / 9.74 | 0.00 | 0.00 | 1.00 |

## B. CONCURRENT E(own) - E(other) with the residual sigma vs the calm sigma (clean)

| sigma | n | p10 / p50 / p90 nats | > 11.5 | < 2 |
|---|---|---|---|---|
| residual (M) | 193 | 1186.3 / 4668.8 / 17174.4 | 1.00 | 0.00 |
| calm (step 1) | 198 | 9796.8 / 55350.6 / 1962744.3 | 1.00 | 0.00 |

sigma ms p10 / p50 / p90: residual 3.87 / 5.77 / 10.40, calm 0.27 / 1.49 / 3.71

## C. Noise on the curves (templates rebuilt from noisy curves)

| noise | SAME EF p50 | CONCURRENT own preferred | ratio p10 / p50 / p90 | ratio < 1.2 | diff_res p50, > 11.5, < 2 | NESTED K1 EF p50 |
|---|---|---|---|---|---|---|
| clean | 0.996 | 1.00 | 2.67 / 5.71 / 10.13 | 0.00 | 4668.8, 1.00, 0.00 | 0.957 |
| iid5 | 0.977 | 1.00 | 1.60 / 2.80 / 5.01 | 0.00 | 2455.4, 0.99, 0.01 | 0.922 |
| iid10 | 0.928 | 0.99 | 1.23 / 1.81 / 3.01 | 0.09 | 887.6, 0.98, 0.01 | 0.869 |
| iid20 | 0.759 | 0.90 | 1.00 / 1.23 / 1.79 | 0.43 | 151.1, 0.87, 0.11 | 0.757 |
| rw5 | 0.979 | 0.99 | 1.66 / 2.86 / 5.60 | 0.02 | 15.4, 0.51, 0.48 | 0.927 |
| rw10 | 0.934 | 0.93 | 1.09 / 1.94 / 3.58 | 0.13 | -7.7, 0.39, 0.55 | 0.861 |
| rw20 | 0.781 | 0.78 | 0.88 / 1.29 / 2.36 | 0.42 | 2.8, 0.34, 0.50 | 0.743 |

## D. Template size (CONCURRENT, clean; own and other templates from k random clients)

| k | n | ratio p10 / p50 / p90 | own preferred | < 1.2 |
|---|---|---|---|---|
| 1 | 189 | 2.56 / 5.36 / 9.15 | 1.00 | 0.00 |
| 2 | 162 | 2.61 / 5.26 / 9.93 | 0.99 | 0.01 |
| 3 | 0 | - | - | - |

## E. The two branches' templates (clean, full templates, per event)

- best lag between the branch templates ms p10/p50/p90 -120 / 0 / 120; correlation at it 0.77 / 0.91 / 0.98; RMS difference ms 11.3 / 23.4 / 44.5; 72 event sides
