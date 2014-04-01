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

## @package architecture

# ::TODO:: Discover how to include patches externally
# ::TODO:: modules description
import sys
import os
import random

path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../"))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, uhd


# UUT
from rankingArch import *


class QaRanking(gr_unittest.TestCase):
    """
    QA tests related to ranking.
    """

    def setUp(self):
        """
        Set globals for all tests. Called before a test is started.
        """
        self.tb = gr.top_block()

    def tear_down(self):
        """
        Destroy globals for all tests. Called right after a test if finished.
        """
        self.tb = None


    def test_001(self):
        """

        """
        ## TODO
        pass


if __name__ == '__main__':
    gr_unittest.main()
