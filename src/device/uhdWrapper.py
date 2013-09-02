## @package algorithm

## Interface to interact with a UHD and some other object 
# 
class UHDWrapper(object):

	## CTOR
	# @param device
	# @param algorithm
	def __init__(self, device, algorithm):
		object.__setattr__(self, '_device', device)
		object.__setattr__(self, '_algorithm', algorithm)

	@property
	def device(self):
		return self._device

	@property
	def algorithm(self):
		return self._algorithm

	# WARNING
	#
	# Changes in __getattr__ and __setattr__ should be made with care
	#
	# Proxied classes

	##
	# @param val
	def __getattr__(self, val):
		tmp = None

		# Check if _device has the attribute, otherwise check in _algorithm
		if hasattr(self._device, val):
			tmp = self._device
		elif hasattr(self._algorithm, val):
			tmp = self._algorithm

		if tmp:
			return getattr(tmp, val)

		raise AttributeError

	## Proxied classes
	def __setattr__(self, name, val):

		tmp = None

		if hasattr(self._device, name):
			tmp = self._device
		elif hasattr(self._algorithm, name):
			tmp = self._algorithm

		if tmp:
			setattr(tmp, name, val)
			return

		raise AttributeError
