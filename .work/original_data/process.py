import numpy
import json
import zlib

def make_element():
  # KEY - 
  return {
         'key': None,
         'symbol': '',
         'symbol_lc': '',
         'element': '',
         'protons': '',
         'neutrons': '',
         'nucleons': '',
         'mass': 0.0,
         'period': None,
         'group': None,
         'stable': {},
         'unstable': {},
         }
         
def make_isotope():
  return {
         'key': 0,
         'code': 0,
         'protons': 0,
         'neutrons': 0,
         'nucleons': 0,
         'stability': None,
         'half_life': None,
         'decay_constant': None,
         'percentage': 0.0,
         }
         
           
isotopes = {}  
elements = {} 
symbols = {}
decay_modes = {}
decay_modes_excited = {}

elements['nn'] = 0
symbols[0] = 'nn'
isotopes[0] = make_element()
isotopes[0]['key'] = 0
isotopes[0]['symbol'] = 'nn'
isotopes[0]['symbol_lc'] = 'nn'
isotopes[0]['element'] = 'Neutron'
isotopes[0]['protons'] = 0
isotopes[0]['neutrons'] = 1
isotopes[0]['nucleons'] = 1
isotopes[0]['mass'] = 1.00866491588
isotopes[0]['period'] = None
isotopes[0]['group'] = None



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


fh = open('elements.csv', 'r')
for line in fh:
  fields = line.split(",")
  try:
    key = int(fields[0])               # PROTONS
    element = str(fields[2]).strip()
    isotopes[key] = make_element()    
    
    isotopes[key]['key'] = key
    isotopes[key]['symbol'] = str(fields[2]).strip()
    isotopes[key]['symbol_lc'] = str(fields[2]).strip().lower()
    isotopes[key]['element'] = str(fields[1]).strip()
    isotopes[key]['protons'] = int(fields[0])
    isotopes[key]['neutrons'] = int(fields[4])
    isotopes[key]['nucleons'] = int(fields[0]) + int(fields[4])
    isotopes[key]['mass'] = float(fields[3])
    isotopes[key]['period'] = int(fields[7])
    try:
      isotopes[key]['group'] = int(fields[8])    
    except:
      isotopes[key]['group'] = None
    elements[isotopes[key]['symbol_lc']] = key      
    symbols[key] = isotopes[key]['symbol']
  except:
    pass
fh.close()
#print(elements)
print(symbols)


fh = open('decaymodes.txt', 'r')
for line in fh:
  fields = line.split(" ")
  
  protons = int(fields[2])  
  nucleons = int(fields[1])
  excited = int(fields[3])
  neutrons = nucleons - protons
  
  protons_to = int(fields[5])  
  nucleons_to = int(fields[4])
  neutrons_to = nucleons_to - protons_to
  decay_chance = float(fields[6])
  half_life = float(fields[7])
  if(half_life == 0.0):
    decay_constant = None
  else:
    decay_constant = numpy.log(2.0) / half_life
  notes = fields[8].strip()  
  
  if(excited == 0):
    if(protons not in decay_modes.keys()):
      decay_modes[protons] = {}
    if(nucleons not in decay_modes[protons].keys()):
      decay_modes[protons][nucleons] = []
    decay_modes[protons][nucleons].append({'code': 1000 * protons + nucleons, 'protons': protons_to, 'neutrons': neutrons_to, 'nucleons': nucleons_to, 'decay_chance': decay_chance, 'half_life': half_life, 'decay_constant' : decay_constant, 'notes': notes, })
  else:  
    if(key not in decay_modes_excited.keys()):
      decay_modes_excited[protons] = {}
    if(nucleons not in decay_modes_excited[protons].keys()):
      decay_modes_excited[protons][nucleons] = []      
    decay_modes_excited[protons][nucleons].append({'code': 1000 * protons + nucleons, 'protons': protons_to, 'neutrons': neutrons_to, 'nucleons': nucleons_to, 'decay_chance': decay_chance, 'half_life': half_life, 'decay_constant' : decay_constant, 'notes': notes, })
fh.close()


#print(decay_modes)



d = {}
u = {
    's': 1.0,
    'y': 3.1557600e7,
    'ys': 1.0e-24,
    'ms': 1.0e-3,
    'as': 1.0e-18,
    'zs': 1.0e-21,
    'd': 86400.0,
    'my': 3.1557600e13,
    'm': 60,
    'ns': 1.0e-9,
    'ky': 3.1557600e10,
    'ps': 1.0e-12,
    'us': 1.0e-6,
    'h': 3600.0,
    'gy': 3.1557600e16,
    'ty': 3.1557600e19,
    'py': 3.1557600e22,
    'ey': 3.1557600e25,
    'zy': 3.1557600e28,
    'yy': 3.1557600e31,    
    }
 
fh = open('nubtab12.asc.txt', 'r')
for line in fh:
  nucleons = int(line[0:3])
  protons = int(line[4:7])
  w = int(line[7:8])

  neutrons = nucleons - protons
  stable_unstable = line[60:72]
  decay_modes = line[110:].strip()
  half_life = None
  if(stable_unstable.strip().lower() == 'stbl'):
    stability = 'stable'
    p = decay_modes.split(' ')
    p = p[0]
    p = p.split("=")
    percentage = float(p[1])    
  elif('p-unst' in stable_unstable.strip().lower()):
    stability = 'p_unstable'
  elif(stable_unstable.strip().lower() == '' or 'r' in stable_unstable.strip().lower() or stable_unstable.strip().lower() == 'contamntn'):
    stability = 'unknown_unstable'
  else:
    stability = 'unstable'
    stable_unstable = stable_unstable.strip()
    ls = stable_unstable.split(" ")
    #print(protons, nucleons, stable_unstable, w)
    val = ls[0].replace('#','')
    val = val.replace('<','')
    val = val.replace('>','')
    val = val.replace('~','')
    val = float(val)
    units = ls[-1].lower()
    half_life = val * float(u[units])
    decay_constant = numpy.log(2.0)/half_life

   
  if(stability == 'stable' and w == 0): 
    isotopes[protons]['stable'][nucleons] = make_isotope() 
    isotopes[protons]['stable'][nucleons]['key'] = nucleons
    isotopes[protons]['stable'][nucleons]['code'] = 1000 * protons + nucleons
    isotopes[protons]['stable'][nucleons]['protons'] = protons
    isotopes[protons]['stable'][nucleons]['neutrons'] = neutrons
    isotopes[protons]['stable'][nucleons]['nucleons'] = nucleons
    isotopes[protons]['stable'][nucleons]['stability'] = stability
    isotopes[protons]['stable'][nucleons]['half_life'] = None
    isotopes[protons]['stable'][nucleons]['decay_constant'] = None
    isotopes[protons]['stable'][nucleons]['percentage'] = percentage 
  
  elif(stability == 'unstable' and w == 0): 
    isotopes[protons]['unstable'][nucleons] = make_isotope() 
    isotopes[protons]['unstable'][nucleons]['key'] = nucleons
    isotopes[protons]['unstable'][nucleons]['code'] = 1000 * protons + nucleons
    isotopes[protons]['unstable'][nucleons]['protons'] = protons
    isotopes[protons]['unstable'][nucleons]['neutrons'] = neutrons
    isotopes[protons]['unstable'][nucleons]['nucleons'] = nucleons
    isotopes[protons]['unstable'][nucleons]['stability'] = stability
    isotopes[protons]['unstable'][nucleons]['half_life'] = half_life
    isotopes[protons]['unstable'][nucleons]['decay_constant'] = decay_constant
    isotopes[protons]['unstable'][nucleons]['percentage'] = 0.0
    

  """
  i = make_isotope() 
  i['key'] = nucleons
  i['code'] = 1000 * protons + nucleons
  i['protons'] = protons
  i['neutrons'] = neutrons
  i['nucleons'] = nucleons
  i['stability'] = stability
  i['half_life'] = None
  i['decay_constant'] = None
  i['percentage'] = 0.0 
   
  if(stability == 'stable' and w == 0): 
    i['percentage'] = percentage
    isotopes[protons]['stable'][nucleons] = i
  
  elif(stability == 'unstable' and w == 0): 
    i['half_life'] = half_life
    i['decay_constant'] = decay_constant
    i['percentage'] = 0.0
    isotopes[protons]['stable'][nucleons] = i
  """  

  #key = elements[protons]      
        
  #neutrons = nucleons - protons
  #key = 1000 * nucleons + protons
  #print(nucleons, protons, stability, stable_unstable)
  
fh.close()

#print(isotopes[26])


#with open('isotopes.dat', 'w') as outfile:
#    json.dump(isotopes, outfile)

  

dat = json.dumps(isotopes)
cdat = zlib.compress(dat.encode(), level=9)
fh = open('isotopes.z', 'wb')
fh.write(cdat)
fh.close()

fh = open('isotopes.d','w')
#print(isotopes)
fh.close()

