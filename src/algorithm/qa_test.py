#!/usr/bin/python

## @package algorithm

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, path)

import unittest
import random

# Modules  tested
from feedbackAlgorithm import FeedbackAlgorithm, ExponentialTimeFeedback, KunstTimeFeedback

# Other modules needed
from device import radioDevice
from abstractAlgorithm import AbstractAlgorithm


## Test algorithm  module
class QaAlgorithm(unittest.TestCase):

	## Test the feedback algorithm
	def test_feedback_001(self):
		mi = 1,
		ma = 256
		base = 3

		obj = ExponentialTimeFeedback( min_time = mi,
				max_time = ma,
				base = base )

		# Estado inicial
		self.assertEqual(False, obj.feedback() )
		
		obj.wait() # wait = 0

		# 3 ^ 0 == 1 (demos 1 wait)
		# wait volta para 0
		self.assertEqual(True, obj.feedback() )

		# Testa se voltou direito
		self.assertEqual(False, obj.feedback() )

		# Aumentamos o tempo de sensoriamento 3^1 = 3
		obj.increase_time()
		self.assertEqual(False, obj.feedback() )
		obj.wait() # wait = 1
		self.assertEqual(False, obj.feedback() )

		obj.wait() # wait = 2
		obj.wait() # wait = 3
		self.assertEqual(True, obj.feedback() ) # volta wait para 0
		self.assertEqual(False, obj.feedback() )


		obj.decrease_time() # reseta tempo 3^0 = 1
		obj.wait() # wait = 1
		self.assertEqual(True, obj.feedback() ) # volta wait para 0

	## Test the feedback algorithm
	def test_feedback_002(self):
		obj = KunstTimeFeedback()

		# Estado inicial
		self.assertEqual(False, obj.feedback() )
		
		obj.wait() # wait = 1

		# 2 ^ 0 == 1
		# wait = 0
		self.assertEqual(True, obj.feedback() )

		# Aumentamos o tempo de sensoriamento 2^1 = 2
		obj.increase_time()
		self.assertEqual(False, obj.feedback() )
		obj.wait() # wait = 1
		self.assertEqual(False, obj.feedback() )

		obj.wait() # wait = 2
		self.assertEqual(True, obj.feedback() ) # volta wait para 0
		self.assertEqual(False, obj.feedback() ) # volta wait para 0

		obj.wait() # wait = 1
		obj.wait() # wait = 2
		obj.wait() # wait = 3
		obj.wait() # wait = 4

		obj.increase_time() # 2^2 = 4
		self.assertEqual(True, obj.feedback() ) # volta wait para 0
		self.assertEqual(False, obj.feedback() ) # volta wait para 0

		obj.decrease_time() # Deve ficar 2^1 = 2

		obj.wait()
		obj.wait()
		self.assertEqual(True, obj.feedback() ) # volta wait para 0
		self.assertEqual(False, obj.feedback() ) # volta wait para 0



if __name__ == '__main__':
	unittest.main()
