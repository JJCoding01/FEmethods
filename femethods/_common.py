"""module that contains base classes used in multiple modules, misc helper
functions, and other code common to several modules
"""


class Forces(object):
    """Base class for all loads and reactions"""

    def __init__(self, value, location=0):
        self._location = location
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    def moment(self):
        return self.value * self.location

    def __str__(self):
        return f'{self._label} ({self._load}, {self._location})'

    def __add__(self, force2):
        return self.value + force2.value

    def __sub__(self, load2):
        return self.value - load2.value