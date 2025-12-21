"""
Functional tests for overhanging beam with two pinned reactions

https://www.structx.com/Beam_Formulas_028.html
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
def beam_setup(beam_length, load, load_location, overhang_length, E, I):
    """Simply supported beam with offset point load"""

    # total beam length
    L = beam_length + overhang_length
    a = load_location
    b = L - a

    mesh = MeshFactory(
        length=L,
        locations=[0, beam_length, L],
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        length=L,
        loads=[PointLoad(magnitude=load, location=a)],
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load, (a, b), overhang_length


# noinspection PyPep8Naming
def test_overhanging_offset_reaction_force(beam_setup, TOL):
    beam, L, P, (a, b), c = beam_setup

    R1 = P * b / L
    R2 = P * a / L

    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == R2


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_overhanging_offset_reaction_moment_0(reaction_index, beam_setup):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


def test_overhanging_offset_max_moment(beam_setup):
    beam, L, P, (a, b), c = beam_setup

    M_max = P * a * b / L
    assert pytest.approx(beam.moment(a), abs=1) == M_max


def test_overhanging_offset_deflection(beam_setup, EI, TOL):
    beam, L, P, (a, b), c = beam_setup

    d_loc = P * a ** 2 * b ** 2 / (3 * EI * L)  # deflection at load

    assert pytest.approx(beam.deflection(a), rel=TOL) == d_loc


def test_overhanging_offset_deflection_max(beam_setup, EI, TOL):
    beam, L, P, (a, b), c = beam_setup

    # TODO: skip this test when a <= b since it doesn't apply
    #   make sure that at least for some cases, this test will apply
    assert a > b

    x = np.sqrt(a * (a + 2 * b) / 3)
    d_max = P * a * b * (a + 2 * b) * np.sqrt(3 * a *(a + 2 * b)) / (27 * EI * L)  # deflection at load

    assert pytest.approx(beam.deflection(x), rel=TOL) == d_max
