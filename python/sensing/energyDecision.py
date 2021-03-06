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
@package algorithm
"""

from algorithm.abstractAlgorithm import ThresholdAlgorithm
from utils import Logger

import numpy as np


class EnergyDecision(ThresholdAlgorithm):
    """
    Simple energy threshold comparison algorithm.
    """

    def __init__(self, th=0):
        """
        CTOR
        @param th Decision threshold.
        """
        ThresholdAlgorithm.__init__(self, th)
        Logger.register('energy_decision', ['energy', 'decision'])

	self._xx = {};
	self._xx[0] = {0: "00", 1: "01"}
	self._xx[1] = {0: "10", 1: "11"}

    def decision(self, data_in):
        """"
        Implementation of base class abstract method.
        @param data_in Mag squared of samples.
        @return Tuple (status, energy)
        """
        energy = np.sum(data_in) / data_in.size

	dec = 1 if self.threshold < energy else 0

        Logger.append('energy_decision', 'energy', energy)
        Logger.append('energy_decision', 'decision', self._xx[Logger._ch_status][dec])

        return dec, energy
