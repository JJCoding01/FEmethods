import pytest

from femethods.loads import MomentLoad, PointLoad


@pytest.mark.parametrize(
    "load, name", ((PointLoad, "point load"), (MomentLoad, "moment load"))
)
def test_load_name(load, name):
    p = load(0, 0)
    assert p.name == name
