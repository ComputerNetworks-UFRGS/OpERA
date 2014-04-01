#!/usr/bin/env python

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


import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, path)

from gnuradio import gr
from gnuradio import blocks
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from struct import *
from threading import Thread
import time
import random

import numpy as np

#from device.uhd import *
from OpERAFlow import OpERAFlow
from device import *
from sensing import EnergyDecision, EnergySSArch
from packet import PacketGMSKRx, PacketGMSKTx, SimpleTx
from utils import Channel, ChannelModeler, Logger
import qnoise

#::TODO:: descricao da funcao e de seus parametros
def dump_qlearner(it, ss_result, noise_w):
    """
    @param it
    @param ss_result
    @param noise_w
    """

    direc = "./chimas_tx/gain_1_noise_weight_%0.2f" % (noise_w)
    if not os.path.exists(direc):
        os.makedirs(direc)

    fname = "%s//ss_result_%d.txt" % (direc, it)

    tmp = []
    for c, d in ss_result.items():
        tmp.append([d[2], c, d[0], d[1]])
    tmp.sort()

    with open(fname, 'w') as fd:
        fd.write("ss_channel sinr decision qvalue\n")
        for channel_data in reversed(tmp):

            qvalue = channel_data[0]
            channel = channel_data[1]
            sinr = channel_data[2]
            decision = channel_data[3]

            fd.write("{0} {1} {2} {3}\n".format(channel, sinr, decision, qvalue))


def build_us_block(options):
    """
    Builds the US top block.
    The RX path performs the ED sensing.
    The TX path transmits a BER.
    @param options
    """
    # TOP BLOCK
    tb = OpERAFlow(name='US')

    # RX PATH
    uhd_source = UHDSource(device_addr=options.args)
    uhd_source.samp_rate = 195512
    #::TODO:: nova versao do radiodevice --> atualizar
    the_source = uhd_source
    the_sink = blocks.probe_signal_f()
    ###device_source = RadioDevice(the_source = uhd_source, the_sink = blocks.probe_signal_f() )
    device_source = RadioDevice()
    device_source.add_arch(source=the_source, arch=None, sink=the_sink, uhd_device=None, name="source")

    # ::TODO:: energyssarch NAO tem o parametro device!!!
    rx_path = EnergySSArch(device=device_source,
                           fft_size=512,
                           mavg_size=5,
                           algorithm=None)
            #algorithm = EnergyDecision( th = 0.00000001 ))

    ## tb.add_arch( abstract_arch = rx_path, radio_device = device_source, name_of_arch = 'rx')
    tb.add_radio(device_source, "rx")

    # TX PATH
    tx_path = PacketGMSKTx()

    uhd_sink = UHDSink(device_addr=options.args)
    uhd_sink.samp_rate = options.samp_rate

    the_source = None
    the_sink = uhd_sink
    uhd_device = uhd_sink
    radio_sink = RadioDevice()
    radio_sink.add_arch(source=the_source, arch=None, sink=the_sink, uhd_device=uhd_device, name="sink")
    ####tb.add_arch( tx_path, radio_sink, 'tx', connection_type = OpERAFlow.CONN_SINK)
    tb.add_radio(radio_sink, "sink")

    return tb


def build_up_block(options, channel_list):
    """
    Builds the UP top block.
    The RX path performs the ED sensing AND BER reception
    @param options
    @param channel_list
    """
    # TOP BLOCK
    tb = OpERAFlow(name='UP')

    def rx_callback(ok, payload):
        """
        @param ok
        @param payload
        """
        global t_rcv, t_cor
        global g_namespace

        t_rcv += 1
        t_cor += 1 if ok else 0

        g_namespace.pkt_r += 1
        #print 'r: ', g_namespace.pkt_r


    def dist_callback(channel, status):
        """
        @param channel
        @param status
        """
        if status:
            return 1.0
        else:
            return channel.channel*0.25

    # RX PATH
    uhd_source = UHDSource(device_addr=options.args)
    uhd_source.samp_rate = options.samp_rate

    #::TODO:: atualizar para novo radiodevice
    the_source = uhd_source
    the_sink = None

    radio_source = RadioDevice()
    radio_source.add_arch(source=the_source, arch=None, sink=the_sink, uhd_device=None, name="source")

    rx_path = PacketGMSKRx(rx_callback)
    ##tb.add_arch( rx_path, radio_source, 'rx' )
    tb.add_radio(radio_source, 'rx')

    # TX PATH
    uhd_sink = UHDSink(device_addr=options.args)
    uhd_sink.samp_rate = 195512
    uhd_sink.gain = 28

    the_source = blocks.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True)
    the_sink = uhd_sink
    uhd_device = uhd_sink

    radio_sink = RadioDevice()
    radio_sink.add_arch(source=the_source, arch=None, sink=the_sink, uhd_device=uhd_device, name="source")

    radio_proxy = ChannelModeler(device=radio_sink,
                                 channel_list=channel_list,
                                 dist_callback=dist_callback)
    tx_path = SimpleTx()

    ###tb.add_arch( tx_path, radio_proxy, 'tx')
    tb.add_radio(radio_proxy, 'tx')

    return tb


def transmitter_loop(tb, channel_list, channel, options):
    """
    US LOOP
    @param tb
    @param channel_list
    @param channel
    @param options
    """

    # Q-Noise+ Parameters
    lookback = 3
    beta = 0.1
    eps = 0.1

    history_weight = [0.2, 0.35, 0.45]
    noise_weight = 0.8
    alpha = 0.2  # alpha + noise+weith = 1
    epochs = 100
    #Q-Noise+
    learner = qnoise.Learner(channel_list, lookback, alpha, beta, eps, history_weight, noise_weight)

    # Connect to slave device
    import xmlrpclib
    proxy = xmlrpclib.ServerProxy("http://%s:8000/" % options.slave_addr)
    start_t = time.time()
    proxy.client_started()
    proxy.set_channel(channel)

    Logger.register('transmitter', ['channel', 'status', 'pkt'])


    class TNamespace():
        """

        """
        pass

    # Sensing -> TX loop
    t_namespace = TNamespace()
    t_namespace.pkt_s = 0
    t_namespace.status = 0
    t_namespace.iteration = 0

    
    t_namespace.ss_result = {}
    for ch in channel_list:
        t_namespace.ss_result[ch.channel] = [0, 0, 0]

    ch_qvalue = 0
    while time.time() < (start_t + options.duration):
        can_transmit = True

        t_namespace.pkt_r = t_namespace.pkt_s = 0

        # Sense
        print '### START SENSING CHANNEL'
        t_namespace.status = tb.rx.sense_channel(channel_list[channel], options.sensing_duration)

        # Update
        #print t_namespace.status
        if t_namespace.status > 0.000005:  # GMSK threahold
        #if t_namespace.status > 0.000000005 :
            print str(channel_list[channel]) + ' is occupied'

            t_now = time.clock()

            can_transmit = True

            # Change channel
            #proxy.set_channel( channel )

        # Transmit
        if can_transmit:
            payload = 0
            if options.pkt_size > 1:
                bytelist = [1] * (options.pkt_size/4)
                payload = pack('%sH' % len(bytelist), *bytelist)
            else:
                bytelist = ['a', ]
                payload = pack('%sc' % 1, *bytelist)

            # thread sending packets
            def send_thread():
                t_namespace.pkt_s = 0
                #while t_namespace.pkt_sending:
                while t_namespace.pkt_s < 200:
                    tb.tx.send_pkt(payload)
                    t_namespace.pkt_s += 1
                    #print 't: ', t_namespace.pkt_s
                    time.sleep(0.03)
                #t_namespace.count += 1

            # init thread
            th = Thread(target=send_thread)
            proxy.start_rcv()
            t_namespace.pkt_sending = True
            th.start()

            # wait for options.sending_duration 
            #time.sleep( options.sending_duration )

            # stop sending
            t_namespace.pkt_sending = False
            th.join()

            t_namespace.pkt_r = proxy.get_rcv()

            print 'pkt_s = ', t_namespace.pkt_s
            print 'pkt_r = ', t_namespace.pkt_r

        ch_qvalue = learner.evaluate(channel_list[channel].channel, t_namespace.pkt_s, t_namespace.pkt_r,
                                     t_namespace.status)

        t_namespace.ss_result[channel+1] = [t_namespace.status, 0 if can_transmit else 1, ch_qvalue]
        channel = learner.choose_next_channel(channel_list[channel].channel) - 1   # -1 cause we use the index in the array.
        print "Using channel  ", channel_list[channel]
        proxy.set_channel(channel)
        tb.tx.radio.center_freq = channel_list[channel]

        Logger.append('transmitter', 'channel',  channel)
        Logger.append('transmitter', 'status',   t_namespace.status)
        Logger.append('transmitter', 'pkt',      t_namespace.pkt_s)

        dump_qlearner(t_namespace.iteration, t_namespace.ss_result, noise_weight)
        t_namespace.iteration += 1

    proxy.close_app()


def receiver_loop(tb, channel_list, channel, options):
    """
    UP LOOP
    @param tb
    @param channel_list
    @param channel
    @param options
    """

    import xmlrpclib
    from SimpleXMLRPCServer import SimpleXMLRPCServer

    class MyNamespace:
        """

        """
        pass

    global g_namespace
    g_namespace = MyNamespace()
    g_namespace.tb = tb
    g_namespace.options = options
    g_namespace.server_run = True

    class StoppableXMLRPCServer(SimpleXMLRPCServer):
        """
        Override of TIME_WAIT
        """
        allow_reuse_address = True

        def __init__(self, options):
            """
            @param options
            """
            SimpleXMLRPCServer.__init__(self, options)
            self.stop = False

        def serve_forever(self):
            """

            """
            while not self.stop:
                self.handle_request()
            print 'exiting server'

        def shutdown(self):
            """

            """
            self.stop = True
            return 0

    server = StoppableXMLRPCServer((options.slave_addr, 8000))
    g_namespace.th = Thread(target=server.serve_forever)

    # Flag that indicates when the execution must stop.
    g_namespace.run = False
    g_namespace.interferer_channel = 0

    # RPC para troca do canal
    #
    def set_channel(channel):
        """
        RPC for changing the channel.
        @param channel
        """
        print "Received command to handoff to channel  ", channel_list[channel]
        g_namespace.tb.rx.radio.center_freq = channel_list[channel]
        g_namespace.tb.tx.radio.center_freq = channel_list[channel]

        g_namespace.interferer_channel = channel
        return 1

    def close_app():
        """
        Closes the app.
        """
        print "Received command to close"
        g_namespace.run = False
        return 1

    def client_started():
        """
        Notifies that the execution has started.
        """
        g_namespace.run = True
        return 1

    def start_rcv():
        """

        """
        g_namespace.pkt_r = 0
        return 1
 
    def get_rcv():
        """

        """
        return g_namespace.pkt_r

    Logger.register('receiver', ['channel', 'pkt', 'start_time'])
    Logger.set('receiver', 'start_time', time.time())

    # Registra funcoes no servidor XML e inicia thread do servidor
    # Registers functions in the XML server and starts the server thread.
    server.register_function(set_channel, 'set_channel')
    server.register_function(close_app, 'close_app')
    server.register_function(client_started, 'client_started')
    server.register_function(start_rcv, 'start_rcv')
    server.register_function(get_rcv, 'get_rcv')

    g_namespace.th.start()
    print "Receiver listening for commands in port 8000"
    print "\t... Waiting for client_started call"

    while g_namespace.run == False:
        1
    print "\t...client connected"

    global t_rcv, t_cor

    channel = 0

    # Enquanto nao recebeu a notificacao de parada, continua a execucao
    # While the stop notification is not received, continues the execution.
    while g_namespace.run:
        #print " ... r: ", t_rcv, ", c: ", t_cor
        time.sleep(1)
        Logger.append('receiver', 'channel', channel, time.time() )

    Logger.append('receiver', 'pkt', t_rcv)
    

    print "Shuting down Server"
    server.shutdown()
    print "\t ... Server exited"


##
def main( options ):
    """
    Main function.
    """
    channel_list = [Channel(ch=1,  freq=199.25e6, bw=200e3),   # L # record 21
                    Channel(ch=2,  freq=259.25e6, bw=200e3),   # L #
                    Channel(ch=3,  freq=427.25e6, bw=200e3),   # L sbt hd  28
                    Channel(ch=4,  freq=719.27e6, bw=200e3),   # L tv cachoeirinha 44 STRONG SIGNAL
                    Channel(ch=5,  freq=671.25e6, bw=200e3),   # L tv cultura do vale 53
                    Channel(ch=6,  freq=991.25e6, bw=200e3),   # L tv urbanaa canal 55 VERY STRONG SIGNAL
                    Channel(ch=7, freq=230.25e6, bw=200e3),    # L
                    Channel(ch=8,  freq=581.25e6, bw=200e3),   # L rbs tv 12
                    Channel(ch=9,  freq=325.25e6, bw=200e3),   # L band hdtv 32 VERY STRONG SIGNAL
                    Channel(ch=10,  freq=291.25e6, bw=200e3),  # L ultra tv 48 STRONG SIGNAL
                    Channel(ch=11,  freq=337.25e6, bw=200e3)]  # L rbs tv hd 34 VERY STRONG SIGNAL

    tb = build_up_block(options, channel_list) if options.interferer else build_us_block(options)

    tb.start()
    time.sleep(3)

    channel = 0

    if not options.interferer:
        # initial frequencies
        tb.rx.radio.center_freq = channel_list[channel]
        tb.tx.radio.center_freq = channel_list[channel]

        transmitter_loop(tb, channel_list, channel, options)
    else:
        global t_rcv
        global t_cor
        t_rcv = 0
        t_cor = 0

        tb.rx.radio.center_freq = channel_list[channel]
        tb.tx.radio.center_freq = channel_list[channel]

        receiver_loop(tb, channel_list, channel, options)

    time.sleep(1)
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    gr.enable_realtime_scheduling()

    parser=OptionParser(option_class=eng_option)
    parser.add_option("-a", "--args", type="string", default="''",
            help="UHD device address args [default=%default]")
    parser.add_option("-A", "--antenna", type="string", default='TX/RX',
            help="select Rx Antenna where appropriate")
    parser.add_option("-g", "--gain", type="eng_float", default=None,
            help="set gain in dB (default is midpoint)")
    parser.add_option("", "--samp-rate", type="eng_float", default=195312,
            help="set device sample rate")
    parser.add_option("", "--interferer", action="store_true", default=False,
            help="set device sample rate")
    parser.add_option("", "--slave-addr", type="string", default='localhost',
            help="Slave (interferer) IP Address. If --interferer is used, this is the server address.")
    parser.add_option("", "--duration", type="float", default='10',
            help="Execution time. Finishes both UP and US. (master device only)")
    parser.add_option("", "--log", action="store_true", default=False,
            help="Enable Logging")
    parser.add_option("", "--mode", type="choice", choices=["txonly", "ss"],
            help="txonly or ss")
    parser.add_option("", "--pkt-size", type="int", default=256,
            help="Size of packet to be send.")
    parser.add_option("", "--platform", type="string", default="mac",
            help="Machine running the test.")
    parser.add_option("", "--iteration", type="int", default=-1,
            help="Test Iteration.")
    parser.add_option("", "--sending-duration", type="float", default=1.0,
            help="TX duration between sensing.")
    parser.add_option("", "--sensing-duration", type="float", default=0.1,
            help="SS duration between transmission.")

    (options, args) = parser.parse_args()

    print '#######################################'
    print '# mode: ' + str(options.mode)
    print '# ss  : ' + str(options.sensing_duration)
    print '# sd  : ' + str(options.sending_duration)
    print '#######################################'

    if options.log:
        Logger._enable = True
    main(options)

    # save log
    dev = './receiver' if options.interferer else './transmitter'
    Logger.dump('./{os}_results'.format(os = options.platform),
                '/' + dev + '_' + options.platform + '_dur_' + str(int(options.duration)) + '_pkt_' +
                str(options.pkt_size) + '_burst_' + '%2.1f' % options.sending_duration + '_ssdur_' +
                '%2.1f' % options.sensing_duration + '_mode_ss',   options.iteration)
