import numpy 
import json
import zlib
import bz2
import pickle
import _pickle as cPickle
import os

###############################################
#
# Used to read TENDL to pickled files 
# and to return xs values from files
#
###############################################

class tendl:

  """

           2: [[0,0,0]],
           3: [[0,0,0]],
           4: [[0,1,1],1],
  """

  mt = {
           11: [[1,3,4],1,1,1002],
           16: [[0,2,2],1,1],
           17: [[0,3,3],1,1,1],
           22: [[2,3,5],1,2004],
           23: [[6,7,13],1,2004,2004,2004],
           24: [[2,4,6],1,1,2004],
           25: [[2,5,7],1,1,1,2004],
           28: [[1,1,2],1,1001],
           29: [[2,4,6],1,2004,2004],
           30: [[4,6,10],1,1,2004,2004],
           32: [[1,2,3],1,1002],
           33: [[1,3,4],1,1003],
           34: [[2,2,4],1,2003],
           35: [[5,6,11],1,1002,2004,2004],
           36: [[5,7,12],1,1003,2004,2004],
           37: [[0,4,4],1,1,1,1],
           41: [[1,2,3],1,1,1001],
           42: [[1,3,4],1,1,1,1001],
           44: [[2,1,3],1,1001,1001],
           45: [[3,3,6],1,1001,2004],
           102: [[0,0,0]],
           103: [[1,0,1],1001],
           104: [[1,1,2],1002],
           105: [[1,2,3],1003],
           106: [[2,1,3],2003],
           107: [[2,2,4],2004],
           108: [[4,4,8],2004,2004],
           109: [[6,6,12],2004,2004,2004],
           111: [[2,0,2],1001,1001],
           112: [[3,2,5],1001,2004],
           113: [[5,6,11],1003,2004,2004],
           114: [[5,5,10],1002,2004,2004],
           115: [[2,1,3],1001,1002],
           116: [[2,2,4],1001,1003],
           117: [[3,3,6],1002,2004],
           }
           
  residual = {}  
  emitted = {}   
  
  
###########################################################
#
#  READ TENDL FUNCTIONS
#
###########################################################

  @staticmethod
  def convert(dir_in, dir_out, projectile):
    
    if(projectile not in tendl.residual.keys()):
      tendl.residual[projectile] = {}
    if(projectile not in tendl.emitted.keys()):
      tendl.emitted[projectile] = {}
  
    # Make output and read through all files
    tendl.make_dir(dir_out)
    files = os.listdir(dir_in)
    for f in files:
      if('.tendl' in f):
        print(f)
        tendl.convert_file(dir_in, dir_out, f, projectile)
        

  @staticmethod
  def convert_file(dir_in, dir_out, file_name, projectile):
    f = {}
    projectile_protons, projectile_neutrons, projectile_nucleons = tendl.read_isotope_code(projectile)

    # Read into MF -> MT
    fh = open(dir_in + "/" + file_name, 'r')    
    for row in fh:
      mf = int(row[70:72])
      mt = int(row[72:75])
      mat = int(row[66:70])
      row_num = int(row[75:])
      
      if(mf == 1 and mt == 451 and row_num == 1):
        code = tendl.read_int(row[0:12])
        target_protons, target_neutrons, target_nucleons = tendl.read_isotope_code(code)
        t = int(1000 * target_protons + target_nucleons)
      if(mf not in f.keys()):
        f[mf] = {}
      if(mt not in f[mf].keys()):
        f[mf][mt] = [] 
      f[mf][mt].append(row[:-1])
    fh.close()
    
    # Create slot in dictionaries
    if(t not in tendl.residual[projectile].keys()):
      tendl.residual[projectile][t] = {}
    if(t not in tendl.emitted[projectile].keys()):
      tendl.emitted[projectile][t] = {}
  
    # Read XS  (MF=3)
    mf = 3
    
    # Loop through defined mt
    for mt in tendl.mt.keys():
      if(mt in f[mf].keys()):
        total_protons_lost = tendl.mt[mt][0][0]
        total_neutrons_lost = tendl.mt[mt][0][1]
        total_nucleons_lost = tendl.mt[mt][0][2]
        redisual_protons = target_protons + projectile_protons - total_protons_lost
        redisual_neutrons = target_neutrons + projectile_neutrons - total_neutrons_lost
        redisual_nucleons = target_nucleons + projectile_nucleons - total_nucleons_lost
        dp = tendl.read_block(f[mf][mt])
    
        # Residual
        r = int(1000 * redisual_protons + redisual_nucleons)
        if(r not in tendl.residual[projectile][t].keys()):
          tendl.residual[projectile][t][r] = []
        tendl.residual[projectile][t][r].append(dp) 

        # Emitted
        for e in range(1, len(tendl.mt[mt])):
          emitted = tendl.mt[mt][e]
          if(emitted not in tendl.emitted[projectile][t].keys()):
            tendl.emitted[projectile][t][emitted] = []
          tendl.emitted[projectile][t][emitted].append(dp)
        
  @staticmethod
  def read_block(block):
    line_counter = 0
    for line in block:
      line_counter = line_counter + 1
      mf = int(line[70:72])
      mt = int(line[72:75])
      mat = int(line[66:70])
      
      if(line_counter == 3):
        point_count = tendl.read_int(line[:12])
        data_points = []
        n = 0
      elif(line_counter > 3):
        l = []
        l.append(line[0:11])
        l.append(line[11:22])
        l.append(line[22:33])
        l.append(line[33:44])
        l.append(line[44:55])
        l.append(line[55:66]) 
        m = 0
        while(n<point_count and m<3):
          data_points.append([tendl.read_float(l[2*m]),tendl.read_float(l[2*m+1])])
          n = n + 1
          m = m + 1
    return data_points




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


###########################################################
#
#  DIR/LOAD/SAVE
#
###########################################################

  @staticmethod
  def make_dir(dir):
    try:
      if(not os.path.exists(dir) and dir.strip() != ''):
        os.mkdir(dir) 
        return True
      return False
    except:
      return False


  @staticmethod
  def psave(file_name, d):
    with bz2.BZ2File(file_name, 'w') as f: 
      cPickle.dump(d, f)


  @staticmethod
  def pload(file_name):
    data = bz2.BZ2File(file_name, 'rb')
    return cPickle.load(data)
    

  @staticmethod
  def save(dir_out):
    tendl.make_dir(dir_out)
    
    tendl.psave(dir_out + '/residual.pz', tendl.residual)
    tendl.psave(dir_out + '/emitted.pz', tendl.emitted)

  @staticmethod
  def load(dir_out):
    tendl.residual = tendl.pload(dir_out + '/residual.pz')
    tendl.emitted = tendl.pload(dir_out + '/emitted.pz')
   


###########################################################
#
#  XS FUNCTIONS
#
###########################################################

  
  @staticmethod
  def get_residual_list(projectile, target):
    r = []
    try:
      projectile = int(projectile)
      target = int(target)
    except:
      return r    
    if(projectile not in tendl.residual.keys()):
      return r
    if(target not in tendl.residual[projectile].keys()):
      return r
    for k in tendl.residual[projectile][target].keys():
      r.append(k)
    return r

  
  @staticmethod
  def get_emitted_list(projectile, target):
    e = []
    try:
      projectile = int(projectile)
      target = int(target)
    except:
      return e    
    if(projectile not in tendl.emitted.keys()):
      return e
    if(target not in tendl.emitted[projectile].keys()):
      return e
    for k in tendl.emitted[projectile][target].keys():
      e.append(k)
    return e


  @staticmethod
  def get_xs_residual(projectile, tn, rn, energy):  
    sigma = 0.0
    try:
      projectile = int(projectile)
      tn = int(tn)
      rn = int(rn)
      energy = float(energy)
    except:
      return sigma  
    if(projectile not in tendl.residual.keys()):
      return sigma  
    if(tn not in tendl.residual[projectile].keys()):
      return sigma 
    if(rn not in tendl.residual[projectile][tn].keys()):
      return sigma     
    for i in range(len(tendl.residual[projectile][tn][rn])):
      sigma = sigma + tendl.get_sigma_value(tendl.residual[projectile][tn][rn][i], energy)
    return sigma
  
  
  @staticmethod
  def get_xs_emitted(projectile, tn, en, energy):
    sigma = 0.0
    try:
      projectile = int(projectile)
      tn = int(tn)
      en = int(en)
      energy = float(energy)
    except:
      return sigma  
    if(projectile not in tendl.residual.keys()):
      return sigma  
    if(tn not in tendl.emitted[projectile].keys()):
      return sigma 
    if(en not in tendl.emitted[projectile][tn].keys()):
      return sigma     
    for i in range(len(tendl.emitted[projectile][tn][en])):
      sigma = sigma + tendl.get_sigma_value(tendl.emitted[projectile][tn][en][i], energy)
    return sigma

  @staticmethod
  def get_sigma_value(d, energy):
    if(len(d) == 0):
      return 0.0
    else:
      if(energy < d[0][0]):
        return 0.0
      if(energy > d[-1][0]):
        return 0.0
      for i in range(len(d)-1):
        if(energy >= d[i][0] and energy <= d[i+1][0]):
          return max(0.0, d[i][1] + ((energy-d[i][0])/(d[i+1][0] - d[i][0])) * (d[i+1][1] - d[i][1]))
          

###########################################################
#
#  TEST FUNCTIONS
#
###########################################################

  @staticmethod
  def load_from_tendl(dir=None):
    if(dir == None):
      dir = 'z'
    # Neutron      1
    # Proton    1001
    # Deuteron  1002
    #tendl.convert('test_fe', dir, 1001)
    tendl.convert('TENDL-p', dir, 1001)
    #tendl.convert('TENDL-n',dir, 1)
    #tendl.convert('TENDL-d',dir, 1002)
    tendl.save(dir)
    

  @staticmethod
  def test_use(dir=None):
    if(dir == None):
      dir = 'z'
    tendl.load(dir)
    print(tendl.residual.keys())
    print(tendl.residual[1001].keys())
    print(tendl.residual[1001][26058].keys())
    print(tendl.residual[1001][26058][26056])
    print()
    residual_list = tendl.get_residual_list(1001, 26058)
    print(residual_list)
    
    print()
    emitted_list = tendl.get_emitted_list(1001, 26058)
    print(emitted_list)
    
    print()
    print()
    print(tendl.get_xs_residual(1001, 26058, 26056, 36000000))
    print(tendl.get_xs_residual(1001, 26054, 27055, 36000000))

    residual_list = tendl.get_residual_list(1001, 26054)
    print()
    print()
    print(residual_list)
    print()



tendl.load_from_tendl('zfull')
#tendl.test_use('zfull')




