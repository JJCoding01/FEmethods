"""
Functional tests for beams with fixed supports

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

"""

import pytest
from settings import E, EI, Ixx, L, P, TOL
from validate import validate

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction


def test_cantilevered_beam_load_at_end():
    """fixed beam with concentrated load at free end
    case 13
    """

    R = -P
    M_max = P * L  # at fixed end

    d_max = P * L ** 3 / (3 * EI)  # at free end

    beam = Beam(
        length=L,
        loads=[PointLoad(magnitude=P, location=0)],
        reactions=[FixedReaction(L)],
        E=E,
        Ixx=Ixx,
    )
    beam.solve()

    validate(beam, loc=0, R=[(R, M_max)], M_loc=0, d_loc=d_max)

    assert pytest.approx(beam.moment(L), rel=TOL) == M_max
