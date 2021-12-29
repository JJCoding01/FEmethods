# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import pytest

from tests.factories import ForceFactory


def test_init_force_magnitude():
    force = ForceFactory(magnitude=500)
    assert force.magnitude == 500


def test_init_force_location():
    force = ForceFactory(location=10)
    assert force.location == 10


def test_force_update_magnitude():
    force = ForceFactory(magnitude=-5)
    force.magnitude = -100
    assert force.magnitude == -100


def test_force_update_location():
    force = ForceFactory(location=15)
    force.location = 25
    assert force.location == 25


@pytest.mark.parametrize(
    "force",
    [
        ForceFactory(magnitude=250, location=15),
        ForceFactory(magnitude=250 * 15 / 10, location=10),
        ForceFactory(magnitude=250 * 15 / 25, location=25),
    ],
)
def test_force_eq(force):
    base_force = ForceFactory(magnitude=250, location=15)

    assert base_force == force


@pytest.mark.parametrize(
    "force1, force2",
    [
        (
            ForceFactory(magnitude=250, location=15),
            ForceFactory(magnitude=250, location=0),
        ),
        (
            ForceFactory(magnitude=250, location=15),
            ForceFactory(magnitude=250, location=10),
        ),
        (
            ForceFactory(magnitude=250, location=15),
            ForceFactory(magnitude=None, location=0),
        ),
        (
            ForceFactory(magnitude=None, location=15),
            ForceFactory(magnitude=None, location=0),
        ),
        (ForceFactory(magnitude=250, location=15), "not a force"),
    ],
)
def test_force_ne(force1, force2):
    assert force1 != force2


@pytest.mark.parametrize("force, location", [(500, 10), (250, 50)])
def test_force_add(force, location):
    force1 = ForceFactory(magnitude=250, location=25)
    force2 = ForceFactory(magnitude=force, location=location)

    force_net = force1 + force2

    f1 = force1.magnitude
    f2 = force2.magnitude

    x1 = force1.location
    x2 = force2.location

    x = (f1 * x1 + f2 * x2) / (f1 + f2)

    force_expected = ForceFactory(magnitude=f1 + f2, location=x)

    assert force_expected == force_net


def test_force_add_pair():
    p1 = ForceFactory(magnitude=-2, location=10)
    p2 = ForceFactory(magnitude=-8, location=20)
    assert p1 + p2 == ForceFactory(magnitude=-10, location=18)


def test_force_add_invalid():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        ForceFactory(magnitude=250, location=25) + 50


@pytest.mark.parametrize("force, location", [(500, 10), (100, 50)])
def test_force_sub(force, location):
    force1 = ForceFactory(magnitude=250, location=25)
    force2 = ForceFactory(magnitude=force, location=location)

    force_net = force1 - force2

    f1 = force1.magnitude
    f2 = force2.magnitude

    x1 = force1.location
    x2 = force2.location

    x = (f1 * x1 - f2 * x2) / (f1 - f2)

    force_expected = ForceFactory(magnitude=f1 - f2, location=x)

    assert force_expected == force_net


def test_force_arithmetic():
    p1 = ForceFactory(magnitude=10, location=10)
    p2 = ForceFactory(magnitude=5, location=20)
    p3 = ForceFactory(magnitude=5, location=0)
    assert p1 - p2 == p3
    assert p3 + p2 == p1
