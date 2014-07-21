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

import math

from gnuradio import blocks  #pylint: disable=F0401
from gnuradio import analog, digital #pylint: disable=F0401

from device import UHDBaseArch  #pylint: disable = F0401
from device import UHDBase      #pylint: disable = F0401

from abstractChannel import AbstractChannel  #pylint: disable=F0401


class AWGNChannel(AbstractChannel):
    """
    Class that applies an Additive White Gaussian Noise over an input signal.

    Design pattern: DECORATOR
    """
    # Architecture (this block comprises the Noise Adder and Mod):
    #  -------        --------
    # | Noise |*--->*| Adder  |*>---> (modified signal)
    #  -------  --->*|        |
    #           |     --------
    #  -----    |
    # | Mod |*>-- (original signal)
    #  -----
    def __init__(self, name="AWGNChannel", bits_per_symbol = 2, component=None, ebn0=10):
        """
        CTOR
        @param name Block name.
        @param component The decorator component.
        @param ebn0
        """

        # ::TRICKY:: Initialization must be AFTER declaring _ch_effect.
        AbstractChannel.__init__(self, name=name, component=component)

	self.bits_per_symbol = bits_per_symbol
        self.set_ebn0(ebn0)


    def set_ebn0(self, ebn0):
        """
        Set the ebn0 value used
        @param ebn0
        """
	ebn0 = float(ebn0)
        # Formula from file ber_simulation.grc in usr/share/gnuradio/examples/digital/demod/
        self._ch_effect.set_amplitude(1.0 / math.sqrt(2.0 * self.bits_per_symbol * 10**(ebn0/10.0)))


    def _build(self, input_signature, output_signature):
        """
        Build the internal structure of this hierarchical block.
        @param input_signature
        @param output_signature
        """

        self._adder = blocks.add_vcc(1)
        self._ch_effect = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0)

        self._add_connections([self._component, (self._adder, 0)])  #pylint: disable = E1101
        self._add_connections([self._ch_effect, (self._adder, 1)])  #pylint: disable = E1101

        # We return the adder, i.e., the original signal is connected in port 0.
        return self._adder
