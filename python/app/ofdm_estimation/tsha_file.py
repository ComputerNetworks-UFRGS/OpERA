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
import threading
import collections
import matplotlib.pyplot as plt

import numpy as np
import scipy
import scipy.stats as sc
import scipy.signal as signal
from abc import ABCMeta, abstractmethod

#Project imports:

from OpERAFlow       import OpERAFlow
from sensing         import EnergyDecision
from sensing         import EnergySSArch
from device          import RadioDevice

from channels        import AWGNChannel
from gr_blocks.utils import UHDSourceDummy
from utils import Logger

# OFDM CONFIGURATION USED
THE_TUPLE      = [1024, 108]
MAX_AVG_SUMMED = 15
MAX_PARSED_SAMPLES = 200e3

def mean_confidence_interval(data, confidence=0.40):
    """
    @param data
    @param confidence
    """
    a = np.array(data)  #pylint: disable=E1101
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)  #pylint: disable=E1101

    #ATENTCAO: MUDAR DISTRIBUICAO
    h = se * scipy.stats.t._ppf((1+confidence)/2., n-1)  #pylint: disable=E1101
    return m, h

def sum_bulk(x, use = MAX_AVG_SUMMED):
    y = np.zeros( len(x[-1]) )

    use = min(MAX_AVG_SUMMED, len(x))

    for i in range(-use, 0):
        y += x[i]

    y /= min(MAX_AVG_SUMMED, len(x))
    return y

def calculate_avg_std(bulk):
    y = sum_bulk(bulk)
    idx = np.argmax(y)

    use = min(MAX_AVG_SUMMED, len(bulk))

    s = []
    for i in range(-use, 0):
        s.append(bulk[i][idx])

    m, h = mean_confidence_interval(s)

    return m, h


class Correlator(gr.sync_block):

    def __init__(self):
        gr.sync_block.__init__(self,
                name="correlator",
                in_sig= [np.dtype((np.float32, 1024)), np.dtype((np.float32, 1024))],#pylint: disable=E1101
                out_sig= None,                                                       #pylint: disable=E1101
        )

        self.LOGGER = {
                # tupe         logger_str, selected
                (128  ,    9):["128_9"   ,         0],
                (128  ,   32):["128_32"  ,         0],
                (256  ,   18):["256_18"  ,         0],
                (256  ,   64):["256_64"  ,         0],
                (512  ,   36):["512_36"  ,         0],
                (512  ,  128):["512_128" ,         0],
                (1024 ,  108):["1024_108",         0],
                (1024 ,  256):["1024_256",         0],
                (2048 ,  144):["2048_144",         0],
                (2048 ,  512):["2048_512",         0],
                "sel_total"  : 0,
                "sel_hit"    : 0,
                "sel_error"  : 0
        }

        self.from_file = (
                (128  ,    9),
                (128  ,   32),
                (256  ,   18),
                (256  ,   64),
                (512  ,   36),
                (512  ,  128),
                (1024 ,  108),
                (1024 ,  256),
                (2048 ,  144),
                (2048 ,  512)
               )

        # correlation coefficients
        self.corr_coeffs = {}
        self.bulk_corr    = {}
        self.plt_id      = {}
        for tup in self.PAIRS:
            self.corr_coeffs[tup] = np.array([])
            self.bulk_corr[tup]    = []

            def fig(x):
                def k():
                    plt.figure(x)
                return k
            self.plt_id[tup]      = fig(tup[0]+tup[1])


        # maximum number of signal samples keep in buffer
        self.bin_length = (2048 + 512) * 2
        #  array of samples
        self.samples = collections.deque()
        # array with all signal samples. used to dump results
        self.signal_dump = []


        self.total_parsed = 0
        self.enable = True


    def dump(self, options):
        for tup, blk in self.bulk_corr.items():
            fft_length = tup[0]
            cp_length  = tup[1]

            blk_sum = sum_bulk( blk )
            m, e = calculate_avg_std(blk)
            with open("cor_stats.txt", "a+") as fd:
                fd.write("FFT:%d\t\tCP:%d\t\tAVG:%f\t\tE:%f\t\tCV:%f\n" %(fft_length, cp_length, m, e, e/m))

                self.plt_id[tup]()
                for d in blk:
                    plt.plot(d)
                plt.savefig('./plot/plot_%d_%d_%d_%d.pdf' % (fft_length, cp_length, options.ebn0, options.it))

                plt.figure()
                plt.plot(blk_sum)
                plt.savefig('./plot/plot_%d_%d_%d_%d_sum.pdf' % (fft_length, cp_length, options.ebn0, options.it))



    def push_sample(self, item):
        self.samples.appendleft( item )

        # remove first sample if bin_length was achieved
        if len(self.samples) > self.bin_length:
            self.samples.pop()


    def push_corr_coeff(self, tup, corr):
        """
        Append correlation 
        @param tup Tupe (FFT, CP) 
        @param corr Correlation
        """

        fft_length = tup[0]
        cp_length  = tup[1]
        t_len = fft_length + cp_length

        self.corr_coeffs[tup] = np.append(self.corr_coeffs[tup], corr )
        corr_block = self.corr_coeffs[tup]

        if len(corr_block) == t_len:
            self.bulk_corr[tup].append( np.array(corr_block) )
            self.corr_coeffs[tup] = []



    def correlate(self):
        def correlate_cp(prefix1, prefix2):
            #mse = np.mean( np.square(np.array(prefix1) - np.array(prefix2)))
            #return 1.0/mse
            return sc.pearsonr(prefix1, prefix2)[0]

        samples = list(self.samples)
        for tup, d in self.corr_coeffs.items():
            fft_length = tup[0]
            cp_length  = tup[1]

            # get CP samples
            prefix = samples[0:cp_length]
            # correlate CP  end of FFT symbol if possible
            if len(samples) >= fft_length + cp_length:
                c = correlate_cp(prefix, samples[fft_length:fft_length+cp_length])
            else:
                c = 0

            self.push_corr_coeff( tup, c )

    def select_ofdm_params(self):

        parsed = {}
        # parse, calculate mean and avg
        for tup, blk in self.bulk_corr.items():
            fft_length = tup[0]
            cp_length  = tup[1]

            if blk:
                m, e = calculate_avg_std( blk )
                parsed[ tup ] = (m, e, m/e)

        ofdm_tup = None
        max_sum = float("-inf")
        for tup, data in parsed.iteritems():
            if data[0] > max_sum:
                ofdm_tup = tup
                max_sum = data[0]

        if ofdm_tup:
            self.LOGGER[ofdm_tup][1] += 1.0
            Logger.set("correlator", "sel_" + self.LOGGER[ofdm_tup][0], self.LOGGER[ofdm_tup][1])

            self.LOGGER["sel_total"]   += 1.0
            if ofdm_tup == THE_TUPLE:
                self.LOGGER["sel_hit"]   += 1.0
            else:
                self.LOGGER["sel_error"] += 1.0

            Logger.set("correlator", "sel_hit"  , self.LOGGER["sel_hit"])
            Logger.set("correlator", "sel_error", self.LOGGER["sel_error"])
            Logger.set("correlator", "sel_total", self.LOGGER["sel_total"])


    def work(self, input_items, output_items):

        for idx in range(len(input_items[0])):

            # Disable parsed when finished
            in0 = input_items[0][idx]
            in1 = input_items[1][idx]
            for i in range(len(in0)):

                self.total_parsed += 1
                if self.total_parsed >= MAX_PARSED_SAMPLES:
                    self.enable = False
                if not self.enable:
                    return  len(input_items[0])

                #if in1[i] == 1:
                self.push_sample(in0[i])
                self.correlate()
                self.select_ofdm_params()

        return  len(input_items[0])


def load_file(options):

    blocks = {}

    for tup in Correlator().PAIRS():
        with open("./correlations/%d_%d_%d_%d_%d_%d.gz" %
           (options.fft_length,
            options.cp_length,
            options.ebn0,
            options.it,
            tup[0],
            tup[1]),
           "r") as fd:
            blocks[tup] = yaml.load(fd)

    return blocks


def parse_file(options):

    blocks = load_file(options)

    correlator = Correlator()

    next_block = {}
    for tup in correlator.PAIRS:
        next_block[tup] = blocks[tup][0][0]

    for i in range(MAX_PARSED_SAMPLES):

        for tup in correlator.PAIRS:
            if i == next_block[tup]:
                the_block = blocks[tup][1]

                blocks[tup].pop(0)
                next_block[tup] = blocks[tup][0][0]


                correlator.bulk_corr[tup].append( the_block  )


        correlator.select_ofdm_params()

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("", "--ebn0", type="float", default=5)
    parser.add_option("", "--fft-length", type="int", default=1024)
    parser.add_option("", "--cp-length", type="int", default=108)
    parser.add_option("", "--it", type="int", default=1)
    parser.add_option("", "--max-parsed", type="int", default=50e3)

    (options, args) = parser.parse_args()

    THE_TUPLE =  (options.fft_length, options.cp_length)
    MAX_PARSED_SAMPLES = options.max_parsed

    import yaml
    noise = yaml.load(open("noise.txt", "r"))
    options.threshold = noise[options.ebn0][0.9]

    Logger._enable = True
    print "#### TESTING WITH EBN0 %f, IT %d" % (options.ebn0, options.it)

    tin = time.clock()
    tb.start()


    parse_file(options)

    #Save correlation to a file
    tfin = time.clock()
    Logger.set('global', 'clock', tfin - tin)

    Logger._enable = False
    tb.stop()
    tb.wait()
    print "### STOPPED"

    d =  "from_file/ebn0_%d/" % options.ebn0
    sd =  "%d_%d" % (options.fft_length, options.cp_length)
    Logger.dump(d, sd, options.it)
    radio.estimator.dump(options)
