# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import numpy as np
import pytest

from tests.factories import MeshFactory


@pytest.mark.parametrize("dof", (-5, -4, 0, 3.25))
def test_mesh_node_dof_invalid_number(dof):
    with pytest.raises(ValueError):
        MeshFactory(node_dof=dof)


@pytest.mark.parametrize("dof", (None, "1", []))
def test_mesh_node_dof_invalid_type(dof):
    with pytest.raises(TypeError):
        MeshFactory(node_dof=dof)


@pytest.mark.parametrize("dof", (2, 4, 5))
def test_mesh_node_dof_valid_number(dof):
    mesh = MeshFactory(node_dof=dof)
    assert mesh.node_dof == dof


@pytest.mark.parametrize("length", (20, 25))
@pytest.mark.parametrize("locations", ([1, 5, 7], [15, 12, 5], [3, 7, 10, 15]))
def test_mesh_nodes(length, locations):
    expected_nodes = set(locations)
    expected_nodes.add(0)
    expected_nodes.add(length)
    expected_nodes = sorted(expected_nodes)

    mesh = MeshFactory(length=length, locations=locations)
    assert expected_nodes == mesh.nodes


@pytest.mark.parametrize("node_dof", (1, 2, 3))
@pytest.mark.parametrize("locations", ([3], [3, 10], [5, 10, 15], [5, 10, 15, 20]))
def test_mesh_dof(node_dof, locations):
    mesh = MeshFactory(length=25, locations=locations, node_dof=node_dof)

    # note, add 2 to account for ends
    expected_dof = (len(locations) + 2) * node_dof
    assert mesh.dof == expected_dof


@pytest.mark.parametrize("total_length", [25, 35])
@pytest.mark.parametrize("locations", ([5, 10], [5, 10, 15], [5, 10, 15, 20]))
def test_mesh_lengths(total_length, locations):
    mesh = MeshFactory(length=total_length, locations=locations)

    locations.append(0)
    locations.append(total_length)
    locations = sorted(set(locations))
    expected_lengths = np.diff(locations)

    assert np.allclose(expected_lengths, mesh.lengths)


def test_nodes_read_only():
    mesh = MeshFactory()
    with pytest.raises(AttributeError):
        mesh.nodes = "Mesh nodes property is read-only"


def test_dof_read_only():
    mesh = MeshFactory()
    with pytest.raises(AttributeError):
        mesh.dof = "Mesh dof should be read-only"


def test_lengths_read_only():
    mesh = MeshFactory()
    with pytest.raises(AttributeError):
        mesh.lengths = "Mesh element lengths are read-only"
