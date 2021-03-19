"""       
    print(g.sims[k]['rr'])
    exit()
    
    # Calculate reaction rates
    #for ion in g.exyz[exyz_file].keys():
    # Loop through target isotopes
    for tn in ilist:
      # Loop through residuals
      residual = xs.get_residual(projectile, tn)  
      for rn in residual.keys():
        if(rn != 0):
          dr_sigma = 0.0
          # Loop over all ions and calculate cross section per ion
          for ion in g.exyz[exyz_file].keys():
            for n in range(len(g.exyz[exyz_file][ion])):   
              dr = g.exyz[exyz_file][ion][n,1]
              if(g.exyz[exyz_file][ion][n,2] > target_depth):
                break
              else:
                f = 1.0
                if(g.exyz[exyz_file][ion][n,3] > target_depth):
                  f = (target_depth - g.exyz[exyz_file][ion][n,2]) / (g.exyz[exyz_file][ion][n,3] - g.exyz[exyz_file][ion][n,2])
                energy = g.exyz[exyz_file][ion][n,0]
                sigma = xs.get_sigma_residual(projectile, tn, rn, energy)
                dr_sigma = dr * sigma * f
              
          # cross section per ion for this thickness 
          dr_sigma = dr_sigma / len(g.exyz[exyz_file])  
          
          if(dr_sigma > 0.0):
            print(tn, rn, dr_sigma)
        
          # target number density      
          tn_nd = g.sims[k]['target'].get_isotope_number_density(tn)
        
          # beam flux
          flux = g.sims[k]['beam'].get_flux()
        
          # Reaction rate (convert from barns to sq metre)
          rr = dr_sigma * flux * tn_nd * 1.0e-28

          # Subtract from target, add to residual
          g.sims[k]['rr'][tn] = g.sims[k]['rr'][tn] - rr
          g.sims[k]['rr'][rn] = g.sims[k]['rr'][rn] + rr
          
      # Loop through emitted
      emitted = xs.get_emitted(projectile, tn)  
      for en in emitted.keys():
        if(en != 0):
          dr_sigma = 0.0
          # Loop over all ions and calculate cross section per ion
          for ion in g.exyz[exyz_file].keys():
            for n in range(len(g.exyz[exyz_file][ion])):   
              dr = g.exyz[exyz_file][ion][n,1]
              if(g.exyz[exyz_file][ion][n,2] > target_depth):
                break
              else:
                f = 1.0
                if(g.exyz[exyz_file][ion][n,3] > target_depth):
                  f = (target_depth - g.exyz[exyz_file][ion][n,2]) / (g.exyz[exyz_file][ion][n,3] - g.exyz[exyz_file][ion][n,2])
                energy = g.exyz[exyz_file][ion][n,0]
                sigma = xs.get_sigma_emitted(projectile, tn, en, energy)
                dr_sigma = dr * sigma * f
              
          # cross section per ion for this thickness 
          dr_sigma = dr_sigma / len(g.exyz[exyz_file])      
         
          # target number density      
          tn_nd = g.sims[k]['target'].get_isotope_number_density(tn)
        
          # beam flux
          flux = g.sims[k]['beam'].get_flux()
        
          # Reaction rate (convert from barns to sq metre)
          rr = dr_sigma * flux * tn_nd * 1.0e-28

          # add to emitted
          g.sims[k]['rr'][en] = g.sims[k]['rr'][en] + rr
               
    # Print out reaction rates
    #for n in g.sims[k]['rr'].keys():
    #  print(n, g.sims[k]['rr'][n])
    
    
    
    
    for target in g.sims[k]['target_residual']:
      if(target not in g.tally[k].keys()):
        g.tally[k][target] = 0.0
      g.tally[k][target] = g.tally[k][target] + v * g.sims[k]['target'].get_isotope_number_density(target)
      for residual in g.sims[k]['target_residual'][target]:
        if(residual not in g.tally[k].keys()):
          g.tally[k][residual] = 0.0
    
    #for key in g.tally[k].keys():
    #  print(key, g.tally[k][key])
    
    
    
    
    #get_target_number_density(
    exyz_file = g.sims[k]['exyz']
    
    print(exyz_file)
    
    projectile = 1001
    tk = 26058
    rk = 27059
    print(xs.xs_data[projectile][tk][rk])
    
    
    exit()
    
    #for ion in g.exyz[exyz_file].keys():
    for ion in range(1,2):
      print(ion)
      for n in range(len(g.exyz[exyz_file][ion])):   
        if(g.exyz[exyz_file][ion][n,2] > target_depth):
          break
        else:
          f = 1.0
          if(g.exyz[exyz_file][ion][n,3] > target_depth):
            f = (target_depth - g.exyz[exyz_file][ion][n,2]) / (g.exyz[exyz_file][ion][n,3] - g.exyz[exyz_file][ion][n,2])
          energy = g.exyz[exyz_file][ion][n,0]
          
          
          
          for target in g.sims[k]['target_residual']:
            for residual in g.sims[k]['target_residual'][target]:
              sigma = xs.get_xs(projectile, target, residual, energy)
            
              print(projectile, target, residual, g.exyz[exyz_file][ion][n,0], f, energy, sigma)
        
    
    print(target_depth)
    
    #1001 26058 27059 31425000.0 0.409733124019 31425000.0 -0.1988622135


    # Calculate reaction rates
    exyz_file = g.sims[k]['exyz']
    
    print(exyz_file)
    
    print(g.sims[k]['target_residual'])
    
    for ion in g.exyz[exyz_file].keys():
      print(ion)

    
    
  #def rr(trajectory, depth):  
    
    
    
    
    """
    #rr(beam, target, exyz)
    projectile = 1001
    target = 26054
    residual = 26052
    energy = 2.6E7
    
    sigma = xs.get_xs(projectile, target, residual, energy)
    
    print(g.sims[k]['target_residual'])
    
    
    #
    #exyz = g.exyz['exyz_file']

    """