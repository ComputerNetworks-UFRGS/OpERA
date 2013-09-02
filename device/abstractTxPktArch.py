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
