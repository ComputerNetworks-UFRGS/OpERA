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

from algorithm.abstractAlgorithm import ThresholdAlgorithm
from utils import Logger

import numpy       as np
import scipy.stats as sc



## Class implementing a Waveform Algorithm
# Uses Pearson correlation do math a received signal  with the known patterns.
class WaveformDecision(ThresholdAlgorithm):

	WAVEFORMS = [ [0.1] * 1024,  ]


	## CTOR
	# @param threshold Decision threshold
	# @param waveforms Array of known patterns
	def __init__(self, threshold, waveforms = WAVEFORMS):
		ThresholdAlgorithm.__init__(self, threshold = threshold)

		self._waveforms = waveforms

		Logger.register('waveform_decision', ['correlation', 'decision'] )

	## @abstractmethod
	# Called from a signal processing block to made a decision
	# @param data_in Mag squared of samples
	# @return Tuple (status, correlation)
	def decision(self, data_in):
		max_corr = -1.0

		for wave in self._waveforms:
			max_corr = max(abs(self.correlate(wave, data_in)), max_corr)

		Logger.append('waveform_decision', 'correlation', max_corr)
		Logger.append('waveform_decision', 'decision', (1 if self.threshold < max_corr else 0))

		return ((1 if self.threshold < max_corr else 0), max_corr)


	## Correlates a signal waveform with a known pattern 
	# @param pattern Known pattern
	# @param signal Received signal
	def correlate(self, pattern, signal):
		return sc.pearsonr(pattern, signal)[0]
