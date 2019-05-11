"""
Reactions module defines different reaction classes

A reaction is required to support a Beam element and resist any input forces.

There are two types of reactions that are defined.

    * PinnnedReaction
      A PinnedReaction represents a pinned, frictionless pivot that can
      resist motion in two directions. Normal and axially to the beam.
      A PinnedReaction does not have any ability to resist moments.
      The deflection of a beam at the PinnedReaction is always zero, but
      the angle is free to change
    * FixedReaction
      A FixedReaction resists both force and moments. The displacement and the
      angle are both constrained and must be zero at the reaction point.
      FixedReactions are typically applied at the ends of a Beam.
"""

from ._common import Forces, Validator


class Reaction(Forces):
    """Base class for all reactions"""

    name = None

    def __init__(self, location):
        super().__init__(magnitude=None, location=location)
        self._force = None
        self._moment = None

    @property
    def force(self):
        return self._force

    @force.setter
    def force(self, f):
        self._force = f

    @property
    def moment(self):
        return self._moment

    @moment.setter
    def moment(self, m):
        self._moment = m

    @property
    def location(self):
        """
        Location of the reaction along the length of the beam

        The location is overloading the location property in Forces so that
        the reaction can be invalidated when the location is changed
        """
        return self._location

    @location.setter
    @Validator.non_negative("location")
    def location(self, location):
        """
        Set the location of the Reaction along the length of the beam

        The location is overloading the location property in Forces so that
        the reaction can be invalidated when the location is changed
        """
        self.invalidate()
        self._location = location

    @property
    def value(self):
        return self.force, self.moment

    def invalidate(self):
        """Invalidate the reaction values

        To be used whenever the parameters change and the reaction values are
        no longer valid
        """
        self._force, self._moment = (None, None)

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
    name = "pinned"

    def __init__(self, location):
        super().__init__(location)
        # limit the vertical displacement but allow rotation
        self.boundary = (0, None)


class FixedReaction(Reaction):
    name = "fixed"

    def __init__(self, location):
        super().__init__(location)
        # do not allow vertical or rotational displacement
        self.boundary = (0, 0)
