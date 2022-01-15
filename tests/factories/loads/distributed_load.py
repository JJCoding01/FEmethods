# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods.loads import DistributedLoad


class DistributedLoadFactory(Factory):
    class Meta:
        model = DistributedLoad

    func = lambda x: 1
    start = 2
    stop = 12
    args = ()
