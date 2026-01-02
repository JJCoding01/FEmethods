# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

# Note:
#   There are numerous tests with E and Ixx (upper case) names, invalid-name error
#   is disabled here to allow engineering conventions to be followed.


import pytest

from femethods.elements import Beam
from femethods.loads import MomentLoad, PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


@pytest.mark.parametrize("length", [100, 250])
def test_beam_length_input(length, reaction_simple, load_centered):
    beam = Beam(length=length, reactions=reaction_simple, loads=load_centered)
    assert beam.length == length, "beam length does not match input"


@pytest.mark.parametrize("length", [100, 250])
def test_beam_length_update(beam_simply_supported, length):
    beam_simply_supported.length = length
    assert (
        beam_simply_supported.length == length
    ), "updated beam length does not match input"


@pytest.mark.parametrize("invalid_length", [-5, 0])
def test_beam_invalid_lengths(invalid_length, load_centered, reaction_simple):
    with pytest.raises(ValueError):
        Beam(
            length=invalid_length,
            reactions=reaction_simple,
            loads=load_centered,
        )


# noinspection PyPep8Naming
def test_beam_E_default(beam_simply_supported):
    assert beam_simply_supported.E == 1, "Check default Young's modulus"


# noinspection PyPep8Naming
@pytest.mark.parametrize("E", [15e6, 30e6])
def test_beam_E_input(length, reaction_simple, load_centered, E):
    beam = Beam(length=length, reactions=reaction_simple, loads=load_centered, E=E)
    assert beam.E == E, "beam modulus of elasticity does not match input"


# noinspection PyPep8Naming
@pytest.mark.parametrize("E", [0, -1])
def test_beam_E_input_errors(length, reaction_simple, load_centered, E):
    with pytest.raises(ValueError):
        Beam(length=length, reactions=reaction_simple, loads=load_centered, E=E)


# noinspection PyPep8Naming
@pytest.mark.parametrize("E", [15e6, 30e6])
def test_beam_E_update(beam_simply_supported, E):
    beam_simply_supported.E = E
    assert beam_simply_supported.E == E, "updated beam length does not match input"


# noinspection PyPep8Naming
def test_beam_Ixx_default(beam_simply_supported):
    assert beam_simply_supported.Ixx == 1, "Check default moment of inertia"


# noinspection PyPep8Naming
@pytest.mark.parametrize("Ixx", [10, 20])
def test_beam_Ixx_input(length, reaction_simple, load_centered, Ixx):
    beam = Beam(length=length, reactions=reaction_simple, loads=load_centered, Ixx=Ixx)
    assert beam.Ixx == Ixx, "beam moment of inertia does not match input"


# noinspection PyPep8Naming
@pytest.mark.parametrize("Ixx", [0, -1])
def test_beam_Ixx_input_errors(length, reaction_simple, load_centered, Ixx):
    with pytest.raises(ValueError):
        Beam(
            length=length,
            reactions=reaction_simple,
            loads=load_centered,
            Ixx=Ixx,
        )


# noinspection PyPep8Naming
@pytest.mark.parametrize("Ixx", [10, 20])
def test_beam_Ixx_update(beam_simply_supported, Ixx):
    beam_simply_supported.Ixx = Ixx
    assert (
        beam_simply_supported.Ixx == Ixx
    ), "beam moment of inertia does not match input"


@pytest.mark.parametrize("invalid_reaction", [[], "string", 10, PointLoad(10, 2)])
def test_invalid_reactions(invalid_reaction, length, load_centered):
    with pytest.raises(TypeError):
        Beam(length=length, reactions=[invalid_reaction], loads=load_centered)


@pytest.mark.parametrize("invalid_load", [[], "string", 10, PinnedReaction(0)])
def test_invalid_loads(invalid_load, length, reaction_simple):
    with pytest.raises(TypeError):
        Beam(length=length, reactions=reaction_simple, loads=[invalid_load])


def test_invalid_load_placement():
    reactions = [PinnedReaction(x) for x in [0, 50, 100]]
    loads = [PointLoad(-100, x) for x in [0, 50, 100]]

    # there should be a warning indicating that the load position was moved
    # slightly so it does not line up with the reaction.
    with pytest.warns(UserWarning):
        beam = Beam(100, loads=loads, reactions=reactions)

    for load, reaction in zip(beam.loads, beam.reactions):
        assert (
            load.location != reaction.location
        ), "moved load is still the same as a reaction"


@pytest.mark.parametrize("invalid_load", ["a string", FixedReaction(0), [], 10])
def test_invalid_load_errors(invalid_load):
    # Check for a TypeError for a variety of invalid loads
    with pytest.raises(TypeError):
        Beam(25, loads=[invalid_load], reactions=[FixedReaction(0)])


@pytest.mark.parametrize("invalid_reaction", ["a string", PointLoad(25, 15), [], 10])
def test_invalid_reaction_errors(invalid_reaction):
    # Check for an TypeError for a variety of invalid reactions
    with pytest.raises(TypeError):
        Beam(25, loads=[PointLoad(-100, 15)], reactions=[invalid_reaction])


def test_shape_function():
    reactions = [PinnedReaction(x) for x in [0, 50, 100]]
    loads = [PointLoad(-100, x) for x in [5, 45, 90]]
    beam = Beam(100, loads, reactions, E=29e6, Ixx=345)

    assert beam.shape(0).shape == (4,), "unexpected shape of shape functions"
    n1, _, n3, _ = beam.shape(0)
    assert n1 == 1, "N1(x=0) != 1"
    assert n3 == 0, "N3(x=0) != 0"
    # verify changing the length will not change the end points
    n1, _, n3, _ = beam.shape(0, L=15)
    assert n1 == 1, "N1(x=0) != 1"
    assert n3 == 0, "N3(x=0) != 0"

    n1, _, n3, _ = beam.shape(100, L=100)  # at x==L
    assert n1 == 0, "N1(x=L) != 0"
    assert n3 == 1, "N3(x=L) != 1"

    # TODO: Add more tests to verify shape functions


def test_stiffness_matrix_k(beam_fixed, length):
    # beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], 29e6, 345)
    beam = beam_fixed
    assert beam.K.shape == (4, 4), "stiffness matrix is not expected size"

    # add another point load and verify the stiffness matrix changes size
    # accordingly
    beam.loads.append(PointLoad(-500, length / 2))
    beam.remesh()
    assert beam.K.shape == (6, 6), "stiffness matrix size did not update"

    # TODO: Add additional checks to verify stiffness function values


def test_apply_boundary_conditions():
    beam = Beam(
        25,
        [PointLoad(-100, 25), PointLoad(-100, 12)],
        [FixedReaction(0)],
        mesh=None,
        E=29e6,
        Ixx=345,
    )

    k = beam.K
    bcs = [(None, None), (0, 0)]
    initial_shape = beam.K.shape
    assert initial_shape == (
        6,
        6,
    ), "stiffness matrix does not match expected size"
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
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], E=29e6, Ixx=345)
    assert beam.node_deflections.shape == (
        4,
    ), "nodal deflections shape is not expected"


def test_node_deflections_at_fixed_end():
    for load in [PointLoad(-100, 25), MomentLoad(-100, 25)]:
        beam = Beam(25, [load], [FixedReaction(0)], E=29e6, Ixx=345)
        # check that the deflection at the fixed end is 0
        msgs = [
            "displacement at fixed end is non-zero",
            "angular displacement at fixed end is non-zero",
        ]
        for i, msg in enumerate(msgs):
            assert beam.node_deflections[i] == 0, msg


def test_node_deflections_at_free_end():
    for load in [PointLoad(-100, 25), MomentLoad(-100, 25)]:
        beam = Beam(25, [load], [FixedReaction(0)], E=29e6, Ixx=345)
        # check that the deflection at the free end is non-zero and negative
        msgs = [
            "displacement at free end is not negative",
            "angular displacement at free end is not negative",
        ]
        for i, msg in enumerate(msgs, 2):
            assert beam.node_deflections[i] < 0, msg


def test_solve_method():
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], E=29e6, Ixx=345)

    reaction = beam.reactions[0]
    assert reaction.force == 100, "Reaction force must be equal to and opposite load"
    assert (
        reaction.moment == 100 * 25
    ), "Reaction moment must be equal to the load times the moment arm"


@pytest.mark.parametrize("invalid_location", [-4, 30])
def test_invalid_deflection_location_value(invalid_location):
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], E=29e6, Ixx=345)
    with pytest.raises(ValueError):
        beam.deflection(invalid_location)


def test_invalid_deflection_location_type():
    beam = Beam(25, [PointLoad(-100, 25)], [FixedReaction(0)], E=29e6, Ixx=345)
    with pytest.raises(TypeError):
        beam.deflection("a string (not a number)")


@pytest.mark.parametrize("location", [0.5, 5.0, 13.0, 20, 24.5])
def test_shear_cantilevered(location):
    beam = Beam(25, [PointLoad(-1000, 25)], [FixedReaction(0)])

    assert (
        pytest.approx(beam.shear(location), rel=1e-5) == -1000
    ), f"shear does not equal load at location {location}"


@pytest.mark.parametrize("location", [-5, 35])
def test_shear_cantilevered_error(location):
    # right now, the derivative function will try to calculate shear outside the beam
    # when calculating shear at or near endpoints. Verify that calculating shear at ends
    # raises a ValueError. It should also raise a ValueError when the input is outside
    # the beam
    beam = Beam(25, [PointLoad(-1000, 25)], [FixedReaction(0)])
    with pytest.raises(ValueError):
        beam.shear(location)


def test_plot_diagrams_invalid_value():
    with pytest.raises(ValueError):
        beam = Beam(10, [PointLoad(10, 10)], [FixedReaction(0)])
        beam.plot(diagrams=("shear", "bad value"))


def test_plot_diagrams_diagrams_label_mismatch():
    with pytest.raises(ValueError):
        beam = Beam(10, [PointLoad(10, 10)], [FixedReaction(0)])
        beam.plot(diagrams=("shear",), diagram_labels=("shear", "moment"))


def test_plot_diagram_labels_without_diagrams():
    with pytest.raises(ValueError):
        beam = Beam(10, [PointLoad(10, 10)], [FixedReaction(0)])
        beam.plot(diagram_labels=("V, lb", "M, in/lb", "delta, in"))


def test_plot_default_labels():
    beam = Beam(10, [PointLoad(10, 10)], [FixedReaction(0)])
    _, axes = beam.plot()
    x_labels = ("", "", "", "Beam position, x")
    y_labels = ("shear", "moment", "angle", "deflection")

    assert len(axes) == len(x_labels), "wrong number of sub-plots"
    for ax, x_label, y_label in zip(axes, x_labels, y_labels):
        assert ax.get_xlabel() == x_label
        assert ax.get_ylabel() == y_label


def test_plot_custom_labels():
    beam = Beam(10, [PointLoad(10, 10)], [FixedReaction(0)])
    diagrams = ("deflection", "deflection", "moment", "shear")
    labels = ("def1", "def2", "M", "V")
    _, axes = beam.plot(diagrams=diagrams, diagram_labels=labels)
    assert len(axes) == len(diagrams), "wrong number of sub-plots"

    x_labels = ["" for _ in range(len(diagrams) - 1)]
    x_labels.append("Beam position, x")
    for ax, x_label, y_label in zip(axes, x_labels, labels):
        assert ax.get_xlabel() == x_label
        assert ax.get_ylabel() == y_label


def test_plot_one_diagram():
    beam = Beam(10, [PointLoad(10, 10)], [FixedReaction(0)])
    _, axes = beam.plot(diagrams=("deflection",))
    assert len(axes) == 1, "expected length of axes was 1"
    for ax, y_label in zip(axes, ("deflection",)):
        assert ax.get_ylabel() == y_label
