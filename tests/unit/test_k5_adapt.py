"""K5-sender CC-driven rate adaptation: off by default, bounded, and absent from the server argv unless on."""

import inspect

import pytest
from pydantic import ValidationError

from quiclab.config.schema import PublisherConfig
from quiclab.orchestrator import mininet_backend


def test_adapt_off_by_default():
    p = PublisherConfig()
    assert p.adapt_x == 0.0
    assert p.adapt_floor == 0.3


@pytest.mark.parametrize("x", [-0.1, 2.5])
def test_adapt_x_bounds(x):
    with pytest.raises(ValidationError):
        PublisherConfig(adapt_x=x)


@pytest.mark.parametrize("floor", [0.0, 1.5])
def test_adapt_floor_bounds(floor):
    with pytest.raises(ValidationError):
        PublisherConfig(adapt_floor=floor)


def test_adapt_flags_only_when_on():
    # the server argv carries --adapt_* only under `if publisher.adapt_x > 0`, so every existing plan
    # (adapt_x unset) starts the server with the same arguments as before
    src = inspect.getsource(mininet_backend)
    i = src.index('f"--adapt_x={publisher.adapt_x}"')
    assert "if publisher.adapt_x > 0 else []" in src[i:i + 200]


def _k5():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    import k5_suite
    return k5_suite


def test_k5_plan_counts():
    k = _k5()
    cells = k.k5()
    runs = [(c.block, c.variant, aqm, s) for c in cells for aqm in c.aqms for s in c.seeds]
    by = {}
    for b, *_ in runs:
        by[b] = by.get(b, 0) + 1
    assert by == {"S1": 48, "S2": 4, "A1": 32, "P1": 28, "G1": 16, "G2": 6, "G3": 8}
    assert len(runs) == 142
    assert not any(a in ("fq_codel", "cake") for _, _, a, _ in runs)
    assert all(c.seeds == (1, 2) and c.point == "DEF" for c in cells)


def test_k5_reference_cells_left_out():
    cells = _k5().k5()
    p1 = {(c.variant, a) for c in cells if c.block == "P1" for a in c.aqms}
    assert ("bbr-b1000-off", "pfifo") not in p1 and ("bbr-b1000-off", "codel") not in p1
    s_off_1000 = {(c.variant, a) for c in cells if c.rtype == "sburst" and c.variant.endswith("b1000-off") for a in c.aqms}
    assert s_off_1000 == {("copa-b1000-off", "pie"), ("copa-b1000-off", "red")}


def test_k5_policy_opts():
    k = _k5()
    v, o = k.policy("copa", 3000, True)
    assert v == "copa-b3000-on" and o == {"cc": "copa", "send_buffer_ms": 3000, "adapt_x": 0.85, "adapt_floor": 0.3}
    v, o = k.policy("bbr", 0, False)
    assert v == "bbr-b0-off" and o == {"send_buffer_ms": 0}
