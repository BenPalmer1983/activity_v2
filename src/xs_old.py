

class xs:
  
  dir = None  
  xs_data = {}
  
  def start(dir):
  
    dir = dir.strip()
    if(dir[-1] != "/"):
      dir = dir + "/"
    xs.dir = dir  
      
      
  def load(ilist, projectile):   
  
    target_residual = {}
    if(projectile not in xs.xs_data.keys()):
      xs.xs_data[projectile] = {}
  
  
    for i in ilist:
      # Save Targets
      protons = i[0]
      nucleons = i[1]
      tk = int(1000 * int(protons) + int(nucleons))
      
      if(tk not in target_residual.keys()):
        target_residual[tk] = []
      
      # XS file Path
      path = xs.dir + '/' + str(protons) + '/' + 'xs_' + str(projectile) + '_' + str(tk) + '.z'
      
      # Save Residuals
      if(os.path.isfile(path)):
        data = zfdict.load(path)

        for k in data.keys(): 
          rprotons = data[k]['residual_protons']
          rneutrons = data[k]['residual_neutrons']
          rnucleons = data[k]['residual_nucleons']
          ds = data[k]['data_size']
          
          rk = int(1000 * int(rprotons) + int(rnucleons))
  
          # Save XS
          if(tk not in xs.xs_data[projectile].keys()):
            xs.xs_data[projectile][tk] = {}              
          xs.xs_data[projectile][tk][rk] = numpy.zeros((ds, 2,),)
          for i in range(ds):
            xs.xs_data[projectile][tk][rk][i,0] = data[k]['data'][i][0]
            xs.xs_data[projectile][tk][rk][i,1] = data[k]['data'][i][1]
          
          if(rk not in target_residual[tk]):
            target_residual[tk].append(rk)
    return target_residual
 
  def get_xs(projectile, target, residual, energy):
    d = xs.xs_data[projectile][target][residual]
    if(energy < d[0,0] or energy > d[-1,0]):
      return 0.0
    else:
      for i in range(len(d)-1):
        if(energy >= d[i,0] and energy <= d[i+1,0]):
          print(d[i,0], d[i+1,0], d[i,1], d[i+1,1])
          return d[i,1] + ((energy-d[i,0])/(d[i+1,0] - d[i,0])) * (d[i+1,1] - d[i,1])
        

 
  """
  def rr(target, residual, projectile):
    d = xs.xs_data[target][residual]
    if(
    
    
    print(d)
  """




