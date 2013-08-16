## @package ss_utils

from gnuradio import gr

## A gr.top_block derived class that offers some facilities.
#	This class offers methods to add a tx and a rx path.
#	Both pathes can be accessed with TopBlock.rx and TopBlock.tx properties.
#	RX path can be a UHDAlgorithmInterface.
class TopBlock( gr.top_block ):

	## CTOR
	# @param name  Name of the top block.
	def __init__(self, name):
		gr.top_block.__init__(self, name = name)

		self._rx_path = self._tx_path = None

	## Getter for RX the path.
	# @return Configured RX path. A gr.hier_block2 instance.
	# @throws RuntimeError if RX path is empty.
	@property
	def rx(self):
		# sanity check
		if self._rx_path == None:
			raise RuntimeError("rx path is None")

		return self._rx_path

	## Getter for TX the path.
	# @return Configured RX path.
	# @throws RuntimeError if RX path is empty.
	@property
	def tx(self):
		# sanity check
		if self._tx_path == None:
			raise RuntimeError("tx path is None")

		return self._tx_path


	## Setter for RX the path.
	# @param rx_path RX path
	@rx.setter
	def rx(self, rx_path):
		# disconnect an already existing rx path
		if self._rx_path != None:
			self.disconnect( self._rx_path )

		self._rx_path = rx_path


	## Setter for RX the path.
	# @param rx_path RX path
	@tx.setter
	def tx(self, tx_path):
		# disconnect an already existing tx path
		if self._tx_path != None:
			self.disconnect( self._tx_path )

		self._tx_path = tx_path
