# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.loads import MomentLoad


class MomentLoadFactory(Factory):
    class Meta:
        model = MomentLoad

    magnitude = 100
    location = 0
