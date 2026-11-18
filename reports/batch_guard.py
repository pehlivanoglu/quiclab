#!/usr/bin/env python3
"""Run an offline batch, paused while the campaign runs a detector weak-spot block (user rule, 2026-11-17).

    python3 reports/batch_guard.py <campaign dir> -- <command ...>

Every POLL_S seconds the guard reads the campaign's run.log; while the run in progress (the last "quiclab run_id=")
matches a weak-spot pattern, the batch's process group gets SIGSTOP, otherwise SIGCONT. It only signals the
batch it started; the campaign is never touched. Each pause / resume is logged to stderr.
Weak spots (FLAG, from R2 / v3 / v4 results): jitter (T2), mild / dense / asymmetric-reverse (T3: smild, sdense,
rrevasym), joins (sjoin, hjoin), PIE, fq_codel, cake.
"""
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

POLL_S = 5
WEAK = re.compile(r"-(T2|T3)-|smild|sdense|rrevasym|sjoin|hjoin|-pie-|-fq_codel-|-cake-|jit\d")


def current(camp: Path) -> str:
    log = camp / "run.log"
    if not log.exists():
        return ""
    ids = re.findall(r"quiclab run_id=(\S+)", log.read_text(errors="ignore")[-200000:])
    return ids[-1] if ids else ""


def main(argv):
    camp = Path(argv[0])
    cmd = argv[argv.index("--") + 1:]
    p = subprocess.Popen(cmd, start_new_session=True)
    paused = False
    while p.poll() is None:
        run = current(camp)
        weak = bool(WEAK.search(run))
        if weak and not paused:
            os.killpg(p.pid, signal.SIGSTOP)
            paused = True
            print(f"{time.strftime('%T')} pause ({run})", file=sys.stderr, flush=True)
        elif not weak and paused:
            os.killpg(p.pid, signal.SIGCONT)
            paused = False
            print(f"{time.strftime('%T')} resume ({run})", file=sys.stderr, flush=True)
        time.sleep(POLL_S)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
