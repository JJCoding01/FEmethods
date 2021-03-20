from typing import Callable

from numpy import float64


def derivative(
    func: Callable, x0: float, n: int = 1, method: str = "forward"
) -> float64:
    """
    Calculate the nth derivative of function f at x0

     Calculate the 1st or 2nd order derivative of a function using
     the forward or backward method.
    """

    if n not in (1, 2):
        raise ValueError("n must be 1 or 2")

    # Note that the value for dx is set manually. This is because the ideal
    # values are not constant based on the method used.
    # TODO determine better method for choosing a more ideal dx value
    if method == "forward":
        dx = 1e-8
        if n == 1:
            return (func(x0 + dx) - func(x0)) / dx
        elif n == 2:
            return (func(x0 + 2 * dx) - 2 * func(x0 + dx) + func(x0)) / dx ** 2
    elif method == "backward":
        dx = 1e-5
        if n == 1:
            return (func(x0) - func(x0 - dx)) / dx
        elif n == 2:
            return (func(x0) - 2 * func(x0 - dx) + func(x0 - 2 * dx)) / dx ** 2

    raise ValueError(f'invalid method parameter "{method}"')
