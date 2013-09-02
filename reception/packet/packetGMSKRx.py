## @package block_utils

from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

from device       import UHDTxPktArch


class PacketGMSKRx(gr.hier_block2):

	## CTOR
	# @param callback
	def __init__(self, callback):

		gr.hier_block2.__init__(
				self,
				name =  'PacketGMSKRx',
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(0, 0, 0),
			)

		self._demod = digital.pkt.demod_pkts(
				demodulator = digital.gmsk_demod(
					samples_per_symbol = 2),
				callback = callback
			)

		#             #
		# Connections #
		#             #
		self.connect(self, self._demod)



