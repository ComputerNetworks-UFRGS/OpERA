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

__author__ = 'jtsreinaldo'


class AbstractDecisionAlgorithm(object):
    """
    Abstract class for decision algorithms.
    """

    # Constants used in the 'data' dictionary:
    RSSI = 0
    CHANNEL_OCCUPANCY = 1
    BIT_RATE = 2
    LINKS = 3
    CHANNELS = 4
    CHANNEL_PU_PRESENCE = 5
    CHANNEL_SU_PRESENCE = 6
    OCCUPANCY_MATRIX = 7
    REWARD_MATRIX = 8
    INTERFERENCE_MATRIX = 9
    ITERATIONS = 10
    UTILITY_MATRIX = 11
    POSSIBLE_LINKS = 12
    POSSIBLE_FREQUENCIES = 13
    SIM_ANNEALING_PARAMETERS = 14

    def __init__(self):
        """
        CTOR
        """
        self.channel_list = []

    def get_channel_list(self):
        """
        Return the ordered channel list (the first element is the best channel, the second element is the second best
        channel and so on).
        @return The ordered channel list.
        """
        return self.channel_list

    def get_channel(self, position):
        """
        Return the channel of a given position.
        @param position
        @return The channel in the position 'position' in the ordered channel list.
        """
        return self.channel_list[position]

    def get_best_channel(self):
        """
        Return the best evaluated channel.
        @return The best channel.
        """
        return self.channel_list[0]

    def evaluate(self, data):
        """
        Must be implemented on derived class.
        Executes the decision algorithm.
        @param data A dictionary with the parameters used by the algorithm.
        """
        pass
