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


def test_mesh_nodes(mesh):
    expected_nodes = [0, 15, 25]
    assert expected_nodes == mesh.nodes


def test_mesh_dof(mesh):
    assert mesh.dof == 6


def test_mesh_lengths(mesh):
    expected_lengths = [15, 10]
    assert expected_lengths == mesh.lengths


def test_element_count(mesh):
    assert mesh.num_elements == 2, "Mesh element count does not match"
    assert mesh.num_elements == len(mesh.lengths)


def test_nodes_read_only(mesh):
    with pytest.raises(AttributeError):
        mesh.nodes = "Mesh nodes property is read-only"


def test_dof_read_only(mesh):
    with pytest.raises(AttributeError):
        mesh.dof = "Mesh dof should be read-only"


def test_lengths_read_only(mesh):
    with pytest.raises(AttributeError):
        mesh.lengths = "Mesh element lengths are read-only"
