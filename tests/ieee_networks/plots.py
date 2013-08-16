#!/usr/bin/env python

import subprocess
from optparse import OptionParser
import re
import math
from math import sqrt



DIR = './{os}_results/{dev}_{os}_dur_{duration}_pkt_{pkt_size}_burst_{sending_burst}_ssdur_{ssdur}_mode_{mode}/'
PKT_FILE = DIR + '{dev}_pkt_{it}.txt'
APP_FILE = DIR + '{dev}_elapsed_{it}.txt'
PKT_PARSED_FILE = './{os}_results/parsed_pkt_{os}_{mode}_{duration}_{sending_burst}_{ssdur}'
APP_PARSED_FILE = './{os}_results/parsed_app'
PERFORMANCE_FILE = 'performance'

MAX_IT = 4
ITERATIONS = {'mac': 20, 'app': 20, 'hp': 20, 'p4': 4 }



numeric_const_pattern = r"""
	 [-+]? # optional sign
	 (?:
		 (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
		 |
		 (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
	 )
	 # followed by optional exponent part if desired
	 (?: [Ee] [+-]? \d+ ) ?
"""

number_regexp = re.compile(numeric_const_pattern, re.VERBOSE)


##
#
def average(llist):
	_sum = 0.0
	for s in llist:
		_sum += s
	return _sum / len(llist) if len(llist) else 0


##
#
def stddev(llist):
	avg = int(average(llist))

	_var = 0
	for v in llist:
		_var += ((v - avg) ** 2)

	return math.sqrt(_var / len(llist) ) if len(llist) else 0


##
#
def parse_pkt(options):
	outfile = PKT_PARSED_FILE.format(os = options.os,
			mode = options.mode,
			duration = options.duration,
			sending_burst = options.sending_burst,
			ssdur = options.sensing_duration) + '.txt'

	tx_pkts    = {'32':[], '64':[], '128':[], '256':[], '512':[], '1024':[], '2048':[], '4096':[]}
	rx_pkts    = {'32':[], '64':[], '128':[], '256':[], '512':[], '1024':[], '2048':[], '4096':[]}
	tx_changed = {'32':[], '64':[], '128':[], '256':[], '512':[], '1024':[], '2048':[], '4096':[]}

	###
	# Get pkt from files
	###
	def readDictPkt( options, dic, raw_infile ):
		for it in xrange(0, ITERATIONS[options.os]):
			for key in dic:
				infile = raw_infile.format( dev = options.device,
						os = options.os,
						duration = options.duration,
						pkt_size = key,
						sending_burst = options.sending_burst,
						ssdur = options.sensing_duration,
						mode = options.mode,
						it = it)

				with open(infile, 'r') as fd:
					llines = fd.readlines()
					if len( llines ) and len( llines[-1] ) > 1:
						x = int(number_regexp.findall(llines[-1])[0]) 
						if x:
							dic[key].append( x )
					else:
						dic[key].append( 0 )

		return dic

	###
	###
	def readDictApp( options, dic, raw_infile ):
		for it in xrange(0, ITERATIONS[options.os]):
			for key in dic:
				infile = raw_infile.format( dev = options.device,
						os = options.os,
						duration = options.duration,
						pkt_size = key,
						sending_burst = options.sending_burst,
						ssdur = options.sensing_duration,
						mode = options.mode,
						it = it)

				try:
					with open(infile, 'r') as fd:
						llines = fd.readlines()
						x = len(llines)
						if x:
							dic[key].append( x )
						else:
							dic[key].append( 0 )
				except IOError:
					print "WARNING: File %s doesnt exist" % infile
					return None
		return dic

	options.device = 'transmitter'
	tx_pkts    = readDictPkt(options, tx_pkts,    PKT_FILE)
	tx_changed = readDictApp(options, tx_changed, APP_FILE)

	options.device = 'receiver'
	rx_pkts = readDictPkt(options, rx_pkts, PKT_FILE)

	###
	# Save in file
	###
	with open(outfile, 'w+') as fd:
		if not tx_changed:
			fd.write('line pkt_size tx rx tx_stddev rx_stddev sqrt_n_elem\n' )
			fd.write('1 32 %d %d %d %d %d\n'   %  (average(tx_pkts['32']  ), average(rx_pkts['32']  ), stddev(tx_pkts['32']  ),  stddev(rx_pkts['32']  ), sqrt(len(tx_pkts['32']  )) ))
			fd.write('2 64 %d %d %d %d %d\n'   %  (average(tx_pkts['64']  ), average(rx_pkts['64']  ), stddev(tx_pkts['64']  ),  stddev(rx_pkts['64']  ), sqrt(len(tx_pkts['64']  )) ))
			fd.write('3 128 %d %d %d %d %d\n'  %  (average(tx_pkts['128'] ), average(rx_pkts['128'] ), stddev(tx_pkts['128'] ),  stddev(rx_pkts['128'] ), sqrt(len(tx_pkts['128'] )) ))
			fd.write('4 256 %d %d %d %d %d\n'  %  (average(tx_pkts['256'] ), average(rx_pkts['256'] ), stddev(tx_pkts['256'] ),  stddev(rx_pkts['256'] ), sqrt(len(tx_pkts['256'] )) ))
			fd.write('5 512 %d %d %d %d %d\n'  %  (average(tx_pkts['512'] ), average(rx_pkts['512'] ), stddev(tx_pkts['512'] ),  stddev(rx_pkts['512'] ), sqrt(len(tx_pkts['512'] )) ))
			fd.write('6 1024 %d %d %d %d %d\n' %  (average(tx_pkts['1024']), average(rx_pkts['1024']), stddev(tx_pkts['1024']),  stddev(rx_pkts['1024']), sqrt(len(tx_pkts['1024'])) ))
			fd.write('7 2048 %d %d %d %d %d\n' %  (average(tx_pkts['2048']), average(rx_pkts['2048']), stddev(tx_pkts['2048']),  stddev(rx_pkts['2048']), sqrt(len(tx_pkts['2048'])) ))
			fd.write('8 4096 %d %d %d %d %d\n' %  (average(tx_pkts['4096']), average(rx_pkts['4096']), stddev(tx_pkts['4096']),  stddev(rx_pkts['4096']), sqrt(len(tx_pkts['4096'])) ))
		else:
			fd.write('line pkt_size tx rx tx_stddev rx_stddev n_elem tx_changed\n' )
			fd.write('1 32 %d %d %d %d %d %f\n'    %  (average(tx_pkts['32'] ), average(rx_pkts['32']  ), stddev(tx_pkts['32']  ),  stddev(rx_pkts['32']  ), sqrt(len(tx_pkts['32']  )), average(tx_changed['32']  ) ))
			fd.write('2 64 %d %d %d %d %d %f\n'   %  (average(tx_pkts['64']  ), average(rx_pkts['64']  ), stddev(tx_pkts['64']  ),  stddev(rx_pkts['64']  ), sqrt(len(tx_pkts['64']  )), average(tx_changed['64']  ) ))
			fd.write('3 128 %d %d %d %d %d %f\n'  %  (average(tx_pkts['128'] ), average(rx_pkts['128'] ), stddev(tx_pkts['128'] ),  stddev(rx_pkts['128'] ), sqrt(len(tx_pkts['128'] )), average(tx_changed['128'] ) ))
			fd.write('4 256 %d %d %d %d %d %f\n'  %  (average(tx_pkts['256'] ), average(rx_pkts['256'] ), stddev(tx_pkts['256'] ),  stddev(rx_pkts['256'] ), sqrt(len(tx_pkts['256'] )), average(tx_changed['256'] ) ))
			fd.write('5 512 %d %d %d %d %d %f\n'  %  (average(tx_pkts['512'] ), average(rx_pkts['512'] ), stddev(tx_pkts['512'] ),  stddev(rx_pkts['512'] ), sqrt(len(tx_pkts['512'] )), average(tx_changed['512'] ) ))
			fd.write('6 1024 %d %d %d %d %d %f\n' %  (average(tx_pkts['1024']), average(rx_pkts['1024']), stddev(tx_pkts['1024']),  stddev(rx_pkts['1024']), sqrt(len(tx_pkts['1024'])), average(tx_changed['1024']) ))
			fd.write('7 2048 %d %d %d %d %d %f\n' %  (average(tx_pkts['2048']), average(rx_pkts['2048']), stddev(tx_pkts['2048']),  stddev(rx_pkts['2048']), sqrt(len(tx_pkts['2048'])), average(tx_changed['2048']) ))
			fd.write('8 4096 %d %d %d %d %d %f\n' %  (average(tx_pkts['4096']), average(rx_pkts['4096']), stddev(tx_pkts['4096']),  stddev(rx_pkts['4096']), sqrt(len(tx_pkts['4096'])), average(tx_changed['4096']) ))



##
#
def plot_bars(options):
	outfile = PKT_PARSED_FILE.format(os = options.os,
			mode = options.mode,
			duration = options.duration,
			sending_burst = options.sending_burst,
			ssdur = options.sensing_duration)

	gnuplot_script = """
set terminal pdf enhanced size 4,2
set output '{outfile}'


set boxwidth 0.7 relative
set style fill solid 1 border -1

set style data histogram
set style histogram cluster gap 1

#set logscale y

set xlabel 'Packet Size (Bytes)'
set ylabel 'Total Bytes'

set xtics ('32' 1, '64' 2,  '128' 3, '256' 4, '512' 5,  '1024' 6, '2048' 7, '4096' 8)

set key inside top 

plot '{infile}' using ($3*$2) t 'Transmitter', '' using ($4*$2):xtic(2)  t 'Receiver'

	""".format( outfile = outfile + '_bytes.pdf', infile = outfile + '.txt' )

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( gnuplot_script )


##
#
def plot_line(options):
	PLOT1_LNAME = './{os}_results/lines'.format(os = options.os)
	PLOT1_LFILES = [
			PKT_PARSED_FILE.format(os = options.os, mode = 'txonly', duration = '60', sending_burst = '60.0', ssdur = '0.0') + '.txt',
			PKT_PARSED_FILE.format(os = options.os, mode = 'ss', duration = '60', sending_burst = '2.0', ssdur = '0.1') + '.txt',
			PKT_PARSED_FILE.format(os = options.os, mode = 'ss', duration = '60', sending_burst = '2.0', ssdur = '0.5') + '.txt',
			PKT_PARSED_FILE.format(os = options.os, mode = 'ss', duration = '60', sending_burst = '2.0', ssdur = '1.0') + '.txt',
	]

	gnuplot_script = """
set terminal pdf enhanced size 4,2 dashed
set output '{outfile}'

set xlabel 'Packet Size [Bytes]'
set ylabel 'Throughput [Mbps]'

set xtics ('32' 1, '64' 2,  '128' 3, '256' 4, '512' 5,  '1024' 6, '2048' 7, '4096' 8)


# lines
set style line 1 linetype 1 linecolor 1 pt 9 ps 1
set style line 2 linetype 2 linecolor 2 pt 4 ps 1.8
set style line 3 linetype 5 linecolor 3 pt 6 ps 0.8
set style line 4 linetype 4 linecolor 12 pt 1

set style line 11 linetype 1 linecolor 1 pt 9 ps 1
set style line 21 linetype 1 linecolor 2 pt 4 ps 1.8
set style line 31 linetype 1 linecolor 3 pt 6 ps 0.8
set style line 41 linetype 1 linecolor 12 pt 1

set key bottom right

plot '{infile1}' using 1:(8*${col}*$2/1000000/60) t 'Without SS' w linespoints ls 1, '{infile2}' using 1:(8*${col}*$2/1000000/60) t 'SS 0.1s' w linespoints ls 2, '{infile3}' using 1:(8*${col}*$2/1000000/60) t 'SS 0.5s' w linespoints ls 3, '{infile4}' using 1:(8*${col}*$2/1000000/60) t 'SS 1.0s' w linespoints ls 4, '{infile1}' using 1:(8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '' w errorbars ls 11,  '{infile2}' using 1:(8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '' w errorbars ls 21,  '{infile3}' using 1:(8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '' w errorbars ls 31,  '{infile4}' using 1:(8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '' w errorbars ls 41

	"""
	tx_script = gnuplot_script.format( outfile = PLOT1_LNAME + '_tx_bytes.pdf', infile1 = PLOT1_LFILES[0], infile2 = PLOT1_LFILES[1], infile3 = PLOT1_LFILES[2], infile4 = PLOT1_LFILES[3], col = '3', var = '5')
	rx_script = gnuplot_script.format( outfile = PLOT1_LNAME + '_rx_bytes.pdf', infile1 = PLOT1_LFILES[0], infile2 = PLOT1_LFILES[1], infile3 = PLOT1_LFILES[2], infile4 = PLOT1_LFILES[3], col = '4', var = '6')


	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( tx_script )

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( rx_script )


##
#
def plot_stack(options):
	OUTPUT_NAME= './comparison'
	INPUT_NAME = [
			PKT_PARSED_FILE.format(os = 'mac', mode = 'txonly', duration = '60', sending_burst = '60.0', ssdur = '0.0') + '.txt',
			PKT_PARSED_FILE.format(os = 'hp', mode = 'txonly', duration = '60', sending_burst = '60.0', ssdur = '0.0') + '.txt',
			PKT_PARSED_FILE.format(os = 'p4', mode = 'txonly', duration = '60', sending_burst = '60.0', ssdur = '0.0') + '.txt',
	]

	gnuplot_script = """
set terminal pdf enhanced size 4,2
set output '{outfile}'

set boxwidth 0.9 absolute
set style fill solid 1.00 border lt -1

set style histogram errorbar gap 5 title offset character 0,0,0
set style data histograms


set xlabel 'Packet Size [Bytes]'
set ylabel 'Throughput [Mbps]'

set xrange [0.5:8.5]
set yrange [0:4]

set xtics ('32' 1, '64' 2,  '128' 3, '256' 4, '512' 5,  '1024' 6, '2048' 7, '4096' 8)

set key inside top left

plot '{infile1}' using (8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '2.70 GHz Core i5' linecolor rgb "#2e75b5",  '{infile2}' using (8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '2.33 GHz C2D E6550' linecolor rgb "#deebf6",  '{infile3}' using (8*${col}*$2/1000000/60):(1.725*(8*${var}*$2/1000000/60)/$7) t '2.8 GHz Pentium 4' linecolor rgb "#bfbfbf"
	"""
	
	tx_script = gnuplot_script.format(outfile = OUTPUT_NAME + '_tx_bytes.pdf', infile1 = INPUT_NAME[0], infile2 = INPUT_NAME[1], infile3 = INPUT_NAME[2], col = '3', var = '5')
	rx_script = gnuplot_script.format(outfile = OUTPUT_NAME + '_rx_bytes.pdf', infile1 = INPUT_NAME[0], infile2 = INPUT_NAME[1], infile3 = INPUT_NAME[2], col = '4', var = '6')

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( tx_script )

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( rx_script )


##
#
def plot_app(options):
	PLOT1_LNAME = './{os}_results/app'.format(os = options.os)
	PLOT1_LFILES = [
			PKT_PARSED_FILE.format(os = options.os, mode = 'ss', duration = '60', sending_burst = '2.0', ssdur = '0.1') + '.txt',
			PKT_PARSED_FILE.format(os = options.os, mode = 'ss', duration = '60', sending_burst = '2.0', ssdur = '0.5') + '.txt',
			PKT_PARSED_FILE.format(os = options.os, mode = 'ss', duration = '60', sending_burst = '2.0', ssdur = '1.0') + '.txt',
	]


	for f in PLOT1_LFILES:
		try:
			print f
			with open(f, 'r') as fd:
				pass
		except IOError:
			print "WARNING: File %s doesnt exist" % f
			return

	gnuplot_script = """
set terminal pdf enhanced size 4,2
set output '{outfile}'

set xlabel 'Packet Size (Bytes)'
set ylabel 'Channel Switches'

set xtics ('32' 1, '64' 2,  '128' 3, '256' 4, '512' 5,  '1024' 6, '2048' 7, '4096' 8)

set key bottom right

plot '{infile1}' using 8 t 'SS 0.1s' w linespoints ls 2, '{infile2}' using 8 t 'SS 0.5s' w linespoints ls 3, '{infile3}' using 8 t 'SS 1.0s' w linespoints ls 4

	"""
	
	app_script = gnuplot_script.format( outfile = PLOT1_LNAME + '_switch.pdf', infile1 = PLOT1_LFILES[0], infile2 = PLOT1_LFILES[1], infile3 = PLOT1_LFILES[2])

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( app_script )


##
#
def parse_appbars(options):
	tx_pkts    = ['32', '64', '128', '256', '512', '1024', '2048', '4096']
	ss_durs = {'0.1': [], '0.5': [], '1.0': []}

	outfile = APP_PARSED_FILE.format(os = options.os) + '.txt'

	for key in ss_durs:
		for tx in tx_pkts:
			for it in xrange(0, ITERATIONS[options.os]):
				infile = APP_FILE.format( dev = 'transmitter',
							os = options.os,
							duration = options.duration,
							pkt_size = tx,
							sending_burst = options.sending_burst,
							ssdur = key,
							mode = options.mode,
							it = it)

				try:
					with open(infile, 'r') as fd:
							llines = fd.readlines()
							x = len(llines)
							if x:
								ss_durs[key].append( x )
							else:
								ss_durs[key].append( 0 )
				except IOError:
					print "WARNING: parsing_appbars: File %s doesnt exist" % infile
					return None

	with open(outfile, 'w+') as fd:
		fd.write('line ss_dur ch_switches std_dev sqrt_n_elem total_ch\n')
		fd.write('1 0.1 %f %f %f 28\n' % (average(ss_durs['0.1']), stddev(ss_durs['0.1']), sqrt(len(ss_durs['0.1']))))
		fd.write('2 0.5 %f %f %f 24\n' % (average(ss_durs['0.5']), stddev(ss_durs['0.5']), sqrt(len(ss_durs['0.5']))))
		fd.write('3 1.0 %f %f %f 20\n' % (average(ss_durs['1.0']), stddev(ss_durs['1.0']), sqrt(len(ss_durs['1.0']))))

	return 1

def plot_appbars(options):
	infile = APP_PARSED_FILE.format(os = options.os) + '.txt'
	outfile = APP_PARSED_FILE.format(os = options.os) + '.pdf'

	gnuplot_script = """
set terminal pdf enhanced size 4,2
set output '{outfile}'

set boxwidth 0.5 relative
set style data histogram
set style histogram rowstacked
set style fill solid 1 border -1

set xlabel 't_{{SS}} [s]'
set ylabel 'Operations Performed'

#unset ylabel

set xrange [0.5:3.5]
set yrange [0:30]

set xtics ('0.1' 1, '0.5' 2,  '1.0' 3)

set key inside top 

plot  '{infile}' using 1:6 t 'Spectrum Sensing' w boxes linecolor rgb '#deebf6', '{infile}' using 1:3:(1.725*($4)/$5) t 'Channel Switching' w boxerror linecolor rgb "#2e75b5",

""".format( outfile = outfile, infile =  infile)

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( gnuplot_script )

##
#
def parse_proc(options):
	transmitter_file = 'mon_transmitter.txt'
	receiver_file = 'mon_receiver.txt'


	## Parse transmitter file
	def parseProcFile(file_name, mapper):
		data  = dict.fromkeys(mapper.keys(), 0)
		count = dict.fromkeys(mapper.keys(), 0)

		with open(file_name, 'r') as fd:
			for line in fd:
				# get clock tic value ( [0] is part of the block name)
				val = float(number_regexp.findall(line)[1])

				xxx = {}

				# for each key of mapper
				for key in mapper:
					# check if this key has the 'block name'
					tups = mapper[key]
					for t in tups:
						# if has, then add the clock tic 
						if t in line:
							if 'ch switching' in t:
								val = (val * 2.7 * (10**9)/(2.7*(10**9)))  # total clock cycles in 10 minutes test
							count[ key ] += 1
							data[ key ] += val


		return data, count


	RECEPTION     = 1
	TRANSMISSION = 2
	APPLICATION   = 3

	mapper_tx = {'OFDM Modulation': ('multiply_const_cc0', 'ofdm_insert_preamble0', 'ofdm_mapper_bcv0', 'ofdm_cyclic_prefixer0', 'fft_vcc_fftw1', ), 'Energy Detector': ('stream_to_vector0', 'fft_vcc_fftw0', 'complex_to_mag_squared0', 'energy_calculator0', 'probe_signal_f0'), 'USRP Reception': ('gr uhd usrp source0', ), 'USRP Transmission': ('gr uhd usrp sink0'), 'Channel Switching Application': ('ch switching tx0', )}
	mapper_rx = {'OFDM Demodulation': ('fft_filter_ccc0', 'add_const_cc0', 'frequency_modulator_fc0', 'multiply_cc1', 'null_sink0', 'ofdm_frame_acquisition0', 'ofdm_frame_sink0', 'fft_vcc_fftw0', 'ofdm_sampler0', 'peak_detector_fb0', 'multiply_cc1', 'frequency_modulator_fc0', 'add_const_ff0', 'sample_and_hold_ff0', 'fir_filter_fff1', 'complex_to_arg0', 'divide_ff0', 'fir_filter_ccf0', 'complex_to_mag_squared1', 'multiply_ff0', 'multiply_cc0' 'fir_filter_fff0', 'complex_to_mag_squared0', 'conjugate_cc0', 'delay0'  ), 'USRP Reception': ('gr uhd usrp source0', ), 'Channel Switching Application': ('ch switching rx0', )}
	mapper_id = {
			'OFDM Modulation': TRANSMISSION,
			'OFDM Demodulation': RECEPTION,
			'Energy Detector': RECEPTION,
			'USRP Reception': RECEPTION,
			'USRP Transmission': TRANSMISSION,
			'Channel Switching Application': APPLICATION,
			
	}
	mapper_txt =  {TRANSMISSION: 'Transmission', RECEPTION: 'Reception', APPLICATION: 'Application'}

	tx_data, tx_count = parseProcFile(transmitter_file, mapper_tx)
	rx_data, rx_count = parseProcFile(receiver_file,    mapper_rx)


	for key in tx_data:
		tx_data[key] /= tx_count[key]
	for key in rx_data:
		rx_data[key] /= rx_count[key]

	outfile = PERFORMANCE_FILE + '.txt'
	with open(outfile, 'w+') as fd:
		tx_total_cicles = sum([k[1] for k in tx_data.iteritems()])
		rx_total_cicles = sum([k[1] for k in rx_data.iteritems()])

		print 'tx: %f' % tx_total_cicles
		print 'rx: %f' % rx_total_cicles
		

		fd.write('id block_name cicles per_cicles type\n')

		print tx_data
		print tx_count
		for key in tx_data:
			fd.write("\"%s\" \"%s\" %f %f tx\n" % (mapper_txt[mapper_id[key]], key, tx_data[key], tx_data[key]/tx_total_cicles*100.0))
		for key in rx_data:
			fd.write("\"%s\" \"%s\" %f %f rx\n" % (mapper_txt[mapper_id[key]], key, rx_data[key], rx_data[key]/rx_total_cicles*100.0))



	###
	###
	tx_dist = dict.fromkeys(mapper_txt, 0)
	rx_dist = dict.fromkeys(mapper_txt, 0)


	with open('g_' + outfile, 'w+') as  fd:
		for key in mapper_txt:
			for t in tx_data:
				if mapper_id[t] == key:
					tx_dist[key] += (tx_data[t]/tx_total_cicles*100.0)

		fd.write('tx %f %f %f\n' % (tx_dist[TRANSMISSION], tx_dist[RECEPTION], tx_dist[APPLICATION]))

		for key in mapper_txt:
			for t in rx_data:
				if mapper_id[t] == key:
					rx_dist[key] += (rx_data[t]/rx_total_cicles*100.0)
		fd.write('rx %f %f %f\n' % (rx_dist[TRANSMISSION], rx_dist[RECEPTION], rx_dist[APPLICATION]))

##
#
def plot_proc(options):
	INFILE = PERFORMANCE_FILE + '.txt'
	OUTFILE = PERFORMANCE_FILE

	R_script = """
pdf('{outfile}_tx.pdf', width=12, height=10)
colors <- c('#3276B3', '#DEEBF5', '#005eb3', '#b3323f', '#b33235')
table  <- read.table('{infile}', header = TRUE)
slices <- c(table$per_cicles[1:5])
lbls   <- table$block_name[1:5]
lbls   <- paste( lbls, round(slices))
lbls   <- paste( lbls, "%", sep="")
pie(slices, labels = lbls, col = colors, radius=0.4, angle=180)

colors <- c('#005eb3', '#b3323f', '#deebf5')
pdf('{outfile}_rx.pdf', width=12, height=10)
slices <- c(table$per_cicles[6:8])
lbls   <- table$block_name[6:8]
lbls   <- paste( lbls, round(slices))
lbls   <- paste( lbls, "%", sep="")
pie(slices, labels = lbls, col = colors, radius=0.4)

dev.off()
	""".format( outfile = OUTFILE , infile = INFILE )

	proc = subprocess.Popen(['R --no-save'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( R_script )

	OUTFILE = 'g_' + PERFORMANCE_FILE
	gnuplot_script = """
set terminal pdf enhanced size 4,2
set output '{outfile}'

set boxwidth 0.7 relative
set style fill solid 1 border -1

set key samplen 1 
set key right 

set xrange[-0.5:1.8]

set ylabel "% of Processing Time"
set ytic (10, 30, 50, 70, 90)

set style data histograms
#set style histogram rowstacked

set xtics ('Base Station' 0, 'Secundary User' 1) 

plot '{infile}' using 2 t 'Transmission' linecolor rgb "#2e75b5", '' using 3 t 'Reception' linecolor rgb "#deebf6", '' using 4 t 'Application' linecolor rgb "#bfbfbf"
	""".format( outfile = OUTFILE + '.pdf', infile = 'g_performance.txt' )

	proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
	proc.communicate( gnuplot_script )


##
#
def main(options):
	if not options.comparison:
		parse_pkt( options )

		plot_bars(options)
		plot_line(options)

		if options.mode != 'txonly':
			if parse_appbars(options):
				plot_app(options)
				plot_appbars(options)
	else:
		plot_stack(options)

		parse_proc(options)
		plot_proc(options)


if __name__ == '__main__':
	parser=OptionParser()
	parser.add_option("-o", "--os", type="string", default="mac",
			help="OS (mac, linux, win) [default=%default]")
	parser.add_option("", "--duration", type="int", default=60,
			help="Test Duration [default=%default]")
	parser.add_option("-m", "--mode", type="string", default="txonly",
			help="Mode (txonly, ss) [default=%default]")
	parser.add_option("", "--sending-burst", type="string", default='0.0',
			help="Sending burst duration [default=%default]")
	parser.add_option("", "--sensing-duration", type="string", default='0.0',
			help="Sensing time [default=%default]")
	parser.add_option("", "--comparison", action='store_true', default=False,
			help="Plot comparison charts [default=%default]")


	(options, args) = parser.parse_args()

	print '#######################################'
	print '# mode: ' + options.mode
	print '# ss  : ' + options.sensing_duration
	print '# sd  : ' + options.sending_burst
	print '#######################################'

	main( options )
