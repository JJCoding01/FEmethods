"""
Examples for FEMethods showing how to use the module

"""

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


def example_1():
    """
    Cantilevered Beam with Fixed Support and End Loading
    """
    print("=" * 79)
    print("Example 1")
    print(
        "Show an example with a cantilevered beam with a fixed support and "
        "point load at the end\n"
    )

    beam_len = 10
    # Note that both the reaction and load are both lists. They must always be
    # given to Beam as a list,
    r = [FixedReaction(0)]  # define reactions as list
    p = [PointLoad(magnitude=-2, location=beam_len)]  # define loads as list

    b = Beam(beam_len, loads=p, reactions=r, E=29e6, Ixx=125)

    # an explicit solve is required to calculate the reaction values
    b.solve()
    print(b)


def example_2():
    """
    Cantilevered Beam with 3 Pinned Supports and End Loading
    """
    print("=" * 79)
    print("Example 2")
    print("Show an example with 3 Pinned Supports and End Loading\n")
    beam_len = 10

    # Note that both the reaction and load are both lists. They must always be
    # given to Beam as a list,
    r = [PinnedReaction(0), PinnedReaction(2), PinnedReaction(6)]  # define reactions
    p = [PointLoad(magnitude=-2, location=beam_len)]  # define loads

    b = Beam(beam_len, loads=p, reactions=r, E=29e6, Ixx=125)

    # an explicit solve is required to calculate the reaction values
    b.solve()
    print(b)


if __name__ == "__main__":
    example_1()
    example_2()
