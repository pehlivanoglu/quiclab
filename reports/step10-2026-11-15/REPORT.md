# Step 10: where observed sets lose clients, four set definitions, two matching fixes, leaf-level scoring (2026-11-15)

**Scope.** Measurement on the v3 runs plus the Step 9 model. The detector, ECG, h3 and the existing scorers are unchanged. Every value is rep 1 / rep 2. Leaf level is the headline; mid / up / root are a side table.

**Files** (all in this folder):
- `step10.py`: the observed sets, Parts A–C and E, and the model of Part D;
- `sets2.py`: the matching variants;
- `report10.py` → `tables.md`;
- intermediate data: `phase1.jsonl`, `model10.json`, `rows10.jsonl`, `synth10.jsonl`.

**Runs.**
- Main set: 34 runs (C7, C8, C9, C10, C11, C12, C13, M7, M8; pfifo / codel / pie / mixab).
- fq_codel: 8 runs (C7, C9, C10, C12).

**Observed-set definitions** (ECG event = [t0, t_close] from metrics.json; detector onsets):
- **O1**: the event's members, as before.
- **O2**: observable clients in alarm at any time in the event.
- **O3**: observable clients whose alarm started within [t0 − base RTT (P), t_close] and is on at t0.
- **O4** (added after Part A): O1 plus observable clients whose ECG onset (aligned time) lies within δ_max = 0.3 s of t0 (T, ECG config), whichever event ECG put it in.

**Matching variants:**
- **old**: Step 9.
- **new**: m per group from member participation; extras allowed up to the binomial 0.99 quantile (T) at the definition's measured false-inclusion rate (M).
- **contain**: S' counts toward S if ≥ 90 % (FLAG) of S' lies inside S.

## A. Where the misses come from: mostly not the detector

3490 (client, event) pairs where a client behind a congested egress is missing from O1:

| reason | share |
|---|---|
| onset put in a neighbouring ECG event | 0.45 / 0.46 |
| (of which within δ = 0.15 s) | 0.07 / 0.08 |
| (of which within δ_max = 0.3 s) | 0.26 / 0.27 |
| (of which beyond δ_max) | 0.12 / 0.11 |
| already in alarm from an earlier onset (median 2.0 s earlier) | 0.43 / 0.39 |
| not observable at t0 | 0.08 / 0.11 |
| never alarmed | 0.04 / 0.04 |

- **The hypothesis holds.** 0.95 / 0.95 of the missing clients were in alarm during the ECG event.
- **"Never alarmed"** is 0.08–0.10 at leaf level and 0.22–0.28 in M8. In M8 these are the fq_codel `b` clients, whose own queue was not constrained.
- **At leaf level the neighbouring event dominates** (0.62 / 0.64). Its onset sits a median 162 ms before t0 (p10 −252, p90 +240 ms). ECG has split one congestion onset into two events.
- **When ≥ 2 clients are missing together** they share neither RTT class (0 %) nor bitrate (4–15 %). In C9 mid events they are always on one branch (8 of 8). Their onsets are 130–210 ms earlier than t0, so they formed the earlier event.
- **"Already in alarm" is mostly combined events:** a staggered second leaf, or an upstream event on top of a congested leaf.

## B. Four definitions (single-egress events)

| definition | leaf miss | leaf false inclusion | leaf O = T | dispersion (leaf; 1 = binomial) | up miss | root miss |
|---|---|---|---|---|---|---|
| O1 | 0.146 | 0.006 | 0.75 | 2.8–3.6 | 0.183 | 0.250 |
| O2 | **0.027** | **0.094** (pie 0.36) | 0.76 | **0.97–1.12** | 0.009 | 0.012 |
| O3 | 0.135 | 0.033 | 0.69 | 2.5–2.9 | 0.178 | 0.217 |
| **O4** | **0.072** | **0.007** | **0.86** | 2.6–3.5 | 0.067 | 0.008 |

- **O2 does not help at leaf level.** It removes the misses and makes them binomial, but it pulls in clients that are in alarm for another reason. When a leaf event overlaps another congested egress, O2's set is the whole union (0.85 of leaf + upstream events, 0.54 of two-leaf events). So the leaf sets do not improve (O = T 0.76).
- **O3 changes little.**
- **O4 is the useful one.** It halves the leaf miss rate (pfifo / codel 0.12 → 0.05) at no extra false inclusion, and raises O = T to 0.86–0.91.
- **O4's misses are still bursty.** 0.05 of events miss ≥ half of the clients, against a binomial 0.017–0.020. The rest are "already in alarm" cases and the M8 fq_codel branch.

## C. SETS with each definition and matching variant

**C1. Leaf headline** (best group per leaf, mean over closes):

| method | leaf P | leaf R | leaf F1 | spurious / close | same-leaf pairs P / R |
|---|---|---|---|---|---|
| SETS O1 old k2 (Step 9) | 0.84 / 0.84 | 0.83 / 0.86 | 0.83 / 0.85 | 0.84 / 0.77 | 0.99 / 0.96, 0.91 / 0.93 |
| SETS O4 old k2 | 0.85 / 0.86 | 0.85 / 0.88 | **0.84 / 0.87** | 1.08 / 0.85 | 0.96 / 0.90, 0.86 / 0.88 |
| SETS O1 new k2 | 0.80 / 0.78 | 0.87 / 0.90 | 0.82 / 0.82 | **0.39 / 0.35** | 0.91 / 0.86, 0.98 / 0.99 |
| SETS O4 new k2 | 0.78 / 0.75 | 0.88 / 0.92 | 0.81 / 0.80 | **0.35 / 0.33** | 0.83 / 0.75, 0.95 / 0.99 |
| SETS O1 contain k2 | 0.80 / 0.78 | 0.87 / 0.91 | 0.82 / 0.82 | 0.37 / 0.36 | 0.91 / 0.84, 0.99 / 0.99 |
| SETS O2 new k2 | 0.65 / 0.65 | 0.89 / 0.94 | 0.73 / 0.75 | 0.35 / 0.25 | 0.64 / 0.62, 0.99 / 0.89 |
| SETS O2 old k2 | 0.84 / 0.84 | 0.87 / 0.90 | 0.85 / 0.86 | 1.23 / 1.78 | 0.94 / 0.87, 0.84 / 0.72 |
| ECG | 0.75 / 0.71 | 0.72 / 0.81 | 0.73 / 0.73 | 0.10 / 0.03 | 0.92 / 0.68, 0.97 / 0.98 |
| h3 | 0.78 / 0.81 | 0.76 / 0.78 | 0.75 / 0.78 | 0.81 / 0.53 | 0.81 / 0.83, 0.61 / 0.74 |

- **Leaf F1 hardly moves.** SETS stays at 0.80–0.87 under every definition except O2 (0.70–0.75), above ECG (0.73) and h3 (0.75–0.78).
- **new / contain trade leaf precision for recall.** They halve the spurious groups (0.33–0.39 against 0.77–1.08 per close), raise pair recall to 0.95–0.99 and lower pair precision to 0.75–0.91.
- **O4 does not improve the leaf result over O1.** Most leaf misses were already absorbed by matching.
- **Jaccard filters** (k2, O1 new): spurious 0.08–0.09 at J ≥ 0.85 and 0.01–0.06 at J ≥ 0.95, but leaf F1 falls to 0.61–0.64 and 0.36–0.45. The filter removes right groups too.
- Per block (`tables.md`): C12 and C13 stay lowest (0.62–0.82), C9 0.74–0.84.

**C2.** Pair scores are in the table above.

**C3. Robustness to upstream events.** Leaf F1 at closes right after an up / mid / root event, minus F1 at the other closes:

| method | difference |
|---|---|
| SETS O1 old k2 | +0.07 / +0.02 |
| SETS O4 old k2 | +0.08 / +0.03 |
| SETS O1 new k2 | +0.06 / −0.02 |
| ECG | +0.02 / −0.00 |
| h3 | +0.06 / −0.01 |

The worst case of any SETS variant is −0.06 (O3 new, rep 2), from 197 / 203 closes after upstream events. **Upstream events do not damage the leaf groups.** In rep 1 the leaf F1 is even higher right after them.

**C4. Time to a leaf group with F1 ≥ 0.9.**
- SETS O4 old k2: 3 leaf events, 82–83 s. Late joiner joins in 34 / 34 cases in both reps, after 6–8 events (88–93 s).
- **new / contain are faster** (2 leaf events, 60–72 s; contain's late joiner after 3 events, 24–36 s). But they join fewer cases (22–29 / 34) and miss a leaf entirely more often (1–4 leaves never reach F1 0.9).
- ECG: 3–4 events, 80–133 s.

**C5. Order.** End groups are identical in 34 / 34 runs for every definition, variant and k.

**C6. Side table (mid / up / root).** new / contain lift the upper levels to 0.86–0.96, against 0.67–0.94 for old. ECG and h3 stay at 0.51–0.73.

## D. Scale model (a model, not a run)

Truth-onset sequences of C7, C9 and C11 under pfifo. Every client becomes r replicas, so leaf sizes are 10–45 (r 5), 50–225 (r 25) and 200–900 (r 100). Misses and false inclusions use each definition's measured rates: either independent, or with the measured per-event fractions resampled (joint). Leaf F1 at the end / spurious groups:

| definition, pattern | old k2 | new k2 | contain k2 |
|---|---|---|---|
| O1 independent, r 25 / 100 | 0.00 / 0.00 | 0.15 / 0.00 | 0.91 (13 spurious) / 0.40 |
| O4 independent, r 25 / 100 | 0.24 / 0.11 | 0.87 (14) / 0.33 | 0.88 (44) / 0.97 (54) |
| O2 independent, r 25 / 100 | 0.44 / 0.22 | 0.72 (23) / 0.66 (19) | 0.66 (11) / 0.71 (32) |
| O1 joint, r 25 / 100 | 1.00 / 1.00 (≤ 0.5) | 1.00 / 1.00 (≤ 1.2) | 0.90 / 0.92 |
| O4 joint, r 25 / 100 | 1.00 / 1.00 (≤ 0.7) | 1.00 / 1.00 (≤ 1.3) | 0.87 / 0.87 |

- **Under independent misses no definition and matching rule holds at 200–900 clients per group without many spurious groups.**
  - What breaks is no longer the old rule's two parts. It is that SETS can only report sets it has observed.
  - With independent misses, no observation of a large group is complete. Every candidate already lacks ~7–15 % of the members, and other observations contain exactly those members. They count as "extras" far beyond a false-inclusion allowance.
  - The 90 % containment rule recovers the members (F1 0.88–0.97) only at the cost of dozens of spurious groups.
- **Under the measured joint pattern every definition holds,** with old or new matching: leaf F1 1.00 at 200–900 clients, ≤ 1.3 spurious groups.
- **The measured misses of O1 and O4 are bursty** (dispersion 2.5–13): many events are complete and a few lose many. That is the joint pattern, but it was measured on groups of 2–16 clients. Whether large groups keep it is exactly what a real scale test has to show.
- **O2's misses are binomial**, so O2 is covered by the independent case, which fails.

## E. Per-flow-queue cells (same-link reading; both readings kept, decision open)

Best F1 per co-constrained set (seen ≥ 2 times), k2, ranges over the 8 runs:

| definition | old | new | contain |
|---|---|---|---|
| O1 | 0.62–0.84 | 0.69–0.83 | 0.68–0.86 |
| O2 | 0.73–0.91 | 0.61–0.84 | 0.76–0.86 |
| O4 | 0.68–0.81 | 0.69–0.83 | 0.75–0.86 |

- Under the same-queue reading every group in these cells is false. SETS reports 0.8–12.8 groups per close here.
- Full table in `tables.md` E.

## Reading against the criteria

- **A: holds.** 95 % of the missing clients were in alarm during the event. The misses come from ECG splitting one onset into neighbouring events (45 %) and from alarms that were already on (41 %), not from the detector.
- **B: O2 does not fix the raw material; O4 helps partly.**
  - O2 brings misses to ~1–3 % with binomial dispersion, but it pulls in clients alarmed for another reason. False inclusion is 9 % at leaf, and its sets do not get better.
  - O4 halves misses with no extra false inclusions, but the misses stay bursty.
- **C: partly.**
  - Leaf F1 is as good as Step 9 (0.80–0.87, best O4 old k2 0.84 / 0.87).
  - The new matching halves the spurious groups at a small leaf-precision cost.
  - There is no drop after upstream events, so this replaces final precision for good.
- **D: the scale claim cannot be made.** It holds only if large groups keep the bursty miss pattern measured here. Under independent misses, SETS's restriction to observed sets breaks it from about 50–200 clients per group.
- **The window stays.** O2 / O3 make the sets worse. O4 is the only redefinition that helps, and it helps less than the matching change.

## What these runs and the model cannot tell us

- **Scale.** The miss pattern of groups larger than 16 clients.
- **Choices left open.** No k or Jaccard threshold is chosen. O4's δ_max is ECG's own constant, not a new one.
- **Truth-set definition.** "Already in alarm" misses depend on it: the truth set includes egresses that were congested before the event.
- **Seeds and thin cells.** 2 seeds. Root / mid exist only in C9.
- **fq_codel.** The decision between the two readings is open.
