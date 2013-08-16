#!/usr/bin/env python

import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, path)

from gnuradio  import gr
from gnuradio.eng_option import eng_option
from optparse  import OptionParser
from struct    import * 
from threading import Thread
import time

import numpy as np



#from device.uhd import *
from device.uhd               import *
from ssf.algorithm            import EnergyAlgorithm
from ssf.uhd.block_util       import *
from ssf.uhd.uhd_wrapper      import UHDWrapper
from ssf.uhd.detectors.energy import EnergySSArch
from ss_utils                 import Channel, TopBlock, Logger

## Builds the US top block.
# The RX path performs the ED sensing
# The TX path transmits a BER 
def buildUSBlock(options):
	# TOP BLOCK
	tb = TopBlock(name = 'TX BLOCK')

	# RX PATH
	if not options.tx_only:
		uhd_source = UHDSource(device_addr = options.args)
		uhd_source.samp_rate = options.samp_rate
		device_source = UHDDevice(the_source = uhd_source, the_sink = gr.probe_signal_f() )

		rx_path = EnergySSArch(
				device = device_source,
				fft_size  = 1024,
				mavg_size = 10,
				algorithm = EnergyAlgorithm( th = 0.0001 )
				)
		tb.rx = UHDWrapper( device = device_source, algorithm = rx_path )
		tb.connect( device_source.source, rx_path )


	# TX PATH
	tx_path = PacketGMSKTx()

	uhd_sink = UHDSink(device_addr = options.args)
	uhd_sink.samp_rate = options.samp_rate
	device_sink = UHDDevice( the_source = None, the_sink = uhd_sink, uhd_device = uhd_sink)

	tb.tx = UHDWrapper( device = device_sink,   algorithm = tx_path )

	tb.connect( tx_path, device_sink.sink )

	return tb

## Builds the UP top block.
# The RX path performs the ED sensing AND BER reception
def buildUPBlock(options):
	# TOP BLOCK
	tb = TopBlock(name = 'RX BLOCK')

	def callback_rx(ok, payload):
		global t_rcv, t_cor

		t_rcv += 1
		t_cor += 1 if ok else 0

		Logger.append('receiver', 'received', (t_rcv, t_cor, time.time()))


    # RX PATH
	uhd_source = UHDSource(device_addr = options.args)
	uhd_source.samp_rate = options.samp_rate
	device_source = UHDDevice(the_source = uhd_source, the_sink = None)

	rx_path = PacketGMSKRx( callback_rx )

	tb.rx = UHDWrapper( device = device_source, algorithm = rx_path)
	tb.connect( device_source.source, rx_path )


	# TX PATH
	if not options.tx_only:
		uhd_sink = UHDSink(device_addr = options.args)
		uhd_sink.samp_rate = options.samp_rate
		device_sink = UHDDevice(
				the_source = gr.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True),
				the_sink = uhd_sink, uhd_device = uhd_sink
			)

		tx_path = simple_tx()
		tb.tx = UHDWrapper( device = device_sink, algorithm = None )
		tb.connect( device_sink.source, tx_path, device_sink.sink )


	return tb


## US LOOP
def transmitter_loop(tb, channel_list, channel, options):

	# Connect to slave device
	import xmlrpclib
	proxy = xmlrpclib.ServerProxy( "http://%s:8000/" % options.slave_addr );

	start_t = time.time()
	proxy.clientStarted()

	Logger.register('transmitter', ['channel', 'status', 'pkt_send'])

	# Sensing -> TX loop
	cont = 0
	pkt_s = 0

	status = 0


	def sendDummys(freq):
		# envia em uma frequencia diferente do receptor
		freq2 = options.freq + 100e6

		tb.tx.center_freq = freq2
		time.sleep(0.1)

		for i in xrange(100, 300):
			bytelist = i 
			payload = pack('!H', bytelist)

			tb.tx.sendPkt( payload )

		print "Sended dummy pkts"
		time.sleep(0.25)
		tb.tx.center_freq = freq
		time.sleep(0.15)
	#sendDummys(options.freq)

	while time.time() < (start_t + options.duration):
		can_transmit = True

		if not options.tx_only:
			# Sense
			status =  tb.rx.senseChannel( channel_list[ channel ], 1 )
			print channel_list[channel], " : ", "IDLE" if status ==0 else "OCCUPIED", " - Pkt Send: ", pkt_s

			# Update
			if status != 0:
				channel = (channel + 1) % len(channel_list)
				can_transmit = False

				# Change channel
				proxy.set_channel( channel )
				tb.tx.center_freq = channel_list [ channel ]

		# Transmit
		if can_transmit:
			bytelist = [1] * options.pkt_size
			payload = pack('%sH' % len(bytelist), *bytelist)

			for i in xrange(0, 1):
				tb.tx.sendPkt( payload )
				#time.sleep(0.15)
				pkt_s += 1
				print "pkt_s ", pkt_s
			cont += 1

		cur_time = time.time()
		Logger.append('transmitter', 'channel',  (channel , cur_time))
		Logger.append('transmitter', 'status',   (status  , cur_time))
		Logger.append('transmitter', 'pkt_send', (pkt_s, cur_time))

	proxy.closeApp()


## UP LOOP
def receiver_loop(tb, channel_list, channel, options):
	import xmlrpclib
	from SimpleXMLRPCServer import SimpleXMLRPCServer

	class MyNamespace:
		pass

	g_namespace = MyNamespace()
	g_namespace.tb = tb

	server = SimpleXMLRPCServer( (options.slave_addr, 8000) )
	g_namespace.th = Thread( target = server.serve_forever )

	# Flag que indica quando a execucao deve parar
	g_namespace.run = False

    # RPC para troca do canal
	def set_channel(channel):
		print "Received command to handoff to channel  ", channel
		g_namespace.tb.rx.center_freq = channel_list[ channel ]
		return 1

	# Fecha app
	def closeApp():
		global continue_running
		print "Received command to close"

		g_namespace.run = False

		return 1

	# Notifica que comecou a executar
	def clientStarted():
		g_namespace.run = True
		return 1

	Logger.register('receiver', ['interfering', 'received', 'start_time'])
	Logger.set('receiver', 'start_time', time.time())

	# Registra funcoes no servidor XML e inicia thread do servidor
	server.register_function( set_channel, 'set_channel' )
	server.register_function( closeApp, 'closeApp' )
	server.register_function( clientStarted, 'clientStarted' )

	g_namespace.th.start()
	print "Receiver listening for commands in port 8000"
	print "\t... Waiting for clientStarted call"

	while g_namespace.run == False:
		1;
	print "\t...client connected"

	global t_rcv, t_cor

	channel = 0
	freq = options.freq

	# Enquanto nao recebeu a notificacao de parada, continua a execucao
	while g_namespace.run:
		if not options.tx_only:
			print "Interfering in Channel ", channel_list[ channel ]
			print " ... r: ", t_rcv, ", c: ", t_cor
			tb.tx.center_freq = channel_list[ channel ]

			time.sleep(1)
			channel = (channel + 1) % len(channel_list)
			Logger.append('receiver', 'interfering', (channel, time.time()) )

	print "Shuting down Server"
	server.shutdown()
	g_namespace.th.join()



##
def main( options ):
	channel_list = [
			Channel(ch = 1, freq = 199.25e6, bw = 200e3),  # L
			Channel(ch = 2, freq = 259.25e6, bw = 200e3),  # L # record 21
			Channel(ch = 3, freq = 427.25e6, bw = 200e3),  # L sbt hd  28
			Channel(ch = 4, freq = 325.25e6, bw = 200e3),  # L band hdtv 32
			Channel(ch = 5, freq = 337.25e6, bw = 200e3),  # L rbs tv hd 34
			Channel(ch = 6, freq = 719.25e6, bw = 200e3),  # L tv cachoeirinha 44
			Channel(ch = 7, freq = 291.25e6, bw = 200e3),  # L ultra tv 48
			Channel(ch = 8, freq = 581.25e6, bw = 200e3),  # L rbs tv 12
			Channel(ch = 9, freq = 671.25e6, bw = 200e3),  # L tv cultura do vale 53
			Channel(ch =10, freq = 991.25e6, bw = 200e3),  # L tv urbanaa canal 55
			Channel(ch =11, freq = 205.25e6, bw = 200e3),  # L
	]

	tb = buildUPBlock(options) if  options.interferer else buildUSBlock(options)

	tb.start()
	time.sleep( 3 )

	channel = 0;

	if not options.interferer:
		# initial frequencies
		if not options.tx_only:
			tb.rx.center_freq = options.freq

		tb.tx.center_freq = options.freq

		transmitter_loop(tb, channel_list, channel, options)
	else:
		global t_rcv
		global t_cor
		t_rcv = 0
		t_cor = 0

		tb.rx.center_freq = options.freq
		time.sleep( 2 )
		receiver_loop(tb, channel_list, channel, options)


	time.sleep(1)
	tb.stop()
	tb.wait()

if __name__ == '__main__':
	parser=OptionParser(option_class=eng_option)
	parser.add_option("-a", "--args", type="string", default="''",
			help="UHD device address args [default=%default]")
	parser.add_option("-A", "--antenna", type="string", default='TX/RX',
			help="select Rx Antenna where appropriate")
	parser.add_option("-f", "--freq", type="eng_float", default=199.25e6,
			help="set frequency to FREQ", metavar="FREQ")
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
	parser.add_option("", "--tx-only", action="store_true", default=False,
			help="Run without sensing, channel handoff and interference. only TX-RX.")
	parser.add_option("", "--pkt-size", type="int", default=256,
			help="Size of packet to be send.")
	parser.add_option("", "--platform", type="string", default="mac",
			help="Machine running the test.")
	parser.add_option("", "--iteration", type="int", default=-1,
			help="Test Iteration.")

	(options, args) = parser.parse_args()


	if options.log:
		Logger._enable = True
	main( options )

	# save log
	dev = './receiver' if options.interferer else './transmitter'
	Logger.dump('./results', '/' + dev + '_' + options.platform + '_' + str(int(options.duration)) + '_' + str(options.pkt_size) + '_txonly' if options.tx_only else '_ss', options.iteration)
