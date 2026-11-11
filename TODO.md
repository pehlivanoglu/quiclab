# TODO

Detector and baselines:

- [ ] Grouping truth and scoring for the SBD baselines (`scripts/sbd_baselines.py`): pairwise co-bottleneck precision/recall, plus their per-client "bottlenecked" decision scored like the shadow detector.
- [ ] Rerun the newscn-base and large campaigns: their oracle OWD predates the client PING fix and the 5 ms bins.
- [ ] FlowBot itself as a baseline (its repo needs torch / pytorch_lightning, a fixed `models.Pipeline` import and sklearn 0.24 pickles).
- Copa: dropped by the user (2026-11-03). If revived: under Copa `bbr_bw_bps` = 0, `phase` empty and mvfst's `app_limited` always false, so the detector needs its own bandwidth max-filter and app-limited flag first.
- [ ] Run the new event scenarios (det_matrix: burstlong, burstcapshallow, burstcapdeep, onoff, revdelay, calm030/065/090, calmcbr090, delaystep, randloss; burstlong is the 10-60 s method-limit test) and read them, per scenario type, never pooled, against the measured truth (`det-*-measured.*`; needs runs with the OWD oracle, i.e. after the client PING fix).
- [ ] Run the split topology (`det_matrix --topology split --scenarios splitcap,splitudp`): a downstream burst must alarm only its group, upstream both, `a+up` = two congested hops in series.
- [ ] Scenario backlog, to be added to the test matrix later (not built; keep 5-8 clients, scale load with cross traffic): capacity random walk; self-induced congestion (join / rendition up); overlapping events; RTT 200+ ms. Also open: shared + private bottleneck in one run. Dropped: policer (user decision, 2026-11-05), reverse jitter beyond K3's revjit10, Copa. Not in the current run plan: `--topology large` (user decision, 2026-11-05; the files stay).
- [ ] On machines without it, build the replay (`shadow/`, README "Usage"), then `det_eval.py score` and `report` on the recorded runs (`.runs/<tag>_det-*`) and `grouping_campaign.py --report-only`.
- [x] Rerun the runs of `.runs/2026-11-05_det-base` hit by a clock jump (checked 2026-11-06 09:03 after the machine died at 06:55, 166 finished runs; `det-burstcapshallow-fq_codel-r2` was running then, is unfinished and restarts by itself on resume; the listed runs still read "done" and have an `end` row, so `--skip-existing` keeps them). Detection: the largest step of `applied_unix_ns - applied_mono_ns` between `events.csv` rows. Laptop suspend (rerun): `det-burstcapdeep-fq_codel-r1` 3238 s, `det-onoff-fq_codel-r1` 3208 s, `det-tcpbbr-red-r1` 1259 s, `det-burstcapdeep-pfifo-r1` 1250 s, `det-burstcaplowrtt-fq_codel-r1` 234 s. Small jump, cause unknown (rerun too, ~23 min): `det-burstcap-pfifo-r2` 2.8 s, `det-randloss-red-r1` 2.4 s, `det-burstcaplowrtt-red-r1` 0.98 s, `det-tcpcubic-pie-r1` 0.68 s, `det-burstcap-red-r1` 0.67 s. Rechecked on all 200 finished runs (2026-11-06 13:10): the same 10 runs, no new ones, the other 190 step at most 0.1 ms. The 10 were rerun on 2026-11-06, 13:32-14:16; rechecked after that: all 200 finished, no failed run, largest step 0.1 ms.
- [ ] Reading the detector scores: `calm090` and `calmcbr090` are not calm by the OWD truth (5-60 episodes per run, except fq_codel 9-20; scoring them as "every alarm is false" overstates false alarms). `calm090-pie` has real loss in both reps (29-37k router drops vs 1.3-1.6k on pfifo, about 15 % retransmitted bytes, client stalls): BBR with PIE at u = 0.9, not a run fault. Router-metrics sampling gaps of about 0.4 s in 19 r1 runs (2026-11-05 evening) did not reach the control client's OWD; those runs stay.
- [ ] Live detectors on qvideo-server via an mvfst observer (today everything is replayed offline from `-acks.csv`).

Grouping (ECG, `grouping/`, brief `grouping-implementation-v01.md`; results in `grouping/README.md`):

- [x] v1.2 rules implemented behind `Config.V12` (README "Campaign results … v1.2"); K1–K6 ran 2026-11-06 (`.runs/old/ip8/2026-11-06_1526_grp`); all five re-scored in `report-v12.md` (K6 pfifo 3/3 correct trees; K1 21 runs, FIFO-like cells 1.0/1.0).
- [x] v1.2 is the default and frozen (2026-11-10, commit d864058); truth and scoring frozen in the README.
- [ ] Campaign v2 (`grouping/campaign-v2-spec.md`, 145 runs, 20.7 h): smoke `--ks N2 --only pfifo-r1` (17 clients) and `--ks N4 --only pfifo-r1` (read its `infra.md`: 4 000–12 000 tc commands, trace lag p99/max must stay under 50 ms), then the full set with `--skip-existing` in tmux; development set `--report-only --compare .runs/old/ip8/2026-11-06_1526_grp`.
- [ ] Merged campaign (review 2026-11-10, `grouping/campaign-v2-spec.md` end): one planner for core (K1–K6, N1–N5, calm per topology, split burstlong), microbenchmarks on base (burstcap/udp/tiny, ramp, tcp, ppbp, burstlong, RTT ×0.25/×2, queue 0.5/1/1.5/2 BDP, reverse jitter 5/10/20, fps 15/30/60, bitrate mixes, gap U(2,5)/U(10,15)/U(45,75); pfifo, red, pie, cake) and negatives (calm030/065/090, calmcbr090, randloss, revcross); both scorers on every run; u {1.1, 1.3, 2.0} everywhere; drop splitcap/udp, isolate, revdelay, capacity, cbr, onoff, delaystep; end-to-end metrics (shared event -> detected members -> attributed group -> confirmed time; group-confirmed vs single alarm P/latency; FA and false groups per minute on negatives). fps and bitrate mixes need topology variants (publisher fps, rate_kbps).
- [ ] Rule changes still open (episode end as an event, in-episode metrics): try on K1–K6 only, then freeze + tag, then score N1–N5 once with `--report-only --score-held-out`, never touching rules or truth afterwards.
- [ ] N5 limits: `det_eval.score` reads the first session of each client only; SBD baselines are off for N5 (no common span over sessions).
- [ ] OWD clock skew / timestamp noise sensitivity (offline, no new runs): perturb `<sub>-owd.csv` (per-client skew ppm + jitter) before `owd_mode.owd_acks`, re-score `shadow-owd` on K1–K6 (grouping) and the detector campaigns (det_eval), report P/R and FA deltas against the unperturbed OWD and the RTT shadow.
- [ ] K3 `revjit5` / `revjit20` if the jitter limit matters.
- [ ] fq_codel light load: report as "no shared congestion" (FQ-native truth would label these pairs negative; tight-link truth makes recall look low).
- [ ] The owd source and the SBD baselines on the newscn-base and large campaigns need those campaigns rerun (high-rate clients lose OWD timestamps mid-run there).
- [ ] Shadow replay should emit the backdated onset itself (today the adapter recovers it from `queue_delay_ms` ≥ 10 ms; spread p50 ≈ 80 ms, p90 ≈ 300 ms within a burst).
- [ ] Phase 2 priming (`Onset.primed`, `ObsSample.intervened` are carried but unused), Phase 4 slow path / weak tree.

Testbed:

- [ ] ECN / L4S: enable ECN on qvideo-server egress (mvfst `enableEcnOnEgress`/`useL4sEcn`, `l4sCETarget`), router ECN marking per AQM, and record CE marks per flow.
- [ ] Fixed client player for QoE truth next to network truth.
- [ ] Scenario designer UI (scenarios are hand-written YAML; the designer edits topologies only).
- [ ] Rejoin: a subscriber joins and leaves at most once per run.
- [ ] Kernel-side event capture (moqlab `tc_events.py`): `events.csv` records what quiclab applied, not tc changes made by hand in `--cli`.
- [ ] BBRv3 (not in mvfst; would be a Bbr2 patch).
- [ ] Router queue occupancy in the visualizer node panel (the CSVs are already written).
