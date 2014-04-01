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


class PacketGMSKTx(UHDTxPktArch):
    """
    Transmit packets using GMSK modulation.
    """

 ## ADICIONADOS PARAMETROS NOVOS NO INIT PARA A GERACAO DE SCRIPTS: FFT LENGHT, CP LENGTH, MODULATION
    def __init__(self, name="PacketGMSKTx",
                 input_signature=gr.io_signature(0, 0, 0),
                 output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                 modulator=digital.gmsk_mod(samples_per_symbol=2, bt=0.35)):
        """
        CTOR
        @param name Instance name.
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """

        self.modulator = modulator

        UHDTxPktArch.__init__(self,
                              name=name,
                              input_signature=gr.io_signature(0, 0, 0),
                              output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex)
                              )


    #::TODO:: checar o tipo retornado
    def _build(self, input_signature, output_signature):
        """
        Implementation of base class abstract method.
        @param input_signature
        @param output_signature
        @return
        """

        # Old values:
        # modulator = digital.gmsk_mod(samples_per_symbol=2, bt=0.35)
        # pad_for_usrp = False

        return digital.pkt.mod_pkts(modulator=self.modulator,
                                    pad_for_usrp=False
                                    )


    def bits_per_symbol(self):
        """
        Implementation of base class abstract method.
        @return Returns an int representing the number of bits per symbol.
        """
        return 2


    def symbols(self):
        """
        Implementation of base class abstract method.
        """
        return 2 ** self.bits_per_symbol()


    def get_modulator(self):
        return self.modulator