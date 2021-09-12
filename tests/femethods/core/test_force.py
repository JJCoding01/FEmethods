import pytest

from femethods.core import Force


def test_init_force():
    force = Force(magnitude=500, location=50)

    assert force.magnitude == 500
    assert force.location == 50


@pytest.mark.parametrize("length", ("non-number", None, -5))
def test_init_force_invalid_location(length):
    # noinspection PyTypeChecker
    with pytest.raises((ValueError, TypeError)):
        Force(0, location=length)


@pytest.mark.parametrize(
    "force",
    [
        Force(250, 15),
        Force(250 * 15 / 10, 10),
        Force(250 * 15 / 25, 25),
    ],
)
def test_force_eq(force):
    base_force = Force(250, 15)

    assert base_force == force


@pytest.mark.parametrize(
    "force1, force2",
    [
        (Force(250, 15), Force(250, 0)),
        (Force(250, 15), Force(250, 10)),
        (Force(250, 15), Force(None, 0)),
        (Force(None, 15), Force(None, 0)),
        (Force(250, 15), "not a force"),
    ],
)
def test_force_ne(force1, force2):
    assert force1 != force2


@pytest.mark.parametrize("force, location", [(500, 10), (250, 50)])
def test_force_add(force, location):
    force1 = Force(250, 25)
    force2 = Force(force, location)

    force_net = force1 + force2

    f1 = force1.magnitude
    f2 = force2.magnitude

    x1 = force1.location
    x2 = force2.location

    x = (f1 * x1 + f2 * x2) / (f1 + f2)

    force_expected = Force(f1 + f2, x)

    assert force_expected == force_net


def test_force_add_invalid():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        Force(250, 25) + 50
