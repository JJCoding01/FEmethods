"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from settings import EI, TOL, E, Ixx, L, P

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam():
    a = L / 4
    p = [PointLoad(magnitude=P, location=x) for x in [a, L - a]]
    r = [PinnedReaction(x) for x in [0, L]]
    beam = Beam(length=L, loads=p, reactions=r, E=E, Ixx=Ixx)
    yield beam


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_eq_symmetric_reaction_force(reaction_index, beam):
    # noinspection PyPep8Naming
    R = -P  # both reactions are equal
    assert pytest.approx(beam.reactions[reaction_index].force, rel=TOL) == R


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_eq_symmetric_reaction_moment_0(reaction_index, beam):
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


def test_simply_supported_eq_symmetric_moment(beam):
    a = L / 4
    # noinspection PyPep8Naming
    M_loc = -P * a  # max moment (at center between loads)
    assert pytest.approx(beam.moment(a), rel=TOL) == M_loc


def test_simply_supported_eq_symmetric_max_deflection(beam):
    a = L / 4

    # max deflection (at center)
    d_loc = P * a / (24 * EI) * (3 * L ** 2 - 4 * a ** 2)
    assert pytest.approx(beam.deflection(L / 2), rel=TOL) == d_loc
