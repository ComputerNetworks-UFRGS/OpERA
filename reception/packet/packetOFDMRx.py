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

## @package block_utils

# ::TODO:: class description

# gnuradio imports
from gnuradio     import gr, digital, blocks
from grc_gnuradio import blks2 as grc_blks2

# project import
from device	import UHDRxArch


##
class PacketOFDMRx(UHDRxArch):

	## CTOR
	# @param callback
	def __init__(self, callback):

		UHDRxArch.__init__(
				self,
				name =  'PacketOFDMRx',
				input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
				output_signature = gr.io_signature(0, 0, 0),
			)

		self._demod = digital.ofdm_demod(
				options=grc_blks2.options(
					modulation="qam64",
					fft_length=512,
					occupied_tones=200,
					cp_length=128,
					snr=30,
					log=None,
					verbose=None,
					),
				callback=callback
			)

		#             #
		# Connections #
		#             #
		self.connect(self, self._demod)
