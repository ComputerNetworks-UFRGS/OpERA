# -*- coding: utf-8 -*- 
import numpy as np
import scipy as sp
import scipy.stats
import math
import re
import subprocess as subprocess

FILES = {
	"ed": "energy_decision_decision_{it}.txt" ,
	"wfd": "waveform_decision_decision_{it}.txt",
	"cfd": "cyclo_decision_decision_{it}.txt",
	"hier_cfd" : "hier_decision_{it}.txt",
	"hier_wfd" : "hier_decision_{it}.txt",
	"ata_wfd" : "bayes_decision_decision_{it}.txt",
	"ata_cfd" : "bayes_decision_decision_{it}.txt",

	"unc_ed": "energy_decision_decision_{it}.txt" ,
	"unc_wfd": "waveform_decision_decision_{it}.txt",
	"unc_cfd": "cyclo_decision_decision_{it}.txt",
	"unc_hier_cfd" : "hier_decision_{it}.txt",
	"unc_hier_wfd" : "hier_decision_{it}.txt",
	"unc_ata_wfd" : "bayes_decision_decision_{it}.txt",
	"unc_ata_cfd" : "bayes_decision_decision_{it}.txt",

	}
SS = ['ed', 'wfd', 'cfd', 'hier_cfd', 'ata_wfd', 'ata_cfd' ]
SS = ['unc_ed', 'unc_wfd', 'unc_cfd', 'unc_hier_cfd', 'unc_ata_wfd', 'unc_ata_cfd' ]
SS = ['ed', 'wfd', 'cfd', 'hier_cfd', 'ata_cfd']
OCC = ['01', '05', '09' ]
PFA = ["00", "50", "100" ]
TOTAL = 10
TOTAL_IT = range(TOTAL)

EBN0 = ['-20', '-15', '-10', '-5', '0', '5']
FILE_PATH = "single/ebn0_{ebn0}/{ss}_{occ}_{pfa}/"

PARSED_FILE_PATH_ACC="parsed/txt/{ss}_{occ}_{ebn0}_{pfa}_x_{x}_acc.txt"
PARSED_FILE_PATH_DUR="parsed/txt/{ss}_{occ}_{ebn0}_{pfa}_x_{x}_dur.txt"
PARSED_FILE_SINGLE_PDF="parsed/txt/{ss}_{mod}{occ}_single_x_{x}_{t}.txt"
PARSED_FILE_COMP_PDF="parsed/txt/all_{mod}{occ}_{pfa}_comp_x_{x}_{t}.txt"



FINAL_RES = { }

SINGLE_PLOT = "plot '{filename}'  w lines t ''"


def mean_confidence_interval(data, confidence=0.95):
    a = np.array(data) #pylint: disable=E1101
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a) #pylint: disable=E1101

    #ATENTCAO: MUDAR DISTRIBUICAO
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1) #pylint: disable=E1101
    return m, m-h, m+h


def parse_results_acc(ebn0, ss, occ, pfa):

    ###############################################
    # PARSE FILES
    results_acc = []
    total_decs = 0

    data_arr = {"00": 0.0, "01": 0.0, "10": 0.0, "11": 0.0 };

    print '----- PARSING ' +  FILE_PATH.format(ebn0 = ebn0, ss = ss, occ = occ, pfa = pfa)
    try:
	    for it in TOTAL_IT:
		    filename = FILE_PATH.format(ebn0 = ebn0, ss = ss, occ = occ, pfa = pfa)
		    filename += FILES[ss].format(it = it)

		    with open(filename, 'r') as fd:
			for l in fd:
			    for k in data_arr:
				if k in l:
				    data_arr[k] += 1.0

		    try:
			p_d = (data_arr["11"] + data_arr["00"]) / sum(data_arr.itervalues())
		    except:
			p_d = 0.0

		    results_acc.append( p_d )
		    total_decs += sum(data_arr.itervalues())

	    m, m_l, m_h = mean_confidence_interval(results_acc)

	    FINAL_RES['acc'][ss][occ][pfa][ebn0]['mean'] = m * 100
	    FINAL_RES['acc'][ss][occ][pfa][ebn0]['error'] = (m-m_l) * 100
	    FINAL_RES['acc'][ss][occ][pfa][ebn0]['total'] = total_decs/TOTAL

    except:
	print '---- File not found: ', filename
	FINAL_RES['acc'][ss][occ][pfa] = None


def parse_results_dur(ebn0, ss, occ, pfa):
	'''
	'''


	if FINAL_RES['acc'][ss][occ][pfa] is None:
		return


	results = []
	for it in TOTAL_IT:	
		filename = FILE_PATH.format(ebn0 = ebn0, ss = ss, occ = occ, pfa = pfa)
		filename += 'global_global_{it}.txt'.format(it = it)

		sensing_total_dur = 0
		with open(filename, 'r') as fd:
			for line in fd:
				if 'clock:' in line:
					sensing_total_dur, = re.findall(r"[-+]?\d*\.\d+|\d+", line)
			results.append( float(sensing_total_dur) )

	m, m_l, m_h = mean_confidence_interval( results )

	FINAL_RES['dur'][ss][occ][pfa][ebn0]['mean'] = 1000  * (m / FINAL_RES['acc'][ss][occ][pfa][ebn0]['total'])
	FINAL_RES['dur'][ss][occ][pfa][ebn0]['error'] = 1000 *((m-m_l) / FINAL_RES['acc'][ss][occ][pfa][ebn0]['total'])


def write_parsed_result_ebn0(ss, occ):

    for ebn0 in EBN0:
        str_file_acc = ""
	str_file_dur = ""

        for pfa in PFA:
   	    # pfa results doest not exists: PASS
	    if FINAL_RES['acc'][ss][occ][pfa] is None:
	        continue

	    # acc results
            the_result =  FINAL_RES['acc'][ss][occ][pfa][ebn0]
            str_file_acc += "%s %f %f\n" % (pfa, the_result['mean'], the_result['error'])

	    # dur results
            the_result =  FINAL_RES['dur'][ss][occ][pfa][ebn0]
            str_file_dur += "%s %f %f\n" % (pfa, the_result['mean'], the_result['error'])

	if str_file_acc != '':

		# write acc file and plot
		filename = PARSED_FILE_PATH_ACC.format(ss = ss, occ = occ, ebn0 = ebn0, pfa='all', x='pfa')
		with open(filename, "w+") as fd:
		    fd.write( str_file_acc )

		if len(str_file_acc.split('\n')) > 2 and False:
			plot_parsed(
				filename = filename,
				plot_line = SINGLE_PLOT.format(filename = filename),
				configs = {
					'range_y':'set yrange [0:1.0]',
					'range_x':'set xrange [0:100]',
					'label_x':'P_{FA}',
					'label_y':'Accuracy',
				}
			)

		# write acc file and plot
		filename = PARSED_FILE_PATH_DUR.format(ss = ss, occ = occ, ebn0 = ebn0, pfa='all', x='pfa')
		with open(filename, "w+") as fd:
		    fd.write( str_file_dur )

		if len(str_file_dur.split('\n')) > 2 and False:
			plot_parsed(
				filename = filename,
				plot_line = SINGLE_PLOT.format(filename = filename),
				configs = {
					'range_y':'',
					'range_x':'set xrange [0:100]',
					'label_x':'P_{FA}',
					'label_y':'Mean Sensing Time',
				}
			)

def write_parsed_result_pfa(ss, occ):
    for pfa in PFA:
	# pfa results doest not exists: PASS
	if FINAL_RES['acc'][ss][occ][pfa] is None:
		continue

        str_file_acc = ""
        str_file_dur = ""

        for ebn0 in EBN0:
            the_result =  FINAL_RES['acc'][ss][occ][pfa][ebn0]
            str_file_acc += "%s %f %f\n" % (ebn0, the_result['mean'], the_result['error'])

            the_result =  FINAL_RES['dur'][ss][occ][pfa][ebn0]
            str_file_dur += "%s %f %f\n" % (ebn0, the_result['mean'], the_result['error'])

	if str_file_acc != '':
		# plot file acc
		filename = PARSED_FILE_PATH_ACC.format(ss = ss, occ = occ, ebn0 = 'all', pfa=pfa, x='ebno')
		with open(filename, "w+") as fd:
		    fd.write( str_file_acc )
		if len(str_file_acc.split('\n')) > 2 and False:
			plot_parsed(
				filename = filename,
				plot_line = SINGLE_PLOT.format(filename = filename),
				configs = {
					'range_y':'set yrange [0:1.0]',
					'range_x':'set xrange [-20:5]',
					'label_x':'Eb/N0',
					'label_y':'Accuracy',
				}
			)

		# plot file dur
		filename = PARSED_FILE_PATH_DUR.format(ss = ss, occ = occ, ebn0 = 'all', pfa=pfa, x='ebno')
		with open(filename, "w+") as fd:
		    fd.write( str_file_dur )
		if len(str_file_dur.split('\n')) > 2 and False:
			plot_parsed(
				filename = filename,
				plot_line = SINGLE_PLOT.format(filename = filename),
				configs = {
					'range_y':'',
					'range_x':'set xrange [-20:5]',
					'label_x':'Eb/N0',
					'label_y':'Mean Sensing Duration',
				}
			)


def plot_parsed(filename, plot_line, configs):
    GNUPLOT_SCRIPT= """
    set term pdf enhanced dashed size 4,3
    set output '{outfile}'

    set style line 10 lt 1 lw 1 pt 11 lc 4 ps 0.0
    set style line 11 lt 1 lw 1 pt 11 lc 4 ps 1.2

    set style line 20 lt 1 lw 1 pt 9 lc 3 ps 0.0
    set style line 21 lt 1 lw 1 pt 9 lc 3 ps 1.2

    set style line 30 lt 1 lw 1 pt 20 lc 7 ps 0.0
    set style line 31 lt 1 lw 1 pt 20 lc 7 ps 1.2

    set style line 40 lt 1 lw 1 pt 5 lc 1 ps 0.0
    set style line 41 lt 1 lw 1 pt 5 lc 1 ps 1.2

    set style line 50 lt 1 lw 1 pt 13 lc 5 ps 0.0
    set style line 51 lt 1 lw 1 pt 13 lc 5 ps 1.2

    set style line 60 lt 1 lw 1 pt 3 lc 9 ps 0.0
    set style line 61 lt 1 lw 1 pt 3 lc 9 ps 1.2


    set xlabel '{label_x}'
    set ylabel '{label_y}'

    {range_y}
    {range_x}

    {extra_opts}

    set key {key_pos} inside box opaque width 1

    {plot_line}
"""

    tmp = GNUPLOT_SCRIPT.format(
            plot_line = plot_line,
            outfile = filename.replace("txt", "pdf"),
	    label_y = configs['label_y'],
	    range_y = configs['range_y'],
	    label_x = configs['label_x'],
	    range_x = configs['range_x'],
	    key_pos = 'bottom right',
	    extra_opts = configs["extra_opts"] if "extra_opts" in configs else ""  
        )

    print "----- Plotting ", filename
    proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
    proc.communicate( tmp )

def get_in_file(ss, occ, pfa, ebn0, t):
	F = {'acc': PARSED_FILE_PATH_ACC,
	     'dur': PARSED_FILE_PATH_DUR
	}

	filename = F[t].format(ss=ss, occ=occ, pfa=pfa, ebn0=ebn0, x = 'pfa')
	


def plot_nice_pfas(ss, occ, key, mod = ''):
	F = {
		'acc': PARSED_FILE_PATH_ACC,
	     	'dur': PARSED_FILE_PATH_DUR
	}
	CONFIGS = {
		'acc':  {
			'range_y':'set yrange [0:1.0]',
			'range_x':'set xrange [-20:5]',
			'label_x':'EBN0 [dB]',
			'label_y':'Accuracy',
			'extra_opts': 'unset ytics\nunset ylabel' 
		},

		'dur':  {
			'range_y':'',
			'range_x':'set xrange [-20:5]',
			'label_x':'EBN0 [dB]',
			'label_y':'Sensing time',
			'extra_opts': 'unset ytics\nunset ylabel' 
		}
	}




	pfas = [("00",   10 ,'0'),
		("30",  20 ,'25'),
		("50",  30 ,'50'),
		("80",  40 ,'75'),
		("100", 50, '100'),
	]	

	files = []
	filetemplate = F[key]
	
	for pf, _ , _  in pfas:
		files.append(
			filetemplate.format(ss = ss, occ = occ, ebn0='all', pfa=pf, x='ebno', mod = mod)
		)


	plot_str = 'plot '
	for idx  in range(len(pfas)):
		if idx > 0:
			plot_str += ','
		f = files[idx]	
		ls = pfas[idx][1]
		t = pfas[idx][2]

		plot_str += "\'%s\'  w linespoints ls %d t \'\'"   % (f, ls)
		plot_str += ",\'%s\' w errorbar    ls %d t \'%s\'" % (f, ls + 1, t)

	plot_parsed(
		filename=PARSED_FILE_SINGLE_PDF.format(ss=ss, occ=occ, x='ebn0', t=key),
		plot_line = plot_str,
		configs = CONFIGS[key]
	)


def plot_comparison(occ, key, mod = ''):
	F = {
		'acc': PARSED_FILE_PATH_ACC,
	     	'dur': PARSED_FILE_PATH_DUR
	}
	CONFIGS = {
		'acc':  {
			'range_y':'set yrange [0:100]',
			'range_x':'set xrange [-20:5]',
			'label_x':'E_B/N_0 [dB]',
			'label_y':'Sensing Accuracy [%]',
			'extra_opts': '' 
		},

		'dur':  {
			'range_y':'set yrange [0:1]',
			'range_x':'set xrange [-20:5]',
			'label_x':'E_B/N_0 [dB]',
			'label_y':'Sensing Duration [ms]',
			'extra_opts': '' 
		}
	}

	dec = [ ("%sed"      % mod,  10 , 'ED'),
		("%swfd"     % mod,  20 , 'WFD'),
		("%scfd"     % mod,  30 , 'CFD'),
		("%shier_cfd"% mod,  40 , 'TSHA'),
		("%sata_wfd" % mod,  50 , 'ATA-ED/WFD'),
		("%sata_cfd" % mod,  60 , 'ATA-ED/CFD'),
	]

	pfas = ["00", "50", "100"]

	
	for pf in pfas:
		configs = dict(CONFIGS[key])
		files = []
		filetemplate = F[key]

		for d, _, _ in dec:
			files.append(
				filetemplate.format(ss=d, occ=occ, ebn0='all', pfa=pf, x='ebno', mod = mod)
			)

		plot_str = 'plot '
		for idx  in range(len(dec)):
			if idx > 0:
				plot_str += ','
			f =  files[idx]	
			ls = dec[idx][1]
			t =  dec[idx][2]
			THE_CONDITION = ""

			plot_str += "\'%s\'  %s  w linespoints ls %d t \'\'"   % (f, THE_CONDITION, ls)
			plot_str += ",\'%s\' %s  w errorbar    ls %d t \'%s\'" % (f, THE_CONDITION, ls + 1, t)


		plot_parsed(
			filename=PARSED_FILE_COMP_PDF.format(occ=occ, x='ebn0', pfa=pf,t=key, mod = mod),
			plot_line = plot_str,
			configs = configs
		)



if __name__ == '__main__':

    for t in ('acc', 'dur'):
	    FINAL_RES[t] = {}
	    for ss in SS:
		FINAL_RES[t][ss] = {}
		for  occ in OCC:
		    FINAL_RES[t][ss][occ] = {}
		    for pfa in PFA:
			FINAL_RES[t][ss][occ][pfa] = {}
			for ebn0 in EBN0:
			    FINAL_RES[t][ss][occ][pfa][ebn0] = {}

    for ebn0 in EBN0:
        for ss in SS:
            for occ in OCC:
                for pfa in PFA:
		    pass
                    #parse_results_acc(ebn0, ss, occ, pfa)
                    #parse_results_dur(ebn0, ss, occ, pfa)

    for ss in SS:
        for occ in OCC:
	    pass
            #write_parsed_result_ebn0(ss, occ)
            #write_parsed_result_pfa(ss, occ)


#    for t in ('acc', 'dur'):
#	    for occ in OCC:
#		for ss in SS:
#			plot_nice_pfas(ss, occ, t)

    for t in ('acc', 'dur'):
	for occ in OCC:
		plot_comparison(occ, t)
