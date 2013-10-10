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

## @package device
# Module with all classes related to device specific

from abc import ABCMeta, abstractmethod
import time
from OpERABase import OpERABase

## Abstract device
# Interface for a specific hardware
class AbstractDevice(OpERABase):
	__metaclass__ = ABCMeta

	## CTOR
	def __init__(self, name="AbstractDevice"):
		OpERABase.__init__(self, name=name)

	## Getter for center_freq property.
	# @return Device center frequency.
	@property
	def center_freq(self):
		return self._get_center_freq()

	## Setter for center_freq property.
	# @param the_channel Channel object.
	@center_freq.setter
	@abstractmethod
	def center_freq(self, the_channel):
		if not type(the_channel) == float and not type(the_channel) == int:
			self._set_center_freq( the_channel.freq )
			the_channel = the_channel.freq
		else:
			self._set_center_freq( the_channel )


	@abstractmethod
	def _get_center_freq(self):
		pass

	@abstractmethod
	def _set_center_freq(self, freq):
		pass


	## Getter for samp_rate property
	# @return Device sample rate
	@property
	def samp_rate(self):
		return self._get_samp_rate()

	## Setter for samp_rate property.
	# @param samp_rate The sample rate (integer).
	@samp_rate.setter
	@abstractmethod
	def samp_rate(self, samp_rate):
		self._set_samp_rate( samp_rate )

	## Device specific getter  for sample rate.
	# Must be implemented on derived classes.
	# @return Sample rate
	@abstractmethod
	def _get_samp_rate(self):
		pass

	## Device specific setter  for sample rate.
	# Must be implemented on derived classes.
	# @param samp_rate Sample rate.
	@abstractmethod
	def _set_samp_rate(self, sample_rate):
		pass

	## Getter for gain property.
	# @return Device gain.
	@property
	def gain(self):
		self._gain = self._get_gain()
		return self._gain

	## Device specific getter for gain.
	# Must be implemented on derived classes.
	# @return Gain.
	@abstractmethod
	def _get_gain():
		pass

	## Setter for gain property.
	# @param gain The gain (float).
	@gain.setter
	def gain(self, gain):
		self._set_gain( gain )
		self._gain = gain

	## Device specific gain for sample rate.
	# Must be implemented on derived classes.
	# @param gain.
	@abstractmethod
	def _set_gain(self, gain):
		pass
