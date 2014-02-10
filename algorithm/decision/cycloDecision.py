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

class CycloDecision(ThresholdAlgorithm):
    """
    Simple energy threshold comparison algorithm.
    """

    def __init__(self, Np, P, L, th = 0):
        """
        CTOR
        @param th Decision threshold.
        """
        ThresholdAlgorithm.__init__(self, th)

        Logger.register('cyclo_decision', ['corr', 'decision'] )

        from opera import cyclo_fam_calcspectrum_vcf
        self._algoritm = cyclo_fam_calcspectrum_vcf(Np, P, L)


    def decision(self, data_in):
        """"
        Implementation of base class abstract method.
        @param data_in Mag squared of samples.
        @return Tuple (status, energy)
        """
        _sum = self._algoritm.calculate_cyclo( data_in.tolist() )
        _sum = _sum / len(data_in)

        Logger.append('cyclo_decision', 'corr', _sum)
        Logger.append('cyclo_decision', 'decision', (1 if self.threshold < _sum else 0))

        return ((1 if self.threshold < _sum else 0), _sum)
