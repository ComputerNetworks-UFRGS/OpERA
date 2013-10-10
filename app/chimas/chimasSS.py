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

#!/usr/bin/env python

import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, uhd

import random


# Project imports
from OpERAFlow		  import OpERAFlow
from device           import * 
from algorithm        import QNoise, Chimas, decision
from utils.block      import GroupInN
from utils.sensing    import Logger, Channel, ChannelModel, ChannelModeler
from reception.architecture import *
from transmission     import SimpleTx


##
#
def dump_list(it, direc, ss_result, qn_result):
	print '#### Saving Results'
	fname = "%s/ss_result_%d.txt" % (direc, it)

	with open(fname, 'w') as fd:
		fd.write("ss_channel sinr decision idle occupied qvalue\n")
		for channel_data in ss_result:
			channel = channel_data[0]
			print channel

			sinr = np.sum( r for r,d in channel_data[1] ) / len( channel_data[1] )
			idle = np.sum( [1-d for r,d in channel_data[1] ])
			occupied = np.sum( [ d for r,d in channel_data[1] ])

			fd.write("{0} {1} {2} {3} {4} {5}\n".format(channel, sinr, 1 if occupied > idle else 0, int(idle), int(occupied), qn_result[1][qn_result[0].index(channel)]))


## Build Gnuradio TopBlock
def build_gnuradio(gain, channel_list):

	# @param channel Channel object
	def dist_callback(channel, status):
		if status:
			return 1;
		else:
			return channel.channel

	tb = OpERAFlow('Chimas Top block')

	# RX PATH
	uhd_source   = UHDSource()
	uhd_source.samp_rate = 195312

	device_source = RadioDevice(the_source = uhd_source, the_sink = None)
	
	max_items_group = 1000
	rx_path = RankingArch(device = device_source,
			detector = SimpleRankingDetector(
				fft_size = 1024,
				mavg_size = 5,
				ed_threshold = 0.0001),
			max_items_group = max_items_group
	)

	tb.add_path(rx_path, device_source, 'rx')

	# TX PATH - CAUSES INTERFERENCE
	uhd_sink = UHDSink()
	uhd_sink.samp_rate = 195312
	radio_sink = RadioDevice(
			the_source = blocks.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True),
			the_sink = uhd_sink, uhd_device = uhd_sink
		)
	radio_proxy = ChannelModeler(
			device = radio_sink,
			channel_list = channel_list,
			dist_callback = dist_callback)
	tx_path = SimpleTx()

	tb.add_path( tx_path, radio_proxy, 'tx')
	return tb


## Build QNoise class
def build_q_noise(n_weight, n_data, h_weight, h_data):
	return QNoise(n_weight = n_weight, n_data = n_data, h_weight = h_weight, h_data = h_data)


confs = [
		#{'gain': 1, 'n_weight': 0.1 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.9, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 100}, # 0.5, 0.5
		{'gain': 1, 'n_weight': 0.2 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.8, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 300}, # 0.2, 0.8
		{'gain': 1, 'n_weight': 0.5 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.5, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 300}, # 0.5, 0.5
		{'gain': 1, 'n_weight': 0.8 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.2, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 300}, # 0.8, 0.2
		#{'gain': 1, 'n_weight': 0.9 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.1, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 100}, # 0.8, 0.2
]

for conf in confs:
	channel_list = [
			Channel(ch = 1,  freq = 199.25e6, bw = 200e3),  # L # record 21
			Channel(ch = 2,  freq = 259.25e6, bw = 200e3),  # L # 
			Channel(ch = 3,  freq = 427.25e6, bw = 200e3),  # L sbt hd  28
			Channel(ch = 4,  freq = 719.27e6, bw = 200e3),  # L tv cachoeirinha 44 STRONG SIGNAL
			Channel(ch = 5,  freq = 671.25e6, bw = 200e3),  # L tv cultura do vale 53
			Channel(ch = 6,  freq = 991.25e6, bw = 200e3),  # L tv urbanaa canal 55 VERY STRONG SIGNAL
			Channel(ch = 7, freq =  230.25e6, bw = 200e3),  # L
			Channel(ch = 8,  freq = 581.25e6, bw = 200e3),  # L rbs tv 12
			Channel(ch = 9,  freq = 325.25e6, bw = 200e3),  # L band hdtv 32 VERY STRONG SIGNAL
			Channel(ch =10,  freq = 291.25e6, bw = 200e3),  # L ultra tv 48 STRONG SIGNAL
			Channel(ch =11,  freq = 337.25e6, bw = 200e3),  # L rbs tv hd 34 VERY STRONG SIGNAL
	]

	# NEVER LET A TOP_BLOCK INSTANCE BE DESTROYED. WILL HANG THE PROGRAM.
	tb     = build_gnuradio( gain = conf['gain'], channel_list = channel_list )
	qnoise = build_q_noise(n_weight = conf['n_weight'], n_data = conf['n_data'], h_weight = conf['h_weight'], h_data = conf['h_data'])

	tb.start()

	## Create dump directory
	d_ = "./results/gain_{0[gain]}_noise_weight_{0[n_weight]}_hist_weight_{0[h_weight]}".format(conf)
	if not os.path.exists( d_ ):
		os.makedirs( d_ ) 

	for it in  xrange(conf['epochs']):
		print "Iteraction %d/%d" % (it, conf['epochs'])

		ss_result = []
		for channel in channel_list:
			tb.tx.radio.center_freq = channel
			ss_result.append( (channel.channel, tb.rx.sense_channel(the_channel = channel, sensing_time = 1)) )

		ln_result = qnoise.evaluate(ss_result)

		def reorder(channel_list, qn_result):
			for i in xrange( len(channel_list) ):
				for j in xrange(i+1, len(channel_list) ):
					if qn_result[1][i] < qn_result[1][j]:
						qn_result[0][i], qn_result[0][j] = qn_result[0][j], qn_result[0][i]
						qn_result[1][i], qn_result[1][j] = qn_result[1][j], qn_result[1][i]
						channel_list[i], channel_list[j] = channel_list[j], channel_list[i]

			return channel_list

		channel_list = reorder(channel_list, ln_result)
		print ln_result

		dump_list(it, d_, ss_result, ln_result)

	tb.stop()
	tb.wait()

os._exit(0)
