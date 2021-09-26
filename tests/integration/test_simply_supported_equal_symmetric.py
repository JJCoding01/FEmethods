"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from .settings import EI, TOL, E, Ixx

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam_setup(beam_length, load):
    a = beam_length / 4
    p = [PointLoad(magnitude=load, location=x) for x in [a, beam_length - a]]
    r = [PinnedReaction(x) for x in [0, beam_length]]
    beam = Beam(length=beam_length, loads=p, reactions=r, E=E, Ixx=Ixx)
    yield beam, beam_length, load, a


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_eq_symmetric_reaction_force(
    reaction_index, beam_setup
):
    beam, beam_length, load, a = beam_setup

    # noinspection PyPep8Naming
    R = -load  # both reactions are equal
    assert pytest.approx(beam.reactions[reaction_index].force, rel=TOL) == R


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_eq_symmetric_reaction_moment_0(
    reaction_index, beam_setup
):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


def test_simply_supported_eq_symmetric_moment(beam_setup):
    beam, beam_length, load, a = beam_setup
    a = beam_length / 4

    # noinspection PyPep8Naming
    M_loc = -load * a  # max moment (at center between loads)
    assert pytest.approx(beam.moment(a), rel=TOL) == M_loc


def test_simply_supported_eq_symmetric_max_deflection(beam_setup):
    beam, beam_length, load, a = beam_setup
    # max deflection (at center)
    d_loc = load * a / (24 * EI) * (3 * beam_length ** 2 - 4 * a ** 2)
    assert pytest.approx(beam.deflection(beam_length / 2), rel=TOL) == d_loc
