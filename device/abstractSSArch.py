## @package device

from abc import ABCMeta, abstractmethod

## Abstract class for a SS architecture.
# Provides simple generic method that must be implemented for all SS architectures.
class AbstractSSArch(object):

	## CTOR
	def __init__(self):
		pass

	## Must be implemented on derived classes.
	# @param the_list List of Channels objects to sense.
	@abstractmethod
	def senseChannel(self, the_list):
		pass


	## Sense a list of channels.
	# @param the_list     List of channels to sense.
	# @param sensing_time Sensing duration in each channel.
	# @return Sensing information of all channels.
	def senseChannelList(self, the_list, sensing_time):
		data = []

		for channel in the_list:
			d = self.senseChannel( channel, sensing_time )
			data.append( d )

		return data
