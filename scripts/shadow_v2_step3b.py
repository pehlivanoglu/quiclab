#!/usr/bin/env python3
"""Shadow v2, Step 3b: loss-score variants for F5 (user request 2026-11-08).

    python3 scripts/shadow_v2_step3b.py .runs/<campaign> [...]   # -> reports/detector-v2/step3b.md, step3b-curves.csv, step3b/curves.png

Same machinery as Step 3 (scripts/shadow_v2_step3.py): G_ref per variant from the calm
pfifo-r1 runs, theta sweep, pass check against v1's loss_only at its false-alarm rate.
Variants: the spec LLR (F5), loss fraction over a trailing 100 / 200 / 300 ms window
normalised like F1-F3, the LLR scaled by 0.1 / 0.3, the LLR with at most 3 lost per tick.
probe_rtt: G kept (Step 3 showed no effect of the reset).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shadow_v2_step3 as s3  # noqa: E402

if __name__ == "__main__":
    s3.FEATURES = tuple(s3.LOSS)
    s3.VARIANTS = ("keep",)
    s3.NAME = "step3b"
    s3.main(sys.argv[1:])
