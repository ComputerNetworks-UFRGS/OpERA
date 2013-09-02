#!/usr/bin/env python

## @package architecture

# ::TODO:: Discover how to include patches externally
import sys
import os
import random

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../.."))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, uhd


# UUT
from ranking_arch import *


## QA tests related to ranking.
class QaRanking(gr_unittest.TestCase):

	## 
	def setUp(self):
		self.tb = gr.top_block()

	##
	def tear_down(self):
		self.tb = None


	##
	def test_001(self):
		## TODO
		pass


if __name__ == '__main__':
	gr_unittest.main()
