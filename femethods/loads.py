"""
Module to define different loads
"""

from typing import Optional

from femethods.core._common import Forces


class Load(Forces):
    """Base class for all load types

    Used primarily for type checking the loads on input
    """

    name = ""


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
