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
import math

import numpy as np
from abc import ABCMeta, abstractmethod

#Project imports:

from OpERAFlow import OpERAFlow
from device import *
from sensing import EnergyDetector, EnergyDecision, WaveformDetector, WaveformDecision, CycloDetector, CycloDecision
from sensing import EnergySSArch,  WaveformSSArch, CycloSSArch
from channels import AWGNChannel
from gr_blocks.utils import  UHDSourceDummy
from utils import Logger

TOTAL_IT = range(10)

options = {}
status = random.choice([0, 1])


def change_status_fun():	
	global status
	global options

	status = (status + 1) % 2
	t_next = math.fabs(random.expovariate(1.0/3.0) * options.ph[status] * 2)

	print '----- status changed to ', status
	Logger._ch_status = status
	return status, t_next

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

        uhd_source = UHDSourceDummy(modulator=modulator, f = change_status_fun)
        uhd_source.pre_connect(tb)  # Gambi
        the_source = AWGNChannel(bits_per_symbol = bits_per_symbol ,component=uhd_source)

	algorithm = None
        if options.sensing == "ed":
            sensing = EnergySSArch(fft_size=1024, mavg_size=1)

            algorithm = EnergyDecision(options.th)
            sink    = EnergyDetector(1024, algorithm)
        elif options.sensing == "wfd":
            sensing = WaveformSSArch(fft_size=1024)

            algorithm = WaveformDecision(options.th)
            sink    = WaveformDetector(1024, algorithm)
        elif options.sensing == "cfd":
            sensing = CycloSSArch(64, 16, 4)

	    from sensing import CycloDecision
            algorithm = CycloDecision(64, 16, 4, options.th)
            sink      = CycloDetector(64, 16, 4, algorithm)
        else:
            raise AttributeError

        radio = RadioDevice(name="radio")
        radio.add_arch(source=the_source, arch=sensing, sink=sink, uhd_device=uhd_source, name='sensing')


        tb.add_radio(radio, "radio")

        return tb, radio, algorithm


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--sensing", type="string", default="ed")
    parser.add_option("", "--ph1", type="float", default=0.5)

    (options, args) = parser.parse_args()
    options.ph0 = 1.0 - options.ph1

    print "Loading YAML"
    with open("lambda_%s.txt" % options.sensing, "r") as fd:
	import yaml
	thresholds = yaml.load(fd)
    print "\tDone"

    enable = True
    is_running = False
    Logger._enable = True

    options.ph0 = 1.0 - options.ph1
    options.ph = {0: options.ph0, 1: options.ph1 }
    options.th = -999999 # temporary, overwritten after setting ebn0
    tb, radio, algorithm = OpERAUtils.device_definition(options)

    for pfa in (0, 50, 100):
	    #for ebn0 in (-20, -15, -10, -5, 0, 5):
	    for ebn0 in (10, ):
		th = thresholds[ebn0][ int(math.ceil(1999 * (1-(pfa/100.0)))) ]

		for options.it in TOTAL_IT:
			print "PFA: %f, EBN0: %d, IT: %d" % (pfa, ebn0, options.it)
			radio.sensing.set_ebn0(ebn0)
			algorithm._threshold =  th 

			tin = time.clock()
################################################################################
			options.ph = {0: options.ph0, 1: options.ph1 }
			t_tot = 0.0
			status = random.choice([0, 1])

			while True:
			    x = random.random()
			    t_next = math.fabs(random.expovariate(1.0/3.0))
		
			    if x < options.ph1:
			        status = 1
		            else:
				status = 0

       			    if t_tot + t_next > 10.0:
     			        t_next = 10.0 - t_tot 

			    if status == 1:
				radio.sensing._component.set_center_freq(1)
				print "--- Setting ch_status to 1"
				Logger._ch_status = 1
			    else:
				radio.sensing._component.set_center_freq(0)
				print "--- Setting ch_status to 0"
				Logger._ch_status = 0

			    if t_tot == 0:
				tb.start()
			    time.sleep(t_next)

			    t_tot += t_next
			    if t_tot >= 10.0:
			   	break;
################################################################################
			tfin = time.clock()
			tb.stop()
			tb.wait()
			enable = False

			Logger.register('global', ['clock', ])
			Logger.set('global', 'clock', tfin - tin)
			
			_sdir = '/%s_%02d_%02d/' % (options.sensing, options.ph1 * 10, pfa)
			_dir =  "single/ebn0_{ebn0}".format(ebn0=ebn0)
			Logger.dump(_dir, _sdir, options.it)
			Logger.clear_all()
			with open("log.txt", "a+") as log:
				log.write(_dir +  _sdir )
