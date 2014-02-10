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

import time
import math
import numpy as np

from device import UHDSSArch #pylint: disable=F0401
from utils import Logger     #pylint: disable=F0401

class EnergyCalculator2(gr.sync_block):
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
        gr.sync_block.__init__(
                self,
                name = name,
                in_sig  = [np.dtype((np.float32, vec_size))],  #pylint: disable=E1101
                out_sig = [np.dtype((np.float32, vec_size))],  #pylint: disable=E1101
            )

        self._algorithm = algorithm

        self._energy   = 0
        self._decision = 0

        if not self._algorithm:
            raise AttributeError("Algorithm must be an ThresholdLearningAlgorithm")

    ## Calculate the energy
    # @param    input_items    Input array with float values
    # @param    output_items    Energy calculated
    def work(self, input_items, output_items):
        #in0  = input_items[0][0]
        #out0 = output_items[0]

        ## Process input
        #self._decision, self._energy = self._algorithm.decision( in0 )
        #out0[0] = np.array([self._decision] * 1024)

        #return 1024 

        for idx in range(len(input_items[0])):
            self._decision, self._energy = self._algorithm.decision( input_items[0][idx] )
            output_items[0][idx] = np.array([self._decision]) * 1024
        return len(input_items[0])


class EnergyDetectorC2(gr.hier_block2):

    def __init__(self, fft_size, mavg_size, algorithm, name = "EnergyDetectorC"):
        """
        CTOR
        @param fft_size FFT Size.
        @param mavg_size Moving average size.
        @param algorithm ThresholdAlgorithm instance.
        """

        gr.hier_block2.__init__(
                self,
                name = name,
                input_signature  =  gr.io_signature(1, 1, gr.sizeof_gr_complex),
                output_signature =  gr.io_signature(1, 1, gr.sizeof_float * 1024),
            )

        # Blocks
        # Convert the output of a FFT
        s2v_0   = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size)
        fft_0   = fft.fft_vcc(fft_size, True, [])
        c2mag_0 = blocks.complex_to_mag_squared(fft_size)

        ## Instatiate the energy calculator
        self._ec  = EnergyCalculator2(fft_size, algorithm)

        ## Flow graph
        self.connect(self, s2v_0, fft_0, c2mag_0, self._ec, self) #pylint: disable=E1101

class EnergySSArch2(UHDSSArch):
    """
    Architecture for performing energy detection
    """

    def __init__(self, fft_size, mavg_size, algorithm):
        """
        CTOR
        @param fft_size FFT Size.
        @param mavg_size Moving average array size.
        @param algorithm  A ThresholdAlgorithm instance.
        """

        self._detector = EnergyDetectorC2(
                fft_size  = fft_size,
                mavg_size = mavg_size,
                algorithm = algorithm
            )


        # ::TRICKY:: Calls abstract _build method
        UHDSSArch.__init__(
            self,
            name = "EnergySSArch",
            input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
            output_signature = gr.io_signature(1, 1, gr.sizeof_float * 1024),
        )


    def _build(self, input_signature, output_signature):
        """
        Implementation of base abstract method.
        """
        return self._detector


    def _get_sensing_data(self, the_channel, sensing_time):
        """
        Implementation of the base class abstract method.
        Return the energy of the the channel
        """
        # Sleep for sensing_time
        time.sleep(sensing_time)
        return self.output()

    def output(self):
        """
        Implementation of the base class abstract method.
        Return tuple (decision, energy)
        """
        return self._detector._ec.output()


class EnergyCalculator(gr.sync_block):
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
        gr.sync_block.__init__(
                self,
                name = name,
                in_sig = [np.dtype((np.float32, vec_size))],  #pylint: disable=E1101
                out_sig = [np.float32]                        #pylint: disable=E1101
            )

        self._algorithm = algorithm

        self._energy   = 0
        self._decision = 0

        if not self._algorithm:
            raise AttributeError("Algorithm must be an ThresholdLearningAlgorithm")

    ## Calculate the energy
    # @param    input_items    Input array with float values
    # @param    output_items    Energy calculated
    def work(self, input_items, output_items):
        in0  = input_items[0][0]
        out0 = output_items[0]

        # Process input
        self._decision, self._energy = self._algorithm.decision(in0)
        out0[0] = self._decision

        return len(input_items)


    def output(self):
        """
        Return a tuple (decision, energy)
        ::WARNING:: This method is called by the EnergySSArch.
        """
        return (self._decision, self._energy)

## Top level of Energy Detector sensing algorithm
# A object of this class must be declared and connected in a flow blocksaph.
# The inputs are:
#     in0    :    A vector of floats with len fft_size
#     out0:    A single float that represents the energy calculated
class EnergyDetectorC(gr.hier_block2):

    def __init__(self, fft_size, mavg_size, algorithm, name = "EnergyDetectorC"):
        """
        CTOR
        @param fft_size FFT Size.
        @param mavg_size Moving average size.
        @param algorithm ThresholdAlgorithm instance.
        """

        gr.hier_block2.__init__(
                self,
                name = name,
                input_signature  =  gr.io_signature(1, 1, gr.sizeof_gr_complex),
                output_signature =  gr.io_signature(1, 1, gr.sizeof_float),
            )

        # Blocks
        # Convert the output of a FFT
        s2v_0   = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size)
        fft_0   = fft.fft_vcc(fft_size, True, [])
        c2mag_0 = blocks.complex_to_mag_squared(fft_size)

        ## Instatiate the energy calculator
        self._ec  = EnergyCalculator(fft_size, algorithm)

        ## Flow graph
        self.connect(self, s2v_0, fft_0, c2mag_0, self._ec, self) #pylint: disable=E1101


class EnergySSArch(UHDSSArch):
    """
    Architecture for performing energy detection
    """

    def __init__(self, fft_size, mavg_size, algorithm):
        """
        CTOR
        @param fft_size FFT Size.
        @param mavg_size Moving average array size.
        @param algorithm  A ThresholdAlgorithm instance.
        """

        self._detector = EnergyDetectorC(
                fft_size  = fft_size,
                mavg_size = mavg_size,
                algorithm = algorithm
            )


        # ::TRICKY:: Calls abstract _build method
        UHDSSArch.__init__(
            self,
            name = "EnergySSArch",
            input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
            output_signature = gr.io_signature(1, 1, gr.sizeof_float),
        )


    def _build(self, input_signature, output_signature):
        """
        Implementation of base abstract method.
        """
        return self._detector


    def _get_sensing_data(self, the_channel, sensing_time):
        """
        Implementation of the base class abstract method.
        Return the energy of the the channel
        """
        # Sleep for sensing_time
        time.sleep(sensing_time)
        return self.output()

    def output(self):
        """
        Implementation of the base class abstract method.
        Return tuple (decision, energy)
        """
        return self._detector._ec.output()
