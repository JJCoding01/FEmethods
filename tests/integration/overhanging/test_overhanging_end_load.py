"""
Functional tests for overhanging beam with two pinned reactions

https://www.structx.com/Beam_Formulas_026.html
"""

import numpy as np
import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction
from tests.factories import MeshFactory


@pytest.fixture()
def beam_setup(beam_length, load, overhang_length, E, I):
    """Simply supported beam with center point load"""

    # total beam length
    L = beam_length + overhang_length

    mesh = MeshFactory(
        length=L,
        locations=[0, beam_length, L],
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        length=L,
        loads=[PointLoad(magnitude=load, location=L)],
        reactions=[PinnedReaction(x) for x in [0, beam_length]],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    # convert L to the length of the supported span
    # noinspection PyPep8Naming
    L = L - overhang_length
    yield beam, L, load, overhang_length


def test_overhang_reaction_force(beam_setup, TOL):
    beam, L, P, a = beam_setup

    # noinspection PyPep8Naming
    R1 = P * a / L  # lbs, reactions
    R2 = P / L * (L + a)
    assert pytest.approx(beam.reactions[0].force, rel=TOL) == R1
    assert pytest.approx(beam.reactions[1].force, rel=TOL) == -R2


def test_overhang_max_moment(beam_setup, TOL):
    beam, L, P, a = beam_setup

    # noinspection PyPep8Naming
    M_max = P * a  # psi, maximum moment (at R2
    assert pytest.approx(beam.moment(L), rel=TOL) == -M_max


def test_overhang_max_deflection_between_supports(beam_setup, EI, TOL):
    beam, L, P, a = beam_setup

    x = L / np.sqrt(3)
    d_max = -P * a * L**2 / (9 * EI * np.sqrt(3))  # max displacement
    assert pytest.approx(beam.deflection(x), rel=TOL) == d_max


def test_overhang_max_deflection_overhang(beam_setup, EI, TOL):
    beam, L, P, a = beam_setup

    x = a
    d_max = P * a**2 / (3 * EI) * (L + a)  # max displacement
    assert pytest.approx(beam.deflection(L + x), rel=TOL) == d_max
