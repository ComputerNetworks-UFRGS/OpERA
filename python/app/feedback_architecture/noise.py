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
from sensing import EnergyDecision, EnergyDetector, WaveformDetector, WaveformDecision, CycloDetector
from sensing import EnergySSArch,  WaveformSSArch, CycloSSArch
from channels import AWGNChannel
from gr_blocks.utils import  UHDSourceDummy
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

	bits_per_symbol = 2
        modulator = grc_blks2.packet_mod_b(digital.ofdm_mod(
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

        uhd_source = UHDSourceDummy(modulator=modulator)
        uhd_source.pre_connect(tb)  # Gambi
        the_source = AWGNChannel(bits_per_symbol = bits_per_symbol, component=uhd_source)

	algorithm = None
        if options.sensing == "ed":
            sensing = EnergySSArch(fft_size=1024, mavg_size=1)

            algorithm = EnergyDecision(0)
            sink    = EnergyDetector(1024, algorithm)
        elif options.sensing == "wfd":
            sensing = WaveformSSArch(fft_size=1024)

            algorithm = WaveformDecision(0)
            sink    = WaveformDetector(1024, algorithm)
        elif options.sensing == "cfd":
            sensing = CycloSSArch(64, 16, 4)

	    from sensing import CycloDecision
            algorithm = CycloDecision(64, 16, 4, 0)
            sink      = CycloDetector(64, 16, 4, algorithm)
        else:
            raise AttributeError



        radio = RadioDevice(name="radio")
        radio.add_arch(source=the_source, arch=sensing, sink=sink, uhd_device=uhd_source, name='sensing')
        tb.add_radio(radio, "radio")

        return tb, radio, sink


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--sensing", type="string", default="ed")
    (options, args) = parser.parse_args()

    tb, radio, sink = OpERAUtils.device_definition(options)
    radio.sensing._component.set_active_freqs([1, ])
    radio.sensing._component.set_center_freq(0)

    Logger._ch_status = 0

    noise = {}
    tb.start()
    for i in (-20, -15, -10, -5, 0, 5, 10, 15):
        radio.sensing.set_ebn0(i)

        tmp = []

	r =  sink.output()[1]
	tmp.append(  r )
	
	time.sleep(2)
        while len(tmp) < 2000:
	    r =  sink.output()[1]
            tmp.append(  r )
	    print r
            time.sleep(0.01)

        tmp = sorted(tmp)
        noise[i] = tmp

    tb.stop()

    with open("lambda_%s.txt" % options.sensing, "w+") as fd:
        import yaml
        fd.write(yaml.dump(noise))
