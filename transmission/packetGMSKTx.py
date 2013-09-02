## @package block_utils

from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

from device       import UHDTxPktArch

###############################################################################
#                                                                             #
#                             GMSK TX/RX                                      #
#                                                                             #
###############################################################################

##
#
class PacketGMSKTx( UHDTxPktArch ):
	def __init__(self):

		UHDTxPktArch.__init__(
				self,
				name =  'PacketGMSKTx',
				input_signature  = gr.io_signature(0, 0, 0),
				output_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex)
			)


	def _build(self):
		return digital.pkt.mod_pkts(
				modulator = digital.gmsk_mod(
					samples_per_symbol = 2,
					bt = 0.35),
				pad_for_usrp = False
			)

##
#
