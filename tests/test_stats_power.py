import numpy as np

from app.executor import cont_stats, power_normal


def test_mean_ci_power():
    a = np.array([1, 2, 3, 4])
    b = np.array([2, 3, 4, 5])
    res = cont_stats(a, b)
    assert round(res["delta"], 1) == 1.0
    pwr = power_normal(1.0, res["sp"], 50, 0.05)
    assert 0 < pwr < 1
