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

## @package ssf

from gnuradio import gr
from gnuradio import fft
from gnuradio import blocks


# OpERA imports
from device import UHDSSArch
from sensing import *
from gr_blocks.utils import GroupInN

import time
import threading
import numpy as np


#::TODO:: descricao de metodos e seus parametros
class QLearningWorker(gr.sync_block):
    """
     QLearning worker block.
    Input: vector of vec_size elements.
    Output: (decision, energy), where:
      - decision: 1 or 0
      - energy  : energy calculated
    """

    def __init__(self, vec_size, algorithm):
        """
        CTOR
        @param vec_size Size of each input.
        @param algorithm Detection algorithm. An AbstractAlgorithm implementation.
        """

        # input: array of floats
        # output: a tuple of (energy, decision)
        gr.sync_block.__init__(self,
                               name="qlearning_worker",
                               in_sig = [np.dtype((np.float32, vec_size))],
                               out_sig= [np.float32, np.float32]
                               )
        self._algorithm = algorithm


    def work(self, input_items, output_items):
        """
        GNU Radio main function.
        @param input_items
        @param output_items
        @return
        """
        for idx in range(len(input_items[0])):
            output_items[1][idx], output_items[0][idx] = self._algorithm.decision( input_items[0][idx] )

        return len(output_items)


class SimpleRankingDetector(gr.hier_block2):
    """
    QLearning hierarchical block.
    Builds flow graph from source to sync.
    """

    def __init__(self, fft_size, mavg_size, ed_threshold):
        """
        CTOR
        @param fft_size FFT Size
        @param mavg_size Energy Detector mavg size.
        """

        gr.hier_block2.__init__(self,
                                name="simple_ranking_detector",
                                input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                                output_signature=gr.io_signature(2, 2, gr.sizeof_float)
                                )

        # Blocks
        # Convert the output of a FFT
        self.s2v_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, fft_size) 
        self.fft_0 = fft.fft_vcc(fft_size, True, [])
        self.c2mag_0 = blocks.complex_to_mag_squared(fft_size)

        # Instantiate the energy calculator
        from sensing import EnergyDecision
        self.ql = QLearningWorker(fft_size, algorithm=EnergyDecision(ed_threshold))

        #::TODO:: parece que nao tem mais o metodo connect
        # Flow graph
        self.connect(self, self.s2v_0, self.fft_0, self.c2mag_0, self.ql)

        self.connect((self.ql, 0), (self, 0))
        self.connect((self.ql, 1), (self, 1))

class RankingArch( UHDSSArch ):
    """
    Ranking architecture.
    Construct the ranking architecture.
    """

    def __init__(self, max_items_group):
        """
        CTOR.
        @param device     RadioDevice instance.
        @param detector   A SS detector. 
        @param max_items_group Number of ouputs to group.
        @return A tuple with 3 elements: (final decision, energy, avg energy)
        """

        #
        self._detector = SimpleRankingDetector(512, 5, 0.3)

        # Group items
        self._grouper  = GroupInN(
                max_items_group = max_items_group,
                callback = None,
                n_inputs = 2
            )


        UHDSSArch.__init__(
                self,
                name = "ranking_arch",
                input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
                output_signature = gr.io_signature(0, 0, 0)
         )


    def _build(self, input_signature, output_signature):
        """
        """

        self._add_connections([(self._detector, 0), (self._grouper, 0)])
        self._add_connections([(self._detector, 1), (self._grouper, 1)])

        return self._detector

        # no outputs

    def _get_sensing_data(self, the_channel, sensing_time):
        """
        Configure the device to sense the given frequency.
        @param the_channel Channel object instance. Channel to sense.
        @param sensing_time Duration of sensing.
        @return SS information of channel.
        """

        # Configure device center frequency
        # ::TRICK:: self._device  can be a DeviceChannelModel object
        #           If is the case, then check the DeviceChannelModel::center_freq method
        self.radio.set_center_freq( the_channel )

        self._grouper.set_enable( True )
        time.sleep( sensing_time )
        self._grouper.set_enable( False )

        return self._grouper.get_items()


    def sense_channel(self, the_channel, sensing_time):
        """
        ## SS on a single channel
        # Reimplement from UHDSSArch::sense_channel
        # @param the_channel Channel to be sensed.
        # @param sensing_time Sensing duration on channel.
        """
        return self._get_sensing_data( the_channel, sensing_time )


    def sense_channel_list(self, the_list, sensing_time):
        """
        @param the_list
        @param sensing_time
        """
        res = []

        for channel in the_list:
            x = self.sense_channel(channel, sensing_time)

            res.append( (channel.get_channel() , x) )

        return res
