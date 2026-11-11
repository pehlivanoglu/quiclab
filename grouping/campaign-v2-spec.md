# Grouping campaign v2: scenario specification

Written before any v2 run (2026-11-10). Sections 1–9 are the reviewer's
specification as received; "Implementation notes" at the end records how the
open points were decided and where each item lives in the repository. The pass
criteria (section 7) are frozen with this file: no rule, threshold or truth
change may follow from N1–N5 results.

Audience: coding agent that maintains the emulation testbed and the grouping tools. This document is self-contained. It lists every scenario of the next grouping campaign: the existing ones (K1, K2, K3, K5, K6) with their changes, and five new ones (N1 to N5) that you need to build. Everything will be run from scratch.

Organise files and scripts however fits the repository. What is fixed here is the content of each scenario, the outputs, and the pass criteria.

## 1. Why this campaign exists

The grouping rules (v1.2) and the truth definition were both corrected while looking at the previous 87 runs. Those runs therefore cannot serve as independent evidence. This campaign has two parts:

- **Development set (K1, K2, K3, K5, K6):** the scenarios the rules were developed on, re-run with small changes. Reported as such.
- **Held-out set (N1 to N5):** scenarios the rules have never seen. These carry the paper's claims.

## 2. Before any run

1. Freeze the grouping engine at v1.2 (the seven rules plus the two deviations found during re-scoring). Make v1.2 the default, commit, and tag the commit. Record the tag in every run's metadata.
2. Freeze the truth definition (shared windows with at least 2 expected clients, intersection of planned sets, private windows excluded) and write it into the README.
3. Write the pass criteria of section 7 into the repository before the first held-out run.
4. After the freeze, no rule, threshold or truth change may be made in response to N1 to N5 results. If a held-out scenario fails, report the failure with the per-flow membership-score plot and the rule you believe is responsible. Do not fix and re-score.

## 3. Common rules (unchanged unless a scenario says otherwise)

| Item | Value |
|---|---|
| Publisher, CC, detector | single publisher, BBR, shadow detector frozen |
| Calm load | video demand (wire, x1.03) / bottleneck capacity = 0.65 |
| Default stimulus | capacity drop: link rate set to demand / u for d seconds, then restored |
| Default cells | u in {1.3, 2.0}, d in {1, 2, 4} s (6 cells) |
| Warm-up and tail | 15 s warm-up, 10 s tail |
| Queues | about 1 BDP (pfifo packet limit; RED thresholds as in the previous campaign) |
| AQMs | pfifo, red, pie, fq_codel on router egress; switches never congest |
| Control client | sub-ctrl on a separate, never-congested path (50 Mb/s, 20 ms); must never join a group |
| Onset sources | shadow, owd, truth; all three scored on every run |
| Seeds | rep index = seed; the same seed gives the same event order across AQMs |

`windows.json` keeps its current fields (start, end, target, cell, expected). Two additions:

- `concurrent`: true when the window overlaps in time (within 1 s) with a window on a different bottleneck. Needed for scenarios with independent timing.
- `stimulus_type`: `capdrop`, `udp`, `tcp`, or `trace`.

### Independent timing (used by N1, N2, N3)

Each bottleneck has its own stimulus process. Gaps between stimuli on the same bottleneck are exponential with the stated mean and a 5 s minimum. Processes on different bottlenecks are independent; simultaneity is never scripted. Cells (u, d) are drawn uniformly at random per stimulus. Accidental overlaps are kept and flagged `concurrent`.

## 4. Development set

### K1 hier (15 runs)

Topology `detector-split.yaml`, unchanged: pub, r1, r2, switch-a and switch-b; a1/a2/a3 and b1/b2/b3 at 1 / 2.5 / 5 Mb/s; bottlenecks up 27 Mb/s (6 clients), a 13.5, b 13.5.

Changes:
- Target kinds reduced from 8 to 7: `up`, `a`, `b`, `a+b`, `a+b@0.5`, `a+b@2`, `a+up`. Drop `a+b@1`.
- AQM variants reduced from 7 to 5: pfifo, red, pie, fq_codel, mixab. Drop mixa and mixb.
- 7 kinds x 6 cells = 42 stimuli per run. 5 AQM variants x 3 reps = 15 runs.
- Report the `a+b` simultaneous cells separately, labelled as a scripted worst case.

### K2 part (24 runs)

Unchanged. Topology `detector.yaml`, single bottleneck 17.5 Mb/s, 4 clients (1 / 2.5 / 2.5 / 5). Poisson-like on/off capacity drops, one severity per run, u in {1.05, 1.10, 1.15, 1.30}; on U(1, 4) s with 15 % U(10, 20) s; off U(5, 20) s; 300 s. pfifo and fq_codel, 3 reps.

### K3 rev (24 runs)

Unchanged scenarios: `revasym`, `revjit10`, `revcross`, `revcrossmix`; pfifo and fq_codel; 3 reps.

Change in scoring only: once the detector has an OWD input mode, score every K3 run with both the RTT-based and the OWD-based shadow. `revcross` is reported in the detector section, not in the grouping table.

### K5 mixed (12 runs)

Topology `detector-access.yaml`, unchanged.

Changes:
- Shared windows: 12 (6 cells x 2), as already planned.
- Private windows: unchanged, 16 (per client u in {1.3, 2.0} x d in {2, 4}).
- sub-d still joins at 60 s.
- sub-b no longer leaves; every client stays until the end. (Leave and path change are moved to a separate extra test, outside this campaign's main results.)
- 4 AQMs x 3 reps = 12 runs.

### K6 depth (10 runs)

Topology `detector-tree8.yaml` with new bitrates. Reason: with 1 and 2.5 Mb/s per leaf, the 1 Mb/s client never queued under fq_codel, so each leaf degenerated to one client.

- Each leaf: x1 = 2.5 Mb/s, x2 = 5 Mb/s.

| Hop | Clients | Demand (x1.03) | Capacity |
|---|---|---|---|
| root (rr to r0) | 8 | 30.9 | 47.5 |
| X, Y (r0 to r1, r0 to r2) | 4 each | 15.45 | 23.8 |
| A, B, C, D (to each switch) | 2 each | 7.73 | 11.9 |

- Queues rescaled to about 1 BDP at the new capacities.
- Targets unchanged: `A`, `B`, `C`, `D`, `X`, `Y`, `root`, `A+C`; 8 kinds x 6 cells = 48 stimuli.
- pfifo and fq_codel, 5 reps = 10 runs.

## 5. Held-out set

All held-out scenarios use 5 reps.

### N1 indep: independent timing on the split topology (15 runs)

Question: do cross-branch false pairs (the a2/b2 case) survive when the branches are stimulated independently? This is the real-data test of the "coincidental overlap" objection.

- Topology: `detector-split.yaml`, same capacities as K1. No new yaml.
- Stimuli: three independent processes on `up`, `a`, `b`; mean gap 30 s each; default cells.
- Duration: 600 s (about 18 windows per bottleneck).
- AQMs: pfifo, pie, fq_codel.

### N2 uneven: large and unequal groups (15 runs)

Question: do the errors seen with 2 and 3 client leaves appear in larger groups? Does a wrong member get in?

- New topology: pub, r1, r2, three switches. The r1 to r2 link is not a bottleneck (200 Mb/s). sub-ctrl as usual.

| Branch | Clients | Bitrates (Mb/s) | Demand (x1.03) | Capacity |
|---|---|---|---|---|
| A | 2 | 5, 8 | 13.4 | 20.6 |
| B | 5 | 1, 2.5, 2.5, 5, 8 | 19.6 | 30.1 |
| C | 9 | 1, 1, 2.5, 2.5, 2.5, 5, 5, 8, 12 | 40.7 | 62.6 |

- Access delays: a distinct value per client between 5 and 45 ms.
- If the testbed cannot run 17 clients, use the reduced C branch: 6 clients (1, 2.5, 2.5, 5, 5, 8), demand 24.7, capacity 38.0. State which variant was run.
- Stimuli: three independent processes on A, B, C; mean gap 30 s each; default cells.
- Duration: 600 s.
- AQMs: pfifo, pie, fq_codel.

### N3 cross: external traffic as the stimulus (10 runs)

Question: every stimulus so far was a capacity drop. Does competing traffic give the same grouping?

- Topology: `detector-split.yaml`, using the existing cross-traffic routes for `up`, `a`, `b`.
- Stimulus types, mixed within a run, drawn with equal probability:
  - **UDP constant-rate burst.** Rate = u x capacity - video demand on that hop, so total offered load is u times capacity. u in {1.3, 2.0}, d in {1, 2, 4} s. Example for hop a (capacity 13.5, demand 8.76): 8.8 Mb/s at u = 1.3, 18.2 Mb/s at u = 2.0.
  - **TCP bulk.** 2 or 4 Cubic flows for d in {4, 8} s (longer, because TCP needs time to ramp). u is not controlled; record the achieved peak load per window.
- Timing: independent processes on `up`, `a`, `b`; mean gap 30 s each.
- Duration: 600 s.
- AQMs: pfifo, fq_codel.
- Expected under fq_codel: the cross traffic gets its own queue, video flows below their share are not affected, few hits. This is not a failure.

### N4 trace: trace-driven access links (10 runs)

Question: does the shared group survive when private congestion comes from real capacity traces and is frequent?

- Topology: `detector-access.yaml`. Shared bottleneck unchanged (17.5 Mb/s).
- Access links: each client gets a different cellular capacity trace, taken from the Mahimahi LTE traces and the Norway HSDPA traces. Aggregate each trace to 200 ms steps and replay it with `tc` rate changes on that client's access router.
- Scaling: multiply each trace so its mean is 2 x the client's bitrate. Target: capacity below the client's bitrate for 5 to 15 % of the run. Compute this fraction from the scaled trace before running and write it to the run metadata. If it is outside the target, adjust the multiplier and note the final value.
- Use the same trace assignment for the same seed across AQMs.
- Shared stimuli: capacity drops on the shared link, gaps U(10, 15) s, default cells.
- No scripted private windows. Private truth for a client: intervals where the replayed access capacity is below that client's send rate, confirmed by the OWD oracle. Write these as windows with `stimulus_type: trace` and `expected` = that client only.
- Duration: 600 s.
- AQMs: shared link pfifo and fq_codel; access links pfifo.

### N5 churn: clients joining and leaving (10 runs)

Question: in a session with turnover, how many clients get grouped, and after how many events?

- Topology: the 8-client `large` topology, single bottleneck. Keep its existing bitrates; set the capacity so that calm load is 0.65 with all 8 clients on.
- Each client alternates independently: on time exponential with mean 90 s (minimum 20 s), off time exponential with mean 30 s. All clients start on.
- Stimuli: capacity drops, gaps U(10, 15) s, default cells. If the tooling can compute the demand of the clients that are on at that instant, use demand / u. If not, drop to 60 % of nominal capacity and record the achieved u per window.
- `expected` for a window = the clients that are on for the whole window.
- Duration: 900 s.
- AQMs: pfifo, fq_codel.

## 6. Outputs per run and per campaign

Per run, in addition to what exists today:
- `windows.json` with the two new fields.
- For each onset source: final tree, per-flow membership score over time, event log with the case of each event.
- For each flow that became a member: the index of the event (among events it took part in) at which it became a member.

Per scenario report:
- Precision, recall and **coverage** (decided pairs / all pairs) side by side, per AQM and per onset source.
- Time to correct grouping in seconds and in number of events at that level of the tree.
- Number of confirmed cross-group pairs.
- sub-ctrl status.
- For fq_codel cells: results against both truths (same tight link; event-level co-congestion).
- Windows flagged `concurrent` scored separately from the rest.

## 7. Pass criteria (write to the repository before running)

Criteria apply to the shadow onset source unless stated. "Correct" means the leaves match the truth groups.

| Scenario | Criterion |
|---|---|
| K1, K2, K3, K5, K6 | Report only (development set). Flag any cell that got worse than in the previous campaign. |
| N1 | pfifo and pie: zero confirmed cross-branch pairs in all 5 reps; both leaves correct; precision and recall >= 0.95. fq_codel: number of cross-branch pairs reported, no threshold. |
| N2 | pfifo and pie: three groups correct, precision and recall >= 0.95, coverage >= 0.7, sub-ctrl ungrouped. Events-to-membership reported per group. |
| N3 | pfifo: same tree as K1 pfifo, for UDP and TCP windows separately. |
| N4 | Shared group precision and recall >= 0.9; at least 90 % of private windows end as solo events; sub-ctrl ungrouped. |
| N5 | sub-ctrl ungrouped; no client confirmed in a group while it was off. Reported without threshold: share of sessions with at least 3 events that became members, and at which event. |
| All fq_codel cells | No pass threshold; reported against both truths. |

## 8. Run counts and order

| Scenario | Runs |
|---|---|
| K1 | 15 |
| K2 | 24 |
| K3 | 24 |
| K5 | 12 |
| K6 | 10 |
| N1 | 15 |
| N2 | 15 |
| N3 | 10 |
| N4 | 10 |
| N5 | 10 |
| Total | 145 |

Suggested order: N1 (no new topology, answers the most urgent question), N2, then K1 to K6, then N3, N4 (needs the trace conversion script), N5.

## 9. Open points to confirm with the user

- Whether the testbed can run 17 clients (N2 full variant): I think yes
- Bitrates and capacity of the `large` topology (N5 is specified relative to it).
- Which specific Mahimahi and Norway trace files to use in N4, and whether the 5 to 15 % target is reachable with a single multiplier per trace:: i dont have any traces
- Whether the detector's OWD mode will be ready before K3 is scored; if not, score K3 with RTT now and re-score later: use OWD

---

## Implementation notes (2026-11-10)

Review of the implementation (same day), four decisions:
1. **Freeze and scoring order.** The engine is *not* frozen yet (rule changes
   under discussion: counting the episode end as an event, in-episode
   metrics). Grouping runs offline on the recordings, so the campaign runs
   now and the held-out set is **not scored until the rules are frozen**:
   N1–N5 get only the infrastructure check (`<run>/grouping/infra.json`,
   `<K>/infra.md`: finished, clients / sessions present, event errors, link
   event lag, windows in which the oracle saw the expected clients, clients
   never hit, control-client congestion). `--score-held-out` is the explicit
   switch for the grouping reports; `scoring.json` next to every report
   records the engine tree (`git describe`) used at scoring time, `plan.json`
   the tree the run was planned from. Rule changes are tried on K1–K6 only,
   then frozen and tagged, then N1–N5 are scored once.
2. **OWD is the main signal.** `shadow-owd` is scored on every run and the
   pass criteria are evaluated on it (`PRIMARY`); the RTT shadow stays as the
   comparison row, with its own criteria block in the held-out reports. Where
   the OWD comes from: the publisher's `<sub>-owd.csv`, written sender-side
   from mvfst's ACK receive timestamps (QUIC ACK receive timestamps extension,
   draft-02, 1 µs; the client sends each packet's receive time in its ACKs
   relative to its connection start, both ends share one CLOCK_MONOTONIC in the
   emulation), not from client logs. `owd_mode.owd_acks` replaces each ACK's
   `rtt_us` by the 5 ms send-bin minimum OWD + R0 (min RTT − min OWD over the
   first 10 s) and `min_rtt_us` by its trailing 10 s minimum. Validation
   status: the OWD mode was scored against GT1, GT2 and GT3 on the detector
   campaigns (recall unchanged, precision +0.01, false alarms −25 to −35 %/min,
   latency +5 to +8 ms, delaystep false alarms halved; `.runs/2026-11-05_owd-mode.md`),
   but it runs with the thresholds tuned for RTT (`det_eval.TUNED`); R0 keeps
   the input on the RTT scale, no OWD-specific re-tuning was done.
3. **N5 has no competitor columns.** DCW / rmcatSBD / dcSBD build one flow
   table over the common time span of all clients (`sbd_baselines.flow_table`)
   and classify fixed flow sets; with sessions the common span is empty and
   the methods have no notion of a flow that leaves and returns. Rather than a
   half comparison, `CAMPAIGNS["N5"]["baselines"] = False` and the report says
   so.
4. **Traces and tc timing.** `configs/traces/README.md` lists the files used,
   their sources and the citations. The infrastructure check reports the lag of
   every applied link event (`applied_s − at_s`, p50 / p99 / max, overall and
   for the `trace` label) and flags an N4 run whose trace lag exceeds 50 ms
   (`TRACE_LAG_MAX_S`; a lag of a whole 200 ms step would be invisible in the
   replayed shape): then the replayed capacity differs from the trace and the
   private truth windows shift. The check was exercised on a 44-event run
   only (max lag 1.9 ms); an N4 run issues 4 000–12 000 commands, so the first
   N4 `infra.md` is the real test.
5. **Clock skew and timestamp noise on the OWD** (still open). Both ends share
   one clock in the emulation. Since the grouping runs on recordings, the
   experiment needs no new runs: perturb `<sub>-owd.csv` offline (per-client
   skew in ppm plus timestamp jitter) before `owd_mode.owd_acks`, re-score
   `shadow-owd` on K1–K6, report the sensitivity. Listed in TODO.md.

Second review (same day), decided by the user:
6. **Truth independent of the detector's input.** The OWD-mode detector reads
   the ACK receive timestamps; the measured truth, GT3 (source A) and the
   grouping truth read the same OWD. The grouping truth therefore moved to
   **GT1 router standing-queue episodes** on the window's egress (`hop`, now
   written by the planner; older runs derive it from the expected set):
   expected clients are hit when the egress has an episode inside
   [start, end + 2 s]. Under fq_codel the router cannot tell which flows
   queued, so the router truth counts every expected client; the **GT3
   per-client truth is the secondary column** ("GT3 P / R", noted as sharing
   the detector's signal). Checked on K1 pfifo r1 (`.runs/old/ip8/2026-11-06_1526_grp`): 78/78 windows
   hit, same leaves and P/R as the old oracle truth.
7. **Per-ACK OWD for the detector.** `owd_mode.owd_acks` worked per ACK row but
   took the 5 ms send-bin minimum of `<sub>-owd.csv`, which can include packets
   acked a few ms later (lookahead), and ignored timestamp coverage. The
   publisher's `AckRecorder` now writes `owd_us` = the largest newly acked
   packet's own receive-timestamp OWD (empty when the ACK carried no
   timestamp; ACK loss and the 64-timestamps-per-ACK limit show up as gaps,
   as they would live); `owd_mode` prefers it and falls back to the bins on
   older runs. qvideo rebuilt 2026-11-10 (`qvideo-selftest ok`); the shadow
   replay reads columns by name, unchanged.
8. **Copa dropped** (user decision). For the record: under Copa mvfst reports
   `bbr_bw_bps` 0, no phase and `app_limited` false, so the shadow's excess,
   bbr_bw_drop, phase masks and app_limited_exit are inert and only the
   delay, loss and send_queue signals remain.
9. **AQMs.** `cake` added (`AqmKind.cake`, `cake unlimited besteffort` under
   the HTB class; it sizes its own buffer, `queue_limit_packets` is not
   applied). Microbenchmarks run on pfifo, red, pie and cake; fq_codel stays in
   the core set. `delaystep` removed from `run_campaigns.sh`.

Smoke runs first: `--ks N2 --only pfifo-r1` (17 clients on the host) and
`--ks N4 --only pfifo-r1` (tc keeps up), read `infra.md`, then the full set
with `--skip-existing` into the same campaign directory.

Everything runs from `scripts/grouping_campaign.py` (`--plan` writes the YAMLs
and the budget; default `--ks` is the suggested order N1,N2,K1,K2,K3,K5,K6,N3,
N4,N5; `--reps` is taken from the campaign: K 3, K6 and N 5). Each run folder
gets `grouping/windows.json` (with `stimulus_type`, `concurrent`) and
`grouping/plan.json` (campaign, type, topology variant, seed, `git describe`
of the tree the run was planned from, N4 trace metadata). Budget: 145 runs,
20.7 h of emulation plus about 1 min setup each.

Open points, decided:
- **17 clients (N2).** The full variant (`detector-uneven.yaml`, type
  `uneven`) is the campaign default. The reduced one exists as type `uneven6`
  (`detector-uneven6.yaml`, branch C = 1, 2.5, 2.5, 5, 5, 8 Mb/s, 38.0 Mb/s,
  180 packets); switch with `--ks N2` after editing `CAMPAIGNS["N2"]["types"]`
  or run `uneven6` as an extra type. The run id and `plan.json` name the
  variant. Per-egress queue limits (A 98, B 143, C 297 packets ≈ 57 ms) are
  kept by `apply_aqm`, which now preserves the base file's `egress` limits and
  sets RED thresholds at each egress's own capacity.
- **`large` topology (N5).** `detector-large.yaml`: 8 clients at 1, 2.5, 2.5,
  5, 5, 8, 8, 12 Mb/s (wire demand 45.3 Mb/s), bottleneck 70 Mb/s in
  `det-burst-large.yaml` (u = 0.647 with all 8 on; kept). Drops are sized to
  the demand of the clients on for the whole window (`demand_on_mbps / u`,
  recorded in the window), so the first option of the spec applies.
- **Traces (N4).** None were on hand; `scripts/trace_prepare.py` downloads
  the 8 public Mahimahi `.down` traces (github.com/ravinet/mahimahi) and 12
  Norway HSDPA logs (two per route: bus, metro, tram, ferry, car, train; UMass
  mirror of datasets.simula.no/hsdpa) and writes them as 200 ms capacity steps
  to `configs/traces/*.csv` (+ `index.json` with source, duration, mean). The
  pool is the 6 LTE traces plus the 12 Norway logs (Verizon-EVDO and
  TMobile-UMTS are 3G, 10–16 % zero steps, prepared but not used); the 18
  names are shuffled per seed; the four clients of a run get four different
  traces from a seeded offset, wrapped around when the trace is shorter than
  600 s (traces range 120–2709 s). Scaling: multiplier = 2 × wire rate / mean
  of the used segment; if the time below the wire rate falls outside 5–15 %,
  the multiplier is re-set so 10 % of the steps are below (`adjusted: true`
  in `plan.json`, final multiplier and fraction recorded). Replay = one `link`
  event per 200 ms step whose rate changed (floor 0.1 Mb/s, tc cannot shape to
  zero); 600 s × 4 clients gives up to 12 000 `tc class change` commands per
  run, serialized by the scenario runner. Private truth windows are the
  runs of steps below the wire rate, dips closer than 1 s merged into one
  window as alarm flaps are (`stimulus_type: trace`, `expected` = that
  client); the OWD oracle confirms the hit as for every window. Citations: Netravali et al. (USENIX ATC 2015) / Winstein et al.
  (NSDI 2013) for Mahimahi; Riiser, Vigmostad, Griwodz, Halvorsen (MMSys 2013)
  for the Norway dataset.
- **OWD shadow.** Source `shadow-owd` in `grouping_adapter.py`: the frozen
  shadow replayed on `owd_mode.owd_acks` (rtt_us := one-way delay of the
  acked packet + R0). Scored on every run and the primary source (decision 2
  above). `revcross` stays in the grouping table as a negative-control row
  (expected: no leaf); the detector section is the user's.

Testbed changes needed by N5 (re-join):
- `quiclab/config/scenario.py`: a subscriber's join / leave events may repeat,
  alternating in time (on at t=0 unless the first event is a join);
  `Scenario.sessions(sid)` lists `(join, leave)` per session,
  `Scenario.session_id(sid, n)` is `sid` for the first session and `sid@n`
  afterwards.
- `quiclab/orchestrator/mininet_backend.py`: a re-joined client is launched
  with `--id=<sid>@<n>`, so the publisher writes `<sid>@<n>-acks.csv` etc. and
  the first session's files survive (the server opens `<id>-*.csv` with
  truncation). Its log is `logs/<sid>@<n>.log`; the events.csv join row
  carries the id.
- `scripts/det_eval.py active()` follows the alternating sessions (used by the
  detector's demand model only).
- `scripts/grouping_adapter.py`: `load_run` returns a `SessionRun` when
  `<sid>@*-acks.csv` files exist: every session is a flow of its own (the ECG
  sees a new flow per session, as a real session-level grouper would), the
  topology gets an alias node per session so the path helpers work unchanged.
  `det_eval.score` still reads the topology's client ids, i.e. the first
  session only (a limit of N5's detector tables, not of the grouping scores);
  the SBD baselines are switched off for N5 (decision 3 above).

Outputs added for section 6 (`grouping_adapter.outcome_metrics`, in
`metrics.json` and the campaign summary): `series` (per-flow L over event
closes; `L.png` plots it), `membership_events` (per flow, events it took part
in up to the close after which it was reported a member), `tree_correct`
(confirmed leaves with ≥ 2 reported members == truth groups), `leaves_truth`,
`ctrl_grouped`, `precision_link` / `recall_link` (both truths, every cell),
`private_windows` {n, solo, silent, grouped} (N4, K5), `sessions`,
`off_membership` (snapshots in which a session was a reported member of a
confirmed leaf before its join or after its leave + 2 s) and `session_stats`
(N5). The report prints the section-7 verdicts first (PASS / FAIL per run with
the failing values), then the per-cell table with cov, link P/R, cross
(confirmed cross-group pairs = shadow fp, median / max), ctrl, tree,
ev->member, then the case matrices with `(concurrent)` windows as separate
rows and N3 cells split by stimulus type (`a:udp`, `a:tcp`, ...), then per
run. `--compare <old campaign dir>` flags development-set cells whose median
shadow precision or recall fell by more than 0.05 against the old
`results-v12.json`.

Deviations from the letter of the spec, stated here rather than hidden:
- N3 "same tree as K1 pfifo, for UDP and TCP windows separately": the final
  tree is one per run, so the check is tree_correct on the run plus the case
  matrix per stimulus type (an A / GLOBAL distribution per type). The achieved
  TCP load per window is not written back into `windows.json`; the iperf3
  interval CSVs under `<run>/traffic/` hold the per-second throughput.
- N4 "confirmed by the OWD oracle": the private windows are written from the
  plan (the trace below the wire rate) and the hit rule confirms them, as for
  every other window; `plan.json` carries the planned below-fraction. "90 % of
  private windows end as solo events" is judged among the private windows in
  which the client fired at all (solo / (solo + grouped)); windows with no
  event (a 200 ms dip the detector never sees) are counted as `silent` and
  reported, not judged, since silence is the detector's, not the grouping's.
- N5 "no client confirmed in a group while it was off" is measured on the
  engine's snapshots at event closes (the only times the state is reported),
  with a 2 s grace after the leave for the last in-flight event.
- The budget assumes the N2 full variant runs; the 17-client capacity of the
  host is checked by the first N2 run, not by this document.
