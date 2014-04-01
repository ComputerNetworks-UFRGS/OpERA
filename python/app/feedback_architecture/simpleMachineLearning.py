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
import time

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)

from gnuradio import gr
from gnuradio import blocks
from gnuradio.eng_option import eng_option
from optparse  import OptionParser

# Project imports
from OpERAFlow import OpERAFlow
from device import *
from sensing import EnergySSArch, EnergyDetectorC, WaveformDetectorC, FeedbackSSArch
from sensing import EnergyDecision, BayesLearningThreshold, WaveformDecision
from algorithm import KunstTimeFeedback, FeedbackAlgorithm
from utils import Logger

# ::TODO:: documentation of the functions, with function explanation and param definitions.
def a_test(options, bayes_fft, feedback_algorithm):
    """

    @param options
    @param bayes_fft
    @param feedback_algorithm
    """

    random.seed()

    # Bayes learning parameters
    delta_th = 0.001 
    min_th = 0
    max_th = 10
    in_th = 0
    k = 1

    # Learning Algorithm for the Feedback
    bl_algo = BayesLearningThreshold(in_th=in_th,
                                     min_th=min_th,
                                     max_th=max_th,
                                     delta_th=delta_th,
                                     k=k)

    # Two sensing techniques for the Feedback
    ev = WaveformDetectorC(bayes_fft, WaveformDecision(0.4))
    bd_detector = EnergyDetectorC(bayes_fft, 10, bl_algo)

    # Feedback architecture
    ss_path = FeedbackSSArch(block_manager=ev,
                             block_learner=bd_detector,
                             feedback_algorithm=FeedbackAlgorithm(bl_algo, feedback_algorithm))

    # Radio device
    source = UHDSource()
    sink = blocks.probe_signal_f()

    radio_device = RadioDevice()
    radio_device.add_arch(source=source, arch=ss_path, sink=sink, uhd_device=source, name='ss')

    #
    tb = OpERAFlow('OperaFlow')
    tb.add_radio(radio_device, 'ss')

    tb.ss.set_center_freq(options.freq)

    Logger.add_to_print_list('waveform_decision', 'correlation')
    tb.start()

    count = 0
    Logger._ch_status = 0
    time.sleep(options.duration + 2) 
    tb.stop()
    tb.wait()


def ideal(options):
    """
    Makes the detection using the Energy Detector (ED), with a perfect threshold.
    @param options
    """
    source = blocks.file_source(gr.sizeof_gr_complex, options.file, False)
    sink = blocks.probe_signal_f()
    arch = EnergySSArch(fft_size=512, mavg_size=1, algorithm=EnergyDecision(0.00001))

    radio_device = RadioDevice()
    radio_device.add_arch(source=source, arch=arch, sink=sink, name='ss', uhd_device=None)

    # top
    tb = OpERAFlow('Ideal Flow')
    tb.add_radio(radio_device, 'ss')
    Logger.add_to_print_list('energy_decision', 'energy')

    tb.start()
    tb.wait()

    Logger.dump('dump', '/algo_ideal', 0)
    Logger.dump_plot('dump', '/algo_ideal',
                     [('energy_decision', ['energy', 'decision']), ],
                     0)
    Logger.clear_all()


def dump_file(options):
    """

    @param options
    """

    ## RX PATH
    source = UHDSource( device_addr=options.args)
    sink = blocks.file_sink(gr.sizeof_gr_complex, 'dump.bin')
    radio = RadioDevice()
    radio.add_arch(source=source, arch=None, sink=sink, name='ss', uhd_device=source)

    radio.set_center_freq(options.freq)
    radio.set_gain(10)

    ## OPERA FLOW
    tb = OpERAFlow("TopBlock")
    tb.add_radio(radio, 'ss')
    tb.start()

    start_t = time.time()
    while time.time() < (options.duration + start_t):
        t = random.expovariate(1/2.0)
        time.sleep(t)

        radio.set_center_freq(options.freq)
        Logger._ch_status = 1

        t = random.expovariate(1/5.0)
        time.sleep(t)
        radio.set_center_freq(843e6)
        Logger._ch_status = 0

    tb.stop()
    tb.wait()


def main(options):
    """
    Main function.
    @param options
    """
    if not options.gen_file:
        ##
        directory = './dump'
        subdir = '/fft_{fft}_algo_{algo}'

        ## Test Setups
        bayes_fft = [1024]
        feedback_algo = [('KunstTimeFeedback()', 'kunst'), ]

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
                                    ['real_state', 'feedback', 'hypothesis', 'threshold']),
                                 ('bayes_analyzer', ['energy'])],
                                i)
                        Logger.clear_all()
    else:
        dump_file(options)


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option)
    parser.add_option("-a", "--args", type="string", default="''",
                      help="UHD device address args [default=%default]")
    parser.add_option("-f", "--freq", type="eng_float", default=205.25e6,
                      help="set frequency to FREQ", metavar="FREQ")
    parser.add_option("-g", "--gain", type="eng_float", default=None,
                      help="set gain in dB (default is midpoint)")
    parser.add_option("", "--samp-rate", type="eng_float", default=195312,
                      help="set device sample rate")
    parser.add_option("", "--gen-file", action="store_true", default=False,
                      help="Generate dump file")
    parser.add_option("", "--duration", type="float", default='10',
                      help="Execution time. Finishes both UP and US. (master device only)")
    parser.add_option("", "--log", action="store_true", default=False,
                      help="Enable Logging")
    parser.add_option("", "--ideal", action="store_true", default=False,
                      help="Execute with Ideal Energy Detector")
    parser.add_option("", "--file", type="string", default="dump.bin",
                      help="Dump file. Read when using --ideal, save when using --gen-file.")
    (options, args) = parser.parse_args()

    if not options.ideal:
        if options.log:
            Logger._enable = True
        main(options)
    else:
        Logger._enable = True
        ideal(options)
