# Shadow v2, Step 5: hold, rebase, episodes

200 runs, theta_on 0.25, theta_off 0.125. G_ref (calm pfifo-r1): v2 52.8, v2 +hold 57.5, v2 +hold +rebase 57.5, v2-fixed 65.2, v2-fixed +hold 71.7, v2-fixed +hold +rebase 71.7. git 7eb1419-dirty.

## 1. Overall, all 200 runs (GT3 + path queue)

recall = an alarm STARTS in [t_on - 1 s, min(end, t_on + 10 s)] (gt_score rule); recall (alarm on) = the alarm is ON at some point of that window, whether it started there or earlier. With the hold rule one alarm spans several GT3 episodes of one long event, which the first rule counts as misses.

| variant | precision | recall | recall (alarm on) | FA / min CLEAR | latency p50 (ms) | p90 (ms) |
|---|---|---|---|---|---|---|
| v2 | 0.95 | 0.86 | 0.89 | 0.46 | 253 | 657 |
| v2 +hold | 0.95 | 0.81 | 0.91 | 0.46 | 249 | 558 |
| v2 +hold +rebase | 0.95 | 0.81 | 0.91 | 0.42 | 249 | 562 |
| v2-fixed | 0.96 | 0.91 | 0.96 | 0.38 | 277 | 626 |
| v2-fixed +hold | 0.97 | 0.84 | 0.97 | 0.32 | 280 | 562 |
| v2-fixed +hold +rebase | 0.97 | 0.84 | 0.97 | 0.26 | 280 | 563 |

## 2. burstlong: coverage and alarm starts per episode-minute (pass: >= 0.9 and <= 3)

| variant | recall | recall (alarm on) | coverage | starts per episode-minute | verdict |
|---|---|---|---|---|---|
| v2 | 0.85 | 0.98 | 0.72 | 10.2 | FAIL |
| v2 +hold | 0.53 | 1.00 | 0.99 | 1.8 | PASS |
| v2 +hold +rebase | 0.53 | 0.99 | 0.98 | 1.9 | PASS |
| v2-fixed | 0.85 | 1.00 | 0.89 | 10.4 | FAIL |
| v2-fixed +hold | 0.53 | 1.00 | 0.99 | 1.9 | PASS |
| v2-fixed +hold +rebase | 0.53 | 0.99 | 0.98 | 1.9 | PASS |

## 3. Rebase: firings, firings inside a GT3 episode (erases real congestion), delaystep FA / min without -> with

| variant | rebases | inside a GT3 episode | top scenarios | delaystep FA / min (hold -> hold + rebase) |
|---|---|---|---|---|
| v2 +hold +rebase | 172 | 11 | delaystep 161 (0 in ep.), tcpbbr 4 (4 in ep.), ppbp 3 (3 in ep.), burstlong 2 (2 in ep.), tcpcubic 2 (2 in ep.) | 2.72 -> 1.63 |
| v2-fixed +hold +rebase | 60 | 13 | delaystep 47 (0 in ep.), tcpbbr 6 (6 in ep.), tcpcubic 6 (6 in ep.), burstlong 1 (1 in ep.) | 2.85 -> 0.95 |

## 4. Onset spread across the clients of one injected event (ms)

| variant | scenario | events with >= 2 clients alarming | arrival spread p50 | p90 | t_onset spread p50 | p90 | t_onset - event start p10 | p50 | p90 |
|---|---|---|---|---|---|---|---|---|---|
| v2 | burstcap | 144 | 132 | 759 | 99 | 749 | 56 | 130 | 536 |
| v2 | splitcap | 240 | 99 | 759 | 99 | 759 | 68 | 125 | 328 |
| v2 | bursttiny | 130 | 99 | 264 | 66 | 231 | 48 | 111 | 183 |
| v2 +hold | burstcap | 144 | 165 | 749 | 99 | 693 | 54 | 122 | 338 |
| v2 +hold | splitcap | 240 | 132 | 759 | 99 | 729 | 52 | 118 | 295 |
| v2 +hold | bursttiny | 130 | 99 | 264 | 66 | 264 | 38 | 107 | 169 |
| v2 +hold +rebase | burstcap | 144 | 165 | 749 | 99 | 693 | 54 | 122 | 338 |
| v2 +hold +rebase | splitcap | 240 | 132 | 759 | 99 | 729 | 52 | 118 | 295 |
| v2 +hold +rebase | bursttiny | 130 | 99 | 264 | 66 | 264 | 38 | 107 | 169 |
| v2-fixed | burstcap | 144 | 198 | 726 | 99 | 726 | 55 | 128 | 516 |
| v2-fixed | splitcap | 240 | 99 | 759 | 99 | 729 | 53 | 114 | 293 |
| v2-fixed | bursttiny | 118 | 99 | 264 | 66 | 208 | 47 | 111 | 180 |
| v2-fixed +hold | burstcap | 144 | 165 | 693 | 99 | 716 | 52 | 121 | 366 |
| v2-fixed +hold | splitcap | 240 | 99 | 759 | 99 | 729 | 41 | 109 | 246 |
| v2-fixed +hold | bursttiny | 119 | 99 | 297 | 66 | 297 | 38 | 109 | 168 |
| v2-fixed +hold +rebase | burstcap | 144 | 165 | 693 | 99 | 716 | 52 | 121 | 366 |
| v2-fixed +hold +rebase | splitcap | 240 | 99 | 759 | 99 | 729 | 41 | 109 | 246 |
| v2-fixed +hold +rebase | bursttiny | 119 | 99 | 297 | 66 | 297 | 38 | 109 | 168 |

## 5. Verdict

- **Hold rule: keeps the alarm on for the whole long event.** burstlong coverage rises from 0.72 (v2) / 0.89 (v2-fixed) to 0.99, and alarm starts per episode-minute fall from about 10 to about 1.9. The spec criterion (>= 0.9 and <= 3) fails without hold and passes with it. Latency p90 falls from 657 to 558 ms (v2) and from 626 to 562 ms (v2-fixed). FA / min is unchanged for v2 and falls from 0.38 to 0.32 for v2-fixed.
- **Hold lowers the gt_score recall, but not the alarm-on recall.** The gt_score rule needs a new alarm START near every GT3 episode. One long event gives several GT3 episodes, and with hold the alarm is already on for the later ones, so they count as misses (burstlong 0.85 -> 0.53). Counted as "alarm on in the window", recall rises with hold: v2 0.89 -> 0.91, v2-fixed 0.96 -> 0.97. Which recall rule is the main one is an open decision; the truth and the scorer were not changed.
- **Rebase: lowers delaystep FA, recall unchanged, a few firings inside real episodes.** delaystep FA / min falls from 2.72 to 1.63 (v2) and from 2.85 to 0.95 (v2-fixed); overall FA / min from 0.46 to 0.42 and from 0.32 to 0.26. Recall and latency do not change. It fires 11 (v2) and 13 (v2-fixed) times inside a GT3 episode, all in tcpbbr, tcpcubic, ppbp and burstlong (long standing queues from competing traffic). These erase the delay level of a real queue; they did not cost a detection here, but they would hide a later rise of the same queue. delaystep has left the matrix, so the benefit is on old runs only.
- **Onset spread: clients of one event alarm within about 100-200 ms (p50), up to about 0.7-0.76 s (p90).** t_onset (last G = 0 before the alarm) lies 107-130 ms after the injected event start at p50 and within 170-370 ms at p90 with hold. The spread is about the same for all variants; hold slightly tightens the onset p90 on burstcap (536 -> 338 ms for v2).
