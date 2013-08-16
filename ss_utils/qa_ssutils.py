#!/usr/bin/env python

## @package ss_utils

import sys, os, random, shutil
import unittest

# ::TODO:: Discover how to include patches externally
path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, path)

# UUT
from logger import Logger

## QA related to all ss_utils classes.
class qa_ssutils(unittest.TestCase):

	## Test Logger class.
	def test_logger(self):
		OBJ_PREFIX = 'obj_'
		ITEM_PREFIX = 'item_'

		num_obj = 5
		num_items = 4

		Logger._enable = True

		# Register objects and items
		for i in xrange( num_obj ):
			obj_name = 'obj_' + str(i)

			obj_items = []
			for j in xrange( num_items ):
				obj_items.append( ITEM_PREFIX + str(j) )

			Logger.register(obj_name, obj_items)

		# Fill data
		for i in xrange( num_obj ):
			obj_name = OBJ_PREFIX + str(i)

			for i in xrange(50):
				j = random.randrange(1, num_items, 1)

				Logger.append(obj_name, ITEM_PREFIX + str(j),
						random.randrange(1, 1000, 1))

		Logger.dump('./dump', '/config1', 1)
		Logger.dump_plot('./dump', '/config1',
				[('obj_1', ['item_1', 'item_2']),
				('obj_2', ['item_2'])],
				1)

		shutil.rmtree('./dump')


if __name__ == '__main__':
	unittest.main ()
