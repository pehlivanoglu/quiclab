# Part A (A1, A3) and Step 2: grouping inside one event without labels (2026-11-12)

Read-only, development set (K*, C1, M*, J1; G0 for negatives), single-queue AQMs
(pfifo, pie, red, codel), N1–N5 not opened. Code `scripts/grouping_step2.py`
(constants and tags in its docstring). Files: `a1-rows.jsonl.gz` / `a1-summary.md`,
`a3-rows.jsonl.gz` / `a3-summary.md`, `step2-rows.jsonl.gz` / `step2-summary.md`,
`step2-example1..5.png` (single group, concurrent, nested, overlapping, negative).
A2 is answered in `reports/baselines-2026-11-12/README.md` ("Reading the two
false-alarm numbers") with `fa_reconcile.md`.

FLAG constants: MARGIN 1 s, N_MIN 10 samples, CONC_S 50 ms, MAX_ITER 10,
MAX_TEMPLATES 8, OBS_SHARE 0.5, NEG_SPAN (−1 s, +2 s) around an ECG event's t0,
event intervals from windows.json (later: from the detector), and the x0 penalty
(diagnostic only).

# Step 2b (2026-11-12)

Files: `step2b-rows.jsonl.gz` / `step2b-summary.md` (A), `neg-rows.jsonl.gz` /
`step2b-neg.md` (B), `calm-rows.jsonl.gz` / `step2b-calm.md` (C), `step2b-d.md`,
`step2b-pair1.png`, `step2b-pair2.png` (D). Code: `grouping_step2.py` commands
`step2b`, `neg`, `calm`, `d-items` (+ `-sum`). New constants: N_SURR 200 (FLAG; 100
and 500 on every 10th run), ALPHA 0.01 (T), Q_TARGET_MS 5 (T, GT1's target),
PEAK_MARGIN 0.5 s (FLAG).

**B. Negatives with a topology truth.** A data class is right when its members share
a recorded router egress whose queue reached 5 ms inside the event. 244 G0 events,
239 data classes: 218 right, 21 wrong, none with sub-ctrl. All 21 wrong ones are
calmuneven: 5–13 clients from branches a, b and c in one class while only the branch
queues formed, not the common r1->r2 queue (simultaneous small branch peaks merged).
ECG's 25 confirmed SAME pairs on G0: all 25 right under the same truth (the pair
shares a recorded egress with at least one GT1 episode in the run).

**C. Short shared queues in calm runs.** Peak = contiguous time with the egress queue
>= 5 ms. They are frequent and tiny: hundreds per minute per egress (calm065 base 392 /
min, branch egresses 570–950 / min), peak p50 6–15 ms, duration p50 one sample (p90
15–65 ms). On the single-queue base topology (calm065) the clients behind the queue
end up in one class in 78 % of peaks with nobody else; on split / tree8 / uneven
another egress always peaks within ±0.5 s, and the branch structure is not recovered
(together and apart 0–10 % per branch egress). By peak size: 5–10 ms 6 %, 10–20 ms
26 %, 20–50 ms 22 %, >= 50 ms 38 % right. So calm periods carry evidence that a queue
is shared, but at this scale not which branch.

**D.** Group of 2 (81 single-group events, 0.51 exact): the failure is step 2's
initial template, not the leave-one-out. The initial template is the median of all
participants; with 2 congested of 6 it follows the quiet majority, both pair members
fit it worse than class 0 (e.g. f 69 vs 46), and no data template forms although
each member fits the other well (f ≈ 8 vs ≈ 40 for class 0). The split step could
recover it, but the penalty blocks it. Most cases: K6 depth (36) and C1 (14).
Iteration cap: 29 passes in 29 events, oscillating between two assignments: J1
jitter runs 11 (5 of them jitter sd 12.6 ms), M6 independent timing 6 (red, codel),
G0 calmsplit / calmuneven 5, other 7.

**A. Surrogate-calibrated split test: it does not separate one-group from two-group
events.** 3547 events, 200 surrogates, alpha 0.01, only the first extra template
tested. One-group events split 13 %, two-group events split 10 %; exact partition
0.62 overall (single group 0.84, concurrent 0.00, nested 0.11, overlapping 0.10,
J1 0.26–0.43). ROC area two-group vs one-group: raw G 0.855, surrogate p-value
0.489 (chance). Surrogate count does not matter (100 / 200 / 500: no decision
changes on 411 events).

Why: the null keeps the group structure. In a two-group event merged into one
class, the members' residuals from the common template are the two groups'
deviations; permuting them among members only relabels which client carries which
deviation, so every surrogate still contains the same two groups and its best
split gain equals the observed one (two-group events: G* q99 p50 100 vs G_obs p50
83, correlation 0.94; G* q99 >= 0.9 G_obs in 94 % of events). The test compares the
data with itself. A null that removes the alignment between clients (each
member's residual circularly shifted by a random lag, keeping its autocorrelation)
would test the right thing; not run. Raw G alone ranks well (AUC 0.86; concurrent
0.96) but, as in step 2, no single threshold separates the classes.
