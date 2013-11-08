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

#!/usr/bin/env python

import sys
import os
import random

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)

from utils import Logger

# constants
IDLE = 0
OCCUPIED = 1

# Class of the algorithm 
class SDController:

	## CTOR
	# @param number_cpes
	# @param feedback_control
	# @param increase_rate
	# @param decrease_rate
	def __init__(self, number_cpes, feedback_control, increase_rate, decrease_rate):
		self._fb_cycle = 0
		self._reward = [1.0] * number_cpes
		self._total_idle = self._total_occ = 0
		Logger.register('sdc', ['decision',])

	## Algorithm sensing decision
	# @param sensing_result
	# @param number_cpes
	def sensing_decision(self, sensing_result, number_cpes):
		#print "simple cycle"

		#feedback cycle control
		self._fb_cycle += 1

		#initialize sum of scores for each decision (0,1)
		sum_result0 = 0.0
		sum_result1 = 0.0

		#keeps the greatest reward for each decision
		greatest_reward0 = 0.0
		greatest_reward1 = 0.0

		#sum of all scores for each decision
		for decision, reward in zip(sensing_result, self._reward):

			#sum of scores for "0" decision
			if (decision == IDLE):
				sum_result0 += reward 
				if (reward > greatest_reward0):
					greatest_reward0 = reward 

			#sum of scores for "1" decision
			elif (decision == OCCUPIED):
				sum_result1 += reward 
				if (reward > greatest_reward1):
					greatest_reward1 = reward 

		#divide the sum of scores by the total number of CPEs
		score_r1 = sum_result1 / number_cpes
		score_r0 = sum_result0 / number_cpes

		#verifies which sum of scores is higher, score1 or score0
		if (score_r0 > score_r1):
			sensing_decision = IDLE

		elif (score_r0 < score_r1):
			sensing_decision = OCCUPIED

		#if both scores are equal, then verifies the decision made by the cpe with the greatest individual score
		elif (score_r0 == score_r1):
			if (greatest_reward0 >= greatest_reward1):
				sensing_decision = IDLE
			elif (greatest_reward0 < greatest_reward1):
				sensing_decision = OCCUPIED

		#verifies if is feedback cycle
		#if (self._fb_cycle % (feedback_control-1) == 0):
		Logger.append('sdc', 'decision', sensing_decision)
		if sensing_decision == OCCUPIED:
			self._total_occ += 1
		else:
			self._total_idle += 1
		self.feedback(sensing_result, sensing_decision, increase_rate, decrease_rate)

	## If it is a Feedback cycle
	# @param sensing_result
	# @param sensing_decision
	# @param increase_rate
	# @param decrease_rate
	def feedback(self, sensing_result, sensing_decision, increase_rate, decrease_rate):
		#print "feedback cycle"

		#analyze if the decision made by each CPE matches the decision made by the SDC
		for index, decision in enumerate(sensing_result):
			#match, increase reward
			if (decision == sensing_decision):
				self._reward[index] *= (1.0 + increase_rate)
				if (self._reward[index] > 1.0):
					self._reward[index] = 1.0

			#doesnt match, decrease reward
			elif (decision != sensing_decision):
				self._reward[index] *= (1.0 - decrease_rate)
		
		print "\n***********************"
		print "result: " + str(sensing_result)
		print "decision: " + str(sensing_decision)
		print self._reward


# executes the sensing decision module of the SDController class.
## Execution of the sensing_decision module.
# @param hit_rate A list with the hit ratio for every cpe. Example: hit_rate = [90, 78, 32] - the first cpe has a hit ratio of 90%, the second has a hit ratio of 78% and the third has a hit ratio of 32%.
# @param num_steps Number of executions of the sensing_result
def executeSensingDecision(hit_rate, num_steps):

	feedback_control = 5
	increase_rate = 0.1
	decrease_rate = 0.1
	num_cpes = len(hit_rate)

	list_str_cpes = []

	for i in range(num_cpes):
		list_str_cpes.append("cpe" + str(i+1))

	# save strings in the Logger
	Logger._enable = True
	Logger.register("reward", list_str_cpes)

	sdc = SDController(num_cpes, feedback_control, increase_rate, decrease_rate)	

	# each element of this array is also an array. the array of the index 0 (ie, array_hit[0]) corresponds to the hit_rate[0] and so on.
	cpe_array = [0] * num_steps
	
	array_hit = []

	# num_cpes is the length of array_hit
	for i in range(num_cpes):
		# need to append as a list because otherwise if we modify some subarray, ALL arrays are modified too.
		array_hit.append(list(cpe_array))

	# list of lists, where the random indexes will be.
	list_indexes = []
	for i in range(num_cpes):
		list_indexes.append(list([]))


	# set some random positions of the arrays to one.
	for i in range(num_cpes):
		while len(list_indexes[i]) < (num_steps - (num_steps * hit_rate[i]/100)):
			rand = random.randint(0, num_steps-1)
			if rand not in list_indexes[i]:
				list_indexes[i].append(rand)
				array_hit[i][rand] = 1


	for step in range(num_steps):
		sensing_result = []
			
		for cpe in range(num_cpes):
			sensing_result.append(array_hit[cpe][step])
			Logger.append("reward", list_str_cpes[cpe], sdc._reward[cpe])	
	

		sdc.sensing_decision(sensing_result, num_cpes)	

	Logger.dump('./dump', '/cpes', 0)

	print "\n\n REWARD\n\n"
	for cpe in range(num_cpes):
		print "reward cpe %i: " %(cpe+1) + str(sdc._reward[cpe])

	print "TOTAL HIT RATE: ", float(sdc._total_idle/float(num_steps))
		

if __name__ == "__main__":

	feedback_control = 5
	increase_rate = 0.1
	decrease_rate = 0.2
	hit_rate = [95, 95, 95, 95, 95]
	num_steps = 1000
	executeSensingDecision(hit_rate, num_steps)
	

