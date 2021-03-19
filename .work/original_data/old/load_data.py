import numpy
import json
import zlib
import bz2
import pickle
import _pickle as cPickle



class load_data:

  symbols = {}
  elements = {}
  
  
  
  def run():
    print("Load Data")
    
    load_data.load_symbols('elements.csv')
    load_data.load_elements('elements.csv')
    load_data.load_isotopes('nubtab12.asc.txt')
    load_data.load_decaymodes('decaymodes.txt')

  

  def load_symbols(file_name):
    load_data.symbols[0] = 'Nn'

    fh = open(file_name, 'r')
    for line in fh:
      fields = line.split(",")
      try:
        protons = int(fields[0])
        symbol = str(fields[2]).strip().capitalize()
        load_data.symbols[protons] = symbol
        load_data.symbols[symbol] = protons
      except:
        pass

    fh.close()


  def load_elements(file_name):
    
    load_data.elements[0] = {
                  'protons': 0,
                  'neutrons': 1,
                  'nucleons': 1,
                  'symbol': 'Nn',
                  'element': 'Neutron',
                  'mass': 0.0,
                  'period': None,
                  'group': None,
                  'isotopes': {},
                  'stable': [],
                  'unstable': [],
                  }

    fh = open(file_name, 'r')
    for line in fh:
      fields = line.split(",")
      try:
        protons = int(fields[0])
        neutrons = int(fields[4])
        protons = int(fields[0])
        period = int(fields[7])
        try:
          group = int(fields[8])    
        except:
          group = None
        load_data.elements[protons] = {
                'protons': protons,
                'neutrons': neutrons,
                'nucleons': protons + neutrons,
                'symbol': str(fields[2]).strip().capitalize(),
                'element': str(fields[1]).strip().capitalize(),
                'mass': float(fields[3]),
                'period': period,
                'group': group,
                'isotopes': {},
                'stable': [],
                'unstable': [],
                }
      except:
        pass
    fh.close()


  def load_isotopes(file_name):

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

    fh = open(file_name, 'r')
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

      # Save
      if(stability == 'stable' and w == 0): 
        load_data.elements[protons]['stable'].append(nucleons)
        load_data.elements[protons]['isotopes'][nucleons] = {
                                                 'neutrons': neutrons,
                                                 'nucleons': nucleons,
                                                 'mass': float(nucleons), 
                                                 'stable': True,
                                                 'half_life': None,
                                                 'decay_constant': None,
                                                 'percentage': percentage,
                                                 'decay_modes': [],
                                                 'gammas': [[],[],[]],
                                                }
      elif(stability == 'unstable' and w == 0):
        load_data.elements[protons]['unstable'].append(nucleons)
        load_data.elements[protons]['isotopes'][nucleons] = {
                                                 'neutrons': neutrons,
                                                 'nucleons': nucleons,
                                                 'mass': float(nucleons), 
                                                 'stable': False,
                                                 'half_life': half_life,
                                                 'decay_constant': decay_constant,
                                                 'percentage': 0.0,
                                                 'decay_modes': [],
                                                 'gammas': [[],[],[]],
                                                }

  

  def load_decaymodes(file_name):
    fh = open(file_name, 'r')
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

      try:
        print(protons, nucleons)
        load_data.elements[protons]['isotopes'][nucleons]['decay_modes'].append({
                                                                   'excited_decay': excited,
                                                                   'protons': protons_to,
                                                                   'neutrons': neutrons_to,
                                                                   'nucleons': nucleons_to,
                                                                   'decay_chance': decay_chance, 
                                                                   'half_life': half_life, 
                                                                   'decay_constant' : decay_constant, 
                                                                   'notes': notes, 
                                                                   })
      except:
        pass
    fh.close()



  def load_gammaenergies(elements, file_name):
    fh = open(file_name, 'r')
    fd = []
    for row in fh:
      fd.append(row.strip())
    i = 0
    mstate = 0
    while(i<len(fd)):
      if(fd[i] == "#Header"):
        i = i + 1
        f = fd[i].split(" ")
        protons = int(f[1])
        nucleons = int(f[2])
        state = int(f[3])  
        if(state > mstate):
          mstate = state
        i = i + 1
        f = fd[i].split(" ")
        data_points = int(f[1])
        m = 0
        while(m<data_points):
          i = i + 1
          f = fd[i].split(" ")
          energy = float(f[0])
          intensity = float(f[1])
          elements[protons]['isotopes'][nucleons]['gammas'][state].append([energy, intensity])
          m = m + 1
      i = i + 1




"""


def load_isotopemasses(elements, file_name):
  fh = open(file_name, 'r')

  alpha = 'abcdefghijklmnopqrstuvwxyz'
  iso_mass = {}

  for line in fh:
    line_lc = line.lower()

    flag = False
    for c in alpha:
      if(c in line_lc[0:12]):
        flag = True
      f = line.strip().split('\t')

    if(flag):
      p = f[0]
      symbol = f[1]
    else:
      f = [p, symbol] + f
    f = f[0:4]

    fa = f[-1].split('(')
    f[0] = int(f[0])
    f[2] = int(f[2])
    f[-1] = float(fa[0].replace(' ',''))
    #print(f[0], f[1], f[2], f[3])
    p = int(f[0])
    nuc = int(f[2])
    mass = float(f[3])
    #print(p)
    #print(mass, elements[p]['isotopes'])

    try:
      elements[p]['isotopes'][nuc]['mass'] = mass 
    except:
      pass

  return elements



def save_z(file_path, dict):
    dat = json.dumps(dict)
    cdat = zlib.compress(dat.encode(), level=9)
    fh = open(file_path, 'wb')
    fh.write(cdat)
    fh.close()


def save_pz(file_path, dict):
  with bz2.BZ2File(file_path, 'w') as f: 
    cPickle.dump(dict, f)
    
    
  
symbols = load_symbols('elements.csv')
elements = load_elements('elements.csv')
elements = load_isotopes(elements, 'nubtab12.asc.txt')
elements = load_decaymodes(elements, 'decaymodes.txt')
elements = load_gammaenergies(elements, 'gammaenergies.txt')
elements = load_isotopemasses(elements, 'isotope_masses.txt')



save_z('symbols.z', symbols)
save_z('elements.z', elements)


save_pz('symbols.pz', symbols)
save_pz('elements.pz', elements)

"""



load_data.run()



