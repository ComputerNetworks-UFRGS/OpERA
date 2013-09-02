#!/usr/bin/python

## @package device

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, path)

from gnuradio import blocks
from time import sleep
import unittest

# Project imports
from radioDevice import RadioDevice

## Test UHD device
class QaUHD(unittest.TestCase):

	## Test RadioDevice instantiation
	## @TODO Create a dummy UHD device
	def test_001(self):
		source = blocks.vector_source_c( [1] * 8 )
		sync = blocks.probe_signal_f()

		dev = RadioDevice(source, sync)


if __name__ == '__main__':
	unittest.main()
