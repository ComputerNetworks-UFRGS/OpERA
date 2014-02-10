#!/usr/bin/python

# Evolutionary Genetic Algorithm
#
# Author: Lucas Bondan
#
# To execute: ./genetic.py <number_of_iterations>

import random
import sys

POPSIZE = 4

class Genetic:
    def __init__(self, occupancy_matrix, reward_matrix, interference_matrix):
        self.occupancy_matrix = occupancy_matrix
        self.reward_matrix = reward_matrix
        self.interference_matrix = interference_matrix

        self.chromo = []
        self.population = []

    def getOccupancyMatrixL(self):
        return self.occupancy_matrix

    def getRewardMatrixB(self):
        return self.reward_matrix

    def getInterferenceMatrixC(self):
        return self.interference_matrix

    def fitness(self, An):

        C = self.getInterferenceMatrixC()
        B = self.getRewardMatrixB()

        fit = 0
        for i in range(len(An)):
            for j in range(len(An[i])):
                fit += An[i][j] * B[i][j] * C[i][j]

        return fit

    def generatePopulation(self, L):
        count = 0
        m = 0
        for i in range(0, len(L)):
            count += L[i].count(1)

        for i in range(0, POPSIZE):
            for j in range(0, count):
                gene = random.randint(0, 1)
                self.chromo.append(gene)

            An = []
            m = 0
            for k in range(len(L)):
                An.append([])
                for n in range(len(L[k])):
                    if L[k][n] == 1:
                        An[k].append(self.chromo[m])
                        m +=1
                    else:
                        An[k].append(L[k][n])

            self.population.append(An)
            self.chromo = []

    def random_parent(self, population):
       wRndNr = random.random() * random.random() * (POPSIZE - 1)
       wRndNr = int(wRndNr)
       return(population[wRndNr])

    def crossAndMutate(self, parent1, parent2, L):
        #Cross
        cross = random.randint(0,len(L)-1)
        child = parent1[:]

        child[cross] = parent2[cross]

        #Mutate
        mutchromo = random.randint(0,len(L)-1)
        mutgene   = random.randint(0,len(L[0])-1)

        child[mutchromo][mutgene] = random.randint(0, 1)

        return child

    def full_process(self, iterations):
        #Passo 1
        L = self.getOccupancyMatrixL()
        self.generatePopulation(L)

        #Passo 2
        bestFitness = self.fitness(self.population[0])
        bestA = self.population[0]
        for An in self.population:
            if self.fitness(An) > bestFitness:
                bestFitness = self.fitness(An)
                bestA = An

        for i in range(iterations):

            #Passos 3, 4 e 5
            parent1 = self.random_parent(self.population)
            parent2 = self.random_parent(self.population)

            child = self.crossAndMutate(parent1, parent2, L)

            if self.fitness(child) > bestFitness:
                bestFitness = self.fitness(child)
                bestA = child

        print(bestA, bestFitness)

        return bestA

if __name__ == "__main__":
                #canal:     1  2  3  4
    occupancy_matrix    = [
    #canal   1  2  3  4             0 para ocupado, 1 para livre
            [0, 1, 1, 1], # rc 1
            [0, 1, 1, 1], # rc 2
            [0, 1, 1, 1], # rc 3
            [0, 1, 1, 1]  # rc 4
    ]
    #canal:                   1    2   3     4          recompensa
    reward_matrix       = [ [0.7, 0.1, 0.4, 0.1], # rc1
                            [0.4, 0.9, 0.1, 0.4], # rc2
                            [0.1, 0.5, 0.0, 1.0], # rc3
                            [0.1, 0.8, 0.3, 0.3]  # rc4
    ]
# canal                      1    2    3     4
    interference_matrix = [ [0.0, 1.0, 1.0, 1.0], # canal 1
                            [1.0, 0.0, 1.0, 1.0], # canal 2
                            [1.0, 1.0, 0.0, 1.0], # canal 3
                            [1.0, 1.0, 1.0, 0.0]  # canal 4
    ]



    g = Genetic(occupancy_matrix, reward_matrix, interference_matrix)
    res = g.full_process(1000)

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
            dev_tx  = tx_rxs[i][0]
            dev_rx  = tx_rxs[i][1]

            _start = 1
            try:
                ch = res[ dev_tx ].index(1)
            except ValueError:
                try:
                    ch = res[ dev_rx ].index(1)
                except ValueError:
                    ch = channels[0]

            if ch in channels:
                d[i] = ch
            else:
                ch = channels[0]

            channels.remove(ch)

    print d
