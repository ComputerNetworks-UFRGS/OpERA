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
@package device
"""

from abc import ABCMeta, abstractmethod

from gnuradio import gr
from abstractArch import AbstractArch

class UHDAbstractArch(AbstractArch, gr.hier_block2):
	"""
	Abstract class for the UHD architectures.
	This is the base class for UHD architectures.
	"""
	
	def __init__(self, name, input_signature, output_signature):
		"""
		CTOR
		@param name
		@param input_signature
		@param output_signature
		"""
		object.__setattr__(self, '_radio_device', None)

		AbstractArch.__init__(self, name=name)
		gr.hier_block2.__init__(
				self,
				name =  name,
				input_signature  = input_signature,
				output_signature = output_signature,
			)


	def set_radio_device(self, radio_device):
		"""
		Set the radio device used for this UHDAbstractArch.
		@param radio_device
		"""
		self._radio_device = radio_device


	def __getattr__(self, name):
		"""
		Intercept any call and forward it to the radio device if possible
		@param name Attribute name
		"""
		if self._radio_device and hasattr(self._radio_device, name):
			return getattr(self._radio_device, name)

		# ::TRICKY::
		# GNURadio uses this return in the connect(...) function
		return gr.hier_block2.__getattr__(self, name)


	@property
	def radio(self):
		"""
		"""
		if self._radio_device is not None:
			return self._radio_device

		raise AttributeError('radio is None')


class UHDSSArch(UHDAbstractArch):
	"""
	Base architecture to spectrum sensing with UHD devices.
	This is the base class for all rx with spectrum sensing paths utilized in the TopBlock class.
	"""

	__metaclass__ = ABCMeta

	def __init__(self, name, input_signature, output_signature):
		"""
		CTOR
		@param radio            RadioDevice
		@param name             SS Arch instance name
		@param input_signature  A gr.io_signature instance.
		@param output_signature A gr.io_signature instance.
		"""
		UHDAbstractArch.__init__(self, name = name,
				input_signature  = input_signature,
				output_signature = output_signature
			)


	@abstractmethod
	def _get_sensing_data(self, channel, sensing_time):
		"""
		Sense channel and return data.
		The channel frequency is already configured when this method is called.
		@param channel Channel object. 
		@param sensing_time Sensing duration.
		@return Sensing data.
		"""
		pass


	def sense_channel(self, channel, sensing_time):
		"""
		SS on a single channel.
		Implements AbstractSSArch abstract method.
		@param the_channel Channel to be sensed.
		@param sensing_time Sensing duration on channel.
		"""

		# save -> sense -> restore

		prev_freq = self.radio.center_freq

		res =  self._get_sensing_data( channel, sensing_time )
		self.radio.center_freq = prev_freq

		return res


	def sense_channel_list(self, channel_list, sensing_time):
		"""
		Sense a list of channels.
		@param the_list     List of channels to sense.
		@param sensing_time Sensing duration in each channel.
		@return Sensing information of all channels.
		"""
		data = []

		for channel in the_list:
			d = self.sense_channel(channel, sensing_time)
			data.append(d)

		return data



class UHDTxPktArch(UHDAbstractArch):
	"""
	Base architecture to send packets with UHD devices
	"""

	__metaclass__ = ABCMeta

	def __init__(self,
			name,
			input_signature,
			output_signature):
		"""
		CTOR
		@param name
		@param input_signature
		@param output_signature
		"""

		self._modulator = self._build()

		UHDAbstractArch.__init__(self, name, input_signature, output_signature)


		if input_signature.min_streams():
			self.connect(self, self._modulator)

		if output_signature.min_streams():
			self.connect(self._modulator, self)


	@abstractmethod
	def _build(self):
		"""
		Build internal blocks  of the architecture. 
		@return Architecture
		"""
		pass

	def send_pkt(self, payload, eof = False):
		"""
		Transmit the payload using a implementation specific modulator
		"""
		self._modulator.send_pkt(payload, eof)


class UHDRxArch(UHDAbstractArch):
	"""
	Receive data through USRP
	This is the base class for the rx devices.
	"""

	def __init__(self, name, input_signature, output_signature):
		"""
		CTOR
		@param name
		@param input_signature
		@param output_signature
		"""
		UHDAbstractArch.__init__(self, name = name,
				input_signature = input_signature,
				output_signature= output_signature
			)


	def receive_pkt(self):
		"""
		::TRICKY:: NOT USED
		Received a Packet.
		"""
		self._modulator.receive_pkt()
