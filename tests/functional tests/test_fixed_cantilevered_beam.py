"""
Functional tests for beams with fixed supports

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

"""

import pytest
from settings import EI, TOL, E, Ixx, L, P

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction


@pytest.fixture()
def beam():
    """cantilevered beam with load at end"""
    beam = Beam(
        length=L,
        loads=[PointLoad(magnitude=P, location=0)],
        reactions=[FixedReaction(L)],
        E=E,
        Ixx=Ixx,
    )
    yield beam


def test_cantilevered_beam_max_moment(beam):
    """fixed beam with concentrated load at free end
    case 13
    """
    # noinspection PyPep8Naming
    M_max = P * L  # at fixed end
    assert pytest.approx(beam.moment(L), rel=TOL) == M_max


def test_cantilevered_beam_load_max_deflection(beam):
    """fixed beam with concentrated load at free end
    case 13
    """
    d_max = P * L ** 3 / (3 * EI)  # at free end
    assert pytest.approx(beam.deflection(0), rel=TOL) == d_max


def test_cantilevered_beam_load_moment_at_free_end(beam):
    """fixed beam with concentrated load at free end
    case 13
    """
    assert pytest.approx(beam.moment(0), abs=1) == 0
