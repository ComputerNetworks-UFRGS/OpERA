from abstractDevice import AbstractDevice
from gnuradio import uhd
from uhdDevice import *

## USRP implementation of a AbstractDevice.
# For now, only the main properties are interfaced:
#    - gain, center_freq and sample_rate
class RadioDevice(AbstractDevice):

	## CTOR
	# @param the_source Source of data
	# @param the_sink sink of data
	def __init__(self, the_source, the_sink, uhd_device = None):
		AbstractDevice.__init__(self)

		self._source = the_source
		self._sink	 = the_sink

		self._uhd = uhd_device or the_source

# source property
	@property
	def source(self):

		# Check if _uhd is a UHDBase object.
		# If it is, return its the uhd property.
		if isinstance(self._source, UHDBase):
			return self._source.uhd

		return self._source

# sink property
	@property
	def sink(self):

		# Check if _uhd is a UHDBase object.
		# If it is, return its the uhd property.
		if isinstance(self._sink, UHDBase):
			return self._sink.uhd

		return self._sink

	@property
	def uhd(self):
		tmp = self._uhd

		# Check if _uhd is a UHDBase object.
		# If it is, return its the uhd property.
		if isinstance(self._uhd, UHDBase):
			tmp = self._uhd.uhd

		return tmp

# center_freq property
	## @abstract
	def _get_center_freq(self):
		return self.uhd.get_center_freq()

	## @abstract
	def _set_center_freq(self, center_freq):
		self.uhd.set_center_freq( center_freq )

# samp_rate property
	def _get_samp_rate(self):
		return self.uhd.get_samp_rate()

	def _set_samp_rate(self, samp_rate):
		self.uhd.set_samp_rate( samp_rate )

# gain property
	def _get_gain(self):
		return self.uhd.get_gain()

	def _set_gain(self, gain):
		self.uhd.set_gain( gain )

# output property
	@property
	def output(self):
		return self.sink.level()
