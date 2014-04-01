#!/usr/bin/env python
from gnuradio import gr, blocks
from gnuradio import uhd
from gnuradio import digital
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2

from threading import Thread
from optparse import OptionParser

import time
import os
import random
import numpy as np

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


class GNamespace():
    """

    """
    pass

globs = GNamespace()

globs.run = False
globs.canario = None
globs.cur_canario = None
globs.prev_canario = None

channel = 2.1e9

# ::TODO:: class and functions definitions
class Server(Thread):
    """

    """
    def __init__(self):
        """
        CTOR
        """
        Thread.__init__(self)
        self.my_srv = SimpleXMLRPCServer(addr=("143.54.83.30", 9001), logRequests=False,
                                         requestHandler=SimpleXMLRPCRequestHandler)

    def run(self):
        """

        """
        print "##### Starting RPC Server"
        self.my_srv.serve_forever()


def build_radio():
    """

    """

    source = blocks.vector_source_b(map(int, np.random.randint(0, 100, 1000)), True)
    uhd_sink = uhd.usrp_sink(device_addr="addr=10.1.1.146", stream_args=uhd.stream_args('fc32'))
    uhd_sink.set_antenna("TX/RX", 0)

    #modulator  = grc_blks2.packet_mod_f(
    #        digital.ofdm_mod(
    #            options = grc_blks2.options(
    #                modulation = "bpsk",
    #                fft_length = 512,
    #                occupied_tones = 200,
    #                cp_length = 128,
    #                pad_for_usrp = True,
    #                log = None,
    #                verbose = None
    #            )
    #        )
    #    )

    modulator = digital.psk.psk_mod(constellation_points=8,
                                    mod_code="none",
                                    differential=False,
                                    samples_per_symbol=2,
                                    excess_bw=0.35,
                                    verbose=False,
                                    log=False)

    tb = gr.top_block()

    tb.connect(source, modulator)
    tb.connect(modulator, uhd_sink)
    
    return tb, uhd_sink


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--wait-for-run", type="int", default=0,
                      help="")
    parser.add_option("", "--poisson-avg", type="float", default=10.0,
                      help="Poisson average and variance")
    (options, args) = parser.parse_args()

    if options.wait_for_run > 0:
        def command(param):
            """
            @param param
            """
            who = param[0]
            cmd = param[1]
            val = param[2]

            print "cmd = " + str(cmd) + "- val = " + str(val)

            if cmd == 'run':
                globs.run = val
                if val == True:
                    globs.prev_canario = globs.canario
                    globs.canario = xmlrpclib.ServerProxy("http://143.54.83.30:9000")
                    globs.cur_canario = True
                else:
                    globs.cur_canario = None
                    globs.canario = None
                    globs.canario_prev = None
            else:
                print "##### command not found"
                os._exit(1)
            print "----- Returning"
            return 1

        my_server = Server()
        my_server.my_srv.register_function(command, "command")
        my_server.start()

    else:
        globs.run = True
        globs.prev_canario = None
        globs.canario = None

    tb, uhd = build_radio()
    tb.start()
    uhd.set_gain(20)

    interference_time = 1.0
    uhd.set_samp_rate(200e3)

    freq = channel
    while True:
        if globs.prev_canario == None and globs.cur_canario:
            while globs.run == False:
                time.sleep(1)

        if freq == channel:
            freq = channel - 1.0e9
            freq = channel
        else:
            freq = channel

        interference_time = random.expovariate(1.0/options.poisson_avg)

        if globs.cur_canario and freq == channel:
            globs.canario.command([666, "interfering_channel",  (0, interference_time)])

        uhd.set_center_freq(freq)
        print 'Interfering in freq: %d' % freq
        time.sleep(interference_time)

    tb.stop()
    tb.wait()
    os._exit(1)
