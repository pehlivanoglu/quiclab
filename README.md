# quiclab: plain-QUIC synthetic video testbed

`quiclab` runs a YAML topology of QUIC video senders, clients, IP routers
(with AQMs), Linux-bridge switches and iperf3 cross traffic, all inside **one
privileged Docker container** with Mininet. Every node is a Mininet host, i.e.
its own network namespace. There is no MoQ: the sender is plain QUIC (mvfst),
so congestion control sees only the video and the path.

It is a fork of the moqlab router/link/AQM machinery (schema, routing,
shaping, router metrics, link schedule, designer, visualizer) with the MoQ
parts removed.

## Layout

```
quiclab/
├── deps/moxygen/           facebookexperimental/moxygen, pinned (see below)
├── qvideo/                 C++ sender/client (mvfst), CMake
│   └── src/  Common.h  Playback.h  Ppbp.h  SendQueue.h  Server.cpp  Client.cpp  Traffic.cpp (qtraffic)  SelfTest.cpp
├── quiclab/                Python package (`python -m quiclab`)
│   ├── cli.py              design / validate / build / run
│   ├── config/schema.py    Pydantic topology model
│   ├── orchestrator/       mininet_backend.py, routing.py, shaping.py
│   ├── config/scenario.py  Pydantic scenario model (conditions + events)
│   ├── orchestrator/scenario_runner.py  timed events -> events.csv
│   ├── designer.py visualizer.py router_metrics.py runtime.py
├── visualizer/             browser assets (designer + live visualizer)
├── configs/topologies/
│   ├── single.yaml  shared.yaml  cc-sweep.yaml  flowbot-like.yaml        standalone runs
│   └── detector.yaml  detector-large.yaml  detector-split.yaml           det_matrix, grouping campaigns
│       detector-access.yaml                                              private bottlenecks (isolate, K5)
│       detector-rev.yaml  detector-tree8.yaml                            grouping campaigns (K3 revcross, K6)
├── configs/scenarios/
│   ├── single-step.yaml  shared-cross.yaml  aqm-cc-sweep.yaml (coverage run)  flowbot-load-{070,080,090,100}.yaml
│   ├── det-capacity.yaml  det-cbr.yaml  det-ppbp.yaml                    fixed detector scenarios
│   └── det-burst.yaml  det-burst-large.yaml  det-burst-split.yaml  det-burst-access.yaml
│       grp-burst-tree8.yaml  grp-burst-rev.yaml
│                                                                         bases: the generators add the events
├── scripts/
│   ├── det_matrix.py  det_eval.py  det_plot.py                           detector matrix, scoring, figures
│   ├── grouping_campaign.py  grouping_adapter.py  grouping_baselines.py  grouping_synth.py   grouping K1-K6
│   └── sbd_baselines.py  owd_estimate.py  run_summary.py
├── grouping/               ECG shared-bottleneck grouping (see grouping/README.md)
├── baselines/sbd/          vendored SBD baselines DCW, rmcatSBD, dcSBD
├── docker/Dockerfile       the one image: mininet, iperf3, iproute2 6.17, runtime libs
└── tests/unit/             pytest, no root/Docker needed
```

## Dependencies

quiclab is self-contained. [facebookexperimental/moxygen](https://github.com/facebookexperimental/moxygen)
is a git submodule at `deps/moxygen`, pinned to `6b14c57d` (2026-10-29);
clone with `git clone --recursive https://github.com/pehlivanoglu/quiclab.git`
(`build qvideo` also initializes it). qvideo builds moxygen through its
`standalone/` CMake entry. That build fetches folly, fizz, wangle, mvfst and
proxygen at the commits pinned in `deps/moxygen/build/deps/github_hashes/`:

| dep | commit |
|-----|--------|
| folly | `41068ce3` |
| fizz | `60d6b223` |
| wangle | `0622f3d8` |
| mvfst | `4b691f3c` |
| proxygen | `8b295f9f` |

Only the targets qvideo links are compiled, inside `qvideo/build/_deps`. Why
not main: the next upstream commit (`399e61ba`, "Updating hashes") deleted
the folly/wangle/mvfst/proxygen pins, so the standalone build of main stops
at configure. The 19 later commits change only MoQ protocol code, getdeps
tooling and a WebTransport proxygen patch; nothing qvideo uses.

## qvideo

- **qvideo-server** (publisher): live synthetic video. Frames follow a
  wall-clock schedule (`fps`, keyframe every `gop_ms`, I-frame mean =
  `ip_ratio` x P-frame mean, mean-preserving lognormal size noise `size_sigma`,
  deterministic in `seed`). Every client of one rendition and phase gets the
  same frames. **One QUIC unidirectional stream per GOP.** Frames wait in a
  sender queue in front of QUIC and are handed over while QUIC's unsent data
  is below one cwnd; a frame older than `send_buffer_ms` (default 1 s of
  media) is dropped with the rest of its GOP and sending resumes at the next
  keyframe, as a live sender discards media past its deadline. The client
  counts such gaps as `skipped_frames`. The schedule is
  anchored at one stream start (T0, `--start_unix_us`): the orchestrator sets
  T0 `startup.stream_start_s` after the publisher launch, checks that every
  t=0 client connected before it, and makes T0 the scenario's t=0, so events
  hit the same point of the GOP grid in every run. A client that joins later
  tunes in at the next keyframe. Frames are produced on schedule whether or not the
  transport is ready, so a congested path builds a sender backlog the way a
  live encoder would, bounded by `send_buffer_ms`. CC: any mvfst controller (`bbr`, `bbr2`, `bbr2modular`,
  `copa`, `cubic`, `newreno`), pacing on, no GSO. One worker thread
  (EventBase) per client by default, capped by mvfst at the CPU count; the
  kernel's SO_REUSEPORT hash assigns connections to workers, so several
  clients can share one. Each connection's state lives on its worker only.
  Measured: 40 clients x 12 Mb/s cost ~0.4 cores in total, <= 4 % per thread.
- **qvideo-client** (subscriber): requests one fixed rendition on a bidi
  stream (`QV1 <id> <kbps> <phase_ms>`; the server checks it against its
  ladder), reads GOP streams, simulates playback with a fixed buffer
  (`buffer_ms`). The first frame plays after the buffer; a late frame stalls
  playback until it arrives.
- All namespaces share one kernel, so the sender's `CLOCK_REALTIME`
  timestamps give **exact one-way delay** at the client.

## Prerequisites

- Docker. Your user must be able to run `docker run --privileged`.
- Build toolchain and the system libraries moxygen's standalone build needs
  (`deps/moxygen/standalone/install-system-deps.sh` lists them): cmake,
  ninja, g++, OpenSSL, glog, gflags, double-conversion, libevent, libsodium,
  zstd, boost, fmt, c-ares, gperf.
- Host Python 3.11+ with `requirements.txt` for `design`, `validate` and the
  `run` launcher: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

## Usage

```bash
python -m quiclab build qvideo     # init pinned moxygen submodule, cmake + ninja + selftest -> qvideo/build/
python -m quiclab build image      # quiclab:latest
python -m quiclab validate -c configs/topologies/shared.yaml -s configs/scenarios/shared-cross.yaml
python -m quiclab design           # drag/drop topology designer on http://127.0.0.1:8765/
python -m quiclab run -c configs/topologies/shared.yaml -s configs/scenarios/shared-cross.yaml --vis
```

Long matrices run in tmux: `scripts/run_detector_matrix.sh`, or
`scripts/grouping_campaign.py`. If one stops, the same command with the same
tag / `--campaign` and `--skip-existing` keeps finished runs and restarts the
interrupted one.

`run` on the host starts `docker run --rm --privileged quiclab:latest` with
the checkout, the topology and scenario directories and the runs dir
bind-mounted at the same paths, plus `/lib/modules` (read-only, for
`modprobe sch_*` / `tcp_bbr`). Inside, the same command builds the topology,
applies the scenario's t=0 conditions, runs its events on time and tears
everything down at `duration_s` (Ctrl-C tears down early). `--cli` opens the
Mininet CLI instead (`sub-a ping pub`, `router tc -s qdisc show`, ...); the
scenario keeps running and exiting the CLI tears down. The qvideo binaries
and the Python code come from the mount, so code changes need no image
rebuild. `--vis` serves the visualizer on `http://127.0.0.1:8765/`: live
per-link rates, live link/AQM editing (recorded as `manual_*` events),
subscriber playback, and per-connection sender CC state (SRTT, min RTT,
cwnd, inflight, pacing rate from the mvfst pacer observer (0 = unpaced),
bandwidth estimate, losses, backlog).

## Run output (`.runs/<run-id>/`)

All outputs are CSV (no JSON on disk).

| path | content |
|------|---------|
| `topology.yaml`, `scenario.yaml` | config copies |
| `events.csv` | ground truth: `epoch` (t=0), every scenario event and live edit with planned `at_s`, applied time (`applied_s` from the epoch, monotonic and unix ns), target, detail, status, error; `end`, `teardown` |
| `publishers/<pub>/<sub>-frames.csv` | every frame sent: index, keyframe, size, send time, stream |
| `publishers/<pub>/<sub>-cc.csv` | sender CC samples every `stats_ms`, plus the sender queue (`queue_bytes`, `queue_age_us`), data QUIC has not sent yet (`quic_unsent_bytes`), their sum `backlog_bytes`, and `dropped_frames` |
| `publishers/<pub>/<sub>-owd.csv` | exact one-way delay of the video's own QUIC packets every 5 ms (FlowBot's step; runs before 2026-11-03: 10 ms) (bins of send time, gap-free grid): `packets_sent`, `packets_timed` (with a receive timestamp; the rest were lost or untimed), `owd_min_us` / `owd_mean_us` / `owd_max_us`. Oracle, not an estimate: the client reports each packet's receive time in its ACKs (QUIC ACK receive timestamps, IETF draft-02, 1 us) relative to its connection start, which it sends in its request; both ends share one CLOCK_MONOTONIC. Includes propagation + transmission + queuing. `--owd=false` on the server turns it off. Clients send a QUIC PING every 50 ms (`--ping_ms`): without an ack-eliciting packet the client never retires old ACK ranges, they fill its ACK packets after enough losses and the timestamps stop (runs before this fix: high-rate clients lose OWD coverage mid-run) |
| `publishers/<pub>/<sub>-owd-est.csv` | sender-side OWD estimate without an oracle, written by `scripts/owd_estimate.py` from `-acks.csv`: RTT sample minus min RTT (forward + reverse queueing), same 5 ms send-time grid as `-owd.csv`, one sample per ACK. Relative only (zero-mean it per window, as FlowBot does) |
| `publishers/<pub>/<sub>-acks.csv`, `-sent.csv` | per-ACK congestion-detector inputs (RTT sample, delivery rate, BBR estimate, cwnd, inflight, sender backlog, BBR phase, losses) and AppData bytes written, in the moq-testbed shadow replay format |
| `publishers/<pub>/<sub>-drops.csv` | every frame the sender queue dropped: index, GOP, size, age |
| `clients/<sub>-frames.csv` | every frame received: send/recv time, OWD, lateness vs playback |
| `clients/<sub>-playback.csv` | goodput, buffer, stalls, mean OWD every `stats_ms` |
| `router-metrics/<router>/<iface>*.csv` | qdisc counters and queue occupancy (`queue_metrics`) |
| `traffic/<flow>.csv` | iperf3 per-interval result (converted from iperf3's JSON, which is deleted) |
| `traffic/<id>-bursts.csv`, `-sent.csv`, `-recv.csv` | PPBP: every burst (offered-load truth); sent bytes and active bursts per 100 ms; received bytes, loss and one-way delay per 100 ms |
| `logs/` | stdout/stderr of every process |

Timestamps: `*_us` columns are `CLOCK_REALTIME` microseconds. `*_mono_ns` are
the monotonic clock (same kernel, so the same clock as the host).

## Topology (`configs/topologies/`)

What exists and how it is wired; no conditions. See
`quiclab/config/schema.py`.

- `publishers`: `listen_port`, `cc_algo`, `ladder_kbps`, `fps`, `gop_ms`,
  `ip_ratio`, `size_sigma`, `seed`, `stats_ms`, `workers`, `send_buffer_ms`
  (sender queue limit in media time, default 1000; 0 = unlimited).
- `subscribers`: `connects_to` (a publisher), `rate_kbps` (on its ladder),
  `phase_ms` (keyframe phase; equal phases mean in-sync keyframes),
  `buffer_ms`, `stats_ms`.
- `routers` (`queue_metrics`), `switches`, `links` (`from`, `to` only).
  Congestion belongs on router egresses: to put clients in one queue, send them
  through one router egress into a switch, which only distributes. A scenario
  `link` event cannot change the capacity of a switch egress. A client that needs
  a private bottleneck gets its own access router (`detector-access.yaml`).
- `traffic`: iperf3 `senders`, `receivers` and named `routes`. Each route gets
  its own /32 alias pair, so its flows follow exactly the declared path.

## Scenario (`configs/scenarios/`)

What the network does over one run. See `quiclab/config/scenario.py`.

- `duration_s`.
- `link_defaults`, `links`: t=0 conditions per link direction
  (`forward` = from→to, `reverse` = to→from): `bandwidth_mbps`, `delay_ms`,
  `jitter_ms`, `loss_pct`. Listed links lay their fields over the defaults;
  unlisted links get the defaults.
- `routers`: AQM per router (`aqm`: `dualpi2`, `red`, `pie`, `fq_codel`,
  `pfifo`; `dualpi2_target_ms`, `red_min_bytes`, `red_max_bytes`), applied to
  every router egress. `queue_limit_packets` sets the hard queue limit for any
  AQM (tc `limit`; RED converts it at 1500 B per packet); unset, the kernel
  default applies (pie 1000, fq_codel 10240, dualpi2 10000 packets).
  `egress: { <neighbor>: { aqm: ..., ... } }` replaces the whole queue on the
  egresses it names, e.g. a different AQM per downstream branch.
- `events` (each with `at_s`, optional `label`):
  - `link`: change one direction in place (`tc change`, queued packets
    survive). It can only change fields whose qdisc exists at t=0: give the
    direction a `bandwidth_mbps`, and `delay_ms` or `loss_pct: 0`, to keep it
    editable.
  - `aqm`: replace a router's AQM leaf on every egress (`router`, `aqm` +
    parameters); earlier `egress` overrides end unless the event declares its own.
  - `flow`: start an iperf3 flow (`id`, `route`, `duration_s`; `kind: tcp`
    with `cc`, `parallel`, or `kind: udp` with `rate_mbps`, `packet_size_bytes`).
  - `ppbp`: PPBP cross traffic from `qtraffic` (FlowBot-style): Poisson
    burst arrivals, Pareto burst lengths (shape 3 - 2·`hurst`), `burst_mbps`
    per active burst, long-run load `mean_mbps`, `mean_burst_s`, `seed`,
    `packet_size_bytes`, `route`, `duration_s`. The seed fixes every burst and
    the sender starts at exactly T0 + `at_s`, so runs repeat. Over a short run
    the realized load of a heavy-tailed process can differ from `mean_mbps`;
    `traffic/<id>-bursts.csv` gives the realized offered load.
  - `join` / `leave`: a subscriber connects late / stops. Subscribers without
    a `join` start at t=0; each joins and leaves at most once.

## Tests

```bash
python -m pytest            # unit tests, no root
qvideo/build/qvideo-selftest
```

Open work is in [TODO.md](TODO.md).
