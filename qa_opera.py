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

## @package algorithm

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),""))
sys.path.insert(0, path)

import unittest

from gnuradio import blocks 

from OpERAFlow import OpERAFlow
from utils import Verify

# Other modules needed
from device.radioDevice   import RadioDevice
from algorithm.decision   import EnergyDecision
from reception.sensing    import EnergySSArch
from device import *

## Test algorithm 
#

class QaAlgorithm(unittest.TestCase):

	## Test OpERAFlow
	def test_uhd_001(self):
		algorithm = EnergyDecision(10)
		opera = OpERAFlow("uhd_device")
		opera.add_path(algorithm, None, "energy_decision")

		self.assertEqual(opera.energy_decision.threshold, 10)
		opera.energy_decision.threshold = 11
		self.assertEqual(opera.energy_decision.threshold, 11)

	## Test UHDAlgorithm  with a EDTopblock
	# In this test the energy outputed is greater than the threshold
	def test_uhd_002(self):
		expected_result =  1

		# ::TRICKY:: ED output is different from the sum os arr elements
		arr = (1, 1, 1, 1, 1, 1, 1, 1) 
		threshold = 1 

		device = RadioDevice(the_source = blocks.vector_source_c(data = arr, vlen = 1),
				the_sink = blocks.probe_signal_f(), uhd_device = None )

		ed = EnergySSArch(
				fft_size = len(arr),
				mavg_size = 1,
				algorithm = EnergyDecision(threshold)
			)

		opera = OpERAFlow("ed_device")
		opera.add_path(ed, device, "ed")
		opera.run()

		# Channel must be declared as occupied
		self.assertEqual(expected_result , opera.ed.radio.sink.level())


	## Test UHDAlgorithm  with a EDTopblock
	# In this test the energy outputed is less than the threshold
	def test_uhd_003(self):
		expected_result = 0

		# ::TRICKY:: ED output is different from the sum os arr elements
		arr = (1, 1, 1, 1)
		threshold = 1000

		device = RadioDevice(the_source = blocks.vector_source_c(data = arr, vlen = 1),
				the_sink = blocks.probe_signal_f())

		ed = EnergySSArch(
				fft_size = len(arr),
				mavg_size = 1,
				algorithm = EnergyDecision(threshold)
			)

		opera = OpERAFlow("ed_device")
		opera.add_path(ed, device, "ed")
		opera.run()

		self.assertEqual(expected_result , opera.ed.radio.sink.level())

	## check if parameters are ok
	def test_parameters01(self):

		arr = (1, 1, 1, 1)
		threshold = 1000

		device = RadioDevice(the_source = blocks.vector_source_c(data = arr, vlen = 1),
				the_sink = blocks.probe_signal_f())

		ed = EnergySSArch(
				fft_size = len(arr),
				mavg_size = 1,
				algorithm = EnergyDecision(threshold)
			)

		opera = OpERAFlow("ed_device")
		opera.add_path(ed, device, "ed")

		a = 12
		b = 9090
		list_error, check_attr = Verify.check_parameters([a, b, device, ed], [(0, 12), [9, 89, 9090, 189], AbstractDevice, AbstractDevice])
		print "checking attr"
		if check_attr is True:
			print "parameters ok"
		else:
			print "error"

		print list_error
	


if __name__ == '__main__':
	unittest.main()
