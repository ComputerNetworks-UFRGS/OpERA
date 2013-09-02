## @package algorithm

from abc import ABCMeta, abstractmethod

## Abstract algorithms
# Meta class for every sensing algorithm
class AbstractAlgorithm(object):
	__metaclass__ = ABCMeta

	def __init__(self):
		pass

	@abstractmethod
	def decision(self, data_in):
		pass

## Abstract algorithm with threshold
class ThresholdAlgorithm(AbstractAlgorithm):

	## CTOR
	# @param threshold Initial threshold
	def __init__(self, threshold):
		AbstractAlgorithm.__init__(self)

		self._threshold = threshold

## Threshold property
	@property
	def threshold(self):
		return self._threshold

	@threshold.setter
	def threshold(self, val):
		self._threshold = val

	@abstractmethod
	def decision(self, data_in):
		pass
