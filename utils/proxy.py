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

# @package ss_utils

## Base class to implement the proxy design patter
class Proxy(object):

	## CTOR
	# @param subject Proxied object
	def __init__(self, subject):
		object.__setattr__(self, '_subject', subject)


	## Called when the Proxy base class doesnot have the 'var' attribute
	# @param val Getted parameter
	# @throw AttributeError
	def __getattr__(self, var):
		if hasattr(self._subject, var) == False:
			raise AttributeError

		return getattr(self._subject, var, None)

	## Called when the Proxy derived class doesnot have the 'var' attribute
	# @param val Setted parameter
	# @throw AttributeError
	def __setattr__(self, var, val):
		if hasattr(self._subject, var) == False:
			raise AttributeError
	
		self._subject.__setattr__(var, val)
