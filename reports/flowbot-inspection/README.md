# FlowBot code inspection (2026-11-15)

Repository: `/home/ubuntu/Research/Repos/multirelay/flowbot` (github.com/PrinceS17/flowbot, 3 commits,
last "Add init README."). Read only; nothing of ours or theirs changed; no campaign run. The smoke
test below ran their code from a scratch script with one in-memory stub (item 3).

## 1. Contents

| item | present? |
|---|---|
| Siamese embedding (stage 2) | yes, `src/models/*.pt` (PyTorch state dicts + params). `final_model.pt`: 2-layer CNN, 4 channels (owd, rtt, slr, cwnd), input 300 samples, 16-d output. `dccnn_fi012_w55.pt` (and `fi01`, `fi02`): dilated CNN (4 x 64, kernel 13, dilation 1-8), fields stored in the file `[owd, rtt, slr]`, 300 samples, 16-d. `dccnn_scan_w=0.1..0.9.pt`: 8-d, a weight scan. Which one is the paper's model is not stated (the README "Usage" section is TODO). |
| non-bottleneck classifier (stage 1) | yes, `src/bin_cls/*.pkl` (scikit-learn 0.24): random forest, decision tree, kNN, SVM, logistic, naive Bayes; the detector's default is `random_forest_93_92.pkl` (6 features: owd_std, rtt_std, slr_avg, slr_std, cwnd_avg, cwnd_std per 1.5 s segment). There is also a hand rule (`DataGetter.f_non_btnk`: owd std < 1 ms and 70th-percentile slr < 0.002, or slr <= 0.001). |
| training code | yes: `siamese/` (dataset, triplet loss, model, pipeline), `final_clean_pipeline.py` (prep_train / train / prep_pred / detect), `data_bin_classifier.py`. |
| ns-3 dataset | no. The README points to an external box.com link ("flowbot-data"). |
| scenarios that generate it | partly: `ns3/script/config_generator.py`, `multiRun.py`, `inflator.py` (left / right bottleneck groups, leaf links, pie / codel queues 100-500 pkts, PPBP cross traffic). The ns-3 module itself is the submodule `ns3/BBR_test` (github.com/PrinceS17/BBR_test), which is **not checked out** (empty folder). |
| clustering | yes: Chinese Whispers on the embeddings (`siamese/chinese_whispers.py`, `siamese/cluster.py`), distance threshold `model_th` (CLI default 0.2; `predict_segment` default 0.4, n_voter 9). |
| baselines | DCW: in `detector.py` (wavelet soft-threshold denoising of OWD, pairwise `np.correlate`, threshold, tag `dcw_0.8`). rmcatSBD: `sbd.py`, RFC 8382 with its default parameters (T 0.35 s, N 50, M 30, p_s 0.15, p_v 0.7, p_f 0.1, p_mad 0.1, p_d 0.1). dcSBD: the same SBD statistics with the non-bottleneck flows removed and the bottleneck flows clustered with Chinese Whispers. |
| license | **none in the repository** (no LICENSE file; no statement in the README). `sbd.py` alone carries an IETF Trust BSD-style header (RFC 8382 code). Without a license we may read and run it for evaluation, but redistributing or publishing their code (or a modified copy) is not covered; ask the authors before any release. |

## 2. Inputs each method expects

All methods read one table `[run, flow, time, owd, rtt, slr, cwnd, drop]` on a **common 5 ms grid**
(`t_unit = 0.005`), the same `time` values for every flow (sender and receiver clock shared, as in
ns-3), OWD and RTT in seconds (auto-converted from us if the median >= 1000), `time` in seconds.

| method | signals | window | output |
|---|---|---|---|
| FlowBot (ml) | stage 1: owd, rtt, slr (+ cwnd) statistics per segment; stage 2: the model's fields (`[owd, rtt, slr]` for dccnn_fi012, `[owd, rtt, slr, cwnd]` for final_model), mean removed per segment | 300 samples = 1.5 s, non-overlapping | one label per flow per 1.5 s window (group number; non-bottleneck flows each get their own label) |
| DCW | owd | 1.5 s | label per flow per window |
| rmcatSBD / dcSBD | owd and `drop` (0/1 per 5 ms sample) | T = 0.35 s, statistics over N = 50 intervals (17.5 s) | label per flow per 0.35 s |

slr ("short-term loss rate") = rolling sum of `drop` over 1000 samples (5 s) / 1000.

**Mapping from our per-client logs** (`publishers/<pub>/<client>-*.csv`):

| theirs | ours | note |
|---|---|---|
| time grid 5 ms, common to all flows | `-owd.csv` bins are 5 ms on the stream clock (`t_us`), the same grid for every client | direct |
| owd (s) | `owd_mean_us` (send-time OWD from ACK receive timestamps) / 1e6 | **sparse**: in C7 pfifo r1 only 17 % (a1, 1000 kb/s) to 40 % (a4, 5000 kb/s) of 5 ms bins hold a sample, because video is sent in frame bursts. Theirs is dense (continuous flows). Needs a fill rule (forward fill or interpolation): a new choice of ours. |
| rtt (s) | `-acks.csv` `rtt_us` per ACK (or `srtt_us`), resampled to 5 ms | same sparsity, fill needed |
| drop (0/1 per sample), slr | `-acks.csv` `newly_lost` per ACK, or `-cc.csv` `lost_packets` (50 ms) | loss is QUIC-detected loss at ACK time, not the router drop time; slr then follows their 5 s rule |
| cwnd | `-cc.csv` `cwnd_bytes` (50 ms) | BBR's cwnd of an application-limited video flow, not a bulk TCP cwnd; only `final_model.pt` uses it |
| truth label per flow and time | our GT1 / GT-Q per egress | see 4 |

Missing: nothing that cannot be derived, but every column needs a resampling or fill choice that
their ns-3 data never needed.

## 3. Does the released code run as is?

- Their venv (`.venv`, Python 3.8.20, torch 1.11.0+cpu, numpy 1.21.4, pandas 1.5.2, scikit-learn
  0.24.0) is present and loads every model file and the random-forest pickle.
- **The code does not import as released**: `detector.py`, `cluster.py` and `final_clean_pipeline.py`
  do `from models import Pipeline` / `MyTransformerEncoder`, a module that is not in the repository
  (`src/models/` holds only `.pt` files). `Pipeline` is not used on the detection path.
- No sample data is shipped, so no smoke test on their data was possible.
- Smoke test on synthetic input (6 flows, two shared queues, 30 s, 5 ms grid; `models` stubbed in
  memory only; script in the session scratchpad): all five methods run end to end on CPU in
  < 1 s each. FlowBot (both model files) put every flow in its own group (f1 0.50), DCW f1 0.84,
  rmcatSBD 0.70, dcSBD 0.76. SBD needs the `drop` column. The numbers mean only "it runs":
  the synthetic signals are not like their training data.
- The requirements.txt is a full system `pip freeze` (Ubuntu desktop packages, TensorFlow, ray,
  ...), not the project's dependency list.

## 4. Retraining

- Data: per flow and 5 ms sample the four signals plus a label = which of the flow's two candidate
  queues is its bottleneck at that time. Their truth rule (`get_truth_from_queue`): 10-sample (50 ms)
  rolling mean of packets in each of the two queues; label = the larger one, `-1` if both < 50
  packets. Each flow has exactly two candidate queues (`qid1`, `qid2`). Training uses triplets of
  1.5 s segments (same / different bottleneck).
- Our development runs can supply it: per-egress queue length every 5 ms (router-metrics queue-only
  sampler, GT-Q per-packet traces) gives the two-queue rule directly on T-SPLIT4(L) (leaf, up) and
  T-ACCESS. Three-level trees (T-TREE16) and T-HAYES (four candidate links) do not fit their
  two-queue label; their 50-packet floor is in packets, ours are 20-400-packet queues.
- Time on this machine (24 cores, 62 GB, RTX 3060): not measured. The models are small (about
  60 k - 160 k parameters) and their pipeline trains 3-6 epochs with early stopping, so training
  itself should take minutes to an hour; preparing triplets from ~200 runs is the larger cost.
- Held-out set: train only on development runs (v3 / v4 seeds 1-5); the held-out seeds 101-105
  (N1-N5) are never preprocessed; keep the training run list in a file and check it against the
  held-out names before training.

## 5. Adapter plan (not built)

For one run (C7 pfifo r1):
1. Build the table: for each client except sub-ctrl, the 5 ms `-owd.csv` grid (t = (t_us - T0) / 1e6),
   owd filled (one fixed rule for all methods), rtt and drop from `-acks.csv` binned to 5 ms, slr by
   their rule, cwnd from `-cc.csv` (forward fill); `flow` = client index; one `run` id.
2. Run each method with their `CobottleneckDetector.classify` (no labels needed for prediction):
   FlowBot (model file + model_th chosen once, before seeing our results), DCW (0.8), rmcatSBD and
   dcSBD (RFC 8382 defaults). Output: per window a label per flow.
3. Map to the common scorer: each window end becomes an "event close"; the groups are the label
   sets with >= 2 members (a singleton = non-bottleneck / no group). Leaf precision / recall / F1,
   pair precision / recall (from each client's group), spurious groups per close and time to a
   leaf group then come from `scripts/grouping_score.py` unchanged, with "closes" = windows. For SETS,
   ECG and h3 the closes are event closes; for FlowBot and the baselines they are fixed windows
   (1.5 s, or 0.35 s for SBD). Report both "all windows" and "windows inside a congested period"
   (their output exists also when nothing is congested).

## 6. What makes a like-for-like comparison hard or unfair

Against FlowBot:
- Trained on ns-3 continuous TCP flows with dense 5 ms OWD; our clients are application-limited
  QUIC video with 17-40 % filled bins and keyframe bursts every second. The fill rule is ours,
  and it shapes their input.
- Their model and thresholds were fitted to their topologies (two candidate queues per flow,
  pie / codel, PPBP cross traffic). Using the released model on our data is out of distribution;
  retraining on our data is fairer but then it is "FlowBot's architecture trained by us".
- Which released model is the paper's is not stated; picking one by our results would be tuning.
- Loss: their drop is the router drop at 5 ms; ours is QUIC loss detection at ACK time.

Against us (in their favour):
- FlowBot and the baselines give an answer every 1.5 s / 0.35 s from the signals alone, also
  within the first congestion; SETS needs repeated events (no group at k = 2 from one long
  overload). This is the FlowBot block's question, and the windowed output must not be scored
  only at our event closes.
- Retraining on our development runs lets FlowBot learn our testbed (same video, same queues),
  which our methods' constants were also chosen on; the held-out runs must stay out for both.
- Their truth (one bottleneck per flow, the fuller of two queues) differs from ours (sets that
  recur, nested leaf / up); a flow in both a congested leaf and a congested up has one label in
  theirs and two group memberships in ours. Scoring both against our leaf truth disadvantages
  a method that reports the up link when it dominates.

License: none stated (item 1); fine for an internal evaluation, not for redistribution.
