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

    def __str__(self):
        return f'PointLoad(value={self.value}, location={self.location})'

    def __repr__(self):
        return f'PointLoad(value={self.value}, location={self.location})'


class MomentLoad(Forces):
    """
    class specific to a moment load
    """

    name = 'moment load'

    def __init__(self, value, location):
        super().__init__(value, location)

    def __str__(self):
        return f'MomentLoad(value={self.value}, location={self.location})'

    def __repr__(self):
        return f'MomentLoad(value={self.value}, location={self.location})'
