"""
Examples for FEMethods showing how to use the module

"""

from femethods.elements import Beam
from femethods.loads import ConstantDistributedLoad, PointLoad
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


def example_3():
    """
    Cantilevered Beam with 3 Pinned Supports and End Loading
    """
    print("=" * 79)
    print("Example 3")
    print("Show an example simply supported beam with distributed load\n")

    beam_len = 10
    w = -2
    p = w * beam_len
    # print(f'COMMON SETUP',
    #       f'L = {beam_len}',
    #       f'W = {w}',
    #       f'P = {p}',
    #       '-' * 79,
    #       sep='\n\t')

    # common reactions
    pr = [PinnedReaction(x) for x in [0, beam_len]]
    dr = [PinnedReaction(x) for x in [0, beam_len]]
    # print('INPUT REACTIONS',
    #       f'reactions: {pr}',
    #       f'forces: {[r.force for r in pr]}',
    #       f'moments: {[r.force for r in pr]}',
    #       '-' * 79,
    #       sep='\n\t')

    # loads
    pl = PointLoad(magnitude=p, location=beam_len / 2)
    dl = ConstantDistributedLoad(W=w, start=0, stop=beam_len)

    # print('INPUT LOADS',
    #       f'point load: {pl}',
    #       f'\tpoint load magnitude: {pl.magnitude}',
    #       f'\tpoint load location: {pl.location}',
    #       f'distributed load: {dl}',
    #       f'\tdistribted equivalent: {dl.equivalent}',
    #       f'\tdistributed load magnitude: {dl.magnitude}',
    #       f'\tdistributed load location: {dl.location}',
    #       '-' * 79,
    #       sep='\n\t'
    #       )

    # beams
    bp = Beam(beam_len, loads=[pl], reactions=pr)
    bd = Beam(beam_len, loads=[dl], reactions=dr)

    # print('beam loading equivalent', pl == dl.equivalent)
    # print('...SOLVE BEAMS...')
    print('=' * 10, 'POINT LOAD', '=' * 10)
    bp.solve()
    print('=' * 10, 'DISTRIBUTED LOAD', '=' * 10)
    bd.solve()
    # print('beam loading equivalent', pl == dl.equivalent)

    # print('pinned reactions', bp.reactions)
    # print('distri reactions', bd.reactions)

    print('SOLVED REACTIONS',
          'Point Loads'
          f'\treactions: {bp.reactions}',
          f'\tforces: {[r.force for r in bp.reactions]}',
          f'\tmoments: {[r.moment for r in bp.reactions]}',
          'Distributed Load',
          f'\treactions: {bd.reactions}',
          f'\tforces: {[r.force for r in bd.reactions]}',
          f'\tmoments: {[r.moment for r in bd.reactions]}',
          '-' * 79,
          sep='\n\t')

    # bp.plot()
    # bd.plot()
    #
    # bd.show()

    # print('pinned reactions', [r.force for r in bp.reactions])
    # print('distri reactions', [r.force for r in bd.reactions])


def example_4():
    beam_len = 30
    reactions = [PinnedReaction(x) for x in [0, 15, 30]]

    beam = Beam(30,
                loads=[ConstantDistributedLoad(0, 30, W=-3)],
                reactions=[PinnedReaction(x) for x in [0, 15, 30]])

    eq_beam = Beam(30,
                   loads=[PointLoad(magnitude=-3, location=x) for x in [7.5, 22.5]],
                   reactions=[PinnedReaction(x) for x in [0, 15, 30]])

    beam.solve()
    eq_beam.solve()
    print(beam.loads[0].equivalent)
    print('=' * 79)
    print(eq_beam)


if __name__ == "__main__":
    # example_1()
    # example_2()
    # example_3()
    example_4()
