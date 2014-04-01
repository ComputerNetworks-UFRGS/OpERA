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

## @package algorithm

from abc import ABCMeta, abstractmethod


class AbstractAlgorithm(object):
    """
    Abstract algorithms.
    Meta class for every sensing algorithm.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """
        CTOR
        """
        pass

    @abstractmethod
    def decision(self, data_in):
        """
        Must be implemented on derived class.
        @param data_in
        """
        pass


class ThresholdAlgorithm(AbstractAlgorithm):
    """
    Abstract algorithm with threshold.
    """

    def __init__(self, threshold):
        """
        CTOR
        @param threshold Initial threshold
        """
        AbstractAlgorithm.__init__(self)

        self._threshold = threshold

    @property
    def threshold(self):
        """
        Threshold property.
        @return Return the threshold.
        """
        return self._threshold

    @threshold.setter
    def threshold(self, val):
        """
        Sets the threshold to the given val.
        @param val The new threshold value.
        """
        self._threshold = val

    @abstractmethod
    def decision(self, data_in):
        """
        Must be implemented on derived class.
        @param data_in
        """
        pass
