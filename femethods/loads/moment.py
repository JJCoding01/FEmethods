from .base import Load


class MomentLoad(Load):
    """
    class specific to a moment load
    """

    name = "moment load"

    def __init__(self, magnitude: float, location: float):
        super().__init__(magnitude, location)
