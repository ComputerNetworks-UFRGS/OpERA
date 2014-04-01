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
import threading
import random

import numpy as np
from abc import ABCMeta, abstractmethod

#Project imports:

from OpERAFlow import OpERAFlow
from device import *
from algorithm import FeedbackAlgorithm, KunstTimeFeedback, AlwaysTimeFeedback
from sensing import EnergyDecision, WaveformDecision, BayesLearningThreshold
from sensing import EnergySSArch,  WaveformSSArch, FeedbackSSArch
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
    def device_definition():
        """
        Definition of the devices used in the program.
        @param options
        """

        tb = OpERAFlow(name='US')

        modulator = grc_blks2.packet_mod_b(digital.ofdm_mod(
        		options=grc_blks2.options(
        			modulation="qam256",
        			fft_length=1024,
        			occupied_tones=32,
        			cp_length=32,
        			pad_for_usrp=True,
        			log=None,
        			verbose=None,
        		),
        	),
        	payload_length=0,
        )

        uhd_source = UHDSourceDummy(modulator=modulator)
        uhd_source.pre_connect(tb)  # Gambi
        the_source = AWGNChannel(component=uhd_source)

        energy = EnergySSArch(fft_size=1024, mavg_size=1, algorithm=EnergyDecision(0))

        radio = RadioDevice(name="radio")
        radio.add_arch(source=the_source, arch=energy, sink=blocks.probe_signal_f(), uhd_device=uhd_source, name='ed')
        tb.add_radio(radio, "radio")

        return tb, radio


if __name__ == "__main__":
    tb, radio = OpERAUtils.device_definition()
    radio.ed._component.set_active_freqs([1, ])
    radio.ed._component.set_center_freq(1)

    noise = {}
    tb.start()
    for i in range(0, 11):
        radio.ed.set_ebn0(i)
        time.sleep(1)

        tmp = []
        while len(tmp) < 2000:
            tmp.append( radio.ed.output()[1] )
            print radio.ed.output()
            time.sleep(0.1)

        tmp = sorted(tmp)
        print tmp
        noise[i] = {0.9: tmp[int(len(tmp)*0.9 )],
                   0.95: tmp[int(len(tmp)*0.95)],
                   0.99: tmp[int(len(tmp)*0.99)],
                   1:    tmp[int(len(tmp)-1   )] }

    tb.stop()

    with open("noise.txt", "a+") as fd:
        import yaml
        fd.write(yaml.dump(noise))
