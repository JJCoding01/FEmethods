"""
Module to define a general mesh element to be used for any FEM element, and
the base element class that all FEM elements will be derived from
"""

from abc import ABC, abstractmethod
from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
import numpy.typing as npt

# Importing loads is only used for checking the type. Find a better way to do
# this without needing to import loads
from .. import validation
from ..loads import Load
from ..reactions import Reaction

if TYPE_CHECKING:
    from femethods.mesh import Mesh


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class Properties:
    """
    Base class for handling geometric and material properties

    Parameters:
        length: numeric: length of overall structure
        E: numeric: optional, Young's modulus of elasticity of structure. Must be in
            compatible units to Ixx
        Ixx: numeric: optional, area moment of inertia. Must be in compatible units to
            Young's modulus

    Raises:
        TypeError: when length, E, or Ixx is not numeric
        ValueError: when length, E, or Ixx is not positive
    """

    def __init__(self, length: float, E: float = 1, Ixx: float = 1) -> None:
        self.length = length
        self.E = E  # Young's modulus
        self.Ixx = Ixx  # area moment of inertia

    @property
    def length(self) -> float:
        """
        length of structure or element

        The length must be given in units that are compatible with Young's modulus (E)
        and the area moment of inertia (Ixx).

        .. note:: this is not the length between nodes, this is the overall length

        Raises:
            TypeError: when non-numeric
            ValueError: when value is less than or equal to 0, (non-positive)
        """
        return self._length

    @length.setter
    @validation.is_numeric
    @validation.positive
    def length(self, length: float) -> None:
        self._length = length

    @property
    def E(self) -> float:
        """
        Young's modulus of elasticity of structure or element

        Young's modulus must be given in units that are compatible with the length (`length`)
        and the area moment of inertia (`Ixx`).

        Raises:
            TypeError: when non-numeric
            ValueError: when value is less than or equal to 0, (non-positive)
        """
        return self._E

    @E.setter
    @validation.is_numeric
    @validation.positive
    def E(self, E: float) -> None:
        self._E = E

    @property
    def Ixx(self) -> float:
        """
        Area moment of inertia in the key direction for the structure or element

        The area moment of inertia must be given in units that are compatible with
        Young's modulus (E) and the length.

        Raises:
            TypeError: when non-numeric
            ValueError: when value is less than or equal to 0, (non-positive)
        """
        return self._Ixx

    @Ixx.setter
    @validation.is_numeric
    @validation.positive
    def Ixx(self, Ixx: float) -> None:
        self._Ixx = Ixx


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class Element(Properties, ABC):
    """General element that will be inherited from for specific elements"""

    def __init__(
        self, length: float, reactions: Sequence[Reaction], E: float = 1, Ixx: float = 1
    ) -> None:
        super().__init__(length, E, Ixx)
        self._node_deflections: npt.NDArray[np.float64] | None = None
        self._K: npt.NDArray[np.float64] | None = None  # global stiffness matrix
        self._reactions: Sequence[Reaction] = reactions
        self._loads: Sequence[Load] = ()

    @property
    def loads(self) -> Sequence[Load]:
        return self._loads

    @loads.setter
    def loads(self, loads: Sequence[Load]) -> None:
        # validate that loads is a list of valid Loads
        for load in loads:
            if not isinstance(load, Load):
                raise TypeError(f"type {type(load)} is not of type Load")

        self.invalidate()
        self._loads = loads

    @property
    def reactions(self) -> Sequence[Reaction]:
        return self._reactions

    @reactions.setter
    def reactions(self, reactions: Sequence[Reaction]) -> None:
        for reaction in reactions:
            if not isinstance(reaction, Reaction):
                msg = f"type {type(reaction)} is not of type Reaction"
                raise TypeError(msg)
        self.invalidate()
        self._reactions = reactions

    @abstractmethod
    def remesh(self) -> "Mesh":
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
    def K(self) -> npt.NDArray[np.float64]:
        """global stiffness matrix"""
        if self._K is None:
            # calculate stiffness matrix
            self._K = self.stiffness_global()
        return self._K

    def solve(self) -> None:
        """solve the system the FEM system to define the nodal displacements
        and reaction forces.
        """
        self.remesh()
        self._calc_node_deflections()
        self.update_reactions()

    @property
    def node_deflections(self) -> npt.NDArray[np.float64]:
        if self._node_deflections is None:
            self._node_deflections = self._calc_node_deflections()
        return self._node_deflections

    @abstractmethod
    def _calc_node_deflections(self) -> npt.NDArray[np.float64]:
        raise NotImplementedError("must be overloaded!")

    @abstractmethod
    def update_reactions(self) -> npt.NDArray[np.float64]:
        raise NotImplementedError("must be overloaded!")

    @property
    def load_vector(self) -> npt.NDArray[np.float64]:
        """
        Calculate the nodal forces acting on each node

        Note that the forces returned here will also include the input forces

        reactions are calculated by solving the matrix equation
        {r} = [K] * {d}

        where
           - {r} is the vector of forces acting on the beam
           - [K] is the global stiffness matrix (without BCs applied)
           - {d} displacements of nodes

        Returns:
            np.array: nodal forces acting on each node
        """

        K = self.K  # global stiffness matrix
        d = self.node_deflections  # force displacement vector
        r: npt.NDArray[np.float64] = np.matmul(K, d)
        return r

    @abstractmethod
    def stiffness(self, L: Optional[float]) -> npt.NDArray[np.float64]:
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam
        """
        raise NotImplementedError("Method must be overloaded!")

    @abstractmethod
    def stiffness_global(self) -> npt.NDArray[np.float64]:
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        raise NotImplementedError("Method must be overloaded!")

    @staticmethod
    def apply_boundary_conditions(
        k: npt.NDArray[np.float64],
        bcs: Sequence[tuple[Optional[float], Optional[float]]],
    ) -> npt.NDArray[np.float64]:
        """
        Given the stiffness matrix 'k_local', and the boundary conditions as a
        list of tuples, apply the boundary conditions to the stiffness matrix
        by setting the rows and columns that correspond to the boundary
        conditions to zeros, with ones on the diagonal.

        The boundary conditions (bcs) are in the form
        bcs = [
            (displacement1, rotation1),
            (displacement2, rotation2),
            (..., ...),
            (displacementn, rotationn),
            ]

        For the boundary condition, if the conditional evaluates to None, then
        movement is allowed, otherwise no displacement is allowed.

        The boundary condition coordinates must match the stiffness matrix.
        That is, if the stiffness matrix is a local matrix, the boundary
        conditions must also be local.

        returns the adjusted  stiffness matrix after the boundary
        conditions are applied
        """

        def apply(k_local: npt.NDArray[np.float64], i: int) -> npt.NDArray[np.float64]:
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
