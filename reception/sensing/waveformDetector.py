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

import numpy as np
from gnuradio import gr, fft, blocks

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

		self.algorithm = algorithm


		Logger.register('waveform', ['decision', ])


	## Process inputs.
	# @param	input_items		Input array with float values.
	# @param	output_items	Energy calculated.
	def work(self, input_items, output_items):
		in0 = input_items[0]
		out0 = output_items[0]

		out0[0] = self.algorithm.decision( in0[0] )

		Logger.append('waveform', 'decision', out0[0])

		return len(input_items)



##  Top level of waveform detector
# Construct the flow graph for a waveform detector from the source to the detection algorithm.
# The flow graph is resumed as follows: source -> [ s2v -> fft -> c2mag**2 ->  waveform analyser] -> sync.
class WaveformDetector(gr.hier_block2):

	## CTOR
	# @param fft_size FFT size (output of FFT is passed to the algorithm object).
	# @param algorithm Waveform Algorithm. An AbstractAlgorithm implementation.
	# @param dec Decimation (usually not necessary). NOT USED ANYMORE.
	def __init__(self, fft_size, algorithm, dec = 1):
		gr.hier_block2.__init__(
			self,
			name = "waveform detector",
			input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
			output_signature = gr.io_signature(1, 1, gr.sizeof_float)
		)

		self.s2v_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
		self.fft_0 = fft.fft_vcc(fft_size, True, [])
		self.c2mag_0 = blocks.complex_to_mag_squared(fft_size)

		self.wd = WaveformAnalyzer(fft_size, algorithm)

		self.connect(self, self.s2v_0, self.fft_0, self.c2mag_0, self.wd, self)

## Waveform detector top block
# Waveform detector as the only top block.
class WaveformTopBlock(gr.top_block):

	## CTOR
	# @param fft_size FFT Size.
	# @param device Device. A UHDAlgorithmInterface instance.
	# @param algorithm Correlation algorithm. An AbstractAlgorithm implementation.
	def __init__(self, fft_size, device, algorithm):
		gr.top_block.__init__(self, "Waveform Detector Blocks")

		self.wd = waveform_detector(fft_size, algorithm)
		self.connect(device.source, self.wd, device.sync)
