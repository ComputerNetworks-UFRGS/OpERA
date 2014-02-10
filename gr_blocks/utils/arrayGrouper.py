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

## @package block_util

from gnuradio import gr

import numpy as np

## Group inputs in blocks of N elements
# The operation if this block is as follows:
# 1) Construct a instance with 'n_inputs' inputs and that will group 'group_vlen' elements.
# 2) When the FlowGraph is running, call group_in_n::enable_grouping to start grouping items.
# 3) Call group_in_n::items to recover items.
# 4) Call group_in_n::enable_grouping again.
#
# ::TODO:: Call a callback function  when group_vlen items are grouped.
class GroupInN(gr.sync_block):

    ## CTOR
    # @param max_items_group Number of elements to group before forwarding
    # @param callback   Function called when the data is grouped
    # @param n_inputs   number of inputs to group
    def __init__(self, max_items_group, callback, n_inputs=1):

        gr.sync_block.__init__(
                self,
                name = 'array_grouper',
                in_sig = [ np.float32 ] * n_inputs,
                out_sig = None
        )

        self._enable   = False
        self._max_vlen = max_items_group
        self._callback = callback
        self._ninputs  = n_inputs

        self._item_group = []

        self._callback = None

    ##
    #
    def set_callback(self, callback):
        self._callback = callback


    ## Enable/Disable grouping.
    #
    def set_enable(self, val):
        if val:
            self._item_group = []

        self._enable = val


    ##
    #
    def get_items(self):
        tmp = self._item_group

        self._item_group = []
        return tmp


    def work(self, input_items, output_items):
        if self._enable and len(self._item_group) < self._max_vlen:
            # this code create the tuple of items
            # items cannot be appended to tuples, so we need to change it in a loop
            if self._ninputs == 1:
                self._item_group.append( input_items[0][0] )
            else:
                self._item_group.append( (input_items[0][0],) )
                for i in xrange(1, self._ninputs ):
                    self._item_group[-1] = self._item_group[-1] + (input_items[i][0], ) 

            # Grouped all items ?
            if len(self._item_group) >= self._max_vlen:
                if self._callback:
                    self._callback(self, self._item_group)
                    self._item_group = []

        return len(input_items)

