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

from abstractAlgorithm import AbstractAlgorithm

from math import *
from abc import ABCMeta, abstractmethod

from utils import Logger  #pylint:disable=F0401


#::TODO:: descricao dos metodos e seus parametros.
class FeedbackAlgorithm(AbstractAlgorithm):
    """
    Simple feedback algorithm class.
    """

    def __init__(self, learner, manager, a_feedback_strategy):
        """
        CTOR
        @param learner Algorithm that will be adjusted.
        @param manager
        @param a_feedback_strategy FeedbackTimeStrategy object.
        """
        AbstractAlgorithm.__init__(self)

        self._learner = learner
        self._manager = manager
        self._strategy = a_feedback_strategy

        self._valid_feedback = True

        self._count = 0
        self._iteraction = 0
        self._time = 0

        # Debug information
        Logger.register('feedback_algorithm', ['total_feedback', 'activation', 'count', 'time'])


    @property
    def learner(self):
        """
        Return the learning algorithm.
        @return The learner (threshold learning) algorithm.
        """
        return self._learner


    @property
    def strategy(self):
        """
        Return the strategy.
        @return The strategy (feedback time algorithm).
        """
        return self._strategy


    def decision(self, data_l, data_m):
        """
        Function called from a signal processing block.
        @param data_l Learner decision regarding channel occupancy.
        @param data_m Manager decision regarding channel occupancy.
        """
        self.strategy.wait()

        self._iteraction += 1

        final_dec = data_l

        if self._valid_feedback:
            final_dec = data_m
            self._time += 19.3
            self._count += 1
            Logger.set('feedback_algorithm', 'total_feedback', self._count)
            Logger.append('feedback_algorithm', 'activation', int(data_m))

            # set feedback in our learning algorithm
            self.learner.feedback = data_m

            # Increase feedback interval if both algorithms are correct
            if data_l == data_m:
                self.strategy.increase_time()
            # else decrease time
            else:
                self.strategy.decrease_time()
        else:
            Logger.append('feedback_algorithm', 'activation', -1)
            self._time += 0.2

        self._valid_feedback = False
        if self.strategy.feedback():
            self._manager.enable(True)
            self._valid_feedback = True

        Logger.append('feedback_algorithm', 'time', self._time)
        Logger.append('feedback_algorithm', 'count', self._count)
        Logger.append('bayes_decision', 'hypothesis', final_dec)

##############################################################################
#                           Feedback strategies                              #
##############################################################################


class FeedbackTimeStrategy(object):
    """
    Feedback time Strategy class
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """
        CTOR
        """
        self._waiting_time = 0


    @property
    def waiting_time(self):
        """
        Return the how long the algorithm is waiting.
        @return  Waiting time.
        """
        return self._waiting_time


    def wait(self):
        """
        Increase waiting time.
        """
        self._waiting_time += 1


    def feedback(self):
        """
        Verify if is time to provide a feedback.
        @return True if waiting time >= feedback interval time.
        """
        t = self._waiting_time >= self.feedback_time()

        if t:
            self._waiting_time = 0

        return t


    @abstractmethod
    def feedback_time(self):
        """
        Return the feedback interval.
        Derived class must implement this method.
        """
        pass


    @abstractmethod
    def increase_time(self):
        """
        Increase the interval between feedbacks.
        Derived class must implement this method.
        """
        pass


    @abstractmethod
    def decrease_time(self):
        """
        Decrease the interval between feedbacks.
        Derived class must implement this method.
        """
        pass


class AlwaysTimeFeedback(FeedbackTimeStrategy):
    """
    1:1 time feedback.
    """

    def __init__(self):
        """
        CTOR
        """
        FeedbackTimeStrategy.__init__(self)


    # @abstractmethod
    def feedback_time(self):
        """
        Inherit from parent.
        """
        return 1


    # @abstractmethod
    def increase_time(self):
        """
        Inherit from parent.
        """
        pass

    # @abstractmethod
    def decrease_time(self):
        """
        Inherit from parent.
        """
        pass


class ExponentialTimeFeedback(FeedbackTimeStrategy):
    """
    1:N Exponential time feedback.
    Increase time to next feedback exponentially.
    Exponential is passed as parameter.
    Return feedback interval to 0.
    """

    ##::TODO:: o parametro recebido eh base, mas na doc tem um 'exponent'
    def __init__(self, min_time, max_time, base):
        """
        CTOR
        @param min_time Min allowed time.
        @param max_time Max allowed time.
        @param base The exponential base.
        @param exponent Exponent.
        """
        FeedbackTimeStrategy.__init__(self)

        self._min = min_time
        self._max = max_time

        self._base = base
        self._exp = 0

    def feedback_time(self):
        """
        Inherit from parent.
        @return The feedback time.
        """
        return pow(self._base, self._exp)


    def increase_time(self):
        """
        Inherit from parent.
        Increase time.
        """
        if pow(self._base, self._exp + 1) <= self._max:
            self._exp += 1

    def decrease_time(self):
        """
        Inherit from parent.
        Reset time.
        """
        self._exp = 0


class KunstTimeFeedback(ExponentialTimeFeedback):
    """
    1:N Exponential time feedback.
    Increase time to next feedback exponentially.
    Exponential is passed as parameter.
    Return feedback interval to the previous utilized interval.
    """
    def __init__(self):
        ExponentialTimeFeedback.__init__(self,
                                         min_time=1,
                                         max_time=128,
                                         base=2)

    def decrease_time(self):
        """
        Inherit from parent.
        """
        if self._exp > 0:
            self._exp -= 1


from gnuradio import gr
import numpy as np


class HierarchicalFeedbackAlgorithm(gr.sync_block):
    """

    """
    ##::TODO:: parametros estao incorretos!!! parametros da funcao != parametros na doc.
    def __init__(self, algorithm, _type=np.float32):
        """
        CTOR
        @param algorithm
        @param _type
        @param learner Algorithm that will be adjusted. ???????????
        @param a_feedback_strategy FeedbackTimeStrategy object.  ????????????
        """
        gr.sync_block.__init__(self,
                               name='bayes_decision',
                               in_sig=[np.dtype((np.float32, 1024)),
                                       np.dtype((_type, 1024))],      #pylint: disable=E1101
                               out_sig=None,  #pylint: disable=E1101
                               )

        self._algorithm = algorithm

        self._count = 0
        self._iteraction = 0
        self._time = 0

        # Debug information
        Logger.register('bayes_decision', ['hypothesis', 'activation', 'count', 'time'])
        Logger.register('feedback_algorithm', ['total_feedback', ])


    def work(self, input_items, output_items):
        """

        @param input_items
        @param output_items
        """
        for idx in range(len(input_items[0])):
            self._iteraction += 1

            ed_dec = input_items[0][idx][0]
            wf = input_items[1][idx]

            final_dec = ed_dec
            if ed_dec == 0:
                final_dec = 1
                final_dec = self._algorithm.decision(wf)[0]

                Logger.set('feedback_algorithm', 'total_feedback', self._count)

            Logger.append('bayes_decision', 'hypothesis', final_dec)

        return len(input_items[0])
