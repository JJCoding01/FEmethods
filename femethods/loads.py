"""
Module to define different loads
"""

from ._common import Forces


class Load(Forces):
    """Base class for all load types

    Used primarily for type checking the loads on input
    """
    pass


class PointLoad(Load):
    """
    class specific to a point load
    """

    name = "point load"

    def __init__(self, magnitude, location):
        super().__init__(magnitude, location)


class MomentLoad(Load):
    """
    class specific to a moment load
    """

    name = "moment load"

    def __init__(self, magnitude, location):
        super().__init__(magnitude, location)
