"""
Base module that contains base classes to be used by other modules
"""

from abc import ABC
from typing import Optional


class Forces(ABC):
    """Base class for all loads and reactions"""

    def __init__(
        self, magnitude: Optional[float], location: float = 0
    ) -> None:
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

    def __add__(self, force2: "Forces") -> Optional["Forces"]:

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
        if self.magnitude is None and other.magnitude is None:
            return self.location == other.location
        if self.magnitude is None or other.magnitude is None:
            return False
        return (
            self.magnitude * self.location == other.magnitude * other.location
        )

    def __sub__(self, force2: "Forces") -> Optional["Forces"]:

        assert self.magnitude is not None
        assert force2.magnitude is not None

        f1 = self.magnitude
        x1 = self.location

        f2 = force2.magnitude
        x2 = force2.location

        x = (f1 * x1 - f2 * x2) / (f1 - f2)
        return self.__class__(f1 - f2, x)
