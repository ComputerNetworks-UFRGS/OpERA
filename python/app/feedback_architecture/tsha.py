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

from gnuradio import gr
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
import math

import numpy as np
from abc import ABCMeta, abstractmethod

#Project imports:

from OpERAFlow import OpERAFlow
from device    import *
from sensing import EnergyDecision, WaveformDecision
from sensing   import EnergySSArch,  WaveformSSArch, CycloSSArch
from channels  import AWGNChannel
from gr_blocks.utils import UHDSourceDummy
from utils import Logger


TOTAL_IT = range(0, 10)

class HierarchicalSSArch(gr.sync_block):

	def __init__(self, input_len, algo1, algo2):
		gr.sync_block.__init__(self,
			name="hier",
			in_sig = [np.dtype((np.float32, input_len)), np.dtype((np.complex64, input_len))],  #pylint: disable=E1101
			#in_sig = [np.dtype((np.float32, input_len)), np.dtype((np.float32, input_len))],  #pylint: disable=E1101
			out_sig= None   #pylint: disable=E1101
		 )

		self.algo1 = algo1
		self.algo2 = algo2

		Logger.register('hier', ['decision',] )

		self._xx = {};
		self._xx[0] = {0: "00", 1: "01"}
		self._xx[1] = {0: "10", 1: "11"}

	def work(self, input_items, output_items):
		for idx in  range(len(input_items[0])):
			decf, vf = self.algo1.decision(input_items[0][idx])

			if decf == 0:
				decf, vf = self.algo2.decision(input_items[1][idx])	

			Logger.append('hier', 'decision', self._xx[Logger._ch_status][decf])
		return len(input_items[0])

			

class OpERAUtils(object):
    """
    Class with useful methods from OpERA
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
        the_source = AWGNChannel(component=uhd_source, bits_per_symbol = bits_per_symbol)

        arch1 = EnergySSArch(fft_size=1024, mavg_size=1)
        algo1 = EnergyDecision(options.th['ed'])

        if options.sensing == "wfd":
            arch2 = WaveformSSArch(fft_size=1024)
            algo2 = WaveformDecision(options.th['wfd'])
        elif options.sensing == 'cfd':
            arch2 = CycloSSArch(64, 16, 4)
	    from sensing import CycloDecision
            algo2 = CycloDecision(64, 16, 4, options.th['cfd'])
	else:
		raise AttributeError

        hier = HierarchicalSSArch(1024, algo1=algo1, algo2=algo2)

        radio = RadioDevice(name="radio")
        radio.add_arch(source=the_source, arch=arch1,   sink=(hier, 0), uhd_device=uhd_source, name='ed')
        radio.add_arch(source=the_source, arch=arch2,   sink=(hier, 1), uhd_device=uhd_source, name='sensing')
        tb.add_radio(radio, "radio")

        return tb, radio, algo1, algo1


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("", "--ph1", type="float", default=0.5)
    parser.add_option("", "--sensing", type="string", default="cfd")
    (options, args) = parser.parse_args()
    options.ph0 = 1.0 - options.ph1

    print "Loading YAML %s" % options.sensing
    thresholds = {}
    with open('lambda_%s.txt' % options.sensing, 'r') as fd:
	import yaml
        thresholds[options.sensing] = yaml.load(fd)

    with open('lambda_ed.txt', 'r') as fd:
	import yaml
        thresholds['ed'] = yaml.load(fd)

    Logger._enable = True

    options.th = {}
    options.th['ed'] = 999999999
    options.th[options.sensing] = 999999999


    for pfa in (0, 50, 100):
	    #for ebn0 in (-20, -15, -10, -5, 0, 5):
	    for ebn0 in (10, ):
		options.th = {}
		options.th['ed'] = thresholds['ed'][ebn0][ int(math.ceil(1999 * (1-(pfa/100.0)))) ]
		
		options.th[options.sensing] = thresholds[options.sensing][ebn0][ int(math.ceil(1999 * (1-(pfa/100.0)))) ] 

		tb, radio, algo1, algo2 = OpERAUtils.device_definition(options)
		radio.ed._component.set_active_freqs([1, ])
		radio.ed._component.set_center_freq(0)

		for options.it in TOTAL_IT:
			print "PFA: %f, EBN0: %d, IT: %d" % (pfa, ebn0, options.it)
			radio.ed.set_ebn0(ebn0)
			algo1._threshold =  options.th['ed'] 
			algo2._threshold =  options.th[options.sensing]

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
				radio.ed._component.set_center_freq(1)
				print "--- Setting ch_status to 1"
				Logger._ch_status = 1
			    else:
				radio.ed._component.set_center_freq(0)
				print "--- Setting ch_status to 0"
				Logger._ch_status = 0

			    if t_tot == 0:
				tb.start()
			    time.sleep(t_next)

			    t_tot += t_next
			    if t_tot >= 10.0:
			   	break;
################################################################################
			tb.stop()
			tb.wait()
			tfin = time.clock()
			enable = False

			Logger.register('global', ['clock', ])
			Logger.set('global', 'clock', tfin - tin)
			
			_sdir = '/hier_%s_%02d_%02d/' % (options.sensing, options.ph1 * 10, pfa)
			_dir =  "single/ebn0_{ebn0}".format(ebn0=ebn0)
			Logger.dump(_dir, _sdir, options.it)
			Logger.clear_all()
			# wait for thread model_channel finish
			with open("log.txt", "a+") as log:
				log.write(_dir +  _sdir )
