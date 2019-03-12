import unittest

import numpy as np
import numpy.testing as npt

from femethods.elements import Beam
from femethods.loads import MomentLoad, PointLoad
from femethods.reactions import FixedReaction, PinnedReaction


class TestBases(unittest.TestCase):

    def setUp(self):
        self.loads = [PointLoad(value=10, location=10)]
        self.reactions = [PinnedReaction(0), PinnedReaction(5)]
        self.beam = Beam(length=10,
                         reactions=self.reactions,
                         loads=self.loads,
                         E=2,
                         Ixx=3)

    def test_base_assignment(self):
        # need to test assignment and getting of base properties
        # length
        # E, youngs modulus
        # Ixx, area moment of inertia

        for length, e, ixx in zip([-1, 1, 1], [1, -1, 1], [1, 1, -1]):
            # verify that a negative value for any property will raise an error
            with self.assertRaises(ValueError):
                self.beam.length = length
                self.beam.E = e
                self.beam.Ixx = ixx

    def test_base_retrieve(self):
        # Verify we can access all properties correctly
        self.assertEqual(self.beam.length, 10)
        self.assertEqual(self.beam.E, 2)
        self.assertEqual(self.beam.Ixx, 3)

    def test_load_types(self):
        self.assertEqual(self.beam.loads, self.loads)
        with self.assertRaises(TypeError, msg='loads must be a list'):
            self.beam.loads = 'not a list'

    def test_load_exceptions(self):
        for load in [PointLoad, MomentLoad]:
            with self.assertRaises(ValueError):
                load(value=-5, location=-10)  # negative location

    def test_reaction_types(self):
        self.assertEqual(self.beam.reactions, self.reactions)
        with self.assertRaises(TypeError, msg='reactions must be a list'):
            self.beam.reactions = 'not a list'

    def test_reaction_exceptions(self):
        for reaction in [PinnedReaction, FixedReaction]:
            with self.assertRaises(ValueError):
                reaction(location=-10)  # negative location


class TestBeam(unittest.TestCase):

    def setUp(self):
        self.loads = [PointLoad(value=10, location=10)]
        self.reactions = [PinnedReaction(0), PinnedReaction(5)]
        self.beam = Beam(length=10,
                         reactions=self.reactions,
                         loads=self.loads)

    def test_beam_properties(self):
        pass

        # properties and attributes of the beam that should be checked
        # K
        # length
        # loads
        # mesh
        #    dof
        #    lengths
        #    nodes
        #    num_elements
        # node_deflections

    def test_shape(self):
        N1 = lambda x, L: 1 / L ** 3 * (L ** 3 - 3 * L * x ** 2 + 2 * x ** 3)
        N2 = lambda x, L: 1 / L ** 2 * (L ** 2 * x - 2 * L * x ** 2 + x ** 3)
        N3 = lambda x, L: 1 / L ** 3 * (3 * L * x ** 2 - 2 * x ** 3)
        N4 = lambda x, L: 1 / L ** 2 * (-L * x ** 2 + x ** 3)
        N = lambda x, L: [N1(x, L), N2(x, L), N3(x, L), N4(x, L)]

        length = self.beam.length
        for x in self.beam.mesh.nodes:
            npt.assert_almost_equal(self.beam.shape(x, length), N(x, length))

    def test_stiffness(self):
        E, Ixx, L = self.beam.E, self.beam.Ixx, self.beam.length
        k = lambda L: E * Ixx / L ** 3 * \
                      np.array([[12, 6 * L, -12, 6 * L],
                                [6 * L, 4 * L ** 2, -6 * L, 2 * L ** 2],
                                [-12, -6 * L, 12, -6 * L],
                                [6 * L, 2 * L ** 2, -6 * L, 4 * L ** 2]])

        for x in self.beam.mesh.lengths:
            npt.assert_almost_equal(self.beam.stiffness(x), k(x),
                                    err_msg='stiffness matrix does not match')

    def test_invalid_deflection(self):
        self.beam.solve()
        self.assertEqual(self.beam.deflection(15), None,
                         msg='invalid deflection location')

    def test_shear(self):
        self.beam.solve()
        # print(self.beam)




class TestMesh(unittest.TestCase):

    def setUp(self):
        self.loads = [PointLoad(value=10, location=10)]
        self.reactions = [PinnedReaction(0), PinnedReaction(5)]
        self.beam = Beam(length=10,
                         reactions=self.reactions,
                         loads=self.loads)
        self.mesh = self.beam.mesh

    def test_nodes(self):
        self.assertEqual(self.mesh.nodes, [0, 5, 10],
                         msg='mesh nodes do not match input')

    def test_dof(self):
        self.assertEqual(self.mesh.dof, 6,
                         msg='system has wrong number of degrees of freedom')

    def test_elements(self):
        self.assertEqual(self.mesh.num_elements, 2,
                         msg='wrong number of elements')
        self.assertEqual(self.mesh.lengths, [5, 5],
                         msg='mesh elements are not correct length')


class TestReactions(unittest.TestCase):

    def setUp(self):
        self.loads = [PointLoad(value=100, location=10)]
        self.reactions = [PinnedReaction(0), FixedReaction(10)]
        self.beam = Beam(length=10,
                         reactions=self.reactions,
                         loads=self.loads)
        self.beam.solve()

    def test_reaction_invalidate(self):
        for reaction in self.reactions:
            reaction.invalidate()
            self.assertEqual(reaction.force, None, 'Force was not invalidated')
            self.assertEqual(reaction.moment, None, 'Moment was not invalidated')

    def test_beam_invalidate(self):
        self.beam.invalidate()
        for reaction in self.reactions:
            self.assertEqual(reaction.force, None, 'Force was not invalidated')
            self.assertEqual(reaction.moment, None, 'Moment was not invalidated')


if __name__ == '__main__':
    unittest.main()
