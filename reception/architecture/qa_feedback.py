"""
Copyright 2013 OpERA

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

#!/usr/bin/env python

## @package device

# ::TODO:: Discover how to include patches externally
# ::TODO:: modules description
import sys
import os
import random

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../"))
sys.path.insert(0, path)

from gnuradio import blocks, gr_unittest, gr

from time import sleep
from math import *
import unittest
import matplotlib.pyplot as plt


# Project imports
from device                     import RadioDevice
from utils.sensing              import Logger
from algorithm                  import BayesLearningThreshold, WaveformDecision, FeedbackAlgorithm, AlwaysTimeFeedback
from reception.sensing          import EnergyDetectorC
from reception.sensing          import WaveformDetector 

# UUT
from feedback import FeedbackTopBlock, FeedbackF

## QA tests related to feeback
class QaFeedback(gr_unittest.TestCase):

	##
	def setUp(self):
		self.tb = gr.top_block()

	##
	def tear_down(self):
		self.tb = None

	## Test Feedback Algorithm architecture
	# This test validades the feedback architecture when the 'manager' says the channel is idle and the 'learner' says is occupied
	def test_001(self):
		data_l = [1]
		data_m = [0]

		# Bayes learning parameters
		in_th = 10
		min_th = 0.001
		max_th = 20
		delta_th = 0.001
		k = 1

		# Feeback architecture
		bl_algo = BayesLearningThreshold( in_th = in_th,
				min_th = min_th,
				max_th = max_th,
				delta_th = delta_th,
				k = k)
		fb_algo = FeedbackAlgorithm( bl_algo, AlwaysTimeFeedback() )

		fb = FeedbackF( fb_algo )

		# Data blocks
		src_l = blocks.vector_source_f( data_l)
		src_m = blocks.vector_source_f( data_m )

		# Flow graph
		self.tb = gr.top_block()
		self.tb.connect(src_l, (fb, 0))
		self.tb.connect(src_m, (fb, 1))

		self.tb.run()

		# bayes feedback has to be 0  
		self.assertEqual(bl_algo.feedback, 0)

	## Test Feedback Algorithm architecture
	# This test validades the feedback architecture when the 'manager' says the channel is occupied and the 'learner' says is idle
	def test_002(self):
		data_l = [0]
		data_m = [1]

		# Bayes learning parameters
		in_th = 10
		min_th = 0.001
		max_th = 20
		delta_th = 0.001
		k = 1

		# Feeback architecture
		bl_algo = BayesLearningThreshold( in_th = in_th,
				min_th = min_th,
				max_th = max_th,
				delta_th = delta_th,
				k = k)
		fb_algo = FeedbackAlgorithm( bl_algo, AlwaysTimeFeedback() )

		fb = FeedbackF( fb_algo )

		# Data blocks
		src_l = blocks.vector_source_f( data_l)
		src_m = blocks.vector_source_f( data_m )

		# Flow graph
		self.tb = gr.top_block()
		self.tb.connect(src_l, (fb, 0))
		self.tb.connect(src_m, (fb, 1))

		self.tb.run()

		# bayes feedback has to be 0  
		self.assertEqual(bl_algo.feedback, 1)


	## Test a more elaboret scenario with feedback
	# In this test the FeedbackTopBlock is utilized with n waveform algorithm as manager, an energy and a feedback algorithm.
	def test_003(self):

		# Random 'signal' utilized in the test
		arr = [random.random() for i in xrange(1024)]
		fft_size = 1024

		device = RadioDevice(blocks.vector_source_c(data = arr, vlen = 1), blocks.probe_signal_f())

		# Bayes learning parameters
		in_th = 1
		min_th = 0.001
		max_th = 20
		delta_th = 0.001
		k = 1

		# Feeback architecture
		bl_algo = BayesLearningThreshold( in_th = in_th,
				min_th = min_th,
				max_th = max_th,
				delta_th = delta_th,
				k = k)

		# detectors utilized
		bl = EnergyDetectorC( fft_size, 1, bl_algo )
		ev = WaveformDetector( fft_size, WaveformDecision(0.7) )


		# top block
		self.tb = FeedbackTopBlock(device = device,
				block_manager =  ev,
				block_learner = bl,
				feedback_algorithm = FeedbackAlgorithm( bl_algo, AlwaysTimeFeedback() ),
			)
		self.tb.run()

		# As the waveform will (probably) not detected the channel as occupied, the feedback system should decrease the threshold by 1
		self.assertEqual(0, bl_algo.feedback)

if __name__ == '__main__':
	gr_unittest.main()
