# A3: independent-timing runs (M6 indepfast / indepslow, single-queue AQMs)

| set | SAME rows | L_flat p10 / p50 / p90 | > 11.5 | < 2 | rows with a wrong-group template | prefers a wrong group |
|---|---|---|---|---|---|---|
| all | 2686 | 2.1 / 149.3 / 457.5 | 0.78 | 0.10 | 1136 | 0.01 |
| event overlapped by another group's window | 1762 | 0.3 / 122.3 / 474.1 | 0.68 | 0.15 | 1136 | 0.01 |
| not overlapped | 924 | 25.6 / 166.5 / 418.5 | 0.98 | 0.00 | 0 | nan |
| indepfast | 2122 | 1.0 / 130.0 / 455.2 | 0.74 | 0.12 | 1040 | 0.01 |
| indepslow | 564 | 23.8 / 192.7 / 471.9 | 0.96 | 0.00 | 96 | 0.00 |

## Clean-member templates (members with no other group's window overlapping the event)

| set | rows | unusable (no clean member) | L_flat clean p10 / p50 / p90 | > 11.5 | < 2 | prefers a wrong group (clean templates) |
|---|---|---|---|---|---|---|
| all | 2688 | 0.33 | 6.6 / 183.4 / 468.9 | 0.88 | 0.07 | 0.00 (n 273) |
| overlapped | 1764 | 0.50 | 0.5 / 209.5 / 495.5 | 0.77 | 0.15 | 0.00 (n 273) |
