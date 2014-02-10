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
@package reception
"""

# gnuradio imports
from gnuradio     import gr, digital

# OpERA imports
from device     import UHDRxPktArch #pylint: disable=F0401

class PacketGMSKRx(UHDRxPktArch):
    """
    Received Packets modulated in OFDM.
    """

    def __init__(self, callback = None, name = "PacketGMSKRx",
            input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
            output_signature = gr.io_signature(0, 0, 0)):
        """
        CTOR
        @param callback Function called when a packet is received.
        @param callback Callback function.
        @param name Instance Name.
        @param input_signature  A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """

        UHDRxPktArch.__init__(
                self,
                callback = callback,
                name =  name,
                input_signature  = input_signature,
                output_signature = output_signature,
            )


    def _build(self, callback, input_signature, output_signature):
        """
        Implementation of UHDRxPktArch abstract method.
        """
        return  digital.pkt.demod_pkts(
                demodulator = digital.gmsk_demod(
                    samples_per_symbol = 2),
                callback = callback
            )
