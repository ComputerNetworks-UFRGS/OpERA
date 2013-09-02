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
