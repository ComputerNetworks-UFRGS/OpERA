#!/usr/bin/env python
import os
import sys
import time
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, path)

import random
import copy
import operator
from optparse import OptionParser   #pylint: disable=F0401

# OpERA imports
from utils import RPCExporter  #pylint: disable=F0401
from utils import RPCImporter  #pylint: disable=F0401
from utils import Logger       #pylint: disable=F0401
from utils import Channel      #pylint: disable=F0401

NUM_CHANNELS = 1
BS_ID = 666
OPERATIONS = {'tx': 0, 'rx': 1, 'idle': 2}
DEVICES = (0, 3)


#::TODO:: functions and classes definitions
def NOTIF_SKEL():
    """

    """
    return {0: False, 3: False}


class GNamespace():
    """

    """
    def __init__(self):
        """
        CTOR
        """

        self.xabu = 0
        self.p_total_iterations = 0
        self.p_up_occ_count = [0.0] * NUM_CHANNELS
        self.p_up_idle_count = [0.0] * NUM_CHANNELS
        self.p_us_occ_count = [0.0] * NUM_CHANNELS
        self.p_us_idle_count = [0.0] * NUM_CHANNELS
        self.p_channels_count = [0.0] * NUM_CHANNELS

        self.p_channels_interference_count = [0.0] * NUM_CHANNELS
        self.p_channels_interference_time = [0.0] * NUM_CHANNELS
        self.p_channels_interference_hit_count = [0.0] * NUM_CHANNELS
        self.p_channels_interference_hit_time = [0.0] * NUM_CHANNELS
        self.p_fin_transmission_time = 0.0

        self.arch = (((0, 1), (2, 3)),
                     ((1, 0), (2, 3)),
                     ((0, 1), (3, 2)),
                     ((0, 2), (1, 3)),
                     ((2, 0), (1, 3)),
                     ((0, 2), (3, 1)),
                     ((0, 3), (1, 2)),
                     ((3, 0), (1, 2)),
                     ((0, 3), (2, 1)),
                     )

        # Sense DATA
        self.free_channels = []
        self.occupied_channels = []

        self.use_channels = []  # channels to use
        self.allocated_channels = []  # channels actually allocated to use

        # Request Transmission 
        self.req_tx_links = {}
        self.tx_links = {}

        # Machine state control GAMBI
        self.sense_done = False
        self.request_transmission_done = False
        self.request_channel_done = False
        self.transmission_done = False

        # Notification control
        self.state_notif = NOTIF_SKEL()

        # client array
        self.rpc_arr = []

        self.channel_list = [Channel(ch=0, freq=2.2e9, bw=200e3)]

    def clear(self):
        """
        """
        # Sense DATA
        self.free_channels = []
        self.occupied_channels = []
        self.use_channels = []
        self.allocated_channels = []

        # Request Transmission
        self.req_tx_links = {}
        self.tx_links = {}

## Global data :)
globs = GNamespace()


def device_notification(dic, who):
    """

    @param dic
    @param who
    """
    dic[who] = True

    # Is has a False, return True
    return not (False in dic.values())


def fusion_function():
    """
    Select available channels for transmission
    """

    # reset channels
    globs.use_channels = []

    # list of unique elements
    free_channels = set(globs.free_channels)

    # if nobody says it is occupied, we can use it
    # AND LOGIC
    for i in free_channels:
        globs.use_channels.append(i)


def sense_data_func(who, val):
    """ 
    Sensing data of a device
    List of tuples [ch1, ch2, ch3] where each tuple is (decision, energy, channel_idx)
    @param who
    @param val
    """ 

    for tup in val:
        decision = tup[0]
        energy = tup[1]
        channel = tup[2]

        if decision == 1:
            globs.occupied_channels.append(channel)
            globs.p_up_occ_count[channel] += 1.0
        else:
            globs.free_channels.append(channel)
            globs.p_up_idle_count[channel] += 1.0

    if device_notification(globs.state_notif, who):
        globs.sense_done = True
        globs.state_notif = NOTIF_SKEL()

        # FUNCAO DE FUSAO
        # Fusion function.
        fusion_function()

    return True


def algo_simple(links, channels):
    """

    @param links
    @param channels
    """
    ret = {}

    for l, ch in zip(links, channels):
        ret[l] = ch

    return ret


def request_tx_func(who, val):
    """
    Called by all BS to inform who wants to transmit to whom.
    @param who
    @param val
    """
    tx = who
    rx = val

    if tx in globs.req_tx_links:
        print "!!!!! Should not have two link requisitions from the same DEV"
        raise ValueError

    # Check if can pass to another level
    if device_notification(globs.state_notif, who):
        globs.request_transmission_done = True
        globs.state_notif = NOTIF_SKEL()

        # We have all links, now we can calculate it

    return True


#::TODO:: se o val nao é usado, pq ainda continua por aqui?
def request_channel_func(who, val):
    """
    Called to request a channel PRIOR to transmission
    val is not used
    @param who
    @param val
    """

    channel = -1
    operation = OPERATIONS['idle']
    side1 = who

    if device_notification(globs.state_notif, who):
        globs.request_channel_done = True
        globs.state_notif = NOTIF_SKEL()

    # return (channel, operation) if who is in tx_links and as a valid channel
    if who in globs.tx_links and globs.tx_links[who][2] != -1:
        return globs.tx_links[who][0], OPERATIONS[globs.tx_links[who][1]], globs.tx_links[who][2]
    else:
        return -1, OPERATIONS['idle'], -1


def transmission_res_func(who, val):
    """
    Transmission results (packets send and received)
    @param who
    @param val
    """
    dev1 = who
    pkt_send = val[0]
    pkt_rec = val[1]

    if device_notification(globs.state_notif, who):
        globs.transmission_done = True
        globs.state_notif = NOTIF_SKEL()

    return True


def interfering_channel_func(who, val):
    """

    @param who
    @param val
    """
    channel = val[0]
    dur = val[1]

    if channel < len(globs.channel_list):
        globs.p_channels_interference_count[channel] += 1.0
        globs.p_channels_interference_time[channel] += dur

    if channel in globs.allocated_channels and globs.p_fin_transmission_time:
        globs.p_channels_interference_hit_count[channel] += 1.0

        interference_time = min(globs.p_fin_transmission_time - time.time(), dur)
        if interference_time < 0.0:  # sanity check
            interference_time = 0.0
        globs.p_channels_interference_hit_time[channel] += interference_time

    return 1


def server_callback(channel_list):
    """
    Build the function called from remote hosts
    @param channel_list
    """

    def command(payload):
        """
        Implementation of commands received here
        SUGGESTION: payload as a tuple (who, cmd, value)
        @param payload
        """
        who = payload[0]  # integer, as in all_radios_ip
        cmd = payload[1]  # string
        val = payload[2]  # parameter


        exec_cmd = {'sense_data': sense_data_func,
                    'transmission_res': transmission_res_func,
                    #'request_tx': request_tx_func,
                    'interfering_channel': interfering_channel_func
                    }

        if cmd in exec_cmd:
            return exec_cmd[cmd](who, val)

        raise AttributeError("Command not found")

    return command


def server_loop(options):
    """
    Receiver radios in this loop
    @param options
    """

    # Export my 'command' function to be accessible via RPC
    my_rpc = RPCExporter(addr=("143.54.83.30", 9000))
    command = server_callback(globs.channel_list)
    my_rpc.register_function('command', command)
    my_rpc.start()

    interferer_rpc = RPCImporter(addr="http://143.54.83.30:9001")
    interferer_rpc.register_function('command')

    ####
    #Import OTHER RADIOS RPCS
    ####

    for i in DEVICES:
        rpc_cli = RPCImporter(addr="http://143.54.83.30:%d" % (8000 + i))
        rpc_cli.register_function('command')
        globs.rpc_arr.append(rpc_cli)

    def command_sense(val):
        """
        @param val
        """
        [x.command([BS_ID, 'sense', val]) for x in globs.rpc_arr]

    def command_request_transmission(val):
        """
        @param val
        """
        [x.command([BS_ID, 'request_transmission', val]) for x in globs.rpc_arr]

    def command_request_channel(val):
        """
        @param val
        """
        [x.command([BS_ID, 'request_channel', val]) for x in globs.rpc_arr]

    def command_transmission(val):
        """
        @param val
        """
        [x.command([BS_ID, 'transmission', val]) for x in globs.rpc_arr]

    # Start execution on all RC nodes
    interferer_rpc.command([BS_ID, 'run', True])
    [x.command([BS_ID, 'run', True]) for x in globs.rpc_arr]

    t_fin = time.time() + options.test_duration
    while t_fin > time.time():
        t_it = time.time()

        print "!!!!! SENSING PHASE"
        command_sense(True)
        while not globs.sense_done:
            1
        globs.sense_done = False

        command_sense(False)
        print "!!!!! TRANSMISSION PHASE"
        command_transmission(True)
        globs.p_fin_transmission_time = time.time() + options.sending_duration
        while not globs.transmission_done:
            1
        globs.p_fin_transmission_time = None

        ## moment to evaluate links
        # HERE
        ####
        # clear all used  data
        globs.transmission_done = False

        globs.clear()
        globs.p_total_iterations += 1

        command_transmission(False)
        Logger.append('bs', 'it_dur', time.time() - t_it)

    # Stop execution on all CR nodes
    interferer_rpc.command([BS_ID, 'run', False])
    [x.command([BS_ID, 'run', False]) for x in globs.rpc_arr]


def main(options):
    """
    Main function.
    @param options
    """
    server_loop(options)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--test-duration", type="int", default=600,
                      help="Test Duration.")
    parser.add_option("", "--iteration", type="int", default=0,
                      help="Iteration")
    parser.add_option("", "--sending-duration", type="int", default=5,
                      help="Sending duration during each transmittion.")

    (options, args) = parser.parse_args()

    globs.options = options

    Logger._enable = True
    Logger.register('bs', ['channel_count', 'links', 'it_dur', 'total_iterations', 'interference_count',
                           'interference_time', 'interference_hit_count', 'interference_hit_time', 'decision_time',
                           'tx_and_rx_pkts'])
    main(options)

    Logger.set('bs', 'channel_count', globs.p_channels_count)
    Logger.set('bs', 'total_iterations', globs.p_total_iterations)
    Logger.set('bs', 'interference_count', globs.p_channels_interference_count)
    Logger.set('bs', 'interference_time', globs.p_channels_interference_time)
    Logger.set('bs', 'interference_hit_count', globs.p_channels_interference_hit_count)
    Logger.set('bs', 'interference_hit_time', globs.p_channels_interference_hit_time)

    Logger.dump('./results/', 'bs_burst_' + str(options.sending_duration) + '_it_' + str(options.iteration))
    os._exit(1)
