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

__author__ = 'jtsreinaldo'

from abstractDecisionAlgorithm import AbstractDecisionAlgorithm

import subprocess
import imp
import os

DIR = "."
TMPFILE = DIR + "/file.tmp"
MODELFILE = DIR + "/shu.mod"
OUTPUTFILE = DIR + "/temp.py"


class BLP(AbstractDecisionAlgorithm):
    """
    BLP decision algorithm class.
    """

    def __init__(self):
        """
        CTOR
        """

        AbstractDecisionAlgorithm.__init__(self)

    @staticmethod
    def blp_execution(n, l, u, p_max, big_b, pi, big_i, big_u, big_c, gama):
        """
        Execution of the BLP algorithm.
        @param n
        @param l
        @param u
        @param p_max
        @param big_b
        @param pi
        @param big_i
        @param big_u
        @param big_c
        @param gama
        """

        ################################## Creating data for GLPK ###########################
        text = "data;\n"
        #Defining channel number
        text += "param n := %d;\n" % (n)
        #Defining number of links
        text += "param l := %d;\n" % (l)
        #Defining u
        text += "param u := %d;\n" % (u)
        #Defining links max power
        text += "param Pmax :="
        for i in range(l):
            text += str(i + 1) + " " + str(p_max[i]) + " "
        text += ";\n"
        #Defining links bandwidth
        text += "param B :="
        for m in range(n):
            text += str(m + 1) + " " + str(big_b[m]) + " "
        text += ";\n"
        #Defining channel capacity per channel or SNR
        text += "param C :="
        for m in range(n):
            text += " %d %f" % (m + 1, big_c[m])
        text += ";\n"
        #Defining power mask
        text += "param Pi := \n"
        for i in range(n):
            text += "%d %f " % (i + 1, pi[i])
        text += ";\n"

        #Creating Intereference matrix
        text += "param I : \n"
        text_aux = ":="
        for i in range(l):
            text += str(i + 1) + " "
            text_aux += "\n"
            text_aux += str(i + 1) + " "
            for j in range(l):
                text_aux += str(big_i[i][j]) + " "
        text += text_aux
        text += ";\n"
        #Defining U
        text += "param U := \n"
        for i in range(u):
            text += "%d %f " % (i + 1, big_u[i])
        text += ";\n"
        #Calculating gama
        text += "param gama : \n"
        for i in range(u):
            text += str(i + 1) + " "
        text += ":="
        for m in range(n):
            text += "\n"
            text += str(m + 1) + " "
            for k in range(u):
                text += str(gama[m][k]) + " "
        text += ";\nend;"
        f = open(TMPFILE, "w")
        f.write(text)
        f.close()

        # Execute this command in terminal.
        cmd = "glpsol -m " + MODELFILE + " -d " + TMPFILE + " -o /dev/null -y " + OUTPUTFILE + " &>/dev/null"

        subprocess.call([cmd], shell=True)

        import temp

        return temp.ret


    def evaluate(self, data):
        """
        Evaluates the decision algorithm.
        @param data A dictionary with the parameters used by the algorithm.
        """
        n = len(data[self.CHANNELS])
        l = len(data[self.LINKS])
        p_max = [1.0] * len(data[self.LINKS])
        big_b = map(lambda x: self.channel_list[x], data[self.CHANNELS])
        pi = [1.0] * len(data[self.CHANNELS])
        big_i = [[1.0] * len(data[self.LINKS])] * len(data[self.LINKS])
        big_u = [1.0]
        u = len(big_u)
        big_c = map(lambda x: data[self.RSSI][x], data[self.CHANNELS])
        gama = [[1.0] * len(data[self.LINKS])] * len(data[self.CHANNELS])

        print "\n******************************************\n"
        print "PARAMETERS"
        print "\nn = " + str(n)
        print "\nl = " + str(l)
        print "\np_max = " + str(p_max)
        print "\nbig_b = " + str(big_b)
        print "\npi = " + str(pi)
        print "\nbig_i = " + str(big_i)
        print "\nbig_u = " + str(big_u)
        print "\nu = " + str(u)
        print "\nbig_c = " + str(big_c)
        print "\ngama = " + str(gama)
        print "\n******************************************\n"

        solution = self.blp_execution(n, l, u, p_max, big_b, pi, big_i, big_u, big_c, gama)

        print "SOLUTION = " + str(solution)
        print "\n******************************************\n"

        return solution


def main():
    """
    Main function.
    """

    # Constants used in the 'data' dictionary:
    RSSI = 0
    LINKS = 3
    CHANNELS = 4

    channels = [0, 1, 2, 3]
    links = [1, 2]
    rssi = [0.1 / 100000000.0, 1000000000.1 / 100000000.0, 0.1 / 100000000.0, 0.1 / 100000000.0]

    data = {}
    data[CHANNELS] = channels
    data[LINKS] = links
    data[RSSI] = rssi

    blp = BLP()
    blp.channel_list = [200, 400, 500, 400]

    solution = blp.evaluate(data)

    d = {}
    for idx, i in enumerate(solution):
        d[links[idx]] = i[1] - 1

    print d

if __name__ == "__main__":
    main()
