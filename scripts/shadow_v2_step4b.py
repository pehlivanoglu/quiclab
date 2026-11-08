#!/usr/bin/env python3
"""Shadow v2, Step 4b: v2 (per-flow normalisation) vs v2-fixed (one global scale), same fusion (d).

    python3 scripts/shadow_v2_step4b.py .runs/<campaign> [...]   # -> reports/detector-v2/step4b.md, step4b-curves.csv, step4b/curves.png

v2-fixed (user, 2026-11-08): the v2 features, CUSUM and fusion (d) S = s1 + s2 + s3 + sL, with each
feature's mean and sigma fixed to the pooled calm ticks of the calm pfifo-r1 runs instead of learned
per flow; arms at the first unmasked tick. G_ref per variant from the calm pfifo-r1 runs as before.
v1 stays in the tables as an internal reference only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shadow_v2_step3 as s3  # noqa: E402

if __name__ == "__main__":
    s3.FEATURES = ("fuse d: s1+s2+s3+sL", "fuse d fixed")
    s3.VARIANTS = ("keep",)
    s3.V1 = {"shadow": "fuse", "gcc": None, "bbr": None}
    s3.EXTRA_CELLS = [("ppbp (all AQMs)", None, ("ppbp",)), ("calm090 (all AQMs)", None, ("calm090",)),
                      ("calmcbr090 (all AQMs)", None, ("calmcbr090",)), ("tcpcubic red", "red", ("tcpcubic",)),
                      ("fq_codel competition", "fq_codel", ("burstudp", "onoff", "tcpcubic", "tcpbbr", "splitudp")),
                      ("burstcapshallow pfifo", "pfifo", ("burstcapshallow",)), ("burstlong (all AQMs)", None, ("burstlong",))]
    s3.NAME = "step4b"
    s3.main(sys.argv[1:])
