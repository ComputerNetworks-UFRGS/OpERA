#!/usr/bin/python

## @package architecture

# ::TODO:: Discover how to include patches externally
import sys
import os
import random
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../.."))
sys.path.insert(0, path)


from time     import *
from math     import *
from gnuradio import gr, gr_unittest, uhd, blocks

# UUT
from block    import GroupInN


## QA tests related to block utils
class QaUtils(gr_unittest.TestCase):

	##
	def setUp(self):
		self.tb = gr.top_block()

	##
	def tear_down(self):
		self.tb = None

	## Test if the group_in_n  is able to group a single input
	# In this test the number os total grouped itens is 1
	def test_001(self):
		arr = [1.0]
		expected_result = [(1, 1, 1)]

		grouper_vlen = len(expected_result) + 1 # +1 to not activate the callback

		src = blocks.vector_source_f( data = arr , vlen = 1)
		grouper = GroupInN( group_vlen = 1, callback = None,  n_inputs = 3 )

		self.tb.connect( src, (grouper, 0))
		self.tb.connect( src, (grouper, 1))
		self.tb.connect( src, (grouper, 2))
		self.tb.run()

		result_data = grouper.items

		# Verify expected result AND if the grouper is disable (should group only 1 input)
		self.assertEqual(expected_result, result_data)
		self.assertEqual(False, grouper._enable)

	## Test if the group_in_n  is able to group a single input
	# In this test the number os total grouped itens is 1
	def test_002(self):
		arr = [1.0, 2.0]
		expected_result = [(1, 1, 1), (2, 2, 2)]

		grouper_vlen = len(expected_result) + 1 # +1 to not activate the callback

		src = blocks.vector_source_f( data = arr , vlen = 1)
		grouper = GroupInN( group_vlen = 2, callback = None,  n_inputs = 3 )

		self.tb.connect( src, (grouper, 0))
		self.tb.connect( src, (grouper, 1))
		self.tb.connect( src, (grouper, 2))
		self.tb.run()

		result_data = grouper.items

		# Verify expected result AND if the grouper is disable (should group only 1 input)
		self.assertEqual(expected_result, result_data)
		self.assertEqual(False, grouper._enable)


if __name__ == '__main__':
	gr_unittest.main()
