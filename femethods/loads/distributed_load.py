"""
Module to define different loads
"""
import numpy as np

from scipy import integrate

from femethods import validation


class DistributedLoad:
    """
    Base class for all distributed loads

    Parameters:
        func: function defining the magnitude of the load distribution.
            Must be a function of x.
        start: numeric: numeric starting position of load distribution. Defaults to 0.
            Must be less than stop.
        stop: numeric: numeric ending position of load distribution. Defaults None.
        args: tuple: additional arguments to func

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

    def __equivalent_magnitudes(self, nodes):
        """
        magnitude of distributed load acting on each element

        Parameters:
            nodes: sequence: locations of nodes. Must include the start and stop
                location of the load

        Raises:
            ValueError: when nodes parameter does not include either start or stop
                locations of the load
            ValueError: when nodes are not sorted in ascending order
        """

        if not np.all(np.diff(nodes) >= 0):
            # the nodes are not sorted in ascending order!
            raise ValueError("invalid nodes! They must be in ascending order!")
        if self.start not in nodes or self.stop not in nodes:
            raise ValueError("invalid nodes and distributed loads! Incompatible mesh.")

        # get the lengths of each element
        lengths = np.diff(nodes)
        magnitudes = []
        for node, length in zip(nodes, lengths):
            if self.start <= node <= self.stop:
                # ignore type check for self.func:
                # Union[function, LowLevelCallable], got Callable instead
                # noinspection PyTypeChecker
                mag = integrate.quad(
                    self.func, a=node, b=node + length, args=self.args
                )[0]
                magnitudes.append(mag)
                if self.stop == node + length:
                    # the distributed loads stops at the end of the current element.
                    # No further analysis is required
                    break

        return magnitudes

    def equivalent_magnitude(self, nodes):
        """
        Magnitude of total force

        The magnitude is equal to the integral of the force function from start to
        stop
        """
        # return integrate.quad(self.func, a=self.start, b=self.stop, args=self.args)[0]
        magnitude = self.__equivalent_magnitudes(nodes)
        if len(magnitude) == 1:
            return magnitude[0]
        return magnitude

    def __centroid_locations(self, nodes):
        """
        locations of centroid of distributed load acting on each element

        There is a location for each element that has the load acting on it. The
        location(s) returned are the centroid of the load acting over each element.

        Parameters:
            nodes: sequence: locations of nodes. Must include the start and stop
                location of the load

        Raises:
            ValueError: when nodes parameter does not include either start or stop
                locations of the load
            ValueError: when nodes are not sorted in ascending order
        """

        def equiv_fun(a, b, func, *args):
            """
            function to calculate centroid of load between a and b

            Parameters:
                a: float: starting location for integration (current node)
                b: float: ending location for integration (next node)
                func: callable: function that defines the load magnitude as a function
                    of position
                args: tuple: optional arguments for func

            See Also:
                page 9 of this PDF defines the equation used to calculate the centroid
                https://web.iit.edu/sites/web/files/departments/academic-affairs/academic-resource-center/pdfs/Distributed_Loading.pdf
            """
            # pylint: disable=invalid-name
            wx = integrate.quad(lambda x: func(x, *args) * x, a, b)[0]
            w = integrate.quad(lambda x: func(x, *args), a, b)[0]
            return wx / w

        if not np.all(np.diff(nodes) >= 0):
            # the nodes are not sorted in ascending order!
            raise ValueError("invalid nodes! They must be in ascending order!")
        if self.start not in nodes or self.stop not in nodes:
            raise ValueError("invalid nodes and distributed loads! Incompatible mesh.")

        lengths = np.diff(nodes)  # lengths of all elements
        locations = []
        used_lengths = []
        for node, length in zip(nodes, lengths):
            if self.start <= node <= self.stop:
                # current node has the distributed load applied to it
                used_lengths.append(length)
                global_location = equiv_fun(node, node + length, self.func, self.args)
                local_location = global_location - node
                locations.append(local_location)
                if node + length == self.stop:
                    # the distributed loads stops at the end of the current element.
                    # No further analysis is required
                    break

        return used_lengths, locations

    def centroid_location(self, nodes):
        """
        locations along beam that define centroid of the distributed load for each element

        Parameters:
            nodes: np.array: locations of nodes in the mesh. There must be a node that
                corresponds to the start and stop locations of the distributed load,
                otherwise an exception is raised.
        """
        _, locations = self.__centroid_locations(nodes)
        if len(locations) == 1:
            return locations[0]
        return locations
