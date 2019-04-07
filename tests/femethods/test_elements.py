import pytest

from femethods.elements import Beam
from femethods.loads import MomentLoad, PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


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


def test_invalid_load_placement():
    reactions = [PinnedReaction(x) for x in [0, 50, 100]]
    loads = [PointLoad(-100, x) for x in [0, 50, 100]]

    with pytest.warns(UserWarning):
        beam = Beam(100, loads=loads, reactions=reactions)

    for load, reaction in zip(beam.loads, beam.reactions):
        assert load.location != reaction.location, \
            'moved load is still the same as a reaction'


def test_invalid_load_errors():
    # Check for a TypeError for a variety of invalid loads
    for invalid_load in ['a string', FixedReaction(0), [], 10]:
        with pytest.raises(TypeError):
            Beam(25, loads=[invalid_load], reactions=[FixedReaction(0)])


def test_invalid_reaction_errors():
    # Check for an TypeError for a variety of invalid reactions
    for invalid_reaction in ['a string', PointLoad(25, 15), [], 10]:
        with pytest.raises(TypeError):
            Beam(25, loads=[PointLoad(-100, 15)], reactions=[invalid_reaction])


def test_shape_function():
    reactions = [PinnedReaction(x) for x in [0, 50, 100]]
    loads = [PointLoad(-100, x) for x in [0, 50, 100]]
    beam = Beam(100, loads, reactions, 29e6, 345)

    assert beam.shape(0).shape == (4,), "unexpected shape of shape functions"
    n1, n2, n3, n4 = beam.shape(0)
    assert n1 == 1, "N1(x=0) != 1"
    assert n3 == 0, "N3(x=0) != 0"
    # verify changing the length will not change the end points
    n1, n2, n3, n4 = beam.shape(0, L=15)
    assert n1 == 1, "N1(x=0) != 1"
    assert n3 == 0, "N3(x=0) != 0"

    n1, n2, n3, n4 = beam.shape(100, L=100)  # at x==L
    assert n1 == 0, "N1(x=L) != 0"
    assert n3 == 1, "N3(x=L) != 1"

    # TODO: Add more tests to verify shape functions


def test_stiffness_matrix_k():
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], 29e6, 345)
    assert beam.K.shape == (4, 4), "stiffness matrix is not expected size"

    # add another point load and verify the stiffness matrix changes size
    # accordingly
    beam.loads.append(PointLoad(-500, 12))
    beam.remesh()
    assert beam.K.shape == (6, 6), "stiffness matrix size did not update"

    # TODO: Add additional checks to verify stiffness function values


def test_apply_boundary_conditions():
    beam = Beam(
        25, [PointLoad(-100, 25), PointLoad(-100, 12)], [FixedReaction(0)], 29e6, 345
    )

    k = beam.K
    bcs = [(None, None), (0, 0)]
    initial_shape = beam.K.shape
    assert initial_shape == (6, 6), "stiffness matrix does not match expected size"
    ki = beam.apply_boundary_conditions(k, bcs)
    final_shape = ki.shape
    assert initial_shape == final_shape, (
        "stiffness matrix changed shape " "when applying boundary conditions"
    )

    # TODO: add additional test to check that boundary conditions where
    #  applied properly
    #  1. Confirm that a 1 is on the diagonal
    #  2. The row/column of all boundary conditions that are removed are all 0's


def test_node_deflections():
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], 29e6, 345)
    # beam.solve()

    assert beam.node_deflections.shape == (4, 1), "nodal deflections shape is not expected"
    # check that the deflection at the fixed end is 0
    dv = beam.node_deflections[0][0]  # vertical displacement at fixed end
    dq = beam.node_deflections[1][0]  # angular displacement at fixed end
    assert dv == 0, "displacement at fixed end is non-zero"
    assert dq == 0, "angular displacement at fixed end is non-zero"

    # check that the deflection at the free end is non-zero and negative
    dv = beam.node_deflections[2][0]  # vertical displacement at free end
    dq = beam.node_deflections[3][0]  # angular displacement at free end
    assert dv < 0, "displacement at free end is not negative"
    assert dq < 0, "angular displacement at free end is not negative"

    # calculate the nodal deflections with a moment load
    beam = Beam(25, [MomentLoad(-100, 25)], [FixedReaction(0)], 29e6, 345)

    assert beam.node_deflections.shape == (4, 1), "nodal deflections shape is not expected"
    # check that the deflection at the fixed end is 0
    dv = beam.node_deflections[0][0]  # vertical displacement at fixed end
    dq = beam.node_deflections[1][0]  # angular displacement at fixed end
    assert dv == 0, "displacement at fixed end is non-zero"
    assert dq == 0, "angular displacement at fixed end is non-zero"

    # check that the deflection at the free end is non-zero and negative
    dv = beam.node_deflections[2][0]  # vertical displacement at free end
    dq = beam.node_deflections[3][0]  # angular displacement at free end
    assert dv < 0, "displacement at free end is not negative"
    assert dq < 0, "angular displacement at free end is not negative"
