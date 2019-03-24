import pytest

from femethods.loads import PointLoad


def test_point_load():
    p = PointLoad(magnitude=-5, location=25)

    assert p.magnitude == -5, 'PointLoad magnitude does not match input'
    assert p.location == 25, 'PointLoad location does not match input'

    # verify parameters are updated successfully
    p.magnitude = -15
    p.location = 30
    assert p.magnitude == -15, 'PointLoad magwas not updated'
    assert p.location == 30, 'PointLoad location was not updated'

    p1 = PointLoad(magnitude=-2, location=10)
    p2 = PointLoad(magnitude=-8, location=20)
    p3 = PointLoad(magnitude=-1, location=10)
    assert p1 + p2 == PointLoad(magnitude=-10, location=18)

    p1 = PointLoad(magnitude=10, location=10)
    p2 = PointLoad(magnitude=5, location=20)
    p3 = PointLoad(magnitude=5, location=0)
    assert p1 - p2 == p3
    assert p3 + p2 == p1

    # Check bad input
    with pytest.raises(ValueError):
        PointLoad(magnitude=-3, location=-10)  # location must be positive
        # or 0

    with pytest.raises(TypeError):
        PointLoad(magnitude=-3, location='a string')  # location must be a
        # number

    with pytest.raises(TypeError):
        PointLoad(magnitude='a string', location=10)  # magnitude must be a
        # number
