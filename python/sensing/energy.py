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

## @file energyDetector.py

## @package ssf
#  Module with algorithms to sense a spectrum

from gnuradio import blocks, gr #pylint: disable = F0401
from gnuradio import fft        #pylint: disable = F0401
from gnuradio import gr         #pylint: disable = F0401

from device import UHDSSArch #pylint: disable=F0401
from utils  import Logger    #pylint: disable=F0401

import time
import numpy as np

class EnergyDetector(gr.sync_block):
    """
    Sink Block
    """

    def __init__(self, vec_size, algorithm, name="energy_calculator"):
        """
        CTOR
        @param vec_size Input array size.
        @param algorithm A ThresholdAlgorithm instance.
        @param name Block name.
        """
        gr.sync_block.__init__(self,
                name=name,
                in_sig = [np.dtype((np.float32, vec_size))],  #pylint: disable=E1101
                out_sig= None   #pylint: disable=E1101
        )

        self._algorithm = algorithm

        self._energy = 0
        self._decision = 0

        if not self._algorithm:
            raise AttributeError("Algorithm must be an ThresholdLearningAlgorithm")


    def work(self, input_items, output_items):
        """
        Calculate the energy.
        @param input_items Input array with float values.
        @param output_items Energy calculated.
        @return
        """
        for idx in range(len(input_items[0])):
            self._decision, self._energy = self._algorithm.decision(input_items[0][idx])

        return len(input_items[0])


    def output(self):
        """
        ::WARNING:: This method is called by the EnergySSArch.
        @return Return a tuple (decision, energy).
        """
        return (self._decision, self._energy)


class EnergyDetectorGambi(gr.hier_block2):
    """
    Top level of Energy Detector sensing algorithm.
    A object of this class must be declared and connected in a flow blocksaph.
    The inputs are:
       in0    :    A vector of floats with len fft_size
    """

    def __init__(self, fft_size, mavg_size, name="EnergyDetectorC"):
        """
        CTOR
        @param fft_size FFT Size.
        """

        gr.hier_block2.__init__(self,
                name=name,
                input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                output_signature=gr.io_signature(1, 1, gr.sizeof_float*fft_size),
         )

        # Blocks
        # Convert the output of a FFT
        s2v_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size)
        fft_0 = fft.fft_vcc(fft_size, True, [])
        c2mag_0 = blocks.complex_to_mag_squared(fft_size)

        ## Flow graph
        self.connect(self, s2v_0, fft_0, c2mag_0, self)  #pylint: disable=E1101
        #self.connect(self, s2v_0, fft_0, self)  #pylint: disable=E1101


class EnergySSArch(UHDSSArch):
    """
    Architecture for performing energy detection
    """

    def __init__(self, fft_size, mavg_size):
        """
        CTOR
        @param fft_size FFT Size.
        @param mavg_size Moving average array size.
        @param algorithm A ThresholdAlgorithm instance.
        """

        self._detector = EnergyDetectorGambi(
                fft_size = fft_size,
                mavg_size = mavg_size,
        )

        # ::TRICKY:: Calls abstract _build method
        UHDSSArch.__init__(self,
                           name="EnergySSArch",
                           input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                           output_signature=gr.io_signature(1, 1, gr.sizeof_float * 1024),
                           )


    #>>TODO:: parametrosd nao usados
    def _build(self, input_signature, output_signature):
        """
        Implementation of base abstract method.
        @param input_signature The input signature.
        @param output_signature The output signature.
        @return Return the detector.
        """
        return self._detector


    def _get_sensing_data(self, the_channel, sensing_time):
        """
        Implementation of the base class abstract method.
        @param the_channel
        @param sensing_time
        @return Return the energy of the the channel
        """
        # Sleep for sensing_time
        time.sleep(sensing_time)
        return self.output()

    def output(self):
        """
        Implementation of the base class abstract method.
        @return Return tuple (decision, energy)
        """
	raise NotImplemented
        return self._detector._ec.output()
