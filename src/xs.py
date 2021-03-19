
import bz2
import pickle
import _pickle as cPickle

class xs:

  residuals = None
  emitted = None

  @staticmethod
  def start(dir):
    print("Loading residual xs")
    xs.residual = xs.pload(dir + '/residual.pz')
    print("Loading emitted xs")
    xs.emitted = xs.pload(dir + '/emitted.pz')
    print("Load complete")

  @staticmethod
  def psave(file_name, d):
    with bz2.BZ2File(file_name, 'w') as f: 
      cPickle.dump(d, f)

  @staticmethod
  def pload(file_name):
    data = bz2.BZ2File(file_name, 'rb')
    return cPickle.load(data)


  
  @staticmethod
  def get_residual(projectile, target):
    return xs.residual[projectile][target]

  
  @staticmethod
  def get_emitted(projectile, target):
    return xs.emitted[projectile][target]

  
  
  @staticmethod
  def get_sigma_residual(projectile, target, residual, energy):
    sigma = 0.0
    for i in range(len(xs.residual[projectile][target][residual])):
      d = xs.residual[projectile][target][residual][i]
      sigma = sigma + xs.get_sigma_value(d, energy)
    return sigma
  
  
  @staticmethod
  def get_sigma_emitted(projectile, target, emitted, energy):
    sigma = 0.0
    for i in range(len(xs.emitted[projectile][target][emitted])):
      d = xs.emitted[projectile][target][emitted][i]
      sigma = sigma + xs.get_sigma_value(d, energy)
    return sigma
    
    
  @staticmethod
  def get_sigma_value(d, energy):
    if(energy < d[0][0] or energy > d[-1][0]):
      return 0.0
    else:
      for i in range(len(d)-1):
        if(energy >= d[i][0] and energy <= d[i+1][0]):
          return max(0.0, d[i][1] + ((energy-d[i][0])/(d[i+1][0] - d[i][0])) * (d[i+1][1] - d[i][1]))
        