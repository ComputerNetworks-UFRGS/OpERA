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

## Interface to interact with a UHD and some other object 
# 
class UHDWrapper(object):

	## CTOR
	def __init__(self):
		object.__setattr__(self, '_dict_of_archs', {})

	def add_path(self, abstract_arch, name_of_arch):
		#abstract_arch must be an instance of some abstract architeture class.

		self._dict_of_archs[name_of_arch] = abstract_arch

		setattr(self, name_of_arch, abstract_arch)

	def __setattr__ (self, name, val):
		tmp = None

		if name in self._dict_of_archs:
			tmp = self._dict_of_archs[name]

		if tmp:
			setattr(UHDWrapper, name, tmp)
			return 

		raise AttributeError
