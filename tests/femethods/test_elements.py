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


def test_invalid_load_placement():
    reactions = [PinnedReaction(x) for x in [0, 50, 100]]
    loads = [PointLoad(-100, x) for x in [0, 50, 100]]

    # there should be a warning indicating that the load position was moved
    # slightly so it does not line up with the reaction.
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


def test_shape_of_node_deflections():
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], 29e6, 345)
    assert beam.node_deflections.shape == (4, 1), \
        "nodal deflections shape is not expected"


def test_node_deflections_at_fixed_end():
    for load in [PointLoad(-100, 25), MomentLoad(-100, 25)]:
        beam = Beam(25, [load], [FixedReaction(0)], 29e6, 345)
        # check that the deflection at the fixed end is 0
        msgs = [
            "displacement at fixed end is non-zero",
            "angular displacement at fixed end is non-zero",
        ]
        for i, msg in enumerate(msgs):
            assert beam.node_deflections[i][0] == 0, msg


def test_node_deflections_at_free_end():
    for load in [PointLoad(-100, 25), MomentLoad(-100, 25)]:
        beam = Beam(25, [load], [FixedReaction(0)], 29e6, 345)
        # check that the deflection at the free end is non-zero and negative
        msgs = [
            "displacement at free end is not negative",
            "angular displacement at free end is not negative",
        ]
        for i, msg in enumerate(msgs, 2):
            assert beam.node_deflections[i][0] < 0, msg


def test_solve_method():
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], 29e6, 345)

    reaction = beam.reactions[0]
    print(reaction)
    assert reaction.force is None, \
        "Reaction force was not None before being solved"
    assert reaction.moment is None, \
        "Reaction moment was not None before being solved"

    beam.solve()
    reaction = beam.reactions[0]
    assert reaction.force == 100, \
        "Reaction force must be equal to and opposite load"
    assert reaction.moment == 100 * 25, \
        "Reaction moment must be equal to the load times the moment arm"
    print(reaction)
    # assert reaction.force is None, "Reaction force was not None before being solved"
    # assert reaction.moment is None, "Reaction moment was not None before being solved"
