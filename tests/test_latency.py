import numpy as np
import pytest

from simlab.latency import Chain, Stage, simulate

QUIET = Chain(rate_hz=50.0, acquisition=Stage(0.002), transport=Stage(0.001), processing=Stage(0.003))


def test_without_jitter_or_loss_latency_is_the_sum_of_the_stages():
    r = simulate(QUIET, n=200)
    assert r.lost == 0
    assert np.allclose(r.latency_s, 0.006)


def test_loss_is_close_to_the_configured_probability():
    chain = Chain(transport=Stage(0.001, 0.0, 0.1))
    r = simulate(chain, n=4000, seed=3)
    assert r.lost / r.sent == pytest.approx(0.1, abs=0.02)


def test_the_same_seed_gives_the_same_result():
    chain = Chain(transport=Stage(0.001, 0.002, 0.05))
    a, b = simulate(chain, n=300, seed=7), simulate(chain, n=300, seed=7)
    assert np.array_equal(a.latency_s, b.latency_s) and a.lost == b.lost


def test_processing_slower_than_the_sampling_period_makes_samples_queue():
    slow = Chain(rate_hz=50.0, processing=Stage(0.030))      # 30 ms service, 20 ms period
    r = simulate(slow, n=200)
    assert r.latency_s[-1] > 5 * r.latency_s[0]
