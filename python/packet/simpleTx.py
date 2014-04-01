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

## @package block_utils

from gnuradio import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2


# OpERA imports
from device import UHDTxPktArch  #pylint: disable=F0401


class SimpleTx(UHDTxPktArch):
    """
    A simple TX
    """

    def __init__(self):
        """
        CTOR
        """
        UHDTxPktArch.__init__(self,
                              name='simple_tx',
                              input_signature=gr.io_signature(1, 1, gr.sizeof_float),
                              output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex)
                              )

    ##::TODO:: descrever funcao
    def _build(self, input_signature, output_signature):
        """
        @param input_signature The input signature.
        @param output_signature The output signature.
        """
        return grc_blks2.packet_mod_f(digital.ofdm_mod(options=grc_blks2.options(modulation="bpsk",
                                                                                 fft_length=512,
                                                                                 occupied_tones=200,
                                                                                 cp_length=128,
                                                                                 pad_for_usrp=True,
                                                                                 log=None,
                                                                                 verbose=None)),
                                      payload_length=0,
                                      )


    def bits_per_symbol(self):
        """
        Implementation of base class abstract method.
        @return The number of bits per symbol.
        """
        return 1


    def symbols(self):
        """
        Implementation of base class abstract method.
        """
        return 2
