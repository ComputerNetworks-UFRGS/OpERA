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

## @package ssf

from gnuradio                   import gr
from gnuradio					import fft
from gnuradio					import blocks
from device                     import UHDSSArch
from utils.sensing.top_block    import TopBlock
from utils.block                import GroupInN
from algorithm                  import decision
from reception.sensing          import EnergyCalculator

import time
import threading
import numpy as np

## QLearning worker block
# Input: vector of vec_size elements
# Ouput: (decision, energy), where:
#	- decision: 1 or 0
#	- energy  : energy calculated
class QLearningWorker(gr.sync_block):

	## CTOR
	# @param vec_size Size of each input.
	# @param algorithm Detection algorithm. An AbstractAlgorithm implementation
	def __init__(self, vec_size, algorithm):
		gr.sync_block.__init__(
				self,
				name = "qlearning_worker",
				in_sig =   [np.dtype((np.float32, vec_size))], 
				out_sig =  [np.float32]
			)
		self.algorithm = algorithm


	## GNU Radio main function.
	# @param input_items
	# @param output_items
	def work(self, input_items, output_items):
		in0 = input_items[0][0]

		# Process input
		energy = np.sum( in0 ) / in0.size
		output_items[0][0] = energy

		return len(input_items)

## QLearning hierarchical block.
# Builds flow graph from source to sync.
class SimpleRankingDetector(gr.hier_block2):

	## CTOR
	# @param fft_size FFT Size
	# @param mavg_size Energy Detector mavg size.
	def __init__(self,
			fft_size,
			mavg_size,
			ed_threshold):

		gr.hier_block2.__init__(
				self,
				name = "simple_ranking_detector",
				input_signature =  gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(1, 1, gr.sizeof_float)
			)

		# Blocks
		# Convert the output of a FFT
		self.s2v_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
		self.fft_0 = fft.fft_vcc(fft_size, True, [])
		self.c2mag_0 = blocks.complex_to_mag_squared(fft_size)

		# Instatiate the energy calculator
		self.ql  = QLearningWorker(fft_size, algorithm = sensing.EnergyAlgorithm( ed_threshold ))
		self.mavg = blocks.moving_average_ff(mavg_size, 1.0/mavg_size)

		# Flow graph
		self.connect(self, self.s2v_0, self.fft_0, self.c2mag_0, self.ql, self)


## Ranking architecture.
# Construct the ranking architecture.
class RankingArch( UHDSSArch ):

	## CTOR.
	# @param device     RadioDevice instance.
	# @param detector   A SS detector. 
	# @param group_vlen Number of ouputs to group.
	# @return A tuple with 3 elements: (final decision, energy, avg energy)
	def __init__(self, device, detector, group_vlen):

		UHDSSArch.__init__(
				self,
				uhd = device,
				name = "ranking_arch",
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(0, 0, 0)
			)

		# Group items
		self._grouper  = GroupInN(
				group_vlen = group_vlen,
				callback = None,
				n_inputs = 1
			)

		self._detector = detector

		# inputs
		self.connect( self, detector, self._grouper)

		# no outputs

	## Configure the device to sense the given frequency.
	# @param the_channel Channel object instance. Channel to sense.
	# @param sensing_time Duration of sensing.
	# @return SS information of channel.
	def _get_sensing_data(self, the_channel, sensing_time):

		# Configure device center frequency
		# ::TRICK:: self._device  can be a DeviceChannelModel object
		#           If is the case, then check the DeviceChannelModel::center_freq method
		#self.uhd.center_freq = the_channel
		self._grouper.set_enable( True )

	## SS on a single channel
	# Reimplement from UHDSSArch::sense_channel
	# @param the_channel Channel to be sensed.
	# @param sensing_time Sensing duration on channel.
	def sense_channel(self, the_channel, sensing_time):
		self._get_sensing_data( the_channel, sensing_time )


## Ranking top block.
class RankingRunner( TopBlock ):

	## CTOR
	# @param device A RadioDevice instance.
	# @param detector A SS with three outputs: 0- decision, 1- energy, 2- avg energy
	# @param group_vlen 
	def __init__(self,
			device,
			detector,
			group_vlen):
		TopBlock.__init__(self, name = 'Ranking Top Block')

		# processing blocks
		self._device = device
		self.rx = RankingArch(device = device, detector = detector, group_vlen = group_vlen)
		self.connect(device.source, self.rx)
