#!/usr/bin/env python

## @package ssa
# SSA classes

# ::TODO:: Discover how to include patches externally
import sys, os

path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, path)

from gnuradio import gr, uhd
import unittest

# Project imports
from device                     import UHDDevice
from ssf.uhd.detectors.energy   import EDTopBlock 
from ssf.uhd.detectors.waveform import WaveformTopBlock 
from ssf.algorithm              import EnergyAlgorithm, WaveformAlgorithm

# UUT
from ssa import SSA
from ssaConfiguration import SSAConfiguration

from time import sleep


## QA tests related to SSA
class qa_ssa(unittest.TestCase):

	def setUp(self):
		self.tb = gr.top_block()

	def tearDown(self):
		self.tb = None

	#def test_001(self):
	#	src = uhd.usrp_source(device_addr='',
	#			stream_args=uhd.stream_args(cpu_format='fc32')
	#		)

	#	device = UHDDevice( src, gr.probe_signal_f() )

	#	device.samp_rate = 195312

	#	ed = EDTopBlock(addr = "",
	#			fft_size = 512,
	#			moving_avg_size = 1,
	#			samp_rate = 195312,
	#			device = device,
	#			algorithm = EDAlgorithm(0.00001)
	#		)


	#	ssa = SSA( SSAConfiguration(), UHDAlgorithmInterface(device, ed))
	##	ssa.start()

	#def test_002(self):
	#	src = uhd.usrp_source(device_addr='',
	#			stream_args=uhd.stream_args(cpu_format='fc32')
	#		)

	#	device = UHDDevice( src, gr.probe_signal_f() )

	#	device.samp_rate = 195312

	#	ed = WaveformTopBlock(fft_size = 512,
	#			device = device,
	#			algorithm = WaveformAlgorithm(0.7)
	#		)

	#	ssa = SSA( SSAConfiguration(), UHDAlgorithmInterface(device, ed))
	#	ssa.start()


	#def test_002(self):
	#	src = uhd.usrp_source(device_addr='',
	#			stream_args=uhd.stream_args(cpu_format='fc32')
	#		)

	#	device = UHDDevice( src, gr.probe_signal_f() )
	#	device.samp_rate = 195312


	#	ed = EDTopBlock(addr = "",
	#			fft_size = 1024,
	#			moving_avg_size = 1,
	#			samp_rate = 195312,
	#			device = device,
	#			algorithm = EDAlgorithm( 0.005 )
	#		)

	#	ssa = SSA( SSAConfiguration(), UHDAlgorithmInterface(device, ed))
	#	ssa.start()

if __name__ == "__main__":
	unittest.main()
