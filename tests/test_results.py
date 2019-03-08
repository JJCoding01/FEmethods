"""
This test module test the validity of the final results for specific cases
"""

import unittest

import numpy as np

from femethods.elements import Beam
from femethods.loads import PointLoad
from femethods.reactions import FixedReaction, PinnedReaction

REACTION_MSG = 'Calculated reactions do not match expected reactions'
NON_ZERO_MOMENT = 'Moment for pinned reaction must be zero'


class TestSimplySupportedBeam(unittest.TestCase):
    """Verify results for a simply supported beam"""

    def setUp(self):
        """Define a standard beam, 10ft (120 in) long, with a single point
        load acting down in the center of the span. (Each test case will adjust
        load position as required.

        """
        self.beam = None
        E = 29e6  # [psi] Young's modulus for steel
        Ixx = 400  # [in^4] Area moment of inertia in in**4 for arbitrary shape

        self.reactions = [PinnedReaction(0), PinnedReaction(120)]
        self.loads = [PointLoad(-1000, location=60)]
        self.beam = Beam(length=120, loads=self.loads,
                         reactions=self.reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_simply_supported_beam_offset_load(self):
        """test several locations for the load, offset to the left, centered
        and offset to the right. This will combine multiple test cases into a
        single unit, simplifying the testing code.
        """

        R1 = [750, 500, 250]  # known reaction values
        R2 = [250, 500, 750]  # known reaction values
        offsets = [30, 60, 90]  # location of load from end

        error_msg = 'Calculated reactions do not match expected reactions'
        for offset, r1_e, r2_e in zip(offsets, R1, R2):
            self.beam.loads[0].location = offset
            self.beam.solve()

            r_calc1, r_calc2 = self.reactions
            self.beam.moment(offset)
            self.assertAlmostEqual(r_calc1.value[0], r1_e,
                                   places=5, msg=REACTION_MSG)
            self.assertAlmostEqual(r_calc2.value[0], r2_e,
                                   places=5, msg=REACTION_MSG)

    def test_simply_supported_beam_equal_symmetrical_loads(self):
        loads = [PointLoad(-1000, 30), PointLoad(-1000, 90)]
        self.beam.loads = loads
        print(self.beam.loads)
        self.beam.solve()

        for r in self.beam.reactions:
            self.assertAlmostEqual(r.value[0], 1000,
                                   msg=REACTION_MSG)
            self.assertAlmostEqual(r.value[1], 0,
                                   msg=NON_ZERO_MOMENT)

    def test_simply_supported_beam_equal_nonsymmetrical_loads(self):
        loads = [PointLoad(-1000, 40), PointLoad(-1000, 100)]
        self.beam.loads = loads
        self.beam.solve()

        L = self.beam.length
        a = self.beam.loads[0].location
        b = L - self.beam.loads[1].location
        P = -self.beam.loads[0].value

        R1 = P / L * (L - a + b)
        R2 = P / L * (L - b + a)
        R = [R1, R2]

        for r, Re in zip(self.beam.reactions, R):
            self.assertAlmostEqual(r.value[0], Re,
                                   msg=REACTION_MSG)
            self.assertAlmostEqual(r.value[1], 0,
                                   msg=NON_ZERO_MOMENT)

    def test_simply_supported_beam_unequal_nonsymmetrical_loads(self):
        loads = [PointLoad(-800, 40), PointLoad(-1200, 100)]
        self.beam.loads = loads
        self.beam.solve()

        L = self.beam.length
        a = self.beam.loads[0].location
        b = L - self.beam.loads[1].location
        P1, P2 = -self.beam.loads[0].value, -self.beam.loads[1].value

        R1 = (P1 * (L - a) + P2 * b) / L
        R2 = (P1 * a + P2 * (L - b)) / L
        R = [R1, R2]

        for r, Re in zip(self.beam.reactions, R):
            self.assertAlmostEqual(r.value[0], Re,
                                   msg=REACTION_MSG)
            self.assertAlmostEqual(r.value[1], 0,
                                   msg=NON_ZERO_MOMENT)

    def test_load_aligned_with_support(self):
        """Test the case where the load is aligned with the support.

        Do this for both supports. When this is the case, the support that is
        under the load should carry all the load, and the opposite support
        should not carry any load.
        """
        for k in range(2):
            self.beam.loads[0].location = self.beam.reactions[k].location
            self.beam.solve()
            self.assertAlmostEqual(self.beam.reactions[k].value[0],
                                   -self.beam.loads[0].value, places=5,
                                   msg='Support directly under load should '
                                       'carry all the load')
            self.assertAlmostEqual(self.beam.reactions[k - 1].value[0],
                                   0, places=5,
                                   msg='When load is directly over support'
                                       ', opposite support should not '
                                       'have any load')

    def test_zero_moment(self):
        # moment reaction for a pinned joint must be zero

        for x in np.linspace(0, self.beam.length, 5):
            self.beam.loads[0].location = x
            self.beam.solve()
            reactions = self.reactions

            for r in reactions:
                self.assertAlmostEqual(r.value[1], 0, places=5,
                                       msg=NON_ZERO_MOMENT)


class TestSimplySupportedBeamWithOverhang(unittest.TestCase):

    def setUp(self):
        self.beam = None
        E = 29e6  # [psi] Young's modulus for steel
        Ixx = 400  # [in^4] Area moment of inertia in in**4 for arbitrary shape

        self.reactions = [PinnedReaction(0), PinnedReaction(100)]
        self.loads = [PointLoad(-1000, location=50)]
        self.beam = Beam(length=120, loads=self.loads,
                         reactions=self.reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_load_at_end_of_overhang(self):
        self.beam.loads[0].location = 120
        self.beam.solve()

        P = -self.beam.loads[0].value
        L = self.beam.reactions[1].location
        a = self.beam.length - L

        R1 = -P * a / L
        R2 = P / L * (L + a)
        R = [R1, R2]

        for r, Re in zip(self.beam.reactions, R):
            self.assertAlmostEqual(r.value[0], Re,
                                   msg=REACTION_MSG)
            self.assertAlmostEqual(r.value[1], 0,
                                   msg=NON_ZERO_MOMENT)

    def test_load_between_supports(self):

        self.beam.loads[0].location = 60
        self.beam.solve()

        a = self.beam.loads[0].location
        b = self.beam.reactions[1].location - a
        P = -self.beam.loads[0].value
        L = self.beam.reactions[1].location

        R1 = P * b / L
        R2 = P * a / L
        R = [R1, R2]

        for r, Re in zip(self.beam.reactions, R):
            self.assertAlmostEqual(r.value[0], Re,
                                   msg=REACTION_MSG)
            self.assertAlmostEqual(r.value[1], 0,
                                   msg=NON_ZERO_MOMENT)


class TestFixedSupportBeam(unittest.TestCase):

    def setUp(self):
        self.beam = None
        E = 29e6
        Ixx = 400

        reactions = [FixedReaction(0)]
        loads = [PointLoad(-1000, location=120)]
        self.beam = Beam(length=120, loads=loads, reactions=reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_force_at_end(self):
        # for a single load, and single fixed end, the force at the reaction
        # must be equal to and opposite the load acting on the beam
        r = self.beam.reactions[0]
        self.assertAlmostEqual(r.value[0], -self.beam.loads[0].value)

    def test_moment_at_end(self):
        # for a single load, and single fixed end, the moment at the reaction
        # must be equal to force times the moment arm
        r = self.beam.reactions[0]
        m = -self.beam.loads[0].value * self.beam.loads[0].location
        self.assertAlmostEqual(r.value[1], m)

    def test_reactions_at_any_point(self):
        self.beam.loads[0].value = -1000
        self.beam.loads[0].location = 100
        L = self.beam.loads[0]
        self.beam.solve()

        self.assertAlmostEqual(self.beam.reactions[0].value[0],
                               -L.value,
                               msg=REACTION_MSG)
        self.assertAlmostEqual(L.value * L.location,
                               -1000 * 100,
                               msg=REACTION_MSG)


class TestFixedFixedBeam(unittest.TestCase):

    def setUp(self):
        self.beam = None
        E = 29e6
        Ixx = 400

        reactions = [FixedReaction(0), FixedReaction(120)]
        loads = [PointLoad(-1000, location=60)]
        self.beam = Beam(length=120, loads=loads, reactions=reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_fixedfixed_load_offset(self):

        offsets = [30, 60, 90]  # location of load from end
        L = self.beam.length
        P = -self.beam.loads[0].value
        for offset in offsets:
            a = offset
            self.beam.loads[0].location = a
            self.beam.solve()
            b = L - a

            R1 = P * b ** 2 / L ** 3 * (3 * a + b)
            R2 = P * a ** 2 / L ** 3 * (a + 3 * b)
            M1 = P * a * b ** 2 / L ** 2
            M2 = -P * a ** 2 * b / L ** 2

            R = [[R1, M1], [R2, M2]]

            for r, Re in zip(self.beam.reactions, R):
                for k in range(2):
                    self.assertAlmostEqual(r.value[k], Re[k], msg=REACTION_MSG)


class TestCompoundBeam(unittest.TestCase):

    def setUp(self):
        self.beam = None
        E = 29e6
        Ixx = 400

        reactions = [PinnedReaction(0), FixedReaction(120)]
        loads = [PointLoad(-1000, location=60)]
        self.beam = Beam(length=120, loads=loads, reactions=reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_load_offset(self):
        L = self.beam.length

        for offset in [25, 60, 87]:
            self.beam.loads[0].location = offset
            self.beam.solve()
            a = self.beam.loads[0].location
            b = L - a
            P = -self.beam.loads[0].value
            R1 = P * b ** 2 / (2 * L ** 3) * (a + 2 * L)  # pinned reaction
            M1 = 0  # pinned reaction
            R2 = P * a / (2 * L ** 3) * (3 * L ** 2 - a ** 2)  # fixed reaction
            M2 = -P * a * b / (2 * L ** 2) * (a + L)  # at fixed reaction

            R = [[R1, M1], [R2, M2]]

            for r, Re in zip(self.beam.reactions, R):
                for k in range(2):
                    self.assertAlmostEqual(r.value[k], Re[k], msg=REACTION_MSG)


class TestEqualSpansSingleLoad(unittest.TestCase):
    """test beam with three pinned reactions, and a single point load
    in the center of one of the spans"""

    def setUp(self):
        self.beam = None
        E = 29e6
        Ixx = 400

        reactions = [PinnedReaction(k) for k in [0, 60, 120]]
        loads = [PointLoad(-1000, location=30)]
        self.beam = Beam(length=120, loads=loads, reactions=reactions,
                         E=E, Ixx=Ixx)
        self.beam.solve()

    def test_two_equal_spans_single_load_centered_on_one_span(self):
        """two equal spans, concentrated load at center of one span
        """

        P = -self.beam.loads[0].value
        R1 = 13 / 32 * P
        R2 = 11 / 16 * P
        R3 = -3 / 32 * P
        R = [R1, R2, R3]
        for r, Re in zip(self.beam.reactions, R):
            self.assertAlmostEqual(r.value[0], Re, msg=REACTION_MSG)

    def test_two_equal_spans_single_load_at_any_point(self):

        L = self.beam.reactions[1].location
        P = -self.beam.loads[0].value

        for offset in [15, 30, 50]:
            self.beam.loads[0].location = offset
            self.beam.solve()
            a = self.beam.loads[0].location
            b = self.beam.reactions[1].location - a

            R1 = P * b / (4 * L ** 3) * (4 * L ** 2 - a * (L + a))
            R2 = P * a / (2 * L ** 3) * (2 * L ** 2 + b * (L + a))
            R3 = -P * a * b / (4 * L ** 3) * (L + a)
            R = [R1, R2, R3]

            for r, Re in zip(self.beam.reactions, R):
                self.assertAlmostEqual(r.value[0], Re, msg=REACTION_MSG)
                self.assertAlmostEqual(r.value[1], 0, msg=REACTION_MSG)


class TestUnequalLoadsUnsymmetricallyLoaded(unittest.TestCase):
    """Validate results for load case where the beam is supported by a
    pinned reaction at each end, with two unequal, non-symmetrically located
    point loads.

    Note that there is a sign difference due to how the forces are defined.
    In this module, a negative force is acting down, and in the reference, the
    arrow direction is down, indicating a downward force.

    load case 11 in reference
    """

    def setUp(self):
        self.P = (-1000, -500)
        self.x = (7, 15)

        reactions = [PinnedReaction(0), PinnedReaction(20)]
        loads = [PointLoad(value=self.P[0], location=self.x[0]),
                 PointLoad(value=self.P[1], location=self.x[1])]
        self.beam = Beam(20, loads, reactions, E=29e6, Ixx=315)
        self.beam.solve()

    def test_reaction_values(self):
        """validate the reaction at 0 (left side)"""
        P1, P2 = self.P
        L = self.beam.length
        a = self.x[0]
        b = L - self.x[1]  # distance from P2 to end
        R1_exact = (P1 * (L - a) + P2 * b) / L
        R2_exact = (P1 * a + P2 * (L - b)) / L

        r1_calc = self.beam.reactions[0].value[0]
        r2_calc = self.beam.reactions[1].value[0]

        err_msg = ('Reaction for unequal, unsymmetrical load not equal to'
                   ' exact method')
        self.assertAlmostEqual(r1_calc, -R1_exact, msg=err_msg)
        self.assertAlmostEqual(r2_calc, -R2_exact, msg=err_msg)

    def test_zero_moment(self):
        for k in range(2):
            self.assertAlmostEqual(self.beam.reactions[k].value[1], 0,
                                   msg=NON_ZERO_MOMENT)


class TestUnequalSpansSymmetricLoad(unittest.TestCase):
    """Continuous beam
    Two uneqal spans
    concentrated load on each span symmetrically placed"""

    def setUp(self):
        self.P = (-1000, -500)
        reactions = [PinnedReaction(k) for k in [0, 10, 16]]
        loads = [PointLoad(value=-1000, location=5),
                 PointLoad(value=-500, location=13)]
        self.beam = Beam(16, loads, reactions, E=29e6, Ixx=350)
        self.beam.solve()

    def test_reaction_values(self):
        P1, P2 = self.P
        L1 = self.beam.reactions[1].location
        L2 = self.beam.length - L1
        M1 = -3 / 16 * ((P1 * L1 ** 2 + P2 * L2 ** 2) / (L1 + L2))

        R1 = M1 / L1 + P1 / 2
        R3 = M1 / L2 + P2 / 2
        R2 = P1 + P2 - R1 - R3

        for k, r in enumerate([R1, R2, R3]):
            self.assertAlmostEqual(r, -self.beam.reactions[k].value[0],
                                   msg='reactions not equal')
            self.assertAlmostEqual(self.beam.reactions[k].value[1], 0,
                                   msg=NON_ZERO_MOMENT)
