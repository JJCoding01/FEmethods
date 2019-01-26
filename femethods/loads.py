"""
Module to define different loads
"""

from ._common import Forces


class PointLoad(Forces):
    """
    class specific to a point load
    """

    name = 'point load'

    def __init__(self, value, location):
        super().__init__(value, location)


class MomentLoad(Forces):
    """
    class specific to a moment load
    """

    name = 'moment load'

    def __init__(self, value, location):
        super().__init__(value, location)
