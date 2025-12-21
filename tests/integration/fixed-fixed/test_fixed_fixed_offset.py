"""
Functional tests for beam with fixed-fixed reactions and offset point load

https://www.structx.com/Beam_Formulas_017.html
"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction
from tests.factories import MeshFactory


@pytest.fixture(params=(25, 50, 75))
def load_location(request):
    return request.param


@pytest.fixture()
def beam_setup(beam_length, load, load_location, E, I):
    """Simply supported beam with offset point load"""

    a = load_location
    b = beam_length - a
    mesh = MeshFactory(
        length=beam_length,
        locations=[0, beam_length],
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        beam_length,
        loads=[PointLoad(load, a)],
        reactions=[FixedReaction(x) for x in [0, beam_length]],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load, (a, b)


# noinspection PyPep8Naming
def test_fixed_fixed_offset_reaction_force(beam_setup, TOL):
    beam, L, P, (a, b) = beam_setup

    R1 = P * b**2 / (L**3) * (3 * a + b)
    R2 = P * a**2 / (L**3) * (a + 3 * b)

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == -R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == -R2


# noinspection PyPep8Naming
def test_fixed_fixed_offset_reaction_moment(beam_setup, TOL):
    beam, L, P, (a, b) = beam_setup

    M1 = P * a * b**2 / L**2  # in-lb, moment at reaction 1
    M2 = P * a**2 * b / L**2  # in-lb, moment at reaction 2

    assert pytest.approx(beam.reactions[0].moment, rel=TOL) == -M1
    assert pytest.approx(beam.reactions[1].moment, rel=TOL) == M2


# noinspection PyPep8Naming
def test_fixed_fixed_offset_moment(beam_setup, TOL):
    beam, L, P, (a, b) = beam_setup

    M_loc = 2 * P * a**2 * b**2 / L**3  # moment at load

    assert pytest.approx(beam.moment(a), rel=TOL) == M_loc


def test_fixed_fixed_offset_deflection(beam_setup, EI, TOL):
    beam, L, P, (a, b) = beam_setup

    # defection at point of load
    d = 2 * P * a**3 * b**3 / (6 * EI * L**3)  # in, deflection at point load
    assert pytest.approx(beam.deflection(a), rel=TOL) == d


def test_fixed_fixed_offset_max_deflection(beam_setup, EI, TOL):
    beam, L, P, (a, b) = beam_setup

    # the below equation is only valid when this is true
    assert a > b, "invalid load position for these equations"

    x = 2 * a * L / (3 * a + b)
    d = 4 * P * a**3 * b**2 / (3 * EI * (3 * a + b) ** 2)
    assert pytest.approx(beam.deflection(x), rel=TOL) == d
