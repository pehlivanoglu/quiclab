import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import owd_mode  # noqa: E402


def fake_run(tmp_path: Path, fwd_ms, rev_ms):
    """One ACK every 5 ms for 30 s; OWD = forward delay, RTT = forward + reverse delay."""
    n = len(fwd_ms)
    sent = 1_000_000 + np.arange(n) * 5000
    rtt = (np.asarray(fwd_ms) + np.asarray(rev_ms)) * 1000
    # ACK processing times increase, as in the real log
    pd.DataFrame({"mono_us": sent + 100_000, "sent_mono_us": sent, "rtt_us": rtt.astype(int),
                  "min_rtt_us": int(rtt.min()), "srtt_us": rtt.astype(int), "phase": "probe_bw"}).to_csv(
        tmp_path / "s-acks.csv", index=False)
    pd.DataFrame({"bin_mono_us": sent // 5000 * 5000, "owd_min_us": (np.asarray(fwd_ms) * 1000).astype(int)}).to_csv(
        tmp_path / "s-owd.csv", index=False)
    return SimpleNamespace(sender_file=lambda sid, kind: tmp_path / f"{sid}-{kind}.csv")


def test_reverse_delay_is_invisible_and_forward_delay_shows(tmp_path):
    n = 6000  # 30 s
    fwd = np.full(n, 20.0)
    rev = np.full(n, 20.0)
    rev[3000:3600] += 50  # reverse (ACK path) step at 15 s for 3 s
    fwd[4400:5000] += 30  # forward step at 22 s for 3 s
    out = tmp_path / "out"
    out.mkdir()
    acks = pd.read_csv(owd_mode.owd_acks(fake_run(tmp_path, fwd, rev), "s", out))
    rtt = acks["rtt_us"].to_numpy() / 1000
    assert np.allclose(rtt[:3000], 40.0)  # R0 = min RTT - min OWD keeps the RTT scale
    assert np.allclose(rtt[3000:3600], 40.0)  # reverse step gone
    assert np.allclose(rtt[4400:5000], 70.0)  # forward step kept
    assert (acks["min_rtt_us"] == 40000).all()
    assert (acks["srtt_us"].to_numpy()[3000:3600] == 90000).all()  # time scales untouched
