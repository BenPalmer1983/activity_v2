import json
import zlib

"""

Data structures

  symbols[0] = 'Nn'
          1+    Other elements 




  elements[0] = {
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
  elements[protons]['stable'].append(nucleons)
  elements[protons]['isotopes'][nucleons] = {
                                             'neutrons': neutrons,
                                             'nucleons': nucleons,
                                             'stable': True,
                                             'half_life': None,
                                             'decay_constant': None,
                                             'percentage': percentage,
                                             'mass': mass,
                                             'decay_modes': [],
                                             'gammas': [[],[],[]],
                                            }

  elements[protons]['unstable'].append(nucleons)
  elements[protons]['isotopes'][nucleons] = {
                                             'neutrons': neutrons,
                                             'nucleons': nucleons,
                                             'stable': False,
                                             'half_life': half_life,
                                             'decay_constant': decay_constant,
                                             'percentage': 0.0,
                                             'mass': mass,
                                             'decay_modes': [],
                                             'gammas': [[],[],[]],
                                            }

"""


class isotopes:

  dir = None
  symbols = None
  elements = None
  
  def start(dir):
  
    dir = dir.strip()
    if(dir[-1] != "/"):
      dir = dir + "/"
      
    isotopes.dir = dir  
      
    isotopes.symbols = isotopes.load(dir + 'symbols.z')  
    isotopes.elements = isotopes.load(dir + 'isotopes.z')


 
  def get_element(protons):
    try:
      return isotopes.symbols[str(protons)]
    except:
      return None

  def get_protons(element):
    element = element.capitalize()
    try:
      return isotopes.symbols[element]
    except:
      return None
      
  def get_isotopes(element, nucleons=None):
    num = "0123456789"
    if(element[0] in num):
      protons = str(element)
    else:
      protons = str(isotopes.symbols[str(element)])
      
    s = []
    if(nucleons == None or nucleons == ''):  
      # Get all stable isotopes
      for k in isotopes.elements[protons]['stable']:
        k = str(k)
        s.append({
               'protons': protons,
               'neutrons': isotopes.elements[protons]['isotopes'][k]['neutrons'],
               'nucleons': isotopes.elements[protons]['isotopes'][k]['nucleons'],
               'percentage': isotopes.elements[protons]['isotopes'][k]['percentage'],
               'mass': isotopes.elements[protons]['isotopes'][k]['mass'],
               })
    else:
      # If specific isotope selected, percentage is 100%
      k = str(nucleons)
      s.append({
                'protons': protons,
                'neutrons': isotopes.elements[protons]['isotopes'][k]['neutrons'],
                'nucleons': isotopes.elements[protons]['isotopes'][k]['nucleons'],
                'percentage': 100.0,
                'mass': isotopes.elements[protons]['isotopes'][k]['mass'],
                })
    return s


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
