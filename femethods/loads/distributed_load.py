"""
Module to define different loads
"""

from femethods import validation


class DistributedLoad:
    """
    Base class for all distributed loads

    Parameters:
        w: func: function defining the magnitude of the load distribution
        start: numeric: numeric starting position of load distribution. Defaults to 0.
            Must be less than stop.
        stop: numeric: numeric ending position of load distribution. Defaults None.

    Raises:
        TypeError: if start or stop are not numeric
        ValueError: if start is not less than stop
        ValueError: if start is negative
    """

    def __init__(self, func, start=0, stop=None, args=()):
        # set both start and stop to None. This way they are both defined for
        # comparisons with each other. They will both be updated to the proper values
        # given later
        self.__start, self.__stop = None, None

        self.func = func  # intensity of load as function of position
        self.start = start
        self.stop = stop
        self.args = args

    @property
    def func(self):
        """magnitude of distributed load as function of position"""
        return self.__func

    @func.setter
    def func(self, value):
        if not callable(value):
            raise TypeError("func must be a function to describe force magnitude!")
        self.__func = value

    @property
    def start(self):
        """
        starting location of load distribution

        Raises:
            TypeError: if not numeric
            ValueError: if greater than or equal to stop
        """
        return self.__start

    @start.setter
    @validation.is_numeric
    @validation.non_negative
    def start(self, value):
        if self.__stop is not None:
            if self.stop <= value:
                # the starting value cannot be greater than the stopping value
                raise ValueError(f"start must be less than stop ({self.stop})")
        self.__start = value

    @property
    def stop(self):
        """
        stopping location of load distribution

        Raises:
            TypeError: if not numeric
            ValueError: if less than or equal to stop
        """
        return self.__stop

    @stop.setter
    @validation.is_numeric
    @validation.non_negative
    def stop(self, value):

        # node that checking if start is None is not required here because start is
        # defined first. If it was deliberately set to None, it will raise an exception
        # and not get to this point anyway.
        if self.start >= value:
            # the starting value cannot be greater than the stopping value
            raise ValueError(f"stop must be greater than start ({self.start})")
        self.__stop = value

    def magnitude(self, x):
        """force magnitude at x"""
        return self.func(x, *self.args)
