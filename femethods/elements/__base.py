"""
Module to define a general mesh element to be used for any FEM element, and
the base element class that all FEM elements will be derived from
"""

from abc import ABC, abstractmethod
from warnings import warn

# Importing loads is only used for checking the type. Find a better way to do
# this without needing to import loads
from .. import validation
from ..loads import Load
from ..reactions import Reaction


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class Base(ABC):
    """base object to be used as base for both FEM analysis"""

    def __init__(self, length, E=1, Ixx=1):
        self.length = length
        self.E = E  # Young's modulus
        self.Ixx = Ixx  # area moment of inertia

    @property
    def length(self):
        return self._length

    @length.setter
    @validation.positive
    def length(self, length):
        self._length = length

    @property
    def E(self):
        return self._E

    @E.setter
    @validation.positive
    def E(self, E):
        self._E = E

    @property
    def Ixx(self):
        return self._Ixx

    @Ixx.setter
    @validation.positive
    def Ixx(self, Ixx):
        self._Ixx = Ixx


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class Element(Base, ABC):
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
    def loads(self, loads):
        # validate that loads is a list of valid Loads
        for load in loads:
            if not isinstance(load, Load):
                raise TypeError(f"type {type(load)} is not of type Load")

        self.invalidate()
        self._loads = loads
        self.__validate_load_locations()

    def __validate_load_locations(self):
        """All loads and reactions must have unique locations

        This function will validate that all loads do not line up with any
        reactions. If a load is aligned with a reaction, it is adjusted by a
        slight amount so it can be solved.
        :returns True if successful, False otherwise
        """

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
    def reactions(self):
        return self._reactions

    @reactions.setter
    def reactions(self, reactions):
        for reaction in reactions:
            if not isinstance(reaction, Reaction):
                msg = f"type {type(reaction)} is not of type Reaction"
                raise TypeError(msg)
        self.invalidate()
        self._reactions = reactions

    @abstractmethod
    def remesh(self):
        """force a remesh calculation and invalidate any calculation results"""
        raise NotImplementedError("method must be overloaded")

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

    @abstractmethod
    def _calc_node_deflections(self):
        raise NotImplementedError("must be overloaded!")

    @abstractmethod
    def _get_reaction_values(self):
        raise NotImplementedError("must be overloaded!")

    @abstractmethod
    def stiffness(self, L):
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam
        """
        raise NotImplementedError("Method must be overloaded!")

    @abstractmethod
    def stiffness_global(self):
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        raise NotImplementedError("Method must be overloaded!")

    @staticmethod
    def apply_boundary_conditions(k, bcs):
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

        def apply(k_local, i):
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
