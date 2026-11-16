"""GT-Q packet logging: router tracer lifecycle, raw trace conversion, sender-log
matching and the per-run health check.

One flag switches both halves of the logging (topology `gtq_logging`, default
on; the environment variable QUICLAB_GTQ_LOGGING=0 / 1 overrides it for a whole
campaign without editing YAML):

* router tracer: bpftrace (router_trace.bt) inside each router's netns, filtered
  in the kernel to the bottleneck egresses (rate-shaped, no netem, on a
  subscriber's forward path). Output: router-trace/<iface>-packets.csv, one row
  per packet leaving or dropped by that egress qdisc.
* sender log: qvideo-server --pkt_log, publishers/<pub>/<sub>-pkts.csv (pn, size,
  send time per packet) and <sub>-pktacks.csv (newly acked ranges per ACK).

The logging must never break or alter a run: every failure here is caught,
recorded in <run>/gtq-health.csv and marks the run gt_q_invalid; the run and the
old ground truths go on as if the logging were off.

Times: the tracer's nsecs and qvideo-server's mono_us are both CLOCK_MONOTONIC
(the container shares the host clock), the clock of router-metrics and events.csv.
"""

from __future__ import annotations

import csv
import io
import logging
import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

_log = logging.getLogger(__name__)

GTQ_ENV = "QUICLAB_GTQ_LOGGING"
TRACE_DIR = "router-trace"
HEALTH_FILE = "gtq-health.csv"
CPU_FILE = "host-cpu.csv"
SCRIPT = Path(__file__).with_name("router_trace.bt")

MTU_BYTES = 1500
ETH_HLEN = 14
# Router skb->len of a QUIC packet = its encoded size + UDP 8 + IPv4 20 + Ethernet 14.
QUIC_OVERHEAD_BYTES = 42
# Sender-log matches below this share of a flow's router packets are not trusted:
# t_obs falls back to the config method (a) for that flow.
MATCH_TRUST = 0.95
MATCH_LOOKAHEAD = 256        # sender packets skipped at most per router packet (loss before the router)
MATCH_MAX_DELAY_US = 2_000_000
NOHIT_GRACE_NS = 1_000_000_000  # nohit dequeues in the tracer's first second: enqueued before attach
# A later dequeue of the same skb address counts as a requeue of that packet only within
# this time of its first dequeue on the same interface; otherwise it is a different packet
# whose enqueue record went missing (seen in the first real run: 2 of 146 334 dequeues,
# 2.8 s after the address's previous use), kept as nohit (enqueue time unknown).
REQUEUE_MAX_NS = 100_000_000
# Late nohit dequeues up to this share of all dequeues are reported, not fatal.
NOHIT_MAX_SHARE = 1e-4
# Packet accounting rule (user, 2026-11-14, second version), per traced egress: unmatched
# dequeues and unmatched enqueues each <= max(UNMATCHED_MIN_ALLOWED, UNMATCHED_MAX_SHARE x
# dequeues), and at most UNMATCHED_MAX_200MS of either kind in any 200 ms window.
UNMATCHED_MAX_SHARE = 5e-5
UNMATCHED_MIN_ALLOWED = 3
UNMATCHED_MAX_200MS = 2


def unmatched_allowed(dequeues: int) -> float:
    return max(UNMATCHED_MIN_ALLOWED, UNMATCHED_MAX_SHARE * dequeues)
# Router packets shorter than this are not matched: the server's pure ACK packets
# (e.g. 90 B answering the client's PINGs) are not ack-eliciting, so mvfst never
# reports them to the sender log.
MATCH_MIN_LEN = 200
READY_TIMEOUT_S = 15.0
STOP_TIMEOUT_S = 20.0
DRAIN_S = 0.5

# bpftrace defaults (4096 map keys, 64 ring pages) are far too small for a router egress.
TRACER_ENV = {"BPFTRACE_MAX_MAP_KEYS": "262144", "BPFTRACE_PERF_RB_PAGES": "512"}

KINDS = {1: "dequeue", 2: "requeue", 3: "nohit", 4: "drop"}
ORPHAN_KIND = 5   # an enqueue record overwritten before its dequeue / drop was seen (router_trace.bt)
UNMATCHED_FILE = "{iface}-unmatched-enq.csv"   # enqueues never matched; never part of <iface>-packets.csv
UNMATCHED_WINDOW_NS = 200_000_000              # gate: unmatched packets per 200 ms window
WIN20_NS = 20_000_000                           # service check: bytes per 20 ms backlogged window
WIN_MIN_PKTS, WIN_PKT_BITS = 25, 12000           # (T, 2026-11-16) a window holds >= 25 full packets: below
                                                 # 15 Mb/s it is longer than 20 ms (one packet must stay
                                                 # well under the +-5 % tolerance; 9.8 Mb/s -> 30.6 ms)


def window_ns(cap_bps: float) -> int:
    """Length of a service-check window at capacity cap_bps: 20 ms, or the time of WIN_MIN_PKTS packets."""
    return max(WIN20_NS, int(round(WIN_MIN_PKTS * WIN_PKT_BITS / cap_bps * 1e9)))
# Per-gap tolerance (user, 2026-11-14): within max(10 % of ideal, GAP_TOL_FLOOR_NS). Dequeue timing
# has a rate-independent jitter of about +-4.5 us (p1 / p99, smoke 2, reports/v3-suite/smoke2/
# gap-jitter.md); 15 us is ~3x that and far below one packet time on the fastest link (101 us).
GAP_TOL_FLOOR_NS = 15_000
RAW_FIELDS = ("kind", "t_enq_ns", "t_ns", "ifindex", "eth_proto", "saddr", "daddr", "ip_proto",
              "sport", "dport", "len", "hash", "prio", "reason")
PACKET_FIELDS = ("kind", "t_enq_ns", "t_deq_ns", "t_drop_ns", "reason", "saddr", "daddr", "proto",
                 "sport", "dport", "len", "hash", "prio")
COUNTERS = ("n_enq", "n_deq", "n_drop", "n_requeue", "n_nohit", "n_batched", "n_truncated", "n_orphan")


def enabled(topology) -> bool:
    """The one GT-Q logging flag: QUICLAB_GTQ_LOGGING when set, else topology.gtq_logging."""
    value = os.environ.get(GTQ_ENV, "").strip().lower()
    if value:
        return value not in ("0", "false", "off", "no")
    return bool(topology.gtq_logging)


# ── tracer lifecycle (orchestrator side) ──────────────────────────────────

@dataclass
class Tracer:
    router: str
    ifaces: dict[int, str]              # ifindex -> interface name
    hops: dict[str, tuple[str, str]]    # interface -> (router, next node)
    raw: Path
    log: Path
    netns: int = 0
    process: subprocess.Popen | None = None
    started_ns: int = 0
    stopped_clean: bool = False
    errors: list[str] = field(default_factory=list)
    # Per BPF program of the tracer at stop: (prog_id, prog_type, recursion_misses) from
    # /proc/<pid>/fdinfo; a program that would nest on a CPU already running BPF is skipped
    # and counted only there (bpftrace's lost events do not include it). None: not read.
    prog_misses: list[tuple[int, str, int]] | None = None


def tracer_argv(raw: Path, netns: int, ifindexes: list[int]) -> list[str]:
    mask = sum(1 << i for i in ifindexes)
    return ["bpftrace", "-B", "full", "-o", str(raw), str(SCRIPT), str(netns), str(mask)]


def ensure_tracefs() -> str:
    """bpftrace reads tracepoint formats from tracefs; a fresh privileged container
    has /sys/kernel/tracing unmounted. Returns an error text or ''."""
    if Path("/sys/kernel/tracing/events/qdisc").exists():
        return ""
    status = subprocess.run(["mount", "-t", "tracefs", "nodev", "/sys/kernel/tracing"],
                            capture_output=True, text=True)
    if Path("/sys/kernel/tracing/events/qdisc").exists():
        return ""
    return f"tracefs unavailable: {status.stderr.strip() or status.returncode}"


def _attached(tracer: Tracer) -> bool:
    for path in (tracer.log, tracer.raw):
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        if "Attaching" in text or "# gtq-tracer start" in text:
            return True
    return False


def wait_ready(tracer: Tracer, timeout_s: float = READY_TIMEOUT_S) -> bool:
    """True once bpftrace reports its probes attached; records an error otherwise."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if tracer.process is None or tracer.process.poll() is not None:
            tracer.errors.append(f"tracer exited at start (status "
                                 f"{None if tracer.process is None else tracer.process.returncode})")
            return False
        if _attached(tracer):
            # "Attaching" is printed before the last probe is in; give it a moment.
            time.sleep(0.5)
            return True
        time.sleep(0.1)
    tracer.errors.append(f"tracer not attached after {timeout_s:g} s")
    return False


def prog_misses(pid: int) -> list[tuple[int, str, int]]:
    """(prog_id, prog_type, recursion_misses) of every BPF program fd the process holds."""
    out = []
    fdinfo = Path(f"/proc/{pid}/fdinfo")
    for f in sorted(fdinfo.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else -1):
        try:
            fields = dict(line.split(":", 1) for line in f.read_text().splitlines() if ":" in line)
        except OSError:
            continue
        if "prog_id" in fields and "recursion_misses" in fields:
            out.append((int(fields["prog_id"]), fields.get("prog_type", "").strip(),
                        int(fields["recursion_misses"])))
    return out


def stop(tracer: Tracer, timeout_s: float = STOP_TIMEOUT_S) -> None:
    """Read the programs' recursion misses, then SIGINT (bpftrace prints its counters and
    open maps and flushes), kill on timeout."""
    process = tracer.process
    if process is None:
        return
    if process.poll() is not None:
        tracer.errors.append(f"tracer died during the run (status {process.returncode})")
        return
    try:
        tracer.prog_misses = prog_misses(process.pid)
    except Exception as e:  # noqa: BLE001 - information only
        tracer.errors.append(f"recursion_misses not read: {e!r}")
    try:
        process.send_signal(signal.SIGINT)
        process.wait(timeout=timeout_s)
        tracer.stopped_clean = process.returncode == 0
        if not tracer.stopped_clean:
            tracer.errors.append(f"tracer exit status {process.returncode}")
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        tracer.errors.append(f"tracer ignored SIGINT for {timeout_s:g} s; killed (counters lost)")
    except Exception as e:  # noqa: BLE001 - never let the logging break teardown
        tracer.errors.append(f"tracer stop failed: {e!r}")


# ── host CPU sampler ──────────────────────────────────────────────────────

class CpuSampler:
    """Host-wide CPU idle share once per second from /proc/stat (the container
    sees the host's), written to <run>/host-cpu.csv. Cheap; never raises."""

    def __init__(self, path: Path, interval_s: float = 1.0) -> None:
        self._path, self._interval = path, interval_s
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="cpu-sampler", daemon=True)

    @staticmethod
    def _read() -> tuple[int, int]:
        with open("/proc/stat") as f:
            fields = [int(x) for x in f.readline().split()[1:]]
        idle = fields[3] + (fields[4] if len(fields) > 4 else 0)  # idle + iowait
        return idle, sum(fields)

    def _loop(self) -> None:
        try:
            with self._path.open("w") as out:
                out.write("mono_ns,idle\n")
                last = self._read()
                while not self._stop.wait(self._interval):
                    now = self._read()
                    total = now[1] - last[1]
                    if total > 0:
                        out.write(f"{time.monotonic_ns()},{(now[0] - last[0]) / total:.4f}\n")
                        out.flush()
                    last = now
        except Exception as e:  # noqa: BLE001
            _log.warning("cpu sampler stopped: %r", e)

    def start(self) -> "CpuSampler":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=3)


# ── raw trace -> per-interface packet CSV ─────────────────────────────────

def _ip(word):
    """Raw network-order IPv4 word (read little-endian) -> dotted strings."""
    import numpy as np
    w = np.asarray(word, dtype=np.uint64)
    parts = [(w >> s) & 255 for s in (0, 8, 16, 24)]
    return [f"{a}.{b}.{c}.{d}" for a, b, c, d in zip(*(p.tolist() for p in parts))]


def _port(word):
    import numpy as np
    w = np.asarray(word, dtype=np.int64)
    return ((w & 0xFF) << 8) | (w >> 8)


@dataclass
class RawTrace:
    records: object                       # pandas DataFrame with RAW_FIELDS
    counters: dict[str, dict[int, int]]   # counter -> ifindex -> value
    lost_events: int
    start_ns: int
    end_ns: int
    open_enq: dict[str, int] = field(default_factory=dict)   # skb address -> enqueue time (exit dump)
    open_if: dict[str, int] = field(default_factory=dict)    # skb address -> ifindex (exit dump)


def parse_raw(text: str) -> RawTrace:
    """Split bpftrace output into records, @n_* counters, lost-event notes and markers."""
    import pandas as pd
    rows: list[str] = []
    counters: dict[str, dict[int, int]] = {c: {} for c in COUNTERS}
    lost, start, end = 0, 0, 0
    open_enq: dict[str, int] = {}
    open_if: dict[str, int] = {}
    for line in text.splitlines():
        if not line:
            continue
        head = line[0]
        if head.isdigit():
            rows.append(line)
        elif head == "@":
            name, _, value = line.partition(":")
            key = name[1:].split("[")[0]
            index = name[name.index("[") + 1:name.index("]")] if "[" in name else "0"
            if key in counters:
                counters[key][int(index)] = int(value.strip())
            elif key == "enq":
                open_enq[index] = int(value.strip())
            elif key == "eif":
                open_if[index] = int(value.strip())
        elif line.startswith("# gtq-tracer start"):
            start = int(line.split()[-1])
        elif line.startswith("# gtq-tracer end"):
            end = int(line.split()[-1])
        elif "Lost" in line and "events" in line:
            for token in line.split():
                if token.isdigit():
                    lost += int(token)
                    break
    df = pd.read_csv(io.StringIO("\n".join(rows)), header=None, names=list(RAW_FIELDS),
                     dtype="int64") if rows else pd.DataFrame({c: pd.Series(dtype="int64") for c in RAW_FIELDS})
    return RawTrace(df, counters, lost, start, end, open_enq, open_if)


def packets_table(raw: RawTrace, ifindex: int):
    """One egress's packet rows: requeues folded into their first dequeue (the last
    dequeue time wins), raw words decoded, sorted by event time."""
    import numpy as np
    import pandas as pd
    df = raw.records[(raw.records["ifindex"] == ifindex) & (raw.records["kind"] != ORPHAN_KIND)].copy()
    req = df[df["kind"] == 2]
    if len(req):
        first_deq = df[df["kind"] == 1].drop_duplicates("t_enq_ns").set_index("t_enq_ns")["t_ns"]
        gap = req["t_ns"] - req["t_enq_ns"].map(first_deq)
        genuine = req[gap.notna() & (gap >= 0) & (gap <= REQUEUE_MAX_NS)]
        if len(genuine):
            last = genuine.groupby("t_enq_ns")["t_ns"].max()
            hit = (df["kind"] == 1) & df["t_enq_ns"].isin(last.index)
            df.loc[hit, "t_ns"] = np.maximum(df.loc[hit, "t_ns"], df.loc[hit, "t_enq_ns"].map(last))
        df.loc[req.index.difference(genuine.index), "kind"] = 3   # a different packet: enqueue unknown
        df = df[df["kind"] != 2]
    ipv4 = df["eth_proto"].to_numpy() == 8  # ETH_P_IP in network order, read little-endian
    out = pd.DataFrame({
        "kind": df["kind"].map(KINDS).to_numpy(),
        "t_enq_ns": np.where(df["kind"] == 3, -1, df["t_enq_ns"]),
        "t_deq_ns": np.where(df["kind"] != 4, df["t_ns"], -1),
        "t_drop_ns": np.where(df["kind"] == 4, df["t_ns"], -1),
        "reason": df["reason"].to_numpy(),
        "saddr": np.where(ipv4, _ip(df["saddr"]), ""),
        "daddr": np.where(ipv4, _ip(df["daddr"]), ""),
        "proto": np.where(ipv4, df["ip_proto"], -1),
        "sport": np.where(ipv4, _port(df["sport"]), -1),
        "dport": np.where(ipv4, _port(df["dport"]), -1),
        "len": df["len"].to_numpy(),
        "hash": df["hash"].to_numpy(),
        "prio": df["prio"].to_numpy(),
    })
    out["_t"] = np.where(out["t_deq_ns"] >= 0, out["t_deq_ns"], out["t_drop_ns"])
    return out.sort_values("_t", kind="stable").drop(columns="_t").reset_index(drop=True)


def unmatched_enqueues(raw: RawTrace, ifindex: int):
    """Enqueues of one egress that were never matched to a dequeue or a drop: `orphan` (the
    record was overwritten by a later enqueue of the same skb address, at t_seen_ns) and
    `open_at_exit` (still open when the tracer stopped: queued at stop, or dequeue missed).
    Kept apart from <iface>-packets.csv, so the GT-Q labeler never sees them."""
    import pandas as pd
    o = raw.records[(raw.records["kind"] == ORPHAN_KIND) & (raw.records["ifindex"] == ifindex)]
    rows = [{"kind": "orphan", "t_enq_ns": int(a), "t_seen_ns": int(b)} for a, b in zip(o["t_enq_ns"], o["t_ns"])]
    rows += [{"kind": "open_at_exit", "t_enq_ns": t, "t_seen_ns": raw.end_ns}
             for addr, t in raw.open_enq.items() if raw.open_if.get(addr) == ifindex and t > 0]
    return pd.DataFrame(rows, columns=["kind", "t_enq_ns", "t_seen_ns"]).sort_values("t_enq_ns", kind="stable")


def read_packets(path: Path):
    """router-trace/<iface>-packets.csv as a DataFrame (-1 = no value)."""
    import pandas as pd
    return pd.read_csv(path, dtype={"saddr": str, "daddr": str}, keep_default_na=False)


def finalize(run_dir: Path, tracers: list[Tracer]) -> list[dict]:
    """Convert every tracer's raw output into per-interface packet CSVs plus
    router-trace/tracer-counts.csv; delete a raw file only after its conversion."""
    trace_dir = run_dir / TRACE_DIR
    counts: list[dict] = []
    for tracer in tracers:
        if not tracer.raw.exists():
            tracer.errors.append("no raw tracer output")
            for ifindex, iface in tracer.ifaces.items():
                counts.append(_count_row(tracer, ifindex, iface, None, None))
            continue
        try:
            raw = parse_raw(tracer.raw.read_text(errors="replace"))
            if tracer.log.exists():  # bpftrace may report lost events on stderr
                raw.lost_events += parse_raw_notes(tracer.log.read_text(errors="replace"))
            for ifindex, iface in tracer.ifaces.items():
                table = packets_table(raw, ifindex)
                table.to_csv(trace_dir / f"{iface}-packets.csv", index=False, columns=list(PACKET_FIELDS))
                unmatched = unmatched_enqueues(raw, ifindex)
                unmatched.to_csv(trace_dir / UNMATCHED_FILE.format(iface=iface), index=False)
                counts.append(_count_row(tracer, ifindex, iface, raw, table, unmatched))
            tracer.raw.unlink()
        except Exception as e:  # noqa: BLE001
            tracer.errors.append(f"conversion failed: {e!r} (raw kept: {tracer.raw.name})")
            for ifindex, iface in tracer.ifaces.items():
                counts.append(_count_row(tracer, ifindex, iface, None, None))
    _write_rows(trace_dir / "tracer-counts.csv", counts)
    return counts


def parse_raw_notes(text: str) -> int:
    return sum(int(tok) for line in text.splitlines() if "Lost" in line and "events" in line
               for tok in line.split()[:3] if tok.isdigit())


def _count_row(tracer: Tracer, ifindex: int, iface: str, raw: RawTrace | None, table, unmatched=None) -> dict:
    row = {"router": tracer.router, "iface": iface, "ifindex": ifindex,
           "started": int(tracer.started_ns > 0), "stopped_clean": int(tracer.stopped_clean),
           "tracer_start_ns": raw.start_ns if raw else 0, "tracer_end_ns": raw.end_ns if raw else 0,
           "lost_events": raw.lost_events if raw else -1}
    for c in COUNTERS:
        row[c] = raw.counters[c].get(ifindex, 0) if raw else -1
    if table is not None:
        # rows as written by the kernel side (before folding requeues): checked against its counters
        kinds = raw.records.loc[raw.records["ifindex"] == ifindex, "kind"].value_counts()
        row.update({f"rows_{KINDS[k]}": int(kinds.get(k, 0)) for k in (1, 4, 3, 2)})
        row["requeue_stale"] = int((table["kind"] == "nohit").sum()) - row["rows_nohit"]
        late = table[(table["kind"] == "nohit") & (table["t_deq_ns"] > raw.start_ns + NOHIT_GRACE_NS)]
        row["nohit_late"] = len(late)
        row["oversize"] = int((table["len"] > MTU_BYTES + ETH_HLEN).sum())
        # unmatched packets (gate check 4a): dequeues without an enqueue record, enqueues never
        # dequeued or dropped; most per 200 ms window of trace time
        unm_deq = table.loc[table["kind"] == "nohit", "t_deq_ns"].to_numpy()
        unm_enq = unmatched["t_enq_ns"].to_numpy() if unmatched is not None else []
        row["unmatched_deq"] = len(unm_deq)
        row["unmatched_enq"] = row["n_enq"] - row["n_deq"] - row["n_drop"]
        row["unmatched_enq_rows"] = len(unm_enq)
        row["unmatched_deq_max_200ms"] = _max_per_window(unm_deq, raw.start_ns)
        row["unmatched_enq_max_200ms"] = _max_per_window(unm_enq, raw.start_ns)
    else:
        row.update({"rows_dequeue": -1, "rows_drop": -1, "rows_nohit": -1, "rows_requeue": -1,
                    "requeue_stale": -1, "nohit_late": -1, "oversize": -1, "unmatched_deq": -1,
                    "unmatched_enq": -1, "unmatched_enq_rows": -1, "unmatched_deq_max_200ms": -1,
                    "unmatched_enq_max_200ms": -1})
    row["errors"] = "; ".join(tracer.errors)
    return row


def _max_per_window(t_ns, start_ns: int = 0) -> int:
    """Most events in any 200 ms window [t, t + 200 ms) (sliding; it suffices to start windows
    at the events themselves)."""
    import numpy as np
    t = np.sort(np.asarray(t_ns, dtype=np.int64))
    if not len(t):
        return 0
    return int((np.searchsorted(t, t + UNMATCHED_WINDOW_NS, side="left") - np.arange(len(t))).max())


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


def rows_match(row: dict) -> tuple[bool, str]:
    """The rows written equal the kernel side's counters (no record lost on the way)."""
    if row["n_enq"] < 0:
        return False, "no counters"
    rows = (row["rows_dequeue"], row["rows_drop"], row["rows_nohit"], row.get("rows_requeue", row["n_requeue"]))
    kernel = (row["n_deq"], row["n_drop"], row["n_nohit"], row["n_requeue"])
    if rows != kernel:
        return False, f"rows (deq, drop, nohit, requeue) {rows} != kernel counters {kernel}"
    return True, ""


def accounting(row: dict) -> tuple[bool, str]:
    """The packet accounting rule on one egress (UNMATCHED_*)."""
    allowed = unmatched_allowed(row["n_deq"])
    bad = []
    for kind in ("deq", "enq"):
        n, w = row.get(f"unmatched_{kind}", -1), row.get(f"unmatched_{kind}_max_200ms", -1)
        if n < 0 or w < 0:
            return False, "no unmatched counts"
        if n > allowed:
            bad.append(f"unmatched {kind} {n} > allowed {allowed:g} (of {row['n_deq']} dequeues)")
        if w > UNMATCHED_MAX_200MS:
            bad.append(f"{w} unmatched {kind} in one 200 ms window > {UNMATCHED_MAX_200MS}")
    return not bad, "; ".join(bad)


def identity(row: dict) -> tuple[bool, str]:
    """enqueue = dequeue + drops, with the rows written equal to the kernel counters."""
    if row["n_enq"] < 0:
        return False, "no counters"
    residual = row["n_enq"] - row["n_deq"] - row["n_drop"]
    if residual != 0:
        return False, f"enq {row['n_enq']} != deq {row['n_deq']} + drop {row['n_drop']} (residual {residual})"
    rows = (row["rows_dequeue"], row["rows_drop"], row["rows_nohit"], row.get("rows_requeue", row["n_requeue"]))
    kernel = (row["n_deq"], row["n_drop"], row["n_nohit"], row["n_requeue"])
    if rows != kernel:  # a record lost between the kernel and the file
        return False, f"rows (deq, drop, nohit, requeue) {rows} != kernel counters {kernel}"
    return True, ""


# ── sender log -> QUIC packet numbers (t_obs method b) ────────────────────

def read_sender_packets(path: Path):
    import pandas as pd
    return pd.read_csv(path)


def first_ack_us(path: Path, max_pn: int):
    """numpy array: first ACK receive time (mono us) per packet number, -1 if never acked."""
    import numpy as np
    first = np.full(max_pn + 1, -1, dtype=np.int64)
    with path.open() as f:
        next(f, None)
        for line in f:
            t, _, ranges = line.rstrip("\n").partition(",")
            if not ranges:
                continue
            t_us = int(t)
            for part in ranges.split(";"):
                a, _, b = part.partition("-")
                lo, hi = int(a), min(int(b or a), max_pn)
                if lo > max_pn:
                    continue
                seg = first[lo:hi + 1]
                seg[seg < 0] = t_us
    return first


def match_flow(router_t_enq_us, router_len, send_us, size) -> tuple[list[int], float]:
    """Map a flow's router packets (enqueue order) to its sender packets (send
    order) by order + size: router len = size + 42 and 0 <= t_enq - t_send <= 2 s.
    Sender packets lost before the router are skipped (lookahead 256). Returns
    (sender index per router packet, -1 = unmatched; match rate)."""
    out = [-1] * len(router_t_enq_us)
    i, n = 0, len(send_us)
    matched = 0
    for j, (t, length) in enumerate(zip(router_t_enq_us, router_len)):
        want = length - QUIC_OVERHEAD_BYTES
        k, stop_k = i, min(n, i + MATCH_LOOKAHEAD)
        while k < stop_k:
            d = t - send_us[k]
            if d < 0:
                break               # sender packets are in send order: none later can precede t
            if size[k] == want and d <= MATCH_MAX_DELAY_US:
                break
            k += 1
        if k < stop_k and size[k] == want and 0 <= t - send_us[k] <= MATCH_MAX_DELAY_US:
            out[j] = k
            matched += 1
            i = k + 1
    return out, (matched / len(out) if out else 0.0)


# ── per-run health check ──────────────────────────────────────────────────

def _dir_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def capacity_timeline(scenario, hop: tuple[str, str]) -> list[tuple[float, float]]:
    """[(run time s, Mb/s)] of one directed hop from the scenario (scheduled times)."""
    a, b = hop
    for link in scenario.links:
        if (link.from_, link.to) == (a, b) or (link.from_, link.to) == (b, a):
            forward, reverse = scenario.initial_link(link.from_, link.to)
            direction = "forward" if (link.from_, link.to) == (a, b) else "reverse"
            spec = forward if direction == "forward" else reverse
            out = [(0.0, spec.bandwidth_mbps or float("inf"))]
            for e in scenario.events:
                if (e.type == "link" and (e.from_, e.to) == (link.from_, link.to) and e.direction == direction
                        and e.bandwidth_mbps is not None):
                    out.append((e.at_s, e.bandwidth_mbps))
            return sorted(out)
    spec = scenario.link_defaults.forward
    return [(0.0, spec.bandwidth_mbps or float("inf"))]


def delay_timeline(scenario, hop: tuple[str, str]) -> list[tuple[float, float]]:
    """[(run time s, netem delay ms)] of one directed hop from the scenario (0 = no netem)."""
    a, b = hop
    for link in scenario.links:
        if (link.from_, link.to) in ((a, b), (b, a)):
            forward, reverse = scenario.initial_link(link.from_, link.to)
            direction = "forward" if (link.from_, link.to) == (a, b) else "reverse"
            spec = forward if direction == "forward" else reverse
            out = [(0.0, spec.delay_ms or 0.0)]
            out += [(e.at_s, e.delay_ms) for e in scenario.events
                    if e.type == "link" and (e.from_, e.to) == (link.from_, link.to)
                    and e.direction == direction and e.delay_ms is not None]
            return sorted(out)
    return [(0.0, scenario.link_defaults.forward.delay_ms or 0.0)]


def step_at(series: list[tuple[float, float]], t):
    """Values of a step series [(t, v)] at times t (numpy)."""
    import numpy as np
    when = np.array([c[0] for c in series])
    value = np.array([c[1] for c in series], dtype=float)
    return value[np.clip(np.searchsorted(when, t, side="right") - 1, 0, len(series) - 1)]


def service_stats(table, epoch_mono_ns: int, caps: list[tuple[float, float]],
                  delays: list[tuple[float, float]] | None = None) -> dict:
    """Service timing while the egress was truly backlogged: packet i+1 ready (enqueued, plus
    the netem delay in force) before packet i left. HTB releases i+1 once it has paid for
    packet i, so the ideal gap is packet i's serialization time 8 len[i] / C.
    gap_p50 / gap_p99: gap / ideal; gap_within10: share of backlogged gaps within +-10 %;
    gap_within_tol: share within max(10 % of ideal, GAP_TOL_FLOOR_NS) (the gated share);
    jitter_us_p1 / jitter_us_p99: gap - ideal in microseconds;
    win20_n / win20_within5: busy periods (chains of backlogged gaps) cut into consecutive
    windows from their start (20 ms, longer below 15 Mb/s: window_ns); share of windows whose
    dequeued bytes are within +-5 % of C x window (windows with a capacity change inside are
    skipped); win_ms: the longest window used."""
    import numpy as np
    nan = float("nan")
    out = {"gaps": 0, "gap_p50": nan, "gap_p99": nan, "gap_within10": nan, "gap_within_tol": nan,
           "jitter_us_p1": nan, "jitter_us_p99": nan, "win20_n": 0, "win20_within5": nan}
    d = table[table["kind"] == "dequeue"].sort_values("t_deq_ns", kind="stable")
    t_deq, t_enq, length = (d[c].to_numpy(dtype=np.int64) for c in ("t_deq_ns", "t_enq_ns", "len"))
    if len(t_deq) < 3:
        return out
    if delays:
        t_enq = np.where(t_enq >= 0, t_enq + (step_at(delays, (t_enq - epoch_mono_ns) / 1e9) * 1e6).astype(np.int64),
                         t_enq)
    busy = (t_enq[1:] >= 0) & (t_enq[1:] < t_deq[:-1])
    when = np.array([c[0] for c in caps])
    mbps = np.array([c[1] for c in caps])
    cap_at = lambda t_ns: mbps[np.clip(np.searchsorted(when, (t_ns - epoch_mono_ns) / 1e9, side="right") - 1,  # noqa: E731
                                       0, len(caps) - 1)] * 1e6
    gap = (t_deq[1:] - t_deq[:-1])[busy]
    if not len(gap):
        return out
    ideal = 8 * length[:-1][busy] / cap_at(t_deq[1:][busy]) * 1e9
    ratio = gap / ideal
    dev = gap - ideal
    out.update(gaps=int(len(ratio)), gap_p50=float(np.median(ratio)), gap_p99=float(np.quantile(ratio, 0.99)),
               gap_within10=float(np.mean(np.abs(ratio - 1) <= 0.10)),
               gap_within_tol=float(np.mean(np.abs(dev) <= np.maximum(0.10 * ideal, GAP_TOL_FLOOR_NS))),
               jitter_us_p1=float(np.quantile(dev, 0.01)) / 1e3, jitter_us_p99=float(np.quantile(dev, 0.99)) / 1e3)
    idx = np.flatnonzero(busy)
    first = idx[np.r_[True, np.diff(idx) > 1]]
    last = idx[np.r_[np.diff(idx) > 1, True]] + 1          # a busy period covers packets first .. last
    cum = np.r_[0, np.cumsum(length)]
    ok, win_max = [], 0
    for a, b in zip(first, last):
        k, ta = 0, t_deq[a]
        win = window_ns(float(cap_at(np.array([ta]))[0]))
        win_max = max(win_max, win)
        while ta + (k + 1) * win <= t_deq[b]:
            w0, w1 = ta + k * win, ta + (k + 1) * win
            c0, c1 = cap_at(np.array([w0, w1]))
            if c0 == c1:
                i0, i1 = np.searchsorted(t_deq, [w0, w1], side="right")
                ok.append(abs((cum[i1] - cum[i0]) * 8 / (c0 * win / 1e9) - 1) <= 0.05)
            k += 1
    if ok:
        out.update(win20_n=len(ok), win20_within5=float(np.mean(ok)), win_ms=round(win_max / 1e6, 2))
    return out


def health(run_dir: Path, *, on: bool, scenario=None, epoch_mono_ns: int = 0,
           tracers: list[Tracer] | None = None, counts: list[dict] | None = None,
           flows: dict[str, tuple[str, str, str]] | None = None,
           setup_errors: list[str] | None = None) -> tuple[dict, str]:
    """Write <run>/gtq-health.csv; return (values, one-line summary).
    flows: subscriber -> (publisher id, publisher loopback, subscriber loopback)."""
    import numpy as np
    values: dict[str, object] = {"gtq_logging": int(on)}
    reasons: list[str] = list(setup_errors or [])
    cpu = run_dir / CPU_FILE
    try:
        idle = np.array([float(r["idle"]) for r in csv.DictReader(cpu.open())]) if cpu.exists() else np.array([])
    except Exception:  # noqa: BLE001
        idle = np.array([])
    values["cpu_idle_min"] = round(float(idle.min()), 4) if len(idle) else ""
    values["cpu_idle_mean"] = round(float(idle.mean()), 4) if len(idle) else ""
    if on:
        tracers = tracers or []
        counts = counts or []
        values["tracer_started"] = int(bool(tracers) and all(t.started_ns > 0 for t in tracers))
        values["tracer_stopped_clean"] = int(bool(tracers) and all(t.stopped_clean for t in tracers))
        values["lost_events"] = sum(max(0, r["lost_events"]) for r in counts) if counts else -1
        if not tracers:
            reasons.append("no traced interface")
        for t in tracers:
            reasons += [f"{t.router}: {e}" for e in t.errors]
            if t.prog_misses is not None:
                values[f"{t.router}.recursion_misses"] = sum(m for _, _, m in t.prog_misses)
                values[f"{t.router}.recursion_misses_per_prog"] = " ".join(f"{i}:{k}:{m}" for i, k, m in t.prog_misses)
        if counts and any(r["lost_events"] != 0 for r in counts):
            reasons.append("lost tracer events")
        for r in counts:
            iface = r["iface"]
            ok, why = identity(r)
            rows_ok, rows_why = rows_match(r)
            acct_ok, acct_why = accounting(r)
            values[f"{iface}.enq"] = r["n_enq"]
            values[f"{iface}.deq"] = r["n_deq"]
            values[f"{iface}.drop"] = r["n_drop"]
            values[f"{iface}.identity_ok"] = int(ok)
            values[f"{iface}.requeue"] = r["n_requeue"]
            values[f"{iface}.batched"] = r["n_batched"]
            values[f"{iface}.nohit_late"] = r["nohit_late"]
            values[f"{iface}.requeue_stale"] = r.get("requeue_stale", 0)
            values[f"{iface}.oversize"] = r["oversize"]
            deq = max(1, r["n_deq"])
            for kind in ("deq", "enq"):
                n = r.get(f"unmatched_{kind}", -1)
                values[f"{iface}.unmatched_{kind}"] = n
                values[f"{iface}.unmatched_{kind}_ratio"] = f"{n / deq:.3e}" if n >= 0 else ""
                values[f"{iface}.unmatched_{kind}_max_200ms"] = r.get(f"unmatched_{kind}_max_200ms", -1)
            values[f"{iface}.unmatched_allowed"] = round(unmatched_allowed(r["n_deq"]), 2)
            values[f"{iface}.unmatched_enq_rows"] = r.get("unmatched_enq_rows", -1)
            values[f"{iface}.rows_match"] = int(rows_ok)
            values[f"{iface}.accounting_ok"] = int(acct_ok)
            # identity_ok (enq = deq + drop exactly) stays as information; validity follows the
            # rows check and the accounting rule
            if not rows_ok:
                reasons.append(f"{iface}: {rows_why}")
            elif not acct_ok:
                reasons.append(f"{iface}: {acct_why}")
            elif r["n_enq"] == 0:  # an attached tracer that saw nothing is not a valid trace
                reasons.append(f"{iface}: no packet traced")
            if r["nohit_late"] > NOHIT_MAX_SHARE * max(1, r["n_deq"]):
                reasons.append(f"{iface}: {r['nohit_late']} of {r['n_deq']} dequeues without an enqueue record "
                               f"(> {NOHIT_MAX_SHARE:g}; map full?)")
            if r["n_truncated"] > 0:
                reasons.append(f"{iface}: {r['n_truncated']} dequeue lists longer than 16 skbs")
            path = run_dir / TRACE_DIR / f"{iface}-packets.csv"
            hop = next((t.hops[iface] for t in tracers if iface in t.hops), None)
            if path.exists() and scenario is not None and hop is not None:
                try:
                    table = read_packets(path)
                    sv = service_stats(table, epoch_mono_ns, capacity_timeline(scenario, hop),
                                       delay_timeline(scenario, hop))
                    values[f"{iface}.interdeq_ratio_p50"] = round(sv["gap_p50"], 3)
                    values[f"{iface}.interdeq_ratio_p99"] = round(sv["gap_p99"], 3)
                    values[f"{iface}.interdeq_within10"] = round(sv["gap_within10"], 5)
                    values[f"{iface}.interdeq_within_tol"] = round(sv["gap_within_tol"], 5)
                    values[f"{iface}.interdeq_jitter_us_p1"] = round(sv["jitter_us_p1"], 2)
                    values[f"{iface}.interdeq_jitter_us_p99"] = round(sv["jitter_us_p99"], 2)
                    values[f"{iface}.interdeq_gaps"] = sv["gaps"]
                    values[f"{iface}.win20_n"] = sv["win20_n"]
                    values[f"{iface}.win20_within5"] = round(sv["win20_within5"], 5)
                    values[f"{iface}.win_ms"] = sv.get("win_ms", "")
                    for sid, (pub, src, dst) in (flows or {}).items():
                        rate = sender_match_rate(run_dir, pub, sid, table, src, dst)
                        if rate is not None:
                            values[f"{iface}.match.{sid}"] = round(rate, 4)
                except Exception as e:  # noqa: BLE001
                    reasons.append(f"{iface}: health read failed: {e!r}")
        rates = [v for k, v in values.items() if ".match." in k]
        values["match_rate_min"] = round(min(rates), 4) if rates else ""
        values["bytes_router_trace"] = _dir_bytes(run_dir / TRACE_DIR)
        values["bytes_sender_log"] = sum(p.stat().st_size for p in (run_dir / "publishers").rglob("*-pkt*.csv"))
        values["bytes_written"] = values["bytes_router_trace"] + values["bytes_sender_log"]
    values["gt_q_invalid"] = int(on and bool(reasons))
    values["invalid_reasons"] = " | ".join(reasons)
    _write_rows(run_dir / HEALTH_FILE, [{"key": k, "value": v} for k, v in values.items()])
    if not on:
        line = f"gtq health: logging off; cpu idle min {values['cpu_idle_min']}"
    else:
        state = "INVALID" if values["gt_q_invalid"] else "ok"
        line = (f"gtq health: {state}; lost {values['lost_events']}; identity "
                f"{'ok' if not any(k.endswith('identity_ok') and v == 0 for k, v in values.items()) else 'FAIL'}; "
                f"cpu idle min {values['cpu_idle_min']} mean {values['cpu_idle_mean']}; "
                f"match min {values['match_rate_min']}; {values['bytes_written'] / 1e6:.1f} MB"
                + (f"; {values['invalid_reasons']}" if reasons else ""))
    return values, line


def sender_match_rate(run_dir: Path, pub: str, sid: str, table, src: str, dst: str) -> float | None:
    pkts = run_dir / "publishers" / pub / f"{sid}-pkts.csv"
    if not pkts.exists():
        return None
    f = table[(table["daddr"] == dst) & (table["saddr"] == src) & (table["proto"] == 17)
              & (table["len"] >= MATCH_MIN_LEN)]
    if not len(f):
        return None
    f = f.sort_values("t_enq_ns", kind="stable")
    s = read_sender_packets(pkts)
    _, rate = match_flow((f["t_enq_ns"] // 1000).tolist(), f["len"].tolist(),
                         s["send_mono_us"].tolist(), s["size"].tolist())
    return rate


def read_health(run_dir: Path) -> dict[str, str]:
    path = run_dir / HEALTH_FILE
    if not path.exists():
        return {}
    return {r["key"]: r["value"] for r in csv.DictReader(path.open())}
