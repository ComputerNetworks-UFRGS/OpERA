#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Mon Mar 17 13:55:59 2014
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import channels
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import math
import numpy
import wx

class top_block(gr.top_block):

    def __init__(self, options):
        gr.top_block.__init__(self, name = "top_block")


        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.fft_len = fft_len = options.fft_length
        self.ebn0 = ebn0 = options.ebn0
        self.cp_len = cp_len = options.cp_length
        self.bits_per_symbol = bits_per_symbol = 8

        ##################################################
        # Blocks
        ##################################################
        self.digital_ofdm_mod_0 = grc_blks2.packet_mod_i(digital.ofdm_mod(
        		options=grc_blks2.options(
        			modulation="qam256",
        			fft_length=fft_len,
        			occupied_tones=40,
        			cp_length=cp_len,
        			pad_for_usrp=True,
        			log=None,
        			verbose=None,
        		),
        	),
        	payload_length=0,
        )
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*1, (fft_len+cp_len)*1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, "./%d_%d_%d_%d_%s.bin" % (fft_len, cp_len, options.ebn0, options.it, options.type), False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_random_source_x_0 = blocks.vector_source_i(map(int, numpy.random.randint(0, 2, 1000)), True)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 1.0 / math.sqrt(2.0 * bits_per_symbol * 10**(ebn0/10.0)), 0)

        self.channels_selective_fading_model_0 = channels.selective_fading_model( 8, 10.0/samp_rate, False, 4.0, 0, options.delay, options.mag, 128 )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.analog_random_source_x_0, 0), (self.digital_ofdm_mod_0, 0))
        self.connect((self.digital_ofdm_mod_0, 0), (self.channels_selective_fading_model_0, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.channels_selective_fading_model_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))


# QT sink close method reimplementation

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len

    def get_ebn0(self):
        return self.ebn0

    def set_ebn0(self, ebn0):
        self.ebn0 = ebn0
        self.analog_noise_source_x_0.set_amplitude(1.0 / math.sqrt(2.0 * self.bits_per_symbol * 10**(self.ebn0/10.0)))

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_bits_per_symbol(self):
        return self.bits_per_symbol

    def set_bits_per_symbol(self, bits_per_symbol):
        self.bits_per_symbol = bits_per_symbol
        self.analog_noise_source_x_0.set_amplitude(1.0 / math.sqrt(2.0 * self.bits_per_symbol * 10**(self.ebn0/10.0)))

if __name__ == '__main__':
    import ctypes
    import os

    if os.name == 'posix':
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser()
    parser.add_option("", "--ebn0", type="float", default=10.0)
    parser.add_option("", "--fft-length", type="int", default=128)
    parser.add_option("", "--type", type="choice", choices = ["urban", ])
    parser.add_option("", "--cp-length", type="int", default=9)
    parser.add_option("", "--it", type="int", default=0)
    (options, args) = parser.parse_args()

    if options.type == "urban":
        options.delay =  (0,    0.3, 3.5, 4.4,    9.5,  12.7)
        options.mag  =   (0,   -12,   -4,   -7,   -15,   -22)
    else:
        raise "ERROR"

    tb = top_block(options)


    import time
    tb.start()
    time.sleep(10)
    tb.stop()
    print "!!!!! Finishing file generation"
