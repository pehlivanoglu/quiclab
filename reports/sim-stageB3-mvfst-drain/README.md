# Stage B3: mvfst-style application-limited mark (patch 2), one-run check -- dropped

**Result: no effect. The patch is dropped; stage B3 was not run.**

Pre-declared attempt (user, 2026-11-18): patch 2 (`simulation/patches/dropped/ns3-tcp-app-limited-mvfst-drain.patch`)
repeats the application-limited check at the end of every `SendPendingData` write round, as mvfst does at the end of
its write loop. Prediction written before the check (patches/README.md): no or almost no effect, because
`delivered + inflight` does not change between the end of a write round and the next `Send()`.

Check (2026-11-19 03:08, job `simulation/runs/joblogs/mvfstcheck.sh`): one build (binary cb92cacb8758f83b, lib
internet dfea94be7ee164f1), v4-A1-calm-base-pfifo-r1, seed 1, ack-matched, run twice:

| run | vs B2 matched | file |
|---|---|---|
| patch 2 off (default) | 78 / 78 files byte-identical | default-vs-B2.md |
| patch 2 on (`NS_GLOBAL_VALUE=QuiclabAppLimitedAtDrain=1`) | 78 / 78 files byte-identical | mvfst-vs-B2.md |

The value was confirmed to reach the simulator: `quicsim --PrintGlobals` with that environment prints
`--QuiclabAppLimitedAtDrain=[true]`. The per-client table (onerun-check.md) is therefore identical for B2 and patch 2;
the keyframe queue peak in calm time stays 12.6 / 14.9 ms (p50 / p90) against the testbed's 14.1 / 16.9 ms.

Consequence: the remaining gap to mvfst in the keyframe peak and D1-bw delay is not caused by where the mark is set.
As decided, no further attempt without the user; the B2 use restrictions (sim-stageB2-applimited/README.md,
"may / may not be used for") stand unchanged.

Undone after the check: patch reversed in the ns-3 tree, `run.py --applimited` and the `mvfst` run set removed.
