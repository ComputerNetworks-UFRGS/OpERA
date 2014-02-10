#!/usr/bin/env python

import os
import sys
import time
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, path)


from optparse  import OptionParser
import struct
import random

# GNURadio
from gnuradio import blocks                 #pylint: disable=F0401
from gnuradio.eng_option import eng_option  #pylint: disable=F0401


# OpERA imports
from OpERAFlow import OpERAFlow                            #pylint: disable=F0401
from algorithm.decision import EnergyDecision              #pylint: disable=F0401
from device             import UHDSource, UHDSink          #pylint: disable=F0401
from device             import RadioDevice                 #pylint: disable=F0401
from gr_blocks.packet   import PacketGMSKRx, PacketGMSKTx  #pylint: disable=F0401
from gr_blocks.sensing  import EnergySSArch                #pylint: disable=F0401
from utils              import RPCExporter, RPCImporter    #pylint: disable=F0401
from utils              import PktQueue, PktSender         #pylint: disable=F0401
from utils              import Logger                      #pylint: disable=F0401
from utils              import Channel                     #pylint: disable=F0401


# 10.1.1.146 is the interferer
all_radios_ip = ["10.1.1.145", "10.1.1.146", "10.1.1.147", "10.1.1.148"]

HOSTS_IP = ["143.54.83.30", "143.54.83.30", "143.54.83.30", "143.54.83.30"]

OPERATIONS = {'tx': 0, 'rx': 1, 'idle': 2}
CHANNEL_IDLE = Channel(ch = 999, freq = 900e6, bw = 200e3)

class GNamespace():
    pass

globs = GNamespace()
globs.total_rx = 0
globs.total_tx = 0
globs.instant_rx = 0
globs.total_starving = 0
globs.wait_for_get = False


def build_radio(options):
    radio = RadioDevice(name = 'radio')

    #############################
    #
    # RX PATH - sensing and packet
    #
    #############################
    ss_and_rx_source = UHDSource(device_addr = "ip=%s" % options.my_ip, antenna = "TX/RX")

    ss_sink = blocks.probe_signal_f()
    ss_path = EnergySSArch(fft_size = 512, mavg_size = 5, algorithm = EnergyDecision(th = 5.0/10**4) )
    radio.add_arch(source = ss_and_rx_source,
            sink = ss_sink,
            arch = ss_path,
            name = 'ss',
            uhd_device = ss_and_rx_source)

    pkt_rx_path = PacketGMSKRx(callback = PktQueue())
    radio.add_arch(source = ss_and_rx_source,
            sink = None,
            arch = pkt_rx_path,
            name = 'rx',
            uhd_device = ss_and_rx_source)


    #############################
    #
    # TX PATH - packet
    #
    #############################
    #uhd_sink = UHDSink("addr=%s" % options.my_ip)
    #pkt_tx_path = PacketGMSKTx()

    #radio.add_arch(source = None,
    #        sink = uhd_sink,
    #        arch = pkt_tx_path,
    #        name = 'tx',
    #        uhd_device = uhd_sink)


    #radio.set_samp_rate(200e3)
    return radio


def callback_radio(radio):
    """
    Build the function called from remote hosts 
    """
##################################################################
##################################################################
##################################################################
    def command(payload):
        """
        Implementation of commands received here
        SUGGESTION: payload as a tuple (who, cmd, value)
        """
        who = payload[0] # integer, as in all_radios_ip
        cmd = payload[1] # string
        val = payload[2] # parameter

        ctrl_params = [ "run", "sense", "request_transmission", "request_channel", "transmission" ]

        exec_cmd = {
                "set_channel"        : radio.set_channel,
                "set_gain"           : radio.set_gain,
                "get_bit_rate"       : radio.rx.counter.get_bps,
                "get_pkts"           : radio.rx.counter.get_pkts,
                "get_accumulated"    : radio.rx.counter.get_pkt_accumulated
        }

        # Valor
        if cmd == "set_channel":
            val = Channel(val['_channel'], val['_freq'], val['_bw'])

        # Ctrl commands
        if cmd in ctrl_params:
            if cmd == "run":
                command.run = val
            elif cmd == 'sense':
                command.sense = val
            elif cmd == 'request_transmission':
                command.request_transmission = val
            elif cmd == 'request_channel':
                command.request_channel = val
            elif cmd == 'transmission':
                command.transmission = val
            else:
                print "##### Command not found"
                raise AttributeError("Command not found")
            return True

        if cmd in exec_cmd:
            if cmd == 'get_accumulated':
                globs.wait_for_get = False
                rx = exec_cmd[cmd](True)
                globs.instant_rx = rx
                return rx

            if val:
                return exec_cmd[cmd](val)
            else:
                return exec_cmd[cmd]()

        raise AttributeError("Command not found")
##################################################################
##################################################################
##################################################################
    # variables
    command.run          = False
    command.sense        = False
    command.request_transmission = False
    command.request_channel = False
    command.transmission = False
    return command


def next_channel(channel_list, cur_channel, radio):
    """
    Algorithm for channel decision implemented here.
    @param channel_list List of Channel objects.
    @param radio A RadioDevice instance.
    @return Integer 0 <= channel_idx < len(channel_list)
    """
    channel_idx = (cur_channel + 1) % len(channel_list)
    return channel_idx


def cognitive_radio_loop(options, radio, channel_list):
    """
    Program loop here.
    @param radio A RadioDevice instance.
    @param channel_list List of Channel objects.
    """

    # Export my server
    command = callback_radio(radio)

    my_rpc = RPCExporter(addr = ("143.54.83.30", 8000 + options.my_id))
    my_rpc.register_function('command', command )
    my_rpc.start()


    # Wait broker start
    while not command.run:
        1

    ####
    #Import OTHER RADIOS RPCS
    ####
    rpc_arr = []
    RADIOS = [0, 3]
    for i in RADIOS:
            rpc_cli = RPCImporter(addr = "http://%s:%d" % (HOSTS_IP[i], 8000 + i))
            rpc_cli.register_function('command')
            rpc_arr.append(rpc_cli)

    # Import PassiveRadio RPC calls
    bs_rpc = RPCImporter(addr = "http://%s:9000" % (options.broker_ip))
    bs_rpc.register_function('command')

    # Register parameters for transmission
    Logger.register('radio', ['tx_pkts', 'rx_pkts', 'rx2_pkts' , 'channel', 'operation', 'receiver', 'starving', 'total_tx', 'total_rx', 'total_starving']) 
    # loop
    pkt_len = options.pkt_len
    payload = struct.pack('%sB' % pkt_len, *[options.my_id] * pkt_len)

    print '##### Entering Transmitter loop'
    c_starving = 0

    while command.run:
        """
        ######## FUNCOES:

        ---- BW do canal
        radio.get_bandwidth()

        ---- Num. simbolos na modulacao
        radio.{tx,rx}.symbols()

        ---- B/S da modulacao
        radio.{tx,rx}.bits_per_symbol()

        ---- Pkt/s NO ULTIMO SEGUNDO
        radio.{tx,rx}.counter.get_pkts()

        ---- b/s NO ULTIMO SEGUNDO.
        radio.{tx,rx}.counter.get_bps()

        ---- Pacotes acumulados desde a ultima chamada.
        radio.{tx,rx}.counter.get_pkt_accumulated(clear = False)

        ---- Troca de canal. channel eh um objeto Channel
        radio.set_channel(channel)
        #################
        """

        # sense
        while not command.sense and command.run:
            1;
        if  not command.run:
            break

        sense_data = []

        radio.set_gain(0)
        for channel in channel_list:
            decision, energy = radio.ss.sense_channel(channel, 0.1)
            sense_data.append( (decision, float(energy), channel.get_channel()) )
            print 'Channel energy: ', energy

        bs_rpc.command([options.my_id, 'sense_data', sense_data])

        while not command.transmission:
            1

        # tx pkts is the number of packets transmitted
        # globs.instant_rx is the number of packets received.
        #   Is global cause it is hard to be synchorined with the TX dev when WE are the RX
        #   The easiest way is to let the TX dev control when get this value. And we do it in the RPC server method
        tx_pkts = globs.instant_rx = 0

        time.sleep(options.sending_duration)
        bs_rpc.command([options.my_id, 'transmission_res', (tx_pkts, globs.instant_rx)])

    Logger.set('radio', 'total_tx', globs.total_tx)
    Logger.set('radio', 'total_rx', globs.total_rx)
    Logger.set('radio', 'total_starving', globs.total_starving)

def main(options):
    options.my_ip = all_radios_ip[options.my_id]

    radio =  build_radio(options)
    radio.id = options.my_id

    tb = OpERAFlow('OperaFlow')
    tb.add_radio(radio, 'radio')
    tb.start()

    channel_list = [ Channel(ch = 0, freq = 2.2e9, bw = 200e3), ]

    cognitive_radio_loop(options, radio, channel_list)

    tb.stop()
    tb.wait()


if __name__ == "__main__":
    parser=OptionParser(option_class=eng_option)
    parser.add_option("", "--pkt-len", type="int", default=64,
            help="Length of packet to be send.")
    parser.add_option("", "--port", type="int", default=8000,
            help="Port for RPC calls.")
    parser.add_option("", "--sending-duration", type="int", default=5,
            help="Sending duration during each transmittion.")
    parser.add_option("", "--sensing-duration", type="eng_float", default=0.1,
            help="Sensing duration during each sensing.")
    parser.add_option("", "--my-id", type="int", help="USRP ID.")
    parser.add_option("", "--iteration", type="int", default = 0,
            help="Iteration")
    parser.add_option("", "--broker-ip", type="string", default = "143.54.83.30",
            help="Broker IP")

    (options, args) = parser.parse_args()

    Logger._enable = True

    main(options)

    device = "radio_" + str(options.my_id)
    Logger.dump('./results/',
            device + '_it_' + str(options.iteration) +  '_pkt_' + str(options.pkt_len) + '_burst_' + '%2.1f' % options.sending_duration + '_ssdur_' + '%2.1f' % options.sensing_duration)

    os._exit(1)
