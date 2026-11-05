from __future__ import annotations

import os
import shlex
import subprocess
import sys
import threading
from pathlib import Path

import click

from quiclab.config.scenario import load_scenario
from quiclab.config.schema import load_topology
from quiclab.designer import DesignerHTTPServer, make_designer_server
from quiclab.exceptions import QuiclabError
from quiclab.runtime import default_run_id, default_runs_dir, validate_run_id

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_IMAGE = "quiclab:latest"
_VIS_HOST = "127.0.0.1"
_VIS_PORT = 8765
_IN_CONTAINER_ENV = "QUICLAB_IN_CONTAINER"
# Pinned as a git submodule: the last upstream main commit whose
# build/deps/github_hashes pins all of folly/fizz/wangle/mvfst/proxygen.
_MOXYGEN_DIR = _PROJECT_ROOT / "deps" / "moxygen"

@click.group(help="Run plain-QUIC synthetic video topologies from YAML in one Mininet container.")
@click.option(
    "--runs-dir",
    type=click.Path(file_okay=False, path_type=Path),
    envvar="QUICLAB_RUNS_DIR",
    default=None,
    help="Directory holding per-run output. Defaults to quiclab/.runs/.",
)
@click.pass_context
def cli(ctx: click.Context, runs_dir: Path | None) -> None:
    ctx.ensure_object(dict)
    ctx.obj["runs_dir"] = runs_dir


@cli.command(help="Open the local drag-and-drop topology YAML designer.")
@click.option("--config", "-c", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              default=None, help="Optional topology YAML to load into the editor.")
@click.option("--port", type=click.IntRange(1, 65535), default=_VIS_PORT, show_default=True)
def design(config: Path | None, port: int) -> None:
    server: DesignerHTTPServer | None = None
    try:
        server = make_designer_server(host=_VIS_HOST, port=port, config_path=config)
        click.echo(f"designer: http://{_VIS_HOST}:{server.server_address[1]}/")
        click.echo("press Ctrl-C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo("\nstopped designer")
    except (QuiclabError, OSError) as error:
        raise click.ClickException(f"failed to start designer: {error}") from error
    finally:
        if server is not None:
            server.server_close()


@cli.command(help="Parse and validate a topology (and optionally a scenario against it).")
@click.option("--config", "-c", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--scenario", "-s", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
def validate(config: Path, scenario: Path | None) -> None:
    try:
        topology = load_topology(config)
        loaded = load_scenario(scenario, topology) if scenario is not None else None
    except QuiclabError as e:
        raise click.ClickException(str(e)) from e
    click.echo(f"OK: {config}")
    for pid, p in topology.publishers.items():
        click.echo(f"  publisher  {pid:14}  cc={p.cc_algo}  port={p.listen_port}  ladder={p.ladder_kbps}")
    for sid, s in topology.subscribers.items():
        click.echo(f"  subscriber {sid:14}  -> {s.connects_to}  {s.rate_kbps} kbps  "
                   f"phase={s.phase_ms} ms  buffer={s.buffer_ms} ms")
    for rid in topology.routers:
        click.echo(f"  router     {rid}")
    for sid in topology.switches:
        click.echo(f"  switch     {sid}")
    click.echo(f"  links={len(topology.links)}")
    if loaded is not None:
        click.echo(f"OK: {scenario}  duration={loaded.duration_s:g} s")
        for rid in topology.routers:
            queue = loaded.router_queue(rid)
            overrides = "".join(f"  {peer}:{q.aqm.value if q.aqm else 'default'}"
                                for peer, q in (queue.egress or {}).items())
            click.echo(f"  router     {rid:14}  aqm={queue.aqm.value if queue.aqm else 'default'}{overrides}")
        for event in sorted(loaded.events, key=lambda e: e.at_s):
            click.echo(f"  t={event.at_s:<7g} {event.type:6} {event.label or ''}")


@cli.group(help="Prepare local build artifacts.")
def build() -> None:
    pass


@build.command(name="qvideo", help="Build qvideo-server/-client with moxygen's pinned Meta deps.")
def build_qvideo() -> None:
    root = str(_PROJECT_ROOT)
    status = subprocess.run(["git", "-C", root, "submodule", "status", "deps/moxygen"],
                            capture_output=True, text=True).stdout.strip()
    if status.startswith("-"):
        _run(["git", "-C", root, "submodule", "update", "--init", "deps/moxygen"])
    elif status.startswith("+"):
        raise click.ClickException(
            f"deps/moxygen is checked out at a commit other than the pinned submodule ({status}); "
            "run `git submodule update deps/moxygen` or commit the new pin"
        )
    elif not status:
        raise click.ClickException("deps/moxygen submodule not found; clone quiclab with --recursive")
    source = _PROJECT_ROOT / "qvideo"
    _run(["cmake", "-S", str(source), "-B", str(source / "build"), "-G", "Ninja"])
    _run(["cmake", "--build", str(source / "build"), "--target",
          "qvideo-server", "qvideo-client", "qvideo-selftest", "qtraffic"])
    _run([str(source / "build" / "qvideo-selftest")])


@build.command(name="image", help=f"Build the {_IMAGE} Docker image.")
def build_image() -> None:
    _run(["docker", "build", "-t", _IMAGE, "-f", str(_PROJECT_ROOT / "docker" / "Dockerfile"), str(_PROJECT_ROOT)])


@cli.command(name="run", help=(
    "Run SCENARIO on TOPOLOGY until the scenario ends. On the host this starts "
    "the quiclab container; --cli opens the Mininet CLI instead (exit tears down)."
))
@click.option("--config", "-c", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Topology YAML.")
@click.option("--scenario", "-s", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Scenario YAML.")
@click.option("--run-id", default=None, help="Run identifier. Auto-generated if omitted.")
@click.option("--cli", "interactive", is_flag=True, help="Open the Mininet CLI for the run.")
@click.option("--vis", "--visualize", "visualize", is_flag=True,
              help="Serve the live visualizer on localhost during the run.")
@click.option("--vis-port", type=click.IntRange(1, 65535), default=_VIS_PORT, show_default=True)
@click.pass_context
def run_topology(ctx: click.Context, config: Path, scenario: Path, run_id: str | None,
                 interactive: bool, visualize: bool, vis_port: int) -> None:
    try:
        load_scenario(scenario, load_topology(config))
        run_id = run_id or default_run_id()
        validate_run_id(run_id)
    except QuiclabError as e:
        raise click.ClickException(str(e)) from e
    runs_dir = (ctx.obj.get("runs_dir") or default_runs_dir()).resolve()
    if os.environ.get(_IN_CONTAINER_ENV) != "1":
        _run_container(config.resolve(), scenario.resolve(), runs_dir, run_id, interactive, visualize, vis_port)
        return

    from quiclab.orchestrator.mininet_backend import MininetBackend

    servers = []

    def on_running(topology, record, network) -> None:
        if visualize:
            servers.append(_start_visualizer(topology, record, network, vis_port))

    try:
        MininetBackend(runs_dir=runs_dir).up(
            config, scenario, run_id=run_id, interactive=interactive, on_running=on_running
        )
    except QuiclabError as e:
        raise click.ClickException(str(e)) from e
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()


def _run_container(config: Path, scenario: Path, runs_dir: Path, run_id: str, interactive: bool,
                   visualize: bool, vis_port: int) -> None:
    # Same absolute paths inside and outside: the checkout, the config and the
    # runs dir are bind-mounted where they live on the host.
    mounts = {_PROJECT_ROOT: "rw", runs_dir: "rw", config.parent: "ro", scenario.parent: "ro"}
    runs_dir.mkdir(parents=True, exist_ok=True)
    argv = [
        "docker", "run", "--rm", "-i", *(["-t"] if sys.stdin.isatty() else []),
        "--privileged", "--name", f"quiclab-{run_id}",
        "-e", f"{_IN_CONTAINER_ENV}=1",
        "-e", f"QUICLAB_HOST_UID={os.getuid()}", "-e", f"QUICLAB_HOST_GID={os.getgid()}",
        "-v", "/lib/modules:/lib/modules:ro",
        "-w", str(_PROJECT_ROOT),
    ]
    for path, mode in mounts.items():
        if not any(path != other and path.is_relative_to(other) for other in mounts):
            argv += ["-v", f"{path}:{path}:{mode}"]
    if visualize:
        argv += ["-p", f"{_VIS_HOST}:{vis_port}:{vis_port}"]
    argv += [
        _IMAGE, "python3", "-m", "quiclab", "--runs-dir", str(runs_dir),
        "run", "-c", str(config), "-s", str(scenario), "--run-id", run_id,
        *(["--cli"] if interactive else []),
        *(["--vis", "--vis-port", str(vis_port)] if visualize else []),
    ]
    if visualize:
        click.echo(f"visualizer: http://{_VIS_HOST}:{vis_port}/")
    status = subprocess.call(argv)
    if status:
        raise click.ClickException(f"container exited with status {status}")


def _start_visualizer(topology, record, network, port: int):
    from quiclab.visualizer import VisualizerHTTPServer, read_netns_counters

    pids = record.pids
    try:
        # 0.0.0.0 inside the container; the host only publishes it on localhost.
        server = VisualizerHTTPServer(
            ("0.0.0.0", port), topology, run_dir=record.run_dir, network=network,
            counter_reader=lambda node, iface: read_netns_counters(pids[node], iface) if node in pids else None,
        )
    except OSError as e:
        raise click.ClickException(f"failed to start visualizer: {e}") from e
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _run(argv: list[str]) -> None:
    click.echo(f"$ {shlex.join(argv)}")
    status = subprocess.call(argv)
    if status:
        raise click.ClickException(f"command failed with status {status}")
