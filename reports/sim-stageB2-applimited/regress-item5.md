| run | files | verdict | differing files |
|---|---|---|---|
| sim-B-A4-hhier-def-pfifo-r1 | 519 identical | identical |  |
| sim-B-G1-sburst-n24-pfifo-r1 | 368 identical | identical |  |

**Correction (2026-11-19):** this regression covered only two pfifo runs. The routing change it was meant to check
also shifted ns-3's automatic random-stream numbering, which changed PIE's drop sequence. PIE runs differ, and the B2
PIE rows from before 2026-11-19 cannot be reproduced with the current build. PIE / RED now use fixed streams; see
README.md section 9.2 and simulation/NOTES.md "Randomness".
