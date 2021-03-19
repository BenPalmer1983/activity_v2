import os
import numpy
import bz2
import copy
import pickle
import _pickle as cPickle



class isotopes:

  symbols = {}
  isotopes = {}
  jeffdata = {}

######################################################### 
#  
# USE DATA
#  
#########################################################

  @staticmethod
  def load_data(dir='isotope_data'):
    
    d = isotopes.load_pz(dir  + '/isotopes.pz')
    isotopes.sources = d[0]
    isotopes.symbols = d[1]
    isotopes.isotopes = d[2]
    isotopes.gammas = d[3]
    isotopes.gammas_array = d[4]
    isotopes.jeffdata = d[5]
  
  
  @staticmethod
  def get_isotope_jeff(code):
    code = int(code)
    if(code in isotopes.jeffdata.keys()):
      return isotopes.jeffdata[code]
    return None
    
  @staticmethod
  def isotope_data(code):
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
    sources = ["Element list/csv: https://gist.github.com/GoodmanSciences/c2dd862cd38f21b0ad36b8f96b4bf1ee", "JEFF 3.3 via NEA"]

    isotopes.make_dir('isotope_data')
    
    d = [sources,
         isotopes.symbols, 
         isotopes.isotopes,
         isotopes.gammas,
         isotopes.gammas_array,
         isotopes.jeffdata]
    
    isotopes.save_pz('isotope_data/isotopes.pz', d)
  
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

  
  @staticmethod
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

        
  
  @staticmethod
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
    
    

  @staticmethod    
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
        isotope['natural_abundance'] = float(row[19:31].strip().replace(" ","")) / 100.0    # 0.0 to 1.0
  
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

    # Read In Gammas    
    n = 0
    gammas = 0
    gn = 0
    while(n < len(blocks_457)):
      row = blocks_457[n]
      l, mat, mf, mt, row_num = isotopes.read_row(row)
      if(row_num == 4):
        decay_modes = int(isotopes.read_float(l[5])) 
      elif(row_num >= 5 and row_num == 5 + decay_modes):
        try:
          if(int(l[4]) == 6 and int(l[5]) > 0):
            gammas = int(l[5])
            isotopes.gammas[isotope['key']] = {} 
            isotopes.gammas_array[isotope['key']] = numpy.zeros((gammas, 2,),)
            
            n = n + 1
            row = blocks_457[n]
            l, mat, mf, mt, row_num = isotopes.read_row(row)
            nfact = float(isotopes.read_float(l[0]))   
        except:
          pass
      elif(gammas > 0 and gn < gammas):     
        try:
        
          # First row
          energy = float(isotopes.read_float(l[0])) * 1000 # eV
          d_energy = float(isotopes.read_float(l[1])) * 1000 # eV
         
          # Second row
          n = n + 1
          row = blocks_457[n]
          l, mat, mf, mt, row_num = isotopes.read_row(row)
        
          intensity_endf = float(isotopes.read_float(l[2]))
          d_intensity_endf = float(isotopes.read_float(l[3]))
          intensity = nfact * float(isotopes.read_float(l[2]))
          d_intensity = nfact * float(isotopes.read_float(l[3]))

          # Third row
          n = n + 1
          row = blocks_457[n]
          l, mat, mf, mt, row_num = isotopes.read_row(row)
        
          tot_int_conv_coeff = float(isotopes.read_float(l[0]))
          d_tot_int_conv_coeff = float(isotopes.read_float(l[1]))
          k_shell_int_conv_coeff = float(isotopes.read_float(l[2]))
          d_k_shell_int_conv_coeff = float(isotopes.read_float(l[3]))
          l_shell_int_conv_coeff = float(isotopes.read_float(l[4]))
          d_l_shell_int_conv_coeff = float(isotopes.read_float(l[5]))
          
          isotopes.gammas[isotope['key']][energy] = {
            'energy': energy,
            'd_energy': d_energy,
            'n_factor': nfact,
            'intensity_endf': intensity_endf,
            'd_intensity_endf': d_intensity_endf,
            'intensity': intensity,
            'd_intensity': d_intensity,
            'tot_int_conv_coeff': tot_int_conv_coeff,
            'd_tot_int_conv_coeff': d_tot_int_conv_coeff,
            'k_shell_int_conv_coeff': k_shell_int_conv_coeff,
            'd_k_shell_int_conv_coeff': d_k_shell_int_conv_coeff,
            'l_shell_int_conv_coeff': l_shell_int_conv_coeff,
            'd_l_shell_int_conv_coeff': d_l_shell_int_conv_coeff,
          }
          
          # Store in array
          isotopes.gammas_array[isotope['key']][gn, 0] = energy
          isotopes.gammas_array[isotope['key']][gn, 1] = intensity
          
          # Increment gn
          gn = gn + 1
        except:     
          pass
        
        
        
      n = n + 1  
            
    isotopes.jeffdata[isotope['key']] = isotope    

    # Add to isotopes
    if(isotope['protons'] not in isotopes.isotopes.keys()):
      isotopes.isotopes[isotope['protons']] = {
              'mass': 0.0,
              'element': isotope['element'],
              'stable': [],
              'unstable': [],
              }
    if(isotope['stable']):
      isotopes.isotopes[isotope['protons']]['stable'].append(isotope['key'])
      isotopes.isotopes[isotope['protons']]['mass'] = isotopes.isotopes[isotope['protons']]['mass'] + isotope['mass_amu'] * isotope['natural_abundance']
    else:
      isotopes.isotopes[isotope['protons']]['unstable'].append(isotope['key'])
      
      
      
  @staticmethod
  def read_row(row):   
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
    return l, mat, mf, mt, row_num
    
      
      
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
  
  
  
  
  @staticmethod
  def get_protons(element):
    try:
      protons = int(element)
    except:
      protons = isotopes.symbols[element.strip().capitalize()]
    return protons
    
  
  @staticmethod
  def get_element(protons):
    element = isotopes.symbols[protons]
    return element
    
  
  @staticmethod
  def get_readable(key):
    metastable, protons, neutrons, nucleons = isotopes.isotope_code(key)
    element = isotopes.get_element(protons)
    out = str(element) + str(nucleons) 
    if(metastable == 1):
      out = out + "-M"
    elif(metastable == 2):
      out = out + "-N"    
    return out
    
  
  @staticmethod
  def get_element_stable(element):
    protons = isotopes.get_protons(element)
    return isotopes.isotopes[protons]['stable']
    
  
  @staticmethod
  def get_element_unstable(element):
    protons = isotopes.get_protons(element)
    return isotopes.isotopes[protons]['unstable']
    
    
  
  @staticmethod
  def get_decay_constant(code):  
    if(code not in isotopes.jeffdata.keys()):
      return 0.0
    if(isotopes.jeffdata[code]['stable']):
      return 0.0
    return numpy.log(2) / isotopes.jeffdata[code]['half_life']
    
  
  @staticmethod
  def get_isotopes(element, nucleons=None):
    protons = isotopes.get_protons(element)
      
    s = []
    if(nucleons == None or nucleons == ''):  
      for k in isotopes.get_element_stable(protons):
        s.append({
               'protons': protons,
               'neutrons': isotopes.jeffdata[k]['neutrons'],
               'nucleons': isotopes.jeffdata[k]['nucleons'],
               'percentage': 100.0 * isotopes.jeffdata[k]['natural_abundance'],
               'mass': isotopes.jeffdata[k]['mass_amu'],
               })
    else:
      # If specific isotope selected, percentage is 100%
      k = 1000 * protons + int(nucleons)
      s.append({
               'protons': protons,
               'neutrons': isotopes.jeffdata[k]['neutrons'],
               'nucleons': isotopes.jeffdata[k]['nucleons'],
               'percentage': 100.0,
               'mass': isotopes.jeffdata[k]['mass_amu'],
               })
    return s
  
  
  @staticmethod
  def get_gammas(key):
    if(isotopes.is_stable(key)):
      return None
    if(key not in isotopes.gammas_array.keys()):
      return None
    return isotopes.gammas_array[key]

  
  
  @staticmethod
  def make_chain(key, l=0, out=[], bf=0.0, q=0.0):
    if(l == 0):   
      isotopes.chains_store = []
    out.append([l, key, bf, q])
    if(isotopes.jeffdata[key]['stable']):
      if(len(out) > 1):
        for i in range(len(out)-1,1,-1):
          if(out[i-1][0]>=out[i][0]):
            out.pop(out[i-1][0])
      isotopes.chains_store.append(copy.deepcopy(out))
    else:
      l = l + 1 
      for k in isotopes.jeffdata[key]['decay_modes'].keys():
        bf = isotopes.jeffdata[key]['decay_modes'][k][0]
        q = isotopes.jeffdata[key]['decay_modes'][k][2]
        isotopes.make_chain(k, l, out, bf, q)
      return out
      #[branching_factor, to_meta, qvalue]


  def chain_isotopes(key, out=None):
    if(key not in out):
      out.append(key)
    if(isotopes.jeffdata[key]['stable']):
      return out
    else:
      for k in isotopes.jeffdata[key]['decay_modes'].keys():
        isotopes.chain_isotopes(k, out)
      return out


  def is_stable(key):
    if(key in isotopes.jeffdata.keys()):
      return isotopes.jeffdata[key]['stable']
    return None
    

  ##########################################
  # DECAY EQUATIONS
  ##########################################

  @staticmethod
  def calculate_activity(t, l, b, w, n0):
    nt = numpy.zeros((len(n0),),)
    for m in range(0,len(n0)):
      if(l[m] > 0.0):
        nt[m] = isotopes.activity_unstable(t, l, b, w, n0, m)
      elif(l[m] == 0.0):
        nt[m] = isotopes.activity_stable(t, l, b, w, n0, m)
    return nt

  @staticmethod
  def activity_unstable(t, l, b, w, n0, m):
    s = 0.0
    for k in range(0, m+1):
      s = s + isotopes.r(k, m, b, l) * ( isotopes.f_unstable(t,k,m,l) * n0[k] + isotopes.g_unstable(t,k,m,l) * w[k])
    return s

  @staticmethod
  def activity_stable(t, l, b, w, n0, m):
    s = n0[m] + w[m] * t
    for k in range(0, m):
      s = s + isotopes.r(k, m, b, l) * (isotopes.f_stable(t,k,m,l) * n0[k] + isotopes.g_stable(t,k,m,l) * w[k])
    return s

  @staticmethod
  def r(k, m, b, l):
    if(k == m):
      return 1.0
    else:
      p = 1.0
      for i in range(k, m):
        p = p * (b[i] * l[i])
      return p

  @staticmethod
  def f_unstable(t,k,m,l):
    s = 0.0
    for i in range(k, m+1):
      p = 1.0
      for j in range(k, m+1):
        if(i != j):
          p = p * (1 / (l[i] - l[j]))
      s = s + numpy.exp(-1 * l[i] * t) * p
    s = (-1)**(m-k) * s
    return s

  @staticmethod
  def g_unstable(t,k,m,l):
    pa = 1.0
    for i in range(k,m+1):
      pa = pa * l[i]
    pa = 1.0 / pa
    s = 0.0
    for i in range(k, m+1):
      pb = 1.0
      for j in range(k, m+1):
        if(i != j):
          pb = pb * (1 / (l[i]-l[j]))
      s = s + (1/l[i]) * numpy.exp(-l[i]*t) * pb
    return pa + s * (-1)**(m-k+1) 


  @staticmethod
  def f_stable(t,k,m_in,l):
    m = m_in - 1

    p = 1.0
    for i in range(k, m+1):
      p = p * l[i]

    s = 0.0
    for i in range(k, m+1):
      r = l[i]
      for j in range(k, m+1):
        if(i != j):
          r = r * (l[i] - l[j])
      s = s + (1/r)*numpy.exp(-1*l[i]*t)
   
    return (1.0/p) + s * (-1.0)**(m-k+1)


  @staticmethod
  def g_stable(t,k,m_in,l):
    m = m_in - 1

    pa = 1.0
    for i in range(k,m+1):
      pa = pa * l[i]
    pa = 1.0 / pa

    sa = 0.0
    for i in range(k, m+1):
      pb = 1.0
      for j in range(k,m+1):
        if(j != i):
          pb = pb * l[j]
      sa = sa + pb
    pc = 1.0 
    for i in range(k, m+1):
      pc = pc * l[i]**2

    sb = 0.0
    for i in range(k, m+1):
      pd = 1.0
      for j in range(k, m+1):
        if(i != j):
          pd = pd * (1 / (l[i]-l[j]))
      sb = sb + (1/(l[i]**2)) * numpy.exp(-l[i]*t) * pd

    return pa * t + sa / pc + sb * (-1)**(m-k+1)  
      



  def activity(parent, t, idata, log_path=None):

    isotopes.chains_store = None
    
    if(log_path != None):
      fh = open(log_path, 'w')
      fh.write("=================================================================================================================\n")
      fh.write("ISOTOPE ACTIVITY CALCULATION \n")
      fh.write("=================================================================================================================\n")
      fh.write("\n")
      fh.write("Parent:    " + str(parent) + "\n")
      fh.write("Time:      " + str(t) + "\n")
      fh.write("\n")

    tally = {}   
    unique = isotopes.chain_isotopes(parent, [])   


    for k in unique:
      i_data = isotopes.isotope_data(k)      
      tally[k] = {
        'element': i_data['element'],
        'protons': i_data['protons'],
        'nucleons': i_data['nucleons'],
        'metastable': i_data['metastable'],
        'stable': i_data['stable'],
        'half_life': None,
        'decay_constant': 0.0,
        'n0': 0.0,
        'nend': 0.0,
        'w': 0.0,
      }
      if(not i_data['stable']):
        tally[k]['half_life'] = i_data['half_life']
        tally[k]['decay_constant'] = numpy.log(2) / i_data['half_life']
      
      
      if(k in idata.keys()):
        tally[k]['n0'] = idata[k]['n0']
        tally[k]['w'] = idata[k]['w']
        

    

    # Get Unique Isotopes
    if(log_path != None):
      fh.write("Start Tally\n")
      fh.write("----------------------------------------------------------------------------\n")  
      for k in tally.keys():
        fh.write(str(k) + "  " + tally[k]['element'] + "  " + str(tally[k]['protons']) + "  " + str(tally[k]['nucleons']))
        fh.write("  " + str(tally[k]['metastable']) + "  " + str(tally[k]['n0']) + "  " + str(tally[k]['w']))
        fh.write("  " + str(tally[k]['half_life']) + "  " + str(tally[k]['decay_constant']))
        fh.write("\n")
      fh.write("\n")    
    
    # Load decay chains

    isotopes.chains_store = []
    isotopes.make_chain(parent, 0, [])

    chains = copy.deepcopy(isotopes.chains_store)
    
    #for ch in chains:
    #  print(ch)    

    # Decay Chains
    if(log_path != None):
      fh.write("Decay Chains\n")
      fh.write("----------------------------------------------------------------------------\n")  

      for n in range(len(chains)):
        fh.write("Chain " + str(n+1) + "    ")  
        for i in range(len(chains[n])):
          if(i > 0):
            fh.write(" -> ")
          fh.write(str(chains[n][i][1])) 
        fh.write("\n")
      fh.write("\n")       

      
    
    if(log_path != None):
      fh.write("Decay Chains\n")
      fh.write("----------------------------------------------------------------------------\n")    
    
    
    set = []      
    for cn in range(len(chains)):
      if(log_path != None):
        fh.write("Chain " + str(cn+1) + "    \n")  
      chain = chains[cn]
      n0 = numpy.zeros((len(chain),),)
      w = numpy.zeros((len(chain),),)
      l = numpy.zeros((len(chain),),)
      b = numpy.zeros((len(chain)-1,),)
      
      for n in range(len(chain)):
        k = chain[n][1]
        n0[n] = tally[k]['n0']
        w[n] = tally[k]['w']
        l[n] = tally[k]['decay_constant']
        if(n > 0):
          b[n-1] = chain[n][2]
          
      nt = isotopes.calculate_activity(t, l, b, w, n0)      
      for n in range(len(chain)):
        k = chain[n][1]
        sk = '0'
        for m in range(n+1):
          sk = sk + str(chain[m][1])   
        prnt = ''
        if(sk not in set):        
          set.append(sk)
          tally[k]['nend'] = tally[k]['nend'] + nt[n]
          prnt = '***'
        if(log_path != None):
          fh.write(str(n) + "   " + str(chain[n][1]) + "  " + str(nt[n]) + "   " + prnt + "     " + "\n")  
       

    
    
    if(log_path != None):
      fh.write("\n")  
          
          
    # Get Unique Isotopes
    if(log_path != None):
      fh.write("End Tally\n")
      fh.write("----------------------------------------------------------------------------\n")  
      for k in tally.keys():
        fh.write(str(k) + "  " + tally[k]['element'] + "  " + str(tally[k]['protons']) + "  " + str(tally[k]['nucleons']))
        fh.write("  " + str(tally[k]['metastable']) + "  " + str(tally[k]['nend']))
        fh.write("\n")
      fh.write("\n")              
          
        
    if(log_path != None):
      fh.close()

    return tally

