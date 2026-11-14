# Per-client GT1 on fq_codel / cake: does it behave as intended? (2026-11-12)

`check.py` → `report.md`. 37 development runs, 3 779 (window, expected client)
pairs on pinned egresses. No grouping conclusion.

| AQM | pairs | congested, aggregate truth | congested, per-client truth | own max backlog kB p50, congested / not | GT3 (own OWD) episode, congested / not |
|---|---|---|---|---|---|
| fq_codel | 1 271 | 1 259 | 884 | 71.2 / 12.7 | 0.78 / 0.03 |
| cake | 2 400 | 2 385 | 1 558 | 71.7 / 11.5 | 0.80 / 0.11 |
| mixab (b side) | 108 | 108 | 71 | 68.8 / 8.9 | 0.75 / 0.00 |

The per-client truth only removes clients (never adds one), it removes those whose
own queue stayed small, and its labels agree with each client's own OWD. Removal
follows the bitrate as expected under fair queueing: share labelled congested for
1 / 2.5 / 5 Mb/s clients 0.13 / 0.78 / 0.98 on fq_codel and 0.21 / 0.76 / 0.92 on cake
(aggregate truth: 0.99 for all).
