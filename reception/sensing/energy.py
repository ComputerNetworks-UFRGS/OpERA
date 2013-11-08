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

from device import UHDSSArch
from utils import Logger, TopBlock

## Calculate the energy
# Receives a vector of floats as inputs.
class EnergyCalculator(gr.sync_block):

	## CTOR
	# @param vec_size
	# @param algorithm
	def __init__(self, vec_size, algorithm, name="energy_calculator"):
		gr.sync_block.__init__(
				self,
				name = name,
				in_sig = [np.dtype((np.float32, vec_size))], 
				out_sig = [np.float32]
			)
		
		self._algorithm = algorithm
		self._energy = 0

		if not self._algorithm:
			raise AttributeError("algorithm must be an ThresholdLearningAlgorithm")

	## Calculate the energy
	# @param	input_items	Input array with float values
	# @param	output_items	Energy calculated
	def work(self, input_items, output_items):
		in0  = input_items[0][0]
		out0 = output_items[0]

		# Process input
		dec, self._energy = self._algorithm.decision( in0 )
		out0[0] = dec

		return len(input_items)

	## Return the energy
	# @return Energy
	def output(self):
		return self._energy

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
		s2v_0   = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
		fft_0   = fft.fft_vcc(fft_size, True, [])
		c2mag_0 = blocks.complex_to_mag_squared(fft_size)

		## Instatiate the energy calculator
		self._ec  = EnergyCalculator(fft_size, algorithm)

		## Flow graph
		self.connect(self, s2v_0, fft_0, c2mag_0, self._ec, self)



## A UHDSSArch with the energy detector.
# Provides the sense_channel() method to sense a list of channels.
class EnergySSArch(UHDSSArch):

	## CTOR
	# @param fft_size FFT Lenght utilized in the EnergyDetector.
	# @param mavg_size Number of elements considered in the energy moving average.
	# @param algorithm Detection algorithm (usually a EnergyAlgorithm instance).
	def __init__(self, fft_size, mavg_size, algorithm):

		UHDSSArch.__init__(
			self,
			name = "EnergySSArch",
			input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
			output_signature = gr.io_signature(1, 1, gr.sizeof_float),
		)

		# Flow
		self._detector = EnergyDetectorC(
				fft_size  = fft_size,
				mavg_size = mavg_size,
				algorithm = algorithm
			)

		#             #
		# Connections #
		#             #
		self.connect(self, self._detector, self)


	## Configure the device to sense the given frequency.
	# @param the_channel Channel object instance. Channel to sense.
	# @param sensing_time Duration of sensing.
	# @return SS information of channel.
	def _get_sensing_data(self, the_channel, sensing_time):

		# Sleep for sensing_time
		time.sleep( sensing_time )
		return self.output()

	##
	#
	def output(self):
		return self._detector._ec.output()
