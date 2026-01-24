"""
The Reaction's module defines different reaction classes

A reaction is required to support an element to resist any input forces.

There are two types of reactions that are defined.

    * PinnedReaction, allows rotational displacement only
    * FixedReaction, does not allow any displacement
"""

from typing import Any, Iterable, Literal, Optional, TypeAlias
from warnings import warn

from .. import validation
from ..core import Force

Dof: TypeAlias = Literal[0] | None
Boundary: TypeAlias = tuple[Dof, Dof]
Boundaries: TypeAlias = tuple[Boundary, ...]


class Reaction(Force):
    """Base class for all reactions

    The Reaction class defines general properties related to all reaction
    types.

    Parameters:
        location: numeric: the axial location of the reaction along the
           length of the beam.
        boundary: 0 | None | sequence: boundary conditions of reaction. This may be
            either 0, None, or a sequence of 0 and/or None. The boundary conditions are
            defined as:
                * 0: this degree-of-freedom is fixed
                * None: this degree-of-freedom is free

    .. note:: Any force or moment values that where calculated values are
             invalidated (set to :obj:`None`) any time the location is set.

    Attributes:
        force (:obj:`float | None`): the force of the reaction after it has
                                     been calculated
        moment (:obj:`float | None`): The moment of the reaction after it has
                                      been calculated

    Warns:
        UserWarning: when the boundary condition does not fix any degrees of freedom
            (ie, all boundary conditions are None)
    """

    name = "reaction"

    def __init__(self, location: float, boundary: Boundary = (None, None)) -> None:
        super().__init__(magnitude=None, location=location)
        self.force = None
        self.moment = None
        self.boundary = boundary

    @property
    def boundary(self) -> Boundary:
        """
        boundary conditions for the reaction

        The boundary conditions are a tuple where each degree of freedom is free to move
        unless the boundary has a 0 in that position
        """
        # if len(self._boundary) == 1:
        #     return self._boundary[0]
        return self._boundary

    @boundary.setter
    def boundary(self, value: Boundary) -> None:

        if not isinstance(value, Iterable):
            value = (value,)

        for dof in value:
            if dof not in (0, None):
                raise ValueError("invalid boundary condition, must be either None or 0")

        if all(map(lambda e: e is None, value)):
            # all boundary conditions for reaction are None
            warn(
                "Reaction with no restrictions does not effect results!",
                UserWarning,
            )
        self._boundary = value

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

        Raises:
            ValueError: when location is less than 0
            TypeError: when location is set to any non-numeric value
        """
        return self._location

    @location.setter
    @validation.is_numeric
    @validation.non_negative
    def location(self, location: float) -> None:
        # The location is overloading the location property in Forces so that
        # the reaction can be invalidated when the location is changed
        self.invalidate()
        self._location = location

    @property
    def value(self) -> tuple[Optional[float], Optional[float]]:
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

    def __eq__(self, other: Any) -> bool:

        if not isinstance(other, self.__class__):
            return False

        return (
            self.location == other.location
            and self.force == other.force
            and self.moment == other.moment
        )
