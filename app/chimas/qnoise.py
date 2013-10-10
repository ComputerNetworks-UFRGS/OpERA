import random

class QChannel(object):

	def __init__(self, index, lookback):
		self.index = index
		self.qvalue = 0.5
		self.history = [0.0] * lookback

	def getId(self):
		return self.index

	def getQValue(self):
		return self.qvalue

	def updateHistoric(self, newValue):
		self.history.pop(0)
		self.history.append(newValue)

	def calculateQValue(self, reward, alpha, hist_weight, noise_weight, sinr):
		def sinr_contribution(rssi):
			print 'sinr: ', rssi
			contribution = [(10e-7, 1), (10e-6, 0.75), (3* 10e-6, 0.50), (6 * 10e-6, 0.25), (10e-4, 0.10)]
			for check, value in contribution:
				if rssi < check:
					return value
			return 0.0

		noise_acc = sinr_contribution(sinr)


		historic_acc = 0.0
		for weight, value in zip(hist_weight, self.history):
			historic_acc += weight * value


		self.qvalue = alpha * reward + ((1-noise_weight) - alpha)*(historic_acc) + noise_weight * noise_acc
		self.updateHistoric(self.qvalue)

		return

	def __lt__(self, other):
		return self.getQValue() > other.getQValue()

class Learner:

	def __init__(self, channel_list, lookback, alpha, beta, eps, hist_weight, noise_weight): 
		self.channelList = []
		self.lookback = lookback
		self.alpha = alpha
		self.hist_weight = hist_weight
		self.noise_weight = noise_weight
		self.eps = eps
		self.beta = beta


		# Initialize self.channelList based on channel_list
		# channel_list is a list of Channel(not the defined in this file) objects
		for i in channel_list:
			self.channelList.append( QChannel( i.channel, lookback ) )

		print [ 'Id: %d, QValue: %f\n' % (x.getId(), x.getQValue()) for x in self.channelList ]
		
				
	def evaluate(self, channelId, pkt_sent, pkt_received, sinr): 

		reward = pkt_received / float(pkt_sent) if pkt_sent else 0
		print 'Ch %d reward: %f'  % (channelId, reward)

		lookback = self.lookback

		print 'ChannelId: ', channelId
		if not (self.channelList):
			currentChannel = QChannel(channelId, lookback)
			self.channelList.append(currentChannel)
		else:
			found = False

			for ch in self.channelList:
				if (ch.getId() == channelId ):
					currentChannel = ch
					found = True
					break
			
			if not(found):
				currentChannel = QChannel(channelId, lookback)
				self.channelList.append(currentChannel)

		currentChannel.calculateQValue(reward, self.alpha, self.hist_weight, self.noise_weight, sinr)

		
		self.channelList.sort()
		for x in self.channelList:
			print  'Id: %d, QValue: %f' % (x.getId(), x.getQValue()) 


		return currentChannel.getQValue()

	def chooseNextChannel(self, currentChannel):

		availableChannels = []

		for ch in self.channelList:
			
			if (ch.getId() == currentChannel):
				currentQValue = ch.getQValue()

			availableChannels.append([ch.getQValue(), ch.getId()])

		exploration = random.random()

		if (exploration <= self.eps):
			nextChannel = random.choice(availableChannels)
			print '@@@ Next Channel is ', nextChannel[1], '[RANDOM]'
			return nextChannel[1]

		maxQChannel = max(availableChannels)

		if (maxQChannel[1] != currentChannel) and ( (maxQChannel[0] - currentQValue) >= self.beta ):
			print '@@@ Next Channel is ', maxQChannel[1], '[QVALUE]'
			return maxQChannel[1]
		else:
			nextChannel = random.choice(availableChannels)
			print '@@@ Next Channel is ', nextChannel[1]
			return nextChannel[1]
