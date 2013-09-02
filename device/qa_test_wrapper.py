#!/usr/bin/python

## @package algorithm

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../"))
sys.path.insert(0, path)

import unittest

from gnuradio import blocks 

from uhdWrapper import UHDWrapper

# Other modules needed
from radioDevice              import RadioDevice
from algorithm.sensing        import EnergyAlgorithm
from reception.sensing.energy import EDTopBlock

## Test algorithm 
#
class Qa_Algorithm(unittest.TestCase):

	## Test UHDWrapper
	def test_uhd_001(self):
		uhd = UHDWrapper(device = None, algorithm = EnergyAlgorithm(10))

		self.assertEqual(uhd.threshold, 10)
		uhd.threshold = 11
		self.assertEqual(uhd.threshold, 11)

	## Test UHDAlgorithm  with a EDTopblock
	# In this test the energy outputed is greater than the threshold
	def test_uhd_002(self):
		expected_result =  1

		# ::TRICKY:: ED output is different from the sum os arr elements
		arr = (1, 1, 1, 1, 1, 1, 1, 1) 
		threshold = 1 

		device = RadioDevice(the_source = blocks.vector_source_c(data = arr, vlen = 1),
				the_sink = blocks.probe_signal_f(), uhd_device = None )

		ed = EDTopBlock(addr = "",
				fft_size = len(arr),
				moving_avg_size = 1,
				samp_rate = 100e3,
				device = device,
				algorithm = EnergyAlgorithm(threshold)
			)

		uhd = UHDWrapper(device, ed)
		uhd.run()

		# Channel must be declared as occupied
		self.assertEqual(expected_result , uhd.output)


	## Test UHDAlgorithm  with a EDTopblock
	# In this test the energy outputed is less than the threshold
	def test_uhd_003(self):
		expected_result = 0

		# ::TRICKY:: ED output is different from the sum os arr elements
		arr = (1, 1, 1, 1)
		threshold = 1000

		device = RadioDevice(the_source = blocks.vector_source_c(data = arr, vlen = 1),
				the_sink = blocks.probe_signal_f())

		ed = EDTopBlock(addr = "",
				fft_size = len(arr),
				moving_avg_size = 1,
				samp_rate = 100e3,
				device = device,
				algorithm = EnergyAlgorithm(threshold)
			)

		uhd = UHDWrapper(device, ed)

		uhd.run()
		self.assertEqual(expected_result , uhd.output)


if __name__ == '__main__':
	unittest.main()
