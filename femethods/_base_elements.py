"""
Module to define a general mesh element to be used for any FEM element, and
the base element class that all FEM elements will be derived from
"""

from warnings import warn

import matplotlib.pyplot as plt
import numpy as np

from ._common import Validator
# Importing loads is only used for checking the type. Find a better way to do
# this without needing to import loads
from .loads import MomentLoad, PointLoad
from .mesh import Mesh


class Base(object):
    """base object to be used as base for both FEM analysis"""

    def __init__(self, length, E=1, Ixx=1):
        self.length = length
        self.E = E  # Young's modulus
        self.Ixx = Ixx  # area moment of inertia

    @property
    def length(self):
        return self._length

    @length.setter
    @Validator.positive('length')
    def length(self, length):
        self._length = length

    @property
    def E(self):
        return self._E

    @E.setter
    @Validator.positive("Young's modulus")
    def E(self, E):
        self._E = E

    @property
    def Ixx(self):
        return self._Ixx

    @Ixx.setter
    @Validator.positive('Area moment of inertia')
    def Ixx(self, Ixx):
        self._Ixx = Ixx


class Element(Base):
    """General element that will be inherited from for specific elements"""

    def __init__(self, length, E=1, Ixx=1):
        super().__init__(length, E, Ixx)
        self._node_deflections = None
        self._K = None  # global stiffness matrix
        self._reactions = None
        self._loads = None

    @property
    def loads(self):
        return self._loads

    @loads.setter
    @Validator.islist('loads')
    def loads(self, loads):

        self.invalidate()
        if self.reactions is None:
            # should this raise an error, or something else
            # warn RuntimeWarning('reactions should be set before loads')
            warn('reactions should be set before loads', RuntimeWarning)
            self._loads = loads
            return
        self._loads = loads
        self.__validate_load_locations()

    def __validate_load_locations(self):
        """All loads and reactions must have unique locations

        This function will validate that all loads do not line up with any
        reactions. If a load is aligned with a reaction, it is adjusted by a
        slight amount so it can be solved.
        :returns True if successful, False otherwise
        """
        if self.reactions is None:
            warn('reactions should be set prior to adding loads')
            return False
        for reaction in self.reactions:
            for load in self.loads:
                if load.location == reaction.location:
                    # the load is directly on the reaction. Offset the load
                    # location a tiny amount so that it is very close, but not
                    # exactly on the reaction.
                    # This is done so that the global stiffness matrix
                    # is calculated properly to give accurate results

                    # offset the load towards the inside of the beam to be sure
                    # the new load position is located on the beam.
                    if reaction.location == 0:
                        load.location += 1e-8
                    else:
                        load.location -= 1e-8
        return True

    @property
    def reactions(self):
        return self._reactions

    @reactions.setter
    @Validator.islist('reactions')
    def reactions(self, reactions):
        self.invalidate()
        self._reactions = reactions

    def remesh(self):
        """force a remesh calculation and invalidate any calculation results"""
        raise NotImplemented('method must be overloaded')

    def invalidate(self):
        """invalidate the element to force resolving"""
        self._node_deflections = None
        self._K = None
        if self.reactions is not None:
            for reaction in self.reactions:
                reaction.invalidate()

    @property
    def K(self):
        """global stiffness matrix"""
        if self._K is None:
            self._K = self.stiffness_global()
        return self._K

    def solve(self):
        """solve the system the FEM system to define the nodal displacements
        and reaction forces.
        """
        self.__validate_load_locations()
        self.remesh()
        self._calc_node_deflections()
        self._get_reaction_values()

    def _calc_node_deflections(self):
        raise NotImplemented('must be overloaded!')

    def _get_reaction_values(self):
        raise NotImplemented('must be overloaded!')

    def stiffness(self):
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam
        """
        raise NotImplemented('Method must be overloaded!')

    def stiffness_global(self):
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        raise NotImplemented('Method must be overloaded!')

    @staticmethod
    def apply_boundary_conditions(k, bcs):
        """
        Given the stiffness matrix 'k', and the boundary conditions as a list
        of tuples, apply the boundary conditions to the stiffness matrix by
        setting the rows and columns that correspond to the boundary conditions
        to zeros, with ones on the diagonal.

        The boundary conditions (bcs) are in the form
        bcs = [(displacement1, rotation1), (displacement2, rotation2)]

        For the boundary condition, if the conditional evaluates to None, then
        movement is allowed, otherwise no displacement is allowed.

        The boundary condition coordinates must match the stiffness matrix.
        That is, if the stiffness matrix is a local matrix, the boundary
        conditions must also be local.

        returns the adjusted  stiffness matrix after the boundary
        conditions are applied
        """

        def apply(k, i):
            """sub function to apply the boundary condition at row/col i to
            stiffness matrix k

            return the stiffness matrix k with boundary conditions applied
            """
            k[i] = 0     # set entire row to zeros
            k[:, i] = 0  # set entire column to zeros
            k[i][i] = 1  # set diagonal to 1
            return k

        # TODO: Check the sizes of the boundary conditions and stiffness matrix

        node = 0
        for bc in bcs:
            v, q = bc
            if v is not None:
                k = apply(k, node * 2)
            if q is not None:
                k = apply(k, node * 2 + 1)
            node += 1
        return k


class BeamElement(Element):
    """base beam element"""

    def __init__(self, length, loads, reactions, E=1, Ixx=1):
        super().__init__(length, E, Ixx)
        self.reactions = reactions
        self.loads = loads  # note loads are set after reactions
        self.mesh = Mesh(length, loads, reactions, 2)

    def remesh(self):
        self.mesh = Mesh(self.length, self.loads, self.reactions, 2)
        self.invalidate()

    @property
    def node_deflections(self):
        if self._node_deflections is None:
            self._node_deflections = self._calc_node_deflections()
        return self._node_deflections

    def __get_boundary_conditions(self):
        # Initialize the  boundary conditions to None for each node, then
        # iterate over reactions and apply them to the boundary conditions
        # based on the reaction type.
        bc = [(None, None) for _ in range(len(self.mesh.nodes))]
        for r in self.reactions:
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
            if isinstance(ld, PointLoad):
                p[i * 2][0] = ld.value  # input force
            elif isinstance(ld, MomentLoad):
                p[i * 2 + 1][0] = ld.value  # input moment

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
        K = self.K                 # global stiffness matrix
        d = self.node_deflections  # force displacement vector
        r = np.matmul(K, d)

        for ri in self.reactions:
            i = self.mesh.nodes.index(ri.location)
            force, moment = r[i * 2: i * 2 + 2]

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
        N4 = 1 / L ** 2 * (-L * x ** 2 + x ** 3)
        return np.array([N1, N2, N3, N4])

    def plot_shapes(self, n=25):
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
            n = self.shape(xi)
            for i in range(4):
                N[i].append(n[i])

        for k in range(4):
            ax = axes[k]
            ax.grid(True)
            ax.plot(x, N[k], label=f'$N_{k + 1}$')
            ax.legend()

        fig.subplots_adjust(wspace=0.25, hspace=0)
        plt.show()

    def stiffness(self, L=None):
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam"""

        if L is None:
            L = self.length

        E = self.E
        Ixx = self.Ixx

        k = np.array([[12, 6 * L, -12, 6 * L],
                      [6 * L, 4 * L ** 2, -6 * L, 2 * L ** 2],
                      [-12, -6 * L, 12, -6 * L],
                      [6 * L, 2 * L ** 2, -6 * L, 4 * L ** 2]])
        return E * Ixx / L ** 3 * k

    def stiffness_global(self):
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        kg = np.zeros((self.mesh.dof, self.mesh.dof))
        for e in range(self.mesh.num_elements):
            # iterate over all the elements and add the local stiffness matrix
            # to the global stiffness matrix at the proper index
            k = self.stiffness(self.mesh.lengths[e])  # local stiffness matrix
            i1, i2 = (e * 2, e * 2 + 4)               # global slicing index
            kg[i1:i2, i1:i2] = kg[i1:i2, i1:i2] + k   # current element
        self._K = kg

        return self._K
