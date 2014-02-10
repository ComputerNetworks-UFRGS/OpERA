import random						as rd
import numpy						as np
from array							import *
from utils	                 		import Logger
from algorithm.abstractAlgorithm	import AbstractAlgorithm

	
###############################################################################################
# This is my Enum. Shining!!!
class Actions:
	DECR = -1
	HOLD = 0
	INCR = 1

###############################################################################################

class SARSA( AbstractAlgorithm ):

	## CTOR.
	def __init__(
			self,
			alpha 	= 0.3,
			gamma 	= 1.0,
			epsilon = 0.1,
			verbose = False,
			min_th = 0.0,
			max_th = 100.0,
			delta_th = 1.0
			):

		#  "The learning rate determines to what extent the newly
		#  acquired information will override the old information. A factor of 0
		#  will make the agent not learn anything, while a factor of 1 would make
		#  the agent consider only the most recent information."
		self.alpha = float( alpha )
		
		# According to Wikipedia: "The discount factor determines the importance
		# of future rewards. A factor of 0 will make the agent "opportunistic" by only
		# considering current rewards, while a factor approaching 1 will make it
		# strive for a long-term high reward."
		self.gamma = float( gamma )

		# Probabilidade de executar uma acao randomicamente.
		self.epsilon = float( epsilon )
		
		# 
		self.verbose = verbose

		# min_th is the lowest threshold
		self.minTh =min_th 

		# max_th is the highest threshold
		self.maxTh = max_th

		# gap is the... gap between states, so, the number of states
		#  will be (max_th - min_th) / gap
		self.gap = delta_th 

		# The feedback
		self._feedback = 0.0

		# Number of Increase Actions in sequence
		self.actionI = 0
		# Number of Decrease Actions in sequence
		self.actionD = 0

		# Set to '1' when a feedback is received
		self.feedbackReceived = True

		# Count how many feedbacks are received by the algorithm.
		# Used only for info gattering
		self.feedbackCounter = 0
		
		# 
		self.cycleCounter = 0
		self.cycleCounterMax = int( 406383 / 8 )

		# Execution Time of this class
		self.mTime = 0.0
		
		# Enum for actions
		self.Action = Actions( )

		# Load in self.actions the possible actions
		self.actions = self.getActionList()
		# Load in self.states the possible actions
		self.states = self.getStateList()

		# How many states?
		self.nstates = len( self.states )
		# Max jump
		self.maxJump = int( self.nstates / 50 )
		
		# Map the threshold value to the index of this threshold in self.states
		self.stateMap = { '0.0' : 0 }
		for i in range ( self.nstates ):
			self.stateMap[ self.states[ i ] ] = i

		# How many actions I'm using?
		self.nactions = len( self.actions )
		
		# Build an empty QTable with size (nactions * nstates)
		self.QTable = self.buildQTable()

		# Guess what?
		self.s = self.getInitialState()
		self.a = self.eGreedySelection( self.s )
		
		# May be messy
		if self.verbose:
			self.printQTable()

		Logger.register( 'bayes_learning', [ 'hiphotesis', 'feedback', 'state', 'reward', 'action' ] )


###############################################################################################

	def printQTable( self ):
		for i in range( self.nstates ):
			print "%.4f  %s" %( self.states[ i ], self.QTable[ i ] )


###############################################################################################
	# 
	def finish( self ):
		print "SARSA Time: %.4f" %( self.mTime )
		print "States: %d [%.2f, %.2f, %.6f]" %( self.nstates, self.minTh, self.maxTh, self.gap )
		print 'Received ' 	+ str( self.feedbackCounter ) + ' feedbacks'
		print 'Alpha: ' 	+ str( self.alpha )
		print 'Gamma: ' 	+ str( self.gamma )
		print "Epsilon: %.4f" %( self.epsilon )


###############################################################################################

	# Feedback property getter
	# @ret _feedback
	@property
	def feedback( self ):
		return self._feedback


###############################################################################################

	## Feedback property setter
	# @param val New feedback value
	@feedback.setter
	def feedback( self, val ):
		#
		self._feedback 			= val
		self.feedbackReceived 	= True
		self.feedbackCounter 	+= 1


###############################################################################################

	# Defined Actions:
	#	-1: Decrease threshold
	#	 0: Keep threshold
	#	 1: Increase threshold
	def getActionList( self ):
		return array( 'i', [ self.Action.DECR, self.Action.HOLD, self.Action.INCR ] )


###############################################################################################
	# Generate State List
	def getStateList( self ):
		# Min to Max with the gap
		return np.arange( self.minTh, self.maxTh, self.gap )


###############################################################################################

	def getInitialState( self ):
		# Last element. Believe it.
		#return self.states[ -1 ]
		# Starting from the middle.
		#return self.states[ int( self.nstates/2 ) ]
		# Lowest threshold, Bayes mode
		return self.states[ 0 ]


###############################################################################################

	def buildQTable( self ):
		# Filled with zeros
		return [ [ 0 for i in range( self.nactions ) ] for i in range( self.nstates ) ]


###############################################################################################

	def getBestAction( self, state ):
		# Get the line corresponding to the state
		stateRow = self.QTable[ self.stateMap[ state ] ]
		# Get action with more rewards ...
		maxVal = max( stateRow )
		# and get the index of this action
		maxValIdx = stateRow.index( maxVal )
		
		if self.verbose:
			print stateRow
			print "MaxVal: %.4f  Idx: %d\n" %( maxVal, maxValIdx )
		
		return maxValIdx

###############################################################################################
	# Chooses an action for the given state
	def eGreedySelection( self, state ):

		idx = 0

		# Higher probability. Get the action with more rewards.
		if ( rd.random() > self.epsilon ):
			idx = self.getBestAction( state )
		else:
			# Randonly choosen action
			idx = rd.randint( 0, self.nactions-1 )

		return self.actions[ idx ]


###############################################################################################
	# 
	def doAction( self, state, action ):

		finalStateIndex = curIdx = self.stateMap[ state ]
		
		if action == self.Action.HOLD:
			#self.actionI = 0
			#self.actionD = 0
			pass

		elif action == self.Action.DECR:
			self.actionI  = 0
			self.actionD += 1

			stateJump = min( self.actionD, self.maxJump )

			finalStateIndex = max( 0, curIdx - stateJump )

		elif action == self.Action.INCR:
			self.actionI += 1
			self.actionD  = 0

			stateJump = min( self.actionI, self.maxJump )

			finalStateIndex = min( self.nstates-1, curIdx + stateJump )

		return self.states[ finalStateIndex ]


###############################################################################################

	def getReward( self, energy, state ):

		if( self.feedbackReceived == False ):
			return 0
		self.feedbackReceived = False
		
		rw = 0
		myDecision = 0

		if energy > state:
			# Occupied
			myDecision = 1
		else:
			# Busy
			myDecision = 0

		if self._feedback != myDecision:
			rw = -100
		else:
			rw = 10

		return rw


###############################################################################################

	def updateQTable( self, s, a, rw, sp, ap ):
		# Index of current state
		stateIdx = self.stateMap[ s ]
		# Index of next state
		nextStateIdx = self.stateMap[ sp ]
		# Index of current action
		actIdx = self.actions.index( a )
		# Index of next action
		nextActIdx = self.actions.index( ap )
		# Current value in QTable
		curVal = self.QTable[ stateIdx ][ actIdx ]
		# QTable value corresponding to the next state and action
		nextVal = self.QTable[ nextStateIdx ][ nextActIdx ]
		# Update current value
		self.QTable[ stateIdx ][ actIdx ] += self.alpha * ( rw + self.gamma * nextVal - curVal )


###############################################################################################

	def decision( self, energy ):
		energy = np.sum(energy) / energy.size

		self.cycleCounter += 1
		
		if self.cycleCounterMax == self.cycleCounter:
			self.cycleCounter = 0
	
		sp = self.doAction( self.s, self.a )
		rw = self.getReward( energy, sp )
		ap = self.eGreedySelection( sp )

		self.updateQTable( self.s, self.a, rw, sp, ap )

		self.s = sp
		self.a = ap

		#self.epsilon *= 0.999

		Logger.append( 'bayes_learning', 'hiphotesis', 1.0 if energy > self.s else 0.0 )
		Logger.append( 'bayes_learning', 'feedback', self._feedback )
		Logger.append( 'bayes_learning', 'state', 	self.s )
		Logger.append( 'bayes_learning', 'reward', 	rw )
		Logger.append( 'bayes_learning', 'action', 	self.a )

		return 1 if( energy > sp ) else 0, energy
