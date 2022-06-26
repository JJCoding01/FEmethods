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


@pytest.mark.parametrize("value", [-2, -1, 0])
def test_max_element_length_value_invalid_value(value):
    with pytest.raises(ValueError):
        MeshFactory(max_element_length=value)


@pytest.mark.parametrize("value", ["string", [1, 2]])
def test_max_element_length_value_invalid_type(value):
    with pytest.raises(TypeError):
        MeshFactory(max_element_length=value)


@pytest.mark.parametrize("value", [None, 1, 5, 10, 15])
def test_max_element_length_value_valid(value):
    mesh = MeshFactory(max_element_length=value)
    assert mesh.max_element_length == value


@pytest.mark.parametrize("value", [-2, -1, 0])
def test_min_element_count_value_invalid_value(value):
    with pytest.raises(ValueError):
        MeshFactory(min_element_count=value)


@pytest.mark.parametrize("value", ["string", [1, 2]])
def test_min_element_count_value_invalid_type(value):
    with pytest.raises(TypeError):
        MeshFactory(min_element_count=value)


def test_min_element_count_value_none():
    mesh = MeshFactory(min_element_count=None)
    assert mesh.min_element_count is None


@pytest.mark.parametrize("value", [None, 1, 5, 10, 15])
def test_min_element_count_value_valid(value):
    mesh = MeshFactory(max_element_length=value)
    assert mesh.max_element_length == value


@pytest.mark.parametrize("max_allowed_length", [1, 5, 7, 10, 100])
def test_nodes_max_length(max_allowed_length):
    mesh = MeshFactory(
        length=10, locations=[0, 4, 10], max_element_length=max_allowed_length
    )
    lengths = np.diff(mesh.nodes)
    assert np.max(lengths) <= max_allowed_length


@pytest.mark.parametrize("min_required", [1, 5, 7, 10, 100])
def test_nodes_min_count(min_required):
    mesh = MeshFactory(length=10, locations=[0, 10], min_element_count=min_required)
    count = np.diff(mesh.nodes).size
    assert min_required <= count
