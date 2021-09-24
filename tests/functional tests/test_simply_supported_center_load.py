"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from settings import EI, TOL, E, Ixx, L, P

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam():
    """cantilevered beam with load at end"""
    beam = Beam(
        length=L,
        loads=[PointLoad(magnitude=P, location=L / 2)],
        reactions=[PinnedReaction(x) for x in [0, L]],
        E=E,
        Ixx=Ixx,
    )
    yield beam


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_center_reaction_force(reaction_index, beam):
    R = -P / 2  # lbs, reactions
    assert pytest.approx(beam.reactions[reaction_index].force, rel=TOL) == R


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_center_reaction_moment_0(reaction_index, beam):
    assert beam.reactions[reaction_index].moment == 0


def test_simply_supported_center_max_moment(beam):
    M_max = -P * L / 4  # psi, maximum moment
    assert pytest.approx(beam.moment(L / 2), rel=TOL) == M_max


def test_simply_supported_center_max_deflection(beam):
    d_max = P * L ** 3 / (48 * EI)  # max displacement
    assert pytest.approx(beam.deflection(L / 2), rel=TOL) == d_max
