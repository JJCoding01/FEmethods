# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.loads import Load


class LoadForFactory(Load):

    def fe(self, a, b):
        pass


class LoadFactory(Factory):
    class Meta:
        model = LoadForFactory

    magnitude = 100
    location = 0
    fm_factor = (0, 1)
