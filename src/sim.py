import numpy


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
                }
                
    # Make directories    
    std.make_dir('output/' + k + '/plots')
    std.make_dir('output/' + k + '/xs_data')
    std.make_dir('output/' + k + '/results')
    std.make_dir('output/' + k + '/gamma_lines')
    std.make_dir('output/' + k + '/saturation_activities')
    
    
    std.make_dir('output/' + k + '/plots/in_beam')
    std.make_dir('output/' + k + '/plots/end_of_sim')
    std.make_dir('output/' + k + '/plots/total_activity')
    std.make_dir('output/' + k + '/plots/xs_plots')
    std.make_dir('output/' + k + '/plots/gamma_lines')
                
    # Beam
    g.sims[k]['beam'] = beam()
    g.sims[k]['beam'].set_duration(g.sims_input[k]['beam_duration'], g.sims_input[k]['beam_duration_unit'])
    g.sims[k]['beam'].set_area(g.sims_input[k]['beam_area'], g.sims_input[k]['beam_area_unit'])
    g.sims[k]['beam'].set_current(g.sims_input[k]['beam_current'], g.sims_input[k]['beam_current_unit'])
    g.sims[k]['beam'].set_energy(g.sims_input[k]['beam_energy'], g.sims_input[k]['beam_energy_unit'])
    g.sims[k]['beam'].set_projectile(g.sims_input[k]['beam_projectile'])
    g.sims[k]['beam'].set()
    g.sims[k]['beam'].display()
    
    
  
    # End time
    try: 
      end_time = units.convert(g.sims_input[k]['end_time_units'], 's', g.sims_input[k]['end_time'])
    except:
      end_time = g.sims[k]['beam'].get_duration()
    g.sims[k]['end_time'] = g.sims_input[k]['end_time']
    

    # Target
    g.sims[k]['target'] = target()
    g.sims[k]['target'].set_composition(g.sims_input[k]['target_composition'])
    g.sims[k]['target'].set_depth(g.sims_input[k]['target_depth'], g.sims_input[k]['target_depth_unit'])
    g.sims[k]['target'].set_density(g.sims_input[k]['target_density'], g.sims_input[k]['target_density_unit'])
    g.sims[k]['target'].calc_nd()
    g.sims[k]['target'].display()
    
    # Load XS
    ilist = g.sims[k]['target'].get_isotope_list()
    
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
    for tn in ilist:
      if(tn not in g.sims[k]['tally'].keys()):
        g.sims[k]['tally'][tn] = 0.0
      if(tn not in g.sims[k]['rr'].keys()):
        g.sims[k]['rr'][tn] = 0.0
      g.sims[k]['tally'][tn] = g.sims[k]['tally'][tn] + v * g.sims[k]['target'].get_isotope_number_density(tn)
      
    # Load residuals to tally, create rr entry
    for tn in ilist:
      residual_list = tendl.get_residual_list(projectile, tn)  
      for rn in residual_list:
        if(rn != 0 and rn not in g.sims[k]['tally'].keys()):
          g.sims[k]['tally'][rn] = 0.0
        if(rn != 0 and rn not in g.sims[k]['rr'].keys()):
          g.sims[k]['rr'][rn] = 0.0
                
    # Load emitted to tally, create rr entry  
    for tn in ilist:
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
    
    
    
    

  def run_sim(k):
    
    print()
    print("Run Sim")
    print("===================") 
    
    
    log.title("Run Sim", True)
    
 
    # Get data
    target_depth = g.sims[k]['target'].get_depth()
    ilist = g.sims[k]['target'].get_isotope_list()
    exyz_file = g.sims[k]['exyz']    
    projectile = g.sims[k]['beam'].get_projectile_code()
    flux = g.sims[k]['beam'].get_flux()
    beam_duration = g.sims[k]['beam'].get_duration()
    end_time = g.sims[k]['end_time']
    
    print("Plot Ion Energy Lost") 
    log.title("Plot Ion Energy Lost")     
    
    # Find exit energies
    d_energy = numpy.zeros((len(g.exyz[exyz_file]),),)
    nn = 0
    min_energy = None
    max_energy = None
    for ion in g.exyz[exyz_file].keys():
      start_energy = g.exyz[exyz_file][ion][0,2]
      energy = g.exyz[exyz_file][ion][0,2]  
      for n in range(len(g.exyz[exyz_file][ion])): 
        if(g.exyz[exyz_file][ion][n,4] > target_depth):
          break
        else:
          energy = g.exyz[exyz_file][ion][n,0]
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
    plt.savefig('output/' + k + '/plots/ion_energy_lost.eps', format='eps')
    plt.close('all') 
    
   

    # Make target-residual and target-emitted lists
    tn_rn = []
    tn_en = []
    for tn in ilist:    
      residual_list = tendl.get_residual_list(projectile, tn)  
      emitted_list = tendl.get_emitted_list(projectile, tn)        
      for rn in residual_list:
        if(rn != 0):
          tn_rn.append([tn,rn])
      for en in emitted_list:
        if(en != 0):
          tn_en.append([tn,en])
          
          
          
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
        file_path = 'output/' + k + '/xs_data/' + 'xs_' + str(isotopes.get_readable(tn)) + '_' + str(isotopes.get_readable(rn))
        std.write_csv(file_path + '.dat', xs_temp, w=14)
    
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('XS Target-Reaction vs Energy ' + isotopes.get_readable(tn) + ' --> ' + isotopes.get_readable(rn))
        plt.xlabel('Energy (eV)')
        plt.ylabel('XS barns (Barns)')
        plt.grid(True)
        plt.plot(xs_temp[:,0], xs_temp[:,1])
        plt.savefig(file_path, format='eps')
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
        file_path = 'output/' + k + '/xs_data/' + 'xs_' + str(isotopes.get_readable(tn)) + '_' + str(isotopes.get_readable(en))
        std.write_csv(file_path + '.dat', xs_temp, w=14)
    
        plt.clf()
        plt.figure(figsize=(12,8))    
        plt.title('XS Target-Emitted vs Energy ' + isotopes.get_readable(tn) + ' --> ' + isotopes.get_readable(en))
        plt.xlabel('Energy (eV)')
        plt.ylabel('XS barns (Barns)')
        plt.grid(True)
        plt.plot(xs_temp[:,0], xs_temp[:,1])
        plt.savefig(file_path, format='eps')
        plt.close('all')     
    
    
    print()
    print("Number Density")  
    print("===================")      
    log.title("Number Density")  
    for tn in ilist:  
      print(std.pad_right(isotopes.get_readable(tn), 10) + "   " + str(g.sims[k]['target'].get_isotope_number_density(tn)))
      log.log(std.pad_right(isotopes.get_readable(tn), 10) + "   " + str(g.sims[k]['target'].get_isotope_number_density(tn)))
    print()
    
    
    
    
    
    print("Calculate reaction rates")  
    log.title("Calculate reaction rates")  

    #
    # Residuals
    #
    
    # Loop through each target-residual permutation
    for i in tn_rn:
      tn = i[0]
      rn = i[1]
      
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

            sigma = tendl.get_xs_residual(projectile, tn, rn, energy)
            sigma_dr = sigma_dr + sigma * f * dr
            
      # cross section per ion for this thickness 
      sigma_dr = sigma_dr / len(g.exyz[exyz_file])  
      
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
    log.br()    
   
    #
    # Emitted
    #
    
    # Loop through each target-residual permutation
    for i in tn_en:
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
    log.br() 
        
    print()
    print("Reaction Rates")
    print("===================")     
    for n in g.sims[k]['rr'].keys():
      if(g.sims[k]['rr'][n] != 0.0):
        print(n, g.sims[k]['rr'][n])
    print()
    
    
    
    
    
    
    
    print()
    print("Saturation Times")
    print("===================")       
    
    log.title("Saturation Times") 
    log.log("Time where saturation is 95%")
    for key in g.sims[k]['rr'].keys():
      if(g.sims[k]['rr'][key] != 0.0 and not isotopes.is_stable(key)): 
        l = isotopes.get_decay_constant(key)
        t = numpy.log(0.05) / (-1.0 * l)
        print(std.pad_right(isotopes.get_readable(key),10) + "  " + std.pad_right(t, 18))
        log.log(std.pad_right(isotopes.get_readable(key),10) + "  " + std.pad_right(t, 18))
    log.br()
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
        plt.savefig('output/' + k + '/saturation_activities/' + 'saturation_' + str(isotopes.get_readable(key)), format='eps')
        plt.close('all') 
    
    
    
    #
    # Decay
    # 

    # Beam End Tally
    #########################
    
    

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
        
        
    print()
    print("End of Beam")
    print("===================")     
    for key in g.sims[k]['tally_beam_end'].keys():    
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
      plt.savefig('output/' + k + '/plots/in_beam/' + 'in_beam_amounts' + str(isotopes.get_readable(key)), format='eps')
      plt.close('all') 
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Activity During Irradiation of  ' + isotopes.get_readable(key))
      plt.xlabel('Time (s)')
      plt.ylabel('Activity (Bq)')
      plt.plot(g.sims[k]['inbeam'][key][:,0], g.sims[k]['inbeam'][key][:,2])
      plt.savefig('output/' + k + '/plots/in_beam/' + 'in_beam_activity_' + str(isotopes.get_readable(key)), format='eps')
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
    plt.savefig('output/' + k + '/plots/total_activity/' + 'in_beam_total_activity' + str(key), format='eps')
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
      plt.savefig('output/' + k + '/plots/end_of_sim/' + 'total_sim_amount_' + str(isotopes.get_readable(key)), format='eps')
      plt.close('all') 

      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Total Activity Throughout Simulation')
      plt.xlabel('Time (s)')
      plt.ylabel('Activity (Bq)')
      plt.plot(plot_x, plot_ya)
      plt.savefig('output/' + k + '/plots/end_of_sim/' + 'total_sim_activity_' + str(isotopes.get_readable(key)), format='eps')
      plt.close('all') 
    
    
    
    plt.clf()
    plt.figure(figsize=(12,8))    
    plt.title('Total Activity Throughout Simulation')
    plt.xlabel('Time (s)')
    plt.ylabel('Activity (Bq)')
    plt.plot(total_activity[:,0], total_activity[:,1])
    plt.savefig('output/' + k + '/plots/total_activity/' + 'total_sim_total_activity', format='eps')
    plt.close('all') 
    
    
    
    
    
    
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
    n = 0
    for key in g.sims[k]['tally_beam_end'].keys():
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_beam_end'][key]
        
        if(isotope_activity != 0):
          try:
            gn = isotopes.get_gammas(key)
            g.sims[k]['gammas_beam_end'][n:n+len(gn), 0] = gn[:,0]
            g.sims[k]['gammas_beam_end'][n:n+len(gn), 1] = isotope_activity * gn[:,1]
            n = n + len(gn)
          except:
            pass

    if(len(g.sims[k]['gammas_beam_end']) > 0):
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Predicted Gamma Lines')
      plt.xlabel('Energy (eV)')
      plt.ylabel('Activity (Bq)')
      plt.stem(g.sims[k]['gammas_beam_end'][:,0], g.sims[k]['gammas_beam_end'][:,1])
      plt.savefig('output/' + k + '/gamma_lines/' + 'end_of_beam_gamma_lines', format='eps')
      plt.close('all') 
      std.write_csv('output/' + k + '/gamma_lines/end_of_beam_gamma_lines.dat', g.sims[k]['gammas_beam_end'], w=14)
    
    
    
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
    n = 0
    for key in g.sims[k]['tally_sim_end'].keys():
      if(not isotopes.is_stable(key)):
        isotope_activity = isotopes.get_decay_constant(key) * g.sims[k]['tally_sim_end'][key]
        
        if(isotope_activity != 0):
          try:
            gn = isotopes.get_gammas(key)
            g.sims[k]['gammas_sim_end'][n:n+len(gn), 0] = gn[:,0]
            g.sims[k]['gammas_sim_end'][n:n+len(gn), 1] = isotope_activity * gn[:,1]
            n = n + len(gn)
          except:
            pass
    
    
    
    if(len(g.sims[k]['gammas_sim_end']) > 0):
    
      plt.clf()
      plt.figure(figsize=(12,8))    
      plt.title('Predicted Gamma Lines')
      plt.xlabel('Energy (eV)')
      plt.ylabel('Activity (Bq)')
      plt.stem(g.sims[k]['gammas_sim_end'][:,0], g.sims[k]['gammas_sim_end'][:,1])
      plt.savefig('output/' + k + '/gamma_lines/' + 'end_of_sim_gamma_lines', format='eps')
      plt.close('all') 
      std.write_csv('output/' + k + '/gamma_lines/end_of_sim_gamma_lines.dat', g.sims[k]['gammas_sim_end'], w=14)
    





    
    
    ###########################
    # Isotopes
    ###########################


    fh = open('output/' + k + '/radioactive_isotopes.dat', 'w')
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
    fh.write('\n')
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





