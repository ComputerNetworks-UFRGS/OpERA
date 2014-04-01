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

import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, path)

from gnuradio  import gr
from gnuradio import blocks
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import digital
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from struct import *
from threading import Thread
import time
import copy
import threading
import random
import yaml

import numpy as np
from abc import ABCMeta, abstractmethod

#Project imports:

from OpERAFlow import OpERAFlow
from device import *
from algorithm import FeedbackAlgorithm, KunstTimeFeedback, AlwaysTimeFeedback
from sensing import EnergyDecision, WaveformDecision, BayesLearningThreshold, SARSA, CycloDecision
from sensing import EnergySSArch2,  WaveformSSArch2, FeedbackSSArch2, CycloSSArch
from packet import PacketGMSKRx, PacketOFDMRx
from packet import PacketGMSKTx, PacketOFDMTx, SimpleTx
from channels import FadingChannel, AWGNChannel
from gr_blocks.utils import SNREstimator, UHDSourceDummy
from utils import Logger


class OpERAUtils(object):
    """
    Class with useful methods from OpERA.
    """
    @staticmethod
    def device_definition(options):
        """
        Definition of the devices used in the program.
        @param options
        """

        tb = OpERAFlow(name='US')

        modulator = digital.psk.psk_mod(constellation_points=8,
                                        mod_code="gray",
                                        differential=True,
                                        samples_per_symbol=2,
                                        excess_bw=0.35,
                                        verbose=False,
                                        log=False,
                                        )

        bl_algo = BayesLearningThreshold(in_th=options.threshold,
                                         min_th=0.0,
                                         max_th=100e3,
                                         delta_th=options.threshold/20.0,
                                         k=1.0)

        #bl_algo = SARSA(min_th = 0.0, max_th = 100e3, delta_th = options.threshold/20.0)

        uhd_source = UHDSourceDummy(modulator=modulator)
        uhd_source.pre_connect(tb)  # Gambi
        the_source = AWGNChannel(component=uhd_source)

        energy = EnergySSArch2(fft_size=1024, mavg_size=1, algorithm=bl_algo)
        energy.pre_connect(tb)

        if options.sensing == "waveform":
            feedback = FeedbackSSArch2(learning_algorithm=bl_algo,
                                       feedback_algorithm=KunstTimeFeedback(),
                                       waveform=WaveformDecision(threshold=0.06),
                )

            waveform = WaveformSSArch2(fft_size=1024)
            waveform.pre_connect(tb)

            #waveform      = WaveformDecision2(fft_size  = 1024, mavg_size = 1, algorithm = EnergyDecision(0.1))

        else:
            feedback = FeedbackSSArch2(learning_algorithm=bl_algo,
                                       feedback_algorithm=KunstTimeFeedback(),
                                       waveform=CycloDecision(1024, 1, 1024, th=options.cft),
                                       _type=np.complex64
                )
            waveform = CycloSSArch(1024, 1, 1024)

        radio = RadioDevice(name="radio")
        radio.add_arch(source=the_source, arch=energy, sink=(feedback, 0), uhd_device=uhd_source, name='ed')
        radio.add_arch(source=the_source, arch=waveform, sink=(feedback, 1), uhd_device=uhd_source, name='feedback')

        #radio.add_arch(source = the_source, arch = waveform, sink = blocks.probe_signal_vf(1024),
        # uhd_device = uhd_source, name = 'feedback')

        tb.add_radio(radio, "radio")

        return tb, radio


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--ebn0", type="float", default=10.0)
    parser.add_option("", "--ph1", type="float", default=0.5)
    parser.add_option("", "--it", type="int", default=0)
    parser.add_option("", "--sensing", type="string", default="cyclostationary")
    (options, args) = parser.parse_args()

    config_tmp = {}
    with open('noise.data', 'r') as fd:
        config_tmp = yaml.load(fd)
    config = copy.deepcopy(config_tmp)

    for key in config_tmp.iterkeys():
        for ebn0 in config_tmp[key].iterkeys():
            config[key][float(ebn0)] = config_tmp[key][ebn0]

    options.threshold = config['energy'][options.ebn0]
    options.wft = config['corr'][options.ebn0]
    options.cft = config['cyclo2'][options.ebn0]
    options.ph0 = 1.0 - options.ph1

    tb, radio = OpERAUtils.device_definition(options)
    radio.feedback._component.set_active_freqs([1, ])
    radio.feedback.set_EbN0(options.ebn0)

    time.sleep(1)
    Logger._enable = True
    print "#### TESTING WITH EBN0 %f, IT %d" % (options.ebn0, options.it)

    enable = True

    def model_channel():
        """

        """
        global enable

        status = random.choice([0, 1])

        while enable:
            if status == 1:
                radio.feedback._component.set_center_freq(1)
                Logger._ch_status = 1
                time.sleep(random.expovariate(1.0/2.0) * options.ph1 * 2)
            else:
                radio.feedback._component.set_center_freq(0)
                Logger._ch_status = 0
                time.sleep(random.expovariate(1.0/2.0) * options.ph0 * 2)

            status = (status + 1) % 2

    t_mc = threading.Thread(target=model_channel)

    tin = time.clock()
    tb.start()
    t_mc.start()

    time.sleep(10)

    enable = False
    tb.stop()
    tfin = time.clock()

    Logger.register('global', ['clock', ])
    Logger.set('global', 'clock', tfin - tin)

    subdir =  "ebn0_{ebn0}".format(ebn0=options.ebn0)
    Logger.dump('./my_%s_%02d/' % (options.sensing, options.ph1 * 10), subdir, options.it)
