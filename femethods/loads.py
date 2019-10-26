"""
Module to define different loads
"""
from abc import ABC
from typing import Optional

from femethods.core._common import Forces


class Load(Forces):
    """Base class for all load types

    Used primarily for type checking the loads on input
    """

    name = ""


class DistributedLoadBase(Load):
    """
    Base class for all distributed loads
    """

    def __init__(
        self,
        start: float = 0,
        stop: Optional[float] = None,
        W: float = 0,
        **kwargs
    ) -> None:
        """
        definition of a distributed load
        """
        super().__init__(**kwargs)
        self._start = start
        self._stop = stop
        self._W = W  # intensity of load

    @property
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, k) -> None:
        self._start = k

    @property
    def stop(self) -> Optional[float]:
        return self._stop

    @stop.setter
    def stop(self, k) -> None:
        self._stop = k

    @property
    def W(self) -> float:
        return self._W

    @W.setter
    def W(self, w) -> None:
        self._W = w


class ConstantDistributedLoad(DistributedLoadBase):

    name = "constant load"

    def __init__(self, start, stop, W, **kwargs) -> None:

        # assert self.stop is not None
        # # calculate the magnitude of the equivalent PointLoad (area under curve)

        # force = self.magnitude * self.start * self.stop
        magnitude = W * (stop - start)

        # calculate the location of the centroid of the distributed load
        loc = (stop + start) / 2

        self._equivalent = PointLoad(magnitude=magnitude, location=loc)
        super().__init__(
            start=start,
            stop=stop,
            W=W,
            magnitude=magnitude,
            location=loc,
            **kwargs
        )

    @property
    def equivalent(self):
        return self._equivalent


class PointLoad(Load):
    """
    class specific to a point load
    """

    name = "point load"

    def __init__(self, magnitude: Optional[float], location: float):
        super().__init__(magnitude, location)


class MomentLoad(Load):
    """
    class specific to a moment load
    """

    name = "moment load"

    def __init__(self, magnitude: float, location: float):
        super().__init__(magnitude, location)
