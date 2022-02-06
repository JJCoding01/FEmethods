"""
Module to define different loads
"""
import numpy as np

from scipy import integrate

from femethods import validation

from .moment import MomentLoad
from .point import PointLoad


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

    # pylint: disable=invalid-name
    @staticmethod
    def __p0(p, a, b, l):
        """
        equivalent point load at node 0

        Note that on its own, this load is not equivalent to the distributed load! It
        is only when p0, m0, p1, and m1 are used together as a system that they are
        equivalent!

        Parameters:
            p: float: equivalent magnitude of distributed load acting on element
            a: float: distance from start of node to load centroid
            b: float: distance from centroid to second node of element
            l: float: length of element

        Returns:
            float: magnitude of force acting on node 0 (left side)

        See Also:
             :class:`__m0`: for moment load at node 0
             :class:`__p1`: for point load at node 1
             :class:`__m1`: for moment load at node 1
        """
        return (p * b ** 2 * (l + 2 * a)) / l ** 3

    # pylint: disable=invalid-name
    @staticmethod
    def __m0(p, a, b, l):
        """
        equivalent moment load at node 0

        Note that on its own, this load is not equivalent to the distributed load! It
        is only when p0, m0, p1, and m1 are used together as a system that they are
        equivalent!

        Note this is the opposite direction as :class:`__m1`.

        Parameters:
            p: float: equivalent magnitude of distributed load acting on element
            a: float: distance from start of node to load centroid
            b: float: distance from centroid to second node of element
            l: float: length of element

        Returns:
            float: magnitude of moment acting on node 0 (left side)

        See Also:
             :class:`__p0`: for point load at node 0
             :class:`__p1`: for point load at node 1
             :class:`__m1`: for moment load at node 1
        """
        return -p * a * b ** 2 / l ** 2

    # pylint: disable=invalid-name
    @staticmethod
    def __p1(p, a, b, l):
        """
        equivalent moment load at node 1

        Note that on its own, this load is not equivalent to the distributed load! It
        is only when p0, m0, p1, and m1 are used together as a system that they are
        equivalent!

        Parameters:
            p: float: equivalent magnitude of distributed load acting on element
            a: float: distance from start of node to load centroid
            b: float: distance from centroid to second node of element
            l: float: length of element

        Returns:
            float: magnitude of force acting on node 1 (right side)

        See Also:
             :class:`__p0`: for point load at node 0
             :class:`__m0`: for moment load at node 0
             :class:`__m1`: for moment load at node 1
        """
        return p * a ** 2 * (l + 2 * b) / l ** 3

    # pylint: disable=invalid-name
    @staticmethod
    def __m1(p, a, b, l):
        """
        equivalent moment load at node 1

        Note that on its own, this load is not equivalent to the distributed load! It
        is only when p0, m0, p1, and m1 are used together as a system that they are
        equivalent!

        Parameters:
            p: float: equivalent magnitude of distributed load acting on element
            a: float: distance from start of node to load centroid
            b: float: distance from centroid to second node of element
            l: float: length of element

        Returns:
            float: magnitude of moment acting on node 1 (right side)

        See Also:
             :class:`__p0`: for point load at node 0
             :class:`__m0`: for moment load at node 0
             :class:`__p1`: for point load at node 1
        """
        return p * a ** 2 * b / l ** 2

    @staticmethod
    def centroid(a, b_, func, *args):
        """
        return the centroid of an arbitrary function between a and b

        Parameters:
            a: float: starting location
            b_: float: ending location
            func: callable: function to find the centroid of
            args: tuple: optional arguments for func

        See Also:
            page 9 of this PDF defines the equation used to calculate the centroid
            https://web.iit.edu/sites/web/files/departments/academic-affairs/academic-resource-center/pdfs/Distributed_Loading.pdf
        """
        # pylint: disable=invalid-name
        wx = integrate.quad(lambda x: func(x, *args) * x, a, b_)[0]
        w = integrate.quad(lambda x: func(x, *args), a, b_)[0]
        return wx / w

    def equiv(self, nodes):
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

        if not np.all(np.diff(nodes) >= 0):
            # the nodes are not sorted in ascending order!
            raise ValueError("invalid nodes! They must be in ascending order!")
        if self.start not in nodes or self.stop not in nodes:
            raise ValueError("invalid nodes and distributed loads! Incompatible mesh.")

        lengths = np.diff(nodes)  # lengths of all elements
        loads = []
        for node, length in zip(nodes, lengths):
            element_is_loaded = self.start <= node <= self.stop
            if not element_is_loaded:
                continue

            # current element is loaded with distributed load

            # calculate the location of the centroid of the load applied to the
            # current element
            global_location = self.centroid(node, node + length, self.func, self.args)
            local_location = global_location - node

            # calculate the magnitude of the equivalent point load acting at the
            # centroid of the distributed load of the active element
            # ignore type check for self.func:
            # Union[function, LowLevelCallable], got Callable instead
            # noinspection PyTypeChecker
            f_equiv = integrate.quad(self.func, node, node + length, args=self.args)[0]

            # setup general geometry terms locating the load relative the element
            # origin (x_local = 0)

            # calculate the equivalent point load and moment produced by relocating the
            # point load acting at the distributed load centroid to the start and stop
            # nodes of the active element.
            # Note that the moments act in opposite directions'
            #
            # description of loads:
            #   * p0: equivalent point load at node 0 (left) of current element
            #   * m0: equivalent moment load at node 0 (left) of current element
            #   * p1: equivalent point load at node 1 (right) of current element
            #   * m1: equivalent moment load at node 1 (right) of current element
            # distance from equivalent load to right node
            b = length - local_location
            p0 = self.__p0(p=f_equiv, a=local_location, b=b, l=length)
            m0 = self.__m0(p=f_equiv, a=local_location, b=b, l=length)
            p1 = self.__p1(p=f_equiv, a=local_location, b=b, l=length)
            m1 = self.__m1(p=f_equiv, a=local_location, b=b, l=length)

            # ... then create proper loads from the point/moment magnitudes and add
            # them to a list of loads. This list of loads will be made up of basic
            # PointLoad and MomentLoad combinations and will be equivalent to the
            # distributed load
            loads.extend(
                [
                    PointLoad(p0, node),
                    MomentLoad(m0, node),
                    PointLoad(p1, node + length),
                    MomentLoad(m1, node + length),
                ]
            )

        return loads
