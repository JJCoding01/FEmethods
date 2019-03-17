"""
This test module test the validity of the final results for specific cases

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""
from pytest import approx

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction

L = 120  # in, length of beam in inches
P = -1000  # load in pounds acting on beam
E = 29e6  # psi, Young's modulus
Ixx = 350  # in^4 area moment of inertia of beam
EI = E * Ixx  # common constant

TOL = 1e-4  # allowable tolerance between exact and numerical solutions to pass


def validate(beam, loc, R1, R2, M_loc, d_loc):
    """Verify key values in the beam to exact values

    Compare the following parameters between the numerical (beam) calculations
    and values from exact, tabulated equations for specific cases.
       * Reactions (R1, R2): given as a tuple of (force, moment)
       * Moment at a specific location (loc)
       * Displacement at a specific location (loc)
    """
    msgs = ('R1 force not equal', 'R1 moment not equal',
            'R2 force not equal', 'R2 moment not equal',
            'Moment at location not equal',
            'Deflection not equal')
    exact = R1[0], R1[1], R2[0], R2[1], M_loc, d_loc

    # print(*exact)
    numerical = (beam.reactions[0].value[0], beam.reactions[0].value[1],
                 beam.reactions[1].value[0], beam.reactions[1].value[1],
                 beam.moment(loc),  # moment at given location
                 beam.deflection(loc),  # deflection at given location
                 )

    for e, n, msg in zip(exact, numerical, msgs):
        if e is None:
            # there is not an exact value to compare, skip it
            continue
        assert approx(n, rel=TOL, abs=TOL) == e, msg


def test_simply_supported_beam_center_load():
    """simple beam - concentrated load at center
    Load case 7
    """
    # General variables
    # P = -1000  # lbs, load acting on beam

    # Exact setup
    R = -P / 2  # lbs, reactions
    M_max = -P * L / 4  # psi, maximum moment
    d_max = P * L ** 3 / (48 * EI)  # max displacement

    # Numerical setup
    beam = Beam(length=L,
                loads=[PointLoad(value=P, location=L / 2)],
                reactions=[PinnedReaction(x) for x in [0, L]],
                E=E, Ixx=Ixx)
    beam.solve()

    # verify shear
    # assert approx(beam.shear(3), rel=TOL) == R
    # assert approx(beam.shear(7), rel=TOL) == -R
    validate(beam, loc=L / 2, R1=(R, 0), R2=(R, 0), M_loc=M_max, d_loc=d_max)


def test_simply_supported_beam_offset_load():
    """simple beam - concentrated load at arbitrary points
    Load case 8
    """
    # General variables
    # P = -1000  # lbs, load acting on beam
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
        beam = Beam(L,
                    loads=[PointLoad(P, location)],
                    reactions=[PinnedReaction(x) for x in [0, L]],
                    E=E, Ixx=Ixx)
        beam.solve()

        # verify reactions
        validate(beam, loc=location, R1=(R1, 0), R2=(R2, 0),
                 M_loc=M_loc, d_loc=d_loc)


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
    validate(beam, loc=L / 2, R1=(R, 0), R2=(R, 0),
             M_loc=M_loc, d_loc=d_loc)


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
        validate(beam, loc=loc, R1=(R1, 0), R2=(R2, 0),
                 M_loc=m, d_loc=None)


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

    p = [PointLoad(value=P1, location=a),
         PointLoad(value=P2, location=L - b)]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)
    beam.solve()

    # verify reactions
    for m, loc in zip((M1, Mx, M2), (a, L / 2, L - b)):
        validate(beam, loc=loc, R1=(R1, 0), R2=(R2, 0),
                 M_loc=m, d_loc=None)
