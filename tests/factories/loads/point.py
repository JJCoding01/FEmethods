# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.loads import PointLoad


class PointLoadFactory(Factory):
    class Meta:
        model = PointLoad

    magnitude = 100
    location = 0
