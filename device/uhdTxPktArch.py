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

# ::TODO:: description of the class UHDTxPktArch
from abc import ABCMeta, abstractmethod

from gnuradio import gr
from uhdAbstractArch import UHDAbstractArch

## Send data through USRP
class UHDTxPktArch(UHDAbstractArch):

	## CTOR
	# @param name
	# @param input_signature
	# @param output_signature
	def __init__(self,
			name,
			input_signature,
			output_signature):

		UHDAbstractArch.__init__(self, name, input_signature, output_signature)
		self._modulator = self._build()

		# ::TODO::
		# Connects based on input_signature and output_signature

		if input_signature.min_streams():
			self.connect(self, self._modulator)

		if output_signature.min_streams():
			self.connect(self._modulator, self)


	## abstractmethod _build
	@abstractmethod
	def _build(self):
		pass

	## abstractTxPktArch abstract method.
	def send_pkt(self, payload, eof = False):
		self._modulator.send_pkt(payload, eof)

	#### novo  - setar radio device #######
	def set_radio_device(self, radio_device):
		self._radio_device = radio_device
