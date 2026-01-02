import numpy as np

from .__base import Load


class PointLoad(Load):
    """
    class specific to a point load
    """

    name = "point load"

    def __init__(self, magnitude, location):
        super().__init__(magnitude, location, fm_factor=(1, 0))

    def fe(self, a, b):
        """
        Return the equivalent loads for the point load acting on adjacent nodes

        This will calculate the equivalent loads for the point load acting on
        the two nearest nodes (ie, the nodes  that define the element that the
        force is acting on). This is needed for relocating the load so that it
        acts on the nodes and not on the element, since the Euler-Bernoulli
        beam equations rely on loads being applied only at nodes.

        This is done by applying the shape functions for the beam element,
        and creating a non-dimensional array by making the following
        substitutions:

        a = x
        z = a / L
        and substituting z for x in all shape functions.

        This results in a normalized array in the form:
        [F1, M1, F2, M2]

        Parameters:
            a: float: offset from left node to location of load
            b: float: offset from load location to right node

        Returns:
             np.array: equivalent loads in the form [F1, M1, F2, M2]
        """

        if a == 0:
            # when a = 0 or b=0, the load is already applied at a node, don't
            # "spread" it out over multiple nodes
            # For this case: the load is applied to the first node
            return self.magnitude * np.array([1, 0, 0, 0])
        if b == 0:
            # when a = 0 or b=0, the load is already applied at a node, don't
            # "spread" it out over multiple nodes
            # For this case: the load is applied to the second node
            return self.magnitude * np.array([0, 0, 1, 0])

        # the load is applied somewhere in the middle, find the equivalent
        # loads and moments spread out over both nodes.

        L = a + b  # length of element
        z = a / L  # non-dimensional zeta

        # calculate the normalized Hermite shape functions in terms of the
        # dimensionless zeta
        N1 = 1 - 3 * z**2 + 2 * z**3
        N2 = L * (z - 2 * z**2 + z**3)
        N3 = 3 * z**2 - 2 * z**3
        N4 = L * (-(z**2) + z**3)
        N = np.array([N1, N2, N3, N4])
        return self.magnitude * N
