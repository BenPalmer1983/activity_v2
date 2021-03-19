import numpy


fh = open('gammaenergies.txt', 'r')
fd = []
for row in fh:
  fd.append(row.strip())
i = 0
gamma = {}
while(i<len(fd)):
  if(fd[i] == "#Header"):
    i = i + 1
    f = fd[i].split(" ")
    protons = int(f[1])
    nucleons = int(f[2])
    state = int(f[3])    
    if(protons not in gamma.keys()):
      gamma[protons] = {}
    if(nucleons not in gamma[protons].keys()):
      gamma[protons][nucleons] = {}
    gamma[protons][nucleons][state] = []    
    i = i + 1
    f = fd[i].split(" ")
    data_points = int(f[1])
    gamma[protons][nucleons][state] = numpy.zeros((data_points,2,),)
    m = 0
    while(m<data_points):
      i = i + 1
      f = fd[i].split(" ")
      gamma[protons][nucleons][state][m,0] = float(f[0])
      gamma[protons][nucleons][state][m,1] = float(f[1])
      m = m + 1
    #print(gamma[protons][nucleons][state])
  i = i + 1
#print(gamma)

energy = []
intensity = []
for p in gamma.keys():
  for n in gamma[p].keys():
    for l in gamma[p][n].keys():
      for i in range(len(gamma[p][n][l])):    
        if(gamma[p][n][l][i,0] != 0.0):
          energy.append(gamma[p][n][l][i,0])
          intensity.append(gamma[p][n][l][i,1])

print(min(energy), max(energy))


