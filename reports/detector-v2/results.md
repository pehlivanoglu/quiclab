# Shadow v2: results

200 runs (campaigns 2026-11-05_det-base, 2026-11-05_det-split, 2026-11-05_det-access), all AQMs and both repetitions. Fitted on the calm pfifo-r1 runs only: G_ref v2 52.8, v2-fixed 65.2; v2-fixed scale F1 mu 3.819 sigma 5.86, F2 mu -0.05271 sigma 7.296, F3 mu -0.008931 sigma 0.05885, F4 mu 0.631 sigma 0.6327, L mu 0.001082 sigma 0.01657. Operating point theta_on 0.25. git 7eb1419-dirty. Truth: git: fda8864-dirty.

## 1. Overall

| truth | detector | theta_on | episodes | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on |
|---|---|---|---|---|---|---|---|---|---|
| GT3 + path queue | v2 | 0.15 | 9696 | 0.88 | 0.88 | 1.31 | 204 | 528 | 0.12 |
| GT3 + path queue | v2 | 0.25 | 9696 | 0.95 | 0.86 | 0.46 | 253 | 657 | 0.07 |
| GT3 + path queue | v2 | 0.4 | 9696 | 0.98 | 0.83 | 0.20 | 324 | 798 | 0.04 |
| GT3 + path queue | v2-fixed | 0.15 | 9696 | 0.90 | 0.93 | 1.10 | 215 | 473 | 0.12 |
| GT3 + path queue | v2-fixed | 0.25 | 9696 | 0.96 | 0.91 | 0.38 | 277 | 626 | 0.07 |
| GT3 + path queue | v2-fixed | 0.4 | 9696 | 0.99 | 0.89 | 0.12 | 364 | 785 | 0.04 |
| GT1 (link) | v2 | 0.15 | 35498 | 0.85 | 0.39 | 0.92 | 233 | 722 | 0.18 |
| GT1 (link) | v2 | 0.25 | 35498 | 0.94 | 0.33 | 0.29 | 296 | 855 | 0.12 |
| GT1 (link) | v2 | 0.4 | 35498 | 0.96 | 0.29 | 0.15 | 375 | 949 | 0.09 |
| GT1 (link) | v2-fixed | 0.15 | 35498 | 0.90 | 0.45 | 0.67 | 240 | 644 | 0.23 |
| GT1 (link) | v2-fixed | 0.25 | 35498 | 0.95 | 0.38 | 0.25 | 311 | 781 | 0.17 |
| GT1 (link) | v2-fixed | 0.4 | 35498 | 0.97 | 0.33 | 0.14 | 401 | 920 | 0.13 |
| GT2 (link) | v2 | 0.15 | 64164 | 0.84 | 0.18 | 0.81 | 250 | 874 | 0.13 |
| GT2 (link) | v2 | 0.25 | 64164 | 0.94 | 0.15 | 0.24 | 311 | 1019 | 0.06 |
| GT2 (link) | v2 | 0.4 | 64164 | 0.97 | 0.14 | 0.11 | 390 | 1158 | 0.05 |
| GT2 (link) | v2-fixed | 0.15 | 64164 | 0.87 | 0.18 | 0.62 | 261 | 881 | 0.13 |
| GT2 (link) | v2-fixed | 0.25 | 64164 | 0.94 | 0.16 | 0.22 | 337 | 1070 | 0.07 |
| GT2 (link) | v2-fixed | 0.4 | 64164 | 0.97 | 0.15 | 0.10 | 425 | 1244 | 0.05 |

GT1 / GT2 are link-level truths charged to every client behind the queue (short keyframe queues included), so their recall is low for any detector; the client-level claim rests on GT3.

## 2. Freeze set vs held-out (GT3 + path queue, theta 0.5)

| set | runs | detector | episodes | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on |
|---|---|---|---|---|---|---|---|---|---|
| freeze set (pfifo-r1) | 25 | v2 | 1383 | 0.99 | 0.85 | 0.13 | 260 | 698 | 0.04 |
| freeze set (pfifo-r1) | 25 | v2-fixed | 1383 | 0.99 | 0.90 | 0.17 | 283 | 644 | 0.04 |
| held out: other AQMs r1 | 75 | v2 | 3472 | 0.94 | 0.86 | 0.56 | 249 | 689 | 0.08 |
| held out: other AQMs r1 | 75 | v2-fixed | 3472 | 0.96 | 0.92 | 0.45 | 271 | 659 | 0.08 |
| held out: every r2 | 100 | v2 | 4841 | 0.95 | 0.86 | 0.47 | 253 | 619 | 0.07 |
| held out: every r2 | 100 | v2-fixed | 4841 | 0.96 | 0.92 | 0.39 | 279 | 592 | 0.07 |

## 3. Per AQM (GT3 + path queue, theta 0.5)

| AQM | detector | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on | episodes |
|---|---|---|---|---|---|---|---|---|
| fq_codel | v2 | 0.82 | 0.86 | 1.21 | 224 | 836 | 0.12 | 1566 |
| fq_codel | v2-fixed | 0.88 | 0.89 | 0.82 | 247 | 921 | 0.12 | 1566 |
| pfifo | v2 | 0.99 | 0.84 | 0.13 | 262 | 651 | 0.05 | 2795 |
| pfifo | v2-fixed | 0.99 | 0.90 | 0.17 | 289 | 618 | 0.05 | 2795 |
| pie | v2 | 0.98 | 0.90 | 0.24 | 255 | 566 | 0.07 | 2573 |
| pie | v2-fixed | 0.98 | 0.93 | 0.25 | 272 | 548 | 0.07 | 2573 |
| red | v2 | 0.98 | 0.83 | 0.19 | 257 | 719 | 0.06 | 2762 |
| red | v2-fixed | 0.98 | 0.92 | 0.25 | 286 | 651 | 0.07 | 2762 |

## 3. Per topology (GT3 + path queue, theta 0.5)

| topology | detector | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on | episodes |
|---|---|---|---|---|---|---|---|---|
| access | v2 | 0.91 | 0.92 | 0.32 | 168 | 357 | 0.08 | 214 |
| access | v2-fixed | 0.97 | 0.91 | 0.10 | 201 | 466 | 0.03 | 214 |
| base | v2 | 0.95 | 0.85 | 0.51 | 261 | 690 | 0.07 | 8115 |
| base | v2-fixed | 0.96 | 0.91 | 0.44 | 293 | 658 | 0.08 | 8115 |
| split | v2 | 0.96 | 0.92 | 0.32 | 221 | 518 | 0.03 | 1367 |
| split | v2-fixed | 0.97 | 0.93 | 0.26 | 220 | 473 | 0.03 | 1367 |

## 4. Per scenario (GT3 + path queue, theta 0.5; precision / recall / FA per min / latency p50 ms)

| topology | scenario | episodes | v2 | v2-fixed |
|---|---|---|---|---|
| access | isolate | 214 | 0.91 / 0.92 / 0.32 / 168 | 0.97 / 0.91 / 0.10 / 201 |
| base | burstcap | 551 | 0.98 / 0.96 / 0.23 / 237 | 0.99 / 0.96 / 0.16 / 256 |
| base | burstcapdeep | 535 | 0.98 / 0.97 / 0.31 / 254 | 0.99 / 0.98 / 0.17 / 269 |
| base | burstcaphighrtt | 524 | 0.97 / 0.98 / 0.37 / 295 | 0.97 / 0.98 / 0.37 / 315 |
| base | burstcaplowrtt | 562 | 0.97 / 0.92 / 0.41 / 192 | 0.98 / 0.92 / 0.29 / 229 |
| base | burstcapshallow | 564 | 0.99 / 0.97 / 0.11 / 198 | 1.00 / 0.96 / 0.04 / 309 |
| base | burstlong | 522 | 0.94 / 0.85 / 0.85 / 333 | 0.97 / 0.85 / 0.44 / 306 |
| base | bursttiny | 256 | 0.94 / 0.95 / 0.33 / 202 | 0.95 / 0.95 / 0.29 / 216 |
| base | burstudp | 484 | 0.95 / 0.97 / 0.56 / 214 | 0.99 / 0.97 / 0.14 / 240 |
| base | calm030 | 0 | 0.00 / - / 0.08 / - | - / - / 0.00 / - |
| base | calm065 | 25 | 0.56 / 0.20 / 0.28 / 211 | 0.78 / 0.28 / 0.14 / 215 |
| base | calm090 | 307 | 0.98 / 0.35 / 0.18 / 507 | 0.92 / 0.78 / 1.94 / 383 |
| base | calmcbr090 | 250 | 0.91 / 0.40 / 0.60 / 469 | 0.83 / 0.68 / 2.03 / 401 |
| base | capacity | 206 | 0.95 / 0.86 / 0.45 / 299 | 0.96 / 0.87 / 0.40 / 272 |
| base | cbr | 177 | 0.97 / 0.94 / 0.35 / 379 | 0.93 / 0.92 / 0.70 / 335 |
| base | delaystep | 27 | 0.13 / 0.30 / 1.80 / 344 | 0.05 / 0.15 / 2.82 / 377 |
| base | onoff | 466 | 0.98 / 0.94 / 0.67 / 348 | 0.99 / 0.96 / 0.27 / 318 |
| base | ppbp | 443 | 0.98 / 0.10 / 0.11 / 2144 | 0.99 / 0.89 / 0.54 / 395 |
| base | ramp | 672 | 0.93 / 0.87 / 1.18 / 406 | 0.98 / 0.88 / 0.33 / 368 |
| base | randloss | 10 | 0.24 / 0.40 / 0.32 / 430 | 0.42 / 0.50 / 0.17 / 447 |
| base | revdelay | 536 | 0.98 / 0.97 / 0.22 / 273 | 0.99 / 0.97 / 0.09 / 297 |
| base | tcpbbr | 469 | 0.94 / 0.95 / 0.68 / 220 | 0.97 / 0.91 / 0.39 / 239 |
| base | tcpcubic | 529 | 0.94 / 0.91 / 0.72 / 344 | 0.98 / 0.90 / 0.31 / 389 |
| split | splitcap | 871 | 0.97 / 0.91 / 0.25 / 226 | 0.98 / 0.91 / 0.20 / 235 |
| split | splitudp | 496 | 0.95 / 0.94 / 0.41 / 213 | 0.95 / 0.96 / 0.35 / 205 |

## 5. Recall by GT3 episode duration (theta 0.5)

| detector | < 0.5 s (n) | 0.5-1 s (n) | 1-2 s (n) | >= 2 s (n) |
|---|---|---|---|---|
| v2 | - (0) | 0.49 (1104) | 0.82 (2393) | 0.94 (6199) |
| v2-fixed | - (0) | 0.66 (1104) | 0.88 (2393) | 0.97 (6199) |
