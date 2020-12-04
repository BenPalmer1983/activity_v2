import numpy


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

