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
THE_TUPLE      = (1024, 108)
MAX_AVG_SUMMED = 5
MAX_PARSED_SAMPLES = int(50e3)

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
    use = min(MAX_AVG_SUMMED, len(x))

    if use < 2:
        return x

    y = np.zeros( len(x[-1]) )

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

    def __init__(self, threshold = None):
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

        self.ALL_PAIRS = (
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

        self.PAIRS = (
                (128  ,    9),
                #(128  ,   32),
                #(256  ,   18),
                #(256  ,   64),
                #(512  ,   36),
                #(512  ,  128),
                #(1024 ,  108),
                #(1024 ,  256),
                #(2048 ,  144),
                (2048 ,  512)
               )

        self.thresholds = threshold

        # correlation coefficients
        self.corr_coeffs  = {}
        self.bulk_corr    = {}
        self.plt_id       = {}
        for tup in self.ALL_PAIRS:
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
        for tup, blk in self.bulk_corr.items():
            if len(blk) < MAX_AVG_SUMMED:
                return

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


def load_file(options):

    blocks = {}

    for tup in Correlator().ALL_PAIRS:
        with open("./correlations/%d_%d_%d_%d_%d_%d_%s.gz" %
           (options.fft_length,
            options.cp_length,
            options.ebn0,
            options.it,
            tup[0],
            tup[1],
            options.type),
           "r") as fd:
            blocks[tup] = yaml.load(fd)

    return blocks


def parse_file(options):
    blocks = load_file(options)

    correlator = Correlator(options.threshold[options.ebn0])

    next_block = {}
    for i in range(MAX_PARSED_SAMPLES):
        for tup in correlator.ALL_PAIRS:

            if not len(blocks[tup]):
                continue

            next_block[tup] = blocks[tup][0][0]

            if i == next_block[tup]:
                the_block = blocks[tup][0][1]

                blocks[tup].pop(0)

                if blocks[tup]:
                    next_block[tup] = blocks[tup][0][0]
                else:
                    next_block[tup] = -1

                correlator.bulk_corr[tup].append( the_block )


        correlator.select_ofdm_params()



if __name__ == "__main__":
    class T():
        pass
    options = T()


    options.type = "hilly"

    for it in range(10):
        options.it = it
        for ebn0 in range(10):
            options.ebn0 = ebn0
            for tup in Correlator().PAIRS:
                THE_TUPLE =  (tup[0], tup[1])
                print "PARSING TUP: %s, EBN0: %d, IT: %d" % (str(tup), ebn0, it)

                options.fft_length = THE_TUPLE[0]
                options.cp_length  = THE_TUPLE[1]

                import yaml
                noise = yaml.load(open("noise.txt", "r"))
                corr = yaml.load(open("corr.txt", "r"))

                options.threshold = noise[options.ebn0][0.9]
                options.threshold = corr
                options.ebn0 = ebn0

                Logger._enable = True

                tin = time.clock()

                parse_file(options)

                #Save correlation to a file
                tfin = time.clock()
                Logger.set('global', 'clock', tfin - tin)
                Logger._enable = False

                print "### STOPPED"

                d =  "always_occupied_%s/ebn0_%d/" % (options.type, options.ebn0)
                sd =  "%d_%d" % (options.fft_length, options.cp_length)
                print "----- SAVING FILES"
                Logger.dump(d, sd, options.it)
