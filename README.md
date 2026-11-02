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
│   └── src/  Common.h  Playback.h  Server.cpp  Client.cpp  SelfTest.cpp
├── quiclab/                Python package (`python -m quiclab`)
│   ├── cli.py              design / validate / build / run
│   ├── config/schema.py    Pydantic topology model
│   ├── orchestrator/       mininet_backend.py, routing.py, shaping.py
│   ├── config/scenario.py  Pydantic scenario model (conditions + events)
│   ├── orchestrator/scenario_runner.py  timed events -> events.csv
│   ├── designer.py visualizer.py router_metrics.py runtime.py
├── visualizer/             browser assets (designer + live visualizer)
├── configs/topologies/     single.yaml, shared.yaml, cc-sweep.yaml
├── configs/scenarios/      single-step.yaml, shared-cross.yaml, aqm-cc-sweep.yaml (coverage run)
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
  same frames. **One QUIC unidirectional stream per GOP.** A client joins at
  the next keyframe. Frames are written when they are "encoded", never when the
  transport is ready, so a congested path builds a sender backlog the way a
  live encoder would. CC: any mvfst controller (`bbr`, `bbr2`, `bbr2modular`,
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
| `publishers/<pub>/<sub>-cc.csv` | sender CC samples every `stats_ms` |
| `clients/<sub>-frames.csv` | every frame received: send/recv time, OWD, lateness vs playback |
| `clients/<sub>-playback.csv` | goodput, buffer, stalls, mean OWD every `stats_ms` |
| `router-metrics/<router>/<iface>*.csv` | qdisc counters and queue occupancy (`queue_metrics`) |
| `traffic/<flow>.csv` | iperf3 per-interval result (converted from iperf3's JSON, which is deleted) |
| `logs/` | stdout/stderr of every process |

Timestamps: `*_us` columns are `CLOCK_REALTIME` microseconds. `*_mono_ns` are
the monotonic clock (same kernel, so the same clock as the host).

## Topology (`configs/topologies/`)

What exists and how it is wired; no conditions. See
`quiclab/config/schema.py`.

- `publishers`: `listen_port`, `cc_algo`, `ladder_kbps`, `fps`, `gop_ms`,
  `ip_ratio`, `size_sigma`, `seed`, `stats_ms`, `workers`.
- `subscribers`: `connects_to` (a publisher), `rate_kbps` (on its ladder),
  `phase_ms` (keyframe phase; equal phases mean in-sync keyframes),
  `buffer_ms`, `stats_ms`.
- `routers` (`queue_metrics`), `switches`, `links` (`from`, `to` only).
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
  `pfifo`; `dualpi2_target_ms`, `queue_limit_packets`, `red_min_bytes`,
  `red_max_bytes`), applied to every router egress.
- `events` (each with `at_s`, optional `label`):
  - `link`: change one direction in place (`tc change`, queued packets
    survive). It can only change fields whose qdisc exists at t=0: give the
    direction a `bandwidth_mbps`, and `delay_ms` or `loss_pct: 0`, to keep it
    editable.
  - `aqm`: replace a router's AQM leaf (`router`, `aqm` + parameters).
  - `flow`: start an iperf3 flow (`id`, `route`, `duration_s`; `kind: tcp`
    with `cc`, `parallel`, or `kind: udp` with `rate_mbps`, `packet_size_bytes`).
  - `join` / `leave`: a subscriber connects late / stops. Subscribers without
    a `join` start at t=0; each joins and leaves at most once.

## Tests

```bash
python -m pytest            # unit tests, no root
qvideo/build/qvideo-selftest
```

Open work is in [TODO.md](TODO.md).
