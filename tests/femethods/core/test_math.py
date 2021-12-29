# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import numpy as np
import pytest

from femethods.core import derivative


@pytest.mark.parametrize("method", ("f", "b", None))
def test_invalid_method(method):
    with pytest.raises(ValueError):
        derivative(lambda x: x, 0, method=method)


@pytest.mark.parametrize("order", (0, 3, None))
def test_invalid_order(order):
    with pytest.raises(ValueError):
        derivative(lambda x: x, 0, n=order)


@pytest.mark.parametrize("method", ("forward", "backward"))
@pytest.mark.parametrize("angle", np.linspace(0, 2 * np.pi, 10))
def test_derivative_1_sine(method, angle):
    expected_derivative = np.cos(angle)
    assert derivative(np.sin, angle, n=1, method=method) == pytest.approx(
        expected_derivative, abs=1e-3
    )


@pytest.mark.parametrize("method", ("forward", "backward"))
@pytest.mark.parametrize("x", np.linspace(0, 10, 3))
def test_derivative_1_poly(method, x):
    expected_derivative = 2 * x + 5
    assert derivative(
        lambda x: x ** 2 + 5 * x + 3, x, n=1, method=method
    ) == pytest.approx(expected_derivative, abs=0.005)


@pytest.mark.parametrize("method", ("forward", "backward"))
@pytest.mark.parametrize("x", np.linspace(0, 10, 3))
def test_derivative_1_line(method, x):
    expected_derivative = 5
    assert derivative(lambda x: 5 * x + 29, x, n=1, method=method) == pytest.approx(
        expected_derivative, abs=1e-3
    )


@pytest.mark.parametrize("method", ("forward", "backward"))
@pytest.mark.parametrize("angle", np.linspace(0, 2 * np.pi, 10))
def test_derivative_2_sine(method, angle):
    expected_derivative = -np.sin(angle)
    assert derivative(np.sin, angle, n=2, method=method) == pytest.approx(
        expected_derivative, abs=1e-3
    )


@pytest.mark.parametrize("method", ("forward", "backward"))
@pytest.mark.parametrize("x", np.linspace(0, 10, 3))
def test_derivative_2_poly(method, x):
    expected_derivative = 2
    assert derivative(
        lambda x: x ** 2 + 5 * x + 3, x, n=2, method=method
    ) == pytest.approx(expected_derivative, abs=1e-3)


@pytest.mark.parametrize("method", ("forward", "backward"))
@pytest.mark.parametrize("x", np.linspace(0, 10, 3))
def test_derivative_2_line(method, x):
    expected_derivative = 0
    assert derivative(lambda x_: 5 * x_ + 29, x, n=2, method=method) == pytest.approx(
        expected_derivative, abs=1e-3
    )
