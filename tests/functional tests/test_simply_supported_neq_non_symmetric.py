"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from settings import TOL, E, Ixx, L, P

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam():
    P1 = -900
    P2 = -1200
    a = L / 4  # location of first load from right
    b = L / 5  # location of second load from left

    p = [
        PointLoad(magnitude=P1, location=a),
        PointLoad(magnitude=P2, location=L - b),
    ]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)
    yield beam


def test_simply_supported_neq_non_symmetric_reaction_force(beam):
    P1 = -900
    P2 = -1200
    a = L / 4  # location of first load from right
    b = L / 5  # location of second load from left

    R1 = -(P1 * (L - a) + P2 * b) / L
    R2 = -(P1 * a + P2 * (L - b)) / L
    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_neq_non_symmetric_reaction_moment_0(
    reaction_index, beam
):
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


@pytest.mark.parametrize("location", ("load1", "center", "load2"))
def test_simply_supported_eq_non_symmetric_moment(location, beam):
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
    if location == "load1":
        assert pytest.approx(beam.moment(a), rel=TOL) == M1
    if location == "center":
        assert pytest.approx(beam.moment(x), rel=TOL) == Mx
    if location == "load2":
        assert pytest.approx(beam.moment(L - b), rel=TOL) == M2
