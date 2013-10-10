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
from uhdAbstractArch import UHDAbstractArch

## Receive data through USRP
# This is the base class for the rx devices.
class UHDRxArch(UHDAbstractArch):

	## CTOR
	def __init__(self, name, input_signature, output_signature):
		UHDAbstractArch.__init__(self, name=name, input_signature=input_signature, output_signature=output_signature)

	## Receives the package
	def receive_pkt(self):
		self._modulator.receive_pkt()

