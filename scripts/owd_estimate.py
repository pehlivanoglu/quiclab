#!/usr/bin/env python3
"""Sender-side OWD estimate (no oracle): RTT sample minus min RTT, per 5 ms.

    python3 scripts/owd_estimate.py .runs/<campaign>/<run> [...]

What a deployed sender can compute without receiver clocks: each ACK's RTT
sample (ack delay removed) minus the connection's min RTT, so it carries the
forward queueing delay plus any reverse-path queueing. Read from
publishers/<pub>/<client>-acks.csv (one sample per ACK, for its largest newly
acked packet) and written next to it as <client>-owd-est.csv, on the same
5 ms send-time grid as the oracle <client>-owd.csv:

    t_us, bin_mono_us, samples, est_min_us, est_mean_us, est_max_us

Bins without an ACK sample have empty values. Like FlowBot's OWD input, the
estimate is relative (zero-mean it per window); it is not an absolute OWD.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

BIN_US = 5_000  # FlowBot's OWD sampling step


def estimate(acks_csv: Path, owd_csv: Path | None, out_csv: Path) -> tuple[int, int]:
    bins: dict[int, list[int]] = defaultdict(list)
    with acks_csv.open() as f:
        for row in csv.DictReader(f):
            if not row["rtt_us"] or not row["min_rtt_us"] or int(row["min_rtt_us"]) <= 0:
                continue
            est = int(row["rtt_us"]) - int(row["min_rtt_us"])
            bins[int(row["sent_mono_us"]) // BIN_US].append(max(0, est))
    if not bins:
        out_csv.write_text("t_us,bin_mono_us,samples,est_min_us,est_mean_us,est_max_us\n")
        return 0, 0
    # Same grid as the oracle log when it exists (mono -> unix offset from its rows; older runs have a 10 ms oracle, bins still align).
    offset_us = None
    if owd_csv is not None and owd_csv.exists():
        with owd_csv.open() as f:
            first = next(csv.DictReader(f), None)
        if first:
            offset_us = int(first["t_us"]) - int(first["bin_mono_us"])
    lo, hi = min(bins), max(bins)
    filled = 0
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_us", "bin_mono_us", "samples", "est_min_us", "est_mean_us", "est_max_us"])
        for b in range(lo, hi + 1):
            v = bins.get(b, [])
            filled += bool(v)
            t = "" if offset_us is None else b * BIN_US + offset_us
            w.writerow([t, b * BIN_US, len(v), *((min(v), sum(v) // len(v), max(v)) if v else ("", "", ""))])
    return filled, hi - lo + 1


def main(runs: list[str]) -> None:
    if not runs:
        sys.exit(__doc__)
    for run in map(Path, runs):
        for acks in sorted(run.glob("publishers/*/*-acks.csv")):
            sid = acks.name[: -len("-acks.csv")]
            filled, total = estimate(acks, acks.with_name(f"{sid}-owd.csv"), acks.with_name(f"{sid}-owd-est.csv"))
            print(f"{run.name} {sid}: {filled}/{total} bins with a sample")


if __name__ == "__main__":
    main(sys.argv[1:])
