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

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
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
        obj.wait() # wait = 1

        # 3 ^ 0 == 1 (wait is 1)
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
