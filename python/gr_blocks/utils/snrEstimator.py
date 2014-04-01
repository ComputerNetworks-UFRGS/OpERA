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

from gnuradio import digital  #pylint: disable=F0401

from device import UHDGenericArch  #pylint: disable=F0401
from utils import Logger           #pylint: disable=F0401


#::TODO:: descricao da classe e de seus metodos
class SNREstimator(UHDGenericArch):
    """

    """

    SIMPLE = 0    
    SKEW = 1
    MOMENT = 2
    SVR = 3

    def __init__(self,
                 name="SNREstimator",
                 algorithm=SVR,
                 alpha=0.001):
        """
        CTOR
        @param name
        @param algorithm
        @param alpha
        """
        self._estimator = digital.probe_mpsk_snr_est_c(algorithm, 10000, alpha)

        UHDGenericArch.__init__(self,
                                name=name,
                                input_signature=self._estimator.input_signature(),
                                output_signature=self._estimator.output_signature())

        Logger.register(name, ['snr', ])

        self.register_scheduling(lambda: Logger.append(name, 'snr', self.get_snr()), delay_sec=0.2)  #pylint: disable=E1101


    #::TODO:: pq tem os parametros input e output signature, se eles nao estao sendo usados?
    def _build(self, input_signature, output_signature):
        """
        @param input_signature
        @param output_signature
        """
        return self._estimator

    def get_snr(self):
        """

        """
        return self._estimator.snr()
