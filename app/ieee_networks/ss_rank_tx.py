#!/usr/bin/env python

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


import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, path)

from gnuradio  import gr, blocks
from gnuradio.eng_option import eng_option
from optparse  import OptionParser
from struct    import * 
from threading import Thread
import time
import random

import numpy as np

#from device.uhd import *
from OpERAFlow import OpERAFlow
from device             import *
from algorithm.decision import EnergyDecision
from utils.block        import *
from reception.sensing  import EnergySSArch
from reception.packet   import PacketGMSKRx, PacketOFDMRx
from transmission       import PacketGMSKTx, PacketOFDMTx, SimpleTx
from utils.sensing      import Channel, TopBlock, Logger, ChannelModeler

## Builds the US top block.
# The RX path performs the ED sensing
# The TX path transmits a BER 
# @param options
def build_us_block(options):
	# TOP BLOCK
	tb = OpERAFlow(name = 'US')

	# RX PATH
	if not options.tx_only:
		uhd_source = UHDSource(device_addr = options.args)
		uhd_source.samp_rate = 195512
		device_source = RadioDevice(the_source = uhd_source, the_sink = blocks.probe_signal_f() )

		rx_path = EnergySSArch(
				device = device_source,
				fft_size  = 512,
				mavg_size = 5,
				algorithm = None
				#algorithm = EnergyDecision( th = 0.00000001 )
			)
		tb.add_path( abstract_arch = rx_path, radio_device = device_source, name_of_arch = 'rx')

	# TX PATH
	tx_path = PacketGMSKTx()

	uhd_sink = UHDSink(device_addr = options.args)
	uhd_sink.samp_rate = options.samp_rate
	radio_sink = RadioDevice( the_source = blocks.multiply_const_cc(0.27), the_sink = uhd_sink, uhd_device = uhd_sink)

	tb.add_path( tx_path, radio_sink, 'tx', connection_type = OpERAFlow.CONN_SINK)

	return tb

## Builds the UP top block.
# The RX path performs the ED sensing AND BER reception
# @param options
# @param channel_list
def build_up_block(options, channel_list):
	# TOP BLOCK
	tb = OpERAFlow(name = 'UP')

	def rx_callback(ok, payload):
		global t_rcv, t_cor

		t_rcv += 1
		t_cor += 1 if ok else 0

	def dist_callback():
		return random.expovariate(1/5.0)

    # RX PATH
	uhd_source = UHDSource(device_addr = options.args)
	uhd_source.samp_rate = options.samp_rate
	radio_source = RadioDevice(the_source = uhd_source, the_sink = None)

	rx_path = PacketGMSKRx( rx_callback )
	tb.add_path( rx_path, radio_source, 'rx' )


	# TX PATH
	if not options.tx_only:
		uhd_sink = UHDSink(device_addr = options.args)
		uhd_sink.samp_rate = 195512
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


## US LOOP
# @param tb
# @param channel_list
# @param channel
# @param options
def transmitter_loop(tb, channel_list, channel, options):

	# Connect to slave device
	import xmlrpclib
	proxy = xmlrpclib.ServerProxy( "http://%s:8000/" % options.slave_addr );

	start_t = time.time()
	proxy.client_started()
	proxy.set_channel( channel )

	Logger.register('transmitter', ['channel', 'status', 'pkt'])


	class TNamespace():
		pass

	# Sensing -> TX loop
	t_namespace = TNamespace()
	t_namespace.pkt_s = 0
	t_namespace.status = 0


	while time.time() < (start_t + options.duration):
		can_transmit = True

		if not options.tx_only:
			# Sense
			t_namespace.status =  tb.rx.sense_channel(channel_list[channel], options.sensing_duration )

			# Update
			print t_namespace.status
			if t_namespace.status > 0.000005 : # GMSK threahold
			#if t_namespace.status > 0.000000005 :
				print str(channel_list[ channel ]) +  ' is occupied'

				t_now = time.clock()

				## Q-NOISE AQUI.
				channel = (channel + 1) % len(channel_list)
				####
				can_transmit = False

				# Change channel
				proxy.set_channel( channel )
				tb.tx.radio.center_freq = channel_list [ channel ]

				t_elapsed = time.clock() - t_now

		# Transmit
		if can_transmit:
			payload = 0
			if options.pkt_size > 1:
				bytelist = [1] * (options.pkt_size/4)
				payload = pack('%sH' % len(bytelist), *bytelist)
			else:
				bytelist = ['a', ]
				payload = pack('%sc' % 1, *bytelist)

			# thred sending packets
			def send_thread():
				while t_namespace.pkt_sending:
					tb.tx.send_pkt( payload )
					t_namespace.pkt_s += 1
					time.sleep(0.001)
				#t_namespace.count += 1

			# init thread
			th = Thread( target = send_thread )
			t_namespace.pkt_sending = True
			th.start()

			# wait for options.sending_duration 
			time.sleep( options.sending_duration )

			# stop sending
			t_namespace.pkt_sending = False
			th.join()

		Logger.append('transmitter', 'channel',  channel)
		Logger.append('transmitter', 'status',   t_namespace.status)
		Logger.append('transmitter', 'pkt',      t_namespace.pkt_s)

	proxy.close_app()


## UP LOOP
# @param tb
# @param channel_list
# @param channel
# @param options
def receiver_loop(tb, channel_list, channel, options):
	import xmlrpclib
	from SimpleXMLRPCServer import SimpleXMLRPCServer

	class MyNamespace:
		pass


	g_namespace = MyNamespace()
	g_namespace.tb = tb
	g_namespace.options = options
	g_namespace.server_run = True

	class StoppableXMLRPCServer(SimpleXMLRPCServer):
		"""Override of TIME_WAIT"""
		allow_reuse_address = True

		def __init__(self, options):
			SimpleXMLRPCServer.__init__(self, options)
			self.stop = False

		def serve_forever(self):
			while not self.stop:
				self.handle_request()
			print 'exiting server'

		def shutdown(self):
			self.stop = True
			return 0

	server = StoppableXMLRPCServer( (options.slave_addr, 8000) )
	g_namespace.th = Thread( target = server.serve_forever )

	# Flag que indica quando a execucao deve parar
	g_namespace.run = False
	g_namespace.interferer_channel = 0

    # RPC para troca do canal
	def set_channel(channel):
		print "Received command to handoff to channel  ", channel

		if not g_namespace.options.tx_only:
			g_namespace.tb.tx.radio.center_freq = channel_list[ channel ]
		g_namespace.tb.rx.radio.center_freq = channel_list[ channel ]

		g_namespace.interferer_channel = channel
		return 1

	# Fecha app
	def close_app():
		print "Received command to close"
		g_namespace.run = False
		return 1

	# Notifica que comecou a executar
	def client_started():
		g_namespace.run = True
		return 1

	Logger.register('receiver', ['channel', 'pkt', 'start_time'])
	Logger.set('receiver', 'start_time', time.time())

	# Registra funcoes no servidor XML e inicia thread do servidor
	server.register_function( set_channel, 'set_channel' )
	server.register_function( close_app, 'close_app' )
	server.register_function( client_started, 'client_started' )

	g_namespace.th.start()
	print "Receiver listening for commands in port 8000"
	print "\t... Waiting for client_started call"

	while g_namespace.run == False:
		1;
	print "\t...client connected"

	global t_rcv, t_cor

	channel = 0

	# Enquanto nao recebeu a notificacao de parada, continua a execucao
	while g_namespace.run:
		print " ... r: ", t_rcv, ", c: ", t_cor
		time.sleep(1)
		if not options.tx_only:
			Logger.append('receiver', 'channel', channel, time.time() )

	Logger.append('receiver', 'pkt', t_rcv)
	

	print "Shuting down Server"
	server.shutdown()
	print "\t ... Server exited"


##
def main( options ):
	channel_list = [
			Channel(ch = 1, freq = 200.25e6, bw = 200e3),  # L
			Channel(ch = 2, freq = 259.25e6, bw = 200e3),  # L # record 21
			Channel(ch = 3, freq = 427.25e6, bw = 200e3),  # L sbt hd  28
			Channel(ch = 4, freq = 325.25e6, bw = 200e3),  # L band hdtv 32
			Channel(ch = 5, freq = 337.25e6, bw = 200e3),  # L rbs tv hd 34
			Channel(ch = 6, freq = 719.25e6, bw = 200e3),  # L tv cachoeirinha 44
			Channel(ch = 7, freq = 291.25e6, bw = 200e3),  # L ultra tv 48
	]

	tb = build_up_block(options, channel_list) if  options.interferer else build_us_block(options)

	tb.start()
	time.sleep( 3 )

	channel = 0;

	if not options.interferer:
		# initial frequencies
		if not options.tx_only:
			tb.rx.radio.center_freq = channel_list[ channel ]

		tb.tx.radio.center_freq = channel_list[ channel ]
		transmitter_loop(tb, channel_list, channel, options)
	else:
		global t_rcv
		global t_cor
		t_rcv = 0
		t_cor = 0

		tb.rx.radio.center_freq = channel_list[ channel ]

		if not options.tx_only:
			tb.tx.radio.center_freq = channel_list[ channel ]
		receiver_loop(tb, channel_list, channel, options)

	time.sleep(1)
	tb.stop()
	tb.wait()

if __name__ == '__main__':
	gr.enable_realtime_scheduling()

	parser=OptionParser(option_class=eng_option)
	parser.add_option("-a", "--args", type="string", default="''",
			help="UHD device address args [default=%default]")
	parser.add_option("-A", "--antenna", type="string", default='TX/RX',
			help="select Rx Antenna where appropriate")
	parser.add_option("-g", "--gain", type="eng_float", default=None,
			help="set gain in dB (default is midpoint)")
	parser.add_option("", "--samp-rate", type="eng_float", default=195312,
			help="set device sample rate")
	parser.add_option("", "--interferer", action="store_true", default=False,
			help="set device sample rate")
	parser.add_option("", "--slave-addr", type="string", default='localhost',
			help="Slave (interferer) IP Address. If --interferer is used, this is the server address.")
	parser.add_option("", "--duration", type="float", default='10',
			help="Execution time. Finishes both UP and US. (master device only)")
	parser.add_option("", "--log", action="store_true", default=False,
			help="Enable Logging")
	parser.add_option("", "--mode", type="choice", choices=["txonly", "ss"],
			help="txonly or ss")
	parser.add_option("", "--pkt-size", type="int", default=256,
			help="Size of packet to be send.")
	parser.add_option("", "--platform", type="string", default="mac",
			help="Machine running the test.")
	parser.add_option("", "--iteration", type="int", default=-1,
			help="Test Iteration.")
	parser.add_option("", "--sending-duration", type="float", default=1.0,
			help="TX duration between sensing.")
	parser.add_option("", "--sensing-duration", type="float", default=0.1,
			help="SS duration between transmission.")

	(options, args) = parser.parse_args()

	options.tx_only = options.mode == 'txonly'

	print '#######################################'
	print '# mode: ' + str(options.mode)
	print '# ss  : ' + str(options.sensing_duration)
	print '# sd  : ' + str(options.sending_duration)
	print '#######################################'

	if options.log:
		Logger._enable = True
	main( options )

	# save log
	dev = './receiver' if options.interferer else './transmitter'
	Logger.dump('./{os}_results'.format(os = options.platform),
			'/' + dev + '_' + options.platform + '_dur_' + str(int(options.duration)) + '_pkt_' + str(options.pkt_size) + '_burst_' + '%2.1f' % options.sending_duration + '_ssdur_' + '%2.1f' % options.sensing_duration + ('_mode_txonly' if options.tx_only else '_mode_ss'), options.iteration)
