# Shadow v2: loss-gate experiment

200 runs, theta_on 0.25, theta_off 0.125. Only the gate of the loss term (and, in the -holdloss rows, the hold rule's loss clause) changes; G_ref refitted per row on the calm pfifo-r1 runs. 'legacy' = Step 6 with the GT3-frozen F3 normaliser (truth leak); every other row uses the causal normaliser. git 7acb64c-dirty.

Gates: growth = F2 or F3 score > 0 in the last 3 ticks (Step 4); level = z(F1) >= 1 in the last 3 ticks; level2 = z(F1) >= 2; either / both = growth or / and level; open = no gate; off = no loss term; +cap = positive loss contribution per excursion of G capped at G_ref / 4 (half the alarm level); -holdloss = hold without its 'loss within T_clear' clause.

| detector | G_ref | precision | recall | recall (alarm on) | FA / min | lat p50 | p90 | randloss FA / min | randloss FA in loss window | calm030 FA | calm065 FA | calm090 FA | calmcbr090 FA | worst negative cell FA | recall loss-triggered GT3 | recall delay-triggered GT3 | fq_codel comp. recall | fq_codel comp. FA | warned before harm B200 | B600 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 legacy | 57.5 | 0.95 | 0.81 | 0.91 | 0.46 | 249 | 558 | 0.54 | 0.95 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.75 | 0.82 | 1.21 | 0.94 | 0.97 |
| v2 growth | 57.5 | 0.95 | 0.81 | 0.91 | 0.46 | 249 | 559 | 0.54 | 0.95 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.75 | 0.82 | 1.21 | 0.94 | 0.97 |
| v2 level | 57.5 | 0.95 | 0.81 | 0.91 | 0.45 | 248 | 551 | 0.37 | 0.93 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.75 | 0.81 | 1.21 | 0.94 | 0.97 |
| v2 level2 | 57.5 | 0.95 | 0.80 | 0.91 | 0.44 | 248 | 547 | 0.34 | 0.93 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.74 | 0.81 | 1.25 | 0.94 | 0.96 |
| v2 either | 57.5 | 0.95 | 0.81 | 0.92 | 0.46 | 249 | 553 | 0.52 | 0.95 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.75 | 0.82 | 1.21 | 0.94 | 0.97 |
| v2 both | 57.5 | 0.95 | 0.80 | 0.91 | 0.45 | 249 | 556 | 0.34 | 0.93 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.75 | 0.81 | 1.21 | 0.94 | 0.97 |
| v2 open | 57.5 | 0.95 | 0.81 | 0.92 | 0.46 | 249 | 554 | 0.61 | 0.96 | 0.08 | 0.35 | 0.18 | 0.42 | 1.71 | 0.90 | 0.75 | 0.82 | 1.21 | 0.94 | 0.97 |
| v2 off | 50.9 | 0.92 | 0.80 | 0.92 | 0.73 | 217 | 489 | 0.76 | 0.61 | 0.08 | 0.14 | 0.53 | 1.13 | 4.65 | 0.89 | 0.75 | 0.81 | 2.20 | 0.95 | 0.98 |
| v2 growth+cap | 57.5 | 0.95 | 0.80 | 0.91 | 0.43 | 250 | 559 | 0.22 | 0.89 | 0.08 | 0.35 | 0.09 | 0.42 | 1.71 | 0.90 | 0.74 | 0.81 | 1.21 | 0.94 | 0.97 |
| v2 level+cap | 57.5 | 0.95 | 0.80 | 0.91 | 0.43 | 249 | 556 | 0.22 | 0.89 | 0.08 | 0.35 | 0.09 | 0.42 | 1.71 | 0.90 | 0.74 | 0.81 | 1.19 | 0.94 | 0.97 |
| v2 either+cap | 57.5 | 0.95 | 0.80 | 0.91 | 0.44 | 249 | 556 | 0.25 | 0.90 | 0.08 | 0.35 | 0.09 | 0.42 | 1.71 | 0.90 | 0.74 | 0.81 | 1.19 | 0.94 | 0.97 |
| v2 growth -holdloss | 52.8 | 0.94 | 0.83 | 0.91 | 0.55 | 241 | 548 | 0.49 | 0.90 | 0.08 | 0.28 | 0.18 | 0.66 | 2.69 | 0.91 | 0.78 | 0.89 | 1.69 | 0.94 | 0.97 |
| v2 level -holdloss | 52.8 | 0.94 | 0.82 | 0.91 | 0.54 | 240 | 538 | 0.27 | 0.82 | 0.08 | 0.28 | 0.18 | 0.66 | 2.69 | 0.91 | 0.77 | 0.89 | 1.71 | 0.94 | 0.97 |
| v2 level+cap -holdloss | 52.8 | 0.94 | 0.82 | 0.91 | 0.54 | 242 | 546 | 0.27 | 0.82 | 0.08 | 0.28 | 0.18 | 0.66 | 2.69 | 0.90 | 0.77 | 0.89 | 1.66 | 0.94 | 0.97 |
| v2-fixed legacy | 71.7 | 0.97 | 0.84 | 0.97 | 0.33 | 280 | 562 | 0.39 | 0.94 | 0.00 | 0.21 | 1.23 | 1.67 | 5.14 | 0.90 | 0.80 | 0.79 | 0.73 | 0.96 | 0.99 |
| v2-fixed growth | 71.7 | 0.97 | 0.84 | 0.97 | 0.33 | 279 | 559 | 0.39 | 0.94 | 0.00 | 0.21 | 1.32 | 1.55 | 4.65 | 0.90 | 0.80 | 0.79 | 0.71 | 0.96 | 0.99 |
| v2-fixed level | 71.7 | 0.97 | 0.84 | 0.97 | 0.32 | 279 | 554 | 0.29 | 0.92 | 0.00 | 0.21 | 1.23 | 1.55 | 4.65 | 0.90 | 0.80 | 0.79 | 0.71 | 0.96 | 0.99 |
| v2-fixed level2 | 71.7 | 0.97 | 0.84 | 0.97 | 0.32 | 279 | 555 | 0.25 | 0.90 | 0.00 | 0.21 | 1.32 | 1.61 | 4.89 | 0.89 | 0.80 | 0.78 | 0.73 | 0.96 | 0.99 |
| v2-fixed either | 71.7 | 0.96 | 0.84 | 0.97 | 0.33 | 279 | 553 | 0.42 | 0.94 | 0.00 | 0.21 | 1.32 | 1.55 | 4.65 | 0.90 | 0.80 | 0.79 | 0.71 | 0.96 | 0.99 |
| v2-fixed both | 71.7 | 0.97 | 0.84 | 0.97 | 0.32 | 280 | 560 | 0.29 | 0.92 | 0.00 | 0.21 | 1.23 | 1.55 | 4.65 | 0.90 | 0.80 | 0.79 | 0.71 | 0.96 | 0.99 |
| v2-fixed open | 71.7 | 0.96 | 0.84 | 0.97 | 0.33 | 279 | 553 | 0.47 | 0.95 | 0.00 | 0.21 | 1.32 | 1.55 | 4.65 | 0.90 | 0.80 | 0.79 | 0.71 | 0.96 | 0.99 |
| v2-fixed off | 68.8 | 0.95 | 0.82 | 0.98 | 0.45 | 255 | 500 | 0.34 | 0.79 | 0.00 | 0.28 | 2.38 | 2.50 | 5.14 | 0.88 | 0.78 | 0.77 | 0.88 | 0.96 | 0.99 |
| v2-fixed growth+cap | 71.7 | 0.97 | 0.84 | 0.97 | 0.32 | 282 | 574 | 0.27 | 0.91 | 0.00 | 0.21 | 1.32 | 1.61 | 4.89 | 0.90 | 0.80 | 0.79 | 0.74 | 0.96 | 0.99 |
| v2-fixed level+cap | 71.7 | 0.97 | 0.84 | 0.97 | 0.33 | 283 | 569 | 0.29 | 0.92 | 0.00 | 0.21 | 1.23 | 1.61 | 4.89 | 0.90 | 0.80 | 0.79 | 0.74 | 0.96 | 0.99 |
| v2-fixed either+cap | 71.7 | 0.97 | 0.84 | 0.97 | 0.33 | 282 | 569 | 0.27 | 0.91 | 0.00 | 0.21 | 1.32 | 1.61 | 4.89 | 0.90 | 0.80 | 0.79 | 0.74 | 0.96 | 0.99 |
| v2-fixed growth -holdloss | 67.2 | 0.96 | 0.86 | 0.97 | 0.39 | 271 | 556 | 0.12 | 0.80 | 0.00 | 0.28 | 2.46 | 2.03 | 7.34 | 0.92 | 0.83 | 0.84 | 0.88 | 0.96 | 0.99 |
| v2-fixed level -holdloss | 67.2 | 0.96 | 0.86 | 0.97 | 0.39 | 270 | 551 | 0.10 | 0.75 | 0.00 | 0.28 | 2.29 | 2.20 | 7.34 | 0.91 | 0.83 | 0.83 | 0.88 | 0.96 | 0.99 |
| v2-fixed level+cap -holdloss | 67.2 | 0.96 | 0.86 | 0.97 | 0.39 | 276 | 569 | 0.10 | 0.75 | 0.00 | 0.21 | 2.29 | 2.15 | 7.34 | 0.91 | 0.83 | 0.83 | 0.89 | 0.96 | 0.99 |

## 95 % bootstrap intervals over runs

| detector | recall | alarm-on recall | FA / min | randloss FA / min |
|---|---|---|---|---|
| v2 legacy | 0.76-0.84 | 0.88-0.94 | 0.36-0.57 | 0.37-0.70 |
| v2 growth | 0.77-0.85 | 0.88-0.95 | 0.35-0.56 | 0.40-0.69 |
| v2 level | 0.77-0.84 | 0.88-0.94 | 0.35-0.56 | 0.22-0.52 |
| v2 level2 | 0.76-0.84 | 0.87-0.94 | 0.35-0.57 | 0.15-0.51 |
| v2 either | 0.77-0.85 | 0.88-0.94 | 0.36-0.56 | 0.34-0.69 |
| v2 both | 0.77-0.84 | 0.88-0.94 | 0.35-0.54 | 0.17-0.49 |
| v2 open | 0.76-0.84 | 0.88-0.94 | 0.36-0.57 | 0.40-0.90 |
| v2 off | 0.76-0.84 | 0.89-0.95 | 0.59-0.87 | 0.62-0.93 |
| v2 growth+cap | 0.76-0.84 | 0.87-0.94 | 0.34-0.54 | 0.06-0.42 |
| v2 level+cap | 0.75-0.84 | 0.87-0.94 | 0.34-0.53 | 0.10-0.37 |
| v2 either+cap | 0.76-0.84 | 0.87-0.94 | 0.34-0.55 | 0.10-0.45 |
| v2 growth -holdloss | 0.79-0.86 | 0.87-0.94 | 0.43-0.68 | 0.30-0.73 |
| v2 level -holdloss | 0.78-0.86 | 0.87-0.94 | 0.43-0.66 | 0.10-0.45 |
| v2 level+cap -holdloss | 0.78-0.86 | 0.87-0.94 | 0.42-0.66 | 0.10-0.45 |
| v2-fixed legacy | 0.81-0.86 | 0.97-0.98 | 0.25-0.42 | 0.24-0.53 |
| v2-fixed growth | 0.81-0.86 | 0.97-0.98 | 0.25-0.41 | 0.26-0.53 |
| v2-fixed level | 0.81-0.86 | 0.96-0.98 | 0.25-0.41 | 0.14-0.43 |
| v2-fixed level2 | 0.80-0.86 | 0.96-0.98 | 0.25-0.41 | 0.10-0.40 |
| v2-fixed either | 0.81-0.86 | 0.97-0.98 | 0.26-0.42 | 0.26-0.57 |
| v2-fixed both | 0.81-0.86 | 0.96-0.98 | 0.24-0.40 | 0.15-0.45 |
| v2-fixed open | 0.80-0.86 | 0.97-0.98 | 0.26-0.42 | 0.30-0.60 |
| v2-fixed off | 0.79-0.85 | 0.97-0.98 | 0.36-0.55 | 0.17-0.55 |
| v2-fixed growth+cap | 0.81-0.86 | 0.96-0.98 | 0.25-0.42 | 0.13-0.45 |
| v2-fixed level+cap | 0.81-0.87 | 0.96-0.98 | 0.25-0.40 | 0.12-0.45 |
| v2-fixed either+cap | 0.81-0.87 | 0.96-0.98 | 0.25-0.41 | 0.11-0.40 |
| v2-fixed growth -holdloss | 0.84-0.89 | 0.97-0.98 | 0.30-0.49 | 0.05-0.20 |
| v2-fixed level -holdloss | 0.84-0.89 | 0.97-0.98 | 0.30-0.50 | 0.02-0.17 |
| v2-fixed level+cap -holdloss | 0.84-0.89 | 0.96-0.98 | 0.29-0.50 | 0.03-0.17 |

## Verdict

- **Best gate: level + cap ("gate:level+cap") for both detectors.** The loss term counts positively only while z(F1) >= 1 in the last 3 ticks (a queue is standing), and its positive contribution per excursion of G is capped at G_ref / 4 (half the alarm level), so loss alone cannot raise an alarm.
  - v2: randloss FA / min 0.54 -> 0.22 (95 % interval 0.40-0.69 -> 0.10-0.37, no overlap); calm090 0.18 -> 0.09; overall recall 0.81 -> 0.80, alarm-on recall 0.91, FA 0.46 -> 0.43, p90 559 -> 556 ms; warned before harm unchanged (0.94 / 0.97 at B 200 / 600 ms).
  - v2-fixed: randloss 0.39 -> 0.29 (intervals overlap: 0.26-0.53 vs 0.12-0.45); overall unchanged (recall 0.84, FA 0.32-0.33); p90 560 -> 569 ms.
  - G_ref did not change (57.5 / 71.7): the calm fit is set by delay features, not by loss.
- **The loss term is needed.** "off" (no loss term) raises FA (v2 0.46 -> 0.73, v2-fixed 0.33 -> 0.46) and the worst negative cell (1.71 -> 4.65, 4.65 -> 5.38): the negative part of the loss score (no loss = evidence of calm) drains G.
- **The hold rule's loss clause must stay.** "-holdloss" lowers G_ref (57.5 -> 52.8, 71.7 -> 67.2), raises recall by 0.02 but raises FA (0.46 -> 0.55, 0.33 -> 0.39) and the worst negative cell (v2 2.69, v2-fixed 7.34).
- **Hypothesis refuted: the level gate does not rescue the fq_codel misses.** Recall on loss-triggered GT3 episodes stays 0.90 and fq_codel competition recall 0.81-0.82 for every gate.
- **What is left on randloss is not the gate.** With the cap, loss can bring G to at most half of the alarm level; the remaining alarms in loss windows need F1 / F2 / F3 evidence. Raw positive term shares before those alarms (v2 level+cap): loss 0.40, F3 0.23, F1 0.22, F2 0.14: loss recovery (retransmissions, pending bytes) moves the delay features too.
- **Negative criterion still fails:** worst cell calmcbr090 fq_codel (v2 1.71, v2-fixed 4.89 with the new gate); loaded links, not loss.
- **randloss is i.i.d. netem loss**, not wireless: real Wi-Fi / cellular loss is mostly hidden by link-layer retransmission and shows as delay jitter. A wireless claim needs Gilbert-Elliott loss and jitter / aggregation scenarios.
- **F4 unit fix (drain time P / R, floor 0.0079) changes no row by more than 0.01 FA / min or 1 ms, except the worst negative cell of v2-fixed off (5.38 -> 5.14).** This table uses the fixed F4.
