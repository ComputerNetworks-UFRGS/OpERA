__author__ = 'jtsreinaldo'

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

#!/usr/bin/python

# Evolutionary Genetic Algorithm
#
# Author: Lucas Bondan
#
# To execute: ./genetic.py <number_of_iterations>

import random
import sys

from abstractDecisionAlgorithm import AbstractDecisionAlgorithm

POPSIZE = 4


class Genetic(AbstractDecisionAlgorithm):
    """
    Class for the Genetic decision algorithm.
    """

    ##::TODO:: em vez de usar os parametros no init, agora eles estarao no dict data, parametro do metodo evaluate
    def __init__(self):

        AbstractDecisionAlgorithm.__init__(self)

        self.chromo = []
        self.population = []

    ## Vou tentar adaptar os metodos de get que havia por aqui
    # Coomo os parametros nao estao mais no construtor, eh necessario passar o data
    ## uma alternativa possivel seria passar o data no construtor e gerar as variaveis a partir dali, mas issso teria
    # de ser feito para TODOS os algoritmos, inclusive o abstract
    def get_occupancy_matrix_l(self, data):
        """
        Return the occupancy matrix.
        @param data
        @return The occupancy matrix.
        """
        return data[self.OCCUPANCY_MATRIX]

    def get_reward_matrix_b(self, data):
        """
        Return the reward matrix.
        @param data
        @return The reward matrix.
        """
        return data[self.REWARD_MATRIX]

    def get_interference_matrix_c(self, data):
        """
        Return the interference matrix.
        @param data
        @return The interference matrix.
        """
        return data[self.INTERFERENCE_MATRIX]

    def fitness(self, An, data):
        """
        @param An
        @param data
        @return
        """
        c = self.get_interference_matrix_c(data)
        b = self.get_reward_matrix_b(data)

        fit = 0
        for i in range(len(An)):
            for j in range(len(An[i])):
                fit += An[i][j] * b[i][j] * c[i][j]

        return fit

    def generate_population(self, l):
        """
        Generates population.
        @param l
        """
        count = 0
        m = 0
        for i in range(0, len(l)):
            count += l[i].count(1)

        for i in range(0, POPSIZE):
            for j in range(0, count):
                gene = random.randint(0, 1)
                self.chromo.append(gene)

            An = []
            m = 0
            for k in range(len(l)):
                An.append([])
                for n in range(len(l[k])):
                    if l[k][n] == 1:
                        An[k].append(self.chromo[m])
                        m += 1
                    else:
                        An[k].append(l[k][n])

            self.population.append(An)
            self.chromo = []

    def random_parent(self, population):
        """
        @param population
        @return
        """
        w_rnd_nr = random.random() * random.random() * (POPSIZE - 1)
        w_rnd_nr = int(w_rnd_nr)
        return (population[w_rnd_nr])

    def cross_and_mutate(self, parent1, parent2, l):
        """
        @param parent1 The first parent.
        @param parent2 The second parent.
        @param l
        @return The child.
        """
        #Cross
        cross = random.randint(0, len(l) - 1)
        child = parent1[:]

        child[cross] = parent2[cross]

        #Mutate
        mutchromo = random.randint(0, len(l) - 1)
        mutgene = random.randint(0, len(l[0]) - 1)

        child[mutchromo][mutgene] = random.randint(0, 1)

        return child

    def evaluate(self, data):
        """
        Evaluates the decision algorithm.
        @param data A dictionary with the parameters used by the algorithm.
        """

        #Passo 1
        # Step 1
        l = self.get_occupancy_matrix_l(data)
        self.generate_population(l)

        #Passo 2
        # Step 2
        best_fitness = self.fitness(self.population[0], data)
        best_a = self.population[0]
        for An in self.population:
            if self.fitness(An, data) > best_fitness:
                best_fitness = self.fitness(An, data)
                best_a = An

        for i in range(data[self.ITERATIONS]):

            #Passos 3, 4 e 5
            # Steps 3, 4 and 5
            parent1 = self.random_parent(self.population)
            parent2 = self.random_parent(self.population)

            child = self.cross_and_mutate(parent1, parent2, l)

            if self.fitness(child, data) > best_fitness:
                best_fitness = self.fitness(child, data)
                best_a = child

        print(best_a, best_fitness)

        return best_a

def main():
    """
    Main function.
    """

    # Constants used in the 'data' dictionary:

    OCCUPANCY_MATRIX = 7
    REWARD_MATRIX = 8
    INTERFERENCE_MATRIX = 9
    ITERATIONS = 10


    # channel 1  2  3  4
    occupancy_matrix = [
        #1  2  3  4  (channels)  -->  0 for occupied, 1 for idle
        [0, 1, 1, 1],  # rc 1
        [0, 1, 1, 1],  # rc 2
        [0, 1, 1, 1],  # rc 3
        [0, 1, 1, 1]   # rc 4
    ]

    #channel:         1    2   3     4      reward
    reward_matrix = [[0.7, 0.1, 0.4, 0.1],  # rc1
                     [0.4, 0.9, 0.1, 0.4],  # rc2
                     [0.1, 0.5, 0.0, 1.0],  # rc3
                     [0.1, 0.8, 0.3, 0.3]   # rc4
                     ]

    # channel               1    2    3     4
    interference_matrix = [[0.0, 1.0, 1.0, 1.0],  # channel 1
                           [1.0, 0.0, 1.0, 1.0],  # channel 2
                           [1.0, 1.0, 0.0, 1.0],  # channel 3
                           [1.0, 1.0, 1.0, 0.0]   # channel 4
                           ]

    data = {}
    data[OCCUPANCY_MATRIX] = occupancy_matrix
    data[REWARD_MATRIX] = reward_matrix
    data[INTERFERENCE_MATRIX] = interference_matrix
    data[ITERATIONS] = 1000

    g = Genetic()
    res = g.evaluate(data)

    print res
    links = [0, 2]
    channels = [0, 1, 2]
    tx_rxs = {
        0: (0, 2),
        1: (2, 3),
        2: (1, 3),
        3: (0, 1),
        4: (0, 3),
        5: (1, 2),
    }

    d = {}
    for i in links:
        if channels:
            dev_tx = tx_rxs[i][0]
            dev_rx = tx_rxs[i][1]

            try:
                ch = res[dev_tx].index(1)
            except ValueError:
                try:
                    ch = res[dev_rx].index(1)
                except ValueError:
                    ch = channels[0]

            if ch in channels:
                d[i] = ch
            else:
                ch = channels[0]

            channels.remove(ch)

    print d


if __name__ == "__main__":
    main()