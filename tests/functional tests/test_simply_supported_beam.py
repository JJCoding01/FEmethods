"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

from settings import E, EI, Ixx, L, P
from validate import validate

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
        loads=[PointLoad(value=P, location=L / 2)],
        reactions=[PinnedReaction(x) for x in [0, L]],
        E=E,
        Ixx=Ixx,
    )
    beam.solve()

    validate(beam, loc=L / 2, R=[(R, 0), (R, 0)], M_loc=M_max, d_loc=d_max)


def test_simply_supported_beam_offset_load():
    """simple beam - concentrated load at arbitrary points
    Load case 8
    """
    locations = [2, 3, 5, 7, 8]
    for location in locations:
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
        beam.solve()

        # verify reactions
        validate(beam, loc=location, R=[(R1, 0), (R2, 0)], M_loc=M_loc, d_loc=d_loc)


def test_simply_supported_beam_equal_symmetric_loads():
    """Simple beam: Two equal concentrated loads symmetrically placed
    load case 9
    """

    R = -P  # both reactions are equal
    a = L / 4
    M_loc = -P * a  # max moment (at center between loads)
    d_loc = P * a / (24 * EI) * (3 * L ** 2 - 4 * a ** 2)  # max deflection (at center)

    p = [PointLoad(value=P, location=x) for x in [a, L - a]]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)
    beam.solve()

    # verify reactions
    validate(beam, loc=L / 2, R=[(R, 0), (R, 0)], M_loc=M_loc, d_loc=d_loc)


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

    p = [PointLoad(value=P, location=x) for x in [a, L - b]]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)
    beam.solve()

    # verify reactions
    for m, loc in zip((M1, Mx, M2), (a, L / 2, L - b)):
        validate(beam, loc=loc, R=[(R1, 0), (R2, 0)], M_loc=m, d_loc=None)


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

    p = [PointLoad(value=P1, location=a), PointLoad(value=P2, location=L - b)]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)
    beam.solve()

    # verify reactions
    for m, loc in zip((M1, Mx, M2), (a, L / 2, L - b)):
        # assert approx(beam.reactions[0].value[0], rel=1e-4) == R1*1.25
        validate(beam, loc=loc, R=[(R1, 0), (R2, 0)], M_loc=m, d_loc=None)
