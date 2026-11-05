# TODO

Detector and baselines:

- [ ] Grouping truth and scoring for the SBD baselines (`scripts/sbd_baselines.py`): pairwise co-bottleneck precision/recall, plus their per-client "bottlenecked" decision scored like the shadow detector.
- [ ] Rerun the newscn-base and large campaigns: their oracle OWD predates the client PING fix and the 5 ms bins.
- [ ] FlowBot itself as a baseline (its repo needs torch / pytorch_lightning, a fixed `models.Pipeline` import and sklearn 0.24 pickles).
- Copa: dropped by the user (2026-11-03). If revived: under Copa `bbr_bw_bps` = 0, `phase` empty and mvfst's `app_limited` always false, so the detector needs its own bandwidth max-filter and app-limited flag first.
- [ ] Run the new event scenarios (det_matrix: burstlong, burstcapshallow, burstcapdeep, onoff, revdelay, calm030/065/090, calmcbr090, delaystep, randloss; burstlong is the 10-60 s method-limit test) and read them, per scenario type, never pooled, against the measured truth (`det-*-measured.*`; needs runs with the OWD oracle, i.e. after the client PING fix).
- [ ] Run the split topology (`det_matrix --topology split --scenarios splitcap,splitudp`): a downstream burst must alarm only its group, upstream both, `a+up` = two congested hops in series.
- [ ] Scenario backlog, to be added to the test matrix later (not built; keep 5-8 clients, scale load with cross traffic): capacity random walk; self-induced congestion (join / rendition up); overlapping events; RTT 200+ ms. Also open: shared + private bottleneck in one run. Dropped: policer (user decision, 2026-11-05), reverse jitter beyond K3's revjit10, Copa. Not in the current run plan: `--topology large` (user decision, 2026-11-05; the files stay).
- [ ] Replay binary `../moq-testbed/build/moqx_shadow_replay` is not on the current machine (det_matrix and the grouping campaigns record runs without it; grouping scores owd / truth only). When it is here: `det_eval.py score` and `report` on the recorded runs, then `grouping_campaign.py --report-only`. The replay source was not reviewed when the group context moved to the leaf queue: check how it uses the group field.
- [ ] Live detectors on qvideo-server via an mvfst observer (today everything is replayed offline from `-acks.csv`).

Grouping (ECG, `grouping/`, brief `grouping-implementation-v01.md`; results in `grouping/README.md`):

- [ ] Decide v1.2 defaults from the synthetic sweep: `theta_J = theta_cov = 0.6` (one miss in three tolerated); a solo penalty scaled by the flow's background rate (the noisy S5 flow joins, then is expelled by its own noise); pairs need two co-occurrences before they take part in case B / GLOBAL; case C should not charge the silent members while the event is recorded as a sub-pattern (split-smoke: b flows fell below A during the four C events and re-confirmed only at 245 s).
- [ ] Run the grouping campaigns K1, K2, K3, K5, K6 (`scripts/grouping_campaign.py --ks K1,K2,K3,K5,K6 --reps 3`, ~10.4 h emulation + setup, in tmux; table in `grouping/README.md` "Campaigns"). Each K writes its `report.md` when it finishes. Not planned: mixed CC, continuous CBR, a separate long-burst campaign, serial double bottleneck as a campaign, migration on real runs (needs a route event), loss, RTT ×4–8.
- [ ] Then: read the K1/K6 case matrices (a+b / A+C cells must not be GLOBAL), K2 partial-event share → θ, K3 revcross false leaves; decide v1.2 and re-score offline with `--report-only --set ...` (no reruns needed).
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
