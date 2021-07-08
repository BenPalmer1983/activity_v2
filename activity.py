################################################################
#    Main Program
#
#
#
#
################################################################


#!/bin/python3
########################################################################
import os
import time
import datetime
import re
import sys
import shutil
import numpy
import json
import zlib
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import bz2
import copy
import pickle
import _pickle as cPickle

###########################################
#  CLASS
###########################################
class g:

  dirs = {
         'wd': 'wd',
         'isotopes': 'data',
         'xs': 'data',
         }
  
  sub_dirs = { 
         'results': 'results',
         }
  
  times = {
          'start' : 0.0,
          'end' : 0.0,
          'duration' : 0.0,
          }

  sims_input = {}
  sims = {}

  exyz = {}

  xs = {}

  tally = {}

###########################################
#  CLASS activit
###########################################
class activity:

  def run():
    
    log.log("Start")
    start_time = time.time()
    
# Make output directories
    std.make_dir('output')
    
# Load input file
    read_input.run()
    
# Start isotopes
    print("Loading isotopes...", end="")
    isotopes.load_data(g.dirs['isotopes'])
    print("complete.")
    
# Start tendl xs
    print("Loading xs data...", end="")
    log.log("Loading isotope tendl xs")
    tendl.load(g.dirs['xs'])
    log.log("Load complete")
    print("complete.")
    
# Load all exyz files
    print("Loading exyz data...", end="")
    exyz.load()
    print("complete.")
    
# Run Sim
    sim.run()
    
    print()
    print("Run Time: ", '{:7.3f}'.format(time.time() - start_time) + "s")
    print()
    
###########################################
#  CLASS st
###########################################
class std:

  @staticmethod
  def file_to_list(file_name, clean=False):
# Init variable
    file_data = []
# Read it in line by line
    fh = open(file_name, "r")
    for line in fh:
      if(clean):
        line = line.strip()
        if(line != ""):
          file_data.append(line)          
      else:
        file_data.append(line[0:-1])
# Return
    return file_data
    
  @staticmethod
  def split_fields(line, sep=" "):
    out = line.split(sep)
    key = out[0]
    value = out[1]
    value_out = ''    
    indata = False
    for char in value:
      if(indata and char != '"'):
        value_out = value_out + char
      elif(indata and char == '"'):
        indata = False
      elif(not indata and char == '"'):
        indata = True
    return key, value_out
    
  @staticmethod
  def one_space(line, sep=" "):
    out = ''   
    indata = 0
    last_char = None
    for char in line:
      if(indata == 1 and char != "'" and last_char != "\\"):
        out = out + char
      elif(indata == 1 and char == "'" and last_char != "\\"):
        out = out + char
        indata = 0
      elif(indata == 2 and char != '"' and last_char != "\\"):
        out = out + char
      elif(indata == 2 and char == '"' and last_char != "\\"):
        out = out + char
        indata = 0
      elif(indata == 0 and not (char == " " and last_char == " ")):
        out = out + char
      last_char = char
    return out   
    
  @staticmethod
  def to_fields(line, sep=" "):
    out = []
    temp = ''
    indata = 0
    last_char = None
    for char in line:
      if(indata == 1 and char != "'" and last_char != "\\"):
        temp = temp + char
      elif(indata == 1 and char == "'" and last_char != "\\"):
        temp = temp + char
        indata = 0
      elif(indata == 2 and char != '"' and last_char != "\\"):
        temp = temp + char
      elif(indata == 2 and char == '"' and last_char != "\\"):
        temp = temp + char
        indata = 0
      elif(indata == 0 and not (char == sep and last_char == sep)):
        if(char == sep):
          temp = temp.strip()
          if(temp != ""):
            out.append(temp)
            temp = ''
        else:
          temp = temp + char
    
    temp = temp.strip()
    if(temp != ""):
      out.append(temp)      
    return out    
    
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
  def copy(src, dest):  
    try:
      std.make_dir(dest)
      src_f = src.split("/")
      if(os.path.isdir(src)):
        shutil.copytree(src, dest + '/' + src_f[-1])      
      else:
        shutil.copyfile(src, dest + '/' + src_f[-1])
      return True
    except:
      return False
      
  @staticmethod
  def path(dir, file):  
    dir = dir.strip()
    file = file.strip()
    if(dir == ''):
      return file
    else:
      if(dir[-1] == '/'):
        return dir + file
      else:      
        return dir + '/' + file
    
  @staticmethod
  def remove_comments(content):
    data = ''
    i = 0
    for line in content:
      if(i > 0):
        data += '\n'
      data += line
      i = i + 1
    out = ''
    indata = 0
    incomment = 0
    for i in range(len(data)):
# Get char and next char
      char = data[i]
      next = None
      prev = None
      if(i < len(data)-1):
        next = data[i + 1]
      if(i > 0):
        prev = data[i - 1]
# If in '  '
      if(indata == 1 and char != "'" and last_char != "\\"):
        out = out + char
      elif(indata == 1 and char == "'" and last_char != "\\"):
        out = out + char
        indata = 0
# If in "  "
      elif(indata == 2 and char != '"' and last_char != "\\"):
        out = out + char
      elif(indata == 2 and char == '"' and last_char != "\\"):
        out = out + char
        indata = 0
      elif(indata == 0):
        if(incomment == 0 and char == "/" and next == "/"):
          incomment = 1
        elif(incomment == 1 and char == "\n"):
          incomment = 0
        if(incomment == 0 and char == "!"):
          incomment = 2
        elif(incomment == 2 and char == "\n"):
          incomment = 0
        if(incomment == 0 and char == "/" and next == "*"):
          incomment = 3
        elif(incomment == 3 and prev == "*" and char == "/"):
          incomment = 0
        elif(incomment == 0):
          out = out + char  
    return out.split("\n")    
    
# Remove comments from a block of data/text
  @staticmethod
  def remove_comments_data(data):
    out = ""
    n = 0
    inquotes = 0
    incomment = 0
    while n < len(data):
# Get char and next char
      char = data[n]
      next = None
      prev = None
      if(n < len(data)-1):
        next = data[n + 1]
      if(n > 0):
        prev = data[n - 1]
        
# If in '  '
      if(inquotes == 1 and char != "'" and last_char != "\\"):
        out = out + char
      elif(inquotes == 1 and char == "'" and last_char != "\\"):
        out = out + char
        inquotes = 0
# If in "  "
      elif(inquotes == 2 and char != '"' and last_char != "\\"):
        out = out + char
      elif(inquotes == 2 and char == '"' and last_char != "\\"):
        out = out + char
        inquotes = 0
# If not inside quotes
      elif(inquotes == 0):
# Comment on a line
        if(incomment == 0 and char == "/" and next == "/"):
          incomment = 1
        elif(incomment == 0 and char == "!"):
          incomment = 1
        elif(incomment == 0 and char == "#"):
          incomment = 1    
# Comment on line close
        elif(incomment == 1 and char == "\n"):
          incomment = 0
# Comment block
        elif(incomment == 0 and char == "/" and next == "*"):
          incomment = 3
        elif(incomment == 3 and prev == "*" and char == "/"):
          incomment = 0
        elif(incomment == 0):
          out = out + char  
# Increment counter
      n = n + 1
    return out        

# Single spaces, tabs to spaces
  @staticmethod
  def prep_data(content):
    out = []
    for line in content:
      line_new = std.prep_data_line(line)
      if(line_new != ''):
        out.append(line_new)
    return out  
      
  @staticmethod
  def prep_data_line(line): 
    temp = ''
    indata = 0
    last_char = None
    for char in line:
      if(char == '\t'):
        char = ' '
      if(indata == 1 and char != "'" and last_char != "\\"):
        temp = temp + char
      elif(indata == 1 and char == "'" and last_char != "\\"):
        temp = temp + char
        indata = 0
      elif(indata == 2 and char != '"' and last_char != "\\"):
        temp = temp + char
      elif(indata == 2 and char == '"' and last_char != "\\"):
        temp = temp + char
        indata = 0
      elif(indata == 0 and not (char == ' ' and last_char == ' ')):
        temp = temp + char       
      last_char = char  
    return temp.strip()    
    
  @staticmethod
  def remove_quotes(inp): 
    if(isinstance(inp, list)):    
      for i in range(len(inp)):
        inp[i] = std.remove_quotes(inp[i])        
      return inp
    else:
      inp = inp.strip()
      if(inp[0] == '"' and inp[-1] == '"'):
        return inp[1:-1]
      if(inp[0] == "'" and inp[-1] == "'"):
        return inp[1:-1]
      return inp
      
  @staticmethod
  def config_file_to_list(file_name):
# Init variable
    file_data = []
# Read it in line by line
    fh = open(file_name, "r")
    for line in fh:
      if(line.strip() != ""):
        line = line.strip()
        line = std.remove_comments(line)
        line = std.prep_data_line(line)
        fields = std.to_fields(line)
        file_data.append(fields)         
# Return
    file_data = std.remove_quotes(file_data)
    return file_data
    
  @staticmethod
  def get_dir(file_path):
    directory = ''
    read = False
    for i in range(len(file_path)):
      if(read):
        directory = file_path[-1-i] + directory
      if(file_path[-1-i] == "/"):
        read = True
    return directory
  
  @staticmethod
  def read_csv(filename, sep=","):
    data = []
    if(os.path.isfile(filename)):
# Read from file into memory
      fh = open(filename, 'r')
      file_data = ""
      for line in fh:
        file_data = file_data + line
      fh.close()
# Remove comments
      file_data = std.remove_comments_data(file_data)
# Read Data
      lines = file_data.split("\n")
      for line in lines:
        line = line.strip()
        if(line != ""):
          data.append(line.split(sep))  
    return data
     
  @staticmethod
  def read_csv_array(filename, sep=","):
    data = []
    if(os.path.isfile(filename)):
# Read from file into memory
      fh = open(filename, 'r')
      file_data = ""
      for line in fh:
        file_data = file_data + line.strip() + '\n'
      fh.close()
# Remove double spaces
      file_data = std.one_space(file_data)
# Remove comments
      file_data = std.remove_comments_data(file_data)
# Read Data
      lines = file_data.split("\n")
      for line in lines:
        line = line.strip()
        if(line != ""):
          data.append(line.split(sep))  
          
      lst = []
      for i in range(len(data)):
        row = []
        for j in range(len(data[0])):
          try:
            row.append(float(data[i][j]))
          except:
            pass
        lst.append(row)
        
      arr = numpy.zeros((len(lst),len(lst[0]),),)
      for i in range(len(lst)):
        for j in range(len(lst[0])):
          arr[i,j] = float(lst[i][j])
      return arr
    return None
    
  @staticmethod
  def write_csv(filename, arr, w=10):  
    fh = open(filename, 'w')
    for i in range(len(arr)):
      for j in range(len(arr[i])):
        fh.write(std.float_padded(arr[i,j],w) + " ")
      fh.write("\n")
    fh.close()
  
  @staticmethod
  def option(input):
    input = input.strip().upper()
    if(input[0:1] == "Y"):
      return True
    elif(input[0:2] == "ON"):
      return True
    elif(input[0:1] == "T"):
      return True
    else:
      return False
    
  @staticmethod
  def float_padded(inp, pad=7):
    out = float(inp)
    out = round(out, pad-3)
    out = str(out)  
    while(len(out)<pad):
      out = out + " "      
    return out[0:pad]
    
  @staticmethod
  def write_file_line(fh, title, title_pad, fields, field_pad):
    if(type(fields) == numpy.ndarray):
      t = fields
      fields = []
      for ti in t:
        fields.append(ti)    
    elif(type(fields) != list):
      fields = [fields]
    
    line = str(title)
    while(len(line)<title_pad):
      line = line + ' '
    for f in fields:
      f_str = str(f)
      while(len(f_str)<field_pad):
        f_str = f_str + ' '
      line = line + f_str + ' '
    line = line + '\n'
    fh.write(line)  
  
  @staticmethod
  def print_file_line(title, title_pad, fields, field_pad):
    if(type(fields) == numpy.ndarray):
      t = fields
      fields = []
      for ti in t:
        fields.append(ti)    
    elif(type(fields) != list):
      fields = [fields]
    
    line = str(title)
    while(len(line)<title_pad):
      line = line + ' '
    for f in fields:
      f_str = str(f)
      while(len(f_str)<field_pad):
        f_str = f_str + ' '
      line = line + f_str + ' '
    line = line + '\n'
    print(line,end='')  
    
  def mem_value(strin):
    num = '0123456789.'
    strin = strin.upper().strip()
    value = ''
    unit = ''
    for c in strin:
      if(c not in num):
        break
      else:
        value = value + c
    for c in strin:
      if(c not in num):
        unit = unit + c
     
    value = float(value)
    if(unit == 'B'):
      return value
    if(unit == 'KB'):
      return 1000 * value
    if(unit == 'MB'):
      return 1000000 * value
    if(unit == 'GB'):
      return 1000000000 * value
    
  @staticmethod
  def dict_to_str(d, pre=''):
    out = ''
    for k in sorted(d):
      if(type(k) == dict or type(k) == list):
        out = out + '\n' + std.dict_to_str(k, pre + '  ')      
      else:
        out = out + pre + str(k) + ': ' + str(d[k]) + '\n'
    return out
    
  @staticmethod
  def pad_right(inp, w=10):
    inp = str(inp)
    while(len(inp)<w):
      inp = inp + " "
    return inp
    
  @staticmethod
  def pad_left(inp, w=10):
    inp = str(inp)
    while(len(inp)<w):
      inp = " " + inp 
    return inp
     
###########################################
#  CLASS zfdic
###########################################
class zfdict:

  def save(file_path, dict):
    dat = json.dumps(xs)
    cdat = zlib.compress(dat.encode(), level=9)
    fh = open(file_path, 'wb')
    fh.write(cdat)
    fh.close()

  def load(file_path):
    fh = open(file_path, 'rb')
    cdat = ''.encode()
    for r in fh:
      cdat = cdat + r
    fh.close()
    return json.loads(zlib.decompress(cdat).decode())

###########################################
#  CLASS unit
###########################################
class units:
  
  @staticmethod
  def convert(conv_from, conv_to, value_in):
    try:
      value_in = float(value_in)
    except:
      return None
    conv_from = conv_from.upper()
    conv_to = conv_to.upper()

# LENGTH METERS
    length = {
    'M': 1.0,
    'CM': 100,
    'MM': 1E3,
    'UM': 1E6,
    'NM': 1E9,
    'ANG': 1E10,
    'BOHR': 1.89E10,
    }
    
# AREA METERS SQUARED
    area = {
    'M2': 1.0,
    'CM2': 1E4,
    'MM2': 1E6,
    'UM2': 1E12,
    'NM2': 1E18,
    'ANG2': 1E20,
    }
    
# VOLUME METERS CUBED
    volume = {
    'M2': 1.0,
    'CM2': 1E6,
    'MM2': 1E9,
    'UM2': 1E18,
    'NM2': 1E27,
    'ANG2': 1E30,
    }

# ENERGY J
    energy = {
    'J': 1.0,
    'EV': 6.2415E18,
    'RY': 4.5874E17,
    'KEV': 6.2415E15,
    'MEV': 6.2415E12,
    }

# FORCE N
    force = {
    'N': 1.0,
    'RY/BOHR': 2.4276e7,
    'EV/ANG':6.2414E8,    
    }
    
# VELOCITY
    velocity = {
    'M/S': 1.0,
    'MPH': 2.25,    
    }
    
# PRESSURE
    pressure = {
    'PA': 1.0,
    'GPA': 1.0E-9,    
    'BAR': 1.0E-5,    
    'ATMOSPHERE': 9.8692E-6,    
    'PSI': 1.45038E-4, 
    'KBAR': 1.0E-8,   
    'RY/BOHR3': 6.857E-14,   
    'EV/ANG3': 6.241E-12
    }
    
# CHARGE DENSITY (UNIT CHARGE PER VOLUME - ANG^3)
    charge_density = {
    'ANG-3': 1.0,
    'BOHR-3': 0.14812,    
    }

# TIME T
    time = {
    'S': 1.0,
    'MINUTE': 0.1666666666E-2,
    'HOUR': 2.7777777777E-4,
    }
    
# CURRENT
    current = {
    'A': 1.0,
    'MA': 1.0E3,
    'UA': 1.0E6,
    }
    
# DENSITY
    density = {
    'KGM3': 1.0,
    'GCM3': 1.0E-3,
    }
    
# TEMPERATURE
    
    unit_list = [length, area, volume, energy, force, velocity, pressure, charge_density, time, current, density]
    
    for l in unit_list:
      if(conv_from in l.keys() and conv_to in l.keys()):
        return round((l[conv_to] / l[conv_from]) * float(value_in),9)
  
"""  
  @staticmethod
  def convert(conv_from, conv_to, value_in):

    conv_from = conv_from.upper()
    conv_to = conv_to.upper()

# METERS
    length = {
    'M': 1.0,
    'CM': 100,
    'MM': 1E3,
    'UM': 1E6,
    'NM': 1E9,
    'ANG': 1E10,
    'BOHR': 1.89E10,
    }

# J
    energy = {
    'J': 1.0,
    'EV': 6.242E18,
    'RY': 4.5874E17,
    }

    if(conv_from in length.keys() and conv_to in length.keys()):
      return round((length[conv_to] / length[conv_from]) * float(value_in),9)

    if(conv_from in energy.keys() and conv_to in energy.keys()):
      return round((energy[conv_to] / energy[conv_from]) * float(value_in),9)
"""

###########################################
#  CLASS read_confi
###########################################
class read_config:
  
  @staticmethod
  def read_file(file_path):
  
# Input dictionary
    input = {}
  
# READ DATA
    d = []
    fh = open(file_path, 'r')
    for line in fh:
      line = line.strip()
      if(len(line) > 0 and line[0] != "#"):
        d.append(line)      
    fh.close()
    
# Count commands
    commands = {}
    for line in d:
      fields = read_config.split_by(line, ' ')
      c = fields[0].lower()
      if(c in commands.keys()):
        commands[c] = commands[c] + 1
      else:
        commands[c] = 1
        
# Prepare input dictionary
    for k in commands.keys():
      if(commands[k] == 1):
        input[k] = None
      else:
        input[k] = []
    
# Read Data into input
    for line in d:
      fields = read_config.split_by(line, ' ')
      fkey = fields[0].lower()
      
      fd_size = {}
      for i in range(1, len(fields)):
        f = fields[i]
        fs = f.split("=")
        fc = fs[0].lower()
        if(fc in fd_size.keys()):
          fd_size[fc] = fd_size[fc] + 1
        else:
          fd_size[fc] = 1
          
# Prepare dictionary
      fd = {} 
      for k in fd_size.keys():
        if(fd_size[k] == 1):
          fd[k] = None
        else:
          fd[k] = []        
        
      for i in range(1, len(fields)):
        f = fields[i]
        fs = f.split("=")     
        fc = fs[0].lower()        
        fs = read_config.split_by(fs[1], ',')         
        fs = read_config.store(fs)
        
        if(fd_size[fc] == 1):
          if(len(fs) == 1):
            fd[fc] = read_config.store(fs[0])
          else:
            fd[fc] = read_config.store(fs)
        else:
          if(len(fs) == 1):
            fd[fc].append(read_config.store(fs[0]))
          else:
            fd[fc].append(read_config.store(fs))
            
      if(commands[fkey] == 1):
        input[fkey] = fd
      else:
        input[fkey].append(fd)  

    return input
        
  @staticmethod  
  def split_by(line, sep=' ', ignore_double_sep=True):
    last_char = None
    in_quotes = 0
    fields = []
    temp_line = ""
    
    for char in line:
      if(char == "'" and in_quotes == 0 and last_char != "\\"):
        in_quotes = 1
      elif(char == "'" and in_quotes == 1 and last_char != "\\"):
        in_quotes = 0
      elif(char == '"' and in_quotes == 0 and last_char != "\\"):
        in_quotes = 2
      elif(char == '"' and in_quotes == 2 and last_char != "\\"):
        in_quotes = 0
      elif(in_quotes > 0):
        temp_line = temp_line + char
      elif(in_quotes == 0 and char != sep):
        temp_line = temp_line + char
      elif(char == sep and last_char == sep and ignore_double_sep):
        pass
      elif(char == sep):
        fields.append(temp_line)
        temp_line = "" 
    if(temp_line != ""):
      fields.append(temp_line)
    
    return fields
    
  @staticmethod
  def store(inp):  
    if(isinstance(inp, list)):
      for i in range(len(inp)):
        try:
          if('.' in inp[i]  or 'e' in inp[i]):
            inp[i] = float(inp[i])
          else:
            inp[i] = int(inp[i])
        except:
          pass
    else:
      try:
        if('.' in inp or 'e' in inp):
          inp = float(inp)
        else:
          inp = int(inp)
      except:
        pass
    return inp
      
###########################################
#  CLASS read_inpu
###########################################
class read_input:

  def run():
  
# Read input file
    if(len(sys.argv)>1):
      try:
        g.inp = read_config.read_file(sys.argv[1])
      except:
        main.end()

# Data directory
    g.dirs['isotopes'] = 'data'
    g.dirs['xs'] = 'data'
    
    try:
      g.dirs['isotopes'] = str(g.inp['data']['isotopes']).strip()
    except:
      pass
    try:
      g.dirs['xs'] = str(g.inp['data']['xs']).strip()
    except:
      pass
      
# Sim input
    read_input.sims()
  
  def sims(): 
    loop = True
    n = 1
    while(loop):
      k = 'sim' + str(n)
      if(k in g.inp.keys()): 
        read_input.sim(k)
      elif(n > 100 and k not in g.inp.keys()): 
        loop = False    
      n = n + 1   
      
  def sim(k): 
# SET DEFAULT
    g.sims_input[k] = {
                       'exyz': 'exyz.exyz',
                       'target_composition': 'FE,100',
                       'target_depth': 1.0,
                       'target_depth_unit': 'mm',
                       'target_density': 10000,
                       'target_density_unit': 'kgm3',
                       'beam_projectile': 'proton',
                       'beam_energy': 10,
                       'beam_energy_unit': 'MeV',
                       'beam_area': 100,
                       'beam_area_unit': 'mm2',
                       'beam_duration': 100,
                       'beam_duration_unit': 's',
                       'beam_current': 10,
                       'beam_current_unit': 'uA',
                       'end_time': 100000,
                       'end_time_unit': 's',
                      }
# Load data
    try:
      g.sims_input[k]['exyz'] = g.inp[k]['exyz']
    except:  
      pass
    try:
      g.sims_input[k]['target_composition'] = g.inp[k]['target_composition']
    except:  
      pass
    try:
      g.sims_input[k]['target_depth'] = float(g.inp[k]['target_depth'][0])
    except:  
      pass
    try:
      g.sims_input[k]['target_depth_unit'] = g.inp[k]['target_depth'][1]
    except:  
      pass
    try:
      g.sims_input[k]['target_density'] = float(g.inp[k]['target_density'][0])
    except:  
      pass
    try:
      g.sims_input[k]['target_density_unit'] = g.inp[k]['target_density'][1]
    except:  
      pass
    try:
      g.sims_input[k]['beam_projectile'] = g.inp[k]['beam_projectile']
    except:  
      pass
    try:
      g.sims_input[k]['beam_energy'] = float(g.inp[k]['beam_energy'][0])
    except:  
      pass
    try:
      g.sims_input[k]['beam_energy_unit'] = g.inp[k]['beam_energy'][1]
    except:  
      pass
    try:
      g.sims_input[k]['beam_area'] = g.inp[k]['beam_area'][0]
    except:  
      pass
    try:
      g.sims_input[k]['beam_area_unit'] = g.inp[k]['beam_area'][1]
    except:  
      pass
    try:
      g.sims_input[k]['beam_duration'] = g.inp[k]['beam_duration'][0]
    except:  
      pass
    try:
      g.sims_input[k]['beam_duration_unit'] = g.inp[ k]['beam_duration'][1]
    except:  
      pass
    try:
      g.sims_input[k]['beam_current'] = g.inp[k]['beam_current'][0]
    except:  
      pass
    try:
      g.sims_input[k]['beam_current_unit'] = g.inp[k]['beam_current'][1]
    except:  
      pass
    try:
      g.sims_input[k]['end_time'] = g.inp[k]['end_time'][0]
    except:  
      pass
    try:
      g.sims_input[k]['end_time_unit'] = g.inp[k]['end_time'][1]
    except:  
      pass
                      
###########################################
#  CLASS lo
###########################################
class log:

  f = False

  def log(line, end='\n'):   
    log.make()
    fh = open('activity.log', 'a') 
    lines = line.split("\n")
    for line in lines:
      fh.write(str("{:.3E}".format(time.time() - log.start_time)) + ' ###   ' + line + end) 
    fh.close()
  
  def hr(): 
    log.log('#############################################################################')
    
  def br(): 
    log.log('')
    
  def title(title, big=False): 
    log.log('')
    if(big):
      log.hr()
      log.hr()
    else:
      log.log('#############################################')
    titles = title.split("\n")
    for title in titles:
      log.log(title)
    if(big):
      log.hr()
      log.hr()
    else:
      log.log('#############################################')
    log.log('')

  def make():
    if(log.f == False):
      log.start_time = time.time()
      fh = open("activity.log", 'w')
      fh.close()
      log.f = True
      
###########################################
#  CLASS exy
###########################################
class exyz:

  def load():   
    for k in g.sims_input.keys():
      log.log("Load " + g.sims_input[k]['exyz'])
      exyz.load_file(g.sims_input[k]['exyz'])

  def load_file(file_name):
    if(file_name in g.exyz):
      return False
      
    fh = open(file_name, 'r')
    in_data = False
    
    temp = {}
    
    for line in fh:
      line = line.strip()
      if(line[0:7] == "0000001"):
        in_data = True
      if(in_data and line != ""):
        ion = int(line[0:7])
        if(ion not in temp.keys()):
          temp[ion] = []
        energy = float(line[8:18])
        x = float(line[19:30])
        y = float(line[31:42])
        z = float(line[43:54])
        temp[ion].append([energy,x,y,z])
    
    g.exyz[file_name] = {}
    for k in temp.keys():
      l = len(temp[k]) - 1
      temp_dr = []
      for i in range(len(temp[k]) - 1):
        e = 0.5 * (temp[k][i][0] + temp[k][i+1][0])
        dr = numpy.sqrt((temp[k][i][1] - temp[k][i+1][1])**2 + (temp[k][i][2] - temp[k][i+1][2])**2 + (temp[k][i][3] - temp[k][i+1][3])**2)
        if(dr > 0.0):
          temp_dr.append([e, dr, temp[k][i][0], temp[k][i+1][0], temp[k][i][1], temp[k][i+1][1]])
          
      g.exyz[file_name][k] = numpy.zeros((len(temp_dr), 6),)
      for i in range(len(temp_dr)):
        g.exyz[file_name][k][i,0] = temp_dr[i][0] * 1000.0   # Energy          Convert to eV
        g.exyz[file_name][k][i,1] = temp_dr[i][1] * 1.0E-10  # m dr
        g.exyz[file_name][k][i,2] = temp_dr[i][2] * 1000.0   # Start Energy    Convert to eV
        g.exyz[file_name][k][i,3] = temp_dr[i][3] * 1000.0   # End Energy      Convert to eV
        g.exyz[file_name][k][i,4] = temp_dr[i][4] * 1.0E-10  # m start depth
        g.exyz[file_name][k][i,5] = temp_dr[i][5] * 1.0E-10  # m end depth

    fh.close()

###########################################
#  CLASS srim_plo
###########################################
class srim_plot:

  def plot(filename, outdir, filename_end, depth_limit):
    
    d = {}
    d_len = {}
    d_pos = {}

    in_data = False
    fh = open(filename, 'r')
    for line in fh:
      if(in_data == False):
        if(line.strip() == ("------- ----------- ---------- ----------- ----------- -----------  ---------------")):
          in_data = True
      else:
        line = std.one_space(line.strip())
        f = line.split(" ")
        for n in range(len(f)):
          f[n] = str(f[n])
          if(f[n][-1] == "-"):
            f[n] = str(f[n][:-1])
        if(len(f)):
          x_depth = float(f[2])
          if(x_depth <= depth_limit):
            ion_number = int(f[0])
            if(ion_number not in d_len.keys()):
              d_len[ion_number] = 0
            d_len[ion_number] = d_len[ion_number] + 1 
    fh.close()

    for k in d_len.keys():
      d[k] = numpy.zeros((d_len[k], 5,),)

    in_data = False
    fh = open(filename, 'r')
    for line in fh:
      if(in_data == False):
        if(line.strip() == ("------- ----------- ---------- ----------- ----------- -----------  ---------------")):
          in_data = True
      else:
        line = std.one_space(line.strip())
        f = line.split(" ")
        for n in range(len(f)):
          f[n] = str(f[n])
          if(f[n][-1] == "-"):
            f[n] = str(f[n][:-1])
        if(len(f)):
          energy = float(f[1])
          x_depth = float(f[2])
          y = float(f[3])
          z = float(f[4])
          r = numpy.sqrt(x_depth**2 + y**2 + z**2)
          if(x_depth <= depth_limit):
            ion_number = int(f[0])
            if(ion_number not in d_pos.keys()):
              d_pos[ion_number] = 0
            d[ion_number][d_pos[ion_number], 0]  = energy
            d[ion_number][d_pos[ion_number], 1]  = x_depth
            d[ion_number][d_pos[ion_number], 2]  = y
            d[ion_number][d_pos[ion_number], 3]  = z
            d[ion_number][d_pos[ion_number], 4]  = r
            d_pos[ion_number] = d_pos[ion_number] + 1 
    fh.close()

    de = numpy.zeros(len(d.keys()),)
    n = 0
    for k in d.keys():
      de[n] = max(d[k][:,0]) - min(d[k][:,0])
      n = n + 1

# the histogram of the data
    plt.figure(figsize=(12,8))
    n, bins, patches = plt.hist(de, 10, density=True, facecolor='g', alpha=0.75)
    plt.xlabel('Energy Lost/KeV')
    plt.ylabel('Fraction of Ions')
    plt.title('Beam Energy Lost in Sample')
    plt.grid(True)
    plt.savefig(outdir + 'energy_lost' + filename_end + '.eps', format='eps')
    plt.close('all') 

    plt.figure(figsize=(12,8))
    plt.title('Ion Trajectory')
    plt.rc('font', family='serif')
    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlabel('x (depth)/Ang')
    ax.set_ylabel('y/ang')
    ax.set_zlabel('z/ang')
    ax.ticklabel_format(style='sci')
    for k in d_len.keys():
      x = d[k][:,1] 
      y = d[k][:,2] 
      z = d[k][:,3] 
      ax.plot(x, y, z)
    plt.savefig(outdir + 'trajectory_3d' + filename_end + '.eps', format='eps')
    plt.close('all') 

    plt.figure(figsize=(12,8))
    plt.title('Ion Energy In Target')
    plt.rc('font', family='serif')
    plt.rc('xtick', labelsize=8)
    plt.rc('ytick', labelsize=8)
    plt.xlabel('x (depth)/Ang')
    plt.ylabel('Energy/KeV')
    for k in d_len.keys():
      x = d[k][:,1] 
      y = d[k][:,0] 
      plt.plot(x,y)
    plt.savefig(outdir + 'energy_depth' + filename_end + '.eps', format='eps')
    plt.close('all') 
     
###########################################
#  CLASS si
###########################################
class sim:

  def run():
    log.log("Run Simulation")
  
# Prepare Sims
    for k in g.sims_input.keys():
      log.log("Prep " + str(k))
      sim.prep(k)
      
# Run Sims
    for k in g.sims_input.keys():
      log.log("Run " + str(k))
      sim.run_sim(k)

  def prep(k):
    print()
  
# Set up sim dictionary
    g.sims[k] = {
                'exyz': g.sims_input[k]['exyz'],
                'beam': None,
                'target': None,
                'tally': None,
                'saturation': None,
                'rr': None,
                'inbeam': None,
                'end_time': None,
                'ilist': None,
                'dir': None,
                'tn_rn': [],
                'tn_en': [],
                'time_size': 200,
                'time': None,
                'amount': None,
                'activity': None,
                'total_activity': None,
                'eob_activity': None,
                'eos_activity': None,
                'eob_gammas': None,
                'eos_gammas': None,
                'gamma_dose': None,                
                }

# Make sim directory
    g.sims[k]['dir'] = 'output/' + k  
    std.make_dir(g.sims[k]['dir'])

# Make subdirs
    std.make_dir(g.sims[k]['dir']  + '/data_files')
    std.make_dir(g.sims[k]['dir']  + '/plots')
    std.make_dir(g.sims[k]['dir']  + '/plots/ions')
    std.make_dir(g.sims[k]['dir']  + '/plots/isotope_amount')
    std.make_dir(g.sims[k]['dir']  + '/plots/isotope_activity')
    std.make_dir(g.sims[k]['dir']  + '/plots/total_activity')
    std.make_dir(g.sims[k]['dir']  + '/plots/gamma_lines')
    std.make_dir(g.sims[k]['dir']  + '/plots/gamma_dose')

# Beam
    g.sims[k]['beam'] = beam()
    g.sims[k]['beam'].set_duration(g.sims_input[k]['beam_duration'], g.sims_input[k]['beam_duration_unit'])
    g.sims[k]['beam'].set_area(g.sims_input[k]['beam_area'], g.sims_input[k]['beam_area_unit'])
    g.sims[k]['beam'].set_current(g.sims_input[k]['beam_current'], g.sims_input[k]['beam_current_unit'])
    g.sims[k]['beam'].set_energy(g.sims_input[k]['beam_energy'], g.sims_input[k]['beam_energy_unit'])
    g.sims[k]['beam'].set_projectile(g.sims_input[k]['beam_projectile'])
    g.sims[k]['beam'].set()
    g.sims[k]['beam'].display()
    
# Target
    g.sims[k]['target'] = target()
    g.sims[k]['target'].set_composition(g.sims_input[k]['target_composition'])
    g.sims[k]['target'].set_depth(g.sims_input[k]['target_depth'], g.sims_input[k]['target_depth_unit'])
    g.sims[k]['target'].set_density(g.sims_input[k]['target_density'], g.sims_input[k]['target_density_unit'])
    g.sims[k]['target'].calc_nd()
    g.sims[k]['target'].display()

# End time
    try: 
      end_time = units.convert(g.sims_input[k]['end_time_units'], 's', g.sims_input[k]['end_time'])
    except:
      end_time = g.sims[k]['beam'].get_duration()
    g.sims[k]['end_time'] = g.sims_input[k]['end_time']
    if(g.sims[k]['end_time'] - g.sims[k]['beam'].get_duration() < g.sims[k]['end_time']):
      g.sims[k]['end_time'] = g.sims[k]['end_time'] + g.sims[k]['beam'].get_duration()
      print("Adjusted sim end time to", g.sims[k]['end_time'])
      print()
      time.sleep(1.0)
    
    print("Time")
    print("======================")
    print("End of Simulation: ", end_time)
    print()

# Get isotope list
    g.sims[k]['ilist'] = g.sims[k]['target'].get_isotope_list()

# Set up tally and reaction rate dictionaries
###################################################
    
    g.sims[k]['tally'] = {}
    g.sims[k]['tally_beam_end'] = {}
    g.sims[k]['tally_sim_end'] = {}
    g.sims[k]['rr'] = {}
    
    beam_area = g.sims[k]['beam'].get_area()
    projectile = g.sims[k]['beam'].get_projectile_code()
    target_depth = g.sims[k]['target'].get_depth()
    v = target_depth * beam_area
    
# Add target isotopes into tally, create rr entry
    for tn in g.sims[k]['ilist']:
      if(tn not in g.sims[k]['tally'].keys()):
        g.sims[k]['tally'][tn] = 0.0
      if(tn not in g.sims[k]['rr'].keys()):
        g.sims[k]['rr'][tn] = 0.0
      g.sims[k]['tally'][tn] = g.sims[k]['tally'][tn] + v * g.sims[k]['target'].get_isotope_number_density(tn)
      
# Load residuals to tally, create rr entry
    for tn in g.sims[k]['ilist']:
      residual_list = tendl.get_residual_list(projectile, tn)  
      for rn in residual_list:
        if(rn != 0 and rn not in g.sims[k]['tally'].keys()):
          g.sims[k]['tally'][rn] = 0.0
        if(rn != 0 and rn not in g.sims[k]['rr'].keys()):
          g.sims[k]['rr'][rn] = 0.0
                
# Load emitted to tally, create rr entry
    for tn in g.sims[k]['ilist']:
      emitted_list = tendl.get_emitted_list(projectile, tn)  
      for en in emitted_list:
        if(en != 0 and en not in g.sims[k]['tally'].keys()):
          g.sims[k]['tally'][en] = 0.0  
        if(en != 0 and en not in g.sims[k]['rr'].keys()):
          g.sims[k]['rr'][en] = 0.0  
      
# Add decay isotopes
    parent_keys = []
    for kn in g.sims[k]['tally'].keys():
      parent_keys.append(kn)
    for kn in parent_keys:
      if(not isotopes.is_stable(kn)):
        unique = isotopes.chain_isotopes(kn, [])  
        for un in unique:
          if(un not in g.sims[k]['tally'].keys()):
            g.sims[k]['tally'][un] = 0.0
    
    print()
    print("Starting Tally")
    print("===================") 
    for kn in g.sims[k]['tally'].keys():
      print(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally'][kn], 18))
    print()

    log.title("Starting Tally")
    for kn in g.sims[k]['tally'].keys():
      log.log(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally'][kn], 18))
    log.hr()
    
    fh = open(g.sims[k]['dir'] + '/data_files/starting_tally.txt', 'w')
    for kn in g.sims[k]['tally'].keys():
      fh.write(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally'][kn], 18) + '\n')
    fh.close()

    """    
    std.make_dir(sim.rd + '/activity_end_of_sim')
    std.make_dir(sim.rd + '/activity_in_beam')
    std.make_dir(sim.rd + '/amount_end_of_sim')
    std.make_dir(sim.rd + '/amount_in_beam')
    std.make_dir(sim.rd + '/xs_plots')
    std.make_dir(sim.rd + '/gammas')
    std.make_dir(sim.rd + '/xs_data')
    std.make_dir(sim.rd + '/saturation_activities')
    std.make_dir(sim.rd + '/tally')
    std.make_dir(sim.rd + '/ion_energy')
    std.make_dir(sim.rd + '/target')
    std.make_dir(sim.rd + '/radioactive_isotopes')
    std.make_dir(sim.rd + '/gamma_dose')
# Load XS
    """

  def run_sim(k):
    
    print()
    print("Run Sim")
    print("===================") 
    print()

    sim.exit_energies(k)
    sim.target_residual_emitted(k)
    sim.output_number_density(k)
    sim.residual_reaction_rates(k)
    sim.emitted_reaction_rates(k)
    sim.saturation_times(k)
    sim.eob_tally(k)
    sim.eos_tally(k)
    sim.activity_plots(k)
    sim.gammas(k)
    sim.dose(k)

  def exit_energies(k):

    print("Plot Ion Energy Lost") 
    log.title("Plot Ion Energy Lost")     
      
    target_depth = g.sims[k]['target'].get_depth()

# Find exit energies
    d_energy = numpy.zeros((len(g.exyz[g.sims[k]['exyz']]),),)
    nn = 0
    min_energy = None
    max_energy = None
    for ion in g.exyz[g.sims[k]['exyz']].keys():
      start_energy = g.exyz[g.sims[k]['exyz']][ion][0,2]
      energy = g.exyz[g.sims[k]['exyz']][ion][0,2]  
      for n in range(len(g.exyz[g.sims[k]['exyz']][ion])): 
        if(g.exyz[g.sims[k]['exyz']][ion][n,4] > target_depth):
          break
        else:
          energy = g.exyz[g.sims[k]['exyz']][ion][n,0]
          if(max_energy == None or energy > max_energy):
            max_energy = energy
          if(min_energy == None or energy < min_energy):
            min_energy = energy
      d_energy[nn] = (start_energy - energy)
      nn = nn + 1
   
    plt.figure(figsize=(12,8))
    n, bins, patches = plt.hist(d_energy, 20, density=True, facecolor='g', alpha=0.75)  
    plt.xlabel('Energy Lost In Target (eV)')
    plt.ylabel('')
    plt.title('Ion Energy Lost In Target')
    plt.grid(True)
    plt.savefig(g.sims[k]['dir']  + '/plots/ions/' + 'ion_energy_lost.eps', format='eps')
    plt.close('all') 

# Plot trajectory data
    srim_plot.plot(g.sims[k]['exyz'], g.sims[k]['dir']  + '/plots/ions/', '_full_depth', 1.0e9)
    srim_plot.plot(g.sims[k]['exyz'], g.sims[k]['dir']  + '/plots/ions/', '_in_target', g.sims[k]['target'].get_depth_ang())

  def target_residual_emitted(k):
    projectile = g.sims[k]['beam'].get_projectile_code()

# Make target-residual and target-emitted lists
    g.sims[k]['tn_rn'] = []
    g.sims[k]['tn_en'] = []
    for tn in g.sims[k]['ilist']:    
      residual_list = tendl.get_residual_list(projectile, tn)  
      emitted_list = tendl.get_emitted_list(projectile, tn)        
      for rn in residual_list:
        if(rn != 0):
          g.sims[k]['tn_rn'].append([tn,rn])
      for en in emitted_list:
        if(en != 0):
          g.sims[k]['tn_en'].append([tn,en])
          
  def output_number_density(k):
    print()
    print("Number Density")  
    print("===================")      
    log.title("Number Density")  
    for tn in g.sims[k]['ilist']:  
      print(std.pad_right(isotopes.get_readable(tn), 10) + "   " + str(g.sims[k]['target'].get_isotope_number_density(tn)))
      log.log(std.pad_right(isotopes.get_readable(tn), 10) + "   " + str(g.sims[k]['target'].get_isotope_number_density(tn)))
    print()

  def residual_reaction_rates(k):
    exyz_file = g.sims[k]['exyz']
    target_depth = g.sims[k]['target'].get_depth()
    projectile = g.sims[k]['beam'].get_projectile_code()
    flux = g.sims[k]['beam'].get_flux()

    print("Calculate residual reaction rates")  
    log.title("Calculate residual reaction rates")  
    
# Loop through each target-residual permutation
    fh = open(g.sims[k]['dir'] + '/data_files/reaction_rates_residual.txt', 'w')
    for i in g.sims[k]['tn_rn']:
      tn = i[0]
      rn = i[1]
      
# Calculate reaction cross section per ion
      sigma_dr = 0.0
      
# Loop over all ions
      for ion in g.exyz[exyz_file].keys():
        for n in range(len(g.exyz[exyz_file][ion])):           
          dr = g.exyz[g.sims[k]['exyz']][ion][n,1]
          if(g.exyz[g.sims[k]['exyz']][ion][n,4] > target_depth):
            break
          else:
            f = 1.0
            if(g.exyz[g.sims[k]['exyz']][ion][n,5] > target_depth):
              f = (target_depth - g.exyz[exyz_file][ion][n,4]) / (g.exyz[exyz_file][ion][n,5] - g.exyz[exyz_file][ion][n,4])
            energy = g.exyz[exyz_file][ion][n,0]

            sigma = tendl.get_xs_residual(projectile, tn, rn, energy)
            sigma_dr = sigma_dr + sigma * f * dr
            
# cross section per ion for this thickness
      sigma_dr = sigma_dr / len(g.exyz[g.sims[k]['exyz']])  
      
      if(sigma_dr > 0.0):
# target number density
        tn_nd = g.sims[k]['target'].get_isotope_number_density(tn)
        
# Reaction rate (convert from barns to sq metre)
        rr = sigma_dr * flux * tn_nd * 1.0e-28

# Subtract from target, add to residual
        g.sims[k]['rr'][tn] = g.sims[k]['rr'][tn] - rr
        g.sims[k]['rr'][rn] = g.sims[k]['rr'][rn] + rr
        
# Log
        log.log(std.pad_right(isotopes.get_readable(tn), 10) + " --> " + std.pad_right(isotopes.get_readable(rn), 10) + "   " + std.pad_right(rr, 20))  
        fh.write(std.pad_right(isotopes.get_readable(tn), 10) + " --> " + std.pad_right(isotopes.get_readable(rn), 10) + "   " + std.pad_right(rr, 20) + '\n')
    log.br()    
    fh.close()

  def emitted_reaction_rates(k):
    exyz_file = g.sims[k]['exyz']
    target_depth = g.sims[k]['target'].get_depth()
    projectile = g.sims[k]['beam'].get_projectile_code()
    flux = g.sims[k]['beam'].get_flux()

    print("Calculate emitted reaction rates")  
    log.title("Calculate emitted reaction rates")  
    
# Loop through each target-emitted permutation
    fh = open(g.sims[k]['dir'] + '/data_files/reaction_rates_emitted.txt', 'w')
    for i in g.sims[k]['tn_en']:
      tn = i[0]
      en = i[1]
      
# Calculate reaction cross section per ion
      sigma_dr = 0.0
      
# Loop over all ions
      for ion in g.exyz[exyz_file].keys():
        for n in range(len(g.exyz[exyz_file][ion])):           
          dr = g.exyz[exyz_file][ion][n,1]
          if(g.exyz[exyz_file][ion][n,4] > target_depth):
            break
          else:
            f = 1.0
            if(g.exyz[exyz_file][ion][n,5] > target_depth):
              f = (target_depth - g.exyz[exyz_file][ion][n,4]) / (g.exyz[exyz_file][ion][n,5] - g.exyz[exyz_file][ion][n,4])
            energy = g.exyz[exyz_file][ion][n,0]

            sigma = tendl.get_xs_emitted(projectile, tn, en, energy)
            sigma_dr = sigma_dr + sigma * f * dr
            
# cross section per ion for this thickness
      sigma_dr = sigma_dr / len(g.exyz[exyz_file])  
      
      if(sigma_dr > 0.0):
# target number density
        tn_nd = g.sims[k]['target'].get_isotope_number_density(tn)
        
# Reaction rate (convert from barns to sq metre)
        rr = sigma_dr * flux * tn_nd * 1.0e-28

# Subtract from target, add to residual
        g.sims[k]['rr'][en] = g.sims[k]['rr'][en] + rr     
        
# Log
        log.log(std.pad_right(isotopes.get_readable(tn), 10) + " --> " + std.pad_right(isotopes.get_readable(en), 10) + "   " + std.pad_right(rr, 20))  
        fh.write(std.pad_right(isotopes.get_readable(tn), 10) + " --> " + std.pad_right(isotopes.get_readable(en), 10) + "   " + std.pad_right(rr, 20) + '\n')
    log.br()  
    fh.close()

  def saturation_times(k):    
    
    print()
    print("Saturation Times")
    print("===================")       
    
    log.title("Saturation Times") 
    log.log("Time where saturation is 95%")
    fh = open(g.sims[k]['dir'] + '/data_files/saturation_times.txt', 'w')
    for key in g.sims[k]['rr'].keys():
      if(g.sims[k]['rr'][key] != 0.0 and not isotopes.is_stable(key)): 
        l = isotopes.get_decay_constant(key)
        t = numpy.log(0.05) / (-1.0 * l)
        print(std.pad_right(isotopes.get_readable(key),10) + "  " + std.pad_right(t, 18))
        log.log(std.pad_right(isotopes.get_readable(key),10) + "  " + std.pad_right(t, 18))
        fh.write(std.pad_right(isotopes.get_readable(key),10) + "  " + std.pad_right(t, 18) + "\n")
    log.br()
    print()
    fh.close() 
        
  def eob_tally(k):
    beam_duration = g.sims[k]['beam'].get_duration()
    exyz_file = g.sims[k]['exyz']
    target_depth = g.sims[k]['target'].get_depth()
    projectile = g.sims[k]['beam'].get_projectile_code()
    flux = g.sims[k]['beam'].get_flux()

    print("End of Beam Tally")

    t = beam_duration
    g.sims[k]['tally_beam_end'] = {}
    for key in g.sims[k]['rr'].keys():
      if(key not in g.sims[k]['tally_beam_end'].keys()):
        g.sims[k]['tally_beam_end'][key] = 0.0      
      if(isotopes.is_stable(key)):
        g.sims[k]['tally_beam_end'][key] = g.sims[k]['tally'][key] + t * g.sims[k]['rr'][key]
      else:
        if(g.sims[k]['tally'][key] > 0.0 or g.sims[k]['rr'][key] > 0.0):
          idata = {}
          idata[key] = {'w': g.sims[k]['rr'][key], 'n0': g.sims[k]['tally'][key]}
          decay_tally = isotopes.activity(key, t, idata)
          for dkey in decay_tally:
            if(dkey not in g.sims[k]['tally_beam_end'].keys()):
              g.sims[k]['tally_beam_end'][dkey] = 0.0
            g.sims[k]['tally_beam_end'][dkey] = g.sims[k]['tally_beam_end'][dkey] + decay_tally[dkey]['nend']

    fh = open(g.sims[k]['dir'] + '/data_files/end_of_beam_tally.txt', 'w')
    for kn in g.sims[k]['tally_beam_end'].keys():
      fh.write(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally_beam_end'][kn], 18) + '\n')
    fh.close()

  def eos_tally(k):
    beam_duration = g.sims[k]['beam'].get_duration()
    exyz_file = g.sims[k]['exyz']
    target_depth = g.sims[k]['target'].get_depth()
    projectile = g.sims[k]['beam'].get_projectile_code()
    flux = g.sims[k]['beam'].get_flux()

    print("End of Sim Tally")

    t = g.sims[k]['end_time'] - beam_duration
    g.sims[k]['tally_sim_end'] = {}
    for key in g.sims[k]['tally_beam_end'].keys():
      if(key not in g.sims[k]['tally_sim_end'].keys()):
        g.sims[k]['tally_sim_end'][key] = 0.0      
      if(isotopes.is_stable(key)):
        g.sims[k]['tally_sim_end'][key] = g.sims[k]['tally_beam_end'][key]
      else:
        if(g.sims[k]['tally_beam_end'][key] > 0.0 ):
          idata = {}
          idata[key] = {'w': 0.0, 'n0': g.sims[k]['tally_beam_end'][key]}
          decay_tally = isotopes.activity(key, t, idata)
          for dkey in decay_tally:
            if(dkey not in g.sims[k]['tally_sim_end'].keys()):
              g.sims[k]['tally_sim_end'][dkey] = 0.0
            g.sims[k]['tally_sim_end'][dkey] = g.sims[k]['tally_sim_end'][dkey] + decay_tally[dkey]['nend']   

    fh = open(g.sims[k]['dir'] + '/data_files/end_of_sim_tally.txt', 'w')
    for kn in g.sims[k]['tally_sim_end'].keys():
      fh.write(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally_sim_end'][kn], 18) + '\n')
    fh.close()

  def activity_plots(k):
    beam_duration = g.sims[k]['beam'].get_duration()

    time_inbeam = numpy.linspace(0.0, beam_duration, 100) 
    time_outofbeam = numpy.linspace(beam_duration, g.sims[k]['end_time'], 101) 
    g.sims[k]['time'] = numpy.zeros((200),)
    g.sims[k]['time'][:100] = time_inbeam[:]
    g.sims[k]['time'][100:] = time_outofbeam[1:]

    g.sims[k]['activity'] = {}
    g.sims[k]['amount'] = {}
    g.sims[k]['total_activity'] = numpy.zeros((200),)

# Stable isotopes - In Beam
    for key in g.sims[k]['tally'].keys():  
      if(isotopes.is_stable(key) and key in g.sims[k]['rr'].keys()):
        if(key not in g.sims[k]['amount'].keys()):
          g.sims[k]['amount'][key] = numpy.zeros((200),)  
        for n in range(0,100):
          g.sims[k]['amount'][key][n] = g.sims[k]['tally'][key] + g.sims[k]['time'][n] * g.sims[k]['rr'][key]

# Unstable isotopes - In Beam
    for key in g.sims[k]['tally'].keys():  
      if(not isotopes.is_stable(key) and key in g.sims[k]['rr'].keys()):
        if(g.sims[k]['rr'][key] > 0.0):
          for n in range(0,100): 
            idata = {}
            idata[key] = {'w': g.sims[k]['rr'][key], 'n0': g.sims[k]['tally'][key]}
            decay_tally = isotopes.activity(key, g.sims[k]['time'][n] , idata)
            for dkey in decay_tally:
              if(dkey not in g.sims[k]['amount'].keys()):
                g.sims[k]['amount'][dkey] = numpy.zeros((200),)  
              g.sims[k]['amount'][dkey][n] = g.sims[k]['amount'][dkey][n] + decay_tally[dkey]['nend']
    
# Stable isotopes - Out Of Beam
    for key in g.sims[k]['amount'].keys():  
      if(isotopes.is_stable(key) and key in g.sims[k]['rr'].keys()):
        if(key not in g.sims[k]['amount'].keys()):
          g.sims[k]['amount'][key] = numpy.zeros((200),)  
        for n in range(100,200):
          g.sims[k]['amount'][key][n] = g.sims[k]['amount'][key][99]

# Unstable isotopes - Out Of Beam
    for key in g.sims[k]['amount'].keys():  
      if(not isotopes.is_stable(key)):
        n_end = g.sims[k]['amount'][key][99]
        if(n_end > 0.0):
          for n in range(100,200):
            idata = {}
            idata[key] = {'w': 0.0, 'n0': n_end}
            decay_tally = isotopes.activity(key, g.sims[k]['time'][n] - g.sims[k]['time'][99], idata)
            for dkey in decay_tally:
              if(dkey not in g.sims[k]['amount'].keys()):
                g.sims[k]['amount'][dkey] = numpy.zeros((200),)   
              g.sims[k]['amount'][dkey][n] = g.sims[k]['amount'][dkey][n] + decay_tally[dkey]['nend']
   
# Calculate activity
    g.sims[k]['total_activity'][:] = 0.0
    for key in g.sims[k]['amount'].keys(): 
      if(key not in g.sims[k]['activity'].keys()):
        g.sims[k]['activity'][key] = numpy.zeros((200),) 
      if(not isotopes.is_stable(key)): 
        l = isotopes.get_decay_constant(key)
        g.sims[k]['activity'][key][:] = l * g.sims[k]['amount'][key][:]
        g.sims[k]['total_activity'][:] = g.sims[k]['total_activity'][:] + g.sims[k]['activity'][key][:]

    for key in g.sims[k]['amount'].keys():     
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Amount of ' + str(isotopes.get_readable(key)) )
      plt.xlabel('Time (s)')
      plt.ylabel('Atom Count')
      plt.plot(g.sims[k]['time'][:], g.sims[k]['amount'][key][:])
      plt.savefig(g.sims[k]['dir']  + '/plots/isotope_amount/' + str(isotopes.get_readable(key)) + '.eps', format='eps')
      plt.close('all') 

      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Amount of ' + str(isotopes.get_readable(key)) + ' (During Irradiation)')
      plt.xlabel('Time (s)')
      plt.ylabel('Atom Count')
      plt.plot(g.sims[k]['time'][:100], g.sims[k]['amount'][key][:100])
      plt.savefig(g.sims[k]['dir']  + '/plots/isotope_amount/' + str(isotopes.get_readable(key)) + '_inbeam.eps', format='eps')
      plt.close('all') 

      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Amount of ' + str(isotopes.get_readable(key)) + ' (After Irradiation)')
      plt.xlabel('Time (s)')
      plt.ylabel('Atom Count')
      plt.plot(g.sims[k]['time'][99:], g.sims[k]['amount'][key][99:])
      plt.savefig(g.sims[k]['dir']  + '/plots/isotope_amount/' + str(isotopes.get_readable(key)) + '_outofbeam.eps', format='eps')
      plt.close('all') 

    for key in g.sims[k]['activity'].keys(): 
      if(not isotopes.is_stable(key)): 
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('Activity of ' + str(isotopes.get_readable(key))  )
        plt.xlabel('Time (s)')
        plt.ylabel('Activity (Bq)')
        plt.plot(g.sims[k]['time'][:], g.sims[k]['activity'][key][:])
        plt.savefig(g.sims[k]['dir']  + '/plots/isotope_activity/' + str(isotopes.get_readable(key)) + '.eps', format='eps')
        plt.close('all') 

        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('Activity of ' + str(isotopes.get_readable(key)) + ' (During Irradiation)')
        plt.xlabel('Time (s)')
        plt.ylabel('Activity (Bq)')
        plt.plot(g.sims[k]['time'][:100], g.sims[k]['activity'][key][:100])
        plt.savefig(g.sims[k]['dir']  + '/plots/isotope_activity/' + str(isotopes.get_readable(key)) + '_inbeam.eps', format='eps')
        plt.close('all') 
        
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('Activity of ' + str(isotopes.get_readable(key)) + ' (After Irradiation)')
        plt.xlabel('Time (s)')
        plt.ylabel('Activity (Bq)')
        plt.plot(g.sims[k]['time'][99:], g.sims[k]['activity'][key][99:])
        plt.savefig(g.sims[k]['dir']  + '/plots/isotope_activity/' + str(isotopes.get_readable(key)) + '_outofbeam.eps', format='eps')
        plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.plot(g.sims[k]['time'][:], g.sims[k]['total_activity'][:])
    plt.savefig(g.sims[k]['dir']  + '/plots/total_activity/total_activity.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity (During Irradiation)')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.plot(g.sims[k]['time'][:100], g.sims[k]['total_activity'][:100])
    plt.savefig(g.sims[k]['dir']  + '/plots/total_activity/total_activity_inbeam.eps', format='eps')
    plt.close('all') 
        
    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity (After Irradiation)')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.plot(g.sims[k]['time'][99:], g.sims[k]['total_activity'][99:])
    plt.savefig(g.sims[k]['dir']  + '/plots/total_activity/total_activity_outofbeam.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(18,12))    
    plt.title('Isotope Activity')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')    
    for key in g.sims[k]['activity'].keys(): 
      if(not isotopes.is_stable(key)): 
        plt.plot(g.sims[k]['time'][:], g.sims[k]['activity'][key][:], label=str(isotopes.get_readable(key)))
    plt.legend()
    plt.savefig(g.sims[k]['dir']  + '/plots/total_activity/all_isotopes.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(18,12))    
    plt.title('Isotope Activity')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')    
    for key in g.sims[k]['activity'].keys(): 
      if(not isotopes.is_stable(key)): 
        plt.plot(g.sims[k]['time'][:100], g.sims[k]['activity'][key][:100], label=str(isotopes.get_readable(key)))
    plt.legend()
    plt.savefig(g.sims[k]['dir']  + '/plots/total_activity/all_isotopes_inbeam.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(18,12))    
    plt.title('Isotope Activity')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')    
    for key in g.sims[k]['activity'].keys(): 
      if(not isotopes.is_stable(key)): 
        plt.plot(g.sims[k]['time'][:99], g.sims[k]['activity'][key][:99], label=str(isotopes.get_readable(key)))
    plt.legend()
    plt.savefig(g.sims[k]['dir']  + '/plots/total_activity/all_isotopes_outofbeam.eps', format='eps')
    plt.close('all') 

    g.sims[k]['eob_activity'] = g.sims[k]['total_activity'][99]
    g.sims[k]['eos_activity'] = g.sims[k]['total_activity'][199]

  def gammas(k):

    n = 0
    for key in g.sims[k]['activity'].keys(): 
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['activity'][key][99]
        if(isotope_activity != 0.0):
          dn = 0
          try:
            gn = isotopes.get_gammas(key)
            dn = len(gn)
          except:
            pass
          n = n + dn
          
    g.sims[k]['eob_gammas'] = numpy.zeros((n, 2),)
    g.sims[k]['eos_gammas'] = numpy.zeros((n, 2),)

    n = 0
    for key in g.sims[k]['activity'].keys(): 
      if(not isotopes.is_stable(key)):
        eob_ia = g.sims[k]['activity'][key][99]
        eos_ia = g.sims[k]['activity'][key][199]
        if(eob_ia != 0.0 or eos_ia != 0.0):
          dn = 0
          try:
            gn = isotopes.get_gammas(key)
            dn = len(gn)
          except:
            pass
          if(dn > 0):
            g.sims[k]['eob_gammas'][n:n+len(gn), 0] = gn[:,0]            
            g.sims[k]['eob_gammas'][n:n+len(gn), 1] = eob_ia * gn[:,1]
            g.sims[k]['eos_gammas'][n:n+len(gn), 0] = gn[:,0]            
            g.sims[k]['eos_gammas'][n:n+len(gn), 1] = eos_ia * gn[:,1]
          n = n + dn

# Plot Gammas
    if(len(g.sims[k]['eob_gammas']) > 0):
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Predicted Gamma Lines')
      plt.xlabel('Energy (eV)')
      plt.ylabel('Activity (Bq)')
      plt.stem(g.sims[k]['eob_gammas'][:,0], g.sims[k]['eob_gammas'][:,1])
      plt.savefig(g.sims[k]['dir'] + '/plots/gamma_lines/' + 'gamma_lines_eob.eps', format='eps')
      plt.close('all') 
      std.write_csv(g.sims[k]['dir'] + '/data_files/gamma_lines_eob.dat', g.sims[k]['eob_gammas'], w=14)

    if(len(g.sims[k]['eos_gammas']) > 0):
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Predicted Gamma Lines')
      plt.xlabel('Energy (eV)')
      plt.ylabel('Activity (Bq)')
      plt.stem(g.sims[k]['eos_gammas'][:,0], g.sims[k]['eos_gammas'][:,1])
      plt.savefig(g.sims[k]['dir'] + '/plots/gamma_lines/' + 'gamma_lines_eos.eps', format='eps')
      plt.close('all') 
      std.write_csv(g.sims[k]['dir'] + '/data_files/gamma_lines_eos.dat', g.sims[k]['eos_gammas'], w=14)

  def dose(k):
    
    g.sims[k]['gamma_dose'] = numpy.zeros((g.sims[k]['time_size'], 5),)

    for n in range(g.sims[k]['time_size']):
      gamma_ev = 0.0
      for key in g.sims[k]['activity'].keys(): 
        if(not isotopes.is_stable(key)):
          ia = g.sims[k]['activity'][key][n]
          if(ia != 0.0):
            try:
              gn = isotopes.get_gammas(key)
              gamma_ev = gamma_ev + ia * sum(gn[:,0] * gn[:,1])
            except:
              pass
      g.sims[k]['gamma_dose'][n,0] = gamma_ev

    g.sims[k]['gamma_dose'][:,1] = 1.60218E-19 * g.sims[k]['gamma_dose'][:,0]
    g.sims[k]['gamma_dose'][:,2] = g.sims[k]['gamma_dose'][:,1] / (12.57 * 80)
    g.sims[k]['gamma_dose'][:,3] = (g.sims[k]['gamma_dose'][:,1] / (12.57 * 80)) * 3600
    g.sims[k]['gamma_dose'][:,4] = (g.sims[k]['gamma_dose'][:,3] / 1.140771128E-04) * 100

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (eV/s)')
    plt.plot(g.sims[k]['time'][:], g.sims[k]['gamma_dose'][:,0])
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_power_ev.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (J/s)')
    plt.plot(g.sims[k]['time'][:], g.sims[k]['gamma_dose'][:,1])
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_power_j.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('Dose (Gy)')
    plt.plot(g.sims[k]['time'][:], g.sims[k]['gamma_dose'][:,2], label="Dose")
    if(max(g.sims[k]['gamma_dose'][:,2]) > 0.00000064):
      plt.axhline(y=0.00000064, color='r', linestyle='dotted', label='Industry worker')
    if(max(g.sims[k]['gamma_dose'][:,2]) > 0.000000032):
      plt.axhline(y=0.000000032, color='b', linestyle='dotted', label='Public worker')
    plt.legend()
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_dose_gy.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('Dose (Gy/Hr)')
    plt.plot(g.sims[k]['time'][:], g.sims[k]['gamma_dose'][:,3], label="Dose")
    if(max(g.sims[k]['gamma_dose'][:,3]) > 2.28E-03):
      plt.axhline(y=2.28E-03, color='r', linestyle='dotted', label='Industry worker')
    if(max(g.sims[k]['gamma_dose'][:,3]) > 1.14E-04):
      plt.axhline(y=1.14E-04, color='b', linestyle='dotted', label='Public worker')
    plt.legend()
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_dose_gy_per_hour.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('% of annual dose per hour')
    plt.plot(g.sims[k]['time'][:], g.sims[k]['gamma_dose'][:,4], label="Dose")
    if(max(g.sims[k]['gamma_dose'][:,4]) > 2000.0):
      plt.axhline(y=2000.0, color='r', linestyle='dotted', label='Industry worker')
    if(max(g.sims[k]['gamma_dose'][:,4]) > 100.0):
      plt.axhline(y=100.0, color='b', linestyle='dotted', label='Public worker')
    plt.legend()
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_percentage_of_annual_dose_per_hour.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('% of annual dose per hour')
    plt.plot(g.sims[k]['time'][:99], g.sims[k]['gamma_dose'][:99,4])
    if(max(g.sims[k]['gamma_dose'][:99,4]) > 2000.0):
      plt.axhline(y=2000.0, color='r', linestyle='dotted', label='Industry worker')
    if(max(g.sims[k]['gamma_dose'][:99,4]) > 100.0):
      plt.axhline(y=100.0, color='b', linestyle='dotted', label='Public worker')
    plt.legend()
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_percentage_of_annual_dose_per_hour_inbeam.eps', format='eps')
    plt.close('all') 

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Gamma Dose')
    plt.xlabel('Time (s)')
    plt.ylabel('% of annual dose per hour')
    plt.plot(g.sims[k]['time'][100:], g.sims[k]['gamma_dose'][100:,4])
    if(max(g.sims[k]['gamma_dose'][100:,4]) > 2000.0):
      plt.axhline(y=2000.0, color='r', linestyle='dotted', label='Industry worker')
    if(max(g.sims[k]['gamma_dose'][100:,4]) > 100.0):
      plt.axhline(y=100.0, color='b', linestyle='dotted', label='Public worker')
    plt.legend()
    plt.savefig(g.sims[k]['dir'] + '/plots/gamma_dose/' + 'gamma_percentage_of_annual_dose_per_hour_outofbeam.eps', format='eps')
    plt.close('all') 
    
    fh = open(g.sims[k]['dir']  + '/data_files/gamma_dose.dat', 'w')

    activity_total = g.sims[k]['total_activity'][99]
    gamma_ev = g.sims[k]['gamma_dose'][99,0]
    gamma_J = g.sims[k]['gamma_dose'][99,1]
    gamma_dose = g.sims[k]['gamma_dose'][99,2]
    gamma_dose_hr = g.sims[k]['gamma_dose'][99,3]
    gamma_dose_p = g.sims[k]['gamma_dose'][99,4]

    print('Gamma Dose - Beam End')
    print('===================================================')
    print()

    print("Activity/Bq                    ", activity_total)
    print("Power eV/s                     ", gamma_ev)
    print("Power J/s                      ", gamma_J)
    print("Dose Gy/s                      ", gamma_dose)
    print("Dose Gy/hr                     ", gamma_dose_hr)
    print("Percentage of annual dose/hr   ", gamma_dose_p, " (public limit)")
    print()

    fh.write('Gamma Dose - Beam End\n')
    fh.write('===================================================\n')
    fh.write('Activity/Bq                    ' + str(activity_total) + '\n')
    fh.write('Power eV/s                     ' + str(gamma_ev) + '\n')
    fh.write('Power J/s                      ' + str(gamma_J) + '\n')
    fh.write('Dose Gy/s                      ' + str(gamma_dose) + '\n')
    fh.write('Dose Gy/hr                     ' + str(gamma_dose_hr) + '\n')
    fh.write('Percentage of annual dose/hr   ' + str(gamma_dose_p) + '\n')
    fh.write('\n')
    fh.write('\n')

    log.br()
    log.log('Gamma Dose - Beam End')
    log.log('Activity/Bq                    ' + str(activity_total))
    log.log('Power eV/s                     ' + str(gamma_ev))
    log.log('Power J/s                      ' + str(gamma_J))
    log.log('Dose Gy/s                      ' + str(gamma_dose))
    log.log('Dose Gy/hr                     ' + str(gamma_dose_hr))
    log.log('Percentage of annual dose/hr   ' + str(gamma_dose_p))
    log.br()

    activity_total = g.sims[k]['total_activity'][199]
    gamma_ev = g.sims[k]['gamma_dose'][199,0]
    gamma_J = g.sims[k]['gamma_dose'][199,1]
    gamma_dose = g.sims[k]['gamma_dose'][199,2]
    gamma_dose_hr = g.sims[k]['gamma_dose'][199,3]
    gamma_dose_p = g.sims[k]['gamma_dose'][199,4]

    print('Gamma Dose - Sim End')
    print('===================================================')
    print()
    print("Activity/Bq                    ", activity_total)
    print("Energy eV/s                    ", gamma_ev)
    print("Energy J/s                     ", gamma_J)
    print("Dose Gy                        ", gamma_dose)
    print("Dose Gy/hr                     ", gamma_dose_hr)
    print("Percentage of annual dose/hr   ", gamma_dose_p)
    print()
    print()

    fh.write('Gamma Dose - Sim End\n')
    fh.write('===================================================\n')
    fh.write('Activity/Bq                    ' + str(activity_total) + '\n')
    fh.write('Power eV/s                     ' + str(gamma_ev) + '\n')
    fh.write('Power J/s                      ' + str(gamma_J) + '\n')
    fh.write('Dose Gy/s                      ' + str(gamma_dose) + '\n')
    fh.write('Dose Gy/hr                     ' + str(gamma_dose_hr) + '\n')
    fh.write('Percentage of annual dose/hr   ' + str(gamma_dose_p) + '\n')
    fh.write('\n')
    fh.write('\n')

    log.br()
    log.log('Gamma Dose - Sim End')
    log.log('Activity/Bq                    ' + str(activity_total))
    log.log('Power eV/s                     ' + str(gamma_ev))
    log.log('Power J/s                      ' + str(gamma_J))
    log.log('Dose Gy/s                      ' + str(gamma_dose))
    log.log('Dose Gy/hr                     ' + str(gamma_dose_hr))
    log.log('Percentage of annual dose/hr   ' + str(gamma_dose_p))
    log.br()

    print("Absorbed Dose Calculations")
    print('===================================================')
    print('Absorbed dose assumptions:')
    print('1. radiation from point, emitted isotropically')   
    print('2. 80Kg human')   
    print('3. 1m from point source')   
    print('4. 1m squared surface area')   
    print('5. all energy absorbed')   
    print()
    print()

    print("Dose Limits")
    print('===================================================')
    print("employees 18+             20 millisieverts/year")
    print("trainees 18+              6 millisieverts/year")
    print("public and under 18s      1 millisievert/year")
    print("public and under 18s      1.140771128E-04 millisieverts/hour")
    print("")
    print("Dose averaged over area of skin not exceeding 1cm2")
    print("Source: http://www.hse.gov.uk/radiation/ionising/doses/")
    print()
    print()
 
    fh.write('Absorbed Dose Calculations\n')
    fh.write('===================================================\n')
    fh.write('Absorbed dose assumptions:\n')
    fh.write('1. radiation from point, emitted isotropically\n')
    fh.write('2. 80Kg human\n')
    fh.write('3. 1m from point source\n')
    fh.write('4. 1m squared surface area\n')
    fh.write('5. all energy absorbed\n')
    fh.write('\n')
    fh.write('\n')

    fh.write('Dose Limits\n')
    fh.write('===================================================\n')
    fh.write('employees 18+             20 millisieverts/year\n')
    fh.write('trainees 18+              6 millisieverts/year\n')
    fh.write('public and under 18s      1 millisievert/year\n')
    fh.write('public and under 18s      1.140771128E-04 millisieverts/hour\n')
    fh.write('\n')
    fh.write('Dose averaged over area of skin not exceeding 1cm2\n')
    fh.write('Source: http://www.hse.gov.uk/radiation/ionising/doses/\n')
    fh.write('\n')
    fh.write('\n')

    fh.close()

  def old():

    sim.rd = 'output/' + k 

    log.title("Run Sim", True)
    
# Get data
    target_depth = g.sims[k]['target'].get_depth()
    ilist = g.sims[k]['target'].get_isotope_list()
    exyz_file = g.sims[k]['exyz']    
    projectile = g.sims[k]['beam'].get_projectile_code()
    
    flux = g.sims[k]['beam'].get_flux()
    beam_duration = g.sims[k]['beam'].get_duration()
    end_time = g.sims[k]['end_time']
    
# Output XD Data
######################
     
    print()     
    print("Ion Min/Max energies") 
    print("===================")  
    print("Max ion energy: ", max_energy)
    print("Min ion energy: ", min_energy)
    print()
              
# Loop through each target-residual permutation
    for i in tn_rn:
      tn = i[0]
      rn = i[1]    
      
      xs_temp = numpy.zeros((51,2,),)
      xs_temp[:,0] = numpy.linspace(min_energy, max_energy, 51) 
      abs_sigma = 0.0
      for n in range(len(xs_temp[:,0])):
        sigma = tendl.get_xs_residual(projectile, tn, rn, energy)
        xs_temp[n,1] = tendl.get_xs_residual(projectile, tn, rn, xs_temp[n,0])
        abs_sigma = abs_sigma + sigma**2
        
      if(abs_sigma > 0.0):
        file_path = sim.rd + '/xs_data/' + 'xs_' + str(isotopes.get_readable(tn)) + '_' + str(isotopes.get_readable(rn))
        std.write_csv(file_path + '.dat', xs_temp, w=14)
    
        file_path = sim.rd + '/xs_plots/' + 'xs_' + str(isotopes.get_readable(tn)) + '_' + str(isotopes.get_readable(rn))
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('XS Target-Reaction vs Energy ' + isotopes.get_readable(tn) + ' --> ' + isotopes.get_readable(rn))
        plt.xlabel('Energy (eV)')
        plt.ylabel('XS barns (Barns)')
        plt.grid(True)
        plt.plot(xs_temp[:,0], xs_temp[:,1])
        plt.savefig(file_path + '.eps', format='eps')
        plt.close('all') 
    
# Loop through each target-emitted permutation
    for i in tn_en:
      tn = i[0]
      en = i[1]    
      
      xs_temp = numpy.zeros((51,2,),)
      xs_temp[:,0] = numpy.linspace(min_energy, max_energy, 51) 
      abs_sigma = 0.0
      for n in range(len(xs_temp[:,0])):
        sigma = tendl.get_xs_residual(projectile, tn, en, energy)
        xs_temp[n,1] = tendl.get_xs_residual(projectile, tn, en, xs_temp[n,0])
        abs_sigma = abs_sigma + sigma**2
        
      if(abs_sigma > 0.0):
        file_path = sim.rd + '/xs_data/' + 'xs_' + str(isotopes.get_readable(tn)) + '_' + str(isotopes.get_readable(en))
        std.write_csv(file_path + '.dat', xs_temp, w=14)
    
        file_path = sim.rd + '/xs_plots/' + 'xs_' + str(isotopes.get_readable(tn)) + '_' + str(isotopes.get_readable(en))
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('XS Target-Emitted vs Energy ' + isotopes.get_readable(tn) + ' --> ' + isotopes.get_readable(en))
        plt.xlabel('Energy (eV)')
        plt.ylabel('XS barns (Barns)')
        plt.grid(True)
        plt.plot(xs_temp[:,0], xs_temp[:,1])
        plt.savefig(file_path + '.eps', format='eps')
        plt.close('all')     
    
    fh = open(sim.rd + '/target/number_density.txt', 'w')
    for tn in ilist:  
      fh.write(std.pad_right(isotopes.get_readable(tn), 10) + "   " + str(g.sims[k]['target'].get_isotope_number_density(tn)))
    fh.close()    
    
#
# Emitted
#
    
    print()
    print("Reaction Rates")
    print("===================")     
    for n in g.sims[k]['rr'].keys():
      if(g.sims[k]['rr'][n] != 0.0):
        print(n, g.sims[k]['rr'][n])
    print()
    
    g.sims[k]['saturation'] = {}
    for key in g.sims[k]['rr'].keys():
      if(g.sims[k]['rr'][key] != 0.0 and not isotopes.is_stable(key)): 
        rr = g.sims[k]['rr'][key]
        l = isotopes.get_decay_constant(key)
        g.sims[k]['saturation'][key] = numpy.zeros((100, 2,),)
        t_end = numpy.log(0.01) / (-1.0 * l)
        
        g.sims[k]['saturation'][key][:,0] = numpy.linspace(0.0, t_end, 100)
        for n in range(100):
          t = g.sims[k]['saturation'][key][n,0] 
          g.sims[k]['saturation'][key][n,1] = rr * (1 - numpy.exp(-1.0 * l * t))
     
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('Saturation In Beam')
        plt.xlabel('Time (s)')
        plt.ylabel('Activity (Bq)')
        plt.plot(g.sims[k]['saturation'][key][:,0], g.sims[k]['saturation'][key][:,1])
        plt.savefig(sim.rd + '/saturation_activities/' + 'saturation_' + str(isotopes.get_readable(key)) + '.eps', format='eps')
        plt.close('all') 

#
# Decay
#

# Beam End Tally
#########################
    
    for key in g.sims[k]['tally_beam_end'].keys():  
      if(g.sims[k]['tally_beam_end'][key] > 0.0):  
        print(std.pad_right(key, 10) + "  ", end="")
        print(std.pad_right(isotopes.get_readable(key), 10) + "  ", end="")
        print(std.pad_right(g.sims[k]['tally_beam_end'][key], 25), end="")
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_beam_end'][key]
        print(std.pad_right(isotope_activity, 25))
    print()     
    
    log.title("End of Beam Tally")  
    for key in g.sims[k]['tally_beam_end'].keys():
      isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_beam_end'][key]
      log.log(std.pad_right(key, 10) + "  " + std.pad_right(isotopes.get_readable(key), 10) + "  " + std.pad_right(g.sims[k]['tally_beam_end'][key], 25) + std.pad_right(isotope_activity, 25))
    log.br()
    
    fh = open(sim.rd + '/tally/end_of_beam_tally.txt', 'w')
    for kn in g.sims[k]['tally_beam_end'].keys():
      fh.write(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally_beam_end'][kn], 18) + '\n')
    fh.close()
    
# Prepare arrays to store data
    steps = 101
    g.sims[k]['inbeam'] = {}
    for key in g.sims[k]['rr'].keys():
      g.sims[k]['inbeam'][key] = numpy.zeros((steps,3,),)
      g.sims[k]['inbeam'][key][:,0] = numpy.linspace(0.0, beam_duration, steps) 

    for key in g.sims[k]['rr'].keys():
      for time_step in range(steps):
        t = g.sims[k]['inbeam'][key][time_step,0]
        if(isotopes.is_stable(key)):
          g.sims[k]['inbeam'][key][time_step,1] = g.sims[k]['tally'][key] + t * g.sims[k]['rr'][key]
        else:
          idata = {}
          idata[key] = {'w': g.sims[k]['rr'][key], 'n0': g.sims[k]['tally'][key]}
#print(t, key)
          decay_tally = isotopes.activity(key, t, idata)
          for dkey in decay_tally:
            if(dkey not in g.sims[k]['inbeam'].keys()):
              g.sims[k]['inbeam'][dkey] = numpy.zeros((steps,3,),)
              g.sims[k]['inbeam'][dkey][:,0] = numpy.linspace(0.0, beam_duration, steps) 
            g.sims[k]['inbeam'][dkey][time_step,1] = g.sims[k]['inbeam'][dkey][time_step,1] + decay_tally[dkey]['nend']
            g.sims[k]['inbeam'][dkey][time_step,2] = isotopes.get_decay_constant(dkey) * g.sims[k]['inbeam'][dkey][time_step,1]
    
    total_activity = numpy.zeros((101,2,),)
    total_activity[:,0] = numpy.linspace(0.0, beam_duration, steps) 
    for key in g.sims[k]['inbeam'].keys():
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Amount During Irradiation of ' + isotopes.get_readable(key))
      plt.xlabel('Time (s)')
      plt.ylabel('Amount (atoms)')
      plt.plot(g.sims[k]['inbeam'][key][:,0], g.sims[k]['inbeam'][key][:,1])
      plt.savefig(sim.rd + '/amount_in_beam/' + str(isotopes.get_readable(key)) + '.eps', format='eps')
      plt.close('all') 
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Activity During Irradiation of  ' + isotopes.get_readable(key))
      plt.xlabel('Time (s)')
      plt.ylabel('Activity (Bq)')
      plt.plot(g.sims[k]['inbeam'][key][:,0], g.sims[k]['inbeam'][key][:,2])
      plt.savefig(sim.rd + '/activity_in_beam/' + str(isotopes.get_readable(key)) + '.eps', format='eps')
      plt.close('all') 
      
      total_activity[:,0] = g.sims[k]['inbeam'][key][:,0]     

# Total Activity
      total_activity[:,1] = total_activity[:,1] + g.sims[k]['inbeam'][key][:,2]

    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity During Irradiation')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.plot(total_activity[:,0], total_activity[:,1])
    plt.savefig(sim.rd + '/activity_in_beam/000___total.eps', format='eps')
    plt.close('all') 
    
# Sim End Tally
#########################

    t = g.sims[k]['end_time'] - beam_duration
    g.sims[k]['tally_sim_end'] = {}
    for key in g.sims[k]['tally_beam_end'].keys():
      if(key not in g.sims[k]['tally_sim_end'].keys()):
        g.sims[k]['tally_sim_end'][key] = 0.0      
      if(isotopes.is_stable(key)):
        g.sims[k]['tally_sim_end'][key] = g.sims[k]['tally_beam_end'][key]
      else:
        if(g.sims[k]['tally_beam_end'][key] > 0.0 ):
          idata = {}
          idata[key] = {'w': 0.0, 'n0': g.sims[k]['tally_beam_end'][key]}
          decay_tally = isotopes.activity(key, t, idata)
          for dkey in decay_tally:
            if(dkey not in g.sims[k]['tally_sim_end'].keys()):
              g.sims[k]['tally_sim_end'][dkey] = 0.0
            g.sims[k]['tally_sim_end'][dkey] = g.sims[k]['tally_sim_end'][dkey] + decay_tally[dkey]['nend']   
    
    print("End of Sim")
    print("===================")     
    for key in g.sims[k]['tally_sim_end'].keys():
      if(g.sims[k]['tally_sim_end'][key] > 0.0):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_sim_end'][key]
        print(std.pad_right(key, 10) + "  ", end="")
        print(std.pad_right(isotopes.get_readable(key), 10) + "  ", end="")
        print(std.pad_right(g.sims[k]['tally_sim_end'][key], 25), end="")
        print(std.pad_right(isotope_activity, 25))
    print() 
    
    log.title("End of Sim Tally")  
    for key in g.sims[k]['tally_sim_end'].keys():
      isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_sim_end'][key]
      log.log(std.pad_right(key, 10) + "  " + std.pad_right(isotopes.get_readable(key), 10) + "  " + std.pad_right(g.sims[k]['tally_sim_end'][key], 25) + std.pad_right(isotope_activity, 25))
    log.br()
    
    fh = open(sim.rd + '/tally/end_of_sim_tally.txt', 'w')
    for kn in g.sims[k]['tally_sim_end'].keys():
      fh.write(std.pad_right(kn, 10) + "  " + std.pad_right(isotopes.get_readable(kn), 10) + "  " + std.pad_right(g.sims[k]['tally_sim_end'][kn], 18) + '\n')
    fh.close()
    
# Prepare arrays to store data
    steps = 101
    g.sims[k]['endsim'] = {}
    for key in g.sims[k]['rr'].keys():
      g.sims[k]['endsim'][key] = numpy.zeros((steps,3,),)
      g.sims[k]['endsim'][key][:,0] = numpy.linspace(beam_duration, g.sims[k]['end_time'] - beam_duration, steps) 

    for key in g.sims[k]['rr'].keys():
      for time_step in range(steps):
        t = g.sims[k]['endsim'][key][time_step,0]
        if(isotopes.is_stable(key)):
          g.sims[k]['endsim'][key][time_step,1] = g.sims[k]['tally_beam_end'][key]
        else:
          idata = {}
          idata[key] = {'w': 0.0, 'n0': g.sims[k]['tally_beam_end'][key]}
          decay_tally = isotopes.activity(key, t, idata)
          
          for dkey in decay_tally:
            if(dkey not in g.sims[k]['endsim'].keys()):
              g.sims[k]['endsim'][dkey] = numpy.zeros((steps,3,),)
              g.sims[k]['endsim'][dkey][:,0] = numpy.linspace(0.0, beam_duration, steps) 
            g.sims[k]['endsim'][dkey][time_step,1] = g.sims[k]['endsim'][dkey][time_step,1] + decay_tally[dkey]['nend']
            g.sims[k]['endsim'][dkey][time_step,2] = isotopes.get_decay_constant(dkey) * g.sims[k]['endsim'][dkey][time_step,1]
            
    total_activity = numpy.zeros((201,2),)
    total_activity[:101,0] = numpy.linspace(0.0, beam_duration, steps)
    total_activity[100:,0] = numpy.linspace(beam_duration, g.sims[k]['end_time'] - beam_duration, steps) 
    
    for key in g.sims[k]['endsim'].keys():
    
      plot_x = numpy.zeros((201,),)
      plot_y = numpy.zeros((201,),)
      plot_ya = numpy.zeros((201,),)
      
      plot_x[:101] = g.sims[k]['inbeam'][key][:,0]
      plot_y[:101] = g.sims[k]['inbeam'][key][:,1]
      plot_ya[:101] = g.sims[k]['inbeam'][key][:,2]
      
      plot_x[100:] = g.sims[k]['endsim'][key][:,0]
      plot_y[100:] = g.sims[k]['endsim'][key][:,1]
      plot_ya[100:] = g.sims[k]['endsim'][key][:,2]
      
      total_activity[:101,1]  = total_activity[:101,1] + g.sims[k]['inbeam'][key][:,2]
      total_activity[100:,1]  = total_activity[100:,1] + g.sims[k]['endsim'][key][:,2]
      
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Total Amount Throughout Simulation')
      plt.xlabel('Time (s)')
      plt.ylabel('Isotope Amount (atoms)')
      plt.plot(plot_x, plot_y)
      plt.savefig(sim.rd + '/amount_end_of_sim/' + str(isotopes.get_readable(key)), format='eps')
      plt.close('all') 

      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Total Activity Throughout Simulation')
      plt.xlabel('Time (s)')
      plt.ylabel('Activity (Bq)')
      plt.plot(plot_x, plot_ya)
      plt.savefig(sim.rd + '/activity_end_of_sim/' + str(isotopes.get_readable(key)), format='eps')
      plt.close('all') 
    
    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity Throughout Simulation')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.plot(total_activity[:,0], total_activity[:,1])
    plt.savefig(sim.rd + '/activity_end_of_sim/000___total.eps', format='eps')
    plt.close('all') 
    
    """
    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity Throughout Simulation')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.yscale('log')
    plt.plot(total_activity[:,0], total_activity[:,1])
    plt.savefig(sim.rd + '/amount_in_beam/total', format='eps')
    plt.close('all') 
    """
    
###########################
# Gamma Lines - End of Beam
###########################
        
    n = 0
    for key in g.sims[k]['tally_beam_end'].keys():
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_beam_end'][key]
        if(isotope_activity != 0):
          gn = isotopes.get_gammas(key)
          try:
            n = n + len(gn)
          except:
            pass
    
    g.sims[k]['gammas_beam_end'] = numpy.zeros((n, 2),)
    g.sims[k]['gammas_beam_end_list'] = []
    g.sims[k]['gammas_beam_end_total'] = 0.0
    g.sims[k]['activity_beam_end_total'] = 0.0

    n = 0
    for key in g.sims[k]['tally_beam_end'].keys():
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_beam_end'][key]
        
        if(isotope_activity != 0):
          try:
            gn = isotopes.get_gammas(key)
            g.sims[k]['gammas_beam_end'][n:n+len(gn), 0] = gn[:,0]
            g.sims[k]['gammas_beam_end'][n:n+len(gn), 1] = isotope_activity * gn[:,1]
            g.sims[k]['activity_beam_end_total'] = g.sims[k]['activity_beam_end_total'] + isotope_activity
            n = n + len(gn)

            for i in range(len(gn)):
              g.sims[k]['gammas_beam_end_list'].append([key, isotopes.get_readable(key), gn[i,0], gn[i,1], isotope_activity, isotope_activity * gn[i,1]])
              g.sims[k]['gammas_beam_end_total'] = g.sims[k]['gammas_beam_end_total'] + gn[i,0] * isotope_activity * gn[i,1]
          except:
            pass

    if(len(g.sims[k]['gammas_beam_end']) > 0):
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Predicted Gamma Lines')
      plt.xlabel('Energy (eV)')
      plt.ylabel('Activity (Bq)')
      plt.stem(g.sims[k]['gammas_beam_end'][:,0], g.sims[k]['gammas_beam_end'][:,1])
      plt.savefig(sim.rd + '/gammas/' + 'end_of_beam_gamma_lines.eps', format='eps')
      plt.close('all') 
      std.write_csv(sim.rd + '/gammas/end_of_beam_gamma_lines.dat', g.sims[k]['gammas_beam_end'], w=14)
    
    if(len(g.sims[k]['gammas_beam_end_list']) > 0):
      gammas = sorted(g.sims[k]['gammas_beam_end_list'], key=lambda x: x[0])
      fh = open(sim.rd + '/gammas/end_of_beam_gamma_lines_by_isotope.dat', 'w')
      for gamma in gammas:
        fh.write(std.pad_right(gamma[0], 10))
        fh.write(std.pad_right(gamma[1], 10))
        fh.write(std.pad_right(gamma[2], 22))
        fh.write(std.pad_right(gamma[3], 22))
        fh.write(std.pad_right(gamma[4], 22))
        fh.write(std.pad_right(gamma[5], 22))
        fh.write('\n')
      fh.close()
    
    if(len(g.sims[k]['gammas_beam_end_list']) > 0):
      gammas = sorted(g.sims[k]['gammas_beam_end_list'], key=lambda x: x[2])
      fh = open(sim.rd + '/gammas/end_of_beam_gamma_lines_by_energy.dat', 'w')
      for gamma in gammas:
        fh.write(std.pad_right(gamma[0], 10))
        fh.write(std.pad_right(gamma[1], 10))
        fh.write(std.pad_right(gamma[2], 22))
        fh.write(std.pad_right(gamma[3], 22))
        fh.write(std.pad_right(gamma[4], 22))
        fh.write(std.pad_right(gamma[5], 22))
        fh.write('\n')
      fh.close()
    
    if(len(g.sims[k]['gammas_beam_end_list']) > 0):
      gammas = sorted(g.sims[k]['gammas_beam_end_list'], key=lambda x: x[5])
      fh = open(sim.rd + '/gammas/end_of_beam_gamma_lines_by_activity.dat', 'w')
      for gamma in gammas:
        fh.write(std.pad_right(gamma[0], 10))
        fh.write(std.pad_right(gamma[1], 10))
        fh.write(std.pad_right(gamma[2], 22))
        fh.write(std.pad_right(gamma[3], 22))
        fh.write(std.pad_right(gamma[4], 22))
        fh.write(std.pad_right(gamma[5], 22))
        fh.write('\n')
      fh.close()

###########################
# Gamma Lines - End of Sim
###########################

    n = 0
    for key in g.sims[k]['tally_sim_end'].keys():
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_sim_end'][key]
        if(isotope_activity != 0):
          gn = isotopes.get_gammas(key)
          try:
            n = n + len(gn)
          except:
            pass
    
    g.sims[k]['gammas_sim_end'] = numpy.zeros((n, 2),)
    g.sims[k]['gammas_sim_end_list'] = []
    g.sims[k]['gammas_sim_end_total'] = 0.0
    g.sims[k]['activity_sim_end_total'] = 0.0
    
    n = 0
    for key in g.sims[k]['tally_sim_end'].keys():
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_sim_end'][key]        
        if(isotope_activity != 0):
          try:
            gn = isotopes.get_gammas(key)
            g.sims[k]['gammas_sim_end'][n:n+len(gn), 0] = gn[:,0]
            g.sims[k]['gammas_sim_end'][n:n+len(gn), 1] = isotope_activity * gn[:,1]
            g.sims[k]['activity_sim_end_total'] = g.sims[k]['activity_sim_end_total'] + isotope_activity
            n = n + len(gn)

            for i in range(len(gn)):
              g.sims[k]['gammas_sim_end_list'].append([key, isotopes.get_readable(key), gn[i,0], gn[i,1], isotope_activity, isotope_activity * gn[i,1]])
              g.sims[k]['gammas_sim_end_total'] = g.sims[k]['gammas_sim_end_total'] + gn[i,0] * isotope_activity * gn[i,1]
          except:
            pass   
    
    if(len(g.sims[k]['gammas_sim_end']) > 0):
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Predicted Gamma Lines')
      plt.xlabel('Energy (eV)')
      plt.ylabel('Activity (Bq)')
      plt.stem(g.sims[k]['gammas_sim_end'][:,0], g.sims[k]['gammas_sim_end'][:,1])
      plt.savefig(sim.rd + '/gammas/end_of_sim_gamma_lines.eps', format='eps')
      plt.close('all') 
#std.write_csv(sim.rd + '/gammas/end_of_sim_gamma_lines.dat', g.sims[k]['gammas_sim_end'], w=14)
    
    if(len(g.sims[k]['gammas_sim_end_list']) > 0):
      gammas = sorted(g.sims[k]['gammas_sim_end_list'], key=lambda x: x[0])
      fh = open(sim.rd + '/gammas/end_of_sim_gamma_lines_by_isotope.dat', 'w')
      for gamma in gammas:
        fh.write(std.pad_right(gamma[0], 10))
        fh.write(std.pad_right(gamma[1], 10))
        fh.write(std.pad_right(gamma[2], 22))
        fh.write(std.pad_right(gamma[3], 22))
        fh.write(std.pad_right(gamma[4], 22))
        fh.write(std.pad_right(gamma[5], 22))
        fh.write('\n')
      fh.close()
    
    if(len(g.sims[k]['gammas_sim_end_list']) > 0):
      gammas = sorted(g.sims[k]['gammas_sim_end_list'], key=lambda x: x[2])
      fh = open(sim.rd + '/gammas/end_of_sim_gamma_lines_by_energy.dat', 'w')
      for gamma in gammas:
        fh.write(std.pad_right(gamma[0], 10))
        fh.write(std.pad_right(gamma[1], 10))
        fh.write(std.pad_right(gamma[2], 22))
        fh.write(std.pad_right(gamma[3], 22))
        fh.write(std.pad_right(gamma[4], 22))
        fh.write(std.pad_right(gamma[5], 22))
        fh.write('\n')
      fh.close()
    
    if(len(g.sims[k]['gammas_sim_end_list']) > 0):
      gammas = sorted(g.sims[k]['gammas_sim_end_list'], key=lambda x: x[5])
      fh = open(sim.rd + '/gammas/end_of_sim_gamma_lines_by_activity.dat', 'w')
      for gamma in gammas:
        fh.write(std.pad_right(gamma[0], 10))
        fh.write(std.pad_right(gamma[1], 10))
        fh.write(std.pad_right(gamma[2], 22))
        fh.write(std.pad_right(gamma[3], 22))
        fh.write(std.pad_right(gamma[4], 22))
        fh.write(std.pad_right(gamma[5], 22))
        fh.write('\n')
      fh.close()

###########################
# Isotopes
###########################

    fh = open(sim.rd + '/radioactive_isotopes/end_of_beam.dat', 'w')
    fh.write('Radioactive Isotopes\n')
    fh.write('===================================================\n')
    fh.write('\n')
    fh.write('End of Beam\n')
    fh.write('-----------\n')
    fh.write('\n')
    
    for key in g.sims[k]['tally_beam_end'].keys():
      if(not isotopes.is_stable(key) and g.sims[k]['tally_beam_end'][key] > 0.0):
        fh.write(std.pad_right(isotopes.get_readable(key), 10) + "  " + str(isotopes.get_decay_constant(key) * g.sims[k]['tally_beam_end'][key]) + '\n')
        
    fh.write('\n')    
    fh.close()  

    fh = open(sim.rd + '/radioactive_isotopes/end_of_sim.dat', 'w')
    fh.write('Radioactive Isotopes\n')
    fh.write('===================================================\n')
    fh.write('\n')
    fh.write('End of Sim\n')
    fh.write('----------\n')
    fh.write('\n')
    
    for key in g.sims[k]['tally_sim_end'].keys():
      if(not isotopes.is_stable(key) and g.sims[k]['tally_sim_end'][key] > 0.0):
        fh.write(std.pad_right(isotopes.get_readable(key), 10) + "  " + str(isotopes.get_decay_constant(key) * g.sims[k]['tally_sim_end'][key]) + '\n')
            
    fh.write('\n')
    fh.write('\n')        
    fh.close()  

    fh = open(sim.rd + '/gamma_dose/gamma_dose.dat', 'w')

    gamma_ev = g.sims[k]['gammas_beam_end_total']
    gamma_J = 1.60218E-19 * gamma_ev
    gamma_dose = gamma_J / (12.57 * 80)
    gamma_dose_hr = (gamma_J / (12.57 * 80)) * 3600
    gamma_dose_p = (gamma_dose_hr / 1.140771128E-04) * 100

    print('Gamma Dose - Beam End')
    print('===================================================')
    print()

    print("Activity/Bq                    ", g.sims[k]['activity_beam_end_total'])
    print("Power eV/s                     ", g.sims[k]['gammas_beam_end_total'])
    print("Power J/s                      ", gamma_J)
    print("Dose Gy/s                      ", gamma_dose)
    print("Dose Gy/hr                     ", gamma_dose_hr)
    print("Percentage of annual dose/hr   ", gamma_dose_p)
    print()

    fh.write('Gamma Dose - Beam End\n')
    fh.write('===================================================\n')
    fh.write('Activity/Bq                    ' + str(g.sims[k]['activity_beam_end_total']) + '\n')
    fh.write('Power eV/s                     ' + str(g.sims[k]['gammas_beam_end_total']) + '\n')
    fh.write('Power J/s                      ' + str(gamma_J) + '\n')
    fh.write('Dose Gy/s                      ' + str(gamma_dose) + '\n')
    fh.write('Dose Gy/hr                     ' + str(gamma_dose_hr) + '\n')
    fh.write('Percentage of annual dose/hr   ' + str(gamma_dose_p) + '\n')
    fh.write('\n')
    fh.write('\n')

    log.br()
    log.log('Gamma Dose - Beam End')
    log.log('Activity/Bq                    ' + str(g.sims[k]['activity_beam_end_total']))
    log.log('Power eV/s                     ' + str(g.sims[k]['gammas_beam_end_total']))
    log.log('Power J/s                      ' + str(gamma_J))
    log.log('Dose Gy/s                      ' + str(gamma_dose))
    log.log('Dose Gy/hr                     ' + str(gamma_dose_hr))
    log.log('Percentage of annual dose/hr   ' + str(gamma_dose_p))
    log.br()

    gamma_ev = g.sims[k]['gammas_sim_end_total']
    gamma_J = 1.60218E-19 * gamma_ev
    gamma_dose = gamma_J / (4.188 * 100)
    gamma_dose_hr = (gamma_J / (12.57 * 80)) * 3600
    gamma_dose_p = (gamma_dose_hr / 1.140771128E-04) * 100

    print('Gamma Dose - Sim End')
    print('===================================================')
    print()
    print("Activity/Bq                    ", g.sims[k]['activity_sim_end_total'])
    print("Energy eV/s                    ", g.sims[k]['gammas_sim_end_total'])
    print("Energy J/s                     ", gamma_J)
    print("Dose Gy                        ", gamma_dose)
    print("Dose Gy/hr                     ", gamma_dose_hr)
    print("Percentage of annual dose/hr   ", gamma_dose_p)
    print()
    print()

    fh.write('Gamma Dose - Sim End\n')
    fh.write('===================================================\n')
    fh.write('Activity/Bq                    ' + str(g.sims[k]['activity_sim_end_total']) + '\n')
    fh.write('Power eV/s                     ' + str(g.sims[k]['gammas_sim_end_total']) + '\n')
    fh.write('Power J/s                      ' + str(gamma_J) + '\n')
    fh.write('Dose Gy/s                      ' + str(gamma_dose) + '\n')
    fh.write('Dose Gy/hr                     ' + str(gamma_dose_hr) + '\n')
    fh.write('Percentage of annual dose/hr   ' + str(gamma_dose_p) + '\n')
    fh.write('\n')
    fh.write('\n')

    log.br()
    log.log('Gamma Dose - Sim End')
    log.log('Activity/Bq                    ' + str(g.sims[k]['activity_sim_end_total']))
    log.log('Power eV/s                     ' + str(g.sims[k]['gammas_sim_end_total']))
    log.log('Power J/s                      ' + str(gamma_J))
    log.log('Dose Gy/s                      ' + str(gamma_dose))
    log.log('Dose Gy/hr                     ' + str(gamma_dose_hr))
    log.log('Percentage of annual dose/hr   ' + str(gamma_dose_p))
    log.br()

    print("Absorbed Dose Calculations")
    print('===================================================')
    print('Absorbed dose assumptions:')
    print('1. radiation from point, emitted isotropically')   
    print('2. 80Kg human')   
    print('3. 1m from point source')   
    print('4. 1m squared surface area')   
    print('5. all energy absorbed')   
    print()
    print()

    print("Dose Limits")
    print('===================================================')
    print("employees 18+             20 millisieverts/year")
    print("trainees 18+              6 millisieverts/year")
    print("public and under 18s      1 millisievert/year")
    print("public and under 18s      1.140771128E-04 millisieverts/hour")
    print("")
    print("Dose averaged over area of skin not exceeding 1cm2")
    print("Source: http://www.hse.gov.uk/radiation/ionising/doses/")
    print()
    print()
 
    fh.write('Absorbed Dose Calculations\n')
    fh.write('===================================================\n')
    fh.write('Absorbed dose assumptions:\n')
    fh.write('1. radiation from point, emitted isotropically\n')
    fh.write('2. 80Kg human\n')
    fh.write('3. 1m from point source\n')
    fh.write('4. 1m squared surface area\n')
    fh.write('5. all energy absorbed\n')
    fh.write('\n')
    fh.write('\n')

    fh.write('Dose Limits\n')
    fh.write('===================================================\n')
    fh.write('employees 18+             20 millisieverts/year\n')
    fh.write('trainees 18+              6 millisieverts/year\n')
    fh.write('public and under 18s      1 millisievert/year\n')
    fh.write('public and under 18s      1.140771128E-04 millisieverts/hour\n')
    fh.write('\n')
    fh.write('Dose averaged over area of skin not exceeding 1cm2\n')
    fh.write('Source: http://www.hse.gov.uk/radiation/ionising/doses/\n')
    fh.write('\n')
    fh.write('\n')

    fh.close()

    """
    fh.write('Gamma Dose - Beam End\n')
    fh.write('===================================================\n')
    fh.write('\n')
    fh.write(g.sims[k]['gammas_beam_end_total'] )
    fh.write('\n')
    fh.write('\n')  

    fh.write('Gamma Dose - Beam End\n')
    fh.write('===================================================\n')
    fh.write('\n')
    fh.write(g.sims[k]['gammas_beam_end_total'] )
    fh.write('\n')
    fh.write('\n')  
   
    fh.write('\n')
    fh.write('\n')  
    """

    """  
      if(key not in g.sims[k]['tally_beam_end'].keys()):
        g.sims[k]['tally_beam_end'][key] = 0.0      
      if(isotopes.is_stable(key)):
        g.sims[k]['tally_beam_end'][key] = g.sims[k]['tally'][key] + t * g.sims[k]['rr'][key]
      else:
        if(g.sims[k]['tally'][key] > 0.0 or g.sims[k]['rr'][key] > 0.0):
          idata = {}
          idata[key] = {'w': g.sims[k]['rr'][key], 'n0': g.sims[k]['tally'][key]}
          decay_tally = isotopes.activity(key, t, idata)
          for dkey in decay_tally:
            if(dkey not in g.sims[k]['tally_beam_end'].keys()):
              g.sims[k]['tally_beam_end'][dkey] = 0.0
            g.sims[k]['tally_beam_end'][dkey]
    """

###########################################
#  CLASS bea
###########################################
class beam:

  def __init__(self):
  
    self.area = None
    self.projectile = None
    self.projectile_code = None
    self.energy = None
    self.duration = None
    self.current = None
    self.flux = None
    
  def set_duration(self, time, unit):
    self.duration = units.convert(unit, 's', time)    
    
  def set_area(self, area, unit):
    self.area = units.convert(unit, 'M2', area)
    
  def set_current(self, current, unit):  
    self.current = units.convert(unit, 'A', current)

  def set_energy(self, energy, unit):  
    self.energy = units.convert(unit, 'eV', energy)
    
  def set_projectile(self, projectile):  
    if(projectile.lower()[0] == 'p'):
      self.projectile = 'Proton'
      self.projectile_code = 1001
    elif(projectile.lower()[0] == 'd'):
      self.projectile = 'Deuteron'
      self.projectile_code = 1002
    
  def set(self):
    q = 1
    if(self.projectile == 'Deuteron'):
      q = 1
    self.flux = self.current * 6.241509129E18
    
  def get_projectile(self):
    return self.projectile
      
  def get_projectile_code(self):
    return self.projectile_code
    
  def get_area(self):
    return self.area
    
  def get_flux(self):
    return self.flux
    
  def get_duration(self):
    return self.duration
    
  def display(self):  
    print("Beam Details")
    print("======================")
    print("Projectile: ", self.projectile)
    print("Energy: ", self.energy, "eV")
    print("Duration: ", self.duration, "s")
    print("Area: ", self.area, "m^2")
    print("Current: ", self.current, "A")
    print("Flux: ", self.flux, "projectiles/s")
    print()
    
###########################################
#  CLASS targe
###########################################
class target:

  avogadro = 6.0221409E23

  def __init__(self):
    self.composition = {}
    self.avgmass = None
    self.depth = None
    self.density = None
    
# example:   Fe,0.8,Cr,0.2
  def set_composition(self, elements_in):  
    num = "0123456789"
    
# String
    elements = []
    masses = []
    for i in range(len(elements_in)//2):
      elements.append(elements_in[2*i])
      masses.append(float(elements_in[2*i+1]))
      
# Mass to a percentage
    for m in range(len(masses)):
      masses[m] = float(masses[m])
    tm = sum(masses)    
    for m in range(len(masses)):
      masses[m] = masses[m] * (100 / tm)
      
# Capitalise elements
    for e in range(len(elements)):
      elements[e] = elements[e].capitalize().strip()
      
# Create target
    self.composition = {}
      
    self.avgmass = 0.0
    for n in range(len(elements)):
      element = ''
      isotope = ''
      for c in elements[n]:
        if(c in num):
          isotope = isotope + c
        else:
          element = element + c

# Get isotope
      s = isotopes.get_isotopes(element, isotope)
      
      for sn in s:        
        k = int(1000 * int(sn['protons']) + int(sn['nucleons']))
       
        self.composition[k] = {
                   'element': isotopes.get_element(sn['protons']),
                   'protons': sn['protons'],
                   'neutrons': sn['neutrons'],
                   'nucleons': sn['nucleons'],
                   'mass': sn['mass'],
                   'percentage_by_mass': (masses[n] / 100) * sn['percentage'],
                   'percentage_by_number': 0.0,
                   'isotope_density': 0.0,
                   'isotope_number_density': 0.0,
                   }
        self.avgmass = self.avgmass + (self.composition[k]['percentage_by_mass'] / 100.0) * sn['mass']       
    
# Calculate number percentage of each isotope
    s = 0.0
    for k in self.composition.keys():
      m = self.composition[k]['mass']
      s = s + self.composition[k]['percentage_by_mass'] / m
    for k in self.composition.keys():
      m = self.composition[k]['mass']
      self.composition[k]['percentage_by_number'] = ((self.composition[k]['percentage_by_mass'] / m) / s) * 100  
           
  def set_depth(self, depth, depth_unit):
    self.depth = units.convert(depth_unit, 'M', depth)
    
  def set_density(self, density, density_unit):
    self.density = units.convert(density_unit, 'KGM3', density)
    
  def calc_nd(self):
    for k in self.composition.keys():
      self.composition[k]['isotope_density'] = self.density * (self.composition[k]['percentage_by_mass'] / 100)
      self.composition[k]['isotope_number_density'] = ((self.composition[k]['isotope_density'] * 1E3) / self.composition[k]['mass']) * target.avogadro

  def get_isotope_list(self):
    i_list = []
    for k in self.composition.keys():
      i_list.append(k)
    return i_list  
    
  def get_depth(self):
    return self.depth

  def get_depth_ang(self):
    return 1.0E10 * self.depth
    
  def get_target_number_density(self, target):
    if(target in self.composition.keys()):
      return self.composition[target]['percentage_by_number']
    return 0.0
    
  def get_isotope_number_density(self, target):
    if(target in self.composition.keys()):
      return self.composition[target]['isotope_number_density']
    return 0.0
          
  def display(self):
    print("Target")
    print("========================================================")
    print("Depth:   ", self.depth, "m")
    print("Density: ", self.density, "kgm3")  
    print("Mass:    ", self.avgmass, "amu")  
    print("Isotope  Mass         PBM          PBN")
    print("========================================================")
    for k in self.composition.keys():
      isotope = '{:6}'.format(self.composition[k]['element'] + str(self.composition[k]['nucleons']))
      mass = str("{:.4E}".format(self.composition[k]['mass']))
      pbm = str("{:.4E}".format(self.composition[k]['percentage_by_mass']))
      pbn = str("{:.4E}".format(self.composition[k]['percentage_by_number']))
      id = str("{:.4E}".format(self.composition[k]['isotope_density']))
      ind = str("{:.4E}".format(self.composition[k]['isotope_number_density']))
      print(isotope, mass, pbm, pbn, id, ind, sep="   ")
  
    print("========================================================")
    print()

###########################################
#  CLASS isotope
###########################################
class isotopes:
  sources = []
  symbols = {}
  isotopes = {}
  jeffdata = {}
  gammas = {}
  gammas_array = {}

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
          
# ONLY PROCESS 457 IF UNSTABLE
#if(not isotope['stable'] and (isotope['key'] == 41090 or isotope['key'] == 39104 or isotope['key'] == 27055)):
    if(not isotope['stable']):
#  and (isotope['key'] == 41090 or isotope['key'] == 39104)
#  and isotope['key'] == 39104
# and isotope['key'] == 41090
# print(isotope['key'])
    
      n_rows = len(blocks_457)
      loop = True
      a_rows = -1
      b_rows = -1
      discrete = 0
      n = 0
      
      modes = {  10: ['B-',1,-1, True], 
                 15: ['B-, N',-1,0, True],
                 20: ['B+',-1,1, True],
                 30: ['IT',0,0, True],
                 40: ['A',-2,-2, True],
                 50: ['N',0,-1, True],
                 60: ['SF',0,0, False],
              }
      
      while(n < n_rows and loop):
        l, mat, mf, mt, row_num = isotopes.read_row(blocks_457[n])
#print(blocks_457[n])
        if(row_num == 2):
          isotope['half_life'] = float(isotopes.read_float(l[0]))   
          isotope['half_life_error'] = float(isotopes.read_float(l[1]))    
          a_points = int(l[4])
          a_rows = int(numpy.ceil(a_points / 6))
#print(row_num, a_points, a_rows)
    
        elif(a_rows > 0 and row_num == 3 + a_rows):
          isotope['spin_parity'] = float(isotopes.read_float(l[0]))   
          b_points = int(l[4])
          b_rows = int(numpy.ceil(b_points / 6))   
#print(row_num, b_points, b_rows)
          
        elif(b_rows > 0 and row_num >= 3 + a_rows + 1 and row_num <= 3 + a_rows + b_rows):
#print("....",blocks_457[n])
          mode_n = int(10 * isotopes.read_float(l[0]))
          if(mode_n in modes.keys()):
            mode = modes[mode_n]
            if(mode[3]):              
              mode_text = mode[0]
              to_p = isotope['protons'] + mode[1]
              to_n = isotope['neutrons'] + mode[2]
              to_meta = int(isotopes.read_float(l[1]))
              qvalue = float(isotopes.read_float(l[2]))            # In eV
              branching_factor = float(isotopes.read_float(l[4]))  # 0.0 to 1.0              
#print(mode_text, to_p, to_n, to_meta, qvalue, branching_factor)
              
              to_key = to_meta * 1000000 + 1000 * to_p + (to_p + to_n)            
              isotope['decay_modes'][to_key] = [branching_factor, to_meta, qvalue]
         
        elif(row_num > 3 + a_rows + b_rows):
          try:
            if(float(isotopes.read_float(l[0])) == 0.0 and float(isotopes.read_float(l[1])) == 0.0 and int(l[3]) == 0 and int(l[5]) > 0):
#print(blocks_457[n])
              
              n = n + 1
              gamma_rows = int(l[5])
              l, mat, mf, mt, row_num = isotopes.read_row(blocks_457[n])
              nfact = float(isotopes.read_float(l[0])) 
#print(blocks_457[n])
              
              isotope['gammas'] = {}
              isotopes.gammas_array[isotope['key']] = numpy.zeros((gamma_rows, 2,),)
              
              for gn in range(gamma_rows):
                           
                n = n + 1
                l, mat, mf, mt, row_num = isotopes.read_row(blocks_457[n])
                
# First row
                energy = float(isotopes.read_float(l[0])) * 1000 # eV
                d_energy = float(isotopes.read_float(l[1])) * 1000 # eV
         
# Second row
                n = n + 1
                l, mat, mf, mt, row_num = isotopes.read_row(blocks_457[n])
        
                intensity_endf = float(isotopes.read_float(l[2]))
                d_intensity_endf = float(isotopes.read_float(l[3]))
                intensity = nfact * float(isotopes.read_float(l[2]))
                d_intensity = nfact * float(isotopes.read_float(l[3]))

# Third row
                n = n + 1
                l, mat, mf, mt, row_num = isotopes.read_row(blocks_457[n])
            
                tot_int_conv_coeff = float(isotopes.read_float(l[0]))
                d_tot_int_conv_coeff = float(isotopes.read_float(l[1]))
                k_shell_int_conv_coeff = float(isotopes.read_float(l[2]))
                d_k_shell_int_conv_coeff = float(isotopes.read_float(l[3]))
                l_shell_int_conv_coeff = float(isotopes.read_float(l[4]))
                d_l_shell_int_conv_coeff = float(isotopes.read_float(l[5]))
          
                isotope['gammas'][energy] = {
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
          
# Increment
        n = n + 1
    
# Store
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
    if(key not in isotopes.jeffdata.keys()):
      return out
    if(l == 0):   
      isotopes.chains_store = []
    out.append([l, key, bf, q])
    if(isotopes.jeffdata[key]['stable']):
      if(len(out) > 1):
        for i in range(len(out)-1,1,-1):
          if(out[i-1][0]>=out[i][0]):
            out.pop(out[i-1][0])
      return isotopes.chains_store.append(copy.deepcopy(out))
    else:
      l = l + 1 
      for k in isotopes.jeffdata[key]['decay_modes'].keys():
        bf = isotopes.jeffdata[key]['decay_modes'][k][0]
        q = isotopes.jeffdata[key]['decay_modes'][k][2]
        isotopes.make_chain(k, l, out, bf, q)
      return out
#[branching_factor, to_meta, qvalue]
      
  @staticmethod
  def make_chain_test(key, l=0, out=[], bf=0.0, q=0.0):
    if(key not in isotopes.jeffdata.keys()):
      return out
    out.append([l, key, bf, q])
    if(isotopes.jeffdata[key]['stable']):
      if(len(out) > 1):
        for i in range(len(out)-1,1,-1):
          if(out[i-1][0]>=out[i][0]):
            out.pop(out[i-1][0])
      return out
    else:
      l = l + 1 
      for k in isotopes.jeffdata[key]['decay_modes'].keys():
        bf = isotopes.jeffdata[key]['decay_modes'][k][0]
        q = isotopes.jeffdata[key]['decay_modes'][k][2]
        isotopes.make_chain_test(k, l, out, bf, q)
      return out  

  @staticmethod
  def chain_isotopes(key, out=[]):
    if(key not in isotopes.jeffdata.keys()):
      return out
    if(key not in out):
      out.append(key)
    else:
      return out
    if(isotopes.jeffdata[key]['stable']):
      return out
    else:
      for k in isotopes.jeffdata[key]['decay_modes'].keys():        
        isotopes.chain_isotopes(k, out)
      return out

  @staticmethod
  def is_stable(key):
    if(key in isotopes.jeffdata.keys()):
      return isotopes.jeffdata[key]['stable']
    return False
 
  @staticmethod
  def is_metastable(key):
    if(key > 1000000):
      return True
    return False

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
   
###########################################
#  CLASS tend
###########################################
class tendl:

  mt = {
           2: [[0,0,0]],
           3: [[0,0,0]],
           4: [[0,1,1],1],
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
    tendl.convert('test_fe', dir, 1001)
#tendl.convert('TENDL-p', dir, 1001)
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
    
    print(tendl.get_xs_residual(1001, 26058, 26056, 25000000))

###########################################
#  CLASS main(
###########################################
class main():

  def start():
  
# RECORD START TIME
    g.times['start'] = time.time()
    
    now = datetime.datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(date_time)	
  
    activity.run()
    
    main.end()
      
  def end(): 
# CLOSE LOG
    g.times['end'] = time.time()
    exit()

# Run
main.start()

###########################################
###########################################
#  MAIN
###########################################
###########################################

class main():



  def start():

  

# RECORD START TIME
    g.times['start'] = time.time()

    

    now = datetime.datetime.now()

    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    print(date_time)	

  

    activity.run()

    

    main.end()

      

  def end(): 

# CLOSE LOG
    g.times['end'] = time.time()

    exit()



# Run
main.start()

