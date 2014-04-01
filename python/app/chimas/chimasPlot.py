#!/usr/bin/python

import subprocess as subprocess
import numpy as np

from multiprocessing import Process
import time

from math import *

PARSED_FILE_NAME = './results/gain_1_noise_weight_{noise_weight}_hist_weight_{hist_weight}'
FILE_NAME_ANIMATED = PARSED_FILE_NAME + "_ch_{ch}"
OUTFILE = './plots/base/multiplot_noise_weight_comparison_{ylabel}'
INFILE_HEAT = './plots/{env}/plot_noise_weight_{noise_weight}_hist_weight_{hist_weight}'
OUTFILE_HEAT = './plots/base/multiplot_heat'
OUTFILE_HIST = './plots/base/multiplot_histogram'
OUTFILE_ENV = './plots/base/environment'

ENVS = ('env_1', 'env_2', 'env_3')

weights = {'left': (0.2, 0.8), 'center': (0.5, 0.5), 'right': (0.8, 0.2)}

##########################################
##########################################
##########################################
##########################################
#::TODO:: breve explicacao sobre cada funcao
def plot_1():
    """
    """

    channels = {'left': [2, 5, 10], 'center': [2, 5, 10], 'right': [2, 5, 10]}

    filenames = {}
    filenames['left'] = {'best': '', 'avg': '', 'worst': ''}
    filenames['center'] = {'best': '', 'avg': '', 'worst': ''}
    filenames['right'] = {'best': '', 'avg': '', 'worst': ''}

    for k in weights:
        for idx, ch in enumerate(('best', 'avg', 'worst')):
            filenames[k][ch] = FILE_NAME_ANIMATED.format(noise_weight=weights[k][0], hist_weight=weights[k][1],
                                                         ch=channels[k][idx]) + ".txt"

    top_extra = "\nset format x ''\nset x2label"
    y_axis = [('historic', 'Historical Occupancy (%)', '(100*$3)', 'set ylabel ''\nset yrange [0:101]' + top_extra),
              ('sinr', 'RSSI (dBm)', '(20*log($4))', 'set yrange [-120:0]'),
              ('qvalue', 'Q-Value', 5, "set yrange [-0.01:1.19]\nset xlabel 'ith ChiMaS Execution' "
               "font 'helvetica,20'\nset key inside top right font 'helvetica,20' spacing 1.5\n")]

    for tup in y_axis:
        y = tup[0]
        ylabel = tup[1]
        col = tup[2]
        extra = tup[3]

        outfile = OUTFILE.format(ylabel=y) + '.pdf'

        subscript = {'a': '', 'b': '', 'c': ''}

        bottom_extra = ''
        if y == 'qvalue':
            subscript['a'] = "set label '(a) {{/Symbol g}}=0.8' at 125, -0.25 font 'helvetica,20'"
            subscript['b'] = "set label '(b) {{/Symbol g}}=0.5' at 125, -0.25 font 'helvetica,20'"
            subscript['c'] = "set label '(c) {{/Symbol g}}=0.2' at 125, -0.25 font 'helvetica,20'"
            # This is only to put the bottom key !!!!

        gnuplot_script = """
set term pdf enhanced dashed size 16,6
set output '{outfile}' 

set lmargin 10
set bmargin 15
set tmargin 5
set rmargin 4

unset grid

unset bars

set multiplot layout 1,3 scale 1,1

unset key

{extra}
set ylabel '{ylabel}' font 'helvetica,20'

{subscript[a]}

plot '{f[left][best]}' using 2:{column} with lines lt 0 lw 5 title 'Channel {channels[left][0]}', '{f[left][avg]}' using 2:{column} with lines lt 1 lw 5 title 'Channel {channels[left][1]}', '{f[left][worst]}' using 2:{column} with lines lt 7 lc 3 lw 5 title 'Channel {channels[left][2]}'

#set lmargin 2
#set format y ''
#unset ylabel
unset label

{subscript[b]}
plot '{f[center][best]}' using 2:{column} with lines lt 0 lw 5 title 'Channel {channels[center][0]}', '{f[center][avg]}' using 2:{column} with lines lt 1 lw 5 title 'Channel {channels[center][1]}', '{f[center][worst]}' using 2:{column} with lines lt 7 lc 3 lw 5 title 'Channel {channels[center][2]}'


unset label
{subscript[c]}
plot '{f[right][best]}' using 2:{column} with lines lt 0 lw 5 title 'Channel {channels[right][0]}', '{f[right][avg]}' using 2:{column} with lines lt 1 lw 5 title 'Channel {channels[right][1]}', '{f[right][worst]}' using 2:{column} with lines lt 7 lw 5 lc 3 title 'Channel {channels[right][2]}'

{bottom_extra}
""".format(outfile=outfile, ylabel=ylabel, column=col, f=filenames, extra=extra, bottom_extra=bottom_extra,
           subscript=subscript, channels=channels)

        proc = subprocess.Popen(['gnuplot'], shell=True, stdin=subprocess.PIPE)
        proc.communicate(gnuplot_script)


##########################################
##########################################
##########################################
##########################################
def plot_2():
    """

    """
    w = (0.5, 0.5)

    filenames = {}

    for e in ENVS:
        if e == 'env_2':
            pass
        filenames[e] = INFILE_HEAT.format(env=e, noise_weight=w[0], hist_weight=w[1]) + ".txt"

    outfile = OUTFILE_HEAT + '.pdf'

    gnuplot_script = """
set term pdf enhanced color size 16,6

set output '{outfile}'

set lmargin 10
set bmargin 15
set tmargin 5
set rmargin 5

set palette rgb 1,0.2,0.1
set palette rgb 21,22,23
set palette rgb 33,13,10
#set palette defined (0 "white", 1 "dark-gray")
set multiplot layout 1,2 scale 1,1

unset grid
unset key
unset bars
unset colorbox

set ylabel 'RSSI [dBm]' font 'helvetica,20'
set xlabel 'Historical Occupancy [%]' font 'helvetica,20'
set xrange [-1:101]
set yrange [-40:50]
set label '(a) 400 MHz Scenario' at 35, -58 font 'helvetica,20'
plot '{f[env_1]}' using (100*$2):3:4 with points lt 1 pt 7 ps 2.7 palette notitle, '{f[env_1]}' using (100*$2):3:1 with labels notitle font 'helvetica,18'

set cblabel 'Q-Value Gradient' font 'helvetica,20'

#unset ylabel
#unset label
#unset ytic
unset label

set rmargin 5
set key
set cbrange [0:1]
set colorbox horizontal user size 0.2, 0.07 origin 0.405, 0.08
set label '(b) 2.4 GHz Scenario' at 35, -58 font 'helvetica,20'

plot '{f[env_3]}' using (100*$2):3:4 with points lt 1 pt 7 ps 2.7 palette notitle,  '{f[env_3]}' using (100*$2):3:1 with labels notitle font 'helvetica,18'

{bottom_extra}
""".format(outfile=outfile, f=filenames, bottom_extra='')

    proc = subprocess.Popen(['gnuplot'], shell=True, stdin=subprocess.PIPE)
    proc.communicate(gnuplot_script)

##########################################
##########################################
##########################################
##########################################
def plot_3():
    """
    """
    best = 2
    worst = 10
    avg = 5
    channels = [best, worst, avg]

    filenames = {}
    filenames['left'] = []
    filenames['center'] = []
    filenames['right'] = []


    for ch in channels:
        for k in weights:
            f = FILE_NAME_ANIMATED.format(noise_weight=weights[k][0], hist_weight=weights[k][1], ch=ch) + ".txt"
            filenames[k].append(f)

    outfile = OUTFILE_ENV + '.pdf'

    l = {'ylabel': 'Historical Occupancy [%]', 'column': '(100*$3)', 'extra': '\nset yrange [0:119]'}
    r = {'ylabel': 'RSSI [dBm]', 'column': '(20*log($4))', 'extra': '\nset yrange [-110:10]'}
    r = {'ylabel': 'RSSI [dBm]', 'column': '((20*log($4) <=-104? -104 : 20*log($4)))', 'extra': '\nset yrange [-110:10]'}

    gnuplot_script = """
set term pdf enhanced dashed size 16,6
set output '{outfile}' 

unset grid
unset bars
unset key

set bmargin 15
set rmargin 10

set multiplot layout 1,2 scale 1,1


set ylabel '{l[ylabel]}' font 'helvetica,20'
set xlabel '{{/Helvetica-Italic i}}th {{/Helvetica-Italic ChiMaS}} Execution' font 'Helvetica,20'

{l[extra]}

set key inside top right font 'helvetica,20' spacing 2.5
set label '(a) Historical Occupancy' at 110.0, -22 font 'helvetica,20'

plot '{f[left][0]}' using 2:{l[column]} with lines lt 0 lw 5 title 'Channel {ch_best} ', '{f[left][2]}' using 2:{l[column]} with lines lt 1 lw 5 title 'Channel {ch_avg} ', '{f[left][1]}' using 2:{l[column]} with lines lt 7 lc 3 lw 5 title 'Channel {ch_worst}'

set ylabel '{r[ylabel]}' font 'helvetica,20'
{r[extra]}
set key inside top right font 'helvetica,20' spacing 2.5

unset label
set label '(b) Channel Condition' at 110.0, -132.5 font 'helvetica,20'
plot '{f[left][0]}' using 2:{r[column]} with lines lt 0 lw 5 title 'Channel {ch_best} ', '{f[left][2]}' using 2:{r[column]} with lines lt 1 lw 5 title 'Channel {ch_avg}', '{f[left][1]}' using 2:{r[column]} with lines lt 7 lc 3 lw 5 title 'Channel {ch_worst}'
""".format(outfile=outfile, f=filenames, ch_best=best, ch_worst=worst, ch_avg=avg, l=l, r=r)

    proc = subprocess.Popen(['gnuplot'], shell=True, stdin=subprocess.PIPE)
    proc.communicate(gnuplot_script)

##########################################
##########################################
##########################################
##########################################
#::TODO::
def plot_4():
    """
    """
    outfile = OUTFILE_HIST + ".pdf"

    labels = {'left': '', 'center': '', 'right': ''}
    filenames = {}

    for k in weights:
        infile = PARSED_FILE_NAME.format(noise_weight=weights[k][0], hist_weight=weights[k][1]) + ".txt"

        content = []
        with open(infile, 'r') as fd:
            next(fd)
            for line in fd:
                (ch, occupancy, sinr, qvalue, sinr_idle) = map(float, line.split(' '))
                ch = int(ch)
                content.append((int(ch), qvalue))

        content.sort(reverse=True, key=lambda tup: tup[1])

        tmp_file = OUTFILE_HIST + '_' + k + '.txt'
        with open(tmp_file, 'w') as fd:
            fd.write("idx ch qvalue\n")
            for idx, tup in enumerate(content):
                fd.write("%d %d %f\n" % (idx+1, tup[0], tup[1]))
        filenames[k] = tmp_file

        for idx, (ch, qvalue) in enumerate(content):
            if ch < 10:
                labels[k] += "set label 'Ch %s' at %f,%f font 'helvetica,18'\n" % (ch, 1+idx-0.40, qvalue+0.03)
            else:
                labels[k] += "set label 'Ch %s' at %f,%f font 'helvetica,18'\n" % (ch, 1+idx-0.55, qvalue+0.03)

    gnuplot_script = """
set term pdf enhanced size 16,6
set output '{outfile}'

set multiplot layout 1,3

set lmargin 10
set bmargin 15
set tmargin 5
set rmargin 4

set xlabel 'Ordained Channel List Index' font 'helvetica,20'
set ylabel 'Q-Value' font 'helvetica,20'

set boxwidth 0.7 relative
set style fill solid 1 border 7

set grid ytics
set yrange [0:1]

{labels[left]}

set label '(a) {{/Symbol g}}=0.8' at 5, -0.2 font 'helvetica,20'

plot  '{filenames[left]}' using 1:3:xtic(1) with boxes ls 3 notitle

#set lmargin 2
#set  format y ''
#
#unset ylabel
unset label

set label '(b) {{/Symbol g}}=0.5' at 5, -0.2 font 'helvetica,20'
{labels[center]}
plot  '{filenames[center]}' using 1:3:xtic(1) with boxes notitle ls 3

unset label
set label '(c) {{/Symbol g}}=0.2' at 5, -0.2 font 'helvetica,20'
{labels[right]}
plot  '{filenames[right]}' using 1:3:xtic(1) with boxes notitle ls 3
""".format(filenames=filenames, outfile=outfile, labels=labels)

    proc = subprocess.Popen(['gnuplot'], shell=True, stdin=subprocess.PIPE)
    proc.communicate(gnuplot_script)


if __name__ == '__main__':
    plot_1()  # qvalue, historic rssi
    plot_2()  # heat
    plot_3()  # environment
    plot_4()  # histogram
