"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest
from settings import TOL, E, Ixx

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam_setup(beam_length, load):
    a = beam_length / 4  # location of first load from right
    b = beam_length / 5  # location of second load from left

    p = [PointLoad(magnitude=load, location=x) for x in [a, beam_length - b]]
    r = [PinnedReaction(x) for x in [0, beam_length]]
    beam = Beam(length=beam_length, loads=p, reactions=r, E=E, Ixx=Ixx)
    yield beam, beam_length, load, a, b


# noinspection PyPep8Naming
@pytest.mark.parametrize("reaction_index", (0, 1))
def test_simply_supported_eq_non_symmetric_reaction_force(
    reaction_index, beam_setup
):
    beam, beam_length, load, a, b = beam_setup

    R1 = -load / beam_length * (beam_length - a + b)
    R2 = -load / beam_length * (beam_length + a - b)
    R = [R1, R2]
    assert (
        pytest.approx(beam.reactions[reaction_index].force, rel=TOL)
        == R[reaction_index]
    )


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_eq_non_symmetric_reaction_moment_0(
    reaction_index, beam_setup
):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


# noinspection PyPep8Naming
@pytest.mark.parametrize("location", ("load1", "center", "load2"))
def test_simply_supported_eq_non_symmetric_moment(location, beam_setup):
    beam, beam_length, load, a, b = beam_setup

    R1 = -load / beam_length * (beam_length - a + b)
    R2 = -load / beam_length * (beam_length + a - b)

    M1 = R1 * a  # moment at first load
    x = beam_length / 2
    Mx = R1 * x + load * (x - a)  # moment at center
    M2 = R2 * b  # moment at second load
    if location == "load1":
        assert pytest.approx(beam.moment(a), rel=TOL) == M1
    if location == "center":
        assert pytest.approx(beam.moment(x), rel=TOL) == Mx
    if location == "load2":
        assert pytest.approx(beam.moment(beam_length - b), rel=TOL) == M2
