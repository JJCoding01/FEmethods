"""
The reactions module defines different reaction classes

A reaction is required to support a Beam element to resist any input forces.

There are two types of reactions that are defined.

    * PinnedReaction
    * FixedReaction

PinnedReaction
+++++++++++++++

A PinnedReaction represents a pinned, frictionless pivot that can
resist motion in two directions. Normal and axially to the beam.
A PinnedReaction does not have any ability to resist moments.
The deflection of a beam at the PinnedReaction is always zero, but
the angle is free to change

FixedReaction
+++++++++++++++

A FixedReaction resists both force and moments. The displacement and the
angle are both constrained and must be zero at the reaction point.
FixedReactions are typically applied at the ends of a Beam.
"""

from ._common import Forces, Validator


class Reaction(Forces):
    """Base class for all reactions

    This class will define general properties related to a reaction

    Parameters:
        location (float): the axial location of the reaction along the length of the beam.

    .. note:: Any force or moment values that where calculated values are
             invalidated (set to None) any time the location is set.

    Attributes:
        force (float | None): the force of the reaction after it has been
                              calculated
        moment (float | None): The moment of the reaction after it has been calculated
    """

    name = None

    def __init__(self, location):
        super().__init__(magnitude=None, location=location)
        self.force = None
        self.moment = None

    @property
    def location(self):
        """
        Location of the reaction along the length of the beam

        .. note:: Any force or moment values that where calculated values are
         invalidated (set to None) any time the location is set.
        """
        return self._location

    @location.setter
    @Validator.non_negative("location")
    def location(self, location):
        # The location is overloading the location property in Forces so that
        # the reaction can be invalidated when the location is changed
        self.invalidate()
        self._location = location

    @property
    def value(self):
        """
        Simple tuple of force and moment

        Returns (force, moment)
        """
        return self.force, self.moment

    def invalidate(self):
        """Invalidate the reaction values

        This will set the force and moment values to None

        To be used whenever the parameters change and the reaction values are
        no longer valid
        """
        self.force, self.moment = (None, None)

    def __str__(self):
        return (
            f"{self.__class__.__name__}\n"
            f"  Location: {self.location}\n"
            f"     Force: {self.force}\n"
            f"    Moment: {self.moment}\n"
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(location={self.location})"

    def __eq__(self, other):

        if self.__class__ != other.__class__:
            return False

        if (
            self.location == other.location
            and self.force == other.force
            and self.moment == other.moment
        ):
            return True

        return False


class PinnedReaction(Reaction):
    """
    A PinnedReaction allows rotation while restraining normal and axial displacements

    Parameters:
        location (float): the axial location of the reaction along the length
                          of the beam

    Attributes:
        name (str): short name of the reaction (pinned). Used internally

    .. warning:: The **name** attribute is for internal use only.
                 Do not change this value.
    """

    name = "pinned"

    def __init__(self, location):
        super().__init__(location)
        # limit the vertical displacement but allow rotation
        self.boundary = (0, None)


class FixedReaction(Reaction):
    """
    A FixedReaction does not allow any displacement or change in angle

    Parameters:

        location (float): the axial location of the reaction along the length
                          of the beam
    .. note:: FixedReactions are normally located at the end(s) of a Beam

    Attributes:
        name (str): short name of the reaction (fixed). Used internally

    .. warning:: The **name** attribute is for internal use only.
                 Do not change this value.
    """

    name = "fixed"

    def __init__(self, location):
        super().__init__(location)
        # do not allow vertical or rotational displacement
        self.boundary = (0, 0)
