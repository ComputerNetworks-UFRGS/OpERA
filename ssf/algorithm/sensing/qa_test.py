#!/usr/bin/python

## @package algorithm

# ::TODO:: Discover how to include patches externally
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, path)

import unittest, random

# Modules  tested
from energyAlgorithm   import EnergyAlgorithm
from waveformAlgorithm import WaveformAlgorithm
from bayesianAlgorithm import BayesLearningThreshold

# Other modules needed
from device            import UHDDevice
from ssf.algorithm     import AbstractAlgorithm


## Test algorithm  module
class qa_algorithm(unittest.TestCase):

	## Test EnergyAlgorithm threhold
	def test_ed_001(self):
		th = 10

		ed = EnergyAlgorithm(th)
		self.assertEqual(th, ed.threshold)
		self.assertEqual(ed.decision(th/2), 0)
		self.assertEqual(ed.decision(th), 0)
		self.assertEqual(ed.decision(th*2), 1)

	## Test Waveform threshold 
	def test_ed_002(self):
		global signal # wrong size. update to 1024 points

		th = 0.8
		wd = WaveformAlgorithm(th)

		self.assertEqual(th, wd.threshold)
		dec = wd.decision([random.random() for i in xrange(1024)])

		# Random will (probaly) not match any signal
		self.assertEqual(0, dec)

	## Test BayesLearningThreshold basic parameters
	def test_bayes_001(self):
		in_th = 10
		min_th = 1
		max_th = 20
		k = 1
		delta_th = 0.0015

		obj = BayesLearningThreshold( in_th = in_th,
				min_th = min_th,
				max_th = max_th,
				delta_th = delta_th,
				k = k)

		self.assertEqual(in_th, obj._th)
		self.assertEqual(min_th, obj._min_th_limit)
		self.assertEqual(max_th, obj._max_th_limit)
		self.assertEqual(k, obj._k)
		self.assertEqual(delta_th, obj._delta_th)

	## Test BayesLearningThreshold basic parameters
	def test_bayes_002(self):
		in_th = 10
		min_th = 1
		max_th = 20
		k = 1
		n = 1000
		delta_th = 0.0015

		obj = BayesLearningThreshold( in_th = in_th,
				min_th = min_th,
				max_th = max_th,
				delta_th = delta_th,
				k = k)

		dec = obj.decision( 9 )

		self.assertEqual(0, dec)




if __name__ == '__main__':
	unittest.main()
