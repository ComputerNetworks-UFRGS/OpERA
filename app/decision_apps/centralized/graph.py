#!/usr/bin/env python

import sys
import argparse
import time
import math
import random


class Graph():

	def __init__(self, interferenceMatrix, utilityMatrix):
		self._intMatrix = interferenceMatrix
		self.graph = utilityMatrix
		self.matching = []


	def calcPossibleShares(self):
		
		possibleShares = []

		for i in range(len(self._intMatrix)):
			for j in range(len(self._intMatrix[i])):
				if (j != i) and (self._intMatrix[i][j] == 0):
					possibleShares.append([i, j])

		pilha = []

		for i in range(len(self._intMatrix)):
			pilha.append(i)

			for j in possibleShares:
				if (i == j[0]):
					pilha.append(j[1])


			elemToRemove = []
			for k in pilha:
				m = k + 1
				while m <= len(pilha):
					if (m in pilha) and (self._intMatrix[k][m] == 1):
						elemToRemove.append(m)
					m += 1

			for l in elemToRemove:
				if (l in pilha):
					pilha.remove(l)
			if (len(pilha) > 2):
				possibleShares.append(pilha)

			pilha = []


		a = []
		for i in possibleShares:
			i.sort()
			if not(i in a):
				a.append(i)

		possibleShares = sorted(a)

		for i in range(6):
			possibleShares.append([i])				

		return possibleShares
	
	def removeAllocated(self, possibleShares, index):

		valuesToRemove = possibleShares
		possibleShares.remove(valuesToRemove)

	def increaseUtility(self, possibleFreqs, possibleLinks):

		#possibleShares = self.calcPossibleShares()
		possibleShares = possibleLinks

		result = []

		#possibleFreqs = [0,1,2, 4]

		dict_links_to_freq = {}
		while (possibleFreqs and possibleShares):

			combinedUtilities = []
			utilityVector = []

			for link in possibleShares:
			
				util = -1
				f = -1
			
				for freq in possibleFreqs:
					soma = self.graph[link][freq]

					if ( soma > util ):
						util = soma
						f = freq
				
				utilityVector.append([util, f])


			maxUtility = max(utilityVector)

			index = utilityVector.index(maxUtility)

			links = possibleShares[index]

			dict_links_to_freq[links] = maxUtility[1]

			possibleShares.pop(index)
			possibleFreqs.remove(maxUtility[1])

		return dict_links_to_freq


if __name__ == '__main__':

	utilityMatrix = [ [4,3,1, 10], [10,5,2, 6], [3,6,1, 4], [1,6,3, 1], [4,5,1, 3], [3,0,6, 11] ]
	interferenceMatrix = [ [1,1,1,1,1,1] * 6 ]

	G = Graph(interferenceMatrix, utilityMatrix)
	l = G.increaseUtility([0, 1, 2, 3], [2])
