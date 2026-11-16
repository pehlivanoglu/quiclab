## Sojourn on router->switch (ms)

| run | smoke 1: n, p50 / p99 / mean, share > 0.2 ms | smoke 2: same |
|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | 234163, 1.03 / 21.238 / 2.67, 0.5802 | 234076, 0.986 / 20.539 / 2.616, 0.5798 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | 359041, 1.286 / 41.345 / 5.005, 0.6139 | 357740, 1.148 / 41.297 / 4.928, 0.6071 |

## Load, share, keyframe peak per bottleneck egress (smoke 1 -> smoke 2)

| run | egress | load | share / 0.96 | keyframe peak p50 ms | p90 ms |
|---|---|---|---|---|---|
| v3-SMOKE-calm-access-pfifo-r1 | main | 0.708 -> 0.708 | 0.307 -> 0.308 | 22.0 -> 22.9 | 26.0 -> 26.2 |
| v3-SMOKE-calm-rev-pfifo-r1 | main | 0.708 -> 0.708 | 0.308 -> 0.308 | 19.6 -> 19.3 | 22.3 -> 22.6 |
| v3-SMOKE-calm-s030u070-pfifo-r1 | main | 0.708 -> 0.708 | 0.308 -> 0.307 | 22.9 -> 21.8 | 26.4 -> 25.4 |
| v3-SMOKE-calm-split4-pfifo-r1 | up | 0.707 -> 0.707 | 0.308 -> 0.308 | 22.1 -> 22.9 | 25.8 -> 25.7 |
| v3-SMOKE-calm-split4-pfifo-r1 | a | 0.708 -> 0.708 | 0.307 -> 0.307 | 11.3 -> 11.7 | 14.1 -> 15.0 |
| v3-SMOKE-calm-split4-pfifo-r1 | b | 0.709 -> 0.709 | 0.307 -> 0.307 | 12.2 -> 11.7 | 14.1 -> 13.5 |
| v3-SMOKE-calm-tree16-pfifo-r1 | root | 0.71 -> 0.71 | 0.309 -> 0.309 | 21.8 -> 22.4 | 25.0 -> 25.2 |
| v3-SMOKE-calm-tree16-pfifo-r1 | X | 0.712 -> 0.712 | 0.308 -> 0.308 | 11.1 -> 11.3 | 13.8 -> 13.8 |
| v3-SMOKE-calm-tree16-pfifo-r1 | Y | 0.711 -> 0.711 | 0.308 -> 0.308 | 12.0 -> 11.3 | 14.4 -> 14.9 |
| v3-SMOKE-calm-tree16-pfifo-r1 | A | 0.71 -> 0.71 | 0.309 -> 0.309 | 6.3 -> 7.1 | 9.7 -> 10.8 |
| v3-SMOKE-calm-tree16-pfifo-r1 | B | 0.708 -> 0.708 | 0.31 -> 0.31 | 7.4 -> 7.5 | 12.0 -> 12.6 |
| v3-SMOKE-calm-tree16-pfifo-r1 | C | 0.713 -> 0.713 | 0.308 -> 0.308 | 7.8 -> 8.1 | 10.7 -> 10.6 |
| v3-SMOKE-calm-tree16-pfifo-r1 | D | 0.71 -> 0.71 | 0.309 -> 0.309 | 6.9 -> 7.1 | 11.0 -> 11.3 |
| v3-SMOKE-calm-uneven-pfifo-r1 | A | 0.708 -> 0.708 | 0.307 -> 0.307 | 23.2 -> 23.3 | 27.3 -> 27.8 |
| v3-SMOKE-calm-uneven-pfifo-r1 | B | 0.71 -> 0.71 | 0.307 -> 0.307 | 23.4 -> 22.4 | 26.9 -> 26.5 |
| v3-SMOKE-calm-uneven-pfifo-r1 | C | 0.708 -> 0.708 | 0.308 -> 0.308 | 22.6 -> 22.8 | 25.4 -> 26.0 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | main | 0.708 -> 0.706 | 0.309 -> 0.307 | 14.6 -> 14.2 | 24.0 -> 24.6 |

Largest |change|: load 0.002, share 0.002, keyframe peak p50 1.1 ms (median 0.4 ms).

## Same egress, tracer-independent (tc backlog every 5 ms / C), ms

| run | smoke 1: p50 / p90 / mean | smoke 2: same |
|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | 0.0 / 5.058 / 1.718 | 0.0 / 5.034 / 1.755 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | 0.0 / 5.88 / 3.414 | 0.0 / 5.859 / 3.394 |

## Sojourn floor on router->switch (empty queue: the enqueue / dequeue probe points), us

| run | smoke 1: min / p1 / p5 | smoke 2: min / p1 / p5 |
|---|---|---|
| v3-SMOKE-calm-s030u070-pfifo-r1 | 0.4 / 0.4 / 0.4 | 0.4 / 0.4 / 0.4 |
| v3-SMOKE-sburst-s030u070-pfifo-r1 | 0.3 / 0.4 / 0.4 | 0.4 / 0.4 / 0.4 |
