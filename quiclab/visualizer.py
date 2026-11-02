from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urlparse

from pydantic import ValidationError

from quiclab.config.scenario import RouterQueue
from quiclab.config.schema import AqmKind, DirectionSpec, TopologyConfig, load_topology
from quiclab.exceptions import OrchestratorError
from quiclab.runtime import edge_interfaces

_log = logging.getLogger(__name__)
_STATIC_ROOT = Path(__file__).resolve().parents[1] / "visualizer"
_STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


@dataclass(frozen=True)
class InterfaceCounters:
    rx_bytes: int
    tx_bytes: int


@dataclass(frozen=True)
class _EdgeCounterSample:
    at_s: float
    a: InterfaceCounters
    b: InterfaceCounters


CounterReader = Callable[[str, str], InterfaceCounters | None]
_METRICS_STALE_MS = 3000
_MAX_REQUEST_BYTES = 64 * 1024


class LinkUpdateError(Exception):
    def __init__(self, status: HTTPStatus, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


def _direction_payload(spec: DirectionSpec | None) -> dict[str, object] | None:
    if spec is None:
        return None
    return {
        "bandwidth_mbps": spec.bandwidth_mbps,
        "delay_ms": spec.delay_ms,
        "jitter_ms": spec.jitter_ms,
        "loss_pct": spec.loss_pct,
    }


def _link_graph_levels(topology: TopologyConfig) -> dict[str, int]:
    """BFS hop counts over the link graph, rooted at publishers.

    Used to place routers and routed endpoints in left-to-right columns; nodes
    in a disconnected component default to level 0.
    """
    adjacency: dict[str, set[str]] = {}
    for link in topology.links:
        adjacency.setdefault(link.from_, set()).add(link.to)
        adjacency.setdefault(link.to, set()).add(link.from_)

    sources = sorted(topology.publishers)
    levels = {nid: 0 for nid in sources}
    queue = deque(sources)
    while queue:
        cur = queue.popleft()
        for neighbor in sorted(adjacency.get(cur, ())):
            if neighbor not in levels:
                levels[neighbor] = levels[cur] + 1
                queue.append(neighbor)
    return levels


def topology_snapshot(topology: TopologyConfig, network=None) -> dict[str, object]:
    """Graph for the browser; link conditions and AQMs come from the running
    network (`LiveNetwork`), none without one."""
    nodes: list[dict[str, object]] = []
    link_levels = _link_graph_levels(topology)

    def _level(nid: str, fallback: int) -> int:
        return link_levels.get(nid, fallback)

    for rid, router in topology.routers.items():
        nodes.append(
            {
                "id": rid,
                "role": "router",
                "level": _level(rid, 1),
                "aqm": _queue(network, rid).aqm.value if _queue(network, rid).aqm else None,
                "dualpi2_target_ms": _queue(network, rid).dualpi2_target_ms,
            }
        )
    for sid in topology.switches:
        nodes.append({"id": sid, "role": "switch", "level": _level(sid, 2)})
    for pid, publisher in topology.publishers.items():
        nodes.append(
            {
                "id": pid,
                "role": "publisher",
                "level": _level(pid, 0),
                "cc_algo": publisher.cc_algo,
                "ladder_kbps": publisher.ladder_kbps,
            }
        )
    for sid, subscriber in topology.subscribers.items():
        nodes.append(
            {
                "id": sid,
                "role": "subscriber",
                "level": _level(sid, 2),
                "connects_to": subscriber.connects_to,
                "rate_kbps": subscriber.rate_kbps,
                "buffer_ms": subscriber.buffer_ms,
            }
        )
    if topology.traffic is not None:
        for role, endpoint in (
            *(("traffic-sender", endpoint) for endpoint in topology.traffic.senders),
            *(("traffic-receiver", endpoint) for endpoint in topology.traffic.receivers),
        ):
            nodes.append(
                {
                    "id": endpoint.id,
                    "role": role,
                    "level": _level(endpoint.id, 0),
                }
            )

    min_level = min((int(node["level"]) for node in nodes), default=0)
    for node in nodes:
        node["level"] = int(node["level"]) - min_level

    links = [
        {
            "id": f"{link.from_}--{link.to}",
            "source": link.from_,
            "target": link.to,
            "forward": _direction_payload(network.links[(index, "forward")] if network else None),
            "reverse": _direction_payload(network.links[(index, "reverse")] if network else None),
        }
        for index, link in enumerate(topology.links)
    ]

    return {
        "nodes": nodes,
        "links": links,
        "summary": {
            "routers": len(topology.routers),
            **({"switches": len(topology.switches)} if topology.switches else {}),
            "publishers": len(topology.publishers),
            "subscribers": len(topology.subscribers),
            "links": len(links),
            **(
                {"traffic_endpoints": len(topology.traffic.senders) + len(topology.traffic.receivers)}
                if topology.traffic is not None else {}
            ),
        },
    }


def _queue(network, router_id: str) -> RouterQueue:
    return network.queues[router_id] if network is not None else RouterQueue()


class ThroughputSampler:
    def __init__(
        self,
        topology: TopologyConfig,
        counter_reader: CounterReader | None = None,
    ) -> None:
        self._edges = edge_interfaces(topology)
        self._counter_reader = counter_reader or (lambda node, iface: None)
        self._previous: dict[str, _EdgeCounterSample] = {}

    def sample(self) -> dict[str, dict[str, object]]:
        now = time.monotonic()
        out: dict[str, dict[str, object]] = {}

        for edge in self._edges:
            edge_id = f"{edge.a}--{edge.b}"
            a = self._counter_reader(edge.a, edge.a_iface)
            b = self._counter_reader(edge.b, edge.b_iface)
            if a is None or b is None:
                self._previous.pop(edge_id, None)
                out[edge_id] = {
                    "status": "unavailable",
                    "throughput_bps": None,
                    "a_to_b_bps": None,
                    "b_to_a_bps": None,
                }
                continue

            current = _EdgeCounterSample(at_s=now, a=a, b=b)
            previous = self._previous.get(edge_id)
            self._previous[edge_id] = current
            if previous is None or now <= previous.at_s:
                out[edge_id] = {
                    "status": "warming",
                    "throughput_bps": None,
                    "a_to_b_bps": None,
                    "b_to_a_bps": None,
                }
                continue

            elapsed = now - previous.at_s
            a_to_b_bps = _bytes_per_second(previous.a.tx_bytes, a.tx_bytes, elapsed) * 8
            b_to_a_bps = _bytes_per_second(previous.b.tx_bytes, b.tx_bytes, elapsed) * 8
            out[edge_id] = {
                "status": "ok",
                "throughput_bps": a_to_b_bps + b_to_a_bps,
                "a_to_b_bps": a_to_b_bps,
                "b_to_a_bps": b_to_a_bps,
            }

        return out


def snapshot_with_rates(
    topology: TopologyConfig,
    sampler: ThroughputSampler,
    network=None,
) -> dict[str, object]:
    snapshot = topology_snapshot(topology, network)
    rates = sampler.sample()
    for link in snapshot["links"]:  # type: ignore[index]
        rate = rates.get(link["id"], {})  # type: ignore[index]
        link.update(rate)  # type: ignore[union-attr]
    snapshot["sampled_at_unix_s"] = time.time()
    return snapshot


class VisualizerHTTPServer(ThreadingHTTPServer):
    """Serves the topology, live link rates, and node metrics of one run.

    `run_dir` holds the qvideo CSVs; `network` is the running `LiveNetwork`.
    Without them (no active run) only the static topology is shown.
    """

    def __init__(
        self,
        server_address: tuple[str, int],
        topology: TopologyConfig,
        run_dir: Path | None = None,
        counter_reader: CounterReader | None = None,
        network=None,
    ) -> None:
        super().__init__(server_address, _VisualizerHandler)
        self.topology = topology
        self.run_dir = run_dir
        self.network = network
        self.sampler = ThroughputSampler(topology, counter_reader)

    def update_link(self, link_id: str, direction: str, raw: object) -> dict[str, object]:
        if self.network is None:
            raise LinkUpdateError(HTTPStatus.CONFLICT, "live link editing requires an active run")
        if direction not in {"forward", "reverse"}:
            raise LinkUpdateError(HTTPStatus.NOT_FOUND, "unknown link direction")
        if not isinstance(raw, dict):
            raise LinkUpdateError(HTTPStatus.BAD_REQUEST, "direction must be a JSON object")
        try:
            spec = DirectionSpec.model_validate(raw)
        except ValidationError as error:
            raise LinkUpdateError(HTTPStatus.UNPROCESSABLE_ENTITY, str(error)) from error
        for index, link in enumerate(self.topology.links):
            if f"{link.from_}--{link.to}" == link_id:
                self._apply("link", f"{link.from_}->{link.to}:{direction}",
                            lambda: self.network.set_link(index, direction, spec),
                            " ".join(f"{k}={v:g}" for k, v in spec.model_dump().items() if v is not None))
                return _direction_payload(spec)
        raise LinkUpdateError(HTTPStatus.NOT_FOUND, "unknown link")

    def update_router(self, router_id: str, raw: object) -> dict[str, object]:
        if self.network is None:
            raise LinkUpdateError(HTTPStatus.CONFLICT, "live router editing requires an active run")
        if not isinstance(raw, dict) or set(raw) != {"aqm"}:
            raise LinkUpdateError(HTTPStatus.BAD_REQUEST, "expected only an aqm field")
        try:
            aqm = AqmKind(raw["aqm"]) if raw["aqm"] is not None else None
        except (TypeError, ValueError) as error:
            raise LinkUpdateError(HTTPStatus.UNPROCESSABLE_ENTITY, "unknown AQM kind") from error
        if router_id not in self.topology.routers:
            raise LinkUpdateError(HTTPStatus.NOT_FOUND, "unknown router")
        # The browser picks only the kind; kind-specific parameters reset to defaults.
        queue = RouterQueue(aqm=aqm)
        self._apply("aqm", router_id, lambda: self.network.set_queue(router_id, queue),
                    f"aqm={aqm.value if aqm else 'default'}")
        return {"aqm": aqm.value if aqm else None}

    def _apply(self, kind: str, target: str, apply: Callable[[], None], detail: str) -> None:
        try:
            self.network.manual(kind, target, apply, detail)
        except OrchestratorError as error:
            raise LinkUpdateError(HTTPStatus.INTERNAL_SERVER_ERROR, str(error)) from error

    def node_metrics(self, node_id: str) -> dict[str, object]:
        if self.run_dir is None:
            return {"status": "unavailable", "reason": "no active run"}
        if node_id in self.topology.subscribers:
            row = read_last_row(self.run_dir / "clients" / f"{node_id}-playback.csv")
            if row is None:
                return {"status": "unavailable", "reason": "metrics not ready"}
            row["client"] = node_id
            row["playing"] = row.get("frames", 0) > 0
            return {"status": snapshot_status(row), "playback": row}
        if node_id in self.topology.publishers:
            connections = []
            for sid in self.topology.subscribers_of(node_id):
                row = read_last_row(self.run_dir / "publishers" / node_id / f"{sid}-cc.csv")
                if row is not None:
                    row["client"] = sid
                    connections.append(row)
            if not connections:
                return {"status": "unavailable", "reason": "no connected client yet"}
            stale = any(snapshot_status(c) == "stale" for c in connections)
            return {"status": "stale" if stale else "ok", "connections": connections}
        return {"status": "unavailable", "reason": "no metrics for this node"}


def make_server(*, config_path: str | Path, host: str, port: int) -> VisualizerHTTPServer:
    return VisualizerHTTPServer((host, port), load_topology(config_path))


def read_last_row(path: Path) -> dict[str, object] | None:
    """Last complete row of a CSV being appended to, numbers parsed."""
    try:
        with path.open("rb") as f:
            header = f.readline().decode().strip().split(",")
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 8192))
            tail = f.read().decode(errors="replace")
    except OSError:
        return None
    lines = tail.split("\n")[:-1]  # drop the part after the last newline: maybe a half-written row
    if not lines or lines[-1].strip() == ",".join(header):
        return None
    values = lines[-1].strip().split(",")
    if len(values) != len(header):
        return None
    row: dict[str, object] = {}
    for name, value in zip(header, values):
        try:
            row[name] = int(value)
        except ValueError:
            try:
                row[name] = float(value)
            except ValueError:
                row[name] = value
    return row if isinstance(row.get("t_us"), int) else None


def snapshot_status(snapshot: dict[str, object], now_unix_ms: float | None = None) -> str:
    now = time.time() * 1000 if now_unix_ms is None else now_unix_ms
    return "stale" if now - float(snapshot["t_us"]) / 1000 > _METRICS_STALE_MS else "ok"


class _VisualizerHandler(BaseHTTPRequestHandler):
    server: VisualizerHTTPServer

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/snapshot":
            snapshot = snapshot_with_rates(self.server.topology, self.server.sampler, self.server.network)
            snapshot["links_editable"] = self.server.network is not None
            snapshot["routers_editable"] = self.server.network is not None
            self._send_json(snapshot)
            return
        prefix = "/api/nodes/"
        suffix = "/metrics"
        if path.startswith(prefix) and path.endswith(suffix):
            node_id = unquote(path[len(prefix):-len(suffix)]).strip("/")
            self._send_json(self.server.node_metrics(node_id))
            return
        static_file = _STATIC_FILES.get(path)
        if static_file is not None:
            self._send_static(*static_file)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        link_prefix = "/api/links/"
        router_prefix = "/api/routers/"
        if not path.startswith((link_prefix, router_prefix)):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if path.startswith(link_prefix):
            parts = path[len(link_prefix):].rsplit("/", 1)
        else:
            parts = []
        if path.startswith(link_prefix) and len(parts) != 2:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            self._send_json({"error": "invalid Content-Length"}, HTTPStatus.BAD_REQUEST)
            return
        if length < 0:
            self._send_json({"error": "Content-Length required"}, HTTPStatus.LENGTH_REQUIRED)
            return
        if length > _MAX_REQUEST_BYTES:
            self._send_json({"error": "request too large"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            raw = json.loads(self.rfile.read(length))
            if path.startswith(link_prefix):
                payload = self.server.update_link(unquote(parts[0]), parts[1], raw)
                response = {"direction": payload}
            else:
                router_id = unquote(path[len(router_prefix):]).strip("/")
                payload = self.server.update_router(router_id, raw)
                response = {"router": payload}
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self._send_json({"error": f"invalid JSON: {error}"}, HTTPStatus.BAD_REQUEST)
            return
        except LinkUpdateError as error:
            self._send_json({"error": error.message}, error.status)
            return
        self._send_json(response)

    def log_message(self, fmt: str, *args: object) -> None:
        _log.debug("visualizer: " + fmt, *args)

    def _send_json(
        self, payload: object, status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self._send_response_body(status, "application/json", body)

    def _send_static(self, filename: str, content_type: str) -> None:
        path = _STATIC_ROOT / filename
        try:
            body = path.read_bytes()
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._send_response_body(HTTPStatus.OK, content_type, body)

    def _send_response_body(
        self,
        status: HTTPStatus,
        content_type: str,
        body: bytes,
    ) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            _log.debug("visualizer client disconnected before response completed")


def _bytes_per_second(previous: int, current: int, elapsed_s: float) -> float:
    return max(0, current - previous) / elapsed_s


def read_netns_counters(pid: int, iface: str) -> InterfaceCounters | None:
    """Interface byte counters of the network namespace `pid` lives in.

    /proc/<pid>/net/dev reflects that process's namespace, so the visualizer
    reads every Mininet host without entering it.
    """
    try:
        text = Path(f"/proc/{pid}/net/dev").read_text()
    except OSError:
        return None
    for line in text.splitlines()[2:]:
        name, _, fields = line.partition(":")
        if name.strip() == iface:
            values = fields.split()
            return InterfaceCounters(rx_bytes=int(values[0]), tx_bytes=int(values[8]))
    return None
