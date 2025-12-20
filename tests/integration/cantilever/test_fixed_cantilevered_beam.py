"""
Functional tests for beams with fixed supports

https://www.structx.com/Beam_Formulas_022.html

"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction
from tests.factories import MeshFactory


@pytest.fixture()
def beam_setup(beam_length, load, E, I):
    """Cantilever beam with load at free end"""

    mesh = MeshFactory(
        length=beam_length,
        locations=[0, beam_length],
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        length=beam_length,
        loads=[PointLoad(magnitude=load, location=0)],
        reactions=[FixedReaction(beam_length)],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, load


def test_cantilevered_beam_max_moment(beam_setup, TOL):
    """
    fixed beam with concentrated load at free end
    """
    beam, L, P = beam_setup
    # noinspection PyPep8Naming
    M_max = P * L  # at fixed end
    assert pytest.approx(beam.moment(L), rel=TOL) == M_max


def test_cantilevered_beam_load_max_deflection(beam_setup, EI, TOL):
    """
    fixed beam with concentrated load at free end
    """
    beam, L, P = beam_setup

    d_max = P * L**3 / (3 * EI)  # at free end
    assert pytest.approx(beam.deflection(0), rel=TOL) == d_max


def test_cantilevered_beam_load_moment_at_free_end(beam_setup):
    """
    fixed beam with concentrated load at free end
    """
    beam = beam_setup[0]
    assert pytest.approx(beam.moment(0), abs=1.5) == 0
