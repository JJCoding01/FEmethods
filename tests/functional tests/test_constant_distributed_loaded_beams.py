"""
Functional tests for beams with distributed loads

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

"""

# from settings import L, E, I, EI

# from .validate import validate

from femethods.loads import ConstantDistributedLoad, PointLoad
from femethods.reactions import PinnedReaction, FixedReaction
from femethods.elements import Beam

E = 29e6  # psi, Young's modulus
Ixx = 350  # in^4 area moment of inertia of beam
EI = E * Ixx  # common constant

def test_simple_beam_uniformly_distributed_load():
    """
    Uniformly distributed load
    Load case 1
    """

    beam_len = 120  # beam length
    w = -25  # load intensity

    r_act = w * beam_len / 2  # exact reaction values
    v_x = lambda x: w * (beam_len/2 - x) # shear force at x
    m_max = w * beam_len ** 2 / 8  # max moment (at center)
    m_x = lambda x: w * x / 2 *(beam_len - x)  # moment at x
    delta_max = 5 * w * beam_len **4 / (384 * E * Ixx)

    b = Beam(length=beam_len,
             # loads=[ConstantDistributedLoad(W=w, start=0, stop=beam_len)],
             loads=[PointLoad(location=120/2, magnitude=-25*120)],
             reactions=[PinnedReaction(x) for x in [0, beam_len]],
             E=E,
             Ixx=Ixx
             )
    b.solve()
    print(b.node_deflections)

    for r in b.reactions:
        assert r.moment == 0, "calculated moment not 0 for pinned reaction"
        assert r.force == r_act, "calculated reaction does not match exact force"

    # print(b.loads[0].equivalent)
    # # print(r_act, [r.force for r in b.reactions])
    # # print(v_x)
    # print(m_max)
    # print(delta_max)
