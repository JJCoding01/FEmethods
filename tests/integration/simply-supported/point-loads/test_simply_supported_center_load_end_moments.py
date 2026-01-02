"""
Functional tests for simply supported beams (beams with two pinned reactions)


https://www.structx.com/Beam_Formulas_033.html
"""

import pytest

from femethods.elements import Beam
from femethods.loads import MomentLoad, PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam_setup(beam_length, load, moment, E, I):
    """Simply supported beam with center point load and moments at ends"""

    # M1 > M2
    M1 = moment
    M2 = -0.75 * moment

    loads = [
        MomentLoad(magnitude=M1, location=0),
        PointLoad(magnitude=load, location=beam_length / 2),
        MomentLoad(magnitude=M2, location=beam_length),
    ]
    beam = Beam(
        length=beam_length,
        loads=loads,
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        mesh=None,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load, (M1, M2)


def test_simply_supported_reaction_force(beam_setup, TOL):
    beam, L, P, M = beam_setup
    M1, M2 = M
    # noinspection PyPep8Naming
    R1 = (-P / 2) + (-M1 + M2) / L  # lbs, reactions
    R2 = (-P / 2) - (-M1 + M2) / L  # lbs, reactions
    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2


def test_simply_supported_center_center_moment(beam_setup, TOL):
    beam, L, P, (M1, M2) = beam_setup

    # noinspection PyPep8Naming
    M_max = (P * L / 4) - (M1 + M2) / L  # psi, maximum moment
    assert pytest.approx(beam.moment(L / 2), rel=TOL) == M_max
