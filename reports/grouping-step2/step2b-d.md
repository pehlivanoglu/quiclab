# Step 2b D

## Single-group events with a truth group of 2: 81

| campaign / type | events | exact | both members in class 0 | one in class 0 |
|---|---|---|---|---|
| C1 burstlongsplit | 14 | 3 | 11 | 0 |
| K1 hier | 4 | 2 | 2 | 0 |
| K5 mixed | 1 | 1 | 0 | 0 |
| K6 depth | 36 | 20 | 16 | 0 |
| M1 burstlong | 2 | 0 | 2 | 0 |
| M1 burstudp | 5 | 3 | 2 | 0 |
| M1 tcpbbr | 1 | 1 | 0 | 0 |
| M2 burstcapq05 | 1 | 1 | 0 | 0 |
| M2 burstcapq15 | 1 | 0 | 1 | 0 |
| M2 burstcapq20 | 1 | 1 | 0 | 0 |
| M3 revjit20 | 1 | 0 | 1 | 0 |
| M4 fps60 | 1 | 0 | 1 | 0 |
| M5 bw8 | 3 | 3 | 0 | 0 |
| M5 bwmix | 1 | 0 | 1 | 0 |
| M6 gapfast | 1 | 1 | 0 | 0 |
| M6 gapslow | 1 | 1 | 0 | 0 |
| M6 indepfast | 5 | 2 | 3 | 0 |
| M6 indepslow | 2 | 2 | 0 | 0 |

### Example 1: grp-burstlongsplit-red-r1 [14.0, 46.0] s, truth pair ['b1', 'b3']

| client | truth | f(class 0) | f(median of all others) | f(the other pair member) | placed |
|---|---|---|---|---|---|
| a1 | quiet | 6.9 | 44.7 | 32.7 | class 0 |
| a2 | quiet | 10.2 | 47.3 | 41.3 | class 0 |
| a3 | quiet | 10.2 | 57.8 | 39.5 | class 0 |
| b1 | r2->switch-b | 46.4 | 69.1 | 7.9 | class 0 |
| b3 | r2->switch-b | 41.2 | 63.5 | 7.9 | class 0 |
| sub-ctrl | quiet | 0.2 | 49.0 | 38.2 | class 0 |

reports/grouping-step2/step2b-pair1.png

### Example 2: grp-burstlongsplit-red-r1 [54.1, 116.1] s, truth pair ['a1', 'a3']

| client | truth | f(class 0) | f(median of all others) | f(the other pair member) | placed |
|---|---|---|---|---|---|
| a1 | r2->switch-a | 35.8 | 49.7 | 8.2 | class 0 |
| a3 | r2->switch-a | 31.2 | 40.9 | 8.2 | class 0 |
| b1 | quiet | 3.8 | 43.3 | 38.0 | class 0 |
| b2 | quiet | 4.7 | 57.1 | 34.6 | class 0 |
| b3 | quiet | 4.9 | 56.3 | 39.3 | class 0 |
| sub-ctrl | quiet | 0.2 | 61.5 | 34.3 | class 0 |

reports/grouping-step2/step2b-pair2.png

## Assignment passes at the iteration cap (10): 29 passes in 29 events

| event class | events |
|---|---|
| overlapping (independent timing) | 6 |
| negative | 5 |
| J1 hierjit20 | 5 |
| J1 hierjit10 | 3 |
| J1 hierjit5 | 3 |
| J1 hierrandphase | 2 |
| two groups, shifted or overlapping windows | 2 |
| single group | 2 |
| J1 hiersamephase | 1 |

| campaign / type | events |
|---|---|
| J1 hierjit20 pfifo | 5 |
| J1 hierjit10 pfifo | 3 |
| J1 hierjit5 pfifo | 3 |
| M6 indepfast red | 3 |
| G0 calmsplit red | 2 |
| G0 calmuneven red | 2 |
| J1 hierrandphase pfifo | 2 |
| M6 indepfast codel | 2 |
| G0 calmsplit pie | 1 |
| K1 hier red | 1 |
| J1 hiersamephase pfifo | 1 |
| K1 hier pie | 1 |
