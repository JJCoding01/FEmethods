"""
The elements module contains finite element classes

Currently the only element that is defined is a beam element.

"""

from warnings import warn

import matplotlib.pyplot as plt
import numpy as np

from scipy.misc import derivative

# local imports
from femethods.core import derivative as comm_derivative

from .__base import BeamElement


# noinspection PyPep8Naming
class Beam(BeamElement):
    """A Beam defines a beam element for analysis

    A beam element is a slender member that is subjected to transverse loading.
    It is assumed to have homogeneous properties, with a constant
    cross-section.


    Parameters:
        length (:obj:`float`): the length of a beam. This is the total length
                        of the beam, this is not the length of the meshed
                        element. This must be a float that is greater than 0.
        loads (:obj:`list`): list of load elements
        reactions (:obj:`list`): list of reactions acting on the beam
        E (:obj:`float`, optional): Young's modulus of the beam in units of
                         :math:`\\frac{force}{length^2}`. Defaults to 1.
                         The :math:`force` units used here are the same
                         units that are used in the input forces, and
                         calculated reaction forces. The :math:`length` unit
                         must be the same as the area moment of inertia
                         (**Ixx**) and the beam **length** units.
        Ixx (:obj:`float`, optional): Area moment of inertia of the beam.
                    Defaults to 1. This is constant (constant cross-sectional
                    area) along the length of the beam. This is in units of
                    :math:`length^4`. This must be the same length unit of
                    Young's modulus (**E**) and the beam **length**.

    """

    def __init__(
        self,
        length,
        loads,
        reactions,
        E=1,
        Ixx=1,
    ):
        super().__init__(length, loads, reactions, E=E, Ixx=Ixx)
        self.solve()

    def deflection(self, x):
        """Calculate deflection of the beam at location x

        Parameters:
            x (:obj:`float | int`): location along the length of the beam where
                           deflection should be calculated.

        Returns:
            :obj:`float`: deflection of the beam in units of the beam length

        Raises:
            :obj:`ValueError`: when the :math:`0\\leq x \\leq length` is False
            :obj:`TypeError`: when x cannot be converted to a float
        """

        # TODO: store the lengths/node locations in the class so they only have
        #  to be assessed without recalculating
        nodes = self.mesh.nodes

        # validate that x is valid by ensuring that x is in the allowed range
        if x < 0 or self.length < x:
            raise ValueError(
                f"cannot calculate deflection at location {x} as "
                f"it is outside of the beam!"
            )

        # Using the given global x-value, determine the local x-value, length
        # of active element, and the nodal displacements (vertical, angular)
        # vector d
        for i in range(len(self.mesh.lengths)):
            if nodes[i] <= x <= nodes[i + 1]:
                # this is the element where the global x-value falls into.
                # Get the parameters in the local system and exit the loop
                x_local = x - nodes[i]
                L = self.mesh.lengths[i]
                d = self.node_deflections[i * 2 : i * 2 + 4]
                return self.shape(x_local, L).dot(d)

    def moment(self, x, dx=1e-5, order=9):
        """Calculate the moment at location x

        Calculate the moment in the beam at the global x value by taking
        the second derivative of the deflection curve.

        .. centered::
            :math:`M(x) = E \\cdot Ixx \\cdot \\frac{d^2 v(x)}{dx^2}`

        where :math:`M` is the moment, :math:`E` is Young's modulus and
        :math:`Ixx` is the area moment of inertia.

        .. note: When calculating the moment near the beginning of the beam
                 the moment calculation may be unreliable.

        Parameters:
            x (:obj:`int`): location along the beam where moment is calculated
            dx (:obj:`float`, optional): spacing. Default is 1e-5
            order (:obj:`int`, optional): number of points to use, must be odd.
                Default is 9

        Returns:
            :obj:`float`: moment in beam at location x

        Raises:
            :obj:`ValueError`: when the :math:`0\\leq x \\leq length` is False
            :obj:`TypeError`: when x cannot be converted to a float

        For more information on the parameters, see the scipy.misc.derivative
        documentation.
        """

        try:
            return (
                self.E
                * self.Ixx
                * derivative(self.deflection, x, dx=dx, n=2, order=order)
            )
        except ValueError:
            # there was an error, probably due to the central difference
            # method attempting to calculate the moment near the ends of the
            # beam. Determine whether the desired position is near the start
            # or end of the beam, and use the forward/backward difference
            # method accordingly

            if x <= self.length / 2:
                # the desired moment is near the beginning of the beam, use the
                # forward difference method
                method = "forward"
            else:
                # the desired moment is near the end of the beam, use the
                # backward difference method
                method = "backward"
            return (
                self.E
                * self.Ixx
                * comm_derivative(self.deflection, x, method=method, n=2)
            )

    def shear(self, x, dx=0.01, order=5):
        """
        Calculate the shear force in the beam at location x

        Calculate the shear in the beam at the global x value by taking
        the third derivative of the deflection curve.

        .. centered::
            :math:`V(x) = E \\cdot Ixx \\cdot \\frac{d^3 v(x)}{dx^3}`

        where :math:`V` is the shear force, :math:`E` is Young's modulus and
        :math:`Ixx` is the area moment of inertia.

        .. note: When calculating the shear near the beginning of the beam
                 the shear calculation may be unreliable.

        Parameters:
            x (:obj:`int`): location along the beam where moment is calculated
            dx (:obj:`float`, optional): spacing. Default is 0.01
            order (:obj:`int`, optional): number of points to use, must be odd.
                Default is 5

        Returns:
            :obj:`float`: moment in beam at location x

        Raises:
            :obj:`ValueError`: when the :math:`0\\leq x \\leq length` is False
            :obj:`TypeError`: when x cannot be converted to a float

        For more information on the parameters, see the scipy.misc.derivative
        documentation.
        """
        return (
            self.E * self.Ixx * derivative(self.deflection, x, dx=dx, n=3, order=order)
        )

    def bending_stress(self, x, dx=1, c=1):
        """
        returns the bending stress at global coordinate x

        .. deprecated:: 0.1.7a1
            calculate bending stress as :obj:`Beam.moment(x) * c / Ixx`

        """
        warn("bending_stress will be removed soon", DeprecationWarning)
        return self.moment(x, dx=dx) * c / self.Ixx

    @staticmethod
    def __validate_plot_diagrams(diagrams, diagram_labels):
        """
        Validate the parameters for the plot function
        """

        # create default (and complete list of valid) diagrams that are
        # implemented
        default_diagrams = ("shear", "moment", "deflection")
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

        Parameters:
            n (:obj:`int`): defaults to `250`:
                number of data-points to use in plots
            title (:obj:`str`) defaults to 'Beam Analysis`
                title on top of plot
            diagrams (:obj:`tuple`): defaults to
                `('shear', 'moment', 'deflection')`
                tuple of diagrams to plot. All values in tuple must be strings,
                and one of the defaults.
                Valid values are :obj:`('shear', 'moment', 'deflection')`
            diagram_labels (:obj:`tuple`): y-axis labels for subplots.
                Must have the same length as `diagrams`

        Returns:
             :obj:`tuple`:
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

        xd = np.linspace(0, self.length, n)  # deflection
        x, y = None, None
        for ax, diagram, label in zip(axes, diagrams, diagram_labels):
            if diagram == "deflection":
                x = xd
                y = [self.deflection(xi) for xi in x]
            if diagram == "moment":
                x = xd
                y = [self.moment(xi, dx=self.length / (n + 3)) for xi in x]
            if diagram == "shear":
                x = np.linspace(0, self.length, n + 4)[2:-2]
                y = [self.shear(xi, dx=self.length / (n + 4)) for xi in x]

            # regardless of the diagram that is being plotted, the number of
            # data points should always equal the number specified by user
            assert len(x) == n, "x does not match n"
            assert len(y) == n, "y does not match n"

            ax.plot(x, y, **kwargs["plot_kwargs"])
            if kwargs["fill"]:
                ax.fill_between(x, y, 0, **kwargs["fill_kwargs"])
            ax.set_ylabel(label)
            ax.grid(kwargs["grid"])

        locations = self.mesh.nodes  # in global coordinate system
        axes[-1].set_xlabel(kwargs["xlabel"])
        axes[-1].set_xticks(locations)

        fig.subplots_adjust(hspace=0.25)
        fig.suptitle(title)
        return fig, axes

    @staticmethod
    def show(*args, **kwargs):
        """Wrapper function for showing matplotlib figure

        This method gives direct access to the matplotlib.pyplot.show function
        so the calling code is not required to import matplotlib directly
        just to show the plots

        Parameters:
             args/kwargs: args and kwargs are passed directly to
                          matplotlib.pyplot.show
        """
        plt.show(*args, **kwargs)  # pragma: no cover

    def __str__(self):

        # TODO: update string representation of Load
        #   since a Load may have both force and moment components, which are scaled by
        #   the magnitude, they both must be accounted for when printing. Currently,
        #   only the standard specially loads are represented properly.

        L = ""
        for load in self.loads:
            L += "Type: {}\n".format(load.name)
            L += "    Location: {}\n".format(load.location)
            L += "   Magnitude: {}\n".format(load.magnitude)

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
