"""
Functional tests for beam with pinned-fixed reactions and offset point load

https://www.structx.com/Beam_Formulas_014.html
"""

import numpy as np
import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


@pytest.fixture(params=(25, 50, 75))
def load_location(request):
    return request.param


@pytest.fixture()
def beam_setup(beam_length, load, load_location, E, I):
    """Simply supported beam with offset point load"""

    a = load_location
    b = beam_length - a

    beam = Beam(
        beam_length,
        loads=[PointLoad(load, a)],
        reactions=[PinnedReaction(0), FixedReaction(beam_length)],
        mesh=None,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load, (a, b)


# noinspection PyPep8Naming
def test_pinned_fixed_offset_reaction_force(beam_setup, TOL):
    beam, L, P, (a, b) = beam_setup

    R1 = P * b**2 / (2 * L**3) * (a + 2 * L)
    R2 = P * a / (2 * L**3) * (3 * L**2 - a**2)

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == -R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == -R2


def test_pinned_fixed_offset_reaction_moment_0_at_pinned(beam_setup):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[0].moment, abs=1) == 0


# noinspection PyPep8Naming
def test_pinned_fixed_offset_moment(beam_setup, TOL):
    beam, L, P, (a, b) = beam_setup

    R1 = P * b**2 / (2 * L**3) * (a + 2 * L)
    M_loc = R1 * a  # moment at load

    assert pytest.approx(beam.moment(a), rel=TOL) == M_loc


# noinspection PyPep8Naming
def test_pinned_fixed_offset_moment_fixed(beam_setup, TOL):
    beam, L, P, (a, b) = beam_setup

    M_fixed = P * a * b / (2 * L**2) * (a + L)  # moment at fixed end

    assert pytest.approx(beam.moment(a), rel=TOL) == M_fixed


def test_pinned_fixed_offset_deflection(beam_setup, EI, TOL):
    beam, L, P, (a, b) = beam_setup

    # defection at point of load
    d = P * a**3 * b**2 / (12 * EI * L**3) * (3 * L + b)
    assert pytest.approx(beam.deflection(a), rel=TOL) == d


def test_pinned_fixed_offset_max_deflection(beam_setup, EI, TOL):
    beam, L, P, (a, b) = beam_setup

    if a < 0.414 * L:
        x = L * (L**2 + a**2) / (3 * L**2 - a**2)
        d_max = P * a / (3 * EI) * (L**2 - a**2) ** 3 / (3 * L**2 - a**2) ** 2
    else:
        assert a > 0.414 * L

        x = L * np.sqrt(a / (2 * L + a))
        d_max = P * a * b**2 / (6 * EI) * np.sqrt(a / (2 * L + a))

    # TODO: Update this test to ensure that both if-statement branches are hit

    assert pytest.approx(beam.deflection(x), rel=TOL) == d_max
