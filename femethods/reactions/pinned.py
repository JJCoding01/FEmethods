from .base import BOUNDARY_CONDITIONS, Reaction


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
        self._boundary: BOUNDARY_CONDITIONS = (0, None)
