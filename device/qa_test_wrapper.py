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
<<<<<<< HEAD
from radioDevice              import RadioDevice
from algorithm.decision        import EnergyDecision
from reception.sensing.energy import EDTopBlock

## Test algorithm 
#
class QaAlgorithm(unittest.TestCase):
from radioDevice          import RadioDevice
from algorithm.decision   import EnergyDecision
from reception.sensing    import EDTopBlock

## Test algorithm 
#

class QaAlgorithm(unittest.TestCase):

	## Test UHDWrapper
	def test_uhd_001(self):
		uhd = UHDWrapper(device = None, algorithm = EnergyDecision(10))

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
				algorithm = EnergyDecision(threshold)
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
				algorithm = EnergyDecision(threshold)
			)

		uhd = UHDWrapper(device, ed)

		uhd.run()
		self.assertEqual(expected_result , uhd.output)


if __name__ == '__main__':
	unittest.main()
