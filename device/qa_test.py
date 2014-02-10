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

## @package device

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)

###from gnuradio import blocks
from time import sleep
import unittest
from gnuradio import gr, gr_unittest, fft, blocks

# Project imports
from radioDevice import RadioDevice
#from uhdAbstractArch import UHDAbstractArch
#from uhdRxArch import UHDRxARch
#from OpERAFlow import OpERAFlow

from reception.packet import PacketGMSKRx

## Test UHD device
class QaUHD(unittest.TestCase):

    ## Test RadioDevice instantiation
    ## @TODO Create a dummy UHD device
    def test_001(self):
        source = blocks.vector_source_c( [1] * 8 )
        sync = blocks.probe_signal_f()

        dev = RadioDevice(source, sync)

    def test_uhd_001(self):
        rx_uhd = PacketGMSKRx(10)

        source = blocks.vector_source_c( [1] * 8 )
        sink = blocks.probe_signal_f()

        dev = RadioDevice(source, sink)

        
        rx_uhd.set_radio_device(dev)
        my_radio = rx_uhd.radio
        print my_radio

        samp_rate_radio = rx_uhd.radio._get_samp_rate
        print samp_rate_radio

        str_radio = rx_uhd.radio.my_str
        print str_radio
        
if __name__ == '__main__':
    unittest.main()
