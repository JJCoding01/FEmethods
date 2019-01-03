"""module that contains base classes used in multiple modules, misc helper
functions, and other code common to several modules
"""


class Forces(object):
    """Base class for all loads and reactions"""

    def __init__(self, location, value=0, label=None):
        self._location = location
        self._label = label
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

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    def moment(self):
        return self._value * self.location

    def __str__(self):
        return f'{self._label} ({self._value}, {self._location})'

    def __add__(self, force2):
        return self._value + force2._value

    def __sub__(self, load2):
        return self.value - load2.value
