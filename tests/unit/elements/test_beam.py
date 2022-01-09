# pylint: disable=missing-function-docstring
import numpy as np
import pytest

from femethods.elements import Beam
from femethods.loads import MomentLoad, PointLoad
from femethods.reactions import FixedReaction


@pytest.mark.parametrize("magnitude", [5, 7, 10])
def test_multi_load_node(magnitude):

    # all loads at free tip
    loads = [PointLoad(magnitude, location=10), MomentLoad(magnitude, location=10)]
    beam = Beam(length=10, loads=loads, reactions=[FixedReaction(0)])

    # calculate force vector acting on each node
    p_vec = np.matmul(beam.stiffness_global(), beam.node_deflections).flatten()

    p_vec_expected = magnitude * np.array([-1, -10, 1, 1])
    p_vec_expected[1] -= magnitude

    assert np.allclose(p_vec, p_vec_expected)
