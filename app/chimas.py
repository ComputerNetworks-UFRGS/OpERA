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
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)

from gnuradio import gr, gr_unittest, uhd

import random


# Project imports
from device           import * 
from algorithm        import QNoise, Chimas, decision
from utils.block      import GroupInN
from utils.sensing    import Logger, Channel, ChannelModel, ChannelModeler
from reception.architecture import *
from transmission     import SimpleTx


if __name__ == '__main__':
	##
	#
	def dump_list(it, direc, ss_result, qn_result):
		fname = "%s/ss_result_%d.txt" % (direc, it)

		with open(fname, 'w') as fd:
			fd.write("ss_channel sinr decision idle occupied qvalue\n")
			for channel in ss_result:
				sinr = np.sum( r for d,r in channel[2] ) / len( channel[2] )
				idle = np.sum( [1-d for d,r in channel[2] ])
				occupied = np.sum( [ d for d,r in channel[2] ])

				fd.write("{0[0]} {1} {0[1]} {2} {3} {4}\n".format(channel, sinr, int(idle), int(occupied), qn_result[1][qn_result[0].index(channel[0])]))


	## Build Gnuradio TopBlock
	def build_gnuradio(gain, channel_list):
		src = UHDSink()
		src.samp_rate = 195312

		def dist_callback():
			return random.expovariate(1/5.0)

		# Channel modeler is a device,
		# passed as parameter to the ranking_runner app
		uhd_sink   = UHDSink('addr=143.54.83.28')
		uhd_source   = UHDSource('addr=143.54.83.29')
		uhd_sink.samp_rate = uhd_source.samp_rate =195512
		device_sink = RadioDevice(
				the_source = gr.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True),
				the_sink = uhd_sink, uhd_device = uhd_sink
			)

		tx_path = simple_tx()

		device = ChannelModeler(
				device = OpERAFlow( device = device_sink, algorithm = None ),
				channel_list = channel_list,
				dist_callback = dist_callback)

		group_vlen = 1000

		tb = TopBlock('Chimas Top block')

		tb.rx = ranking_arch(device = device,
				detector = simple_ranking_detector(
					fft_size = 1024,
					mavg_size = 5,
					ed_threshold = 0.001),
				group_vlen = group_vlen
		)

		tb.connect( uhd_source.uhd, tb.rx )

		tb.start()
		return tb


	## Build QNoise class
	def build_q_noise(n_weight, n_data, h_weight, h_data):
		return QNoise(n_weight = n_weight, n_data = n_data, h_weight = h_weight, h_data = h_data)



	confs = [
			{'gain': 1, 'n_weight': 0.1 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.9, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 10}, # 0.5, 0.5
			{'gain': 1, 'n_weight': 0.2 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.8, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 10}, # 0.2, 0.8
			{'gain': 1, 'n_weight': 0.5 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.5, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 10}, # 0.2, 0.8
			{'gain': 1, 'n_weight': 0.8 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.2, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 10}, # 0.8, 0.2
			{'gain': 1, 'n_weight': 0.9 , 'n_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'h_weight': 0.1, 'h_data': (0.5, 3, [0.2, 0.35, 0.45] ), 'epochs': 10}, # 0.8, 0.2
	]
 
	for conf in confs:
		channel_list = [
				ChannelModel(idle_param=(199.25e6, 1.0), occupied_param=(205.25e6,0.0), channel=Channel(ch = 1,  freq = 199.25e6,bw = 200e3)),  # L
				ChannelModel(idle_param=(259.25e6, 0.9), occupied_param=(205.25e6, 0.1),channel=Channel(ch = 2, freq = 259.25e6, bw = 200e3)),  # L # record 21
				ChannelModel(idle_param=(427.25e6, 0.8), occupied_param=(205.25e6, 0.2),channel=Channel(ch = 3, freq = 427.25e6, bw = 200e3)),  # L sbt hd  28
				ChannelModel(idle_param=(325.25e6, 0.7), occupied_param=(205.25e6, 0.3),channel=Channel(ch = 4, freq = 325.25e6, bw = 200e3)),  # L band hdtv 32
				ChannelModel(idle_param=(337.25e6, 0.6), occupied_param=(205.25e6, 0.4),channel=Channel(ch = 5, freq = 337.25e6, bw = 200e3)),  # L rbs tv hd 34
				ChannelModel(idle_param=(719.25e6, 0.5), occupied_param=(205.25e6, 0.5),channel=Channel(ch = 6, freq = 719.27e6, bw = 200e3)),  # L tv cachoeirinha 44
				ChannelModel(idle_param=(291.25e6, 0.4), occupied_param=(205.25e6, 0.6),channel=Channel(ch = 7, freq = 291.25e6, bw = 200e3)),  # L ultra tv 48
				ChannelModel(idle_param=(581.25e6, 0.3), occupied_param=(205.25e6, 0.7),channel=Channel(ch = 8, freq = 581.25e6,bw = 200e3)),   # L rbs tv 12
				ChannelModel(idle_param=(671.25e6, 0.2), occupied_param=(205.25e6, 0.8),channel=Channel(ch = 9, freq = 671.25e6, bw = 200e3)),  # L tv cultura do vale 53
				ChannelModel(idle_param=(991.25e6, 0.1), occupied_param=(205.25e6, 0.9),channel=Channel(ch =10, freq = 991.25e6,bw = 200e3)),   # L tv urbanaa canal 55
				ChannelModel(idle_param=(205.25e6, 0.0), occupied_param=(205.25e6,1.0), channel=Channel(ch = 11, freq = 205.25e6,bw = 200e3)),  # L
		]

		# NEVER LET A TOP_BLOCK INSTANCE BE DESTROYED. WILL HANG THE PROGRAM.
		tb   = build_gnuradio( gain = conf['gain'], channel_list = channel_list )
		qnoise = build_q_noise(n_weight = conf['n_weight'], n_data = conf['n_data'], h_weight = conf['h_weight'], h_data = conf['h_data'])

		## Create dump directory
		d_ = "./results/gain_{0[gain]}_noise_weight_{0[n_weight]}_hist_weight_{0[h_weight]}".format(conf)
		if not os.path.exists( d_ ):
			os.makedirs( d_ ) 

		for it in  xrange(conf['epochs']):
			print "Iteraction %d/%d" % (it, conf['epochs'])

			ss_result = tb.rx.sense_channel_list(the_list = channel_list, sensing_time = 1)
			ln_result = qnoise.evaluate(ss_result)

			channel_list = reorder(channel_list, ln_result)

			dump_list(it, d_, ss_result, ln_result)
