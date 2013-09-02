#!/usr/bin/env python

from gnuradio            import gr, digital, uhd
from gnuradio			 import blocks
from grc_gnuradio        import blks2 as grc_blks2
from gnuradio.eng_option import eng_option
from optparse            import OptionParser

import numpy as np


## Builds a top block.
def build_tx_top_block(options):

	# TX PATH
	tx_src = blocks.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True)
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
	device =  uhd.usrp_sink( device_addr = options.args, stream_args= uhd.stream_args(cpu_format='fc32'))
	device.set_samp_rate( options.samp_rate )


	# TOP BLOCK
	tb = gr.top_block(name = 'our top block')
	tb.connect( tx_src, tx_mod, device );

	return (tb, device)


##
def main(options):

	tb = build_tx_top_block( options )

	freq = options.freq
	while freq > -1: 
			tb[1].set_center_freq( freq )

			tb[0].start()
			raw_input('')

			tb[0].stop()
			tb[0].wait()

			new_freq =  float(raw_input( "Digite uma frequencia para ocupar ou [-1] para sair:" ))
			freq = new_freq or freq

	tb[0].stop()
	tb[0].wait()


if __name__ == '__main__':
	parser=OptionParser(option_class=eng_option)
	parser.add_option("-a", "--args", type="string", default="''",
			help="UHD device address args [default=%default]")
	parser.add_option("-A", "--antenna", type="string", default='TX/RX',
			help="select Rx Antenna where appropriate")
	parser.add_option("-f", "--freq", type="eng_float", default=205.25e6,
			help="set frequency to FREQ", metavar="FREQ")
	parser.add_option("-g", "--gain", type="eng_float", default=None,
			help="set gain in dB (default is midpoint)")
	parser.add_option("", "--samp-rate", type="int", default=195312,
			help="set device sample rate")

	(options, args) = parser.parse_args()

	main( options )
