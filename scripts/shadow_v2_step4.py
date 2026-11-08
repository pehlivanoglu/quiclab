#!/usr/bin/env python3
"""Shadow v2, Step 4: fusion of the per-feature scores, the decision gate (spec v1.0 section 12).

    python3 scripts/shadow_v2_step4.py .runs/<campaign> [...]   # -> reports/detector-v2/step4.md, step4-curves.csv, step4/curves.png

Variants (scripts/shadow_v2_step3.py FUSION), loss term = loss fraction over 100 ms (Step 3b)
gated by a positive F2 / F3 score in the last 3 ticks:
  a  S = s2 + s3 + sL                b  delta' Sigma^-1 (zc - delta/2) over {F2, F3} + sL
  c  S = max(s2, s3) + sL            d  S = s1 + s2 + s3 + sL (user decision: F1 enters the score)
  e  covariance form over {F1, F2, F3} + sL
Sigma = EWMA calm covariance of the clipped z vector (tau 60 s), shrunk halfway to its diagonal.
F1 alone and the loss rate alone are kept as reference rows. No hold rule yet (Step 5).
G_ref per variant from the calm pfifo-r1 runs as in Step 3. Gate on the freeze set: at v1's
(full 2-of-4, grouping none) false-alarm rate, recall >= v1 - 0.02 and latency p90 <= v1.
tcpcubic-red is reported as its own cell (user request), plus the other Step 0 weak cells.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shadow_v2_step3 as s3  # noqa: E402

if __name__ == "__main__":
    s3.FEATURES = (*s3.FUSION, "F1", "F5 rate 100ms")
    s3.VARIANTS = ("keep",)
    s3.V1 = {"shadow": "fuse", "gcc": None, "bbr": None, "gradient_only": None, "backlog_only": None, "loss_only": None}
    s3.EXTRA_CELLS = [("tcpcubic red", "red", ("tcpcubic",)),
                      ("fq_codel competition", "fq_codel", ("burstudp", "onoff", "tcpcubic", "tcpbbr", "splitudp")),
                      ("burstcapshallow pfifo", "pfifo", ("burstcapshallow",)),
                      ("burstlong (all AQMs)", None, ("burstlong",)),
                      ("calm090 (all AQMs)", None, ("calm090",))]
    s3.NAME = "step4"
    s3.main(sys.argv[1:])
