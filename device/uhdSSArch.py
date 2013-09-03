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

# GNU Radio imports
from gnuradio import gr

# Project imports
from abstractSSArch   import AbstractSSArch

## Specific implementation of the AbstractSSArch for the UHD device.
# This is the base class for all rx with spectrum sensing paths utilized in the TopBlock class.
class UHDSSArch(AbstractSSArch, gr.hier_block2):

	## CTOR
	# @param uhd              UHD Device
	# @param name             SS Arch instance name
	# @param input_signature  A gr.io_signature instance.
	# @param output_signature A gr.io_signature instance.
	def __init__(self,
			uhd,
			name,
			input_signature,
			output_signature):

		AbstractSSArch.__init__(self)

		gr.hier_block2.__init__(self,
				name = name,
				input_signature  = input_signature,
				output_signature = output_signature
			)

		self._uhd = uhd

	@property
	def uhd(self):
		return self._uhd

	## SS on a single channel
	# Implements AbstractSSArch abstract method.
	# @param the_channel Channel to be sensed.
	# @param sensing_time Sensing duration on channel.
	def sense_channel(self, the_channel, sensing_time):
		return self._get_sensing_data( the_channel, sensing_time )
