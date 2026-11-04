import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402
import det_matrix  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402


@pytest.mark.parametrize("topology", sorted(det_matrix.TOPOLOGIES))
@pytest.mark.parametrize("name", sorted(det_matrix.BURST_SCENARIOS))
def test_every_event_scenario_validates(name: str, topology: str, tmp_path: Path) -> None:
    targets = {t for tgt in det_matrix.BURST_SCENARIOS[name].get("targets", ()) for t in tgt.split("+")}
    if not targets <= set(det_matrix.TOPOLOGIES[topology][2]):
        pytest.skip(f"{name} targets bottlenecks {topology} does not have")
    topo = load_topology(ROOT / "configs" / "topologies" / det_matrix.TOPOLOGIES[topology][0])
    load_scenario(det_matrix.scenario_for(name, "pfifo", 1, tmp_path, topology), topo)


def test_split_bursts_hit_only_their_bottleneck() -> None:
    n = det_matrix.topology_numbers("split")
    assert set(n["hops"]["a"]["clients"]) == {"a1", "a2", "a3"}
    assert set(n["hops"]["up"]["clients"]) == {"a1", "a2", "a3", "b1", "b2", "b3"}  # sub-ctrl branches off r1
    events, _ = det_matrix.burst_events("splitcap", seed=1, topology="split")
    starts = [e for e in events if e.get("label", "").startswith("burst u=")]
    assert len(starts) == 2 * 3 * 5  # (u, d) x targets, "a+up" drops two links
    serial = [e for e in starts if e["at_s"] == next(x["at_s"] for x in starts if x["label"].endswith(" a")
                                                       and sum(y["at_s"] == x["at_s"] for y in starts) == 2)]
    assert {(e["from"], e["to"]) for e in serial} == {("r1", "r2"), ("r2", "switch-a")}


def _pts(owd_of, t_end=3.0, step=0.005):
    """(t, owd_min_ms, sent, timed) every 5 ms; owd_of(t) -> (owd_ms, sent, timed)."""
    return [(round(i * step, 3), *owd_of(i * step)) for i in range(int(t_end / step))]


def test_measured_bands_keyframe_spike_is_not_congestion() -> None:
    # 10 ms propagation; a 100 ms keyframe queue (shorter than the 200 ms transient window).
    pts = _pts(lambda t: (10 + (30 if 1.0 <= t < 1.1 else 0), 2, 2))
    assert {b for _, b in det_eval.measured_bands(pts, [])} == {"clear"}


def test_measured_bands_standing_queue_onset_and_delay_step() -> None:
    # Queue of 40 ms from 1.0 s to 1.5 s; propagation steps +20 ms at 2.0 s (not a queue).
    # One packet stamped just before the step leaves after it (lower delay than its segment).
    pts = _pts(lambda t: (10 + (40 if 1.0 <= t < 1.5 else 0) + (20 if 2.0 <= t < 2.5 else 0)
                          - (20 if abs(t - 2.495) < 1e-9 else 0), 2, 2))
    bands = det_eval.measured_bands(pts, [2.0, 2.5])
    congested = [t for t, b in bands if b == "congested"]
    assert congested[0] == 1.0  # onset at the queue's start, not a window later
    assert all(t < 1.5 for t in congested)
    after = [(t, b) for t, b in bands if t >= 2.0]
    assert all(b == "none" for t, b in after if min(abs(t - 2.0), abs(t - 2.5)) < 0.25)  # netem transition
    assert all(b == "clear" for t, b in after if min(abs(t - 2.0), abs(t - 2.5)) >= 0.25)


def test_measured_bands_loss_onset_and_oracle_gap() -> None:
    # 40 % loss from 1.0 s, no queue; no receive timestamps at all after 2.0 s (oracle gap).
    def owd(t):
        if t >= 2.0:
            return None, 2, 0
        return 10, 5, (3 if t >= 1.0 else 5)
    bands = det_eval.measured_bands(_pts(owd), [])
    assert next(t for t, b in bands if b == "congested") == 1.0
    assert all(b == "ambiguous" for t, b in bands if t >= 2.0)
