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
@package block_utils
"""


# gnuradio imports
from gnuradio     import gr, digital

# project import
from device 	import UHDRxArch

class PacketGMSKRx(UHDRxArch):
	"""
	"""

	def __init__(self, callback):
		"""
		CTOR
		@param callback Function called when a packet is received
		"""

		UHDRxArch.__init__(
				self,
				name =  'PacketGMSKRx',
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(0, 0, 0),
			)

		self._demod = digital.pkt.demod_pkts(
				demodulator = digital.gmsk_demod(
					samples_per_symbol = 2),
				callback = callback
			)

		#             #
		# Connections #
		#             #
		self.connect(self, self._demod)
