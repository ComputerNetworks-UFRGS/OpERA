## @package block_util

from gnuradio import gr

import numpy as np

## Group inputs in blocks of N elements
# The operation if this block is as follows:
# 1) Construct a instance with 'n_inputs' inputs and that will group 'group_vlen' elements.
# 2) When the FlowGraph is running, call group_in_n::enableGrouping to start grouping items.
# 3) Call group_in_n::items to recover items.
# 4) Call group_in_n::enableGrouping again.
#
# ::TODO:: Call a callback function  when group_vlen items are grouped.
class group_in_n(gr.sync_block):

	## CTOR
	# @param group_vlen Number of elements to group before forwarding
	# @param callback   Function called when the data is grouped
	# @param n_inputs   number of inputs to group
	def __init__(self, group_vlen, callback, n_inputs = 1):

		gr.sync_block.__init__(
				self,
				name = 'array_grouper',
				in_sig = [ np.float32 ] * n_inputs,
				out_sig = None
			)

		self._enable   = True
		self._max_vlen = group_vlen
		self._callback = callback
		self._ninputs  = n_inputs

		self._item_group = []

	## Return grouped items.
	# @return Grouped items.
	@property
	def items(self):

		# Wait until  all items are grouped (if enought items have not been received)
		print 'entering grouper loop'
		while self._enable:
			1
		print 'exiting grouper loop'

		# clear current _item_group
		tmp = self._item_group
		self._item_group = []

		return tmp 

	## Enable grouping.
	def enable(self):
		self._enable = True

	def isEnable(self):
		return self._enable

	## GNU Radio main function.
	# The items are received and grouped in this function.
	def work(self, input_items, output_items):

		# Group data if enable
		if (self._enable == True) and ((len(self._item_group) < self._max_vlen) or self._max_vlen == -1):

			# this code create the tuple of items
			# items cannot be appended to tuples, so we need to change it in a loop
			self._item_group.append( (input_items[0][0], ) )
			for i in xrange(1, self._ninputs ):
				self._item_group[-1] = self._item_group[-1] + (input_items[i][0], ) 

			# Grouped all items ?
			if len(self._item_group) >= self._max_vlen and self._max_vlen > 0:
				self._enable = False

				if self._callback:
					self._callback()

		# One input is consumed at a time
		return 1 
