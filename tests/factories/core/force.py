# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.core import Force


class ForceFactory(Factory):
    class Meta:
        model = Force

    magnitude = 1_000
    location = 15
