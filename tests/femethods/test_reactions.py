import pytest

from femethods.reactions import FixedReaction, PinnedReaction, Reaction


def test_reaction_parameters():
    r = Reaction(0)

    assert r.force is None, "Reaction should not have force before solving"
    assert r.moment is None, "Reaction should not have moment before solving"
    assert r.value == (None, None), "Reaction value initialized incorrectly"

    r.force = 10
    r.moment = 20
    assert r.force == 10, "Reaction force not set properly"
    assert r.moment == 20, "Reaction moment not set properly"
    assert r.value == (10, 20), "value to returning (force, moment)"

    # check that when the reaction is invalidated, all calculated values are removed
    r.invalidate()
    assert r.location == 0
    assert r.value == (None, None), "reaction not invalidated"

    r1 = Reaction(0)
    r1.force = 10
    r1.moment = 20
    r2 = Reaction(0)
    r2.force = 10
    r2.moment = 20
    assert r1 == r2
    assert not r1 == Reaction(10)
    assert (
        not r1 == "10"
    ), "Reaction should never equal anything but a reaction"

    # verify that changing the location of a calculated reaction,
    # it is automatically invalidated
    assert r1.value == (10, 20)
    r1.location = 10
    assert r1.location == 10, "location not updated"
    assert r1.value == (None, None), "Reaction not invalidated when moved"
    # check for bad input
    with pytest.raises(ValueError):
        Reaction(-5)

    with pytest.raises(TypeError):
        Reaction("some value")

    # check that invalidating a reaction removes calculated
    # values
    r = Reaction(5)
    r.force = 15
    r.moment = 25
    assert r.value == (15, 25), "Reaction values do not match expected"
    r.invalidate()
    assert r.value == (None, None), "Reaction values where not invalidated"


def test_reaction_types():
    pr = PinnedReaction(0)
    fr = FixedReaction(0)

    assert pr.boundary == (
        0,
        None,
    ), "PinnedReaction only has one degree of freedom"
    assert fr.boundary == (
        0,
        0,
    ), "FixedReaction does not have any degrees of freedom"
