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

# ::TODO:: modules definition
## @package device

# GNU Radio imports
from gnuradio import gr

from abstractArch import AbstractArch

## Abstract class for the UHD devices
# This is the base class for UHD devices
class UHDAbstractArch(AbstractArch, gr.hier_block2):
	
	## CTOR
	# @param name
	# @param input_signature
	# @param output_signature
	def __init__(self, name, input_signature, output_signature):

		self._radio_device = None

		AbstractArch.__init__(self, name=name)

		gr.hier_block2.__init__(
				self,
				name =  name,
				input_signature  = input_signature,
				output_signature = output_signature,
			)

	## Set the radio device of the architeture to a given radio device.
	# @param radio_device
	def set_radio_device(self, radio_device):
		self._radio_device = radio_device

	## 
	@property
	def radio(self):
		if self._radio_device is not None:
			return self._radio_device
		else:
			raise AttributeError
