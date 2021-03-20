"""
Module to contain common verification code for functional tests
"""

from pytest import approx
from settings import TOL


def validate(beam, loc, R, M_loc, d_loc):
    """Verify key values in the beam to exact values

    Compare the following parameters between the numerical (beam) calculations
    and values from exact, tabulated equations for specific cases.
       * Reactions: given as a tuple of (force, moment)
       * Moment at a specific location (loc)
       * Displacement at a specific location (loc)
    """

    msgs = []
    exact = []
    for r in R:
        exact.append(r[0])
        exact.append(r[1])
        msgs.append("Reaction force not equal")
        msgs.append("Reaction moment not equal")

    exact.append(M_loc)
    exact.append(d_loc)
    msgs.append("Moment at location not equal")
    msgs.append("Deflection at location not equal")

    numerical = []
    for r in beam.reactions:
        numerical.append(r.value[0])
        numerical.append((r.value[1]))
    numerical.append(beam.moment(loc))  # moment at given location
    numerical.append(beam.deflection(loc))  # deflection at given location

    for e, n, msg in zip(exact, numerical, msgs):
        if e is None:
            # there is not an exact value to compare, skip it
            continue
        assert approx(n, rel=TOL, abs=TOL) == e, msg
