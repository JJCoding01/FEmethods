"""
Base module that contains base classes to be used by other modules
"""


class Force:
    """Base class for all loads and reactions"""

    def __init__(self, magnitude, location=0):
        self.magnitude = magnitude
        self.location = location

    @property
    def magnitude(self):
        return self._magnitude

    @magnitude.setter
    def magnitude(self, magnitude):
        self._magnitude = magnitude

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(magnitude={self.magnitude}, "
            + f"location={self.location})"
        )

    def __add__(self, force2):

        if not isinstance(force2, self.__class__):
            # only addition between forces is implemented
            raise TypeError(f"cannot add {self.__class__} and {type(force2)}")

        f1 = self.magnitude
        x1 = self.location

        f2 = force2.magnitude
        x2 = force2.location

        x = (f1 * x1 + f2 * x2) / (f1 + f2)
        return self.__class__(f1 + f2, x)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.magnitude is None and other.magnitude is None:
            return self.location == other.location
        if self.magnitude is None or other.magnitude is None:
            return False
        return (
            self.magnitude * self.location == other.magnitude * other.location
        )

    def __sub__(self, force2):
        return self + self.__class__(-force2.magnitude, force2.location)
