"""
Module to define different loads
"""

from ._common import Forces


class PointLoad(Forces):
    """
    class specific to a point load
    """

    name = 'point load'

    def __init__(self, location, value):
        super().__init__(location, value)

    def __str__(self):
        return f'PointLoad(location={self.location}, value={self.value})'

    def __repr__(self):
        return f'PointLoad(location={self.location}, value={self.value})'


class MomentLoad(Forces):
    """
    class specific to a moment load
    """

    name = 'moment load'

    def __init__(self, location, value):
        super().__init__(location, value)

    def __str__(self):
        return f'MomentLoad(location={self.location}, value={self.value})'
