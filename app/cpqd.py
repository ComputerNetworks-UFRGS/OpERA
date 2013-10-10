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

#!/usr/bin/env python

## @package device

# ::TODO:: Discover how to include patches externally
import sys
import os
import random

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)

from gnuradio import gr
from gnuradio import blocks
from gnuradio.eng_option import eng_option
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from math      import *
from optparse  import OptionParser

# Project imports
from OpERAFlow import OpERAFlow
from device import *
from reception.sensing import EnergyDetectorC
from reception.sensing import WaveformDetector 
from reception.architecture import FeedbackTopBlock, FeedbackF
from algorithm.decision import BayesLearningThreshold, WaveformDecision
from algorithm import KunstTimeFeedback, FeedbackAlgorithm
from gr_blcoks import *
from utils import Logger, TopBlock



def a_test(options, bayes_fft, feedback_algorithm):
	random.seed()

	uhd_source = UHDSource()
	uhd_source.samp_rate = 1e6
	uhd_source.gain = 1
	device_source = RadioDevice( the_source = uhd_source, the_sink = blocks.probe_signal_f() )

	# Bayes learning parameters
	delta_th = 0.001 
	min_th   = 0
	max_th   = 10
	in_th    = 0
	k        = 1

	# Feeback architecture
	bl_algo = BayesLearningThreshold( in_th = in_th,
			min_th = min_th,
			max_th = max_th,
			delta_th = delta_th,
			k = k)
	ev = WaveformDetector(bayes_fft, WaveformDecision(0.4) )

	bd_detector = EnergyDetectorC(bayes_fft, 10, bl_algo)

	tb = FeedbackTopBlock(device = OpERAFlow(device = device_source, algorithm = None),
			block_manager =  ev,
			block_learner = bd_detector,
			feedback_algorithm = FeedbackAlgorithm( bl_algo, feedback_algorithm )
		)
	tb.rx.center_freq = options.freq

	tb.start()

	count = 0
	Logger._ch_status = 0

	time.sleep(options.duration + 2) 
	tb.stop()
	tb.wait()


def transmitter_loop(options):

	uhd_sink = UHDSink(device_addr = options.args)
	uhd_sink.samp_rate = options.samp_rate
	device_sink = RadioDevice(
			the_source = blocks.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True),
			the_sink = uhd_sink, uhd_device = uhd_sink
		)

	tx_path = simple_tx()

	tb = OpERAFlow("tx")
	tb.add_path(abstract_arch = tx_path, radio_device = device_sink, name_of_arch = "device_sink")
	tb.start()

	start_t = time.time()
	while time.time() < (options.duration + start_t):
		r = random.random()
		t = 3 / exp(r)
		time.sleep(t)
		tb.tx.center_freq = options.freq
		Logger._ch_status = 1

		r = random.random()
		t = 2 / exp(r)
		time.sleep(t)
		tb.tx.center_freq = 843e6
		Logger._ch_status = 0

	tb.stop()
	tb.wait()


def main( options ):
	if not options.interferer:
		##
		directory = './dump'
		subdir = '/fft_{fft}_algo_{algo}'

		## Test Setups
		bayes_fft = [1024]
		feedback_algo = [ ('KunstTimeFeedback()', 'kunst'), ]

		max_it = 1

		for bfft in bayes_fft:
			for algo in feedback_algo:
				for i in xrange(max_it):
					sdir = subdir.format(fft=bfft, algo=algo[1])
					print sdir + '_it_', str(i)

					a_test(options, bfft, eval(algo[0]))

					if options.log:
						Logger.dump(directory, sdir, i)
						Logger.dump_plot(directory, sdir,
								[('bayes_learning',
									['real_state', 'feedback', 'hiphotesis', 'threshold']),
								 ('bayes_analyzer', ['energy'])],
								i)
						Logger.clear_all()
	else:
		transmitter_loop(options)


if __name__ == '__main__':
	parser=OptionParser(option_class=eng_option)
	parser.add_option("-a", "--args", type="string", default="''",
			help="UHD device address args [default=%default]")
	parser.add_option("-f", "--freq", type="eng_float", default=199.25e6,
			help="set frequency to FREQ", metavar="FREQ")
	parser.add_option("-g", "--gain", type="eng_float", default=None,
			help="set gain in dB (default is midpoint)")
	parser.add_option("", "--samp-rate", type="eng_float", default=195312,
			help="set device sample rate")
	parser.add_option("", "--interferer", action="store_true", default=False,
			help="set as interferer")
	parser.add_option("", "--duration", type="float", default='10',
			help="Execution time. Finishes both UP and US. (master device only)")
	parser.add_option("", "--log", action="store_true", default=False,
			help="Enable Logging")

	(options, args) = parser.parse_args()

	if options.log:
		Logger._enable = True
	main( options )
