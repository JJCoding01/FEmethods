"""
Module to define different loads
"""

from ._common import Forces


class PointLoad(Forces):
    """
    class specific to a point load
    """

    name = "point load"

    def __init__(self, magnitude, location):
        super().__init__(magnitude, location)


class MomentLoad(Forces):
    """
    class specific to a moment load
    """

    name = "moment load"

    def __init__(self, magnitude, location):
        super().__init__(magnitude, location)
