"""
The reactions module defines different reaction classes

A reaction is required to support an element to resist any input forces.

There are two types of reactions that are defined.

    * PinnedReaction, allows rotational displacement only
    * FixedReaction, does not allow any displacement

"""
from typing import Optional, Tuple

from ._common import Forces


class Reaction(Forces):
    """Base class for all reactions

    The Reaction class defines general properties related to all reaction
    types.

    Parameters:
        location (:obj:`float`): the axial location of the reaction along the
                                 length of the beam.

    .. note:: Any force or moment values that where calculated values are
             invalidated (set to :obj:`None`) any time the location is set.

    Attributes:
        force (:obj:`float | None`): the force of the reaction after it has
                                     been calculated
        moment (:obj:`float | None`): The moment of the reaction after it has
                                      been calculated
    """

    name = ""

    def __init__(self, location: float):
        super().__init__(magnitude=None, location=location)
        self.force = None
        self.moment = None

    @property
    def location(self) -> float:
        """
        Location of the reaction along the length of the beam

        The units of the length property is the same as the units of the beam
        length.

        The value of the location must be a positive value that is less than
        or equal to the length of the beam, or it will raise a ValueError.

        .. note:: The force and moment values are set to :obj:`None` any time
                  the location is set.
        """
        return self._location

    @location.setter
    def location(self, location: float) -> None:
        # The location is overloading the location property in Forces so that
        # the reaction can be invalidated when the location is changed
        if location < 0:
            # location cannot be a negative number
            raise ValueError("location must be positive!")
        self.invalidate()
        self._location = location

    @property
    def value(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Simple tuple of force and moment

        Returns:
            :obj:`tuple` (force, moment)
        """
        return self.force, self.moment

    def invalidate(self) -> None:
        """Invalidate the reaction values

        This will set the force and moment values to :obj:`None`

        To be used whenever the parameters change and the reaction values are
        no longer valid.
        """
        self.force, self.moment = (None, None)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}\n"
            f"  Location: {self.location}\n"
            f"     Force: {self.force}\n"
            f"    Moment: {self.moment}\n"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(location={self.location})"

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, self.__class__):
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
    A PinnedReaction allows rotation displacements only

    A PinnedReaction represents a pinned, frictionless pivot that can
    resist motion both normal and axial directions to the beam. It will not
    resist moments.
    The deflection of a beam at the PinnedReaction is always zero, but
    the angle is free to change

    Parameters:
        location (:obj:`float`): the axial location of the reaction along the
                                 length of the beam

    Attributes:
        name (:obj:`str`): short name of the reaction (pinned). Used internally

    .. warning:: The **name** attribute is used internally.
                 **Do not change this value!**
    """

    name = "pinned"

    def __init__(self, location: float):
        super().__init__(location)
        # limit the vertical displacement but allow rotation
        self.boundary = (0, None)


class FixedReaction(Reaction):
    """
    A FixedReaction does not allow any displacement or change in angle

    A FixedReaction resists both force and moments. The displacement and the
    angle are both constrained and must be zero at the reaction point.
    FixedReactions are typically applied at the ends of a Beam.

    Parameters:
        location (:obj:`float`): the axial location of the reaction along the
                                 length of the beam

    Attributes:
        name (:obj:`str`): short name of the reaction (fixed). Used internally

    .. warning:: The **name** attribute is used internally.
                 **Do not change this value!**
    """

    name = "fixed"

    def __init__(self, location: float):
        super().__init__(location)
        # do not allow vertical or rotational displacement
        self.boundary = (0, 0)
