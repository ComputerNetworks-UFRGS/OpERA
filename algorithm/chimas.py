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
	def __init__(self, chimas_arch, learning_algorithm):

		self._rx = chimas_arch
		self._evaluater = learning_algorithm


	## Sense channels and evaluate them.
	# @param iterations Number of evaluation.
	# @return (SS result, learning result) when finished.
	def run(self, channels, iterations = 1):
		ln_result = 0

		if isinstance(channels, list):
			for i in range(1, iterations):
				ss_result    = self._rx.sense_channel_list(the_list = channels, sensing_time= 1)
				ln_result    = self._evaluater.evaluate( ss_result )
		else:
			self._rx.sense_channel(the_channels = channels, sensing_time = 1 )
			ln_result    = self._evaluater.evaluate( ss_result )

		return ss_result, ln_result
