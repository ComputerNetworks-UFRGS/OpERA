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

from algorithm.abstractAlgorithm import ThresholdAlgorithm

## Simple energy detection algorithm based in threshold comparion
class EnergyDecision(ThresholdAlgorithm):

	## CTOR
	# @param th Initial threshold
	def __init__(self, th = 0):
		ThresholdAlgorithm.__init__(self, th)

	## @abstractmethod
	# Called from a signal processing block to made a decision
	def decision(self, data_in):
		return (self.threshold < data_in)
