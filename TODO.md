# TODO

Detector and baselines:

- [ ] Shared-bottleneck test: two separate shared bottlenecks (`detector-split.yaml`, can start from `flowbot-like.yaml`), bursts on one link or both. Needs a new campaign.
- [ ] Scenarios that show method limits: long congestion (20-60 s; SBD needs 10-17 s of history) next to the short 1-4 s bursts. Report per scenario type, never pooled.
- [ ] Grouping truth and scoring for the SBD baselines (`scripts/sbd_baselines.py`): pairwise co-bottleneck precision/recall, plus their per-client "bottlenecked" decision scored like the shadow detector.
- [ ] Rerun the newscn-base and large campaigns: their oracle OWD predates the client PING fix and the 5 ms bins.
- [ ] Per-client measured truth (frame OWD + sender loss). The model truth is wrong for fq_codel with bursty video, ramps at u 0.9-0.95, and elastic TCP (scored "uncertain").
- [ ] FlowBot itself as a baseline (its repo needs torch / pytorch_lightning, a fixed `models.Pipeline` import and sklearn 0.24 pickles).
- [ ] Live detectors on qvideo-server via an mvfst observer (today everything is replayed offline from `-acks.csv`).

Testbed:

- [ ] ECN / L4S: enable ECN on qvideo-server egress (mvfst `enableEcnOnEgress`/`useL4sEcn`, `l4sCETarget`), router ECN marking per AQM, and record CE marks per flow.
- [ ] Fixed client player for QoE truth next to network truth.
- [ ] Scenario designer UI (scenarios are hand-written YAML; the designer edits topologies only).
- [ ] Rejoin: a subscriber joins and leaves at most once per run.
- [ ] Kernel-side event capture (moqlab `tc_events.py`): `events.csv` records what quiclab applied, not tc changes made by hand in `--cli`.
- [ ] BBRv3 (not in mvfst; would be a Bbr2 patch).
- [ ] Router queue occupancy in the visualizer node panel (the CSVs are already written).
