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

"""
@package utils
"""

import random
from math import *

class Channel(object):
	"""
	Represents a channel with number, central frequency and bandwidth
	"""

	def __init__(self, ch, freq, bw):
		"""
		CTOR
		@param	ch Channel number
		@param	freq Channel central frequency
		@param	bw	Channel bandwidth
		"""
		self._channel = ch
		self._freq 	 = freq
		self._bw 	 = bw

	@property
	def channel(self):
		"""
		Return channel number.
		"""
		return self._channel

	@property
	def freq(self):
		"""
		Return  channel frequency.
		"""
		return self._freq

	@property
	def bw(self):
		"""
		Return channel bandwidth.
		"""
		return self._bw

	def __repr__(self):
		return repr("Channel %d (%f)" % (self.channel, self.freq))
