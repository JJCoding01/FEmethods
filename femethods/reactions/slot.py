from .__base import Reaction


class SlotReaction(Reaction):
    """
    A SlotReaction does not allow any angular displacement

    A SlotReaction resists moments, but vertical displacements are allowed.
    Only the angle is constrained and must be zero at the reaction point.

    Parameters:
        location (:obj:`float`): the axial location of the reaction along the
                                 length of the beam

    Attributes:
        name (:obj:`str`): short name of the reaction (slot). Used internally

    .. warning:: The **name** attribute is used internally.
                 **Do not change this value!**
    """

    name = "slot"

    def __init__(self, location):
        # allow vertical displacement but no rotation
        super().__init__(location, boundary=(None, 0))
