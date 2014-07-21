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

"""
@package ssf
"""


from gnuradio import gr
from device import UHDSSArch
import numpy as np


#::TODO:: descricao de metodos e seus parametros
class FeedbackF(gr.sync_block):
    """
    Feedback block
    Has two inputs: 0- decision from the learning algorithm; 1- decision from the manager algorithm
    Both inputs are passed to a controller  algorithm (self._algorithm).

    Ideally, the frequency of both inputs should be equal (1:1)
    """

    def __init__(self, algorithm):
        """
        CTOR
        @param algorithm AbstractAlgorithm. Must implement algorithm.decision(param1, param2).
        """

        # initialize base class
        gr.sync_block.__init__(self,
                               name='FeedbackF',
                               in_sig=[np.float32, np.float32],
                               out_sig=None
                               )

        # algorithm de feedback
        self._algorithm = algorithm

    def work(self, input_items, output_items):
        """
        GNURadio loop function.
        @param input_items
        @param output_items
        """
        print "nooooooooooooooooooooooooooooo!!!!"

        in0 = input_items[0][0]  # learner
        in1 = input_items[1][0]  # manager

        self._algorithm.decision(in0, in1)

        return len(input_items[0])


class FeedbackSSArch(gr.sync_block):
    """
    Feedback Architecture.

    Instantiate this block if you want the feedback architecture described in the paper: "An Adaptive Feedback System
    to Threshold Learning for Cognitive Radios".

    Inputs: 1 complex at a time.
    Output: {0,1} regarding channel occupancy.
    """

    def __init__(self, input_len, algo1, algo2, feedback_algorithm):
        """
        CTOR
        
        @param block_manager Sensing block that is considered always correct.
        @param block_learner Sensing block which threshold is adjusted.
        @param feedback_algorithm Feedback Algorithm.
        """

	self._algo1 = algo1
	self._algo2 = algo2
	self._feedback = feedback_algorithm

	gr.sync_block.__init__(self,
		name="hier",
		in_sig = [np.dtype((np.float32, input_len)), np.dtype((np.float32, input_len))], 
		#in_sig = [np.dtype((np.float32, input_len)), np.dtype((np.complex64, input_len))], 
		out_sig= None   #pylint: disable=E1101
	 )


	Logger.register('ata', ['decision', ] )



    def work(self, input_items, output_items):
		for idx in range(len(input_items[0])):
			self._feedback.wait()
			if self._feedback.feedback():
				dec2, e2 = self._algo2.decision(input_items[1][idx])
				self._algo1.feedback = dec2

				dec1, e1 = self._algo1.decision(input_items[1][idx])

				if dec1 == dec2:
					self._feedback.increase_time()
				else:
					self._feedback.decrease_time()
			else:
				dec1, e1 = self._algo1.decision(input_items[0][idx])
			
            		Logger.append('ata', 'decision', dec1)

		return len(input_items[0])
				
			
    #::TODO:: parametros nao usados
    def _get_sensing_data(self, channel, sensing_time):
        """
        @param channel
        @param sensing_time
        """
        return 0

from utils import Logger


#class FeedbackSSArch2(gr.sync_block):
#    """
#    Feedback Architecture.
#
#    Instantiate this block if you want the feedback architecture described in the paper: "An Adaptive Feedback System
#    to Threshold Learning for Cognitive Radios".
#
#    Inputs: 1 complex at a time.
#    Output: {0,1} regarding channel occupancy.
#    """
#
#    #::TODO:: parametros da funcao diferentes dos da doc
#    def __init__(self, learning_algorithm, feedback_algorithm, waveform, _type=np.float32):
#        """
#        CTOR
#        @param learning_algorithm
#        @param feedback_algorithm Feedback Algorithm.
#        @param waveform
#        @param _type
#
#        OLD
#        @param block_manager Sensing block that is considered always correct
#        @param block_learner Sensing block which threshold is adjusted
#        @param feedback_algorithm
#        @param _type
#        """
#        gr.sync_block.__init__(self,
#                               name='feedback_ss_arch',
#                               in_sig=[np.dtype((np.float32, 1)), np.dtype((_type, 1024))],  #pylint: disable=E1101
#                               out_sig=None,  #pylint: disable=E1101
#            )
#
#        self._feedback_algorithm = feedback_algorithm
#        self._learning_algorithm = learning_algorithm
#        self._waveform = waveform
#
#        self._count = 0
#        self._iteraction = 0
#        self._time = 0
#
#        # Debug information
#        Logger.register('bayes_decision', ['hypothesis', 'activation', 'count', 'time'])
#        Logger.register('feedback_algorithm', ['total_feedback', ])
#
#
#    def work(self, input_items, output_items):
#        """
#        @param input_items
#        @param output_items
#        """
#        #for ed_dec, wf in zip(input_items[0], input_items[1]):
#        for idx in range(len(input_items[0])):
#            ed_dec = input_items[0][idx][0]
#            wf = input_items[1][idx]
#            final_dec = ed_dec
#
#            self._iteraction += 1
#            self._feedback_algorithm.wait()
#            if self._feedback_algorithm.feedback():
#                data_m = self._waveform.decision(wf)[0]
#                self._learning_algorithm.feedback = data_m
#
#                if data_m == ed_dec:
#                    self._feedback_algorithm.increase_time()
#                else:
#                    self._feedback_algorithm.decrease_time()
#
#                final_dec = data_m
#                self._count += 1
#
#            Logger.append('bayes_decision', 'hypothesis', final_dec)
#
#        return len(input_items[0])
