"""
Functional tests for beams with fixed supports

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

"""

import pytest
from settings import EI, TOL, E, Ixx

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction


@pytest.fixture()
def beam_setup(beam_length, load):
    """cantilevered beam with load at end"""
    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=0)],
        reactions=[FixedReaction(beam_length)],
        E=E,
        Ixx=Ixx,
    )
    yield beam, beam_length, load


def test_cantilevered_beam_max_moment(beam_setup):
    """fixed beam with concentrated load at free end
    case 13
    """
    beam, beam_length, load = beam_setup
    # noinspection PyPep8Naming
    M_max = load * beam_length  # at fixed end
    assert pytest.approx(beam.moment(beam_length), rel=TOL) == M_max


def test_cantilevered_beam_load_max_deflection(beam_setup):
    """fixed beam with concentrated load at free end
    case 13
    """
    beam, beam_length, load = beam_setup

    d_max = load * beam_length ** 3 / (3 * EI)  # at free end
    assert pytest.approx(beam.deflection(0), rel=TOL) == d_max


def test_cantilevered_beam_load_moment_at_free_end(beam_setup):
    """fixed beam with concentrated load at free end
    case 13
    """
    beam = beam_setup[0]
    assert pytest.approx(beam.moment(0), abs=1.5) == 0
