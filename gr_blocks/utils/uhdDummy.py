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
import numpy as np

from gnuradio import gr     #pylint: disable=F0401
from gnuradio import blocks #pylint: disable=F0401
from gnuradio import digital #pylint: disable=F0401
from gnuradio import analog #pylint: disable=F0401
from grc_gnuradio import blks2 as grc_blks2 #pylint: disable=E0611


# OpERA imports
from device import UHDGenericArch  #pylint: disable=F0401


class UHDPrototype(object):

    def __init__(self, samp_rate = 200e3, output_controller = None):
        self._samp_rate = samp_rate
        self._center_freq = 0.0
        self._output_controller = output_controller

        self._active_freqs = []

    def set_active_freqs(self, freqs):
        self._active_freqs = freqs

    def get_center_freq(self):
        return self._center_freq
    def get_samp_rate(self):
        return self._samp_rate
    def get_gain(self):
        return 0.0
    def set_center_freq(self, val):
        self._center_freq = val

        # Multiplying the output by 0.0 is equal to "filtering" it.
        if self._output_controller:
            self._output_controller.set_k((1.0,) if val in self._active_freqs else (0.0,)) #pylint:disable=E1101

    def set_samp_rate(self, samp_rate):
        pass
    def set_gain(self, gain):
        pass
    def set_bandwidth(self, bw):
        pass


class UHDSourceDummy(UHDGenericArch, UHDPrototype):

    def __init__(self, name = "UHDSourceDummy", modulator = None):
        """
        """

        self._modulator = modulator
        self._multiply = blocks.multiply_const_vcc((0.0,) )

        UHDPrototype.__init__(self, output_controller = self._multiply)
        UHDGenericArch.__init__(
                self,
                name = name,
                input_signature  = gr.io_signature(0, 0, 0),
                output_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex)
            )


    def _build(self, input_signature, output_signature):
        """
        """
        self._source = blocks.vector_source_b(map(int, np.random.randint(0, 100, 1024)), True) #pylint: disable=E1101

        self._add_connections([self._source, self._modulator, blocks.throttle(gr.sizeof_gr_complex, 200e3), self._multiply]) #pylint: disable=E1101
        return self._multiply
