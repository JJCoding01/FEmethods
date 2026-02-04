# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.loads import ConstantDistributedLoad


class ConstantDistributedLoadFactory(Factory):
    class Meta:
        model = ConstantDistributedLoad

    magnitude = 100
    start = 0
    stop = 10
