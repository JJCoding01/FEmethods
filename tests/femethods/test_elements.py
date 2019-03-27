import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


def test_beam_params():

    reactions = [PinnedReaction(x) for x in [1, 120]]
    loads = [PointLoad(magnitude=-120, location=50)]
    beam = Beam(length=120, loads=loads, reactions=reactions, E=29e6, Ixx=350)

    # check parameters of the beam to ensure they match the input
    assert beam.length == 120, "beam length does not match input"
    assert beam.E == 29e6, "Young's modulus does not match input"
    assert beam.Ixx == 350, "area moment of inertia does not match input"

    # update parameters and verify update was successful
    beam.length = 130
    beam.E = 29.9e6
    beam.Ixx = 345
    assert beam.length == 130, "beam length does not match input"
    assert beam.E == 29.9e6, "Young's modulus does not match input"
    assert beam.Ixx == 345, "area moment of inertia does not match input"


def test_reaction_load_warnings():
    reactions = [PinnedReaction(x) for x in [0, 120]]
    loads = [PointLoad(magnitude=-120, location=50)]
    #
    with pytest.raises(TypeError):
        # create a beam where the reactions are not a list
        Beam(120, reactions=PinnedReaction(0), loads=loads)
    with pytest.raises(TypeError):
        # create a beam where the loads are not a list
        Beam(120, reactions=reactions, loads=PointLoad(-10, 5))

    with pytest.raises(ValueError):
        # beam length must be positive
        Beam(-10, reactions=reactions, loads=loads)
    with pytest.raises(TypeError):
        # beam length must be a number
        Beam("length is not a number", reactions=reactions, loads=loads)


def test_load_positions():
    """check that load positions are adjusted when they line up with the
    reaction position
    """

    reactions = [PinnedReaction(x) for x in [0, 50, 100]]
    loads = [PointLoad(-100, x) for x in [0, 50, 100]]

    for load, reaction in zip(loads, reactions):
        assert load.location == reaction.location

    beam = Beam(100, loads=loads, reactions=reactions)

    for load, reaction in zip(beam.loads, beam.reactions):
        assert load.location != reaction.location
