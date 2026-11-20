#!/usr/bin/env python3
"""Run an offline batch under the shared rules (user, 2026-11-17 / 2026-11-18; quiclab/.no-batch-blocks.md).

    python3 reports/batch_guard.py auto --session ID --what TEXT --cores N --expect HH:MM -- <command ...>

- Campaign: "auto" follows the campaign whose run.log changed last under .runs/ (K2 -> K3 -> ...).
- CPU budget: at most MAX_CORES cores in total across sessions while a campaign runs (2026-11-18: 4, 2 per
  session). Before starting, the guard waits while the other entries in quiclab/.batch-slot plus N exceed it.
  It adds its own line (session, what, cores, start, expected end, state) and removes it when the batch ends.
- Weak-spot blocks: every POLL_S seconds the guard reads the run in progress (the last "quiclab run_id="); while it
  matches WEAK, the batch's process group gets SIGSTOP (state "paused"), otherwise SIGCONT.
- Back-off: if that run's CPU idle (host-cpu.csv, minimum over the last BACKOFF_WINDOW_S) falls below BACKOFF_IDLE,
  the total drops to BACKOFF_CORES until the run ends: entries keep running in start order while their cumulative
  cores fit, the later ones pause (state "backoff"). Every back-off and its end are logged to stderr and to
  quiclab/.batch-backoff.log.
- Proactive rule (user, 2026-11-18): when a campaign run starts, the guard looks up the CPU idle minimum of the same
  cell's earlier seeds without batch overlap (else of the nearest cells of the block); below PREDICT_IDLE no batch
  runs during that run at all (state "paused"). Each decision is logged to quiclab/.batch-backoff.log. Every state
  change of every guard is appended to quiclab/.batch-history.log, which is how "without batch overlap" is known.
Only the batch the guard started is signalled; the campaign is never touched.
"""
import argparse
import csv
import fcntl
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

POLL_S = 5
MAX_CORES = 4                 # user, 2026-11-18 (was 2): total while a campaign runs, 2 per session
BACKOFF_IDLE = 0.6            # user, 2026-11-18 (0.5 -> 0.6 after K3 L2 x80 codel r2 lost tracer events)
BACKOFF_CORES = 2
BACKOFF_WINDOW_S = 60
# Weak spots (user, 2026-11-17 / 2026-11-18; reasons in quiclab/.no-batch-blocks.md)
WEAK = re.compile(r"-(T2|T3)-|smild|sdense|rrevasym|sjoin|hjoin|-pie-|-fq_codel-|-cake-|jit\d"
                  r"|-M-|-I1-|-C1-calm-copa|-C1-sburst-copa|-L7-|-S1-|-S2-|-A1-"
                  r"|-GATE-calm-(base|split4l)-(bbr|copa)-|-GATE-sburst-adapt-"   # K5 gate (adaptation check)
                  r"|-L2-fbcross-x80-codel-|-L11-spause-")                        # re-run list (T2 jit5: jit\d)
ROOT = Path(__file__).resolve().parents[1]
SLOT = Path(os.environ.get("BATCH_SLOT", ROOT / ".batch-slot"))          # env: tests only
RUNS = Path(os.environ.get("BATCH_RUNS", ROOT / ".runs"))                # env: tests only
BACKOFF_LOG = Path(os.environ.get("BATCH_BACKOFF_LOG", ROOT / ".batch-backoff.log"))
HISTORY = Path(os.environ.get("BATCH_HISTORY", ROOT / ".batch-history.log"))   # when each guard's batch ran
PREDICT_IDLE = 0.70           # user, 2026-11-18: proactive rule (no batch during a run whose cell ran below this)


def campaign_dir(camp) -> Path | None:
    if str(camp) == "auto":
        logs = sorted(RUNS.glob("*/run.log"), key=lambda p: p.stat().st_mtime)
        return logs[-1].parent if logs else None
    return Path(camp)


def current(camp) -> str:
    d = campaign_dir(camp)
    log = d / "run.log" if d else None
    if not log or not log.exists():
        return ""
    ids = re.findall(r"quiclab run_id=(\S+)", log.read_text(errors="ignore")[-200000:])
    if not ids:
        return ""
    # campaign over (or stopped): last run finished and the log quiet for 10 min -> no run in progress
    # (fix 2026-11-19: after K3 ended the last run, a weak L7 run, kept the batch paused for 6 h)
    if (d / ids[-1] / "v3-checks.json").exists() and time.time() - log.stat().st_mtime > 600:
        return ""
    return ids[-1]


def idle_min(camp, run: str) -> float | None:
    """Minimum CPU idle of the run in progress over its last BACKOFF_WINDOW_S of samples (host-cpu.csv)."""
    d = campaign_dir(camp)
    f = d / run / "host-cpu.csv" if d and run else None
    if not f or not f.exists():
        return None
    try:
        rows = list(csv.reader(f.open()))[1:]
    except OSError:
        return None
    if not rows:
        return None
    t_last = int(rows[-1][0])
    vals = [float(r[1]) for r in rows if t_last - int(r[0]) <= BACKOFF_WINDOW_S * 1e9]
    return min(vals) if vals else None


def _wall_span(run_dir: Path):
    """(start, end) wall-clock seconds of a finished run, from its host-cpu.csv (monotonic ns)."""
    f = run_dir / "host-cpu.csv"
    try:
        rows = list(csv.reader(f.open()))[1:]
    except OSError:
        return None
    if not rows:
        return None
    off = time.time() - time.monotonic()
    return int(rows[0][0]) / 1e9 + off, int(rows[-1][0]) / 1e9 + off


def _overlapped(span) -> bool | None:
    """True if a guard's batch was running during span (from HISTORY); None if the history does not cover it."""
    try:
        lines = HISTORY.read_text().splitlines()
    except OSError:
        return None
    if not lines or float(lines[0].split()[0]) > span[0]:
        return None
    running = {}
    for ln in lines:
        t, who, st = ln.split()[:3]
        t = float(t)
        if t > span[1]:
            break
        if st == "running":
            running[who] = t
        else:
            a = running.pop(who, None)
            if a is not None and t >= span[0]:
                return True
    return any(a <= span[1] for a in running.values()) or None


def _cell_idle(run_dir: Path):
    """min CPU idle of each finished run, preferring runs without a recorded batch overlap."""
    try:
        rows = list(csv.reader((run_dir / "host-cpu.csv").open()))[1:]
        return min(float(r[1]) for r in rows) if rows else None
    except (OSError, ValueError):
        return None


def predicted_idle(camp, run: str):
    """Proactive rule: the CPU idle minimum of the same cell's earlier seeds (without batch overlap where the history
    knows it); for a first seed, of the same block's cells of the same scenario type, else of the whole block.
    Returns (value, basis) or (None, reason)."""
    d = campaign_dir(camp)
    m = re.match(r"(v4-([^-]+)-([^-]+)-.*)-r(\d+)$", run or "")
    if not d or not m:
        return None, "no cell"
    cell, block, rtype = m.group(1), m.group(2), m.group(3)

    def finished(pattern):
        out = []
        for rd in d.glob(pattern):
            if rd.name == run or not (rd / "v3-checks.json").exists():
                continue
            v = _cell_idle(rd)
            if v is None:
                continue
            span = _wall_span(rd)
            ov = _overlapped(span) if span else None
            out.append((v, ov, rd.name))
        return out
    for basis, pat in (("same cell", f"{cell}-r*"), ("same block and type", f"v4-{block}-{rtype}-*"),
                       ("same block", f"v4-{block}-*")):
        xs = finished(pat)
        if xs:
            clean = [x for x in xs if x[1] is False]
            use = clean or xs
            v = min(x[0] for x in use)
            return v, f"{basis}: {len(use)} run(s){'' if clean else ', overlap unknown or present'}"
    return None, "no earlier run of the block"


def _history(who: str, state: str) -> None:
    try:
        with HISTORY.open("a") as fh:
            fh.write(f"{time.time():.3f} {who} {state}\n")
    except OSError:
        pass


def _edit(fn):
    SLOT.touch(exist_ok=True)
    with SLOT.open("r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        lines = [x for x in fh.read().splitlines() if x.strip()]
        lines, ret = fn(lines)
        fh.seek(0)
        fh.truncate()
        fh.write("".join(x + "\n" for x in lines))
        return ret


def _cores(line: str) -> int:
    m = re.search(r"cores=(\d+)", line)
    return int(m.group(1)) if m else 0


def _alive(line: str) -> bool:
    m = re.search(r"pid=(\d+)", line)
    if not m:
        return True
    try:
        os.kill(int(m.group(1)), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _log(msg: str) -> None:
    line = f"{time.strftime('%F %T')} {msg}"
    print(line, file=sys.stderr, flush=True)
    try:
        with BACKOFF_LOG.open("a") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def main(argv):
    i = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign")
    ap.add_argument("--session", required=True)
    ap.add_argument("--what", required=True)
    ap.add_argument("--cores", type=int, default=2)
    ap.add_argument("--expect", default="?")
    a = ap.parse_args(argv[:i])
    cmd = argv[i + 1:]
    tag = f"pid={os.getpid()}"
    start = time.strftime("%F %T")
    me = lambda st: (f"session={a.session} {tag} cores={a.cores} start={start} "   # noqa: E731
                     f"expect={a.expect} state={st} what={a.what}")

    def claim(lines):
        lines = [x for x in lines if _alive(x)]          # drop entries of guards that died without cleaning up
        others = sum(_cores(x) for x in lines if tag not in x)
        if others + a.cores > MAX_CORES:
            return lines, False
        return lines + [me("running")], True
    while not _edit(claim):
        print(f"{time.strftime('%T')} waiting for cores ({SLOT})", file=sys.stderr, flush=True)
        time.sleep(30)
    p = subprocess.Popen(cmd, start_new_session=True)
    state = "running"

    def set_state(st):
        _edit(lambda lines: ([x if tag not in x else re.sub(r"state=\S+", f"state={st}", x) for x in lines], None))

    def my_backoff_turn() -> bool:
        """Under back-off: True if this guard must pause (its cumulative cores in start order exceed the limit)."""
        def fn(lines):
            live = [x for x in lines if _alive(x)]
            order = sorted(live, key=lambda x: re.search(r"start=(\S+ \S+)", x).group(1) if "start=" in x else "")
            cum = 0
            for x in order:
                if re.search(r"state=paused", x) and tag not in x:
                    continue                              # a guard paused for a weak spot uses no CPU
                cum += _cores(x)
                if tag in x:
                    return lines, cum > BACKOFF_CORES
            return lines, False
        return _edit(fn)

    def _term(signum, frame):   # stop the batch and release the slot on SIGTERM / SIGINT
        try:
            os.killpg(p.pid, signal.SIGCONT)
            os.killpg(p.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        raise SystemExit(1)
    signal.signal(signal.SIGTERM, _term)
    signal.signal(signal.SIGINT, _term)

    backoff_run = None     # the campaign run during which back-off is in force
    predicted = {}         # run -> (value, basis): the proactive rule's decision, once per run
    who = f"{a.session}:{os.getpid()}"
    _history(who, "running")
    try:
        while p.poll() is None:
            run = current(a.campaign)
            if backoff_run is not None and run != backoff_run:
                _log(f"back-off ends ({backoff_run} finished) [{a.session}: {a.what}]")
                backoff_run = None
            if backoff_run is None:
                idle = idle_min(a.campaign, run)
                if idle is not None and idle < BACKOFF_IDLE:
                    backoff_run = run
                    _log(f"back-off: {run} CPU idle {idle:.3f} < {BACKOFF_IDLE} over the last {BACKOFF_WINDOW_S} s; "
                         f"total {BACKOFF_CORES} cores until it ends [{a.session}: {a.what}]")
            if run and run not in predicted:
                predicted[run] = predicted_idle(a.campaign, run)
                v, basis = predicted[run]
                if v is not None and v < PREDICT_IDLE:
                    _log(f"proactive: no batch during {run}: predicted CPU idle {v:.3f} < {PREDICT_IDLE} ({basis}) "
                         f"[{a.session}: {a.what}]")
            pv = predicted.get(run, (None, ""))[0]
            if WEAK.search(run + "-") or (pv is not None and pv < PREDICT_IDLE):
                want = "paused"
            else:
                want = "backoff" if backoff_run is not None and my_backoff_turn() else "running"
            if want != state:
                if want == "running":
                    os.killpg(p.pid, signal.SIGCONT)
                elif state == "running":
                    os.killpg(p.pid, signal.SIGSTOP)
                set_state(want)
                _history(who, want)
                print(f"{time.strftime('%T')} {want} ({run})", file=sys.stderr, flush=True)
                state = want
            time.sleep(POLL_S)
    finally:
        if state != "running" and p.poll() is None:
            os.killpg(p.pid, signal.SIGCONT)
        _edit(lambda lines: ([x for x in lines if tag not in x], None))
        _history(who, "ended")
    return p.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
