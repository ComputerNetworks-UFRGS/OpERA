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

## @package reception

from gnuradio import gr      #pylint: disable = F0401
from gnuradio import fft     #pylint: disable = F0401
from gnuradio import blocks  #pylint: disable = F0401

import numpy as np
import time

from device import UHDSSArch   #pylint: disable=F0401
from utils import Logger       #pylint: disable=F0401


#::TODO:: descricao das classes, metodos e seus parametros
#class WaveformDetectorC2(gr.hier_block2):
#    """
#
#    """
#
#    #::TODO:: tem um parametro a mais na doc.
#    def __init__(self, fft_size):
#        """
#        CTOR
#        @param fft_size FFT size (output of FFT is passed to the algorithm object).
#
#        OLD
#        @param algorithm Waveform Algorithm. An AbstractAlgorithm implementation.
#        """
#        gr.hier_block2.__init__(self,
#                                name="waveform detector",
#                                input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
#                                output_signature=gr.io_signature(1, 1, gr.sizeof_float * 1024)
#                                )
#
#        s2v_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size)
#        fft_0 = fft.fft_vcc(fft_size, True, [])
#        c2mag_0 = blocks.complex_to_mag_squared(fft_size)
#        log10 = blocks.nlog10_ff(1, 1024, 0)
#
#        self.connect(self, s2v_0, fft_0, c2mag_0, log10, self)  #pylint: disable=E1101
#
#
#class WaveformSSArch2(UHDSSArch):
#    """
#    Architecture to perform Waveform sensing.
#    """
#
#    #::TODO:: doc tem um parametro a mais (algorithm)
#    def __init__(self,  fft_size):
#        """
#        CTOR.
#        @param fft_size FFT Size. WARNING: must be of the size of the pattern used by the WaveformDecision algorithm.
#
#        OLD
#        @param algorithm A ThresholdAlgorithm. 
#        """
#
#        self._detector = WaveformDetectorC2(fft_size=fft_size)
#
#        # ::TRICKY:: Calls abstract _build method
#        UHDSSArch.__init__(self,
#                           name="WaveformSSArch2",
#                           input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
#                           output_signature=gr.io_signature(1, 1, gr.sizeof_float * 1024),
#                           )
#
#    #::TODO:: parametros nao usados
#    def _build(self, input_signature, output_signature):
#        """
#        Implementation of base abstract method.
#        @param input_signature
#        @param output_signature
#        @return The detector.
#        """
#        return self._detector
#
#    #::TODO:: parametros nao usados
#    def _get_sensing_data(self, the_channel, sensing_time):
#        """
#        Implementation of the base class abstract method.
#        @param the_channel
#        @param sensing_time
#        @return Return a tuple (decision, correlation)
#        """
#        time.sleep(sensing_time)
#        return self.output()
#
#
#    def output(self):
#        """
#        Implementation of the base class abstract method.
#        @return Return tuple (decision, correlation)
#        """
#        return self._detector._wa.output()


class WaveformDetector(gr.sync_block):
    """
    Waveform analyzer.
    Receives a waveform and output if a match occurs.
    """

    def __init__(self, vec_size, algorithm):
        """
        CTOR.
        @param vec_size Size of each input.
        @param algorithm Waveform detection algorithm.
        """
        gr.sync_block.__init__(self,
		name="WaveformDetector",
		in_sig=[np.dtype((np.float32, vec_size))], #pylint: disable=E1101
		out_sig=None                               #pylint: disable=E1101
	)

        self._algorithm = algorithm
        self._corr = 0
        self._dec = 0

    def work(self, input_items, output_items):
        """
        Process inputs.
        @param input_items Input array with float values.
        @param output_items Energy calculated.
        @return
        """
        for idx in range(len(input_items[0])):
            self._dec, self._corr = self._algorithm.decision(input_items[0][idx])

        return len(input_items[0])

    def output(self):
        """
        Return the most recent calculated correlation.
        @return Most recent correlation.
        """
        return (self._dec, self._corr)


class WaveformDetectorGambi(gr.hier_block2):
    """
    Top level of waveform detector.
    Construct the flow graph for a waveform detector from the source to the detection algorithm.
    The flow graph is resumed as follows: source -> [ s2v -> fft -> c2mag**2 ->  waveform analyser] -> sync.
    """

    def __init__(self, fft_size):
        """
        CTOR
        @param fft_size FFT size (output of FFT is passed to the algorithm object).
        @param algorithm Waveform Algorithm. An AbstractAlgorithm implementation.
        """

        gr.hier_block2.__init__(self,
                                name="waveform detector",
                                input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                                output_signature=gr.io_signature(1, 1, gr.sizeof_float * fft_size)
                                )

        s2v_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size)
        fft_0 = fft.fft_vcc(fft_size, True, [])
        c2mag_0 = blocks.complex_to_mag_squared(fft_size)

        self.connect(self, s2v_0, fft_0, c2mag_0,  self)  #pylint: disable=E1101


class WaveformSSArch(UHDSSArch):
    """
    Architecture to perform Waveform sensing.
    """

    def __init__(self,  fft_size):
        """
        CTOR.
        @param fft_size FFT Size. WARNING: must be of the size of the pattern used by the WaveformDecision algorithm.
        @param algorithm A ThresholdAlgorithm. 
        """

        self._detector = WaveformDetectorGambi(fft_size=fft_size)

        # ::TRICKY:: Calls abstract _build method
        UHDSSArch.__init__(self,
                           name="WaveformSSArch",
                           input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                           output_signature=gr.io_signature(1, 1, gr.sizeof_float*fft_size),
                           )

    #::TODO:: parametros nao usados
    def _build(self, input_signature, output_signature):
        """
        Implementation of base abstract method.
        @param input_signature
        @param output_signature
        """
        return self._detector

    #::TODO:: parametros nao usados
    def _get_sensing_data(self, the_channel, sensing_time):
        """
        Implementation of the base class abstract method.
        @param the_channel
        @param sensing_time
        @return Return a tuple (decision, correlation)
        """
        time.sleep( sensing_time )
        return self.output()


    def output(self):
        """
        Implementation of the base class abstract method.
        @return Return tuple (decision, correlation)
        """
	raise NotImplemented
        return self._detector._wa.output()
