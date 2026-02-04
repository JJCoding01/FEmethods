# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.reactions import Reaction


class ReactionFactory(Factory):
    class Meta:
        model = Reaction

    location = 15
    boundary = (None, 0)
