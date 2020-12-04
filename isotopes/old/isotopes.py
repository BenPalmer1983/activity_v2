import os
import numpy
import bz2
import pickle
import _pickle as cPickle



class isotopes:

  symbols = {}
  jeffdata = {}

######################################################### 
#  
# USE DATA
#  
#########################################################

  def load_data(dir='isotope_data'):
    
    isotopes.symbols = isotopes.load_pz(dir  + '/symbols.pz')
    isotopes.elements = isotopes.load_pz(dir  + '/elements.pz')
    isotopes.jeffdata = isotopes.load_pz(dir  + '/jeffdata.pz')

  
  
  
  def get_isotope_jeff(code):
    code = int(code)
    if(code in isotopes.jeffdata.keys()):
      return isotopes.jeffdata[code]
    return None





  
######################################################### 
#  
# MAKE DATA
#  
#########################################################
  
  @staticmethod
  def make_data():
    print("Make Data")    
    isotopes.load_symbols('data/elements.csv')


    isotopes.load_jeff('data/JEFF33-rdd_all.asc')

    isotopes.make_dir('isotope_data')
    isotopes.save_pz('isotope_data/symbols.pz', isotopes.symbols)
    isotopes.save_pz('isotope_data/elements.pz', isotopes.elements)
    isotopes.save_pz('isotope_data/jeffdata.pz', isotopes.jeffdata)
  
  @staticmethod
  def make_dir(dir):
    dirs = dir.split("/")
    try:
      dir = ''
      for i in range(len(dirs)):
        dir = dir + dirs[i]
        if(not os.path.exists(dir) and dir.strip() != ''):
          os.mkdir(dir) 
        dir = dir + '/'
      return True
    except:
      return False

  def load_symbols(file_name):
    isotopes.symbols[0] = 'Nn'

    fh = open(file_name, 'r')
    for line in fh:
      fields = line.split(",")
      try:
        protons = int(fields[0])
        symbol = str(fields[2]).strip().capitalize()
        isotopes.symbols[protons] = symbol
        isotopes.symbols[symbol] = protons
      except:
        pass
    fh.close()


  def load_elements(file_name):
    
    isotopes.elements[0] = {
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
        isotopes.elements[protons] = {
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
        isotopes.elements[protons]['stable'].append(nucleons)
        isotopes.elements[protons]['isotopes'][nucleons] = {
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
        isotopes.elements[protons]['unstable'].append(nucleons)
        isotopes.elements[protons]['isotopes'][nucleons] = {
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
        isotopes.elements[protons]['isotopes'][nucleons]['decay_modes'].append({
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
        
        
    #  try:
    #    pn = 1000 * protons + nucleons
    #    dn = 1000 * protons_to + nucleons_to
    fh.close()



  def load_gammaenergies(file_name):
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
          isotopes.elements[protons]['isotopes'][nucleons]['gammas'][state].append([energy, intensity])
          m = m + 1
      i = i + 1


  def load_isotopemasses(file_name):
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
        isotopes.elements[p]['isotopes'][nuc]['mass'] = mass 
      except:
        pass
        
        
        
  def load_jeff(file_path):
    blocks_451 = {}   
    blocks_457 = {}   
    
    # Read into MF -> MT
    fh = open(file_path, 'r')    
    n = 0
    for row in fh:
      n = n + 1
      mf = int(row[70:72])
      mt = int(row[72:75])
      mat = int(row[66:70])
      row_num = int(row[75:]) 
      if(mt == 451):
        if(mat not in blocks_451.keys()):
          blocks_451[mat] = []
        blocks_451[mat].append(row[:-1])
      if(mt == 457):
        if(mat not in blocks_457.keys()):
          blocks_457[mat] = []
        blocks_457[mat].append(row[:-1])
    fh.close()
        
    # Process blocks
    for k in blocks_451.keys():
      isotopes.jeff_block(blocks_451[k], blocks_457[k])
    

      
  def jeff_block(blocks_451, blocks_457):
    isotope = {
    'key': None,    
    'element': None,  
    'protons': None, 
    'neutrons': None, 
    'nucleons': None, 
    'metastable': None, 
    'stable': False,
    'natural_abundance': 0.0,
    'mass_to_neutron': None,
    'mass_amu': None,
    'half_life': None,
    'decay_modes': {},
    }
    
    for row in blocks_451:
      if("STABLE NUCLEUS" in row):
        isotope['stable'] = True
      elif("NATURAL ABUNDANCE" in row):
        isotope['natural_abundance'] = float(row[19:31].strip().replace(" ",""))
  
    for row in blocks_451:
      l = []
      l.append(row[0:11])
      l.append(row[11:22])
      l.append(row[22:33])
      l.append(row[33:44])
      l.append(row[44:55])
      l.append(row[55:66]) 
      mat = int(row[66:70])
      mf = int(row[70:72])
      mt = int(row[72:75])
      row_num = int(row[75:]) 
      #print(l[0],l[1],l[2],l[3],l[4],l[5],mat,mf,mt, row_num)  
    
      if(row_num == 1):
        isotope['key'] = int(isotopes.read_float(l[0]))
        isotope['protons'], isotope['neutrons'], isotope['nucleons'] = isotopes.read_isotope_code(isotope['key'])
        isotope['element'] = isotopes.symbols[isotope['protons']]
        isotope['mass_to_neutron'] = float(isotopes.read_float(l[1]))
        isotope['mass_amu'] = isotope['mass_to_neutron'] * 1.00866531
      elif(row_num == 2):
        if(int(isotopes.read_float(l[3])) == 0):
          isotope['metastable'] = int(isotopes.read_float(l[3]))
        else:
          isotope['metastable'] = int(isotopes.read_float(l[3]))
          isotope['key'] = isotope['key'] + 1000000 * int(isotopes.read_float(l[3]))

    
    for row in blocks_457:
      l = []
      l.append(row[0:11])
      l.append(row[11:22])
      l.append(row[22:33])
      l.append(row[33:44])
      l.append(row[44:55])
      l.append(row[55:66]) 
      mat = int(row[66:70])
      mf = int(row[70:72])
      mt = int(row[72:75])
      row_num = int(row[75:]) 
      if(row_num == 2):
        isotope['half_life'] = float(isotopes.read_float(l[0]))    
      if(row_num == 4):
        decay_modes = int(isotopes.read_float(l[5])) 
      if(row_num >= 5 and row_num < 5 + decay_modes):
        f = float(isotopes.read_float(l[0]))
        n = int(f)
        if(float(n) == f):
          mode = -1
          if(n == 1):
            mode = 1
            mode_text = 'B-'      
            to_p = isotope['protons'] + 1
            to_n = isotope['neutrons'] - 1
          elif(n == 2):
            mode = 2
            mode_text = 'B+ or EC'
            to_p = isotope['protons'] - 1
            to_n = isotope['neutrons'] + 1
          elif(n == 3):
            mode = 3
            mode_text = 'IT'
            to_p = isotope['protons'] 
            to_n = isotope['neutrons']
          elif(n == 4):
            mode = 4
            mode_text = 'A'
            to_p = isotope['protons'] - 2
            to_n = isotope['neutrons'] - 2
          elif(n == 5):
            mode = 5
            mode_text = 'N'
            to_p = isotope['protons'] 
            to_n = isotope['neutrons'] - 1
          elif(n == 6):
            # Ignore
            mode = -1
            mode_text = 'SF'
            
          if(mode > 0):
            to_meta = int(isotopes.read_float(l[1]))
            qvalue = float(isotopes.read_float(l[2]))            # In eV
            branching_factor = float(isotopes.read_float(l[4]))  # 0.0 to 1.0
            to_key = to_meta * 1000000 + 1000 * to_p + (to_p + to_n)
            
            isotope['decay_modes'][to_key] = [branching_factor, to_meta, qvalue]
            
    isotopes.jeffdata[isotope['key']] = isotope    

    
    
      
  @staticmethod
  def read_float(inp):
    out = ''
    if('e' not in inp.lower()):
      for i in range(len(inp)):
        if(i>1 and inp[i] == '+'):
          out = out + 'e'
        elif(i>1 and inp[i] == '-'):
          out = out + 'e-'
        elif(inp[i] != ' '):
          out = out + inp[i]
    else:
      out = inp
    return float(out)


  @staticmethod
  def read_int(inp):
    out = ''
    if('e' not in inp.lower()):
      for i in range(len(inp)):
        if(i>1 and inp[i] == '+'):
          out = out + 'e'
        elif(i>1 and inp[i] == '-'):
          out = out + 'e-'
        elif(inp[i] != ' '):
          out = out + inp[i]
    else:
      out = inp
    return int(numpy.floor(float(out)))

  @staticmethod
  def read_isotope_code(code):
    protons = int(numpy.floor(code/1000))
    nucleons = int(code - 1000 * protons)
    neutrons = nucleons - protons
    return protons, neutrons, nucleons
   
  @staticmethod
  def isotope_code(code):
    metastable = int(numpy.floor(code/1000000))
    code = code - metastable * 1000000
    protons = int(numpy.floor(code/1000))
    nucleons = int(code - 1000 * protons)
    neutrons = nucleons - protons
    return metastable, protons, neutrons, nucleons 

  @staticmethod
  def save_pz(file_path, dict):
    with bz2.BZ2File(file_path, 'w') as f: 
      cPickle.dump(dict, f)
    
  @staticmethod
  def load_pz(file_path):
    data = bz2.BZ2File(file_path, 'rb')
    return cPickle.load(data)
  
  
  
  def make_chain():
    pass


isotopes.make_data()

isotopes.load_data()


print(isotopes.get_isotope_jeff(82210))


