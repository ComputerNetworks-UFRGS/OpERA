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

## @package architecture

# ::TODO:: Discover how to include patches externally
# ::TODO:: modules description
import sys
import os
import random
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../"))
sys.path.insert(0, path)


from time     import *
from math     import *
from gnuradio import gr, gr_unittest, uhd, blocks

# UUT
from utils.block    import GroupInN


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
		arr = [1.0, 1.0, 1.0]
		expected_result = [(1, 1, 1)]

		grouper_vlen = len(expected_result) + 1 # +1 to not activate the callback

		src = blocks.vector_source_f( data = arr , vlen = 1)
		grouper = GroupInN( group_vlen = 1, callback = None,  n_inputs = 3 )
		grouper.set_enable( True )

		self.tb.connect( src, (grouper, 0))
		self.tb.connect( src, (grouper, 1))
		self.tb.connect( src, (grouper, 2))
		self.tb.run()

		result_data = grouper._item_group

		# Verify expected result 
		self.assertEqual(expected_result, result_data)


	## Test if the group_in_n  is able to group a single input
	# In this test the number os total grouped itens is 1
	def test_002(self):
		arr = [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]
		expected_result = [(1, 1, 1), (2, 2, 2)]

		grouper_vlen = len(expected_result) + 1 # +1 to not activate the callback

		src = blocks.vector_source_f( data = arr , vlen = 1, repeat = False )
		grouper = GroupInN( group_vlen = 2, callback = None,  n_inputs = 3 )
		grouper.set_enable( True )

		self.tb.connect( src, (grouper, 0))
		self.tb.connect( src, (grouper, 1))
		self.tb.connect( src, (grouper, 2))
		self.tb.run()

		result_data = grouper._item_group

		# Verify expected result
		self.assertEqual(expected_result, result_data)


if __name__ == '__main__':
	gr_unittest.main()
