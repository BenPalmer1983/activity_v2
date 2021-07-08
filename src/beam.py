

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
    
    
    
    
    
    
    
    
    
 