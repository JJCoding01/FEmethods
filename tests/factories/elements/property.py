# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.elements.__base import Properties


class PropertyFactory(Factory):
    class Meta:
        model = Properties

    length = 25
    E = 29e6
    Ixx = 231
