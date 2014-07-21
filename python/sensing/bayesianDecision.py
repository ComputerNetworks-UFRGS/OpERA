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

from algorithm import AbstractAlgorithm
from utils import Logger

import math
from scipy import arange
import numpy as np
from collections import OrderedDict


class BayesLearningThreshold(AbstractAlgorithm):
    pass
#    """
#    Class for learning thresholds with bayes hypothesis.
#    """
#
#    def __init__(self, in_th, min_th, max_th, delta_th, k):
#        """
#        CTOR
#        @param in_th Initial threshold.
#        @param min_th Minimum threshold.
#        @param max_th Maximum threshold.
#        @param k Bayesian k factor.
#        """
#        Logger.register('bayes_decision', ['threshold', 'energy', 'hypothesis', 'real_state', 'feedback', 'risk', 'pd',
#                                           'pf', 'pm', 'db'])
#
#        # Initialize data structures
#        self._p = {}
#        self._pd = {}
#        self._pf = {}
#        self._pm = {}
#
#        self._c = {}
#        self._c_sum = {}
#        self._r = {}
#
#        self._k = k
#
#        self._feedback = 1
#        self._hypothesis = 1
#
#        for p in ['h0', 'h1', 'pf', 'pd', 'pm']:
#            self._p[p] = 0
#        for c in ['00', '01', '10', '11']:
#            self._c_sum[c] = 0
#
#        self._min_th = in_th
#        self._max_th = in_th
#        self._delta_th = delta_th
#
#        self._min_th_limit = min_th
#        self._max_th_limit = max_th
#
#        self._th = in_th
#        self.insert_th(in_th)
#
#
#    @property
#    def feedback(self):
#        """
#        Feedback property getter
#        @ret _feedback
#        """
#        return self._feedback
#
#
#    @feedback.setter
#    def feedback(self, val):
#        """
#        Feedback property setter.
#        @param val New feedback value
#        """
#        self._feedback = val
#
#
#    def insert_th(self, th):
#        """
#        Insert a new threshold in list of usable thresholds.
#        Add all intermediate thresholds if necessary.
#        @param th New threshold
#        """
#        def new_th(self, th):
#            """
#            New Threshold initialization.
#            @param th
#            """
#            self._pd[th] = self._pf[th] = self._pm[th] = 1.0
#            self._r[th] = 0.0
#
#            self._c[th] = {}
#            for c in ['00', '01', '10', '11']:
#                self._c[th][c] = 0
#
#        # Insert thresholds between low and high
#        new_th(self, th)
#
#        # update min and max threshold
#        self._max_th = max(self._max_th, th)
#        self._min_th = min(self._min_th, th)
#
#
#    def calculate_w(self, th):
#        """
#        w function.
#        @param th Threshold
#        """
#        num = self._pd[th] * (1.0 - self._pf[th])
#        den = self._pf[th] * (1.0 - self._pd[th])
#
#        try:
#            return log10(num / den)
#        except:
#            return 1.0
#
#    def calculate_Mu(self, th, N):
#        """
#        calculate_Mu function.
#        @param th Threshold
#        @param N
#        """
#
#        elem_1 = 0
#        try:
#            elem_1 = (1.0/N) * log10(self._p['h0'] / self._p['h1'])
#        except:
#            pass
#
#        elem_2 = 0
#        try:
#            elem_2 = log10((1.0-self._pf[th]) / (1.0-self._pd[th]))
#        except:
#            pass
#
#        return elem_1 + elem_2
#
#
#    #::TODO:: pq tem o parametro signal que nao esta na lista de parametros, e nessa lista tem um 'energy' que nao eh parametro??
#    def bayesian_hypothesis(self, th, signal):
#        """
#        Calculate bayesian hipthosis
#        @param th Threshold
#        @param energy Calculated energy
#        @param signal
#        """
#        N = signal.size
#
#        #energy = np.sum(signal) / N
#        #return 1 if energy > th else -1
#
#        # OLD (BUT CORRECT) IMPLEMENTATION OF THE BAYESIAN DETECTOR
#        # @WARNING Without numpy this is a MAJOR bottleneck
#        energy = np.sum(np.multiply([self.calculate_w(th)] * N,
#                                    np.sign(np.subtract(signal, th))))
#
#
#        s = (energy/N) - self.calculate_Mu(th, N)
#        return 1 if s > 0 else -1
#
#
#    #::TODO: parametro th aparece na documentacao mas nao eh um parametro da funcao!
#    def update_global_counter(self, bayes_hyp):
#        """
#        Update values of PD, PF, P, C, etc, based on bayesian hypothesis and the feedback
#        @param th Threshold utilized
#        @param bayes_hyp Bayes hypothesis. 1 (occupied) or 0 (vacant)
#        """
#        c = ''
#        th = self._th
#
#        # Feedback says channel is free ...
#        if self.feedback == 0:
#            # ... and we too
#            if bayes_hyp < 0:
#                c = '00'
#            # ... but we no
#            else:
#                c = '10'
#
#                # Need to increase threshold
#                if th == self._max_th and th < self._max_th_limit:
#                    self.insert_th(th + self._delta_th)
#        # Feedback says channel is occupied ...
#        else:
#            # ... and we too
#            if bayes_hyp > 0:
#                c = '11'
#            # ... but we no
#            else:
#                c = '01'
#
#                if th == self._min_th and th > self._min_th_limit:
#                    self.insert_th(th - self._delta_th)
#
#        # update counter
#        self._c_sum[c] += 1.0
#
#        s = 0.0
#        for c in self._c_sum:
#            s += self._c_sum[c]
#
#        self._p['h0'] = (self._c_sum['00'] + self._c_sum['10']) / s
#        self._p['h1'] = (self._c_sum['11'] + self._c_sum['01']) / s
#
#
#    def update_th_counter(self, signal):
#        """
#        Update values of counters specifics of a threshold
#        @param signal Signal received on antenna
#        """
#        th = self._th
#        th_p = self._th - self._delta_th
#        th_n = self._th + self._delta_th
#
#        self.update_th(th, self._hypothesis)
#
#        if th_p in self._r:
#            self.update_th(th_p, self._hypothesis)
#
#        if th_n in self._r:
#            self.update_th(th_n, self._hypothesis)
#
#
#    def update_th(self, th, hyp):
#        """
#        Update the threshold.
#        @param th Current Threshold
#        @param hyp Bayesian hypothesis regarding channel status
#        """
#
#        c = ''
#
#        # Feedback says channel is free ...
#        if self.feedback == 0:
#            # ... and we too
#            if hyp < 0:
#                c = '00'
#            # ... but we no
#            else:
#                c = '10'
#        # Feedback says channel is occupied ...
#        else:
#            # ... and we too
#            if hyp > 0:
#                c = '11'
#            # ... but we no
#            else:
#                c = '01'
#
#        # update counter
#        self._c[th][c] += 1.0
#
#        s00 = self._c_sum['00']
#        s01 = self._c_sum['01']
#        s10 = self._c_sum['10']
#        s11 = self._c_sum['11']
#
#        # update pf
#        try:
#            self._pf[th] = self._c[th]['10'] / (s00 + s10)
#        except ZeroDivisionError:
#            self._pf[th] = 0
#
#        # update pd
#        try:
#            self._pd[th] = self._c[th]['11'] / (s01 + s11)
#        except ZeroDivisionError:
#            self._pd[th] = 0
#
#        # update pf
#        try:
#            self._pm[th] = self._c[th]['01'] / (s01 + s11)
#        except ZeroDivisionError:
#            self._pm[th] = 0
#
#        # update threshold bayesian risk. IMPORTANT !!!
#        r = (self._pf[th] * self._p['h0'] + self._k * self._pm[th] * self._p['h1'])
#        self._r[th] = r
#
#
#    # ::TODO:: bayes_hyp eh um parametro, mas nao eh usado na funcao!
#    def get_min_risk(self, bayes_hyp):
#        """
#        Get minimum bayes risk and threshold.
#        @param bayes_hyp
#        @return Tuple (risk:threshold)
#        """
#        min_risk = min_th = 1000
#
#        for th in sorted(self._r.iterkeys()):
#            risk = self._r[th]
#
#            if (risk * 0.999) < min_risk:
#                min_risk = risk
#                min_th = th
#
#        return min_risk, min_th
#
#    #:TODO:: o nome do paramtero eh signal, mas na doc tem um 'energy'
#    def decision(self, signal):
#        """
#        Method called for a USRP block (probably bayesian_detector).
#        @param energy Signal Energy
#        @param signal
#        """
#        #hypothesis
#        bayes_hyp = self.bayesian_hypothesis(self._th, signal)
#        self._hypothesis = bayes_hyp
#
#        # update counters
#        self.update_global_counter(bayes_hyp)
#
#        # update bayes
#        self.update_th_counter(signal)
#
#        # ::TRICKY::
#        # The original implementation first check if r[th] < r[th-Delta] and r[th] < r[th+Delta]
#        # If the above condition is true, then th = th/2
#        # else, does the code below
#        bayes_r, self._th = self.get_min_risk(bayes_hyp)
#
#        # Save all data
#        Logger.append('bayes_decision', 'threshold', self._th)
#        #Logger.append('bayes_decision', 'hypothesis', 1 if bayes_hyp > 0 else 0 )
#        Logger.append('bayes_decision', 'feedback', self.feedback)
#        Logger.append('bayes_decision', 'real_state', Logger._ch_status)
#        Logger.append('bayes_decision', 'risk', self._r[self._th])
#        Logger.append('bayes_decision', 'energy', np.sum(signal)/signal.size)
#
#        return 1 if bayes_hyp > 0 else 0, 0.0


class BayesLearningThreshold2(AbstractAlgorithm):
    """
    Class for learning thresholds with bayes hypothesis.
    """

    def __init__(self, in_th, min_th, max_th, delta_th, k):
        """
        CTOR
        @param in_th Initial threshold.
        @param min_th Minimum threshold.
        @param max_th Maximum threshold.
        @param k Bayesian k factor.
        """
        Logger.register('bayes_decision', ['threshold', 'decision', 'risk']) 

        self._feedback = self._feedback_prev =  -1
        self._delta_th = delta_th
        self._min_th_limit = min_th
        self._max_th_limit = max_th

        self._k = k
        self._th = in_th

        self.init(in_th)


	self._th_dec = {}

	self._xx = {};
	self._xx[0] = {0: "00", 1: "01"}
	self._xx[1] = {0: "10", 1: "11"}
    

    def init(self, in_th):
        # Initialize data structures
        self._p = {}

	self._black_list = []
        self._c = {}
        self._c_sum = {}
        self._r = {}

        for p in ['h0', 'h1', 'pf', 'pd', 'pm']:
            self._p[p] = 0
        for c in ['00', '01', '10', '11', 'ones', 'zeroes', '0', '1']:
            self._c[c] = 0.0
        self.t = { 1: {1: '11', 0: '10'}, 0: {1: '01', 0: '00'} }

	#i = self._min_th_limit
	#while i <= self._max_th_limit:
        #	self.insert_th(i)
	#	i+= self._delta_th
	self.insert_th( in_th )


    @property
    def feedback(self):
        """
        Feedback property getter
        @ret _feedback
        """
	if self._feedback != -1:
        	return self._feedback
	else:
		return self._feedback_prev


    @feedback.setter
    def feedback(self, val):
        """
        Feedback property setter.
        @param val New feedback value
        """
	self._feedback_prev = self._feedback
        self._feedback = val


    def insert_th(self, th):
        """
        Insert a new threshold in list of usable thresholds.
        Add all intermediate thresholds if necessary.
        @param th New threshold
        """
        if th in self._r:
            return;

        def new_th(self, th):
            """
            New Threshold initialization.
            @param th
            """
            self._r[th] = 0.5

            self._c[th] = {}
            for c in ['00', '01', '10', '11', 'zeroes', 'ones']:
                self._c[th][c] = 0.0
            self._p[th] = {}
            for c in ['pd', 'pf', 'pm', 'h0', 'h1']:
                self._p[th][c] = 0.0

        # Insert thresholds between low and high
        new_th(self, th)


    def calculate_w(self, th):
        """
        w function.
        @param th Threshold
        """
        num = self._p[th]['pd'] * (1.0 - self._p[th]['pf'])
        den = self._p[th]['pf'] * (1.0 - self._p[th]['pd'])

        
        try:
            r =  log10(num/den)
        except:
            r = 1.0
        return r

    def calculate_Mu(self, th, N):
        """
        calculate_Mu function.
        @param th Threshold
        @param N
        """

        elem_1 = 0
        try:
            #elem_1 = (1.0/N) * log10(self._p[th]['h0'] / self._p[th]['h1'])
            elem_1 = (1.0/N) * log10(self._p['h0'] / self._p['h1'])
        except:
            pass

        elem_2 = 0
        try:
            elem_2 = log10((1.0-self._p[th]['pf']) / (1.0-self._p[th]['pd']))
        except:
            pass

        return elem_1 + elem_2


    def bayesian_hypothesis(self, th, signal):
        """
        Calculate bayesian hipthosis
        @param th Threshold
        @param signal
        """
        N = signal.size
	th_r = math.e ** th
        energy = np.sum(signal) / N

	#l = list(np.sign(np.subtract(signal, th_r)))
        #ones   = l.count(1)
        #zeroes = l.count(-1) + l.count(0)
        ones   = 1 if energy > th_r else 0
        zeroes  = 1 if energy < th_r else 0

        self._c[th]['zeroes'] = zeroes
        self._c[th]['ones']   = ones
	self._th_dec[th] =  1 if energy > th_r else 0

        return 1 if energy > th_r else 0

        # OLD (BUT CORRECT) IMPLEMENTATION OF THE BAYESIAN DETECTOR
        # @WARNING Without numpy this is a MAJOR bottleneck

        #w = self.calculate_w(th)
        #mu = self.calculate_Mu(th, N)

	#l = list(np.sign(np.subtract(signal, th_r)))
        #ones   = l.count(1)
        #zeroes = l.count(-1) + l.count(0)

        #self._c[th]['zeroes'] = zeroes
        #self._c[th]['ones']   = ones

        #energy = np.sum(np.multiply([w] * N, np.sign(np.subtract(signal, th_r)))-mu)
        #s = ((energy/N) - mu)
	#dec = 1 if s > 0 else 0
	#self._th_dec[th] = dec 

        #return dec 

    #::TODO: parametro th aparece na documentacao mas nao eh um parametro da funcao!
    def update_global_counter(self):
        """
        Update values of PD, PF, P, C, etc, based on bayesian hypothesis and the feedback
        @param th Threshold utilized
        @param bayes_hyp Bayes hypothesis. 1 (occupied) or 0 (vacant)
        """
        # update counter
        self._c[str(self.feedback)] += 1.0

        self._p['h0'] = self._c['0'] / sum(self._c[c] for c in ['0', '1'])
        self._p['h1'] = self._c['1'] / sum(self._c[c] for c in ['0', '1'])

    def update_th_counter(self, signal):
        """
        Update values of counters specifics of a threshold
        @param signal Signal received on antenna
        """
        th = self._th
        th_p = max(th - self._delta_th, self._min_th_limit)
        th_n = min(th + self._delta_th, self._max_th_limit)

	if th_p != th:
		self.insert_th(th_p)
	if th_n != th:
		self.insert_th(th_n)

	for t in self._r.iterkeys() :
		if t not in self._black_list:
			self._black_list.append( t )
			self.update_th(t, self.bayesian_hypothesis(t, signal))
	#if self._feedback == 1:
	#	for t in arange(th_p, th, self._delta_th):
	#		self.update_th(t, self.bayesian_hypothesis(t, signal))
	#elif self._feedback == 0:
	#	for t in arange(th, th_n, self._delta_th):
	#		self.update_th(t, self.bayesian_hypothesis(t, signal))

	#if th_p != th:
	#	self.insert_th(th_p)
	#	self.update_th(th_p, self.bayesian_hypothesis(th_p, signal))
	#if th_n != th:
	#	self.insert_th(th_n)
	#	self.update_th(th_n, self.bayesian_hypothesis(th_n, signal))


    def update_th(self, th, hyp):
        """
        Update the threshold.
        @param th Current Threshold
        @param hyp Bayesian hypothesis regarding channel status
        """
        self._c[th][self.t[self.feedback][0]] += float(self._c[th]['zeroes'])
        self._c[th][self.t[self.feedback][1]] += float(self._c[th]['ones'])

	self._p[th]['h0'] = (self._c[th]['00']+self._c[th]['01']) / sum(self._c[th][c] for c in ['00', '01', '10', '11'])
        self._p[th]['h1'] = (self._c[th]['10']+self._c[th]['11']) / sum(self._c[th][c] for c in ['00', '01', '10', '11'])

        # update pf
        try:
            self._p[th]['pf'] = self._c[th]['01'] / sum(self._c[th][c] for c in ['01', '00'])
        except ZeroDivisionError:
            self._p[th]['pf'] = 1.5

        # update pd
        try:
            self._p[th]['pd'] = self._c[th]['11'] / sum(self._c[th][c] for c in ['10', '11'])
            self._p[th]['pm'] = 1.0 -  self._p[th]['pd']
        except ZeroDivisionError:
            self._p[th]['pd' ] = 1.5
            self._p[th]['pm' ] = 1.5

        # update threshold bayesian risk. IMPORTANT !!!
        r = (self._p[th]['pf'] * self._p['h0'] + self._k * self._p[th]['pm']* self._p['h1'])
	self._r[th] = r


    def get_min_risk(self):
        """
        Get minimum bayes risk and threshold.
        @param bayes_hyp
        @return Tuple (risk:threshold)
        """
        rl = list(OrderedDict(sorted(self._r.items())).iterkeys() )
        rt = list(OrderedDict(sorted(self._r.items())).iteritems())
    
	if self.feedback == 1:
		iterator = reversed(sorted(self._r.iterkeys()))
	elif self.feedback == 0:
		iterator = sorted(self._r.iterkeys())
	else:
		raise NotImplementedError

        min_th = self._th
        min_risk = self._r[min_th]
	at_least_one = False
        for th in iterator:
	    if self._th_dec[th] != self.feedback:
		continue
            at_least_one = True

            risk = self._r[th]
	    #print "r: ", risk, "[", min_risk ,"] d:", self._th_dec[th], " f:", self.feedback
            if risk < min_risk:
                min_risk = risk
                min_th = th

	if at_least_one == False:
		if self.feedback == 1:
			min_th = sorted(self._r)[0]
			min_risk = self._r[min_th]
		elif self.feedback == 0:
			min_th = sorted(self._r)[len(self._r)-1]
			min_risk = self._r[min_th]
		else:
			raise NotImplementedError

        return min_risk, min_th
    
        #if (idx == 0) or ( (idx < len(rl)-1) and rl[idx] > rl[idx-1] and rl[idx] > rl[idx+1]):
        #    for th in sorted(self._r.iterkeys()):
        #        risk = self._r[th]
    
        #        if risk < min_risk:
        #            min_risk = risk
        #            min_th = th
        #else:
        #    min_th =   rt[int(idx/2)][0]
	#    idx = 0
	#    while idx < len(rl) and min_th > rl[idx]:
	#	idx+=1
	#    min_th = rl[idx]
	#    min_risk = self._r[min_th]


        #return min_risk, min_th

    #:TODO:: o nome do paramtero eh signal, mas na doc tem um 'energy'
    def decision(self, signal):
        """
        Method called for a USRP block (probably bayesian_detector).
        @param energy Signal Energy
        @param signal
        """
        #hypothesis
        # update counters

	if self._feedback == 0 or self._feedback == 1:
        	self.update_global_counter()

		th = self._th
		r = self._r[th]
		while True:
			# update bayes
			self.update_th_counter(signal)
		    
			# update risk
			bayes_r, self._th = self.get_min_risk()

			# invalidate threshold. Wait until a new is provided
			if th == self._th or r == bayes_r :
				self.feedback = -1 
				break
			th = self._th
			r = self._r[th]
		# Clear black list of threshold
		self._black_list = []
		#print "d:", self.bayesian_hypothesis(self._th, signal), " f:", self.feedback, " t:", math.e ** self._th, " e:", sum(signal)/50

	bayes_hyp = self.bayesian_hypothesis(self._th, signal)

	# Save all data
	dec = 1 if bayes_hyp > 0 else 0
        Logger.append('bayes_decision', 'decision', self._xx[Logger._ch_status][dec])
	Logger.append('bayes_decision', 'threshold', self._th)
	Logger.append('bayes_decision', 'risk', self._r[self._th])
        return dec, 0.0
