"""
The Reaction's module defines different reaction classes

A reaction is required to support an element to resist any input forces.

There are two types of reactions that are defined.

    * PinnedReaction, allows rotational displacement only
    * FixedReaction, does not allow any displacement
"""

from .. import validation
from ..core import Force


class Reaction(Force):
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

    def __init__(self, location):
        super().__init__(magnitude=None, location=location)
        self.force = None
        self.moment = None
        self._boundary = (None, None)

    @property
    def boundary(self):
        return self._boundary

    @property
    def location(self):
        """
        Location of the reaction along the length of the beam

        The units of the length property is the same as the units of the beam
        length.

        The value of the location must be a positive value that is less than
        or equal to the length of the beam, or it will raise a ValueError.

        .. note:: The force and moment values are set to :obj:`None` any time
                  the location is set.

        Raises:
            ValueError: when location is less than 0
            TypeError: when location is set to any non-numeric value
        """
        return self._location

    @location.setter
    @validation.is_numeric
    @validation.non_negative
    def location(self, location):
        # The location is overloading the location property in Forces so that
        # the reaction can be invalidated when the location is changed
        self.invalidate()
        self._location = location

    @property
    def value(self):
        """
        Simple tuple of force and moment

        Returns:
            :obj:`tuple` (force, moment)
        """
        return self.force, self.moment

    def invalidate(self):
        """Invalidate the reaction values

        This will set the force and moment values to :obj:`None`

        To be used whenever the parameters change and the reaction values are
        no longer valid.
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

        if not isinstance(other, self.__class__):
            return False

        return (
            self.location == other.location
            and self.force == other.force
            and self.moment == other.moment
        )
