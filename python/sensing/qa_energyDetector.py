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

## @package ssf

# ::TODO:: Discover how to include patches externally
import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, fft, blocks, digital

from OpERAFlow import OpERAFlow
from energy import EnergyDetectorC, EnergySSArch
from device import RadioDevice
from sensing import EnergyDecision
from gr_blocks.utils import SNREstimator, UHDSourceDummy

import numpy as np


class QaEnergyDetector(gr_unittest.TestCase):
    """
    QA related to EnergyDetector class.
    """

    def setUp(self):
        """
        Set globals for all tests. Called before a test is started.
        """
        self.tb = OpERAFlow(name='top')

    def tear_down(self):
        """
        Destroy globals for all tests. Called right after a test if finished.
        """
        self.tb = None

    def test_001(self):
        """
        Test the energy of a simple sequence (1, 2, -1, -2).
        """
        # input and expected results
        src_data = (1, 1, 1, 1)
        expected_result = 1

        # blocks
        fft_size = len(src_data)
        mavg_size = 1

        src = blocks.vector_source_c(data=src_data)
        dst = blocks.probe_signal_f()
        ed = EnergySSArch(fft_size, mavg_size, EnergyDecision(1))
        #radio_device = RadioDevice(the_source = src, the_sink = dst)

        radio_device = RadioDevice()
        radio_device.add_arch(source=src, arch=ed, sink=dst, uhd_device=None, name='ed')
        ################ FIM NOVO RADIO DEVICE

        ## flowgraph
        ##self.tb.add_arch(ed, radio_device, 'ed')
        self.tb.add_radio(radio_device)
        self.tb.run()

        result_data = dst.level()
        self.assertEqual(expected_result, result_data)

    def test_002(self):
        """
        Test a sequence with float number (0.1, 0.1, 0.1, 0.1).
        """
        # input and expected results
        src_data = (0.1, 0.1, 0.1, 0.1)
        expected_result = 0

        # blocks
        fft_size = len(src_data)
        mavg_size = 1

        src = blocks.vector_source_c(data=src_data)
        ed = EnergyDetectorC(fft_size, mavg_size, EnergyDecision(1))

        dst = blocks.probe_signal_f()

        # flowgraph
        self.tb.connect(src, ed, dst)
        self.tb.run()

        result_data = dst.level()
        self.assertEqual(expected_result, result_data)

    def test_003(self):
        """
        Test EDTopBlock with the input (1, 1, 1, 1, 1, 1, 1, 1).
        """
        arr = (1, 1, 1, 1, 1, 1, 1, 1)
        expected_out = 8

        ed = EnergySSArch(fft_size=len(arr),
                          mavg_size=8,
                          algorithm=EnergyDecision(expected_out - 1)
                          )

        src = blocks.vector_source_c(data=arr, vlen=1)
        sink = blocks.probe_signal_f()

        device = RadioDevice()
        device.add_arch(source=src, arch=ed, sink=sink, uhd_device=None, name='ed')

        self.tb.add_radio(device, 'ed')
        self.tb.run()

        ##self.assertEqual(1 , device.sink.level()) # didn't work
        self.assertEqual(1, device.output()[0])

    def test_004(self):
        """
        Test EDTopBlock with a simple input (1, 2, 3, 4).
        """
        arr = (1.0, 2.0, 3.0, 4.0)
        expected_result = 30  # before expected result was 2536

        ed = EnergySSArch(fft_size=len(arr),
                          mavg_size=1,
                          algorithm=EnergyDecision(expected_result + 1)  # (expected_out + 1)
                          )

        src = blocks.vector_source_c(data=arr, vlen=1)
        sink = blocks.probe_signal_f()

        device = RadioDevice()
        device.add_arch(source=src, arch=ed, sink=sink, uhd_device=None, name='ed')

        self.tb.add_radio(device, 'ed')

        self.tb.start()
        self.tb.wait()

        ###self.assertEqual(expected_result , device.sink.output()[1])
        self.assertEqual(expected_result, device.ed.output()[1])  # uses 'name' parameter of the add_arch method


if __name__ == '__main__':
    gr_unittest.main()
