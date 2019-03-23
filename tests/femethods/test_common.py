import numpy as np
from pytest import approx, raises
from scipy.misc import derivative

import femethods._common as comm


def test_derivative():
    funcs = [np.cos, np.sin, lambda x: np.e ** x]  # test functions
    x0s = [0, np.pi, 0]  # test points
    dx = 1e-5

    # iterate over functions and test points and check first and second
    # derivatives using the forward and backward method and compare them to
    # scipy's central difference method
    for func, x0, in zip(funcs, x0s):
        for n, method in zip([1, 2], ['forward', 'backward']):
            der = comm.derivative(func, x0=x0, method=method, n=n)
            central = derivative(func, x0, dx=dx, n=n)
            assert approx(der, rel=1) == central

        with raises(ValueError):
            comm.derivative(func, 0, method='incorrect method')

        with raises(ValueError):
            comm.derivative(func, 0, method='forward', n=3)
