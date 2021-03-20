from .base import BOUNDARY_CONDITIONS, Reaction


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
        self._boundary: BOUNDARY_CONDITIONS = (0, 0)
