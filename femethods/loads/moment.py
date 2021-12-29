from .__base import Load


class MomentLoad(Load):
    """
    class specific to a moment load
    """

    name = "moment load"

    def __init__(self, magnitude, location):
        super().__init__(magnitude, location)
