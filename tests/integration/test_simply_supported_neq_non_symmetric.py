"""
Functional tests for simply supported beams (beams with two pinned reactions)

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf
"""

import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction

from .settings import E, Ixx, TOL


# noinspection PyPep8Naming
@pytest.fixture(params=(0.50, 0.75, 1, 1.25, 1.50))
def beam_setup(request, beam_length, load):
    load_ratio = request.param
    P1 = load
    P2 = P1 * load_ratio

    a = beam_length / 4  # location of first load from right
    b = beam_length / 5  # location of second load from left

    p = [
        PointLoad(magnitude=P1, location=a),
        PointLoad(magnitude=P2, location=beam_length - b),
    ]
    r = [PinnedReaction(x) for x in [0, beam_length]]
    beam = Beam(length=beam_length, loads=p, reactions=r, E=E, Ixx=Ixx)
    yield beam, beam_length, load, P1, P2, a, b


# noinspection PyPep8Naming
@pytest.mark.parametrize("reaction_index", (0, 1))
def test_simply_supported_neq_non_symmetric_reaction_force(reaction_index, beam_setup):
    beam, beam_length, load, P1, P2, a, b = beam_setup

    R1 = -(P1 * (beam_length - a) + P2 * b) / beam_length
    R2 = -(P1 * a + P2 * (beam_length - b)) / beam_length
    R = [R1, R2]
    assert (
        pytest.approx(beam.reactions[reaction_index].force, rel=TOL)
        == R[reaction_index]
    )


@pytest.mark.parametrize("reaction_index", [0, 1])
def test_simply_supported_neq_non_symmetric_reaction_moment_0(
    reaction_index, beam_setup
):
    beam = beam_setup[0]
    assert pytest.approx(beam.reactions[reaction_index].moment, abs=1) == 0


# noinspection PyPep8Naming
@pytest.mark.parametrize("location", ("load1", "center", "load2"))
def test_simply_supported_eq_non_symmetric_moment(location, beam_setup):
    beam, beam_length, load, P1, P2, a, b = beam_setup
    R1 = -(P1 * (beam_length - a) + P2 * b) / beam_length
    R2 = -(P1 * a + P2 * (beam_length - b)) / beam_length

    M1 = R1 * a
    x = beam_length / 2
    Mx = R1 * x + P1 * (x - a)
    M2 = R2 * b
    if location == "load1":
        assert pytest.approx(beam.moment(a), rel=TOL) == M1
    if location == "center":
        assert pytest.approx(beam.moment(x), rel=TOL) == Mx
    if location == "load2":
        assert pytest.approx(beam.moment(beam_length - b), rel=TOL) == M2
