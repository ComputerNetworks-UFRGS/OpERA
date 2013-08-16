## @package ssf

from gnuradio           import gr
from ss_utils           import TopBlock

import numpy as np


## Feedback block
# Has two inputs: 0- decision from the learning algorithm; 1- decision from the manager algorithm
# Both inputs are passed to a controller  algorithm (self._algorithm).
# Ideally, the frequency of both inputs should be equal (1:1)
class feedback_f(gr.sync_block):
	"""
	Feedback block
	Has two inputs: 0- decision from the learning algorithm; 1- decision from the manager algorithm
	Both inputs are passed to a controller  algorithm (self._algorithm).

	Ideally, the frequency of both inputs should be equal (1:1)
	"""

	## CTOR
	#@param algorithm AbstractAlgorithm implementation. Should implement a decision function with received two parameters
	def __init__(self, algorithm):

		# initialize base class
		gr.sync_block.__init__(
				self,
				name = 'feedback_f',
				in_sig = [np.float32, np.float32],
				out_sig = None
			)

		# algorithm de feedback
		self._algorithm = algorithm

	## GNURadio loop function
	# @param input_items
	# @param output_items
	def work(self, input_items, output_items):

		in0 = input_items[0][0] # learner
		in1 = input_items[1][0] # manager

		self._algorithm.decision(in0, in1)

		return len(input_items[0])

class feedback_arch(gr.hier_block2):
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

		gr.hier_block2.__init__( 
				self,
				name = "feedback_arch",
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(1, 1, gr.sizeof_float)
			)

		# feedback block
		self.fb = feedback_f( feedback_algorithm ) 	

		# dump file
		#self._file = gr.file_sink( gr.sizeof_gr_complex, '/tmp/signal.bin')
		#self.connect(self, self._file)

		# source -> ss algorithm (learning) -> sink 
		self.connect(self, block_learner, self)

		# source -> ss algorithm (always correct) -> sink
		self.connect(self, block_manager)

		# ss algorithm (learning) -> feedback system
		self.connect(block_learner, (self.fb, 0))

		# ss algorithm (always correct) -> feedback system
		self.connect(block_manager, (self.fb, 1))


class FeedbackTopBlock(TopBlock):
	"""
	A Feedback top block
	"""

	def __init__(self,
			device,
			block_manager,
			block_learner,
			feedback_algorithm):
		"""
		CTOR

		@param device             Device ( a UHDWrapper object)
		@param block_manager      Sensing block that is considered always correct
		@param block_learner      Sensing block which threshold is adjusted
		@param feedback_algorithm Feedback Algorithm
		@param use_throttle       To use a throttle control before the feedback_f
		"""

		TopBlock.__init__(self, "Feedback Topblock")

		arch = feedback_arch( 
				block_manager = block_manager,
				block_learner = block_learner,
				feedback_algorithm = feedback_algorithm
			)

		self.connect(device.source, arch, device.sink)

		self.rx        = device
		self.algorithm = arch
