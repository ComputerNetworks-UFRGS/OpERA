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

import random
import math
from abstractDecisionAlgorithm import AbstractDecisionAlgorithm


# ::TODO:: definicao de parametros e metodos.
class Channel(AbstractDecisionAlgorithm):
    """
    Simulated Annealing decision algorithm.
    """

    def __init__(self):
        """
        CTOR
        """

        AbstractDecisionAlgorithm.__init__(self)

        self.w1 = None
        self.w2 = None
        self.w3 = None
        self.w4 = None
        self.w5 = None
        self.w6 = None
        self.temperature = None
        self.min_bandwidth = None
        self.max_bandwidth = None
        self.min_power = None
        self.max_power = None
        self.maximum_scheme = None
        self.maximum_modulation_index = None
        self.min_symbol_rate = None
        self.max_symbol_rate = None
        self.min_tdd = None
        self.max_tdd = None
        self.min_pbe = None
        self.max_pbe = None
        self.solution = -1
        # Chance of changing a value in simulated
        self.chance = 0.05
        self.pu_rate = None


    def normalize(self, value, mini, maxi, nmin=0, nmax=1):
        """
        @param value
        @param mini
        @param maxi
        @param nmin
        @param nmax
        @return
        """
        delta = maxi - mini
        a = (value - mini) / delta
        #Then scale to [x,y] via:
        range2 = nmax - nmin
        a = (a * range2) + nmin
        return a

    def minimize_power(self, power):
        """
        @param power
        @return
        """
        if self.max_power is not None:
            return power / self.max_power
        else:
            return None

    def min_ber(self, pbe):
        """
        @param pbe
        @return
        """
        return math.log10(0.5) / math.log10(pbe)

    def max_throughput(self, modulation_index):
        """
        @param modulation_index
        @return
        """

        if self.maximum_scheme is not None and self.maximum_modulation_index is not None:
            return ((math.log(self.maximum_scheme[modulation_index], 2) / math.log(
                self.maximum_scheme[self.maximum_modulation_index], 2)))

        else:
            return None

    def min_interference(self, bandwidth, tdd, power):
        """
        @param bandwidth
        @param tdd
        @param power
        @return
        """

        if self.min_power is not None and self.min_bandwidth is not None and self.max_power is not None and \
           self.max_bandwidth is not None and self.max_symbol_rate is not None:
            return ((power + bandwidth + tdd) - (self.min_power + self.min_bandwidth + 1)) / (
                self.max_power + self.max_bandwidth + self.max_symbol_rate)

        else:
            return None

    def max_spectral_eff(self, modulation_index, symbol_rate, bandwidth):
        """
        @param modulation_index
        @param symbol_rate
        @param bandwidth
        @return
        """

        if self.maximum_scheme is not None and self.min_bandwidth is not None and self.maximum_scheme is not None and \
           self.maximum_modulation_index is not None and self.max_symbol_rate is not None:
            return (1 - ((self.maximum_scheme[modulation_index] * self.min_bandwidth * symbol_rate) / (
                bandwidth * self.maximum_scheme[self.maximum_modulation_index] * self.max_symbol_rate)))

        else:
            return None

    def five_objective(self, bandwidth, power, modulation_index, symbol_rate, tdd, pbe):
        """
        @param bandwidth
        @param power
        @param modulation_index
        @param symbol_rate
        @param tdd
        @param pbe
        @return
        """
        fmin_power = self.minimize_power(power)
        fmin_ber = self.min_ber(pbe)
        fmax_throughput = self.max_throughput(modulation_index)
        f_min_interference = self.min_interference(bandwidth, tdd, power)
        f_max_spec_eff = self.max_spectral_eff(modulation_index, symbol_rate, bandwidth)

        print "\nParametros:::\n"
        print "\nw1 = " + str(self.w1)
        print "\nw2 = " + str(self.w2)
        print "\nw3 = " + str(self.w3)
        print "\nw4 = " + str(self.w4)
        print "\nw5 = " + str(self.w5)
        print "\nw6 = " + str(self.w6)
        print "\npu_rate = " + str(self.pu_rate)
        print "\n"


        if self.w1 is not None and self.w2 is not None and self.w3 is not None and self.w4 is not None and \
           self.w5 is not None and self.w6 is not None and self.pu_rate is not None:
            return (
                (self.w1 * fmin_power) + (self.w2 * fmin_ber) + (self.w3 * fmax_throughput) +
                (self.w4 * f_min_interference) + (self.w5 * f_max_spec_eff) + (self.w6 * self.pu_rate))

        else:
            return None

    def three_objective(self, power, modulation_index, pbe):
        """
        @param power
        @param modulation_index
        @param pbe
        @return
        """
        fmin_power = self.minimize_power(power)
        fmin_ber = self.min_ber(pbe)
        fmax_throughput = self.max_throughput(modulation_index)

        if self.w1 is not None and self.w2 is not None and self.w3 is not None:
            return (self.w1 * fmin_power) + (self.w2 * fmin_ber) + (self.w3 * fmax_throughput)

        else:
            return None

    def acceptance_probability(self, energy, new_energy, temperature):
        """
        @param energy
        @param new_energy
        @param temperature
        @return
        """
        return math.exp((energy - new_energy) / temperature)

    def calculate_ber(self, maximum_scheme):
        #::TODO:: implementacao (???)
        """
        @param maximum_scheme
        """
        return "nada"

    def head_text(self, number_objectives):
        """
        @param number_objectives
        @return
        """
        if (number_objectives == 3):
            return "Score, Power, Modulation"
        else:
            return "Score, Power, Modulation, Bandwidth, TDD, symbol_rate"

    def evaluate(self, data):
        """
        @return The solution.
        """

        self.w1 = data[self.SIM_ANNEALING_PARAMETERS]['w1']
        self.w2 = data[self.SIM_ANNEALING_PARAMETERS]['w2']
        self.w3 = data[self.SIM_ANNEALING_PARAMETERS]['w3']
        self.w4 = data[self.SIM_ANNEALING_PARAMETERS]['w4']
        self.w5 = data[self.SIM_ANNEALING_PARAMETERS]['w5']
        self.w6 = data[self.SIM_ANNEALING_PARAMETERS]['w6']
        self.temperature = data[self.SIM_ANNEALING_PARAMETERS]['temperature']
        self.min_bandwidth = data[self.SIM_ANNEALING_PARAMETERS]['min_bandwidth']
        self.max_bandwidth = data[self.SIM_ANNEALING_PARAMETERS]['max_bandwidth']
        self.min_power = data[self.SIM_ANNEALING_PARAMETERS]['min_power']
        self.max_power = data[self.SIM_ANNEALING_PARAMETERS]['max_power']
        self.maximum_scheme = data[self.SIM_ANNEALING_PARAMETERS]['maximum_scheme']
        self.maximum_modulation_index = data[self.SIM_ANNEALING_PARAMETERS]['maximum_modulation_index']
        self.min_symbol_rate = data[self.SIM_ANNEALING_PARAMETERS]['min_symbol_rate']
        self.max_symbol_rate = data[self.SIM_ANNEALING_PARAMETERS]['max_symbol_rate']
        self.min_tdd = data[self.SIM_ANNEALING_PARAMETERS]['min_tdd']
        self.max_tdd = data[self.SIM_ANNEALING_PARAMETERS]['max_tdd']
        self.min_pbe = data[self.SIM_ANNEALING_PARAMETERS]['min_pbe']
        self.max_pbe = data[self.SIM_ANNEALING_PARAMETERS]['max_pbe']
        self.solution = -1
        # Chance of changing a value in simulated
        self.chance = 0.05
        self.pu_rate = data[self.SIM_ANNEALING_PARAMETERS]['pu_rate']


        Tk = self.temperature

        # -----Initial solution -> Random solution
        power = random.uniform(self.min_power, self.max_power)
        sol_power = power

        modulation_index = random.randint(0, self.maximum_modulation_index)
        maximum_scheme = self.maximum_scheme[modulation_index]
        sol_modulation = maximum_scheme

        bandwidth = random.uniform(self.min_bandwidth, self.max_bandwidth)
        sol_bandwidth = bandwidth

        tdd = random.uniform(self.min_tdd, self.max_tdd)
        sol_tdd = tdd

        symbol_rate = random.uniform(self.min_symbol_rate, self.max_symbol_rate)
        sol_symbol_rate = symbol_rate

        pbe = random.uniform(self.min_pbe, self.max_pbe)
        sol_pbe = pbe
        solution = self.five_objective(bandwidth, power, modulation_index, symbol_rate, tdd, pbe)
        #-----

        # Control of number of iterations
        k = 0
        sign = True
        while (Tk > 0.1):

            # T value for each iteration Paper Szu
            Tk = self.temperature / (k + 1.0)

            # Choosing if the next parameter will be modified
            choose_parameter = random.random()
            # Transmit power
            if (choose_parameter <= self.chance):
                ntk = self.normalize(Tk, 0, self.temperature, self.min_power, self.max_power)
                if (sign):
                    power = sol_power + ntk
                else:
                    power = sol_power - ntk
                # Power must not exceed min_power and max_power
                if (power > self.max_power):
                    power = self.max_power
                elif (power < self.min_power):
                    power = self.min_power
            # Choosing if the next parameter will be modified
            choose_parameter = random.random()
            # Transmit power
            if (choose_parameter <= self.chance):
                ntk = self.normalize(Tk, 0, self.temperature, self.min_pbe, self.max_pbe)
                if (sign):
                    pbe = sol_pbe + ntk
                else:
                    pbe = sol_pbe - ntk
                # Power must not exceed min_power and max_power
                if (pbe > self.max_pbe):
                    pbe = self.max_pbe
                elif (pbe < self.min_pbe):
                    pbe = self.min_pbe
            # Choosing if the next parameter will be modified
            choose_parameter = random.random()
            # Modulation Scheme
            if (choose_parameter <= self.chance):
                # Circular list of modulations
                if (not (sign)):
                    if (modulation_index == 0):
                        modulation_index = self.maximum_modulation_index
                    else:
                        modulation_index -= 1

                else:
                    if (modulation_index == self.maximum_modulation_index):
                        modulation_index = 0
                    else:
                        modulation_index += 1

                maximum_scheme = self.maximum_scheme[modulation_index]

            # Choosing if the next parameter will be modified
            choose_parameter = random.random()
            # Bandwidth
            if (choose_parameter <= self.chance):
                ntk = self.normalize(Tk, 0, self.temperature, self.min_bandwidth, self.max_bandwidth)
                if (sign):
                    bandwidth = sol_bandwidth + ntk
                else:
                    bandwidth = sol_bandwidth - ntk
                # Bandwidth must not exceed min_bandwidth and max_bandwidth
                if (bandwidth > self.max_bandwidth):
                    bandwidth = self.max_bandwidth
                elif (bandwidth < self.min_bandwidth):
                    bandwidth = self.min_bandwidth
            choose_parameter = random.random()
            # TDD
            if (choose_parameter <= self.chance):
                ntk = self.normalize(Tk, 0, self.temperature, self.min_tdd, self.max_tdd)
                if (sign):
                    tdd = sol_tdd + ntk
                else:
                    tdd = sol_tdd - ntk
                # TDD must not exceed min_tdd and max_tdd
                if (tdd > self.max_tdd):
                    tdd = self.max_tdd
                elif (tdd < self.min_tdd):
                    tdd = self.min_tdd

            choose_parameter = random.random()
            # Symbol Rate
            if (choose_parameter <= self.chance):  #(choose_parameter <= 1.00):
                ntk = self.normalize(Tk, 0, self.temperature, self.min_symbol_rate, self.max_symbol_rate)
                if (sign):
                    symbol_rate = sol_symbol_rate + ntk
                else:
                    symbol_rate = sol_symbol_rate - ntk
                # symbol_rate must not exceed min_symbol_rate and max_symbol_rate
                if (symbol_rate > self.max_symbol_rate):
                    symbol_rate = self.max_symbol_rate
                elif (symbol_rate < self.min_symbol_rate):
                    symbol_rate = self.min_symbol_rate


            # New solution
            new_solution = self.five_objective(bandwidth, power, modulation_index, symbol_rate, tdd, pbe)


            # New solution is better than the old solution
            if (new_solution < solution ):
                solution = new_solution
                sol_power = power
                sol_modulation = modulation_index
                sol_bandwidth = bandwidth
                sol_tdd = tdd
                sol_symbol_rate = symbol_rate
                sol_pbe = pbe
                if (new_solution > self.solution):
                    self.solution = new_solution
                    self.power = power
                    self.modulation = modulation_index
                    self.bandwidth = bandwidth
                    self.TDD = tdd
                    self.symbol_rate = symbol_rate
                    self.pbe = sol_pbe
                    self.throughput = self.max_throughput(modulation_index)

            else:
                # Probability of solution exchange, even if new solution is worse
                p = self.acceptance_probability(solution, new_solution, self.temperature)
                gen_prob = random.random()

                if (gen_prob < p):
                    solution = new_solution

            # Controlling iteration and temperature
            k += 1
            #Changing between inc/decrementing vars
            sign = not (sign)
        return self.solution


def main():
    SIM_ANNEALING_PARAMETERS = 14

    l = [1, 2]
    ch = [1, 2, 3]
    pu_rate = [1.0, 0.5, 0.1]
    links = [[(1, pu_rate[0]), (2, pu_rate[1]), (3, pu_rate[2])], [(1, pu_rate[0]), (2, pu_rate[1]), (3, pu_rate[2])]]

    data = {}
    data[SIM_ANNEALING_PARAMETERS] = {}

    # Weights for maximizing throughput
    data[SIM_ANNEALING_PARAMETERS]['w1'] = 0.05
    data[SIM_ANNEALING_PARAMETERS]['w2'] = 0.05
    data[SIM_ANNEALING_PARAMETERS]['w3'] = 0.05
    data[SIM_ANNEALING_PARAMETERS]['w4'] = 0.05
    data[SIM_ANNEALING_PARAMETERS]['w5'] = 0.05
    data[SIM_ANNEALING_PARAMETERS]['w6'] = 0.75

    # Transmitted power between 0.158 and 251 mW
    data[SIM_ANNEALING_PARAMETERS]['min_power'] = 1
    data[SIM_ANNEALING_PARAMETERS]['max_power'] = 1

    # Modulation Scheme QAM between 2 and 256
    # data[SIM_ANNEALING_PARAMETERS]['modulation_scheme'] = [4]
    data[SIM_ANNEALING_PARAMETERS]['maximum_scheme'] = [4]
    data[SIM_ANNEALING_PARAMETERS]['maximum_modulation_index'] = 0

    # Bandwidth between 2 and 32 MHz
    data[SIM_ANNEALING_PARAMETERS]['min_bandwidth'] = 200
    data[SIM_ANNEALING_PARAMETERS]['max_bandwidth'] = 400

    # TDD between
    data[SIM_ANNEALING_PARAMETERS]['min_tdd'] = 485
    data[SIM_ANNEALING_PARAMETERS]['max_tdd'] = 490

    # Symbol Rate between 125kbps and 1Mbps
    data[SIM_ANNEALING_PARAMETERS]['min_symbol_rate'] = 125
    data[SIM_ANNEALING_PARAMETERS]['max_symbol_rate'] = 1024

    # BER
    data[SIM_ANNEALING_PARAMETERS]['max_pbe'] = math.pow(10, -6)
    data[SIM_ANNEALING_PARAMETERS]['min_pbe'] = math.pow(10, -8)

    # Initial temperature
    data[SIM_ANNEALING_PARAMETERS]['temperature'] = 1000

    # Primary user rate.
    data[SIM_ANNEALING_PARAMETERS]['pu_rate'] = pu_rate


    # to_sa is a list of list.
    # inner list is  for each link
    # [ [(ch1, pu_rate) (ch2, pu_rate) (ch3, pu_rate)] ]

    ## links = [[(1, pu_rate[0]), (2, pu_rate[1]), (3, pu_rate[2])], [(1, pu_rate[0]), (2, pu_rate[1]), (3, pu_rate[2])]]
    links = [77, 79]
    channels = [1, 2, 3]

    to_sa = [[(1, 77), (2, 77), (3, 77)], [(1, 79), (2, 79), (3, 79)]]

    results = []
    for i in range(0, len(to_sa)):
        for c in to_sa[i]:

            channel = Channel()

            data[channel.SIM_ANNEALING_PARAMETERS]['pu_rate'] = c[1]

            simu = channel.evaluate(data)

            flag = False
            j = 0
            while flag is False and j < len(results):
                if results[j][2] > simu:
                    results.insert(j, [i, c[0], simu])
                    flag = True
                j = j + 1
            if flag is False:
                results.append([i, c[0], simu])

    d = {}

    for l, ch, rw in results:
        if l in d or ch in d.itervalues():
            pass
        else:
            d[l] = ch

    print "\nLinks = " + str(to_sa)

    print "\nResults = " + str(results)
    print "\nDict = " + str(d)


if __name__ == '__main__':
    main()