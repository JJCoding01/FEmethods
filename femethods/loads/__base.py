"""
Module to define different loads
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable

import numpy as np
import numpy.typing as npt

from ..core import Force


class Load(Force, ABC):
    """Base class for all load types

    Used primarily for type checking the loads on input

    Parameters:
        magnitude: number: magnitude of the force of moment load
        location: number: defaults to 0. Location of the load
        fm_factor: force-moment factor. This is pair of factors that are applied to the
            magnitude to get the force and moment of the load.
    """

    name = ""

    __fm_factor: npt.NDArray[np.float64]

    def __init__(
        self, magnitude: float, location: float = 0, fm_factor: tuple[int, int] = (1, 0)
    ) -> None:
        super().__init__(magnitude, location)

        self.fm_factor = fm_factor

    @property
    def fm_factor(self) -> npt.NDArray[np.float64]:
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
    def fm_factor(self, value: tuple[int, int]) -> None:
        if not isinstance(value, Iterable):
            raise TypeError("fm_factor must be an iterable of length 2!")
        output_value = np.array(value)
        if len(output_value) != 2:
            raise ValueError("fm_factor must have length 2!")
        self.__fm_factor = output_value

    @property
    def __load_magnitude(self) -> npt.NDArray[np.float64]:
        """the actual magnitude of force and moment after applying the proper split"""
        assert self.magnitude is not None
        return self.magnitude * self.fm_factor

    @abstractmethod
    def fe(self, a: float, b: float) -> npt.NDArray[np.float64]:
        """
        Equivalent nodal forces and moments
        Parameters:
            a: float: offset from left node to location of load
            b: float: offset from load location to right node

        Returns:
             np.array: equivalent loads in the form [F1, M1, F2, M2]
        """

        raise NotImplementedError

    def __getitem__(self, item: int) -> float:
        # force the index of the numpy array to a float
        return float(self.__load_magnitude[item])

    def __str__(self) -> str:
        str_ = (
            f"Type: {self.name}\n"
            f"    Location: {self.location}\n"
            f"    Magnitude: {self.__load_magnitude}\n"
        )
        return str_
