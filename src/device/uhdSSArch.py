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
