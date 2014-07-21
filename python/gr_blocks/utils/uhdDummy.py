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

from gnuradio import gr       #pylint: disable=F0401
from gnuradio import blocks   #pylint: disable=F0401
from gnuradio import digital  #pylint: disable=F0401
from gnuradio import analog   #pylint: disable=F0401
from grc_gnuradio import blks2 as grc_blks2 #pylint: disable=E0611

import time

# OpERA imports
from device import UHDGenericArch  #pylint: disable=F0401


#::TODO:: descricao de classe e seus metodos
class UHDPrototype(object):
    """

    """

    def __init__(self,
                 samp_rate=200e3,
                 output_controller=None,
		 t_input=None):
        """
        CTOR
        @param samp_rate
        @param output_controller
        """
        self._samp_rate = samp_rate
        self._center_freq = 0.0
        self._output_controller = output_controller

        self._active_freqs = []

    def set_active_freqs(self, freqs):
        """
        @param freqs
        """
        self._active_freqs = freqs

    def get_center_freq(self):
        """
        @return
        """
        return self._center_freq

    def get_samp_rate(self):
        """
        @return
        """
        return self._samp_rate

    def get_gain(self):
        """
        @return
        """
        return 0.0

    def set_center_freq(self, val):
        """
        @param val
        """
        self._center_freq = val

        # Multiplying the output by 0.0 is equal to "filtering" it.
        if self._output_controller:
            self._output_controller.set_k((1.0,) if val in self._active_freqs else (0.0,))  #pylint:disable=E1101
	else:
	   print "WARNING: cannot change central frequency"

    def set_samp_rate(self, samp_rate):
        """
        @param samp_rate
        """
        pass

    def set_gain(self, gain):
        """
        @param gain
        """
        pass

    def set_bandwidth(self, bw):
        """
        @param bw
        """
        pass


class multiply(gr.sync_block):
    """

    """
    def __init__(self, f):

        gr.sync_block.__init__(self,
                               name="CycloDetector",
                               in_sig=[np.complex64],  #pylint: disable=E1101
                               out_sig=[np.complex64],  #pylint: disable=E1101
                               )

	self._f = f
	self._status = self._f()

	s, t = self._f()
	self._status, self._t_change = s, t + time.time()

    def change_status(self):
        if time.time() > self._t_change:	
		s, t = self._f()
		self._status, self._t_change = s, t + time.time()
################################################################################

    def work(self, input_items, output_items):
        """
        @param input_items
        @param output_items
        """
	self.change_status()

	if self._status:
		output_items[0][:] = input_items[0][:]
	else:
		output_items[0][:] = input_items[0][:] * 0

        return len(output_items[0])


class UHDSourceDummy(UHDGenericArch, UHDPrototype):
    """
    Dummy source uhd device.

    """

    def __init__(self,
                 name="UHDSourceDummy",
                 modulator=None,
		 f=None):
        """
        @param name Instance name.
        @param modulator
        """

        self._modulator = modulator

	self._multiply = blocks.multiply_const_vcc((0.0, ))

        UHDPrototype.__init__(self, output_controller=self._multiply)
        UHDGenericArch.__init__(self,
                                name=name,
                                input_signature=gr.io_signature(0, 0, 0),
                                output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex)
	)

    #::TODO:: pq parametros input e output signature nao sao usados???
    def _build(self, input_signature, output_signature):
        """
        @param input_signature The input signature.
        @param output_signature The output signature.
        """
        self._source = blocks.vector_source_b(map(int, np.random.randint(0, 100, 1024)), True)  #pylint: disable=E1101

        self._add_connections([self._source, self._modulator, blocks.throttle(gr.sizeof_gr_complex, 100e6), self._multiply])   #pylint: disable=E1101

        return self._multiply


class UHDSinkDummy(UHDGenericArch, UHDPrototype):
    """
    Dummy sink uhd device.
    """

    def __init__(self,
                 name="UHDSinkDummy",
                 modulator=None):
        """
        @param name Instance name.
        @param modulator
        """

        UHDPrototype.__init__(self, output_controller=None, t_input=None)
        UHDGenericArch.__init__(self,
                name=name,
                input_signature=gr.io_signature(0, 0, 0),
                output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex)
        )


    #::TODO:: pq parametros input e output signature nao sao usados???
    def _build(self, input_signature, output_signature):
        """
        @param input_signature The input signature.
        @param output_signature The output signature.
        """
        self._sink = blocks.null_sink(gr.sizeof_gr_complex)   #pylint: disable=E1101
        return self._sink
