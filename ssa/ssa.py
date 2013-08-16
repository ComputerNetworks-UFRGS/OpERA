# @package spectrum_sensing_automaton
# Module with the SSA implementation

from threading import Thread
from ss_utils import SSA_STATES

import sys

## SSA machine state
#
# Runs forever. Inherits from Thread
# Implements a simplified version of the state machine specified in the IEEE 802.22 Std.
class SSA(Thread):

	## CTOR
	# @param configuration	Object of class configuration
	# @param device			Device specific configuration
	def __init__(self, configuration, device):
		Thread.__init__(self)

		self._mDev = device
		self._mConf = configuration
		self._mState =  SSA_STATES.INITIALIZE

		self.mChannelList = []
		self.mFreeChannelList = []


	## Update state machine
	# @return Next state
	def updateState(self):
		self._mState = self.nextState()

		return self._mState

	## Returns the next state machine state
	# @return Next state
	def nextState(self):
		state = self._mState

		# Initialized ? Start sensing
		if state == SSA_STATES.INITIALIZE:
			return SSA_STATES.SS_1

		# Sensed a channel? Go to next
		if state == SSA_STATES.SS_1:
			return SSA_STATES.SS_1_NEXT_CH

		if state == SSA_STATES.SS_1_NEXT_CH:
			# List not empy ? Next Channel
			if self.mChannelList != None and len(self.mChannelList) > 0:
				return SSA_STATES.SS_1

			# Free List empy? Abort
			#if self.mFreeChannelList == None or len(self.mFreeChannelList) == 0:
			#	return SSA_STATES.ABORT

			return SSA_STATES.SS_2

		if state == SSA_STATES.SS_2:
			return SSA_STATES.INITIALIZE

		return SSA_STATES.ABORT

	##
	#
	def nextChannel(self):
		return self.mChannelList.pop( 0 )

	## Initialize SSA configuration (aka reset)
	def initialize(self):
		self.mChannelList = self._mConf.priorityChannelList()
		self.mFreeChannelList = []

	## Finish SSA execution
	def finish(self):
		print "## Finishing Execution ##\n"

	## Abort SSA execution
	def abort(self):
		print "## Aborting ##"
		sys.exit(0)

	## Sense a channel
	def senseChannel(self):
		channel_obj = self.mChannelList.pop( 0 )
		out = self._mDev.senseChannel( channel_obj )

		if out == 0:
			self.mFreeChannelList.append( channel_obj )

	def stage2(self):
		print "Free channels:"
		for k in self.mFreeChannelList:
			print k.channel

	## Execution starts here. 
	def run(self): 
		# Start Device
		self._mDev.start()

		state = self._mState

		# Machine state. Should exit only when something odd occurs
		while state != SSA_STATES.ABORT:

			if state == SSA_STATES.INITIALIZE:
				self.initialize()

			if state == SSA_STATES.SS_1:
				self.senseChannel()

			if state == SSA_STATES.SS_2:
				self.stage2()

			#if state == ABORT:
			#	abort()

			state = self.updateState()

		self.finish()

		return 1 if state != SSA_STATES.ABORT else 0
