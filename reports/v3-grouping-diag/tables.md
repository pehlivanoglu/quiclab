# Grouping diagnostics (v3): tables

## Q1a. Per ECG event and egress: gt1 (router counters) vs qlog (per-packet trace, same CoDel rule)

Counts of event x egress; `both` = both congested, `gt1 only`, `qlog only`, `neither`. Rep 1 / rep 2.

### generous (overlap)

| cell | level | both | gt1 only | qlog only | neither | disagree share |
|---|---|---|---|---|---|---|
| C7-hhier-s030-pfifo | mid | 18 / 18 | 0 / 0 | 0 / 0 | 53 / 52 | 0.00 / 0.00 |
| C7-hhier-s030-pfifo | leaf | 93 / 92 | 0 / 0 | 0 / 0 | 49 / 48 | 0.00 / 0.00 |
| C9-hdepth-tree16-codel | root | 9 / 7 | 0 / 0 | 0 / 0 | 42 / 47 | 0.00 / 0.00 |
| C9-hdepth-tree16-codel | mid | 12 / 13 | 0 / 0 | 0 / 0 | 90 / 95 | 0.00 / 0.00 |
| C9-hdepth-tree16-codel | leaf | 36 / 39 | 0 / 0 | 0 / 0 | 168 / 177 | 0.00 / 0.00 |
| C9-hdepth-tree16-fq_codel | root | 15 / 16 | 0 / 0 | 0 / 0 | 86 / 86 | 0.00 / 0.00 |
| C9-hdepth-tree16-fq_codel | mid | 26 / 28 | 0 / 0 | 0 / 0 | 176 / 176 | 0.00 / 0.00 |
| C9-hdepth-tree16-fq_codel | leaf | 77 / 66 | 0 / 1 | 0 / 2 | 327 / 339 | 0.00 / 0.01 |
| C9-hdepth-tree16-pfifo | root | 9 / 7 | 0 / 0 | 0 / 0 | 48 / 46 | 0.00 / 0.00 |
| C9-hdepth-tree16-pfifo | mid | 13 / 15 | 0 / 0 | 0 / 0 | 101 / 91 | 0.00 / 0.00 |
| C9-hdepth-tree16-pfifo | leaf | 45 / 37 | 0 / 0 | 0 / 0 | 183 / 175 | 0.00 / 0.00 |

### strict (>= half of the interval)

| cell | level | both | gt1 only | qlog only | neither | disagree share |
|---|---|---|---|---|---|---|
| C7-hhier-s030-pfifo | mid | 18 / 18 | 0 / 0 | 0 / 0 | 53 / 52 | 0.00 / 0.00 |
| C7-hhier-s030-pfifo | leaf | 82 / 83 | 0 / 0 | 0 / 1 | 60 / 56 | 0.00 / 0.01 |
| C9-hdepth-tree16-codel | root | 9 / 7 | 0 / 0 | 0 / 0 | 42 / 47 | 0.00 / 0.00 |
| C9-hdepth-tree16-codel | mid | 12 / 13 | 0 / 0 | 0 / 0 | 90 / 95 | 0.00 / 0.00 |
| C9-hdepth-tree16-codel | leaf | 36 / 39 | 0 / 0 | 0 / 0 | 168 / 177 | 0.00 / 0.00 |
| C9-hdepth-tree16-fq_codel | root | 15 / 16 | 0 / 0 | 0 / 0 | 86 / 86 | 0.00 / 0.00 |
| C9-hdepth-tree16-fq_codel | mid | 25 / 28 | 0 / 0 | 1 / 0 | 176 / 176 | 0.00 / 0.00 |
| C9-hdepth-tree16-fq_codel | leaf | 34 / 38 | 43 / 28 | 0 / 0 | 327 / 342 | 0.11 / 0.07 |
| C9-hdepth-tree16-pfifo | root | 9 / 7 | 0 / 0 | 0 / 0 | 48 / 46 | 0.00 / 0.00 |
| C9-hdepth-tree16-pfifo | mid | 13 / 15 | 0 / 0 | 0 / 0 | 101 / 91 | 0.00 / 0.00 |
| C9-hdepth-tree16-pfifo | leaf | 45 / 36 | 0 / 0 | 0 / 0 | 183 / 176 | 0.00 / 0.00 |

Episodes per egress over the run, gt1 / qlog (rep 1; rep 2):

| cell | egress: gt1/qlog r1 ; r2 |
|---|---|
| C7-hhier-s030-pfifo | r1->r2 15/15 ; 15/15, r2->switch-a 33/33 ; 34/33, r2->switch-b 27/27 ; 28/28 |
| C9-hdepth-tree16-codel | r0->r1 6/6 ; 6/6, r0->r2 6/6 ; 6/6, r1->switch-a 12/12 ; 16/15, r1->switch-b 9/8 ; 10/9, r2->switch-c 14/14 ; 14/14, r2->switch-d 6/6 ; 6/8, rr->r0 6/6 ; 6/6 |
| C9-hdepth-tree16-fq_codel | r0->r1 6/69 ; 6/62, r0->r2 6/69 ; 6/74, r1->switch-a 12/62 ; 12/56, r1->switch-b 6/30 ; 6/24, r2->switch-c 12/61 ; 12/65, r2->switch-d 7/34 ; 6/32, rr->r0 6/111 ; 6/108 |
| C9-hdepth-tree16-pfifo | r0->r1 6/6 ; 6/6, r0->r2 6/6 ; 6/6, r1->switch-a 12/12 ; 12/12, r1->switch-b 7/7 ; 6/6, r2->switch-c 12/12 ; 13/13, r2->switch-d 6/6 ; 8/8, rr->r0 6/6 ; 6/6 |

## Q1b. B1 votes the gt1 rule types `---` (no own leaf / other leaf / shared upstream congested)

| cell | rep | votes | `---` votes | pair | what gt1 sees in that event | what qlog (generous) sees | votes |
|---|---|---|---|---|---|---|---|
| C7-hhier-s030-pfifo | 1 | 526 | 0 | - | - | - | 0 |
| C7-hhier-s030-pfifo | 2 | 494 | 0 | - | - | - | 0 |
| C9-hdepth-tree16-codel | 1 | 2376 | 1064 | across | other | qlog sees leaf | 400 |
|  |  |  |  | across | other mid | qlog sees mid | 192 |
|  |  |  |  | across | own mid | qlog sees mid | 192 |
|  |  |  |  | siblings | other | qlog sees leaf | 184 |
|  |  |  |  | siblings | other | qlog sees mid | 96 |
| C9-hdepth-tree16-codel | 2 | 2306 | 1154 | across | other | qlog sees leaf | 408 |
|  |  |  |  | siblings | other | qlog sees leaf | 208 |
|  |  |  |  | across | own mid | qlog sees mid | 200 |
|  |  |  |  | across | other mid | qlog sees mid | 196 |
|  |  |  |  | siblings | other | qlog sees mid | 94 |
|  |  |  |  | across | gt1 sees nothing | qlog sees nothing | 32 |
|  |  |  |  | siblings | gt1 sees nothing | qlog sees nothing | 16 |
| C9-hdepth-tree16-fq_codel | 1 | 70 | 19 | across | own mid | qlog sees mid | 9 |
|  |  |  |  | across | other mid | qlog sees mid | 6 |
|  |  |  |  | siblings | other | qlog sees mid | 4 |
| C9-hdepth-tree16-fq_codel | 2 | 93 | 25 | across | gt1 sees nothing | qlog sees nothing | 8 |
|  |  |  |  | across | other | qlog sees nothing | 7 |
|  |  |  |  | siblings | gt1 sees nothing | qlog sees nothing | 4 |
|  |  |  |  | siblings | other | qlog sees nothing | 3 |
|  |  |  |  | across | other | qlog sees leaf | 3 |
| C9-hdepth-tree16-pfifo | 1 | 2605 | 1156 | across | other | qlog sees leaf | 466 |
|  |  |  |  | siblings | other | qlog sees leaf | 200 |
|  |  |  |  | across | other mid | qlog sees mid | 198 |
|  |  |  |  | across | own mid | qlog sees mid | 196 |
|  |  |  |  | siblings | other | qlog sees mid | 96 |
| C9-hdepth-tree16-pfifo | 2 | 2425 | 1187 | across | other | qlog sees leaf | 408 |
|  |  |  |  | across | other mid | qlog sees mid | 224 |
|  |  |  |  | across | own mid | qlog sees mid | 219 |
|  |  |  |  | siblings | other | qlog sees leaf | 184 |
|  |  |  |  | siblings | other | qlog sees mid | 104 |
|  |  |  |  | across | gt1 sees nothing | qlog sees nothing | 32 |
|  |  |  |  | siblings | gt1 sees nothing | qlog sees nothing | 16 |

Events behind the `---` votes: stimulus active at t0 (cell) and what each truth calls congested.

| cell | rep | events | stimulus cells (events) | gt1 empty | qlog strict empty | qlog strict levels (events) |
|---|---|---|---|---|---|---|
| C9-hdepth-tree16-codel | 1 | 41 | D 6, A+C 6, Y 6, X 6, A 6, B 6 | 0 | 0 | D 6, A+C 6, Y 6, X 6, A 6, B 6 |
| C9-hdepth-tree16-codel | 2 | 42 | B 7, A 7, X 7, Y 6, D 6, C 6 | 1 | 1 | B 7, A 7, X 7, Y 6, D 6, C 6 |
| C9-hdepth-tree16-fq_codel | 1 | 2 | X 2 | 0 | 0 | X 2 |
| C9-hdepth-tree16-fq_codel | 2 | 3 | D 2, none 1 | 1 | 2 | none 2, D 1 |
| C9-hdepth-tree16-pfifo | 1 | 47 | A+C 9, X 7, A 7, D 6, Y 6, C 6 | 0 | 0 | A+C 9, X 7, A 7, D 6, Y 6, C 6 |
| C9-hdepth-tree16-pfifo | 2 | 46 | Y 8, X 7, B 6, D 6, A+C 6, A 6 | 1 | 1 | Y 8, X 7, B 6, D 6, A+C 6, A 6 |

## Q1c. False memberships (same-leaf wrong; strict = wrong minus those sharing a congested egress with >= half the members)

| cell | method | memberships r1 / r2 | wrong (same-leaf) r1 / r2 | strict wrong, gt1 r1 / r2 | strict wrong, qlog r1 / r2 | generous-rule wrong, gt1 / qlog r1 ; r2 | wrong pairs not sharing (strict), gt1 / qlog r1 ; r2 |
|---|---|---|---|---|---|---|---|
| C7-hhier-s030-pfifo | ecg | 19 / 14 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 ; 0 / 0 | 0/0 / 0/0 ; 0/0 / 0/0 |
| C7-hhier-s030-pfifo | h3 | 44 / 22 | 11 / 8 | 0 / 0 | 0 / 0 | 0 / 0 ; 0 / 0 | 4/51 / 4/51 ; 56/108 / 56/108 |
| C9-hdepth-tree16-codel | ecg | 45 / 46 | 13 / 32 | 13 / 16 | 13 / 16 | 13 / 13 ; 16 / 16 | 404/500 / 404/500 ; 512/656 / 512/656 |
| C9-hdepth-tree16-codel | h3 | 227 / 186 | 134 / 127 | 76 / 70 | 76 / 70 | 76 / 76 ; 70 / 70 | 564/873 / 564/873 ; 778/1244 / 778/1244 |
| C9-hdepth-tree16-fq_codel | ecg | 36 / 46 | 20 / 29 | 6 / 11 | 6 / 11 | 6 / 6 ; 11 / 11 | 323/444 / 319/444 ; 299/434 / 310/434 |
| C9-hdepth-tree16-fq_codel | h3 | 46 / 51 | 34 / 41 | 12 / 22 | 13 / 26 | 12 / 12 ; 22 / 22 | 670/977 / 693/977 ; 893/1383 / 921/1383 |
| C9-hdepth-tree16-pfifo | ecg | 40 / 55 | 5 / 43 | 5 / 25 | 5 / 25 | 5 / 5 ; 25 / 25 | 404/588 / 404/588 ; 1852/2378 / 1852/2378 |
| C9-hdepth-tree16-pfifo | h3 | 162 / 198 | 99 / 142 | 61 / 75 | 61 / 75 | 61 / 61 ; 75 / 75 | 994/1673 / 994/1673 ; 683/1236 / 683/1236 |

## Q1d. Wrong pairs (pair x close) by where the paths separate and what is congested (qlog strict)

### h3

| cell | across mids: not shared; congested on paths: leaf | across mids: not shared; congested on paths: mid | across mids: not shared; congested on paths: none | across mids: shared root congested | siblings (same mid): not shared; congested on paths: leaf | siblings (same mid): not shared; congested on paths: none | siblings (same mid): shared leaf congested | siblings (same mid): shared mid congested | siblings (same mid): shared root congested |
|---|---|---|---|---|---|---|---|---|---|
| C9-hdepth-tree16-codel | 78 / 37 | 10 / 87 | 145 / 186 | 69 / 189 | 123 / 157 | 208 / 311 | 0 / 0 | 144 / 144 | 96 / 133 |
| C9-hdepth-tree16-fq_codel | 79 / 91 | 65 / 122 | 195 / 193 | 116 / 90 | 53 / 72 | 301 / 443 | 17 / 38 | 53 / 159 | 98 / 175 |
| C9-hdepth-tree16-pfifo | 134 / 67 | 40 / 27 | 185 / 179 | 274 / 204 | 287 / 165 | 348 / 245 | 0 / 0 | 149 / 217 | 256 / 132 |

### ecg

| cell | across mids: not shared; congested on paths: leaf | across mids: not shared; congested on paths: mid | across mids: not shared; congested on paths: none | across mids: shared root congested | siblings (same mid): not shared; congested on paths: leaf | siblings (same mid): not shared; congested on paths: none | siblings (same mid): shared leaf congested | siblings (same mid): shared mid congested | siblings (same mid): shared root congested |
|---|---|---|---|---|---|---|---|---|---|
| C9-hdepth-tree16-codel | 172 / 0 | 108 / 0 | 124 / 0 | 96 / 0 | 0 / 224 | 0 / 288 | 0 / 0 | 0 / 80 | 0 / 64 |
| C9-hdepth-tree16-fq_codel | 29 / 45 | 50 / 67 | 109 / 62 | 55 / 36 | 18 / 16 | 113 / 120 | 1 / 13 | 27 / 40 | 42 / 35 |
| C9-hdepth-tree16-pfifo | 0 / 584 | 0 / 352 | 0 / 408 | 0 / 248 | 216 / 280 | 188 / 228 | 0 / 0 | 96 / 154 | 88 / 124 |

## Q2a. First ten ECG events per rep (stimulus cell active at t0 [ECG case] members by leaf)

- **C13-llong-s030-pfifo r1**: b [D] b3; b [SOLO] b1; b [A] b4; b [A] b3; b [SOLO] b1; a [D] a4; up [GLOBAL] a4,b4; up [GLOBAL] a4,b4; a [A] a4; up [GLOBAL] a4,b4
- **C13-llong-s030-pfifo r2**: up [D] a4,b4; b [C] b4; a [C] a4; b [C] b4; a [C] a4; up [A] a4,b4; up [A] a4,b4; up [A] a4,b4; a [C] a4; b [C] b4
- **C7-hhier-s030-pfifo r1**: a+b@2 [D] a2; a+b@2 [D] a2; a+b@2 [D] b4; a [B] a4; a+up [GLOBAL] a4,b4; a+b [GLOBAL] a4,b4; b [A] b4; up [GLOBAL] a4,b4; a+b@2 [GLOBAL] a4; a+b@2 [A] b4
- **C7-hhier-s030-pfifo r2**: b [D] b4; b [A] b4; a+b@0.5 [D] a4; a+b@0.5 [A] b4; a+b@2 [A] a4; a+b@2 [C] b2; a+b@2 [C] b2; a+b@2 [A] a4; a+b@2 [A] b4; b [A] b4
- **C9-hdepth-tree16-pfifo r1**: D [D] D4; A+C [D] C3; A+C [D] A3; A+C [SOLO] C1; A+C [SOLO] A1; Y [B] C4,D4; root [GLOBAL] A4,B4,C4,D4; D [A] D4; C [A] C4; Y [GLOBAL] C4,D4
- **C9-hdepth-tree16-pfifo r2**: B [D] B4; none [SOLO] A1; root [A] A4,B4,C4,D3; root [SOLO] D1; Y [C] C3,D2; Y [A] C1,D2; Y [A] C4,D3; Y [SOLO] D1; D [A] D4; A+C [A] A4,C4

Stimulus order (cells of the stimulus windows, as scheduled) per rep:

- C13-llong-s030-pfifo r1: b > a > up > a > up > a > b > up
- C13-llong-s030-pfifo r2: up > b > a > b > a > up > a > b > a > b
- C7-hhier-s030-pfifo r1: a+b@2 > a > a+up > a+b > b > up > a+b@2 > a > b > a > b > up > a+b@2 > b
- C7-hhier-s030-pfifo r2: b > a+b@0.5 > a+b@2 > b > up > a > b > a+up > a > a+b > a > a+b@0.5 > a+b@2 > a+b@0.5
- C9-hdepth-tree16-pfifo r1: D > A+C > Y > root > D > C > Y > C > X > A > B > A+C > B > X
- C9-hdepth-tree16-pfifo r2: B > none > root > Y > D > A+C > B > A+C > A > D > A > Y > D > B

## Q2b. Time to first membership: own-leaf events, all events, seconds (median over clients; n members)

ECG: first close as a member; own-leaf events = ECG events during a stimulus whose cell names the client's leaf. h3: replay4 first_member (took_part = events the client took part in).

| cell | ECG own-leaf events r1 / r2 | ECG member events (ECG count) r1 / r2 | ECG seconds r1 / r2 | h3 own-leaf events r1 / r2 | h3 events took part r1 / r2 | h3 seconds r1 / r2 | h3 first memberships wrong r1 / r2 |
|---|---|---|---|---|---|---|---|
| C13-llong-s030-codel | 3.0 / 1.0 | 4.5 / 2.0 | 206.7 / 48.7 | 1.5 / 1.5 | 1.5 / 2.5 | 101.0 / 82.2 | 0/8 / 0/8 |
| C13-llong-s030-pfifo | 3.0 / 1.0 | 6.0 / 2.0 | 312.4 / 48.6 | 3.0 / 2.0 | 4.0 / 3.0 | 206.8 / 103.5 | 0/8 / 1/8 |
| C7-hhier-s030-codel | 2.5 / 2.5 | 4.0 / 2.0 | 86.9 / 53.0 | 2.0 / 2.0 | 3.0 / 2.5 | 58.5 / 49.9 | 0/8 / 0/8 |
| C7-hhier-s030-fq_codel | 4.0 / 6.0 | 4.0 / 6.0 | 144.0 / 121.0 | 18.5 / 16.0 | 23.5 / 26.0 | 243.4 / 195.9 | 8/8 / 6/8 |
| C7-hhier-s030-pfifo | 3.0 / 2.5 | 4.0 / 2.0 | 86.9 / 53.0 | 2.0 / 2.0 | 2.5 / 2.5 | 33.9 / 49.9 | 0/8 / 0/8 |
| C7-hhier-s030-pie | 4.5 / 2.5 | 6.0 / 2.0 | 139.8 / 53.0 | 2.0 / 2.0 | 3.0 / 2.5 | 17.0 / 50.2 | 0/8 / 0/8 |
| C9-hdepth-tree16-codel | 2.0 / 1.5 | 5.0 / 4.0 | 189.2 / 146.7 | 1.0 / 0.0 | 3.0 / 2.0 | 64.0 / 39.2 | 9/16 / 15/16 |
| C9-hdepth-tree16-fq_codel | 6.0 / 0.5 | 4.5 / 2.5 | 275.9 / 64.5 | 6.0 / 1.0 | 11.0 / 5.5 | 269.3 / 115.7 | 10/13 / 9/12 |
| C9-hdepth-tree16-pfifo | 2.5 / 1.0 | 3.0 / 2.0 | 150.2 / 62.6 | 2.5 / 0.0 | 5.0 / 2.0 | 72.9 / 39.3 | 8/16 / 15/16 |

## Q2c. Groups: born mixed (members of > 1 leaf at birth), separated later, never separated

| cell | h3 groups r1 / r2 | h3 born mixed | h3 mixed separated (median events) | h3 mixed never separated | h3 first group: stimulus, mixed r1 ; r2 | ECG nodes | ECG born mixed | ECG separated (median closes) | ECG first node: stimulus, mixed r1 ; r2 |
|---|---|---|---|---|---|---|---|---|---|
| C13-llong-s030-codel | 10 / 3 | 3 / 2 | 1.5 (2) / 1.0 (2) | 1 / 0 | b, mixed ; up, mixed | 2 / 1 | 0 / 0 | - (0) / - (0) | b, pure ; b, pure |
| C13-llong-s030-pfifo | 4 / 5 | 3 / 2 | 3.0 (1) / 1.0 (2) | 2 / 0 | b, mixed ; up, mixed | 2 / 1 | 0 / 0 | - (0) / - (0) | b, pure ; b, pure |
| C7-hhier-s030-codel | 21 / 20 | 2 / 2 | 1.0 (1) / 1.0 (2) | 1 / 0 | a+b@2, mixed ; b, mixed | 2 / 2 | 0 / 0 | - (0) / - (0) | a, pure ; b, pure |
| C7-hhier-s030-fq_codel | 10 / 6 | 5 / 2 | - (0) / - (0) | 5 / 2 | a, mixed ; b, mixed | 7 / 7 | 2 / 3 | - (0) / 13.0 (3) | a, pure ; b, pure |
| C7-hhier-s030-pfifo | 14 / 12 | 2 / 4 | 1.0 (1) / 1.0 (2) | 1 / 2 | a+b@2, mixed ; b, mixed | 3 / 2 | 0 / 0 | - (0) / - (0) | a, pure ; b, pure |
| C7-hhier-s030-pie | 17 / 7 | 2 / 1 | 1.0 (1) / 1.0 (1) | 1 / 0 | a+b@2, mixed ; b, mixed | 2 / 2 | 0 / 0 | - (0) / - (0) | a, pure ; b, pure |
| C9-hdepth-tree16-codel | 33 / 23 | 17 / 18 | 3.5 (6) / 5.0 (7) | 11 / 11 | D, mixed ; B, mixed | 5 / 3 | 0 / 1 | - (0) / 4.0 (1) | C, pure ; Y, mixed |
| C9-hdepth-tree16-fq_codel | 13 / 11 | 11 / 11 | - (0) / - (0) | 11 / 11 | A+C, mixed ; none, mixed | 4 / 5 | 2 / 3 | 32.0 (2) / 23.0 (3) | root, pure ; root, mixed |
| C9-hdepth-tree16-pfifo | 30 / 31 | 22 / 20 | 2.0 (9) / 2.0 (5) | 13 / 15 | D, mixed ; B, mixed | 5 / 3 | 0 / 1 | - (0) / - (0) | Y, pure ; root, pure |

## Q2d. h3 replayed offline with the other rep's stimulus order (same events, permuted)

| cell | variant | last P / R / cov | per-close P (pooled) | groups (born mixed) | first membership event p50 | first memberships wrong | first ten stimulus cells |
|---|---|---|---|---|---|---|---|
| C13-llong-s030-codel | rep1 as recorded | 0.60 / 0.50 / 0.78 | 0.62 | 10 (3) | 3.0 | 0/8 | b > b > b > b > a > up > up > a > up > a |
| C13-llong-s030-codel | rep1 events, rep2 order | 0.80 / 0.67 / 0.78 | 0.64 | 4 (1) | 3.0 | 0/8 | up > b > a > b > a > up > up > up > a > b |
| C13-llong-s030-codel | rep2 as recorded | 1.00 / 1.00 / 0.78 | 0.94 | 3 (2) | 3.0 | 0/8 | up > b > a > b > a > up > up > up > a > b |
| C13-llong-s030-codel | rep2 events, rep1 order | 1.00 / 0.43 / 0.42 | 0.70 | 7 (1) | 3.0 | 0/8 | b > b > b > b > a > up > up > a > up > a |
| C13-llong-s030-pfifo | rep1 as recorded | 0.50 / 1.00 / 0.78 | 0.88 | 4 (3) | 7.0 | 0/8 | b > b > b > b > b > a > up > up > a > up |
| C13-llong-s030-pfifo | rep1 events, rep2 order | 1.00 / 1.00 / 0.78 | 0.83 | 8 (3) | 6.5 | 2/8 | up > b > a > b > a > up > up > up > a > b |
| C13-llong-s030-pfifo | rep2 as recorded | 1.00 / 1.00 / 0.58 | 0.86 | 5 (2) | 3.5 | 1/8 | up > b > a > b > a > up > up > up > a > b |
| C13-llong-s030-pfifo | rep2 events, rep1 order | 0.42 / 0.67 / 0.78 | 0.77 | 6 (3) | 4.0 | 0/8 | b > b > b > b > a > up > up > a > up > a |
| C7-hhier-s030-codel | rep1 as recorded | 0.58 / 0.92 / 0.78 | 0.84 | 21 (2) | 3.0 | 0/8 | a+b@2 > a+b@2 > a > a+up > a+b > b > up > up > a+b@2 > a+b@2 |
| C7-hhier-s030-codel | rep1 events, rep2 order | 1.00 / 1.00 / 0.78 | 0.88 | 9 (2) | 2.5 | 0/8 | b > b > a+b@0.5 > a+b@0.5 > a+b@2 > a+b@2 > a+b@2 > a+b@2 > b > up |
| C7-hhier-s030-codel | rep2 as recorded | 1.00 / 1.00 / 0.78 | 0.93 | 20 (2) | 2.5 | 0/8 | b > b > a+b@0.5 > a+b@0.5 > a+b@2 > a+b@2 > a+b@2 > a+b@2 > b > up |
| C7-hhier-s030-codel | rep2 events, rep1 order | 1.00 / 1.00 / 0.78 | 0.97 | 13 (1) | 3.0 | 0/8 | a+b@2 > a+b@2 > a > a+up > a+b > b > up > up > a+b@2 > a+b@2 |
| C7-hhier-s030-fq_codel | rep1 as recorded | 0.00 / 0.00 / 0.78 | 0.02 | 10 (5) | 31.0 | 8/8 | a+b@2 > a+b@2 > a+b@2 > a > a > a > a > a > a+up > a+up |
| C7-hhier-s030-fq_codel | rep1 events, rep2 order | 0.00 / 0.00 / 0.78 | 0.03 | 10 (6) | 34.5 | 6/8 | b > b > b > b > a+b@0.5 > a+b@0.5 > a+b@0.5 > a+b@0.5 > a+b@0.5 > a+b@0.5 |
| C7-hhier-s030-fq_codel | rep2 as recorded | 0.00 / 0.00 / 0.78 | 0.04 | 6 (2) | 33.0 | 6/8 | b > b > b > b > a+b@0.5 > a+b@0.5 > a+b@0.5 > a+b@0.5 > a+b@0.5 > a+b@0.5 |
| C7-hhier-s030-fq_codel | rep2 events, rep1 order | 0.00 / 0.00 / 0.78 | 0.00 | 6 (4) | 49.0 | 6/8 | a+b@2 > a+b@2 > a+b@2 > a > a > a > a > a > a+up > a+up |
| C7-hhier-s030-pfifo | rep1 as recorded | 0.77 / 0.83 / 0.78 | 0.94 | 14 (2) | 3.0 | 0/8 | a+b@2 > a+b@2 > a+b@2 > a > a+up > a+b > b > up > a+b@2 > a+b@2 |
| C7-hhier-s030-pfifo | rep1 events, rep2 order | 0.62 / 0.83 / 0.78 | 0.91 | 12 (1) | 2.5 | 0/8 | b > b > a+b@0.5 > a+b@0.5 > a+b@2 > a+b@2 > a+b@2 > a+b@2 > a+b@2 > b |
| C7-hhier-s030-pfifo | rep2 as recorded | 1.00 / 1.00 / 0.78 | 0.89 | 12 (4) | 2.5 | 0/8 | b > b > a+b@0.5 > a+b@0.5 > a+b@2 > a+b@2 > a+b@2 > a+b@2 > a+b@2 > b |
| C7-hhier-s030-pfifo | rep2 events, rep1 order | 1.00 / 1.00 / 0.78 | 0.91 | 9 (1) | 3.5 | 0/8 | a+b@2 > a+b@2 > a+b@2 > a > a+up > a+b > b > up > a+b@2 > a+b@2 |
| C7-hhier-s030-pie | rep1 as recorded | 1.00 / 0.67 / 0.78 | 0.96 | 17 (2) | 3.0 | 0/8 | a+b@2 > a+b@2 > a+b@2 > a+b@2 > a > a+up > a+up > a+b > b > b |
| C7-hhier-s030-pie | rep1 events, rep2 order | 1.00 / 0.67 / 0.78 | 0.95 | 23 (2) | 2.5 | 0/8 | b > b > a+b@0.5 > a+b@0.5 > none > a+b@2 > a+b@2 > a+b@2 > a+b@2 > b |
| C7-hhier-s030-pie | rep2 as recorded | 1.00 / 1.00 / 0.78 | 0.90 | 7 (1) | 3.0 | 0/8 | b > b > a+b@0.5 > a+b@0.5 > none > a+b@2 > a+b@2 > a+b@2 > a+b@2 > b |
| C7-hhier-s030-pie | rep2 events, rep1 order | 0.75 / 1.00 / 0.78 | 0.94 | 8 (2) | 4.0 | 0/8 | a+b@2 > a+b@2 > a+b@2 > a+b@2 > a > a+up > a+up > a+b > b > b |
| C9-hdepth-tree16-codel | rep1 as recorded | 0.37 / 0.61 / 0.67 | 0.45 | 33 (17) | 4.0 | 9/16 | D > A+C > Y > root > root > D > C > Y > C > X |
| C9-hdepth-tree16-codel | rep1 events, rep2 order | 0.21 / 0.62 / 0.49 | 0.36 | 24 (19) | 6.5 | 7/16 | B > root > root > Y > Y > D > A+C > B > A+C > A |
| C9-hdepth-tree16-codel | rep2 as recorded | 0.27 / 0.87 / 0.57 | 0.39 | 23 (18) | 3.0 | 15/16 | B > none > root > root > Y > Y > D > A+C > B > A+C |
| C9-hdepth-tree16-codel | rep2 events, rep1 order | 0.39 / 0.67 / 0.67 | 0.41 | 20 (17) | 5.5 | 7/16 | D > A+C > Y > root > root > D > C > Y > C > X |
| C9-hdepth-tree16-fq_codel | rep1 as recorded | 0.12 / 0.60 / 0.57 | 0.20 | 13 (11) | 25.0 | 10/13 | D > A+C > A+C > A+C > A+C > A+C > Y > Y > root > D |
| C9-hdepth-tree16-fq_codel | rep1 events, rep2 order | 0.07 / 0.20 / 0.49 | 0.15 | 17 (16) | 11.0 | 9/12 | B > none > root > root > root > root > Y > Y > D > D |
| C9-hdepth-tree16-fq_codel | rep2 as recorded | 0.16 / 0.80 / 0.49 | 0.15 | 11 (11) | 11.0 | 9/12 | B > none > root > root > root > root > Y > Y > D > D |
| C9-hdepth-tree16-fq_codel | rep2 events, rep1 order | 0.08 / 1.00 / 0.21 | 0.10 | 10 (10) | 20.0 | 10/12 | D > A+C > A+C > A+C > A+C > A+C > Y > Y > root > D |
| C9-hdepth-tree16-pfifo | rep1 as recorded | 0.28 / 1.00 / 0.88 | 0.33 | 30 (22) | 6.5 | 8/16 | D > A+C > A+C > A+C > A+C > Y > root > D > C > Y |
| C9-hdepth-tree16-pfifo | rep1 events, rep2 order | 0.44 / 0.76 / 0.77 | 0.40 | 31 (16) | 5.5 | 8/16 | B > root > root > Y > Y > Y > Y > D > A+C > B |
| C9-hdepth-tree16-pfifo | rep2 as recorded | 0.24 / 0.75 / 0.57 | 0.38 | 31 (20) | 3.0 | 15/16 | B > none > root > root > Y > Y > Y > Y > D > A+C |
| C9-hdepth-tree16-pfifo | rep2 events, rep1 order | 0.40 / 0.58 / 0.88 | 0.37 | 29 (16) | 5.5 | 6/16 | D > A+C > A+C > A+C > A+C > Y > root > D > C > Y |

## Q3. C13 L-LONG

### C13-llong-s030-codel r1: ECG final P / R / cov 1.00 / 1.00 / 0.58; h3 last 0.60 / 0.50 / 0.78

ECG final groups (node: members by leaf; born at close, stimulus; membership by close where it changed):

- node 2 right {'a': 4}; born #9 t312.4 (a); #9 t312.4 a: {'a': 4}
- node 1 right {'b': 3}; born #2 t59.7 (b); #2 t59.7 b: {'b': 3} → #3 t101.0 b: {'b': 4} → #4 t121.8 a: {'b': 3}

h3 groups at the last close:

- group 5 WRONG {'b': 2, 'a': 1}; born #8 (split, parent 0, up) with {'a': 1, 'b': 2}; #8 t291.6 up: {'b': 2} → #11 t353.3 b: {'b': 3} → #12 t373.5 up: {'b': 2, 'a': 1}
- group 7 right {'b': 3}; born #9 (single group, parent None, a) with {'b': 4}; #11 t353.3 b: {'b': 2} → #12 t373.5 up: {'b': 3}
- group 8 WRONG {'a': 2, 'b': 1}; born #10 (split, parent 2, a) with {'a': 2}; #10 t333.1 a: {'a': 1} → #12 t373.5 up: {'a': 2, 'b': 1}
- group 9 right {'a': 2}; born #10 (split, parent 2, a) with {'a': 2}; #10 t333.1 a: {'a': 2}

Stimulus windows:

| start | d s | cell | ECG events | onsets per expected client | onsets of other clients | ECG events with both leaves | event sizes |
|---|---|---|---|---|---|---|---|
| 15.0 | 30 | b | 2 | 1.0 | 0 | 0 | [3, 1] |
| 59.7 | 30 | b | 1 | 1.0 | 0 | 0 | [4] |
| 100.9 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 121.7 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 163.0 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 206.7 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 251.4 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 291.5 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |
| 312.4 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 333.0 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 353.2 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 373.5 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |

Undecided clients at the end (ECG): b4 (leaf b, L 4.25, node 1, onsets 8, events 8, membership events 3)

### C13-llong-s030-codel r2: ECG final P / R / cov 0.43 / 1.00 / 0.78; h3 last 1.00 / 1.00 / 0.78

ECG final groups (node: members by leaf; born at close, stimulus; membership by close where it changed):

- node 1 WRONG {'a': 4, 'b': 4}; born #1 t36.7 (b); #1 t36.7 b: {'b': 4} → #2 t60.6 a: {'a': 4} → #3 t82.2 b: {'b': 4} → #4 t124.9 a: {'a': 4, 'b': 4}

h3 groups at the last close:

- group 0 right {'b': 4}; born #0 (single group, parent None, up) with {'a': 4, 'b': 4}; #3 t82.2 b: {'b': 4} → #5 t164.9 up: {'b': 3, 'a': 1} → #6 t205.9 up: {'b': 3} → #7 t227.5 up: {'b': 3, 'a': 1} → #8 t271.6 a: {'b': 3} → #11 t359.4 b: {'b': 4}
- group 2 right {'a': 4}; born #9 (single group, parent None, b) with {'a': 2}; #10 t338.5 a: {'a': 4}

Stimulus windows:

| start | d s | cell | ECG events | onsets per expected client | onsets of other clients | ECG events with both leaves | event sizes |
|---|---|---|---|---|---|---|---|
| 15.0 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |
| 36.6 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 60.5 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 82.2 | 30 | b | 1 | 1.0 | 0 | 0 | [4] |
| 124.8 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 164.8 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 205.8 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |
| 227.4 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 271.6 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 315.2 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 338.4 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 359.3 | 30 | b | 1 | 1.0 | 0 | 0 | [4] |

### C13-llong-s030-pfifo r1: ECG final P / R / cov 1.00 / 1.00 / 0.58; h3 last 0.50 / 1.00 / 0.78

ECG final groups (node: members by leaf; born at close, stimulus; membership by close where it changed):

- node 2 right {'a': 4}; born #10 t312.4 (a); #10 t312.4 a: {'a': 4}
- node 1 right {'b': 3}; born #2 t59.7 (b); #2 t59.7 b: {'b': 3}

h3 groups at the last close:

- group 0 WRONG {'b': 4, 'a': 3}; born #0 (single group, parent None, b) with {'a': 4, 'b': 4}; #3 t101.0 b: {'b': 2} → #4 t101.2 b: {'b': 3} → #7 t206.8 up: {'b': 4} → #13 t373.5 up: {'b': 4, 'a': 3}
- group 3 right {'a': 4}; born #4 (single group, parent None, b) with {'a': 4}; #7 t206.8 up: {'a': 3} → #8 t251.6 a: {'a': 4}

Stimulus windows:

| start | d s | cell | ECG events | onsets per expected client | onsets of other clients | ECG events with both leaves | event sizes |
|---|---|---|---|---|---|---|---|
| 15.0 | 30 | b | 2 | 1.0 | 0 | 0 | [3, 1] |
| 59.7 | 30 | b | 1 | 1.0 | 0 | 0 | [4] |
| 100.9 | 10 | b | 2 | 1.0 | 0 | 0 | [3, 1] |
| 121.7 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 163.0 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 206.7 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 251.4 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 291.5 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |
| 312.4 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 333.0 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 353.2 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 373.5 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |

Undecided clients at the end (ECG): b3 (leaf b, L 0, node None, onsets 8, events 8, membership events None)

### C13-llong-s030-pfifo r2: ECG final P / R / cov 0.43 / 1.00 / 0.78; h3 last 1.00 / 1.00 / 0.58

ECG final groups (node: members by leaf; born at close, stimulus; membership by close where it changed):

- node 1 WRONG {'a': 4, 'b': 4}; born #1 t36.7 (b); #1 t36.7 b: {'b': 4} → #2 t60.5 a: {'a': 4} → #3 t82.2 b: {'b': 4} → #4 t124.9 a: {'a': 4, 'b': 4}

h3 groups at the last close:

- group 1 right {'a': 3}; born #1 (single group, parent None, b) with {'a': 4, 'b': 2}; #3 t82.2 b: {'a': 1} → #4 t124.9 a: {'a': 3} → #5 t164.9 up: {'a': 2} → #7 t227.5 up: {'a': 3}
- group 3 right {'b': 4}; born #6 (split, parent 0, up) with {'b': 3}; #6 t205.9 up: {'b': 3} → #7 t227.5 up: {'b': 3, 'a': 1} → #8 t271.6 a: {'b': 3} → #11 t359.4 b: {'b': 4}

Stimulus windows:

| start | d s | cell | ECG events | onsets per expected client | onsets of other clients | ECG events with both leaves | event sizes |
|---|---|---|---|---|---|---|---|
| 15.0 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |
| 36.6 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 60.5 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 82.2 | 30 | b | 1 | 1.0 | 0 | 0 | [4] |
| 124.8 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 164.8 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 205.8 | 10 | up | 1 | 1.0 | 0 | 1 | [8] |
| 227.4 | 30 | up | 1 | 1.0 | 0 | 1 | [8] |
| 271.6 | 30 | a | 1 | 1.0 | 0 | 0 | [4] |
| 315.2 | 10 | b | 1 | 1.0 | 0 | 0 | [4] |
| 338.4 | 10 | a | 1 | 1.0 | 0 | 0 | [4] |
| 359.3 | 30 | b | 1 | 1.0 | 0 | 0 | [4] |

## Q4. fq_codel under the per-flow truth

Part 4 scored these rows against the static same-leaf truth (ECG pairwise: same_access(truth_leaf); h3: pairs_leaf; strict per-event: gt1 = the egress's summed backlog). Per-flow truth here: per ECG event, the clients behind the stimulated egress whose own sub-queue has a queue-log episode (gt1 CoDel rule) overlapping [t0 - 1, t0 + 2]; a pair is the same when co-constrained in >= half of the events in which either was constrained (M); never-constrained clients are correct when left out (their pairs count only if grouped). Rep 1 / rep 2.

| cell | clients ever constrained | ECG P / R / cov same-leaf | ECG P / R / cov per-flow | h3 P / R / cov same-leaf | h3 P / R / cov per-flow | ECG memberships: wrong same-leaf / per-flow | h3 memberships: wrong same-leaf / per-flow |
|---|---|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | 5 of 8 / 8 of 8 | 0.40 / 1.00 / 0.28 ; 0.60 / 0.43 / 0.58 | 1.00 / 1.00 / 1.00 ; 0.60 / 0.43 / 0.75 | 0.25 / 0.25 / 0.28 ; 0.00 / 0.00 / 0.78 | 1.00 / 0.40 / 1.00 ; 0.75 / 0.33 / 1.00 | 11: 7 / 1 ; 15: 3 / 2 | 11: 4 / 5 ; 17: 11 / 4 |
| C12-amixed-access-fq_codel | 4 of 4 / 4 of 4 | 1.00 / 1.00 / 0.60 ; 1.00 / 1.00 / 0.30 | 0.50 / 1.00 / 1.00 ; 1.00 / 1.00 / 0.50 | - / - / 0.00 ; 1.00 / 1.00 / 0.10 | - / - / 0.00 ; 1.00 / 1.00 / 0.17 | 8: 0 / 3 ; 4: 1 / 1 | 0: 0 / 0 ; 2: 0 / 1 |
| C7-hhier-s030-fq_codel | 8 of 8 / 6 of 8 | 1.00 / 0.50 / 0.42 ; 1.00 / 0.50 / 0.28 | 1.00 / 0.17 / 0.54 ; 1.00 / 0.33 / 0.67 | 0.00 / 0.00 / 0.78 ; 0.00 / 0.00 / 0.78 | 0.75 / 0.43 / 1.00 ; 0.25 / 0.33 / 1.00 | 22: 9 / 9 ; 29: 13 / 12 | 19: 18 / 12 ; 13: 10 / 10 |
| C9-hdepth-tree16-fq_codel | 14 of 16 / 12 of 16 | 0.00 / 0.00 / 0.26 ; 0.09 / 0.50 / 0.26 | 0.00 / - / 0.40 ; 0.27 / 1.00 / 0.55 | 0.12 / 0.60 / 0.57 ; 0.16 / 0.80 / 0.49 | 0.00 / - / 0.86 ; 0.16 / 1.00 / 1.00 | 36: 20 / 36 ; 46: 29 / 37 | 46: 34 / 46 ; 51: 41 / 41 |

Per event: clients behind the stimulated egress that were constrained (generous / strict >= half), and ECG members that were constrained. Medians over the events with a stimulus; share of events by count constrained.

| cell | rep | events | behind | constrained p50 (strict p50) | events with 0 / 1 / 2 / 3 / all constrained | ECG members p50 | members constrained share |
|---|---|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | 1 | 118 | 8 | 5.0 (2.0) | 0 / 1 / 40 / 77 / 0 | 1.0 | 0.91 |
| C10-hindep-s030-fq_codel | 2 | 107 | 8 | 4.0 (2.0) | 0 / 0 / 30 / 75 / 2 | 1.0 | 0.84 |
| C12-amixed-access-fq_codel | 1 | 31 | 4 | 3.0 (1.0) | 0 / 0 / 2 / 16 / 13 | 1.0 | 0.87 |
| C12-amixed-access-fq_codel | 2 | 30 | 4 | 3.0 (1.0) | 0 / 0 / 0 / 18 / 12 | 1.0 | 0.88 |
| C7-hhier-s030-fq_codel | 1 | 132 | 8 | 4.0 (2.0) | 1 / 2 / 40 / 86 / 3 | 1.5 | 0.75 |
| C7-hhier-s030-fq_codel | 2 | 139 | 8 | 4.0 (2.0) | 0 / 1 / 44 / 94 / 0 | 1.0 | 0.74 |
| C9-hdepth-tree16-fq_codel | 1 | 100 | 8 | 2.0 (1.0) | 0 / 33 / 27 / 40 / 0 | 1.0 | 0.64 |
| C9-hdepth-tree16-fq_codel | 2 | 99 | 4 | 2.0 (1.0) | 1 / 35 / 31 / 32 / 0 | 1.0 | 0.60 |

By stimulus cell (all reps): median constrained / behind

| cell | stimulus | events r1 / r2 | constrained / behind p50 r1 / r2 |
|---|---|---|---|
| C10-hindep-s030-fq_codel | a | 28 / 26 | 2.0 / 4 ; 3.0 / 4 |
| C10-hindep-s030-fq_codel | b | 55 / 43 | 3.0 / 4 ; 4.0 / 8 |
| C10-hindep-s030-fq_codel | up | 35 / 38 | 5.0 / 8 ; 4.0 / 8 |
| C12-amixed-access-fq_codel | private | 12 / 12 | 1.0 / 1 ; 1.0 / 1 |
| C12-amixed-access-fq_codel | shared | 19 / 18 | 3.0 / 4 ; 3.0 / 4 |
| C7-hhier-s030-fq_codel | a | 21 / 15 | 2.0 / 4 ; 2.0 / 4 |
| C7-hhier-s030-fq_codel | a+b | 14 / 12 | 4.0 / 8 ; 4.0 / 8 |
| C7-hhier-s030-fq_codel | a+b@0.5 | 16 / 26 | 4.0 / 8 ; 4.0 / 8 |
| C7-hhier-s030-fq_codel | a+b@2 | 26 / 29 | 4.0 / 4 ; 4.0 / 4 |
| C7-hhier-s030-fq_codel | a+up | 15 / 15 | 4.0 / 8 ; 4.0 / 8 |
| C7-hhier-s030-fq_codel | b | 16 / 16 | 2.0 / 4 ; 2.0 / 4 |
| C7-hhier-s030-fq_codel | up | 24 / 26 | 4.0 / 8 ; 4.0 / 8 |
| C9-hdepth-tree16-fq_codel | A | 11 / 11 | 1.0 / 4 ; 1.0 / 4 |
| C9-hdepth-tree16-fq_codel | A+C | 18 / 12 | 2.0 / 8 ; 2.0 / 8 |
| C9-hdepth-tree16-fq_codel | B | 7 / 10 | 1.0 / 4 ; 1.0 / 4 |
| C9-hdepth-tree16-fq_codel | C | 10 / 10 | 1.0 / 4 ; 1.0 / 4 |
| C9-hdepth-tree16-fq_codel | D | 13 / 12 | 1.0 / 4 ; 1.0 / 4 |
| C9-hdepth-tree16-fq_codel | X | 12 / 14 | 2.0 / 8 ; 2.0 / 8 |
| C9-hdepth-tree16-fq_codel | Y | 14 / 14 | 3.0 / 8 ; 2.0 / 8 |
| C9-hdepth-tree16-fq_codel | root | 15 / 16 | 4.0 / 16 ; 5.0 / 16 |

