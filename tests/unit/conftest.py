# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name


import matplotlib

# disable pylint "redefined-outer-name" error as this is triggered by using pytest
# fixtures
import pytest

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction

# Use static backend for matplotlib to avoid tkinter issues when running tests
# that generate a plot. Since the window isn't needed for the tests, there's
# no reason to create it. Use a simple backend to keep tests streamlined.
# https://matplotlib.org/stable/users/explain/figure/backends.html
matplotlib.use("Agg")


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
        length=length,
        loads=[PointLoad(-100, length)],
        reactions=[FixedReaction(0)],
    )
