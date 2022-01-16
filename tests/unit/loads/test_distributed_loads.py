# pylint: disable=missing-function-docstring
import numpy as np
import pytest

from tests.factories import DistributedLoadFactory


@pytest.mark.parametrize("func", [lambda x: x, lambda x: 2 * x])
def test_distributed_load_func_valid(func):
    dload = DistributedLoadFactory(func=func)
    assert dload.func is func


@pytest.mark.parametrize("func", [10, None])
def test_distributed_load_func_invalid(func):
    with pytest.raises(TypeError):
        _ = DistributedLoadFactory(func=func)


@pytest.mark.parametrize("start", [0, 5, 10])
def test_distributed_load_start_valid_init(start):
    dload = DistributedLoadFactory(start=start, stop=20)
    assert dload.start == start


@pytest.mark.parametrize("stop", [5, 10, 15])
def test_distributed_load_stop_valid_init(stop):
    dload = DistributedLoadFactory(start=0, stop=stop)
    assert dload.stop == stop


@pytest.mark.parametrize("start", [0, 5, 10])
def test_distributed_load_start_valid_update(start):
    dload = DistributedLoadFactory(start=0, stop=20)
    dload.start = start
    assert dload.start == start


@pytest.mark.parametrize("stop", [5, 10, 15])
def test_distributed_load_stop_valid_update(stop):
    dload = DistributedLoadFactory(start=0, stop=25)
    dload.stop = stop
    assert dload.stop == stop


@pytest.mark.parametrize("start", [5, 10])
def test_distributed_load_start_after_stop_invalid_init(start):
    with pytest.raises(ValueError):
        _ = DistributedLoadFactory(start=start, stop=5)


@pytest.mark.parametrize("stop", [-1, 5, 10])
def test_distributed_load_stop_before_start_invalid_init(stop):
    with pytest.raises(ValueError):
        _ = DistributedLoadFactory(start=10, stop=stop)


@pytest.mark.parametrize("start", [-1, 5, 10])
def test_distributed_load_start_after_stop_invalid_update(start):
    dload = DistributedLoadFactory(start=0, stop=5)
    with pytest.raises(ValueError):
        dload.start = start


@pytest.mark.parametrize("stop", [-1, 5, 10])
def test_distributed_load_stop_before_start_invalid_update(stop):
    dload = DistributedLoadFactory(start=10, stop=15)
    with pytest.raises(ValueError):
        dload.stop = stop


@pytest.mark.parametrize("start", [None, "str", (1,)])
def test_distributed_load_start_invalid_type(start):
    with pytest.raises(TypeError):
        _ = DistributedLoadFactory(start=start)


@pytest.mark.parametrize("stop", [None, "str", (1,)])
def test_distributed_load_stop_invalid_type(stop):
    with pytest.raises(TypeError):
        _ = DistributedLoadFactory(stop=stop)


@pytest.mark.parametrize("args", [(), (1, 2)])
def test_distributed_load_args_valid(args):
    dload = DistributedLoadFactory(args=args)
    assert dload.args == args


@pytest.mark.parametrize(
    "func",
    [
        lambda x, y=0, z=0: x + y + z,
        lambda x, y=0, z=0: x * y * z,
        lambda x, y=0, z=0: 2 * x + 3 * y + 4 * z,
    ],
)
@pytest.mark.parametrize("args", [(), (1,), (1, 2)])
@pytest.mark.parametrize("x", [0, 5, 7])
def test_distributed_load_magnitude(func, args, x):
    dload = DistributedLoadFactory(func=func, args=args)
    expected_magnitude = func(x, *args)
    assert expected_magnitude == dload.magnitude(x)


@pytest.mark.parametrize("n", (2, 4, 16))
@pytest.mark.parametrize("a", (0, 4, 6))
@pytest.mark.parametrize("b", (8, 16, 20))
@pytest.mark.parametrize("w", (100, 250))
def test_distributed_load_equiv_mag_multi_node(n, a, b, w):

    dload = DistributedLoadFactory(func=lambda x, *args: w, start=a, stop=b)

    # get an array of nodes that includes 0, a, b, 20, where 0 and 20 are the start and
    # end of the beam, and a and b are the start and end of the distributed load
    nodes = np.linspace(a, b, num=n, endpoint=True)
    nodes = np.append(nodes, [0, 20])
    nodes = np.unique(nodes)
    nodes.sort()

    # note the verbose conditional is to simulate an exclusive or
    if (a == 0 and not b == 20) or (not a == 0 and b == 20):
        # case where one node (start or ending) is at either the start or end of beam
        assert len(nodes) == n + 1
    elif a == 0 and b == 20:
        # case where load is applied to entire beam
        assert len(nodes) == n
    else:
        # case where both the start and end of the beam are not loaded
        assert len(nodes) == n + 2

    # get the locations of the expected loads. They are going to be midway between each
    # node where the load is applied
    expected = []
    lengths = np.diff(nodes)
    for node, length in zip(nodes[:-1], lengths):
        if a <= node <= b:
            expected.append(w * length)
        if node + length == b:
            break
    actual = dload.equivalent_magnitude(nodes)
    if len(expected) == 1:
        actual = [actual]
    assert np.allclose(actual, expected, atol=1.0e-8)


@pytest.mark.parametrize("n", (2, 4, 16))
@pytest.mark.parametrize("a", (0, 4, 6))
@pytest.mark.parametrize("b", (8, 16, 20))
def test_distributed_load_centroid_loc_multi_node(n, a, b):
    dload = DistributedLoadFactory(func=lambda x, *args: 100, start=a, stop=b)

    # get an array of nodes that includes 0, a, b, 20, where 0 and 20 are the start and
    # end of the beam, and a and b are the start and end of the distributed load
    nodes = np.linspace(a, b, num=n, endpoint=True)
    nodes = np.append(nodes, [0, 20])
    nodes = np.unique(nodes)
    nodes.sort()

    # note the verbose conditional is to simulate an exclusive or
    if (a == 0 and not b == 20) or (not a == 0 and b == 20):
        # case where one node (start or ending) is at either the start or end of beam
        assert len(nodes) == n + 1
    elif a == 0 and b == 20:
        # case where load is applied to entire beam
        assert len(nodes) == n
    else:
        # case where both the start and end of the beam are not loaded
        assert len(nodes) == n + 2

    # get the locations of the expected loads. They are going to be midway between each
    # node where the load is applied
    expected = []
    lengths = np.diff(nodes)
    for node, length in zip(nodes[:-1], lengths):
        if a <= node <= b:
            expected.append(node + length / 2)
        if node + length == b:
            break
    assert np.allclose(dload.centroid_location(nodes), expected, atol=1.0e-8)


@pytest.mark.parametrize("nodes", ((0, 12), (0, 5, 9, 11), (1, 10), (1, 5, 10)))
def test_distributed_load_invalid_mesh_magnitude(nodes):
    dload = DistributedLoadFactory(start=0, stop=10)

    with pytest.raises(ValueError):
        dload.equivalent_magnitude(nodes)


@pytest.mark.parametrize("nodes", ((0, 12), (0, 5, 9, 11), (1, 10), (1, 5, 10)))
def test_distributed_load_invalid_mesh_location(nodes):
    dload = DistributedLoadFactory(start=0, stop=10)

    with pytest.raises(ValueError):
        dload.centroid_location(nodes)


def test_distributed_load_invalid_mesh_order_magnitude():
    dload = DistributedLoadFactory(start=0, stop=10)

    with pytest.raises(ValueError):
        dload.equivalent_magnitude((10, 0))


def test_distributed_load_invalid_mesh_order_location():
    dload = DistributedLoadFactory(start=0, stop=10)

    with pytest.raises(ValueError):
        dload.centroid_location((10, 0))
