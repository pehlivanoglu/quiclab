# Check 1 with all planned clients present and the background on (2026-11-17)

Raw check 1 stays in each run's v3-checks.json; this is the restricted evaluation. Code: [loadshare_present.py](loadshare_present.py).

| run | raw check 1 | restricted check 1 | egress: load / U, share / s, seconds used |
|---|---|---|---|
| v4-N3-hchurn-def-codel-r1 | FAIL | ok | up 0.51 / 0.5, 0.312 / 0.3, 56 s; a 0.511 / 0.5, 0.313 / 0.3, 56 s; b 0.508 / 0.5, 0.312 / 0.3, 56 s |
| v4-N3-hchurn-def-codel-r2 | FAIL | ok | up 0.508 / 0.5, 0.311 / 0.3, 38 s; a 0.506 / 0.5, 0.31 / 0.3, 38 s; b 0.51 / 0.5, 0.313 / 0.3, 38 s |
| v4-N3-hchurn-def-pfifo-r1 | FAIL | ok | up 0.508 / 0.5, 0.311 / 0.3, 56 s; a 0.51 / 0.5, 0.311 / 0.3, 56 s; b 0.507 / 0.5, 0.31 / 0.3, 56 s |
| v4-N3-hchurn-def-pfifo-r2 | FAIL | ok | up 0.503 / 0.5, 0.306 / 0.3, 38 s; a 0.5 / 0.5, 0.3 / 0.3, 38 s; b 0.508 / 0.5, 0.309 / 0.3, 38 s |
| v4-T1-dclean-def-pfifo-r1 | FAIL | ok | main 0.507 / 0.5, 0.311 / 0.3, 223 s |
| v4-T1-dclean-def-pfifo-r2 | FAIL | ok | main 0.505 / 0.5, 0.308 / 0.3, 211 s |
| v4-T1-dclean-ext-pfifo-r1 | FAIL | ok | main 0.709 / 0.7, 0.31 / 0.3, 223 s |
| v4-T1-dclean-ext-pfifo-r2 | FAIL | ok | main 0.708 / 0.7, 0.309 / 0.3, 211 s |
| v4-T1-dclean-hs50-pfifo-r1 | FAIL | ok | main 0.511 / 0.5, 0.513 / 0.5, 223 s |
| v4-T1-dclean-hs50-pfifo-r2 | FAIL | ok | main 0.51 / 0.5, 0.513 / 0.5, 211 s |
