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

from utils import Logger

## Simple feedback algorithm class
class FeedbackAlgorithm(AbstractAlgorithm):

	## CTOR
	# @param learner Algorithm that will be adjusted
	# @param aFeedbackStrategy FeedbackTimeStrategy object
	def __init__(self, learner, aFeedbackStrategy):
		self._learner = learner
		self._strategy = aFeedbackStrategy

		self._count = 0
		self._iteraction = 0
		self._time = 0

		# Debug information
		Logger.register('feedback_algorithm', ['total_feedback', 'activation', 'count', 'time'])


	## Return the learning algorithm
	# @ret The learner (threshold learning) algorithm
	@property
	def learner(self):
		return self._learner


	## Return the strategy
	# @ret The strategy (feedback time algorithm)
	@property
	def strategy(self):
		return self._strategy


	## Function called from a signal processing block
	# @param data_l Learner decision regarding channel occupancy
	# @param data_m Manager decision regarding channel occupancy
	def decision(self, data_l, data_m):
		self.strategy.wait()

		self._iteraction += 1;

		# Check if is time to provide a feedback
		if self.strategy.feedback():
			self._time += 19.3
			self._count += 1
			Logger.set('feedback_algorithm', 'total_feedback', self._count)
			Logger.append('feedback_algorithm', 'activation', int(data_m))

			# set feeback in our learning algorithm
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

		Logger.append('feedback_algorithm', 'time', self._time)
		Logger.append('feedback_algorithm', 'count', self._count)



##############################################################################
#                           Feedback strategies                              #
##############################################################################

## Feedback time Strategy class
class FeedbackTimeStrategy(object):
	__metaclass__ = ABCMeta

	## CTOR
	def __init__(self):
		self._waiting_time = 0


	## Return the how long the algorithm is waiting
	# @ret  Waiting time
	@property
	def waiting_time(self):
		return self._waiting_time


	## Increase waiting time
	def wait(self):
		self._waiting_time += 1


	## Verify if is time to provide a feedback
	# @ret True if waiting time >= feedback interval time
	def feedback(self):
		t = self._waiting_time >= self.feedback_time()

		if t:
			self._waiting_time = 0

		return t


	## Return the feedback interval
	# Derived class must implement this method
	@abstractmethod
	def feedback_time(self):
		pass


	## Increase the interval between feedbacks
	# Derived class must implement this method
	@abstractmethod
	def increase_time(self):
		pass

	## Decrease the interval between feedbacks
	# Derived class must implement this method
	@abstractmethod
	def decrease_time(self):
		pass


## 1:1 time feedback 
class AlwaysTimeFeedback( FeedbackTimeStrategy ):

	## CTOR
	def __init__(self):
		FeedbackTimeStrategy.__init__(self)

	## Inherit from parent
	# @abstractmethod
	def feedback_time(self):
		return 1

	## Inherit from parent
	# @abstractmethod
	def increase_time(self):
		pass

	## Inherit from parent
	# @abstractmethod
	def decrease_time(self):
		pass


## 1:N Exponential time feedback
# Increase time to next feedback exponentially.
# Exponential is passed as parameter
# Return feedback interval to 0 
class ExponentialTimeFeedback( FeedbackTimeStrategy ):
	
	## CTOR
	# @param min_time Min allowed time
	# @param max_time Max allowed time
	# @param exponent Exponent
	def __init__(self, min_time, max_time, base):
		FeedbackTimeStrategy.__init__(self)

		self._min = min_time
		self._max = max_time

		self._base = base
		self._exp  = 0

	## Inherit from parent
	def feedback_time(self):
		return pow(self._base, self._exp)

	## Inherit from parent
	# Increase time
	def increase_time(self):
		if pow(self._base, self._exp + 1) <= self._max:
			self._exp += 1

	## Inherit from parent
	# Reset time
	def decrease_time( self ):
		self._exp = 0

## 1:N Exponential time feedback
# Increase time to next feedback exponentially.
# Exponential is passed as parameter
# Return feedback interval to the previous utilized interval
class KunstTimeFeedback( ExponentialTimeFeedback ):
	def __init__(self):
		ExponentialTimeFeedback.__init__(self,
				min_time = 1,
				max_time = 256,
				base = 2) 

	## Inherit from parent
	def decrease_time(self):
		if self._exp > 0:
			self._exp -= 1
