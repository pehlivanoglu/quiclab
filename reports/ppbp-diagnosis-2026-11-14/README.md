# Detector diagnosis on the ppbp runs (2026-11-14)

Measurement only. The frozen Shadow v2 (`scripts/shadow_v2_frozen.py`: OWD ticks, fusion d,
hold, loss gate level+cap, θ_on 0.25) and its fixed-statistics variant are called, not changed.
Truths: GT1, GT3 and the frame-latency harm label (`shadow_v2_step0.harm_times`: a frame that
missed its playout deadline). No GT-Q / GT-H.

Code `ppbp.py` (`run` / `sum` / `plots`); rows `rows.jsonl`; tables `summary.md`; plots
`missed1..10.png`.

**Runs.** `.runs/old-wrong-scenaris/ip4-not-sync-keyframes-oldGT`: base topology, staggered
phases, **one rep each**.
- M1 ppbp and M1 burstcap on pfifo / red / pie / codel / cake;
- G0 calm065, calm090, calmcbr090 on pfifo / red / pie / cake / fq_codel.

The two-rep detector campaign (`.runs/old/ip4/2026-11-08_det-base`, with ppbp r1 / r2) is no
longer on the machine, so **no rep comparison is possible**: every number below is a single run.

**Checking the detector state.** Item 2 re-derives the detector's internal baseline and noise
beside it, from its own outputs. Check: the per-tick F1 z-score from the re-derived state
matches the one implied by the detector's own F1 term within 0.004–0.018 (learned v2) and
exactly (fixed).

## 0. How the detector works (details: `reports/detector-v2/methodology-tr.md`, `methodology.tex`)

**Inputs, one tick per frame (33 ms):**
- **F1** = the tick's minimum OWD minus `base`, the running minimum of the whole run so far
  (it only moves down);
- **F2** = the 2-tick slope of F1;
- **F3** = growth of pending bytes (in flight + stream buffer) over 30 ticks, divided by the
  delivered rate;
- **F4** = the drain time of the pending bytes;
- **L** = the loss rate over 100 ms.

**Calm statistics.** Each feature has a calm mean μ and variance σ²:
- initialised from the first 3 s of calm ticks;
- then updated by an EWMA (τ = 60 s) on every calm tick. A tick is calm when the detector's
  own score stayed below 0.125 over the trailing 1 s, and the tick is neither masked nor
  without data;
- σ has a floor (OWD: F1 0.27 ms, F2 0.37, F3 0.0043, F4 0.0041).

**CUSUM.** Each feature gives z = (x − μ)/σ, clipped to ±4, and a per-tick term
s = δ(z − δ/2) with δ = 2. The term is positive only when z > 1, i.e. the feature is more than
one σ above its calm mean.
- Fusion d sums the F1, F2, F3 and L terms. The loss term is positive only while F1's z is
  ≥ 1 within the last 3 ticks, and is capped at g_ref/4 per excursion.
- G = max(0, G + Σs), capped at 2·g_ref (g_ref = 67.7 for OWD v2, 77.9 for fixed).
- **Drain:** G falls whenever the summed term is negative, i.e. the features are near or below
  their calm means.
- **Hold:** negative terms are set to zero while F1 or F4 is ≥ 1σ high, or within
  max(0.3 s, 2·SRTT) of a loss. While the delay stays high, G does not drain.
- There is no other reset (probe-RTT ticks are masked; G is frozen there).

**Score and alarm.** score = G / (2·g_ref), from 0 to 1. The alarm starts at score ≥ 0.25 and
ends at 0.125.

**Variants:**
- **v2:** the calm statistics are learned per flow as above.
- **v2-fixed:** μ and σ are frozen at values fitted on the ip4 calm030 / calm065 pfifo runs
  (OWD F1: μ 1.5 ms, σ 3.18 ms) and never updated. Everything else is identical.

## 1. Is it the scoring?

**a. GT1 on the shared bottleneck (router→switch):**

| | episodes per min | duration p10 / p50 / p90 s | share of time on | peak queue delay p50 (client episodes) |
|---|---|---|---|---|
| ppbp (5 AQMs) | 15.7–30.9 | 0.17–0.31 / 0.53–1.80 / 2.4–9.6 | **0.47–0.84** | 47 ms |
| burstcap | 6.4–7.5 | 0.17–0.22 / 0.88–1.18 / 2.3–4.2 | 0.14–0.19 | 96 ms |
| calm065 | 1.1–3.2 | ~0.15 / 0.15–0.28 / 0.17–0.34 | 0.00–0.01 | 51 ms |
| calm090 / calmcbr090 | 20–54 | 0.15–0.17 / 0.23–0.33 / 0.8–1.1 | 0.14–0.45 | 28–36 ms |

Under ppbp the bottleneck has a standing queue most of the time. GT1 cuts this into many
episodes, some long.

**b. Recall by duration and peak delay (v2, GT1; start rule, overlap rule in `summary.md`):**

| | all | < 0.5 s | 0.5–1 s | 1–2 s | **≥ 2 s** | **peak ≥ 50 ms** |
|---|---|---|---|---|---|---|
| ppbp | 0.02–0.12 | 0.00–0.03 | 0.00–0.07 | 0.00–0.20 | **0.07–0.34** | **0.05–0.24** |
| burstcap | 0.49–0.64 | 0.00–0.10 | 0.00–0.40 | 0.75–1.00 | **0.92–1.00** | **0.77–0.99** |

- GT3, all episodes: ppbp 0.12–0.44, burstcap 0.91–1.00.
- With the overlap rule (the 0.16 of the brief): ppbp 0.11–0.19, burstcap 0.64–0.86.

**c. Harm.** Of the missed GT1 episodes in ppbp, 1–17 per run overlap a playout-deadline miss
and 111–250 do not; most ppbp episodes are harmless. But the harmful ones are missed too:

| | recall on harmful episodes | harmful ≥ 1 s |
|---|---|---|
| ppbp | 0.15–0.75 | 0.20–0.75 |
| burstcap | 0.59–1.00 | 0.93–1.00 |

**d. Precision and false alarms (GT1).**
- ppbp: precision 0.83–1.00; false alarms 0 per client-minute except pie (0.22).
- burstcap: precision 0.94–1.00; false alarms 0–0.31.
- The detector is not noisy on ppbp; it is quiet.

**Reading:** not a scoring effect. The misses include long (≥ 2 s) and deep (≥ 50 ms)
episodes, and harmful ones, at rates far below burstcap. One scoring element exists: most
ppbp episodes are short and harmless fragments of one persistent queue. It inflates the
episode count but does not explain the misses on long and harmful episodes.

## 2. Is the calm baseline contaminated?

Per run, median over clients:

| | learned baseline above the queue-free delay (base + μ_F1 − min OWD) | learned noise σ_F1 p50 | sustained queueing delay needed to alarm within 1 s / 0.5 s |
|---|---|---|---|
| **ppbp v2** | **15.9–39.8 ms** (> 10 ms for 50–100 % of the time) | **17.3–22.1 ms** | **43–73 / 52–85 ms** |
| burstcap v2 | 3.3–3.5 ms | 3.3–4.8 ms | 8–11 / 10–14 ms |
| calm065 v2 | 5.0–5.2 ms | 2.3–4.3 ms | 9–12 / 10–15 ms |
| calm090 v2 | 7.1–15.2 ms | 5.7–12.8 ms | 16–35 / 19–41 ms |
| calmcbr090 v2 | 7.3–10.0 ms | 5.3–9.3 ms | 15–25 / 18–30 ms |
| any run, v2-fixed | 1.5 ms (fixed) | 3.18 ms (fixed) | 6.7 / 8.8 ms |

Under ppbp the learned baseline sits 16–40 ms above the queue-free delay and σ grows 4–6
times. Mechanism:
1. The background load is present from t = 0, so the 3 s initialisation already learns a
   loaded path.
2. The EWMA keeps learning it, because the detector rarely alarms, so most ticks count as calm.
3. A sustained queue of 43–73 ms is then needed just to reach the alarm level in 1 s. The
   typical ppbp episode peaks at 47 ms.

calm090 and calmcbr090 show the same effect at a smaller scale. So it comes with **any
persistent background load**, not only with self-similar bursts.

**v2-fixed on the same runs:**

| | GT1 on share | time in alarm, v2 | time in alarm, v2-fixed | recall (overlap), v2 | recall (overlap), v2-fixed | recall (start), v2 → v2-fixed |
|---|---|---|---|---|---|---|
| ppbp | 0.45–0.82 | 0.09–0.21 | **0.72–0.95** | 0.11–0.19 | **0.35–0.86** (pfifo / red / pie / codel 0.76–0.86) | 0.02–0.12 → 0.09–0.44 |
| burstcap | 0.14–0.19 | 0.21–0.31 | 0.23–0.32 | 0.64–0.86 | 0.64–0.87 | v2 = fixed |

- With frozen calm statistics the detector sees most ppbp congestion, on the same level as
  burstcap except cake.
- Its start-rule recall stays low because it is already in alarm when most new GT1 fragments
  begin. That part is a scoring effect, and it only shows once the detector is sensitive.
- Price of the fixed variant:
  - In alarm 72–95 % of the time when GT1 says 45–82 % (pie 0.95 vs 0.54, cake 0.72 vs 0.45).
  - More false alarms on calm065: 0.28–1.22 per client-minute, against 0–1.01 for v2.

## 3. Is it the shape of the signal?

Missed GT1 episodes of ≥ 1 s (v2, start rule), classified:

| | missed ≥ 1 s | never moved (score max < 0.05) | rose and drained | crossed late | other |
|---|---|---|---|---|---|
| ppbp (5 runs) | 50–99 per run | **26–57** (229 of 361) | 1–11 (37) | 0–4 (11) | 7–44 (84; 44 in pie) |
| burstcap | 0–9 | 0 | 0–5 | 0 | 0–8 |

- Of 10 randomly drawn ppbp episodes (seed 7), 7 never moved and 3 are "other": the score
  rose slightly and stayed below the alarm level. Plots: `missed1..10.png`.
  - **missed1:** before the episode the client's OWD is ~55 ms above its floor while G sits
    at 17 (score 0.12, held). G drains when the OWD dips, and the next 60 ms rise inside the
    episode does not move it at all.
  - **missed4:** the client's OWD rises only 10–20 ms during the episode, against a learned
    σ of ~17 ms.
- **Drained class (37 episodes):** p50 of 4 negative ticks per episode. The negative terms,
  summed: F3 −718, L −403, F1 −372, F4 −295, F2 −275.
  - Mostly the pending-bytes growth term (F3) and the loss term, which go negative between
    bursts, plus F1 dips. The hold rule does not apply there because F1 and F4 are below 1σ.
  - Never a reset (the detector has none besides masking).

**Reading:** the statistic mostly never moves. Draining before the threshold is a minority
(≈ 10 % of the long misses), and crossing late is rarer still. The "tuned for steps, misses
fluctuating onsets" explanation accounts for a small part.

## 4. Summary

**The data supports explanation 2: the calm baseline is contaminated.**
- Under ppbp the learned baseline sits 16–40 ms above the queue-free delay and σ_F1 is 17–22
  ms (burstcap 3–5 ms). A 43–73 ms sustained queue is then needed to alarm within 1 s, while
  ppbp's congestion peaks around 47 ms.
- So 63 % of the long misses never move the statistic, and v2 is in alarm 9–21 % of the time
  while GT1 is on 45–82 %.
- With the calm statistics frozen (v2-fixed), overlap recall rises from 0.11–0.19 to
  0.35–0.86. That closes most of the gap to burstcap (0.64–0.86) on four of five AQMs.

**Smaller parts:**
- **Scoring (explanation 1).** Most ppbp GT1 episodes are short, harmless fragments of one
  persistent queue, and the start rule cannot credit a detector that is already in alarm. This
  lowers v2-fixed's start-rule recall to 0.09–0.44, but it explains little of v2's own 0.16:
  v2 also misses the long, deep and harmful episodes.
- **Signal shape (explanation 3).** Rise-then-drain or late crossing account for ~13 % of the
  long misses.

The same desensitisation appears in calm090 / calmcbr090 (recall 0.04–0.12). It is a property
of persistent background load in general, which matters for the planned campaign with
background traffic in every run. Fixing it has a cost: v2-fixed alarms well beyond the GT1
time on pie and cake and raises calm false alarms. No fix was proposed or tried.

**What these runs cannot tell us:**
- One rep per configuration; the two-rep ppbp campaign is gone. No number here is checked for
  rep-to-rep stability, so treat single-run values as "not reliable" individually. The
  pattern holds across 5 AQMs and 3 kinds of background load.
- One traffic model (PPBP, Hurst 0.8, mean load ~0.95, present from t = 0) on one topology
  (base, 4 clients, staggered phases).
- No run where background load starts after the detector has learned a clean baseline; that
  would separate initialisation from ongoing EWMA learning.
- No other load levels of self-similar traffic; and pie / cake behave differently under the
  fixed variant.
