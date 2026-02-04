import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import PinnedReaction


@pytest.fixture()
def beam():
    beam_ = Beam(
        length=100,
        loads=[PointLoad(500, location=50)],
        reactions=[PinnedReaction(x) for x in [0, 100]],
    )
    return beam_


def test_init_beam_solved(beam):
    for reaction in beam.reactions:
        assert reaction.force is not None


def test_updated_beam_unsolved(beam):
    beam.loads = [PointLoad(500, 25)]

    # reactions should have been invalidated since beam structure changed but an
    # explicit solve was not initiated
    for reaction in beam.reactions:
        assert reaction.force is None


def test_solve_updated_beam(beam):
    beam.loads = [PointLoad(500, 25)]

    beam.solve()
    for reaction in beam.reactions:
        assert reaction.force is not None
