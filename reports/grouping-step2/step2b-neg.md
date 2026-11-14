# Step 2b B: negatives (G0) against a topology-based truth

A data class is right when its members share a recorded router egress whose queue reached 5 ms (GT1 target) inside the event interval; wrong otherwise (sub-ctrl with anyone; branches without a formed common upstream queue). Step 2 placements at penalty x1.

| type | events | data classes | right | wrong | wrong classes containing sub-ctrl |
|---|---|---|---|---|---|
| calm065 | 15 | 15 | 15 | 0 | 0 |
| calm090 | 36 | 36 | 36 | 0 | 0 |
| calmcbr090 | 39 | 39 | 39 | 0 | 0 |
| calmsplit | 37 | 37 | 37 | 0 | 0 |
| calmtree8 | 45 | 44 | 44 | 0 | 0 |
| calmuneven | 54 | 52 | 31 | 21 | 0 |
| randloss | 18 | 16 | 16 | 0 | 0 |
| all | 244 | 239 | 218 | 21 | 0 |

## ECG's confirmed SAME pairs on G0 (end of run, delta 0.15, v2-owd)

A pair is right when the two clients share a recorded router egress with at least one GT1 episode in the run.

| type | AQM | SAME pairs | right | wrong | wrong pairs |
|---|---|---|---|---|---|
| calm090 | pfifo | 3 | 3 | 0 | - |
| calm090 | pie | 3 | 3 | 0 | - |
| calm090 | red | 1 | 1 | 0 | - |
| calmcbr090 | pfifo | 3 | 3 | 0 | - |
| calmcbr090 | pie | 6 | 6 | 0 | - |
| calmcbr090 | red | 3 | 3 | 0 | - |
| calmsplit | pie | 1 | 1 | 0 | - |
| calmsplit | red | 1 | 1 | 0 | - |
| randloss | pfifo | 3 | 3 | 0 | - |
| randloss | pie | 1 | 1 | 0 | - |

Total: 25 right, 0 wrong.
