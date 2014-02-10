# -*- coding: utf-8 -*- 
import numpy as np
import scipy as sp
import scipy.stats
import math
import re
import subprocess as subprocess


SCENARIOS = ("my", "my_unc_11", "hierarchical", "hierarchical_unc_11")
SCENARIOS_POS = ("_waveform_05", "_waveform_01", "_waveform_09", "_cyclostationary_05", "_cyclostationary_09", "_cyclostationary_01")

RES = ('mean_time', 'acc')
#SCENARIOS_POS = ("_cyclostationary_05", )
#RES = ('acc', )


FILES = {
        'mean_time': 'global_global_{it}.txt',
        'acc': 'bayes_decision_hiphotesis_{it}.txt',
        'energy': 'bayes_decision_energy_{it}.txt',
        'corr': 'waveform_decision_correlation_{it}.txt'
}
EBN0 = ["-20.0", "-19.0", "-18.0", "-17.0", "-16.0", "-15.0", "-14.0", "-13.0", "-12.0", "-11.0", "-10.0", "-9.0", "-8.0", "-7.0", "-6.0", "-5.0", "-4.0", "-3.0", "-2.0", "-1.0", "0.0", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0", "10.0", "11.0", "12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0", "20.0" ]
FILE_PATH = "{scenario}/ebn0_{ebn0}/"

PARSED_FILE_PATH = "{scenario}_{res}.txt"
TOTAL_IT = range(40)

FINAL_RES = { }


def mean_confidence_interval(data, confidence=0.40):
    a = np.array(data) #pylint: disable=E1101
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a) #pylint: disable=E1101

    #ATENTCAO: MUDAR DISTRIBUICAO
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1) #pylint: disable=E1101
    return m, m-h, m+h


def remove_additional_status(scenario, res):
    ###############################################
    # REMOVE ADDITIONAL DATA
    for ebn0 in EBN0:
        data_arr = []
        for it in TOTAL_IT:
            filename = FILE_PATH.format(scenario = scenario, ebn0 = ebn0)
            filename += '/' + FILES[res].format(it = it)

            try:
                with open(filename, 'r') as fd:
                    print '----- PARSING ' + filename
                    for line in fd:
                        try:
                            data, additional = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                            data_arr.append( data )
                        except:
                            pass

                    with open(filename + '_r', 'w+') as fd:
                        fd.write("\n".join(data_arr))
            except IOError:
                print "----- %s not found" % filename


def parse_results_multiline(scenario, res):

    ###############################################
    # NESTED FUNC TO PARSE ACC
    def parse_acc(fd, scenario, ebn0, it):
        hit = error = 0
        for line in fd:
            try:
                hiphotesis, correct = re.findall(r"[-+]?\d*\.\d+|\d+", line)

                hiphotesis = int(hiphotesis)
                correct = int(correct)

                if hiphotesis > 2:
                    hiphotesis = 1

                if int(hiphotesis) == int(correct):
                    hit += 1
                else:
                    error += 1
            except:
                if line == "(1.0, 0)\n" or line == "(1024.0, 0)\n":
                    error +=1
                elif line == "(0.0, 1)\n" or line == "(0.0, 1024.0)\n":
                    error +=1
                else:
                    hit += 1


        return float(hit)/ (hit + error)

    ###############################################
    # NESTED FUNC TO PARSE MEAN_TIME
    def parse_mean_time(fd, scenario, ebn0, it):
        sensing_total_dur = 0
        for line in fd:
            if 'clock:' in line:
              sensing_total_dur, = re.findall(r"[-+]?\d*\.\d+|\d+", line)

        with open(FILE_PATH.format(scenario = scenario, ebn0 = ebn0) + '/' + FILES['acc'].format(it = it)) as xxx:
            n_sensing = len(xxx.readlines())

        return float(sensing_total_dur)/n_sensing * 1000.0

    ###############################################
    # PARSE FILES
    for ebn0 in EBN0:
        data_arr = []
        for it in TOTAL_IT:
            filename = FILE_PATH.format(scenario = scenario, ebn0 = ebn0)
            filename += FILES[res].format(it = it)

            try:
                with open(filename, 'r') as fd:
                    print '----- PARSING ' + filename
                    if res == 'acc':
                        data_arr.append( parse_acc(fd, scenario, ebn0, it) )
                    elif res == 'mean_time':
                        data_arr.append( parse_mean_time(fd, scenario, ebn0, it) )
            except IOError:
                print "----- %s not found" % filename

        m, m_l, m_h = mean_confidence_interval(data_arr)
        print 'M: %f - ERR: %f' % (m, m-m_l)

        FINAL_RES[scenario][res][ebn0]['mean'] = m
        FINAL_RES[scenario][res][ebn0]['error'] = m-m_l
        FINAL_RES[scenario][res][ebn0]['data'] = data_arr

def write_parsed_result(scenario, res):
    filename = PARSED_FILE_PATH.format(scenario = scenario, res = res)

    the_result =  FINAL_RES[scenario][res]

    str_file = ""
    for ebn0 in EBN0:
        if 'mean' in the_result[ebn0]:
            str_file += "%s %f %f\n" % (ebn0, the_result[ebn0]['mean'], the_result[ebn0]['error'])

    fd = open(filename, 'w')
    fd.write( str_file )
    fd.close()

def plot_parsed(key, labels, scenario_pos):
    LINES = (
            ('my', 10, "Proposal"),
            ('hierarchical', 20, "Hierarchical"),
            ('hierarchical_unc_11', 30, "Hierarchical +10% Uncertainty"),
            #('hierarchical_unc_09', 40, "Hierarchical -10% Uncertainty"),
            #('sarsa', 50, "Sarsa")
      )

    lines = "plot "
    for idx, _t in enumerate(LINES):
        l, ls, t = _t
        l = l + scenario_pos
        if idx > 0:
            lines += ','
        lines += "\'%s_%s.txt\' w linespoints ls %d t \'\'" % (l, key, ls)
        lines += ",\'%s_%s.txt\' w errorbar ls %d t \'%s\'" % (l, key, ls + 1, t)


    GNUPLOT_SCRIPT= """
set term pdf enhanced dashed size 4,3
set output '{outfile}'

set style line 10 lt 3 lw 1 pt 18 lc 7 ps 0.0
set style line 11 lt 1 lw 1 pt 18 lc 7 ps 0.5

set style line 20 lt 4 lw 1 pt 7 lc 4 ps 0.0
set style line 21 lt 1 lw 1 pt 7 lc 4 ps 0.5

set style line 30 lt 5 lw 1 pt 9 lc 12 ps 0.0
set style line 31 lt 1 lw 1 pt 9 lc 12 ps 0.5

set style line 40 lt 6 lw 1 pt 10 lc 1 ps 0.0
set style line 41 lt 1 lw 1 pt 10 lc 1 ps 0.5

set style line 50 lt 9 lw 1 pt 11 lc 18 ps 0.0
set style line 51 lt 1 lw 1 pt 11 lc 18 ps 0.5


set xlabel 'Eb/N0 (dB)'
set ylabel '{label_y}'

{range_y}

set key {key_pos} inside 

{plot_line}
"""


    tmp = GNUPLOT_SCRIPT.format(outfile = key + scenario_pos + ".pdf",
            #key = key,
            key_pos = "bottom right" if key == "acc" else "top right",
            label_y = labels['label_y'],
            range_y = labels['range_y'],
            plot_line = lines
        )

    proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
    proc.communicate( tmp )


def plot_final():
    LINES = {
            "_all3_no_err":  ( # CHART GROUP 1
                    ('my_cyclostationary', 10, "ATA-ED/CFD"),
                    #('my_cyclostationary', 20, "Proposal w/ CFD"),
                    ('my_waveform', 20, "ATA-ED/WFD"),
                    ('hierarchical_cyclostationary', 30, "TSHA [5]"),
                    #('hierarchical_unc_11_cyclostationary', 40, "Hierarchical +10% Uncertainty"),
                    #('hierarchical_unc_09', 40, "Hierarchical -10% Uncertainty"),
                    #('sarsa', 50, "Sarsa")
                ),

            "_all3_wh_err":  ( # CHART GROUP 1
                    ('my_unc_11_cyclostationary', 10, "ATA-ED/CFD"),
                    #('my_cyclostationary', 20, "Proposal w/ CFD"),
                    ('my_unc_11_waveform', 20, "ATA-ED/WFD"),
                    ('hierarchical_unc_11_cyclostationary', 30, "TSHA [5]"),
                    #('hierarchical_unc_11_cyclostationary', 40, "Hierarchical +10% Uncertainty"),
                    #('hierarchical_unc_09', 40, "Hierarchical -10% Uncertainty"),
                    #('sarsa', 50, "Sarsa")
                ),

            "_group1":  ( # CHART GROUP 1
                    ('my_cyclostationary', 10, "ATA-ED/CFD"),
                    #('my_cyclostationary', 20, "Proposal w/ CFD"),
                    ('hierarchical_cyclostationary', 30, "TSHA [5]"),
                    #('hierarchical_unc_11_cyclostationary', 40, "Hierarchical +10% Uncertainty"),
                    #('hierarchical_unc_09', 40, "Hierarchical -10% Uncertainty"),
                    #('sarsa', 50, "Sarsa")
                ),

            "_group2":  ( # CHART GROUP 2
                    ('my_waveform', 20, "ATA-ED/WFD"),
                    #('my_cyclostationary', 20, "Proposal w/ CFD"),
                    ('hierarchical_cyclostationary', 30, "TSHA [5]"),
                    #('hierarchical_unc_11_cyclostationary', 40, "Hierarchical +10% Uncertainty"),
                    #('hierarchical_unc_09', 40, "Hierarchical -10% Uncertainty"),
                    #('sarsa', 50, "Sarsa")
                ),

            "_group3":  ( # CHART GROUP 2
                    ('my_waveform', 20, "ATA-ED/WFD"),
                    #('my_cyclostationary', 20, "Proposal w/ CFD"),
                    #('hierarchical_cyclostationary', 30, "Hierarchical"),
                    ('hierarchical_unc_11_cyclostationary', 40, "TSHA [5]"),
                    #('hierarchical_unc_09', 40, "Hierarchical -10% Uncertainty"),
                    #('sarsa', 50, "Sarsa")
                )

            }

    labels =  {
            '_acc':    {'label_y': 'Spectrum Sensing Accuracy','range_y': 'set yrange [0:1.02]'},
            '_mean_time':    {'label_y': 'Mean Response Time [ms]', 'range_y': 'set yrange [0:100]'}
            }


    for group, _LINES in LINES.iteritems():
        for key1 in ('_01', '_05', '_09'):
            for key2 in ('_acc', '_mean_time'):
                lines = "plot "

                outfile = "final" + key1 + key2 + group

                for idx, _t in enumerate(_LINES):
                    l, ls, t = _t
                    l = l + key1 + key2
                    if idx > 0:
                        lines += ','
                    lines += "\'%s.txt\' w linespoints ls %d t \'\'" % (l, ls)
                    lines += ",\'%s.txt\' w errorbar ls %d t \'%s\'" % (l, ls + 1, t)


                GNUPLOT_SCRIPT= """
    set term pdf enhanced dashed size 3.42,2.57
    set output '{outfile}'

    set style line 10 lt 3 lw 1 pt 11 lc 4 ps 0.0
    set style line 11 lt 1 lw 1 pt 11 lc 4 ps 1.0

    set style line 20 lt 4 lw 1 pt 20 lc 7 ps 0.0
    set style line 21 lt 1 lw 1 pt 20 lc 7 ps 1.0

    set style line 30 lt 5 lw 1 pt 9 lc 12 ps 0.0
    set style line 31 lt 1 lw 1 pt 9 lc 12 ps 1.0

    set style line 40 lt 6 lw 1 pt 10 lc 1 ps 0.0
    set style line 41 lt 1 lw 1 pt 10 lc 1 ps 1.0

    set style line 50 lt 9 lw 1 pt 11 lc 18 ps 0.0
    set style line 51 lt 1 lw 1 pt 11 lc 18 ps 1.0


    set xlabel 'Eb/N0 (dB)'
    set ylabel '{label_y}'

    {range_y}
    set xrange [-20:5]

    set key {key_pos} inside 

    {plot_line}
            """


                tmp = GNUPLOT_SCRIPT.format(outfile = outfile + ".pdf",
                        #key = key,
                        key_pos = "bottom right" if key2 == "_acc" else "top right",
                        label_y = labels[key2]['label_y'],
                        range_y = labels[key2]['range_y'],
                        plot_line = lines
                    )

                proc = subprocess.Popen(['gnuplot'], shell = True, stdin = subprocess.PIPE)
                proc.communicate( tmp )


if __name__ == '__main__':

    for scenario in SCENARIOS:
        for k in SCENARIOS_POS:
            FINAL_RES[scenario+k] = {}
            for  res in RES:
                FINAL_RES[scenario+k][res] = {}
                for ebn0 in EBN0:
                    FINAL_RES[scenario+k][res][ebn0] = {}

    #for scenario in SCENARIOS:
    #    for res in ('acc', 'mean_time', 'energy', 'corr' ):
    #        remove_additional_status(scenario, res)

    for scenario in SCENARIOS:
        for k in SCENARIOS_POS:
            for res in ('acc', 'mean_time' ):
                #parse_results_multiline(scenario + k, res)
                #write_parsed_result(scenario + k, res)
                pass

            plot_parsed('acc', {'label_y': 'Spectrum Sensing Accuracy','range_y': 'set yrange [0:1.02]'}, k)
            plot_parsed('mean_time', {'label_y': 'Mean Response Time [ms]', 'range_y': 'set yrange [0:100]' }, k)

    plot_final()
