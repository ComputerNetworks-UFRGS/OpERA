## @package algorithm

from ssf.algorithm.abstractAlgorithm import ThresholdAlgorithm

## Simple energy detection algorithm based in threshold comparion
class EnergyAlgorithm(ThresholdAlgorithm):

	## CTOR
	# @param th Initial threshold
	def __init__(self, th = 0):
		ThresholdAlgorithm.__init__(self, th)

	## @abstractmethod
	# Called from a signal processing block to made a decision
	def decision(self, data_in):
		return (self.threshold < data_in)
