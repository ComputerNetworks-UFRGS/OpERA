#!/usr/bin/env python
import os
import sys
import time
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, path)


import random
import copy
import operator
from optparse  import OptionParser   #pylint: disable=F0401

# OpERA imports
from utils              import RPCExporter #pylint: disable=F0401
from utils              import RPCImporter #pylint: disable=F0401
from utils              import Logger      #pylint: disable=F0401
from utils              import Channel     #pylint: disable=F0401


from fuzzy              import Fuzzy
from graph              import Graph
from genetic            import Genetic
import simAnnealing
import blp



NUM_CHANNELS = 4
BS_ID = 666
OPERATIONS = {'tx': 0, 'rx': 1, 'idle': 2}
DEVICES = (0, 1, 2, 3)

def NOTIF_SKEL():
    return {0: False, 1: False, 2: False, 3: False}

class GNamespace():
    def __init__(self):

        self.xabu = 0
        self.p_total_iterations  = 0
        self.p_up_occ_count      = [0.0] * NUM_CHANNELS
        self.p_up_idle_count     = [0.0] * NUM_CHANNELS
        self.p_us_occ_count      = [0.0] * NUM_CHANNELS
        self.p_us_idle_count     = [0.0] * NUM_CHANNELS
        self.p_channels_count    = [0.0] * NUM_CHANNELS


        self.p_channels_interference_count = [0.0] * NUM_CHANNELS
        self.p_channels_interference_time  = [0.0] * NUM_CHANNELS
        self.p_channels_interference_hit_count = [0.0] * NUM_CHANNELS
        self.p_channels_interference_hit_time  = [0.0] * NUM_CHANNELS
        self.p_fin_transmission_time = 0.0

        self.arch = (
                ((0, 1), (2, 3)),
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

        self.use_channels       = [] # channels to use
        self.allocated_channels = [] # channels actually allocated to use

        # Request Transmission 
        self.req_tx_links = {}
        self.tx_links = {}

        # Machine state control GAMBI
        self.sense_done                = False
        self.request_transmission_done = False
        self.request_channel_done      = False
        self.transmission_done         = False

        # Notification control
        self.state_notif     = NOTIF_SKEL()

        # client array
        self.rpc_arr = []

        self.channel_list = [
                Channel(ch = 0, freq = 1.11e9, bw = 200e3),
                Channel(ch = 1, freq = 1.51e9, bw = 400e3),
                Channel(ch = 2, freq = 1.7e9, bw = 500e3),
                Channel(ch = 3, freq = 1.9e9, bw = 400e3),
         ]

        self.links = [
                #A    B   C  D
                [-1,  3,  0,  4], # A
                [3,  -1,  5,  2], # B
                [0,   5, -1,  1], # C
                [4,   2,  1, -1] # D
        ]
        self.tx_rxs = {
                0: (0, 2),
                1: (2, 3),
                2: (1, 3),
                3: (0, 1),
                4: (0, 3),
                5: (1, 2),
         }

        self.tx_pkts = { 
                0: (0, 0),
                1: (0, 0),
                2: (0, 0),
                3: (0, 0),
                4: (0, 0),
                5: (0, 0)
        }

        # GRAPH DECISION ALGORITHM VARIABLES
        self.interference_matrix =  [
                [1,1,1,1,1,1],
                [1,1,1,1,1,1],
                [1,1,1,1,1,1],
                [1,1,1,1,1,1],
                [1,1,1,1,1,1],
                [1,1,1,1,1,1]
        ]
        self.utility_matrix = [
#frequency        1  2  3   4
                 [1.0, 1.0, 1.0,  1.0], # link 1
                 [1.0 ,1.0, 1.0,  1.0], # link 2
                 [1.0, 1.0, 1.0,  1.0], # link 3
                 [1.0, 1.0, 1.0,  1.0], # link 4
                 [1.0, 1.0, 1.0,  1.0], # link 5
                 [1.0, 1.0, 1.0,  1.0]  # link 6
                 ]
        self.graph = Graph(self.interference_matrix, self.utility_matrix)



        # GENETIC Algorithm
        self.gen_occ_matrix = [
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1]
         ]

        self.gen_reward_matrix = [
                [0.0, 1.0, 1.0, 1.0], # canal 1
                [1.0, 0.0, 1.0, 1.0], # canal 2
                [1.0, 1.0, 0.0, 1.0], # canal 3
                [1.0, 1.0, 1.0, 1.0]  # canal 4
        ]

        self.gen_interference_matrix = [
                [0.0, 1.0, 1.0, 1.0], # canal 1
                [1.0, 0.0, 1.0, 1.0], # canal 2
                [1.0, 1.0, 0.0, 1.0], # canal 3
                [1.0, 1.0, 1.0, 0.0]  # canal 4
        ]


        self.genetic = Genetic(self.gen_occ_matrix, self.gen_reward_matrix, self.gen_interference_matrix )


        # blp
        self.blp_rssi = [0.0] * NUM_CHANNELS


    def clear(self):
        # Sense DATA
        self.free_channels = []
        self.occupied_channels = []
        self.use_channels = []
        self.allocated_channels = []

        # Request Transmission
        self.req_tx_links = {}
        self.tx_links = {}


        self.blp_rssi = [0.0] * NUM_CHANNELS


## Global data :)
globs = GNamespace()

def device_notification(dic, who):
    dic[who] = True

    # Is has a False, return True
    return not (False in dic.values())


def select_channels():
    """
    Select available channels for transmission
    """

    # reset channels
    globs.use_channels = []

    # list of unique elemets 
    free_channels = set(globs.free_channels)

    # if nobody says it is occupied, we can use it
    # AND LOGIC
    for i in free_channels:
        globs.use_channels.append( i )


def select_links():

    """
    Select pairs of transmitter/receiver devices randomly
    """
    # while there are links
    try:
        while globs.req_tx_links:
                # select pair
                tx1 = random.choice( [k for k in globs.req_tx_links])
                rx1 = globs.req_tx_links[tx1]

                # insert in selected links tx1 -> rx1 as tx
                # insert in selected links rx1 -> tx1 as rx
                globs.tx_links[tx1] = [rx1, OPERATIONS['tx']]
                globs.tx_links[rx1] = [tx1, OPERATIONS['rx']]
                # remove tx1 and rx1 from transmitters
                del globs.req_tx_links[tx1]

                # check if not deleted the last pair of data
                if globs.req_tx_links:
                    del globs.req_tx_links[rx1]
                    #  remove tx1 and rx1 from receivers
                    tmp = { k : v for k,v in globs.req_tx_links.iteritems() if v != tx1 and v != rx1 }
                    globs.req_tx_links = tmp
    except:
        print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@ XABIIIIIIIIIIIIIIIIIIIII'


def sense_data_func(who, val):
    """ 
    Sensing data of a device
    List of tuples [ch1, ch2, ch3] where each tuple is (decision, energy, channel_idx)
    """ 

    for tup in val:
        decision = tup[0]
        energy   = tup[1]
        channel  = tup[2]

        globs.blp_rssi[channel] += energy

        if decision == 1:
            globs.occupied_channels.append(channel)
            globs.p_up_occ_count[channel] += 1.0

        else:
            globs.free_channels.append(channel)
            globs.p_up_idle_count[channel] += 1.0

        globs.gen_occ_matrix[who][channel] = 1 if decision == 0 else 1

    if device_notification(globs.state_notif, who):
        globs.sense_done = True
        globs.state_notif = NOTIF_SKEL()

        if len(globs.occupied_channels) == 0:
            globs.xabu += 1
            if globs.xabu > 5:
                with open("test.txt", "w") as fd:
                    fd.write("XABU em %s iteracao %d\n" % (globs.options.algo_name, globs.options.iteration))
        else:
            globs.xabu = 0

        select_channels()
        select_links_and_channels()

    return True

def algo_simple(links, channels):
    ret = {}

    for l, ch in zip(links, channels):
        ret[l] = ch

    return ret


def algo_fuzzy(links, channels):
    # a_link is the link. NOT USED IN ALGO_FUZZY

    # INFORMACOES DISPONIVEIS:
    # - taxa ocupacao canal n pelo US
    # - taxa ocupacao canal n pelo US
    # - canais livres
    # - BER
    #

    channel_pu_presence = [] 
    channel_su_presence = [] 
    for ch in channels:
        pu_occ = globs.p_up_occ_count[ch]
        pu_total =  globs.p_up_occ_count[ch] + globs.p_up_idle_count[ch]

        channel_pu_presence.append(100.0*pu_occ/float(pu_total) if pu_total > 0 else 0)

        su_occ    = globs.p_channels_count[ch]
        su_total = globs.p_total_iterations
        channel_su_presence.append(100.0*su_occ/float(su_total) if su_total > 0 else 0)

    #############
    #############
    #############
    rewards = Fuzzy.full_process(channel_pu_presence, channel_su_presence)



    # map {ch1: reward, ch2: reward}
    valid_reward = {}
    for i in channels:
        valid_reward[i] = rewards.pop(0)

    # get higher rewards
    ret = {}
    for l in links:
        if valid_reward:
            # Search highesest reward
            v_cur = -1
            k_cur = -1
            for k, v in valid_reward.iteritems():
                if v > v_cur:
                    k_cur = k
                    v_cur = v

            # remove item from valid_rewards
            if k_cur > -1:
                ret[l] = k_cur
                del valid_reward[k_cur]

    return ret


def algo_graph(links, channels):
    # LOGIC HERE
    globs.graph.graph = globs.utility_matrix
    links_dict =  globs.graph.increaseUtility(channels, links)
    return links_dict

def algo_genetic(links, channels):
    globs.genetic.occupancy_matrix = globs.gen_occ_matrix
    globs.genetic.reward_matrix = globs.gen_reward_matrix

    res = globs.genetic.full_process(1000)

    d = {}
    for i in links:
        if channels:
            dev_tx  = globs.tx_rxs[i][0]
            dev_rx  = globs.tx_rxs[i][1]

            _start = 1
            try:
                ch = res[ dev_tx ].index(1)
            except ValueError:
                try:
                    ch = res[ dev_rx ].index(1)
                except ValueError:
                    ch = channels[0]

            if ch in channels:
                d[i] = ch
            else:
                ch = channels[0]

            channels.remove(ch)

    return d


def algo_sim_annealing(links, channels):
    to_sa = []
    trans_bck = {}
    for idx, i in enumerate(links):
        trans_bck[idx] = i
        tmp = []
        for idx2, ch in enumerate(channels):
            pu_occ =     globs.p_up_occ_count[ch]
            pu_total =  globs.p_up_occ_count[ch] + globs.p_up_idle_count[ch]

            tmp.append((ch, pu_occ/float(pu_total)))

        to_sa.append(tmp)


    # to_sa is a list of list.
    # inner list is  for each link
    # [ [(ch1, purate) (ch2, purate) (ch3, purate)] ]
    tup = simAnnealing.full_process(to_sa)

    dtmp = {}
    for l, ch, rw in tup:
        if trans_bck[l] in dtmp or ch in dtmp.itervalues():
            pass
        else:
            dtmp[ trans_bck[l] ] = ch

    return dtmp


def algo_blp(links, channels):
    n    = len(channels)
    l    = len(links)
    Pmax = [1.0] * len(links)
    B = []
    for i in channels:
        B.append( globs.channel_list[i].get_bandwidth())
    Pi = [1.0/(10**6)] * len(channels)
    I = [ [1.0] *len(links) ] * len(links)
    U = [1.0]
    u = len(U)
    # average rssi
    globs.blp_rssi = [rssi/4.0 for rssi in globs.blp_rssi]
    C = map(lambda x: globs.blp_rssi[x], channels)
    gama = [[1.0] * len(links)] * len(channels)

    res = blp.BLP(n, l, u, Pmax, B, Pi, I, U, C, gama)
    print n
    print l
    print Pmax
    print B
    print Pi
    print I
    print u
    print U
    print C
    print gama


    d = {}
    for idx, i in enumerate(res):
        d[links[idx]] = i[1]-1


    return d


def select_links_and_channels():

    _idx =  random.randint(0, len(globs.arch)-1)
    tups = globs.arch[ _idx ]

    links = []
    links_to_tx_rx = {}

    for tup in tups:
        dev_tx = tup[0]
        dev_rx = tup[1]

        globs.tx_links[dev_tx] = [dev_rx, 'tx', -1]
        globs.tx_links[dev_rx] = [dev_tx, 'rx', -1]

        l = globs.links[dev_tx][dev_rx]

        links.append( l )
        links_to_tx_rx[l] = (dev_tx, dev_rx)

    t_now = time.time()
    links_to_ch = globs.decision_func(links, globs.use_channels)
    Logger.append('bs', 'decision_time', time.time() - t_now)

    for link, ch in links_to_ch.iteritems():
        dev_tx, dev_rx = links_to_tx_rx[ link ]

        # increment counter os used channels
        globs.p_channels_count[ch] += 1
        globs.allocated_channels.append( ch )

        # tx links was {key: [other_side, operation]}
        # tx links and now is {key: [other_side, operation, channel]}
        globs.tx_links[dev_tx] = [ dev_rx, "tx", ch ]
        globs.tx_links[dev_rx] = [ dev_tx, "rx", ch ]

    #links = copy.deepcopy(globs.tx_links)
    #used = []
    #for dev1, _tup in links.iteritems():
    #        if globs.use_channels and dev1 not in used:
    #            dev2      = _tup[0]
    #            operation = _tup[1]

    #            used.extend( [dev1, dev2])

    #            ## LOGIC TO SELECT CHANNELS
    #            channel = globs.decision_func()

    #            # channel can be either a single element OR
    #            # a dictionary: {link_x: frequency, link_y: frequency y, ...}
    #            if isinstance(channel, dict):
    #                print "##### Channel list returned is a dict"
    #                channel = channel[globs.links[dev1][dev2]]
    #            ####


    #            # increment counter os used channels
    #            globs.p_channels_count[channel] += 1
    #            globs.allocated_channels.append( channel )

    #            # tx links was {key: [other_side, operation]}
    #            # tx links and now is {key: [other_side, operation, channel]}
    #            globs.tx_links[dev1].append(channel)
    #            globs.tx_links[dev2].append(channel)

    Logger.append('bs', 'links', globs.tx_links)

def request_tx_func(who, val):
    """
    Called by all BS to inform who wants to transmit to who
    """
    tx = who
    rx = val

    if tx in globs.req_tx_links:
        print "!!!!! Should not have two link requisitions from the same DEV"
        raise ValueError

    globs.req_tx_links[tx] = rx

    # Check if can pass to another level
    if device_notification(globs.state_notif, who):
        globs.request_transmission_done = True
        globs.state_notif = NOTIF_SKEL()

        # We have all links, now we can calcultad it
        select_links()
        select_links_and_channels()

    return True

def request_channel_func(who, val):
    """
    Called to request a channel PRIOR to transmission
    val is not used
    """

    channel = -1
    operation = OPERATIONS['idle']
    side1 = who

    if device_notification(globs.state_notif, who):
        globs.request_channel_done = True
        globs.state_notif = NOTIF_SKEL()

    # return (channel, operation) if who is in tx_links and as a valid channel
    if who in  globs.tx_links and globs.tx_links[who][2] != -1:
        return (globs.tx_links[who][0], OPERATIONS[globs.tx_links[who][1]], globs.tx_links[who][2])
    else:
        return (-1, OPERATIONS['idle'], -1)


def transmission_res_func(who, val):
    """
    Transmission results (packets send and received)
    """
    dev1 = who
    pkt_send = val[0]
    pkt_rec = val[1]

    if dev1 in globs.tx_links and globs.tx_links[dev1][1] == OPERATIONS['tx']:
        dev2 = globs.tx_links[dev1][0]
        ch_used = globs.tx_links[dev1][2]
        l = globs.links[dev1][dev2]
        globs.utility_matrix[l][ch_used] = globs.utility_matrix[l][ch_used] * 0.75 + (float(pkt_rec)/pkt_send) * 0.25

        l = globs.tx_links[dev1][dev2]

        globs.tx_pkts[l][0] += pkt_send
        globs.tx_pkts[l][1] += pkt_rec

        globs.gen_reward_matrix[dev1][ ch_used ] += globs.gen_reward_matrix[dev1][ ch_used ] *0.75 + (float(pkt_rec)/pkt_send) * 0.25


    if device_notification(globs.state_notif, who):
        globs.transmission_done = True
        globs.state_notif = NOTIF_SKEL()

    return True


def interfering_channel_func(who, val):
    channel = val[0]
    dur     = val[1]

    if channel < len(globs.channel_list):
        globs.p_channels_interference_count[channel] += 2.0 #bondam multiplipes by 0.5
        globs.p_channels_interference_time[channel] += dur

    if channel in globs.allocated_channels and globs.p_fin_transmission_time:
        globs.p_channels_interference_hit_count[channel] += 2.0

        interference_time = min( globs.p_fin_transmission_time - time.time(), dur )
        if interference_time < 0.0: # sanity check
            interference_time = 0.0
        globs.p_channels_interference_hit_time[channel] += interference_time


    return 1


def server_callback(channel_list):
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


        exec_cmd = {
                'sense_data'           : sense_data_func,
                'transmission_res'     : transmission_res_func,
                'request_tx'           : request_tx_func,
                'request_channel'      : request_channel_func,
                'interfering_channel'  : interfering_channel_func
        }

        if cmd in exec_cmd:
            return exec_cmd[cmd](who, val)

        raise AttributeError("Command not found")
##################################################################
##################################################################
##################################################################
    return command


def next_channel(cur_channel, radio):
    """
    Algorithm for channel decision implemented here.
    @param channel_list List of Channel objects.
    @param radio A RadioDevice instance.
    @return Integer 0 <= channel_idx < len(channel_list)
    """
    channel_idx = (cur_channel + 1) % len(globs.channel_list)
    return channel_idx


def server_loop(options):
    """
    Receiver radios in this loop
    """
    # Export my 'command' function to be accessible via RPC
    my_rpc = RPCExporter(addr = ("143.54.83.30", 9000))
    command = server_callback(globs.channel_list)
    my_rpc.register_function('command', command )
    my_rpc.start()

    interferer_rpc = RPCImporter(addr = "http://10.1.1.149:9001")
    interferer_rpc.register_function('command')

    ####
    #Import OTHER RADIOS RPCS
    ####
    for i in [0, 1, 2, 3]:
        rpc_cli = RPCImporter(addr = "http://143.54.83.30:%d" % (8000 + i))
        rpc_cli.register_function('command')
        globs.rpc_arr.append(rpc_cli)

    def command_sense(val):
        [x.command([BS_ID, 'sense', val]) for x in globs.rpc_arr]

    def command_request_transmission(val):
        [x.command([BS_ID, 'request_transmission', val]) for x in globs.rpc_arr]

    def command_request_channel(val):
        [x.command([BS_ID, 'request_channel', val]) for x in globs.rpc_arr]

    def command_transmission(val):
        [x.command([BS_ID, 'transmission', val]) for x in globs.rpc_arr]

    # Start execution on all RC nodes
    interferer_rpc.command([BS_ID, 'run', True])
    [x.command([BS_ID, 'run', True]) for x in globs.rpc_arr]

    t_fin = time.time() + options.test_duration
    while  t_fin > time.time():
        t_it =  time.time()

        print "!!!!! SENSING PHASE"
        command_sense(True)
        while not globs.sense_done:
            1
        globs.sense_done = False

        command_sense(False)
        #print "!!!!! TRANSMISISON REQUEST PHASE"
        #command_request_transmission(True)
        #while not globs.request_transmission_done:
        #    1
        #globs.request_transmission_done = False

        #print "!!!!! CHANNEL REQUEST PHASE"
        #command_request_transmission(False)
        command_request_channel(True)
        while not globs.request_channel_done:
            1
        globs.request_channel_done = False

        command_request_channel(False)

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
    server_loop(options)


if __name__ == "__main__":
    parser=OptionParser()
    parser.add_option("", "--test-duration", type="int", default = 600,
            help="Test Duration.")
    parser.add_option("", "--algo-name", type="string", default = None,
            help="Algorithm name.")
    parser.add_option("", "--iteration", type="int", default = 0,
            help="Iteration")
    parser.add_option("", "--sending-duration", type="int", default=5,
            help="Sending duration during each transmittion.")

    (options, args) = parser.parse_args()
    if not options.algo_name:
        raise AttributeError("--algo-name must be provided")

    decision_func = {
            'simple'       : algo_simple,
            'fuzzy'        : algo_fuzzy,
            'graph'        : algo_graph,
            'genetic'      : algo_genetic,
            'sim_annealing': algo_sim_annealing,
            'blp'          : algo_blp
    }

    globs.decision_func = decision_func[options.algo_name]
    globs.options = options

    Logger._enable = True
    Logger.register('bs', ['channel_count', 'links', 'it_dur', 'total_iterations', 'interference_count', 'interference_time', 'interference_hit_count', 'interference_hit_time', 'decision_time', 'tx_and_rx_pkts'])
    main(options)


    Logger.set('bs', 'channel_count', globs.p_channels_count)
    Logger.set('bs', 'total_iterations', globs.p_total_iterations)
    Logger.set('bs', 'interference_count', globs.p_channels_interference_count)
    Logger.set('bs', 'interference_time', globs.p_channels_interference_time)
    Logger.set('bs', 'interference_hit_count', globs.p_channels_interference_hit_count)
    Logger.set('bs', 'interference_hit_time', globs.p_channels_interference_hit_time)
    Logger.set('bs', 'tx_and_rx_pkts', globs.tx_pkts)

    Logger.dump('./results_{algo}/'.format(algo = options.algo_name),
            'bs_burst_' + str(options.sending_duration) + '_it_' + str(options.iteration))

    os._exit(1)
