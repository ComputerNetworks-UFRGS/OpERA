#!/usr/bin/env python

import random

IDLE = 0
OCCUPIED = 1

class SDController:

	def __init__(self, number_cpes, feedback_control, increase_rate, decrease_rate):
		self._fb_cycle = 0
		self._reward = [1.0] * number_cpes

		print self._reward


	def sensing_decision(self, sensing_result, number_cpes):
		print "simple cycle"

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
		if (self._fb_cycle % (feedback_control-1) == 0):
			self.feedback(sensing_result, sensing_decision, increase_rate, decrease_rate)


	def feedback(self, sensing_result, sensing_decision, increase_rate, decrease_rate):
		print "feedback cycle"

		#analyze if the decision made by each CPE matches the decision made by the SDC
		for decision, index in enumerate(sensing_result):
			#match, increase reward
			if (decision == sensing_decision):
				self._reward[index] *= (1.0 + increase_rate)
				if (self._reward[index] > 1.0):
					self._reward[index] = 1.0

			#doesnt match, decrease reward
			elif (decision != sensing_decision):
				self._reward[index] *= (1.0 - decrease_rate)

		print sensing_result
		print sensing_decision
		print self._reward


if __name__ == "__main__":

	#initialize variables
	number_cpes = 4
	feedback_control = 5
	increase_rate = 0.1
	decrease_rate = 0.2
	sensing_result = [0] * number_cpes

	#initialize the Sensing Decision Controller
	sdc = SDController(number_cpes, feedback_control, increase_rate, decrease_rate)

	while True:
		#random spectrum sensing, just for testing
		for i in range(number_cpes):
			sensing_result[i] = random.randint(0,1)

		#Spectrum Sensing Decision
		sdc.sensing_decision(sensing_result, number_cpes)
