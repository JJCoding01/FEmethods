# pylint: disable=missing-function-docstring
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
