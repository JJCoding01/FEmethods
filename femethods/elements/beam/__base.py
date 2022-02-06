import matplotlib.pyplot as plt
import numpy as np

from femethods.mesh import Mesh

from ...loads import DistributedLoad
from ..__base import Element


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class BeamElement(Element):
    """base beam element"""

    def __init__(
        self,
        length,
        loads,
        reactions,
        E=1,
        Ixx=1,
    ):
        super().__init__(length, E, Ixx)
        self.reactions = reactions
        self.loads = loads  # note loads are set after reactions
        self.mesh = self.remesh()

    @property
    def loads(self):
        """loads on system"""
        return self.__loads

    @loads.setter
    def loads(self, value):
        # basic loads

        self.__loads = value

        # update equivalent_loads
        self.__equivalent_loads = []
        for load in self.__loads:
            if isinstance(load, DistributedLoad):
                self.__equivalent_loads.extend(load.equivalent_loads(self.mesh.nodes))
            else:
                self.__equivalent_loads.append(load)

    @property
    def equivalent_loads(self):
        """load that are equivalent to distributed loads"""
        return self.__equivalent_loads

    def remesh(self):
        self.invalidate()

        locations = [r.location for r in self.reactions]
        locations.extend([load.location for load in self.equivalent_loads])
        self.mesh = Mesh(self.length, locations, 2)
        return self.mesh

    @property
    def node_deflections(self):
        if self._node_deflections is None:
            self._node_deflections = self._calc_node_deflections()
        return self._node_deflections

    def __get_boundary_conditions(self):
        # Initialize the  boundary conditions to None for each node, then
        # iterate over reactions and apply them to the boundary conditions
        # based on the reaction type.
        assert self.reactions is not None
        bc = [(None, None) for _ in self.mesh.nodes]
        for r in self.reactions:
            assert r is not None
            i = self.mesh.nodes.index(r.location)
            bc[i] = r.boundary
        return bc

    def _calc_node_deflections(self):
        """solve for vertical and angular displacement at each node"""

        # Get the boundary conditions from the reactions
        bc = self.__get_boundary_conditions()

        # Apply boundary conditions to global stiffness matrix. Note that the
        # boundary conditions are applied to a copy of the stiffness matrix to
        # avoid changing the property K, so it can still be used with further
        # calculations (ie, for calculating reaction values)
        kg = self.K.copy()
        kg = self.apply_boundary_conditions(kg, bc)

        # Use the same method of adding the input loads as the boundary
        # conditions. Start by initializing a numpy array to zero loads, then
        # iterate over the loads and add them to the appropriate index based on
        # the load type (force or moment)
        p = np.zeros((self.mesh.dof, 1))
        for ld in self.loads:
            i = self.mesh.nodes.index(ld.location)
            # add force and moment components of load to respective node. Load
            # components must be added and not simply assigned to account for the
            # special case where multiple loads are applied to the same node (location)
            p[i * 2][0] += ld[0]  # input force
            p[i * 2 + 1][0] += ld[1]  # input moment

        # Solve the global system of equations {p} = [K]*{d} for {d}
        # save the deflection vector for the beam, so the analysis can be
        # reused without recalculating the stiffness matrix.
        # This vector should be cleared anytime any of the beam parameters
        # gets changed.
        self._node_deflections = np.linalg.solve(kg, p)
        return self._node_deflections

    def _get_reaction_values(self):
        """Calculate the nodal forces acting on the beam. Note that the forces
        will also include the input forces.

        reactions are calculated by solving the matrix equation
        {r} = [K] * {d}

        where
           - {r} is the vector of forces acting on the beam
           - [K] is the global stiffness matrix (without BCs applied)
           - {d} displacements of nodes
        """
        K = self.K  # global stiffness matrix
        d = self.node_deflections  # force displacement vector

        r = np.matmul(K, d)
        assert self.reactions is not None

        for ri in self.reactions:
            i = self.mesh.nodes.index(ri.location)
            force, moment = r[i * 2 : i * 2 + 2]

            # set the values in the reaction objects
            ri.force = force[0]
            ri.moment = moment[0]
        return r

    def shape(self, x, L=None):
        """return an array of the shape functions evaluated at x the local
        x-value
        """
        if L is None:
            L = self.length
        N1 = 1 / L ** 3 * (L ** 3 - 3 * L * x ** 2 + 2 * x ** 3)
        N2 = 1 / L ** 2 * (L ** 2 * x - 2 * L * x ** 2 + x ** 3)
        N3 = 1 / L ** 3 * (3 * L * x ** 2 - 2 * x ** 3)
        N4 = 1 / L ** 2 * (x ** 3 - L * x ** 2)
        return np.array([N1, N2, N3, N4])

    def plot_shapes(self, n=25):  # pragma: no cover
        """plot shape functions for the with n data points"""
        x = np.linspace(0, self.length, n)

        # set up list of axes with a grid where the two figures in each column
        # share an x axis
        axes = []
        fig = plt.figure()
        axes.append(fig.add_subplot(221))
        axes.append(fig.add_subplot(222))
        axes.append(fig.add_subplot(223, sharex=axes[0]))
        axes.append(fig.add_subplot(224, sharex=axes[1]))

        N = [[], [], [], []]
        for xi in x:
            n_local = self.shape(xi)
            for i in range(4):
                N[i].append(n_local[i])

        for k in range(4):
            ax = axes[k]
            ax.grid(True)
            ax.plot(x, N[k], label=f"$N_{k + 1}$")
            ax.legend()

        fig.subplots_adjust(wspace=0.25, hspace=0)
        plt.show()

    def stiffness(self, L):
        """
        local stiffness matrix as numpy array

        Parameters:
            L: numeric: optional: length of element.
                Defaults to None (which means use the overall length of the structure)
        """

        k = np.array(
            [
                [12, 6 * L, -12, 6 * L],
                [6 * L, 4 * L ** 2, -6 * L, 2 * L ** 2],
                [-12, -6 * L, 12, -6 * L],
                [6 * L, 2 * L ** 2, -6 * L, 4 * L ** 2],
            ]
        )
        return self.E * self.Ixx / L ** 3 * k

    def stiffness_global(self):
        """
        Global stiffness matrix of entire structure
        """
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        kg = np.zeros((self.mesh.dof, self.mesh.dof))
        for i, element_length in enumerate(self.mesh.lengths):
            # iterate over all the elements and add the local stiffness matrix
            # to the global stiffness matrix at the proper index
            k = self.stiffness(element_length)  # local stiffness matrix
            i1, i2 = (i * 2, i * 2 + 4)  # global slicing index
            kg[i1:i2, i1:i2] = kg[i1:i2, i1:i2] + k  # current element
        self._K = kg

        return self._K
