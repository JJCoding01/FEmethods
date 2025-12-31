"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.structx.com/Beam_Formulas_008.html
"""

import numpy as np
import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction
from tests.factories import MeshFactory


@pytest.fixture(params=(25, 50, 75))
def load_location(request):
    return request.param


@pytest.fixture()
def beam_setup(beam_length, load, load_location, E, I):
    """Simply supported beam with offset point load"""

    mesh = MeshFactory(
        length=beam_length,
        locations=np.linspace(0, beam_length, num=6, endpoint=True),
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        beam_length,
        loads=[PointLoad(load, load_location)],
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load, load_location


# noinspection PyPep8Naming
def test_simply_supported_offset_reaction_force(beam_setup, TOL):
    beam, beam_length_, load_, load_location_ = beam_setup

    a = load_location_
    b = beam_length_ - a
    R1 = -load_ * b / beam_length_
    R2 = -load_ * a / beam_length_

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_offset_reaction_moment_0(reaction_index, beam_setup):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


# noinspection PyPep8Naming
def test_simply_supported_offset_moment(beam_setup, TOL):
    beam, beam_length_, load_, load_location_ = beam_setup

    a = load_location_
    b = beam_length_ - a

    M_loc = -load_ * a * b / beam_length_  # moment at load

    assert pytest.approx(beam.moment(load_location_), rel=TOL) == M_loc


def test_simply_supported_offset_max_deflection(beam_setup, EI, TOL):
    beam, beam_length_, load_, load_location_ = beam_setup

    a = load_location_

    b = beam_length_ - a
    d_loc = load_ * a**2 * b**2 / (3 * EI * beam_length_)  # deflection at load

    assert pytest.approx(beam.deflection(load_location_), rel=TOL) == d_loc
