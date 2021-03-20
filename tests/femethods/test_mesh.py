import pytest

from femethods.loads import PointLoad
from femethods.mesh import Mesh
from femethods.reactions import FixedReaction

LOADS = [PointLoad(magnitude=-1000, location=15)]
REACTIONS = [FixedReaction(0)]
LENGTH = 25


@pytest.fixture
def mesh():
    return Mesh(LENGTH, LOADS, REACTIONS, dof=2)


def test_mesh_properties(mesh):
    # there should be a node at the start and end of the beam, as well as a
    # node for any loads
    assert mesh.nodes == [0, 15, 25], "Mesh nodes do not match expected"
    assert mesh.dof == 6, "Wrong number of global degrees-of-freedom"
    assert mesh.lengths == [
        15,
        10,
    ], "Mesh elements do not have expected lengths"
    assert mesh.num_elements == 2, "Mesh element count does not match"
    assert mesh.num_elements == len(mesh.lengths)

    with pytest.raises(AttributeError):
        mesh.nodes = "Mesh nodes property is read-only"
    with pytest.raises(AttributeError):
        mesh.dof = "Mesh dof should be read-only"
    with pytest.raises(AttributeError):
        mesh.lengths = "Mesh element lengths are read-only"
