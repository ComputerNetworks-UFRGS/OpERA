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
