"""
Functional tests for beam with fixed-fixed reactions and center point load

https://www.structx.com/Beam_Formulas_016.html
"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction


@pytest.fixture()
def beam_setup(beam_length, load, E, I):
    """Simply supported beam with center point load"""

    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=beam_length / 2)],
        reactions=[FixedReaction(x) for x in [0, beam_length]],
        mesh=None,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load


def test_fixed_fixed_center_reaction_force(beam_setup, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    R1 = P / 2
    assert pytest.approx(beam.reactions[0].force, rel=TOL) == -R1


def test_fixed_fixed_center_max_moment(beam_setup, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    M_max = P * L / 8  # in-lb, moment at center and ends
    assert pytest.approx(beam.moment(0), rel=TOL) == -M_max  # start
    assert pytest.approx(beam.moment(L / 2), rel=TOL) == M_max  # center
    assert pytest.approx(beam.moment(L), rel=TOL) == -M_max  # end


def test_fixed_fixed_center_deflection(beam_setup, EI, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    d1 = P * L**3 / (192 * EI)  # in, deflection at point of load
    assert pytest.approx(beam.deflection(L / 2), rel=TOL) == d1
