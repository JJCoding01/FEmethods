"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.structx.com/Beam_Formulas_007.html
"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction
from tests.factories import MeshFactory


@pytest.fixture()
def beam_setup(beam_length, load, E, I):
    """Simply supported beam with center point load"""

    mesh = MeshFactory(
        length=beam_length,
        locations=[0, beam_length],
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=beam_length / 2)],
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_center_reaction_force(reaction_index, beam_setup, TOL):
    beam, beam_length_, load_ = beam_setup

    # noinspection PyPep8Naming
    R = -load_ / 2  # lbs, reactions
    assert pytest.approx(beam.reactions[reaction_index].force, rel=TOL) == R


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_center_reaction_moment_0(reaction_index, beam_setup):
    beam = beam_setup[0]
    assert beam.reactions[reaction_index].moment == 0


def test_simply_supported_center_max_moment(beam_setup, TOL):
    beam, beam_length_, load_ = beam_setup

    # noinspection PyPep8Naming
    M_max = -load_ * beam_length_ / 4  # psi, maximum moment
    assert pytest.approx(beam.moment(beam_length_ / 2), rel=TOL) == M_max


def test_simply_supported_center_max_deflection(beam_setup, EI, TOL):
    beam, beam_length_, load_ = beam_setup

    d_max = load_ * beam_length_**3 / (48 * EI)  # max displacement
    assert pytest.approx(beam.deflection(beam_length_ / 2), rel=TOL) == d_max
