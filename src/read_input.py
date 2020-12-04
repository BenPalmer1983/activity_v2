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
      elif(n > 10 and k not in g.inp.keys()): 
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
                      


