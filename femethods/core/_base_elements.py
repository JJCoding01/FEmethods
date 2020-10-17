"""
Module to define a general mesh element to be used for any FEM element, and
the base element class that all FEM elements will be derived from
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from warnings import warn

import matplotlib.pyplot as plt
import numpy as np

# Importing loads is only used for checking the type. Find a better way to do
# this without needing to import loads
from femethods.loads import Load, PointLoad
from femethods.mesh import Mesh
from femethods.reactions import Reaction

BOUNDARY_CONDITIONS = List[Tuple[Optional[int], Optional[int]]]


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class Base(ABC):
    """base object to be used as base for both FEM analysis"""

    def __init__(self, length: float, E: float = 1, Ixx: float = 1) -> None:
        self.length = length
        self.E = E  # Young's modulus
        self.Ixx = Ixx  # area moment of inertia

    @property
    def length(self) -> float:
        return self._length

    @length.setter
    def length(self, length: float) -> None:
        if length <= 0:
            # length must be a positive number
            raise ValueError("length must be positive!")
        self._length = length

    @property
    def E(self) -> float:
        return self._E

    @E.setter
    def E(self, E: float) -> None:
        if E <= 0:
            raise ValueError("Young's modulus must be positive!")
        self._E = E

    @property
    def Ixx(self) -> float:
        return self._Ixx

    @Ixx.setter
    def Ixx(self, Ixx: float) -> None:
        if Ixx <= 0:
            raise ValueError("Area moment of inertia must be positive!")
        self._Ixx = Ixx


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class Element(Base, ABC):
    """General element that will be inherited from for specific elements"""

    def __init__(self, length: float, E: float = 1, Ixx: float = 1) -> None:
        super().__init__(length, E, Ixx)
        self._node_deflections = None
        self._K = None  # global stiffness matrix
        self._reactions: Optional[List[Reaction]] = None
        self._loads: Optional[List[Load]] = None

    @property
    def loads(self) -> Optional[List[Load]]:
        return self._loads

    @loads.setter
    def loads(self, loads: List[Load]) -> None:
        # validate that loads is a list of valid Loads
        for load in loads:
            if not isinstance(load, Load):
                raise TypeError(f"type {type(load)} is not of type Load")

        self.invalidate()
        self._loads = loads
        self.__validate_load_locations()

    def __validate_load_locations(self) -> bool:
        """All loads and reactions must have unique locations

        This function will validate that all loads do not line up with any
        reactions. If a load is aligned with a reaction, it is adjusted by a
        slight amount so it can be solved.
        :returns True if successful, False otherwise
        """
        assert self.reactions is not None
        assert self.loads is not None

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
                        warn(
                            f"load location moved by 1e-8 to avoid reaction "
                            f"at {reaction.location}"
                        )
                    else:
                        load.location -= 1e-8
                        warn(
                            f"load location moved by -1e-8 to avoid reaction"
                            f" at {reaction.location}"
                        )
        return True

    @property
    def reactions(self) -> Optional[List[Reaction]]:
        return self._reactions

    @reactions.setter
    def reactions(self, reactions: List[Reaction]) -> None:
        for reaction in reactions:
            if not isinstance(reaction, Reaction):
                msg = f"type {type(reaction)} is not of type Reaction"
                raise TypeError(msg)
        self.invalidate()
        self._reactions = reactions

    @abstractmethod
    def remesh(self) -> None:
        """force a remesh calculation and invalidate any calculation results"""
        raise NotImplementedError("method must be overloaded")

    def invalidate(self) -> None:
        """invalidate the element to force resolving"""
        self._node_deflections = None
        self._K = None
        if self.reactions is not None:
            for reaction in self.reactions:
                reaction.invalidate()

    @property
    def K(self) -> np.array:
        """global stiffness matrix"""
        if self._K is None:
            self._K = self.stiffness_global()
        return self._K

    def solve(self) -> None:
        """solve the system the FEM system to define the nodal displacements
        and reaction forces.
        """
        self.__validate_load_locations()
        self.remesh()
        self._calc_node_deflections()
        self._get_reaction_values()

    @abstractmethod
    def _calc_node_deflections(self) -> None:
        raise NotImplementedError("must be overloaded!")

    @abstractmethod
    def _get_reaction_values(self) -> None:
        raise NotImplementedError("must be overloaded!")

    @abstractmethod
    def stiffness(self, L: float) -> None:
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam
        """
        raise NotImplementedError("Method must be overloaded!")

    @abstractmethod
    def stiffness_global(self) -> None:
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        raise NotImplementedError("Method must be overloaded!")

    @staticmethod
    def apply_boundary_conditions(
        k: np.array, bcs: BOUNDARY_CONDITIONS
    ) -> np.array:
        """
        Given the stiffness matrix 'k_local', and the boundary conditions as a list
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

        def apply(k_local: np.array, i: int) -> np.array:
            """sub function to apply the boundary condition at row/col i to
            stiffness matrix k_local

            return the stiffness matrix k_local with boundary conditions applied
            """
            k_local[i] = 0  # set entire row to zeros
            k_local[:, i] = 0  # set entire column to zeros
            k_local[i][i] = 1  # set diagonal to 1
            return k_local

        # TODO: Check the sizes of the boundary conditions and stiffness matrix

        for node, bc in enumerate(bcs):
            v, q = bc
            if v is not None:
                k = apply(k, node * 2)
            if q is not None:
                k = apply(k, node * 2 + 1)
        return k


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class BeamElement(Element):
    """base beam element"""

    def __init__(
        self,
        length: float,
        loads: List[Load],
        reactions: List[Reaction],
        E: float = 1,
        Ixx: float = 1,
    ):
        super().__init__(length, E, Ixx)
        self.reactions = reactions
        self.loads = loads  # note loads are set after reactions
        self.mesh = Mesh(length, loads, reactions, 2)

    def remesh(self) -> None:
        assert self.loads is not None
        assert self.reactions is not None
        self.mesh = Mesh(self.length, self.loads, self.reactions, 2)
        self.invalidate()

    @property
    def node_deflections(self) -> np.ndarray:
        if self._node_deflections is None:
            self._node_deflections = self._calc_node_deflections()
        return self._node_deflections

    def __get_boundary_conditions(self) -> BOUNDARY_CONDITIONS:
        # Initialize the  boundary conditions to None for each node, then
        # iterate over reactions and apply them to the boundary conditions
        # based on the reaction type.
        assert self.reactions is not None
        bc: BOUNDARY_CONDITIONS = [
            (None, None) for _ in range(len(self.mesh.nodes))
        ]
        for r in self.reactions:
            assert r is not None
            i = self.mesh.nodes.index(r.location)
            bc[i] = r.boundary
        return bc

    def _calc_node_deflections(self) -> np.ndarray:
        """solve for vertical and angular displacement at each node"""
        assert self.loads is not None

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
        # noinspection PyUnresolvedReferences
        p = np.zeros((self.mesh.dof, 1))
        for ld in self.loads:
            i = self.mesh.nodes.index(ld.location)
            if isinstance(ld, PointLoad):
                p[i * 2][0] = ld.magnitude  # input force
            else:
                p[i * 2 + 1][0] = ld.magnitude  # input moment

        # Solve the global system of equations {p} = [K]*{d} for {d}
        # save the deflection vector for the beam, so the analysis can be
        # reused without recalculating the stiffness matrix.
        # This vector should be cleared anytime any of the beam parameters
        # gets changed.
        self._node_deflections = np.linalg.solve(kg, p)
        return self._node_deflections

    def _get_reaction_values(self) -> np.ndarray:
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

        # noinspection PyUnresolvedReferences
        r = np.matmul(K, d)
        assert self.reactions is not None

        for ri in self.reactions:
            i = self.mesh.nodes.index(ri.location)
            force, moment = r[i * 2 : i * 2 + 2]

            # set the values in the reaction objects
            ri.force = force[0]
            ri.moment = moment[0]
        return r

    def shape(self, x: float, L: Optional[float] = None) -> np.ndarray:
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

    def plot_shapes(self, n: int = 25) -> None:  # pragma: no cover
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

        N: List[List[int]] = [[], [], [], []]
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

    def stiffness(self, L: float) -> np.ndarray:
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L
        """

        E = self.E
        Ixx = self.Ixx

        k = np.array(
            [
                [12, 6 * L, -12, 6 * L],
                [6 * L, 4 * L ** 2, -6 * L, 2 * L ** 2],
                [-12, -6 * L, 12, -6 * L],
                [6 * L, 2 * L ** 2, -6 * L, 4 * L ** 2],
            ]
        )
        return E * Ixx / L ** 3 * k

    def stiffness_global(self) -> np.array:
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        # noinspection PyUnresolvedReferences
        kg = np.zeros((self.mesh.dof, self.mesh.dof))
        for e in range(self.mesh.num_elements):
            # iterate over all the elements and add the local stiffness matrix
            # to the global stiffness matrix at the proper index
            k = self.stiffness(self.mesh.lengths[e])  # local stiffness matrix
            i1, i2 = (e * 2, e * 2 + 4)  # global slicing index
            kg[i1:i2, i1:i2] = kg[i1:i2, i1:i2] + k  # current element
        self._K = kg

        return self._K
