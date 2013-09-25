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

## @package algorithm

from gnuradio import gr

## Interface to interact with a UHD and some other object 
# 
class OpERAFlow(gr.top_block):

	## Constants to specify the connection type
	CONN_SOURCE = 0b001
	CONN_SINK   = 0b010
	CONN_SOURCE_SINK = CONN_SOURCE | CONN_SINK

	## CTOR
	# @param name
	def __init__(self, name):
		object.__setattr__(self, '_dict_of_archs', {})
		gr.top_block.__init__(self, name = name)
		

	## Add an abstract archicteture to be manageable through OpERA and allow an instance of the OpERAFlow class to call modules from a given abstract architeture
	# @param abstract_arch
	# @param radio_device
	# @param name_of_arch
	# @param connection_type
	def add_path(self, abstract_arch, radio_device, name_of_arch, connection_type = CONN_SOURCE_SINK):

		# abstract_arch must be an instance of some abstract architeture class.

		self._dict_of_archs[name_of_arch] = abstract_arch

		setattr(self, name_of_arch, abstract_arch)

		if radio_device:
			if radio_device.source and (connection_type & OpERAFlow.CONN_SOURCE):
				self.connect(radio_device.source, abstract_arch)

			if radio_device.sink and (connection_type & OpERAFlow.CONN_SINK):
				self.connect(abstract_arch, radio_device.sink)

			abstract_arch.set_radio_device( radio_device )


	## Definition of the getattr for the class
	def __getattr__(self, name):
		if name == "_dict_of_archs":
			return object.getattr(self, "_dict_of_archs")
		else:
			for key in self._dict_of_archs:
				if hasattr(self._dict_of_archs[key], name):
					return self._dict_of_archs[key].name

		raise AttributeError("%r object has no attribute %r" %
			(self.__class__, attr))

	## Setattr method for the class
	def __setattr__ (self, name, val):
		tmp = None


		# in add_path
		if name in self._dict_of_archs:
			tmp = self._dict_of_archs[name]

		# common atribuition
		else:
			object.__setattr__(self, name, val)
			return
			

		if tmp:
			setattr(OpERAFlow, name, tmp)
			return 

		raise AttributeError
