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

## @package ss_utils

from time import sleep
from abc import abstractmethod
from struct import *

import time
import random
import threading

## Thread representing a channel whose status changes in time.
# Each channel thread must be associated to a Channel object.
# When the center_freq method on the ChannelModeler is called, the corresponding ChannelThread is activated.
# The ChannelThread controls an AbstractDevice object, by changing is central frequency following a random distribution.
# The distribution is a function callback.
class ChannelThread(threading.Thread):

	# Class variable.
	_running = False

	## CTOR.
	# @param channel_modeler ChannelModeler instance.
	# @param device AbstractDevice object instance.
	# @param the_channel Channel object instance.
	# @param dist_callback Distribution callback.
	def __init__(self, channel_modeler, device, the_channel, dist_callback):
		threading.Thread.__init__(self)

		# ctor parameters
		self._channel_modeler = channel_modeler
		self._the_device = device
		self._the_channel = the_channel
		self._dist_callback = dist_callback

		self._active = False

	## Channel Thread thread
	def run(self):

		# 0 = idle
		# 1 = occupied
		status = random.randrange(0, 2, 1)

		# Thread loop
		while ChannelThread._running:
			# if this thread is controlling the device
			if self._active:
				if status:
					print 'Interfering in channel ' + str(self._the_channel)
					self._the_device.center_freq = self._the_channel.freq
				else:
					print 'Setted outside range ' + str(self._the_channel)
					self._the_device.center_freq = 2.0e9

			if self._active:
				time.sleep( self._dist_callback() )
			else:
				time.sleep( 0.1 )

			# Change status betweeen idle <-> occupied
			status = (status+1) % 2

		print 'Thread finished'


	## Enable/disable thread control of USRP
	# @param value True or False
	def active(self, value):
		self._active = value


## Proxy calls an AbstractDevice object.
# This class is used to 'fake' channel changes by intercepting the 'center_freq' call.
class ChannelModeler(object):

	## CTOR.
	# @param device AbstractDevice implementation.
	# @param channel_list List of channels manage by the channel modeler
	# @param dist_callback Distribution Callback
	def __init__(self, device, channel_list, dist_callback ):
		object.__init__(self)

		# Subject is the proxied object.
		object.__setattr__(self, '_device', device)
		object.__setattr__(self, '_curThread', None)

		# dictionary (channel, thread) to easily find the thread given a channel
		object.__setattr__(self, '_threads',
				{channel: ChannelThread(self, device, channel, dist_callback) for channel in channel_list})

		# call start() on all threads
		ChannelThread._running = True
		map(lambda x: x.start(), self._threads.itervalues())

	##
	# @param channel_thread
	def _disable_thread(self, channel_thread):
		if channel_thread:
			channel_thread.active(False)
		else:
			print 'Thread not found!!!!'

	##
	# @param channel_thread
	def _enable_thread(self, channel_thread):
		if channel_thread:
			channel_thread.active(True)
		else:
			print 'Thread not found!!!!'

	## Intercept center_freq call to AbstractDevice
	# @param chann ChannelModel object
	# @param the_semaphore stays here until the semaphore is freed
	def center_freq(self, channel):
		print 'Channel Modeler'
		the_thread = self._threads[ channel ]

		self._disable_thread( self._curThread )                         # disable current thread
		self._enable_thread( the_thread )      # activate it
		object.__setattr__(self, '_curThread', the_thread) # set new current thread based on channel value

	## Python way to proxy a object.
	# Proxy calls to device object.
	def __getattr__(self, var):
		return getattr(self._device, var, None)

	## Python way to proxy a object.
	# Intercept any change to the center_freq property on the AbstractDevice object.
	# @param var Name of the property changed.
	# @param val The new value for this property.
	def __setattr__(self, var, val):
		# Check if is the 'center_freq' parameter
		if hasattr(self, var):
			if var == 'center_freq':
				self.center_freq(val)
			elif var == '_disable_thread':
				self._disable_thread(val)
			elif var == '_enable_thread':
				self._enable_thread(val)
		else:
			self._device.__setattr__(var, val)
