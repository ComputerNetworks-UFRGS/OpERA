## @package ssa

from gnuradio import eng_notation

# Local imports
from ss_utils import Channel

## Class with configurations of the SSA machine state
#
class SSAConfiguration:
	def __init__(self):

		## List of channels that have to be sensed
		#self.channel_list = [
		#		Channel(ch = 1,  freq = 2.412e9, bw = 2e3),	# L
		#		Channel(ch = 2,  freq = 2.417e9, bw = 2e3),	# L
		#		Channel(ch = 3,  freq = 2.422e9, bw = 2e3),	# L
		#		Channel(ch = 4,  freq = 2.427e9, bw = 2e3),	# L
		#		Channel(ch = 5,  freq = 2.432e9, bw = 2e3),	# L
		#		Channel(ch = 6,  freq = 2.437e9, bw = 2e3),	# L
		#		Channel(ch = 7,  freq = 2.442e9, bw = 2e3),	# L
		#		Channel(ch = 9,  freq = 2.447e9, bw = 2e3),	# L
		#		Channel(ch = 10, freq = 2.452e9, bw = 2e3),	# L
		#		Channel(ch = 11, freq = 2.457e9, bw = 2e3),	# L
		#		Channel(ch = 12, freq = 2.462e9, bw = 2e3),	# L
		#		Channel(ch = 13, freq = 2.467e9, bw = 2e3),	# L
		#		Channel(ch = 14, freq = 2.472e9, bw = 2e3),	# L
		#		Channel(ch = 15, freq = 2.477e9, bw = 2e3),	# L

		#		Channel(ch = 16, freq = 2.990e9, bw = 2e3),	# L
		#		Channel(ch = 17, freq = 2.995e9, bw = 2e3),	# L
		#		Channel(ch = 18, freq = 3.000e9, bw = 2e3),	# L
		#		Channel(ch = 19, freq = 3.005e9, bw = 2e3),	# L
		#		Channel(ch = 20, freq = 3.010e9, bw = 2e3),	# L
		#		Channel(ch = 21, freq = 3.015e9, bw = 2e3),	# L
		#]

		self.channel_list = [
				Channel(ch = 1,  freq = 94.30e6, bw = 200e3),	# L
				Channel(ch = 2,  freq = 90.3e6,  bw = 200e3),	# L
				Channel(ch = 3,  freq = 93.7e6,  bw = 200e3),	# L
				Channel(ch = 4,  freq = 101.3e6, bw = 200e3),	# L
				Channel(ch = 5,  freq = 94.9e6,  bw = 200e3),	# L
				Channel(ch = 6,  freq = 99.3e6,  bw = 200e3),	# L
				Channel(ch = 7,  freq = 205.25e6,bw = 200e3),	# L
				Channel(ch = 8,  freq = 83.25e6,bw = 200e3),	# L
				Channel(ch = 9,  freq = 211.25e6,bw = 200e3),	# L
				Channel(ch = 10, freq = 199.25e6,bw = 200e3),	# L
				Channel(ch = 11, freq = 193.25e6,bw = 200e3),	# L
				Channel(ch = 12, freq = 187.25e6,bw = 200e3),	# L
				Channel(ch = 13, freq = 711.25e6,bw = 200e3),	# L
		]

	## Get channel list
	# @return List of channels
	def priorityChannelList(self):
		return self.channel_list[:]
