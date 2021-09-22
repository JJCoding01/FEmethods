"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from settings import EI, TOL, E, Ixx, L, P

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


def test_simply_supported_beam_center_load():
    """simple beam - concentrated load at center
    Load case 7
    """

    # Exact setup
    R = -P / 2  # lbs, reactions
    M_max = -P * L / 4  # psi, maximum moment
    d_max = P * L ** 3 / (48 * EI)  # max displacement

    # Numerical setup
    beam = Beam(
        length=L,
        loads=[PointLoad(magnitude=P, location=L / 2)],
        reactions=[PinnedReaction(x) for x in [0, L]],
        E=E,
        Ixx=Ixx,
    )

    assert pytest.approx(beam.moment(L / 2), rel=TOL) == M_max
    assert pytest.approx(beam.deflection(L / 2), rel=TOL) == d_max

    for r in beam.reactions:
        assert pytest.approx(r.moment, abs=1e-6) == 0
        assert pytest.approx(r.force, rel=TOL) == R


@pytest.mark.parametrize("location", [2, 3, 5, 7, 8])
def test_simply_supported_beam_offset_load(location):
    """simple beam - concentrated load at arbitrary points
    Load case 8
    """
    # Exact setup
    a = location
    b = L - a
    R1 = -P * b / L
    R2 = -P * a / L
    M_loc = -P * a * b / L  # moment at load
    d_loc = P * a ** 2 * b ** 2 / (3 * EI * L)  # deflection at load

    # numerical result
    beam = Beam(
        L,
        loads=[PointLoad(P, location)],
        reactions=[PinnedReaction(x) for x in [0, L]],
        E=E,
        Ixx=Ixx,
    )

    assert pytest.approx(beam.moment(location), rel=TOL) == M_loc
    assert pytest.approx(beam.deflection(location), rel=TOL) == d_loc

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2

    assert pytest.approx(beam.reactions[0].moment, abs=1e-6) == 0
    assert pytest.approx(beam.reactions[1].moment, abs=1e-6) == 0


def test_simply_supported_beam_equal_symmetric_loads():
    """Simple beam: Two equal concentrated loads symmetrically placed
    load case 9
    """

    R = -P  # both reactions are equal
    a = L / 4
    M_loc = -P * a  # max moment (at center between loads)
    d_loc = (
        P * a / (24 * EI) * (3 * L ** 2 - 4 * a ** 2)
    )  # max deflection (at center)

    p = [PointLoad(magnitude=P, location=x) for x in [a, L - a]]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)

    assert pytest.approx(beam.moment(L / 2), rel=TOL) == M_loc
    assert pytest.approx(beam.deflection(L / 2), rel=TOL) == d_loc

    for r in beam.reactions:
        assert r.moment == 0
        assert pytest.approx(r.force, rel=TOL) == R


def test_simply_supported_beam_equal_non_symmetric_loads():
    """Simple beam: Two equal concentrated loads non-symmetrically placed
    load case 10
    """

    a = L / 4  # location of first load from right
    b = L / 5  # location of second load from left
    R1 = -P / L * (L - a + b)
    R2 = -P / L * (L + a - b)

    M1 = R1 * a  # moment at first load
    x = L / 2
    Mx = R1 * x + P * (x - a)  # moment at center
    M2 = R2 * b  # moment at second load

    p = [PointLoad(magnitude=P, location=x) for x in [a, L - b]]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)

    assert pytest.approx(beam.moment(a), rel=TOL) == M1
    assert pytest.approx(beam.moment(x), rel=TOL) == Mx
    assert pytest.approx(beam.moment(L - b), rel=TOL) == M2

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2

    for r in beam.reactions:
        assert r.moment == 0


def test_simply_supported_beam_unequal_non_symmetric_loads():
    """Simple beam: Two unequal concentrated loads non-symmetrically placed
    load case 11
    """

    P1 = -900
    P2 = -1200
    a = L / 4  # location of first load from right
    b = L / 5  # location of second load from left

    R1 = -(P1 * (L - a) + P2 * b) / L
    R2 = -(P1 * a + P2 * (L - b)) / L

    M1 = R1 * a
    x = L / 2
    Mx = R1 * x + P1 * (x - a)
    M2 = R2 * b

    p = [
        PointLoad(magnitude=P1, location=a),
        PointLoad(magnitude=P2, location=L - b),
    ]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)

    assert pytest.approx(beam.moment(a), rel=TOL) == M1
    assert pytest.approx(beam.moment(x), rel=TOL) == Mx
    assert pytest.approx(beam.moment(L - b), rel=TOL) == M2

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2

    for r in beam.reactions:
        assert r.moment == 0
