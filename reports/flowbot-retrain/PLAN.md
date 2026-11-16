# FlowBot retraining plan (2026-11-16, draft for decision)

Background: [../flowbot-inspection/README.md](../flowbot-inspection/README.md). Nothing here is built or run.

## 0. Goal and what is compared

Three FlowBot variants, scored on the same test runs as SETS, ECG, h3 and the baselines (DCW, rmcatSBD,
dcSBD):

| variant | stage 1 (non-bottleneck classifier) | stage 2 (Siamese embedding) | trained on |
|---|---|---|---|
| FB-R (released) | `bin_cls/random_forest_93_92.pkl` | `models/dccnn_fi012_w55.pt` (fields owd, rtt, slr) | their ns-3 data (not retrained) |
| FB-T1 | retrained | retrained, same architecture and hyperparameters | track A: v3 runs only |
| FB-T2 | retrained | retrained, same | track B: v3 + v4 training seeds |

FB-R is the paper's method as released. FB-T1 / FB-T2 are reported as "FlowBot architecture,
trained by us on our testbed". Both labels go into every table.

Which released file is FB-R is fixed now, before any result: `dccnn_fi012_w55.pt`. It is the only
file that stores its own fields. `final_model.pt` (with cwnd) is a secondary row only.

## 1. Data

### Track A: data we have (can start now)

The v3 campaign (`.runs/2026-11-14_1818_v3`), all at EXT (U 0.70):

| topology | runs | h | use |
|---|---|---|---|
| split4 (leaf a / b + up) | 27 | 5.1 | main source: every client has two candidate queues, as in their data |
| access (main + access link) | 9 | 0.9 | two candidate queues |
| base (one queue) | 146 | 10.7 | stage 1 (bottleneck vs not) and same-group positives; no different-bottleneck negatives |
| tree16, uneven, rev | 21 | 2.7 | excluded from training (more than two candidate queues, or reverse path) |

Limits: one load point; different-bottleneck windows only inside stimulus windows (unbalanced);
about 6 h with two candidate queues.

### Track B: v4 runs (after K1 / K2)

Same topologies at DEF (U 0.50) plus new ones. These runs are planned anyway, so no extra
campaign is needed.

| use | runs |
|---|---|
| train | seeds 1-2 of A4 (H-HIERL), A5 (H-INDEPL), A7 (A-MIXED), A8 (L-LONG2), N1 (H-SHIFT), N4 (H-CONC, T-PAR2), N5 (H-SPARSE) |
| validation | seed 3 of the same blocks (early stopping, threshold) |
| test | seeds 4-5 of those blocks, and every run of the blocks never trained on (K3 literature blocks L1-L9, T-HAYES, T-TEACUP, G1-G3 group size, NEG-*) |

Split rule: by seed, never by window inside a run. The AQM variants of one seed stay on the same
side, because they share the stimulus timing. The held-out seeds 101-105 (N1-N5) are never
exported. The planner writes the train / validation / test run lists to a file, and the export
refuses any held-out name.

## 2. Export: one of our runs -> their input files

Written in their own file layout, so that their `prep_train` / `prep_pred` run unchanged. This is an
adapter of ours; their repository is not modified.

- **Time grid:** 5 ms bins of `<client>-owd.csv` on the stream clock (common to all clients, t = 0 at
  T0). Their tolerance is fine with a few ms of host jitter.
- **owd** = `owd_mean_us / 1e6`.
- **Fill rule (FLAG, fixed before training):** a bin without a sample takes the last sample (forward
  fill), never a later one, so the signal could be computed online. Interpolation is rejected
  because it uses the future. Bins before the first sample are dropped.
- **rtt:** `rtt_us` of `-acks.csv`, binned to 5 ms (mean), forward fill.
- **drop:** 1 in a bin when `newly_lost > 0` there (QUIC loss detection time, not the router drop
  time). **slr** by their rule: drops over 1000 bins / 1000.
- **cwnd:** `cwnd_bytes` of `-cc.csv`, forward fill. Used only by the final_model row.
- **flows:** every client except sub-ctrl. A client's flow id is fixed per run.
- **queues:** each candidate egress of a client = its leaf egress (qid1) and the shared egress
  (qid2), from the plan's egress list. Queue length: `queue_packets` of
  `router-metrics/<r>/<iface>-queue.csv` (5 ms). `max_q_size` = the pfifo limit, or for AQMs the
  kernel limit as configured.

## 3. Labels

Two label sets, decided now which one is primary:

- **L-orig (primary):** their rule unchanged. 50 ms rolling mean of packets in each candidate
  queue; label = the fuller queue; `-1` if both are below 50 packets.
- **L-gt (secondary):** our GT1 episodes on the client's two egresses. Label = the egress with an
  episode at that time, the deeper one if both, `-1` if none.

Known effect, stated before training: at EXT the synchronized keyframe queue alone reaches about
100 packets on a leaf, so L-orig marks calm keyframe pulses as bottleneck time. L-gt does not.
Both FB-T variants are trained once per label set. L-orig is the headline.

fq_codel / cake runs are excluded from training: per-flow sub-queues make "which queue" undefined
for their rule. They stay in the test set.

## 4. Training (their code and hyperparameters, unchanged)

- Stage 2: architecture of `dccnn_fi012_w55` (c_in 3, l_in 300 = 1.5 s, 4 x 64 dilated CNN,
  16-d, abs_triplet loss), max 6 epochs, patience 3, their triplet sampling and batch size.
- Stage 1: their `data_bin_classifier.py`, random forest, their feature list.
- Clustering threshold `model_th`: their scan procedure, on the validation runs only, then frozen.
- Runs on CPU with their venv (torch 1.11+cpu). Expected minutes per training, not measured.
  Export and triplet building of about 100 runs is the larger part (estimate: tens of minutes).
- Seeds: three training seeds per variant; report all three side by side.

## 5. Evaluation

- Their per-window metric (precision / recall / F1 / ARI per 1.5 s window), as a sanity check
  against their paper's numbers.
- Our common scorer, unchanged (`scripts/grouping_score.py`): a window end counts as a close; a
  group is a label set with at least 2 members.
- Reported on two subsets: all windows, and windows inside a congested period.
- **ULL columns (all methods):**
  - time from the start of the first congestion to the first correct group, in ms;
  - the same time compared with the 600 ms client buffer;
  - the same after the 2nd, 3rd and 4th repetition (the FlowBot block question).
- Comparison sets:
  - Track A: FB-R and FB-T1 on v4 test runs (trained on EXT, tested on DEF: a load shift).
  - Track B: FB-R, FB-T1 and FB-T2 on v4 test seeds.
  - SETS, ECG, h3 and the baselines on the same runs.

## 6. Decisions needed

1. Approve the variant set (FB-R, FB-T1, FB-T2) and FB-R = `dccnn_fi012_w55.pt`.
2. Fill rule: forward fill (recommended).
3. Labels: L-orig primary, L-gt secondary (recommended).
4. Train / validation / test split by seed as in 1 (track B), and whether track A starts now.
5. Optional, not in the plan unless asked: a shorter-window variant (e.g. 0.5 s) for ULL. It is a
   new design of ours, not FlowBot.

## 7. Risks

- The released code needs one missing module stubbed (`models.Pipeline`, unused on the detection path).
- Their `prep_train` expects ns-3 file names and columns. If it reads more than documented, the
  export grows.
- Unbalanced labels (mostly `-1`): their triplet sampler may over-sample calm windows. This is
  reported, not tuned.
- No license: internal evaluation only; nothing of theirs goes into our repository.
