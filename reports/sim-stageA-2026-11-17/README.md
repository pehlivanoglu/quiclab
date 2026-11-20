**Not usable: the FlowBot ns-3 environment (custom ns-3.27 in submodule `ns3/BBR_test`) is not on this machine and its repository no longer exists publicly; per decision 8.5 the simulation is built on mainline ns-3 (3.48), reusing FlowBot's scenario generator, PPBP parameters and the already-vendored baselines.**

# Simulation stage A: FlowBot environment inspection (2026-11-17)

Spec: [../../docs/simulation-spec.md](../../docs/simulation-spec.md), section 3. Answered from code; no ns-3
build, no simulation run. Only command executed: FlowBot's `config_generator.py` (pure Python, their venv,
`nice 19`, output in the session scratchpad, < 5 s). Nothing the campaign uses was touched.

## 0. What "the FlowBot environment" is on this machine

| piece | where | state |
|---|---|---|
| FlowBot repo | `multirelay/flowbot` (github.com/PrinceS17/flowbot, local HEAD a7a21fa, 2023-10-22; upstream has one newer commit 18c3418, 2026-11-08, README dataset link only) | present |
| ns-3 tree (their "customized modules", ns-3.27 + BBR + tracing + `scratch/brite-for-all`, edb program) | submodule `ns3/BBR_test` -> github.com/PrinceS17/BBR_test @ 2bc27be | **folder empty; repository returns 404** (deleted or private; `git ls-remote` fails). Not found anywhere on disk. |
| install recipe | github.com/PrinceS17/NS_Simulation_Toolkit (920fce8, 2023-07-30) `install.sh` | clones the same missing repo, plus BRITE from `hg code.nsnam.org` (service retired) |
| scenario generator | `flowbot/ns3/script/config_generator.py`, `inflator.py`, `multiRun.py` | present, runs (item 9) |
| models, classifiers, baselines | `flowbot/src` | present; already inspected and vendored ([../flowbot-inspection/README.md](../flowbot-inspection/README.md), [../../baselines/sbd/README.md](../../baselines/sbd/README.md)) |
| licence | none in either repo (only `sbd.py` carries the IETF BSD header) | internal use only until the authors answer (FLAG) |

The only way to inspect their ns-3 code is to ask the authors for `BBR_test` (they gave permission to reuse;
they may still have it). The recommendation in item 10 does not depend on it.

Side finding: `~/.local/share/Trash/files/simulation/.build/ns3` is a mainline **ns-3.48** git checkout
(tag `ns-3.48`, d2add90, 2026-06-02, origin gitlab.com/nsnam/ns-3-dev) left by an earlier moq-testbed
simulation that was deleted on 2026-10-27. Its working tree carries 51 local modifications from that
project; the git objects are intact, so the clean upstream files were read with `git show HEAD:<path>`.
All mainline facts below are from that tag.

## 1. Answers to the ten questions

| # | question | FlowBot ns-3 (theirs) | mainline ns-3.48 |
|---|---|---|---|
| 1 | version, build system, builds here? | ns-3.27 (2017), waf, python2-era PyViz; README tested on Ubuntu 20.04 / g++ 11.4. **Cannot build: source absent.** | 3.48, CMake (`./ns3 configure`). Not built yet (section 3: disk). Expected: core + network + internet + point-to-point + traffic-control + applications + stats + flow-monitor, optimized, `-j2`, roughly 30-60 min, about 1-2 GB build output, < 2 GB RAM per compiler job (estimate, not measured). |
| 2 | TCP CCs; BBR; pacing | ns-3.27 mainline had no BBR and no pacing; the repo name says BBR was added by them. Which BBR and how paced: unknown. | `TcpBbr` = **BBRv1** (Jain et al. port of Linux BBRv1: 4 modes, 8-phase gain cycle, HighGain 2.89, BwWindowLength 10 rounds, RttWindowLength 10 s, ProbeRttDuration 200 ms, extra-acked aggregation filter; no long-term/policer mode). Pacing in `TcpSocketState` (`EnablePacing` default false -> on; `PaceInitialWindow`; BBR sets the pacing rate itself). SACK on by default. Others: Cubic, NewReno, LinuxReno, DCTCP, Vegas, etc. Testbed runs mvfst `bbr` = BBRv1 modes (startup / drain / probe_bw / probe_rtt), so the mode names map 1:1. |
| 3 | queue discs; PIE / CoDel / FIFO / RED; ECN | from the generator: `C(pie codel)`, size in packets (100-500, large-2d 750); FIFO / RED not used by them | `FifoQueueDisc`, `PfifoFastQueueDisc`, `CoDelQueueDisc` (Target 5 ms, Interval 100 ms, MaxSize 1500 p, UseEcn false), `PieQueueDisc` (QueueDelayReference 15 ms, Tupdate 15 ms, MaxSize 25 p, A 0.125, B 1.25, dequeue-rate estimator selectable), `RedQueueDisc` (MinTh / MaxTh in packets, adaptive / gentle options), plus CoBALT, FQ-CoDel, FQ-PIE, DualPI2, TBF. ECN off by default everywhere. **Limits are packets or bytes, never time**: the spec's 50 ms pfifo limit and RED 15 / 45 / 150 ms become bytes from each egress capacity (FLAG, same conversion the testbed uses). |
| 4 | topology generator vs our trees | "extended dumbbell": `leaf -> gw -> left_mid -> right_mid -> gw -> leaf`, N left and M right bottleneck gateways, 1-3 leaves per gw, a flow has exactly two candidate queues (left, right). Topology itself built in their missing C++. | Our tree (publisher -> upstream -> leaf links -> per-client access) is a 3-level fan-out. Their dumbbell expresses T-BASE / T-SPLIT4(L) (left = upstream, right = leaves) but not per-client access links nor nested leaves of 2-200 clients. Needed in either code base: our own tree builder (point-to-point links, a queue disc on every egress we call a bottleneck, static routing). Small. |
| 5 | cross traffic | PPBP (their module, code missing). Generator parameters: Hurst `U(0.5 0.9)`, mean burst duration `N(0.547 0.1)` s, edge rate 1000 Mb/s, cross share 0.01-0.2 per link. | **No PPBP in mainline** (contrib PPBP modules are old). Our own `qvideo/src/Ppbp.h` (Hurst 0.8, the testbed's BG-BURSTY) is ported as an ns-3 application; Poisson UDP (BG-CBR) from `OnOff` with exponential on/off or a small custom app. |
| 6 | what they trace | `MboxStatistics/<type>_<mid>_<flow>.dat` / `.csv`: DataRate, AckLatency (owd), RttLlr (rtt + loss), cwnd, and per-queue length (`q_monitor = tx` on bottleneck links). Detector input = 5 ms grid `[owd, rtt, slr, cwnd, drop]`. Labels: from queue length, `get_truth_from_queue` (50 ms mean, larger of the two candidate queues, `-1` if both < 50 packets). | Trace sources available: socket `Tx`, `Rx`, `RTT`, `CongestionWindow`, `BytesInFlight`, `PacingRate`, `CongState`, `Retransmission`; BBR `MinRtt`, `PacingGain`, `CwndGain`; rate ops `TcpRateSampleUpdated` (app-limited flag, delivery rate); queue disc `Enqueue` / `Dequeue` / `Drop` / `PacketsInQueue` / `BytesInQueue`; device `MacRx`. BBR mode via public `TcpBbr::GetBbrState()`; bandwidth estimate = pacing rate / pacing gain (no patch to the model needed). |
| 7 | what is needed for (a) video app, (b) per-packet CSV, (c) BBR columns | all three new: their flows are rate-capped bulk flows with a YouTube-bitrate distribution `Y()` and delayed ACK 1 | (a) new `VideoSource` app: port of `qvideo/src/SendQueue.h` + the frame model (30 fps, GOP 1 s, I/P 4, sigma 0.2, 1000 ms drop-to-keyframe), writing to the socket only up to about one cwnd unsent (`GetTxAvailable` / bytes in flight). (b) sender `Tx` + receiver `MacRx`/socket `Rx` joined by TCP sequence number offline -> `-pkts.csv`, `-pktacks.csv`, `-acks.csv`, `-owd.csv` with the testbed headers; send time and arrival time from one simulator clock (idealisation, FLAG). (c) `-cc.csv` / `-acks.csv` columns from the trace sources in item 6; `phase` from `GetBbrState()`; mask derived exactly as on the testbed by the frozen code. |
| 8 | largest scenario: run time / memory | `large-2d` profile: 1000 flows, 1 left bottleneck (3 Gb/s) and 4-16 right bottlenecks (569-142 Mb/s), queue 750-188 p, 30 s, 4 runs. **Not runnable** (no ns-3). | Not measured (no build yet). Order of magnitude for stage C: 1000 clients x 0.75 Mb/s video plus BG at s 0.30 (BG = 2.33 x video) is about 2.5 Gb/s through the bottleneck egresses, about 2-4 x 10^5 packets/s, i.e. roughly 2-6 x slower than real time on one core; 900 s -> about 0.5-1.5 h per run (to be measured in the stage C smoke). |
| 9 | released models without `models.Pipeline`; scenario generator usable? | Models: yes, the detection path never uses `Pipeline`; the 2026-11-15 inspection ran FlowBot (both model files), DCW, rmcatSBD, dcSBD end to end with an in-memory stub of `models`; DCW / rmcatSBD / dcSBD are already vendored in `baselines/sbd/`. Generator: **runs** (`config_generator.py -p large-2d`, their venv, < 5 s) and writes their link / flow / cross CSVs with distributions (`N()`, `U()`, `C()`, `Y()`), inflated per run by `inflator.py`. The program that reads those CSVs is in the missing tree, so their published blocks can be re-created only by writing our own reader on mainline. | same |
| 10 | recommendation | see section 2 | |

## 2. Recommendation

**Build on mainline ns-3.48 with the spec's design** (decision 8.5). Reasons, in order:
1. Their ns-3 tree is not available; even if the authors send it, it is ns-3.27 (2017, waf, python2
   tooling) with an unknown BBR port, while mainline has a maintained BBRv1 matching the testbed's
   mvfst BBRv1 mode set, pacing, SACK, and all four queue types of the spec.
2. None of the stage B / C measures need anything specific to their code; FlowBot as a baseline
   needs only its released models on our traces (item 9).

Worth copying from FlowBot into `quiclab/simulation/third_party/flowbot-sim/` (unmodified, with
`PROVENANCE.md`): `ns3/script/config_generator.py` and `inflator.py` (their scenario grammar and PPBP /
cross parameters; used only if we re-create their published blocks in the FlowBot comparison).
Not worth copying: `multiRun.py` (waf launcher for their program), BRITE.

ns-3 source: either `git archive ns-3.48` from the trashed checkout (offline, tag-verifiable, 50 MB pack)
or a fresh `ns-allinone-3.48` / `ns-3-dev` tag download. Either way the tree goes under
`quiclab/simulation/` only, with our additions as a `contrib/` module or `scratch/` program plus patches,
never edits in upstream files.

## 3. Blocking before implementation (needs the user)

1. **Disk.** `/` has 10.3 GB free (19:13). K2 writes about 270 MB per 6-min run (53 GB so far for 98
   runs); with about 8.7 h of K2 planned left plus K3 after it, **the disk fills in about 2-4 h and
   kills the campaign**, independent of the simulation. Candidates the user may free (nothing deleted
   by me): `~/.local/share/Trash` 108 GB (of it `simulation/` 87 GB from the old moq-testbed, `multirelay-s`
   21 GB), `~/.cache` 42 GB, `quiclab/.runs/old-wrong-scenaris` 82 GB, `moq-testbed/.scratch` 18 GB.
   No ns-3 build until there is room for it (section 0: "check free disk before large runs").
   If the trashed `simulation/` folder is emptied, take the ns-3.48 source from a fresh download instead.
2. **Stage C output volume.** Per-packet records at 1000 clients are about 10^8 rows per 900 s run
   (several GB as CSV). Stage C will need compressed (or binary, converted per client on read) records,
   and GT-Q per-packet queue records only on a sample of egresses. Plan item for stage C, flagged now.
3. Order against the other queue (NPR 0b and steps 1-3, K1 scoring, K5 code): implementation and
   stage B are several days of coding plus about a day of 2-core runs. Waiting for the user's word.

## 4. Flags (section 10)

| item | difference | could move |
|---|---|---|
| BBR model | ns-3 `TcpBbr` is a Linux BBRv1 port; mvfst BBRv1 differs in details (startup exit, probe_rtt handling, app-limited sampling, ack aggregation) | detector calm sigma, D1-bw reaction time |
| ACKs | TCP delayed ACK (count 2, timeout set to 25 ms from the 200 ms default) vs QUIC ACK frequency; TCP has head-of-line blocking at the receiver | frame completion (hence GT3 from per-packet OWD, spec 4) |
| timestamps | arrival time from the simulator clock (ideal) vs the testbed's QUIC receive-timestamp extension | OWD noise, detection delay |
| queue limits | ns-3 queue discs size in packets / bytes; time limits converted with the egress capacity | keyframe queue peak under pfifo |
| PIE | ns-3 PIE (RFC 8033 with options) vs Linux `pie` defaults (burst allowance, dequeue-rate estimation) | PIE cells of stage B |
| licence | no licence in FlowBot repos | any release of copied code |

## 5. Constants introduced

None yet. (Defaults quoted above are ns-3's own; every value set in the implementation will be tagged.)

## 6. What this stage cannot tell

Whether the authors' BBR port behaves differently from mainline's; build time and per-run cost on
this machine (no build was made); whether their published FlowBot blocks re-create exactly on mainline.
