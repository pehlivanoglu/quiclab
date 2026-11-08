# Shadow v2: results

200 runs (campaigns 2026-11-05_det-base, 2026-11-05_det-split, 2026-11-05_det-access), all AQMs and both repetitions. Fitted on the calm pfifo-r1 runs only: G_ref v2 57.5, v2-fixed 71.7; v2-fixed scale F1 mu 3.819 sigma 5.86, F2 mu -0.05271 sigma 7.296, F3 mu -0.008933 sigma 0.05886, F4 mu 0.02837 sigma 0.07304, L mu 0.001082 sigma 0.01657. Operating point theta_on 0.25. git 7acb64c-dirty. Truth: git: fda8864-dirty.

## 1. Overall

| truth | detector | theta_on | episodes | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on |
|---|---|---|---|---|---|---|---|---|---|
| GT3 + path queue | v2 | 0.15 | 9696 | 0.89 | 0.81 | 1.08 | 200 | 464 | 0.11 |
| GT3 + path queue | v2 | 0.25 | 9696 | 0.95 | 0.80 | 0.43 | 249 | 556 | 0.06 |
| GT3 + path queue | v2 | 0.4 | 9696 | 0.98 | 0.79 | 0.21 | 324 | 699 | 0.04 |
| GT3 + path queue | v2-fixed | 0.15 | 9696 | 0.91 | 0.84 | 0.86 | 216 | 428 | 0.10 |
| GT3 + path queue | v2-fixed | 0.25 | 9696 | 0.97 | 0.84 | 0.33 | 283 | 569 | 0.06 |
| GT3 + path queue | v2-fixed | 0.4 | 9696 | 0.98 | 0.82 | 0.16 | 381 | 750 | 0.03 |
| GT1 (link) | v2 | 0.15 | 35498 | 0.87 | 0.33 | 0.71 | 225 | 608 | 0.15 |
| GT1 (link) | v2 | 0.25 | 35498 | 0.94 | 0.28 | 0.23 | 285 | 701 | 0.09 |
| GT1 (link) | v2 | 0.4 | 35498 | 0.96 | 0.25 | 0.15 | 366 | 814 | 0.07 |
| GT1 (link) | v2-fixed | 0.15 | 35498 | 0.91 | 0.35 | 0.50 | 241 | 578 | 0.18 |
| GT1 (link) | v2-fixed | 0.25 | 35498 | 0.95 | 0.30 | 0.20 | 319 | 694 | 0.12 |
| GT1 (link) | v2-fixed | 0.4 | 35498 | 0.97 | 0.26 | 0.12 | 416 | 830 | 0.08 |
| GT2 (link) | v2 | 0.15 | 64164 | 0.86 | 0.17 | 0.64 | 245 | 791 | 0.11 |
| GT2 (link) | v2 | 0.25 | 64164 | 0.94 | 0.15 | 0.20 | 306 | 896 | 0.06 |
| GT2 (link) | v2 | 0.4 | 64164 | 0.96 | 0.13 | 0.12 | 388 | 1013 | 0.04 |
| GT2 (link) | v2-fixed | 0.15 | 64164 | 0.89 | 0.16 | 0.48 | 264 | 851 | 0.10 |
| GT2 (link) | v2-fixed | 0.25 | 64164 | 0.95 | 0.15 | 0.18 | 345 | 960 | 0.06 |
| GT2 (link) | v2-fixed | 0.4 | 64164 | 0.97 | 0.13 | 0.11 | 440 | 1102 | 0.04 |

GT1 / GT2 are link-level truths charged to every client behind the queue (short keyframe queues included), so their recall is low for any detector; the client-level claim rests on GT3.

## 2. Freeze set vs held-out (GT3 + path queue, theta 0.5)

| set | runs | detector | episodes | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on |
|---|---|---|---|---|---|---|---|---|---|
| freeze set (pfifo-r1) | 25 | v2 | 1383 | 0.98 | 0.80 | 0.17 | 256 | 576 | 0.05 |
| freeze set (pfifo-r1) | 25 | v2-fixed | 1383 | 0.98 | 0.84 | 0.18 | 290 | 592 | 0.04 |
| held out: other AQMs r1 | 75 | v2 | 3472 | 0.94 | 0.80 | 0.51 | 246 | 587 | 0.07 |
| held out: other AQMs r1 | 75 | v2-fixed | 3472 | 0.96 | 0.83 | 0.34 | 279 | 591 | 0.06 |
| held out: every r2 | 100 | v2 | 4841 | 0.95 | 0.81 | 0.45 | 249 | 526 | 0.06 |
| held out: every r2 | 100 | v2-fixed | 4841 | 0.96 | 0.84 | 0.35 | 282 | 548 | 0.06 |

## 3. Per AQM (GT3 + path queue, theta 0.5)

| AQM | detector | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on | episodes |
|---|---|---|---|---|---|---|---|---|
| fq_codel | v2 | 0.83 | 0.76 | 1.02 | 224 | 780 | 0.09 | 1566 |
| fq_codel | v2-fixed | 0.89 | 0.75 | 0.63 | 248 | 938 | 0.08 | 1566 |
| pfifo | v2 | 0.98 | 0.79 | 0.16 | 255 | 541 | 0.05 | 2795 |
| pfifo | v2-fixed | 0.98 | 0.85 | 0.19 | 293 | 560 | 0.05 | 2795 |
| pie | v2 | 0.98 | 0.85 | 0.26 | 253 | 521 | 0.07 | 2573 |
| pie | v2-fixed | 0.98 | 0.86 | 0.21 | 282 | 526 | 0.05 | 2573 |
| red | v2 | 0.98 | 0.79 | 0.24 | 255 | 574 | 0.05 | 2762 |
| red | v2-fixed | 0.98 | 0.86 | 0.25 | 289 | 571 | 0.06 | 2762 |

## 3. Per topology (GT3 + path queue, theta 0.5)

| topology | detector | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | p90 (ms) | share alarmed before t_on | episodes |
|---|---|---|---|---|---|---|---|---|
| access | v2 | 0.92 | 0.91 | 0.26 | 166 | 334 | 0.09 | 214 |
| access | v2-fixed | 0.98 | 0.91 | 0.05 | 206 | 473 | 0.03 | 214 |
| base | v2 | 0.95 | 0.78 | 0.48 | 257 | 567 | 0.07 | 8115 |
| base | v2-fixed | 0.96 | 0.82 | 0.37 | 297 | 588 | 0.06 | 8115 |
| split | v2 | 0.97 | 0.91 | 0.29 | 224 | 504 | 0.03 | 1367 |
| split | v2-fixed | 0.97 | 0.92 | 0.22 | 231 | 487 | 0.02 | 1367 |

## 4. Per scenario (GT3 + path queue, theta 0.5; precision / recall / FA per min / latency p50 ms)

| topology | scenario | episodes | v2 | v2-fixed |
|---|---|---|---|---|
| access | isolate | 214 | 0.92 / 0.91 / 0.26 / 166 | 0.98 / 0.91 / 0.05 / 206 |
| base | burstcap | 551 | 0.98 / 0.95 / 0.23 / 240 | 0.99 / 0.95 / 0.16 / 271 |
| base | burstcapdeep | 535 | 0.98 / 0.96 / 0.24 / 257 | 0.99 / 0.97 / 0.17 / 286 |
| base | burstcaphighrtt | 524 | 0.98 / 0.98 / 0.26 / 304 | 0.98 / 0.98 / 0.22 / 322 |
| base | burstcaplowrtt | 562 | 0.97 / 0.91 / 0.36 / 191 | 0.99 / 0.91 / 0.17 / 235 |
| base | burstcapshallow | 564 | 0.99 / 0.96 / 0.18 / 208 | 1.00 / 0.92 / 0.00 / 393 |
| base | burstlong | 522 | 0.93 / 0.53 / 0.66 / 226 | 0.97 / 0.54 / 0.25 / 252 |
| base | bursttiny | 256 | 0.92 / 0.95 / 0.44 / 213 | 0.96 / 0.93 / 0.22 / 229 |
| base | burstudp | 484 | 0.97 / 0.97 / 0.40 / 227 | 0.99 / 0.96 / 0.12 / 252 |
| base | calm030 | 0 | 0.00 / - / 0.08 / - | - / - / 0.00 / - |
| base | calm065 | 25 | 0.44 / 0.16 / 0.35 / 211 | 0.67 / 0.24 / 0.21 / 215 |
| base | calm090 | 307 | 0.99 / 0.35 / 0.09 / 566 | 0.94 / 0.69 / 1.23 / 409 |
| base | calmcbr090 | 250 | 0.93 / 0.36 / 0.42 / 463 | 0.87 / 0.71 / 1.61 / 419 |
| base | capacity | 206 | 0.96 / 0.81 / 0.35 / 299 | 0.97 / 0.81 / 0.30 / 272 |
| base | cbr | 177 | 0.96 / 0.90 / 0.41 / 372 | 0.96 / 0.90 / 0.41 / 332 |
| base | delaystep | 27 | 0.06 / 0.19 / 2.62 / 526 | 0.02 / 0.07 / 2.85 / 569 |
| base | onoff | 466 | 0.99 / 0.84 / 0.33 / 338 | 0.98 / 0.80 / 0.53 / 301 |
| base | ppbp | 443 | 0.97 / 0.09 / 0.11 / 2727 | 0.99 / 0.58 / 0.32 / 383 |
| base | ramp | 672 | 0.91 / 0.66 / 1.15 / 307 | 0.97 / 0.62 / 0.36 / 323 |
| base | randloss | 10 | 0.25 / 0.30 / 0.22 / 338 | 0.25 / 0.40 / 0.29 / 447 |
| base | revdelay | 536 | 0.98 / 0.97 / 0.25 / 272 | 0.99 / 0.97 / 0.13 / 308 |
| base | tcpbbr | 469 | 0.95 / 0.88 / 0.55 / 223 | 0.97 / 0.87 / 0.29 / 245 |
| base | tcpcubic | 529 | 0.95 / 0.78 / 0.52 / 346 | 0.98 / 0.78 / 0.18 / 390 |
| split | splitcap | 871 | 0.97 / 0.90 / 0.29 / 225 | 0.98 / 0.90 / 0.16 / 241 |
| split | splitudp | 496 | 0.96 / 0.94 / 0.30 / 221 | 0.96 / 0.94 / 0.30 / 215 |

## 5. Recall by GT3 episode duration (theta 0.5)

| detector | < 0.5 s (n) | 0.5-1 s (n) | 1-2 s (n) | >= 2 s (n) |
|---|---|---|---|---|
| v2 | - (0) | 0.44 (1104) | 0.79 (2393) | 0.87 (6199) |
| v2-fixed | - (0) | 0.59 (1104) | 0.84 (2393) | 0.88 (6199) |
