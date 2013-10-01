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

## @file energyDetector.py

## @package ssf
#  Module with algorithms to sense a spectrum

from gnuradio import blocks, fft, gr

import time
import math
import numpy as np

from device					  import UHDSSArch
from utils.sensing.top_block  import TopBlock
from utils.sensing            import Logger

## Calculate the energy
# Receives a vector of floats as inputs.
class EnergyCalculator(gr.sync_block):

	## CTOR
	# @param vec_size
	# @param algorithm
	def __init__(self, vec_size, algorithm):
		gr.sync_block.__init__(
				self,
				name = "energy_calculator",
				in_sig =   [np.dtype((np.float32, vec_size))], 
				out_sig =  [np.float32]
			)
		self.algorithm = algorithm

		Logger.register('energy_calculator', ['energy', 'decision' ] )


		self._count = 0

	## Calculate the energy
	# @param	input_items	Input array with float values
	# @param	output_items	Energy calculated
	def work(self, input_items, output_items):
		in0  = input_items[0][0]
		out0 = output_items[0]

		# Process input
		energy = np.sum( np.square(in0) ) / (in0.size)
		out0[0] = self.algorithm.decision( energy ) if self.algorithm else energy


		Logger.append('energy_calculator', 'energy', energy)
		Logger.append('energy_calculator', 'decision', out0[0])

		return len( input_items )

## Top level of Energy Detector sensing algorithm
# A object of this class must be declared and connected in a flow blocksaph.
# The inputs are:
# 	in0	:	A vector of floats with len fft_size
# 	out0:	A single float that represents the energy calculated
class EnergyDetectorC(gr.hier_block2):

	## CTOR
	# @param fft_size
	# @param mavg_size
	def __init__(self, fft_size, mavg_size, algorithm):
		gr.hier_block2.__init__(
				self,
				name = "energy_detector",
				input_signature  =  gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature =  gr.io_signature(1, 1, gr.sizeof_float),
			)

		# Blocks
		# Convert the output of a FFT
		self.s2v_0   = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
		self.fft_0   = fft.fft_vcc(fft_size, True, [])
		self.c2mag_0 = blocks.complex_to_mag_squared(fft_size)

		## Instatiate the energy calculator
		self.ec  = EnergyCalculator(fft_size, algorithm)

		## Flow graph
		self.connect(self, self.s2v_0, self.fft_0, self.c2mag_0, self.ec, self)

## A UHDSSArch with the energy detector.
# Provides the sense_channel() method to sense a list of channels.
class EnergySSArch( UHDSSArch ):

	## CTOR
	# @param device RadioDevice instance.
	# @param fft_size FFT Lenght utilized in the EnergyDetector.
	# @param mavg_size Number of elements considered in the energy moving average.
	# @param algorithm Detection algorithm (usually a EnergyAlgorithm instance).
	def __init__(self, device, fft_size, mavg_size, algorithm):

		UHDSSArch.__init__(
			self,
			uhd				 = device,
			name			 = "EnergySSArch",
			input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
			output_signature = gr.io_signature(1, 1, gr.sizeof_float),
		)


		# Flow
		self._detector = EnergyDetectorC(
				fft_size  = fft_size,
				mavg_size = mavg_size,
				algorithm = algorithm
			)

		self._sink = device.sink

		#             #
		# Connections #
		#             #
		self.connect(self, self._detector, self)

	## Configure the device to sense the given frequency.
	# @param the_channel Channel object instance. Channel to sense.
	# @param sensing_time Duration of sensing.
	# @return SS information of channel.
	def _get_sensing_data(self, the_channel, sensing_time):
		# Configure device center frequency
		# ::TRICK:: self._device  can be a DeviceChannelModel object
		#		   If is the case, then check the DeviceChannelModel::center_freq method
		self.uhd.center_freq = the_channel

		# Sleep for sensing_time
		# ::TODO:: This should be removed.
		time.sleep( sensing_time )

		return self._sink.level()


	@property
	def output(self):
		return self._sink.level()


## Energy Detector top block
# ::TODO:: Update to UHDSSArch implementation
class EDTopBlock( TopBlock ):

	# CTOR
	# @param addr
	# @param fft_size
	# @param moving_avg_size
	# @param samp_rate
	# @param device RadioDevice object
	# @param algorithm
	def __init__(self, addr, fft_size, moving_avg_size, samp_rate, device, algorithm):
		## @TODO Flow graph should be constructed outside
		TopBlock.__init__(self, "Energy Detector Blocks")

		ed = EnergyDetectorC(fft_size, moving_avg_size, algorithm)
		self.connect(device.source, ed, device.sink)

		self.rx = ed
