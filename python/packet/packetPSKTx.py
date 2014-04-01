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

# ::TODO:: class and modules description

from gnuradio import gr, digital  #pylint: disable=F0401


# OpERA imports
from device import UHDTxPktArch  #pylint: disable=F0401


class PacketPSKTx(UHDTxPktArch):
    """
    Trasmit packets using PSK modulation.
    """

    def __init__(self, name="PacketGMSKTx",
                 input_signature=gr.io_signature(0, 0, 0),
                 output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex)
                 ):
        """
        CTOR
        @param name Instance name.
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """

        UHDTxPktArch.__init__(self,
                              name=name,
                              input_signature=gr.io_signature(0, 0, 0),
                              output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex)
                              )


    #::TODO:: pq tem os parametros input e output signature se nao usa eles??
    def _build(self, input_signature, output_signature):
        """
        Implementation of base class abstract method.
        @param input_signature The input signature.
        @param output_signature The output signature.
        """
        return digital.pkt.mod_pkts(modulator=digital.psk.psk_mod(constellation_points=8,
                                                                  mod_code="none",
                                                                  differential=False,
                                                                  samples_per_symbol=2,
                                                                  excess_bw=0.35,
                                                                  verbose=False,
                                                                  log=False),
                                    pad_for_usrp=False
                                    )

    def bits_per_symbol(self):
        """
        Implementation of base class abstract method.
        @return Number of bits per symbol.
        """
        return 3


    def symbols(self):
        """
        Implementation of base class abstract method.
        """
        return 2 ** self.bits_per_symbol()
