## @package algorithm

# Reorder channel list.
# Utilized withn Chimas.
def reorder(channel_list, qn_result):
	for i in xrange( len(channel_list) ):
		for j in xrange(i+1, len(channel_list) ):
			if qn_result[1][i] < qn_result[1][j]:
				qn_result[0][i], qn_result[0][j] = qn_result[0][j], qn_result[0][i]
				qn_result[1][i], qn_result[1][j] = qn_result[1][j], qn_result[1][i]
				channel_list[i], channel_list[j] = channel_list[j], channel_list[i]

	return channel_list

## Chimas class
# Implements the Chimas algorithm proposed by Bondan for the LCN 2014 conference
class Chimas(object):

	## CTOR
	# @param top_block TopBlock instance
	# @param learning_algorithm Learning algorithm (Qnoise)
	# @param channel_list List of Channels objects to sense.
	def __init__(self, top_block, learning_algorithm, channel_list = []):

		self._top_block = top_block
		self._evaluater = learning_algorithm

		self._channelList = channel_list

	## Return list of channels to sense.
	# @return List of channels to sense.
	@property
	def channelList(self):
		return self._channelList


	## Set list of channels to sense.
	# @param the_list
	@channelList.setter
	def channelList(self, the_list ):
		self._channelList = the_list

	## Sense channels and evaluate them.
	# @param iterations Number of evaluation.
	# @return (SS result, learning result) when finished.
	def run(self, iterations):

		# sanity check
		if not self.channelList:
			raise ValueError('Channel List is empy')

		# sense and channgel evaluation
		while iterations > 0 and iterations != -1 :
			print iterations
			ss_result    = self._top_block.rx.senseChannelList(the_list = self.channelList, sensing_time= 1)
			ln_result    = self._evaluater.evaluate( ss_result )
			self.channelList = reorder( self.channelList, ln_result )

			print '---------------------------------------------------'
			iterations -= 1

		return ss_result, ln_result
