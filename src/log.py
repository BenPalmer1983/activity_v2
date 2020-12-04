import time

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
      
      
      