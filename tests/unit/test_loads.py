# pylint: disable=missing-function-docstring

import numpy as np
import pytest

from femethods.loads import MomentLoad, PointLoad
from tests.factories import LoadFactory, MomentLoadFactory, PointLoadFactory


@pytest.mark.parametrize("force", [0.25, 0.50, 0.75, 1.00])
@pytest.mark.parametrize("moment", [0.25, 0.50, 0.75, 1.00])
def test_load_force_moment_factor_valid(force, moment):
    load = LoadFactory(fm_factor=(force, moment))
    expected = np.array([force, moment])

    assert np.all(load.fm_factor == expected)


@pytest.mark.parametrize("type_func", [list, tuple, np.array])
def test_load_force_moment_factor_valid_type(type_func):
    factor = type_func([0.25, 0.75])
    load = LoadFactory(fm_factor=factor)
    expected = np.array([0.25, 0.75])
    assert np.all(load.fm_factor == expected)


@pytest.mark.parametrize("factor", [1, None, {"force": 0, "moment": 1}, True, "string"])
def test_load_force_moment_factor_invalid_type(factor):
    with pytest.raises(TypeError):
        LoadFactory(fm_factor=factor)


@pytest.mark.parametrize("factor", [(0,), (0, 1, 2)])
def test_load_force_moment_factor_invalid_len(factor):
    with pytest.raises(ValueError):
        LoadFactory(fm_factor=factor)


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("magnitude", [125, 300, 575])
@pytest.mark.parametrize("force", [0.25, 1.00])
@pytest.mark.parametrize("moment", [0.25, 1.00])
def test_load_index(index, magnitude, force, moment):
    expected_percentage = (force, moment)
    load = LoadFactory(magnitude=magnitude, fm_factor=expected_percentage)
    assert load[index] == magnitude * expected_percentage[index]


@pytest.mark.parametrize("index", [2, 3])
def test_load_index_invalid(index):
    load = LoadFactory()
    with pytest.raises(IndexError):
        _ = load[index]


@pytest.mark.parametrize(
    "load, name", ((PointLoad, "point load"), (MomentLoad, "moment load"))
)
def test_load_name(load, name):
    p = load(0, 0)
    assert p.name == name


@pytest.mark.parametrize("magnitude", [5, 75, 100])
def test_point_load_no_moment(magnitude):
    load = PointLoadFactory(magnitude=magnitude)
    assert load[0] == magnitude
    assert load.magnitude == load[0]
    assert load[1] == 0


@pytest.mark.parametrize("magnitude", [5, 75, 100])
def test_moment_load_no_force(magnitude):
    load = MomentLoadFactory(magnitude=magnitude)
    assert load[1] == magnitude
    assert load.magnitude == load[1]
    assert load[0] == 0
