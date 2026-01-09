"""
Base module that contains base classes to be used by other modules
"""

from typing import Any, Optional


class Force:
    """Base class for all loads and reactions"""

    def __init__(self, magnitude: Optional[float], location: float = 0):
        self.magnitude = magnitude
        self.location = location

    @property
    def magnitude(self) -> Optional[float]:
        return self._magnitude

    @magnitude.setter
    def magnitude(self, magnitude: Optional[float]) -> None:
        self._magnitude = magnitude

    @property
    def location(self) -> float:
        return self._location

    @location.setter
    def location(self, location: float) -> None:
        self._location = location

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(magnitude={self.magnitude}, "
            + f"location={self.location})"
        )

    def __add__(self, force2: "Force") -> "Force":

        if not isinstance(force2, self.__class__):
            # only addition between forces is implemented
            raise TypeError(f"cannot add {self.__class__} and {type(force2)}")

        f1 = self.magnitude
        x1 = self.location
        assert f1 is not None

        f2 = force2.magnitude
        x2 = force2.location
        assert f2 is not None

        x = (f1 * x1 + f2 * x2) / (f1 + f2)
        return self.__class__(f1 + f2, x)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if self.magnitude is None and other.magnitude is None:
            return self.location == other.location
        if self.magnitude is None or other.magnitude is None:
            return False
        return self.magnitude * self.location == other.magnitude * other.location

    def __sub__(self, force2: "Force") -> "Force":
        if force2.magnitude is None:
            return self + self.__class__(None, force2.location)
        return self + self.__class__(-force2.magnitude, force2.location)
