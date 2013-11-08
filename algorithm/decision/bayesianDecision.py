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
#!/usr/bin/python

## @package algorithm

from algorithm.abstractAlgorithm  import AbstractAlgorithm
from utils import Logger

from math import *
import numpy as np

## Class for learning thresholds with bayes hiphotesis
class BayesLearningThreshold(AbstractAlgorithm):
	
	## CTOR
	# @param in_th Initial threshol
	# @param min_th Minimum threshold
	# @param max_th Maximum threshold
	# @param k Bayesian k factor
	def __init__(self,
			in_th,
			min_th,
			max_th,
			delta_th,
			k):
		Logger.register('bayes_learning', ['threshold', 'energy', 'hiphotesis', 'real_state', 'feedback', 'risk', 'pd', 'pf', 'pm', '00', '01', '11', '10'] )

		# Initialize data structures
		self._p  = {}
		self._pd = {}
		self._pf = {}
		self._pm = {}

		self._c    = {}
		self._cSum = {}
		self._r = {}

		self._k = k

		self._feedback = 1

		for p in [ 'h0', 'h1', 'pf', 'pd', 'pm']:
			self._p[ p ] = 0
		for c in ['00', '01', '10', '11']:
			self._cSum[c] = 0

		self._min_th = in_th
		self._max_th = in_th 
		self._delta_th = delta_th

		self._min_th_limit = min_th
		self._max_th_limit = max_th
		
		self._th =  in_th
		self.insert_th( in_th )




	## Feedback property getter
	# @ret _feedback
	@property
	def feedback(self):
		return self._feedback

	## Feedback property setter
	# @param val New feedback value
	@feedback.setter
	def feedback(self, val):
		self._feedback = val

	## Insert a new threshold in list of usable thresholds
	# Add all intermediate thresholds if necessary
	# @param th New threshold
	def insert_th(self, th ):
		## @TODO Verify th value
		if self._pd.has_key( th ):
			return

		# New Threshold initialization
		def newTh(self, th):
			self._pd[th] = self._pf[th] = self._pm[th] = 1.0
			self._r[th] = 0.0

			self._c[th] = {}
			for c in ['00', '01', '10', '11']:
				self._c[th][c] = 0

		# Set low and high limits
		high = low = th 
		if th < self._min_th:
			high = self._min_th
			low  = th
		elif th > self._max_th:
			high = th
			low  = self._max_th

		# Insert thresholds between low and high
		t = low
		while t <= high:
			newTh(self, t )
			t += self._delta_th

		# update min and max threshold
		self._max_th = max(self._max_th, high)
		self._min_th = min(self._min_th, low)


	## w function
	# @param th Threshold
	def calculate_w(self, th):
		num = self._pd[th] * (1.0 - self._pf[th])
		den = self._pf[th] * (1.0 - self._pd[th])

		try:
			return log10( num / den ) 
		except:
			return 1.0

	## calculate_Mu function
	# @param th Threshold
	def calculate_Mu(self, th, N):

		elem_1 = 0
		try:
			elem_1 = (1.0/N) * log10(self._p['h0'] / self._p['h1'])
		except:
			pass

		elem_2 = 0
		try:
			elem_2 = log10( (1.0-self._pf[th] ) / (1.0-self._pd[th]) )
		except:
			pass

		return elem_1 + elem_2

	## Calculate bayesian hipthosis
	# @param th Threshold
	# @param energy Calculated energy
	def bayesian_hiphotesis(self, th, signal):
		N = signal.size

		# OLD (BUT CORRECT) IMPLEMENTATION OF THE BAYESIAN DETECTOR
		# @WARNING Without numpy this is a MAJOR bottleneck
		s = np.sum( np.multiply(
						[self.calculate_w(th)] * N,
						np.sign( np.subtract(signal, th) )
					)
				)

		s = (s/N) - self.calculate_Mu(th, N)
		return s

	## Update values of PD, PF, P, C, etc, based on bayesian hiphotesis and the feedback
	# @param th Threshold utilized
	# @param bayes_hip Bayes hiphothesis. 1 (occupied) or 0 (vacant)
	def update_global_counter(self, bayes_hip):
		c = ''
		th = self._th

		# Feedback says channel is free ...
		if self.feedback == 0:
			# ... and we too
			if bayes_hip < 0:
				c = '00'
			# ... but we no
			else:
				c = '10'

				# Need to increase threshold
				if th == self._max_th and th < self._max_th_limit:
					self.insert_th( th + self._delta_th)
		# Feedback says channel is occupied ...
		else:
			# ... and we too
			if bayes_hip > 0:
				c = '11'
			# ... but we no
			else:
				c = '01'

				if th == self._min_th and th > self._min_th_limit:
					self.insert_th( th - self._delta_th)

		# update counter
		self._cSum[ c ] += 1.0

		s = 0.0
		for c in self._cSum:
			s += self._cSum[c]

		self._p['h0'] = (self._cSum['00'] + self._cSum['10']) / s
		self._p['h1'] = (self._cSum['11'] + self._cSum['01']) / s

		try:
			self._p['pd'] = self._cSum['11'] / (self._cSum['01']+self._cSum['11'])
		except ZeroDivisionError:
			self._p['pd'] = 0.0

		try:
			self._p['pf'] = self._cSum['10'] / (self._cSum['00']+self._cSum['10'])
		except ZeroDivisionError:
			self._p['pf'] = 0.0


	## Update values of counters specifics of a threshold
	# @param signal Signal received on antenna
	def update_th_counter(self, signal):
		th = self._th
		th_p = self._th - self._delta_th
		th_n = self._th + self._delta_th

		self.update_th(th, self.bayesian_hiphotesis(th, signal))

		if th_p in self._r:
			self.update_th(th_p, self.bayesian_hiphotesis(th_p, signal))

		if th_n in self._r:
			self.update_th(th_n, self.bayesian_hiphotesis(th_n, signal))

	## Update the threshold
	# @param th Current Threshold
	# @param hip Bayesian hiphotesis regarding channel status
	def update_th(self, th, hip):
		c = ''

		# Feedback says channel is free ...
		if self.feedback == 0:
			# ... and we too
			if hip < 0:
				c = '00'
			# ... but we no
			else:
				c = '10'
		# Feedback says channel is occupied ...
		else:
			# ... and we too
			if hip > 0:
				c = '11'
			# ... but we no
			else:
				c = '01'

		# update counter
		self._c[ th ][ c ] += 1.0

		s00 = self._cSum['00']
		s01 = self._cSum['01']
		s10 = self._cSum['10']
		s11 = self._cSum['11']

		# update pf
		try:
			self._pf[th] = self._c[th]['10'] / (s00 + s10)
		except ZeroDivisionError:
			self._pf[th] = 0

		# update pd
		try:
			self._pd[th] = self._c[th]['11'] / (s01 + s11)
		except ZeroDivisionError:
			self._pd[th] = 0

		# update pf
		try:
			self._pm[th] = self._c[th]['01'] / (s01 + s11)
		except ZeroDivisionError:
			self._pm[th] = 0

		# update threshold bayesian risk. IMPORTANT !!!
		r = (self._pf[th] * self._p['h0'] + self._k * self._pm[th] * self._p['h1'])
		self._r[th] = r


	## Get minimum bayes risk and threshold
	# @return Tuple (risk:threshold)
	def get_min_risk(self):
		min_risk = min_th = 1000

		for th in sorted(self._r.iterkeys()):
			risk = self._r[th]

			if risk < min_risk:
				min_risk = risk
				min_th = th

		return min_risk, min_th

	## Method called for a USRP block (probably bayesian_detector)
	# @param energy Signal Energy
	def decision(self, energy):
		# hiphotetis
		bayes_hip = self.bayesian_hiphotesis(self._th, energy)

		# update counters
		self.update_global_counter(bayes_hip)

		# upate bayes
		self.update_th_counter(energy)

		# ::TRICKY::
		# The original implementation first check if r[th] < r[th-Delta] and r[th] < r[th+Delta]
		# If the above condition is true, then th = th/2
		# else, does the code below
		bayes_R, self._th = self.get_min_risk()

		# Save all data
		Logger.append('bayes_learning', 'threshold', self._th)
		Logger.append('bayes_learning', 'hiphotesis', 1 if bayes_hip > 0 else 0)
		Logger.append('bayes_learning', 'feedback', self.feedback)
		Logger.append('bayes_learning', 'real_state', Logger._ch_status)
		Logger.append('bayes_learning', 'risk', self._r[self._th])
		Logger.append('bayes_learning', 'energy', energy)

		Logger.append('bayes_learning', 'pd', self._pd[self._th])
		Logger.append('bayes_learning', 'pf', self._pf[self._th])
		Logger.append('bayes_learning', 'pm', self._pm[self._th])

		return (1 if bayes_hip > 0 else 0, 0.0)
