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

import random

#::TODO:: documentacao


class QChannel(object):
    """

    """

    def __init__(self, index, lookback):
        """
        CTOR
        @param index
        @param lookback
        """
        self.index = index
        self.qvalue = 0.5
        self.history = [0.0] * lookback

    def get_id(self):
        """
        Return the index.
        """
        return self.index

    def get_qvalue(self):
        """
        Return the qvalue.
        """
        return self.qvalue

    def update_historic(self, new_value):
        """
        @param new_value
        """
        self.history.pop(0)
        self.history.append(new_value)

    def calculate_qvalue(self, reward, alpha, hist_weight, noise_weight, sinr):
        """
        @param reward
        @param alpha
        @param hist_weight
        @param noise_weight
        @param sinr
        """

        #::TODO:: checar essa funcao. nao tem self e nem é static.
        def sinr_contribution(rssi):
            """
            @param rssi
            """
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
        self.update_historic(self.qvalue)

        return

    def __lt__(self, other):
        """
        @param other
        """
        return self.get_qvalue() > other.get_qvalue()


class Learner:
    """

    """

    def __init__(self, channel_list, lookback, alpha, beta, eps, hist_weight, noise_weight):
        """
        CTOR
        @param channel_list
        @param lookback
        @param alpha
        @param beta
        @param eps
        @param hist_weight
        @param noise_weight
        """
        self.channel_list = []
        self.lookback = lookback
        self.alpha = alpha
        self.hist_weight = hist_weight
        self.noise_weight = noise_weight
        self.eps = eps
        self.beta = beta


        # Initialize self.channel_list based on channel_list
        # channel_list is a list of Channel(not the defined in this file) objects
        for i in channel_list:
            self.channel_list.append(QChannel(i.channel, lookback))

        print ['Id: %d, QValue: %f\n' % (x.get_id(), x.get_qvalue()) for x in self.channel_list]

    def evaluate(self, channel_id, pkt_sent, pkt_received, sinr):
        """

        @param channel_id
        @param pkt_sent
        @param pkt_received
        @param sinr
        """

        reward = pkt_received / float(pkt_sent) if pkt_sent else 0
        print 'Ch %d reward: %f' % (channel_id, reward)

        lookback = self.lookback

        print 'channel_id: ', channel_id
        if not self.channel_list:
            current_channel = QChannel(channel_id, lookback)
            self.channel_list.append(current_channel)
        else:
            found = False

            for ch in self.channel_list:
                if ch.get_id() == channel_id:
                    current_channel = ch
                    found = True
                    break
            
            if not found:
                current_channel = QChannel(channel_id, lookback)
                self.channel_list.append(current_channel)

        current_channel.calculate_qvalue(reward, self.alpha, self.hist_weight, self.noise_weight, sinr)
        
        self.channel_list.sort()
        for x in self.channel_list:
            print 'Id: %d, QValue: %f' % (x.get_id(), x.get_qvalue())


        return current_channel.get_qvalue()

    def choose_next_channel(self, current_channel):
        """
        @param current_channel
        """

        available_channels = []

        for ch in self.channel_list:
            
            if ch.get_id() == current_channel:
                current_qvalue = ch.get_qvalue()

            available_channels.append([ch.get_qvalue(), ch.get_id()])

        exploration = random.random()

        if exploration <= self.eps:
            next_channel = random.choice(available_channels)
            print '@@@ Next Channel is ', next_channel[1], '[RANDOM]'
            return next_channel[1]

        max_q_channel = max(available_channels)

        if (max_q_channel[1] != current_channel) and ((max_q_channel[0] - current_qvalue) >= self.beta):
            print '@@@ Next Channel is ', max_q_channel[1], '[QVALUE]'
            return max_q_channel[1]
        else:
            next_channel = random.choice(available_channels)
            print '@@@ Next Channel is ', next_channel[1]
            return next_channel[1]
