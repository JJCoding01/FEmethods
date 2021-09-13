import pytest

from femethods.core import Force


def test_init_force():
    force = Force(magnitude=500, location=50)

    assert force.magnitude == 500
    assert force.location == 50


def test_force_update():
    p = Force(magnitude=-5, location=25)

    p.magnitude = -100
    p.location = 30
    assert p.magnitude == -100
    assert p.location == 30


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


def test_force_add_pair():
    p1 = Force(magnitude=-2, location=10)
    p2 = Force(magnitude=-8, location=20)
    assert p1 + p2 == Force(magnitude=-10, location=18)


def test_force_add_invalid():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        Force(250, 25) + 50


@pytest.mark.parametrize("force, location", [(500, 10), (100, 50)])
def test_force_sub(force, location):
    force1 = Force(250, 25)
    force2 = Force(force, location)

    force_net = force1 - force2

    f1 = force1.magnitude
    f2 = force2.magnitude

    x1 = force1.location
    x2 = force2.location

    x = (f1 * x1 - f2 * x2) / (f1 - f2)

    force_expected = Force(f1 - f2, x)

    assert force_expected == force_net


def test_force_arithmetic():
    p1 = Force(magnitude=10, location=10)
    p2 = Force(magnitude=5, location=20)
    p3 = Force(magnitude=5, location=0)
    assert p1 - p2 == p3
    assert p3 + p2 == p1
