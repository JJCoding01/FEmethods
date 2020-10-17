import pytest
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction
from femethods.elements import Beam


@pytest.fixture()
def length():
    """basic fixture for common beam length"""
    yield 10


@pytest.fixture()
def load_magnitude():
    yield -100


@pytest.fixture()
def reaction_simple(length):
    """common reactions for simply supported beam"""
    yield [PinnedReaction(x) for x in [0, length]]


@pytest.fixture()
def reaction_fixed():
    """common fixed reaction at 0"""
    yield [FixedReaction(0)]


@pytest.fixture()
def load_centered(length, load_magnitude):
    yield [PointLoad(magnitude=load_magnitude, location=length / 2)]


@pytest.fixture()
def beam_simply_supported(length, reaction_simple, load_centered):
    yield Beam(length=length, loads=load_centered, reactions=reaction_simple)


@pytest.fixture()
def beam_fixed(length):
    yield Beam(
        length=length, loads=[PointLoad(-100, length)], reactions=[FixedReaction(0)]
    )
