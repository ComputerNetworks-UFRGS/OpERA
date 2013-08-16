#!/usr/bin/python

## @package ssf
# SSF classes

# ::TODO:: Discover how to include patches externally
import sys, os

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../../"))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, fft
import numpy as np

from waveformDetector import waveform_analyzer, WaveformTopBlock
from device import UHDDevice
from ssf.algorithm import WaveformAlgorithm

## QA related to Waveform class
#
class qa_waveform(gr_unittest.TestCase):

	def setUp(self):
		self.tb = gr.top_block()

	def tearDown(self):
		self.tb = None

	def test_0001(self):
		## @TODO
		pass

if __name__ == '__main__':
	gr_unittest.main ()
