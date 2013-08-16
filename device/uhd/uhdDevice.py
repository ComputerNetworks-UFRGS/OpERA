## @package device

from gnuradio import uhd
from device.abstractDevice import AbstractDevice

## Base class to UHDSource and UHDSink
class UHDBase(AbstractDevice):

	## CTOR.
	# @param uhd UHD Device: uhd.usrp_source or uhd.usrp_sink.
	def __init__(self, uhd):
		AbstractDevice.__init__(self)
		self._uhd = uhd

	## Getter for the UHD device.
	# @return The uhd_source/sink device.
	@property
	def uhd(self):
		return self._uhd

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


## Wrapper for uhd.usrp_source device.
# Always utilizes the 'RX2' antenna.
class UHDSource(UHDBase):

	## CTOR.
	# @param  device_addr USRP IP address.
	# @param stream_args USRP stream arguments.
	def __init__(
			self,
			device_addr = '',
			stream_args = uhd.stream_args('fc32')
			):

		# Only creates the base class passing a uhd.usrp_source
		UHDBase.__init__(
				self,
				uhd = uhd.usrp_source(
					device_addr = device_addr,
					stream_args = stream_args)
				)

		self.uhd.set_antenna('RX2', 0)

## Wrapper for uhd.usrp_sink device.
# Always utilize the TX/RX antenna.
class UHDSink(UHDBase):

	## CTOR.
	# @param  device_addr USRP IP address.
	# @param stream_args USRP stream arguments.
	def __init__(
			self,
			device_addr = '',
			stream_args = uhd.stream_args('fc32')
			):

		# Only creates the base class passing a uhd.usrp_sink
		UHDBase.__init__(
				self,
				uhd = uhd.usrp_sink(
					device_addr = device_addr,
					stream_args = stream_args)
				)

		self.uhd.set_antenna('TX/RX', 0)


## USRP implementation of a AbstractDevice.
# For now, only the main properties are interfaced:
#    - gain, center_freq and sample_rate
class UHDDevice(AbstractDevice):

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
