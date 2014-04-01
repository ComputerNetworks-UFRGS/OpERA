#!/usr/bin/env python

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

""
# @package ss_utils

import sys
import os
import random
import shutil
import unittest

# ::TODO:: Discover how to include patches externally
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../"))
sys.path.insert(0, path)

# OpERA UUT 
from logger import Logger


class QaUtils(unittest.TestCase):
    """
    QA tests for all functionality in OpERA/utils.
    """

    def test_logger(self):
        """
        Test the Logger dump and dump_plot functions.
        """

        OBJ_PREFIX = 'obj_'
        ITEM_PREFIX = 'item_'

        num_obj = 5
        num_items = 4

        Logger._enable = True

        # Register objects and items
        for i in xrange(num_obj):
            obj_name = 'obj_' + str(i)

            obj_items = []
            for j in xrange(num_items):
                obj_items.append(ITEM_PREFIX + str(j))

            Logger.register(obj_name, obj_items)

        # Fill data
        for i in xrange(num_obj):
            obj_name = OBJ_PREFIX + str(i)

            for i in xrange(50):
                j = random.randrange(1, num_items, 1)

                Logger.append(obj_name, ITEM_PREFIX + str(j), random.randrange(1, 1000, 1))

        Logger.dump('./dump', '/config1', 1)
        Logger.dump_plot('./dump', '/config1',
                         [('obj_1', ['item_1', 'item_2']),
                          ('obj_2', ['item_2'])],
                         1)

        shutil.rmtree('./dump')


if __name__ == '__main__':
    unittest.main()
