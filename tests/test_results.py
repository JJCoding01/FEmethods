"""
This test module test the validity of the final results for specific cases
"""

import unittest

import numpy as np

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


class TestSimplySupportedBeam(unittest.TestCase):

    def setUp(self):
        E = 29e6
        Ixx = 400

        self.reactions = [PinnedReaction(0), PinnedReaction(10)]
        self.loads = [PointLoad(1000, location=5)]
        self.beam = Beam(length=10, loads=self.loads, reactions=self.reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_simply_supported_beam_offset_load(self):

        R1 = [-750, -500, -250]
        R2 = [-250, -500, -750]
        offsets = [2.5, 5, 7.5]
        for offset, r1, r2 in zip(offsets, R1, R2):
            self.beam.loads[0].location = offset
            self.beam.solve()

            r_calc1, r_calc2 = self.reactions
            self.assertAlmostEqual(r_calc1.value[0], r1, places=5)
            self.assertAlmostEqual(r_calc2.value[0], r2, places=5)

    def test_load_on_support(self):
        for k in range(2):
            self.beam.loads[0].location = self.beam.reactions[k].location
            self.beam.solve()
            self.assertAlmostEqual(self.beam.reactions[k].value[0],
                                   -self.beam.loads[0].value,
                                   msg='Support directly under load should carry all the load')
            self.assertAlmostEqual(self.beam.reactions[k - 1].value[0],
                                   0, msg='When load is directly over support, the opposite support should not have '
                                          'any load')

    def test_zero_moment(self):
        # moment reaction for a pinned joint must be zero

        for x in np.linspace(0, self.beam.length, 5):
            self.beam.loads[0].location = x
            self.beam.solve()
            reactions = self.reactions

            for r in reactions:
                self.assertAlmostEqual(r.value[1], 0, places=7,
                                       msg='Moment should be zero for pinned reaction')


class TestFixedSupportBeam(unittest.TestCase):

    def setUp(self):
        E = 29e6
        Ixx = 400

        self.reactions = [FixedReaction(0)]
        self.loads = [PointLoad(1000, location=10)]
        self.beam = Beam(length=10, loads=self.loads, reactions=self.reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_force_at_end(self):
        # for a single load, and single fixed end, the force at the reaction
        # must be equal to and opposite the load acting on the beam
        r = self.reactions[0]
        self.assertAlmostEqual(r.value[0], -self.loads[0].value)

    def test_moment_at_end(self):
        # for a single load, and single fixed end, the moment at the reaction
        # must be equal to force times the moment arm
        r = self.reactions[0]
        m = -self.loads[0].value * self.loads[0].location
        self.assertAlmostEqual(r.value[1], m)
