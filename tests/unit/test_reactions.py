# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import pytest

from tests.factories import ReactionFactory


@pytest.mark.parametrize("location", (0, 5, 10))
def test_reaction_location_valid_init(location):
    reaction = ReactionFactory(location=location)
    assert reaction.location == location


def test_reaction_location_invalid_negative():
    with pytest.raises(ValueError):
        ReactionFactory(location=-5)


@pytest.mark.parametrize("invalid_location", (None, "str", [0]))
def test_reaction_location_invalid(invalid_location):
    with pytest.raises(TypeError):
        ReactionFactory(location=invalid_location)


@pytest.mark.parametrize("bc1", (None, 0))
def test_reaction_boundary_valid_len1(bc1):
    if bc1 is None:
        pytest.skip("skip None boundary")
    reaction = ReactionFactory(boundary=bc1)
    assert reaction.boundary == bc1


@pytest.mark.parametrize("bc1", (None, 0))
@pytest.mark.parametrize("bc2", (None, 0))
def test_reaction_boundary_valid_len2(bc1, bc2):
    boundary = (bc1, bc2)
    if boundary == (None, None):
        pytest.skip("skip (None, None) boundary")
    reaction = ReactionFactory(boundary=boundary)
    assert reaction.boundary == boundary


@pytest.mark.parametrize("bc1", (None, 0))
@pytest.mark.parametrize("bc2", (None, 0))
@pytest.mark.parametrize("bc3", (None, 0))
def test_reaction_boundary_valid_len3(bc1, bc2, bc3):
    boundary = (bc1, bc2, bc3)
    if boundary == (None, None, None):
        pytest.skip("skip (None, None, None) boundary")
    reaction = ReactionFactory(boundary=boundary)
    assert reaction.boundary == boundary


@pytest.mark.parametrize("bc1", ("str", 1, 2))
def test_reaction_boundary_invalid_len1(bc1):
    with pytest.raises(ValueError):
        ReactionFactory(boundary=bc1)


@pytest.mark.parametrize("bc1", (None, "str", 1, 2))
@pytest.mark.parametrize("bc2", (None, "str", 1, 2))
def test_reaction_boundary_invalid_len2(bc1, bc2):
    boundary = (bc1, bc2)
    if boundary == (None, None):
        pytest.skip("skip (None, None) boundary")
    with pytest.raises(ValueError):
        ReactionFactory(boundary=boundary)


@pytest.mark.parametrize("bc1", (None, "str", 1, 2))
@pytest.mark.parametrize("bc2", (None, "str", 1, 2))
@pytest.mark.parametrize("bc3", (None, "str", 1, 2))
def test_reaction_boundary_invalid_len3(bc1, bc2, bc3):
    boundary = (bc1, bc2, bc3)
    if boundary == (None, None, None):
        pytest.skip("skip (None, None, None) boundary")
    with pytest.raises(ValueError):
        ReactionFactory(boundary=boundary)


@pytest.mark.parametrize("boundary", (None, (None, None), (None, None, None)))
def test_reaction_boundary_useless_none(boundary):
    with pytest.warns(UserWarning):
        ReactionFactory(boundary=boundary)


@pytest.mark.parametrize("force", (-100, 0, 100))
def test_reaction_force(force):
    reaction = ReactionFactory()
    reaction.force = force
    assert reaction.force == force


@pytest.mark.parametrize("moment", (-150, 0, 150))
def test_reaction_moment(moment):
    reaction = ReactionFactory()
    reaction.moment = moment
    assert reaction.moment == moment


@pytest.mark.parametrize("force", (-200, 0, 200))
@pytest.mark.parametrize("moment", (-150, 0, 150))
def test_reaction_value(force, moment):
    reaction = ReactionFactory()
    reaction.force = force
    reaction.moment = moment
    assert reaction.value == (force, moment)


@pytest.mark.parametrize("location", (0, 15, 20))
def test_reaction_invalidate_on_location_update(location):
    reaction = ReactionFactory()
    reaction.force = 100
    reaction.moment = 150
    assert reaction.value == (100, 150)

    # update location
    reaction.location = location

    # assert the force/moment was invalidated
    assert reaction.value == (None, None)


def test_reaction_invalidate_manual():
    r = ReactionFactory()
    r.force = 100
    r.moment = 15
    assert r.value == (100, 15)
    r.invalidate()
    assert r.value == (None, None), "reaction not invalidated"


@pytest.mark.parametrize("location", (0, 10))
@pytest.mark.parametrize("force", (None, -10, 0, 10))
@pytest.mark.parametrize("moment", (None, -10, 0, 10))
def test_reaction_eq(location, force, moment):
    r1 = ReactionFactory(location=location)
    r2 = ReactionFactory(location=location)

    r1.force = force
    r1.moment = moment

    r2.force = force
    r2.moment = moment
    assert r1 == r2


@pytest.mark.parametrize("other", (None, 10, "str"))
def test_reaction_not_eq_type(other):
    assert ReactionFactory() != other


@pytest.mark.parametrize("force", (None, -100, 0, 100))
@pytest.mark.parametrize("moment", (None, -100, 0, 100))
def test_reaction_not_eq_location(force, moment):
    r1 = ReactionFactory(location=0)
    r2 = ReactionFactory(location=10)

    r1.force = force
    r1.moment = moment

    r2.force = force
    r2.moment = moment
    assert r1 != r2


@pytest.mark.parametrize("location", (0, 100))
@pytest.mark.parametrize("moment", (None, -100, 0, 100))
def test_reaction_not_eq_force(location, moment):
    r1 = ReactionFactory(location=location)
    r2 = ReactionFactory(location=location)

    r1.force = 0
    r2.force = 10

    r1.moment = moment
    r2.moment = moment

    assert r1 != r2


@pytest.mark.parametrize("location", (0, 100))
@pytest.mark.parametrize("force", (None, -100, 0, 100))
def test_reaction_not_eq_moment(location, force):
    r1 = ReactionFactory(location=location)
    r2 = ReactionFactory(location=location)

    r1.force = force
    r2.force = force

    r1.moment = 0
    r2.moment = 10

    assert r1 != r2
