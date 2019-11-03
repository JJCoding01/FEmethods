"""
Functional tests for beams with distributed loads

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

"""

import pytest
from settings import TOL

from femethods.elements import Beam
from femethods.loads import ConstantDistributedLoad
from femethods.reactions import FixedReaction, PinnedReaction

# from .validate import validate


E = 29e6  # psi, Young's modulus
Ixx = 350  # in^4 area moment of inertia of beam
EI = E * Ixx  # common constant


def test_simply_supported_beam_uniformly_distributed_load():
    """
    Uniformly distributed load
    Load case 1
    """

    beam_len = 120  # beam length
    w = -25  # load intensity

    r_act = -w * beam_len / 2  # exact reaction values
    v_x = lambda x: w * (beam_len / 2 - x)  # shear force at x
    m_max = w * beam_len ** 2 / 8  # max moment (at center)
    m_x = lambda x: w * x / 2 * (beam_len - x)  # moment at x
    delta_max = 5 * w * beam_len ** 4 / (384 * E * Ixx)

    b = Beam(
        length=beam_len,
        loads=[ConstantDistributedLoad(W=w, start=0, stop=beam_len)],
        reactions=[PinnedReaction(x) for x in [0, beam_len]],
        E=E,
        Ixx=Ixx,
    )
    b.solve()

    for r in b.reactions:
        assert (
                pytest.approx(r.moment, TOL) == 0
        ), "calculated moment not 0 for pinned reaction"
        assert (
                pytest.approx(r.force, TOL) == r_act
        ), "calculated reaction does not match exact force"


def test_simply_supported_beam_partially_distributed_load_at_end():
    """
    load case 3
    """

    beam_len = 25
    w = -25
    w_len = 8

    r_act = [
        (-w * w_len) / (2 * beam_len) * (2 * beam_len - w_len),
        (-w * w_len ** 2) / (2 * beam_len),
    ]
    # vx = lambda x: r1 - w * x

    beam = Beam(
        beam_len,
        loads=[ConstantDistributedLoad(start=0, stop=w_len, W=w)],
        reactions=[PinnedReaction(x) for x in [0, beam_len]],
    )

    beam.solve()
    msg = "pinned force reaction for distributed load does not match expected"
    for ra, re in zip(r_act, beam.reactions):
        assert pytest.approx(re.force, TOL) == ra, msg
        assert (
                pytest.approx(re.moment, TOL) == 0
        ), "moment not equal to 0 for pinned reaction"


def test_fixed_beam_constant_distributed_load():
    """
    test case 12
    """

    beam_len = 15
    w = -25

    r = -w * beam_len
    m = w * beam_len ** 2 / 2
    beam = Beam(
        beam_len,
        loads=[ConstantDistributedLoad(W=w, start=0, stop=beam_len)],
        reactions=[FixedReaction(beam_len)],
    )
    beam.solve()

    assert pytest.approx(beam.reactions[0].force, TOL) == r, (
        "reaction force does not match " "expected"
    )
    assert pytest.approx(beam.reactions[0].moment, TOL) == m, (
        "reaction moment does not match " "expected"
    )
