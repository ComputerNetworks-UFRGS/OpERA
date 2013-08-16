# @package ss_utils

import random
from proxy import Proxy
from math import *

## Class that represents a channel
class Channel(object):

	## CTOR
	#
	# @param	ch Channel number
	# @param	freq Channel central frequency
	# @param	bw	Channel bandwidth
	def __init__(self, ch, freq, bw):
		self._channel = ch
		self._freq 	 = freq
		self._bw 	 = bw

	## Get channel
	@property
	def channel(self):
		return self._channel

	## Get frequency
	@property
	def freq(self):
		return self._freq

	## Get bandwidth
	@property
	def bw(self):
		return self._bw

	def __repr__(self):
		return repr("Channel %d (%f)" % (self.channel, self.freq))

################################################################################
# ChannelModel is obsolete
################################################################################
## Class representing a channel usage model
# The important parameters:
#   - exp: Poisson exponent distribution
#   - freq_idle: Idle frequency
#   - freq_occupied: Occupied frequency
#   - channel: Used to maskerade the ChannelModel (pretend that channel obj is the REAL behavior)
class ChannelModel( Channel ):

	## CTOR
	# @param exp
	# @param freq_idle
	# @param freq_occupied
	# @param channel
	def __init__(self, idle_param, occupied_param, channel):
		Channel.__init__(self, ch = channel.channel, freq = channel.freq, bw = channel.bw)

		self._exp = exp
		self._ch_param = [ idle_param, occupied_param]
		self._cur_channel = random.randrange(0, 2, 1)


	## Convert ChannelModel to Channel only object
	def to_channel(self):
		self._cur_channel = (self._cur_channel + 1) % 2
		return Channel(ch = self.channel, freq = self._ch_param[ self._cur_channel ][0], bw = self.bw)

	## Return time in a specific channel
	@property
	def time(self):
		r = random.random()
		return self._ch_param[ self._cur_channel ][1] / exp(r * 1.0)
