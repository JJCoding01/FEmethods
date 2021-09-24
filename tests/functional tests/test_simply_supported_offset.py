"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from settings import EI, TOL, E, Ixx, L, P

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture(params=(2, 3, 5, 77))
def beam_setup(request):
    """cantilevered beam with load at end"""
    beam = Beam(
        L,
        loads=[PointLoad(P, request.param)],
        reactions=[PinnedReaction(x) for x in [0, L]],
        E=E,
        Ixx=Ixx,
    )
    yield beam, request.param


def test_simply_supported_offset_reaction_force(beam_setup):
    beam, location = beam_setup

    a = location
    b = L - a
    R1 = -P * b / L
    R2 = -P * a / L

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_offset_reaction_moment_0(reaction_index, beam_setup):
    beam, _ = beam_setup
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


def test_simply_supported_offset_moment(beam_setup):
    beam, location = beam_setup

    a = location
    b = L - a
    M_loc = -P * a * b / L  # moment at load

    assert pytest.approx(beam.moment(location), rel=TOL) == M_loc


def test_simply_supported_offset_max_deflection(beam_setup):
    beam, location = beam_setup

    a = location
    b = L - a
    d_loc = P * a ** 2 * b ** 2 / (3 * EI * L)  # deflection at load

    assert pytest.approx(beam.deflection(location), rel=TOL) == d_loc
