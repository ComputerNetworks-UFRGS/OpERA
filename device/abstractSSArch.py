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

from abc import ABCMeta, abstractmethod
from OpERABase import OpERABase

## Abstract class for a SS architecture.
# Provides simple generic method that must be implemented for all SS architectures.
class AbstractSSArch(OpERABase):

	## CTOR
	def __init__(self, name="AbstractSSArch"):
		OpERABase.__init__(self, name=name)

	## Must be implemented on derived classes.
	# @param the_list List of Channels objects to sense.
	@abstractmethod
	def sense_channel(self, the_list):
		pass


	## Sense a list of channels.
	# @param the_list     List of channels to sense.
	# @param sensing_time Sensing duration in each channel.
	# @return Sensing information of all channels.
	def sense_channel_list(self, the_list, sensing_time):
		data = []

		for channel in the_list:
			d = self.sense_channel(channel, sensing_time)
			data.append(d)

		return data
