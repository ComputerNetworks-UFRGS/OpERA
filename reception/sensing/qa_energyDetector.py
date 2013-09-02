#!/usr/bin/python

## @package ssf

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../.."))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, fft, blocks

from energyDetector         import EnergyDetectorC, EDTopBlock
from device.radioDevice     import RadioDevice
from algorithm.decision      import EnergyDecision

import numpy as np

## QA related to EnergyDetector class.
class QaEnergyDetector(gr_unittest.TestCase):

	## Set globals for all tests. Called before a test is started.
	def setUp (self):
		self.tb = gr.top_block ()

	## Destroy globals for all tests. Called right after a test if finished.
	def tear_down (self):
		self.tb = None

	## Test the energy of a simple sequence (1, 2, -1, -2)
	def test_001(self):
		# input and expected results
		src_data = (1,1,1,1)
		expected_result = 1

		# blocks
		fft_size = len(src_data)
		mavg_size = 1

		src = blocks.vector_source_c(data = src_data)
		ed = EnergyDetectorC(fft_size, mavg_size, EnergyDecision(1) )
		dst = blocks.probe_signal_f()

		## flowgraph
		self.tb.connect (src, ed, dst)
		self.tb.run ()

		result_data = dst.level ()
		self.assertEqual(expected_result, result_data)

	## Test a sequence with float number (0.1, 0.1, 0.1, 0.1)
	def test_002(self):
		# input and expected results
		src_data = (0.1, 0.1, 0.1, 0.1)
		expected_result = 0

		# blocks
		fft_size = len(src_data)
		mavg_size = 1

		src = blocks.vector_source_c(data = src_data)
		ed = EnergyDetectorC(fft_size, mavg_size, EnergyDecision(1) )

		dst = blocks.probe_signal_f ()

		# flowgraph
		self.tb.connect (src, ed, dst)
		self.tb.run ()

		result_data = dst.level ()
		self.assertEqual(expected_result, result_data)

	## Test EDTopBlock with the input (1, 1, 1, 1, 1, 1, 1, 1)
	def test_003(self):
		arr = (1, 1, 1, 1, 1, 1, 1, 1)
		expected_out = 8

		device = RadioDevice(blocks.vector_source_c(data = arr, vlen = 1), blocks.probe_signal_f())

		ed = EDTopBlock(addr = "UHDSSArch",
				fft_size = len(arr),
				moving_avg_size = 8,
				samp_rate = 100e3,
				device = device,
				algorithm = EnergyDecision(expected_out - 1)
			)
		ed.run();

		out = device.output
		self.assertEqual(1 , out)

	## Test EDTopBlock with a simple input (1, 2, 3, 4)
	def test_004(self):
		arr = (1.0, 2.0, 3.0, 4.0)
		expected_out = 2536

		device = RadioDevice(blocks.vector_source_c(data = arr, vlen = 1), blocks.probe_signal_f())

		ed = EDTopBlock(addr = "",
				fft_size = len(arr),
				moving_avg_size = 1,
				samp_rate = 100e3,
				device = device,
				algorithm = EnergyDecision(expected_out + 1)
			)
		ed.run()

		out = device.output
		self.assertEqual(0, out)

if __name__ == '__main__':
	gr_unittest.main ()
