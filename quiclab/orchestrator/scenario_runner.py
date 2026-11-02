"""Applies a scenario's events on the run epoch and archives them to events.csv.

The runner owns timing and the archive only; the backend supplies one apply
callback per event type. Live edits from the visualizer go through the same
EventLog, so events.csv is the single ground-truth record of what changed.
"""

from __future__ import annotations

import csv
import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path

from quiclab.config.scenario import Scenario

_log = logging.getLogger(__name__)

EVENT_FIELDS = (
    "event", "at_s", "applied_s", "applied_mono_ns", "applied_unix_ns",
    "target", "detail", "label", "status", "error",
)


class EventLog:
    """Thread-safe events.csv writer; times are relative to the run epoch."""

    def __init__(self, path: Path, epoch_mono_s: float) -> None:
        self._epoch = epoch_mono_s
        self._lock = threading.Lock()
        self._file = path.open("w", newline="", buffering=1)
        self._writer = csv.DictWriter(self._file, fieldnames=EVENT_FIELDS)
        self._writer.writeheader()

    def write(self, event: str, at_s: float | str, target: str = "", detail: str = "",
              label: str | None = None, error: str = "") -> None:
        mono = time.monotonic_ns()
        with self._lock:
            if self._file.closed:
                return
            self._writer.writerow({
                "event": event,
                "at_s": at_s if at_s == "" else f"{at_s:g}",
                "applied_s": f"{mono / 1e9 - self._epoch:.6f}",
                "applied_mono_ns": mono,
                "applied_unix_ns": time.time_ns(),
                "target": target,
                "detail": detail,
                "label": label or "",
                "status": "error" if error else "applied",
                "error": error,
            })

    def close(self) -> None:
        with self._lock:
            self._file.close()


Apply = Callable[[object], tuple[str, str]]  # event -> (target, detail)


class ScenarioRunner:
    """One thread: waits for each event's planned time, applies it, records it."""

    def __init__(self, scenario: Scenario, epoch_mono_s: float, log: EventLog,
                 apply: dict[str, Apply]) -> None:
        self._scenario = scenario
        self._epoch = epoch_mono_s
        self._log = log
        self._apply = apply
        self._stop = threading.Event()
        self.finished = threading.Event()
        self._thread = threading.Thread(target=self._run, name="quiclab-scenario", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=10)

    def _run(self) -> None:
        # Stable sort: events at the same time apply in file order.
        for event in sorted(self._scenario.events, key=lambda e: e.at_s):
            if self._stop.wait(max(0.0, self._epoch + event.at_s - time.monotonic())):
                return
            target = detail = error = ""
            try:
                target, detail = self._apply[event.type](event)
            except Exception as e:  # keep the scenario going; record the failure
                error = str(e)
                _log.error("scenario event at %gs (%s) failed: %s", event.at_s, event.type, e)
            self._log.write(event.type, event.at_s, target, detail, event.label, error)
        if not self._stop.wait(max(0.0, self._epoch + self._scenario.duration_s - time.monotonic())):
            self._log.write("end", self._scenario.duration_s)
            self.finished.set()
