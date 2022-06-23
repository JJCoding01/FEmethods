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
def beam_setup(beam_length, load, load_location):

    """cantilevered beam with load at end"""
    beam = Beam(
        beam_length,
        loads=[PointLoad(load, load_location)],
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        E=E,
        Ixx=Ixx,
    )
    yield beam, beam_length, load, load_location


# noinspection PyPep8Naming
def test_simply_supported_offset_reaction_force(beam_setup):
    beam, beam_length, load, load_location = beam_setup

    a = load_location
    b = beam_length - a
    R1 = -load * b / beam_length
    R2 = -load * a / beam_length

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_offset_reaction_moment_0(reaction_index, beam_setup):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


# noinspection PyPep8Naming
def test_simply_supported_offset_moment(beam_setup):
    beam, beam_length, load, load_location = beam_setup

    a = load_location
    b = beam_length - a

    M_loc = -load * a * b / beam_length  # moment at load

    assert pytest.approx(beam.moment(load_location), rel=TOL) == M_loc


def test_simply_supported_offset_max_deflection(beam_setup):
    beam, beam_length, load, load_location = beam_setup

    a = load_location

    b = beam_length - a
    d_loc = load * a**2 * b**2 / (3 * EI * beam_length)  # deflection at load

    assert pytest.approx(beam.deflection(load_location), rel=TOL) == d_loc
