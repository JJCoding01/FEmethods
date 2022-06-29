"""
Examples for FEMethods showing how to use the module

"""
import numpy as np

from femethods.elements import Beam
from femethods.loads import PointLoad, MomentLoad
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
    P = -200
    E = 29e6
    I = 125
    # Note that both the reaction and load are both lists. They must always be
    # given to Beam as a list,
    r = [FixedReaction(beam_len)]  # define reactions as list
    p = [PointLoad(magnitude=P, location=0)]  # define loads as list

    b = Beam(beam_len, loads=p, reactions=r, E=E, Ixx=I)

    # an explicit solve is required to calculate the reaction values
    b.solve()
    print(b)

    fig, axes = b.plot()
    x = np.linspace(0, beam_len, 100)
    Mx = P * x
    Vx = P * np.ones(np.size(x))
    dx = (P / (6 * E * I)) * (2 * beam_len**3 - 3 * beam_len**2 * x + x**3)
    axes[0].plot(x, Vx)
    axes[1].plot(x, Mx)
    axes[2].plot(x, dx)
    b.show()



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


def example_3():
    """
    Cantilevered Beam with Fixed Support and Force and Moment at end
    """
    print("=" * 79)
    print("Example 3")
    print(
        "Show an example with a cantilevered beam with a fixed support and "
        "point load and moment load at the end\n"
    )

    beam_len = 10
    # Note that both the reaction and load are both lists. They must always be
    # given to Beam as a list,
    r = [FixedReaction(0)]  # define reactions as list

    p = [PointLoad(-2, beam_len), MomentLoad(-2, beam_len)]  # define loads as list

    # since the force and moment are acting at the same location, it can also be applied
    # using the base Load and defining the fm_factor, as shown below. Defining the loads
    # this way will give the same results
    # from femethods.loads import Load
    # p = [Load(magnitude=1, location=beam_len, fm_factor=(-2, -2))]

    b = Beam(beam_len, loads=p, reactions=r, E=29e6, Ixx=125)
    print(b)


if __name__ == "__main__":
    example_1()
    example_2()
    example_3()
