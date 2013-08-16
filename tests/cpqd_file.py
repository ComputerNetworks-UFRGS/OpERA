#!/usr/bin/env python

## @package device

# ::TODO:: Discover how to include patches externally
import sys, os, random

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)



from gnuradio import gr
from gnuradio.eng_option import eng_option
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from math      import *
from optparse  import OptionParser

# Project imports
from device.uhd       import *
from ssf.uhd.detectors.energy      import energy_detector_c
from ssf.uhd.detectors.waveform    import waveform_detector 
from ssf.uhd.block_util            import *
from ssf.uhd.architecture.feedback import FeedbackTopBlock, feedback_f
from ssf.algorithm    import BayesLearningThreshold, WaveformAlgorithm, FeedbackAlgorithm
from ssf.algorithm    import KunstTimeFeedback
from ssf.uhd.uhd_wrapper import UHDWrapper
from ss_utils        import Logger, TopBlock


def aTest(options, bayes_fft, feedback_algorithm):
	random.seed()

	uhd_source = gr.file_source(gr.sizeof_gr_complex, options.file, False)
	device_source = UHDDevice( the_source = uhd_source, the_sink = gr.probe_signal_f() )

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
	ev = waveform_detector(bayes_fft, WaveformAlgorithm(0.4) )

	bd_detector = energy_detector_c(bayes_fft, 10, bl_algo)

	tb = FeedbackTopBlock(device = UHDWrapper(device = device_source, algorithm = None),
			block_manager =  ev,
			block_learner = bd_detector,
			feedback_algorithm = FeedbackAlgorithm( bl_algo, feedback_algorithm )
		)

	tb.start()

	count = 0
	Logger._ch_status = 0

	tb.wait()

def main( options ):
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

				aTest(options, bfft, eval(algo[0]))

				Logger.dump(directory, sdir, i)
				Logger.dump_plot(directory, sdir,
						[('bayes_learning',
							['real_state', 'feedback', 'hiphotesis', 'threshold']),
						 ('bayes_analyzer', ['energy'])],
						i)
				Logger.clear_all()


if __name__ == '__main__':
	parser=OptionParser(option_class=eng_option)
	parser.add_option("-g", "--gain", type="eng_float", default=None,
			help="set gain in dB (default is midpoint)")
	parser.add_option("", "--samp-rate", type="eng_float", default=195312,
			help="set device sample rate")
	parser.add_option("", "--log", action="store_true", default=False,
			help="Enable Logging")
	parser.add_option("-f", "--file", type="string", default= "",
			help="Signal file to read.")

	(options, args) = parser.parse_args()

	if options.log:
		Logger._enable = True
	main( options )
