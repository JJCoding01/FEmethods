"""
The elements module contains finite element classes

Currently the only element that is defined is a beam element.

"""

import matplotlib.pyplot as plt
import numpy as np

from .__base import BeamElement


# noinspection PyPep8Naming
class Beam(BeamElement):
    """A Beam defines a beam element for analysis

    A beam element is a slender member that is subjected to transverse loading.
    It is assumed to have homogeneous properties, with a constant
    cross-section.

    Parameters
    ----------
    length : float
        the length of a beam. This is the total length of the beam, this is
        not the length of the meshed element. This must be a float that is
        greater than 0.
    loads : list
        applied load elements
    reactions : list
        reactions acting on the beam
    mesh : Mesh: default = None
        mesh object for beam. Default is to auto create the mesh
    E : float: Optional: default = `1`
        Young's modulus of the beam in units of :math:`\\frac{force}{length^2}`.
         The :math:`force` units used here are the same units
         that are used in the input forces, and calculated reaction forces.
         The :math:`length` unit must be the same as the area moment of inertia
         (`Ixx`) and the beam `length` units.
    Ixx : float Optional: default = `1`
        Area moment of inertia of the beam. This is constant (constant
        cross-sectional area) along the length of the beam. This is in units
        of :math:`length^4`. This must be the same length unit of Young's
        modulus (`E`) and the beam `length`.
    """

    def __init__(
        self,
        length,
        loads,
        reactions,
        mesh=None,
        E=1,
        Ixx=1,
    ):
        super().__init__(length, loads, reactions, mesh=mesh, E=E, Ixx=Ixx)
        self.solve()

    def validate_x(self, x):
        """
        Validate the `x` value for use when calculating deflection, angle moment or shear

        This will perform the following validations:

        * `x` is an array (even for single values)
        * all values in `x` are greater than or equal to `0`
        * all values in `x` are less than or equal to beam length


        Parameters
        ----------
            x : numeric | array_like
                x-coordinate to validate

        Returns
        -------
        array_like:
            `x` as an array

        Raises
        ------
        ValueError:
            any `x` values are less than 0
            any `x` values are greater than length
        """

        # update x to ensure it is an array, regardless of how it was entered
        if np.isscalar(x):
            # the input is a scalar, update it to be an array
            x = np.array([x])

        # ensure that even if lists, tuples etc are given, x is always treated
        # like an array
        x = np.asarray(x)

        # validate that x is valid by ensuring that x is in the allowed range
        invalid_mask = (x < 0) | (self.length < x)
        if np.any(invalid_mask):
            # there are some invalid x-values, show these in the error message
            raise ValueError(
                f"cannot perform calculation outside the beam "
                f"(range of 0 to {self.length})!"
                f" Invalid entries: {x[invalid_mask]}"
            )
        # once it gets to this point, the x value has been validated
        # and is an array
        return x

    def __result_setup(self, x):
        """
        Perform the setup calculations for deflection, moment and shear calculations

        This will perform the calculations/transforms to return the following:

        * validate the x values and array
        * array with the local x-coordinates for each x-value
        * nodal displacements
        * element length for each x-value

        Parameters
        ----------
            x : array_like
                global x-coordinates along the beam

        Returns
        -------
            tuple
                (validated x coordinates, local x coordinates, nodal displacements, lengths)
        """

        # Ensure that all x-values are valid and are in array form
        x = self.validate_x(x)

        # Calculate some values that are needed for calculating deflection
        nodes = self.mesh.nodes  # node locations (entire beam)
        lengths = self.mesh.lengths  # element lengths (entire beam)
        nd = self.node_deflections  # nodal deflections (entire beam)

        # for each x-value, find the element index where it is located
        i = np.clip(
            np.searchsorted(nodes, x, side="left") - 1,  # index
            a_min=0,
            a_max=None,
        )
        x_local = x - nodes[i]  # local x-coordinates
        L = lengths[i]  # array of local lengths

        # collect nodal deflections that are related to these x's
        idx = (2 * i)[:, None] + np.arange(4)[None, :]
        d_nodal = nd[idx]  # nodal deflections for each x

        return x, x_local, d_nodal, L

    def deflection(self, x):
        """
        Calculate deflection of the beam at location x

        Parameters
        ----------
            x : array_like
                locations along the beam where deflection is calculated.

        Returns
        -------
            array_like
                deflection of the beam in units of the beam length

        Raises
        ------
            ValueError
                when the :math:`0\\leq x \\leq length` is False

        Notes
        -----
        The deflections are calculated by taking the dot product of the shape
        functions, and the nodal displacements.
        This is represented in the form:

        .. centered::
            :math:`d(x) = \\vec{N} \\cdot \\vec{d}_{nodal}`

        Where :math:`\\vec{N}` is the shape function vector evaluated at the
        local `x` values of each element for each `x` coordinate, and
        :math:`\\vec{d_{nodal}}` is the nodal displacement vector.
        """

        x, x_local, d_nodal, L = self.__result_setup(x)

        # calculate the shape functions for all local x and L values
        N = self.shape(x_local, L)

        # calculate the deflections as the dot product of the nodal
        # displacements and shape functions.
        return np.sum(N * d_nodal, axis=1)

    def angle(self, x):
        """
        Calculate angle of the beam at location x in degrees

        Parameters
        ----------
            x : array_like
                locations along the beam where moment is calculated.

        Returns
        -------
            array_like
                moment of the beam

        Raises
        ------
            ValueError
                when the :math:`0\\leq x \\leq length` is False

        Notes
        -----

        The angles are calculated by taking the first derivative of the
        deflection equation:

        .. centered::
            :math:`\\theta(x) = \\frac{d v(x)}{dx}`

        An alternate representation can be calculated using the first
        derivative of the shape functions, and taking the dot product of the
        nodal displacements. This method is more reliable when the function
        :math:`v(x)` is unknown, so taking the derivative is done numerically.

        .. centered::
            :math:`\\theta(x) = \\frac{d\\vec{N}}{dx} \\cdot \\vec{d}_{nodal}`

        Where :math:`\\vec{N}` is the shape functions evaluated at the local
        `x` values of each element for each `x` coordinate, and
        :math:`\\vec{d}_{nodal}` is the nodal displacement vector.
        """

        x, x_local, d, L = self.__result_setup(x)

        # calculate the shape functions for all local x and L values
        N = self.shape_d(x_local, L)

        # calculate the angle as the dot product of the first derivative of
        # the shape functions and nodal displacements
        ang = np.sum(N * d, axis=1)
        return np.rad2deg(ang)

    def moment(self, x):
        """
        Calculate moment of the beam at location x


        Parameters
        ----------
            x : array_like
                locations along the beam where moment is calculated.

        Returns
        -------
            array_like
                moment of the beam

        Raises
        ------
            ValueError
                when the :math:`0\\leq x \\leq length` is False

        Notes
        -----
        The moments are calculated by solving this equation:

        .. centered::
            :math:`M(x) = E \\cdot Ixx \\cdot \\frac{d^2 v(x)}{dx^2}`

        where :math:`M` is the moment, :math:`E` is Young's modulus and
        :math:`Ixx` is the area moment of inertia.

        An alternate representation can be calculated using the second
        derivative of the shape functions, and taking the dot product of the
        nodal displacements. This method is more reliable when the function
        :math:`v(x)` is unknown, so taking the derivative is done numerically.

        .. centered::
            :math:`M(x) = \\frac{d^2 \\vec{N}}{dx^2} \\cdot \\vec{d}_{nodal}`

        Where :math:`\\vec{N}` is the shape functions evaluated at the local
        `x` values of each element for each `x` coordinate, and
        :math:`\\vec{d}_{nodal}` is the nodal displacement vector.

        """

        x, x_local, d, L = self.__result_setup(x)

        # calculate the shape functions for all local x and L values
        N = self.shape_dd(x_local, L)

        # calculate the moment as the dot product of the second derivative of
        # the shape functions and nodal displacements
        return -self.E * self.Ixx * np.sum(N * d, axis=1)

    def shear(self, x):
        """
        Calculate shear force of the beam at location x

        Parameters
        ----------
            x : array_like
                locations along the beam where moment is calculated.

        Returns
        --------
            array_like
                shear force in the beam

        Raises
        -------
            ValueError
                when the :math:`0\\leq x \\leq length` is False

        Notes
        -----
        The shear forces are calculated by solving this equation:

        .. centered::
            :math:`V(x) = E \\cdot Ixx \\cdot \\frac{d^3 v(x)}{dx^3}`

        where :math:`M` is the moment, :math:`E` is Young's modulus and
        :math:`Ixx` is the area moment of inertia.

        An alternate representation can be calculated using the third
        derivative of the shape functions, and taking the dot product of the
        nodal displacements. This method is more reliable when the function
        :math:`v(x)` is unknown, so taking the derivative is done numerically.

        .. centered::
            :math:`V(x) = \\frac{d^3 \\vec{N}}{dx^3} \\cdot \\vec{d}_{nodal}`

        Where :math:`\\vec{N}` is the shape functions evaluated at the local
        `x` values of each element for each `x` coordinate, and
        :math:`\\vec{d}_{nodal}` is the nodal displacement vector.
        """

        x, x_local, d, L = self.__result_setup(x)

        # calculate the shape functions for all local x and L values
        N = self.shape_ddd(x_local, L)

        # calculate the shear as the dot product of the third derivative of
        # the shape functions and nodal displacements
        return -self.E * self.Ixx * np.sum(N * d, axis=1)

    @staticmethod
    def __validate_plot_diagrams(diagrams, diagram_labels):
        """
        Validate the parameters for the plot function
        """

        # create default (and complete list of valid) diagrams that are
        # implemented
        default_diagrams = ("shear", "moment", "angle", "deflection")
        if diagrams is None and diagram_labels is None:
            # set both the diagrams and labels to their defaults
            # no need for further validation of these values since they are
            # set internally
            return default_diagrams, default_diagrams

        if diagrams is None and diagram_labels is not None:
            raise ValueError("cannot set diagrams from labels")

        if diagram_labels is None:
            diagram_labels = diagrams

        if len(diagrams) != len(diagram_labels):
            raise ValueError("length of diagram_labels must match length of diagrams")
        for diagram in diagrams:
            if diagram not in default_diagrams:
                raise ValueError(f"values of diagrams must be in {default_diagrams}")
        return diagrams, diagram_labels

    def plot(
        self,
        n=250,
        title="Beam Analysis",
        diagrams=None,
        diagram_labels=None,
        fig=None,
        axes=None,
        **kwargs,
    ):
        """
        Plot the deflection, moment, and shear along the length of the beam

        The plot method will create a :obj:`matplotlib.pyplot` figure with the
        deflection, moment, and shear diagrams along the length of the beam
        element. Which of these diagrams, and their order may be customized.

        Parameters
        ----------
            n : int: default = `250`
                number of data-points to use in plots
            title : str: default = "Beam Analysis"
                title on top of plot
            diagrams : tuple | None: {"shear", "moment", "angle", "deflection"}
                tuple of diagrams to plot. All values in tuple must be strings,
                and one of the defaults.
                Default value is all charts: ("shear", "moment", "angle", "deflection")
            diagram_labels : tuple | None
                y-axis labels for subplots. Must have the same length as `diagrams`
                Default is the name of the chart (ie "shear")
            fig : matplotlib.figure.Figure | None: default = None
                figure where the chart should be made. If `None`, one is created.
            axes : matplotlib.axes.Axes | None: default = None
                axes where plots are made. If `None`, one is created.
            **kwargs:
                Additional keyword arguments used to format the figure and
                axes. Some key ones are:

                * `grid`: bool: whether grid is applied, default is `True`
                * `xlabel`: str: x-axis label, default is `Beam Position, x`
                * `fill`: bool: whether to fill between the x-axis and value
                    for all charts
                * `plot_kwargs`: any keyword argument to pass to the
                    `matplotlib.pyplot.plot()` function.
                    Default is no additional arguments.
                * `fill_kwargs`: any keyword argument to pass to the
                  `matplotlib.pyplot.fill_between()` function()

        Returns
        -------
             tuple
                Tuple of :obj:`matplotlib.pyplot` figure and list of axes in
                the form :obj:`(figure, axes)`

        .. note:: The plot method will create the figure handle, but will not
                  automatically show the figure.
                  To show the figure use :obj:`Beam.show()` or
                  :obj:`matplotlib.pyplot.show()`

        .. versionchanged:: 0.1.7a1 Removed :obj:`bending_stress` parameter
        .. versionchanged:: 0.1.7a1
            Added :obj:`diagrams` and :obj:`diagram_labels` parameters

        """

        kwargs.setdefault("title", "Beam Analysis")
        kwargs.setdefault("grid", True)
        kwargs.setdefault("xlabel", "Beam position, x")
        kwargs.setdefault("fill", True)
        kwargs.setdefault("plot_kwargs", {})
        kwargs.setdefault("fill_kwargs", {"color": "b", "alpha": 0.25})

        diagrams, diagram_labels = self.__validate_plot_diagrams(
            diagrams, diagram_labels
        )
        if axes is None:
            fig, axes = plt.subplots(len(diagrams), 1, sharex="all")

            if len(diagrams) == 1:
                # make sure axes are iterable, even if there is only one
                axes = [axes]

        x = np.linspace(0, self.length, n, endpoint=True)
        y = None
        for ax, diagram, label in zip(axes, diagrams, diagram_labels):
            if diagram == "deflection":
                y = self.deflection(x)
            if diagram == "angle":
                y = self.angle(x)
            if diagram == "moment":
                y = self.moment(x)
            if diagram == "shear":
                y = self.shear(x)

            ax.plot(x, y, **kwargs["plot_kwargs"])
            if kwargs["fill"]:
                ax.fill_between(x, y, 0, **kwargs["fill_kwargs"])
            ax.set_ylabel(label)
            ax.grid(kwargs["grid"])

        locations = self.mesh.nodes  # in global coordinate system
        axes[-1].set_xlabel(kwargs["xlabel"])
        axes[-1].set_xticks(locations)

        fig.subplots_adjust(hspace=0.06)
        fig.suptitle(title)
        return fig, axes

    @staticmethod
    def show(*args, **kwargs):
        """Wrapper function for showing matplotlib figure

        This method gives direct access to the matplotlib.pyplot.show function
        so the calling code is not required to import matplotlib directly
        just to show the plots

        Parameters:
             args kwargs
                args and kwargs are passed directly to `matplotlib.pyplot.show()` method
        """
        plt.show(*args, **kwargs)  # pragma: no cover

    def __str__(self):

        # TODO: update string representation of Load
        #   since a Load may have both force and moment components, which are scaled by
        #   the magnitude, they both must be accounted for when printing. Currently,
        #   only the standard specially loads are represented properly.

        L = ""
        for load in self.loads:
            L += str(load)

        r = ""
        for reaction in self.reactions:
            r += "Type: {}\n".format(reaction.name)
            r += "    Location: {}\n".format(reaction.location)
            r += "       Force: {}\n".format(reaction.force)
            r += "      Moment: {}\n".format(reaction.moment)

        msg = (
            "PARAMETERS\n"
            f"Length (length): {self.length}\n"
            f"Young's Modulus (E): {self.E}\n"
            f"Area moment of inertia (Ixx): {self.Ixx}\n"
            f"LOADING\n"
            f"{L}\n"
            f"REACTIONS\n"
            f"{r}\n"
        )
        return msg
