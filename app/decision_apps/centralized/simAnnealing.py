#!/usr/bin/env python
import timeit
import re 
import random
import math
class Channel(object):
	def __init__(self, w1, w2, w3, w4, w5, w6, temperature, minBandwidth,
 		maxBandwidth, minPower, maxPower, modulationScheme,
		maximumModulationIndex, minSymbolRate, maxSymbolRate, minTDD, maxTDD, minPbe, maxPbe, puRate):
		self.w1 = w1
		self.w2 = w2
		self.w3 = w3
		self.w4 = w4
		self.w5 = w5
		self.w6 = w6
		self.temperature = temperature
		self.minBandwidth = minBandwidth
		self.maxBandwidth = maxBandwidth
		self.minPower = minPower
		self.maxPower = maxPower
		self.modulationScheme = modulationScheme
		self.maximumModulationIndex = maximumModulationIndex
		self.minSymbolRate = minSymbolRate
		self.maxSymbolRate = maxSymbolRate
		self.minTDD = minTDD
		self.maxTDD = maxTDD
		self.minPbe = minPbe
		self.maxPbe = maxPbe
		self.solution = -1
		#Chance of changing a value in simulated
		self.chance = 0.05
		self.puRate = puRate



	def normalize(self, value, mini, maxi, nmin=0, nmax=1):
		delta = maxi - mini;
	 	a = (value - mini) / delta;
		#Then scale to [x,y] via:
	 	range2 = nmax - nmin;
	 	a = (a*range2) + nmin;
	 	return a

	def minimizePower(self, power):
		return power/self.maxPower

	def minBER(self, Pbe):
		return math.log10(0.5) / math.log10(Pbe)

	def maxThroughput(self, modulationIndex):
		return ( (math.log(self.modulationScheme[modulationIndex], 2) / math.log(self.modulationScheme[self.maximumModulationIndex], 2)))

	def minInterference(self, bandwidth, tdd, power):
		return ((power + bandwidth + tdd) - (self.minPower + self.minBandwidth + 1)) / (self.maxPower + self.maxBandwidth + self.maxSymbolRate)

	def maxSpectralEff(self, modulationIndex, symbolRate, bandwidth):
		return (1 - ((self.modulationScheme[modulationIndex] * self.minBandwidth * symbolRate) / (bandwidth * self.modulationScheme[self.maximumModulationIndex] * self.maxSymbolRate)))

	def fiveObjective(self, bandwidth, power, modulationIndex, symbolRate, tdd, Pbe):
		fMinPower = self.minimizePower(power)
		fMinBER = self.minBER(Pbe)
		fMaxThroughput = self.maxThroughput(modulationIndex)
		fMinInterference = self.minInterference(bandwidth, tdd, power)
		fMaxSpecEff = self.maxSpectralEff(modulationIndex, symbolRate, bandwidth)

		return ( (self.w1 * fMinPower) + (self.w2 * fMinBER) + (self.w3 * fMaxThroughput) + (self.w4 * fMinInterference) + (self.w5 * fMaxSpecEff) + (self.w6 * self.puRate) )

	def threeObjective(w1, w2, w3, power, maxPower, modulationIndex, maximumModulationIndex, Pbe):
		fMinPower = minPower(power)
		fMinBER = minBER(Pbe)
		fMaxThroughput = maxThroughput(modulationIndex)

		return ( (self.w1 * fMinPower) + (self.w2 * fMinBER) + (self.w3 * fMaxThroughput) )

	def acceptanceProbability(self, energy, newEnergy, temperature):
		return math.exp((energy - newEnergy) / temperature )

	def CalculateBER(self, modulationScheme):
		return "nada"

	def headText(self, numberObjectives):
		if (numberObjectives == 3):
			return "Score, Power, Modulation"
		else:
			return "Score, Power, Modulation, Bandwidth, TDD, SymbolRate"	

	def simulatedAnnealing (self):
		
		Tk = self.temperature

		# -----Initial solution -> Random solution
		power = random.uniform(self.minPower, self.maxPower)
		solPower = power

		modulationIndex = random.randint(0, self.maximumModulationIndex)
		modulationScheme = self.modulationScheme[modulationIndex]
		solModulation = modulationScheme

		bandwidth = random.uniform(self.minBandwidth, self.maxBandwidth)
		solBandwidth = bandwidth

		tdd = random.uniform(self.minTDD, self.maxTDD)
		solTDD = tdd
		
		symbolRate = random.uniform(self.minSymbolRate, self.maxSymbolRate)
		solSymbolRate = symbolRate

		Pbe = random.uniform(self.minPbe, self.maxPbe)
		solPbe = Pbe
		solution = self.fiveObjective(bandwidth, power, modulationIndex, symbolRate, tdd, Pbe)
		#-----
		
		# Control of number of iterations
		k = 0
		sign = True
		while (Tk > 0.1):
			
			# T value for each iteration Paper Szu
			Tk =  self.temperature/(k+1.0)
			
			# Choosing if the next parameter will be modified
			chooseParameter = random.random()
			# Transmit power 
			if (chooseParameter <= self.chance):
				nTk = self.normalize(Tk, 0, self.temperature, self.minPower, self.maxPower )
				if(sign):
					power = solPower + nTk
				else:
					power = solPower - nTk
				# Power must not exceed minPower and maxPower
				if (power > self.maxPower):
					power = self.maxPower
				elif (power < self.minPower):
					power = self.minPower
			# Choosing if the next parameter will be modified
			chooseParameter = random.random()
			# Transmit power 
			if (chooseParameter <= self.chance):
				nTk = self.normalize(Tk, 0, self.temperature, self.minPbe, self.maxPbe )
				if(sign):
					Pbe = solPbe + nTk
				else:
					Pbe = solPbe - nTk
				# Power must not exceed minPower and maxPower
				if (Pbe > self.maxPbe):
					Pbe = self.maxPbe
				elif (Pbe < self.minPbe):
					Pbe = self.minPbe
			# Choosing if the next parameter will be modified
			chooseParameter = random.random()
			# Modulation Scheme
			if (chooseParameter <= self.chance):
				# Circular list of modulations
				if(not(sign)):
					if (modulationIndex == 0):
						modulationIndex = self.maximumModulationIndex
					else:
						modulationIndex -= 1

				else:
					if (modulationIndex == self.maximumModulationIndex):
						modulationIndex = 0
					else:
						modulationIndex += 1

				modulationScheme = self.modulationScheme[modulationIndex]
			
			# Choosing if the next parameter will be modified
			chooseParameter = random.random()
			# Bandwidth
			if (chooseParameter <= self.chance):
				nTk = self.normalize(Tk, 0, self.temperature, self.minBandwidth, self.maxBandwidth)
				if(sign):
					bandwidth = solBandwidth + nTk
				else:
					bandwidth = solBandwidth - nTk
				# Bandwidth must not exceed minBandwidth and maxBandwidth
				if (bandwidth > self.maxBandwidth):
					bandwidth = self.maxBandwidth
				elif (bandwidth < self.minBandwidth):
					bandwidth = self.minBandwidth
			chooseParameter = random.random()
			# TDD
			if (chooseParameter <= self.chance):
				nTk = self.normalize(Tk, 0, self.temperature, self.minTDD, self.maxTDD)
				if(sign):
					tdd = solTDD + nTk
				else:
					tdd = solTDD - nTk
				# TDD must not exceed minTDD and maxTDD
				if (tdd > self.maxTDD):
					tdd = self.maxTDD
				elif (tdd < self.minTDD):
					tdd = self.minTDD

			chooseParameter = random.random()
			# Symbol Rate
			if (chooseParameter <= self.chance):			#(chooseParameter <= 1.00):
				nTk = self.normalize(Tk, 0, self.temperature, self.minSymbolRate, self.maxSymbolRate)
				if(sign):
					symbolRate = solSymbolRate + nTk
				else:
					symbolRate = solSymbolRate - nTk
				# symbolRate must not exceed minSymbolRate and maxSymbolRate
				if (symbolRate > self.maxSymbolRate):
					symbolRate = self.maxSymbolRate
				elif (symbolRate < self.minSymbolRate):
					symbolRate = self.minSymbolRate


			# New solution
			newSolution = self.fiveObjective(bandwidth, power, modulationIndex, symbolRate, tdd, Pbe)
	

			# New solution is better than the old solution
			if (newSolution < solution ):
				solution = newSolution
				solPower = power
				solModulation = modulationIndex
				solBandwidth = bandwidth
				solTDD = tdd
				solSymbolRate = symbolRate
				solPbe = Pbe
				if(newSolution > self.solution):
					self.solution = newSolution
					self.power = power
					self.modulation = modulationIndex
					self.bandwidth = bandwidth
					self.TDD = tdd
					self.symbolRate = symbolRate
					self.Pbe = solPbe
					self.throughput = self.maxThroughput(modulationIndex)
					
			else:
				# Probability of solution exchange, even if new solution is worse
				p = self.acceptanceProbability(solution, newSolution, self.temperature)
				genProb = random.random()

				if (genProb < p):
					solution = newSolution

			# Controlling iteration and temperature
			k += 1 
			#Changing between inc/decrementing vars
			sign = not(sign)
			#k, self.power, self.modulationScheme[self.modulation], self.bandwidth, self.TDD, self.symbolRate, self.Pbe
		return self.solution
	


def full_process(links):
	#Five objs
	#Weights for maximizing throughput
	w1 = 0.05
	w2 = 0.05
	w3 = 0.05
	w4 = 0.05
	w5 = 0.05
	w6 = 0.75

	# Transmitted power between 0.158 and 251 mW
	minPower = 1
	maxPower = 1

	# Modulation Scheme QAM between 2 and 256
	modulationScheme = [4]
	maximumModulationIndex = 0

	# Bandwidth between 2 and 32 MHz
	minBandwidth = 200
	maxBandwidth = 400

	#TDD between
	minTDD = 485
	maxTDD = 490

	# Symnol Rate between 125kbps and 1Mbps
	minSymbolRate = 125
	maxSymbolRate = 1024

	#BER
	maxPbe = math.pow(10, -6)
	minPbe = math.pow(10, -8)
	
	# Initial temperature
	temperature = 1000
	
	results = []
	for i in range(0, len(links)):
		for c in links[i]:
			channel = Channel(w1, w2, w3, w4, w5, w6, temperature, minBandwidth,
 				maxBandwidth, minPower, maxPower, modulationScheme,
				maximumModulationIndex, minSymbolRate, maxSymbolRate, minTDD, maxTDD, minPbe, maxPbe, c[1])

			simu = channel.simulatedAnnealing()
			flag = False
			j = 0
			while( flag == False and j < len(results)):
				if(results[j][2] > simu ):
					results.insert(j, [i,c[0], simu])
					flag = True
				j = j + 1
			if flag == False:
				results.append( [i,c[0], simu])

	return results



if __name__ == '__main__':
    l = [1, 2]
    ch = [1, 2, 3]

    to_sa = []
    for i in l:
        to_sa.append( ch )

    ret = full_process(to_sa)

    d = {}
    for l, ch, rw in ret:
        if l in d or ch in d.itervalues():
            pass
        else:
            d[l] = ch

    print ret
    print d
