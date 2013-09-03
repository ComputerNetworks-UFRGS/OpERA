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

from gnuradio import gr
from abstractTxPktArch import AbstractTxPktArch

class UHDTxPktArch( AbstractTxPktArch, gr.hier_block2 ):
	_tx = 0

	## CTOR
	# @param input_signature
	# @param output_signature
	def __init__(self,
			name,
			input_signature,
			output_signature):

		AbstractTxPktArch.__init__(self)

		gr.hier_block2.__init__(
				self,
				name = name,
				input_signature  = input_signature,
				output_signature = output_signature
			)

		self._modulator = self._build()

		# ::TODO::
		# Connects based on input_signature and output_signature
		self._connect(self._modulator, self)


	@abstractmethod
	def _build(self):
		pass

	## abstractTxPktArch abstract method.
	def send_pkt(self, payload, eof = False):
		self._modulator.send_pkt(payload, eof)
