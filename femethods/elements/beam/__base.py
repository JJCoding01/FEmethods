from typing import Optional, Sequence, TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from femethods.mesh import Mesh

from ...loads import DistributedLoad, Load, MomentLoad, PointLoad
from ...reactions import Reaction
from ..__base import Element

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

BOUNDARY = tuple[float | None, float | None]


# Allow upper case letters for variable names to match engineering conventions
# for variables, such as E for Young's modulus and I for the polar moment of
# inertia
# noinspection PyPep8Naming
class BeamElement(Element):
    """base beam element"""

    def __init__(
        self,
        length: float,
        loads: Sequence[Load],
        reactions: Sequence[Reaction],
        *,
        mesh: Optional[Mesh] = None,
        E: float = 1,
        Ixx: float = 1,
    ) -> None:
        super().__init__(length, reactions, E, Ixx)

        if mesh is None:
            # create the default mesh
            mesh = self.__default_mesh(length, reactions, loads)
        self.mesh = mesh

        # note loads are set after reactions and mesh
        self.loads = loads

    @staticmethod
    def __default_mesh(
        length: float, reactions: Sequence[Reaction], loads: Sequence[Load]
    ) -> Mesh:
        try:
            locations = [r.location for r in reactions]
            locations.extend([load.location for load in loads])
        except AttributeError as e:
            # error likely due to either reaction or load not being of a
            # proper type, causing an error on r.location or load.location
            raise TypeError(e) from e
        mesh = Mesh(length, np.array(locations), 2)
        return mesh

    @property
    def loads(self) -> Sequence[Load]:
        """loads on system"""
        return super().loads

    @loads.setter
    def loads(self, value: Sequence[Load]) -> None:  # pylint: disable=too-many-locals
        # basic loads
        # call super loads method to take advantage of the error checking and validation
        # performed at that level
        super(BeamElement, self.__class__).loads.fset(self, value)
        self.__loads = value

        # update equivalent_loads
        self.__equivalent_loads = []
        for load in self.__loads:
            if isinstance(load, DistributedLoad):
                self.__equivalent_loads.extend(load.equivalent_loads(self.mesh.nodes))
            elif isinstance(load, Load):
                # this is a point load/moment

                # find the index for the right node where the load is applied.
                # Do this by finding index where the load location would be
                # inserted into the mesh and offsetting it down by one, which
                # will get the start of the element
                idx = int(
                    np.searchsorted(self.mesh.nodes, load.location, side="right") - 1
                )
                # Then, clip the index to be a valid index WITHOUT ROLLING TO
                # THE OPPOSITE SIDE. When the index is near the beginning of
                # the beam, there's a chance that the index would be negative,
                # this will effectively roll it to the other side, which is not
                # what should happen in this case.
                e = int(np.clip(idx, 0, len(self.mesh.nodes) - 2))

                # Now that we have the proper index for the node, define the
                # first (left) node, and calculate the second (right) node and
                # element length.
                node1 = self.mesh.nodes[e]  # left node of element
                node2 = self.mesh.nodes[e + 1]  # right node of element
                length = node2 - node1  # length of element with load

                # calculate the load position
                a = load.location - node1  # local load position relative to left node
                b = length - a  # local load position relative to right node

                # calculate the equivalent load vector for the load
                fe = load.fe(a, b)
                p1, m1, p2, m2 = fe  # extract the magnitudes for equivalent loads
                eq_loads = [  # create an equivalent load vector of actual loads
                    PointLoad(p1, node1),  # force at node 1
                    MomentLoad(m1, node1),  # moment at node 1
                    PointLoad(p2, node2),  # force at node 2
                    MomentLoad(m2, node2),  # moment at node 2
                ]
                self.__equivalent_loads.extend(eq_loads)
            else:
                raise TypeError(
                    f"load must be of type Load or DistributedLoad, not {type(load)})"
                )

    @property
    def equivalent_loads(self) -> Sequence[Load]:
        """load that are equivalent to distributed loads"""
        return self.__equivalent_loads

    def remesh(self) -> Mesh:
        self.invalidate()
        mesh = self.__default_mesh(self.length, self.reactions, self.loads)
        self.mesh = mesh
        return self.mesh

    def __get_boundary_conditions(self) -> npt.NDArray[BOUNDARY]:
        assert self.reactions is not None

        # Initialize the  boundary conditions to None for each node
        bc = np.array([(None, None) for _ in self.mesh.nodes])

        # get location of all reactions
        locations = np.array([r.location for r in self.reactions])

        # create a boolean index map for the boundary conditions. True on the index
        # (node) where a reaction is located
        map_ = np.isin(self.mesh.nodes, locations, assume_unique=True)

        # using the reaction map, apply the boundary conditions for each reaction to
        # the total boundary conditions of all nodes
        bc_r = np.array([r.boundary for r in self.reactions])
        bc[map_] = bc_r

        return bc

    @property
    def Kbc(self) -> npt.NDArray[np.float64]:
        """
        Stiffness matrix with boundary conditions applied

        Returns
        -------
            np.array
                Stiffness matrix with boundary conditions applied
        """
        # Get the boundary conditions from the reactions
        bc = self.__get_boundary_conditions()

        # Apply boundary conditions to global stiffness matrix. Note that the
        # boundary conditions are applied to a copy of the stiffness matrix to
        # avoid changing the property K, so it can still be used with further
        # calculations (ie, for calculating reaction values)
        kg = self.K.copy()
        kg = self.apply_boundary_conditions(kg, bc)
        return kg

    @property
    def b_input(self) -> npt.NDArray[np.float64]:
        """
        input load vector `b`

        Returns
        -------
            np.array
                input load vector `b`
        """

        # create an array for all loads (forces and moments) initialized to
        # zero. This vector is the input load vector that will be used to
        # solve for the reaction forces
        b = np.zeros(self.mesh.dof)

        # create boolean index mapping for b vector to select all forces and
        # moments (separately). Force and moment values are in alternating
        # pairs, starting with force.
        # Note these vectors have the same size as the number of nodes
        force_map = np.array([True, False] * int(b.size / 2))
        moment_map = np.array([not force for force in force_map])

        # create array of load magnitudes. The locations of these loads line
        # up with the locations array
        forces = np.array([p[0] for p in self.equivalent_loads])
        moments = np.array([m[1] for m in self.equivalent_loads])

        # create a location vector with the locations of all loads acting on
        # the beam.
        # Note there may be multiple loads acting at the same location.
        # There also may be forces and moments acting at the same location.
        # These must be recorded separately.
        locations = np.array([p_.location for p_ in self.equivalent_loads])

        # total force and  magnitudes are aligned with mesh nodes (locations)
        forces_total = np.array(
            [forces[locations == iloc].sum(axis=0) for iloc in self.mesh.nodes]
        )
        moments_total = np.array(
            [moments[locations == iloc].sum(axis=0) for iloc in self.mesh.nodes]
        )

        # update the input force vector with the total force and moments for
        # each node
        b[force_map] = forces_total
        b[moment_map] = moments_total

        # Get the boundary conditions from the reactions
        bc = self.__get_boundary_conditions()

        # get a mask for the elements in the b matrix to apply the boundary
        # conditions to
        bci = np.array([val is not None for val in bc.ravel()])
        b[bci] = 0
        return b

    def _calc_node_deflections(self) -> npt.NDArray[np.float64]:
        """solve for vertical and angular displacement at each node"""

        # get the stiffness matrix with boundary conditions applied
        kg = self.Kbc

        # get the input load vector
        b = self.b_input

        # Solve the global system of equations {b} = [K]*{d} for {d}
        # save the deflection vector for the beam, so the analysis can be
        # reused without recalculating the stiffness matrix.
        # This vector should be cleared anytime any of the beam parameters
        # gets changed.
        nd = np.linalg.solve(kg, b)
        nd64 = np.asarray(nd, dtype=np.float64)
        self._node_deflections = nd64
        return self._node_deflections

    def update_reactions(self) -> npt.NDArray[np.float64]:

        # get the load vector of all loads on each node
        r = self.load_vector

        assert self.reactions is not None
        # go over all reactions and update the force/moment value
        for ri in self.reactions:
            i = np.where(self.mesh.nodes == ri.location)[0][0]
            force, moment = r[i * 2 : i * 2 + 2]

            # set the values in the reaction objects
            ri.force = force
            ri.moment = moment
        return r

    def shape(
        self, x: npt.NDArray[np.float64], L: Optional[float] = None
    ) -> npt.NDArray[np.float64]:
        """
        array of shape functions

        Parameters
        ----------
            x : numeric | array_like
                local x-coordinates where shape function is evaluated
            L : numeric | None
                length of element.Default is total beam length

        Returns
        -------
            np.array
                array of shape functions
        """
        x = np.asarray(x, dtype=float)
        if L is None:
            L = self.length
        N1 = 1 / L**3 * (L**3 - 3 * L * x**2 + 2 * x**3)
        N2 = 1 / L**2 * (L**2 * x - 2 * L * x**2 + x**3)
        N3 = 1 / L**3 * (3 * L * x**2 - 2 * x**3)
        N4 = 1 / L**2 * (x**3 - L * x**2)
        return np.stack([N1, N2, N3, N4], axis=-1)  # (..., 4)

    def shape_d(
        self, x: npt.NDArray[np.float64], L: Optional[float] = None
    ) -> npt.NDArray[np.float64]:
        """
        first derivative of shape functions

        Parameters
        ----------
            x : numeric | array_like
                local x-coordinates where shape function is evaluated
            L : numeric | None
                length of element. Defaults to beam length when None.

        Returns
        -------
            np.array
                array of the first derivative of shape functions
        """
        x = np.asarray(x, dtype=float)
        if L is None:
            L = self.length
        N1 = 6 * x / L**3 * (-L + x)
        N2 = 1 - 4 * x / L + 3 * x**2 / L**2
        N3 = 6 * x / L**3 * (L - x)
        N4 = x / L**2 * (-2 * L + 3 * x)
        return np.stack([N1, N2, N3, N4], axis=-1)  # (..., 4)

    def shape_dd(
        self, x: npt.NDArray[np.float64], L: Optional[float] = None
    ) -> npt.NDArray[np.float64]:
        """
        second derivative of shape functions

        Parameters
        ----------
            x : numeric | array_like
                local x-coordinates where shape function is evaluated
            L : numeric | None
                length of element. Defaults to beam length when None.

        Returns
        -------
            np.array
                array of the second derivative of shape functions
        """

        x = np.asarray(x, dtype=float)
        if L is None:
            L = self.length
        N1 = -6 / L**3 * (L - 2 * x)
        N2 = 2 / L**2 * (-2 * L + 3 * x)
        N3 = 2 / L**3 * (3 * L - 6 * x)
        N4 = 2 / L**2 * (-L + 3 * x)
        return np.stack([N1, N2, N3, N4], axis=-1)  # (..., 4)

    def shape_ddd(
        self, x: npt.NDArray[np.float64], L: Optional[float] = None
    ) -> npt.NDArray[np.float64]:
        """
        third derivative of shape functions

        Parameters
        ----------
            x : numeric | array_like
                local x-coordinates where shape function is evaluated
            L : numeric | None
                length of element. Defaults to beam length when None.

        Returns
        -------
            np.array
                array of the third derivative of shape functions
        """

        x = np.asarray(x, dtype=float)
        if L is None:
            L = self.length
        N1 = 12 / L**3 * np.ones(x.shape)
        N2 = 6 / L**2 * np.ones(x.shape)
        N3 = -12 / L**3 * np.ones(x.shape)
        N4 = 6 / L**2 * np.ones(x.shape)
        return np.stack([N1, N2, N3, N4], axis=-1)  # (..., 4)

    def plot_shapes(
        self, n: int = 25
    ) -> tuple["Figure", list["Axes"]]:  # pragma: no cover
        """
        plot shape functions for the with `n` data points

        Does not automatically show the figure. Use the `.show()` method to
        show the figure.

        Parameters
        ----------
            n : int
                number of data points

        Returns
        -------
             (fig, axes) : tuple
                matplotlib figure and axes for the generated figure in a tuple
        """

        # set up list of axes with a grid where the two figures in each column
        # share an x-axis
        axes: list["Axes"] = []
        fig = plt.figure()
        axes.append(fig.add_subplot(221))
        axes.append(fig.add_subplot(222))
        axes.append(fig.add_subplot(223, sharex=axes[0]))
        axes.append(fig.add_subplot(224, sharex=axes[1]))

        # calculate the shape functions and their derivatives
        x = np.linspace(0, self.length, n, endpoint=True)
        N = self.shape(x, self.length).T
        Nd = self.shape_d(x, self.length).T
        Ndd = self.shape_dd(x, self.length).T
        Nddd = self.shape_ddd(x, self.length).T

        for k in range(4):
            ax = axes[k]
            ax.grid(True)
            ax.plot(x, N[k], "-", color="tab:blue", label=f"$N_{k + 1}$")
            ax.plot(x, Nd[k], "--", color="tab:orange", label="$\\frac{dN}{dx}$")
            ax.plot(x, Ndd[k], ":", color="tab:green", label="$\\frac{d^2N}{dx^2}$")
            ax.plot(x, Nddd[k], "-.", color="tab:red", label="$\\frac{d^3N}{dx^3}$")
            ax.legend()

        fig.subplots_adjust(wspace=0.125, hspace=0)

        return fig, axes

    def stiffness(self, L: Optional[float] = None) -> npt.NDArray[np.float64]:
        """
        local stiffness matrix as numpy array

        Parameters
        ----------
            L : numeric | optional
                length of element. Defaults to beam length when None.
        """
        if L is None:
            L = self.length

        k = np.array(
            [
                [12, 6 * L, -12, 6 * L],
                [6 * L, 4 * L**2, -6 * L, 2 * L**2],
                [-12, -6 * L, 12, -6 * L],
                [6 * L, 2 * L**2, -6 * L, 4 * L**2],
            ]
        )
        return self.E * self.Ixx / L**3 * k

    def stiffness_global(self) -> npt.NDArray[np.float64]:
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
