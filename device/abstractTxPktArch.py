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

## @package device

from abc import ABCMeta, abstractmethod


## Abstract class for a TX architecture.
#
class AbstractTxPktArch( object ):
	__metaclass__ = ABCMeta

	## CTOR
	def __init__(self):
		pass


	## Send payload.
	# @param payload Pkt Payload.
	# @param eof End Of File.
	@abstractmethod
	def send_pkt(self, payload, eof = False):
		pass
