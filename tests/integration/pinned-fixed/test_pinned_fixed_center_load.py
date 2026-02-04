"""
Functional tests for beam with pinned-fixed reactions and center point load

https://www.structx.com/Beam_Formulas_013.html
"""

import numpy as np
import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


@pytest.fixture()
def beam_setup(beam_length, load, E, I):
    """Simply supported beam with center point load"""

    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=beam_length / 2)],
        reactions=[PinnedReaction(0), FixedReaction(beam_length)],
        mesh=None,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load


def test_pinned_fixed_center_reaction_force(beam_setup, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    R1 = 5 * P / 16  # lbs, Pinned reaction
    R2 = 11 * P / 16  # lbs, Fixed reaction (MAX)
    print(R1)
    print(R2)
    assert pytest.approx(beam.reactions[0].force, rel=TOL) == -R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == -R2


def test_pinned_fixed_center_max_moment(beam_setup, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    M_max = 3 * P * L / 16  # in-lb, moment at fixed end
    assert pytest.approx(beam.moment(L), rel=TOL) == -M_max


def test_pinned_fixed_center_moment(beam_setup, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    M1 = 5 * P * L / 32  # in-lb, moment at point of load
    assert pytest.approx(beam.moment(L / 2), rel=TOL) == M1


def test_pinned_fixed_center_deflection(beam_setup, EI, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    d1 = 7 * P * L**3 / (768 * EI)  # in, deflection at point of load
    assert pytest.approx(beam.deflection(L / 2), rel=TOL) == d1


def test_pinned_fixed_max_deflection(beam_setup, EI, TOL):
    beam, L, P = beam_setup

    # noinspection PyPep8Naming
    x = L * np.sqrt(1 / 5)  # point of max deflection
    d_max = P * L**3 / (48 * EI * np.sqrt(5))  # in, deflection at point of load
    assert pytest.approx(beam.deflection(x), rel=TOL) == d_max
