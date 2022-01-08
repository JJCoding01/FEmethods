"""
Module to define different loads
"""
from collections.abc import Iterable

import numpy as np

from ..core import Force


class Load(Force):
    """Base class for all load types

    Used primarily for type checking the loads on input

    Parameters:
        magnitude: number: magnitude of the force of moment load
        location: number: defaults to 0. Location of the load
        fm_factor: force-moment factor. This is pair of factors that are applied to the
            magnitude to get the force and moment of the load.
    """

    name = ""

    def __init__(self, magnitude, location=0, fm_factor=(1, 0)):
        super().__init__(magnitude, location)
        self.fm_factor = fm_factor

    @property
    def fm_factor(self):
        """
        Force-Moment split in magnitude

        The magnitude of the load is applied to a force and a moment.The fm_factor
        parameter determines how much of the magnitude is split into a force and a
        moment.

        Therefore, fm_factor must be of length 2.

        Attempts to convert iterable to numpy array.

        Raises:
            TypeError: when not an iterable
            ValueError: when not of length 2

        Warns:
            UserWarning: when both force and moment are 0 as this indicates the
                indicates no load is applied
        """
        return self.__fm_factor

    @fm_factor.setter
    def fm_factor(self, value):
        if not isinstance(value, Iterable):
            raise TypeError("fm_factor must be an iterable of length 2!")
        value = np.array(value)
        if len(value) != 2:
            raise ValueError("fm_factor must have length 2!")
        self.__fm_factor = value

    @property
    def __load_magnitude(self):
        """the actual magnitude of force and moment after applying the proper split"""
        return self.magnitude * self.fm_factor

    def __getitem__(self, item):
        return self.__load_magnitude[item]
