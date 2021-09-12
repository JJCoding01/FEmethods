from typing import Optional

from .__base import Load


class PointLoad(Load):
    """
    class specific to a point load
    """

    name = "point load"

    def __init__(self, magnitude: Optional[float], location: float):
        super().__init__(magnitude, location)
