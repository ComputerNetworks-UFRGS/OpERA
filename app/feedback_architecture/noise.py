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
from optparse  import OptionParser
from struct    import *
from threading import Thread
import time
import threading
import random

import numpy as np
from abc import ABCMeta, abstractmethod

#Project imports:

from OpERAFlow          import OpERAFlow
from device             import *
from algorithm          import FeedbackAlgorithm, KunstTimeFeedback, AlwaysTimeFeedback
from algorithm.decision import EnergyDecision, WaveformDecision, BayesLearningThreshold
from gr_blocks.sensing  import EnergySSArch,  WaveformSSArch, FeedbackSSArch
from gr_blocks.packet   import PacketGMSKRx, PacketOFDMRx
from gr_blocks.packet   import PacketGMSKTx, PacketOFDMTx, SimpleTx
from gr_blocks.channels import FadingChannel, AWGNChannel
from gr_blocks.utils    import SNREstimator, UHDSourceDummy
from utils              import Logger


## Class with useful methods from OpERA
class OpERAUtils(object):
    @staticmethod
    ## Definition of the devices used in the program.
    def device_definition(options):

        tb = OpERAFlow(name = 'US')

        modulator = digital.psk.psk_mod(
                constellation_points=8,
                mod_code="gray",
                differential=True,
                samples_per_symbol=2,
                excess_bw=0.35,
                verbose=False,
                log=False,
            )

        bl_algo = BayesLearningThreshold(in_th = 0.0,
                min_th = 0.0,
                max_th = 100e3,
                delta_th = 1,
                k = 1.0)

        uhd_source   = UHDSourceDummy(modulator = modulator)
        uhd_source.pre_connect( tb ) # Gambi
        the_source   = AWGNChannel(component = uhd_source)

        energy        = EnergySSArch(fft_size    = 1024, mavg_size = 1, algorithm = bl_algo)
        waveform      = WaveformSSArch(fft_size  = 1024, algorithm = WaveformDecision(threshold = 0.1))
        energy.pre_connect(tb)
        waveform.pre_connect(tb)


        feedback = FeedbackSSArch(block_manager = waveform,
                block_learner = energy,
                feedback_algorithm = FeedbackAlgorithm(learner = bl_algo,
                    manager = waveform._detector._wa,
                    aFeedbackStrategy = KunstTimeFeedback()
                    )
                )

        radio = RadioDevice(name = "radio")
        radio.add_arch(source = the_source, arch = feedback, sink = blocks.probe_signal_f(), uhd_device = uhd_source, name = 'feedback')

        tb.add_radio(radio, "radio")

        return tb, radio


if __name__ == "__main__":
    parser=OptionParser()
    parser.add_option("", "--ebn0", type="float", default = 10.0)
    parser.add_option("", "--it", type="int", default = 0)
    (options, args) = parser.parse_args()

    tb, radio = OpERAUtils.device_definition(options)
    radio.feedback._component.set_active_freqs([1, ])
    radio.feedback._component.set_center_freq(0)
    radio.feedback.set_EbN0(options.ebn0)

    time.sleep(1)
    print "#### TESTING WITH EBN0 %f, IT %d" % (options.ebn0, options.it)

    tin = time.clock()
    tb.start()
    Logger._enable = True

    time.sleep(60)

    enable = False
    tb.stop()
    tfin = time.clock()

    Logger.register('global', ['clock', ])
    Logger.set('global', 'clock', tfin - tin)

    subdir =  "ebn0_{ebn0}".format(ebn0 = options.ebn0)
    Logger.dump('./noise/', subdir, options.it)
