"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction

from .settings import E, EI, Ixx, TOL


@pytest.fixture()
def beam_setup(beam_length, load):
    """cantilevered beam with load at end"""
    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=beam_length / 2)],
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        E=E,
        Ixx=Ixx,
    )
    yield beam, beam_length, load


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_center_reaction_force(reaction_index, beam_setup):
    beam, beam_length, load = beam_setup

    # noinspection PyPep8Naming
    R = -load / 2  # lbs, reactions
    assert pytest.approx(beam.reactions[reaction_index].force, rel=TOL) == R


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_center_reaction_moment_0(reaction_index, beam_setup):
    beam = beam_setup[0]
    assert beam.reactions[reaction_index].moment == 0


def test_simply_supported_center_max_moment(beam_setup):
    beam, beam_length, load = beam_setup

    # noinspection PyPep8Naming
    M_max = -load * beam_length / 4  # psi, maximum moment
    assert pytest.approx(beam.moment(beam_length / 2), rel=TOL) == M_max


def test_simply_supported_center_max_deflection(beam_setup):
    beam, beam_length, load = beam_setup

    d_max = load * beam_length**3 / (48 * EI)  # max displacement
    assert pytest.approx(beam.deflection(beam_length / 2), rel=TOL) == d_max
