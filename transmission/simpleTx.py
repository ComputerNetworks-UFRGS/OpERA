## @package block_utils

from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

from device       import UHDTxPktArch

class SimpleTx(gr.hier_block2):

	## CTOR
	# A simple TX without source/sink
	def __init__(self):
		gr.hier_block2.__init__(
				self,
				name = 'simple_tx',
				input_signature = gr.io_signature(1, 1, gr.sizeof_float),
				output_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex)
			)

		tx_mod = grc_blks2.packet_mod_f(
				digital.ofdm_mod(
					options=grc_blks2.options(
						modulation="bpsk",
						fft_length=512,
						occupied_tones=200,
						cp_length=128,
						pad_for_usrp=True,
						log=None,
						verbose=None,
						),
					),
				payload_length=0,
			)
		self.connect(self, tx_mod, self)


