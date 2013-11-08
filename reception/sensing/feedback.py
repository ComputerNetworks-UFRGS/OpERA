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

"""
@package ssf
"""


from gnuradio        import gr
from device          import UHDSSArch
import numpy as np


class FeedbackF(gr.sync_block):
	"""
	Feedback block
	Has two inputs: 0- decision from the learning algorithm; 1- decision from the manager algorithm
	Both inputs are passed to a controller  algorithm (self._algorithm).

	Ideally, the frequency of both inputs should be equal (1:1)
	"""

	def __init__(self, algorithm):
		"""
		CTOR
		@param algorith AbstractAlgorithm. Must implement algorithm.decision(param1, param2)
		"""

		# initialize base class
		gr.sync_block.__init__(
				self,
				name = 'FeedbackF',
				in_sig = [np.float32, np.float32],
				out_sig = None
			)

		# algorithm de feedback
		self._algorithm = algorithm

	def work(self, input_items, output_items):
		"""
		GNURadio loop function.
		@param input_items
		@param output_items
		"""

		in0 = input_items[0][0] # learner
		in1 = input_items[1][0] # manager

		self._algorithm.decision(in0, in1)

		return len(input_items[0])


class FeedbackSSArch( UHDSSArch ):
	"""
	Feedback Architecture.

	Instantiate this block if you want the feedback architecture described in the paper: "An Adaptive Feedback System to Threshold Learning for Cognitive Radios".

	Inputs: 1 complex at a time.
	Output: {0,1} regarding channel occupancy.
	"""

	def __init__(self,
			block_manager,
			block_learner,
			feedback_algorithm):
		"""
		CTOR
		
        @param block_manager Sensing block that is considered always correct
        @param block_learner Sensing block which threshold is adjusted
        @param feedback_algorithm Feedback Algorithm
		"""

		UHDSSArch.__init__( 
				self,
				name = "feedback_arch",
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(1, 1, gr.sizeof_float)
			)

		# feedback block
		self.fb = FeedbackF( feedback_algorithm ) 	

		# source -> ss algorithm (learning) -> sink 
		self.connect(self, block_learner, self)

		# source -> ss algorithm (always correct) -> sink
		self.connect(self, block_manager)

		# ss algorithm (learning) -> feedback system
		self.connect(block_learner, (self.fb, 0))

		# ss algorithm (always correct) -> feedback system
		self.connect(block_manager, (self.fb, 1))



	def _get_sensing_data(self, channel, sensing_time):
		return 0
