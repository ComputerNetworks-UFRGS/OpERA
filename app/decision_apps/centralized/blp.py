import subprocess 
import imp
import os

DIR = "."
TMPFILE= DIR+"/file.tmp"
MODELFILE=DIR+"/shu.mod"
OUTPUTFILE=DIR+"/temp.py"
#Fixados

# param Pmax[links] :=1 1 2 1 3 1 4 1 5 1 6 1 ;
#Pmax = [1, 1, 1, 1, 1, 1]

# param B[canais] :=1 200 2 400 3 500 4 400;
#B = [200, 400, 500, 400]

# param Pi [canais] : 
# 1 2 3 4 5 6 :=
# 1 0.2 0.2 0.2 0.2 0.2
# 2 0.2 0.2 0.2 0.2 0.2 
# 3 0.2 0.2 0.2 0.2 0.2
# 3 0.2 0.2 0.2 0.2 0.2;
#Pi = [0.2, 0.2, 0.2, 0.2, 0.2]
	
# param I[links,links]: 
# 1 2 3 4 5 6 :=
# 1 1 1 1 1 1 1 
# 2 1 1 1 1 1 1 
# 3 1 1 1 1 1 1 
# 4 1 1 1 1 1 1 
# 5 1 1 1 1 1 1 
# 6 1 1 1 1 1 1;
#I = [
#	[1,1,1,1,1,1],
#	[1,1,1,1,1,1],
#	[1,1,1,1,1,1],
#	[1,1,1,1,1,1],
#	[1,1,1,1,1,1],
#	[1,1,1,1,1,1]
#	]
# param n := 3;
#n = 4
# param l := 6;
#l = 6
#param u := 5;
#u = 1
#param U[vazoes]:= 
#1 0.0001 2 0.5 3 1 4 1.5 5 2 ;
#U = [1.0]
# param C[canais] : # 
#1 35.0514146042 35.0514146047 35.0514146043 35.0514146042 35.0514146084 35.0514146049
#C = [ 1.0, 1.0, 1.0, 1.0 ]
#param gama[canais, vazao] : 
#1 2 3 4 5 :=
#1 0.000270654782058 1.35327391029 2.70654782058 4.05982173087 5.41309564115 
#2 0.000101494140551 0.507470702754 1.01494140551 1.52241210826 2.02988281102 
#3 0.000115734113511 0.578670567553 1.15734113511 1.73601170266 2.31468227021 
#4 0.000287567470488 1.43783735244 2.87567470488 4.31351205732 5.75134940976 
#5 0.000195136974863 0.975684874313 1.95136974863 2.92705462294 3.90273949725 ;
#gama = [
#	[1.0, 1.0, 1.0, 1.0, 1.0 ],
#	[1.0, 1.0, 1.0, 1.0, 1.0 ],
#	[1.0, 1.0, 1.0, 1.0, 1.0 ],
#	[1.0, 1.0, 1.0, 1.0, 1.0 ],
#]

# n = numero canais
# l = num links
# U = 
def BLP(n,l,u, Pmax, B, Pi, I, U, C, gama):
	
	##################################Creating data for GLPK###########################
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
		text += str(i+1)+" "+str(Pmax[i])+" "
	text += ";\n"
	#Defining links bandwidth
	text += "param B :="
	for m in range(n):
		text += str(m+1)+" "+str(B[m])+" "
	text += ";\n"
	#Defining channel capacity per channel or SNR
	text += "param C :="
	for m in range(n):
		text += " %d %f" % (m+1, C[m])
	text += ";\n"
	#Defining power mask
	text += "param Pi := \n"
	for i in range(n):
		text += "%d %f " % (i+1, Pi[i])
	text += ";\n"
	
	#Creating Intereference matrix
	text+="param I : \n"
	textAux = ":="
	for i in range(l):
		text += str(i+1)+" "
		textAux +="\n"
		textAux += str(i+1)+" "
		for j in range(l):
			textAux += str(I[i][j])+" "
	text += textAux;
	text += ";\n"
	#Defining U
	text += "param U := \n"
	for i in range(u):
		text += "%d %f " % (i+1, U[i])
	text += ";\n"
	#Calculating gama
	text += "param gama : \n"
	for i in range(u):
		text += str(i+1)+" "
	text += ":="
	for m in range(n):
		text += "\n"
		text += str(m+1)+" "
		for k in range(u):
			text += str(gama[m][k])+" "
	text+=";\nend;"
	f = open(TMPFILE, "w")
	f.write(text)
	f.close()
	cmd="/usr/local/bin/glpsol -m "+MODELFILE+" -d "+TMPFILE+" -o /dev/null -y "+OUTPUTFILE+" &>/dev/null"
	subprocess.call([cmd], shell=True)
	import temp
	return temp.ret

def full_process(links, channels):
	channel_list = [200, 400, 500, 400]
	rssi = [0.1/ 100000000.0, 1000000000.1/ 100000000.0, 0.1/ 100000000.0, 0.1/ 100000000.0]

	n	= len(channels)
	l	= len(links)
	Pmax = [1.0] * len(links)
	B	= map(lambda x: channel_list[x], channels)
	Pi = [1.0] * len(channels)
	I = [ [1.0] *len(links) ] * len(links)
	U = [1.0]
	u = len(U)
	C = map(lambda x: rssi[x], channels)
	gama = [[1.0] * len(links)] * len(channels)

	print n
	print l
	print Pmax
	print B
	print Pi
	print I
	print u
	print U
	print C
	print gama

	sol = BLP(n, l, u, Pmax, B, Pi, I, U, C, gama)
	print sol
	return sol

channels = [0, 1, 2, 3]
links = [1, 2]
res = full_process(links, channels)


d = {}
for idx, i in enumerate(res):
	d[links[idx]] = i[1]-1

print d
