#!/usr/bin/env python3

###############################################################################
#                                                                             #
# RMG - Reaction Mechanism Generator                                          #
#                                                                             #
# Copyright (c) 2002-2021 Prof. William H. Green (whgreen@mit.edu),           #
# Prof. Richard H. West (r.west@neu.edu) and the RMG Team (rmg_dev@mit.edu)   #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the 'Software'),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included in  #
# all copies or substantial portions of the Software.                         #
#                                                                             #
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
#                                                                             #
###############################################################################

"""
This script contains unit tests of the :mod:`rmgpy.kinetics.falloff` module.
"""

import unittest

import numpy as np

from rmgpy.kinetics.arrhenius import Arrhenius
from rmgpy.kinetics.falloff import ThirdBody, Lindemann, Troe
from rmgpy.molecule import Molecule
from rmgpy.species import Species


################################################################################

class TestThirdBody(unittest.TestCase):
    """
    Contains unit tests of the ThirdBody class.
    """

    def setUp(self):
        """
        A function run before each unit test in this class.
        """
        self.arrheniusLow = Arrhenius(
            A=(2.62e+33, "cm^6/(mol^2*s)"),
            n=-4.76,
            Ea=(10.21, "kJ/mol"),
            T0=(1, "K"),
        )
        self.efficiencies = {"C": 3, "C(=O)=O": 2, "CC": 3, "O": 6, "[Ar]": 0.7, "[C]=O": 1.5, "[H][H]": 2}
        self.Tmin = 300.
        self.Tmax = 2000.
        self.Pmin = 0.01
        self.Pmax = 100.
        self.comment = """H + CH3 -> CH4"""
        self.thirdBody = ThirdBody(
            arrheniusLow=self.arrheniusLow,
            Tmin=(self.Tmin, "K"),
            Tmax=(self.Tmax, "K"),
            Pmin=(self.Pmin, "bar"),
            Pmax=(self.Pmax, "bar"),
            efficiencies=self.efficiencies,
            comment=self.comment,
        )

    def test_arrhenius_low(self):
        """
        Test that the ThirdBody arrhenius property was properly set.
        """
        self.assertTrue(self.thirdBody.arrheniusLow is self.arrheniusLow)

    def test_temperature_min(self):
        """
        Test that the ThirdBody Tmin property was properly set.
        """
        self.assertAlmostEqual(self.thirdBody.Tmin.value_si, self.Tmin, 6)

    def test_temperature_max(self):
        """
        Test that the ThirdBody Tmax property was properly set.
        """
        self.assertAlmostEqual(self.thirdBody.Tmax.value_si, self.Tmax, 6)

    def test_pressure_min(self):
        """
        Test that the ThirdBody Pmin property was properly set.
        """
        self.assertAlmostEqual(self.thirdBody.Pmin.value_si * 1e-5, self.Pmin, 6)

    def test_pressure_max(self):
        """
        Test that the ThirdBody Pmax property was properly set.
        """
        self.assertAlmostEqual(self.thirdBody.Pmax.value_si * 1e-5, self.Pmax, 6)

    def test_comment(self):
        """
        Test that the ThirdBody comment property was properly set.
        """
        self.assertEqual(self.thirdBody.comment, self.comment)

    def test_is_pressure_dependent(self):
        """
        Test the ThirdBody.is_pressure_dependent() method.
        """
        self.assertTrue(self.thirdBody.is_pressure_dependent())

    def test_get_effective_pressure(self):
        """
        Test the ThirdBody.get_effective_pressure() method.
        """
        P = 1.0
        # Test that each pure bath gas gives the correct effective pressure
        # Create list of species objects 
        species = [Species(molecule=[mol]) for mol in self.thirdBody.efficiencies.keys()]
        for mol, eff in self.thirdBody.efficiencies.items():
            for spec in species:
                if spec.is_isomorphic(mol):
                    i = species.index(spec)
                    break
            fractions = np.zeros(len(species))
            fractions[i] = 1.0
            Peff = self.thirdBody.get_effective_pressure(P, species, fractions)
            self.assertAlmostEqual(P * eff, Peff)
        # Also test a mixture of bath gases
        fractions = np.zeros(len(species))
        fractions[0] = 0.5
        fractions[1] = 0.5
        eff = 0
        for mol in self.thirdBody.efficiencies.keys():
            if species[0].is_isomorphic(mol):
                eff += 0.5 * self.thirdBody.efficiencies[mol]
            if species[1].is_isomorphic(mol):
                eff += 0.5 * self.thirdBody.efficiencies[mol]
        Peff = self.thirdBody.get_effective_pressure(P, species, fractions)
        self.assertAlmostEqual(P * eff, Peff)

        # Test the same thing, only with a list of species that are Molecule objects
        species = [mol.copy(deep=True) for mol in self.thirdBody.efficiencies.keys()]
        for mol, eff in self.thirdBody.efficiencies.items():
            for spec in species:
                if spec.is_isomorphic(mol):
                    i = species.index(spec)
                    break
            fractions = np.zeros(len(species))
            fractions[i] = 1.0
            Peff = self.thirdBody.get_effective_pressure(P, species, fractions)
            self.assertAlmostEqual(P * eff, Peff)
        # Also test a mixture of bath gases
        eff = 0
        for mol in self.thirdBody.efficiencies.keys():
            if species[0].is_isomorphic(mol):
                eff += 0.5 * self.thirdBody.efficiencies[mol]
            if species[1].is_isomorphic(mol):
                eff += 0.5 * self.thirdBody.efficiencies[mol]

        fractions = np.zeros(len(species))
        fractions[0] = 0.5
        fractions[1] = 0.5
        Peff = self.thirdBody.get_effective_pressure(P, species, fractions)
        self.assertAlmostEqual(P * eff, Peff)

        # Here, test a non-normalized set of fractions (they are still 50% of each)
        fractions = np.zeros(len(species))
        fractions[0] = 0.7
        fractions[1] = 0.7
        Peff = self.thirdBody.get_effective_pressure(P, species, fractions)
        self.assertAlmostEqual(P * eff, Peff)

    def test_get_effective_collider_efficiencies(self):
        """
        Test the get_effective_collider_efficiencies() method
        """
        # Create list of molecules
        molecules = [Molecule(smiles=smiles) for smiles in ["C", "C(=O)=O", "CC", "O", "[Ar]", "[C]=O", "[H][H]"]]
        method_efficiencies = self.thirdBody.get_effective_collider_efficiencies(molecules)
        efficiencies = np.array([3, 2, 3, 6, 0.7, 1.5, 2])
        np.testing.assert_array_almost_equal(efficiencies, method_efficiencies)

        # Use a smaller list of molecules
        molecules = [Molecule(smiles=smiles) for smiles in ["C", "CC", "[Ar]"]]
        method_efficiencies = self.thirdBody.get_effective_collider_efficiencies(molecules)
        efficiencies = np.array([3, 3, 0.7])
        np.testing.assert_array_almost_equal(efficiencies, method_efficiencies)

    def test_get_rate_coefficient(self):
        """
        Test the ThirdBody.get_rate_coefficient() method.
        """
        Tlist = np.array([300, 500, 1000, 1500])
        Plist = np.array([1e4, 1e5, 1e6])
        Kexp = np.array([
            [2.83508e+08, 2.83508e+09, 2.83508e+10],
            [7.68759e+07, 7.68759e+08, 7.68759e+09],
            [4.84353e+06, 4.84353e+07, 4.84353e+08],
            [7.05740e+05, 7.05740e+06, 7.05740e+07],
        ])
        for t in range(Tlist.shape[0]):
            for p in range(Plist.shape[0]):
                Kact = self.thirdBody.get_rate_coefficient(Tlist[t], Plist[p])
                self.assertAlmostEqual(Kact, Kexp[t, p], delta=1e-4 * Kexp[t, p])

    def test_pickle(self):
        """
        Test that a ThirdBody object can be successfully pickled and
        unpickled with no loss of information.
        """
        import pickle
        thirdBody = pickle.loads(pickle.dumps(self.thirdBody, -1))
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.A.value, thirdBody.arrheniusLow.A.value, delta=1e0)
        self.assertEqual(self.thirdBody.arrheniusLow.A.units, thirdBody.arrheniusLow.A.units)
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.n.value, thirdBody.arrheniusLow.n.value, 4)
        self.assertEqual(self.thirdBody.arrheniusLow.n.units, thirdBody.arrheniusLow.n.units, 4)
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.Ea.value, thirdBody.arrheniusLow.Ea.value, 4)
        self.assertEqual(self.thirdBody.arrheniusLow.Ea.units, thirdBody.arrheniusLow.Ea.units)
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.T0.value, thirdBody.arrheniusLow.T0.value, 4)
        self.assertEqual(self.thirdBody.arrheniusLow.T0.units, thirdBody.arrheniusLow.T0.units)
        self.assertAlmostEqual(self.thirdBody.Tmin.value, thirdBody.Tmin.value, 4)
        self.assertEqual(self.thirdBody.Tmin.units, thirdBody.Tmin.units)
        self.assertAlmostEqual(self.thirdBody.Tmax.value, thirdBody.Tmax.value, 4)
        self.assertEqual(self.thirdBody.Tmax.units, thirdBody.Tmax.units)
        self.assertAlmostEqual(self.thirdBody.Pmin.value, thirdBody.Pmin.value, 4)
        self.assertEqual(self.thirdBody.Pmin.units, thirdBody.Pmin.units)
        self.assertAlmostEqual(self.thirdBody.Pmax.value, thirdBody.Pmax.value, 4)
        self.assertEqual(self.thirdBody.Pmax.units, thirdBody.Pmax.units)
        efficiencies = {}
        for mol, eff in self.thirdBody.efficiencies.items():
            efficiencies[mol.to_smiles()] = eff
        pickled_efficiencies = {}
        for mol, eff in thirdBody.efficiencies.items():
            pickled_efficiencies[mol.to_smiles()] = eff
        self.assertEqual(efficiencies, pickled_efficiencies)
        self.assertEqual(self.thirdBody.comment, thirdBody.comment)

    def test_repr(self):
        """
        Test that a ThirdBody object can be successfully reconstructed
        from its repr() output with no loss of information.
        """
        namespace = {}
        exec('thirdBody = {0!r}'.format(self.thirdBody), globals(), namespace)
        self.assertIn('thirdBody', namespace)
        thirdBody = namespace['thirdBody']
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.A.value, thirdBody.arrheniusLow.A.value, delta=1e0)
        self.assertEqual(self.thirdBody.arrheniusLow.A.units, thirdBody.arrheniusLow.A.units)
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.n.value, thirdBody.arrheniusLow.n.value, 4)
        self.assertEqual(self.thirdBody.arrheniusLow.n.units, thirdBody.arrheniusLow.n.units, 4)
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.Ea.value, thirdBody.arrheniusLow.Ea.value, 4)
        self.assertEqual(self.thirdBody.arrheniusLow.Ea.units, thirdBody.arrheniusLow.Ea.units)
        self.assertAlmostEqual(self.thirdBody.arrheniusLow.T0.value, thirdBody.arrheniusLow.T0.value, 4)
        self.assertEqual(self.thirdBody.arrheniusLow.T0.units, thirdBody.arrheniusLow.T0.units)
        self.assertAlmostEqual(self.thirdBody.Tmin.value, thirdBody.Tmin.value, 4)
        self.assertEqual(self.thirdBody.Tmin.units, thirdBody.Tmin.units)
        self.assertAlmostEqual(self.thirdBody.Tmax.value, thirdBody.Tmax.value, 4)
        self.assertEqual(self.thirdBody.Tmax.units, thirdBody.Tmax.units)
        self.assertAlmostEqual(self.thirdBody.Pmin.value, thirdBody.Pmin.value, 4)
        self.assertEqual(self.thirdBody.Pmin.units, thirdBody.Pmin.units)
        self.assertAlmostEqual(self.thirdBody.Pmax.value, thirdBody.Pmax.value, 4)
        self.assertEqual(self.thirdBody.Pmax.units, thirdBody.Pmax.units)
        efficiencies = {}
        for mol, eff in self.thirdBody.efficiencies.items():
            efficiencies[mol.to_smiles()] = eff
        pickled_efficiencies = {}
        for mol, eff in thirdBody.efficiencies.items():
            pickled_efficiencies[mol.to_smiles()] = eff
        self.assertEqual(efficiencies, pickled_efficiencies)
        self.assertEqual(self.thirdBody.comment, thirdBody.comment)

    def test_change_rate(self):
        """
        Test the ThirdBody.change_rate() method.
        """
        Tlist = np.array([300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500])
        k0list = np.array([self.thirdBody.get_rate_coefficient(T, 1e5) for T in Tlist])
        self.thirdBody.change_rate(2)
        for T, kexp in zip(Tlist, k0list):
            kact = self.thirdBody.get_rate_coefficient(T, 1e5)
            self.assertAlmostEqual(2 * kexp, kact, delta=1e-6 * kexp)


################################################################################

class TestLindemann(unittest.TestCase):
    """
    Contains unit tests of the Lindemann class.
    """

    def setUp(self):
        """
        A function run before each unit test in this class.
        """
        self.arrheniusHigh = Arrhenius(
            A=(1.39e+16, "cm^3/(mol*s)"),
            n=-0.534,
            Ea=(2.243, "kJ/mol"),
            T0=(1, "K"),
        )
        self.arrheniusLow = Arrhenius(
            A=(2.62e+33, "cm^6/(mol^2*s)"),
            n=-4.76,
            Ea=(10.21, "kJ/mol"),
            T0=(1, "K"),
        )
        self.efficiencies = {"C": 3, "C(=O)=O": 2, "CC": 3, "O": 6, "[Ar]": 0.7, "[C]=O": 1.5, "[H][H]": 2}
        self.Tmin = 300.
        self.Tmax = 2000.
        self.Pmin = 0.01
        self.Pmax = 100.
        self.comment = """H + CH3 -> CH4"""
        self.lindemann = Lindemann(
            arrheniusHigh=self.arrheniusHigh,
            arrheniusLow=self.arrheniusLow,
            Tmin=(self.Tmin, "K"),
            Tmax=(self.Tmax, "K"),
            Pmin=(self.Pmin, "bar"),
            Pmax=(self.Pmax, "bar"),
            efficiencies=self.efficiencies,
            comment=self.comment,
        )

    def test_arrhenius_high(self):
        """
        Test that the Lindemann arrheniusHigh property was properly set.
        """
        self.assertTrue(self.lindemann.arrheniusHigh is self.arrheniusHigh)

    def test_arrhenius_low(self):
        """
        Test that the Lindemann arrheniusLow property was properly set.
        """
        self.assertTrue(self.lindemann.arrheniusLow is self.arrheniusLow)

    def test_temperature_min(self):
        """
        Test that the Lindemann Tmin property was properly set.
        """
        self.assertAlmostEqual(self.lindemann.Tmin.value_si, self.Tmin, 6)

    def test_temperature_max(self):
        """
        Test that the Lindemann Tmax property was properly set.
        """
        self.assertAlmostEqual(self.lindemann.Tmax.value_si, self.Tmax, 6)

    def test_pressure_min(self):
        """
        Test that the Lindemann Pmin property was properly set.
        """
        self.assertAlmostEqual(self.lindemann.Pmin.value_si * 1e-5, self.Pmin, 6)

    def test_pressure_max(self):
        """
        Test that the Lindemann Pmax property was properly set.
        """
        self.assertAlmostEqual(self.lindemann.Pmax.value_si * 1e-5, self.Pmax, 6)

    def test_comment(self):
        """
        Test that the Lindemann comment property was properly set.
        """
        self.assertEqual(self.lindemann.comment, self.comment)

    def test_is_pressure_dependent(self):
        """
        Test the Lindemann.is_pressure_dependent() method.
        """
        self.assertTrue(self.lindemann.is_pressure_dependent())

    def test_get_rate_coefficient(self):
        """
        Test the Lindemann.get_rate_coefficient() method.
        """
        Tlist = np.array([300, 500, 1000, 1500])
        Plist = np.array([1e4, 1e5, 1e6])
        Kexp = np.array([
            [1.38023e+08, 2.45661e+08, 2.66439e+08],
            [6.09146e+07, 2.12349e+08, 2.82604e+08],
            [4.75671e+06, 4.09594e+07, 1.71441e+08],
            [7.03616e+05, 6.85062e+06, 5.42111e+07],
        ])
        for t in range(Tlist.shape[0]):
            for p in range(Plist.shape[0]):
                Kact = self.lindemann.get_rate_coefficient(Tlist[t], Plist[p])
                self.assertAlmostEqual(Kact, Kexp[t, p], delta=1e-4 * Kexp[t, p])

    def test_pickle(self):
        """
        Test that a Lindemann object can be pickled and unpickled with no loss
        of information.
        """
        import pickle
        lindemann = pickle.loads(pickle.dumps(self.lindemann, -1))
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.A.value, lindemann.arrheniusHigh.A.value, delta=1e0)
        self.assertEqual(self.lindemann.arrheniusHigh.A.units, lindemann.arrheniusHigh.A.units)
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.n.value, lindemann.arrheniusHigh.n.value, 4)
        self.assertEqual(self.lindemann.arrheniusHigh.n.units, lindemann.arrheniusHigh.n.units, 4)
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.Ea.value, lindemann.arrheniusHigh.Ea.value, 4)
        self.assertEqual(self.lindemann.arrheniusHigh.Ea.units, lindemann.arrheniusHigh.Ea.units)
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.T0.value, lindemann.arrheniusHigh.T0.value, 4)
        self.assertEqual(self.lindemann.arrheniusHigh.T0.units, lindemann.arrheniusHigh.T0.units)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.A.value, lindemann.arrheniusLow.A.value, delta=1e0)
        self.assertEqual(self.lindemann.arrheniusLow.A.units, lindemann.arrheniusLow.A.units)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.n.value, lindemann.arrheniusLow.n.value, 4)
        self.assertEqual(self.lindemann.arrheniusLow.n.units, lindemann.arrheniusLow.n.units, 4)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.Ea.value, lindemann.arrheniusLow.Ea.value, 4)
        self.assertEqual(self.lindemann.arrheniusLow.Ea.units, lindemann.arrheniusLow.Ea.units)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.T0.value, lindemann.arrheniusLow.T0.value, 4)
        self.assertEqual(self.lindemann.arrheniusLow.T0.units, lindemann.arrheniusLow.T0.units)
        self.assertAlmostEqual(self.lindemann.Tmin.value, lindemann.Tmin.value, 4)
        self.assertEqual(self.lindemann.Tmin.units, lindemann.Tmin.units)
        self.assertAlmostEqual(self.lindemann.Tmax.value, lindemann.Tmax.value, 4)
        self.assertEqual(self.lindemann.Tmax.units, lindemann.Tmax.units)
        self.assertAlmostEqual(self.lindemann.Pmin.value, lindemann.Pmin.value, 4)
        self.assertEqual(self.lindemann.Pmin.units, lindemann.Pmin.units)
        self.assertAlmostEqual(self.lindemann.Pmax.value, lindemann.Pmax.value, 4)
        self.assertEqual(self.lindemann.Pmax.units, lindemann.Pmax.units)
        efficiencies = {}
        for mol, eff in self.lindemann.efficiencies.items():
            efficiencies[mol.to_smiles()] = eff
        pickled_efficiencies = {}
        for mol, eff in lindemann.efficiencies.items():
            pickled_efficiencies[mol.to_smiles()] = eff
        self.assertEqual(efficiencies, pickled_efficiencies)
        self.assertEqual(self.lindemann.comment, lindemann.comment)

    def test_repr(self):
        """
        Test that a Lindemann object can be reconstructed from its repr()
        output with no loss of information.
        """
        namespace = {}
        exec('lindemann = {0!r}'.format(self.lindemann), globals(), namespace)
        self.assertIn('lindemann', namespace)
        lindemann = namespace['lindemann']
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.A.value, lindemann.arrheniusHigh.A.value, delta=1e0)
        self.assertEqual(self.lindemann.arrheniusHigh.A.units, lindemann.arrheniusHigh.A.units)
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.n.value, lindemann.arrheniusHigh.n.value, 4)
        self.assertEqual(self.lindemann.arrheniusHigh.n.units, lindemann.arrheniusHigh.n.units, 4)
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.Ea.value, lindemann.arrheniusHigh.Ea.value, 4)
        self.assertEqual(self.lindemann.arrheniusHigh.Ea.units, lindemann.arrheniusHigh.Ea.units)
        self.assertAlmostEqual(self.lindemann.arrheniusHigh.T0.value, lindemann.arrheniusHigh.T0.value, 4)
        self.assertEqual(self.lindemann.arrheniusHigh.T0.units, lindemann.arrheniusHigh.T0.units)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.A.value, lindemann.arrheniusLow.A.value, delta=1e0)
        self.assertEqual(self.lindemann.arrheniusLow.A.units, lindemann.arrheniusLow.A.units)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.n.value, lindemann.arrheniusLow.n.value, 4)
        self.assertEqual(self.lindemann.arrheniusLow.n.units, lindemann.arrheniusLow.n.units, 4)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.Ea.value, lindemann.arrheniusLow.Ea.value, 4)
        self.assertEqual(self.lindemann.arrheniusLow.Ea.units, lindemann.arrheniusLow.Ea.units)
        self.assertAlmostEqual(self.lindemann.arrheniusLow.T0.value, lindemann.arrheniusLow.T0.value, 4)
        self.assertEqual(self.lindemann.arrheniusLow.T0.units, lindemann.arrheniusLow.T0.units)
        self.assertAlmostEqual(self.lindemann.Tmin.value, lindemann.Tmin.value, 4)
        self.assertEqual(self.lindemann.Tmin.units, lindemann.Tmin.units)
        self.assertAlmostEqual(self.lindemann.Tmax.value, lindemann.Tmax.value, 4)
        self.assertEqual(self.lindemann.Tmax.units, lindemann.Tmax.units)
        self.assertAlmostEqual(self.lindemann.Pmin.value, lindemann.Pmin.value, 4)
        self.assertEqual(self.lindemann.Pmin.units, lindemann.Pmin.units)
        self.assertAlmostEqual(self.lindemann.Pmax.value, lindemann.Pmax.value, 4)
        self.assertEqual(self.lindemann.Pmax.units, lindemann.Pmax.units)
        efficiencies = {}
        for mol, eff in self.lindemann.efficiencies.items():
            efficiencies[mol.to_smiles()] = eff
        pickled_efficiencies = {}
        for mol, eff in lindemann.efficiencies.items():
            pickled_efficiencies[mol.to_smiles()] = eff
        self.assertEqual(efficiencies, pickled_efficiencies)
        self.assertEqual(self.lindemann.comment, lindemann.comment)

    def test_change_rate(self):
        """
        Test the Lindemann.change_rate() method.
        """
        Tlist = np.array([300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500])
        k0list = np.array([self.lindemann.get_rate_coefficient(T, 1e5) for T in Tlist])
        self.lindemann.change_rate(2)
        for T, kexp in zip(Tlist, k0list):
            kact = self.lindemann.get_rate_coefficient(T, 1e5)
            self.assertAlmostEqual(2 * kexp, kact, delta=1e-6 * kexp)


################################################################################

class TestTroe(unittest.TestCase):
    """
    Contains unit tests of the Troe class.
    """

    def setUp(self):
        """
        A function run before each unit test in this class.
        """
        self.arrheniusHigh = Arrhenius(
            A=(1.39e+16, "cm^3/(mol*s)"),
            n=-0.534,
            Ea=(2.243, "kJ/mol"),
            T0=(1, "K"),
        )
        self.arrheniusLow = Arrhenius(
            A=(2.62e+33, "cm^6/(mol^2*s)"),
            n=-4.76,
            Ea=(10.21, "kJ/mol"),
            T0=(1, "K"),
        )
        self.alpha = 0.783
        self.T3 = 74
        self.T1 = 2941
        self.T2 = 6964
        self.efficiencies = {"C": 3, "C(=O)=O": 2, "CC": 3, "O": 6, "[Ar]": 0.7, "[C]=O": 1.5, "[H][H]": 2}
        self.Tmin = 300.
        self.Tmax = 2000.
        self.Pmin = 0.01
        self.Pmax = 100.
        self.comment = """H + CH3 -> CH4"""
        self.troe = Troe(
            arrheniusHigh=self.arrheniusHigh,
            arrheniusLow=self.arrheniusLow,
            alpha=self.alpha,
            T3=(self.T3, "K"),
            T1=(self.T1, "K"),
            T2=(self.T2, "K"),
            Tmin=(self.Tmin, "K"),
            Tmax=(self.Tmax, "K"),
            Pmin=(self.Pmin, "bar"),
            Pmax=(self.Pmax, "bar"),
            efficiencies=self.efficiencies,
            comment=self.comment,
        )

    def test_arrhenius_high(self):
        """
        Test that the Troe arrheniusHigh property was properly set.
        """
        self.assertTrue(self.troe.arrheniusHigh is self.arrheniusHigh)

    def test_arrhenius_low(self):
        """
        Test that the Troe arrheniusLow property was properly set.
        """
        self.assertTrue(self.troe.arrheniusLow is self.arrheniusLow)

    def test_alpha(self):
        """
        Test that the Troe alpha property was properly set.
        """
        self.assertEqual(self.troe.alpha, self.alpha)

    def test_t3(self):
        """
        Test that the Troe T3 property was properly set.
        """
        self.assertAlmostEqual(self.troe.T3.value_si, self.T3, 6)

    def test_t1(self):
        """
        Test that the Troe T1 property was properly set.
        """
        self.assertAlmostEqual(self.troe.T1.value_si, self.T1, 6)

    def test_t2(self):
        """
        Test that the Troe T2 property was properly set.
        """
        self.assertAlmostEqual(self.troe.T2.value_si, self.T2, 6)

    def test_temperature_min(self):
        """
        Test that the Troe Tmin property was properly set.
        """
        self.assertAlmostEqual(self.troe.Tmin.value_si, self.Tmin, 6)

    def test_temperature_max(self):
        """
        Test that the Troe Tmax property was properly set.
        """
        self.assertAlmostEqual(self.troe.Tmax.value_si, self.Tmax, 6)

    def test_pressure_min(self):
        """
        Test that the Troe Pmin property was properly set.
        """
        self.assertAlmostEqual(self.troe.Pmin.value_si * 1e-5, self.Pmin, 6)

    def test_pressure_max(self):
        """
        Test that the Troe Pmax property was properly set.
        """
        self.assertAlmostEqual(self.troe.Pmax.value_si * 1e-5, self.Pmax, 6)

    def test_comment(self):
        """
        Test that the Troe comment property was properly set.
        """
        self.assertEqual(self.troe.comment, self.comment)

    def test_is_pressure_dependent(self):
        """
        Test the Troe.is_pressure_dependent() method.
        """
        self.assertTrue(self.troe.is_pressure_dependent())

    def test_get_rate_coefficient(self):
        """
        Test the Troe.get_rate_coefficient() method.
        """
        Tlist = np.array([300, 500, 1000, 1500])
        Plist = np.array([1e4, 1e5, 1e6])
        Kexp = np.array([
            [1.00648177e+08, 2.01999460e+08, 2.53938097e+08],
            [4.71247326e+07, 1.41526885e+08, 2.45386923e+08],
            [3.94987723e+06, 2.87338709e+07, 9.57539092e+07],
            [5.88566395e+05, 5.10614193e+06, 3.10462030e+07],
        ])
        for t in range(Tlist.shape[0]):
            for p in range(Plist.shape[0]):
                Kact = self.troe.get_rate_coefficient(Tlist[t], Plist[p])
                self.assertAlmostEqual(Kact, Kexp[t, p], delta=1e-4 * Kexp[t, p])

    def test_pickle(self):
        """
        Test that a Troe object can be pickled and unpickled with no loss of
        information.
        """
        import pickle
        troe = pickle.loads(pickle.dumps(self.troe, -1))
        self.assertAlmostEqual(self.troe.arrheniusHigh.A.value, troe.arrheniusHigh.A.value, delta=1e0)
        self.assertEqual(self.troe.arrheniusHigh.A.units, troe.arrheniusHigh.A.units)
        self.assertAlmostEqual(self.troe.arrheniusHigh.n.value, troe.arrheniusHigh.n.value, 4)
        self.assertEqual(self.troe.arrheniusHigh.n.units, troe.arrheniusHigh.n.units, 4)
        self.assertAlmostEqual(self.troe.arrheniusHigh.Ea.value, troe.arrheniusHigh.Ea.value, 4)
        self.assertEqual(self.troe.arrheniusHigh.Ea.units, troe.arrheniusHigh.Ea.units)
        self.assertAlmostEqual(self.troe.arrheniusHigh.T0.value, troe.arrheniusHigh.T0.value, 4)
        self.assertEqual(self.troe.arrheniusHigh.T0.units, troe.arrheniusHigh.T0.units)
        self.assertAlmostEqual(self.troe.arrheniusLow.A.value, troe.arrheniusLow.A.value, delta=1e0)
        self.assertEqual(self.troe.arrheniusLow.A.units, troe.arrheniusLow.A.units)
        self.assertAlmostEqual(self.troe.arrheniusLow.n.value, troe.arrheniusLow.n.value, 4)
        self.assertEqual(self.troe.arrheniusLow.n.units, troe.arrheniusLow.n.units, 4)
        self.assertAlmostEqual(self.troe.arrheniusLow.Ea.value, troe.arrheniusLow.Ea.value, 4)
        self.assertEqual(self.troe.arrheniusLow.Ea.units, troe.arrheniusLow.Ea.units)
        self.assertAlmostEqual(self.troe.arrheniusLow.T0.value, troe.arrheniusLow.T0.value, 4)
        self.assertEqual(self.troe.arrheniusLow.T0.units, troe.arrheniusLow.T0.units)
        self.assertAlmostEqual(self.troe.alpha, troe.alpha, 6)
        self.assertAlmostEqual(self.troe.T3.value, troe.T3.value, 6)
        self.assertEqual(self.troe.T3.units, troe.T3.units)
        self.assertAlmostEqual(self.troe.T1.value, troe.T1.value, 6)
        self.assertEqual(self.troe.T1.units, troe.T1.units)
        self.assertAlmostEqual(self.troe.T2.value, troe.T2.value, 6)
        self.assertEqual(self.troe.T2.units, troe.T2.units)
        self.assertAlmostEqual(self.troe.Tmin.value, troe.Tmin.value, 4)
        self.assertEqual(self.troe.Tmin.units, troe.Tmin.units)
        self.assertAlmostEqual(self.troe.Tmax.value, troe.Tmax.value, 4)
        self.assertEqual(self.troe.Tmax.units, troe.Tmax.units)
        self.assertAlmostEqual(self.troe.Pmin.value, troe.Pmin.value, 4)
        self.assertEqual(self.troe.Pmin.units, troe.Pmin.units)
        self.assertAlmostEqual(self.troe.Pmax.value, troe.Pmax.value, 4)
        self.assertEqual(self.troe.Pmax.units, troe.Pmax.units)
        efficiencies = {}
        for mol, eff in self.troe.efficiencies.items():
            efficiencies[mol.to_smiles()] = eff
        pickled_efficiencies = {}
        for mol, eff in troe.efficiencies.items():
            pickled_efficiencies[mol.to_smiles()] = eff
        self.assertEqual(efficiencies, pickled_efficiencies)
        self.assertEqual(self.troe.comment, troe.comment)

    def test_repr(self):
        """
        Test that a Troe object can be reconstructed from its repr() output
        with no loss of information.
        """
        namespace = {}
        exec('troe = {0!r}'.format(self.troe), globals(), namespace)
        self.assertIn('troe', namespace)
        troe = namespace['troe']
        self.assertAlmostEqual(self.troe.arrheniusHigh.A.value, troe.arrheniusHigh.A.value, delta=1e0)
        self.assertEqual(self.troe.arrheniusHigh.A.units, troe.arrheniusHigh.A.units)
        self.assertAlmostEqual(self.troe.arrheniusHigh.n.value, troe.arrheniusHigh.n.value, 4)
        self.assertEqual(self.troe.arrheniusHigh.n.units, troe.arrheniusHigh.n.units, 4)
        self.assertAlmostEqual(self.troe.arrheniusHigh.Ea.value, troe.arrheniusHigh.Ea.value, 4)
        self.assertEqual(self.troe.arrheniusHigh.Ea.units, troe.arrheniusHigh.Ea.units)
        self.assertAlmostEqual(self.troe.arrheniusHigh.T0.value, troe.arrheniusHigh.T0.value, 4)
        self.assertEqual(self.troe.arrheniusHigh.T0.units, troe.arrheniusHigh.T0.units)
        self.assertAlmostEqual(self.troe.arrheniusLow.A.value, troe.arrheniusLow.A.value, delta=1e0)
        self.assertEqual(self.troe.arrheniusLow.A.units, troe.arrheniusLow.A.units)
        self.assertAlmostEqual(self.troe.arrheniusLow.n.value, troe.arrheniusLow.n.value, 4)
        self.assertEqual(self.troe.arrheniusLow.n.units, troe.arrheniusLow.n.units, 4)
        self.assertAlmostEqual(self.troe.arrheniusLow.Ea.value, troe.arrheniusLow.Ea.value, 4)
        self.assertEqual(self.troe.arrheniusLow.Ea.units, troe.arrheniusLow.Ea.units)
        self.assertAlmostEqual(self.troe.arrheniusLow.T0.value, troe.arrheniusLow.T0.value, 4)
        self.assertEqual(self.troe.arrheniusLow.T0.units, troe.arrheniusLow.T0.units)
        self.assertAlmostEqual(self.troe.alpha, troe.alpha, 6)
        self.assertAlmostEqual(self.troe.T3.value, troe.T3.value, 6)
        self.assertEqual(self.troe.T3.units, troe.T3.units)
        self.assertAlmostEqual(self.troe.T1.value, troe.T1.value, 6)
        self.assertEqual(self.troe.T1.units, troe.T1.units)
        self.assertAlmostEqual(self.troe.T2.value, troe.T2.value, 6)
        self.assertEqual(self.troe.T2.units, troe.T2.units)
        self.assertAlmostEqual(self.troe.Tmin.value, troe.Tmin.value, 4)
        self.assertEqual(self.troe.Tmin.units, troe.Tmin.units)
        self.assertAlmostEqual(self.troe.Tmax.value, troe.Tmax.value, 4)
        self.assertEqual(self.troe.Tmax.units, troe.Tmax.units)
        self.assertAlmostEqual(self.troe.Pmin.value, troe.Pmin.value, 4)
        self.assertEqual(self.troe.Pmin.units, troe.Pmin.units)
        self.assertAlmostEqual(self.troe.Pmax.value, troe.Pmax.value, 4)
        self.assertEqual(self.troe.Pmax.units, troe.Pmax.units)
        efficiencies = {}
        for mol, eff in self.troe.efficiencies.items():
            efficiencies[mol.to_smiles()] = eff
        pickled_efficiencies = {}
        for mol, eff in troe.efficiencies.items():
            pickled_efficiencies[mol.to_smiles()] = eff
        self.assertEqual(efficiencies, pickled_efficiencies)
        self.assertEqual(self.troe.comment, troe.comment)

    def test_change_rate(self):
        """
        Test the Troe.change_rate() method.
        """
        Tlist = np.array([300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500])
        k0list = np.array([self.troe.get_rate_coefficient(T, 1e5) for T in Tlist])
        self.troe.change_rate(2)
        for T, kexp in zip(Tlist, k0list):
            kact = self.troe.get_rate_coefficient(T, 1e5)
            self.assertAlmostEqual(2 * kexp, kact, delta=1e-6 * kexp)


################################################################################

if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
