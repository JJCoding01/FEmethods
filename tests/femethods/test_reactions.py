import pytest

from femethods.reactions import FixedReaction, PinnedReaction, Reaction


@pytest.mark.parametrize(
    "reaction, name", ((PinnedReaction, "pinned"), (FixedReaction, "fixed"))
)
def test_reaction_name(reaction, name):
    r = reaction(0)
    assert r.name == name


@pytest.mark.parametrize("reaction", (PinnedReaction, FixedReaction))
def test_reaction_init(reaction):
    r = reaction(0)
    assert r.force is None
    assert r.moment is None


@pytest.mark.parametrize("invalid_type", (None, "str", (0, 0)))
def test_invalid_location_type(invalid_type):
    with pytest.raises(TypeError):
        Reaction(location=invalid_type)


def test_negative_location():
    with pytest.raises(ValueError):
        Reaction(location=-5)


@pytest.mark.parametrize("moment", (None, -100, 0, 100))
@pytest.mark.parametrize("force", (None, -100, 0, 100))
@pytest.mark.parametrize("location", (0, 10))
def test_reaction_value(location, force, moment):
    r = Reaction(location)
    r.force = force
    r.moment = moment
    assert r.value == (force, moment)


def test_reaction_value_invalidate():
    r = Reaction(0)
    r.force = 100
    r.moment = 15
    r.invalidate()
    assert r.value == (None, None), "reaction not invalidated"


def test_reaction_invalidated_when_moved():
    r = Reaction(0)
    r.force = 100
    r.moment = 200

    r.location = 10  # move reaction
    assert r.value == (None, None), "reaction not invalided"


@pytest.mark.parametrize(
    "reaction, bc", ((PinnedReaction, (0, None)), (FixedReaction, (0, 0)))
)
def test_reaction_boundary_conditions(reaction, bc):
    r = reaction(0)
    assert (
        r.boundary == bc
    ), "boundary conditions does not match expected value"


@pytest.mark.parametrize("location", (0, 10))
@pytest.mark.parametrize("force", (None, -10, 0, 10))
@pytest.mark.parametrize("moment", (None, -10, 0, 10))
def test_reaction_eq(location, force, moment):
    r1 = Reaction(location)
    r2 = Reaction(location)

    r1.force = force
    r1.moment = moment

    r2.force = force
    r2.moment = moment
    assert r1 == r2


@pytest.mark.parametrize("other", (None, 10, "str"))
def test_reaction_not_eq_type(other):
    assert Reaction(0) != other


@pytest.mark.parametrize("force", (None, -100, 0, 100))
@pytest.mark.parametrize("moment", (None, -100, 0, 100))
def test_reaction_not_eq_location(force, moment):
    r1 = Reaction(0)
    r2 = Reaction(10)

    r1.force = force
    r1.moment = moment

    r2.force = force
    r2.moment = moment
    assert r1 != r2


@pytest.mark.parametrize("location", (0, 100))
@pytest.mark.parametrize("moment", (None, -100, 0, 100))
def test_reaction_not_eq_force(location, moment):
    r1 = Reaction(location)
    r2 = Reaction(location)

    r1.force = 0
    r2.force = 10

    r1.moment = moment
    r2.moment = moment

    assert r1 != r2


@pytest.mark.parametrize("location", (0, 100))
@pytest.mark.parametrize("force", (None, -100, 0, 100))
def test_reaction_not_eq_moment(location, force):
    r1 = Reaction(location)
    r2 = Reaction(location)

    r1.force = force
    r2.force = force

    r1.moment = 0
    r2.moment = 10

    assert r1 != r2
