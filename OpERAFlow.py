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

"""
@package algorithm
"""

from gnuradio import gr #pylint: disable=F0401

# OpERA imports
from device import UHDBase

class OpERAFlow(gr.top_block):
    """
    """

    def __init__(self, name):
        """
        CTOR
        @param name
        """
        object.__setattr__(self, '_dict_of_archs', {})
        gr.top_block.__init__(self, name = name)


    def start(self, max_noutput_items = 1024):
        """
        Override gr.top_block method.
        @param max_noutput_items From gnuradio::top_block defaults.
        """
        self._connect_all_pending()

        gr.top_block.start(self, max_noutput_items)


    def add_radio(self, radio, name):
        """
        @param radio
        @param name
        """
        self._dict_of_archs[name] = radio #pylint: disable=E1101
        radio.set_top_block( self )

        setattr(self, name, radio)


    def _connect_all_pending(self):
        """
        Perform all conections.
        """
        # For each radio, perform its connections
        for radio in  self._dict_of_archs.values(): #pylint: disable=E1101
            radio.connect()
