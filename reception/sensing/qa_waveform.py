#!/usr/bin/python

## @package ssf
# SSF classes

# ::TODO:: Discover how to include patches externally
import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../../"))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, fft
import numpy as np

from waveformDetector import WaveformAnalyzer, WaveformTopBlock
from device import radioDevice
from algorithm import WaveformDecision

## QA related to Waveform class
#
class QaWaveform(gr_unittest.TestCase):

	def setUp(self):
		self.tb = gr.top_block()

	def tear_down(self):
		self.tb = None

	def test_0001(self):
		## @TODO
		pass

if __name__ == '__main__':
	gr_unittest.main ()
