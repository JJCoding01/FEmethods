# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from factory import Factory

from femethods import Mesh


class MeshFactory(Factory):
    class Meta:
        model = Mesh

    length = 25
    locations = [10, 15]
    node_dof = 2
