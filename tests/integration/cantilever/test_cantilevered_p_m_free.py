"""
Functional tests for cantilevered beam

https://www.structx.com/Beam_Formulas_023.html

"""

import numpy as np
import pytest

from femethods.elements import Beam
from femethods.loads import MomentLoad, PointLoad
from femethods.reactions import FixedReaction
from tests.factories import MeshFactory

# TODO: update setup for vertical deflection with no-rotation
#   This was originally misunderstood as a cantilevered beam with end point
#   load and end moment. The end moment is used specifically to prevent all
#   rotation, it is not an applied moment.

pytest.skip(
    "Skip these tests. "
    "These are for a beam with vertical displacement with no rotation; "
    "test setup is for a point load and moment load at the end",
    allow_module_level=True,
)


@pytest.fixture()
def beam_setup(beam_length, load, E, I):
    """Cantilever beam with load and moment at free end"""

    P = load
    M = -load
    mesh = MeshFactory(
        length=beam_length,
        locations=np.linspace(0, beam_length, num=2),
        node_dof=2,
        max_element_length=None,
        min_element_count=None,
    )

    beam = Beam(
        length=beam_length,
        loads=[
            PointLoad(magnitude=P, location=0),
            MomentLoad(magnitude=M, location=0),
        ],
        reactions=[FixedReaction(beam_length)],
        mesh=mesh,
        E=E,
        Ixx=I,
    )
    yield beam, beam_length, (P, M)


def test_cantilevered_beam_reaction(beam_setup, TOL):
    beam, L, (P, M) = beam_setup
    assert pytest.approx(beam.reactions[0].force, rel=TOL) == -P
    assert pytest.approx(beam.reactions[0].moment, rel=TOL) == P * L / 2


def test_cantilevered_beam_max_moment(beam_setup, TOL):
    """
    fixed beam with concentrated load at free end
    """
    beam, L, (P, M) = beam_setup

    # noinspection PyPep8Naming
    M_max = P * L / 2  # both ends
    assert pytest.approx(beam.moment(L), rel=TOL) == M_max
    assert pytest.approx(beam.moment(0), rel=TOL) == M_max


def test_cantilevered_beam_load_max_deflection(beam_setup, EI, TOL):
    """
    fixed beam with concentrated load at free end
    """
    beam, L, (P, M) = beam_setup

    d_max = P * L**3 / (12 * EI)  # at free end
    assert pytest.approx(beam.deflection(0), rel=TOL, abs=0.100) == d_max
