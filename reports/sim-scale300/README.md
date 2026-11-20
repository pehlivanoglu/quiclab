# Item 5: 300-client test (2026-11-19)

One run, started by the user (tmux, batch_guard, nice 19, one core; no campaign running). Job:
`simulation/runs/joblogs/scale300.sh`; raw numbers: `timings.txt`, `sizes.txt`, `spread-stimuli.json`.

Cell: G1-type from the v4 planner (`simlab/gen_plan.py`, scripts/v4_suite.plan_run unchanged): one shaped leaf with
300 clients at 500 kb/s plus sub-ctrl, S-BURST stimuli (18 surges), DEF point, pfifo, seed 1, ack-matched, 335 s.
Build: quicsim `84f298fb962ba77d`, libns3 internet `21eecfc6eeaf93bd` (= B2), item-5 code (byte regression on two B2
runs passed, `../sim-stageB2-applimited/regress-item5.md`).

## 1. Validity

| item | value |
|---|---|
| completed | yes, all steps exit 0 |
| late arrivals (E-horizon 10 s) | **0** |
| files open at exit | 0 |
| GT-Q health | ok; lost 0; identity ok; match min 1.0 |
| events | 18 stimuli, all 300 members expected; 5,389 of 5,400 member-onsets found (11 missed) |

## 2. Time and memory per step (measured, one core)

| step | wall | peak RSS | note |
|---|---|---|---|
| plan (gen_plan + plan.py) | 0.2 s | 35 MB | |
| quicsim (simulation itself) | **475 s** (1.42 s per simulated s) | **520 MB** | bounded: 256 MiB pool + state; 366 MB at 25 clients |
| post-processing in run.py (frozen `quiclab.router_trace.health` + qdiscs) | **557 s** | **8.96 GB** | reads the whole 2.9 GB router trace into memory |
| frozen detector (v2-owd, builds tick cache) | **184 s** | 1.41 GB | |
| frozen SETS k = 2 / 3 (on cached detector onsets, grouping_score) | **200 s** | 2.29 GB | |
| GT1 | ~1 s | (in truth step) | from file times |
| GT3 | 145 s | (in truth step) | from file times |
| GT-Q / GT-H | **1,345 s** | (in truth step) | from file times |
| truth step total (GT1 + GT3 + GT-Q, detector re-read from cache) | 1,529 s | **11.0 GB** | peak is the step's maximum; attributed to GT-Q (whole trace in memory), not separately measured |
| **end to end** | **49 min** (11:26:57 - 12:16:18) | max 11.0 GB | |

The simulation is bounded; **the frozen trace tools are not** (health 9.0 GB, truth 11.0 GB at 300 clients; both read
the full router trace).

## 3. Disk per run (measured)

| part | raw | zstd -3 (measured as a stream, nothing written) |
|---|---|---|
| run folder total | **5.23 GB** (52.1 kB per client-second) | **0.916 GB** (9.1 kB per client-s; ratio 5.7) |
| of which router-trace | 2.91 GB | 0.394 GB |
| of which publishers (per-subscriber sender logs) | 1.96 GB | 0.446 GB |
| of which clients | 0.23 GB | 0.067 GB |
| of which truth | 0.12 GB | 0.008 GB |
| tick cache (`reports/sim-cache/scale300`) | **1.25 GB** (12.4 kB per client-s) | **0.406 GB** (4.0 kB per client-s) |

Free disk: 231 GB before, 225 GB after.

## 4. Onset spread by leaf size, and onsets outside 0.5 s after the first onset

Same definitions as `../sim-stageB2-applimited/spread-by-leaf.md` (first frozen v2-owd onset per expected member in
[start - 1 s, start + 10 s]; late = onset > first onset + 0.5 s). Listing only, no criterion. One leaf size here.

| leaf size | side | stimuli | p50 | p90 | p98 | max ms | stimuli > 0.5 s | late onsets / onsets found | share outside 0.5 s | missed members |
|---|---|---|---|---|---|---|---|---|---|---|
| 300 | sim | 18 | **280** | **558** | 801 | 891 | 3 / 18 | 16 / 5,389 | **0.30 %** | 11 |

Context (from the B2 listing): testbed p50 / p90 66 / 132 ms at leaf 4, 165 / 439 ms at leaf 40; simulation 33 / 99 ms
at leaf 4, 99 / 379 ms at leaf 24. Spread keeps growing with leaf size; the share of late onsets stays small.
Per-stimulus spreads: 33, 33, 33, 33, 66, 132, 132, 198, 231, 330, 330, 363, 363, 429, 495, 528, 627, 891 ms.
In the 3 stimuli over 0.5 s, 0.3 %, 3 % and 2 % of the members are late (lateness p50 594 ms, max 891 ms).
Late by access delay: 5 ms 0 / 1,350, 7.5 ms 3 / 1,350, 12.5 ms 8 / 1,350, 20 ms 5 / 1,350 (all clients 500 kb/s).
No repeat offender (one client late twice, the rest once).

## 5. SETS at 300 (reported, not a criterion; not yet examined)

| | 300 clients (this run) | 24 clients (B2, same cell type) |
|---|---|---|
| pair precision / recall (k = 2) | 1.00 / 0.996 | 1.00 / 0.98 |
| leaf F1, mean over closes (k = 2 and k = 3) | **0.50** | 0.97 / 0.93 |
| leaf group with F1 >= 0.9 reached after | **19 events of the leaf, 139 s** | 2 events, 41 s |

Leaf F1 0.50 is exact: in 20 of 40 closes no group exists at all; in the other 20 the group equals the leaf. Pair
precision / recall are high because they count only the closes where groups exist. At 300 members SETS needs about
19 stimuli before it forms the leaf group, against 2 at 24 members. The cause is not examined yet. A likely
mechanism, not checked: with 300 members a near-identical member set has to repeat k times, and missed or late
members make that rarer. This bears directly on "grouping at scale" (the stage C use) and should be understood
before stage C.

## 6. Extrapolation to 1,000 and 10,000 clients (same cell, 335 s)

Measured columns and extrapolated columns are separate. The 100-client column is the earlier smoke run on the
**pre-item-5 build** (global routing, 1 MB buffer per file, spec ACK): only its wall and size are comparable.

| quantity | measured 25 | measured 100 (old build) | **measured 300** | extrapolated 1,000 | extrapolated 10,000 | rule |
|---|---|---|---|---|---|---|
| quicsim wall | 21.7 s | 164 s | **475 s** | 26 - 35 min | 4.4 - 10 h | linear from 300 (100 -> 300 was x2.9) to N^1.24 (25 -> 300) |
| wall per simulated s | 0.065 s | 0.49 s | **1.42 s** | 4.7 - 6.3 s | 47 - 110 s | as above |
| quicsim peak RSS | 366 MB | (1,279 MB, old buffers) | **520 MB** | 0.9 GB | 5.9 GB | linear 0.56 MB per client (25 -> 300) |
| raw output per run | 0.43 GB | 1.79 GB | **5.23 GB** | 17 GB | 174 GB (62 GB at 120 s) | linear per client-s (52 kB) |
| compressed output per run | - | - | **0.92 GB** | 3.1 GB | 31 GB (11 GB at 120 s) | linear (9.1 kB per client-s) |
| tick cache raw / compressed | - | 0.45 GB / - | **1.25 / 0.41 GB** | 4.2 / 1.4 GB | 42 / 14 GB | linear |
| health check (frozen) wall / RSS | - | - | **557 s / 9.0 GB** | 31 min / **30 GB** | 5.2 h / **300 GB** | linear in trace size |
| detector wall / RSS | (3.8 s, cached) | - | **184 s / 1.4 GB** | 10 min / <= 4.7 GB | 1.7 h / <= 47 GB | linear (RSS: upper bound, per-client loading not checked) |
| SETS scoring wall / RSS | 10 s | - | **200 s / 2.3 GB** | 14 min - 37 min / ? | 3.7 h - 62 h / ? | N^1.2 (25 -> 300) to N^2 (grouping_score's pair loop is O(N^2) per close) |
| GT3 wall | - | - | **145 s** | 8 min | 1.3 h | linear |
| GT-Q wall / RSS | - | - | **1,345 s / <= 11 GB** | 75 min / **37 GB** | 12.5 h / **370 GB** | linear in trace size |

**10,000 clients without the router trace (user decision 2026-11-19: no GT-Q and no per-packet router trace in that
run).** Same rules, extrapolated, with the router trace and the publishers' -pkts / -pktacks (GT-Q matching only)
left out. Per client-second that is 20.9 kB raw and 4.5 kB zstd output, plus the tick cache at 12.4 / 4.0 kB.

| quantity, 10,000 clients, no router trace | 120 s | 335 s | rule |
|---|---|---|---|
| quicsim wall | 1.6 - 3.6 h | 4.4 - 10 h | as above (the trace costs little simulation time; not measured separately) |
| quicsim peak RSS | 5.9 GB | 5.9 GB | per client, not per second |
| raw output | 25 GB | 70 GB | 20.9 kB per client-s |
| compressed output | 5.4 GB | 15 GB | 4.5 kB per client-s |
| tick cache raw / compressed | 15 / 4.8 GB | 42 / 14 GB | linear |
| health check | the lighter check only (`../sim-stageC-plan/README.md` section 5) | same | no trace to read |
| GT-Q | not run | not run | user decision |
| detector wall / RSS | 37 min / <= 17 GB | 1.7 h / <= 47 GB | linear; RSS an upper bound, unmeasured above 300 |
| SETS scoring wall / RSS | 1.3 h - 22 h / <= 27 GB | 3.7 h - 62 h / <= 76 GB | as above; **plus ~30 h for the N^2 input reading** (`sets-npr.md` section 4) |
| GT3 wall | 28 min (+ ~30 h N^2 input reading) | 1.3 h (+ ~30 h) | linear + N^2 |

At 10,000 clients the detector and SETS memory upper bounds pass 45 GB at 335 s. Whether they really grow linearly
is not known; the first measurement above 300 clients (stage C smoke runs) decides it.

What the extrapolation says (assumptions above, not measured):
- The simulator scales: memory stays far below 16 GB even at 10,000 clients, and time is linear or a little worse.
- **The frozen trace tools do not fit the memory rule (< 16 GB) at 1,000 clients:** health ~30 GB and GT-Q ~37 GB.
  SETS scoring time is at least superlinear and may be quadratic at 10,000.
- Raw output of one 10,000-client run at 335 s (174 GB) is more than the disk that is free after the emulation.

## 7. Decisions for the user (numbers above; nothing changed before the answer)

The full grid from the stage B report, section 5: 100 / 300 / 1,000 clients x 4 placements x 2 AQM x 2 seeds x
600 s = 13.4 M client-seconds. Measured rates apply: 9.1 kB per client-s compressed output, 4.0 / 12.4 kB per
client-s tick cache compressed / raw.

**D1. Where does the stage C tick cache go?**

| option | permanent under quiclab/ | outside quiclab/ | transient per running 1,000 x 600 s run |
|---|---|---|---|
| (a) compressed, inside the budget | 123 GB outputs + **54 GB** cache = **177 GB** | 0 | ~31 GB raw output + 7.4 GB raw cache before compression |
| (b) temporary folder outside quiclab/, deleted by the user | **123 GB** outputs | up to 167 GB raw cache (or 7.4 GB per run if deleted after each run's scoring) | same |

Both totals are far above the 60 GB stage C budget and above the ~130-140 GB expected to be free after K5 and the
re-runs. The grid as proposed does not fit with either option. A smaller grid, or sampled router traces and fewer
per-subscriber sender logs (router-trace and publishers are 92 % of the compressed size), belongs in the stage C
plan. The cache choice still matters there: compressed cache is about 30 % of the compressed total.

**D2. The 35,535 background-flow ceiling (10,000-client attempt).** The background planner gives one flow per
2.5 Mb/s of background. At 300 clients the largest event had 330 flows (19 events, last port 35,847 of 65,535). Linear
in clients, a 10,000-client cell of this type needs about 11,000 flows per event, so at most ~3 such events fit under
the ceiling; the S-BURST schedule here has 19. Lifting it: port blocks per source node instead of one global range.
That changes no run with <= 300 flows per event, but it changes the port labels of runs with several source nodes, so
it needs its own byte regression.

**Update 2026-11-19 (user):** D3 is closed for 10,000 clients: no GT-Q and no router trace there, and no chunked
copies. Up to 1,000 clients see `../sim-stageC-plan/README.md` section 3. Sets of numbers for D1 / D3 recomputed
there. The text below is as first written.

**D3 (new, from the measurement). The frozen trace tools above 300 clients.** Health check and GT-Q hold the whole
router trace in memory: 9.0 / 11.0 GB at 300, ~30 / ~37 GB at 1,000 by extrapolation, above the 16 GB rule. These are
frozen files; this session does not change them. Options:
- (i) at 1,000 clients run only detector, SETS and GT3 (all well under 16 GB by extrapolation), and no GT-Q / health;
- (ii) sampled router traces for 1,000 (GT-Q on a sample changes what GT-Q measures, so it would need a definition);
- (iii) a chunked copy of the two tools under simulation/, accepted only if byte-identical to the frozen tools on the
  B2 runs and this 300-client run.

Not used for anything: the run's onset spread and SETS numbers are a single seed of a single generated cell.

## Correction (2026-11-19): surges partly lost at the traffic source

The background / stimulus source host is on a 1 Gb/s link (the testbed's NIC). At 300 clients an S-BURST surge at
u = 1.3 offers 796 Mb/s on top of 348 Mb/s of background, so part of each such surge was dropped in the source host's
queue, before the router (light health check item 4: 676k packets lost outside the router).

- The surges at u = 1.3, and slightly those at u = 1.15, reached the bottleneck weaker than planned.
- Calm load / share (background only) was unaffected.
- The spread and SETS numbers above come from those weakened stimuli. They are a lower bound on stimulus strength,
  not the planned one.

simulation/NOTES.md, "Traffic sources limited ...".
