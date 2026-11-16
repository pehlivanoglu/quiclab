"""qtraffic's suite-v3 processes (qvideo/src/Departures.h) through `--mode=plan`,
which writes every departure a send run would emit, plus one short loopback
send/recv for the per-flow sockets. Skipped when the binary predates them
(rebuild: cmake --build qvideo/build --target qtraffic)."""

from __future__ import annotations

import csv
import math
import subprocess
import time
from pathlib import Path

import numpy as np
import pytest

QTRAFFIC = Path(__file__).resolve().parents[2] / "qvideo" / "build" / "qtraffic"


def _has_plan() -> bool:
    if not QTRAFFIC.exists():
        return False
    out = subprocess.run([str(QTRAFFIC), "--helpfull"], capture_output=True, text=True)
    return "flow_weights" in out.stdout + out.stderr


pytestmark = pytest.mark.skipif(not _has_plan(), reason="qtraffic without --mode=plan; rebuild qvideo")


def plan(tmp_path: Path, *args: str) -> np.ndarray:
    out = tmp_path / "p"
    subprocess.run([str(QTRAFFIC), "--mode=plan", "--dest=0.0.0.0", f"--out={out}", *args], check=True)
    rows = list(csv.DictReader(open(f"{out}-plan.csv")))
    return np.array([(int(r["t_us"]), int(r["flow"]), int(r["bytes"])) for r in rows], dtype=float).reshape(-1, 3)


def test_poisson_rates_and_exponential_gaps(tmp_path):
    d = plan(tmp_path, "--process=poisson", "--flow_weights=1,1,1,1,1,1,1,1,1,1,1",
             "--schedule=0:60:26.4", "--duration_s=60", "--seed=1")
    assert set(d[:, 1]) == set(range(11))
    total = d[:, 2].sum() * 8 / 60 / 1e6
    assert abs(total - 26.4) / 26.4 < 0.02
    for f in range(11):
        t = d[d[:, 1] == f, 0]
        rate = len(t) * 1200 * 8 / 60 / 1e6
        assert abs(rate - 2.4) / 2.4 < 0.05
        g = np.diff(t)
        assert abs(g.std() / g.mean() - 1) < 0.05            # exponential: CV 1
        # KS distance to the exponential law with the same mean
        x = np.sort(g)
        ks = np.max(np.abs(np.arange(1, len(x) + 1) / len(x) - (1 - np.exp(-x / g.mean()))))
        assert ks < 1.36 / math.sqrt(len(x)) * 1.5
    assert (d[:, 2] == 1200).all()


def test_poisson_weights_seeds_and_independence(tmp_path):
    d = plan(tmp_path, "--process=poisson", "--flow_weights=2.5,2.5,0.5", "--schedule=0:40:5.5",
             "--duration_s=40", "--seed=7")
    rates = [d[d[:, 1] == f, 2].sum() * 8 / 40 / 1e6 for f in range(3)]
    assert abs(rates[0] - 2.5) < 0.15 and abs(rates[1] - 2.5) < 0.15 and abs(rates[2] - 0.5) < 0.06
    # flows are independent: 10 ms counts of flows 0 and 1 uncorrelated
    bins = np.arange(0, 40e6 + 1, 1e4)
    c0, _ = np.histogram(d[d[:, 1] == 0, 0], bins)
    c1, _ = np.histogram(d[d[:, 1] == 1, 0], bins)
    assert abs(np.corrcoef(c0, c1)[0, 1]) < 0.05
    again = plan(tmp_path, "--process=poisson", "--flow_weights=2.5,2.5,0.5", "--schedule=0:40:5.5",
                 "--duration_s=40", "--seed=7")
    other = plan(tmp_path, "--process=poisson", "--flow_weights=2.5,2.5,0.5", "--schedule=0:40:5.5",
                 "--duration_s=40", "--seed=8")
    assert np.array_equal(d, again) and not np.array_equal(d[:100], other[:100])


def test_poisson_surge_and_ramp_schedule(tmp_path):
    # on 5-7 s at 10 Mb/s, plus a staircase 10-12 s in 0.5 s steps of 2 Mb/s held to 14 s
    sched = "5:2:10," + ",".join(f"{10 + 0.5 * k:g}:{4 - 0.5 * k:g}:2" for k in range(4))
    d = plan(tmp_path, "--process=poisson", "--flow_weights=1,1,1,1", f"--schedule={sched}",
             "--duration_s=15", "--seed=2")
    t = d[:, 0] / 1e6
    assert ((t >= 5) & (t < 7) | (t >= 10) & (t < 14)).all()
    rate = lambda a, b: d[(t >= a) & (t < b), 2].sum() * 8 / (b - a) / 1e6   # noqa: E731
    assert abs(rate(5, 7) - 10) < 0.6
    for k in range(4):
        assert abs(rate(10 + 0.5 * k, 10.5 + 0.5 * k) - 2 * (k + 1)) < 0.9
    assert abs(rate(12, 14) - 8) < 0.5


def test_poisson_not_phase_locked(tmp_path):
    """Gate check 6 on the generator itself: 5 ms byte counts show no 1 Hz / 30 Hz line."""
    d = plan(tmp_path, "--process=poisson", "--flow_weights=" + ",".join(["1"] * 10),
             "--schedule=0:120:26.4", "--duration_s=120", "--seed=1")
    counts, _ = np.histogram(d[:, 0], np.arange(0, 120e6 + 1, 5000), weights=d[:, 2])
    spec = np.abs(np.fft.rfft(counts - counts.mean())) ** 2
    freq = np.fft.rfftfreq(len(counts), 0.005)
    for f0 in (1.0, 30.0):
        i = int(np.argmin(np.abs(freq - f0)))
        neigh = np.r_[spec[i - 60:i - 3], spec[i + 4:i + 61]]
        assert spec[i - 1:i + 2].max() < np.percentile(neigh, 99.9) * 3


def test_asv_pattern_rate_and_grid(tmp_path):
    # stream T0 = 0; ASV starts at 2 s; rate 5 Mb/s for GOPs 2-3, 10 Mb/s for 4-5
    d = plan(tmp_path, "--process=asv", "--start_unix_us=2000000", "--stream_start_us=0",
             "--schedule=0:2:5,2:2:10", "--duration_s=4", "--asv_key_spread_us=33000",
             "--asv_p_spread_us=4000", "--video_seed=1")
    t = d[:, 0] / 1e6
    r1 = d[t < 2, 2].sum() * 8 / 2 / 1e6
    r2 = d[t >= 2, 2].sum() * 8 / 2 / 1e6
    assert abs(r1 - 5) < 0.3 and abs(r2 - 10) < 0.6
    # frames start on the 30 fps grid of the shared stream, keyframes at whole seconds
    starts = np.unique(np.floor(t * 30 + 1e-6))
    assert len(starts) == 120
    gop = d[(t >= 0) & (t < 1)]
    key = gop[gop[:, 0] < 33000]
    assert key[:, 2].sum() > 3 * gop[(gop[:, 0] >= 33334) & (gop[:, 0] < 66667), 2].sum()
    assert key[:, 0].max() < 33000                   # a keyframe spreads over its 33 ms
    pf = gop[(gop[:, 0] >= 33334) & (gop[:, 0] < 66667), 0]
    assert pf.max() - pf.min() < 4000                # a P-frame over its 4 ms


def test_asv_ramp_zero_rate_gop_is_silent(tmp_path):
    d = plan(tmp_path, "--process=asv", "--stream_start_us=0", "--schedule=1:1:5", "--duration_s=3")
    t = d[:, 0] / 1e6
    assert len(d) and ((t >= 1) & (t < 2)).all()


def test_loopback_flows_have_distinct_source_ports(tmp_path):
    port = 47311
    out = tmp_path / "lo"
    recv = subprocess.Popen([str(QTRAFFIC), "--mode=recv", "--bind=127.0.0.1", f"--port={port}", f"--out={out}"])
    try:
        time.sleep(0.2)
        subprocess.run([str(QTRAFFIC), "--mode=send", "--process=poisson", "--flow_weights=1,1,1,1",
                        "--bind=127.0.0.1", "--dest=127.0.0.1", f"--port={port}", "--schedule=0:1.5:8",
                        "--duration_s=1.5", f"--out={out}"], check=True, timeout=10)
        time.sleep(0.3)
    finally:
        recv.terminate()
        recv.wait(5)
    flows = list(csv.DictReader(open(f"{out}-flows.csv")))
    assert len(flows) == 4 and len({f["src_port"] for f in flows}) == 4
    sent = sum(int(f["bytes"]) for f in flows)
    assert abs(sent * 8 / 1.5 / 1e6 - 8) < 1.2
    rx = list(csv.DictReader(open(f"{out}-recv.csv")))
    assert sum(int(r["lost"]) for r in rx) == 0
    assert sum(int(r["bytes"]) for r in rx) == sent
    s5 = list(csv.DictReader(open(f"{out}-sent5.csv")))
    assert sum(int(r["sent_bytes"]) for r in s5) <= sent and len(s5) >= 250


def test_loopback_tcp_paced_on_off(tmp_path):
    port = 47312
    out = tmp_path / "tcp"
    recv = subprocess.Popen([str(QTRAFFIC), "--mode=recv", "--proto=tcp", "--bind=127.0.0.1", f"--port={port}",
                             f"--out={out}"])
    try:
        time.sleep(0.2)
        subprocess.run([str(QTRAFFIC), "--mode=send", "--proto=tcp", "--cc=cubic", "--bind=127.0.0.1",
                        "--dest=127.0.0.1", f"--port={port}", "--schedule=0:0.5:16,1:0.5:16", "--duration_s=1.6",
                        f"--out={out}"], check=True, timeout=10)
        time.sleep(0.3)
    finally:
        recv.terminate()
        recv.wait(5)
    s5 = list(csv.DictReader(open(f"{out}-sent5.csv")))
    t = np.array([int(r["t_us"]) for r in s5], dtype=float)
    b = np.array([int(r["sent_bytes"]) for r in s5], dtype=float)
    rel = (t - t[0]) / 1e6
    on = b[(rel > 0.05) & (rel < 0.45)].sum() * 8 / 0.4 / 1e6
    off = b[(rel > 0.6) & (rel < 0.95)].sum()
    assert abs(on - 16) < 2.5 and off == 0
    rx = list(csv.DictReader(open(f"{out}-recv.csv")))
    assert sum(int(r["bytes"]) for r in rx) > 0.9 * b.sum()
