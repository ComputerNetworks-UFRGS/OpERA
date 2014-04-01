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
import time
import collections
import yaml

import numpy as np
import scipy
import scipy.stats as sc

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
MAX_AVG_SUMMED = 15
SKIP = 50e3
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
    y   = sum_bulk(bulk)
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

        self.PAIRS = (THE_TUPLE ,)

        # correlation coefficients
        self.corr_coeffs = {}
        self.bulk_corr   = {}
        for tup in self.PAIRS:
            self.corr_coeffs[tup]  = np.array([])
            self.bulk_corr[tup]    = []


        # maximum number of signal samples keep in buffer
        self.bin_length = (2048 + 512) * 2
        #  array of samples
        self.samples = collections.deque()
        # array with all signal samples. used to dump results
        self.signal_dump = []


        self.total_parsed = 0
        self.enable = True

        self.all_parsed_corrs = []
        self.all_bulks        = []


    def dump(self, options):
        for tup, blk in self.bulk_corr.items():
            print "##### Saving ", tup
            with open("./correlations/%d_%d_%s_%s_%d.gz" % (options.fft_length, options.cp_length, options.att, options.fad, options.it), "w+") as fd:
                fd.write(yaml.dump(self.all_bulks))


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

        self.corr_coeffs[tup] = np.append(self.corr_coeffs[tup], corr)
        corr_block            = self.corr_coeffs[tup]

        if len(corr_block) == t_len:
            self.bulk_corr[tup].append(np.array(corr_block))
            self.corr_coeffs[tup] = []

            if tup == THE_TUPLE:
                self.all_bulks.append([self.total_parsed, np.array(corr_block)]  )


    def correlate(self):
        def correlate_cp(prefix1, prefix2):
            #mse = np.mean( np.square(np.array(prefix1) - np.array(prefix2)))
            #return 1.0/mse
            return sc.pearsonr(prefix1, prefix2)[0]

        samples = list(self.samples)
        for tup in self.PAIRS:
            fft_length = tup[0]
            cp_length  = tup[1]

            # get CP samples
            prefix = samples[0:cp_length]
            # correlate CP  end of FFT symbol if possible
            if len(samples) >= fft_length + cp_length:
                c = correlate_cp(prefix, samples[fft_length:fft_length+cp_length])
            else:
                c = 0

            self.push_corr_coeff(tup, c)

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

        self.all_parsed_corrs.append(parsed)


    def work(self, input_items, output_items):

        for idx in range(len(input_items[0])):
            # Disable parsed when finished
            in0 = input_items[0][idx]
            in1 = input_items[1][idx]
            for i in range(len(in0)):

                self.total_parsed += 1
                if self.total_parsed > SKIP:
                    if self.total_parsed >= (MAX_PARSED_SAMPLES + SKIP):
                        print "##### Finished Parsing File"
                        self.enable = False
                    if not self.enable:
                        return  len(input_items[0])

                    #if in1[i] == 1:
                    self.push_sample(in0[i])
                    self.correlate()
                    #self.select_ofdm_params()

        return  len(input_items[0])


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


        the_source = blocks.file_source(gr.sizeof_gr_complex, options.file, False)
        radio = RadioDevice(name="radio")

        det = Correlator()
        middle = gr.hier_block2(
                name='hier',
                input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
                output_signature = gr.io_signature(1, 1, gr.sizeof_float * 1024),
        )
        middle.connect(middle, blocks.stream_to_vector(gr.sizeof_gr_complex, 1024), blocks.complex_to_mag(1024), middle)
        ed = EnergySSArch(1024, 1, EnergyDecision(th = options.threshold))

        radio.add_arch(source = the_source, arch = middle, sink =(det,0), uhd_device=the_source, name='estimator')
        radio.add_arch(source = the_source, arch = ed,     sink =(det,1), uhd_device=the_source, name = "ed")
        tb.add_radio(radio, "radio")

        return tb, radio, det


if __name__ == "__main__":
    import tarfile
    tar_file =  tarfile.open("/media/video/realLTEsignal.tar.gz", "r")


    class T():
        pass
    options = T()

    FADINGS      = ["Rural", "Hilly", "TU"]
    ATTENUATIONS = ["Att20", "Att30", "Att40", "Att50", "Att 60", "Att65" ]

    CONVERT_FILES = {}
    for fad in FADINGS:
        CONVERT_FILES[fad] = {}
        for att in ATTENUATIONS:
            CONVERT_FILES[fad][att] = 0

    CONVERT_FILES["parsed"] = []

    try:
        with open("parsed_files_lte.log", "r") as fd:
            CONVERT_FILES = yaml.load(fd)
    except:
        pass

    for _f in tar_file.getmembers():
            if not _f in CONVERT_FILES["parsed"]:

                fad = None
                att = None
                for i, x in enumerate(FADINGS):
                    if x in _f.name:
                        fad = x
                for i, x in enumerate(ATTENUATIONS):
                    if x in _f.name:
                        att = x

                if not (att == None or fad == None) and CONVERT_FILES[fad][att] < 4:
                    print "##### Extracting: ", _f.name
                    tar_file.extract(_f.name)
                    options.file = _f.name

                    for tup in Correlator().ALL_PAIRS:
                        THE_TUPLE =  (tup[0], tup[1])

                        options.att = att
                        options.fad = fad
                        options.it = CONVERT_FILES[fad][att]
                        options.threshold = 100
                        options.fft_length  = THE_TUPLE[0]
                        options.cp_length   = THE_TUPLE[1]

                        log = "#### FILE: %s - Att %s, Fading: %s -- CORR FFT %d CP %d [%d]" % (options.file, att, fad, THE_TUPLE[0], THE_TUPLE[1], options.it)
                        print log

                        tb, radio, correlator = OpERAUtils.device_definition(options)
                        Logger._enable = True

                        tin = time.clock()
                        tb.start()

                        try:
                            print "### STARTED"
                            while  correlator.enable:
                                print correlator.total_parsed
                                time.sleep(1)
                        except KeyboardInterrupt:
                            pass
                            #Save correlation to a file
                        tfin = time.clock()
                        Logger.set('global', 'clock', tfin - tin)

                        Logger._enable = False
                        tb.stop()
                        tb.wait()
                        print "### STOPPED"

                        radio.estimator.dump(options)

                    CONVERT_FILES[fad][att] += 1

                    with open("parsed_files_lte.log", "w+") as fd:
                        fd.write(yaml.dump(CONVERT_FILES))

                    import shutil
                    shutil.rmtree(att + "/")
