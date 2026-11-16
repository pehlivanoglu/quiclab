# Scenario and Topology Suite v4: hand-over (2026-11-15)

Spec: [spec.md](spec.md) (verbatim). Code: `scripts/v4_suite.py` (planner, runner; imports
`scripts/v3_suite.py` unchanged), `scripts/v4_checks.py` (path / pause / salvo checks),
`scripts/run_v4_smoke.sh`, `scripts/run_v4_campaign.sh`. Tests: `tests/unit/test_v4_suite.py`
(33). Full unit suite: 993 passed, 38 skipped, 2 xfailed.

**Nothing has been emulated.** You start the smoke and each campaign; the commands are below.

## 1. Commands

Run each one inside tmux.

```bash
# 1. Smoke (spec 7.2): 25 runs, 0.47 h emulated (~35-40 min wall). Writes smoke-report.md and nmax.json.
bash scripts/run_v4_smoke.sh
#   watch:   tail -f .runs/*_v4-smoke/run.log
#   result:  .runs/<ts>_v4-smoke/smoke-report.md   ("# Smoke: PASS" / "# Smoke: FAIL")
#            .runs/<ts>_v4-smoke/nmax.json         (n_max for K1; null = below 24, spec 9 FLAG)
#   resume:  bash scripts/run_v4_smoke.sh .runs/<ts>_v4-smoke

# 2. Campaigns (each starts with its gate block; exit 3 + gate-report.md on a failed gate check)
NMAX=<n_max> bash scripts/run_v4_campaign.sh K1      # 210 runs, 23.65 h emulated
bash scripts/run_v4_campaign.sh K2                   # 155 runs, 24.22 h
bash scripts/run_v4_campaign.sh K3                   # 203 runs, 20.87 h
#   watch:   tail -f .runs/*_v4-K1/run.log ; grep -E "^(==|!!|gate)" .runs/*_v4-K1/run.log
#   resume:  bash scripts/run_v4_campaign.sh K1 .runs/<ts>_v4-K1   (NMAX again for K1)
#   per run: <run>/v3-checks.json, <run>/v4-checks.json; at the end <campaign>/run-checks.{md,jsonl}

# Plan only (writes the YAMLs, prints budget, per-egress table, constraint flags, run list)
.venv/bin/python3 scripts/v4_suite.py --set K1 --plan-only --nmax 40 --campaign /tmp/v4-K1 > /tmp/v4-K1.md

# Held-out N1-N5 at DEF on v4 topologies: prepared, NOT to be run (60 runs, 10.83 h)
.venv/bin/python3 scripts/v4_suite.py --held-out --plan-only
# .venv/bin/python3 scripts/v4_suite.py --held-out --run       # later, after the freeze
```

The binaries `qvideo/build/qtraffic` and `qvideo/build/qvideo-server` are rebuilt on the host
(bind-mounted, as for v3); no image rebuild.

## 2. Budget (from the planner)

| campaign | gate runs / h | campaign runs / h | total h | spec h |
|---|---|---|---|---|
| K1 | 14 / 0.47 | 196 / 23.18 | 23.65 | 23.7 |
| K2 | 10 / 0.33 | 145 / 23.90 | 24.22 | 23.9 |
| K3 | 17 / 0.51 | 186 / 20.36 | 20.87 | 21.1 |
| **all** | 41 / 1.31 | 527 / 67.44 | **68.74** | 68.7 |

Every block of the spec is in; nothing dropped (no cut rule). Run counts per block equal the
spec except C1 (22, see 5.10) and L11 (10: + S-SHORT-RFC, decision 2026-11-15). Blocks off the spec's hours by >= 0.2 h: N4 2.73 h (spec 2.0),
N5 1.28 h (1.5), see 5.8 / 5.9.

Queue order: inside a campaign, all seed 1 in block order, then seed 2, and so on. X1-X3
(seeds 3-5) therefore run after seeds 1-2 of the other blocks. Seeds are the same across AQMs.
X1-X3 reproduce v3 exactly at rep 3-5 (same v3 builder and scenario code; only the run name
and the plan's `campaign` field differ).

## 3. Shared code changes (backward compatible)

v3 plans regenerate byte-identical (609 scenario / topology / window files of
`.runs/2026-11-14_1818_v3/_gen` compared).

1. **Subscriber `path`** (`quiclab/config/schema.py`): forced forward path publisher -> subscriber
   (validated: ends, links, no repeats). The backend installs the subscriber's /32 along it
   after the shortest-path routes; `mininet_backend._path_hops` and `det_eval.path_hops` return it
   for publisher -> subscriber. Only the forward direction is pinned (routes are per
   destination): T-HAYES ACKs take the shortest path back (unshaped reverse directions).
2. **`bg` `periods`** (poisson only): explicit on periods; BG-ONOFF.
3. **`salvo` event** + qtraffic `--process=salvo --proto=tcp --flows=start_s:bytes,...`: one
   connection per flow at its start, writes its bytes, closes; `<id>-flows.csv` per flow
   (planned start, connect, done, bytes sent, errno). The qtraffic TCP sink now accepts any
   number of connections (poll); for v3's one-connection `bg` TCP it counts the same bytes, but
   no longer exits when its connection closes (it stops at SIGTERM like the UDP sink).
4. **`pause` event** + qvideo-server `--pause=<client>@<start_s>+<d_s>,...`: no frame due in the
   window is produced for that client; production resumes at the first keyframe due at or after
   the end. Frames already queued at the pause start still drain (the sender queue is not flushed).
5. **Per-egress target point**: `v3_gate` check 1 and `v3_stimuli` (check 5's planned load) use an
   egress's own `s` / `U` from the plan when it has one (T-TEACUP up); every other plan is unchanged.

## 4. Spec section 9 flags

| flag | state |
|---|---|
| cells violating section 1 | none. Kept as in v3: M11 `bw4x12` (12000 kb/s = 27 % of 46.4 Mb/s; M11 keeps its own s / U) |
| n_max below 24 | decided by the smoke (`nmax.json`) |
| T-HAYES routing | realised with forced forward paths (3.1); the smoke and the K3 gate check that every group crosses exactly its four links (GT-Q trace destinations per bottleneck) |
| H-CHURN move | **skipped** (accepted 2026-11-15): a client host is wired to one switch, so it cannot reappear behind leaf b with the same identity; a client changing branch is not measured |
| Copa | available (mvfst `copa`; v3 M13 ran 4 runs and was read separately in `reports/copa-2026-11-15/REPORT.md`), C1 kept |
| RFC 8867 short TCP values | differ; S-SHORT keeps our Pareto model, S-SHORT-RFC added (decision 2026-11-15), see 5.1 |
| fq_codel / cake cells with no constrained flow | after each campaign (needs run data) |
| new hand-picked constants | listed (T) in 5 and tagged in the code |

## 5. Deviations and decisions made on your behalf

Constants are tagged in `scripts/v4_suite.py`: (S) spec, (M) measured, (T) my choice, (FLAG) yours.

1. **shorttcp (decided 2026-11-15).** S-SHORT keeps the Pareto model below: it is our own overload
   stimulus, not attributed to RFC 8867. New type **S-SHORT-RFC** (`sshortrfc`, K3 L11, T-BASE DEF, pfifo
   and codel, 2 seeds): 10 short TCP flows (2 start ON, 8 OFF), files uniform 30-50 kB, idle exponential
   mean 10 s, the whole 300 s run, no other stimulus, no truth window (scored like CALM: false alarms per
   client-minute, groups declared, next to CALM at DEF). One salvo event; a flow's next file starts one
   idle period after the previous file's start (T: a 30-50 kB file takes milliseconds here).
   Background: RFC 8867 section 5.7 gives 10 short TCP flows (2 start ON, 8 OFF),
   default TCP congestion control, 300 s, and refers the model to RFC 8868. RFC 8868 section 5.1
   gives files of "30-50 KB" and idle periods exponential with mean 10 s (its group has 30
   connections). Those values cannot carry the stimulus load: 10 flows x 40 KB per 10 s is
   ~0.3 Mb/s, against (u - U) C_e = 41-60 Mb/s at DEF. I kept the spec's model: salvos of 10
   CUBIC flows, Pareto sizes mean 500 kB shape 1.5 (not truncated), starts uniform over 2 s,
   salvos evenly spaced over [0, d - 2 s] until their bytes reach (u - U) C_e d. S-SHORT at
   DEF gives 110-170 flows per stimulus. The salvo process lives d + 10 s (T); later flows are cut.
2. **cold (T).** The FB-COLD surge is on from t = 0 for 30 s (FlowBot's run length); clients join
   at U(0.05, 3) s (a join at exactly 0 would be the initial launch); the run lasts 45 s.
3. **H-SHIFT (T).** The first surge of a phase starts 2 s into it, then U(10, 15) s gaps after each
   surge end; u from {1.15, 1.3}. Variant sustained: one persist from 10 s to 50 s into each phase
   (40 s, spec), u drawn from {1.15, 1.3}.
4. **S-PAUSE (T).** Pauses start on GOP boundaries (integer seconds, phase 0). Five pauses have
   their own slot in the sequence (no surge during them); the sixth starts at the next GOP
   boundary of the first 10 s surge and is cut to fit inside it. Every client is paused at least
   once; d alternates 5 / 20 s. Truth: per-client window, `expected` empty, no hop.
5. **T-TEACUP (accepted 2026-11-15: matches the original setup, shared link 2.5 x an access link).** The spec fixes C_leaf (calm 0.80) and C_up = 2.5 C_leaf = 53.6. The up
   background follows the v3 rule (24.0 Mb/s), so up's calm load is 0.64, not 0.80; the plan
   carries per-egress targets and check 1 uses them. Access delays 45 ms (+ 5 ms feed = 100 ms
   base RTT). Variant rev: r2 -> r1 at 10 Mb/s with a constant 9 Mb/s UDP background (always on,
   not a stimulus).
6. **T-HAYES.** The six stage links are router nodes `l12 .. l23`: the bottleneck is the egress
   R_i -> l_xx (with its own background pair); l_xx -> R_{i+1} is unshaped (1000 Mb/s, no AQM);
   R4 -> switch-gk keeps the default 100 Mb/s (load < 0.1). L1234 is R3 -> R4.
7. **FB-LAG.** The two far clients of each leaf get U(50, 210) ms one way, seeded per (seed, leaf).
8. **H-CONC** (accepted 2026-11-15) is 40 surges in sequence with v3's U(10, 15) s gaps: ~820 s, not ~600 s (N4 2.73 h).
9. **H-SPARSE** is 12 events with U(45, 75) s gaps: ~770 s, not ~900 s (N5 1.28 h).
10. **C1** (accepted 2026-11-15) has 22 runs from its own list (CALM DEF + EXT, S-TCP, S-JOIN, H-INDEPL, A-MIXED on pfifo:
    6; S-BURST x 3 AQMs; H-HIERL x 2; x 2 seeds), not the 24 of the table.
11. **M at DEF.** M7 (noroot) and M8 (mixab) run on T-SPLIT4L: T-SPLIT4 does not fit at DEF (up
    130 Mb/s). M13 is not in M (Copa is block C1).
12. **Held-out N5** at DEF: v3 `large` needs C 137 Mb/s; it uses the low set twice (8 clients) (T).
13. **NEG-PRIV** keeps A-MIXED's sub-d join at 60 s (only the shared surges are removed).
14. **Gate block.** One 120 s CALM per topology of the campaign (each T-LEAFn size counts as one;
    the M microbenchmark variants are not gated by topology), plus a 90 s run per new stimulus
    (persist, shorttcp, pause), the 45 s FB-COLD and a 90 s BG-ONOFF CALM where the campaign uses
    them. Gating: v3 checks 1-6 plus the v4 checks (path on T-HAYES, pause window, salvo connections).
15. **BG-ONOFF.** n = max(4, round(BG_e / 2.5)) sources per egress, each a separate qtraffic
    process with its own seeded on / off sequence (exp(1 s) each, random first state), on rate
    2 x BG_e / n, Poisson gaps while on. Mean checked within 10 % in the tests.
16. **Known limits of unchanged scoring code:** GT2's cause labels and det_eval's cross-traffic list
    do not know `salvo` events (GT2 episodes still come from router counters; their cause shows
    as not from a burst). D-CLEAN (no background for 60 s) and H-CHURN (absent clients) fail v3
    check 1 by construction; neither is in a gate.

## 6. Untested

- No v4 run has been emulated. Untested in Mininet: forced paths (the smoke's T-HAYES path check
  is the test), qtraffic salvo inside namespaces (loopback test only), qvideo-server `--pause`
  (built and flag-parsed only; the smoke's pause check reads frames.csv), BG-ONOFF processes with
  ~250 schedule entries, 32-client T-PAR4x8 and 40-client T-LEAF40 CPU load (the n_max search).
- After each campaign, spec section 8 (scoring) runs with the existing scripts, unchanged.
