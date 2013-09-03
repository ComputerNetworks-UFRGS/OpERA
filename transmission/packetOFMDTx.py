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

from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

from device       import UHDTxPktArch


###############################################################################
#                                                                             #
#                             OFDM TX/RX                                      #
#                                                                             #
###############################################################################

##
#
class PacketOFDMTx( UHDTxPktArch ):
	def __init__(self):
		UHDTxPktArch.__init__(
				self,
				name =  'PacketOFDMTx',
				input_signature  = gr.io_signature(0, 0, 0),
				output_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex)
			)

	def _build(self):
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

##
#
