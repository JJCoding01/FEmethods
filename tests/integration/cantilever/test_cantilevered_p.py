"""
Functional tests for cantilevered beam with point load at any point

https://www.structx.com/Beam_Formulas_021.html
"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction
from tests.factories import MeshFactory


@pytest.fixture(params=(0.125, 0.25, 0.5, 0.75))
def beam_setup(request, beam_length, load, E, I):
    """Cantilever beam with load at free end"""
    L = beam_length
    a = request.param * L  # distance from free end to load
    b = L - a  # distance from load to fixed end
    P = load

    mesh = MeshFactory(
        length=beam_length,
        locations=[0, a, beam_length],
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=a)],
        reactions=[FixedReaction(beam_length)],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load, a, b


def test_cantilevered_beam_max_moment(beam_setup, TOL):
    """
    fixed beam with concentrated load at free end
    """
    beam, L, P, a, b = beam_setup
    # noinspection PyPep8Naming
    M_max = P * b  # at fixed end
    assert pytest.approx(beam.moment(L), rel=TOL) == -M_max


def test_cantilevered_d_max(beam_setup, EI, TOL):
    beam, L, P, a, b = beam_setup

    d_max = P * b**2 / (6 * EI) * (3 * L - b)  # at free end
    assert pytest.approx(beam.deflection(0), rel=TOL) == d_max


def test_cantilevered_d_a(beam_setup, EI, TOL):
    beam, L, P, a, b = beam_setup

    d = P * b**3 / (3 * EI)  # at point load
    assert pytest.approx(beam.deflection(a), rel=TOL) == d
