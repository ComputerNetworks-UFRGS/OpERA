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

## @package reception

from gnuradio import gr
from gnuradio import fft
from gnuradio import blocks

import numpy as np

from device import UHDSSArch
from utils import Logger


## Waveform analyzer.
# Receives a waveform and output if a match occurs.
class WaveformAnalyzer(gr.sync_block):

	## CTOR.
	# @param vec_size Size of each input.
	# @param algorithm Waveform detection algorithm.
	def __init__(self, vec_size, algorithm):
		gr.sync_block.__init__(
				self,
				name = "WaveformAnalyzer",
				in_sig = [np.dtype((np.float32, vec_size))],
				out_sig = [np.float32]
		)

		self._algorithm = algorithm
		self._corr = 0


	## Process inputs.
	# @param	input_items		Input array with float values.
	# @param	output_items	Energy calculated.
	def work(self, input_items, output_items):
		in0  = input_items[0]
		out0 = output_items[0]

		dec, self._corr =  self._algorithm.decision( in0[0] )
		out0[0] = dec 

		return len(input_items)

	## Return the most recent calculated correlation.
	# @return Most recent correlation.
	def output(self):
		return self._corr



##  Top level of waveform detector
# Construct the flow graph for a waveform detector from the source to the detection algorithm.
# The flow graph is resumed as follows: source -> [ s2v -> fft -> c2mag**2 ->  waveform analyser] -> sync.
class WaveformDetectorC(gr.hier_block2):

	## CTOR
	# @param fft_size FFT size (output of FFT is passed to the algorithm object).
	# @param algorithm Waveform Algorithm. An AbstractAlgorithm implementation.
	def __init__(self, fft_size, algorithm):
		gr.hier_block2.__init__(
				self,
				name = "waveform detector",
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(1, 1, gr.sizeof_float)
		)

		s2v_0   = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
		fft_0   = fft.fft_vcc(fft_size, True, [])
		c2mag_0 = blocks.complex_to_mag_squared(fft_size)

		self._wd = WaveformAnalyzer(fft_size, algorithm)

		self.connect(self, s2v_0, fft_0, c2mag_0, self._wd, self)


class WaveformSSArch( UHDSSArch ):

	## CTOR
	# @param fft_size
	# @param algorithm
	def __init__(self,  fft_size, algorithm):
		UHDSSArch.__init__(
			self,
			name = "WaveformSSArch",
			input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
			output_signature = gr.io_signature(1, 1, gr.sizeof_float),
		)


		# Flow
		self._detector = WaveformDetectorC(
				fft_size  = fft_size,
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
		# Configure device center frequency
		# ::TRICK:: self._device  can be a DeviceChannelModel object
		#		   If is the case, then check the DeviceChannelModel::center_freq method

		self.radio.center_freq = the_channel

		# Sleep for sensing_time
		# ::TODO:: This should be removed.
		time.sleep( sensing_time )
		return self.output()


	##
	#
	def output(self):
		return self._detector._wc.output()
