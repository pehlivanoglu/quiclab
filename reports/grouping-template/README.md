# Step 1: evidence in one episode's delay curve (2026-11-11)

Measurement only, read-only, development set of `.runs/2026-11-10_1946_v2`
(K1–K6, C1, M1–M6; pfifo / pie / red; N1–N5 not opened; G0 has no shared
window, so no template). Code and every definition / constant with its origin:
`scripts/grouping_template_study.py` (docstring). Files: `rows.jsonl.gz` (one row
per client × window × class × config × calm variant), `summary.md` (all
breakdowns), `overlay*.png` (2 SAME, 2 CONCURRENT, 1 NESTED, picked at the median).

    python3 scripts/grouping_template_study.py rows    .runs/2026-11-10_1946_v2 reports/grouping-template/rows.jsonl
    python3 scripts/grouping_template_study.py summary reports/grouping-template/rows.jsonl.gz > reports/grouping-template/summary.md
    python3 scripts/grouping_template_study.py plots   .runs/2026-11-10_1946_v2 reports/grouping-template/rows.jsonl.gz reports/grouping-template/

91 runs, 2362 shared windows; base config = margin 1 s, per-bin minimum OWD, calm = strict.

## Headline (nats; reference line 11.5)

| class | n | p10 / p50 / p90 | > 11.5 | other |
|---|---|---|---|---|
| SAME (own leave-one-out template) | 9341 | 4 322 / 54 993 / 5 885 818 | 0.99 | 66 at or below the line: 59 in M6 `up` windows |
| QUIET (not congested, vs template) | 3342 | −31 113 349 / −2 452 385 / −1 301 | 0.00 | all negative |
| CONCURRENT E(own) − E(other) | 198 (K1 a+b, K6 A+C) | 9 797 / 55 351 / 1 962 744 | 1.00 | < 2: 0.00; E(other) alone > 11.5: 0.98; E(other) / E(own) p50 0.05–0.20 per cell |
| NESTED (vs upstream-only template) | 539 | −45 / 1 976 / 30 187 | 0.89 | violation mean(max(0, s − q)) p50 1.40 ms, p90 19.9 ms |

NESTED by cell: K1 `a+up` (81 rows): E p10 2 057, violation p50 0.62 ms (clean
nesting). M6 `a` / `b` within `up` (458 rows, independent timing): the
"upstream-only" group (the other branch) is often in its own leaf episode at the
same time, so that template is not upstream-only; these rows carry the low tail
and the large violations (see overlay5). The same contamination explains the SAME
rows below the line in M6 `up` windows.

Sensitivity (`summary.md`, last table): SAME, QUIET and CONCURRENT shares do not
move (margin 0.5 / 2 s, per-bin mean OWD, calm "excl"); NESTED > 11.5 is 0.89 at
1 s, 0.96 at 0.5 s and 0.81 at 2 s (a wider interval takes in more of the
other branch's independent episodes).

## Definition issue: the scale of E

sigma_i (calm MAD) is 0.16 / 1.89 / 2.95 ms (p10 / p50 / p90): the emulated
paths have almost no delay noise outside congestion, while episodes reach tens
of ms over ~250 samples. E then reaches 10^4–10^7 nats, every same-group score
clears 11.5 by orders of magnitude, and so does the *wrong* template in
concurrent cells (E(other) > 11.5 in 98 %). The line does not discriminate here;
only differences between templates do. Second version (not a new definition, a
rescaling): E scales exactly with 1 / sigma^2 for a fixed residual, so with sigma
floored at a realistic per-client jitter:

| sigma floor | SAME p50, > 11.5 | QUIET p50, < 0 | CONCURRENT diff p50, > 11.5, < 2 | E(other) > 11.5 | NESTED p50, > 11.5 |
|---|---|---|---|---|---|
| none | 54 993, 0.99 | −2 452 385, 1.00 | 55 351, 1.00, 0.00 | 0.98 | 1 976, 0.89 |
| 5 ms | 6 307, 0.99 | −385, 1.00 | 7 001, 1.00, 0.00 | 0.98 | 240, 0.86 |
| 10 ms | 1 577, 0.99 | −96, 1.00 | 1 750, 0.99, 0.00 | 0.98 | 60, 0.76 |
| 20 ms | 394, 0.97 | −24, 1.00 | 438, 0.98, 0.01 | 0.95 | 15, 0.56 |

This is optimistic: real jitter would also enter the residual, which the
rescaling ignores (the 2026-11-11 noise test on correlation / level difference,
`reports/grouping-episode/`, saw fixed thresholds collapse at 10–20 ms).

## Other questions

- **Alignment:** best lag on the send-time grid is within one bin for 91 % of
  SAME rows (0 ms 42 %, ±5 ms 49 %): no alignment search needed on send time.
  On a receive-time grid only 19 % (typical ±25–35 ms): receive time adds each
  client's own one-way delay, so the send-time grid is the right one.
- **n_eff:** p10 / p50 / p90 22 / 126 / 323 (n 84 / 170 / 398; n_eff / n
  0.12 / 0.95 / 1.00). Samples per client per episode 112 / 250 / 591; 1 Mb/s
  clients 93 / 135 / 265.
- **Saturation** (template within 10 % of its maximum; median 0.08): saturated and
  unsaturated episodes score alike (CONCURRENT diff p50 58 653 vs 50 161).
- **Stimuli:** ppbp is the weakest SAME cell (p50 3 955) but still clear; tcp,
  udp and capacity drops alike.

## FLAG constants

MARGIN 1 s (sensitivity 0.5 / 2 s), N_MIN 10 samples, SAT 10 %, CONC_S 50 ms,
plus the "excl" calm variant's 1 s before / 2 s after each window. The ppbp
whole-run window is split into GT1 episodes, as the grouping truth does
(a reading of "event = shared window" for the one continuous stimulus).

# Step 1b (2026-11-11): scale-free numbers, residual sigma, noise on the curves, template size

Same development set and base configuration (margin 1 s, per-bin minimum OWD).
Code: `grouping_template_study.py rows1b / summary1b / plot1b` (definitions in the
comment block above `NOISE`). Files: `rows1b.jsonl.gz`, `summary1b.md`,
`branches-ab.png`, `branches-AC.png`.

    python3 scripts/grouping_template_study.py rows1b    .runs/2026-11-10_1946_v2 reports/grouping-template/rows1b.jsonl
    python3 scripts/grouping_template_study.py summary1b reports/grouping-template/rows1b.jsonl.gz > reports/grouping-template/summary1b.md
    python3 scripts/grouping_template_study.py plot1b    .runs/2026-11-10_1946_v2 reports/grouping-template/rows1b.jsonl.gz reports/grouping-template/

**A. Scale-free.** Explained fraction p10 / p50 / p90: SAME 0.973 / 0.996 / 0.999;
CONCURRENT own 0.992 / 0.996 / 0.998, other 0.592 / 0.853 / 0.959; NESTED K1 a+up
0.775 / 0.957 / 0.986 (M6 −0.06 / 0.35 / 0.95, contaminated, see step 1).
CONCURRENT residual ratio RMS(q − s_other) / RMS(q − s_own): 2.67 / 5.71 / 10.13,
none below 1.5, own preferred 198 / 198 (pfifo 7.4, pie 4.6, red 3.6, K6 6.7 at p50).

**B. Residual sigma (M).** sigma_res 3.9 / 5.8 / 10.4 ms (calm sigma 0.3 / 1.5 / 3.7 ms).
CONCURRENT E(own) − E(other) with it: 1 186 / 4 669 / 17 174 nats, all > 11.5.

**C. Noise on the curves** (templates rebuilt from the noisy curves):

| noise | SAME EF p50 | own preferred | ratio p10 / p50 / p90 | ratio < 1.2 | diff_res p50, > 11.5, < 2 |
|---|---|---|---|---|---|
| none | 0.996 | 1.00 | 2.67 / 5.71 / 10.13 | 0.00 | 4 669, 1.00, 0.00 |
| iid 5 ms | 0.977 | 1.00 | 1.60 / 2.80 / 5.01 | 0.00 | 2 455, 0.99, 0.01 |
| iid 10 ms | 0.928 | 0.99 | 1.23 / 1.81 / 3.01 | 0.09 | 888, 0.98, 0.01 |
| iid 20 ms | 0.759 | 0.90 | 1.00 / 1.23 / 1.79 | 0.43 | 151, 0.87, 0.11 |
| slow 5 ms | 0.979 | 0.99 | 1.66 / 2.86 / 5.60 | 0.02 | 15, 0.51, 0.48 |
| slow 10 ms | 0.934 | 0.93 | 1.09 / 1.94 / 3.58 | 0.13 | −8, 0.39, 0.55 |
| slow 20 ms | 0.781 | 0.78 | 0.88 / 1.29 / 2.36 | 0.42 | 3, 0.34, 0.50 |

"slow" = per-client Ornstein–Uhlenbeck offset, time constant 1 s (FLAG). The
residual-sigma score breaks under a slow offset even at 5 ms: the MAD is taken
around the residual's median, so a constant offset leaves sigma_res small, while
the score's sum of squares pays the offset in full against both templates; the
difference then becomes noise. The ratio (scale-free) degrades gradually.

**D. Template size** (clean, own and other built from k random clients): k = 1
ratio 2.56 / 5.36 / 9.15, own preferred 1.00; k = 2 2.61 / 5.26 / 9.93, 0.99. k = 3
is not possible here: the concurrent groups (K1 a / b, K6 A / C) have three and two
clients, so the leave-one-out own template has at most two.

**E. Why the branches differ.** The two drops start at the same instant (best lag
between the branch templates p50 0 ms; correlation 0.91; RMS difference 23 ms p50),
and both queues end at the same full level and drain together; the difference is
the fill trajectory, which follows each branch's offered load right after the drop:
keyframe phases (a 0 / 250 / 500 ms, b 125 / 375 / 625 ms in K1), the clients'
access delays (a 5 / 20 / 40 ms, b 10 / 25 / 45 ms) and their BBR cycle state, so one
branch can fill in tens of ms while the other ramps over most of a second
(`branches-ab.png`, `branches-AC.png`). Scripted equal drops therefore separate
through the transient, not through the plateau; a branch that saturates before
the other's fill starts carries little separating shape.

# Step 1c (2026-11-11): unknown-variance score, no sigma

`grouping_template_study.py rows1c / summary1c` → `rows1c.jsonl.gz`, `summary1c.md`.
CONCURRENT rows (K1 a+b on pfifo / pie / red, K6 A+C on pfifo; 198 per noise
condition). L = n_eff × ln(RMS(r_other) / RMS(r_own)); each residual centred by its
own median over the scored bins (the analysis interval, window ± 1 s, where q_i and
both templates exist); n_eff from the autocorrelation of the centred r_own.

| noise | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p10 / p50 / p90 | centred ratio p50 |
|---|---|---|---|---|---|---|
| none | 53.8 / 140.4 / 264.1 | 0.99 | 0.00 | 1.00 | 34 / 85 / 160 | 5.41 |
| iid 5 ms | 25.7 / 78.0 / 197.2 | 0.98 | 0.00 | 1.00 | 46 / 94 / 165 | 2.61 |
| iid 10 ms | 10.7 / 40.9 / 119.7 | 0.88 | 0.02 | 0.99 | 44 / 90 / 170 | 1.67 |
| iid 20 ms | −1.1 / 14.9 / 54.9 | 0.56 | 0.17 | 0.89 | 42 / 94 / 172 | 1.20 |
| slow 5 ms | 4.0 / 13.3 / 40.2 | 0.58 | 0.01 | 1.00 | 6 / 11 / 31 | 3.08 |
| slow 10 ms | 1.1 / 5.8 / 20.6 | 0.22 | 0.18 | 0.98 | 5 / 9 / 22 | 1.98 |
| slow 20 ms | −0.8 / 2.6 / 9.3 | 0.05 | 0.43 | 0.81 | 4 / 8 / 16 | 1.37 |

Slow drift shrinks n_eff tenfold (85 → 9 at 10 ms): the residual becomes strongly
autocorrelated, so L is small although the preference stays right (0.98 at 10 ms).
White noise leaves n_eff where it is (it even rises slightly: it decorrelates the
residual). Template size (k random clients in both templates):

| noise | k = 1: L p50, > 11.5, own preferred | k = 2: L p50, > 11.5, own preferred |
|---|---|---|
| none | 48.6, 0.92, 0.99 | 92.4, 0.99, 1.00 |
| iid 10 ms | 18.2, 0.61, 0.95 | 28.3, 0.77, 0.98 |
| slow 10 ms | 4.9, 0.20, 0.97 | 5.5, 0.22, 0.96 |

(k = 1: 147 rows, K1 111, K6 36; k = 2: 162 rows, K1 only, where k = 2 is the whole
leave-one-out group.)

# Step F preparation (2026-11-11): order-keeping jitter, campaign J1 (not run yet)

**Reordering probe** (`scripts/netem_order_probe.sh`, quiclab image, kernel 7.0,
iproute2 6.17): numbered UDP packets, 2.5 Mbit/s, 10 s, through
`netem delay 20ms <J>ms distribution normal`; the receiver counts packets that
arrive after a higher sequence number.

| setup | reordered at J = 5 / 10 / 20 ms | OWD sd ms | OWD p50 ms |
|---|---|---|---|
| netem alone | 34.8 / 57.5 / 62.5 % | 5.0 / 9.8 / 17.7 | 19.7 / 20.2 / 19.8 |
| netem + pfifo child | 36.8 / 55.7 / 61.5 % | 5.1 / 9.8 / 17.4 | 20.1 / 20.0 / 19.5 |
| netem `rate 10gbit` | **0 / 0 / 0** | 4.0 / 7.1 / 12.6 | 21.4 / 25.4 / 37.8 |

The pfifo-child recipe does not keep order on this kernel (netem releases packets
from its own time-ordered queue whatever the child). A netem `rate` far above the
link does: no packet leaves before its predecessor. Cost: the delay law becomes
FIFO-like, so the realised spread is lower than the nominal sd (4 / 7 / 13 ms for
5 / 10 / 20) and time-correlated, and the median rises. The J1 runs use this
(`DirectionSpec.jitter_keep_order`). Note: the existing reverse-path jitter runs
(K3 `revjit10`, M3 `revjit5/10/20`) used plain netem, so their ACKs were reordered.

**Campaign J1** (`grouping_campaign.py`, group "study", not in the default `--ks`):
split topology, pfifo, the K1 plan (all K1 cells, a+b and a+up included), 2 reps:
`hierjit5 / 10 / 20` (forward jitter on every access link a1–b3 after the shared
bottleneck, `distribution normal`, order kept; sub-ctrl without), `hiersamephase`
(b1–b3 take a1–a3's keyframe phases 0 / 250 / 500 ms), `hierrandphase` (every
client draws its phase in [0, 1000) ms per run, seed = rep; written to
`_gen/<run>-topology.yaml`, phases in the plan json). 10 runs, 2.8 h of emulation.
Scoring after the runs: `rows1c` and the ratio (rows1b) on the J1 directory.

**J1 scoring (ready, run after the J1 runs):**

    python3 scripts/grouping_template_study.py rowsj1    .runs/2026-11-10_1946_v2 reports/grouping-template/rowsj1.jsonl && gzip reports/grouping-template/rowsj1.jsonl
    python3 scripts/grouping_template_study.py summaryj1 reports/grouping-template/rowsj1.jsonl.gz reports/grouping-template/rows1c.jsonl.gz > reports/grouping-template/summaryj1.md
    python3 scripts/grouping_template_study.py plotj1    .runs/2026-11-10_1946_v2 reports/grouping-template/rowsj1.jsonl.gz reports/grouping-template/

CONCURRENT (a+b) and NESTED (a+up; own = the leaf's leave-one-out template, other =
the upstream-only template) per variant next to the no-jitter K1 pfifo baseline
(`K1/grp-hier-pfifo-r*`) and the injected-noise rows of step 1c on the same cell;
jitter variants are labelled with the realised sd (4.0 / 7.1 / 12.6 ms) and the
measured calm OWD spread of the jittered clients; detector false alarms per minute,
alarm precision and onset spread per variant; branch-template overlays for the two
phase variants.

# J1 results (2026-11-12)

Files: `rowsj1.jsonl.gz`, `summaryj1.md`, `j1-branches-hiersamephase.png`,
`j1-branches-hierrandphase.png`. Jitter is stated as the realised sd of the
order-keeping `rate` method (probe: 4.0 / 7.1 / 12.6 ms for a nominal 5 / 10 / 20 ms).
Measured in the runs themselves, the calm OWD spread of the jittered clients (MAD
of the per-bin minimum OWD) is 5.2 / 9.3 / 16.1 ms (no jitter: 1.4 ms); it is
larger than the probe's because it also holds the path's own variation.

CONCURRENT (a+b), step 1c score L and the centred ratio, 2 reps each (the baseline is K1 pfifo r1):

| variant | n | L p50 | > 11.5 | < 2 | own preferred | n_eff p50 | ratio p50 |
|---|---|---|---|---|---|---|---|
| no jitter (K1 pfifo) | 54 | 152 | 1.00 | 0.00 | 1.00 | 82 | 6.67 |
| jitter sd 4.0 ms | 108 | 51 | 0.91 | 0.02 | 0.98 | 67 | 2.19 |
| jitter sd 7.1 ms | 108 | 32 | 0.82 | 0.05 | 0.96 | 66 | 1.77 |
| jitter sd 12.6 ms | 108 | 16 | 0.64 | 0.11 | 0.94 | 52 | 1.38 |
| same keyframe phases | 108 | 102 | 0.87 | 0.09 | 0.91 | 98 | 3.17 |
| random keyframe phases | 108 | 140 | 1.00 | 0.00 | 1.00 | 80 | 5.68 |

Real jitter degrades about like injected independent noise of the same size (step
1c on the same cell: iid 5 / 10 / 20 ms → L p50 98 / 51 / 19, own preferred 1.00 /
1.00 / 0.93), not like the slow offset (n_eff stays 52–67, not ~9). NESTED (a+up,
own = the leaf's leave-one-out template, other = the upstream-only template): L
p50 126 / 47 / 43 / 22 for no jitter / 4.0 / 7.1 / 12.6 ms, own preferred 1.00 / 0.96 /
0.91 / 0.94; same phases 143 (0.96), random phases 101 (1.00).

Phases. With identical keyframe phases the two fill transients coincide (overlay:
both templates rise together to the same plateau); the remaining separation comes
from the drain after the window and plateau fluctuations, and it is weaker
(ratio 3.2, own preferred 0.91, 9 % below 2 nats). With random phases the branches
still differ (ratio 5.7), here mostly because one branch's queue drains and
refills inside the episode while the other stays full.

Detector (v2-owd, numbers only):

| variant | runs | false alarms / min p50 | alarm precision p50 | onset spread p50 / p90 ms |
|---|---|---|---|---|
| no jitter (K1 pfifo r1) | 1 | 2.24 | 0.90 | 66 / 165 |
| jitter sd 4.0 ms | 2 | 0.73 | 0.96 | 66 / 182 |
| jitter sd 7.1 ms | 2 | 0.70 | 0.97 | 99 / 248 |
| jitter sd 12.6 ms | 2 | 1.06 | 0.95 | 132 / 330 |
| same phases | 2 | 1.49 | 0.93 | 66 / 198 |
| random phases | 2 | 1.76 | 0.92 | 66 / 314 |

# Step 1c measures on every single-queue development run (2026-11-12)

`rows2 / summary2` → `rows2.jsonl.gz`, `summary2.md`. 127 runs on pfifo / pie / red /
codel (35 not in step 1: the 25 codel microbenchmarks and J1). All runs use BBR;
no Copa run exists (Copa was dropped on 2026-11-03), so the controller cannot be
broken down. SAME: member vs its own leave-one-out template against a flat line
(L_flat, FLAG: the 1c form with "no shape" as the alternative); QUIET: a
non-congested client vs the full template, same score. EF = explained fraction.

| class | n | L p50 | > 11.5 | < 2 | prefers own / template | EF p50 |
|---|---|---|---|---|---|---|
| SAME, all | 15 167 | 274 | 0.95 | 0.02 | 0.99 | 0.996 |
| SAME, new runs | 5 826 | 194 | 0.95 | 0.01 | 0.99 | 0.993 |
| QUIET | 5 540 | −26 | 0.00 | 1.00 | 0.00 | – |
| CONCURRENT | 738 | (K1 121, K6 219, J1 51) | 0.85–1.00 | 0–0.05 | 0.96–1.00 | 0.99 |
| NESTED | 961 | (K1 87, J1 49, M6 208–210) | 0.88–0.96 | 0.01–0.06 | 0.95–1.00 | 0.99 |

New CONCURRENT rows: 540, all J1 (108 per variant). New NESTED rows: 423 (J1 270,
M6 codel 153). The codel runs add no concurrent cell. By factor (SAME, L p50, all
> 11.5 share 1.00 unless noted): queue depth 0.5 / 1 / 1.5 / 2 BDP 332 / 446 / 451 / 486;
frame rate 15 / 60 290 / 497; bitrate 1 / 8 Mb/s / mix 120 / 1 119 / 583; event density
high / low 426 / 411; independent timing mean 10 / 60 s 130 (0.74, 12 % < 2) / 193
(0.96); gradual onset (ramp) 644; long episodes 1 775; tiny bursts 185; stimulus
capacity drop / UDP / TCP / ppbp 263 (0.94) / 304 / 488 / 344; AQM codel / pfifo / pie /
red 353 / 214 / 362 / 275 (red 0.92). Low bitrate (1 Mb/s, fewer delay samples) and
dense independent timing (other episodes overlap the template) are the weakest.

FLAG constants (all steps): MARGIN 1 s, N_MIN 10, SAT 10 %, CONC_S 50 ms, the
"excl" calm window (1 s before / 2 s after), RW_TAU_S 1 s (slow offset), the ppbp
window split into GT1 episodes, and L_flat's flat alternative.
