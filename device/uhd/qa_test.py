#!/usr/bin/python

## @package device

# ::TODO:: Discover how to include patches externally
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, path)

from gnuradio import gr
from time import sleep
import unittest

# Project imports
from uhdDevice import UHDDevice

## Test UHD device
class qa_uhd(unittest.TestCase):

	## Test UHDDevice instantiation
	## @TODO Create a dummy UHD device
	def test_001(self):
		source = gr.vector_source_c( [1] * 8 )
		sync = gr.probe_signal_f()

		dev = UHDDevice(source, sync)


if __name__ == '__main__':
	unittest.main()
