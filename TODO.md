# TODO

- [ ] ECN / L4S: enable ECN on qvideo-server egress (mvfst `enableEcnOnEgress`/`useL4sEcn`, `l4sCETarget`), router ECN marking per AQM, and record CE marks per flow.

Deferred (not in the setup step):

- [ ] Matrix runner: generate topology x scenario cells (AQM, bitrate, client count) with repetitions.
- [ ] Scenario designer UI (scenarios are hand-written YAML; the designer edits topologies only).
- [ ] Rejoin: a subscriber joins and leaves at most once per run.
- [ ] Detectors (shadow detector, SBD baselines) on qvideo-server via an mvfst observer.
- [ ] Kernel-side event capture (moqlab `tc_events.py`): `events.csv` records what quiclab applied, not tc changes made by hand in `--cli`.
- [ ] BBRv3 (not in mvfst; would be a Bbr2 patch).
- [ ] Router queue occupancy in the visualizer node panel (the CSVs are already written).
