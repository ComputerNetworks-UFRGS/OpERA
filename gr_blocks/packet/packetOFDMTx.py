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

from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

from device       import UHDTxPktArch #pylint: disable=F0401

class PacketOFDMTx( UHDTxPktArch ):
    """
    Transmit packets modulated as OFDM.

    This module doesn`t has inputs, threrefor it cannot be connected
    as a sink.
    """

    _map = {
            'qam32':  {'bits_per_symbol': 5, 'symbols': 32 },
            'qam64':  {'bits_per_symbol': 6, 'symbols': 64 },
            'qam128': {'bits_per_symbol': 7, 'symbols': 128},
            'qam256': {'bits_per_symbol': 8, 'symbols': 256}
           }

    def __init__(self, name = "PacketOFDMTx",
            modulation = "qam64",
            input_signature = gr.io_signature(0, 0, 0),
            output_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex)):
        """
        CTOR
        @param name Instance name.
        @param input_signature Input signature.
        @param output_signature Output signature.
        """

        # sanity check
        if modulation not in PacketOFDMTx._map:
            raise AttributeError('Cannot use %s modulation in OFDM' % modulation)

        UHDTxPktArch.__init__(
                self,
                name =  name,
                input_signature  = input_signature,
                output_signature = output_signature
            )

        self._mod_data = PacketOFDMTx._map[ modulation ]


    def _build(self, input_signature, output_signature):
        """
        Implemention of base class abstract method.
        """
        return digital.ofdm_mod(
                    options=grc_blks2.options(
                        modulation="qam64",
                        fft_length=512,
                        occupied_tones=200,
                        cp_length=128,
                        log=None,
                        verbose=None,
                     ),
                msgq_limit=4,
                pad_for_usrp=False)


    def bits_per_symbol(self):
        """
        Implementation of base class abstract method.
        """
        return self._mod_data['bits_per_symbol']


    def symbols(self):
        """
        Implementation of base class abstract method.
        """
        return self._mod_data['symbols']
