## @package block_utils

from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

from device       import UHDTxPktArch


class PacketOFDMRx(gr.hier_block2):

	## CTOR
	# @param callback
	def __init__(self, callback):

		gr.hier_block2.__init__(
				self,
				name =  'PacketOFDMRx',
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(0, 0, 0),
			)

		self._demod = digital.ofdm_demod(
				options=grc_blks2.options(
					modulation="qam64",
					fft_length=512,
					occupied_tones=200,
					cp_length=128,
					snr=30,
					log=None,
					verbose=None,
					),
				callback=callback
			)

		#             #
		# Connections #
		#             #
		self.connect(self, self._demod)
