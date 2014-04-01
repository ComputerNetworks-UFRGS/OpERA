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


#::TODO:: descricao dos metodos e de seus parametros
def reorder(channel_list, qn_result):
    """
    Reorder channel list.
    Utilized with Chimas.
    @param channel_list A list of channels.
    @param qn_result
    @return The modified channel list.
    """
    for i in xrange(len(channel_list)):
        for j in xrange(i+1, len(channel_list)):
            if qn_result[1][i] < qn_result[1][j]:
                qn_result[0][i], qn_result[0][j] = qn_result[0][j], qn_result[0][i]
                qn_result[1][i], qn_result[1][j] = qn_result[1][j], qn_result[1][i]
                channel_list[i], channel_list[j] = channel_list[j], channel_list[i]

    return channel_list

from abc import abstractmethod

import numpy as np

## Represent a QLearner
# Base class for QValue based algorithms
class QLearner:
    ## CTOR
    # @param alpha Weight most recent values
    # @param hist_weight Weight of the last QValues. Array of [nth, n-1th, n-2th, ..., 1st]
    # @param noise_weight Weight of SINR
    # @param reward_callback
    def __init__(self, alpha, lookback, hist_weight):
        self._qval      = [ 0.0 ]  * len( hist_weight ) 

        ##
        self._l = lookback 
        self._a = alpha
        self._h = hist_weight

    ## Calculate the reward based on data
    # Should be implemented by the derived class
    @abstractmethod
    def _reward(self, data):
        pass

    ## Return the current QValue
    # @return Last QValue
    def get_q_val(self):
        return self._qval[-1]

    ## Append a value to QValues kept
    # @param value Value to append
    #            Ex: lookback = 3;
    #            t=1;    Channel: [Qval t=1]
    #            t=2;    Channel: [Qval t=1][Qval t=2]
    #            t=3;    Channel: [Qval t=1][Qval t=2][Qval t=3]
    #            t=4;    Channel: [Qval t=2][Qval t=3][Qval t=4]
    #            t=5;    Channel: [Qval t=3][Qval t=4][Qval t=5]
    def add_q_val(self, value):
        self._qval.append( value )

        if len( self._qval ) > self._l:
            self._qval.pop( 0 )

    ## Calculate the QValue for the given sensing result
    # @param data Data utilized in the QValue calculation
    def calc_q_val(self, data):
        reward = self._reward( data ) 

        # Multiply each element on hist_weight by each column on historic table
        #  Ex: hist_weight = [0.2, 0.35, 0.45]
        #        historic table = [[0.4, 0.8, 0.6, 0.3], [0.6, 0.3, 0.5, 0.8], [0.5, 0.4, 0.4, 0.8]
        #  Calc:
        #        Channel 1:    0.2 * 0.4 + 0.35 * 0.6 + 0.45 * 0.5 
        #        Channel 2:    0.2 * 0.8 + 0.35 * 0.3 + 0.45 * 0.4
        #        Channel 3:    0.2 * 0.6 + 0.35 * 0.5 + 0.45 * 0.4
        #        Channel 4:    0.2 * 0.3 + 0.35 * 0.8 + 0.45 * 0.8
        hist_total = sum([q*h for q,h in zip(self._qval, self._h)])

        # Calculate the QValue
        # qvalue = alpha * reward + (1-alpha) * historic
        qval = self._a * reward + (1 - self._a) * hist_total

        self.add_q_val( qval )

## Considers both RSSI and Historic occupancy to calculate the channel QValue
class QChannel:

    ## Internal class that implements thq Noise QValue.
    class QNoiseLearner(QLearner):

        ## CTOR
        # @param alpha Weight of the most recent reward. Integer
        # @param lookback How many qvalues we should kept in history. Integer
        # @hist_weight Weights of last N QValues. List of Integer.
        def __init__(self, alpha, lookback, hist_weight):
            QLearner.__init__(self, alpha = alpha, lookback = lookback, hist_weight = hist_weight)

        ## Inherited from parrent
        # Calculate the reward based on a simple table that maps a RSSI value to a reward.
        def _reward(self, data):
            # Sanity check
            if all(rssi == 1 or rssi == 0 for rssi, dec in data ):
                raise ValueError("RSSI is all 0s and 1s. It this right?")

            def sinr_contribution(rssi):
                contribution = [(10e-7, 1), (10e-6, 0.75), (3* 10e-6, 0.50), (6 * 10e-6, 0.25), (10e-4, 0.10)]
                for check, value in contribution:
                    if rssi < check:
                        return value
                return 0.0

            rssi = 0.0
            count = 0


            for _rssi, _dec in data:
                if _dec == 0:
                    rssi += _rssi
                    count += 1

            if count:
                return sinr_contribution( rssi / count )
            else:
                return 0.0

    ## Internal class that implements the Historic Occupancy QValue
    class QHistoricLearner( QLearner ):

        ## CTOR
        # @param alpha
        # @param lookback
        # @param hist_weight
        def __init__(self, alpha, lookback, hist_weight):
            QLearner.__init__(self, alpha = alpha, lookback = lookback, hist_weight = hist_weight)


        ## Inherited from parent
        # Calculated the reward by dividing the number of 'idles decisions' by the total of decisions.
        def _reward(self, data):

            # Sanity check
            if not all(d == 1 or d == 0 for s, d in data ):
                raise ValueError("Decisions must be all 0s and 1s")

            idle = np.sum( [ 1-d for s, d in data] ) # pylint: disable=E1101
            return float(idle) / len(data)

    ## CTOR
    # @param h_weight Weight of Historic QLearner instance
    # @param h_data Historic QLearner instance data. Tuple: (alpha, lookback, hist_weight)
    # @param n_weight Weight of Noise QLearner instance
    # @param n_data Noise QLearner instance data. Tuple: (alpha, lookback, hist_weight)
    def __init__(self, h_weight, h_data, n_weight, n_data):

        #
        self._historic = QChannel.QHistoricLearner( alpha = h_data[0],
                lookback = h_data[1],
                hist_weight = h_data[2]
        )

        #
        self._noise = QChannel.QNoiseLearner( alpha = n_data[0],
                lookback = n_data[1],
                hist_weight = n_data[2]
        )

        self._hw = h_weight
        self._nw = n_weight

    ##
    #
    def get_q_val(self):
        print' historic: ', self._historic.get_q_val()
        print' noise:    ', self._noise.get_q_val()
        return self._hw * self._historic.get_q_val() +  self._nw * self._noise.get_q_val()

    ##
    # @param final_decision Final decision regarding channel occupancy
    # @param usensing Array of tuples (dec, rssi)
    def calc_q_val(self, final_decision, usensing):

        # calculate RSSI only if channel if idle
        if final_decision == 0:
            self._noise.calc_q_val( usensing )

        self._historic.calc_q_val( usensing )


## QNoise algorithm
# Keeps the qvalue for all channels created
class QNoise:

    ## CTOR
    def __init__(self, n_weight, n_data, h_weight, h_data):
        self._channel = {}

        # Weight of noise in the QChannel object
        self._n_weight = n_weight
        self._n_data = n_data

        # Weight of historic in the QChannel object
        self._h_weight = h_weight
        self._h_data = h_data

    ## Calculate QValue for all channels
    # @param matrix Each row represents a channel. columns have the following semantics
    #  [Channel][Array tuples (RSSI,decisions)]
    #  <---1---><---parameter udecisions------>    
    def evaluate(self, matrix):
        channel_list = []
        qvalue_list = []

        # Decides if the channel  is occupied/vacant based on udecisions
        def data_to_final_decision( dec_tuples ):
            occupied = 0
            vacant = 0

            occupied = np.sum( 1 if dec else 0 for rssi, dec in dec_tuples ) # pylint: disable=E1101
            vacant   = np.sum( 0 if dec else 1 for rssi, dec in dec_tuples ) # pylint: disable=E1101

            return 1 if occupied > vacant else 0

        for ch_data in matrix:
            ch = ch_data[0]

            # Check if ch is in channel dictionary
            if ch not in self._channel:
                self._channel[ch] = QChannel( h_weight = self._h_weight,
                        h_data = self._h_data,
                        n_weight = self._n_weight,
                        n_data = self._n_data)

            # Calculate QValue
            self._channel[ch].calc_q_val(
                    final_decision = data_to_final_decision( ch_data[1] ),
                    usensing      =  ch_data[1]
            )

            # Use leonard's format
            channel_list.append( ch )
            qvalue_list.append( self._channel[ch].get_q_val() )

        # Return expect format
        return [channel_list, qvalue_list]

#if __name__ == '__main__':
#
#    alpha = 0.3
#    hist_weight = [0.2, 0.35, 0.45]
#    noise_weight = 0.5
#
#    l = QNoise( n_weight = 0.5, n_data = ( 0.5, 3, hist_weight ), h_weight = 0.5, h_data = ( 0.5, 3, hist_weight ) )
#
#    matrix = ([1,0,[(1, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (0, 0.0001)]], )
#
#    print l.evaluate( matrix )


## Chimas class
# Implements the Chimas algorithm proposed by Bondan for the LCN 2014 conference
class Chimas(object):
    """
    Chimas class
    Implements the Chimas algorithm proposed by Bondan for the LCN 2014 conference.
    """

    ##::TODO:: verificar os parametros, pq os parametros da funcao nao sao condizentes com a da documentacao
    def __init__(self, radio, learning_algorithm):
        """
        CTOR
        @param chimas_arch
        @param learning_algorithm Learning algorithm (Qnoise)
        @param channel_list List of Channels objects to sense.
        """

        self._radio = radio
        self._evaluater = learning_algorithm


    def run(self, channels, iterations=1):
        """
        Sense channels and evaluate them.
        @param channels
        @param iterations Number of evaluation.
        @return (SS result, learning result) when finished.
        """
        ln_result = 0

        if isinstance(channels, list):
            for i in range(0, iterations):
                ss_result    = self._radio.sense_channel_list(the_list = channels, sensing_time= 1)
                ln_result    = self._evaluater.evaluate( ss_result )
        else:
            ss_result     = self._radio.sense_channel(the_channels = channels, sensing_time = 1 )
            ln_result     = self._evaluater.evaluate( ss_result )

        return ln_result


if __name__ == '__main__':
    import sys
    import os
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    sys.path.insert(0, path)



    import OpERAFlow                            #pylint: disable=F0401
    from utils import Channel                   #pylint: disable=F0401
    from device import UHDSource, RadioDevice   #pylint: disable=F0401
    from sensing import RankingArch   #pylint: disable=F0401

    channel_list = [
            Channel(1, 205.25e6, 200e3),
            Channel(2, 211.25e6, 200e3),
            Channel(3, 219.25e6, 200e3),
        ]


    source = UHDSource()
    arch   = RankingArch(100)

    radio = RadioDevice(name = 'radio')
    radio.add_arch(source = source, arch = arch, sink = None, uhd_device = source, name = 'ss')

    top = OpERAFlow.OpERAFlow(name = "top_block")
    top.add_radio( radio, "radio")

    top.start()


    l = QNoise(
            n_weight = 0.5, n_data = ( 0.5, 3, [0.2, 0.35, 0.45] ),
            h_weight = 0.5, h_data = ( 0.5, 3, [0.2, 0.35, 0.45] ) )
    chimas = Chimas(radio, l)


    while True:
        #implementacao
        import time
        time.sleep(1)

        res = chimas.run( channel_list, 1)
        print res

    top.stop()
