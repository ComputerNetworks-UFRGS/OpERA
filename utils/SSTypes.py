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

## @package utils
# Utilities for the project


## Enum class
# States used in the SSA class
# @sa ssa
class SSA_STATES:

	## Inicial State
	INITIALIZE 		= "INITIALIZE"
	## Spectrum sensing over channel list
	SS_1 			= "SS_1"
	## Change channel
	SS_1_NEXT_CH 	= "SS_1_NEXT_CH"

	## Spectrum sensing over adjacent channels
	SS_2			= "SS_2"

	## Abort
	ABORT 			= "ABORT"
