## @package ssf

import numpy as np
from gnuradio import gr, fft, blocks

from ss_utils import Logger


## Waveform analyzer.
# Receives a waveform and output if a match occurs.
class waveform_analyzer(gr.sync_block):

	## CTOR.
	# @param vec_size Size of each input.
	# @param algorithm Waveform detection algorithm.
	def __init__(self, vec_size, algorithm):
		gr.sync_block.__init__(
				self,
				name = "waveform_analyzer",
				in_sig = [np.dtype((np.float32, vec_size))],
				out_sig = [np.float32]
			)

		self.algorithm = algorithm

		# Debug
		Logger.register('waveform_analyzer', ['decision'])


	## Process inputs.
	# @param	input_items		Input array with float values.
	# @param	output_items	Energy calculated.
	def work(self, input_items, output_items):
		in0 = input_items[0]
		out0 = output_items[0]

		out0[:] = self.algorithm.decision( in0[0] )

		# Debug
		Logger.append('waveform_analyzer', 'decision', out0[0])

		return len(in0)



##  Top level of waveform detector
# Construct the flow graph for a waveform detector from the source to the detection algorithm.
# The flow graph is resumed as follows: source -> [ s2v -> fft -> c2mag**2 ->  waveform analyser] -> sync.
class waveform_detector(gr.hier_block2):

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

		self.s2v_0 = gr.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
		self.fft_0 = fft.fft_vcc(fft_size, True, [])
		self.c2mag_0 = gr.complex_to_mag_squared(fft_size)

		self.wd = waveform_analyzer(fft_size, algorithm)


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
