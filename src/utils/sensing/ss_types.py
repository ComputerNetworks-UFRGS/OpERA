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
