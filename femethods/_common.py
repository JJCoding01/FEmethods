"""
Base module that contains base classes to be used by other modules
"""

from abc import ABC
from typing import Callable, Optional

from numpy import float64


class Forces(ABC):
    """Base class for all loads and reactions"""

    def __init__(self, magnitude: Optional[float], location: float = 0) -> None:
        self.magnitude = magnitude
        self.location = location

    @property
    def magnitude(self) -> Optional[float]:
        return self._magnitude

    @magnitude.setter
    def magnitude(self, magnitude: float) -> None:
        if not isinstance(magnitude, (int, float, type(None))):
            raise TypeError("force value must be a number")
        self._magnitude = magnitude

    @property
    def location(self) -> float:
        return self._location

    @location.setter
    def location(self, location: float) -> None:
        if location < 0:
            # location must be positive to be a valid length/position
            raise ValueError("location must be positive!")
        self._location = location

    def __repr__(self) -> str:
        return (
                f"{self.__class__.__name__}(magnitude={self.magnitude}, "
                + f"location={self.location})"
        )

    def __add__(self, force2: "Forces") -> "Forces":

        # assert to validate type checking for mypy
        assert self.magnitude is not None
        assert force2.magnitude is not None

        f1 = self.magnitude
        x1 = self.location

        f2 = force2.magnitude
        x2 = force2.location

        x = (f1 * x1 + f2 * x2) / (f1 + f2)
        return self.__class__(f1 + f2, x)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if self.magnitude is None or other.magnitude is None:
            return False
        return self.magnitude * self.location == other.magnitude * other.location

    def __sub__(self, force2: "Forces") -> "Forces":

        assert self.magnitude is not None
        assert force2.magnitude is not None

        f1 = self.magnitude
        x1 = self.location

        f2 = force2.magnitude
        x2 = force2.location

        x = (f1 * x1 - f2 * x2) / (f1 - f2)
        return self.__class__(f1 - f2, x)


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
