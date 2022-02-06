from itertools import cycle

import numpy as np

from .distributed_load import DistributedLoad
from .moment import MomentLoad
from .point import PointLoad


class ConstantDistributedLoad(DistributedLoad):
    """
    Constant distributed load

    Parameters:
        magnitude: numeric: linear load
        start: numeric: starting location of the load distribution, defaults to 0
        stop: numeric: ending location of the load distribution, defaults to None
    """

    name = "constant load"

    def __init__(self, magnitude, start=0, stop=None):
        super().__init__(func=lambda x, *args: magnitude, start=start, stop=stop)
        self.magnitude = magnitude

    def __equivalent_point_loads(self, nodes):
        magnitudes = self.equivalent_magnitude(nodes)
        locations = self.centroid_location(nodes)
        point_loads = [
            PointLoad(magnitude=f, location=x) for f, x in zip(magnitudes, locations)
        ]
        return point_loads

    def __equivalent_moments(self, nodes):
        lengths = np.diff(nodes)
        signs = cycle((-1, 1))
        magnitudes = [
            self.magnitude * length ** 2 / 12 for sign, length in zip(signs, lengths)
        ]
        moments = []
        for k, (f, sign) in enumerate(zip(magnitudes, signs)):
            moments.append(MomentLoad(magnitude=-f, location=nodes[k]))
            moments.append(MomentLoad(magnitude=f, location=nodes[k + 1]))
        return moments

    def equivalent_loads(self, nodes):
        """
        Return list of equivalent loads for the distributed load

        This will be a combination of PointLoads and MomentLoads that are statically
        equivalent to the distributed load
        """

        point_loads = self.__equivalent_point_loads(nodes)
        moment_loads = self.__equivalent_moments(nodes)
        loads = []
        loads.extend(point_loads)
        loads.extend(moment_loads)
        return loads

    @property
    def equivalent_force(self):
        return self.magnitude * (self.stop - self.start)

    # @property
    # def centroid_location(self):
    #     return (self.start + self.stop) / 2
