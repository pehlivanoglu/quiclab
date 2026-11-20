# K5-sender and re-runs: start sheet (prepared 2026-11-19 00:05; nothing started)

The user starts everything below. Plan unchanged (scripts/k5_suite.py: 142 runs + 5 gate, 20.74 h emulated).

## 0. Order

1. K3 finishes (`tail -3 .runs/2026-11-16_0105_v4-all/status.txt` shows `K3 done`); Claude runs the K3 health and
   overlap check (rule 3) and says when it is done.
2. **Re-runs and the 8 unrun K3 I1 runs first, before the rebuild**, with the same qvideo binary as K2 / K3
   (`qvideo/build`, built 2026-11-15 23:22, no adaptation code): 4 re-runs + 8 I1 runs (`ip1.2` -> run id `ip1p2`),
   12 runs, 1.39 h emulated, about 1 h 40 min wall. Claude does their health check before the rebuild.
3. Rebuild `qvideo/build` by hand (step 3 below): the runner always uses `qvideo/build/qvideo-server`, which has no
   `--adapt_x` yet. Without the rebuild every K5 run with adaptation would fail at the server's flag parsing.
4. K5: gate (5 runs) then 142 runs, about 24 h wall (K3: 20.84 h emulated, about 24 h wall, factor about 1.15).

Re-runs before K5 rather than inside or after: they then run on the binary their originals used, and K5 is not
interrupted. They go into their own folder; the originals are never touched.

## 1. Re-runs and the 8 I1 runs (updated 2026-11-19)

```
cd ~/Research/Repos/multirelay/quiclab
RR=.runs/$(date +%Y-%m-%d_%H%M)_v4-rerun; mkdir -p $RR; echo $RR
tmux new -d -s rerun "cd $PWD && .venv/bin/python3 scripts/rerun_v4.py --run --out $RR \
  v4-T2-sburst-jit5-pfifo-r2 v4-L2-fbcross-x80-codel-r2 v4-L11-spause-def-pfifo-r2 v4-C1-sjoin-copa-pfifo-r2 \
  v4-I1-calm-ip1.2-pfifo-r1 v4-I1-calm-ip1.2-pfifo-r2 v4-I1-hhier-ip1.2-pfifo-r1 v4-I1-hhier-ip1.2-pfifo-r2 \
  v4-I1-sburst-ip1.2-codel-r1 v4-I1-sburst-ip1.2-codel-r2 v4-I1-sburst-ip1.2-pfifo-r1 v4-I1-sburst-ip1.2-pfifo-r2 \
  2>&1 | tee -a $RR/run.log"
tail -f $RR/run.log          # watch;  resume after a stop: the same command with the same $RR (finished runs skip)
grep -c "^== v4-" $RR/run.log; ls $RR/v4-*/v3-checks.json | wc -l    # 12 / 12 when done
```

`scripts/rerun_v4.py` regenerates each run with the suite v4 planner unchanged and refuses to run unless the
regenerated plan / topology / scenario / windows files are identical to the original campaign's `_gen` files (only
the plan's recorded `git` field may differ). The I1 names are given as planned (`ip1.2`); the script runs them as
`ip1p2` (byte-identical copies of the files, only the name changes; mapping in reports/npr-2026-11-17/a4-rules.md).
Checked 2026-11-19 (plan only): 12 runs, 48 files identical (T2: only `git`), 32 renamed copies byte-identical.
`tee ... run.log` matters: the batch guard (`auto`) follows the newest `run.log`, so these runs are protected (all 12
match the no-batch pattern: T2, sjoin, I1, and the re-run entries).

## 2. Rebuild for K5 (after the re-runs, before K5)

```
cd ~/Research/Repos/multirelay/quiclab
.venv/bin/python3 -m quiclab build qvideo      # incremental: Server.cpp + SelfTest.cpp only, then qvideo-selftest
qvideo/build/qvideo-server --helpfull 2>&1 | grep -E "adapt_x|adapt_floor|send_buffer_ms"   # all three must show
```

The Docker image needs no rebuild: binaries and the Python package are bind-mounted (docker/Dockerfile).

## 3. K5

```
cd ~/Research/Repos/multirelay/quiclab
K5=.runs/$(date +%Y-%m-%d_%H%M)_v4-K5; mkdir -p $K5; echo $K5
tmux new -d -s k5 "cd $PWD && .venv/bin/python3 scripts/k5_suite.py --run --set K5 --campaign $K5 2>&1 | tee -a $K5/run.log"
tail -f $K5/run.log
# resume after a stop (gate is skipped once gate-report.md says PASS; finished runs are skipped):
tmux new -d -s k5 "cd $PWD && .venv/bin/python3 scripts/k5_suite.py --run --set K5 --campaign <same K5 folder> 2>&1 | tee -a <same K5 folder>/run.log"
```

A failed gate stops K5 (exit 3, `$K5/gate-report.md`); nothing else runs until a decision.

**After the gate (the gate does not check this itself):** the gate's adaptation run passes the health checks, but no
check asserts that adaptation acted. Claude checks it as soon as the run exists (`reports/k5-start/adapt_check.py`,
reading only) and reports at once if adaptation did not engage. The same look by hand:

```
f=$(find $K5/v4-GATE-sburst-adapt-* -name "*-adapt.csv" | head -1); echo $f; awk -F, 'NR>1 && $4<1' $f | wc -l
```

The file must exist and some rows must have `scale < 1` (target below nominal during the surges).

## 4. Duration and disk

| item | runs | emulated | wall (about) | disk (about) |
|---|---|---|---|---|
| K3 rest (from 00:00) | 62 | - | to ~06:30 | ~30 GB (534 MB per K3 run) |
| re-runs + I1 | 12 | 1.39 h | ~1 h 40 min | ~7 GB |
| K5 gate + campaign | 147 | 20.74 h | ~24 h | ~79 GB |

K5 disk by its reference cells: S-BURST runs (S1, S2, A1, gate) about 290 MB (K1 A2, K3 C1 sburst), S-PERSIST (P1)
about 580 MB (K2 N2), H-HIERL (G1-G3) about 1.2 GB (K1 A4, K3 C1 hhier): 84 x 0.29 + 28 x 0.58 + 30 x 1.2 + 5 x 0.4.
Free 2026-11-19 evening (re-checked before the start): **222 GB** -> about 216 GB at K5 start (after re-runs + I1, ~6 GB at
K3's measured 0.485 GB per run) -> **about 137 GB at K5 end**; with the A.4 validation's tick cache (~34 GB, under
reports/npr-2026-11-17/a4/valset/cache) during K5: about 103 GB, so K5 and the simulation's scale runs fit. Limits unchanged: warning below 50 GB, no batch / no run
below 30 GB. Standing rule: nothing under quiclab/ is deleted, moved or compressed to make room (caches
included); if space runs short, the numbers are reported and work stops until the user frees space.

## 5. Build and test check of the current tree (Claude, before K3 ends)

`reports/k5-start/build_k5.sh` (guarded batch, nice 19): compiles the current `Server.cpp` and `SelfTest.cpp` into
`qvideo/build-k5` with `qvideo/build`'s own compile and link commands (printed by `ninja -t commands`, outputs
redirected, dependency libraries only read; `build.ninja` / `.ninja_log` checksums compared before and after), runs
the new selftest (Adapt.h assertions), checks that the new server lists `--adapt_x`, `--adapt_floor`,
`--send_buffer_ms`, runs `tests/unit/test_k5_adapt.py`, and plans K5 into `qvideo/build-k5/plan-check`.
Result (2026-11-19 03:08): **pass**: build-k5 built, qvideo/build untouched, selftest ok, new server lists the three flags (old one only `send_buffer_ms`), test_k5_adapt.py 9 passed, K5 plans 147 runs. Log
`reports/k5-start/build-k5.log`.

Send-queue options: `send_buffer_ms` (0 = unlimited, 600, 1000, 3000) is existing code (K1-K3 ran 1000); schema
`ge=0, le=60000`; passed to the server on every run.

## 6. No-batch blocks for K5 (both sessions; in reports/batch_guard.py, loaded by every new guard)

| runs | why |
|---|---|
| S1, S2, A1 (S-BURST, 84 runs) | the sender-policy and adaptation comparisons, the campaign's main detector cells |
| every PIE cell (G1, G2 pie) | as in K1-K3 (PIE diagnosis open) |
| K5 gate (5 runs) | added 2026-11-19: includes the only adaptation check before the campaign |
| the three re-runs | added 2026-11-19: L2 x80 codel lost tracer events under batch load; T2 jit5 already blocked |

K5 time with batches allowed: 11.0 h of 20.74 h (53 %). The guard pattern is the source of truth; the running sim
guard still has the old pattern until it is restarted (its next batch loads the new one).

## 7. By hand before the start

- Confirm `K3 done` in the chain status and Claude's K3 health note.
- Re-runs + I1 runs (section 1), Claude's health check of them, then rebuild (section 2), then K5 (section 3).
- Disk check before K5 (`df -h /`, expect about 215-220 GB free).
- After the K5 gate: the adaptation look (section 3).

## 8. Rebuild done (2026-11-19 22:11, by Claude at the user's request; log reports/k5-start/rebuild-2026-11-19.log)

Exit 0; `qvideo selftest ok`; `qvideo-server --helpfull` lists `--adapt_x`, `--adapt_floor`, `--send_buffer_ms`.
**Deviation from section 2's "incremental: Server.cpp + SelfTest.cpp only":** ninja also recompiled four mvfst client
objects (QuicClientTransport.cpp, QuicClientTransportLite.cpp, FizzClientHandshake.cpp,
FizzClientQuicHandshakeContext.cpp) and relinked qvideo-client. Cause: the libc6-dev upgrade of 2026-11-13
(2.39-0ubuntu8.9 -> 8.12, /var/log/dpkg.log) installed /usr/include headers with mtime 2026-11-05, newer than those
objects (2026-11-01). The 2026-11-15 build relinked qvideo-server only, so the client was never rebuilt until now.
Same mvfst sources (mtime 2026-11-01, unchanged), same compile commands (ninja command hashes identical to the old
entries), same runtime libc (the shared library K3 already ran on). So K5's qvideo-client differs from the K1-K3 one
(linked 2026-11-10 18:38) only by being compiled against glibc 2.39's patch-release headers; the old client binary
was overwritten and cannot be rebuilt bit-identically (the old headers are gone). The K5 gate runs (CALM per CC per
topology + S-BURST adaptation) are the functional check of the new client.

## 9. Gate result (2026-11-19 22:38): PASS; adaptation engaged

gate-report.md: all five gate runs pass checks 1-6. adapt-check.md: every -adapt.csv exists, scale < 1 in every file,
lowest scale 0.300 (the floor) in every file. Split of the scale < 1 rows (read-only look, Claude): before the 5 s
warm-up (session start, low first estimate) 59-79 rows per client; inside a surge window (+3 s, display margin) sub-a
453, sub-b 1088, sub-c 1298, sub-d 1647; elsewhere 0-197. sub-ctrl only at session start. The floor after warm-up:
sub-a 2 rows, sub-b 138, sub-c 256, sub-d 632, sub-ctrl 0. So adaptation acted during the surges for every video
client; the floor counts in adapt-check.md include the start-up rows.
