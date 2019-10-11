import pytest

from femethods.loads import MomentLoad, PointLoad


def check_load(load):
    p = load(magnitude=-5, location=25)

    assert p.magnitude == -5, f"{load.__name__} magnitude does not match input"
    assert p.location == 25, f"{load.__name__} location does not match input"

    # verify parameters are updated successfully
    p.magnitude = -15
    p.location = 30
    assert p.magnitude == -15, f"{load.__name__} magnitude was not updated"
    assert p.location == 30, f"{load.__name__} location was not updated"

    # Check load arithmetic
    p1 = load(magnitude=-2, location=10)
    p2 = load(magnitude=-8, location=20)
    assert p1 + p2 == load(magnitude=-10, location=18)

    p1 = load(magnitude=10, location=10)
    p2 = load(magnitude=5, location=20)
    p3 = load(magnitude=5, location=0)
    assert p1 - p2 == p3
    assert p3 + p2 == p1

    # Check bad input
    with pytest.raises(ValueError):
        load(magnitude=-3, location=-10)  # location must be positive
        # or 0

    with pytest.raises(TypeError):
        load(magnitude=-3, location="a string")  # location must be a number

    with pytest.raises(TypeError):
        load(magnitude="a string", location=10)  # magnitude must be a number


def test_PointLoad_equality():
    p1 = PointLoad(magnitude=10, location=30)
    p2 = PointLoad(magnitude=10, location=30)
    p3 = PointLoad(magnitude=12, location=20)
    p4 = PointLoad(magnitude=None, location=20)

    assert p1 == p1, "loads should equal itself"
    assert p2 == p2, "loads should equal itself"
    assert p3 == p3, "loads should equal itself"
    assert p4 == p4, "loads should equal itself"

    assert p1 == p2, "equivalent loads should be equal"
    assert p1 != p3, "different loads should not be equal"
    assert p1 != p4, "different loads should not be equal"

    assert p1 != "not a load", "load should not equal something that is not a load"


def test_loads():
    check_load(PointLoad)
    check_load(MomentLoad)
